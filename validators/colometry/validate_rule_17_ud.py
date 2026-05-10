"""
Rule 17 (Complement Integrity) — UD-query implementation.

Phase 0 prototype using validators/parsing/conllu_query.py + line_mapping.py.

UD signature (per canon §3):
    ccomp(V, clause) where mark(clause) = 'that' and V.lemma in governing-verb set.

Violation: V and the 'that' mark sit on different v2-mine lines. The line
break should be removed (MERGE across boundary).

Why this is cleaner than the regex implementation:
  - LEMMA collapses surface morphology (saith/said/saying/sayest -> say).
  - ccomp distinguishes complement clauses from advcl/acl:relcl/parataxis,
    so the regex's exception filters (purpose 'that they might', AICTP,
    'that is' appositive, 'so X that Y' result, resumptive-after-if,
    relative 'that which has been', aspectual bare-finite) do not need
    individual handling — UD assigns each a non-ccomp deprel.

Comparison target: validators/colometry/validate_rule_17_complement_integrity.py
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Allow running as a script from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from validators.parsing.conllu_query import load_conllu
from validators.parsing.line_mapping import build_line_map, book_paths


# ---------------------------------------------------------------------------
# Vocative detection — Rule 15 collision guard
# ---------------------------------------------------------------------------
# Conservative seed matching canon Rule 15 true-vocative patterns.
# We only test the MATRIX LINE (head_line), not the ccomp body.  A vocative
# on the matrix line would — after the Rule 17 merge — sit inline in the
# merged line, violating Rule 15's "vocative earns its own line" prescription.
#
# Pattern design mirrors the VOCATIVE_PHRASES list in validate_rule_15_vocative.py
# but expressed as compiled regexes for direct line-level matching.

VOCATIVE_PATTERNS = [
    # "O Lord", "O God", "O Father", "O ye ...", "O my ...", "O house of Israel"
    re.compile(r"\bO\s+(?:Lord|God|Father|ye|my|house)\b", re.IGNORECASE),
    # Comma-preceded "my <vocative-noun>" mid-line: ", my son", ", my brethren", etc.
    re.compile(
        r",\s*my\s+(?:son|sons|brethren|beloved|people|father|friend|friends|"
        r"kindred|children|daughter|daughters|brother|brothers|sister|sisters|"
        r"fellow\s+servant|fellow\s+servants|fellow\s+labor)s?\b",
        re.IGNORECASE,
    ),
    # Line-initial "My <vocative-noun>" (address opening, not possessive object)
    re.compile(
        r"^\s*My\s+(?:son|sons|brethren|beloved|people|friend|friends|"
        r"kindred|children|daughter|daughters|brother|brothers|sister|sisters)\b",
        re.IGNORECASE,
    ),
]

# NP-object disqualifier: if the matrix line contains one of these verbs
# immediately before "my ...", the phrase is a syntactic object, not a vocative.
# We apply this only when no O-vocative is present (O-vocatives are never objects).
_NP_OBJECT_VERBS_RE = re.compile(
    r"\b(unto|with|of|among|to|for|by|upon|against|"
    r"spake|preach(?:ed)?|teach|teach(?:ed)?|sent|commanded|exhort(?:ed)?|"
    r"cried unto|went unto|went to)\s+my\b",
    re.IGNORECASE,
)


def is_vocative_on_matrix_line(v2_path: Path, head_line: int) -> bool:
    """Return True if the matrix line (head_line) contains a true vocative.

    Reads the single line at head_line from v2_path.  Applies the VOCATIVE_PATTERNS
    regex battery.  If an O-vocative fires, returns True immediately (O-vocatives
    are never NP-objects).  For "my <noun>" patterns, additionally checks the
    NP-object disqualifier before confirming.
    """
    try:
        with open(v2_path, encoding="utf-8") as fh:
            for i, raw in enumerate(fh, start=1):
                if i == head_line:
                    line = raw.rstrip("\n")
                    break
            else:
                return False
    except OSError:
        return False

    # O-vocative patterns (INTJ "O" + noun-phrase) are never NP-objects.
    if VOCATIVE_PATTERNS[0].search(line):
        return True

    # "my <noun>" mid-line (comma-preceded) or line-initial — check disqualifier.
    for pat in VOCATIVE_PATTERNS[1:]:
        if pat.search(line):
            # Disqualify if a transitive/prepositional verb precedes "my"
            if _NP_OBJECT_VERBS_RE.search(line):
                return False
            return True

    return False


# Governing-verb lemmas, by class. Matches canon §5 Rule 17.
CAUSATIVE = {"cause", "suffer", "permit", "command", "grant"}
ASPECTUAL = {"begin", "cease", "continue"}
SPEECH = {
    "say", "speak", "declare", "testify", "swear", "proclaim",
    "tell", "confess", "rehearse", "preach", "answer", "cry",
}
COGNITION = {
    "know", "believe", "perceive", "remember", "understand", "hear",
    "see", "suppose", "imagine", "forget", "think",
}
VOLITION = {"wish", "desire", "hope", "long", "trust", "pray", "seek"}

# {beseech, ask, plead} added 2026-05-10 per Wave 6 audit (Defect A): they were
# previously in PETITION_FRAME_VERBS but NOT in GOVERNING_LEMMAS, so 14 corpus
# cases (5 beseech + 1 ask + 8 plead) were silently unrouted by categorize().
GOVERNING_LEMMAS = CAUSATIVE | ASPECTUAL | SPEECH | COGNITION | VOLITION | {"beseech", "ask", "plead"}

# Petition-frame ambiguity filter (canon §5 Rule 17 exception).
# Speech- and volition-class verbs whose "that"-complement with a modal aux
# reads ambiguously between content (UD ccomp) and purpose (UD advcl).
# {cry, beseech, ask, plead} are speech-class; {pray, seek} are volition-class.
# When matrix lemma is in this set AND the ccomp body has a modal aux,
# bucket as REVIEW-REQUIRED instead of STRONG-MERGE-CANDIDATE.
# Renamed 2026-05-10 from DIRECTIVE_PETITION per Wave 6 audit (Defect C):
# speech-act-theory label was bandwagon-shape; mechanical-trigger naming
# describes the verb-set × modal-aux conjunction faithfully.
PETITION_FRAME_VERBS = {"cry", "pray", "beseech", "ask", "seek", "plead"}

# Modal aux lemmas that mark the ambiguity. Lemma 'will' covers will/would;
# lemma 'shall' covers shall/should; etc.
MODAL_AUX_LEMMAS = {"will", "shall", "may", "can", "must", "might", "should", "would", "could"}


def lemma_class(lemma: str) -> str:
    if lemma in CAUSATIVE: return "causative"
    if lemma in ASPECTUAL: return "aspectual"
    if lemma in SPEECH: return "speech"
    if lemma in COGNITION: return "cognition"
    if lemma in VOLITION: return "volition"
    return "unknown"


def categorize(sent, ccomp_root, head, head_line, mark_line, v2_path) -> tuple[str, str | None]:
    """Return (bucket, reason). Buckets: STRONG-MERGE-CANDIDATE or REVIEW-REQUIRED.

    Filters per audit findings (2026-05-10):
    0. Vocative on matrix line → Rule 15 collision (highest priority)
    1. Petition-frame matrix (cry/pray/beseech/ask/seek/plead) + modal-aux on
       ccomp body → ambiguous content vs purpose
    2. Speech-indirect long-complement: matrix in {say, speak, tell, declare}
       AND ccomp body has ≥8 word tokens (canon §5 Rule 17 exception)
    3. Multi-line gap with intervening polysyndetic series
    4. Coordinate that-series (N=2 adjudication territory)
    """
    # Filter 0 (highest priority): vocative on matrix line → Rule 15 collision.
    # Merging would fold the vocative inline, violating Rule 15's prescriptive
    # "vocative earns its own line" requirement.
    if is_vocative_on_matrix_line(Path(v2_path), head_line):
        return ("REVIEW-REQUIRED", "vocative-on-matrix-line-Rule-15-collision")

    # Filter 1: petition-frame + modal aux
    if head.lemma in PETITION_FRAME_VERBS:
        for aux in sent.aux_of(ccomp_root):
            if aux.lemma in MODAL_AUX_LEMMAS:
                return ("REVIEW-REQUIRED", "petition-frame+modal-aux")

    # Filter 2: speech-indirect long-complement exception (canon §5 Rule 17)
    if head.lemma in {"say", "speak", "tell", "declare"}:
        body_tokens = sent.subtree(ccomp_root)
        word_count = sum(1 for t in body_tokens if t.upos != "PUNCT")
        if word_count >= 8:
            return ("REVIEW-REQUIRED", "speech-long-complement")

    # Filter 3: multi-line gap. Mechanical merge across gap>1 risks
    # collapsing intermediate lines that may carry independent thought
    # units (parenthetical adjuncts, polysyndetic series members,
    # anaphoric resumptions). Route gap>1 to REVIEW unconditionally.
    if abs(mark_line - head_line) > 1:
        return ("REVIEW-REQUIRED", "multi-line-gap")

    # Filter 4: coordinate that-series (N=2 adjudication)
    for child in sent.dependents_of(ccomp_root, deprel="conj"):
        if sent.mark_of(child) is not None:
            child_mark = sent.mark_of(child)
            if child_mark and child_mark.lemma == "that":
                return ("REVIEW-REQUIRED", "coordinate-that-series-N2")

    return ("STRONG-MERGE-CANDIDATE", None)


# All 15 BofM books in the corpus.
BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]


def scan_book(book_id: str, *, verbose: bool = False) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)

    violations = []
    for sent in sentences:
        for ccomp in sent.find(deprel="ccomp"):
            head = sent.head_of(ccomp)
            if head is None:
                continue
            # Rule 17 governs VERB complements; ccomp of a noun (e.g. the noun
            # "desire" + that-clause) is a separate pattern not currently
            # codified. Surface those cases via a different signature if
            # canon ever adds a rule.
            if head.upos != "VERB":
                continue
            if head.lemma not in GOVERNING_LEMMAS:
                continue
            mark = sent.mark_of(ccomp)
            if mark is None or mark.lemma != "that":
                continue
            head_line = line_map.get((sent.sent_id, head.id))
            mark_line = line_map.get((sent.sent_id, mark.id))
            if head_line is None or mark_line is None:
                continue
            if head_line == mark_line:
                continue  # already merged; not a violation
            bucket, reason = categorize(sent, ccomp, head, head_line, mark_line, v2_path)
            violations.append({
                "book": book_id,
                "sent_id": sent.sent_id,
                "head_id": head.id,
                "head_form": head.form,
                "head_lemma": head.lemma,
                "head_class": lemma_class(head.lemma),
                "head_line": head_line,
                "mark_line": mark_line,
                "v2_path": str(v2_path),
                "bucket": bucket,
                "review_reason": reason,
            })
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

    print("=" * 72)
    print("Rule 17 UD-query — BofM corpus")
    print("=" * 72)
    print(f"Books scanned: {len(book_ids)}")
    print(f"Violations:    {len(all_violations)}")
    strong = [v for v in all_violations if v["bucket"] == "STRONG-MERGE-CANDIDATE"]
    review = [v for v in all_violations if v["bucket"] == "REVIEW-REQUIRED"]
    print(f"  STRONG-MERGE-CANDIDATE: {len(strong)}")
    print(f"  REVIEW-REQUIRED:        {len(review)}")
    if review:
        by_reason: dict[str, int] = {}
        for v in review:
            by_reason[v.get("review_reason") or "petition-frame+modal-aux"] = (
                by_reason.get(v.get("review_reason") or "petition-frame+modal-aux", 0) + 1
            )
        for reason, n in sorted(by_reason.items()):
            print(f"    {reason}: {n}")
    print()

    if all_violations:
        by_class: dict[str, list] = {}
        for v in all_violations:
            by_class.setdefault(v["head_class"], []).append(v)

        for cls in sorted(by_class):
            items = by_class[cls]
            n_strong = sum(1 for v in items if v["bucket"] == "STRONG-MERGE-CANDIDATE")
            n_review = len(items) - n_strong
            print(f"--- {cls.upper()} ({len(items)}: {n_strong} strong, {n_review} review) ---")
            for v in items[:8]:
                tag = "[R]" if v["bucket"] == "REVIEW-REQUIRED" else "   "
                print(f"  {tag} [{v['book']}] sent={v['sent_id']} "
                      f"{v['head_form']!r} (lemma={v['head_lemma']}) "
                      f"line {v['head_line']} -> mark on line {v['mark_line']}")
            if len(items) > 8:
                print(f"      ... +{len(items) - 8} more")
            print()

    print(f"RESULT: violations={len(all_violations)} strong={len(strong)} review={len(review)}")
    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
