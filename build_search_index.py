#!/usr/bin/env python3
"""
Build a compact JSON search index from v0 (original paragraph) text files.

Output: data/search_index.json
Format:
{
  "books": ["1 Nephi", "2 Nephi", ...],
  "bookIds": ["1nephi", "2nephi", ...],
  "verses": [
    {"b": 0, "c": 1, "v": 1, "t": "I, Nephi, having been born..."},
    ...
  ]
}

Usage: python3 build_search_index.py
"""
import json, os, re
from pathlib import Path

V0_DIR = Path(__file__).resolve().parent / 'data' / 'text-files' / 'v0-bofm-original'

# Ordered list: (bookId, displayName, v0Filename)
BOOKS = [
    ('1nephi',          '1 Nephi',          '1_Nephi.txt'),
    ('2nephi',          '2 Nephi',          '2_Nephi.txt'),
    ('jacob',           'Jacob',            'Jacob.txt'),
    ('enos',            'Enos',             'Enos.txt'),
    ('jarom',           'Jarom',            'Jarom.txt'),
    ('omni',            'Omni',             'Omni.txt'),
    ('words-of-mormon', 'Words of Mormon',  'Words_of_Mormon.txt'),
    ('mosiah',          'Mosiah',           'Mosiah.txt'),
    ('alma',            'Alma',             'Alma.txt'),
    ('helaman',         'Helaman',          'Helaman.txt'),
    ('3nephi',          '3 Nephi',          '3_Nephi.txt'),
    ('4nephi',          '4 Nephi',          '4_Nephi.txt'),
    ('mormon',          'Mormon',           'Mormon.txt'),
    ('ether',           'Ether',            'Ether.txt'),
    ('moroni',          'Moroni',           'Moroni.txt'),
]


def parse_v0_file(filepath):
    """Parse a v0 text file into list of (chapter, verse, text) tuples."""
    verses = []
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    for block in text.strip().split('\n\n'):
        lines = block.strip().split('\n')
        if not lines:
            continue
        header = lines[0].strip()
        # v0 format: "1 Nephi 1:1" or "Alma 5:3" — extract chapter:verse
        m = re.match(r'.+\s+(\d+):(\d+)$', header)
        if not m:
            continue
        ch = int(m.group(1))
        vs = int(m.group(2))
        # Join remaining lines into single paragraph
        para = ' '.join(l.strip() for l in lines[1:] if l.strip())
        if para:
            verses.append((ch, vs, para))
    return verses


def main():
    books = []
    book_ids = []
    all_verses = []

    for book_idx, (bid, display_name, filename) in enumerate(BOOKS):
        fpath = V0_DIR / filename
        if not fpath.exists():
            print(f"  WARNING: {fpath} not found, skipping {display_name}")
            continue

        books.append(display_name)
        book_ids.append(bid)
        verses = parse_v0_file(fpath)
        print(f"  {display_name}: {len(verses)} verses")

        for ch, vs, text in verses:
            all_verses.append({
                'b': book_idx,
                'c': ch,
                'v': vs,
                't': text,
            })

    index = {
        'books': books,
        'bookIds': book_ids,
        'verses': all_verses,
    }

    outpath = Path(__file__).resolve().parent / 'data' / 'search_index.json'
    os.makedirs(outpath.parent, exist_ok=True)
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, separators=(',', ':'))

    size_kb = outpath.stat().st_size / 1024
    print(f"\n  Total: {len(all_verses)} verses across {len(books)} books")
    print(f"  Output: {outpath} ({size_kb:.0f} KB)")


if __name__ == '__main__':
    main()
