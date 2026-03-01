#!/usr/bin/env python3
"""Parse Parry's parallelism data into a structured JSON index for the reader app.

LITE FILTER: chiasmus ≤3 deep, simple synonymous, simple alternate,
             antithetical, contrasting ideas.
"""

import json
import re
import sys
import os


def norm(s):
    return s.replace('\u00a0', ' ').replace('\r', '').strip()


def classify_type(ptype):
    ptype = norm(ptype).lower()
    if 'chiasmus' in ptype:
        return 'chiasmus'
    if 'synonymous' in ptype:
        return 'synonymous'
    if 'alternate' in ptype:
        return 'alternate'
    if 'antithetical' in ptype:
        return 'antithetical'
    if 'contrasting' in ptype:
        return 'contrast'
    return None


BOOK_MAP = {
    'The First Book of Nephi': '1nephi',
    'The Second Book of Nephi': '2nephi',
    'The Book of Jacob': 'jacob',
    'The Book of Enos': 'enos',
    'The Book of Jarom': 'jarom',
    'The Book of Omni': 'omni',
    'The Words of Mormon': 'words-of-mormon',
    'The Book of Mosiah': 'mosiah',
    'The Book of Alma': 'alma',
    'The Book of Helaman': 'helaman',
    'The Third Book of Nephi': '3nephi',
    'The Fourth Book of Nephi': '4nephi',
    'The Book of Mormon': 'mormon',
    'The Book of Ether': 'ether',
    'The Book of Moroni': 'moroni',
}

WORD_NUMS = {}
_ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
         'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen',
         'Seventeen', 'Eighteen', 'Nineteen']
_tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty']
for i, w in enumerate(_ones):
    if w:
        WORD_NUMS[w] = i
for ti, t in enumerate(_tens):
    if t:
        WORD_NUMS[t] = ti * 10
        for oi in range(1, 10):
            WORD_NUMS[f'{t}-{_ones[oi]}'] = ti * 10 + oi


def clean_parry_text(text):
    """Clean a line from Parry for matching against BofM sense-lines."""
    # Remove type annotations
    text = re.sub(r'\s*\([^)]+\)\s*$', '', text)
    # Remove leading verse numbers
    text = re.sub(r'^\s*\d+\s*', '', text)
    # Remove letter labels (A  text... or a  text...)
    text = re.sub(r'^[A-Ka-k]\s+', '', text)
    # Remove tab-indented letter labels
    text = re.sub(r'^[\t ]*[A-Ka-k]\t', '', text)
    return text.strip()


def has_letter_label(line_text):
    """Check if a normalized line has a Parry letter label."""
    s = norm(line_text)
    s = re.sub(r'^\d+\s+', '', s)  # strip verse num
    s = s.lstrip('\t ')
    return bool(re.match(r'^[A-Ka-k]\s', s))


def get_label(line_text):
    """Extract the letter label from a line, or None."""
    s = norm(line_text)
    s = re.sub(r'^\d+\s+', '', s)
    s = s.lstrip('\t ')
    m = re.match(r'^([A-Ka-k])\s', s)
    return m.group(1).upper() if m else None


def parse_parry(filepath, book_filter=None):
    with open(filepath, encoding='utf-8') as f:
        raw_lines = [l.rstrip('\r\n') for l in f.readlines()]

    index = {}
    current_book = None
    current_chapter = 0
    current_verse = 0

    def add_entry(book, chapter, entry):
        if book not in index:
            index[book] = {}
        ch = str(chapter)
        if ch not in index[book]:
            index[book][ch] = []
        # Dedup: don't add if identical entry already exists
        for existing in index[book][ch]:
            if (existing['verse_start'] == entry['verse_start'] and
                existing['verse_end'] == entry['verse_end'] and
                existing['type'] == entry['type'] and
                len(existing['lines']) == len(entry['lines'])):
                return
        index[book][ch].append(entry)

    i = 0
    while i < len(raw_lines):
        raw = raw_lines[i]
        stripped = norm(raw)

        # Detect book headers
        for header, bid in BOOK_MAP.items():
            if stripped.startswith(header):
                if header == 'The Book of Mormon' and current_book == '4nephi':
                    current_book = 'mormon'
                elif header != 'The Book of Mormon':
                    current_book = bid
                break

        # Detect chapter headers
        cm = re.match(r'^Chapter\s+([A-Za-z-]+)', stripped)
        if cm:
            ch_text = cm.group(1).strip()
            current_chapter = WORD_NUMS.get(ch_text, 0)
            i += 1
            continue

        # Detect verse numbers
        vm = re.match(r'^\s*(\d+)\s', stripped)
        if vm:
            current_verse = int(vm.group(1))

        # Skip if filtering
        if book_filter and current_book != book_filter:
            i += 1
            continue
        if not current_book or current_chapter == 0:
            i += 1
            continue

        # Check for type annotation on this line
        type_match = re.search(r'\(([^)]+)\)\s*$', stripped)
        if not type_match:
            i += 1
            continue

        ptype_raw = type_match.group(1)
        our_type = classify_type(ptype_raw)
        if our_type is None:
            i += 1
            continue

        # ---- Check if this is a LABELED structure (has A/B/C markers nearby) ----
        # Scan backward from this line to find labeled lines
        labeled = []
        max_depth = 0

        for j in range(i, max(i - 30, 0), -1):
            l = raw_lines[j]
            l_stripped = norm(l)

            # Stop at chapter headers or book headers
            if l_stripped.startswith('Chapter ') or any(l_stripped.startswith(h) for h in BOOK_MAP):
                break

            if has_letter_label(l):
                label = get_label(l)
                if label:
                    if label >= 'A' and label <= 'K':
                        depth = ord(label) - ord('A') + 1
                    else:
                        depth = ord(label.upper()) - ord('A') + 1
                    max_depth = max(max_depth, depth)

                    text = clean_parry_text(l)
                    # Get verse for this line
                    vv = re.match(r'^\s*(\d+)\s', l_stripped)
                    v = int(vv.group(1)) if vv else current_verse

                    labeled.insert(0, {
                        'text_fragment': text[:60],
                        'level': label,
                        'verse': v
                    })
            elif j < i:
                # Non-labeled line: if it's a plain verse start (number without label),
                # and we already have some labeled lines, stop scanning
                if labeled and re.match(r'^\s*\d+\s+[^A-Ka-k\t]', l_stripped):
                    break

        # If we found labeled lines, use them
        if len(labeled) >= 2:
            # LITE FILTER: skip deep chiasms
            if our_type == 'chiasmus' and max_depth > 3:
                i += 1
                continue

            verse_start = min(ll['verse'] for ll in labeled)
            verse_end = max(ll['verse'] for ll in labeled)
            add_entry(current_book, current_chapter, {
                'type': our_type,
                'verse_start': verse_start,
                'verse_end': verse_end,
                'lines': labeled
            })
            i += 1
            continue

        # ---- UNLABELED COUPLET: simple synonymous / antithetical pair ----
        # The annotated line is the "B" half; the line above is the "A" half.
        annotated_text = clean_parry_text(stripped)
        if not annotated_text:
            i += 1
            continue

        # Find previous content line (skip empties, stop at verse/chapter markers)
        prev_text = None
        prev_verse = current_verse
        for j in range(i - 1, max(i - 4, 0), -1):
            pl = norm(raw_lines[j])
            if not pl:
                continue
            if pl.startswith('Chapter '):
                break
            # Skip lines that have their own type annotation (they're separate structures)
            if re.search(r'\(([^)]+)\)\s*$', pl):
                break
            # This is our partner line
            prev_text = clean_parry_text(pl)
            vv = re.match(r'^\s*(\d+)\s', pl)
            if vv:
                prev_verse = int(vv.group(1))
            break

        if prev_text and annotated_text:
            add_entry(current_book, current_chapter, {
                'type': our_type,
                'verse_start': min(prev_verse, current_verse),
                'verse_end': max(prev_verse, current_verse),
                'lines': [
                    {'text_fragment': prev_text[:60], 'level': 'A', 'verse': prev_verse},
                    {'text_fragment': annotated_text[:60], 'level': 'A', 'verse': current_verse}
                ]
            })

        i += 1

    return index


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    parry_file = os.path.join(base, 'data', 'parry-parallels-full.txt')

    if not os.path.exists(parry_file):
        print(f"Error: {parry_file} not found")
        sys.exit(1)

    book_filter = None
    if len(sys.argv) > 1:
        book_filter = sys.argv[1]
        print(f"Filtering to book: {book_filter}")

    index = parse_parry(parry_file, book_filter=book_filter)

    total = 0
    for bid in sorted(index.keys()):
        chapters = index[bid]
        book_total = sum(len(entries) for entries in chapters.values())
        total += book_total
        print(f"  {bid}: {book_total} structures across {len(chapters)} chapters")
    print(f"  TOTAL: {total} lite structures")

    out_path = os.path.join(base, 'data', 'parallel_index.json')
    with open(out_path, 'w') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {out_path}")


if __name__ == '__main__':
    main()
