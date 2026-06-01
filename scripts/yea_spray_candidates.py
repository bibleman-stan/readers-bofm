"""Corpus-wide candidate pool for the yea-increment spray.
Validated on Alma 32 (Stan gold): a clause-initial heightening "yea" introducing
an increment (own/gapped predication OR heightening adverbial) splits to its own
line; a mid-clause in-place intensifier does NOT. Candidate signal = a DEPLOYED
line carrying a clause-internal lowercase ", yea," (the answer-word "Yea" is
capitalized and excluded; lines already starting with "yea," are done).
Emits verses (ref + deployed lines) grouped by book for parallel adjudication.
"""
import json, re, sys
from pathlib import Path

REPO = Path(r"C:\Users\bibleman\repos\readers-bofm")
sys.path.insert(0, str(REPO / "scripts"))
import bofm_generate as bg

BOOKS = []
for ln in (REPO / "booklist.txt").read_text(encoding="utf-8").splitlines():
    ln = ln.strip()
    if ln and not ln.startswith("#"):
        BOOKS.append(ln.split(None, 1)[0])

CAND = re.compile(r"[^\s].*[,;]\s+yea,")   # clause-internal lowercase yea (content precedes it)

out = {}
total_verses = total_yea_lines = 0
for book in BOOKS:
    verses = bg.read_v0(book)
    parsed = bg.parse_book(book)
    book_cands = []
    for (c, v) in sorted(verses):
        vt = verses[(c, v)]
        lines = bg.deployed_atu_lines(book, c, v, vt, parsed.get((c, v), []))
        hits = [i for i, ln in enumerate(lines) if CAND.search(ln)]
        if hits:
            book_cands.append({"ref": f"{book} {c}:{v}", "lines": lines, "yea_line_idx": hits})
            total_verses += 1
            total_yea_lines += len(hits)
    if book_cands:
        out[book] = book_cands

OUTP = Path(r"C:\tmp\yea_candidates.json")
OUTP.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"candidate verses: {total_verses} | clause-internal yea lines: {total_yea_lines}")
print("per book:")
for b in BOOKS:
    if b in out:
        n = len(out[b]); yl = sum(len(x["yea_line_idx"]) for x in out[b])
        print(f"  {b:16} {n:3} verses  {yl:3} yea-lines")
print(f"\nwrote {OUTP}")
