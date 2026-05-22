#!/usr/bin/env python3
"""BoFM pure-method generator — v0 -> UD -> clause-atoms -> surface-order ATU
lines, anchored ENTIRELY on v0 (LDS versification prose). Zero dependence on the
hand-edited v2-mine breaks: stanza parses each verse, bofm_v1_fabric segments by
UD clause structure, and lines render in surface order with exact original
punctuation (char-offset slice of the verse text). This is the initial PURE-
METHOD segmentation the BoFM canon appliers (apply_rule_*) then refine.

Usage (needs atu-method on PYTHONPATH, repo .venv):
  PYTHONPATH=../atu-method .venv/Scripts/python.exe scripts/bofm_generate.py 1nephi 1
  (book, chapter; omit chapter for whole book)
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from bofm_v1_fabric import clause_atoms  # noqa: E402  (duck-typed tokens)

V0 = REPO / "data" / "text-files" / "v0-bofm-original"
BOOKFILE = {
    "1nephi": "1_Nephi.txt", "2nephi": "2_Nephi.txt", "jacob": "Jacob.txt",
    "enos": "Enos.txt", "jarom": "Jarom.txt", "omni": "Omni.txt",
    "words-of-mormon": "Words_of_Mormon.txt", "mosiah": "Mosiah.txt",
    "alma": "Alma.txt", "helaman": "Helaman.txt", "3nephi": "3_Nephi.txt",
    "4nephi": "4_Nephi.txt", "mormon": "Mormon.txt", "ether": "Ether.txt",
    "moroni": "Moroni.txt",
}
_REF = re.compile(r"^(.+?) (\d+):(\d+)$")


class Tok:
    __slots__ = ("id", "head", "deprel", "upos", "lemma", "form", "start", "end")

    def __init__(self, w):
        self.id, self.head = w.id, w.head
        self.deprel, self.upos = w.deprel, w.upos
        self.lemma, self.form = w.lemma, w.text
        self.start, self.end = w.start_char, w.end_char


class Sent:
    def __init__(self, toks):
        self.tokens = toks


_nlp = None


def nlp():
    global _nlp
    if _nlp is None:
        import stanza
        _nlp = stanza.Pipeline("en", processors="tokenize,pos,lemma,depparse",
                               verbose=False, download_method=None)
    return _nlp


def read_v0(book):
    """{(chap, verse): verse_text} from v0-bofm-original (verse-keyed prose)."""
    text = (V0 / BOOKFILE[book]).read_text(encoding="utf-8")
    out, ref = {}, None
    for line in text.splitlines():
        m = _REF.match(line.strip())
        if m:
            ref = (int(m.group(2)), int(m.group(3))); out[ref] = ""
        elif ref is not None and line.strip():
            out[ref] = (out[ref] + " " + line.strip()).strip()
    return out


def verse_atu_lines(verse_text):
    """Pure-method ATU lines for one verse: surface-order display segments, each
    sliced verbatim from verse_text (exact punctuation/spacing preserved)."""
    doc = nlp()(verse_text)
    spans = []                       # (start, end, atom_id)
    aid = 0
    for sent in doc.sentences:
        toks = [Tok(w) for w in sent.words]
        for atom in clause_atoms(Sent(toks)):
            for t in atom:
                spans.append((t.start, t.end, aid))
            aid += 1
    spans.sort(key=lambda s: s[0])
    lines, cur_id, lo, hi = [], None, None, None
    for start, end, a in spans:
        if a != cur_id and cur_id is not None:
            lines.append(verse_text[lo:hi].strip())
            lo = None
        if lo is None:
            lo = start
        hi = end; cur_id = a
    if lo is not None:
        lines.append(verse_text[lo:hi].strip())
    lines = [ln for ln in lines if ln]
    # Punctuation attaches BACKWARD (Stan's convention: a line ends with its
    # punctuation, never opens with it). Move any leading ,;:.!?)— onto the
    # previous line; this is a rendering concern, distinct from the canon's
    # rule-level merges (R9 cc-forward, etc.) applied downstream.
    fixed = []
    for ln in lines:
        m = re.match(r"^([,;:.!?)—–’\"]+)\s*(.*)$", ln)
        if m and fixed:
            fixed[-1] = fixed[-1] + m.group(1)
            rest = m.group(2).strip()
            if rest:
                fixed.append(rest)
        else:
            fixed.append(ln)
    # R9: a bare coordinating conjunction never stands as its own line — it LEADS
    # its content, so merge it forward into the next line (the clause it joins).
    _CC = {"and", "or", "but", "nor", "yet"}
    out = []
    carry = ""
    for ln in fixed:
        ln = (carry + " " + ln).strip() if carry else ln
        carry = ""
        if ln.strip().lower().rstrip(",;:") in _CC:
            carry = ln
        else:
            out.append(ln)
    if carry:
        (out.append(carry) if not out else out.__setitem__(-1, out[-1] + " " + carry))
    return out


def generate(book, chap=None):
    verses = read_v0(book)
    out = []
    for (c, v) in sorted(verses):
        if chap is not None and c != chap:
            continue
        out.append(f"{c}:{v}")
        out.extend(verse_atu_lines(verses[(c, v)]))
        out.append("")
    return out


OUT_DIR = REPO / "data" / "text-files" / "v2-puremethod-draft"


def write_book(book):
    """Generate the whole book and write a pure-method v-file (v2-mine format:
    verse marker + one ATU per line). Draft layer, parallel to v2-mine — the
    systematic PRE-applier segmentation the canon appliers refine next."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lines = generate(book)
    path = OUT_DIR / f"{book}.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main():
    if "--write" in sys.argv:
        book = sys.argv[1]
        print(f"wrote {write_book(book)}")
        return
    book = sys.argv[1] if len(sys.argv) > 1 else "1nephi"
    chap = int(sys.argv[2]) if len(sys.argv) > 2 else None
    print("\n".join(generate(book, chap)))


if __name__ == "__main__":
    main()
