"""
Apply Rule 28 STRONG-SPLIT-CANDIDATE findings to v2-mine.

Splits the speech-act announcement off the advcl frame line so the matrix
clause (subject + speech verb + colon-introduced quote) gets its own line.

T1.1 char-offset: detector emits split_col directly via build_line_map_full.
The applier inserts a line break BEFORE split_col so the trailing comma (if
any) stays on the frame line.

Usage:
    python validators/apply_rule_28_ud.py            # dry-run
    python validators/apply_rule_28_ud.py --apply    # write

Each --apply run writes a transaction log to validators/.tx/ so the changes
can be reversed in 30 seconds:

    python validators/rollback.py --latest
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from validators.colometry.validate_rule_28_ud import scan_book, BOOKS  # noqa: E402
from validators.tx_log import TxLog  # noqa: E402


def main() -> int:
    apply_mode = "--apply" in sys.argv
    by_file: dict[Path, list[tuple[int, int]]] = {}
    skipped: list[tuple[str, int, str]] = []

    total_strong = 0
    for book_id in BOOKS:
        try:
            _, strong = scan_book(book_id)
        except FileNotFoundError:
            continue
        total_strong += len(strong)
        for v in strong:
            v2_path = Path(v["v2_path"])
            line_idx = v["verb_line"] - 1
            split_col = v.get("split_col")

            if split_col is None:
                skipped.append(
                    (book_id, v["verb_line"], "no-split-col-from-detector")
                )
                continue
            if split_col == 0:
                skipped.append(
                    (book_id, v["verb_line"], "split-col-0-defensive-skip")
                )
                continue

            by_file.setdefault(v2_path, []).append((line_idx, split_col))

    plan_count = sum(len(items) for items in by_file.values())
    print(f"Rule 28 STRONG-SPLIT detected: {total_strong}")
    print(f"Plannable splits:              {plan_count}")
    print(f"Skipped:                       {len(skipped)}")
    if skipped:
        print()
        for s in skipped[:15]:
            print(f"  {s}")
        if len(skipped) > 15:
            print(f"  ... +{len(skipped) - 15} more")
    print()

    if not apply_mode:
        for v2_path, items in by_file.items():
            print(f"--- {v2_path.name} ({len(items)} planned) ---")
            with open(v2_path, encoding="utf-8") as fh:
                lines = fh.read().split("\n")
            for line_idx, split_at in sorted(items)[:3]:
                line = lines[line_idx]
                left = line[:split_at].rstrip()
                right = line[split_at:].lstrip()
                print(f"  line {line_idx + 1}: split @ pos {split_at}")
                print(f"    -> {left[-60:] if len(left) > 60 else left!r}")
                print(f"    -> {right[:60]!r}")
        print("\n(dry run -- pass --apply to write)")
        return 0

    tx = TxLog("rule_28")
    total_applied = 0
    for v2_path, items in by_file.items():
        with open(v2_path, encoding="utf-8") as fh:
            content = fh.read()
        lines = content.split("\n")
        unique_items = sorted(set(items), key=lambda x: (x[0], x[1]), reverse=True)
        for line_idx, split_at in unique_items:
            if line_idx >= len(lines):
                continue
            line = lines[line_idx]
            if split_at >= len(line):
                continue
            left = line[:split_at].rstrip()
            right = line[split_at:].lstrip()
            tx.record_split(str(v2_path), line_idx, line, left, right)
            lines[line_idx] = left
            lines.insert(line_idx + 1, right)
            total_applied += 1
        with open(v2_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        print(f"  {v2_path.name}: {len(unique_items)} splits applied")
    print(f"\nTotal Rule 28 splits applied: {total_applied}")

    if total_applied:
        tx_path = tx.commit()
        print(f"\nTransaction log: {tx_path}")
        print("To undo: python validators/rollback.py --latest")

    return 0


if __name__ == "__main__":
    sys.exit(main())
