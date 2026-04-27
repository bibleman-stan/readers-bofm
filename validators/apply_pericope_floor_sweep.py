#!/usr/bin/env python3
"""
Sweep #1 from the pericope canon v0.1 → v1.0 audit:
Apply the §1 Floor rule (3-verse minimum). Find every pericope shorter
than 3 verses and absorb it into its previous-or-next neighbor.

The neighbor receives a re-titled range; the sub-3 pericope is removed
from data/pericope_index.json.

Per the audit, ~30-50 such violations corpus-wide.

Title-range update: each pericope's title typically ends with "(vv. N-M)"
or "(v. N)". When we delete a sub-3 pericope, the previous pericope's
range expands to include the deleted verses. Title's range string is
updated accordingly.

Usage:
    python3 validators/apply_pericope_floor_sweep.py            # dry-run
    python3 validators/apply_pericope_floor_sweep.py --apply    # apply
    python3 validators/apply_pericope_floor_sweep.py --verbose  # show each
"""

import argparse
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = REPO_ROOT / "data" / "pericope_index.json"
CORPUS_DIR = REPO_ROOT / "data" / "text-files" / "v2-mine"

BOOK_FILES = {
    "1nephi": "01-1_nephi-2020-sb-v2.txt",
    "2nephi": "02-2_nephi-2020-sb-v2.txt",
    "jacob": "03-jacob-2020-sb-v2.txt",
    "enos": "04-enos-2020-sb-v2.txt",
    "jarom": "05-jarom-2020-sb-v2.txt",
    "omni": "06-omni-2020-sb-v2.txt",
    "words-of-mormon": "07-words_of_mormon-2020-sb-v2.txt",
    "mosiah": "08-mosiah-2020-sb-v2.txt",
    "alma": "09-alma-2020-sb-v2.txt",
    "helaman": "10-helaman-2020-sb-v2.txt",
    "3nephi": "11-3_nephi-2020-sb-v2.txt",
    "4nephi": "12-4_nephi-2020-sb-v2.txt",
    "mormon": "13-mormon-2020-sb-v2.txt",
    "ether": "14-ether-2020-sb-v2.txt",
    "moroni": "15-moroni-2020-sb-v2.txt",
}

VERSE_HEADER_RE = re.compile(r"^(\d+):(\d+)\s*$")
TITLE_RANGE_RE = re.compile(r"\s*\((?:vv?\.\s*\d+(?:[\-–]\d+)?)\)\s*$")


def get_chapter_max_verse(book_id: str) -> dict:
    """Return {chapter: max_verse_number} for the book."""
    path = CORPUS_DIR / BOOK_FILES[book_id]
    if not path.exists():
        return {}
    chapters = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = VERSE_HEADER_RE.match(line)
            if m:
                ch, vs = int(m.group(1)), int(m.group(2))
                if ch not in chapters or vs > chapters[ch]:
                    chapters[ch] = vs
    return chapters


def format_range(start: int, end: int) -> str:
    if start == end:
        return f"(v. {start})"
    return f"(vv. {start}–{end})"


def strip_range(title: str) -> str:
    """Remove trailing '(vv. N-M)' or '(v. N)' from a title."""
    return TITLE_RANGE_RE.sub("", title).rstrip()


def find_sub_floor_violations(index: dict) -> list:
    """Return list of (book_id, chapter, pericope_idx, span) for pericopes
    shorter than 3 verses."""
    violations = []
    for book_id, chapters in index.items():
        max_verses = get_chapter_max_verse(book_id)
        for ch_str, pericopes in chapters.items():
            ch = int(ch_str)
            chapter_max = max_verses.get(ch, 999)  # fall-through: don't penalize
            for i, p in enumerate(pericopes):
                start = p["verse"]
                if i + 1 < len(pericopes):
                    end = pericopes[i + 1]["verse"] - 1
                else:
                    end = chapter_max
                span = end - start + 1
                # Special case: chapters with <3 verses overall (Moroni 5 etc.)
                # — single-pericope coverage is canonical even if span < 3.
                if chapter_max < 3 and len(pericopes) == 1:
                    continue
                if span < 3:
                    violations.append({
                        "book": book_id,
                        "chapter": ch,
                        "pidx": i,
                        "start": start,
                        "end": end,
                        "span": span,
                        "title": p["title"],
                    })
    return violations


def absorb(index: dict, v: dict, max_verses: dict) -> str:
    """Absorb the sub-floor pericope into its previous neighbor (or next if
    it's the chapter's first). Update neighbor's title range. Return action
    description."""
    book = v["book"]
    ch = v["chapter"]
    pidx = v["pidx"]
    pericopes = index[book][str(ch)]
    me = pericopes[pidx]

    if pidx > 0:
        # Absorb into previous
        prev = pericopes[pidx - 1]
        prev_start = prev["verse"]
        new_end = v["end"]
        prev_title_base = strip_range(prev["title"])
        prev["title"] = f"{prev_title_base} {format_range(prev_start, new_end)}"
        del pericopes[pidx]
        return f"  ABSORB→PREV: '{me['title']}' → '{prev['title']}'"
    elif pidx + 1 < len(pericopes):
        # First in chapter: absorb into next (next's start moves down to me's start)
        nxt = pericopes[pidx + 1]
        nxt_end_idx = pidx + 2 if pidx + 2 < len(pericopes) else None
        nxt_end = pericopes[nxt_end_idx]["verse"] - 1 if nxt_end_idx is not None else max_verses.get(ch, 999)
        nxt["verse"] = me["verse"]
        nxt_title_base = strip_range(nxt["title"])
        nxt["title"] = f"{nxt_title_base} {format_range(me['verse'], nxt_end)}"
        del pericopes[pidx]
        return f"  ABSORB→NEXT: '{me['title']}' → '{nxt['title']}'"
    else:
        # Singleton sub-floor in chapter — leave it alone
        return f"  SKIP (singleton sub-floor in chapter): '{me['title']}'"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    with open(INDEX_PATH, encoding="utf-8") as f:
        index = json.load(f)

    violations = find_sub_floor_violations(index)
    print(f"Sub-3-verse pericope violations found: {len(violations)}")
    print()

    # Group by book for readable output
    by_book = {}
    for v in violations:
        by_book.setdefault(v["book"], []).append(v)

    for book in sorted(by_book.keys()):
        print(f"{book}: {len(by_book[book])} violation{'s' if len(by_book[book]) != 1 else ''}")
        if args.verbose:
            for v in by_book[book]:
                print(f"  ch {v['chapter']} v{v['start']} (span={v['span']}): {v['title']}")
        print()

    if not args.apply:
        print("DRY RUN. Re-run with --apply to apply absorptions.")
        return 0

    # Apply: absorb each sub-floor pericope. Process in REVERSE order within
    # each chapter so indices don't shift under us.
    actions = []
    by_book_chapter = {}
    for v in violations:
        by_book_chapter.setdefault((v["book"], v["chapter"]), []).append(v)
    for (book, ch), vs in by_book_chapter.items():
        max_verses = get_chapter_max_verse(book)
        for v in sorted(vs, key=lambda x: -x["pidx"]):
            actions.append(absorb(index, v, max_verses))

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Applied {len(actions)} absorptions to data/pericope_index.json")
    if args.verbose:
        for a in actions[:20]:
            print(a)

    return 0


if __name__ == "__main__":
    sys.exit(main())
