#!/usr/bin/env python3
"""
Analyze the first 50 allusions and extract BoM phrases that echo biblical sources.
"""

import json
import re
from pathlib import Path
import sys

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from bom_abbreviations import parse_bom_ref, ABBREV_TO_ID

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
TEXT_FILES_DIR = BASE_DIR / 'text-files' / 'v0-bofm-original'

def load_hardy_references():
    """Load the Hardy biblical references data."""
    with open(DATA_DIR / 'hardy_biblical_references.json', 'r') as f:
        data = json.load(f)
    return data['entries']

def load_kjv_text():
    """Load KJV Bible text from lds-scriptures.txt"""
    kjv = {}
    with open(DATA_DIR / 'lds-scriptures.txt', 'r', encoding='utf-8') as f:
        for line in f:
            # Don't strip - need to preserve the spacing pattern
            line = line.rstrip('\r\n')
            if not line.strip():
                continue

            # Format: "Genesis 1:1     Text here" with 5+ spaces
            # Find the first verse reference pattern (Book Ch:V)
            match = re.match(r'^([A-Za-z\s]+?\s+\d+:\d+)\s{5,}(.+)$', line)
            if match:
                ref = match.group(1).strip()
                text = match.group(2)

                # Normalize chapter:verse to chapter.verse for consistency
                ref = ref.replace(':', '.')
                kjv[ref] = text
    return kjv

def parse_bible_ref(bible_ref):
    """Parse a Bible reference string like 'Genesis 1.1' or 'Genesis 1.1, 27'"""
    import re

    bible_ref = bible_ref.strip()

    # Match pattern like "Book Chapter.Verse_List"
    match = re.match(r'^(.+?)\s+(\d+)\.(.+)$', bible_ref)
    if not match:
        return []

    book = match.group(1).strip()
    chapter = int(match.group(2))
    verse_spec = match.group(3).strip()

    results = []

    # Parse verse_spec: could be "1", "1, 27", "10-12", "1, 3, 5", etc.
    # Split on commas to get segments
    for segment in verse_spec.split(','):
        segment = segment.strip()
        if not segment:
            continue

        if '-' in segment:
            # Range: "10-12"
            try:
                parts = segment.split('-')
                start_v = int(parts[0].strip())
                end_v = int(parts[1].strip())
                for v in range(start_v, end_v + 1):
                    results.append(f"{book} {chapter}:{v}")
            except (ValueError, IndexError):
                continue
        elif '.' in segment:
            # New chapter: "2.3"
            try:
                ch, v = segment.split('.')
                results.append(f"{book} {int(ch)}:{int(v)}")
            except ValueError:
                continue
        else:
            # Single verse: "27"
            try:
                v = int(segment)
                results.append(f"{book} {chapter}:{v}")
            except ValueError:
                continue

    return results

def get_bom_book_filename(book_id):
    """Convert book_id like '1nephi' to filename like '1_Nephi.txt'"""
    mapping = {
        '1nephi': '1_Nephi.txt',
        '2nephi': '2_Nephi.txt',
        '3nephi': '3_Nephi.txt',
        '4nephi': '4_Nephi.txt',
        'jacob': 'Jacob.txt',
        'enos': 'Enos.txt',
        'jarom': 'Jarom.txt',
        'omni': 'Omni.txt',
        'words-of-mormon': 'Words_of_Mormon.txt',
        'mosiah': 'Mosiah.txt',
        'alma': 'Alma.txt',
        'helaman': 'Helaman.txt',
        'mormon': 'Mormon.txt',
        'ether': 'Ether.txt',
        'moroni': 'Moroni.txt',
    }
    return mapping.get(book_id)

def load_bom_verses():
    """Load BoM verses from text files."""
    bom = {}

    for book_id, filename in [
        ('1nephi', '1_Nephi.txt'),
        ('2nephi', '2_Nephi.txt'),
        ('3nephi', '3_Nephi.txt'),
        ('4nephi', '4_Nephi.txt'),
        ('jacob', 'Jacob.txt'),
        ('enos', 'Enos.txt'),
        ('jarom', 'Jarom.txt'),
        ('omni', 'Omni.txt'),
        ('words-of-mormon', 'Words_of_Mormon.txt'),
        ('mosiah', 'Mosiah.txt'),
        ('alma', 'Alma.txt'),
        ('helaman', 'Helaman.txt'),
        ('mormon', 'Mormon.txt'),
        ('ether', 'Ether.txt'),
        ('moroni', 'Moroni.txt'),
    ]:
        filepath = TEXT_FILES_DIR / filename
        if not filepath.exists():
            print(f"Warning: {filename} not found")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Format is like "1 Nephi 1:1\ntext\n\n1 Nephi 1:2\ntext\n\n"
        # Split on double newline to get verses
        verses = content.split('\n\n')

        for verse_block in verses:
            lines = verse_block.strip().split('\n', 1)
            if len(lines) != 2:
                continue

            header = lines[0].strip()
            verse_text = lines[1].strip()

            # Parse header like "1 Nephi 1:1"
            # Match patterns like "Book Name C:V"
            match = re.match(r'^[\d\s\w]+?(\d+):(\d+)$', header)
            if match:
                chapter = int(match.group(1))
                verse = int(match.group(2))
                key = f"{book_id}_{chapter}_{verse}"
                bom[key] = verse_text

    return bom

def load_existing_phrase_index():
    """Load already-matched phrases from hardy_phrase_index.json"""
    phrase_index = {}
    filepath = DATA_DIR / 'hardy_phrase_index.json'
    if filepath.exists():
        with open(filepath, 'r') as f:
            data = json.load(f)
            phrase_index = data
    return phrase_index

def find_bom_text(book_id, chapter, verse, bom_verses):
    """Find the BoM text for a specific verse."""
    key = f"{book_id}_{chapter}_{verse}"
    return bom_verses.get(key, "")

def normalize_for_matching(text):
    """Normalize text for matching, handling common variations."""
    text = text.lower()
    # Replace plural/singular variants
    text = re.sub(r'\bheavens?\b', 'heaven', text)
    text = re.sub(r'\bCh?ild?ren?\b', 'child', text)
    text = re.sub(r'\bthey?\b', 'it', text)  # be careful with this
    text = ' '.join(text.split())  # normalize whitespace
    return text

def find_matching_phrases(kjv_text, bom_text):
    """Find phrases from KJV that appear in BoM text."""
    if not kjv_text or not bom_text:
        return None, "thematic"

    # Normalize for comparison (lowercase, remove extra spaces)
    kjv_normalized = normalize_for_matching(kjv_text)
    bom_normalized = normalize_for_matching(bom_text)

    # Check for exact full match first
    if kjv_normalized in bom_normalized:
        return kjv_text, "verbal"

    # Try to find key phrases (words that appear in both)
    kjv_words = set(kjv_normalized.split())
    bom_words = set(bom_normalized.split())

    common_words = kjv_words & bom_words
    if common_words and len(common_words) >= 2:
        # Try to find longest matching phrases (5+ words preferred, down to 3)
        kjv_tokens = kjv_text.split()
        best_phrase = None
        best_length = 0

        for i in range(len(kjv_tokens)):
            # Try lengths from longest down to 3 words
            for length in range(min(8, len(kjv_tokens) - i), 2, -1):
                phrase = ' '.join(kjv_tokens[i:i+length])
                phrase_normalized = normalize_for_matching(phrase)

                if phrase_normalized in bom_normalized:
                    # Found a match - keep the longest one
                    if length > best_length:
                        best_phrase = phrase
                        best_length = length

        if best_phrase:
            return best_phrase, "verbal"

        # If we have common words but can't find exact phrase, it's thematic
        return None, "thematic"

    return None, "thematic"

def main():
    print("Loading data...")
    entries = load_hardy_references()
    kjv_texts = load_kjv_text()
    bom_verses = load_bom_verses()
    phrase_index = load_existing_phrase_index()

    # Filter to allusions only
    allusions = [e for e in entries if e.get('type') == 'allusion']
    print(f"Total allusions: {len(allusions)}")

    # Process first 50
    results = []
    for idx, entry in enumerate(allusions[:50]):
        print(f"\n--- Allusion {idx + 1}/50 ---")
        bible_ref = entry.get('bible_ref', '')
        bom_ref = entry.get('bom_ref', '')

        print(f"Bible: {bible_ref}")
        print(f"BoM: {bom_ref}")

        # Parse BoM reference
        bom_refs = parse_bom_ref(bom_ref)
        if not bom_refs:
            print(f"Could not parse BoM ref: {bom_ref}")
            continue

        # Take the first parsed reference
        book_id, chapter, verse = bom_refs[0]

        # Parse Bible reference
        bible_refs = parse_bible_ref(bible_ref)
        kjv_text = ""
        if bible_refs:
            # Try with colon first, then replace with period if not found
            ref_with_colon = bible_refs[0]
            ref_with_period = ref_with_colon.replace(':', '.')
            kjv_text = kjv_texts.get(ref_with_period, "")

        print(f"KJV text: {kjv_text[:100]}")

        # Find BoM text
        bom_text = find_bom_text(book_id, chapter, verse, bom_verses)
        print(f"BoM text: {bom_text[:100] if bom_text else 'NOT FOUND'}")

        # Check if already in phrase index
        key = f"{book_id}_{chapter}_{verse}"
        already_matched = key in phrase_index

        # Find matching phrase
        extracted_phrase, match_type = find_matching_phrases(kjv_text, bom_text)

        result = {
            "bible_ref": bible_ref,
            "bom_ref": bom_ref,
            "bom_book": book_id,
            "bom_chapter": chapter,
            "bom_verse": verse,
            "kjv_text": kjv_text,
            "bom_text": bom_text,
            "extracted_phrase": extracted_phrase,
            "match_type": match_type,
            "already_matched": already_matched,
            "notes": ""
        }

        results.append(result)
        print(f"Extracted: {extracted_phrase}")
        print(f"Match type: {match_type}")
        print(f"Already matched: {already_matched}")

    # Save results
    output_path = DATA_DIR / 'allusion_extractions_batch1_2.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nSaved {len(results)} results to {output_path}")

if __name__ == '__main__':
    main()
