#!/usr/bin/env python3
"""
BoM abbreviation mapping and verse reference parsing.
Maps Hardy's abbreviations to internal book IDs used by the site.
"""

import re

# Hardy abbreviation → site book ID
ABBREV_TO_ID = {
    '1 Ne': '1nephi', '2 Ne': '2nephi', '3 Ne': '3nephi', '4 Ne': '4nephi',
    'Jac': 'jacob', 'Enos': 'enos', 'Jar': 'jarom', 'Omni': 'omni',
    'WoM': 'words-of-mormon', 'Mos': 'mosiah', 'Al': 'alma',
    'Hel': 'helaman', 'Morm': 'mormon', 'Eth': 'ether', 'Ether': 'ether',
    'Moro': 'moroni',
}

# Sort by length descending so "3 Ne" matches before "Ne"
_SORTED_ABBREVS = sorted(ABBREV_TO_ID.keys(), key=len, reverse=True)


def parse_bom_ref(ref_str):
    """Parse a Hardy BoM reference string into a list of (book_id, chapter, verse) tuples.

    Examples:
        'Al 32.28'        → [('alma', 32, 28)]
        '2 Ne 9.10-12'    → [('2nephi', 9, 10), ('2nephi', 9, 11), ('2nephi', 9, 12)]
        'Mos 7.27, 29'    → [('mosiah', 7, 27), ('mosiah', 7, 29)]
        'Eth 1.33, 35, 36' → [('ether', 1, 33), ('ether', 1, 35), ('ether', 1, 36)]

    Returns empty list for cross-references (starting with 'see') or unparseable refs.
    """
    ref_str = ref_str.strip()
    if ref_str.startswith('see '):
        return []

    # Find the book abbreviation
    book_id = None
    rest = ref_str
    for abbr in _SORTED_ABBREVS:
        if ref_str.startswith(abbr):
            book_id = ABBREV_TO_ID[abbr]
            rest = ref_str[len(abbr):].strip()
            break

    if not book_id:
        return []

    # rest should be like "32.28" or "9.10-12" or "7.27, 29" or "1.33, 35, 36"
    # Split on '.' to get chapter and verse part
    dot_parts = rest.split('.', 1)
    if len(dot_parts) != 2:
        return []

    try:
        chapter = int(dot_parts[0])
    except ValueError:
        return []

    verse_str = dot_parts[1].strip()
    results = []

    # Parse comma-separated verse groups
    for segment in verse_str.split(','):
        segment = segment.strip()
        if not segment:
            continue
        # Check for range (e.g., "10-12")
        if '-' in segment:
            range_parts = segment.split('-', 1)
            try:
                start = int(range_parts[0].strip())
                end = int(range_parts[1].strip())
                for v in range(start, end + 1):
                    results.append((book_id, chapter, v))
            except ValueError:
                continue
        else:
            try:
                results.append((book_id, chapter, int(segment)))
            except ValueError:
                continue

    return results


if __name__ == '__main__':
    # Quick test
    tests = [
        'Al 32.28', '2 Ne 9.10-12', 'Mos 7.27, 29',
        'Eth 1.33, 35, 36', '3 Ne 4.32-33', 'see Jas 2.21, 23',
        'WoM 1.4', '1 Ne 16.20, 25',
    ]
    for t in tests:
        print(f'{t:30s} → {parse_bom_ref(t)}')
