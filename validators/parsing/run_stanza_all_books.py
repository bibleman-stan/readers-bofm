"""
Run stanza on all 15 books, output per-book CoNLL-U.

Used to build skeletons for the LLM-overlay annotation pipeline.
"""
import os
import re
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
CORPUS_DIR = REPO / "data/text-files/v2-mine"
OUT_DIR = REPO / "data/parses/ensemble/stanza"

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


def extract_prose(book_id):
    fp = CORPUS_DIR / BOOK_FILES[book_id]
    with open(fp, encoding="utf-8") as f:
        lines = f.readlines()
    prose = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if VERSE_REF_RE.match(s):
            continue
        prose.append(s)
    return " ".join(prose), len(prose)


def main():
    import stanza
    from stanza.utils.conll import CoNLL

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    nlp = stanza.Pipeline(
        "en", processors="tokenize,pos,lemma,depparse",
        verbose=False, use_gpu=False,
    )

    # Skip books we already have
    skip_set = set()
    for book_id in BOOK_FILES:
        out_path = OUT_DIR / f"{book_id}.conllu"
        if out_path.exists() and out_path.stat().st_size > 1000:
            skip_set.add(book_id)
            print(f"  [SKIP] {book_id}: already parsed at {out_path.relative_to(REPO)}")

    for book_id, fname in BOOK_FILES.items():
        if book_id in skip_set:
            continue
        text, line_count = extract_prose(book_id)
        print(f"\n[{book_id}] {line_count} ATU lines, {len(text)} chars")
        t0 = time.time()
        doc = nlp(text)
        elapsed = time.time() - t0

        out_path = OUT_DIR / f"{book_id}.conllu"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".conllu", delete=False) as f:
            tmppath = f.name
        CoNLL.write_doc2conll(doc, tmppath)
        with open(tmppath, encoding="utf-8") as f:
            conllu = f.read()
        os.unlink(tmppath)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(conllu)

        n_sents = len(doc.sentences)
        n_tokens = sum(len(s.words) for s in doc.sentences)
        print(f"  parsed in {elapsed:.1f}s: {n_sents} sentences, {n_tokens} tokens")
        print(f"  saved to {out_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
