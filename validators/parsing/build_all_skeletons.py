"""
Build skeletons for all 15 books once stanza parsing is complete.

For each book, splits its CoNLL-U into batches sized for parallel agent dispatch.

Tiny books (≤30 sentences): 1 batch
Small/medium: 15-sentence batches
Large books (Alma, 1/2/3 Nephi, Mosiah): 25-sentence batches to reduce agent count
"""
import argparse
import sys
from pathlib import Path
from build_skeleton import parse_stanza_sentences, blank_token_row

REPO = Path(__file__).resolve().parent.parent.parent
STANZA_DIR = REPO / "data/parses/ensemble/stanza"
LLM_DIR = REPO / "data/parses/llm-direct"

BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]

# Larger batches for large books to reduce total agent count
LARGE_BOOKS = {"alma", "1nephi", "2nephi", "3nephi", "mosiah"}
LARGE_BATCH_SIZE = 25
DEFAULT_BATCH_SIZE = 15


def build_book_skeletons(book_id: str):
    stanza_path = STANZA_DIR / f"{book_id}.conllu"
    if not stanza_path.exists():
        print(f"  [SKIP] {book_id}: stanza output not found at {stanza_path.name}")
        return None

    out_dir = LLM_DIR / f"{book_id}-batches"
    out_dir.mkdir(parents=True, exist_ok=True)

    sentences = list(parse_stanza_sentences(stanza_path))
    n_sents = len(sentences)
    n_tokens = sum(n for _, n in sentences)

    batch_size = LARGE_BATCH_SIZE if book_id in LARGE_BOOKS else DEFAULT_BATCH_SIZE
    n_batches = (n_sents + batch_size - 1) // batch_size

    for i in range(n_batches):
        batch = sentences[i * batch_size : (i + 1) * batch_size]
        out_path = out_dir / f"skeleton-{i+1:02d}.conllu"
        with open(out_path, "w", encoding="utf-8") as f:
            for block, _ in batch:
                f.write("\n".join(block) + "\n\n")

    print(f"  {book_id}: {n_sents} sentences, {n_tokens} tokens → {n_batches} batches "
          f"(batch size {batch_size}) in {out_dir.relative_to(REPO)}")
    return {"book": book_id, "sentences": n_sents, "tokens": n_tokens, "batches": n_batches}


def main():
    print(f"Building skeletons for {len(BOOKS)} books...\n")
    results = []
    for book in BOOKS:
        r = build_book_skeletons(book)
        if r:
            results.append(r)

    print(f"\n{'='*72}")
    print(f"{'BOOK':<20} {'SENTS':>8} {'TOKENS':>8} {'BATCHES':>10}")
    print("-" * 72)
    total_b = 0
    total_s = 0
    total_t = 0
    for r in results:
        print(f"  {r['book']:<18} {r['sentences']:>8} {r['tokens']:>8} {r['batches']:>10}")
        total_b += r["batches"]
        total_s += r["sentences"]
        total_t += r["tokens"]
    print("-" * 72)
    print(f"  {'TOTAL':<18} {total_s:>8} {total_t:>8} {total_b:>10}")


if __name__ == "__main__":
    main()
