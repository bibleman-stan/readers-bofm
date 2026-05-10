"""
Rule 5 (Equivalence "Or" as Appositive) — UD-query implementation.

UD signature (per canon §3):
    cc(conj, or) — a 'cc' dependent with form="or" attached to a 'conj' token.

    When *or* connects synonymous reformulations ("in other words"), the two
    conjuncts and their linking *or* should sit on the SAME v2-mine line.
    If they are split across two lines, flag as STRONG-MERGE-CANDIDATE.

Heuristic (from canon §5 Rule 5):
    Substitute "that is to say" for *or*. If the meaning holds, it is
    equivalence-*or* → MERGE. If it breaks, it is genuine disjunction.

UD-detectable heuristic: if both conjuncts have the SAME UPOS *and* each
conjunct's subtree is short (≤4 content tokens), the pair is likely
appositive → STRONG. Otherwise → REVIEW-REQUIRED (requires substitution test).

Note: the 'cc' token attaches to the HEAD of the second conjunct (the conj
token). The first conjunct is the head of the second conjunct's 'conj'
relation — i.e., sent.head_of(conj_token).
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

# Max subtree word-count for a conjunct to be flagged STRONG rather than REVIEW.
SHORT_CONJUNCT_THRESHOLD = 4


def content_token_count(sent: Sentence, tok: Token) -> int:
    """Count non-PUNCT tokens in the subtree of tok."""
    return sum(1 for t in sent.subtree(tok) if t.upos != "PUNCT")


def scan_book(book_id: str, *, verbose: bool = False) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)

    findings = []
    for sent in sentences:
        # Find all 'cc' tokens whose form is "or" (case-insensitive surface)
        for cc_tok in sent.find(deprel="cc"):
            if cc_tok.form.lower() != "or":
                continue
            # The cc token attaches to the second conjunct head
            conj_head = sent.head_of(cc_tok)
            if conj_head is None:
                continue
            # conj_head must itself carry a 'conj' deprel pointing to the
            # first conjunct (its own head)
            if conj_head.deprel != "conj":
                continue
            first_conjunct = sent.head_of(conj_head)
            if first_conjunct is None:
                continue

            # Both conjuncts must be on different lines for a violation to exist
            first_line = line_map.get((sent.sent_id, first_conjunct.id))
            second_line = line_map.get((sent.sent_id, conj_head.id))
            if first_line is None or second_line is None:
                continue
            if first_line == second_line:
                continue  # already on same line — no violation

            # Categorise by heuristic
            same_upos = first_conjunct.upos == conj_head.upos
            first_size = content_token_count(sent, first_conjunct)
            second_size = content_token_count(sent, conj_head)
            both_short = (
                first_size <= SHORT_CONJUNCT_THRESHOLD
                and second_size <= SHORT_CONJUNCT_THRESHOLD
            )

            # Two STRONG conditions:
            # (a) both conjuncts short + same UPOS
            # (b) second conjunct short (≤4) + same UPOS: short restatement of
            #     a longer phrase — canonical Mosiah 15:24 pattern ("have a part
            #     in the first resurrection, or have eternal life"). Asymmetric-
            #     short second conjunct is the primary BofM equivalence signal.
            second_short = second_size <= SHORT_CONJUNCT_THRESHOLD
            if same_upos and (both_short or second_short):
                bucket = "STRONG-MERGE-CANDIDATE"
            else:
                bucket = "REVIEW-REQUIRED"

            findings.append({
                "book": book_id,
                "sent_id": sent.sent_id,
                "cc_id": cc_tok.id,
                "first_conjunct_form": first_conjunct.form,
                "first_conjunct_upos": first_conjunct.upos,
                "second_conjunct_form": conj_head.form,
                "second_conjunct_upos": conj_head.upos,
                "first_line": first_line,
                "second_line": second_line,
                "first_size": first_size,
                "second_size": second_size,
                "bucket": bucket,
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

    strong = [f for f in all_findings if f["bucket"] == "STRONG-MERGE-CANDIDATE"]
    review = [f for f in all_findings if f["bucket"] == "REVIEW-REQUIRED"]

    print("=" * 72)
    print("Rule 5 UD-query — Equivalence 'or' as appositive — BofM corpus")
    print("=" * 72)
    print(f"Books scanned:          {len(book_ids)}")
    print(f"Total findings:         {len(all_findings)}")
    print(f"  STRONG-MERGE-CANDIDATE: {len(strong)}")
    print(f"  REVIEW-REQUIRED:        {len(review)}")
    print()

    if all_findings:
        print("--- STRONG-MERGE-CANDIDATE (first 8) ---")
        for f in strong[:8]:
            print(f"  [{f['book']}] sent={f['sent_id']} "
                  f"'{f['first_conjunct_form']}' ({f['first_conjunct_upos']}, sz={f['first_size']}) "
                  f"OR '{f['second_conjunct_form']}' ({f['second_conjunct_upos']}, sz={f['second_size']}) "
                  f"lines {f['first_line']}->{f['second_line']}")
            if args.verbose:
                print(f"    text: {f['sent_text'][:120]}")
        if len(strong) > 8:
            print(f"  ... +{len(strong) - 8} more")
        print()

        print("--- REVIEW-REQUIRED (first 8) ---")
        for f in review[:8]:
            print(f"  [{f['book']}] sent={f['sent_id']} "
                  f"'{f['first_conjunct_form']}' ({f['first_conjunct_upos']}, sz={f['first_size']}) "
                  f"OR '{f['second_conjunct_form']}' ({f['second_conjunct_upos']}, sz={f['second_size']}) "
                  f"lines {f['first_line']}->{f['second_line']}")
            if args.verbose:
                print(f"    text: {f['sent_text'][:120]}")
        if len(review) > 8:
            print(f"  ... +{len(review) - 8} more")

    sys.exit(1 if all_findings else 0)


if __name__ == "__main__":
    main()
