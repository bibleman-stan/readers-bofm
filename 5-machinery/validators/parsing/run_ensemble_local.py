"""
Run local 2-parser ensemble (stanza + spaCy) on a single chapter.

Phase 0 reconnaissance: produces per-parser CoNLL-U files for downstream
agreement_measure.py.  CPU-only, takes ~30-60 seconds per chapter.

Usage:
    python 5-machinery/validators/parsing/run_ensemble_local.py --book alma --chapter 30
    python 5-machinery/validators/parsing/run_ensemble_local.py --book enos        # whole book

Outputs:
    data/parses/ensemble/stanza/{book}-{ch?}.conllu
    data/parses/ensemble/spacy/{book}-{ch?}.conllu
"""
import argparse
import os
import re
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent.parent
CORPUS_DIR = REPO / "data/text-files/v2"
OUT_DIR = REPO / "data/parses/ensemble"

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

VERSE_REF_RE = re.compile(r"^\d+:\d+\s*$")


def extract_prose(book_id: str, chapter_num: int | None = None) -> tuple[str, int]:
    fp = CORPUS_DIR / BOOK_FILES[book_id]
    with open(fp, encoding="utf-8") as f:
        lines = f.readlines()
    in_chapter = chapter_num is None
    prose = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if VERSE_REF_RE.match(s):
            if chapter_num is not None:
                if s.startswith(f"{chapter_num}:"):
                    in_chapter = True
                    continue
                elif in_chapter and s.startswith(f"{chapter_num + 1}:"):
                    in_chapter = False
                    break
            continue
        if in_chapter:
            prose.append(s)
    return " ".join(prose), len(prose)


def parse_stanza(text: str) -> str:
    import stanza
    from stanza.utils.conll import CoNLL
    if not hasattr(parse_stanza, "nlp"):
        parse_stanza.nlp = stanza.Pipeline(
            "en", processors="tokenize,pos,lemma,depparse",
            verbose=False, use_gpu=False,
        )
    doc = parse_stanza.nlp(text)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".conllu", delete=False) as f:
        tmppath = f.name
    CoNLL.write_doc2conll(doc, tmppath)
    with open(tmppath, encoding="utf-8") as f:
        out = f.read()
    os.unlink(tmppath)
    return out


def parse_spacy(text: str) -> str:
    """Parse with spaCy and emit CoNLL-U directly (no spacy_conll dep).

    spaCy uses ClearNLP-style dep labels by default but is also UD-compatible
    via the same column ordering.  We emit dep_ as deprel; that's English
    spaCy's UD-like label set.
    """
    import spacy
    if not hasattr(parse_spacy, "nlp"):
        parse_spacy.nlp = spacy.load("en_core_web_sm")
    doc = parse_spacy.nlp(text)
    lines = []
    for sent_idx, sent in enumerate(doc.sents):
        lines.append(f"# sent_id = {sent_idx}")
        lines.append(f"# text = {sent.text}")
        # Build mapping from doc-level token index → in-sentence 1-based index
        sent_token_map = {tok.i: i + 1 for i, tok in enumerate(sent)}
        for tok in sent:
            in_sent_id = sent_token_map[tok.i]
            head_id = sent_token_map.get(tok.head.i, 0) if tok.head.i != tok.i else 0
            lines.append("\t".join([
                str(in_sent_id),
                tok.text,
                tok.lemma_ or "_",
                tok.pos_ or "_",
                tok.tag_ or "_",
                "_",  # feats — spaCy provides via morph but skip for simplicity
                str(head_id),
                tok.dep_ or "_",
                "_",
                "_",
            ]))
        lines.append("")
    return "\n".join(lines)


PARSERS = {
    "stanza": parse_stanza,
    "spacy": parse_spacy,
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book", required=True, choices=list(BOOK_FILES.keys()))
    ap.add_argument("--chapter", type=int, default=None,
                    help="Specific chapter; omit to parse the whole book")
    args = ap.parse_args()

    text, line_count = extract_prose(args.book, args.chapter)
    label = f"{args.book}-ch{args.chapter}" if args.chapter else args.book
    print(f"\n[{label}] {line_count} ATU lines, {len(text)} chars")
    print()

    for name, fn in PARSERS.items():
        out_dir = OUT_DIR / name
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{label}.conllu"

        t0 = time.time()
        print(f"[{name}] parsing...")
        conllu = fn(text)
        elapsed = time.time() - t0
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(conllu)
        n_tokens = sum(
            1 for line in conllu.split("\n")
            if line and not line.startswith("#") and "\t" in line
        )
        print(f"  saved {n_tokens} tokens to {out_path.relative_to(REPO)} ({elapsed:.1f}s)")
    print()


if __name__ == "__main__":
    main()
