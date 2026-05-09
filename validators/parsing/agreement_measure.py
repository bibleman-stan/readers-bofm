"""
Measure per-token agreement across multiple parser CoNLL-U outputs.

Inputs: per-parser CoNLL-U files for the same source text (one per parser).
Output: agreement statistics + sample disagreements categorized by severity.

Usage:
    python validators/parsing/agreement_measure.py \\
        --stanza data/parses/ensemble/stanza/alma-30.conllu \\
        --spacy data/parses/ensemble/spacy/alma-30.conllu \\
        --trankit data/parses/ensemble/trankit/alma-30.conllu \\
        --udpipe data/parses/ensemble/udpipe/alma-30.conllu

Categorizes per-token agreement:
  FULL      — all 4 parsers agree on POS+lemma+head+deprel
  STRONG    — 3/4 parsers agree (one minority opinion)
  SPLIT     — 2/2 split
  NONE      — 4 unique answers (no consensus)

Reports:
  - Per-feature agreement rate (POS, lemma, head, deprel separately)
  - Token-level full-agreement rate
  - Disagreement samples by category (for adjudication queue)
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Token:
    idx: int           # 1-based token position within sentence
    sent_id: int       # 1-based sentence id
    text: str
    pos: str
    lemma: str
    head: int          # 0 = ROOT
    deprel: str

    def signature(self) -> tuple:
        """Comparable signature: POS+lemma+head+deprel."""
        return (self.pos, self.lemma.lower(), self.head, self.deprel)


def parse_conllu(path: Path) -> list[list[Token]]:
    """Parse CoNLL-U file → list of sentences, each a list of Token."""
    sentences = []
    current = []
    sent_id = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if current:
                    sentences.append(current)
                    current = []
                    sent_id += 1
                continue
            if line.startswith("#"):
                continue
            cols = line.split("\t")
            if len(cols) < 8:
                continue
            try:
                idx = int(cols[0])
            except ValueError:
                continue  # skip multi-word tokens (e.g., "1-2")
            try:
                head = int(cols[6]) if cols[6] != "_" else 0
            except ValueError:
                head = 0
            current.append(Token(
                idx=idx,
                sent_id=sent_id + 1,
                text=cols[1],
                pos=cols[3],
                lemma=cols[2],
                head=head,
                deprel=cols[7],
            ))
        if current:
            sentences.append(current)
    return sentences


def flatten(sentences: list[list[Token]]) -> list[Token]:
    """Flatten sentences to single token list."""
    return [tok for sent in sentences for tok in sent]


def align_by_surface(parser_tokens: dict[str, list[Token]]) -> list[dict[str, Token]]:
    """Align tokens across parsers by surface form.

    Best-effort alignment. When parsers disagree on tokenization, skip the
    misaligned region and continue. Returns list of aligned token-dicts:
    each dict maps parser_name → Token.
    """
    iterators = {name: iter(toks) for name, toks in parser_tokens.items()}
    current = {name: next(it, None) for name, it in iterators.items()}
    aligned = []

    while all(t is not None for t in current.values()):
        # Compare surface forms
        surfaces = {name: tok.text.lower() for name, tok in current.items()}
        if len(set(surfaces.values())) == 1:
            # Full agreement on surface — record and advance all
            aligned.append(dict(current))
            current = {name: next(it, None) for name, it in iterators.items()}
        else:
            # Disagreement on tokenization. Try to advance the shortest-text
            # parser to catch up.
            shortest = min(current.values(), key=lambda t: len(t.text))
            shortest_name = next(n for n, t in current.items() if t is shortest)
            current[shortest_name] = next(iterators[shortest_name], None)
            if current[shortest_name] is None:
                break

    return aligned


def categorize_agreement(aligned: list[dict[str, Token]]) -> dict:
    """Categorize each aligned position by signature agreement.

    For N parsers:
      FULL    — all N agree
      STRONG  — N-1 agree (one minority), only meaningful for N >= 3
      SPLIT   — exactly 2 distinct signatures (any split)
      NONE    — N distinct signatures (max diversity)
    """
    parser_names = list(aligned[0].keys()) if aligned else []
    categories = {"FULL": [], "STRONG": [], "SPLIT": [], "NONE": []}
    feature_agreement = {
        "pos": 0, "lemma": 0, "head": 0, "deprel": 0
    }
    n = len(parser_names)

    for pos_idx, tokens in enumerate(aligned):
        sigs = [t.signature() for t in tokens.values()]
        sig_counts = Counter(sigs)
        most_common, count = sig_counts.most_common(1)[0]

        if count == n:
            cat = "FULL"
        elif n >= 3 and count == n - 1:
            cat = "STRONG"
        elif len(sig_counts) == 2:
            cat = "SPLIT"
        else:
            cat = "NONE"
        categories[cat].append((pos_idx, tokens))

        # Per-feature agreement (independent of full signature match)
        pos_set = {t.pos for t in tokens.values()}
        lemma_set = {t.lemma.lower() for t in tokens.values()}
        head_set = {t.head for t in tokens.values()}
        deprel_set = {t.deprel for t in tokens.values()}
        if len(pos_set) == 1: feature_agreement["pos"] += 1
        if len(lemma_set) == 1: feature_agreement["lemma"] += 1
        if len(head_set) == 1: feature_agreement["head"] += 1
        if len(deprel_set) == 1: feature_agreement["deprel"] += 1

    return {
        "categories": categories,
        "feature_agreement": feature_agreement,
        "total": len(aligned),
        "parser_names": parser_names,
    }


def report(agreement: dict, sample_size: int = 5) -> None:
    total = agreement["total"]
    parsers = agreement["parser_names"]

    print()
    print("=" * 72)
    print("ENSEMBLE PARSER AGREEMENT REPORT")
    print("=" * 72)
    print(f"Parsers: {', '.join(parsers)}")
    print(f"Aligned tokens: {total}")
    print()

    print("Per-feature agreement (all parsers identical on this feature):")
    print("-" * 72)
    for feat, count in agreement["feature_agreement"].items():
        pct = 100 * count / total if total else 0
        print(f"  {feat:10s} {count:5d} / {total:5d}  ({pct:5.1f}%)")
    print()

    print("Token-level signature agreement (POS+lemma+head+deprel combined):")
    print("-" * 72)
    for cat in ["FULL", "STRONG", "SPLIT", "NONE"]:
        n = len(agreement["categories"][cat])
        pct = 100 * n / total if total else 0
        marker = {
            "FULL": "✓ all agree",
            "STRONG": "~ 3/4 agree, 1 minority",
            "SPLIT": "± 2/2 split",
            "NONE": "✗ no consensus",
        }[cat]
        print(f"  {cat:8s} {n:5d}  ({pct:5.1f}%)  {marker}")
    print()

    # Adjudication queue: STRONG + SPLIT + NONE
    queue_size = sum(len(agreement["categories"][c]) for c in ["STRONG", "SPLIT", "NONE"])
    print(f"Adjudication queue: {queue_size} tokens")
    print()

    # Show samples from each disagreement category
    for cat in ["STRONG", "SPLIT", "NONE"]:
        items = agreement["categories"][cat]
        if not items:
            continue
        print(f"Sample {cat} disagreements (first {min(sample_size, len(items))}):")
        print("-" * 72)
        for pos_idx, tokens in items[:sample_size]:
            sample = next(iter(tokens.values()))
            print(f"  pos={pos_idx} sent={sample.sent_id} text='{sample.text}'")
            for name, tok in tokens.items():
                print(f"    [{name:8s}] pos={tok.pos:6s} lemma={tok.lemma:12s} "
                      f"head={tok.head:3d} deprel={tok.deprel}")
            print()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stanza", type=Path)
    ap.add_argument("--spacy", type=Path)
    ap.add_argument("--trankit", type=Path)
    ap.add_argument("--udpipe", type=Path)
    ap.add_argument("--sample-size", type=int, default=5,
                    help="Number of disagreements to show per category (default 5)")
    args = ap.parse_args()

    parser_paths = {
        name: getattr(args, name)
        for name in ("stanza", "spacy", "trankit", "udpipe")
        if getattr(args, name) is not None
    }
    if len(parser_paths) < 2:
        print("ERROR: at least 2 parsers required for agreement measurement", file=sys.stderr)
        sys.exit(2)

    # Load each parser's output
    parser_tokens = {}
    for name, path in parser_paths.items():
        if not path.exists():
            print(f"ERROR: {path} not found", file=sys.stderr)
            sys.exit(2)
        sentences = parse_conllu(path)
        toks = flatten(sentences)
        parser_tokens[name] = toks
        print(f"Loaded {name}: {len(sentences)} sentences, {len(toks)} tokens")

    # Align
    print("\nAligning tokens by surface form...")
    aligned = align_by_surface(parser_tokens)
    print(f"Aligned: {len(aligned)} positions "
          f"(loss: {min(len(t) for t in parser_tokens.values()) - len(aligned)} "
          f"due to tokenization mismatch)")

    # Categorize and report
    agreement = categorize_agreement(aligned)
    report(agreement, sample_size=args.sample_size)


if __name__ == "__main__":
    main()
