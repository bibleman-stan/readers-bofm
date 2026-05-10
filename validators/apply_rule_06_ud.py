"""
Apply Rule 6 STRONG-SPLIT-CANDIDATE findings — split before 'because'.

Re-runs the detector internally for fresh line numbers.

Usage:
    python validators/apply_rule_06_ud.py            # dry-run
    python validators/apply_rule_06_ud.py --apply    # write
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from validators.colometry.validate_rule_06_ud import scan_book, BOOKS  # noqa: E402


BECAUSE_PATTERN = re.compile(r"\bbecause\b", re.IGNORECASE)


def find_split_position(line: str) -> int | None:
    """Find char index where 'because' begins. Detector has already filtered
    fronted-because and 'because of NP', so the remaining 'because' on the
    line is the matrix-trailing causal mark."""
    matches = list(BECAUSE_PATTERN.finditer(line))
    if not matches:
        return None
    # Take the LAST "because" — fronted-becauses are filtered upstream, but if
    # the line happens to contain multiple, the trailing matrix-because is
    # the right split point.
    return matches[-1].start()


def main() -> int:
    apply_mode = "--apply" in sys.argv
    by_file: dict[Path, list[int]] = {}
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
            v2_path = Path(f.get("v2_path", "")) if f.get("v2_path") else None
            if v2_path is None:
                # scan_book doesn't set v2_path; resolve via book_paths
                from validators.parsing.line_mapping import book_paths
                v2_path, _ = book_paths(book_id)
            line_idx = f["matrix_line"] - 1
            with open(v2_path, encoding="utf-8") as fh:
                lines = fh.read().split("\n")
            if line_idx < 0 or line_idx >= len(lines):
                skipped.append((book_id, f["matrix_line"], "out-of-range"))
                continue
            line = lines[line_idx]
            split_at = find_split_position(line)
            if split_at is None:
                skipped.append((book_id, f["matrix_line"], "no-because-on-line"))
                continue
            by_file.setdefault(v2_path, []).append((line_idx, split_at))

    plan_count = sum(len(items) for items in by_file.values())
    print(f"Rule 6 STRONG-SPLIT detected: {total_strong}")
    print(f"Plannable splits:             {plan_count}")
    print(f"Skipped:                      {len(skipped)}")
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

    total_applied = 0
    for v2_path, items in by_file.items():
        with open(v2_path, encoding="utf-8") as fh:
            content = fh.read()
        lines = content.split("\n")
        for line_idx, split_at in sorted(items, key=lambda x: x[0], reverse=True):
            line = lines[line_idx]
            left = line[:split_at].rstrip()
            right = line[split_at:].lstrip()
            lines[line_idx] = left
            lines.insert(line_idx + 1, right)
            total_applied += 1
        with open(v2_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        print(f"  {v2_path.name}: {len(items)} splits applied")
    print(f"\nTotal Rule 6 splits applied: {total_applied}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
