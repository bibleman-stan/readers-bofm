#!/usr/bin/env python3
"""
Enrich Hardy biblical references for build-time intertext injection.

Reads data/hardy_biblical_references.json, resolves BoM references to
(book_id, chapter, verse) tuples, and outputs data/hardy_intertext.json
keyed by book_id for fast lookup during HTML generation.

Output format:
{
  "alma": {
    "32": {
      "28": [{"type": "allusion", "bible_ref": "Matthew 13.3-8"}],
      ...
    }
  },
  ...
}
"""

import json, sys
from collections import defaultdict
from bom_abbreviations import parse_bom_ref

def main():
    with open('data/hardy_biblical_references.json') as f:
        raw = json.load(f)

    index = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    skipped = 0
    resolved = 0

    for entry in raw['entries']:
        if entry['type'] == 'cross-reference':
            skipped += 1
            continue

        refs = parse_bom_ref(entry['bom_ref'])
        if not refs:
            skipped += 1
            continue

        for book_id, chapter, verse in refs:
            index[book_id][str(chapter)][str(verse)].append({
                'type': 'quotation' if entry['type'] == 'quotation' else 'allusion',
                'bible_ref': entry['bible_ref'],
            })
            resolved += 1

    # Convert defaultdicts to regular dicts for JSON serialization
    out = {}
    for book_id in sorted(index):
        out[book_id] = {}
        for ch in sorted(index[book_id], key=int):
            out[book_id][ch] = {}
            for vs in sorted(index[book_id][ch], key=int):
                out[book_id][ch][vs] = index[book_id][ch][vs]

    with open('data/hardy_intertext.json', 'w') as f:
        json.dump(out, f, indent=2)

    # Stats
    books_with_refs = len(out)
    total_verses = sum(len(vs) for ch in out.values() for vs in ch.values())
    print(f"Resolved {resolved} verse-level entries across {books_with_refs} books, {total_verses} unique verse slots")
    print(f"Skipped {skipped} (cross-references or unparseable)")
    print(f"Output: data/hardy_intertext.json ({len(json.dumps(out)):,} bytes)")

    # Per-book summary
    for bid in sorted(out):
        q = sum(1 for ch in out[bid].values() for vs in ch.values() for e in vs if e['type'] == 'quotation')
        a = sum(1 for ch in out[bid].values() for vs in ch.values() for e in vs if e['type'] == 'allusion')
        print(f"  {bid:20s}  Q={q:3d}  A={a:4d}")

if __name__ == '__main__':
    main()
