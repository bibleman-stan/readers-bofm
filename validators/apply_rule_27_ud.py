"""
Apply Rule 27 STRONG-SPLIT-CANDIDATE findings — split before 'insomuch that'.

Re-runs the detector internally for fresh line numbers.

Usage:
    python validators/apply_rule_27_ud.py            # dry-run
    python validators/apply_rule_27_ud.py --apply    # write
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from validators.colometry.validate_rule_27_ud import scan_book, BOOKS  # noqa: E402


# Match "insomuch that" with optional comma between
INSOMUCH_THAT_PATTERN = re.compile(r"\binsomuch\b\s*(?:,\s*)?that\b", re.IGNORECASE)


def find_split_position(line: str) -> int | None:
    """Find char index where 'insomuch that' begins."""
    matches = list(INSOMUCH_THAT_PATTERN.finditer(line))
    if len(matches) != 1:
        return None
    return matches[0].start()


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
            if f.get("bucket") != "STRONG-SPLIT-CANDIDATE":
                continue
            total_strong += 1
            from validators.parsing.line_mapping import book_paths
            v2_path, _ = book_paths(book_id)

            # Detector tracks where the merged line is — use the matrix line
            # (which contains insomuch+that+result-clause when merged).
            line_num = f.get("matrix_line") or f.get("line") or f.get("insomuch_line")
            if line_num is None:
                skipped.append((book_id, 0, "no-line-in-finding"))
                continue
            line_idx = line_num - 1

            with open(v2_path, encoding="utf-8") as fh:
                lines = fh.read().split("\n")
            if line_idx < 0 or line_idx >= len(lines):
                skipped.append((book_id, line_num, "out-of-range"))
                continue
            line = lines[line_idx]
            split_at = find_split_position(line)
            if split_at is None:
                skipped.append((book_id, line_num, "no-insomuch-that-on-line"))
                continue
            by_file.setdefault(v2_path, []).append((line_idx, split_at))

    plan_count = sum(len(items) for items in by_file.values())
    print(f"Rule 27 STRONG-SPLIT detected: {total_strong}")
    print(f"Plannable splits:              {plan_count}")
    print(f"Skipped:                       {len(skipped)}")
    if skipped:
        print()
        for s in skipped[:10]:
            print(f"  {s}")
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
    print(f"\nTotal Rule 27 splits applied: {total_applied}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
