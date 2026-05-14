"""
Apply Rule 7 SCOPE-merge findings (motion-verb + infinitival purpose) to v2-mine.

For each STRONG-MERGE-CANDIDATE: matrix motion-VERB on line N, mark='to'
on line N+1. Merge by joining the two lines.

Re-runs the detector internally to get fresh line numbers.

Usage:
    python validators/apply_rule_07_inf_merge_ud.py            # dry-run
    python validators/apply_rule_07_inf_merge_ud.py --apply    # write
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from validators.colometry.validate_rule_07_inf_merge_ud import scan_book, BOOKS  # noqa: E402
from validators.tx_log import TxLog  # noqa: E402


def main() -> int:
    apply_mode = "--apply" in sys.argv
    by_file: dict[Path, list[int]] = {}
    skipped: list[tuple[str, int, str]] = []

    total_strong = 0
    for book_id in BOOKS:
        try:
            vs = scan_book(book_id)
        except FileNotFoundError:
            continue
        for v in vs:
            if v["bucket"] != "STRONG-MERGE-CANDIDATE":
                continue
            total_strong += 1
            v2_path = Path(v["v2_path"])
            head_idx = v["head_line"] - 1
            mark_idx = v["mark_line"] - 1
            if mark_idx != head_idx + 1:
                skipped.append((book_id, v["head_line"], "non-adjacent-gap"))
                continue
            by_file.setdefault(v2_path, []).append(head_idx)

    plan_count = sum(len(set(items)) for items in by_file.values())
    print(f"Rule 7 SCOPE-merge STRONG detected: {total_strong}")
    print(f"Plannable merges (gap=1):           {plan_count}")
    print(f"Skipped:                            {len(skipped)}")
    print()

    if not apply_mode:
        for v2_path, items in by_file.items():
            print(f"\n--- {v2_path.name} ({len(set(items))} planned) ---")
            with open(v2_path, encoding="utf-8") as f:
                lines = f.read().split("\n")
            for line_idx in sorted(set(items))[:3]:
                if line_idx + 1 >= len(lines):
                    continue
                a = lines[line_idx].rstrip()
                b = lines[line_idx + 1].lstrip()
                print(f"  line {line_idx + 1}+{line_idx + 2}: merge")
                print(f"    cur: {a[-60:] if len(a) > 60 else a!r}")
                print(f"    nxt: {b[:60]!r}")
        print("\n(dry run — pass --apply to write)")
        return 0

    tx = TxLog("rule_07_inf_merge")
    total_applied = 0
    for v2_path, items in by_file.items():
        with open(v2_path, encoding="utf-8") as f:
            content = f.read()
        lines = content.split("\n")
        for line_idx in sorted(set(items), reverse=True):
            if line_idx + 1 >= len(lines):
                continue
            a = lines[line_idx].rstrip()
            b = lines[line_idx + 1].strip()
            merged = a + " " + b
            tx.record_merge(str(v2_path), line_idx, lines[line_idx], lines[line_idx + 1], merged)
            lines[line_idx] = merged
            del lines[line_idx + 1]
            total_applied += 1
        with open(v2_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"  {v2_path.name}: {len(set(items))} merges applied")
    print(f"\nTotal Rule 7 SCOPE-merge merges applied: {total_applied}")

    if total_applied:
        tx_path = tx.commit()
        print(f"\nTransaction log: {tx_path}")
        print("To undo: python validators/rollback.py --latest")

    return 0


if __name__ == "__main__":
    sys.exit(main())
