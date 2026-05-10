"""
Rule 26 (Adjective + "that" Complement) — UD-query implementation.

UD signature (per canon §3 / §5 Rule 26):
    ccomp(ADJ, clause) with mark(clause) = 'that', where the head token
    has upos == "ADJ" (or is a predicative adjective — VERB with ADJ function
    resolved by checking head_upos).

Action: MERGE — the adjective predicate is grammatically incomplete without
its clausal complement. "It is expedient" leaves "expedient what?" open;
the that-clause closes the valence slot.

The canonical BofM case: "it is expedient that X" where 'expedient' is the
predicate ADJ.

Violation: ADJ head and the 'that' mark sit on different v2-mine lines.
The line break should be removed (STRONG-MERGE-CANDIDATE).

REVIEW-REQUIRED: cases where the head is tagged as something other than ADJ
but functions predicatively (e.g., past participle used adjectively, or
VERB in copular construction), or where the ccomp is nested inside a larger
complement already handled by Rule 17.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from validators.parsing.conllu_query import load_conllu
from validators.parsing.line_mapping import build_line_map, book_paths


BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]

# Known BofM predicate adjectives that take that-complements (for confidence).
# This list is informational; the UD query does not need it — upos=ADJ is
# the primary signal. Listed for annotation in the report.
KNOWN_PRED_ADJ = {
    "expedient", "possible", "impossible", "necessary", "needful",
    "desirous", "good", "meet", "proper", "right", "just", "important",
    "true", "certain", "clear", "plain",
}


def scan_book(book_id: str) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)

    results = []
    for sent in sentences:
        for ccomp_tok in sent.find(deprel="ccomp"):
            head = sent.head_of(ccomp_tok)
            if head is None:
                continue

            # Primary target: head is an ADJ
            if head.upos == "ADJ":
                head_is_adj = True
                review_reason = None
            elif head.upos in {"VERB", "AUX"}:
                # Some parsers tag predicative adjectives as VERB in copular
                # constructions; check for ADJ-lemma in known list as a
                # secondary heuristic.
                if head.lemma in KNOWN_PRED_ADJ:
                    head_is_adj = True
                    review_reason = "head tagged VERB but lemma in known-adj list"
                else:
                    continue    # VERB head → Rule 17 territory, not Rule 26
            else:
                continue        # other upos → out of scope

            mark = sent.mark_of(ccomp_tok)
            if mark is None or mark.lemma != "that":
                continue

            head_line = line_map.get((sent.sent_id, head.id))
            mark_line = line_map.get((sent.sent_id, mark.id))
            if head_line is None or mark_line is None:
                continue

            if head_line == mark_line:
                continue    # already merged → no violation

            bucket = "REVIEW-REQUIRED" if review_reason else "STRONG-MERGE-CANDIDATE"

            results.append({
                "book": book_id,
                "sent_id": sent.sent_id,
                "head_id": head.id,
                "head_form": head.form,
                "head_lemma": head.lemma,
                "head_upos": head.upos,
                "head_line": head_line,
                "mark_line": mark_line,
                "bucket": bucket,
                "review_reason": review_reason,
                "known_adj": head.lemma in KNOWN_PRED_ADJ,
                "sent_text": sent.text[:120],
            })

    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book", help="single book id (default: all)")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    book_ids = [args.book] if args.book else BOOKS

    all_results: list[dict] = []
    for bid in book_ids:
        try:
            recs = scan_book(bid)
        except FileNotFoundError as e:
            print(f"[skip] {bid}: {e}", file=sys.stderr)
            continue
        all_results.extend(recs)
        if args.verbose:
            print(f"{bid}: {len(recs)} candidates")

    strong = [r for r in all_results if r["bucket"] == "STRONG-MERGE-CANDIDATE"]
    review = [r for r in all_results if r["bucket"] == "REVIEW-REQUIRED"]

    print("=" * 72)
    print("Rule 26 UD-query — ADJ + 'that' Complement Integrity — BofM corpus")
    print("=" * 72)
    print(f"Books scanned:             {len(book_ids)}")
    print(f"Total candidates:          {len(all_results)}")
    print(f"  STRONG-MERGE-CANDIDATE:  {len(strong)}")
    print(f"  REVIEW-REQUIRED:         {len(review)}")
    print()

    # Lemma frequency breakdown
    from collections import Counter
    lemma_counts = Counter(r["head_lemma"] for r in all_results)
    print("Top predicate-ADJ lemmas:")
    for lemma, cnt in lemma_counts.most_common(10):
        known = " [known]" if lemma in KNOWN_PRED_ADJ else ""
        print(f"  {lemma!r:20s}  {cnt:3d}{known}")
    print()

    def show_samples(label: str, items: list[dict], n: int = 5):
        if not items:
            return
        print(f"--- {label} (up to {n} samples) ---")
        for r in items[:n]:
            reason = f"  reason={r['review_reason']}" if r["review_reason"] else ""
            print(f"  [{r['book']}] sent={r['sent_id']}{reason}")
            print(f"    head: {r['head_form']!r} (lemma={r['head_lemma']}, upos={r['head_upos']}) "
                  f"line {r['head_line']}")
            print(f"    mark: 'that' on line {r['mark_line']}")
            print(f"    text: {r['sent_text']}")
            print()

    show_samples("STRONG-MERGE-CANDIDATE", strong)
    show_samples("REVIEW-REQUIRED", review)

    print(f"RESULT: violations={len(strong)} strong={len(strong)} review={len(review)}")
    sys.exit(1 if strong else 0)


if __name__ == "__main__":
    main()
