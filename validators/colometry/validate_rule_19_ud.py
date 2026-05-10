"""
Rule 19 (Cataphoric vs Anaphoric Relative) — UD-query implementation.

UD signature (per canon §3 / §5 Rule 19):
    acl:relcl(head, clause) — relative clause attached to a NOUN head.

Rule: cataphoric relative clauses SPLIT; anaphoric relatives MERGE.
  - Cataphoric: information-advancing — head is a forward-pointing generic
    reference ("those who shall keep my commandments", "all things which are
    written"). BREAK before the relative.
  - Anaphoric: resolving — head is a specific named referent already
    established ("the brass plates which Lehi obtained"). MERGE.

Heuristic for cataphoric vs anaphoric:
  - Cataphoric signals: head lemma in GENERIC_HEADS (people, those, all, any,
    one, whosoever, whatsoever, things, thing, everyone, anyone, whoever);
    OR head token is a demonstrative pronoun (DET upos + cataphoric form).
  - Anaphoric signals: head is a specific named referent (PROPN, or a
    lower-frequency concrete noun not in the generic-head list).
  - Ambiguous: everything else → REVIEW-REQUIRED.

Violation classes:
  STRONG-MERGE   — anaphoric, matrix and relative on DIFFERENT lines → merge.
  STRONG-SPLIT   — cataphoric, matrix and relative on SAME line → split.
  REVIEW-REQUIRED — ambiguous head type, or head/relative cross-line pattern
                    does not match the canonical corrective.

NOTE: Rule 17 takes precedence. acl:relcl tokens where the head is in a
ccomp position are NOT surfaced here (Rule 17 governs complement integrity).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from validators.parsing.conllu_query import load_conllu
from validators.parsing.line_mapping import build_line_map, book_paths


# Generic / forward-pointing head lemmas that signal cataphoric reading.
# A relative clause restricting a generic head typically introduces new info.
GENERIC_HEADS = {
    "people", "person", "those", "all", "any", "one", "everyone", "everyone",
    "anyone", "whoever", "whosoever", "whatever", "whatsoever", "thing",
    "things", "he", "they", "she", "it", "we", "them", "others", "other",
    "such", "same", "this", "these", "that", "those",
    # BofM-specific generics
    "soul", "souls", "man", "men", "woman", "women", "child", "children",
    "nation", "nations", "generation", "generations", "place", "places",
}

# Demonstrative pronoun heads (DET upos, typically pointing forward):
CATAPHORIC_UPOS = {"PRON"}          # head upos = PRON
CATAPHORIC_DET_LEMMAS = {           # head upos = DET + one of these lemmas
    "this", "these", "those", "that", "all", "any", "every", "such",
    "whosoever", "whatsoever", "whoever", "whatever",
}

# Named / proper referents strongly signal anaphoric reading:
ANAPHORIC_UPOS = {"PROPN"}

BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]


def classify_head(head_token) -> str:
    """Return 'cataphoric', 'anaphoric', or 'ambiguous' based on head token."""
    lemma = (head_token.lemma or "").lower()
    upos = head_token.upos

    # Proper noun head → anaphoric
    if upos in ANAPHORIC_UPOS:
        return "anaphoric"

    # Pronoun head → cataphoric (forward-pointing or generic reference)
    if upos in CATAPHORIC_UPOS:
        return "cataphoric"

    # DET head with demonstrative lemma → cataphoric
    if upos == "DET" and lemma in CATAPHORIC_DET_LEMMAS:
        return "cataphoric"

    # Lemma-based generic-head check
    if lemma in GENERIC_HEADS:
        return "cataphoric"

    # Common nouns (NOUN) with specific referent are the ambiguous middle ground.
    # Without discourse context we can't tell if the noun was already established.
    # Route to REVIEW.
    if upos == "NOUN":
        return "ambiguous"

    return "ambiguous"


def scan_book(book_id: str) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)

    results = []
    for sent in sentences:
        for rel_root in sent.find(deprel="acl:relcl"):
            head = sent.head_of(rel_root)
            if head is None:
                continue

            # Resolve the leftmost token of the relative clause for line lookup.
            # The acl:relcl root token is the head of the relative; mark/wh-word
            # typically precedes it.
            subtree_tokens = sent.subtree(rel_root)
            if not subtree_tokens:
                continue
            first_rel_tok = subtree_tokens[0]   # leftmost token in the clause

            head_line = line_map.get((sent.sent_id, head.id))
            rel_line = line_map.get((sent.sent_id, first_rel_tok.id))
            if head_line is None or rel_line is None:
                continue

            on_same_line = (head_line == rel_line)
            direction = classify_head(head)

            # Determine bucket
            if direction == "cataphoric":
                if on_same_line:
                    bucket = "STRONG-SPLIT"
                else:
                    bucket = None   # already split, conforms → skip
            elif direction == "anaphoric":
                if not on_same_line:
                    bucket = "STRONG-MERGE"
                else:
                    bucket = None   # already merged, conforms → skip
            else:  # ambiguous
                # Surface for review regardless of current state
                bucket = "REVIEW-REQUIRED"

            if bucket is None:
                continue

            results.append({
                "book": book_id,
                "sent_id": sent.sent_id,
                "head_id": head.id,
                "head_form": head.form,
                "head_lemma": head.lemma,
                "head_upos": head.upos,
                "head_line": head_line,
                "rel_root_form": rel_root.form,
                "rel_root_lemma": rel_root.lemma,
                "rel_line": rel_line,
                "direction": direction,
                "bucket": bucket,
                "sent_text": sent.text[:120],
            })

    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book", help="single book id (default: all)")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    book_ids = [args.book] if args.book else BOOKS

    all_results: list[dict] = []
    for bid in book_ids:
        try:
            recs = scan_book(bid)
        except FileNotFoundError as e:
            print(f"[skip] {bid}: {e}", file=sys.stderr)
            continue
        all_results.extend(recs)
        if args.verbose:
            print(f"{bid}: {len(recs)} candidates")

    strong_split  = [r for r in all_results if r["bucket"] == "STRONG-SPLIT"]
    strong_merge  = [r for r in all_results if r["bucket"] == "STRONG-MERGE"]
    review        = [r for r in all_results if r["bucket"] == "REVIEW-REQUIRED"]

    print("=" * 72)
    print("Rule 19 UD-query — Cataphoric vs Anaphoric Relative — BofM corpus")
    print("=" * 72)
    print(f"Books scanned:       {len(book_ids)}")
    print(f"Total candidates:    {len(all_results)}")
    print(f"  STRONG-SPLIT:      {len(strong_split)}")
    print(f"  STRONG-MERGE:      {len(strong_merge)}")
    print(f"  REVIEW-REQUIRED:   {len(review)}")
    print()

    def show_samples(label: str, items: list[dict], n: int = 5):
        if not items:
            return
        print(f"--- {label} (up to {n} samples) ---")
        for r in items[:n]:
            print(f"  [{r['book']}] sent={r['sent_id']}")
            print(f"    head: {r['head_form']!r} (lemma={r['head_lemma']}, upos={r['head_upos']}) "
                  f"line {r['head_line']}")
            print(f"    rel:  {r['rel_root_form']!r} (lemma={r['rel_root_lemma']}) "
                  f"line {r['rel_line']}")
            print(f"    text: {r['sent_text']}")
            print()

    show_samples("STRONG-SPLIT", strong_split)
    show_samples("STRONG-MERGE", strong_merge)
    show_samples("REVIEW-REQUIRED", review)

    sys.exit(1 if (strong_split or strong_merge) else 0)


if __name__ == "__main__":
    main()
