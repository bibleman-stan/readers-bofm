#!/usr/bin/env python3
"""Extract every acl:relcl from Isaiah-quoting BoFM chapters for parser-error scan.

Per directive 2026-05-16-2102-isaiah-quotation-parser-scan.md. Reads the UD
parses, isolates acl:relcl tokens in scoped Isaiah-quoting chapters, and emits
per-token records with verse reference, head form/lemma/upos, relative-clause-
root form/lemma, surrounding token sequence, and verse text.

Output: JSONL to stdout (or --out FILE). Each line one acl:relcl case.
Downstream consumers (Sonnet classifier agent) read this to classify each
as probable-parser-error / genuine-relative / ambiguous.

Scope (per directive Item 1):
  2 Nephi 12-24    — Isaiah 2-14 with intervening discourse
  3 Nephi 22-24    — Isaiah 54 + parts of Malachi 3-4
  Mosiah 14        — Isaiah 53
  1 Nephi 20-22    — Isaiah 48-49 with discourse
  2 Nephi 7-8      — Isaiah 50-51 with discourse
  2 Nephi 27       — Isaiah 29 (heavily expanded)

This is a READ-ONLY DIAGNOSTIC. No corpus modifications.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from validators.parsing.conllu_query import load_conllu
from validators.parsing.line_mapping import book_paths, build_line_map


# (book_id, chapter_range_inclusive)
ISAIAH_SCOPE = [
    ("1nephi", (20, 22)),
    ("2nephi", (7, 8)),
    ("2nephi", (12, 24)),
    ("2nephi", (27, 27)),
    ("mosiah", (14, 14)),
    ("3nephi", (22, 24)),
]


VERSE_REF_RE = re.compile(r"^\s*(\d+):(\d+)\s*$")


def build_line_to_verse(v2_path: Path) -> dict[int, tuple[int, int]]:
    """Map every content-line-number to its (chapter, verse). Lines that are
    themselves verse-ref markers map to the SAME verse they introduce."""
    out: dict[int, tuple[int, int]] = {}
    cur: tuple[int, int] | None = None
    with open(v2_path, encoding="utf-8") as f:
        for ln, line in enumerate(f, start=1):
            stripped = line.rstrip("\n")
            m = VERSE_REF_RE.match(stripped)
            if m:
                cur = (int(m.group(1)), int(m.group(2)))
                # Verse-ref line itself maps to the verse it introduces
                out[ln] = cur
                continue
            if cur is not None and stripped.strip():
                out[ln] = cur
    return out


def scan_book_for_aclrelcl(book: str, chapters: tuple[int, int]) -> list[dict]:
    """Return all acl:relcl tokens in `book` whose chapter is in `chapters`."""
    try:
        v2_path, conllu_path = book_paths(book)
    except Exception:
        return []
    if not conllu_path.exists():
        return []

    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)   # (sent_id, tok.id) -> v2_line
    line_to_verse = build_line_to_verse(v2_path)

    out: list[dict] = []
    lo, hi = chapters
    for sent in sentences:
        for tok in sent.tokens:
            if tok.deprel != "acl:relcl":
                continue
            head = sent.by_id(tok.head) if tok.head else None
            # Determine chapter via line-map → v2 line → verse-ref lookup
            line_num = line_map.get((sent.sent_id, tok.id))
            verse_ref = line_to_verse.get(line_num) if line_num is not None else None
            if verse_ref is None:
                continue
            ch, vv = verse_ref
            if not (lo <= ch <= hi):
                continue

            subtree_ids = {t.id for t in sent.subtree(tok)}
            head_ids = {head.id} if head else set()
            window_ids = sorted(subtree_ids | head_ids)
            min_id = max(1, min(window_ids) - 2)
            max_id = min(len(sent.tokens), max(window_ids) + 2)
            fragment = " ".join(
                t.form for t in sent.tokens
                if min_id <= t.id <= max_id and t.upos != "PUNCT"
            )

            out.append({
                "book": book,
                "chapter": ch,
                "verse": vv,
                "verse_ref": f"{book} {ch}:{vv}",
                "sent_id": sent.sent_id,
                "head_form": head.form if head else None,
                "head_lemma": head.lemma if head else None,
                "head_upos": head.upos if head else None,
                "head_id": head.id if head else None,
                "rel_root_form": tok.form,
                "rel_root_lemma": tok.lemma,
                "rel_root_upos": tok.upos,
                "rel_root_id": tok.id,
                "fragment": fragment,
                "sent_text": sent.text[:200],
                "subtree_size": len(subtree_ids),
            })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=str, help="JSONL output file (default stdout)")
    args = ap.parse_args()

    all_recs: list[dict] = []
    for book, chrange in ISAIAH_SCOPE:
        recs = scan_book_for_aclrelcl(book, chrange)
        all_recs.extend(recs)
        print(
            f"  {book} ch {chrange[0]}-{chrange[1]}: {len(recs)} acl:relcl tokens",
            file=sys.stderr,
        )

    print(f"Total: {len(all_recs)} acl:relcl tokens across scoped Isaiah chapters", file=sys.stderr)

    output = "\n".join(json.dumps(r) for r in all_recs) + "\n"
    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Wrote {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
