#!/usr/bin/env python3
"""
Validate Rule 23 (Date/Colophon Formula Integrity) across the BofM corpus.

Rule 23: Editorial timestamps and colophon formulas are bureaucratic —
they always stay on one line. Do not break:
- "in the Nth year of the reign of the judges"
- "in the Nth year of the reign of king X"
- "in the Nth year since..." (since-clause formulas)
- Book/chapter colophons if any

Detection: look for date/colophon regex patterns that span line boundaries.

Exit code: 0 if zero violations, 1 if violations found.

Usage:
    python3 validate_rule_23_date_colophon.py
"""

import argparse
import re
import sys
from pathlib import Path

# Date/colophon formula patterns — these should always appear on a single line
# Pattern uses \s+ which matches newlines; if match crosses line boundary, violation
DATE_PATTERNS = [
    (
        r"\bin\s+the\s+(?:\w+\s+)?(?:and\s+)?(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|\w+(?:teen|ty)?)\s+year\s+of\s+the\s+reign\s+of\s+the\s+judges\b",
        "reign-of-the-judges formula",
    ),
    (
        r"\bin\s+the\s+(?:\w+\s+)?(?:and\s+)?(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|\w+(?:teen|ty)?)\s+year\s+of\s+the\s+reign\s+of\s+king\b",
        "reign-of-king formula",
    ),
    (
        r"\bin\s+the\s+(?:\w+\s+)?(?:and\s+)?(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|\w+(?:teen|ty)?)\s+year\s+since\s+Lehi\b",
        "year-since-Lehi formula",
    ),
]


def scan_file(path: Path) -> list[dict]:
    """Scan one v2-mine file for Rule 23 violations (date formula split across lines)."""
    violations = []
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    offsets = []
    pos = 0
    for i, line in enumerate(lines):
        offsets.append((i, pos, pos + len(line)))
        pos += len(line)

    def find_line_for_offset(offset: int) -> int:
        for i, start, end in offsets:
            if start <= offset < end:
                return i
        return -1

    for pattern_str, name in DATE_PATTERNS:
        pattern = re.compile(pattern_str, re.IGNORECASE)
        for match in pattern.finditer(content):
            start_line = find_line_for_offset(match.start())
            end_line = find_line_for_offset(match.end() - 1)
            if start_line != end_line:
                violations.append(
                    {
                        "file": path.name,
                        "formula": name,
                        "start_line_num": start_line + 1,
                        "end_line_num": end_line + 1,
                        "matched_text": match.group(0).replace("\n", " / ").strip(),
                    }
                )

    return violations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--v2-dir",
        default="c:/Users/bibleman/repos/readers-bofm/data/text-files/v2-mine",
    )
    args = parser.parse_args()

    v2_dir = Path(args.v2_dir)
    if not v2_dir.exists():
        print(f"ERROR: {v2_dir} not found", file=sys.stderr)
        sys.exit(2)

    all_violations = []
    files = sorted(v2_dir.glob("*-v2.txt"))
    for path in files:
        violations = scan_file(path)
        all_violations.extend(violations)

    print("=" * 72)
    print("Rule 23 (Date/Colophon Formula Integrity) validator")
    print("=" * 72)
    print(f"Files scanned: {len(files)}")
    print(f"Formula patterns checked: {len(DATE_PATTERNS)}")
    print(f"Violations found: {len(all_violations)}")
    print()

    if all_violations:
        for v in all_violations:
            print(
                f"[DEVIATION]  {v['file']}:{v['start_line_num']}-{v['end_line_num']} — "
                f"{v['formula']} split:"
            )
            print(f"    {v['matched_text'][:120]}")
            print()
    else:
        print("No violations found. Rule 23 compliance is clean.")

    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
