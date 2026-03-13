#!/usr/bin/env python3
"""
Sense-line rebalancing tool for Book of Mormon reader text files.

Identifies and fixes lines that are too long (front-heavy) by splitting
at natural grammatical break points, and consolidates lines that are
over-split into fragments too short to stand alone.

Style rules (derived from 1-2 Nephi editorial decisions):
1. Break long front-heavy lines at natural grammatical pivots:
   subordinate clauses (that, which, for, because, wherefore),
   appositives, prepositional phrases that shift the scene
2. Give rhetorically significant phrases their own line
3. Keep natural units together — don't over-split short phrases
4. Mirror parallel structures across lines
5. Don't touch what already works — be conservative

Threshold: lines > 78 chars get examined; lines < 25 chars that
form a natural unit with their neighbor get examined for consolidation.
"""

import re
import sys
import os

# ── Break-point patterns, ordered by preference ──
# Each is (regex, priority) — higher priority = preferred break point
BREAK_PATTERNS = [
    # Subordinate clause boundaries
    (r',\s+that\s+', 10),
    (r',\s+which\s+', 10),
    (r',\s+who\s+', 10),
    (r',\s+whom\s+', 10),
    (r',\s+whose\s+', 10),
    (r',\s+where\s+', 9),
    (r',\s+when\s+', 9),
    (r';\s+and\s+', 9),
    (r';\s+for\s+', 9),
    (r';\s+yea,?\s+', 8),
    (r';\s+neither\s+', 8),
    (r';\s+but\s+', 8),
    (r';\s+wherefore,?\s+', 8),
    (r';\s+nevertheless,?\s+', 8),
    (r';\s+insomuch\s+', 8),
    (r',\s+for\s+', 7),
    (r',\s+because\s+', 7),
    (r',\s+insomuch\s+', 7),
    (r',\s+even\s+', 6),
    (r',\s+yea,?\s+', 6),
    (r',\s+and\s+', 5),
    (r',\s+but\s+', 5),
    (r',\s+neither\s+', 5),
    (r',\s+or\s+', 5),
    (r',\s+save\s+', 5),
    (r',\s+unto\s+', 4),
    (r',\s+according\s+', 4),
    (r',\s+after\s+', 4),
    (r',\s+to\s+', 3),
]

MIN_FRAGMENT = 28  # Don't create fragments shorter than this
LONG_THRESHOLD = 78  # Lines longer than this get examined


def find_best_break(line):
    """Find the best break point in a long line.

    Returns (pos, new_line1, new_line2) or None if no good break found.
    pos is the character position after which to break.
    """
    if len(line) <= LONG_THRESHOLD:
        return None

    candidates = []
    for pattern, priority in BREAK_PATTERNS:
        for m in re.finditer(pattern, line):
            # Break after the comma/semicolon, before the keyword
            # Find the position right after the punctuation
            match_start = m.start()
            match_text = m.group()

            # Find the split: after the comma/semicolon+space, before keyword
            # e.g. ", that " -> break after ", " yielding "..., " and "that ..."
            punct_end = match_start
            for i, c in enumerate(match_text):
                if c in ',;':
                    punct_end = match_start + i + 1
                    break

            part1 = line[:punct_end].rstrip()
            part2 = line[punct_end:].lstrip()

            # Check minimum fragment sizes
            if len(part1) < MIN_FRAGMENT or len(part2) < MIN_FRAGMENT:
                continue

            # Prefer breaks that create balanced halves
            balance = abs(len(part1) - len(part2))
            # Prefer breaks closer to the middle
            mid_distance = abs((len(line) / 2) - punct_end)

            # Score: higher priority pattern + better balance + closer to middle
            score = priority * 100 - balance - mid_distance * 0.5

            candidates.append((score, punct_end, part1, part2))

    if not candidates:
        return None

    # Pick highest scoring candidate
    candidates.sort(key=lambda x: -x[0])
    _, pos, part1, part2 = candidates[0]
    return (pos, part1, part2)


def process_file(filepath, dry_run=True):
    """Process a single text file, finding and optionally fixing long lines."""
    with open(filepath) as f:
        lines = f.readlines()

    changes = []
    current_verse = "?"

    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n')

        # Track verse references
        verse_match = re.match(r'^(\d+:\d+)$', line)
        if verse_match:
            current_verse = verse_match.group(1)
            i += 1
            continue

        # Skip blank lines
        if not line.strip():
            i += 1
            continue

        # Check for long lines
        if len(line) > LONG_THRESHOLD:
            result = find_best_break(line)
            if result:
                pos, part1, part2 = result
                changes.append({
                    'line_num': i + 1,
                    'verse': current_verse,
                    'original': line,
                    'part1': part1,
                    'part2': part2,
                })
                if not dry_run:
                    lines[i] = part1 + '\n' + part2 + '\n'

        i += 1

    if not dry_run and changes:
        with open(filepath, 'w') as f:
            f.writelines(lines)

    return changes


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Sense-line rebalancing tool')
    parser.add_argument('files', nargs='+', help='Text files to process')
    parser.add_argument('--apply', action='store_true', help='Apply changes (default: dry run)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show all changes')
    args = parser.parse_args()

    total_changes = 0
    for filepath in args.files:
        bookname = os.path.basename(filepath)
        changes = process_file(filepath, dry_run=not args.apply)

        if changes:
            print(f"\n{'=' * 60}")
            print(f"  {bookname}: {len(changes)} changes")
            print(f"{'=' * 60}")
            for c in changes:
                print(f"\n  {c['verse']} (line {c['line_num']}):")
                print(f"    OLD: {c['original']}")
                print(f"    NEW: {c['part1']}")
                print(f"         {c['part2']}")
            total_changes += len(changes)
        else:
            print(f"  {bookname}: no changes needed")

    print(f"\n{'=' * 60}")
    print(f"  TOTAL: {total_changes} changes across {len(args.files)} files")
    if not args.apply:
        print(f"  (DRY RUN — use --apply to write changes)")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
