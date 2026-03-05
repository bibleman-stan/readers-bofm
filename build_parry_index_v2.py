#!/usr/bin/env python3
"""
Build parry_index.json from per-book Parry text files in text-files/parry/.

Each Parry file has the FULL verse text with poetic labels embedded.
This parser extracts every line of every verse, preserving:
  - Label (A, B, C, a, b, c, A', etc.) or empty string for unlabeled lines
  - Indent level (derived from label letter, capped at 2)
  - Text content (with inline type annotations stripped)
  - Type annotations collected per verse

Output format:
{
  "bookid": {
    "chapter": [
      {"v": 1, "lines": [{"text": "...", "label": "A", "indent": 0}, ...], "types": ["chiasmus"]},
      ...
    ]
  }
}
"""

import os, re, json, glob

PARRY_DIR = 'text-files/parry'
OUTPUT = 'data/parry_index.json'

# Map filename prefix to book ID
FILE_TO_BOOKID = {
    '01-1nephi': '1nephi',
    '02-2nephi': '2nephi',
    '03-jacob': 'jacob',
    '04-enos': 'enos',
    '05-jarom': 'jarom',
    '06-omni': 'omni',
    '07-words-of-mormon': 'words-of-mormon',
    '08-mosiah': 'mosiah',
    '09-alma': 'alma',
    '10-helaman': 'helaman',
    '11-3nephi': '3nephi',
    '12-4nephi': '4nephi',
    '13-mormon': 'mormon',
    '14-ether': 'ether',
    '15-moroni': 'moroni',
}

# Type annotation pattern: parenthesized text at end of line containing only
# lowercase words (no proper nouns, no verse content). Examples:
#   (chiasmus)  (simple alternate)  (contrasting ideas)  (extended alternate)
# We match any parenthesized phrase at the end that is all-lowercase and
# consists of 1-4 words, which distinguishes type labels from verse content
# like "(see Alma 5:3)" or "(for he has been faithful)".
TYPE_PATTERN = re.compile(r'\s*\(([a-z][a-z ]{0,40})\)\s*$')

# Verse number pattern: line starts with optional space + number + tab
# Verse numbers appear with only spaces before them (never tabs).
# Structure sub-numbers like "1", "2", "3" appear with leading tabs.
VERSE_RE = re.compile(r'^[ ]*(\d+)\t')

# Chapter header pattern
CHAPTER_RE = re.compile(r'^Chapter\s+', re.IGNORECASE)

# Label pattern: one or more tabs, then a letter label, then a tab
# Labels can be: A, B, C, ... K, a, b, c, ... g, A', B', etc.
# They can also have multiple labels on one line (nested structures): "C\t\t\tA\t"
LABEL_RE = re.compile(r'^(\t+)([A-Za-z]\'?)\t')


def extract_types(text):
    """Extract type annotations from text, return (cleaned_text, [types])."""
    # Normalize non-breaking spaces to regular spaces
    text = text.replace('\xa0', ' ')
    types = []
    m = TYPE_PATTERN.search(text)
    if m:
        types.append(m.group(1).strip())
        text = text[:m.start()].strip()
    return text, types


def count_leading_tabs(line):
    """Count leading tabs."""
    n = 0
    for c in line:
        if c == '\t':
            n += 1
        else:
            break
    return n


def parse_line(line):
    """Parse a single line from the Parry file.

    Returns dict: {label, text, indent, types}
    - label: the letter label (e.g. 'A', 'b', "C'") or '' for unlabeled
    - text: the text content with type annotations stripped
    - indent: visual indent level (0, 1, or 2 based on label letter)
    - types: list of type annotations found on this line
    """
    # Strip trailing whitespace
    raw = line.rstrip()
    if not raw:
        return None

    # Check if this line has labels
    # Labels appear as tab-indented letters followed by tab
    # There can be multiple labels (nested structures) — we want the outermost
    # e.g. "\t\tC\t\t\tA\tAnd now I, Nephi..."
    # Parse all labels and take the first (outermost structure)
    remaining = raw
    labels_found = []

    # Scan for label patterns: sequences of tabs + letter (or number) + tab
    # Letters (A, B, a, b, etc.) are Parry's structural labels
    # Numbers (1, 2, 3) are sub-level markers within a verse
    while True:
        m = re.match(r'^(\t*)([A-Za-z]\'?|\d+)\t', remaining)
        if m:
            lbl = m.group(2)
            # Only keep letter labels; skip numeric sub-markers
            if not lbl.isdigit():
                labels_found.append(lbl)
            remaining = remaining[m.end():]
        else:
            break

    if labels_found:
        # Use the first label (outermost structure)
        label = labels_found[0]
        text = remaining.strip()
    else:
        label = ''
        # Use remaining (after stripping any consumed numeric sub-labels),
        # not raw (which still has the tab+digit+tab prefix)
        text = remaining.strip()

    # Strip type annotations from text
    text, types = extract_types(text)

    # Store raw label — indent calculation happens at HTML render time
    # in build_book.py where we can track context (preceding uppercase level).
    return {'label': label, 'text': text, 'indent': 0, 'types': types}


def parse_book(filepath):
    """Parse a Parry book file into chapter → verse structure."""
    with open(filepath, encoding='utf-8') as f:
        lines = f.readlines()

    chapters = {}
    current_chapter = 0
    current_verse = 0
    current_verse_lines = []
    current_verse_types = []

    def flush_verse():
        nonlocal current_verse_lines, current_verse_types
        if current_verse > 0 and current_verse_lines:
            ch_key = str(current_chapter)
            if ch_key not in chapters:
                chapters[ch_key] = []
            chapters[ch_key].append({
                'v': current_verse,
                'lines': current_verse_lines,
                'types': list(set(current_verse_types)),  # dedupe
            })
        current_verse_lines = []
        current_verse_types = []

    for raw_line in lines:
        line = raw_line.rstrip('\n')

        # Chapter header
        if CHAPTER_RE.match(line.strip()):
            flush_verse()
            current_chapter += 1
            current_verse = 0
            continue

        # Skip blank lines
        if not line.strip():
            continue

        # Check for verse number at start of line
        vm = VERSE_RE.match(line)
        if vm:
            flush_verse()
            current_verse = int(vm.group(1))
            # Remove verse number prefix, keep the rest
            after_verse = line[vm.end():]
            parsed = parse_line(after_verse)
            if parsed and parsed['text']:
                current_verse_lines.append({
                    'label': parsed['label'],
                    'text': parsed['text'],
                    'indent': parsed['indent'],
                })
                current_verse_types.extend(parsed['types'])
        else:
            # Continuation line (no verse number)
            if current_verse > 0:
                parsed = parse_line(line)
                if parsed and parsed['text']:
                    current_verse_lines.append({
                        'label': parsed['label'],
                        'text': parsed['text'],
                        'indent': parsed['indent'],
                    })
                    current_verse_types.extend(parsed['types'])

    flush_verse()
    return chapters


def main():
    print("Building Parry index from per-book files...\n")

    index = {}
    total_verses = 0
    total_lines = 0

    for filename in sorted(os.listdir(PARRY_DIR)):
        if not filename.endswith('.txt'):
            continue
        stem = filename[:-4]
        if stem not in FILE_TO_BOOKID:
            continue
        bid = FILE_TO_BOOKID[stem]
        filepath = os.path.join(PARRY_DIR, filename)
        chapters = parse_book(filepath)
        index[bid] = chapters

        book_verses = sum(len(vlist) for vlist in chapters.values())
        book_lines = sum(len(v['lines']) for vlist in chapters.values() for v in vlist)
        total_verses += book_verses
        total_lines += book_lines
        print(f"  {bid}: {book_verses} verses, {book_lines} lines")

    # Write output
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(index, f, separators=(',', ':'))

    size_kb = os.path.getsize(OUTPUT) / 1024
    print(f"\n  Total: {total_verses} verses, {total_lines} lines")
    print(f"  Output: {OUTPUT} ({size_kb:.0f} KB)")


if __name__ == '__main__':
    main()
