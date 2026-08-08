"""
Build CoNLL-U annotation skeletons from stanza output, batched for parallel
LLM-overlay annotation.

Skeleton = stanza's tokens + IDs + text comments, with annotation columns
(LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL) replaced by '_'.

LLM agents fill in the blanked columns without modifying tokens, IDs, or
text — preventing the tokenization bugs we saw in the first dispatch.
"""
import argparse
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent.parent


def blank_token_row(line: str) -> str:
    """Blank annotation columns; preserve ID + FORM."""
    cols = line.split("\t")
    if len(cols) < 10:
        return line
    # ID FORM are cols 0,1; LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC are cols 2-9
    cols[2] = "_"  # LEMMA
    cols[3] = "_"  # UPOS
    cols[4] = "_"  # XPOS
    cols[5] = "_"  # FEATS
    cols[6] = "_"  # HEAD
    cols[7] = "_"  # DEPREL
    cols[8] = "_"  # DEPS
    cols[9] = "_"  # MISC
    return "\t".join(cols)


def parse_stanza_sentences(conllu_path: Path):
    """Yield (sent_block_lines, n_tokens) for each sentence."""
    block = []
    n_tokens = 0
    with open(conllu_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if block:
                    yield block, n_tokens
                    block = []
                    n_tokens = 0
                continue
            if line.startswith("#"):
                block.append(line)
            else:
                # token row
                cols = line.split("\t")
                try:
                    int(cols[0])
                    n_tokens += 1
                except (ValueError, IndexError):
                    pass
                block.append(blank_token_row(line))
    if block:
        yield block, n_tokens


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stanza-conllu", type=Path, required=True,
                    help="Stanza CoNLL-U output to use as skeleton source")
    ap.add_argument("--out-dir", type=Path, required=True,
                    help="Directory to write batch skeleton files")
    ap.add_argument("--batch-size", type=int, default=15,
                    help="Sentences per batch (default 15)")
    ap.add_argument("--prefix", default="skeleton",
                    help="Filename prefix (default 'skeleton')")
    args = ap.parse_args()

    sentences = list(parse_stanza_sentences(args.stanza_conllu))
    total_tokens = sum(n for _, n in sentences)
    print(f"Loaded {len(sentences)} sentences, {total_tokens} tokens")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    n_batches = (len(sentences) + args.batch_size - 1) // args.batch_size
    for i in range(n_batches):
        batch = sentences[i * args.batch_size : (i + 1) * args.batch_size]
        out_path = args.out_dir / f"{args.prefix}-{i+1:02d}.conllu"
        with open(out_path, "w", encoding="utf-8") as f:
            for block, _ in batch:
                f.write("\n".join(block) + "\n\n")
        n_toks = sum(n for _, n in batch)
        print(f"  wrote {len(batch)} sentences ({n_toks} tokens) to {out_path.name}")


if __name__ == "__main__":
    main()
