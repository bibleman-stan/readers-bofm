#!/usr/bin/env python3
"""
Split parry-parallels-full2.txt into per-book files in text-files/parry/.

Each output file contains only the chapter/verse content for that book,
with all original formatting (tabs, labels, type annotations) preserved.
Book intros, subtitle lines, and chapter-number index lines are stripped.
"""

import os, re

INPUT = 'data/parry-parallels-full2.txt'
OUTDIR = 'text-files/parry'

# Map book header text → output filename
BOOK_MAP = [
    ("The First Book of Nephi",   "01-1nephi.txt"),
    ("The Second Book of Nephi",  "02-2nephi.txt"),
    ("The Book of Jacob",         "03-jacob.txt"),
    ("The Book of Enos",          "04-enos.txt"),
    ("The Book of Jarom",         "05-jarom.txt"),
    ("The Book of Omni",          "06-omni.txt"),
    ("The Words of Mormon",       "07-words-of-mormon.txt"),
    ("The Book of Mosiah",        "08-mosiah.txt"),
    ("The Book of Alma",          "09-alma.txt"),
    ("The Book of Helaman",       "10-helaman.txt"),
    ("The Third Book of Nephi",   "11-3nephi.txt"),
    ("The Fourth Book of Nephi",  "12-4nephi.txt"),
    ("The Book of Mormon",        "13-mormon.txt"),
    ("The Book of Ether",         "14-ether.txt"),
    ("The Book of Moroni",        "15-moroni.txt"),
]

BOOK_HEADERS = [h for h, _ in BOOK_MAP]

def is_book_header(line):
    return line.strip() in BOOK_HEADERS

def is_chapter_header(line):
    """Match 'Chapter One', 'Chapter Twenty-Two', etc."""
    return bool(re.match(r'^Chapter\s+', line.strip()))

def is_chapter_index(line):
    """Match lines like '1  2  3  4  5  ...' (chapter number lists)."""
    stripped = line.strip()
    if not stripped:
        return False
    # All tokens should be numbers separated by spaces
    return all(t.isdigit() for t in stripped.split())

def is_subtitle(line):
    """Match book subtitles like 'His Reign and Ministry', 'Chapters', etc."""
    stripped = line.strip()
    if stripped == 'Chapters':
        return True
    if stripped == 'His Reign and Ministry':
        return True
    return False

def is_book_intro(line):
    """Match the long 'An account of...' intro paragraph.
    These are long lines that don't start with a verse number or tab."""
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith('An account of') or stripped.startswith('Comprising'):
        return True
    return False

def main():
    os.makedirs(OUTDIR, exist_ok=True)

    with open(INPUT, encoding='utf-8') as f:
        lines = f.readlines()

    current_book = -1
    book_lines = {}  # index → list of lines
    skip_intro = False

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip('\n')

        # Check for book header
        if is_book_header(stripped):
            current_book += 1
            book_lines[current_book] = []
            skip_intro = True
            i += 1
            continue

        # Skip subtitle, chapter index, blank lines, and intro paragraphs
        # until we hit the first Chapter header
        if skip_intro:
            if is_chapter_header(stripped):
                skip_intro = False
                book_lines[current_book].append(stripped + '\n')
                i += 1
                continue
            else:
                i += 1
                continue

        if current_book < 0:
            i += 1
            continue

        book_lines[current_book].append(stripped + '\n')
        i += 1

    # Write output files
    for idx, (header, filename) in enumerate(BOOK_MAP):
        if idx not in book_lines:
            print(f"  WARNING: No content for {header}")
            continue
        outpath = os.path.join(OUTDIR, filename)
        with open(outpath, 'w', encoding='utf-8') as f:
            f.writelines(book_lines[idx])
        line_count = len(book_lines[idx])
        print(f"  {filename}: {line_count} lines")

    print(f"\nDone. {len(BOOK_MAP)} files written to {OUTDIR}/")

if __name__ == '__main__':
    main()
