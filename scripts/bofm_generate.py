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
import json
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

    @classmethod
    def from_dict(cls, d):
        t = cls.__new__(cls)
        (t.id, t.head, t.deprel, t.upos, t.lemma, t.form, t.start, t.end) = d
        return t

    def as_list(self):
        return [self.id, self.head, self.deprel, self.upos, self.lemma, self.form,
                self.start, self.end]


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


CACHE_DIR = REPO / "data" / "parses" / "v0-cache"


def parse_book(book):
    """{(chap,verse): [[Tok,...sentence...], ...]} for the whole book — UD parse
    of the v0 (LDS-versification) prose, CACHED to JSON so rule iteration doesn't
    re-run stanza (a full-book parse is minutes; the cache load is instant). The
    cache IS the v1 substrate; ensemble+Claude adjudication is the future quality
    lift that would replace what stanza writes here."""
    cache = CACHE_DIR / f"{book}.json"
    if cache.exists():
        raw = json.loads(cache.read_text(encoding="utf-8"))
        return {tuple(int(x) for x in k.split(":")): [[Tok.from_dict(d) for d in s]
                for s in sents] for k, sents in raw.items()}
    verses = read_v0(book)
    out = {}
    for (c, v), text in verses.items():
        doc = nlp()(text)
        out[(c, v)] = [[Tok(w) for w in sent.words] for sent in doc.sentences]
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({f"{c}:{v}": [[t.as_list() for t in s] for s in sents]
                                 for (c, v), sents in out.items()}), encoding="utf-8")
    return out


def _merge_back(segs, i):
    """Merge segment i into the previous segment (surface-contiguous)."""
    segs[i - 1]["hi"] = segs[i]["hi"]
    segs[i - 1]["toks"].extend(segs[i]["toks"])
    del segs[i]


def _rule_passes(segs):
    """UD-aware canon binding rules, applied as segment merges on the pure-method
    segmentation (ported into the generator — operates ONLY on pure-method data,
    never the hand-edits; validated against the canon detectors via run_all)."""
    # R29 (bare infinitival orphan integrity): an infinitive segment opening with
    # "to <VERB|AUX>" is not its own thought — it binds to its governor in the
    # prior segment ("I ordain you to be a teacher) / to preach repentance").
    i = 1
    while i < len(segs):
        toks = segs[i]["toks"]
        if len(toks) >= 2 and toks[0].form.lower() == "to" and toks[1].upos in ("VERB", "AUX"):
            _merge_back(segs, i)
        else:
            i += 1
    # AICTP frame binds FORWARD (Hebrew B5): a segment whose only verbs are the
    # empty frame "came to pass" is not a thought on its own (fails the
    # bidirectional test) -> merge into the clause it introduces.
    def _bare_aictp(seg):
        verbs = [t for t in seg["toks"] if t.upos in ("VERB", "AUX")]
        return bool(verbs) and {(t.lemma or "").lower() for t in verbs} <= {"come", "pass"}
    out, carry = [], None
    for seg in segs:
        if carry is not None:
            seg = {"aid": seg["aid"], "lo": carry["lo"], "hi": seg["hi"],
                   "toks": carry["toks"] + seg["toks"]}
            carry = None
        if _bare_aictp(seg):
            carry = seg
        else:
            out.append(seg)
    if carry is not None:
        out.append(carry)
    return out


def verse_atu_lines(verse_text, sentences):
    """Pure-method ATU lines for one verse: surface-order display segments, each
    sliced verbatim from verse_text (exact punctuation/spacing preserved).
    `sentences` is the pre-parsed UD (list of per-sentence Tok lists)."""
    # Build surface-contiguous display SEGMENTS that keep their tokens, so the
    # UD-aware binding rule-passes can operate before we render to text.
    spans = []                       # (start, end, atom_id, Tok)
    aid = 0
    for toks in sentences:
        for atom in clause_atoms(Sent(toks)):
            for t in atom:
                spans.append((t.start, t.end, aid, t))
            aid += 1
    spans.sort(key=lambda s: s[0])
    segs = []                        # each: {'lo','hi','toks'}
    for start, end, a, t in spans:
        if segs and a == segs[-1]["aid"]:
            segs[-1]["hi"] = end; segs[-1]["toks"].append(t)
        else:
            segs.append({"aid": a, "lo": start, "hi": end, "toks": [t]})
    segs = _rule_passes(segs)
    lines = [verse_text[s["lo"]:s["hi"]].strip() for s in segs]
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
    # R9 + opener-integrity: a line that is ONLY a leader word (coordinating
    # conjunction or a subordinate/relative opener) never stands alone — it LEADS
    # its content, so merge it forward into the clause it introduces.
    _LEADERS = {"and", "or", "but", "nor", "yet", "yea",     # coordinators / launchers (R9, M3)
                "that", "which", "who", "whom", "whose",     # relativizers / complementizer
                "when", "where", "while", "if", "because",   # subordinate openers
                "behold", "lo", "wherefore", "now", "for"}   # discourse launchers — lead, never alone
    _SPEECH_FRAME = {"saying", "saith"}                      # speech-frame -> binds BACKWARD to its verb

    def _all_leaders(s):
        words = [w.strip(",;:.!?—–’\"()").lower() for w in s.split()]
        words = [w for w in words if w]
        return bool(words) and all(w in _LEADERS for w in words)

    out = []
    carry = ""
    for ln in fixed:
        ln = (carry + " " + ln).strip() if carry else ln
        carry = ""
        bare = ln.strip().lower().rstrip(",;:.!?")
        if bare in _SPEECH_FRAME and out:   # lone "saying"/"saith" binds backward to the speech verb
            out[-1] = out[-1].rstrip() + " " + ln.strip()
        elif _all_leaders(ln):              # content-less launcher ("yea, and", "and behold") leads forward
            carry = ln
        else:
            out.append(ln)
    if carry:
        (out.append(carry) if not out else out.__setitem__(-1, out[-1] + " " + carry))
    return out


def generate(book, chap=None):
    verses = read_v0(book)
    parsed = parse_book(book)
    out = []
    for (c, v) in sorted(verses):
        if chap is not None and c != chap:
            continue
        out.append(f"{c}:{v}")
        out.extend(verse_atu_lines(verses[(c, v)], parsed.get((c, v), [])))
        out.append("")
    return out


OUT_DIR = REPO / "data" / "text-files" / "v2-puremethod-draft"


CONLLU_OUT = REPO / "data" / "parses" / "v0-cache-conllu"


def write_conllu(book):
    """Emit the cached v0 parse as standard CoNLL-U keyed to match the pure-method
    v-file (so the canon validators can score the pure-method edition via the
    BOFM_CONLLU_DIR override). # text = the verbatim verse-text span so
    line_mapping's char-anchor locks onto the v-file content."""
    verses = read_v0(book)
    parsed = parse_book(book)
    out, sid = [], 0
    for (c, v) in sorted(verses):
        vtext = verses[(c, v)]
        for sent in parsed.get((c, v), []):
            if not sent:
                continue
            lo, hi = min(t.start for t in sent), max(t.end for t in sent)
            out.append(f"# sent_id = {sid}")
            out.append(f"# text = {vtext[lo:hi]}")
            for t in sent:
                out.append("\t".join([str(t.id), t.form, t.lemma, t.upos, "_", "_",
                                       str(t.head), t.deprel, "_", "_"]))
            out.append("")
            sid += 1
    CONLLU_OUT.mkdir(parents=True, exist_ok=True)
    p = CONLLU_OUT / f"{book}.conllu"
    p.write_text("\n".join(out) + "\n", encoding="utf-8")
    return p


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
