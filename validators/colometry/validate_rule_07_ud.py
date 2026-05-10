"""
Rule 7 (Purpose Clauses Break) — UD-query implementation.

UD signature (per canon §3):
    advcl with mark='that' and aux ∈ {may, might, shall, should, will, would, ...}

Action: BREAK before 'that'.

Violation: the matrix and the 'that' mark sit on the SAME v2-mine line
(no break) — the purpose clause hasn't been split off.

This rule existed previously only as an exception filter inside the regex
Rule 17 validator. As a first-class detector it closes a gap in mechanical
coverage: cases where a purpose clause never got its own line.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from validators.parsing.conllu_query import load_conllu
from validators.parsing.line_mapping import build_line_map, book_paths


MODAL_AUX_LEMMAS = {
    "will", "shall", "may", "can", "must",
    "might", "should", "would", "could",
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
        for advcl in sent.find(deprel="advcl"):
            mark = sent.mark_of(advcl)
            if mark is None or mark.lemma != "that":
                continue
            modals = [a for a in sent.aux_of(advcl) if a.lemma in MODAL_AUX_LEMMAS]
            if not modals:
                continue
            head = sent.head_of(advcl)
            if head is None:
                continue
            head_line = line_map.get((sent.sent_id, head.id))
            mark_line = line_map.get((sent.sent_id, mark.id))
            if head_line is None or mark_line is None:
                continue
            if head_line != mark_line:
                continue  # split already exists; no violation
            violations.append({
                "book": book_id,
                "sent_id": sent.sent_id,
                "head_form": head.form,
                "head_lemma": head.lemma,
                "advcl_form": advcl.form,
                "modal": modals[0].form,
                "line": head_line,
                "v2_path": str(v2_path),
            })
    return violations


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book")
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
    print("Rule 7 UD-query — BofM corpus (purpose-clause missing-break)")
    print("=" * 72)
    print(f"Books scanned: {len(book_ids)}")
    print(f"STRONG-SPLIT-CANDIDATE: {len(all_violations)}")
    print()

    for v in all_violations[:20]:
        print(f"  [{v['book']}] sent={v['sent_id']} "
              f"matrix={v['head_form']!r} (lemma={v['head_lemma']}) "
              f"+ that {v['modal']} {v['advcl_form']}  on line {v['line']}")
    if len(all_violations) > 20:
        print(f"  ... +{len(all_violations) - 20} more")

    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
