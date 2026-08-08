"""
Extract sentences from a stanza CoNLL-U file into batches for parallel
LLM-direct parsing.

Output: one .txt file per batch, each line "sent_id=N | sentence text".
The agent dispatcher reads these batches and dispatches one agent per batch.
"""
import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent.parent
SENT_ID_RE = re.compile(r"# sent_id = (\S+)")
TEXT_RE = re.compile(r"# text = (.*)")


def parse_sentences(conllu_path: Path):
    """Yield (sent_id, text) for each sentence in a CoNLL-U file."""
    sent_id = None
    text = None
    with open(conllu_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("# sent_id"):
                m = SENT_ID_RE.match(line)
                if m:
                    sent_id = m.group(1)
            elif line.startswith("# text"):
                m = TEXT_RE.match(line)
                if m:
                    text = m.group(1)
            elif not line and sent_id is not None and text is not None:
                yield sent_id, text
                sent_id = None
                text = None
    if sent_id is not None and text is not None:
        yield sent_id, text


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stanza-conllu", type=Path, required=True,
                    help="Stanza CoNLL-U output to extract sentences from")
    ap.add_argument("--out-dir", type=Path, required=True,
                    help="Directory to write batch files")
    ap.add_argument("--batch-size", type=int, default=15,
                    help="Sentences per batch (default 15)")
    ap.add_argument("--prefix", default="batch",
                    help="Filename prefix (default 'batch')")
    args = ap.parse_args()

    sentences = list(parse_sentences(args.stanza_conllu))
    print(f"Loaded {len(sentences)} sentences from {args.stanza_conllu}")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    n_batches = (len(sentences) + args.batch_size - 1) // args.batch_size
    for i in range(n_batches):
        batch = sentences[i * args.batch_size : (i + 1) * args.batch_size]
        out_path = args.out_dir / f"{args.prefix}-{i+1:02d}.txt"
        with open(out_path, "w", encoding="utf-8") as f:
            for sid, txt in batch:
                f.write(f"sent_id={sid} | {txt}\n")
        print(f"  wrote {len(batch)} sentences to {out_path.name}")


if __name__ == "__main__":
    main()
