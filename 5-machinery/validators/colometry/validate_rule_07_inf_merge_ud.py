"""
Rule 7 (Purpose Clauses Break) — SCOPE-merge direction.

Canon §5 R7 SCOPE statement (verbatim):
  "Non-finite infinitival purpose adjuncts (bare to + VERB, without subject
  or modal) are NOT in scope [of R7 SPLIT] and MUST merge with their matrix
  motion verb by this rule."

This validator detects cross-line cases of motion-verb + infinitival-purpose
(advcl or xcomp with mark=to) where the canon-mandated merge has not been
applied. Companion to validate_rule_07_ud.py (which detects the SPLIT
direction for finite that+modal purpose clauses).

UD signature:
  relation: [advcl, xcomp]
  head: { upos: VERB, lemma_in: MOTION_VERBS }
  mark: { lemma: to }
  action: MERGE_MATRIX_AND_PURPOSE_INF

The MOTION_VERBS set is subject-control motion lemmas. Causative-motion
verbs (send, command-to, suffer-to) are R17 territory (causative class +
obj-control xcomp+to) and are already covered by validate_rule_17_ud.py.

Why this validator exists:
  - Canon R7 SCOPE mandates the merge but there was no detector firing on
    it (per `feedback_principle_vs_mechanical_coverage`: principle-soundness
    does not equal mechanical coverage).
  - Stan-flagged Alma 31:11 ("Alma and his brethren went into the land /
    to preach the word unto them.") surfaced the gap.
  - Corpus survey: 1491 same-line conformance vs 81 cross-line drift
    (95% existing conformance; the cross-line cases are the editorial drift
    the validator now catches).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from validators.parsing.conllu_query import load_conllu
from validators.parsing.line_mapping import build_line_map, book_paths


# Subject-control motion verbs. Causative-motion (send/command/suffer-to)
# is R17 territory (causative class + xcomp+to), excluded here.
MOTION_VERBS = {
    "go", "come", "depart", "return", "journey", "travel",
    "ascend", "descend", "march", "run", "walk", "flee",
    "retreat", "arise", "rise", "hasten", "pass", "wander",
    "tarry", "stay", "remain", "abide", "sit",
    "gather", "assemble",
    "lift", "fall",
}


BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]


def scan_book(book_id: str) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)

    violations = []
    for sent in sentences:
        for deprel in ("advcl", "xcomp"):
            for inf in sent.find(deprel=deprel):
                head = sent.head_of(inf)
                if head is None or head.upos != "VERB":
                    continue
                if head.lemma not in MOTION_VERBS:
                    continue
                mark = sent.mark_of(inf)
                if mark is None or mark.lemma != "to":
                    continue
                head_line = line_map.get((sent.sent_id, head.id))
                mark_line = line_map.get((sent.sent_id, mark.id))
                if head_line is None or mark_line is None:
                    continue
                if head_line == mark_line:
                    continue  # already merged; not a violation
                # Bucket by gap. gap=1 = STRONG-MERGE-CANDIDATE.
                # gap>1 = REVIEW (intervening lines may carry their own ATU).
                gap = abs(mark_line - head_line)
                if gap == 1:
                    bucket = "STRONG-MERGE-CANDIDATE"
                    reason = None
                else:
                    bucket = "REVIEW-REQUIRED"
                    reason = "multi-line-gap"
                violations.append({
                    "book": book_id,
                    "sent_id": sent.sent_id,
                    "head_form": head.form,
                    "head_lemma": head.lemma,
                    "head_line": head_line,
                    "mark_line": mark_line,
                    "deprel": deprel,
                    "v2_path": str(v2_path),
                    "bucket": bucket,
                    "review_reason": reason,
                })
    return violations


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    book_ids = [args.book] if args.book else BOOKS
    all_v: list[dict] = []
    for bid in book_ids:
        try:
            vs = scan_book(bid)
        except FileNotFoundError as e:
            print(f"[skip] {bid}: {e}", file=sys.stderr)
            continue
        all_v.extend(vs)
        if args.verbose:
            print(f"{bid}: {len(vs)} violations")

    strong = [v for v in all_v if v["bucket"] == "STRONG-MERGE-CANDIDATE"]
    review = [v for v in all_v if v["bucket"] == "REVIEW-REQUIRED"]

    print("=" * 72)
    print("Rule 7 SCOPE-merge — motion-verb + infinitival-purpose (BofM corpus)")
    print("=" * 72)
    print(f"Books scanned: {len(book_ids)}")
    print(f"STRONG-MERGE-CANDIDATE: {len(strong)}")
    print(f"REVIEW (gap>1):         {len(review)}")
    print()

    if all_v:
        from collections import Counter
        per_lemma = Counter(v["head_lemma"] for v in strong)
        print("STRONG by motion-verb lemma:")
        for lemma, n in per_lemma.most_common():
            print(f"  {lemma:12s} {n}")
        print()
        for v in strong[:15]:
            print(f"  [{v['book']}] sent={v['sent_id']} "
                  f"{v['head_form']!r} (lemma={v['head_lemma']}, {v['deprel']}) "
                  f"L{v['head_line']} -> L{v['mark_line']}")
        if len(strong) > 15:
            print(f"  ... +{len(strong) - 15} more")

    print(f"\nRESULT: violations={len(all_v)} strong={len(strong)} review={len(review)}")
    sys.exit(1 if all_v else 0)


if __name__ == "__main__":
    main()
