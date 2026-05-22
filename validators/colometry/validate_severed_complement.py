#!/usr/bin/env python3
"""
Validate severed complement-spanning-frame patterns across the BofM corpus.

Pattern (Alma 30:18 type):
  Line N:   [V-ing | speech-verb] them that [WHEN|AFTER|BEFORE|AS|...] ...,
  Line N+1: [matrix predication starting with subject pronoun OR demonstrative]

The complementizer 'that' belongs to a speech/cognition governor on line N;
inside its complement, a temporal/conditional frame is followed by a matrix
predication that has been split onto line N+1. Per Rule 17 + M3 + frame+matrix
one-proposition, the body should rejoin the governor.

Paired applier: validators/apply_severed_complement.py

Exit code: 0 if no violations, 1 if violations found.

Usage:
    python3 validate_severed_complement.py
    python3 validate_severed_complement.py --verbose
"""

import argparse
import re
import sys
from pathlib import Path


SEVERED_COMP_RE = re.compile(
    r'\bthat\s+(when|after|before|as|while|until|if|because|since|though|although)\b'
    r'.*,\s*$',
    re.IGNORECASE
)

PRED_LEAD_RE = re.compile(
    r'^(?:'
    r'there (?:was|were|came|arose|did|stood|appeared|shall|will|is|are|hath|have)'
    r'|that (?:was|were|is|are|shall|will|hath|have)'
    r'|this (?:was|were|is|are|shall|will|hath|have)'
    r'|(?:he|she|they|it|we|I|ye|thou)\b'
    r'|(?:the )?(?:people|Lord|king|Lamanites|Nephites|land|words?|brethren|'
    r'priests?|servants?|men|man|woman|earth|spirit|voice|prophets?|whole)\b'
    r')',
    re.IGNORECASE
)


def is_verse_number(line: str) -> bool:
    return bool(re.match(r"^\s*\d+:\d+\s*$", line))


def scan_file(path: Path, verbose: bool = False):
    violations = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for i in range(len(lines) - 1):
        cur = lines[i].strip()
        nxt = lines[i + 1].strip()
        if not cur or not nxt or is_verse_number(cur) or is_verse_number(nxt):
            continue
        if not SEVERED_COMP_RE.search(cur):
            continue
        if not PRED_LEAD_RE.match(nxt):
            continue
        violations.append({
            "file": path.name,
            "line_num": i + 1,
            "cur": cur,
            "nxt": nxt,
        })
        if verbose:
            print(f"[DEVIATION] {path.name}:{i+1}")
            print(f"    cur: {cur[:90]}")
            print(f"    nxt: {nxt[:90]}")
    return violations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument(
        "--v2-dir",
        default="c:/Users/bibleman/repos/readers-bofm/data/text-files/v2",
    )
    args = parser.parse_args()

    v2_dir = Path(args.v2_dir)
    if not v2_dir.exists():
        print(f"ERROR: {v2_dir} not found", file=sys.stderr)
        sys.exit(2)

    all_violations = []
    files = sorted(v2_dir.glob("*-v2.txt"))
    for path in files:
        all_violations.extend(scan_file(path, verbose=args.verbose))

    print()
    print("Severed complement-spanning-frame — BofM v2-mine corpus")
    print("=" * 72)
    print(f"Files scanned: {len(files)}")
    print(f"violations found: {len(all_violations)}")
    print()

    if all_violations and not args.verbose:
        print("Sample (first 10):")
        for v in all_violations[:10]:
            print(f"  [{v['file']}:{v['line_num']}]")
            print(f"    cur: {v['cur'][:90]}")
            print(f"    nxt: {v['nxt'][:90]}")

    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
