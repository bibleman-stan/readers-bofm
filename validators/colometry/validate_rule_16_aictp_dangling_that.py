#!/usr/bin/env python3
"""
Validate Rule 16 (Dangling "that" after AICTP) across the BofM corpus.

Rule 16: After an AICTP formula ("And it came to pass"), the "that" clause
earns its own line. The "that" must LEAD the next line, not dangle at the
end of the AICTP line.

Violation: line ends with "And (now) it (came|shall come|had come) to pass
that," (or similar) instead of cleanly terminating at "to pass," with "that"
leading the next line.

Exit code: 0 if zero violations, 1 if violations found.

Usage:
    python3 validate_rule_16_aictp_dangling_that.py
"""

import argparse
import re
import sys
from pathlib import Path

# AICTP pattern — matches the full formula including variants
AICTP_PATTERN = re.compile(
    r"\b(?:And\s+(?:now\s+)?)?it\s+(?:came|shall come|had come|will come)\s+to\s+pass\b",
    re.IGNORECASE,
)

# Dangling "that" at AICTP line end — violation
AICTP_DANGLING_THAT = re.compile(
    r"\bto\s+pass\s+that\s*[,.;:]?\s*$",
    re.IGNORECASE,
)

# Line begins with "that " (not "that which" or similar relative/demonstrative)
NEXT_LINE_THAT = re.compile(r"^that\s+(?!which\b)", re.IGNORECASE)


def scan_file(path: Path) -> list[dict]:
    """Scan one v2-mine file for Rule 16 violations."""
    violations = []
    lines = path.read_text(encoding="utf-8").splitlines()

    for i, line in enumerate(lines):
        if not line.strip() or re.match(r"^\d+:\d+$", line.strip()):
            continue

        # Check: does this line have AICTP AND end with dangling "that"?
        if AICTP_DANGLING_THAT.search(line):
            violations.append(
                {
                    "file": path.name,
                    "line_num": i + 1,
                    "pattern": "AICTP + dangling 'that' at line end",
                    "line": line.rstrip(),
                    "next_line": lines[i + 1].rstrip() if i + 1 < len(lines) else "",
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
    print("Rule 16 (Dangling 'that' after AICTP) validator")
    print("=" * 72)
    print(f"Files scanned: {len(files)}")
    print(f"Violations found: {len(all_violations)}")
    print()

    if all_violations:
        for v in all_violations:
            print(f"[DEVIATION]  {v['file']}:{v['line_num']} — {v['pattern']}")
            print(f"    {v['line'][:100]}")
            if v["next_line"]:
                print(f"    {v['next_line'][:100]}")
            print()
    else:
        print("No violations found. Rule 16 compliance is clean.")

    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
