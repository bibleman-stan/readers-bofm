"""
Map (sent_id, token_id) in a CoNLL-U file to v2-mine line numbers.

CoNLL-U sentences are stanza-output-bounded (typically a verse, sometimes
spanning verses on long anacolutha). v2-mine has one ATU per line plus
verse-number marker lines. The mapping lets a UD-query violation report
point back to the v2-mine line a token sits on.

Algorithm: walk forward through v2-mine content tokens, advancing through
the CoNLL-U FORM stream in sync. When the FORM stream crosses a v2-mine
newline boundary, increment the line cursor.

Caveats:
- Assumes v2-mine state matches the parse state (no edits since the parse).
- A FORM that doesn't appear in the upcoming v2-mine slice gets skipped
  (with a warning). This shouldn't happen for a clean parse.

Usage:
    from validators.parsing.line_mapping import build_line_map

    m = build_line_map(
        v2_mine_path=Path("data/text-files/v2-mine/04-enos-2020-sb-v2.txt"),
        conllu_path=Path("data/parses/llm-direct/enos.conllu"),
    )
    line_num = m[("0", 7)]  # the 'that' complementizer in sent 0
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from validators.parsing.conllu_query import load_conllu


VERSE_NUM_RE = re.compile(r"^\s*\d+:\d+\s*$")


def _v2_content_lines(v2_path: Path) -> list[tuple[int, str]]:
    """Return [(line_num, content), ...] for v2-mine content lines.
    Skips blank lines and verse-number marker lines."""
    out: list[tuple[int, str]] = []
    with open(v2_path, encoding="utf-8") as f:
        for ln, raw in enumerate(f, start=1):
            stripped = raw.rstrip()
            if not stripped.strip():
                continue
            if VERSE_NUM_RE.match(stripped):
                continue
            out.append((ln, stripped))
    return out


def build_line_map_full(
    v2_mine_path: Path,
    conllu_path: Path,
    *,
    verbose: bool = False,
) -> dict[tuple[str, int], tuple[int, int]]:
    """Return {(sent_id, token_id): (v2_line_num, col_offset)} for every
    parsed token.

    `col_offset` is the character offset of the token's first character
    *within* its v2-mine line. Appliers can use this to know exactly where
    to insert a line break (split before col_offset → ATU break exactly
    before the token).

    Tokens that cannot be aligned are omitted; warning to stderr if verbose.
    """
    content = _v2_content_lines(v2_mine_path)

    # Build a flat character stream with line-start offsets recorded.
    full_text_parts: list[str] = []
    line_starts: list[tuple[int, int]] = []  # (v2_line_num, char_offset_in_full_text)
    cursor = 0
    for line_num, text in content:
        line_starts.append((line_num, cursor))
        full_text_parts.append(text)
        full_text_parts.append(" ")
        cursor += len(text) + 1
    full_text = "".join(full_text_parts)

    import bisect
    line_offsets = [c for _, c in line_starts]

    def line_and_col(idx: int) -> tuple[int, int]:
        """Return (v2_line_num, col_offset_within_line) for char position idx."""
        i = bisect.bisect_right(line_offsets, idx) - 1
        if i < 0:
            i = 0
        line_num, line_start_offset = line_starts[i]
        col_offset = idx - line_start_offset
        return (line_num, col_offset)

    sentences = load_conllu(conllu_path)

    pos = 0
    prev_anchor = 0
    out: dict[tuple[str, int], tuple[int, int]] = {}
    misses = 0
    anchor_misses = 0

    def normalize(s: str) -> str:
        return " ".join(s.split())

    for sent in sentences:
        sent_text_norm = normalize(sent.text)
        if sent_text_norm:
            anchor_key = sent_text_norm[:60] if len(sent_text_norm) >= 60 else sent_text_norm
            anchor_idx = full_text.find(anchor_key, prev_anchor)
            if anchor_idx < 0:
                anchor_idx = full_text.find(anchor_key)
            if anchor_idx >= 0:
                pos = anchor_idx
                prev_anchor = anchor_idx + 1
            else:
                anchor_misses += 1
                if verbose:
                    print(f"[anchor-miss] sent={sent.sent_id}: {anchor_key!r} not found",
                          file=sys.stderr)

        for tok in sent.tokens:
            form = tok.form
            idx = full_text.find(form, pos)
            if idx == -1:
                misses += 1
                if verbose:
                    print(f"[miss] sent={sent.sent_id} tok={tok.id} form={form!r}",
                          file=sys.stderr)
                continue
            out[(sent.sent_id, tok.id)] = line_and_col(idx)
            pos = idx + len(form)

    if (misses or anchor_misses) and verbose:
        total = sum(len(s.tokens) for s in sentences)
        print(f"[line_mapping] {misses} token misses, {anchor_misses} sentence-anchor misses "
              f"(of {total} tokens, {len(sentences)} sentences)", file=sys.stderr)

    return out


def build_line_map(
    v2_mine_path: Path,
    conllu_path: Path,
    *,
    verbose: bool = False,
) -> dict[tuple[str, int], int]:
    """Backward-compat wrapper: return {(sent_id, token_id): v2_line_num}.

    For new appliers that need char-offset precision, use
    build_line_map_full() instead.
    """
    full = build_line_map_full(v2_mine_path, conllu_path, verbose=verbose)
    return {key: line_col[0] for key, line_col in full.items()}


def book_paths(book_id: str) -> tuple[Path, Path]:
    """Resolve (v2_mine_path, conllu_path) for a book id like 'enos' or '1nephi'.
    Looks up v2-mine via the canonical NN-bookname-2020-sb-v2.txt convention."""
    repo = Path(__file__).resolve().parent.parent.parent
    v2_dir = repo / "data" / "text-files" / "v2-mine"
    conllu_dir = repo / "data" / "parses" / "llm-direct"

    # v2-mine uses underscores (1_nephi, words_of_mormon); conllu uses bare
    # (1nephi, words-of-mormon).
    v2_id = book_id.replace("-", "_")
    if v2_id and v2_id[0].isdigit():
        # 1nephi -> 1_nephi
        v2_id = v2_id[0] + "_" + v2_id[1:]
        # but if it was already 1_nephi, the above produces 1__nephi — guard
        v2_id = v2_id.replace("__", "_")
    matches = sorted(v2_dir.glob(f"*{v2_id}-2020-sb-v2.txt"))
    if not matches:
        raise FileNotFoundError(
            f"No v2-mine file for book id {book_id!r} (tried glob *{v2_id}-2020-sb-v2.txt)"
        )
    v2_path = matches[0]

    conllu_path = conllu_dir / f"{book_id}.conllu"
    if not conllu_path.exists():
        raise FileNotFoundError(f"No conllu for book id {book_id!r}: {conllu_path}")

    return v2_path, conllu_path


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("book", help="book id (e.g. 'enos', '1nephi')")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--probe", nargs=2, metavar=("SENT_ID", "TOKEN_ID"),
                    help="report the v2-mine line of one (sent_id, token_id)")
    args = ap.parse_args()

    v2_path, conllu_path = book_paths(args.book)
    print(f"v2:     {v2_path}")
    print(f"conllu: {conllu_path}")

    m = build_line_map(v2_path, conllu_path, verbose=args.verbose)
    print(f"\nMapped {len(m)} tokens to v2-mine lines.")

    if args.probe:
        sid, tid = args.probe[0], int(args.probe[1])
        ln = m.get((sid, tid))
        if ln is None:
            print(f"\nNo line mapping for ({sid!r}, {tid})")
        else:
            print(f"\n({sid!r}, {tid}) -> v2-mine line {ln}")
            with open(v2_path, encoding="utf-8") as f:
                lines = f.readlines()
            print(f"  {ln}: {lines[ln-1].rstrip()}")
