#!/usr/bin/env python3
"""Build the Book-of-Mormon Text-Fabric (the queryable colometric fabric, BHSA-ecosystem format).

Node types (coarsest -> finest):
  book  -> chapter -> verse -> atu -> word(slot)
The `atu` layer is the distinctive one: each node spans the words of one DEPLOYED ATU line
(the colometric segmentation that ships to bomreader.com), so the fabric is queryable BY
atomic-thought-unit, not just by verse.

Slot (word) features come from the cached Stanza UD parse (verse-keyed, scripts/bofm_generate.parse_book):
  form, lemma, pos (upos), deprel  + a `head` edge (dependent -> governor).
NB: the dependency layer is the *weak* Stanza-modern-English parse -- it is the layer the
PCEEC-trained EModE parser will REPLACE. form/lemma/pos are solid; head/deprel are provisional
(flagged in featureMeta). The TF structure + morphology + ATU layer are sound now; the syntax
layer upgrades in place later.

Token -> verse is free (the parse is verse-keyed). Token -> atu is an alnum-offset walk within
each verse (robust to whitespace/punctuation differences between the parse and the v2 lines).

Output: data/tf/0.1/*.tf   (load with: Fabric(locations='data/tf', modules='0.1'))
"""
import re, sys, unicodedata
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8")
from tf.convert.walker import CV
from tf.fabric import Fabric
import bofm_generate as B

def _nfc(s):
    return unicodedata.normalize("NFC", s)

REPO = Path(__file__).resolve().parent.parent
TF_DIR = REPO / "data" / "tf"
# version + syntax-layer provenance are CLI-overridable so v0.2 (EModE re-parse) builds as a NEW
# module dir (audit #4: never rewrite a version in place — TF caches by version).
#   python build_tf.py [VERSION] [SYN_SOURCE]
VERSION = sys.argv[1] if len(sys.argv) > 1 else "0.1"
SYN_SOURCE = sys.argv[2] if len(sys.argv) > 2 else "stanza-en"
BOOK_ORDER = list(B.BOOKFILE.keys())
BOOK_NAME = {  # display names
    "1nephi": "1 Nephi", "2nephi": "2 Nephi", "jacob": "Jacob", "enos": "Enos",
    "jarom": "Jarom", "omni": "Omni", "words-of-mormon": "Words of Mormon",
    "mosiah": "Mosiah", "alma": "Alma", "helaman": "Helaman", "3nephi": "3 Nephi",
    "4nephi": "4 Nephi", "mormon": "Mormon", "ether": "Ether", "moroni": "Moroni",
}
_REF = re.compile(r"^\d+:\d+$")


def _alnum(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def v2_lines_by_verse(book):
    """{(c,v): [atu_line, ...]} from the deployed v2 file for a book."""
    out, cur = {}, None
    for ln in B._v2_target(book).read_text(encoding="utf-8").splitlines():
        s = ln.strip()
        if _REF.match(s):
            c, v = s.split(":"); cur = (int(c), int(v)); out[cur] = []
        elif cur and s:
            out[cur].append(s)
    return out


def atu_char_ranges(verse_text, lines):
    """[(start,end)] raw char-ranges of each v2 atu-line within verse_text (Stanza token
    offsets are verse-relative, so a token belongs to the line whose raw range contains
    token.start -- exact, punctuation included). v2 lines are contiguous substrings of the
    verse text (parity guarantees it), tolerant here of internal-whitespace differences."""
    ranges, pos = [], 0
    n = len(verse_text)
    for line in lines:
        ls = line.strip()
        while pos < n and verse_text[pos].isspace():
            pos += 1
        start, li, cur = pos, 0, pos
        while li < len(ls):
            if ls[li].isspace():
                li += 1; continue
            while cur < n and verse_text[cur].isspace():
                cur += 1
            cur += 1; li += 1
        ranges.append((start, cur)); pos = cur
    if ranges:
        ranges[-1] = (ranges[-1][0], n)        # last line absorbs any trailing chars
    return ranges


def range_index(offset, ranges):
    for i, (s, e) in enumerate(ranges):
        if s <= offset < e:
            return i
    return len(ranges) - 1


def director(cv):
    stats = {"books": 0, "verses": 0, "atus": 0, "words": 0, "sentences": 0, "misaligned": [], "atu_count_fail": []}
    ov_keys = set(B._overrides().keys())       # "book c:v" -> v2-LLM-adjudicated boundary provenance
    for book in BOOK_ORDER:
        parsed = B.parse_book(book)            # {(c,v): [[Tok,...sentence...], ...]}
        v2 = v2_lines_by_verse(book)
        verses_v0 = B.read_v0(book)            # {(c,v): verse_text} -- token offsets are relative to this
        bk = cv.node("book")
        cv.feature(bk, book=BOOK_NAME[book], book_id=book)
        stats["books"] += 1
        cur_chap, ch = None, None
        for (c, v) in sorted(parsed):
            if c != cur_chap:
                assert cur_chap is None or c > cur_chap, f"non-monotonic chapter {book} {c}<= {cur_chap}"  # audit #12
                if ch is not None:
                    cv.terminate(ch)
                ch = cv.node("chapter")
                cv.feature(ch, chapter=c, book=BOOK_NAME[book])
                cur_chap = c
            verse_text = verses_v0[(c, v)]
            lines = v2.get((c, v)) or [verse_text]   # fallback: whole verse = one atu
            ranges = atu_char_ranges(verse_text, lines)
            b_source = "v2-llm" if f"{book} {c}:{v}" in ov_keys else "mechanical-v1"   # audit #5 provenance
            vs = cv.node("verse")
            cv.feature(vs, chapter=c, verse=v, ref=f"{c}:{v}", book=BOOK_NAME[book])
            stats["verses"] += 1
            cur_idx, atu_node, atus_here = -1, None, 0
            head_pairs, assigned_alnum = [], 0
            for sent in parsed[(c, v)]:
                snode = cv.node("sentence")      # audit #1: preserve the parse-sentence layer
                cv.feature(snode, ref=f"{c}:{v}")
                stats["sentences"] += 1
                localmap = {}
                for tok in sent:
                    idx = range_index(tok.start, ranges)
                    if idx != cur_idx:
                        if atu_node is not None:
                            cv.terminate(atu_node)
                        atu_node = cv.node("atu")
                        cv.feature(atu_node, atu_seq=idx + 1, atu_text=_nfc(lines[idx].strip()),
                                   ref=f"{c}:{v}", boundary_source=b_source)
                        cur_idx = idx; atus_here += 1; stats["atus"] += 1
                    s = cv.slot()
                    cv.feature(s, form=_nfc(tok.form),                       # audit #8 NFC
                               lemma=_nfc(tok.lemma) if tok.lemma else _nfc(tok.form),
                               lemma_source="stanza" if tok.lemma else "fallback-form",  # audit #11
                               pos=tok.upos or "X", upos=tok.upos or "X",     # audit #2 canonical upos
                               deprel=tok.deprel or "_", udrel=tok.deprel or "_",         # audit #2 canonical udrel
                               syn_source=SYN_SOURCE,                          # audit #5 provenance
                               is_root=1 if (not tok.head or tok.head == 0) else 0)       # audit #1 root flag
                    localmap[tok.id] = s
                    assigned_alnum += len(_alnum(tok.form))
                    stats["words"] += 1
                for tok in sent:                # head edges within the sentence (dep -> governor)
                    if tok.head and tok.head in localmap and tok.id in localmap:
                        head_pairs.append((localmap[tok.id], localmap[tok.head]))
                cv.terminate(snode)
            if atu_node is not None:
                cv.terminate(atu_node)
            cv.terminate(vs)
            for dep, gov in head_pairs:
                cv.edge(dep, gov, head=None)
            if assigned_alnum != len(_alnum(verse_text)):
                stats["misaligned"].append(f"{book} {c}:{v}")
            if atus_here != len(lines):          # audit #3: fail-loud ATU-count identity
                stats["atu_count_fail"].append(f"{book} {c}:{v} (built={atus_here} v2={len(lines)})")
        if ch is not None:
            cv.terminate(ch)
        cv.terminate(bk)
        print(f"  {book}: done", flush=True)
    print(f"\nNODES: books={stats['books']} verses={stats['verses']} sentences={stats['sentences']} "
          f"atus={stats['atus']} words={stats['words']}")
    if stats["atu_count_fail"]:                  # HARD fail — never absorb-into-last silently
        raise SystemExit(f"ATU-COUNT MISMATCH in {len(stats['atu_count_fail'])} verses (audit #3): "
                         + ", ".join(stats['atu_count_fail'][:10]))
    if stats["misaligned"]:
        raise SystemExit(f"ALNUM DRIFT in {len(stats['misaligned'])} verses: " + ", ".join(stats['misaligned'][:10]))
    print("alignment: CLEAN; ATU-count identity: CLEAN")


META = {
    "": dict(
        name="bofm", version=VERSION,
        purpose="Book of Mormon colometric Text-Fabric (queryable by ATU)",
        source="v0-bofm-original + cached UD parse + deployed v2 ATU segmentation",
        syntaxSource=SYN_SOURCE,
        writtenBy="readers-bofm/scripts/build_tf.py",
    ),
    "otext": {
        "fmt:text-orig-full": "{form} ",
        "sectionTypes": "book,chapter,verse",
        "sectionFeatures": "book,chapter,verse",
        "structureTypes": "book,chapter,verse,atu",          # audit #7: atu addressable as structure
        "structureFeatures": "book,chapter,verse,atu_seq",
    },
    "form": {"description": "word surface form, NFC-normalized (1830 BoFM orthography)"},
    "lemma": {"description": "lemma (Stanza)"},
    "lemma_source": {"description": "stanza | fallback-form (audit #11: distinguishes failed lemmatization)"},
    "pos": {"description": "UD upos (Stanza); alias of upos"},
    "upos": {"description": "canonical cross-corpus UPOS (audit #2 harmonization; same feature name across all corpus TFs)"},
    "deprel": {"description": "UD dependency relation; alias of udrel -- PROVISIONAL (weak Stanza-modern-English parse; replaced by the EModE parser at v0.2)"},
    "udrel": {"description": "canonical cross-corpus UD relation (audit #2 harmonization) -- PROVISIONAL until v0.2"},
    "syn_source": {"description": "provenance of the syntax layer per token (audit #5): stanza-en (v0.1) | emode-pceec-* (v0.2+)"},
    "is_root": {"description": "1 if this token is its sentence's dependency root (head==0), else 0 (audit #1)"},
    "head": {"description": "dependency head edge dep->governor -- PROVISIONAL (see udrel)"},
    "book": {"description": "book display name"},
    "book_id": {"description": "book slug (1nephi, 2nephi, ...)"},
    "chapter": {"description": "chapter number"},
    "verse": {"description": "verse number"},
    "ref": {"description": "chapter:verse reference"},
    "atu_seq": {"description": "1-based sequence of the ATU line within its verse"},
    "atu_text": {"description": "the deployed ATU line text (the colometric unit shipped to bomreader.com)"},
    "boundary_source": {"description": "provenance of the ATU boundary (audit #5): mechanical-v1 | v2-llm (adjudicated override)"},
}


def main():
    out = TF_DIR / VERSION
    out.mkdir(parents=True, exist_ok=True)
    print(f"building BoFM TF v{VERSION} (syntax={SYN_SOURCE}) -> {out}")
    cv = CV(Fabric(locations=str(out)))
    ok = cv.walk(
        director,
        slotType="word",
        otext=META["otext"],
        generic=META[""],
        intFeatures={"chapter", "verse", "atu_seq", "is_root"},
        featureMeta={k: v for k, v in META.items() if k not in ("", "otext")},
        warn=True,
    )
    print("BUILD OK" if ok else "BUILD FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
