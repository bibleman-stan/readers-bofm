#!/usr/bin/env python3
"""
Parse Donald Parry's Hebrew parallelisms from parry-parallels-full.txt
into a structured JSON index for the BOM reader.

Output: data/parry_index.json
Format:
{
  "bookid": {
    "chapter_num": [
      {
        "type": "chiasmus",
        "vs": 1,       // verse_start
        "ve": 3,       // verse_end
        "lines": [
          {"level": "A", "indent": 1, "text": "...", "v": 1},
          ...
        ]
      }
    ]
  }
}

Usage: python3 build_parry_index.py
"""

import json, os, re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / 'data'
PARRY_FILE = DATA_DIR / 'parry-parallels-full.txt'

# Map Parry book headers → our bookIds
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

# Chapter name → number
CHAPTER_WORDS = {
    'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5,
    'Six': 6, 'Seven': 7, 'Eight': 8, 'Nine': 9, 'Ten': 10,
    'Eleven': 11, 'Twelve': 12, 'Thirteen': 13, 'Fourteen': 14,
    'Fifteen': 15, 'Sixteen': 16, 'Seventeen': 17, 'Eighteen': 18,
    'Nineteen': 19, 'Twenty': 20, 'Twenty-One': 21, 'Twenty-Two': 22,
    'Twenty-Three': 23, 'Twenty-Four': 24, 'Twenty-Five': 25,
    'Twenty-Six': 26, 'Twenty-Seven': 27, 'Twenty-Eight': 28,
    'Twenty-Nine': 29, 'Thirty': 30, 'Thirty-One': 31, 'Thirty-Two': 32,
    'Thirty-Three': 33, 'Thirty-Four': 34, 'Thirty-Five': 35,
    'Thirty-Six': 36, 'Thirty-Seven': 37, 'Thirty-Eight': 38,
    'Thirty-Nine': 39, 'Forty': 40, 'Forty-One': 41, 'Forty-Two': 42,
    'Forty-Three': 43, 'Forty-Four': 44, 'Forty-Five': 45,
    'Forty-Six': 46, 'Forty-Seven': 47, 'Forty-Eight': 48,
    'Forty-Nine': 49, 'Fifty': 50, 'Fifty-One': 51, 'Fifty-Two': 52,
    'Fifty-Three': 53, 'Fifty-Four': 54, 'Fifty-Five': 55,
    'Fifty-Six': 56, 'Fifty-Seven': 57, 'Fifty-Eight': 58,
    'Fifty-Nine': 59, 'Sixty': 60, 'Sixty-One': 61, 'Sixty-Two': 62,
    'Sixty-Three': 63,
}

# Type annotation patterns
TYPE_RE = re.compile(r'\(([^)]+)\)\s*$')
KNOWN_TYPES = {
    'chiasmus', 'synonymous', 'simple synonymous', 'antithetical',
    'alternate', 'contrast', 'progression', 'many ands',
    'random repetition', 'regular repetition', 'number parallelism',
    'like sentence beginnings', 'like paragraph endings',
    'like sentence endings', 'repeated alternation', 'epitome',
    'climax', 'anaphora', 'extended alternation', 'extended alternate',
}

# Regex for verse number at start of line
VERSE_RE = re.compile(r'^\s*(\d+)\s')

# Regex for label at start of content (after optional verse number)
LABEL_RE = re.compile(r'^([A-Ga-g]\'?)\s+')


def parse_chapter_num(line):
    """Parse 'Chapter Twenty-Two (Compare Isaiah 12)' → 22"""
    m = re.match(r'^Chapter\s+(.+?)(?:\s*\(.*\))?$', line.strip())
    if not m:
        return None
    word = m.group(1).strip()
    return CHAPTER_WORDS.get(word)


def classify_type(raw_type):
    """Normalize a Parry type annotation string."""
    t = raw_type.lower().strip()
    # Remove trailing notes like "1 Ne. 1:16–17"
    t = re.sub(r'\d+\s*ne\..*', '', t).strip()
    t = re.sub(r'\bsee\b.*', '', t).strip()
    if t in KNOWN_TYPES:
        return t
    # Partial matches
    for kt in KNOWN_TYPES:
        if kt in t:
            return kt
    return t if t else 'parallelism'


def is_type_annotation(text):
    """Check if text ends with a known type annotation in parens."""
    m = TYPE_RE.search(text)
    if not m:
        return None
    candidate = m.group(1).lower().strip()
    # Filter out things that look like parenthetical content, not annotations
    # Type annotations are usually short phrases
    if len(candidate) > 60:
        return None
    # Must contain at least one known type word or be a plausible type
    type_words = {'chiasmus', 'synonymous', 'antithetical', 'alternate',
                  'contrast', 'progression', 'ands', 'repetition',
                  'parallelism', 'anaphora', 'climax', 'epitome',
                  'beginnings', 'endings'}
    if any(w in candidate for w in type_words):
        return m.group(1).strip()
    return None


def parse_parry():
    """Parse the entire Parry file into structured data."""
    with open(PARRY_FILE, 'r', encoding='utf-8') as f:
        raw_lines = f.readlines()

    index = {}  # bookid → {chapter → [structures]}
    current_book = None
    current_chapter = None

    # Buffer for collecting labeled lines of the current structure
    struct_lines = []   # list of (level, indent, text, verse_num)
    struct_verses = set()
    current_verse = 0

    def flush_structure(ptype):
        """Save the current buffered structure."""
        nonlocal struct_lines, struct_verses
        if not struct_lines or not current_book or not current_chapter:
            struct_lines = []
            struct_verses = set()
            return

        bid = current_book
        ch = str(current_chapter)

        if bid not in index:
            index[bid] = {}
        if ch not in index[bid]:
            index[bid][ch] = []

        vs = min(struct_verses) if struct_verses else struct_lines[0][3]
        ve = max(struct_verses) if struct_verses else struct_lines[-1][3]

        lines_out = []
        for level, indent, text, vn in struct_lines:
            # Clean embedded inner-structure labels from text (e.g. "A\ttext")
            cleaned = re.sub(r'^[A-Ga-g]\'?\t+', '', text.strip())
            # Also strip inline type annotations like "(random repetition)"
            cleaned = re.sub(r'\s*\([^)]*repetition[^)]*\)', '', cleaned)
            cleaned = re.sub(r'\s*\(many ands\)', '', cleaned)
            lines_out.append({
                'level': level,
                'indent': indent,
                'text': cleaned.strip(),
                'v': vn,
            })

        index[bid][ch].append({
            'type': classify_type(ptype),
            'vs': vs,
            've': ve,
            'lines': lines_out,
        })

        struct_lines = []
        struct_verses = set()

    for raw_line in raw_lines:
        line = raw_line.rstrip('\n\r')

        # Check for book header
        stripped = line.strip()
        if stripped in BOOK_MAP:
            # Flush any pending structure
            if struct_lines:
                flush_structure('parallelism')
            current_book = BOOK_MAP[stripped]
            current_chapter = None
            current_verse = 0
            continue

        # Check for chapter header
        ch_num = parse_chapter_num(stripped)
        if ch_num is not None:
            if struct_lines:
                flush_structure('parallelism')
            current_chapter = ch_num
            current_verse = 0
            continue

        if not current_book or not current_chapter:
            continue

        # Skip known non-content lines
        if stripped.startswith('Chapters') or stripped.startswith('An account') or not stripped:
            continue
        if stripped.startswith('His Reign') or stripped.startswith('(1 Ne') or stripped.startswith('(2 Ne'):
            continue
        if re.match(r'^\d+\s+\d+\s+\d+', stripped):  # chapter number lists
            continue

        # Check for verse number
        vm = VERSE_RE.match(line)
        if vm:
            current_verse = int(vm.group(1))

        # Count leading tabs for indent level
        tabs = 0
        for ch in line:
            if ch == '\t':
                tabs += 1
            else:
                break

        # Strip leading whitespace/tabs and verse number
        content = line.lstrip()
        if vm:
            content = VERSE_RE.sub('', content, count=1).lstrip()

        if not content:
            continue

        # Check for type annotation
        type_ann = is_type_annotation(content)
        if type_ann:
            # Remove the annotation from the content
            content = TYPE_RE.sub('', content).strip()

        # Check for label
        lm = LABEL_RE.match(content)
        if lm:
            level = lm.group(1)
            text = content[lm.end():].strip()
            # This is a labeled line
            struct_lines.append((level, tabs, text, current_verse))
            struct_verses.add(current_verse)

            if type_ann:
                # This line has a type annotation — flush the structure
                flush_structure(type_ann)
        elif type_ann and struct_lines:
            # Unlabeled line with type annotation — it's part of the structure
            # Add as continuation text, then flush
            if content:
                struct_lines.append(('', tabs, content, current_verse))
                struct_verses.add(current_verse)
            flush_structure(type_ann)
        elif type_ann and not struct_lines:
            # Type annotation on a standalone/unlabeled passage — skip or create minimal
            pass
        else:
            # Unlabeled line — could be continuation of a labeled line
            # or just regular verse text outside any structure
            # If we have an active structure being built, this might be interstitial text
            pass

    # Flush any remaining
    if struct_lines:
        flush_structure('parallelism')

    return index


def main():
    print("Parsing Parry parallelisms...")
    index = parse_parry()

    total_structures = 0
    total_lines = 0
    for bid in index:
        for ch in index[bid]:
            for s in index[bid][ch]:
                total_structures += 1
                total_lines += len(s['lines'])

    outpath = DATA_DIR / 'parry_index.json'
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=1)

    size_kb = outpath.stat().st_size / 1024
    print(f"\n  Books: {len(index)}")
    print(f"  Total structures: {total_structures}")
    print(f"  Total labeled lines: {total_lines}")
    print(f"  Output: {outpath} ({size_kb:.0f} KB)")

    # Print per-book summary
    for bid in sorted(index.keys()):
        chapters = index[bid]
        n_structs = sum(len(v) for v in chapters.values())
        n_lines = sum(len(s['lines']) for v in chapters.values() for s in v)
        print(f"    {bid}: {n_structs} structures, {n_lines} lines")


if __name__ == '__main__':
    main()
