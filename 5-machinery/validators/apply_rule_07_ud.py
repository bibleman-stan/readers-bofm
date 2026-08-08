"""
Apply Rule 7 STRONG-SPLIT-CANDIDATE findings to v2-mine.

T1.1 (2026-05-10): uses char-offset positions emitted directly by the
detector via build_line_map_full. No more regex-position-finder ambiguity —
the 18 previously-skipped "ambiguous-that-<modal>" cases now resolve because
the detector distinguishes tokens by id, not surface form.

Re-runs the detector internally for fresh line numbers (corpus may have
shifted from earlier appliers in the same session).

Usage:
    python 5-machinery/validators/apply_rule_07_ud.py            # dry-run
    python 5-machinery/validators/apply_rule_07_ud.py --apply    # write

Each --apply run writes a transaction log to 5-machinery/validators/.tx/ so the changes
can be reversed in 30 seconds if a pre-commit regression check fires:

    python 5-machinery/validators/rollback.py --latest
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from validators.colometry.validate_rule_07_ud import scan_book, BOOKS  # noqa: E402
from validators.tx_log import TxLog  # noqa: E402


def main() -> int:
    apply_mode = "--apply" in sys.argv
    by_file: dict[Path, list[tuple[int, int]]] = {}
    skipped: list[tuple[str, int, str]] = []

    total_strong = 0
    for book_id in BOOKS:
        try:
            strong, _ = scan_book(book_id)
        except FileNotFoundError:
            continue
        total_strong += len(strong)
        for v in strong:
            v2_path = Path(v["v2_path"])
            line_idx = v["line"] - 1
            split_col = v.get("split_col")

            if split_col is None:
                skipped.append(
                    (book_id, v["line"], "no-split-col-from-detector")
                )
                continue
            if split_col == 0:
                # Already at line-start; no break needed (defensive)
                skipped.append(
                    (book_id, v["line"], "split-col-0-already-at-start")
                )
                continue

            with open(v2_path, encoding="utf-8") as fh:
                lines = fh.read().split("\n")
            if line_idx < 0 or line_idx >= len(lines):
                skipped.append((book_id, v["line"], "out-of-range"))
                continue

            # Defensive: verify the split position actually starts "that"
            # (guards against duplicate-token-id parse artifacts where
            # line_map_full maps the wrong homonym token).
            line_text = lines[line_idx]
            if not line_text[split_col:split_col + 4].lower() == "that":
                skipped.append(
                    (book_id, v["line"], f"split-col-{split_col}-not-that-token")
                )
                continue

            by_file.setdefault(v2_path, []).append((line_idx, split_col))

    plan_count = sum(len(items) for items in by_file.values())
    print(f"Rule 7 STRONG-SPLIT detected: {total_strong}")
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

    tx = TxLog("rule_07")
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
    print(f"\nTotal Rule 7 splits applied: {total_applied}")

    if total_applied:
        tx_path = tx.commit()
        print(f"\nTransaction log: {tx_path}")
        print("To undo: python 5-machinery/validators/rollback.py --latest")

    return 0


if __name__ == "__main__":
    sys.exit(main())
