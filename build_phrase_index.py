#!/usr/bin/env python3
"""
Build a phrase-level index of direct quotations from KJV Bible text
that appear in Book of Mormon verses.

Reads Hardy's biblical references JSON, looks up verse texts from
lds-scriptures.txt, performs phrase matching with normalized text,
and outputs results to hardy_phrase_index.json.
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from bom_abbreviations import parse_bom_ref, ABBREV_TO_ID


# Mapping from Hardy's abbreviations to full book names as they appear in lds-scriptures.txt
HARDY_ABBREV_TO_NAME = {
    '1 Ne': '1 Nephi',
    '2 Ne': '2 Nephi',
    '3 Ne': '3 Nephi',
    '4 Ne': '4 Nephi',
    'Jac': 'Jacob',
    'Enos': 'Enos',
    'Jar': 'Jarom',
    'Omni': 'Omni',
    'WoM': 'Words of Mormon',
    'Mos': 'Mosiah',
    'Al': 'Alma',
    'Hel': 'Helaman',
    'Morm': 'Mormon',
    'Eth': 'Ether',
    'Ether': 'Ether',
    'Moro': 'Moroni',
}


def normalize_text(text):
    """Normalize text for phrase matching: lowercase, remove punctuation, keep spaces."""
    # Remove punctuation but keep spaces
    text = re.sub(r'[^\w\s]', ' ', text, flags=re.UNICODE)
    # Lowercase
    text = text.lower()
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def get_words(text):
    """Split text into words."""
    return text.split()


def find_phrase_matches(bible_text, bom_text, min_words=3):
    """
    Find longest matching phrases between Bible and BoM text.

    Returns list of dicts: {"start": char_offset, "end": char_offset, "text": original_text}
    Character offsets are into the ORIGINAL (non-normalized) BoM text.
    """
    if not bible_text or not bom_text:
        return []

    # Normalize for matching
    bible_norm = normalize_text(bible_text)
    bom_norm = normalize_text(bom_text)

    bible_words = get_words(bible_norm)
    bom_words = get_words(bom_norm)

    if not bible_words or not bom_words:
        return []

    # Create a set of all n-grams in Bible text for quick lookup
    bible_ngrams = set()
    for n in range(1, len(bible_words) + 1):
        for i in range(len(bible_words) - n + 1):
            bible_ngrams.add(tuple(bible_words[i:i+n]))

    # For each position in BoM text, find longest matching phrase
    matches = []
    bom_word_positions = []  # Map from word index to char position in original text

    # Build word position map
    current_pos = 0
    for i, word in enumerate(bom_words):
        # Find the word in the original normalized text
        word_start = bom_norm.find(word, current_pos)
        bom_word_positions.append(word_start)
        current_pos = word_start + len(word)

    # Find matches using a different approach:
    # For each word in BoM, check if it and following words form a phrase in Bible
    matched_bom_words = set()  # Track which BoM words we've already matched

    for bom_start_idx in range(len(bom_words)):
        if bom_start_idx in matched_bom_words:
            continue

        # Try to find longest matching phrase starting at this position
        best_match_len = 0
        for length in range(min(len(bom_words) - bom_start_idx, len(bible_words)), min_words - 1, -1):
            phrase = tuple(bom_words[bom_start_idx:bom_start_idx + length])
            if phrase in bible_ngrams:
                best_match_len = length
                break

        if best_match_len >= min_words:
            # Record this match
            # Map back to character positions in original BoM text
            word_start_idx = bom_start_idx
            word_end_idx = bom_start_idx + best_match_len - 1

            # Find character positions in normalized text
            char_start_norm = bom_word_positions[word_start_idx]
            # Find end position: after the last word of the match
            if word_end_idx + 1 < len(bom_word_positions):
                char_end_norm = bom_word_positions[word_end_idx + 1]
            else:
                char_end_norm = len(bom_norm)

            # Now map back to character positions in ORIGINAL text
            # This is tricky because we removed punctuation
            # We need to find where this phrase appears in the original text
            phrase_text_norm = ' '.join(bom_words[word_start_idx:word_end_idx + 1])

            # Simple approach: find the first occurrence of this phrase in the original
            # after normalizing character-by-character
            # Actually, let's use a smarter approach: expand from normalized positions

            # For now, let's use a pattern matching approach
            # Create a regex that matches the phrase allowing for punctuation variations
            phrase_pattern = r'\b' + r'\s+'.join(re.escape(w) for w in bom_words[word_start_idx:word_end_idx + 1]) + r'\b'
            phrase_match = re.search(phrase_pattern, bom_text, re.IGNORECASE)

            if phrase_match:
                matched_text = bom_text[phrase_match.start():phrase_match.end()]
                matches.append({
                    "start": phrase_match.start(),
                    "end": phrase_match.end(),
                    "text": matched_text
                })
                # Mark words as matched
                for idx in range(word_start_idx, word_end_idx + 1):
                    matched_bom_words.add(idx)

    return matches


def parse_bible_ref(ref_str):
    """
    Parse a Bible reference string like "Genesis 2.17" or "Genesis 3.4-5" or "1 Corinthians 13.8, 13"
    Returns a list of (book, chapter, verse) tuples.
    """
    # Use dots from Hardy format, convert to colons for lookup
    ref_str = ref_str.strip()

    # Split on the first digit to separate book name from chapter:verse
    match = re.match(r'^(.+?)\s+(\d+)\.(.+)$', ref_str)
    if not match:
        return []

    book = match.group(1)
    try:
        chapter = int(match.group(2))
    except ValueError:
        return []

    verse_str = match.group(3).strip()
    results = []

    # Parse comma-separated verse groups
    for segment in verse_str.split(','):
        segment = segment.strip()
        if not segment:
            continue

        # Check for range (e.g., "4-5")
        if '-' in segment:
            range_parts = segment.split('-', 1)
            try:
                start = int(range_parts[0].strip())
                end = int(range_parts[1].strip())
                for v in range(start, end + 1):
                    results.append((book, chapter, v))
            except ValueError:
                continue
        else:
            try:
                results.append((book, chapter, int(segment)))
            except ValueError:
                continue

    return results


def load_scripture_text(scripture_file):
    """
    Load lds-scriptures.txt into a dict.
    Key: "Book Chapter:Verse" (normalized format)
    Value: verse text
    """
    scripture_dict = {}

    with open(scripture_file, 'r', encoding='utf-8') as f:
        for line_no, line in enumerate(f, 1):
            line = line.rstrip('\n\r')
            if not line.strip():
                continue

            # Format: "Book Chapter:Verse     Text" (multiple spaces separator)
            # Use lazy match to capture everything up to 2+ spaces
            match = re.match(r'^(.+?)\s{2,}(.*)$', line)
            if not match:
                continue

            ref, text = match.group(1).strip(), match.group(2)
            # ref is like "Genesis 1:1" or "1 Nephi 2:3" or "Words of Mormon 1:1"
            scripture_dict[ref] = text

    return scripture_dict


def convert_hardy_bible_ref_to_scripture_key(hardy_ref):
    """
    Convert Hardy format "Genesis 2.17" to scripture key format "Genesis 2:17"
    """
    return hardy_ref.replace('.', ':')


def get_bom_book_name_from_id(book_id):
    """Get the full Book of Mormon book name from site book_id."""
    id_to_name = {v: k for k, v in ABBREV_TO_ID.items()}

    # Map from book_id to full name
    bom_id_to_name = {
        '1nephi': '1 Nephi',
        '2nephi': '2 Nephi',
        '3nephi': '3 Nephi',
        '4nephi': '4 Nephi',
        'jacob': 'Jacob',
        'enos': 'Enos',
        'jarom': 'Jarom',
        'omni': 'Omni',
        'words-of-mormon': 'Words of Mormon',
        'mosiah': 'Mosiah',
        'alma': 'Alma',
        'helaman': 'Helaman',
        'mormon': 'Mormon',
        'ether': 'Ether',
        'moroni': 'Moroni',
    }

    return bom_id_to_name.get(book_id, '')


def build_phrase_index(hardy_data_file, scripture_file, output_file):
    """Main function to build the phrase index."""

    print(f"Loading scripture text from {scripture_file}...")
    scripture_dict = load_scripture_text(scripture_file)
    print(f"  Loaded {len(scripture_dict)} verses")

    print(f"\nLoading Hardy data from {hardy_data_file}...")
    with open(hardy_data_file, 'r', encoding='utf-8') as f:
        hardy_data = json.load(f)

    # Filter for quotations only
    quotations = [e for e in hardy_data.get('entries', []) if e.get('type') == 'quotation']
    print(f"  Found {len(quotations)} quotations")

    # Build phrase index
    phrase_index = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

    stats = {
        'total_quotations': len(quotations),
        'matched': 0,
        'unmatched_bible_lookup': 0,
        'unmatched_bom_lookup': 0,
        'no_phrase_match': 0,
        'successful_matches': [],
    }

    print("\nProcessing quotations...")
    for idx, quotation in enumerate(quotations, 1):
        if idx % 20 == 0:
            print(f"  {idx}/{len(quotations)}...")

        bible_ref_hardy = quotation.get('bible_ref', '')
        bom_ref_hardy = quotation.get('bom_ref', '')

        # Parse BoM reference
        bom_refs = parse_bom_ref(bom_ref_hardy)
        if not bom_refs:
            stats['unmatched_bom_lookup'] += 1
            continue

        # Parse Bible reference
        bible_refs = parse_bible_ref(bible_ref_hardy)
        if not bible_refs:
            stats['unmatched_bible_lookup'] += 1
            continue

        # Look up Bible verse text
        bible_texts = []
        for book, chapter, verse in bible_refs:
            scripture_key = f"{book} {chapter}:{verse}"
            if scripture_key in scripture_dict:
                bible_texts.append(scripture_dict[scripture_key])
            else:
                # Try without the book prefix in case it's partially in the file
                found = False
                for key in scripture_dict:
                    if key.endswith(f"{chapter}:{verse}") and book in key:
                        bible_texts.append(scripture_dict[key])
                        found = True
                        break
                if not found:
                    # Still not found
                    pass

        if not bible_texts:
            stats['unmatched_bible_lookup'] += 1
            continue

        # Combine Bible texts (for ranges)
        combined_bible_text = ' '.join(bible_texts)

        # For each BoM reference, look up and match
        for book_id, chapter, verse in bom_refs:
            bom_book_name = get_bom_book_name_from_id(book_id)
            scripture_key = f"{bom_book_name} {chapter}:{verse}"

            if scripture_key not in scripture_dict:
                stats['unmatched_bom_lookup'] += 1
                continue

            bom_text = scripture_dict[scripture_key]

            # Perform phrase matching
            matches = find_phrase_matches(combined_bible_text, bom_text, min_words=3)

            if not matches:
                stats['no_phrase_match'] += 1
                continue

            # Add to phrase index
            phrase_index[book_id][str(chapter)][str(verse)] = {
                "bible_ref": bible_ref_hardy,
                "matches": matches
            }

            stats['matched'] += 1
            stats['successful_matches'].append({
                'bible_ref': bible_ref_hardy,
                'bom_ref': bom_ref_hardy,
                'match_count': len(matches)
            })

    print("\n=== Statistics ===")
    print(f"Total quotations processed: {stats['total_quotations']}")
    print(f"Quotations with at least one match: {len(stats['successful_matches'])}")
    print(f"Total match instances (verses × matches): {stats['matched']}")
    print(f"Unmatched (Bible lookup failed): {stats['unmatched_bible_lookup']}")
    print(f"Unmatched (BoM lookup failed): {stats['unmatched_bom_lookup']}")
    print(f"Unmatched (no phrase match found): {stats['no_phrase_match']}")
    success_quotations = len(stats['successful_matches'])
    print(f"Quotation success rate: {success_quotations / stats['total_quotations'] * 100:.1f}%")

    # Sample successful matches
    print("\nSample successful matches:")
    for match in stats['successful_matches'][:5]:
        print(f"  {match['bible_ref']} → {match['bom_ref']} ({match['match_count']} phrase(s))")

    # Convert defaultdict to regular dict for JSON serialization
    output_data = {}
    for book_id, chapters in phrase_index.items():
        output_data[book_id] = {}
        for chapter, verses in chapters.items():
            output_data[book_id][chapter] = {}
            for verse, entry in verses.items():
                output_data[book_id][chapter][verse] = entry

    # Additional stats
    total_bom_verses_with_matches = len([v for book in output_data.values() for ch in book.values() for v in ch.values()])
    total_phrase_matches = sum(len(v.get('matches', [])) for book in output_data.values() for ch in book.values() for v in ch.values())

    print(f"\nOutput Summary:")
    print(f"  BoM verses with phrase matches: {total_bom_verses_with_matches}")
    print(f"  Total phrase matches: {total_phrase_matches}")
    print(f"  Average phrases per verse: {total_phrase_matches / total_bom_verses_with_matches:.1f}")

    print(f"\nWriting phrase index to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print("Done!")


if __name__ == '__main__':
    base_path = Path('/sessions/compassionate-dreamy-faraday/mnt/readers-bofm')

    hardy_data_file = base_path / 'data' / 'hardy_biblical_references.json'
    scripture_file = base_path / 'lds-scriptures.txt'
    output_file = base_path / 'data' / 'hardy_phrase_index.json'

    build_phrase_index(hardy_data_file, scripture_file, output_file)
