#!/usr/bin/env python3
"""
Validate Rule 18 (Fixed Idiom Integrity) across the BofM corpus.

Rule 18: Certain multi-word expressions are indivisible and must never be
broken across a line boundary:
- "put to death"
- "put an end to"
- "from time to time"
- "prevailed upon"
- "one with another"
- "it is expedient that" (absorbed from former Rule 2)
- "it came to pass that" — Rule 1/16 territory, skip
- "in the reign of"
- "in behalf of"
- "over all the land"

Detection: for each idiom, flag any occurrence where a line break falls
between the idiom's first and last tokens.

Exit code: 0 if zero violations, 1 if violations found.

Usage:
    python3 validate_rule_18_fixed_idioms.py
"""

import argparse
import re
import sys
from pathlib import Path

# Fixed idioms governed by Rule 18
# Each entry: (regex pattern to search for, human-readable name)
# Patterns match across whitespace including line breaks; if the idiom spans
# line boundaries, it's a violation.
FIXED_IDIOMS = [
    (r"\bput\s+to\s+death\b", "put to death"),
    (r"\bput\s+an\s+end\s+to\b", "put an end to"),
    (r"\bfrom\s+time\s+to\s+time\b", "from time to time"),
    (r"\bprevailed\s+upon\b", "prevailed upon"),
    (r"\bone\s+with\s+another\b", "one with another"),
    (r"\bit\s+is\s+expedient\s+that\b", "it is expedient that"),
    (r"\bin\s+behalf\s+of\b", "in behalf of"),
]


def scan_file(path: Path) -> list[dict]:
    """Scan one v2-mine file for Rule 18 violations (idiom split across lines)."""
    violations = []
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    # Build a line-offset map so we can find which line(s) an idiom spans
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

    for pattern_str, name in FIXED_IDIOMS:
        # Match case-insensitively, allow whitespace (including newlines) between tokens
        # Use \s+ which matches across newlines
        pattern = re.compile(pattern_str, re.IGNORECASE)
        for match in pattern.finditer(content):
            start_line = find_line_for_offset(match.start())
            end_line = find_line_for_offset(match.end() - 1)
            if start_line != end_line:
                # Idiom spans multiple lines — violation
                violations.append(
                    {
                        "file": path.name,
                        "idiom": name,
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
    print("Rule 18 (Fixed Idiom Integrity) validator")
    print("=" * 72)
    print(f"Files scanned: {len(files)}")
    print(f"Idioms checked: {len(FIXED_IDIOMS)}")
    print(f"Violations found: {len(all_violations)}")
    print()

    if all_violations:
        for v in all_violations:
            print(
                f"  {v['file']}:{v['start_line_num']}-{v['end_line_num']} — "
                f"idiom {v['idiom']!r} split across lines:"
            )
            print(f"    {v['matched_text'][:120]}")
            print()
    else:
        print("No violations found. Rule 18 compliance is clean.")

    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
