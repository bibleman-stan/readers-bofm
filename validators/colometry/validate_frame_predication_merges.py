#!/usr/bin/env python3
"""
Validate frame+predication merge candidates across the BofM corpus.

Pattern: AICTP/temporal-frame line (ends with comma, no own finite predication
beyond the frame) immediately followed by a matrix-predication line. The two
are one proposition per §1 generative principle + M4 fragmented-ATU.

Distinct from Rule 28 (validate_rule_28_speech_act_after_frame.py): Rule 28
catches frame + colon-terminated speech tag specifically. This validator
catches the broader frame+matrix one-proposition pattern (any predication-
lead, not just speech tags).

Length cap: 130c. Anything over is flagged but applier skips it for editorial
review (frame+predication validator still reports it as deviation).

Paired applier: validators/apply_frame_merges.py

Exit code: 0 if no violations, 1 if violations found.

Usage:
    python3 validate_frame_predication_merges.py
    python3 validate_frame_predication_merges.py --verbose
"""

import argparse
import re
import sys
from pathlib import Path


FRAME_LINE_RE = re.compile(
    r'^(?:And |But |Now |Then |And now |But now |Yea, |For )?'
    r'(?:it came to pass|in the days|after\b|in the \w+ year|in the year|'
    r'when |after they|after I|after he|after we|as he\b|as I\b|as they\b|'
    r'in the (?:commencement|midst|latter|space)|during)\b',
    re.IGNORECASE
)

PRED_LEAD_RE = re.compile(
    r'^(?:there (?:was|were|came|arose|did|stood|appeared)|'
    r'that (?:was|were|is|are)\b|'
    r'this (?:was|were|is|are)\b|'
    r'(?:he|she|they|it|we|I|ye|thou|the (?:people|Lord|king|Lamanites|Nephites|land|words?|brethren|priests?|servants?|men|man|woman|earth|wind|man|fruit|spirit|voice|prophets?|whole))\b)',
    re.IGNORECASE
)


def is_verse_number(line: str) -> bool:
    return bool(re.match(r"^\s*\d+:\d+\s*$", line))


def is_frame_only(line: str) -> bool:
    s = line.strip()
    if not s.endswith(','):
        return False
    if not FRAME_LINE_RE.match(s):
        return False
    return True


def scan_file(path: Path, verbose: bool = False):
    violations = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for i in range(len(lines) - 1):
        cur = lines[i]
        nxt = lines[i + 1]
        if not cur.strip() or not nxt.strip():
            continue
        if is_verse_number(cur) or is_verse_number(nxt):
            continue
        if not is_frame_only(cur):
            continue
        if not PRED_LEAD_RE.match(nxt.strip()):
            continue
        violations.append({
            "file": path.name,
            "line_num": i + 1,
            "cur": cur.strip(),
            "nxt": nxt.strip(),
        })
        if verbose:
            print(f"[DEVIATION] {path.name}:{i+1}")
            print(f"    cur: {cur.strip()[:90]}")
            print(f"    nxt: {nxt.strip()[:90]}")
    return violations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", "-v", action="store_true")
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
        all_violations.extend(scan_file(path, verbose=args.verbose))

    print()
    print("Frame+predication merge candidates — BofM v2-mine corpus")
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
