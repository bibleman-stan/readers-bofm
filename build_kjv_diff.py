#!/usr/bin/env python3
"""
Generate a word-level diff between KJV Bible verses and their Book of Mormon
parallel verses for injection into HTML at build time.

Reads from lds-scriptures.txt and outputs to data/kjv_diff_index.json
"""

import json
import re
from difflib import SequenceMatcher
from collections import defaultdict

# Known parallel passages: (bom_book_name_in_file, bom_chapter, kjv_book_name_in_file, kjv_chapter)
PARALLEL_CHAPTERS = [
    # 1 Nephi — Isaiah
    ("1 Nephi", 20, "Isaiah", 48),
    ("1 Nephi", 21, "Isaiah", 49),
    # 2 Nephi — Isaiah
    ("2 Nephi", 7, "Isaiah", 50),
    ("2 Nephi", 8, "Isaiah", 51),  # also includes 52:1-2
    ("2 Nephi", 12, "Isaiah", 2),
    ("2 Nephi", 13, "Isaiah", 3),
    ("2 Nephi", 14, "Isaiah", 4),
    ("2 Nephi", 15, "Isaiah", 5),
    ("2 Nephi", 16, "Isaiah", 6),
    ("2 Nephi", 17, "Isaiah", 7),
    ("2 Nephi", 18, "Isaiah", 8),
    ("2 Nephi", 19, "Isaiah", 9),
    ("2 Nephi", 20, "Isaiah", 10),
    ("2 Nephi", 21, "Isaiah", 11),
    ("2 Nephi", 22, "Isaiah", 12),
    ("2 Nephi", 23, "Isaiah", 13),
    ("2 Nephi", 24, "Isaiah", 14),
    # 3 Nephi — Sermon on the Mount (Matthew)
    ("3 Nephi", 12, "Matthew", 5),
    ("3 Nephi", 13, "Matthew", 6),
    ("3 Nephi", 14, "Matthew", 7),
    # 3 Nephi — Isaiah/Malachi
    ("3 Nephi", 22, "Isaiah", 54),
    ("3 Nephi", 24, "Malachi", 3),
    ("3 Nephi", 25, "Malachi", 4),
]

# Book IDs for the JSON output
BOOK_ID_MAP = {
    "1 Nephi": "1nephi",
    "2 Nephi": "2nephi",
    "3 Nephi": "3nephi",
    "Isaiah": "isaiah",
    "Matthew": "matthew",
    "Malachi": "malachi",
}


def parse_scripture_file(filepath):
    """
    Parse the lds-scriptures.txt file and return a dict keyed by (book, chapter, verse).

    Format: Book Chapter:Verse<MULTIPLE_SPACES>Text
    """
    scriptures = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\r\n')
            if not line.strip():
                continue

            # Split on multiple spaces (at least 2)
            parts = re.split(r'\s{2,}', line, 1)
            if len(parts) != 2:
                continue

            ref, text = parts
            ref = ref.strip()
            text = text.strip()

            # Parse the reference: "Book Chapter:Verse"
            # Handle multi-word book names (e.g., "1 Nephi", "3 Nephi", etc.)
            match = re.match(r'^(.+?)\s+(\d+):(\d+)$', ref)
            if not match:
                continue

            book, chapter, verse = match.groups()
            chapter = int(chapter)
            verse = int(verse)

            scriptures[(book, chapter, verse)] = text

    return scriptures


def tokenize_words(text):
    """
    Tokenize text into words. Preserve punctuation attached to words.
    Return list of words.
    """
    # Split on whitespace
    words = text.split()
    return words


def word_diff(kjv_text, bom_text):
    """
    Perform word-level diff between KJV and BoM text.
    Returns a list of dicts with keys: type, text
    where type is "equal", "delete", or "insert"
    """
    kjv_words = tokenize_words(kjv_text)
    bom_words = tokenize_words(bom_text)

    # For matching, use lowercase versions
    kjv_words_lower = [w.lower() for w in kjv_words]
    bom_words_lower = [w.lower() for w in bom_words]

    # Use SequenceMatcher to find matching blocks
    matcher = SequenceMatcher(isjunk=None, a=kjv_words_lower, b=bom_words_lower)
    blocks = matcher.get_matching_blocks()

    # Build diff result
    diff_result = []
    bom_idx = 0
    kjv_idx = 0

    for block in blocks:
        kjv_start, bom_start, size = block

        # Handle text before this matching block
        # First, any deletions (in KJV but not in BoM before this block)
        if kjv_idx < kjv_start:
            deleted_words = kjv_words[kjv_idx:kjv_start]
            diff_result.append({
                "type": "delete",
                "text": " ".join(deleted_words)
            })

        # Then, any insertions (in BoM but not in KJV before this block)
        if bom_idx < bom_start:
            inserted_words = bom_words[bom_idx:bom_start]
            diff_result.append({
                "type": "insert",
                "text": " ".join(inserted_words)
            })

        # Add the matching block (use BoM text to preserve its casing)
        if size > 0:
            equal_words = bom_words[bom_start:bom_start + size]
            diff_result.append({
                "type": "equal",
                "text": " ".join(equal_words)
            })

        kjv_idx = kjv_start + size
        bom_idx = bom_start + size

    return diff_result


def get_book_id(book_name):
    """Get the standardized book ID from the book name."""
    return BOOK_ID_MAP.get(book_name, book_name.lower())


def build_kjv_diff_index(scriptures):
    """
    Build the KJV diff index by processing all parallel verses.
    Returns a dict with structure: {book_id: {chapter: {verse: {kjv_ref, diff}}}}
    """
    index = defaultdict(lambda: defaultdict(dict))

    stats = {
        "total_verses": 0,
        "verses_with_diff": 0,
        "verses_identical": 0,
        "total_words_equal": 0,
        "total_words_deleted": 0,
        "total_words_inserted": 0,
    }

    for bom_book, bom_chap, kjv_book, kjv_chap in PARALLEL_CHAPTERS:
        # For each verse in the BoM chapter
        max_verse = 0
        for (book, chap, verse), text in scriptures.items():
            if book == bom_book and chap == bom_chap:
                max_verse = max(max_verse, verse)

        for bom_verse in range(1, max_verse + 1):
            bom_key = (bom_book, bom_chap, bom_verse)
            kjv_key = (kjv_book, kjv_chap, bom_verse)

            # Check if both versions exist
            if bom_key not in scriptures:
                continue
            if kjv_key not in scriptures:
                # BoM verse has no corresponding KJV verse (BoM addition)
                continue

            bom_text = scriptures[bom_key]
            kjv_text = scriptures[kjv_key]

            stats["total_verses"] += 1

            # Compute word-level diff
            diff = word_diff(kjv_text, bom_text)

            # Check if identical
            is_identical = (len(diff) == 1 and diff[0]["type"] == "equal")

            if is_identical:
                stats["verses_identical"] += 1
            else:
                stats["verses_with_diff"] += 1

            # Count words
            for item in diff:
                word_count = len(item["text"].split())
                if item["type"] == "equal":
                    stats["total_words_equal"] += word_count
                elif item["type"] == "delete":
                    stats["total_words_deleted"] += word_count
                elif item["type"] == "insert":
                    stats["total_words_inserted"] += word_count

            # Store in index
            book_id = get_book_id(bom_book)
            kjv_ref = f"{kjv_book} {kjv_chap}:{bom_verse}"

            index[book_id][str(bom_chap)][str(bom_verse)] = {
                "kjv_ref": kjv_ref,
                "diff": diff
            }

    return dict(index), stats


def main():
    print("Parsing lds-scriptures.txt...")
    scriptures = parse_scripture_file('/sessions/compassionate-dreamy-faraday/mnt/readers-bofm/lds-scriptures.txt')
    print(f"Loaded {len(scriptures)} scripture verses")

    print("Building KJV diff index...")
    index, stats = build_kjv_diff_index(scriptures)

    # Convert defaultdicts to regular dicts for JSON serialization
    index_serializable = {}
    for book_id, chapters in index.items():
        index_serializable[book_id] = {}
        for chapter, verses in chapters.items():
            index_serializable[book_id][chapter] = dict(verses)

    # Write output
    output_path = '/sessions/compassionate-dreamy-faraday/mnt/readers-bofm/data/kjv_diff_index.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(index_serializable, f, indent=2, ensure_ascii=False)

    print(f"\nWrote index to {output_path}")

    # Print statistics
    print("\n=== Statistics ===")
    print(f"Total parallel verses processed: {stats['total_verses']}")
    print(f"Verses with differences: {stats['verses_with_diff']}")
    print(f"Identical verses: {stats['verses_identical']}")
    print(f"Total words equal: {stats['total_words_equal']}")
    print(f"Total words deleted (KJV only): {stats['total_words_deleted']}")
    print(f"Total words inserted (BoM only): {stats['total_words_inserted']}")

    # Print a few example diffs
    print("\n=== Example Diffs ===")
    example_count = 0
    for book_id, chapters in index.items():
        for chapter, verses in chapters.items():
            for verse, data in verses.items():
                if example_count >= 3:
                    break
                diff = data['diff']
                # Only show if there are actual differences
                has_diff = any(item['type'] != 'equal' for item in diff)
                if has_diff:
                    print(f"\n{book_id.upper()} {chapter}:{verse} → {data['kjv_ref']}")
                    for item in diff:
                        marker = ""
                        if item['type'] == 'equal':
                            marker = ""
                        elif item['type'] == 'delete':
                            marker = "[-] "
                        elif item['type'] == 'insert':
                            marker = "[+] "
                        print(f"  {marker}{item['text']}")
                    example_count += 1
            if example_count >= 3:
                break
        if example_count >= 3:
            break


if __name__ == '__main__':
    main()
