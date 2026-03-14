#!/usr/bin/env python3
"""
Audio generation pipeline for bomreader.com
Generates chapter-level MP3 files + timing manifests from book HTML files
using the Kokoro TTS model (offline generation).

Usage:
  pip install kokoro soundfile numpy lameenc beautifulsoup4
  python generate_audio.py enos          # generate Enos (test)
  python generate_audio.py 1nephi        # generate 1 Nephi (all chapters)
  python generate_audio.py --all         # generate everything

Output:
  audio/<book>-<chapter>.mp3       e.g. audio/enos-1.mp3
  audio/<book>-<chapter>.json      timing manifest for line highlighting
"""

import argparse
import json
import os
import re
import struct
import sys
import time
from pathlib import Path

import numpy as np
from bs4 import BeautifulSoup, NavigableString

# ── Configuration ──
VOICE = 'bm_george'        # British male
SAMPLE_RATE = 24000         # Kokoro default
LINE_PAUSE_S = 0.18         # 180ms between sense-lines
VERSE_PAUSE_S = 0.50        # 500ms between verses
PERICOPE_PAUSE_S = 0.90     # 900ms before a section header

BOOKS = [
    ('1nephi', 22), ('2nephi', 33), ('jacob', 7), ('enos', 1),
    ('jarom', 1), ('omni', 1), ('words-of-mormon', 1), ('mosiah', 29),
    ('alma', 63), ('helaman', 16), ('3nephi', 30), ('4nephi', 1),
    ('mormon', 9), ('ether', 15), ('moroni', 10),
]

BOOK_NAMES = {
    '1nephi': '1 Nephi', '2nephi': '2 Nephi', 'jacob': 'Jacob',
    'enos': 'Enos', 'jarom': 'Jarom', 'omni': 'Omni',
    'words-of-mormon': 'Words of Mormon', 'mosiah': 'Mosiah',
    'alma': 'Alma', 'helaman': 'Helaman', '3nephi': '3 Nephi',
    '4nephi': '4 Nephi', 'mormon': 'Mormon', 'ether': 'Ether',
    'moroni': 'Moroni',
}


def get_text_from_element(el, use_modern=True):
    """
    Extract readable text from an HTML element.
    If use_modern=True, replaces archaic words with their data-mod equivalents.
    Removes verse numbers, parry labels, and punct spans (reads natural punctuation).
    """
    # Work on a copy
    clone = BeautifulSoup(str(el), 'html.parser')

    # Replace swap spans with modern text
    if use_modern:
        for swap in clone.find_all(class_=['swap', 'swap-quiet']):
            mod = swap.get('data-mod')
            if mod:
                swap.string = mod

    # Remove verse numbers and parry labels
    for remove in clone.find_all(class_=['verse-num', 'parry-label-spacer', 'parry-label']):
        remove.decompose()

    # Get text — punct spans just contain the punctuation character, which is fine
    text = clone.get_text()
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_chapter(html_path, book_id, chapter_num):
    """
    Parse a chapter from the book HTML file.
    Returns list of items: { type, text, verse_num, line_index }
    where type is 'pericope', 'line', or 'verse-gap'
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    chapter_id = f'ch-{book_id}-{chapter_num}'
    chapter_div = soup.find(id=chapter_id)
    if not chapter_div:
        print(f'  Warning: chapter {chapter_id} not found')
        return []

    items = []
    line_idx = 0  # global line index for timing manifest

    for child in chapter_div.children:
        if isinstance(child, NavigableString):
            continue

        classes = child.get('class', [])

        # Pericope header
        if 'pericope-header' in classes:
            main_el = child.find(class_='pericope-main')
            if main_el:
                text = main_el.get_text().strip()
                if text:
                    items.append({
                        'type': 'pericope',
                        'text': text,
                        'verse_num': '',
                        'line_index': line_idx,
                    })
                    line_idx += 1
            continue

        # Verse
        if 'verse' in classes:
            verse_num_el = child.find(class_='verse-num')
            vn = verse_num_el.get_text().strip() if verse_num_el else ''

            # Use sense-lines (.line elements, not .line-para or .line-parry)
            sense_lines = child.find_all(
                class_='line',
                recursive=False  # direct children only
            )
            # Filter: only elements whose class is exactly ['line']
            # (exclude line-para, line-parry, etc.)
            sense_lines = [
                el for el in child.find_all('span', recursive=False)
                if el.get('class') == ['line']
            ]

            for line_el in sense_lines:
                text = get_text_from_element(line_el, use_modern=True)
                if text:
                    items.append({
                        'type': 'line',
                        'text': text,
                        'verse_num': vn,
                        'line_index': line_idx,
                    })
                    line_idx += 1

            # Verse gap
            if items and items[-1]['type'] != 'verse-gap':
                items.append({
                    'type': 'verse-gap',
                    'text': '',
                    'verse_num': '',
                    'line_index': -1,
                })

    return items


def generate_silence(duration_s, sample_rate=SAMPLE_RATE):
    """Generate silence as a numpy array."""
    return np.zeros(int(duration_s * sample_rate), dtype=np.float32)


def generate_chapter_audio(items, tts, voice=VOICE):
    """
    Generate audio for a chapter.
    Returns (audio_samples, timing_manifest).
    audio_samples: numpy float32 array of concatenated audio
    timing_manifest: list of { start_s, end_s, type, text, verse_num, line_index }
    """
    all_samples = []
    timing = []
    current_time = 0.0

    total_speakable = sum(1 for item in items if item['type'] in ('pericope', 'line'))
    done = 0

    for item in items:
        if item['type'] == 'verse-gap':
            silence = generate_silence(VERSE_PAUSE_S)
            all_samples.append(silence)
            current_time += VERSE_PAUSE_S
            continue

        if item['type'] == 'pericope':
            # Pause before pericope
            silence = generate_silence(PERICOPE_PAUSE_S)
            all_samples.append(silence)
            current_time += PERICOPE_PAUSE_S

        # Generate speech
        start_time = current_time
        try:
            result = tts.generate(item['text'], voice=voice)
            audio_data = result.audio
            if hasattr(audio_data, 'numpy'):
                audio_data = audio_data.numpy()
            audio_data = np.array(audio_data, dtype=np.float32).flatten()
        except Exception as e:
            print(f'    Error generating "{item["text"][:50]}...": {e}')
            # Insert a short silence as placeholder
            audio_data = generate_silence(0.5)

        all_samples.append(audio_data)
        duration = len(audio_data) / SAMPLE_RATE
        current_time += duration

        timing.append({
            'start': round(start_time, 3),
            'end': round(current_time, 3),
            'type': item['type'],
            'text': item['text'],
            'verse': item['verse_num'],
            'lineIndex': item['line_index'],
        })

        done += 1
        pct = round(done / total_speakable * 100)
        print(f'\r    [{pct:3d}%] {done}/{total_speakable} lines generated', end='', flush=True)

        # Line pause after sense-lines
        if item['type'] == 'line':
            silence = generate_silence(LINE_PAUSE_S)
            all_samples.append(silence)
            current_time += LINE_PAUSE_S

        # Extra pause after pericope audio
        if item['type'] == 'pericope':
            silence = generate_silence(PERICOPE_PAUSE_S)
            all_samples.append(silence)
            current_time += PERICOPE_PAUSE_S

    print()  # newline after progress

    # Concatenate all audio
    if all_samples:
        combined = np.concatenate(all_samples)
    else:
        combined = np.array([], dtype=np.float32)

    return combined, timing


def samples_to_mp3(samples, sample_rate=SAMPLE_RATE, bitrate=64):
    """Convert float32 samples to MP3 bytes using lameenc."""
    import lameenc

    # Convert to 16-bit PCM
    pcm_16 = (samples * 32767).astype(np.int16)

    encoder = lameenc.Encoder()
    encoder.set_bit_rate(bitrate)
    encoder.set_in_sample_rate(sample_rate)
    encoder.set_channels(1)
    encoder.set_quality(2)  # high quality

    mp3_data = encoder.encode(pcm_16.tobytes())
    mp3_data += encoder.flush()
    return mp3_data


def process_book(book_id, num_chapters, tts, output_dir):
    """Process all chapters of a book."""
    html_path = Path('books') / f'{book_id}.html'
    if not html_path.exists():
        print(f'  ERROR: {html_path} not found')
        return

    book_name = BOOK_NAMES.get(book_id, book_id)

    for ch in range(1, num_chapters + 1):
        label = f'{book_name} {ch}' if num_chapters > 1 else book_name
        print(f'\n  Processing {label}...')

        # Parse chapter
        items = parse_chapter(html_path, book_id, ch)
        speakable = [i for i in items if i['type'] in ('pericope', 'line')]
        print(f'    Found {len(speakable)} speakable items')

        if not speakable:
            print('    Skipping (no content)')
            continue

        # Generate audio
        t0 = time.time()
        audio_samples, timing = generate_chapter_audio(items, tts)
        elapsed = time.time() - t0
        duration = len(audio_samples) / SAMPLE_RATE

        print(f'    Audio: {duration:.1f}s, generated in {elapsed:.1f}s '
              f'({duration/elapsed:.1f}x realtime)')

        # Save MP3
        mp3_path = output_dir / f'{book_id}-{ch}.mp3'
        mp3_data = samples_to_mp3(audio_samples)
        mp3_path.write_bytes(mp3_data)
        print(f'    Saved: {mp3_path} ({len(mp3_data) / 1024:.0f} KB)')

        # Save timing manifest
        json_path = output_dir / f'{book_id}-{ch}.json'
        manifest = {
            'book': book_id,
            'bookName': book_name,
            'chapter': ch,
            'voice': VOICE,
            'duration': round(duration, 3),
            'lines': timing,
        }
        json_path.write_text(json.dumps(manifest, indent=2))
        print(f'    Saved: {json_path}')


def main():
    parser = argparse.ArgumentParser(description='Generate TTS audio for bomreader.com')
    parser.add_argument('books', nargs='*', help='Book IDs to process (e.g. enos, 1nephi)')
    parser.add_argument('--all', action='store_true', help='Process all books')
    parser.add_argument('--voice', default=VOICE, help=f'Voice to use (default: {VOICE})')
    parser.add_argument('--output', default='audio', help='Output directory (default: audio)')
    args = parser.parse_args()

    if not args.books and not args.all:
        parser.print_help()
        sys.exit(1)

    # Initialize Kokoro
    print('Loading Kokoro TTS model...')
    try:
        from kokoro import KPipeline
        tts = KPipeline(lang_code='a')  # 'a' = American/British English
        print(f'  Model loaded. Voice: {args.voice}')
    except ImportError:
        print('ERROR: kokoro not installed. Run: pip install kokoro')
        sys.exit(1)

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)

    # Determine which books to process
    if args.all:
        to_process = BOOKS
    else:
        to_process = []
        for book_id in args.books:
            match = next((b for b in BOOKS if b[0] == book_id), None)
            if match:
                to_process.append(match)
            else:
                print(f'Unknown book: {book_id}')
                print(f'Valid books: {", ".join(b[0] for b in BOOKS)}')
                sys.exit(1)

    # Process
    total_start = time.time()
    for book_id, num_chapters in to_process:
        book_name = BOOK_NAMES.get(book_id, book_id)
        print(f'\n{"="*60}')
        print(f'  {book_name} ({num_chapters} chapter{"s" if num_chapters > 1 else ""})')
        print(f'{"="*60}')
        process_book(book_id, num_chapters, tts, output_dir)

    total_elapsed = time.time() - total_start
    print(f'\nDone! Total time: {total_elapsed:.0f}s')
    print(f'Output in: {output_dir}/')


if __name__ == '__main__':
    main()
