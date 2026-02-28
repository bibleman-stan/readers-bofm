#!/usr/bin/env python3
"""
Comprehensive script to extract verbal echoes from all Hardy biblical allusions.
Optimized to find meaningful phrases while avoiding too-generic matches.
"""

import json
import re
from collections import defaultdict
from typing import Dict, Tuple, Optional, List

BOOK_MAPPING = {
    "1 Ne": ("1nephi", "1 Nephi"),
    "2 Ne": ("2nephi", "2 Nephi"),
    "Jac": ("jacob", "Jacob"),
    "Enos": ("enos", "Enos"),
    "Jarom": ("jarom", "Jarom"),
    "Omni": ("omni", "Omni"),
    "WofM": ("wordsofmormon", "Words of Mormon"),
    "Mos": ("mosiah", "Mosiah"),
    "Al": ("alma", "Alma"),
    "Hel": ("helaman", "Helaman"),
    "3 Ne": ("3nephi", "3 Nephi"),
    "4 Ne": ("4nephi", "4 Nephi"),
    "Morm": ("mormon", "Mormon"),
    "Eth": ("ether", "Ether"),
    "Moro": ("moroni", "Moroni"),
}

# Phrases that are too generic/common to be meaningful
GENERIC_PHRASES = {
    "and it came to pass",
    "the lord",
    "and the",
    "that the",
    "and he",
    "of the",
    "in the",
    "it came to pass",
    "to the",
    "with the",
    "for the",
    "by the",
    "from the",
    "on the",
    "from heaven",
    "saith the lord",
    "thus saith the lord",
    "and all",
    "the spirit",
    "shall be",
}


def load_lds_scriptures() -> Tuple[Dict[str, Dict[int, Dict[int, str]]], Dict[str, Dict[int, Dict[int, str]]]]:
    """Load scripture texts."""
    kjv = defaultdict(lambda: defaultdict(dict))
    bom = defaultdict(lambda: defaultdict(dict))

    with open('data/lds-scriptures.txt', 'r') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line or line.isspace():
                continue

            match = re.match(r'^([^\s]+(?:\s+[^\s]+)*?)\s{2,}(.*)$', line)
            if not match:
                continue

            ref = match.group(1).strip()
            text = match.group(2).strip()

            if ':' not in ref:
                continue

            parts = ref.rsplit(':', 1)
            if len(parts) != 2:
                continue

            try:
                verse_num = int(parts[1])
            except ValueError:
                continue

            chapter_match = re.search(r'\s+(\d+)$', parts[0])
            if not chapter_match:
                continue

            chapter_num = int(chapter_match.group(1))
            book_name = parts[0][:chapter_match.start()].strip()

            bom_books = {
                '1 Nephi', '2 Nephi', 'Jacob', 'Enos', 'Jarom', 'Omni',
                'Words of Mormon', 'Mosiah', 'Alma', 'Helaman', '3 Nephi',
                '4 Nephi', 'Mormon', 'Ether', 'Moroni',
                'Joseph Smith--History', 'Articles of Faith'
            }

            if book_name in bom_books:
                bom[book_name][chapter_num][verse_num] = text
            else:
                kjv[book_name][chapter_num][verse_num] = text

    return kjv, bom


def get_verse_text(verses_dict: Dict, book: str, chapter: int, verse: int) -> Optional[str]:
    """Get verse text."""
    if book in verses_dict and chapter in verses_dict[book]:
        if verse in verses_dict[book][chapter]:
            return verses_dict[book][chapter][verse]
    return None


def normalize_text(text: str) -> str:
    """Normalize text for matching."""
    text = text.lower()
    # KJV variations
    text = re.sub(r'\b(hath|doth|saith|dost|wouldst|shouldst|hast)\b', '', text)
    text = re.sub(r'eth\b', 's', text)
    text = re.sub(r"'", '', text)
    text = re.sub(r'[,;:!?]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_phrases_from_text(text: str) -> List[Tuple[str, int]]:
    """
    Extract meaningful phrases, prioritizing longer/more distinctive ones.
    Returns list of (phrase, priority_score) where higher score = better.
    """
    normalized = normalize_text(text)
    words = normalized.split()

    phrases_with_scores = []

    # Try all n-grams from longer to shorter
    for length in range(min(10, len(words)), 2, -1):  # Down to 3-word phrases
        for i in range(len(words) - length + 1):
            phrase = ' '.join(words[i:i+length])

            # Skip generic phrases
            if phrase in GENERIC_PHRASES:
                continue

            # Skip if too short in characters
            if len(phrase) < 12:
                continue

            # Skip if mostly function words
            func_words = {'the', 'and', 'of', 'to', 'in', 'a', 'that', 'is', 'it', 'was', 'at', 'or', 'for'}
            content_words = [w for w in phrase.split() if w not in func_words and len(w) > 2]
            if len(content_words) < 1:
                continue

            # Calculate priority: longer phrases with more content words score higher
            priority = (len(phrase) * 2) + (len(content_words) * 10)
            phrases_with_scores.append((phrase, priority))

    # Deduplicate and sort by priority
    seen = set()
    unique = []
    for p, score in phrases_with_scores:
        if p not in seen:
            seen.add(p)
            unique.append((p, score))

    unique.sort(key=lambda x: x[1], reverse=True)
    return unique


def find_match_in_text(search_phrase: str, target_text: str) -> Optional[Tuple[int, int, str]]:
    """
    Find search phrase in target text (normalized).
    Returns (start_pos, end_pos, original_matched_text) or None.
    """
    normalized_target = normalize_text(target_text)
    normalized_phrase = normalize_text(search_phrase)

    if not normalized_phrase or not normalized_target:
        return None

    idx = normalized_target.find(normalized_phrase)
    if idx == -1:
        return None

    # Map back to original text
    target_words = target_text.split()
    normalized_words = normalized_target.split()

    # Count words up to match position
    words_before = normalized_target[:idx].strip()
    word_count_before = len(words_before.split()) if words_before else 0

    search_word_count = len(normalized_phrase.split())
    matched_words = target_words[word_count_before:word_count_before + search_word_count]

    if not matched_words:
        return None

    matched_text = ' '.join(matched_words)

    # Character positions
    start_pos = len(' '.join(target_words[:word_count_before]))
    if word_count_before > 0:
        start_pos += 1

    end_pos = start_pos + len(matched_text)

    return (start_pos, end_pos, matched_text)


def find_best_echo(kjv_text: str, bom_text: str) -> Optional[Tuple[str, int, int]]:
    """
    Find best verbal echo. Strongly prefer longer phrases over short fragments.
    """
    kjv_phrases = extract_phrases_from_text(kjv_text)
    bom_phrases = extract_phrases_from_text(bom_text)

    best_match = None
    best_score = 0

    # Try each KJV phrase in BoM
    for phrase, priority in kjv_phrases:
        result = find_match_in_text(phrase, bom_text)
        if result:
            _, _, matched_text = result
            # Score heavily favors longer phrases
            word_count = len(matched_text.split())
            char_score = len(matched_text)
            # Exponential boost for longer phrases to avoid short fragments
            length_boost = (word_count ** 1.5) * 10
            score = length_boost + char_score
            if score > best_score:
                best_match = result
                best_score = score

    # Also try BoM phrases in KJV
    for phrase, priority in bom_phrases:
        result = find_match_in_text(phrase, kjv_text)
        if result:
            _, _, matched_text = result
            word_count = len(matched_text.split())
            char_score = len(matched_text)
            length_boost = (word_count ** 1.5) * 10
            score = length_boost + char_score
            if score > best_score:
                best_match = result
                best_score = score

    if best_match:
        _, _, matched_text = best_match

        # Clean punctuation for evaluation
        clean_matched = matched_text.rstrip(';:,.\'"')
        word_count = len(clean_matched.split())
        char_count = len(clean_matched)

        # Require at least 4 words (no more short fragments)
        if word_count >= 4:
            return best_match

    return None


def parse_bom_ref(bom_ref: str) -> Optional[Tuple[str, int, int]]:
    """Parse BoM reference."""
    match = re.match(
        r'^(\d*\s*)(1 Ne|2 Ne|Jac|Enos|Jarom|Omni|WofM|Mos|Al|Hel|3 Ne|4 Ne|Morm|Eth|Moro)\s+(\d+)\.(\d+)',
        bom_ref.strip()
    )
    if match:
        abbrev = match.group(2)
        chapter = int(match.group(3))
        verse = int(match.group(4))
        if abbrev in BOOK_MAPPING:
            _, book_name = BOOK_MAPPING[abbrev]
            return (book_name, chapter, verse)
    return None


def parse_bible_ref(bible_ref: str) -> List[Tuple[str, int, int]]:
    """Parse Bible reference."""
    refs = []
    parts = bible_ref.split(',')

    for i, part in enumerate(parts):
        part = part.strip()
        if i == 0:
            match = re.match(r'^([A-Za-z\s]+?)\s+(\d+)\.(\d+)$', part)
            if match:
                book = match.group(1).strip()
                chapter = int(match.group(2))
                verse = int(match.group(3))
                refs.append((book, chapter, verse))
        else:
            match = re.match(r'^(\d+)$', part)
            if match and refs:
                verse = int(match.group(1))
                book, chapter, _ = refs[0]
                refs.append((book, chapter, verse))

    return refs


def main():
    print("Loading scripture texts...")
    kjv, bom = load_lds_scriptures()
    print(f"  KJV loaded: {sum(len(ch) for book in kjv.values() for ch in book.values())} verses")
    print(f"  BoM loaded: {sum(len(ch) for book in bom.values() for ch in book.values())} verses")

    print("Loading Hardy references...")
    with open('data/hardy_biblical_references.json', 'r') as f:
        hardy_data = json.load(f)
    hardy_entries = hardy_data['entries']

    print("Loading existing phrase index...")
    with open('data/hardy_phrase_index.json', 'r') as f:
        phrase_index = json.load(f)

    phrase_index_keys = set()
    for book_id in phrase_index:
        for chapter in phrase_index[book_id]:
            for verse in phrase_index[book_id][chapter]:
                phrase_index_keys.add((book_id, int(chapter), int(verse)))

    print(f"  Already-matched verses: {len(phrase_index_keys)}")
    print(f"\nProcessing {len(hardy_entries)} allusions...\n")

    results = []
    skipped = 0
    matched = 0
    no_match = 0
    errors = 0

    for idx, entry in enumerate(hardy_entries):
        if (idx + 1) % 250 == 0:
            pct = 100.0 * (idx + 1) / len(hardy_entries)
            print(f"  {idx + 1}/{len(hardy_entries)} ({pct:.1f}%) - matched: {matched}, thematic: {no_match}")

        bible_ref = entry.get('bible_ref', '')
        bom_ref = entry.get('bom_ref', '')

        bom_parse = parse_bom_ref(bom_ref)
        if not bom_parse:
            errors += 1
            continue

        bom_book_name, bom_chapter, bom_verse = bom_parse

        book_id = None
        for _, (bid, bname) in BOOK_MAPPING.items():
            if bname == bom_book_name:
                book_id = bid
                break

        if not book_id:
            errors += 1
            continue

        if (book_id, bom_chapter, bom_verse) in phrase_index_keys:
            skipped += 1
            continue

        bible_refs = parse_bible_ref(bible_ref)
        if not bible_refs:
            errors += 1
            continue

        bible_book, bible_chapter, bible_verse = bible_refs[0]
        kjv_text = get_verse_text(kjv, bible_book, bible_chapter, bible_verse)
        bom_text = get_verse_text(bom, bom_book_name, bom_chapter, bom_verse)

        if not kjv_text or not bom_text:
            errors += 1
            continue

        result = {
            "bible_ref": bible_ref,
            "bom_ref": bom_ref,
            "bom_book": book_id,
            "bom_chapter": bom_chapter,
            "bom_verse": bom_verse,
            "kjv_text": kjv_text,
            "bom_text": bom_text,
            "extracted_phrase": None,
            "match_type": "thematic",
            "already_matched": False,
            "notes": ""
        }

        match_result = find_best_echo(kjv_text, bom_text)
        if match_result:
            _, _, matched_text = match_result
            result["extracted_phrase"] = matched_text
            result["match_type"] = "verbal"
            matched += 1
        else:
            no_match += 1

        results.append(result)

    print(f"\n" + "="*70)
    print("FINAL RESULTS SUMMARY")
    print("="*70)
    print(f"Total allusions in Hardy: {len(hardy_entries)}")
    print(f"Total processed: {len(results)}")
    print(f"Already-matched (skipped): {skipped}")
    print(f"New verbal matches FOUND: {matched}")
    print(f"Marked as thematic (no echo): {no_match}")
    print(f"Parsing errors: {errors}")

    print("\nSaving extractions...")
    with open('data/allusion_extractions_all.json', 'w') as f:
        json.dump(results, f, indent=2)

    # Show samples
    print("\n" + "="*70)
    print("SAMPLE VERBAL MATCHES (first 10)")
    print("="*70)
    verbal = [r for r in results if r['match_type'] == 'verbal']
    for i, r in enumerate(verbal[:10]):
        phrase = r['extracted_phrase']
        print(f"\n{i+1}. {r['bible_ref']} -> {r['bom_ref']}")
        print(f"   \"{phrase}\"")
        print(f"   ({len(phrase)} chars, {len(phrase.split())} words)")


if __name__ == '__main__':
    main()
