"""
Validate compound coordinate argument under shared verb — UD-query implementation.

UD signature:
  A `conj` token whose head is a noun functioning as obj/nsubj/obl of a verb,
  where the conj sits on a DIFFERENT v2-mine line than its head (first conjunct),
  AND:
    - the conj has a "cc" dependent with lemma "and" or "or"
    - there is a sibling ADV token with lemma "also" on the same line as the conj
    - the conj subtree contains no finite predicate (no AUX or VERB with Tense/
      VerbForm=Fin/Tense feats)

This is the UD equivalent of the regex pattern:
  line N ends with comma after an NP;
  line N+1 starts with "and|or also <DET/POSS/PREP>…" without own predication.

Why UD is cleaner:
  - DEPREL `conj` distinguishes NP-coordination from VP-coordination; the regex
    had to blacklist participial-coord/VP-coord forms by wordlist.
  - LEMMA collapses saith/said/spake → say, etc., so the governing-verb check
    is orthographic-free.
  - Finite-predicate detection uses Feats (VerbForm=Fin or Tense) rather than
    a 90-entry regex alternation.

Paired regex validator: 5-machinery/validators/colometry/validate_compound_coord.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from validators.parsing.conllu_query import load_conllu, Token, Sentence
from validators.parsing.line_mapping import build_line_map, book_paths

BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]

# Deprels that make an NP an argument of a verb
NP_ARG_DEPRELS = {"obj", "nsubj", "nsubj:pass", "obl", "iobj"}


def _has_finite_predicate(sent: Sentence, subtree_tokens: list[Token]) -> bool:
    """Return True if any token in the subtree looks like a finite predicate.

    Heuristic: a VERB or AUX token with VerbForm=Fin, or with a Tense feature,
    or with deprel `cop` on a nominal predicate. Bare infinitives (VerbForm=Inf)
    and present participles (VerbForm=Part, Tense absent) are excluded — they
    are the non-finite forms that legitimately appear in NP-coord fragments.
    """
    for t in subtree_tokens:
        if t.upos in {"VERB", "AUX"}:
            vf = t.feats.get("VerbForm", "")
            tense = t.feats.get("Tense", "")
            mood = t.feats.get("Mood", "")
            if vf == "Fin" or tense or mood == "Imp":
                return True
        if t.deprel == "cop":
            return True
    return False


def _has_also_sibling(sent: Sentence, conj_token: Token) -> bool:
    """True if a sibling ADV/PART with lemma 'also' appears on the conj's branch.

    The regex requires 'and|or also' as a two-word opener. In UD, 'also'
    typically attaches as an ADV/PART directly to the conj root or to the cc.
    We check both: sibling of conj.head that precedes conj, or dependent of conj.
    """
    # Direct dependent of conj_token with lemma 'also'
    for dep in sent.dependents_of(conj_token):
        if dep.lemma == "also":
            return True
    # Sibling: another dependent of conj_token.head with lemma 'also'
    head = sent.head_of(conj_token)
    if head is not None:
        for sibling in sent.dependents_of(head):
            if sibling.lemma == "also" and sibling.id < conj_token.id:
                return True
    return False


def scan_book(book_id: str) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)

    from validators.colometry.stack_detection import stack_leader_ids
    violations = []
    for sent in sentences:
        stack_leaders = stack_leader_ids(sent.tokens)
        for conj in sent.find(deprel="conj"):
            head = sent.head_of(conj)
            if head is None:
                continue
            # Head must be a NOUN (first conjunct NP)
            if head.upos not in {"NOUN", "PROPN", "PRON"}:
                continue
            # Head must itself be an argument of a VERB
            head_head = sent.head_of(head)
            if head_head is None:
                continue
            if head_head.upos != "VERB":
                continue
            if head.deprel not in NP_ARG_DEPRELS:
                continue
            # conj must have a cc dependent with lemma 'and' or 'or'
            cc_tokens = [c for c in sent.dependents_of(conj, deprel="cc")]
            if not any(c.lemma in {"and", "or"} for c in cc_tokens):
                continue
            # 'also' must appear
            if not _has_also_sibling(sent, conj):
                continue
            # Line boundary: head and conj must be on different lines
            head_line = line_map.get((sent.sent_id, head.id))
            conj_line = line_map.get((sent.sent_id, conj.id))
            if head_line is None or conj_line is None:
                continue
            if head_line == conj_line:
                continue  # already on same line; no violation
            # conj subtree must not contain a finite predicate
            subtree = sent.subtree(conj)
            if _has_finite_predicate(sent, subtree):
                continue
            # ISOLATION CONSTRAINT: the conj line must be a standalone fragment.
            # If tokens from OUTSIDE the conj subtree also appear on conj_line,
            # the conj is embedded mid-line alongside other content — not a
            # dangling-fragment violation. (Mirrors the regex's ≤60c length cap.)
            conj_subtree_ids = {t.id for t in subtree}
            non_conj_on_conj_line = [
                t for t in sent.tokens
                if t.id not in conj_subtree_ids
                and line_map.get((sent.sent_id, t.id)) == conj_line
                and t.upos not in {"PUNCT"}
            ]
            if non_conj_on_conj_line:
                continue  # conj line shared with non-conj tokens; not isolated
            # §2.2 exemption: if the surrounding verse exhibits a §2.2 stack
            # (>=2 stack-leader 'that'-marks), the new split landed in a
            # §2.2-restructured verse where compound-coord-isolation may be
            # a §2.2 byproduct (matrix verb + stack splits + DO landing on
            # its own line). Skip.
            if stack_leaders:
                continue
            violations.append({
                "book": book_id,
                "sent_id": sent.sent_id,
                "head_form": head.form,
                "conj_form": conj.form,
                "governor": head_head.form,
                "governor_lemma": head_head.lemma,
                "head_line": head_line,
                "conj_line": conj_line,
                "v2_path": str(v2_path),
            })

    # -----------------------------------------------------------------------
    # Post-detection filters — each can demote STRONG → REVIEW
    # Applied in order; once demoted, later filters still run but can't
    # re-promote.
    # -----------------------------------------------------------------------

    # FILTER 1 — Over-length-cap: if merging head_line + conj_line would
    # produce a line longer than LENGTH_CAP characters, the merge is not
    # authorized (length-cap discipline, 2026-05-09 session).  The pattern
    # is still worth noting, so demote to REVIEW rather than discard.
    LENGTH_CAP = 85
    v2_line_cache: dict[str, list[str]] = {}
    for v in violations:
        path = v["v2_path"]
        if path not in v2_line_cache:
            with open(path, encoding="utf-8") as fh:
                v2_line_cache[path] = fh.readlines()
        file_lines = v2_line_cache[path]
        h_text = file_lines[v["head_line"] - 1].rstrip()
        c_text = file_lines[v["conj_line"] - 1].rstrip()
        merged_len = len(h_text) + 1 + len(c_text.lstrip())
        if merged_len > LENGTH_CAP:
            v["bucket"] = "REVIEW-REQUIRED"
            v["review_reason"] = f"over-length-cap ({merged_len}>{LENGTH_CAP})"

    # FILTER 2 — Non-adjacent multi-line spread: if the conj line is more
    # than 1 line away from the head line, intervening lines already provide
    # enumeration members — this is a catalog/list spread, not a simple
    # dangling conjunct.  Merging the tail member onto the (distant) head
    # would skip over the intervening items.  Demote to REVIEW.
    for v in violations:
        gap = v["conj_line"] - v["head_line"]
        if gap > 1:
            if v.get("bucket") != "REVIEW-REQUIRED":
                v["bucket"] = "REVIEW-REQUIRED"
                v["review_reason"] = f"non-adjacent-spread (gap={gap})"
            elif "non-adjacent" not in v.get("review_reason", ""):
                v["review_reason"] += f"; non-adjacent-spread (gap={gap})"

    # FILTER 3 — Antimetabole: within a single sentence, if a (head=X, conj=Y,
    # gov=G) finding has a mirror (head=Y, conj=X, gov=G) finding, both are
    # members of an antimetabole chiasm (e.g., 1 Ne 22:7-8 "manifested unto
    # the Jews / and also unto the Gentiles ... unto the Gentiles / and also
    # unto the Jews"). The mirroring is a deliberate rhetorical structure —
    # preserving the visual parallelism is the editorial intent. Demote both
    # members to REVIEW.
    by_sent: dict[str, list[dict]] = {}
    for v in violations:
        by_sent.setdefault(v["sent_id"], []).append(v)
    for vs in by_sent.values():
        forms_to_v = {
            (v["head_form"].lower(), v["conj_form"].lower(), v["governor_lemma"]): v
            for v in vs
        }
        for v in vs:
            head_l = v["head_form"].lower()
            conj_l = v["conj_form"].lower()
            # Antimetabole requires distinct mirrored elements (X != Y); a
            # same-form coord (year/year/year/year list) is catalog repetition,
            # not antimetabole.
            if head_l == conj_l:
                if "bucket" not in v:
                    v["bucket"] = "STRONG-MERGE-CANDIDATE"
                continue
            mirror_key = (conj_l, head_l, v["governor_lemma"])
            mirror = forms_to_v.get(mirror_key)
            if mirror is not None and mirror is not v:
                if v.get("bucket") != "REVIEW-REQUIRED":
                    v["bucket"] = "REVIEW-REQUIRED"
                    v["review_reason"] = "antimetabole-mirror"
                elif "antimetabole" not in v.get("review_reason", ""):
                    v["review_reason"] += "; antimetabole-mirror"
            else:
                if "bucket" not in v:
                    v["bucket"] = "STRONG-MERGE-CANDIDATE"

    # Any violation not yet assigned a bucket is STRONG by default
    for v in violations:
        if "bucket" not in v:
            v["bucket"] = "STRONG-MERGE-CANDIDATE"

    return violations


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book", help="single book id (default: all)")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    book_ids = [args.book] if args.book else BOOKS

    all_violations = []
    for bid in book_ids:
        try:
            vs = scan_book(bid)
        except FileNotFoundError as e:
            print(f"[skip] {bid}: {e}", file=sys.stderr)
            continue
        all_violations.extend(vs)
        if args.verbose:
            print(f"{bid}: {len(vs)} violations")

    strong = [v for v in all_violations if v.get("bucket") == "STRONG-MERGE-CANDIDATE"]
    review = [v for v in all_violations if v.get("bucket") == "REVIEW-REQUIRED"]

    print("=" * 72)
    print("Compound coordinate argument under shared verb — UD-query")
    print("=" * 72)
    print(f"Books scanned:           {len(book_ids)}")
    print(f"STRONG-MERGE-CANDIDATE:  {len(strong)}")
    print(f"REVIEW-REQUIRED:         {len(review)}")
    print()

    if strong:
        print("STRONG sample (first 10):")
        for v in strong[:10]:
            print(f"  [{v['book']}] sent={v['sent_id']}  "
                  f"head={v['head_form']!r} conj={v['conj_form']!r}  "
                  f"gov={v['governor']!r}({v['governor_lemma']})  "
                  f"lines {v['head_line']}->{v['conj_line']}")

    if review and args.verbose:
        print()
        print(f"REVIEW (filtered, e.g., antimetabole — first 10):")
        for v in review[:10]:
            print(f"  [{v['book']}] sent={v['sent_id']}  "
                  f"head={v['head_form']!r} conj={v['conj_form']!r}  "
                  f"({v.get('review_reason', '')})")

    print(f"RESULT: violations={len(strong)} strong={len(strong)} review={len(review)}")
    sys.exit(1 if strong else 0)


if __name__ == "__main__":
    main()
