#!/usr/bin/env python3
"""
Build a geographic index from the geographic verses spreadsheet.

Processes the bom_geographic_verses.xlsx file and creates a JSON index
structured by book, chapter, and verse for build-time injection.
"""

import json
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd


# Book name to site ID mapping
BOOK_ID_MAP = {
    "1 Nephi": "1nephi",
    "2 Nephi": "2nephi",
    "3 Nephi": "3nephi",
    "4 Nephi": "4nephi",
    "Jacob": "jacob",
    "Enos": "enos",
    "Jarom": "jarom",
    "Omni": "omni",
    "Words of Mormon": "words-of-mormon",
    "Mosiah": "mosiah",
    "Alma": "alma",
    "Helaman": "helaman",
    "Mormon": "mormon",
    "Ether": "ether",
    "Moroni": "moroni",
}


def parse_reference(reference_str):
    """
    Parse a reference string like "Alma 22:27" or "Helaman 3:3-4".

    Returns:
        list of tuples: [(book_id, chapter, verse), ...]
    """
    if not reference_str or not isinstance(reference_str, str):
        return []

    reference_str = reference_str.strip()

    # Try to match the pattern: "Book Name chapter:verse" or "Book Name chapter:verse-verse"
    # Handle multi-word book names like "Words of Mormon" and "3 Nephi"
    match = re.match(r"^(.+?)\s+(\d+):(\d+)(?:-(\d+))?$", reference_str)
    if not match:
        print(f"Warning: Could not parse reference: {reference_str}")
        return []

    book_name = match.group(1).strip()
    chapter = int(match.group(2))
    verse_start = int(match.group(3))
    verse_end = int(match.group(4)) if match.group(4) else verse_start

    # Look up the book ID
    if book_name not in BOOK_ID_MAP:
        print(f"Warning: Unknown book name: {book_name}")
        return []

    book_id = BOOK_ID_MAP[book_name]

    # Expand verse ranges
    results = []
    for verse in range(verse_start, verse_end + 1):
        results.append((book_id, chapter, verse))

    return results


def build_index(xlsx_path, output_path):
    """
    Build the geographic index from the spreadsheet.

    Args:
        xlsx_path: Path to the input xlsx file
        output_path: Path to write the output JSON file
    """
    # Read the spreadsheet
    df = pd.read_excel(xlsx_path, sheet_name='Geographic Verses')

    print(f"Read {len(df)} rows from {xlsx_path}")

    # Initialize the index structure
    index = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    # Track statistics
    total_entries = 0
    entries_by_book = defaultdict(int)
    entries_by_category = defaultdict(int)
    skipped_rows = 0

    # Process each row
    for idx, row in df.iterrows():
        reference = row.get('Reference')
        extract = row.get('Textual Extract')
        category = row.get('Category')
        sub_category = row.get('Sub-Category')

        # Skip rows with missing required fields
        if not reference or not extract or pd.isna(reference) or pd.isna(extract):
            skipped_rows += 1
            continue

        # Parse the reference
        parsed = parse_reference(reference)
        if not parsed:
            skipped_rows += 1
            continue

        # Create the entry
        entry = {
            "extract": str(extract).strip(),
            "category": str(category).strip().lower(),
        }
        if sub_category and not pd.isna(sub_category):
            entry["sub_category"] = str(sub_category).strip()

        # Add entry for each verse in the range
        for book_id, chapter, verse in parsed:
            index[book_id][str(chapter)][str(verse)].append(entry)
            total_entries += 1
            entries_by_book[book_id] += 1
            entries_by_category[entry["category"]] += 1

    # Convert defaultdicts to regular dicts for JSON serialization
    final_index = {}
    for book_id, chapters in index.items():
        final_index[book_id] = {}
        for chapter, verses in chapters.items():
            final_index[book_id][chapter] = {}
            for verse, entries in verses.items():
                final_index[book_id][chapter][verse] = entries

    # Write the output
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(final_index, f, indent=2)

    print(f"\nWrote index to {output_path}")
    print(f"\n=== Statistics ===")
    print(f"Total entries: {total_entries}")
    print(f"Skipped rows: {skipped_rows}")
    print(f"\nEntries per book:")
    for book_id in sorted(entries_by_book.keys()):
        print(f"  {book_id}: {entries_by_book[book_id]}")
    print(f"\nEntries per category:")
    for category in sorted(entries_by_category.keys()):
        print(f"  {category}: {entries_by_category[category]}")


if __name__ == "__main__":
    input_path = Path(__file__).parent / "data" / "bom_geographic_verses.xlsx"
    output_path = Path(__file__).parent / "data" / "geo_index.json"

    build_index(str(input_path), str(output_path))
