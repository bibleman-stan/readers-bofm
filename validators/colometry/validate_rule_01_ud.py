"""
Rule 1 (AICTP Formula Integrity) — UD-query implementation.

UD signature (per canon §3 / §5 Rule 1):
    expl(came, it) — dummy subject 'it' is expl dependent of the VERB
    with lemma 'come', which is the root of the AICTP frame.

Violation: one or more tokens of the AICTP span (And / And now / it /
came|come / to / pass) sit on DIFFERENT v2-mine lines — the formula has
been broken across a line boundary.

The AICTP span is defined as all tokens from the first token of the
sentence (CCONJ 'and' or ADV 'now' if present) up to and including
'pass' (the xcomp of 'came').  The following 'that' SCONJ is NOT part of
the formula span — it belongs to Rule 16.

Variants covered:
  - "And it came to pass"       (standard)
  - "And now it came to pass"   ('now' as advmod between 'And' and 'it')
  - "And it shall come to pass" ('shall' as aux)
  - "Now, it came to pass"      ('Now' as leading ADV, no 'And')
  - "it came to pass" (bare)    (sentence-initial expl without cc)

Exit code: 0 if zero violations, 1 if violations found.

Comparison target: none (first UD-query implementation of Rule 1).
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


def _aictp_span_token_ids(sent) -> list[int] | None:
    """Return the ordered token ids comprising the AICTP formula span, or
    None if this sentence contains no AICTP frame.

    Span = [optional cc 'and'] + [optional advmod 'now'] + expl 'it' +
           come-verb + [optional aux] + 'to' (mark) + 'pass' (xcomp).

    Detection anchor: find the VERB with lemma 'come' that has an expl
    dependent whose lemma is 'it'.  Then walk the formula tokens out from
    that anchor.
    """
    # Find came/come token with expl(come, it)
    come_tok = None
    it_tok = None
    for tok in sent.tokens:
        if tok.lemma == "come" and tok.upos == "VERB":
            for dep in sent.dependents_of(tok, deprel="expl"):
                if dep.lemma == "it":
                    come_tok = tok
                    it_tok = dep
                    break
        if come_tok:
            break

    if come_tok is None:
        return None

    # 'pass' is the xcomp of come_tok
    pass_tok = None
    for dep in sent.dependents_of(come_tok, deprel="xcomp"):
        if dep.lemma == "pass":
            pass_tok = dep
            break
    if pass_tok is None:
        # Non-standard parse — can't identify span; skip
        return None

    # 'to' is the mark of pass_tok (PART TO)
    to_tok = sent.mark_of(pass_tok)  # may be None for malformed parse

    # cc 'and' — cc dependent of come_tok that is immediately adjacent (within
    # 3 tokens of come_tok or it_tok).  Sentence-initial 'And' that attaches
    # as cc to a deeply-embedded come-verb (long anacolutha) is NOT part of
    # the AICTP span; include only when it sits within the formula window.
    and_tok = None
    formula_start = min(it_tok.id, come_tok.id)
    for dep in sent.dependents_of(come_tok, deprel="cc"):
        if dep.lemma in {"and", "and"} and abs(dep.id - formula_start) <= 3:
            and_tok = dep
            break

    # advmod 'now' — any advmod dependent of come_tok whose lemma is 'now'
    # (only for "And now it came to pass" variant)
    now_tok = None
    for dep in sent.dependents_of(come_tok, deprel="advmod"):
        if dep.lemma == "now" and dep.id < it_tok.id:
            now_tok = dep
            break

    # aux (shall/will/had) — aux dependent of come_tok
    aux_toks = [t for t in sent.aux_of(come_tok)]

    span_ids = set()
    if and_tok:
        span_ids.add(and_tok.id)
    if now_tok:
        span_ids.add(now_tok.id)
    span_ids.add(it_tok.id)
    span_ids.add(come_tok.id)
    for a in aux_toks:
        span_ids.add(a.id)
    if to_tok:
        span_ids.add(to_tok.id)
    span_ids.add(pass_tok.id)

    return sorted(span_ids)


def scan_book(book_id: str, *, verbose: bool = False) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)

    violations = []
    for sent in sentences:
        span_ids = _aictp_span_token_ids(sent)
        if span_ids is None:
            continue

        # Map each span token to its v2-mine line
        span_lines = {}
        for tid in span_ids:
            ln = line_map.get((sent.sent_id, tid))
            if ln is not None:
                span_lines[tid] = ln

        if not span_lines:
            continue

        unique_lines = set(span_lines.values())
        if len(unique_lines) > 1:
            # Sanity check: the AICTP formula is at most ~6 tokens and should
            # span at most 1–2 adjacent v2-mine lines in the worst case
            # (e.g., "And" on one line and "it came to pass" split onto the
            # next — the violation we want to catch). A span range > 5 lines
            # indicates a line_map alignment failure (usually caused by a
            # malformed conllu block that merged two consecutive sentences
            # without a blank-line separator). Skip these as false positives.
            min_line = min(unique_lines)
            max_line = max(unique_lines)
            if max_line - min_line > 5:
                if verbose:
                    print(f"  [SKIP line_map artifact] sent={sent.sent_id} "
                          f"span range={max_line - min_line}: {sent.text[:60]}")
                continue
            violations.append({
                "book": book_id,
                "sent_id": sent.sent_id,
                "sent_text": sent.text[:80],
                "span_ids": span_ids,
                "span_lines": span_lines,
                "min_line": min_line,
                "max_line": max_line,
                "v2_path": str(v2_path),
                "bucket": "STRONG-SPLIT-VIOLATION",
            })
            if verbose:
                print(f"  [VIOLATION] sent={sent.sent_id} "
                      f"lines {sorted(unique_lines)}: {sent.text[:70]}")

    return violations


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book", help="single book id (default: all)")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    book_ids = [args.book] if args.book else BOOKS

    all_violations = []
    books_scanned = 0
    for bid in book_ids:
        try:
            vs = scan_book(bid, verbose=args.verbose)
        except FileNotFoundError as e:
            print(f"[skip] {bid}: {e}", file=sys.stderr)
            continue
        books_scanned += 1
        all_violations.extend(vs)
        if args.verbose:
            print(f"{bid}: {len(vs)} violation(s)")

    print("=" * 72)
    print("Rule 1 (AICTP Formula Integrity) — UD-query detector")
    print("=" * 72)
    print(f"Books scanned: {books_scanned}")
    print(f"Violations:    {len(all_violations)}")
    print(f"  STRONG-SPLIT-VIOLATION: {len(all_violations)}")
    print(f"  REVIEW-REQUIRED:        0  (Rule 1 has no exceptions)")
    print()

    if all_violations:
        by_book: dict[str, list] = {}
        for v in all_violations:
            by_book.setdefault(v["book"], []).append(v)

        for bk, items in by_book.items():
            print(f"--- {bk.upper()} ({len(items)} violation(s)) ---")
            for v in items:
                lines_str = sorted(set(v["span_lines"].values()))
                print(f"  sent={v['sent_id']} lines={lines_str}")
                print(f"    {v['sent_text']}")
            print()

    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
