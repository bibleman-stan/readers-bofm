"""
Rule 23 (Date Colophon Integrity) — UD-query implementation.

UD signature (per canon §3/§5):
    Token sequence matching a date-colophon formula. All tokens in the
    formula must sit on the same v2-mine line. A cross-line occurrence
    is a violation.

Canonical formula patterns (matched by token lemma/form chain):
    (a) "in the Nth year of the reign of the judges"
        → in / the / <ordinal> / year / of / the / reign / of / the / judge|judges
    (b) "in the Nth year of the reign of king <name>"
        → in / the / <ordinal> / year / of / the / reign / of / king
    (c) "in the Nth year since Lehi left Jerusalem" (variant)
        → in / the / <ordinal> / year / since
    (d) Numeric variant: "in the X and Nth year..." — ordinal preceded by
        a number word + "and"

Detection strategy:
    Scan token stream for the anchor sequence "in the" immediately followed
    (within 4 tokens) by a word whose lemma is "year". Collect the full
    date-colophon span from "in" through the last expected formula token.
    If any token in the span maps to a different v2-mine line than the
    anchor, flag STRONG-MERGE-CANDIDATE.

Why UD over regex:
    The regex validator uses \\s+ to catch cross-line matches, which is correct
    but operates on raw text. The UD approach integrates with the standard
    line-mapping infrastructure, gives accurate per-token line numbers, and is
    the consistent interface for the audit dashboard.

Comparison target: validators/colometry/validate_rule_23_date_colophon.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from validators.parsing.conllu_query import load_conllu, Token
from validators.parsing.line_mapping import build_line_map, book_paths


BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]

# Ordinal word forms (lowercased) that appear in date formulas.
ORDINALS = {
    "first", "second", "third", "fourth", "fifth", "sixth", "seventh",
    "eighth", "ninth", "tenth", "eleventh", "twelfth", "thirteenth",
    "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth",
    "nineteenth", "twentieth", "twenty", "thirtieth", "thirty",
    "fortieth", "forty", "fiftieth", "fifty", "sixtieth", "sixty",
    "seventieth", "seventy", "eightieth", "eighty", "ninetieth", "ninety",
    "hundredth", "hundred",
}

# Number words that can appear as "X and Nth year" (e.g. "forty and second")
NUMBER_WORDS = {
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
    "sixty", "seventy", "eighty", "ninety", "hundred",
}


def _is_ordinal_or_number(form: str) -> bool:
    return form.lower() in ORDINALS or form.lower() in NUMBER_WORDS


def _find_date_colophon_spans(tokens: list[Token]) -> list[tuple[int, int, str]]:
    """
    Scan token list for date-colophon anchors.
    Returns list of (start_idx, end_idx, formula_type) where start/end are
    indices into `tokens`.

    Formula detected:
      "in" + "the" + [optional number + "and"] + ordinal + "year" + "of" + ...
    The span extends from "in" to at minimum "year". Further extension:
      - after "year" if "of the reign" follows (capture through "judges" or "king")
      - after "year" if "since" follows (capture 2 more tokens as context)
    """
    spans: list[tuple[int, int, str]] = []
    n = len(tokens)
    i = 0
    while i < n:
        # Anchor: "in" (form) followed by "the" within next 1 token
        if tokens[i].form.lower() != "in":
            i += 1
            continue
        if i + 1 >= n or tokens[i + 1].form.lower() != "the":
            i += 1
            continue
        # Now look for ordinal/number word within next 3 positions
        j = i + 2
        # Allow "X and Nth" prefix (e.g. "forty and second")
        # Skip at most: [number word] [and] [ordinal]
        while j < n and j < i + 5 and (
            tokens[j].form.lower() in NUMBER_WORDS
            or tokens[j].form.lower() == "and"
        ):
            j += 1
        if j >= n or not _is_ordinal_or_number(tokens[j].form):
            i += 1
            continue
        # Expect "year" next (possibly after another "and <ordinal>")
        k = j + 1
        # Allow compound ordinals: "forty and second year" — skip "and <ordinal>"
        if k < n and tokens[k].form.lower() == "and":
            k += 1  # "and"
            if k < n and _is_ordinal_or_number(tokens[k].form):
                k += 1  # <ordinal>
        if k >= n or tokens[k].form.lower() != "year":
            i += 1
            continue
        # We have confirmed "in the ... year". Determine formula type and extent.
        year_idx = k
        end_idx = year_idx  # minimum span end
        formula_type = "year-formula"

        # Look ahead after "year" for "of the reign of the judges/king" or "since"
        m = year_idx + 1
        if m < n and tokens[m].form.lower() == "of":
            # "of the reign of the judges" or "of the reign of king"
            if (m + 1 < n and tokens[m + 1].form.lower() == "the"
                    and m + 2 < n and tokens[m + 2].form.lower() == "reign"
                    and m + 3 < n and tokens[m + 3].form.lower() == "of"):
                end_idx = m + 3  # "of the reign of"
                formula_type = "reign-formula"
                # One more: "the judges" or "king <name>"
                if m + 4 < n:
                    if tokens[m + 4].form.lower() == "the":
                        # "the judges" — extend 2 more
                        if m + 5 < n and tokens[m + 5].lemma.lower() in {"judge", "judges"}:
                            end_idx = m + 5
                            formula_type = "reign-of-the-judges"
                        else:
                            end_idx = m + 4
                    elif tokens[m + 4].form.lower() == "king":
                        end_idx = m + 4
                        formula_type = "reign-of-king"
            else:
                end_idx = m  # just "year of" for now
        elif m < n and tokens[m].form.lower() == "since":
            formula_type = "year-since"
            end_idx = m + 1 if m + 1 < n else m  # capture one more token

        spans.append((i, end_idx, formula_type))
        i = end_idx + 1  # advance past this span

    return spans


def scan_book(book_id: str) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)

    violations: list[dict] = []

    for sent in sentences:
        toks = sent.tokens
        spans = _find_date_colophon_spans(toks)
        for start_idx, end_idx, formula_type in spans:
            span_tokens = toks[start_idx:end_idx + 1]
            lines_hit: list[int] = []
            for t in span_tokens:
                ln = line_map.get((sent.sent_id, t.id))
                if ln is not None:
                    lines_hit.append(ln)
            if len(lines_hit) < 2:
                continue
            if min(lines_hit) != max(lines_hit):
                surface = " ".join(t.form for t in span_tokens)
                gap = max(lines_hit) - min(lines_hit)
                # Large gaps (>3 lines) indicate a line-mapping drift rather
                # than a genuine date-formula split: the formula tokens resolved
                # to widely-separated lines because the sentence's line anchor
                # drifted. Flag those as REVIEW-REQUIRED.
                bucket = "REVIEW-REQUIRED" if gap > 3 else "STRONG-MERGE-CANDIDATE"
                violations.append({
                    "book":         book_id,
                    "sent_id":      sent.sent_id,
                    "formula_type": formula_type,
                    "surface":      surface,
                    "line_min":     min(lines_hit),
                    "line_max":     max(lines_hit),
                    "line_gap":     gap,
                    "bucket":       bucket,
                })

    return violations


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book", help="single book id (default: all)")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    book_ids = [args.book] if args.book else BOOKS

    all_violations: list[dict] = []
    books_scanned = 0
    for bid in book_ids:
        try:
            vs = scan_book(bid)
        except FileNotFoundError as e:
            print(f"[skip] {bid}: {e}", file=sys.stderr)
            continue
        books_scanned += 1
        all_violations.extend(vs)
        if args.verbose:
            print(f"{bid}: {len(vs)} violations")

    print("=" * 72)
    print("Rule 23 UD-query (Date Colophon Integrity) — BofM corpus")
    print("=" * 72)
    strong = [v for v in all_violations if v["bucket"] == "STRONG-MERGE-CANDIDATE"]
    review = [v for v in all_violations if v["bucket"] == "REVIEW-REQUIRED"]
    print(f"Books scanned: {books_scanned}")
    print(f"Violations:    {len(all_violations)}")
    print(f"  STRONG-MERGE-CANDIDATE: {len(strong)}")
    print(f"  REVIEW-REQUIRED:        {len(review)}")
    print()

    if all_violations:
        by_type: dict[str, list[dict]] = {}
        for v in all_violations:
            by_type.setdefault(v["formula_type"], []).append(v)

        for ft in sorted(by_type):
            items = by_type[ft]
            n_strong = sum(1 for v in items if v["bucket"] == "STRONG-MERGE-CANDIDATE")
            n_review = len(items) - n_strong
            print(f"--- {ft} ({len(items)}: {n_strong} strong, {n_review} review) ---")
            for v in items[:5]:
                tag = "[R]" if v["bucket"] == "REVIEW-REQUIRED" else "   "
                print(f"  {tag} [{v['book']}] sent={v['sent_id']} "
                      f"lines {v['line_min']}-{v['line_max']} (gap={v['line_gap']})  "
                      f"surface: {v['surface']!r}")
            if len(items) > 5:
                print(f"    ... +{len(items) - 5} more")
            print()
    else:
        print("No violations found. Rule 23 compliance is clean.")

    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
