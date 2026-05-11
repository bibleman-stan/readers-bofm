"""Line-mapping helpers — BoFM-specific glue + re-exports from atu_method.

The universal `build_line_map`, `build_line_map_full`, and `_v2_content_lines`
implementations live in `atu_method.parsing.line_mapping`. This module
re-exports them and adds the BoFM-specific `book_paths()` resolver that
maps a book id (e.g. 'enos', '1nephi') to (v2-mine-path, conllu-path)
under the readers-bofm directory layout.
"""
from pathlib import Path

from atu_method.parsing.line_mapping import (  # noqa: F401  (re-export)
    VERSE_NUM_RE,
    _v2_content_lines,
    build_line_map,
    build_line_map_full,
)


def book_paths(book_id: str) -> tuple[Path, Path]:
    """Resolve (v2_mine_path, conllu_path) for a book id like 'enos' or '1nephi'.

    Looks up v2-mine via the canonical readers-bofm `NN-bookname-2020-sb-v2.txt`
    convention and conllu via `data/parses/llm-direct/<book>.conllu`.
    """
    repo = Path(__file__).resolve().parent.parent.parent
    v2_dir = repo / "data" / "text-files" / "v2-mine"
    conllu_dir = repo / "data" / "parses" / "llm-direct"

    # v2-mine uses underscores (1_nephi, words_of_mormon); conllu uses bare
    # (1nephi, words-of-mormon).
    v2_id = book_id.replace("-", "_")
    if v2_id and v2_id[0].isdigit():
        # 1nephi -> 1_nephi
        v2_id = v2_id[0] + "_" + v2_id[1:]
        # but if it was already 1_nephi, the above produces 1__nephi -- guard
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
