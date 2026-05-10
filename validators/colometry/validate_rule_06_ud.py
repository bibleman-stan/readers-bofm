"""
Rule 6 (Causal Clauses Break) — UD-query implementation.

UD signature (per canon §3):
    advcl with mark = 'because'

A causal advcl introduced by 'because' should begin on its OWN line — the
break falls BEFORE 'because'. Violation: the 'because' mark token and the
matrix predicate (the head of the advcl) sit on the SAME v2-mine line
(no break exists before 'because').

Buckets:
    STRONG-SPLIT-CANDIDATE — matrix and 'because' on the same line.
    (No REVIEW tier — the UD signature is unambiguous per canon §5 Rule 6.
     The canon's only exception is "short-line contexts where the combined
     line passes the atomic-thought test," which requires human review; those
     cases are captured as REVIEW-REQUIRED when the combined line is short.)

Short-line exception: if the advcl subtree + matrix are together ≤10 content
words, route to REVIEW-REQUIRED (short combined line may pass atomic-thought
test per Rule 6 exception).
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

# Combined content-word count at or below which we flag REVIEW rather than STRONG.
SHORT_LINE_THRESHOLD = 10


def content_count(sent: Sentence, tok: Token) -> int:
    """Count non-PUNCT tokens in subtree of tok."""
    return sum(1 for t in sent.subtree(tok) if t.upos != "PUNCT")


def scan_book(book_id: str, *, verbose: bool = False) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)

    findings = []
    for sent in sentences:
        # Find all advcl tokens
        for advcl_tok in sent.find(deprel="advcl"):
            # Check for a 'mark' dependent with lemma/form 'because'
            mark = sent.mark_of(advcl_tok)
            if mark is None:
                continue
            if mark.lemma.lower() != "because" and mark.form.lower() != "because":
                continue

            # Rule 6 targets verbal causal clauses.  "because of NP" constructions
            # parse as advcl with a NOUN head (e.g. "because of their faith" →
            # advcl head = faith/NOUN).  These are PP-equivalents, not finite
            # subordinate clauses, and do not warrant a break under Rule 6.
            # Filter: advcl head must be VERB or ADJ.
            if advcl_tok.upos not in {"VERB", "ADJ"}:
                continue

            # Audit-driven filter (2026-05-10): "because of NP" leaks through
            # when the parser tags a gerund/nominalization as VERB. If the
            # advcl head has a 'case' dependent with form/lemma 'of', this is
            # a "because of" PP-equivalent, not a finite causal clause.
            has_of_case = any(
                d.deprel == "case" and (d.form.lower() == "of" or d.lemma.lower() == "of")
                for d in sent.dependents_of(advcl_tok)
            )
            if has_of_case:
                continue

            # The matrix is the head of the advcl
            matrix = sent.head_of(advcl_tok)
            if matrix is None:
                continue

            matrix_line = line_map.get((sent.sent_id, matrix.id))
            because_line = line_map.get((sent.sent_id, mark.id))

            if matrix_line is None or because_line is None:
                continue
            if matrix_line != because_line:
                continue  # already split — no violation

            # Audit-driven filter (2026-05-10): fronted causal clauses.
            # "(For/And now,) because X, they Y" — the natural break is
            # AFTER the fronted clause, not before "because". Detect:
            # mark token id < matrix token id (because precedes matrix).
            # The current detector flags these because they're on the same
            # line, but the right action would be to break after the advcl
            # subtree, not before the mark. Bucket as REVIEW.
            because_fronted = mark.id < matrix.id

            # Both on the same line — violation.
            # Measure combined length for short-line exception.
            advcl_size = content_count(sent, advcl_tok)
            matrix_size = content_count(sent, matrix)
            combined = advcl_size + matrix_size  # rough (may double-count matrix deps)

            if because_fronted:
                bucket = "REVIEW-REQUIRED"
                review_reason = "fronted-because-needs-break-after"
            elif combined <= SHORT_LINE_THRESHOLD:
                bucket = "REVIEW-REQUIRED"
                review_reason = "short-combined-line"
            else:
                bucket = "STRONG-SPLIT-CANDIDATE"
                review_reason = None

            findings.append({
                "book": book_id,
                "sent_id": sent.sent_id,
                "matrix_id": matrix.id,
                "matrix_form": matrix.form,
                "matrix_lemma": matrix.lemma,
                "because_id": mark.id,
                "matrix_line": matrix_line,
                "because_line": because_line,
                "combined_size": combined,
                "bucket": bucket,
                "review_reason": review_reason,
                "sent_text": sent.text,
            })

    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book", help="single book id (default: all)")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    book_ids = [args.book] if args.book else BOOKS

    all_findings: list[dict] = []
    for bid in book_ids:
        try:
            fs = scan_book(bid, verbose=args.verbose)
        except FileNotFoundError as e:
            print(f"[skip] {bid}: {e}", file=sys.stderr)
            continue
        all_findings.extend(fs)
        if args.verbose:
            print(f"{bid}: {len(fs)} findings")

    strong = [f for f in all_findings if f["bucket"] == "STRONG-SPLIT-CANDIDATE"]
    review = [f for f in all_findings if f["bucket"] == "REVIEW-REQUIRED"]

    print("=" * 72)
    print("Rule 6 UD-query — Causal clauses break — BofM corpus")
    print("=" * 72)
    print(f"Books scanned:          {len(book_ids)}")
    print(f"Total findings:         {len(all_findings)}")
    print(f"  STRONG-SPLIT-CANDIDATE: {len(strong)}")
    print(f"  REVIEW-REQUIRED:        {len(review)}")
    print()

    if all_findings:
        print("--- STRONG-SPLIT-CANDIDATE (first 8) ---")
        for f in strong[:8]:
            print(f"  [{f['book']}] sent={f['sent_id']} "
                  f"matrix='{f['matrix_form']}' (lemma={f['matrix_lemma']}) "
                  f"line {f['matrix_line']} — 'because' on same line "
                  f"(combined~{f['combined_size']} words)")
            if args.verbose:
                print(f"    text: {f['sent_text'][:120]}")
        if len(strong) > 8:
            print(f"  ... +{len(strong) - 8} more")
        print()

        print("--- REVIEW-REQUIRED (first 8) ---")
        for f in review[:8]:
            print(f"  [{f['book']}] sent={f['sent_id']} "
                  f"matrix='{f['matrix_form']}' (lemma={f['matrix_lemma']}) "
                  f"line {f['matrix_line']} — combined~{f['combined_size']} words "
                  f"[{f['review_reason']}]")
            if args.verbose:
                print(f"    text: {f['sent_text'][:120]}")
        if len(review) > 8:
            print(f"  ... +{len(review) - 8} more")

    sys.exit(1 if all_findings else 0)


if __name__ == "__main__":
    main()
