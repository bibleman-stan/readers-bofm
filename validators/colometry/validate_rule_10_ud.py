"""
Rule 10 (V + DO split forbidden) — UD-query implementation.

UD signature (per canon §3):
    line-final VERB whose obj on the following line (bare NP continuation).

Action: MERGE.

Detection: a token with deprel=obj where the obj's line > head VERB's line.
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


def scan_book(book_id: str) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)

    violations = []
    for sent in sentences:
        for obj in sent.find(deprel="obj"):
            head = sent.head_of(obj)
            if head is None or head.upos != "VERB":
                continue
            head_line = line_map.get((sent.sent_id, head.id))
            obj_line = line_map.get((sent.sent_id, obj.id))
            if head_line is None or obj_line is None:
                continue
            # Violation: obj on a later line than its governing VERB.
            # Skip large gaps (> 3 lines) — likely parse-graph noise rather
            # than a real V+DO split.
            gap = obj_line - head_line
            if gap <= 0 or gap > 3:
                continue
            violations.append({
                "book": book_id,
                "sent_id": sent.sent_id,
                "head_form": head.form,
                "head_lemma": head.lemma,
                "obj_form": obj.form,
                "head_line": head_line,
                "obj_line": obj_line,
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
    print("Rule 10 UD-query — V+DO split (BofM corpus)")
    print("=" * 72)
    print(f"Books scanned: {len(book_ids)}")
    print(f"STRONG-MERGE-CANDIDATE: {len(all_violations)}")
    print()

    for v in all_violations[:20]:
        print(f"  [{v['book']}] sent={v['sent_id']} "
              f"VERB {v['head_form']!r} (line {v['head_line']}) -> "
              f"obj {v['obj_form']!r} (line {v['obj_line']})")
    if len(all_violations) > 20:
        print(f"  ... +{len(all_violations) - 20} more")

    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
