"""
Validate severed complement-spanning-frame patterns — UD-query implementation.

UD signature:
  A `ccomp` clause headed by a speech/cognition verb V, where inside the ccomp:
    - an advcl or adverbial modifier (advcl/obl) sits on a DIFFERENT v2-mine
      line than the ccomp root (the matrix predication of the complement)
    - the advcl/obl subtree ends one v2-mine line and the ccomp root starts
      the next line (so the frame/advcl was severed from its own matrix clause)

The regex pattern (validate_severed_complement.py) matched:
  line N: `…that (when|after|before|as|while|until|if|because|since|
            though|although)…,`
  line N+1: subject-pronoun or common-NP lead (matrix predication)

UD translation:
  - The triggering verb V has a `ccomp` child (complement clause root = CR)
  - CR has an `advcl` child whose MARK lemma is one of the temporal/conditional
    subordinators above
  - advcl sits on line N; CR sits on line N+1 (or later)
  - V.lemma in SPEECH | COGNITION (matches the regex's implicit assumption
    that this is a complement-governor context)

Why UD is cleaner:
  - DEPREL `ccomp` scopes the search to complement clauses; the regex matched
    any occurrence of 'that (when|after|…)' regardless of syntactic context,
    producing false positives where 'that' is a relative pronoun.
  - The `advcl` + mark-lemma pattern explicitly encodes the frame+matrix
    structure rather than approximating it with surface word-order.
  - LEMMA normalization eliminates the need for PRED_LEAD_RE's wordlist of
    subject/demonstrative openers.

Paired regex validator: validators/colometry/validate_severed_complement.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from validators.parsing.conllu_query import load_conllu, Sentence, Token
from validators.parsing.line_mapping import build_line_map, book_paths

BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]

SPEECH = {
    "say", "speak", "declare", "testify", "swear", "proclaim",
    "tell", "confess", "rehearse", "preach", "answer", "cry",
}
COGNITION = {
    "know", "believe", "perceive", "remember", "understand", "hear",
    "see", "suppose", "imagine", "forget", "think",
}
GOVERNING_LEMMAS = SPEECH | COGNITION

# Temporal/conditional subordinators that introduce a frame inside a complement
FRAME_MARKS = {
    "when", "after", "before", "as", "while", "until",
    "if", "because", "since", "though", "although",
}


def _line_ends_with_colon(v2_path: str, line_num: int) -> bool:
    """Read v2-mine line `line_num` (1-based) and check if it ends with ':'."""
    try:
        with open(v2_path, encoding="utf-8") as f:
            for i, line in enumerate(f, start=1):
                if i == line_num:
                    return line.rstrip().endswith(":")
                if i > line_num:
                    break
    except OSError:
        pass
    return False


def _word_token_count(sent: Sentence, root: Token) -> int:
    """Count non-PUNCT tokens in the subtree of root."""
    return sum(1 for t in sent.subtree(root) if t.upos != "PUNCT")


def _is_substantive_advcl(sent: Sentence, advcl_root: Token) -> bool:
    """Return True if the advcl frame is substantive and earns its own line.

    Mirrors _is_substantive_frame from validate_frame_predication_merges_ud.py.
    A severed-complement advcl (the conditional/temporal frame inside a ccomp)
    is substantive — and therefore REVIEW-REQUIRED rather than STRONG — when
    ANY of:
    - >=8 word tokens (PUNCT excluded) — bulk threshold
    - contains a relative clause inside (acl/acl:relcl) — internal predication
    - contains a coordinate stack of >=2 conj members — list-shaped
    - contains a purpose-adjunct child (advcl with modal aux) — embedded frame

    See: validate_frame_predication_merges_ud._is_substantive_frame for the
    parallel application of this heuristic on frame+matrix violations.
    """
    subtree = list(sent.subtree(advcl_root))
    word_tokens = [t for t in subtree if t.upos != "PUNCT"]
    if len(word_tokens) >= 8:
        return True
    for t in subtree:
        if t is advcl_root:
            continue
        if t.deprel in ("acl", "acl:relcl"):
            return True
    conj_count = sum(1 for t in subtree if t.deprel == "conj")
    if conj_count >= 2:
        return True
    for t in subtree:
        if t is advcl_root:
            continue
        if t.deprel == "advcl":
            for aux in sent.aux_of(t):
                if aux.upos == "AUX" and aux.lemma in {
                    "may", "might", "shall", "should", "will", "would",
                    "can", "could", "must",
                }:
                    return True
    return False


def scan_book(book_id: str) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)
    v2_path_str = str(v2_path)

    violations = []
    for sent in sentences:
        for ccomp in sent.find(deprel="ccomp"):
            # Governor must be a speech/cognition verb
            head = sent.head_of(ccomp)
            if head is None or head.upos != "VERB":
                continue
            if head.lemma not in GOVERNING_LEMMAS:
                continue
            head_line = line_map.get((sent.sent_id, head.id))
            # Inside the ccomp, look for advcl children of the ccomp root
            for advcl in sent.dependents_of(ccomp, deprel="advcl"):
                mark = sent.mark_of(advcl)
                if mark is None:
                    continue
                if mark.lemma not in FRAME_MARKS:
                    continue
                # The advcl (frame) and the ccomp root (matrix predication)
                # must sit on different lines
                advcl_line = line_map.get((sent.sent_id, advcl.id))
                ccomp_line = line_map.get((sent.sent_id, ccomp.id))
                if advcl_line is None or ccomp_line is None:
                    continue
                if advcl_line == ccomp_line:
                    continue  # frame and matrix already merged; no violation
                # Frame must appear BEFORE the ccomp root (line N < line N+1)
                if advcl_line >= ccomp_line:
                    continue

                # Filter A: direct-discourse colon exception. If the
                # governor's line ends with ':', the ccomp is direct
                # discourse — complement-integrity does not apply
                # (the reader is reading the quote itself, not a
                # complement-spanned predication).
                review_reason = None
                if head_line is not None and _line_ends_with_colon(
                    v2_path_str, head_line
                ):
                    review_reason = "direct-discourse-colon"

                # Filter B: Rule 17 speech-indirect long-complement
                # exception (canon §5 R17). If the speech-tag is short
                # (head's line has <=8 word tokens within the matrix
                # subtree, excluding ccomp content) AND the complement
                # body is substantial (>=8 word tokens), the split is
                # licensed per the canon §5 R17 long-complement exception.
                if review_reason is None:
                    ccomp_word_count = _word_token_count(sent, ccomp)
                    if ccomp_word_count >= 8:
                        # Count head_line word tokens NOT in ccomp subtree
                        ccomp_ids = {t.id for t in sent.subtree(ccomp)}
                        head_line_word_count = sum(
                            1 for t in sent.tokens
                            if line_map.get((sent.sent_id, t.id)) == head_line
                            and t.id not in ccomp_ids
                            and t.upos != "PUNCT"
                        )
                        if head_line_word_count <= 8:
                            review_reason = "R17-long-complement-short-tag"

                # Filter C: advcl-substantive exception. If the advcl frame
                # itself is substantive (>=8 word tokens, contains relcl,
                # coordinate stack, or embedded modal advcl), it earns its own
                # line per J5 and the split is not a violation.  Mirrors the
                # _is_substantive_frame filter in
                # validate_frame_predication_merges_ud.py.
                if review_reason is None:
                    if _is_substantive_advcl(sent, advcl):
                        review_reason = "substantive-advcl-J5"

                # Bucket: multi-line gaps are REVIEW-REQUIRED
                gap = ccomp_line - advcl_line
                if gap != 1:
                    bucket = "REVIEW-REQUIRED"
                    review_reason = review_reason or "non-adjacent-gap"
                elif review_reason is not None:
                    bucket = "REVIEW-REQUIRED"
                else:
                    bucket = "STRONG-MERGE-CANDIDATE"

                violations.append({
                    "book": book_id,
                    "sent_id": sent.sent_id,
                    "governor_form": head.form,
                    "governor_lemma": head.lemma,
                    "advcl_form": advcl.form,
                    "mark_lemma": mark.lemma,
                    "ccomp_form": ccomp.form,
                    "advcl_line": advcl_line,
                    "ccomp_line": ccomp_line,
                    "bucket": bucket,
                    "review_reason": review_reason,
                    "v2_path": v2_path_str,
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

    strong = [v for v in all_violations if v["bucket"] == "STRONG-MERGE-CANDIDATE"]
    review = [v for v in all_violations if v["bucket"] == "REVIEW-REQUIRED"]

    print("=" * 72)
    print("Severed complement-spanning-frame — UD-query")
    print("=" * 72)
    print(f"Books scanned: {len(book_ids)}")
    print(f"Violations:    {len(all_violations)}")
    print(f"  STRONG-MERGE-CANDIDATE: {len(strong)}")
    print(f"  REVIEW-REQUIRED:        {len(review)}")
    print()

    if all_violations:
        print("Sample (first 10):")
        for v in all_violations[:10]:
            tag = "[R]" if v["bucket"] == "REVIEW-REQUIRED" else "   "
            print(f"  {tag} [{v['book']}] sent={v['sent_id']}  "
                  f"gov={v['governor_form']!r}({v['governor_lemma']})  "
                  f"mark={v['mark_lemma']!r}  "
                  f"frame-line={v['advcl_line']} ccomp-line={v['ccomp_line']}")

    print(f"RESULT: violations={len(strong)} strong={len(strong)} review={len(review)}")
    sys.exit(1 if strong else 0)


if __name__ == "__main__":
    main()
