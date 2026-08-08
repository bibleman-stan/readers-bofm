#!/usr/bin/env python3
"""Marschall-view experiment — segment BoFM text by Marschall's criteriology.

EXPERIMENTAL PROBE, NOT A SHIPPED LAYER. Builds an alternate segmentation of a
chapter using Priscille Marschall's colometric criteria (Marschall 2024, WUNT
2/603, Table 2 pp.173-174: 8 Laws + 13 Tendencies) so it can be eyeballed beside
the deployed ATU rendering. It changes nothing the reader serves.

Rules implemented (the mechanically tractable ones):
  L1  <7 syllables  -> the unit is a *comma*, not a colon (it still stands alone)
  T1  7-25 syllables -> standard colon length
  L2  >35 syllables -> FORBIDDEN. A law, not a tendency: force a split.
  T3a colon boundaries tend to coincide with clause divisions (uses the UD parse)
  T9  gar marks the start of a period / autonomous colon -> EME analogue "for"
  T4  periods run 2-4 cola
  T5  periods run 25-60 syllables
  L6  a period corresponds to a sentence

NOT implemented (not mechanically tractable here, and Marschall grades them as
clues rather than binding): L7/L8/T10 antithesis, T11-T13 sound echo/parisosis,
T2 balance. Their absence means this view UNDER-splits relative to a faithful
hand application — so any over-merge it detects in the ATU rendering is a floor,
not a ceiling.

Syllable counting is an English heuristic (vowel-group with silent-e and -ed
correction). Marschall counts Greek syllables; EME English syllable weight is a
different thing, so treat absolute counts as indicative and comparisons within
this run as sound.

Usage:
    python 5-machinery/scripts/marschall_view.py 1nephi 3
"""

import re
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
V2 = REPO / "data" / "text-files" / "v2"
CONLLU = REPO / "data" / "parses" / "v0-cache-conllu"

BOOK_FILES = {"1nephi": "01-1_nephi-2020-sb-v2.txt"}

# Clause-head relations: a token bearing one of these opens a new clause, which
# is where T3(a) says colon boundaries tend to fall.
CLAUSE_DEPRELS = {"conj", "advcl", "ccomp", "parataxis", "acl", "acl:relcl",
                  "csubj", "xcomp"}

VOWELS = "aeiouy"


def syllables(text: str) -> int:
    """Vowel-group heuristic with silent-e and past-tense -ed correction."""
    total = 0
    for w in re.findall(r"[A-Za-z']+", text.lower()):
        w = w.replace("'", "")
        if not w:
            continue
        groups = re.findall(r"[aeiouy]+", w)
        n = len(groups)
        if w.endswith("e") and not w.endswith(("le", "ee", "ye")) and n > 1:
            n -= 1
        if w.endswith("ed") and len(w) > 3 and w[-3] not in "dt" and n > 1:
            n -= 1          # "commanded" 3, but "returned" 2
        if w.endswith("eth") and n > 1:
            n -= 0          # EME "hath/doeth" — keep the syllable
        total += max(1, n)
    return total


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def load_chapter(book: str, chapter: str):
    """-> [(verse, [atu_line, ...]), ...] for one chapter."""
    path = V2 / BOOK_FILES[book]
    out, cur_v, cur_lines, in_ch = [], None, [], False
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        m = re.match(r"^(\d+):(\d+)$", line)
        if m:
            if cur_v and in_ch:
                out.append((cur_v, cur_lines))
            ch, vs = m.group(1), m.group(2)
            in_ch = (ch == str(chapter))
            cur_v, cur_lines = (vs if in_ch else None), []
            continue
        if in_ch and line and cur_v:
            cur_lines.append(line)
    if cur_v and in_ch:
        out.append((cur_v, cur_lines))
    return out


def load_parses(book: str) -> dict:
    """normalized sentence text -> [(id, form, head, deprel), ...]"""
    text = (CONLLU / f"{book}.conllu").read_text(encoding="utf-8", errors="replace")
    parses, sent_text, toks = {}, None, []
    for line in text.splitlines():
        if line.startswith("# text ="):
            sent_text = line.split("=", 1)[1].strip()
        elif not line.strip():
            if sent_text and toks:
                parses[norm(sent_text)] = toks
            sent_text, toks = None, []
        elif not line.startswith("#"):
            f = line.split("\t")
            if len(f) > 7 and f[0].isdigit():
                toks.append((int(f[0]), f[1], f[3], f[6], f[7]))  # id form upos head deprel
    if sent_text and toks:
        parses[norm(sent_text)] = toks
    return parses


def clause_starts(toks) -> set:
    """Token ids that open a clause (T3a boundary candidates).

    Restricted to VERB/AUX-headed clause openers. An earlier pass allowed any
    `conj`, which fired on noun conjuncts ("thou and thy brethren") and cut
    mid-phrase — T3(a) is about clause divisions, not coordination as such.
    """
    starts, by_id = set(), {t[0]: t for t in toks}
    for tid, form, upos, head, deprel in toks:
        base = deprel.split(":")[0]
        is_clausal = deprel in CLAUSE_DEPRELS or base in CLAUSE_DEPRELS
        if is_clausal and upos in ("VERB", "AUX"):
            # walk left to the clause's leftmost dependent (its subordinator,
            # subject, or conjunction) so the cut precedes the whole clause
            left = tid
            for t2 in toks:
                if t2[0] < tid and str(t2[3]) == str(tid):
                    left = min(left, t2[0])
            starts.add(left)
        if form.lower() == "for" and upos in ("SCONJ", "CCONJ"):   # T9 analogue
            starts.add(tid)
    return starts


def segment(line: str, toks) -> list:
    """Split one ATU line into Marschall cola."""
    words = re.findall(r"\S+", line)
    if not toks or len(words) < 4:
        return [line]
    # The parse covers the WHOLE verse; this line is a fragment of it. Locate the
    # fragment as a contiguous token window, or alignment drifts and cuts land
    # mid-phrase.
    nform = [norm(t[1]) for t in toks]
    nword = [norm(w) for w in words]
    offset = None
    for s in range(len(nform) - len(nword) + 1):
        if nform[s:s + len(nword)] == nword:
            offset = s
            break
    if offset is None:
        # No reliable alignment — but L2 is a LAW, so fall through to its
        # enforcement below rather than returning the line untouched.
        cuts = []
    else:
        starts = clause_starts(toks)
        cuts = [wi for wi in range(1, len(words))
                if toks[offset + wi][0] in starts]
    pieces, prev = [], 0
    for c in cuts + [len(words)]:
        if c > prev:
            pieces.append(" ".join(words[prev:c]))
            prev = c
    pieces = [p for p in pieces if p.strip()]
    if not pieces:
        return [line]
    # L2 is a LAW: nothing over 35 syllables survives. If a piece still exceeds
    # it, cut at the midpoint word — crude, and flagged in the report.
    out = []
    for p in pieces:
        while syllables(p) > 35:
            pw = p.split()
            # cut at the comma nearest the syllable midpoint — the least-bad
            # parse-free juncture, and flagged as such in the report
            commas = [i for i, w in enumerate(pw[:-1]) if w.endswith((",", ";", ":"))]
            idx = min(commas, key=lambda i: abs(i - len(pw) // 2)) + 1 \
                if commas else len(pw) // 2
            out.append(" ".join(pw[:idx]))
            p = " ".join(pw[idx:])
        out.append(p)
    return [o for o in out if o.strip()]


def label(n: int) -> str:
    if n < 7:
        return "comma (L1)"
    if n <= 9:
        return "comma/colon (L1)"
    if n <= 25:
        return "colon (T1)"
    if n <= 35:
        return "long colon (L2 ok)"
    return "**L2 VIOLATION**"


def main() -> int:
    book = sys.argv[1] if len(sys.argv) > 1 else "1nephi"
    chapter = sys.argv[2] if len(sys.argv) > 2 else "3"
    verses = load_chapter(book, chapter)
    parses = load_parses(book)

    atu_total = mar_total = 0
    viol = over25 = 0
    rows = []
    for vs, lines in verses:
        vtext = " ".join(lines)
        toks = parses.get(norm(vtext), [])
        for line in lines:
            n = syllables(line)
            atu_total += 1
            if n > 35:
                viol += 1
            if n > 25:
                over25 += 1
            cola = segment(line, toks)
            mar_total += len(cola)
            rows.append((vs, line, n, cola))

    print(f"# Marschall view — {book} {chapter}\n")
    print(f"Deployed ATU lines: **{atu_total}**   "
          f"Marschall cola: **{mar_total}**   "
          f"ratio {mar_total/atu_total:.2f}x\n")
    print(f"ATU lines over Marschall's T1 ceiling (25 syll): **{over25}** "
          f"({100*over25/atu_total:.0f}%)")
    print(f"ATU lines breaking L2, the 35-syllable LAW: **{viol}** "
          f"({100*viol/atu_total:.0f}%)\n")
    print("---\n")
    for vs, line, n, cola in rows:
        mark = "  ← " + label(n) if n > 25 else ""
        print(f"**{chapter}:{vs}**  ({n} syll){mark}")
        print(f"> ATU: {line}")
        if len(cola) > 1:
            for c in cola:
                print(f">   | {c}  *({syllables(c)})*")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
