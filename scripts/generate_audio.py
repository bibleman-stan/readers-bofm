#!/usr/bin/env python3
"""
Local audio generation script for BOM Reader — Samuel voice.

Replaces the Colab pipeline. Generates MP3 + JSON timing manifests
for each chapter using ElevenLabs TTS API.

Usage:
  # Set your API key (one time per session):
  export ELEVENLABS_API_KEY="sk-..."

  # Dry run — see character counts without spending credits:
  python scripts/generate_audio.py --book 2nephi --dry-run

  # Generate a single chapter:
  python scripts/generate_audio.py --book 2nephi --chapter 6

  # Generate a range of chapters:
  python scripts/generate_audio.py --book 2nephi --chapters 6-24

  # Generate all chapters of a book:
  python scripts/generate_audio.py --book jacob

  # Voice test — generate first 5 lines only:
  python scripts/generate_audio.py --book jacob --test

  # Force regenerate (ignore cache):
  python scripts/generate_audio.py --book jacob --chapter 1 --no-cache
"""

import argparse
import hashlib
import io
import json
import os
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup, NavigableString

# Fix ffmpeg path for pydub on systems without system-installed ffmpeg
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except ImportError:
    pass

from pydub import AudioSegment

# ══════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════

VOICE_ID = 'ddDFRErfhdc2asyySOG5'  # Samuel (Nigerian-accented English)
VOICE_NAME = 'samuel'
MODEL_ID = 'eleven_multilingual_v2'

VOICE_SETTINGS = {
    'stability': 0.50,
    'similarity_boost': 0.75,
    'style': 0.35,
    'use_speaker_boost': True,
}

LINE_PAUSE_MS = 180
VERSE_PAUSE_MS = 500

# Book metadata: id -> (display name, chapter count, audio folder name)
BOOKS = {
    '1nephi':          ('1 Nephi',           22, '01-1_Nephi'),
    '2nephi':          ('2 Nephi',           33, '02-2_Nephi'),
    'jacob':           ('Jacob',              7, '03-Jacob'),
    'enos':            ('Enos',               1, '04-Enos'),
    'jarom':           ('Jarom',              1, '05-Jarom'),
    'omni':            ('Omni',               1, '06-Omni'),
    'words-of-mormon': ('Words of Mormon',    1, '07-Words_of_Mormon'),
    'mosiah':          ('Mosiah',            29, '08-Mosiah'),
    'alma':            ('Alma',              63, '09-Alma'),
    'helaman':         ('Helaman',           16, '10-Helaman'),
    '3nephi':          ('3 Nephi',           30, '11-3_Nephi'),
    '4nephi':          ('4 Nephi',            1, '12-4_Nephi'),
    'mormon':          ('Mormon',             9, '13-Mormon'),
    'ether':           ('Ether',             15, '14-Ether'),
    'moroni':          ('Moroni',            10, '15-Moroni'),
}

# ══════════════════════════════════════════
# PATHS
# ══════════════════════════════════════════

REPO_ROOT = Path(__file__).resolve().parent.parent
BOOKS_DIR = REPO_ROOT / 'books'
AUDIO_DIR = REPO_ROOT / 'audio'
CACHE_DIR = REPO_ROOT / '.audio-cache'


# ══════════════════════════════════════════
# CACHING — per-line SHA256 cache on disk
# ══════════════════════════════════════════

def cache_key(text, voice_id, model_id, settings):
    blob = json.dumps({
        'text': text, 'voice_id': voice_id,
        'model_id': model_id, 'settings': settings
    }, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def get_cached_audio(key):
    path = CACHE_DIR / f'{key}.mp3'
    if path.exists():
        return AudioSegment.from_mp3(str(path))
    return None


def save_to_cache(key, audio_seg):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    audio_seg.export(str(CACHE_DIR / f'{key}.mp3'), format='mp3', bitrate='128k')


# ══════════════════════════════════════════
# HTML PARSING
# ══════════════════════════════════════════

def get_text_from_element(el, use_modern=False):
    """Extract text from a line element. TTS uses data-orig (authentic text)."""
    clone = BeautifulSoup(str(el), 'html.parser')
    if use_modern:
        for swap in clone.find_all(class_=['swap', 'swap-quiet']):
            mod = swap.get('data-mod')
            if mod:
                swap.string = mod
    for remove in clone.find_all(class_=['verse-num', 'parry-label-spacer', 'parry-label']):
        remove.decompose()
    return re.sub(r'\s+', ' ', clone.get_text()).strip()


def parse_chapter(html_path, book_id, chapter_num):
    """Parse a built HTML file to extract speakable lines with line indices."""
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    chapter_div = soup.find(id=f'ch-{book_id}-{chapter_num}')
    if not chapter_div:
        print(f'  WARNING: ch-{book_id}-{chapter_num} not found in {html_path}')
        return []

    items = []
    line_idx = 0

    for child in chapter_div.children:
        if isinstance(child, NavigableString):
            continue
        classes = child.get('class', [])

        # Pericope headers increment line index but aren't spoken
        if 'pericope-header' in classes:
            line_idx += 1
            continue

        if 'verse' in classes:
            vn_el = child.find(class_='verse-num')
            vn = vn_el.get_text().strip() if vn_el else ''
            for line_el in child.find_all('span', recursive=False):
                if 'line' not in (line_el.get('class') or []):
                    continue
                text = get_text_from_element(line_el, use_modern=False)
                if text:
                    items.append({
                        'type': 'line',
                        'text': text,
                        'verse_num': vn,
                        'line_index': line_idx,
                    })
                    line_idx += 1
            if items and items[-1]['type'] != 'verse-gap':
                items.append({
                    'type': 'verse-gap',
                    'text': '',
                    'verse_num': '',
                    'line_index': -1,
                })

    return items


# ══════════════════════════════════════════
# ELEVENLABS TTS
# ══════════════════════════════════════════

def tts_elevenlabs(text, api_key, use_cache=True):
    """Generate TTS audio for a single line. Returns (AudioSegment, from_cache)."""
    key = cache_key(text, VOICE_ID, MODEL_ID, VOICE_SETTINGS)

    if use_cache:
        cached = get_cached_audio(key)
        if cached is not None:
            return cached, True

    url = f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}'
    headers = {
        'xi-api-key': api_key,
        'Content-Type': 'application/json',
        'Accept': 'audio/mpeg',
    }
    payload = {
        'text': text,
        'model_id': MODEL_ID,
        'voice_settings': VOICE_SETTINGS,
    }

    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code != 200:
        print(f'  API ERROR {resp.status_code}: {resp.text[:200]}')
        raise RuntimeError(f'ElevenLabs API error {resp.status_code}')

    audio_seg = AudioSegment.from_mp3(io.BytesIO(resp.content))
    save_to_cache(key, audio_seg)
    return audio_seg, False


# ══════════════════════════════════════════
# CHAPTER STITCHING
# ══════════════════════════════════════════

def stitch_chapter(items, api_key, use_cache=True):
    """Generate and stitch audio for all lines in a chapter."""
    combined = AudioSegment.empty()
    timing = []
    current_time_ms = 0
    stats = {'cached': 0, 'generated': 0, 'chars_used': 0}

    speakable = [i for i in items if i['type'] == 'line']
    total = len(speakable)
    done = 0

    for item in items:
        if item['type'] == 'verse-gap':
            combined += AudioSegment.silent(duration=VERSE_PAUSE_MS)
            current_time_ms += VERSE_PAUSE_MS
            continue

        if item['type'] != 'line':
            continue

        done += 1
        audio_seg, from_cache = tts_elevenlabs(item['text'], api_key, use_cache)

        if from_cache:
            stats['cached'] += 1
            tag = 'cache'
        else:
            stats['generated'] += 1
            stats['chars_used'] += len(item['text'])
            tag = 'NEW'
            time.sleep(0.05)  # Rate limit courtesy

        start_ms = current_time_ms
        combined += audio_seg
        current_time_ms += len(audio_seg)

        timing.append({
            'start': round(start_ms / 1000, 3),
            'end': round(current_time_ms / 1000, 3),
            'type': 'line',
            'text': item['text'],
            'verse': item['verse_num'],
            'lineIndex': item['line_index'],
        })

        preview = item['text'][:50] + ('...' if len(item['text']) > 50 else '')
        print(f'  [{done}/{total}] [{tag}] v{item["verse_num"]}: {preview}')

        combined += AudioSegment.silent(duration=LINE_PAUSE_MS)
        current_time_ms += LINE_PAUSE_MS

    return combined, timing, stats


# ══════════════════════════════════════════
# OUTPUT
# ══════════════════════════════════════════

def save_chapter(book_id, book_name, chapter_num, audio_dir, combined, timing):
    """Save MP3 and JSON manifest for a chapter."""
    audio_dir.mkdir(parents=True, exist_ok=True)

    mp3_path = audio_dir / f'{book_id}-{chapter_num}-{VOICE_NAME}.mp3'
    combined.export(str(mp3_path), format='mp3', bitrate='128k')

    duration_s = len(combined) / 1000
    manifest = {
        'book': book_id,
        'bookName': book_name,
        'chapter': chapter_num,
        'voice': {
            'provider': 'elevenlabs',
            'voice_id': VOICE_ID,
            'model_id': MODEL_ID,
            'settings': VOICE_SETTINGS,
            'name': 'Samuel',
        },
        'pauses': {
            'line_ms': LINE_PAUSE_MS,
            'verse_ms': VERSE_PAUSE_MS,
        },
        'duration': round(duration_s, 3),
        'lines': timing,
    }

    json_path = audio_dir / f'{book_id}-{chapter_num}-{VOICE_NAME}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    file_size_kb = mp3_path.stat().st_size / 1024
    print(f'  Saved: {mp3_path.name} ({duration_s:.1f}s, {file_size_kb:.0f}KB)')
    return mp3_path, json_path


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════

def parse_chapter_range(s, total):
    """Parse chapter spec: '6', '6-24', or None (all)."""
    if s is None:
        return list(range(1, total + 1))
    if '-' in s:
        start, end = s.split('-', 1)
        return list(range(int(start), int(end) + 1))
    return [int(s)]


def main():
    parser = argparse.ArgumentParser(description='Generate Samuel voice audio for BOM Reader')
    parser.add_argument('--book', required=True, choices=list(BOOKS.keys()),
                        help='Book ID (e.g. 2nephi, jacob, alma)')
    parser.add_argument('--chapter', type=str, default=None,
                        help='Single chapter number')
    parser.add_argument('--chapters', type=str, default=None,
                        help='Chapter range (e.g. 6-24)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Count characters without generating audio')
    parser.add_argument('--test', action='store_true',
                        help='Generate only first 5 lines of chapter 1')
    parser.add_argument('--no-cache', action='store_true',
                        help='Ignore line cache, regenerate everything')
    parser.add_argument('--skip-existing', action='store_true', default=True,
                        help='Skip chapters that already have MP3+JSON (default: true)')
    parser.add_argument('--no-skip-existing', action='store_true',
                        help='Regenerate even if MP3+JSON already exist')

    args = parser.parse_args()

    book_id = args.book
    book_name, total_chapters, audio_folder = BOOKS[book_id]
    html_path = BOOKS_DIR / f'{book_id}.html'
    audio_out = AUDIO_DIR / audio_folder

    if not html_path.exists():
        print(f'ERROR: {html_path} not found. Run build_book.py first.')
        sys.exit(1)

    # Determine chapter range
    if args.chapter:
        chapters = [int(args.chapter)]
    elif args.chapters:
        chapters = parse_chapter_range(args.chapters, total_chapters)
    else:
        chapters = list(range(1, total_chapters + 1))

    skip_existing = not args.no_skip_existing

    print(f'Book: {book_name} ({book_id})')
    print(f'Chapters: {chapters[0]}-{chapters[-1]} ({len(chapters)} total)')
    print(f'HTML source: {html_path}')
    print(f'Audio output: {audio_out}')
    print(f'Cache: {CACHE_DIR}')
    print()

    # ── DRY RUN ──
    if args.dry_run:
        total_lines = 0
        total_chars = 0
        for ch in chapters:
            items = parse_chapter(html_path, book_id, ch)
            speakable = [i for i in items if i['type'] == 'line']
            chars = sum(len(i['text']) for i in speakable)
            total_lines += len(speakable)
            total_chars += chars

            existing = ''
            mp3 = audio_out / f'{book_id}-{ch}-{VOICE_NAME}.mp3'
            if mp3.exists():
                existing = ' [EXISTS]'

            print(f'  Ch {ch:2d}: {len(speakable):3d} lines, {chars:5,d} chars{existing}')

        print(f'\n{"="*50}')
        print(f'{book_name}: {len(chapters)} chapters')
        print(f'  Total lines:  {total_lines}')
        print(f'  Total chars:  {total_chars:,}')
        print(f'  ~Credits:     {total_chars:,} characters')
        print(f'{"="*50}')
        return

    # ── API KEY ──
    api_key = os.environ.get('ELEVENLABS_API_KEY', '')
    if not api_key:
        # Check for .env file in repo root
        env_path = REPO_ROOT / '.env'
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith('ELEVENLABS_API_KEY='):
                    api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break
    if not api_key:
        print('ERROR: No API key found.')
        print('  Set ELEVENLABS_API_KEY environment variable, or')
        print('  Create .env file in repo root with ELEVENLABS_API_KEY=sk-...')
        sys.exit(1)

    use_cache = not args.no_cache

    # ── VOICE TEST ──
    if args.test:
        print(f'Voice test: first 5 lines of {book_name} 1\n')
        items = parse_chapter(html_path, book_id, 1)
        speakable = [i for i in items if i['type'] == 'line'][:5]
        test_chars = sum(len(i['text']) for i in speakable)
        print(f'  {len(speakable)} lines, ~{test_chars} chars\n')

        combined = AudioSegment.empty()
        for i, item in enumerate(speakable):
            print(f'  [{i+1}/5] {item["text"][:60]}...')
            seg, cached = tts_elevenlabs(item['text'], api_key, use_cache)
            print(f'         [{"cache" if cached else "NEW"}]')
            combined += seg + AudioSegment.silent(duration=LINE_PAUSE_MS)
            if not cached:
                time.sleep(0.1)

        test_path = REPO_ROOT / 'test_voice.mp3'
        combined.export(str(test_path), format='mp3', bitrate='128k')
        print(f'\n  Saved: {test_path} ({len(combined)/1000:.1f}s)')
        print(f'  Play it to verify the voice sounds right before full generation.')
        return

    # ── FULL GENERATION ──
    results = []
    total_chars_used = 0

    for ch in chapters:
        print(f'\n{"="*60}')
        print(f'CHAPTER {ch} of {book_name}')
        print(f'{"="*60}')

        # Skip existing
        if skip_existing:
            mp3_path = audio_out / f'{book_id}-{ch}-{VOICE_NAME}.mp3'
            json_path = audio_out / f'{book_id}-{ch}-{VOICE_NAME}.json'
            if mp3_path.exists() and json_path.exists():
                sz = mp3_path.stat().st_size / 1024
                print(f'  ALREADY EXISTS ({sz:.0f}KB) — skipping!')
                results.append({
                    'ch': ch, 'lines': 0, 'duration': 0,
                    'size_kb': sz, 'cached': 0, 'generated': 0, 'chars_used': 0,
                })
                continue

        items = parse_chapter(html_path, book_id, ch)
        speakable = [i for i in items if i['type'] == 'line']
        ch_chars = sum(len(i['text']) for i in speakable)
        print(f'  {len(speakable)} lines, ~{ch_chars} chars')

        combined, timing, stats = stitch_chapter(items, api_key, use_cache)

        save_chapter(book_id, book_name, ch, audio_out, combined, timing)

        duration_s = len(combined) / 1000
        file_size_kb = (audio_out / f'{book_id}-{ch}-{VOICE_NAME}.mp3').stat().st_size / 1024
        total_chars_used += stats['chars_used']

        results.append({
            'ch': ch, 'lines': len(speakable), 'duration': duration_s,
            'size_kb': file_size_kb, 'cached': stats['cached'],
            'generated': stats['generated'], 'chars_used': stats['chars_used'],
        })

        print(f'  Cache hits: {stats["cached"]}, New: {stats["generated"]}, Credits: ~{stats["chars_used"]}')

    # ── SUMMARY ──
    print(f'\n\n{"="*60}')
    print(f'COMPLETE — {book_name} ({len(chapters)} chapters)')
    print(f'{"="*60}')
    td = sum(r['duration'] for r in results)
    ts = sum(r['size_kb'] for r in results)
    tl = sum(r['lines'] for r in results)
    tn = sum(r['generated'] for r in results)
    tc = sum(r['cached'] for r in results)
    print(f'  Total lines:     {tl}')
    print(f'  Total duration:  {td/60:.1f} min ({td:.0f}s)')
    print(f'  Total size:      {ts/1024:.1f} MB')
    print(f'  Cache hits:      {tc}')
    print(f'  Newly generated: {tn}')
    print(f'  Credits used:    ~{total_chars_used:,} chars')
    print()
    for r in results:
        print(f'  Ch{r["ch"]:2d}: {r["lines"]:3d} lines, {r["duration"]:6.1f}s, {r["size_kb"]:6.0f}KB')


if __name__ == '__main__':
    main()
