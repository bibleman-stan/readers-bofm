"""
Rule 18 (Fixed Idiom Integrity) — UD-query implementation.

UD signature (per canon §3/§5):
    Token sequence matching the fixed-idiom list. Every token in the idiom
    must sit on the same v2-mine line. A cross-line occurrence is a violation.

Why UD over regex:
    The regex implementation (validate_rule_18_fixed_idioms.py) works on raw
    text with \\s+ matching across newlines. The UD version works on the same
    aligned token positions used by Rule 17 and avoids false positives from
    hyphenated or unusual whitespace forms. It also integrates naturally with
    the rest of the UD-query audit dashboard.

Detection logic:
    For each sentence, scan the token list for idiom anchor tokens (by lemma
    or lowercased form). When an anchor is found, verify the full idiom token
    sequence matches. Collect the min/max v2-mine line numbers for the idiom
    span. If min != max, the idiom straddles a line break → STRONG-MERGE-CANDIDATE.

Fixed-idiom list (per canon §5 Rule 18):
    - put to death
    - put an end to
    - from time to time
    - prevailed upon
    - one with another
    - it is expedient that
    - in behalf of
    (Rule 23 date-colophon formulas are handled by validate_rule_23_ud.py)

Comparison target: 5-machinery/validators/colometry/validate_rule_18_fixed_idioms.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from validators.parsing.conllu_query import load_conllu
from validators.parsing.line_mapping import build_line_map, book_paths
from validators.colometry.stack_detection import stack_leader_ids


# Fixed idioms as sequences of (form or lemma) to match token-by-token.
# Each entry: (name, sequence_of_lowercased_forms)
# We match by lowercased token FORM for surface-faithful matching.
FIXED_IDIOMS: list[tuple[str, list[str]]] = [
    ("put to death",        ["put", "to", "death"]),
    ("put an end to",       ["put", "an", "end", "to"]),
    ("from time to time",   ["from", "time", "to", "time"]),
    ("prevailed upon",      ["prevailed", "upon"]),
    ("one with another",    ["one", "with", "another"]),
    ("it is expedient that", ["it", "is", "expedient", "that"]),
    ("in behalf of",        ["in", "behalf", "of"]),
]

# Index: first token -> list of (name, full_sequence) for quick lookup
_ANCHOR_INDEX: dict[str, list[tuple[str, list[str]]]] = {}
for _name, _seq in FIXED_IDIOMS:
    _anchor = _seq[0]
    _ANCHOR_INDEX.setdefault(_anchor, []).append((_name, _seq))


BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]


def _match_idiom_at(tokens: list, start_idx: int, seq: list[str]) -> list[int] | None:
    """Try to match `seq` starting at token index `start_idx`.
    Returns list of token indices (into `tokens`) if matched, else None.
    Skips multi-word tokens (those with non-integer ids are already filtered
    by the conllu loader, so all tokens have integer ids).
    """
    indices: list[int] = []
    ti = start_idx
    for expected in seq:
        if ti >= len(tokens):
            return None
        if tokens[ti].form.lower() != expected:
            return None
        indices.append(ti)
        ti += 1
    return indices


def scan_book(book_id: str) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)

    violations: list[dict] = []

    for sent in sentences:
        toks = sent.tokens  # list[Token], integer ids, in order
        stack_leaders = stack_leader_ids(toks)
        for i, tok in enumerate(toks):
            anchor = tok.form.lower()
            if anchor not in _ANCHOR_INDEX:
                continue
            for name, seq in _ANCHOR_INDEX[anchor]:
                matched_indices = _match_idiom_at(toks, i, seq)
                if matched_indices is None:
                    continue
                # Collect v2-mine line numbers for the matched tokens
                lines_hit: list[int] = []
                for idx in matched_indices:
                    t = toks[idx]
                    ln = line_map.get((sent.sent_id, t.id))
                    if ln is not None:
                        lines_hit.append(ln)
                if len(lines_hit) < 2:
                    continue  # can't confirm a split without ≥2 mapped tokens
                # §2.2 exemption: if any token in the matched idiom is a stack-
                # leader 'that'-mark, the line split is §2.2-licensed (not a
                # §2.1 idiom-integrity violation). E.g. "it is expedient that X,
                # that Y" splits at each 'that' per §2.2; idiom "it is expedient
                # that" straddling that split is canon-compliant.
                if any(toks[idx].id in stack_leaders for idx in matched_indices):
                    continue
                if min(lines_hit) != max(lines_hit):
                    gap = max(lines_hit) - min(lines_hit)
                    # Large gaps indicate line-mapping drift rather than a genuine
                    # idiom split. Apply the same threshold used in Rule 23 (>3).
                    bucket = "REVIEW-REQUIRED" if gap > 3 else "STRONG-MERGE-CANDIDATE"
                    violations.append({
                        "book":      book_id,
                        "sent_id":   sent.sent_id,
                        "idiom":     name,
                        "sequence":  " ".join(t.form for t in [toks[j] for j in matched_indices]),
                        "line_min":  min(lines_hit),
                        "line_max":  max(lines_hit),
                        "line_gap":  gap,
                        "bucket":    bucket,
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
    print("Rule 18 UD-query (Fixed Idiom Integrity) — BofM corpus")
    print("=" * 72)
    strong = [v for v in all_violations if v["bucket"] == "STRONG-MERGE-CANDIDATE"]
    review = [v for v in all_violations if v["bucket"] == "REVIEW-REQUIRED"]
    print(f"Books scanned: {books_scanned}")
    print(f"Violations:    {len(all_violations)}")
    print(f"  STRONG-MERGE-CANDIDATE: {len(strong)}")
    print(f"  REVIEW-REQUIRED:        {len(review)}")
    print()

    if all_violations:
        by_idiom: dict[str, list[dict]] = {}
        for v in all_violations:
            by_idiom.setdefault(v["idiom"], []).append(v)

        for idiom_name in sorted(by_idiom):
            items = by_idiom[idiom_name]
            n_strong = sum(1 for v in items if v["bucket"] == "STRONG-MERGE-CANDIDATE")
            n_review = len(items) - n_strong
            print(f"--- {idiom_name!r} ({len(items)}: {n_strong} strong, {n_review} review) ---")
            for v in items[:5]:
                tag = "[R]" if v["bucket"] == "REVIEW-REQUIRED" else "   "
                print(f"  {tag} [{v['book']}] sent={v['sent_id']} "
                      f"lines {v['line_min']}-{v['line_max']} (gap={v['line_gap']})  "
                      f"surface: {v['sequence']!r}")
            if len(items) > 5:
                print(f"    ... +{len(items) - 5} more")
            print()
    else:
        print("No violations found. Rule 18 compliance is clean.")

    print(f"RESULT: violations={len(all_violations)} strong={len(strong)} review={len(review)}")
    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
