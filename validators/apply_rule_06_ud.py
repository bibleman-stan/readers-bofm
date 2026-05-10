"""
Apply Rule 6 STRONG-SPLIT-CANDIDATE findings — split before 'because'.

T1.1 (2026-05-10): uses char-offset positions emitted directly by the
detector via build_line_map_full. No more regex-position-finder ambiguity —
the detector knows the exact column where 'because' starts; the applier
splits before that column.

Re-runs the detector internally for fresh line numbers.

Usage:
    python validators/apply_rule_06_ud.py            # dry-run
    python validators/apply_rule_06_ud.py --apply    # write

Each --apply run writes a transaction log to validators/.tx/ so the changes
can be reversed in 30 seconds if a pre-commit regression check fires:

    python validators/rollback.py --latest
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from validators.colometry.validate_rule_06_ud import scan_book, BOOKS  # noqa: E402
from validators.tx_log import TxLog  # noqa: E402


def main() -> int:
    apply_mode = "--apply" in sys.argv
    by_file: dict[Path, list[tuple[int, int]]] = {}
    skipped: list[tuple[str, int, str]] = []

    total_strong = 0
    for book_id in BOOKS:
        try:
            findings = scan_book(book_id)
        except FileNotFoundError:
            continue
        for f in findings:
            if f["bucket"] != "STRONG-SPLIT-CANDIDATE":
                continue
            total_strong += 1
            v2_path = Path(f["v2_path"])
            line_idx = f["matrix_line"] - 1
            split_col = f.get("split_col")

            if split_col is None:
                skipped.append(
                    (book_id, f["matrix_line"], "no-split-col-from-detector")
                )
                continue
            if split_col == 0:
                # Already at line-start; no break needed (defensive)
                skipped.append(
                    (book_id, f["matrix_line"], "split-col-0-already-at-start")
                )
                continue

            with open(v2_path, encoding="utf-8") as fh:
                lines = fh.read().split("\n")
            if line_idx < 0 or line_idx >= len(lines):
                skipped.append((book_id, f["matrix_line"], "out-of-range"))
                continue

            # Defensive: verify the split position actually starts "because"
            # (guards against duplicate-token-id parse artifacts).
            line_text = lines[line_idx]
            if not line_text[split_col:split_col + 7].lower() == "because":
                skipped.append(
                    (book_id, f["matrix_line"], f"split-col-{split_col}-not-because-token")
                )
                continue

            by_file.setdefault(v2_path, []).append((line_idx, split_col))

    plan_count = sum(len(items) for items in by_file.values())
    print(f"Rule 6 STRONG-SPLIT detected: {total_strong}")
    print(f"Plannable splits:             {plan_count}")
    print(f"Skipped:                      {len(skipped)}")
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
        print("\n(dry run — pass --apply to write)")
        return 0

    tx = TxLog("rule_06")
    total_applied = 0
    for v2_path, items in by_file.items():
        with open(v2_path, encoding="utf-8") as fh:
            content = fh.read()
        lines = content.split("\n")
        # Apply in reverse line order; dedupe in case of repeats per line
        unique_items = sorted(set(items), key=lambda x: (x[0], x[1]), reverse=True)
        for line_idx, split_at in unique_items:
            if line_idx >= len(lines):
                continue
            line = lines[line_idx]
            if split_at >= len(line):
                continue
            left = line[:split_at].rstrip()
            right = line[split_at:].lstrip()
            # Record BEFORE the mutation so indices are still valid
            tx.record_split(str(v2_path), line_idx, line, left, right)
            lines[line_idx] = left
            lines.insert(line_idx + 1, right)
            total_applied += 1
        with open(v2_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        print(f"  {v2_path.name}: {len(unique_items)} splits applied")
    print(f"\nTotal Rule 6 splits applied: {total_applied}")

    if total_applied:
        tx_path = tx.commit()
        print(f"\nTransaction log: {tx_path}")
        print("To undo: python validators/rollback.py --latest")

    return 0


if __name__ == "__main__":
    sys.exit(main())
