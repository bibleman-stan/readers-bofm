"""
Rule 16 (AICTP Dangling 'that') — UD-query implementation.

UD signature (per canon §3 / §5 Rule 16):
    expl(came, it)  — identifies an AICTP sentence
    mark(content, that)  — the SCONJ 'that' marking the content clause
                           introduced by the AICTP frame

Violation: the SCONJ 'that' that immediately follows AICTP sits on the
SAME v2-mine line as the 'pass' token (i.e., 'that' is line-final on the
AICTP line instead of leading the next line).

Correct form:
    And it came to pass
    that [content clause...]

Violation form (dangling 'that'):
    And it came to pass that
    [content clause...]

OR equivalently: 'pass' and 'that' are on the same line AND 'that' is
the last substantive token on that line.

Detection note: because the SCONJ 'that' introduces the content clause,
it is the mark() of the content clause root (ccomp or advcl or csubj of
'came'/'pass'), NOT of 'pass' itself. The rule fires when:
  1. Sentence has AICTP frame (expl(came, it) as in Rule 1).
  2. A SCONJ 'that' is the mark() of a direct dependent of come_tok
     (the content clause root), OR it is the first non-PUNCT token of the
     sentence after 'pass'.
  3. that_line == pass_line  (they share a v2-mine line)

Comparison: 5-machinery/validators/colometry/validate_rule_16_aictp_dangling_that.py
  (regex version — catches 'to pass that' at line end)

Exit code: 0 if zero violations, 1 if violations found.
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


def _find_aictp_come_and_pass(sent):
    """Return (come_tok, pass_tok) or (None, None) if no AICTP frame."""
    for tok in sent.tokens:
        if tok.lemma == "come" and tok.upos == "VERB":
            for dep in sent.dependents_of(tok, deprel="expl"):
                if dep.lemma == "it":
                    # Found the AICTP anchor; now find 'pass'
                    for xc in sent.dependents_of(tok, deprel="xcomp"):
                        if xc.lemma == "pass":
                            return tok, xc
    return None, None


def _find_aictp_that(sent, come_tok):
    """Return the SCONJ 'that' token that belongs to this AICTP frame, or None.

    The 'that' marks the main content clause of the AICTP. It is the mark()
    of a child of come_tok (typically the ccomp/advcl root of the content
    clause), OR occasionally the mark() of a csubj/xcomp of pass.

    Strategy: find all SCONJ tokens with lemma 'that' that are mark()
    dependents of any direct child of come_tok, where that child's id is
    > pass_tok.id (i.e., appears after 'pass' in the sequence).  Take the
    earliest such 'that'.
    """
    pass_tok_id = None
    for xc in sent.dependents_of(come_tok, deprel="xcomp"):
        if xc.lemma == "pass":
            pass_tok_id = xc.id
            break
    if pass_tok_id is None:
        return None

    # Gather all direct children of come_tok that come after pass
    content_roots = [
        c for c in sent.dependents_of(come_tok)
        if c.id > pass_tok_id and c.deprel in {"ccomp", "advcl", "csubj", "xcomp", "parataxis"}
    ]

    candidates = []
    for cr in content_roots:
        m = sent.mark_of(cr)
        if m and m.lemma == "that" and m.upos == "SCONJ":
            candidates.append(m)

    # Also check: any SCONJ 'that' token with id == pass_tok_id + 1
    # (directly following 'pass') that is a mark() of anything — handles
    # cases where the parse hangs the 'that' off a deeply nested node.
    for tok in sent.tokens:
        if (tok.lemma == "that" and tok.upos == "SCONJ"
                and tok.id == pass_tok_id + 1):
            if tok not in candidates:
                candidates.append(tok)
        # Also check pass_tok_id + 2 in case a comma intervenes
        if (tok.lemma == "that" and tok.upos == "SCONJ"
                and tok.id == pass_tok_id + 2):
            if tok not in candidates:
                candidates.append(tok)

    if not candidates:
        return None
    return min(candidates, key=lambda t: t.id)


def scan_book(book_id: str, *, verbose: bool = False) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)

    violations = []
    for sent in sentences:
        come_tok, pass_tok = _find_aictp_come_and_pass(sent)
        if come_tok is None:
            continue

        that_tok = _find_aictp_that(sent, come_tok)
        if that_tok is None:
            # No 'that' in this AICTP — sentence ends at 'pass' or uses
            # a different subordinator. Rule 16 only governs 'that'. Skip.
            continue

        pass_line = line_map.get((sent.sent_id, pass_tok.id))
        that_line = line_map.get((sent.sent_id, that_tok.id))

        if pass_line is None or that_line is None:
            continue

        if pass_line == that_line:
            # 'that' is on the same line as 'pass' — potential dangling 'that'
            # but only a violation if 'that' is the LAST non-PUNCT token on
            # that v2-mine line (i.e., it truly dangles at line end).
            # Strategy: find all tokens on pass_line whose id > that_tok.id;
            # if all of them are PUNCT or outside the AICTP line, it dangles.
            tokens_on_same_line = [
                t for t in sent.tokens
                if line_map.get((sent.sent_id, t.id)) == pass_line
                and t.id > that_tok.id
                and t.upos != "PUNCT"
            ]
            if tokens_on_same_line:
                # 'that' is NOT line-final — conforming (something follows it
                # on the same line before the content clause continues)
                continue

            # 'that' IS effectively line-final on the AICTP line → violation
            violations.append({
                "book": book_id,
                "sent_id": sent.sent_id,
                "sent_text": sent.text[:80],
                "pass_line": pass_line,
                "that_line": that_line,
                "that_tok_id": that_tok.id,
                "v2_path": str(v2_path),
                "bucket": "STRONG-SPLIT-CANDIDATE",
            })
            if verbose:
                print(f"  [VIOLATION] sent={sent.sent_id} "
                      f"pass+that on line {pass_line}: {sent.text[:70]}")

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
    print("Rule 16 (AICTP Dangling 'that') — UD-query detector")
    print("=" * 72)
    print(f"Books scanned: {books_scanned}")
    print(f"Violations:    {len(all_violations)}")
    print(f"  STRONG-SPLIT-CANDIDATE: {len(all_violations)}")
    print(f"  REVIEW-REQUIRED:        0  (Rule 16 has no exceptions)")
    print()

    if all_violations:
        by_book: dict[str, list] = {}
        for v in all_violations:
            by_book.setdefault(v["book"], []).append(v)

        for bk, items in by_book.items():
            print(f"--- {bk.upper()} ({len(items)} violation(s)) ---")
            for v in items:
                print(f"  sent={v['sent_id']} line={v['pass_line']}")
                print(f"    {v['sent_text']}")
            print()

    print(f"RESULT: violations={len(all_violations)} strong={len(all_violations)} review=0")
    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
