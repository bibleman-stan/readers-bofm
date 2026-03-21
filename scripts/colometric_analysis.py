#!/usr/bin/env python3
"""
Colometric Analysis of Book of Mormon Sense-Line Corpus
Computes per-chapter metrics across all 15 books for linguistic/stylometric research.
Outputs CSV to research/colometric_metrics.csv
"""

import re, os, csv, sys
from pathlib import Path
from collections import defaultdict

# Book definitions: (book_id, filename, total_chapters)
BOOKS = [
    ("1nephi", "01-1_nephi-2020-sb-v2.txt", 22),
    ("2nephi", "02-2_nephi-2020-sb-v2.txt", 33),
    ("jacob", "03-jacob-2020-sb-v2.txt", 7),
    ("enos", "04-enos-2020-sb-v2.txt", 1),
    ("jarom", "05-jarom-2020-sb-v2.txt", 1),
    ("omni", "06-omni-2020-sb-v2.txt", 1),
    ("words-of-mormon", "07-words_of_mormon-2020-sb-v2.txt", 1),
    ("mosiah", "08-mosiah-2020-sb-v2.txt", 29),
    ("alma", "09-alma-2020-sb-v2.txt", 63),
    ("helaman", "10-helaman-2020-sb-v2.txt", 16),
    ("3nephi", "11-3_nephi-2020-sb-v2.txt", 30),
    ("4nephi", "12-4_nephi-2020-sb-v2.txt", 1),
    ("mormon", "13-mormon-2020-sb-v2.txt", 9),
    ("ether", "14-ether-2020-sb-v2.txt", 15),
    ("moroni", "15-moroni-2020-sb-v2.txt", 10),
]

REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "data" / "text-files" / "v2-mine"

def parse_chapters(filepath):
    """Parse a v2 source file into chapters, each containing verses with lines."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    chapters = {}
    current_chapter = None
    current_verse = None
    verse_pattern = re.compile(r'^(\d+):(\d+)$')

    for raw_line in text.split('\n'):
        line = raw_line.rstrip()
        m = verse_pattern.match(line)
        if m:
            ch, vs = int(m.group(1)), int(m.group(2))
            current_chapter = ch
            current_verse = f"{ch}:{vs}"
            if ch not in chapters:
                chapters[ch] = {'verses': {}, 'lines': []}
            chapters[ch]['verses'][current_verse] = []
        elif line.strip() == '':
            continue
        elif current_chapter is not None:
            chapters[current_chapter]['lines'].append(line)
            if current_verse:
                chapters[current_chapter]['verses'][current_verse].append(line)

    return chapters

def count_words(text):
    return len(text.split())

def analyze_chapter(book_id, chapter_num, chapter_data):
    """Compute all metrics for a single chapter."""
    lines = chapter_data['lines']
    verses = chapter_data['verses']

    if not lines:
        return None

    all_text = ' '.join(lines)
    total_words = count_words(all_text)
    total_lines = len(lines)
    total_verses = len(verses)

    if total_words == 0 or total_lines == 0:
        return None

    # Line length metrics
    line_word_counts = [count_words(l) for l in lines]
    line_char_counts = [len(l) for l in lines]
    avg_words_per_line = total_words / total_lines
    avg_chars_per_line = sum(line_char_counts) / total_lines
    max_line_chars = max(line_char_counts)
    min_line_chars = min(line_char_counts) if line_char_counts else 0
    lines_per_verse = total_lines / total_verses if total_verses > 0 else 0

    # Short lines (potential parallel stacking indicator)
    short_lines = sum(1 for wc in line_word_counts if wc <= 5)
    short_line_ratio = short_lines / total_lines

    # AICTP count
    aictp_pattern = re.compile(r'(And |Now |For |Wherefore |But )?[Ii]t came to pass', re.IGNORECASE)
    aictp_count = len(aictp_pattern.findall(all_text))
    aictp_rate = aictp_count / total_verses if total_verses > 0 else 0

    # Future AICTP ("shall/will come to pass")
    future_aictp = len(re.findall(r'shall come to pass|will come to pass', all_text, re.IGNORECASE))

    # "I say unto you" count
    isay_count = len(re.findall(r'I say unto you', all_text))
    isay_per_1k = (isay_count / total_words) * 1000 if total_words > 0 else 0

    # "Caused that" count
    caused_that_count = len(re.findall(r'caused? that', all_text, re.IGNORECASE))
    caused_that_per_1k = (caused_that_count / total_words) * 1000 if total_words > 0 else 0

    # "Began to" count
    began_to_count = len(re.findall(r'began to', all_text, re.IGNORECASE))
    began_to_per_1k = (began_to_count / total_words) * 1000 if total_words > 0 else 0

    # Rhetorical questions
    question_count = all_text.count('?')
    question_per_verse = question_count / total_verses if total_verses > 0 else 0

    # "Wo unto" count
    wo_count = len(re.findall(r'[Ww]o unto', all_text))

    # "Behold" count
    behold_count = len(re.findall(r'[Bb]ehold', all_text))
    behold_per_1k = (behold_count / total_words) * 1000 if total_words > 0 else 0

    # "Verily" count (Christ's voice marker)
    verily_count = len(re.findall(r'[Vv]erily', all_text))

    # "And thus we see" (Mormon editorial marker)
    thus_we_see = len(re.findall(r'[Aa]nd thus we see', all_text))

    # "My brethren" / "my beloved brethren" (sermonic address)
    brethren_count = len(re.findall(r'my (?:beloved )?brethren', all_text, re.IGNORECASE))

    # Parallel stacking indicator: consecutive lines under 6 words
    consec_short = 0
    max_consec_short = 0
    for wc in line_word_counts:
        if wc <= 6:
            consec_short += 1
            max_consec_short = max(max_consec_short, consec_short)
        else:
            consec_short = 0

    return {
        'book': book_id,
        'chapter': chapter_num,
        'total_verses': total_verses,
        'total_lines': total_lines,
        'total_words': total_words,
        'avg_words_per_line': round(avg_words_per_line, 2),
        'avg_chars_per_line': round(avg_chars_per_line, 1),
        'max_line_chars': max_line_chars,
        'min_line_chars': min_line_chars,
        'lines_per_verse': round(lines_per_verse, 2),
        'short_line_ratio': round(short_line_ratio, 3),
        'max_consec_short_lines': max_consec_short,
        'aictp_count': aictp_count,
        'aictp_rate': round(aictp_rate, 3),
        'future_aictp': future_aictp,
        'isay_count': isay_count,
        'isay_per_1k': round(isay_per_1k, 2),
        'caused_that_count': caused_that_count,
        'caused_that_per_1k': round(caused_that_per_1k, 2),
        'began_to_count': began_to_count,
        'began_to_per_1k': round(began_to_per_1k, 2),
        'question_count': question_count,
        'question_per_verse': round(question_per_verse, 3),
        'wo_count': wo_count,
        'behold_count': behold_count,
        'behold_per_1k': round(behold_per_1k, 2),
        'verily_count': verily_count,
        'thus_we_see': thus_we_see,
        'brethren_count': brethren_count,
    }

def main():
    all_results = []

    for book_id, filename, total_chapters in BOOKS:
        filepath = SOURCE_DIR / filename
        if not filepath.exists():
            print(f"  WARNING: {filepath} not found, skipping")
            continue

        print(f"Processing {book_id}...")
        chapters = parse_chapters(filepath)

        for ch_num in sorted(chapters.keys()):
            result = analyze_chapter(book_id, ch_num, chapters[ch_num])
            if result:
                all_results.append(result)

    # Write CSV
    output_path = REPO_ROOT / "research" / "colometric_metrics.csv"
    if all_results:
        fieldnames = list(all_results[0].keys())
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\nWrote {len(all_results)} chapter rows to {output_path}")

    # Print summary by book
    print(f"\n{'='*80}")
    print(f"{'BOOK':<18} {'CH':>3} {'VERSES':>6} {'LINES':>6} {'WORDS':>7} {'W/L':>5} {'L/V':>5} {'AICTP%':>7} {'ISAY/1k':>8} {'CAUSED/1k':>10} {'?/V':>5} {'BEHOLD/1k':>10}")
    print(f"{'-'*80}")

    book_stats = defaultdict(lambda: {
        'chapters': 0, 'verses': 0, 'lines': 0, 'words': 0,
        'aictp': 0, 'isay': 0, 'caused': 0, 'questions': 0,
        'behold': 0, 'wo': 0, 'verily': 0, 'thus_we_see': 0,
        'began_to': 0, 'brethren': 0
    })

    for r in all_results:
        b = book_stats[r['book']]
        b['chapters'] += 1
        b['verses'] += r['total_verses']
        b['lines'] += r['total_lines']
        b['words'] += r['total_words']
        b['aictp'] += r['aictp_count']
        b['isay'] += r['isay_count']
        b['caused'] += r['caused_that_count']
        b['questions'] += r['question_count']
        b['behold'] += r['behold_count']
        b['wo'] += r['wo_count']
        b['verily'] += r['verily_count']
        b['thus_we_see'] += r['thus_we_see']
        b['began_to'] += r['began_to_count']
        b['brethren'] += r['brethren_count']

    for book_id, _, _ in BOOKS:
        b = book_stats[book_id]
        if b['verses'] == 0:
            continue
        aictp_pct = (b['aictp'] / b['verses']) * 100
        isay_1k = (b['isay'] / b['words']) * 1000 if b['words'] > 0 else 0
        caused_1k = (b['caused'] / b['words']) * 1000 if b['words'] > 0 else 0
        q_per_v = b['questions'] / b['verses']
        behold_1k = (b['behold'] / b['words']) * 1000 if b['words'] > 0 else 0
        w_per_l = b['words'] / b['lines'] if b['lines'] > 0 else 0
        l_per_v = b['lines'] / b['verses'] if b['verses'] > 0 else 0

        print(f"{book_id:<18} {b['chapters']:>3} {b['verses']:>6} {b['lines']:>6} {b['words']:>7} "
              f"{w_per_l:>5.1f} {l_per_v:>5.2f} {aictp_pct:>6.1f}% {isay_1k:>7.2f} {caused_1k:>9.2f} "
              f"{q_per_v:>5.2f} {behold_1k:>9.2f}")

    # Grand totals
    gt = defaultdict(int)
    for b in book_stats.values():
        for k, v in b.items():
            gt[k] += v

    print(f"{'-'*80}")
    aictp_pct = (gt['aictp'] / gt['verses']) * 100 if gt['verses'] > 0 else 0
    isay_1k = (gt['isay'] / gt['words']) * 1000 if gt['words'] > 0 else 0
    caused_1k = (gt['caused'] / gt['words']) * 1000 if gt['words'] > 0 else 0
    q_per_v = gt['questions'] / gt['verses'] if gt['verses'] > 0 else 0
    behold_1k = (gt['behold'] / gt['words']) * 1000 if gt['words'] > 0 else 0
    w_per_l = gt['words'] / gt['lines'] if gt['lines'] > 0 else 0
    l_per_v = gt['lines'] / gt['verses'] if gt['verses'] > 0 else 0

    print(f"{'TOTAL':<18} {gt['chapters']:>3} {gt['verses']:>6} {gt['lines']:>6} {gt['words']:>7} "
          f"{w_per_l:>5.1f} {l_per_v:>5.2f} {aictp_pct:>6.1f}% {isay_1k:>7.2f} {caused_1k:>9.2f} "
          f"{q_per_v:>5.2f} {behold_1k:>9.2f}")

    # Voice marker summary
    print(f"\n{'='*80}")
    print("VOICE MARKER SUMMARY (per 1,000 words)")
    print(f"{'BOOK':<18} {'AICTP':>6} {'ISAY':>6} {'CAUSED':>7} {'BEGAN':>6} {'BEHOLD':>7} {'VERILY':>7} {'THUSWS':>7} {'WO':>4} {'BRETH':>6} {'?rate':>6}")
    print(f"{'-'*80}")

    for book_id, _, _ in BOOKS:
        b = book_stats[book_id]
        if b['words'] == 0:
            continue
        w = b['words']
        print(f"{book_id:<18} {b['aictp']/w*1000:>6.2f} {b['isay']/w*1000:>6.2f} {b['caused']/w*1000:>7.2f} "
              f"{b['began_to']/w*1000:>6.2f} {b['behold']/w*1000:>7.2f} {b['verily']/w*1000:>7.2f} "
              f"{b['thus_we_see']/w*1000:>7.2f} {b['wo']:>4} {b['brethren']/w*1000:>6.2f} "
              f"{b['questions']/b['verses']:>6.3f}")

if __name__ == '__main__':
    main()
