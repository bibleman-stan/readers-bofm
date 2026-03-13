#!/usr/bin/env python3
"""
Sense-line rebalancing v3 — incorporates lessons from stan's Mosiah 1-3 edits.

Key changes from v2:
  - Lowered LONG_THRESHOLD to 55 (stan breaks lines well under 65)
  - Lowered MIN_FRAGMENT to 18 (allows shorter left pieces like appositives)
  - Added ", than " as a break pattern (comparative clauses)
  - Added ", except " as a break pattern (exception clauses)
  - Added ", nor " as a break pattern
  - Added ", such as " for itemized-example breaks
  - Boosted priority of ", among " / ", through " / ", among " (prepositional after verb)
  - Better scoring: prioritize grammatical quality over balance
  - Still protects OR-lists and AND-enumerations from splitting
  - Iterative: after breaking a line, re-checks the two halves for further breaks
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

# Break patterns with priorities (higher = preferred break point)
BREAK_PATTERNS = [
    # Relative/subordinate clauses — strongest breaks
    (r',\s+that\s+', 14),
    (r',\s+which\s+', 13),
    (r',\s+who\s+', 12),
    (r',\s+whom\s+', 12),
    (r',\s+whose\s+', 12),
    (r',\s+where\s+', 11),
    (r',\s+when\s+', 11),
    # Comparative/exception clauses (new from Mosiah 3)
    (r',\s+than\s+', 11),
    (r',\s+except\s+', 11),
    # Semicolon breaks
    (r';\s+and\s+', 10),
    (r';\s+for\s+', 10),
    (r';\s+yea,?\s+', 9),
    (r';\s+neither\s+', 9),
    (r';\s+but\s+', 9),
    (r';\s+wherefore,?\s+', 9),
    (r';\s+nevertheless,?\s+', 9),
    (r';\s+insomuch\s+', 9),
    # Causal/conditional
    (r',\s+for\s+', 8),
    (r',\s+because\s+', 8),
    (r',\s+insomuch\s+', 8),
    # Itemized examples (new from Mosiah 3:5 miracles list)
    (r',\s+such as\s+', 8),
    # Intensifiers / restatements
    (r',\s+even\s+', 7),
    (r',\s+yea,?\s+', 7),
    # Conjunctions
    (r',\s+but\s+', 7),
    (r',\s+neither\s+', 7),
    (r',\s+nor\s+', 7),
    (r',\s+save\s+', 7),
    (r',\s+and\s+', 5),
    (r',\s+or\s+', 5),
    # Prepositional phrases (verb → direction/location — boosted from v2)
    (r',\s+among\s+', 6),
    (r',\s+through\s+', 6),
    (r',\s+unto\s+', 5),
    (r',\s+according\s+', 6),
    (r',\s+after\s+', 5),
    (r',\s+to\s+', 4),
    (r',\s+by\s+', 4),
    (r',\s+in\s+', 4),
    (r',\s+upon\s+', 4),
    (r',\s+from\s+', 4),
    (r',\s+within\s+', 5),
    (r',\s+out of\s+', 5),
    (r',\s+concerning\s+', 6),
]

MIN_FRAGMENT = 18
LONG_THRESHOLD = 55


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
    enum_matches = list(re.finditer(r'(\w+(?:\s+\w+)*), and (\w+(?:\s+\w+)*), and (\w+)', line))
    for em in enum_matches:
        start, end = em.start(), em.end()
        break_pos = len(part1)
        if start < break_pos < end:
            return True

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
            if len(part2) >= MIN_FRAGMENT and len(line) > 45 and len(part1) >= 16:
                return (len(part1), part1, part2)
    return None


def find_best_break(line):
    """Find the best break point in a line."""
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

            # Score: prioritize grammatical quality (priority) over balance
            score = priority * 120 - balance * 0.3 - mid_distance * 0.2

            candidates.append((score, punct_end, part1, part2))

    if not candidates:
        return None

    candidates.sort(key=lambda x: -x[0])
    _, pos, part1, part2 = candidates[0]
    return (pos, part1, part2)


def process_file(filepath, dry_run=True):
    """Process a single text file, finding and optionally fixing long lines.

    Iterative: after breaking a line, re-checks the resulting halves.
    """
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

                # Collect all parts (may break further)
                all_parts = []

                # Try to break part1 further
                sub1 = find_best_break(part1) if len(part1) > LONG_THRESHOLD else None
                if sub1:
                    all_parts.extend([sub1[1], sub1[2]])
                else:
                    all_parts.append(part1)

                # Try to break part2 further
                sub2 = find_best_break(part2) if len(part2) > LONG_THRESHOLD else None
                if sub2:
                    all_parts.extend([sub2[1], sub2[2]])
                else:
                    all_parts.append(part2)

                changes.append({
                    'line_num': i + 1,
                    'verse': current_verse,
                    'original': line,
                    'parts': all_parts,
                })
                if not dry_run:
                    lines[i] = '\n'.join(all_parts) + '\n'

        i += 1

    if not dry_run and changes:
        with open(filepath, 'w') as f:
            f.writelines(lines)

    return changes


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Sense-line rebalancing tool v3')
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
                parts = c['parts']
                print(f"    NEW: {parts[0]}")
                for p in parts[1:]:
                    print(f"         {p}")
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
