"""
Rule 19 (Cataphoric vs Anaphoric Relative) — UD-query implementation.

UD signature (per canon §3 / §5 Rule 19):
    acl:relcl(head, clause) — relative clause attached to a NOUN head.

Rule: cataphoric relative clauses SPLIT; anaphoric relatives MERGE.
  - Cataphoric: information-advancing — head is a forward-pointing generic
    reference ("those who shall keep my commandments", "all which are
    written"). BREAK before the relative.
  - Anaphoric: resolving — head is a specific named referent already
    established ("the brass plates which Lehi obtained"). MERGE.

Heuristic (v2 — UPOS-gated):
  - PROPN head → anaphoric (95% TP, audit-confirmed). STRONG-MERGE.
  - PRON or DET head → cataphoric (80% TP, audit-confirmed). STRONG-SPLIT.
    Common BofM examples: those, whoso, whatsoever, all, any, every, this, that.
  - NOUN head → ambiguous. Cannot determine cataphoric vs anaphoric without
    discourse tracking. Route to REVIEW-REQUIRED.
    Rationale: audit showed most "things/words/men" cases are anaphoric, making
    a GENERIC_HEADS lemma-list over-fire badly (was: ~1458 false STRONG-SPLITs).
  - All other UPOS → REVIEW-REQUIRED with labelled reason.

Violation classes:
  STRONG-MERGE    — PROPN head, matrix and relative on DIFFERENT lines → merge.
  STRONG-SPLIT    — PRON/DET head, matrix and relative on SAME line → split.
  REVIEW-REQUIRED — NOUN head (discourse-ambiguous) or unclassified UPOS.

REVIEW-REQUIRED subtypes (added 2026-05-16 per directive
2026-05-16-2100-r19-output-restructure.md):
  review_subtype="same-line"  — head and relative already on the SAME v2 line.
                                Editorial question: "verify this existing
                                merge is correct" (resolver is auditing).
  review_subtype="cross-line" — head and relative on DIFFERENT v2 lines.
                                Editorial question: "should we close this
                                split?" (resolver is deciding).
The distinction matters for downstream resolvers and any future auto-apply
gating — the two subtypes have different risk profiles. The resolver
prototype (commit eb821f6) surfaced ~60% same-line / ~40% cross-line in
its first 25-case sample; this field surfaces the distinction systemically.

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


# UPOS sets for direct dispatch (v2 heuristic).
# The old GENERIC_HEADS lemma list caused ~1400+ false STRONG-SPLITs on NOUN
# heads ("things", "words", "men", etc.) — audit confirmed most are anaphoric.
# NOUN heads are now unconditionally routed to REVIEW-REQUIRED.

# PRON or DET head → cataphoric → STRONG-SPLIT (80% TP, audit-confirmed).
# Typical BofM heads: those, whoso, whatsoever, all, any, every, this, that, these.
CATAPHORIC_UPOS = {"PRON", "DET"}

# PROPN head → anaphoric → STRONG-MERGE (95% TP, audit-confirmed).
ANAPHORIC_UPOS = {"PROPN"}

BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]


def classify_head(head_token) -> tuple[str, str | None]:
    """Return (direction, reason) where direction ∈ {'cataphoric','anaphoric','ambiguous'}.

    v2 heuristic: UPOS-gated only — no lemma list.
      PROPN  → anaphoric  (95% TP)
      PRON   → cataphoric (80% TP)
      DET    → cataphoric (80% TP)
      NOUN   → ambiguous  (cannot classify without discourse tracking)
      other  → ambiguous  (unclassified)
    """
    upos = head_token.upos

    if upos in ANAPHORIC_UPOS:          # PROPN
        return "anaphoric", None
    if upos in CATAPHORIC_UPOS:         # PRON, DET
        return "cataphoric", None
    if upos == "NOUN":
        return "ambiguous", "noun-head-ambiguous-needs-discourse-context"
    return "ambiguous", f"unclassified-head-upos-{upos}"


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
            # PUNCT-exclusion fix (2026-05-13, class-fix sweep): UD parsers
            # routinely attach the non-restrictive-comma at head-line-end to
            # the relative verb as `deprel=punct`. That comma's id is the
            # smallest in the subtree (comma precedes "which"), so without
            # exclusion `first_rel_tok` = comma — and its line is head_line,
            # not the rel-clause line. That collapses `on_same_line` to True
            # and short-circuits the STRONG-SPLIT/STRONG-MERGE routing.
            # Per feedback_punctuation_not_evidence: routing must rest on
            # grammar (the wh-word's position), not punctuation placement.
            subtree_tokens = sent.subtree(rel_root)
            content_tokens = [t for t in subtree_tokens if t.upos != "PUNCT"]
            if not content_tokens:
                continue
            first_rel_tok = content_tokens[0]   # leftmost content (non-PUNCT) token

            head_line = line_map.get((sent.sent_id, head.id))
            rel_line = line_map.get((sent.sent_id, first_rel_tok.id))
            if head_line is None or rel_line is None:
                continue

            on_same_line = (head_line == rel_line)
            direction, reason = classify_head(head)

            # Determine bucket (v2: UPOS-gated dispatch)
            if direction == "cataphoric":
                # PRON/DET head → cataphoric → split required
                if on_same_line:
                    bucket = "STRONG-SPLIT"
                else:
                    bucket = None   # already split, conforms → skip
            elif direction == "anaphoric":
                # PROPN head → anaphoric → merge required
                if not on_same_line:
                    bucket = "STRONG-MERGE"
                else:
                    bucket = None   # already merged, conforms → skip
            else:
                # NOUN head or unclassified UPOS → needs discourse context
                bucket = "REVIEW-REQUIRED"

            if bucket is None:
                continue

            # SAME-LINE / CROSS-LINE subtype for REVIEW cases (per directive
            # 2026-05-16-2100-r19-output-restructure.md, codified per the
            # resolver-prototype finding that ~60% of REVIEW cases are
            # already-merged same-line and ~40% are cross-line splits — two
            # structurally-different editorial questions that auto-apply
            # gating would need to handle with different risk profiles).
            review_subtype = None
            if bucket == "REVIEW-REQUIRED":
                review_subtype = "same-line" if on_same_line else "cross-line"

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
                "reason": reason,
                "bucket": bucket,
                "review_subtype": review_subtype,
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
    review_same   = [r for r in review if r.get("review_subtype") == "same-line"]
    review_cross  = [r for r in review if r.get("review_subtype") == "cross-line"]

    print("=" * 72)
    print("Rule 19 UD-query — Cataphoric vs Anaphoric Relative — BofM corpus")
    print("=" * 72)
    print(f"Books scanned:       {len(book_ids)}")
    print(f"Total candidates:    {len(all_results)}")
    print(f"  STRONG-SPLIT:      {len(strong_split)}")
    print(f"  STRONG-MERGE:      {len(strong_merge)}")
    print(f"  REVIEW-REQUIRED:   {len(review)}")
    print(f"    same-line:       {len(review_same)}   (verify existing merge)")
    print(f"    cross-line:      {len(review_cross)}   (close existing split?)")
    print()

    def show_samples(label: str, items: list[dict], n: int = 5):
        if not items:
            return
        print(f"--- {label} (up to {n} samples) ---")
        for r in items[:n]:
            print(f"  [{r['book']}] sent={r['sent_id']}")
            reason_parts = []
            if r.get("review_subtype"):
                reason_parts.append(f"subtype={r['review_subtype']}")
            if r.get("reason"):
                reason_parts.append(f"reason={r['reason']}")
            reason_str = "  " + "  ".join(reason_parts) if reason_parts else ""
            print(f"    head: {r['head_form']!r} (lemma={r['head_lemma']}, upos={r['head_upos']}) "
                  f"line {r['head_line']}{reason_str}")
            print(f"    rel:  {r['rel_root_form']!r} (lemma={r['rel_root_lemma']}) "
                  f"line {r['rel_line']}")
            print(f"    text: {r['sent_text']}")
            print()

    show_samples("STRONG-SPLIT", strong_split)
    show_samples("STRONG-MERGE", strong_merge)
    show_samples("REVIEW-REQUIRED", review)

    _violations_19 = len(strong_split) + len(strong_merge)
    print(f"RESULT: violations={_violations_19} strong={_violations_19} review={len(review)}")
    sys.exit(1 if (strong_split or strong_merge) else 0)


if __name__ == "__main__":
    main()
