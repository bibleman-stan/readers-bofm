#!/usr/bin/env python3
"""
Filtered version of rebreak2 — applies changes but skips lines that would
split OR-lists, AND-enumerations, compound phrases, or create too-short fragments.
"""

import re
import sys
import os

# ── Patterns that should NOT be broken (lists, compound subjects) ──
LIST_PATTERNS = [
    r'\w+,\s+and\s+\w+,\s+and\s+\w+',
    r'both\s+\w+\s+and\s+\w+',
    r'(?:Nephi|Laman|Lemuel|Sam|Jacob|Joseph|Mosiah|Alma|Helaman|Mormon|Moroni|Ether)\s*,\s*and\s+',
]

OR_LIST_PATTERNS = [
    r'\w+,\s+or\s+\w+,\s+or\s+\w+',
    r'\w+,\s+or\s+\w+\s+',
]

VOCATIVE_PATTERNS = [
    r'^(My (?:sons?|brethren|people|friends),)\s+',
    r'^(And now,? my (?:sons?|brethren|people|friends),)\s+',
    r'^(But,? O my (?:sons?|brethren|people|friends),)\s+',
    r'^(O (?:my )?(?:sons?|brethren|people|friends),)\s+',
    r'^(I say unto you,? (?:my (?:sons?|brethren|people),)?)\s+',
    r'^(And (?:now,? )?I say unto you,)\s+',
    r'^(Behold,? I say unto you,)\s+',
    r'^(And (?:behold,? )?moreover,)\s+',
]

BREAK_PATTERNS = [
    (r',\s+that\s+', 12),
    (r',\s+which\s+', 12),
    (r',\s+who\s+', 11),
    (r',\s+whom\s+', 11),
    (r',\s+whose\s+', 11),
    (r',\s+where\s+', 10),
    (r',\s+when\s+', 10),
    (r';\s+and\s+', 10),
    (r';\s+for\s+', 10),
    (r';\s+yea,?\s+', 9),
    (r';\s+neither\s+', 9),
    (r';\s+but\s+', 9),
    (r';\s+wherefore,?\s+', 9),
    (r';\s+nevertheless,?\s+', 9),
    (r';\s+insomuch\s+', 9),
    (r',\s+for\s+', 8),
    (r',\s+because\s+', 8),
    (r',\s+insomuch\s+', 8),
    (r',\s+even\s+', 7),
    (r',\s+yea,?\s+', 7),
    (r',\s+and\s+', 5),
    (r',\s+but\s+', 6),
    (r',\s+neither\s+', 6),
    (r',\s+or\s+', 5),
    (r',\s+save\s+', 6),
    (r',\s+unto\s+', 4),
    (r',\s+according\s+', 5),
    (r',\s+after\s+', 4),
    (r',\s+to\s+', 3),
    (r',\s+by\s+', 3),
    (r',\s+in\s+', 3),
    (r',\s+upon\s+', 3),
    (r',\s+from\s+', 3),
    (r',\s+within\s+', 4),
    (r',\s+among\s+', 4),
    (r',\s+out of\s+', 4),
    (r',\s+through\s+', 4),
]

MIN_FRAGMENT = 22
LONG_THRESHOLD = 65


def is_in_list_context(line, break_pos):
    """Check if the break position falls inside a list construction."""
    window_start = max(0, break_pos - 40)
    window_end = min(len(line), break_pos + 40)
    window = line[window_start:window_end]

    for pat in LIST_PATTERNS:
        if re.search(pat, window):
            return True
    return False


def is_in_or_list_context(line, break_pos):
    """Check if break falls inside an OR-list."""
    window_start = max(0, break_pos - 40)
    window_end = min(len(line), break_pos + 40)
    window = line[window_start:window_end]

    for pat in OR_LIST_PATTERNS:
        if re.search(pat, window):
            return True
    return False


def would_split_enumeration(line, part1, part2):
    """Check if this break splits an X, and Y, and Z enumeration."""
    # Check for AND-enumeration pattern in original line
    enum_matches = list(re.finditer(r'(\w+(?:\s+\w+)*), and (\w+(?:\s+\w+)*), and (\w+)', line))
    for em in enum_matches:
        start, end = em.start(), em.end()
        break_pos = len(part1)
        if start < break_pos < end:
            return True

    # Check for OR-enumeration
    or_enum_matches = list(re.finditer(r'(\w+(?:\s+\w+)*), or (\w+(?:\s+\w+)*), or (\w+)', line))
    for em in or_enum_matches:
        start, end = em.start(), em.end()
        break_pos = len(part1)
        if start < break_pos < end:
            return True

    return False


def find_vocative_break(line):
    """Check if line starts with a direct address that should be on its own line."""
    for pat in VOCATIVE_PATTERNS:
        m = re.match(pat, line)
        if m:
            part1 = m.group(1)
            part2 = line[m.end():]
            # Only break if the remainder is substantial AND left side is substantial
            if len(part2) >= MIN_FRAGMENT and len(line) > 50 and len(part1) >= 18:
                return (len(part1), part1, part2)
    return None


def find_best_break(line):
    """Find the best break point in a long line, with enhanced filtering."""
    if len(line) <= LONG_THRESHOLD:
        return None

    # First check for vocative breaks (highest priority)
    voc = find_vocative_break(line)
    if voc:
        return voc

    candidates = []
    for pattern, priority in BREAK_PATTERNS:
        for m in re.finditer(pattern, line):
            match_start = m.start()
            match_text = m.group()

            punct_end = match_start
            for i, c in enumerate(match_text):
                if c in ',;':
                    punct_end = match_start + i + 1
                    break

            part1 = line[:punct_end].rstrip()
            part2 = line[punct_end:].lstrip()

            if len(part1) < MIN_FRAGMENT or len(part2) < MIN_FRAGMENT:
                continue

            # Skip if this would break an AND-enumeration
            if is_in_list_context(line, punct_end):
                if priority <= 6:
                    continue

            # Skip if this would break an OR-list
            if is_in_or_list_context(line, punct_end):
                if priority <= 6:
                    continue

            # Skip if part2 starts with "or " (likely splitting an alternative)
            if part2.startswith('or '):
                continue

            # Skip if would split enumeration
            if would_split_enumeration(line, part1, part2):
                continue

            balance = abs(len(part1) - len(part2))
            mid_distance = abs((len(line) / 2) - punct_end)

            score = priority * 100 - balance * 0.5 - mid_distance * 0.3

            candidates.append((score, punct_end, part1, part2))

    if not candidates:
        return None

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

        verse_match = re.match(r'^(\d+:\d+)$', line)
        if verse_match:
            current_verse = verse_match.group(1)
            i += 1
            continue

        if not line.strip():
            i += 1
            continue

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
    parser = argparse.ArgumentParser(description='Sense-line rebalancing tool v2 (filtered)')
    parser.add_argument('files', nargs='+', help='Text files to process')
    parser.add_argument('--apply', action='store_true', help='Apply changes (default: dry run)')
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
