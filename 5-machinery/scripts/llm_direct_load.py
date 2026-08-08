#!/usr/bin/env python3
"""Load LLM-direct CoNLL-U parses into the pure-method pipeline's parse structure.

The 2026-05-09 pilot (data/parses/llm-direct/PILOT_FINDINGS.md) validated that
Claude-direct parsing matches stanza on easy sentences and is DECISIVELY better
on EME-stress constructions (formal inversion, topicalization) — the exact cases
where stanza produces internally-inconsistent parses (two heads for one token,
clauses buried as relatives under a nominal root) that fracture the colometry.

LLM-direct CoNLL-U has full UD (id/form/lemma/upos/head/deprel) + a `# text =`
per sentence but NO char offsets, and is keyed one sentence per verse. This
loader aligns each parse sentence to its v0 verse (greedy text match, in order),
recovers char offsets by walking the verse text, and returns
{(chap,verse): [[Tok,...sentence...], ...]} — drop-in for parse_book's output, so
bofm_generate can render from the higher-quality parse where it exists.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "5-machinery" / "scripts"))
import bofm_generate as G  # noqa: E402  (Tok, read_v0, BOOKFILE)

LLM_DIR = REPO / "data" / "parses" / "llm-direct"


def _norm(s):
    return re.sub(r"\s+", " ", s).strip()


def _read_conllu(path):
    """[(text, [(id, form, lemma, upos, head, deprel), ...]), ...]."""
    sents, text, toks = [], None, []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("# text = "):
            text = line[len("# text = "):]
        elif line.startswith("#"):
            continue
        elif line.strip() == "":
            if toks:
                sents.append((text, toks)); toks = []
            text = None
        else:
            c = line.split("\t")
            if len(c) >= 8 and "-" not in c[0] and "." not in c[0]:
                toks.append((c[0], c[1], c[2], c[3], c[6], c[7]))
    if toks:
        sents.append((text, toks))
    return sents


def _toks_with_offsets(token_rows, vtext, cursor):
    """Build Tok list for one sentence, recovering char offsets by a MONOTONIC
    walk of vtext from `cursor` (the LLM may tokenize differently from v0 — e.g.
    splitting "noon-day" into noon/-/day — and may alter a form, so match
    literally when possible, else by the form's alnum core, else assign a
    zero-width span without advancing). Returns (toks, new_cursor)."""
    out = []
    for tid, form, lemma, upos, head, deprel in token_rows:
        while cursor < len(vtext) and vtext[cursor].isspace():
            cursor += 1
        if vtext[cursor:cursor + len(form)] == form:
            start, end = cursor, cursor + len(form)
        else:
            core = re.sub(r"[^0-9A-Za-z]", "", form)
            m = re.search(re.escape(core), vtext[cursor:cursor + 60]) if core else None
            if m:
                start, end = cursor + m.start(), cursor + m.end()
            else:
                start = end = cursor      # form not in surface (altered) — no advance
        t = G.Tok.__new__(G.Tok)
        t.id, t.head, t.deprel, t.upos = tid, head, deprel, upos
        t.lemma, t.form = lemma, form
        t.start, t.end = start, end
        out.append(t)
        cursor = end
    return out, cursor


def load_llm_direct(book):
    """{(chap,verse): [[Tok,...], ...]} from the LLM-direct CoNLL-U, aligned to v0
    and char-offset-recovered. Raises FileNotFoundError if the book has no
    LLM-direct parse (caller falls back to the stanza cache)."""
    path = LLM_DIR / f"{book}.conllu"
    if not path.exists():
        raise FileNotFoundError(path)
    sents = _read_conllu(path)
    verses = G.read_v0(book)
    keys = sorted(verses)
    out = {}
    si = 0
    for key in keys:
        vtext = verses[key]
        vn = _norm(vtext)
        collected, acc, cursor = [], "", 0
        while si < len(sents):
            stext, rows = sents[si]
            toks, cursor = _toks_with_offsets(rows, vtext, cursor)
            collected.append(toks)
            si += 1
            acc = _norm(acc + " " + (stext or _norm(" ".join(r[1] for r in rows))))
            if acc == vn or vn.startswith(acc) is False:
                # stop when we've covered the verse (exact) or overshot
                if acc == vn:
                    break
                if len(acc) >= len(vn):
                    break
        out[key] = collected
    return out


def _main():
    book = sys.argv[1] if len(sys.argv) > 1 else "1nephi"
    chap = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    parsed = load_llm_direct(book)
    verses = G.read_v0(book)
    for (c, v) in sorted(verses):
        if c != chap:
            continue
        print(f"{c}:{v}")
        for ln in G.verse_atu_lines(verses[(c, v)], parsed.get((c, v), [])):
            print(f"  | {ln}")


if __name__ == "__main__":
    _main()
