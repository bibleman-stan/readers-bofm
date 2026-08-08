"""Rollback corpus changes recorded by a TxLog transaction file.

Processes entries in REVERSE order (newest-first) so that line-index
offsets introduced by earlier splits/merges are correctly unwound.

For each entry:
  split  → verify line_idx == after_left AND line_idx+1 == after_right,
            then merge them back to `before`.
  merge  → verify line_idx == after,
            then split back into before_a and before_b.

If the current on-disk state doesn't match what the log recorded, the
entry is skipped with a warning — it was likely already reversed or was
never applied.  The rest of the rollback continues.

Usage:
    python 5-machinery/validators/rollback.py --list                     # all tx files
    python 5-machinery/validators/rollback.py --latest                   # newest tx
    python 5-machinery/validators/rollback.py --tx <path-to-json>        # specific tx
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
TX_DIR = REPO / "5-machinery" / "validators" / ".tx"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _load_tx(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _tx_files() -> list[Path]:
    if not TX_DIR.exists():
        return []
    return sorted(TX_DIR.glob("*.json"))


# ---------------------------------------------------------------------------
# rollback engine
# ---------------------------------------------------------------------------


def rollback_tx(tx_path: Path) -> int:
    """Apply a single transaction file in reverse.  Returns exit code."""
    if not tx_path.exists():
        print(f"ERROR: tx file not found: {tx_path}", file=sys.stderr)
        return 1

    data = _load_tx(tx_path)
    rule = data.get("rule", "?")
    ts = data.get("timestamp", "?")
    entries = data.get("entries", [])

    print(f"Rolling back {rule} @ {ts}  ({len(entries)} entries)")
    print(f"  tx file: {tx_path}")
    print()

    if not entries:
        print("No entries — nothing to do.")
        return 0

    # Group entries by file so we can do a single read/write per file.
    # We must process files in the same order as the original apply pass,
    # but the entries list is already in application order.  Reversing the
    # full list naturally reverses both the within-file order and the
    # cross-file order.
    reversed_entries = list(reversed(entries))

    # Bucket by file path (preserving reversed order within each file)
    by_file: dict[str, list[dict]] = {}
    for entry in reversed_entries:
        by_file.setdefault(entry["file"], []).append(entry)

    total_applied = 0
    total_skipped = 0

    for file_str, file_entries in by_file.items():
        file_path = Path(file_str)
        if not file_path.exists():
            print(f"  SKIP file not found: {file_str}")
            total_skipped += len(file_entries)
            continue

        with open(file_path, encoding="utf-8") as f:
            lines = f.read().split("\n")

        applied_in_file = 0
        skipped_in_file = 0

        for entry in file_entries:
            action = entry["action"]
            idx = entry["line_idx"]  # 0-based

            if action == "split":
                # Verify: line_idx → after_left, line_idx+1 → after_right
                expected_left = entry["after_left"]
                expected_right = entry["after_right"]
                before = entry["before"]

                if idx >= len(lines) or idx + 1 >= len(lines):
                    print(
                        f"  SKIP split @ {file_path.name}:{idx + 1} "
                        f"— index out of range (file has {len(lines)} lines)"
                    )
                    skipped_in_file += 1
                    continue

                current_left = lines[idx]
                current_right = lines[idx + 1]

                if current_left != expected_left or current_right != expected_right:
                    print(
                        f"  SKIP split @ {file_path.name}:{idx + 1} "
                        f"— current state does not match tx record\n"
                        f"      expected left : {expected_left!r}\n"
                        f"      found left    : {current_left!r}\n"
                        f"      expected right: {expected_right!r}\n"
                        f"      found right   : {current_right!r}"
                    )
                    skipped_in_file += 1
                    continue

                # Reverse: merge the two lines back into the original
                lines[idx] = before
                del lines[idx + 1]
                applied_in_file += 1

            elif action == "merge":
                # Verify: line_idx → after
                expected_after = entry["after"]
                before_a = entry["before_a"]
                before_b = entry["before_b"]

                if idx >= len(lines):
                    print(
                        f"  SKIP merge @ {file_path.name}:{idx + 1} "
                        f"— index out of range"
                    )
                    skipped_in_file += 1
                    continue

                current = lines[idx]
                if current != expected_after:
                    print(
                        f"  SKIP merge @ {file_path.name}:{idx + 1} "
                        f"— current state does not match tx record\n"
                        f"      expected: {expected_after!r}\n"
                        f"      found   : {current!r}"
                    )
                    skipped_in_file += 1
                    continue

                # Reverse: split the merged line back into two originals
                lines[idx] = before_a
                lines.insert(idx + 1, before_b)
                applied_in_file += 1

            else:
                print(f"  SKIP unknown action {action!r} @ {file_path.name}:{idx + 1}")
                skipped_in_file += 1
                continue

        if applied_in_file or skipped_in_file:
            status = f"{applied_in_file} reversed"
            if skipped_in_file:
                status += f", {skipped_in_file} skipped"
            print(f"  {file_path.name}: {status}")

        if applied_in_file:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

        total_applied += applied_in_file
        total_skipped += skipped_in_file

    print()
    print(f"Rollback complete: {total_applied} reversed, {total_skipped} skipped")
    return 0 if total_skipped == 0 else 2  # 2 = partial rollback


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    args = sys.argv[1:]

    if not args or "--help" in args or "-h" in args:
        print(__doc__)
        return 0

    if "--list" in args:
        files = _tx_files()
        if not files:
            print("No transaction files found in", TX_DIR)
            return 0
        print(f"Transaction files in {TX_DIR}:")
        for p in files:
            data = _load_tx(p)
            n = len(data.get("entries", []))
            print(f"  {p.name}  ({n} entries)")
        return 0

    if "--latest" in args:
        files = _tx_files()
        if not files:
            print("No transaction files found.", file=sys.stderr)
            return 1
        tx_path = files[-1]
        return rollback_tx(tx_path)

    if "--tx" in args:
        idx = args.index("--tx")
        if idx + 1 >= len(args):
            print("ERROR: --tx requires a file path", file=sys.stderr)
            return 1
        tx_path = Path(args[idx + 1])
        return rollback_tx(tx_path)

    print(f"Unknown arguments: {args}", file=sys.stderr)
    print("Use --list, --latest, or --tx <path>", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
