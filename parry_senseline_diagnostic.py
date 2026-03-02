#!/usr/bin/env python3
"""
Diagnostic script to compare Parry's line breaks to sense-line breaks.

Analyzes the parallel_index.json structures and compares Parry's text fragments
to our sense-line boundaries from the v2 text files.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple, Set


class SenseLineLoader:
    """Load and manage sense-line text files."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.books = {}
        self.load_booklist()

    def load_booklist(self):
        """Load book ID to filename mapping."""
        booklist_path = self.base_path / "booklist.txt"
        self.book_mapping = {}

        with open(booklist_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    book_id = parts[0]
                    filename = parts[1]
                    self.book_mapping[book_id] = filename

    def load_book(self, book_id: str) -> Dict:
        """Load a book's sense lines. Returns dict keyed by chapter."""
        if book_id in self.books:
            return self.books[book_id]

        if book_id not in self.book_mapping:
            print(f"Warning: No mapping for {book_id}")
            return {}

        filename = self.book_mapping[book_id]
        filepath = self.base_path / filename

        if not filepath.exists():
            print(f"Warning: File not found: {filepath}")
            return {}

        book_data = {}
        current_verse = None
        current_lines = []

        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.rstrip('\n')

                # Check for verse marker (format: "ch:v")
                verse_match = re.match(r'^(\d+):(\d+)$', line.strip())
                if verse_match:
                    # Save previous verse
                    if current_verse:
                        chapter, verse = current_verse
                        if chapter not in book_data:
                            book_data[chapter] = {}
                        book_data[chapter][verse] = current_lines

                    chapter = verse_match.group(1)
                    verse = verse_match.group(2)
                    current_verse = (chapter, verse)
                    current_lines = []
                elif line.strip() and current_verse:
                    current_lines.append(line)

        # Save last verse
        if current_verse:
            chapter, verse = current_verse
            if chapter not in book_data:
                book_data[chapter] = {}
            book_data[chapter][verse] = current_lines

        self.books[book_id] = book_data
        return book_data

    def get_sense_lines(self, book_id: str, chapter: str, verse: str) -> List[str]:
        """Get sense lines for a specific chapter:verse."""
        book_data = self.load_book(book_id)

        if chapter not in book_data:
            return []
        if verse not in book_data[chapter]:
            return []

        return book_data[chapter][verse]


class TextMatcher:
    """Match Parry's text fragments to sense-lines."""

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for matching."""
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[—–-]', '-', text)
        text = text.strip()
        return text

    @staticmethod
    def word_overlap(text1: str, text2: str) -> float:
        """Calculate word overlap between two texts."""
        words1 = set(TextMatcher.normalize_text(text1).split())
        words2 = set(TextMatcher.normalize_text(text2).split())

        if not words1 or not words2:
            return 0.0

        overlap = len(words1 & words2)
        total = len(words1 | words2)

        return overlap / total if total > 0 else 0.0

    @staticmethod
    def find_substring_position(fragment: str, text: str) -> Tuple[int, int]:
        """Find where a fragment appears in text (by word position).
        Returns (start_word_idx, end_word_idx) or (-1, -1) if not found.
        """
        norm_frag = TextMatcher.normalize_text(fragment)
        norm_text = TextMatcher.normalize_text(text)

        frag_words = norm_frag.split()
        text_words = norm_text.split()

        if not frag_words:
            return (-1, -1)

        for i in range(len(text_words) - len(frag_words) + 1):
            if text_words[i:i+len(frag_words)] == frag_words:
                return (i, i + len(frag_words))

        return (-1, -1)


class DiagnosticAnalyzer:
    """Analyze alignment between Parry and sense-line breaks."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.loader = SenseLineLoader(base_path)
        self.results = {
            'perfect': [],
            'partial': [],
            'unmatched': []
        }
        self.split_patterns = defaultdict(list)

    def analyze_parallel_structure(self, book_id: str, chapter: str,
                                   structure: Dict) -> None:
        """Analyze a single parallel structure."""
        verse_start = str(structure.get('verse_start', ''))
        verse_end = str(structure.get('verse_end', ''))
        lines = structure.get('lines', [])

        if not lines:
            return

        # Collect all sense-lines for the verse range
        sense_lines_dict = {}  # {verse: [lines]}

        for verse_num in range(int(verse_start), int(verse_end) + 1):
            verse_str = str(verse_num)
            sense_lines = self.loader.get_sense_lines(book_id, chapter, verse_str)
            if sense_lines:
                sense_lines_dict[verse_str] = sense_lines

        if not sense_lines_dict:
            for line_item in lines:
                self.results['unmatched'].append({
                    'book': book_id,
                    'chapter': chapter,
                    'verse_start': verse_start,
                    'verse_end': verse_end,
                    'parry_fragment': line_item.get('text_fragment', ''),
                    'reason': 'No sense-lines found for this verse range'
                })
            return

        # Analyze each Parry fragment
        for line_item in lines:
            parry_fragment = line_item.get('text_fragment', '').strip()
            parry_verse = str(line_item.get('verse', ''))

            if not parry_fragment:
                continue

            match_result = self._find_best_match(
                parry_fragment,
                sense_lines_dict,
                parry_verse
            )

            if match_result['type'] == 'perfect':
                self.results['perfect'].append({
                    'book': book_id,
                    'chapter': chapter,
                    'verse': parry_verse,
                    'parry_fragment': parry_fragment,
                    'matched_line': match_result['matched_line']
                })
            elif match_result['type'] == 'partial':
                split_info = match_result.get('split_info', {})
                self.results['partial'].append({
                    'book': book_id,
                    'chapter': chapter,
                    'verse': parry_verse,
                    'parry_fragment': parry_fragment,
                    'full_sense_line': match_result['full_sense_line'],
                    'split_position': split_info.get('position', ''),
                    'left_part': split_info.get('left_part', ''),
                    'right_part': split_info.get('right_part', '')
                })

                # Track pattern
                pattern = split_info.get('pattern', 'unknown')
                self.split_patterns[pattern].append({
                    'book': book_id,
                    'chapter': chapter,
                    'verse': parry_verse
                })
            else:
                self.results['unmatched'].append({
                    'book': book_id,
                    'chapter': chapter,
                    'verse': parry_verse,
                    'parry_fragment': parry_fragment,
                    'reason': 'No good match found'
                })

    def _find_best_match(self, parry_fragment: str,
                         sense_lines_dict: Dict,
                         parry_verse: str) -> Dict:
        """Find the best matching sense-line for a Parry fragment."""

        # Try to find in the specific verse first
        if parry_verse in sense_lines_dict:
            result = self._check_against_verse_lines(
                parry_fragment,
                sense_lines_dict[parry_verse]
            )
            if result['type'] in ['perfect', 'partial']:
                return result

        # Try all verses in the range
        for verse_key in sorted(sense_lines_dict.keys(),
                               key=lambda x: int(x)):
            result = self._check_against_verse_lines(
                parry_fragment,
                sense_lines_dict[verse_key]
            )
            if result['type'] in ['perfect', 'partial']:
                return result

        return {'type': 'unmatched'}

    def _check_against_verse_lines(self, parry_fragment: str,
                                   sense_lines: List[str]) -> Dict:
        """Check a Parry fragment against a list of sense-lines."""

        best_overlap = 0.0
        best_result = {'type': 'unmatched'}

        for i, sense_line in enumerate(sense_lines):
            # Check for perfect match (entire sense-line)
            norm_sense = TextMatcher.normalize_text(sense_line)
            norm_parry = TextMatcher.normalize_text(parry_fragment)

            if norm_sense == norm_parry:
                return {
                    'type': 'perfect',
                    'matched_line': sense_line
                }

            # Check for partial match
            overlap = TextMatcher.word_overlap(parry_fragment, sense_line)

            if overlap > 0.5:  # Significant overlap
                # Try to find where the fragment falls in this line
                split_info = self._find_split_point(
                    parry_fragment,
                    sense_line
                )

                if split_info:
                    return {
                        'type': 'partial',
                        'matched_line_idx': i,
                        'full_sense_line': sense_line,
                        'split_info': split_info
                    }

            # Track best overlap for potential match
            if overlap > best_overlap:
                best_overlap = overlap
                if overlap > 0.3:
                    best_result = {
                        'type': 'partial',
                        'matched_line_idx': i,
                        'full_sense_line': sense_line,
                        'split_info': self._find_split_point(
                            parry_fragment,
                            sense_line
                        )
                    }

        return best_result if best_result['type'] == 'partial' else {'type': 'unmatched'}

    def _find_split_point(self, parry_fragment: str,
                          full_sense_line: str) -> Dict:
        """Find where Parry wants to split within a sense-line."""

        start_pos, end_pos = TextMatcher.find_substring_position(
            parry_fragment,
            full_sense_line
        )

        if start_pos == -1:
            return {}

        words = full_sense_line.split()

        # Find split pattern near the end of the fragment
        if end_pos < len(words):
            split_word = words[end_pos] if end_pos < len(words) else ''

            left_part = ' '.join(words[:end_pos])
            right_part = ' '.join(words[end_pos:])

            # Identify pattern
            pattern = self._identify_split_pattern(split_word)

            return {
                'position': end_pos,
                'split_word': split_word,
                'left_part': left_part,
                'right_part': right_part,
                'pattern': pattern
            }

        return {}

    @staticmethod
    def _identify_split_pattern(next_word: str) -> str:
        """Identify the pattern at a split point."""
        norm_word = TextMatcher.normalize_text(next_word)

        if norm_word.startswith('and'):
            return 'starts_with_and'
        elif norm_word.startswith(','):
            return 'starts_with_comma'
        elif ',' in norm_word:
            return 'contains_comma'
        elif ';' in norm_word:
            return 'contains_semicolon'
        else:
            return 'other'

    def analyze_all(self, index_path: Path) -> None:
        """Analyze the entire parallel index."""
        with open(index_path, 'r', encoding='utf-8') as f:
            index = json.load(f)

        total_structures = 0

        for book_id, chapters in index.items():
            for chapter, structures in chapters.items():
                for structure in structures:
                    total_structures += 1
                    self.analyze_parallel_structure(book_id, chapter, structure)

        print(f"Total structures analyzed: {total_structures}")

    def generate_report(self, output_path: Path) -> None:
        """Generate a diagnostic report."""

        perfect_count = len(self.results['perfect'])
        partial_count = len(self.results['partial'])
        unmatched_count = len(self.results['unmatched'])
        total = perfect_count + partial_count + unmatched_count

        report_lines = []

        report_lines.append("=" * 80)
        report_lines.append("PARRY vs SENSE-LINE DIAGNOSTIC REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")

        # Summary statistics
        report_lines.append("SUMMARY STATISTICS")
        report_lines.append("-" * 80)
        report_lines.append(f"Total structures analyzed: {total}")
        report_lines.append(f"Perfect alignment: {perfect_count} ({100*perfect_count/total:.1f}%)")
        report_lines.append(f"Partial alignment: {partial_count} ({100*partial_count/total:.1f}%)")
        report_lines.append(f"Unmatched: {unmatched_count} ({100*unmatched_count/total:.1f}%)")
        report_lines.append("")

        # Per-book breakdown
        report_lines.append("PER-BOOK BREAKDOWN")
        report_lines.append("-" * 80)

        book_stats = defaultdict(lambda: {'perfect': 0, 'partial': 0, 'unmatched': 0})

        for result in self.results['perfect']:
            book_stats[result['book']]['perfect'] += 1
        for result in self.results['partial']:
            book_stats[result['book']]['partial'] += 1
        for result in self.results['unmatched']:
            book_stats[result['book']]['unmatched'] += 1

        for book_id in sorted(book_stats.keys()):
            stats = book_stats[book_id]
            book_total = sum(stats.values())
            perfect_pct = 100 * stats['perfect'] / book_total if book_total > 0 else 0
            partial_pct = 100 * stats['partial'] / book_total if book_total > 0 else 0
            unmatched_pct = 100 * stats['unmatched'] / book_total if book_total > 0 else 0

            report_lines.append(f"{book_id:20} | Perfect: {stats['perfect']:4} ({perfect_pct:5.1f}%) | "
                              f"Partial: {stats['partial']:4} ({partial_pct:5.1f}%) | "
                              f"Unmatched: {stats['unmatched']:4} ({unmatched_pct:5.1f}%)")

        report_lines.append("")

        # Split patterns
        if self.split_patterns:
            report_lines.append("SPLIT PATTERNS IN PARTIAL MATCHES")
            report_lines.append("-" * 80)

            sorted_patterns = sorted(self.split_patterns.items(),
                                    key=lambda x: -len(x[1]))

            for pattern, occurrences in sorted_patterns:
                report_lines.append(f"{pattern}: {len(occurrences)} occurrences")
                for occ in occurrences[:5]:  # Show first 5
                    report_lines.append(f"  - {occ['book']} {occ['chapter']}:{occ['verse']}")
                if len(occurrences) > 5:
                    report_lines.append(f"  ... and {len(occurrences) - 5} more")
                report_lines.append("")

        # Detailed partial matches
        if self.results['partial']:
            report_lines.append("DETAILED PARTIAL MATCHES")
            report_lines.append("-" * 80)
            report_lines.append("")

            for result in self.results['partial']:
                report_lines.append(f"Book: {result['book']} {result['chapter']}:{result['verse']}")
                report_lines.append(f"Full sense-line:")
                report_lines.append(f"  {result['full_sense_line']}")
                report_lines.append(f"Parry's fragment:")
                report_lines.append(f"  {result['parry_fragment']}")
                report_lines.append(f"Proposed split at: '{result['split_position']}'")
                report_lines.append(f"  Left:  {result['left_part']}")
                report_lines.append(f"  Right: {result['right_part']}")
                report_lines.append("")

        # Write report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        print(f"Report written to {output_path}")

        # Also print summary to console
        print("\n" + "\n".join(report_lines[:20]))


def main():
    base_path = Path(__file__).parent

    print("Loading parallel index...")
    index_path = base_path / "data" / "parallel_index.json"

    analyzer = DiagnosticAnalyzer(base_path)
    print("Analyzing parallel structures...")
    analyzer.analyze_all(index_path)

    print("Generating report...")
    output_path = base_path / "parry_senseline_diagnostic_report.txt"
    analyzer.generate_report(output_path)


if __name__ == '__main__':
    main()
