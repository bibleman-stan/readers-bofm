#!/usr/bin/env python3
"""Generator-integrity / word-drift check: the ATU rendering only RE-GROUPS the
v0 word stream into lines; it must never add, drop, or reorder a word. Compares
the word-token sequence of each v0 verse against its rendered v2 line set
(verse markers + punctuation excluded). Prints any drift; exit 0 iff drift==0.

Run: PYTHONIOENCODING=utf-8 py -3 scripts/check_word_drift.py
"""
import re
import sys

sys.path.insert(0, ".")
import scripts.bofm_generate as G  # noqa: E402


def words(s):
    return re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)?", s)


def main():
    drift_total = 0
    for book in G.BOOKFILE:
        verses = G.read_v0(book)
        parsed = G.parse_book(book)
        for (c, v) in sorted(verses):
            src = words(verses[(c, v)])
            ov = G._apply_override(verses[(c, v)], f"{book} {c}:{v}")
            lines = ov if ov is not None else \
                G.verse_atu_lines(verses[(c, v)], parsed.get((c, v), []))
            rendered = words(" ".join(lines))
            if src != rendered:
                drift_total += 1
                if drift_total <= 10:
                    print(f"DRIFT {book} {c}:{v}: src={len(src)} rendered={len(rendered)}")
    print(f"TOTAL WORD-DRIFT VERSES: {drift_total}")
    return 0 if drift_total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
