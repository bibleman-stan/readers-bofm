#!/usr/bin/env python3
"""Extract all bare `relcl` tokens (deprel="relcl", NOT "acl:relcl") corpus-wide.

Per directive 2026-05-16-2401-r19-bare-relcl-corpus-survey.md. The 2206 audit
surfaced 340 bare `relcl` tokens across 15 books — labeling inconsistency
that may represent legitimate relative clauses invisible to R19's
deprel="acl:relcl" query.

Per token captures: book + chapter + verse + token forms + UPOS + verse text
fragment + parse fragment. Output JSONL for Sonnet classification.

READ-ONLY diagnostic.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from validators.parsing.conllu_query import load_conllu
from validators.parsing.line_mapping import book_paths, build_line_map


VERSE_REF_RE = re.compile(r"^\s*(\d+):(\d+)\s*$")

BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]


def build_line_to_verse(v2_path: Path) -> dict[int, tuple[int, int]]:
    out: dict[int, tuple[int, int]] = {}
    cur: tuple[int, int] | None = None
    with open(v2_path, encoding="utf-8") as f:
        for ln, line in enumerate(f, start=1):
            s = line.rstrip("\n")
            m = VERSE_REF_RE.match(s)
            if m:
                cur = (int(m.group(1)), int(m.group(2)))
                out[ln] = cur
                continue
            if cur and s.strip():
                out[ln] = cur
    return out


def scan_book(book: str) -> list[dict]:
    try:
        v2_path, conllu_path = book_paths(book)
    except Exception:
        return []
    if not conllu_path.exists():
        return []

    sents = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)
    line_to_verse = build_line_to_verse(v2_path)

    out = []
    for sent in sents:
        for tok in sent.tokens:
            if tok.deprel != "relcl":
                continue
            head = sent.by_id(tok.head) if tok.head else None
            ln = line_map.get((sent.sent_id, tok.id))
            verse = line_to_verse.get(ln) if ln else None
            if verse is None:
                continue
            ch, vv = verse

            subtree_ids = {t.id for t in sent.subtree(tok)}
            head_ids = {head.id} if head else set()
            window = sorted(subtree_ids | head_ids)
            if not window:
                continue
            min_id = max(1, min(window) - 2)
            max_id = min(len(sent.tokens), max(window) + 2)
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
                "rel_root_form": tok.form,
                "rel_root_lemma": tok.lemma,
                "rel_root_upos": tok.upos,
                "fragment": fragment,
                "sent_text": sent.text[:200],
            })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    all_recs = []
    for b in BOOKS:
        recs = scan_book(b)
        all_recs.extend(recs)
        print(f"  {b}: {len(recs)} bare relcl tokens", file=sys.stderr)
    print(f"Total: {len(all_recs)}", file=sys.stderr)

    Path(args.out).write_text("\n".join(json.dumps(r) for r in all_recs) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
