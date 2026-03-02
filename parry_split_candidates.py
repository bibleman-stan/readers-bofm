#!/usr/bin/env python3
"""Find sense-lines where Parry wants splits — practical approach.

Strategy: for each parallel structure, match Parry's fragments to our sense-lines.
When 2+ Parry fragments map to the SAME sense-line, that line needs splitting.

LOW-HANGING FRUIT filter:
- Line is long enough to split (>45 chars)
- The split point falls at natural punctuation (, ; :) or conjunction
- Both halves are meaningful (>12 chars each)
"""

import json
import re
import os

BASE = os.path.dirname(os.path.abspath(__file__))


def load_booklist():
    mapping = {}
    with open(os.path.join(BASE, 'booklist.txt')) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 2:
                mapping[parts[0]] = parts[1]
    return mapping


def load_sense_lines(filepath):
    verses = {}
    current_verse = 0
    current_lines = []
    with open(filepath, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\r\n')
            m = re.match(r'^=(\d+)=$', line.strip())
            if m:
                if current_verse > 0 and current_lines:
                    verses[current_verse] = current_lines
                current_verse = int(m.group(1))
                current_lines = []
            elif line.strip():
                current_lines.append(line.rstrip())
    if current_verse > 0 and current_lines:
        verses[current_verse] = current_lines
    return verses


def get_words(text):
    """Extract lowercase words from text."""
    return [w.lower() for w in re.findall(r"[a-zA-Z']+", text)]


def match_frag_to_line(frag_words, line_words):
    """Score how well a Parry fragment matches a sense-line. Returns (score, is_full_match)."""
    if not frag_words or not line_words:
        return 0, False

    # Count overlapping words
    overlap = sum(1 for w in frag_words if w in line_words)
    # Bonus for first-word match
    first_bonus = 2 if frag_words[0] == line_words[0] else 0
    score = overlap + first_bonus

    # Is this a full match (fragment covers most of the line)?
    coverage = overlap / max(len(frag_words), 1)
    is_full = coverage > 0.7 and abs(len(frag_words) - len(line_words)) < 3

    return score, is_full


def find_natural_split(sense_line, frag1_text, frag2_text):
    """Try to find where to split a sense-line based on two Parry fragments.

    frag1 should be the START of the line, frag2 the END.
    Returns (left, right) or None.
    """
    sl = sense_line.strip()
    f1_words = get_words(frag1_text)
    f2_words = get_words(frag2_text)

    if not f1_words or not f2_words:
        return None

    # Strategy: find where frag1 ends in the sense-line by matching words forward
    sl_words = get_words(sl)

    # Match frag1 words from the start
    matched_f1 = 0
    for i, fw in enumerate(f1_words):
        if i < len(sl_words) and fw == sl_words[i]:
            matched_f1 = i + 1
        elif i < len(sl_words):
            # Try to recover from minor mismatches
            if i + 1 < len(f1_words) and i + 1 < len(sl_words) and f1_words[i + 1] == sl_words[i + 1]:
                matched_f1 = i + 1
                continue
            break

    if matched_f1 < 2:
        # Try frag2 from the end
        matched_f2 = 0
        for i in range(1, min(len(f2_words), len(sl_words)) + 1):
            if f2_words[-i] == sl_words[-i]:
                matched_f2 += 1
            else:
                break
        if matched_f2 >= 2:
            # Split at where frag2 starts
            split_word_idx = len(sl_words) - matched_f2
            matched_f1 = split_word_idx

    if matched_f1 < 2 or matched_f1 >= len(sl_words):
        return None

    # Find the character position in the original string after the matched_f1 words
    pos = _char_pos_after_words(sl, matched_f1)
    if pos is None:
        return None

    left = sl[:pos].rstrip()
    right = sl[pos:].lstrip()

    # Check minimum lengths
    if len(left) < 12 or len(right) < 12:
        return None

    return left, right


def _char_pos_after_words(text, n_words):
    """Find character position after the nth word in text."""
    count = 0
    i = 0
    while i < len(text) and count < n_words:
        # Skip non-alpha
        while i < len(text) and not text[i].isalpha():
            i += 1
        if i >= len(text):
            break
        # Skip word
        while i < len(text) and (text[i].isalpha() or text[i] == "'"):
            i += 1
        count += 1

    if count != n_words:
        return None

    # Now we're right after the nth word. Look for a natural break:
    # Skip to the next natural break point (punctuation + space, or just space before conjunction)
    scan = i
    while scan < len(text) and scan < i + 5:
        if text[scan] in ',;:' and scan + 1 < len(text) and text[scan + 1] == ' ':
            return scan + 2
        if text[scan] == ' ':
            return scan + 1
        scan += 1

    return i


def is_good_split(left, right):
    """Check if the proposed split makes sense for readability."""
    left = left.strip()
    right = right.strip()

    # Ends with punctuation = strong break
    ends_punct = left[-1] in ',;:—' if left else False

    # Starts with conjunction/break word
    rwords = right.split()
    first_word = rwords[0].lower() if rwords else ''
    break_words = {'and', 'but', 'for', 'or', 'nor', 'yet', 'that', 'which',
                   'who', 'whom', 'whose', 'where', 'when', 'because',
                   'therefore', 'wherefore', 'nevertheless', 'notwithstanding',
                   'according', 'even', 'yea', 'behold', 'unto', 'inasmuch',
                   'save', 'except', 'after', 'before', 'until', 'since'}
    starts_break = first_word in break_words

    return ends_punct or starts_break


def main():
    booklist = load_booklist()
    with open(os.path.join(BASE, 'data', 'parallel_index.json')) as f:
        parallel_idx = json.load(f)

    candidates = []

    book_order = ['1nephi', '2nephi', 'jacob', 'enos', 'jarom', 'omni',
                  'words-of-mormon', 'mosiah', 'alma', 'helaman',
                  '3nephi', '4nephi', 'mormon', 'ether', 'moroni']

    for book_id in book_order:
        if book_id not in parallel_idx or book_id not in booklist:
            continue

        src_path = os.path.join(BASE, 'text-files', 'v2-mine', booklist[book_id])
        if not os.path.exists(src_path):
            continue

        verses = load_sense_lines(src_path)
        book_data = parallel_idx[book_id]

        for ch_str, structures in sorted(book_data.items(), key=lambda x: int(x[0])):
            for struct in structures:
                # Group Parry lines by verse
                by_verse = {}
                for pline in struct['lines']:
                    by_verse.setdefault(pline['verse'], []).append(pline)

                for vnum, plines in by_verse.items():
                    if vnum not in verses:
                        continue
                    sl_list = verses[vnum]

                    # For each sense-line, check if multiple Parry fragments match it
                    for li, sl in enumerate(sl_list):
                        if len(sl.strip()) < 45:
                            continue

                        sl_words = get_words(sl)
                        if len(sl_words) < 5:
                            continue

                        # Score each Parry fragment against this sense-line
                        matches = []
                        for pi, pl in enumerate(plines):
                            fw = get_words(pl['text_fragment'])
                            score, is_full = match_frag_to_line(fw, sl_words)
                            if score >= max(2, len(fw) * 0.4):
                                matches.append((pi, pl, score, is_full))

                        # If 2+ fragments match this line AND none is a full match,
                        # we have a split candidate
                        if len(matches) >= 2:
                            # Check if any single fragment covers the whole line
                            any_full = any(m[3] for m in matches)
                            if any_full:
                                continue

                            # Take the first two matches as the split pair
                            m1, m2 = matches[0], matches[1]
                            result = find_natural_split(sl, m1[1]['text_fragment'], m2[1]['text_fragment'])
                            if result is None:
                                continue
                            left, right = result
                            if not is_good_split(left, right):
                                continue

                            candidates.append({
                                'book': book_id,
                                'chapter': int(ch_str),
                                'verse': vnum,
                                'line_idx': li,
                                'original': sl,
                                'left': left,
                                'right': right,
                                'type': struct['type'],
                                'frag1': m1[1]['text_fragment'],
                                'frag1_level': m1[1]['level'],
                                'frag2': m2[1]['text_fragment'],
                                'frag2_level': m2[1]['level'],
                            })

    # Dedup by (book, chapter, verse, line_idx)
    seen = set()
    unique = []
    for c in candidates:
        key = (c['book'], c['chapter'], c['verse'], c['line_idx'])
        if key not in seen:
            seen.add(key)
            unique.append(c)
    candidates = unique

    # Report
    print(f"\n{'='*80}")
    print(f"PARRY SENSE-LINE SPLIT CANDIDATES — LOW-HANGING FRUIT")
    print(f"{'='*80}")
    print(f"\nCriteria: 2+ Parry fragments match one sense-line (>45 chars),")
    print(f"          natural break point (punctuation/conjunction), both halves >12 chars")
    print(f"Total candidates: {len(candidates)}")
    print()

    by_book = {}
    for c in candidates:
        by_book.setdefault(c['book'], []).append(c)

    print(f"{'BOOK':<20s} {'COUNT':>6s}")
    print(f"{'-'*26}")
    for bid in book_order:
        if bid in by_book:
            print(f"{bid:<20s} {len(by_book[bid]):>6d}")
    print()

    for c in candidates:
        print(f"--- {c['book']} {c['chapter']}:{c['verse']} (line {c['line_idx']+1}) [{c['type']}] ---")
        print(f"  CURRENT:  {c['original']}")
        print(f"  SPLIT →   {c['left']}")
        print(f"            {c['right']}")
        print(f"  Parry {c['frag1_level']}: {c['frag1']}")
        print(f"  Parry {c['frag2_level']}: {c['frag2']}")
        print()

    outpath = os.path.join(BASE, 'parry_split_candidates.txt')
    with open(outpath, 'w') as f:
        f.write(f"PARRY SENSE-LINE SPLIT CANDIDATES — LOW-HANGING FRUIT\n")
        f.write(f"Total: {len(candidates)}\n\n")
        for c in candidates:
            f.write(f"--- {c['book']} {c['chapter']}:{c['verse']} (line {c['line_idx']+1}) [{c['type']}] ---\n")
            f.write(f"  CURRENT:  {c['original']}\n")
            f.write(f"  SPLIT →   {c['left']}\n")
            f.write(f"            {c['right']}\n\n")
    print(f"Report written to {outpath}")


if __name__ == '__main__':
    main()
