"""
EP-1 ("According To" Manner vs. Source) — UD-query candidate surfacer.

Canon §5 EP-1 is Category B (editorial, judgment-required). Per canon:
  "Applier: none (Category B; auto-applier MUST NOT exist for EP-1;
  editorial-judgment required per-case)."

This validator SURFACES candidate cross-line "according to" PP cases
with heuristic manner/source classification per the canon's indicator
closed-lists. Each candidate is emitted as REVIEW-REQUIRED; no
STRONG-MERGE or STRONG-SPLIT bucket exists for EP-1.

UD signature (per canon §5 EP-1):
  Token: lemma="according" (the case-marker of an obl/advmod PP)
  Fixed: lemma="to" (deprel=fixed, head=according)
  NP-head: deprel=obl|advmod, head=matrix predication
  Cross-line: matrix-line != NP-head-line

Heuristic classification (NOT decision-gating per canon):
  SOURCE_AUTHORITY_INDICATORS = spirit, power, will, workings, faith,
                                commandment, covenant
  MANNER_INDICATORS           = word, time, memory, plainness, manner, custom

Per canon: heuristic SOURCE candidates → likely stay-split is canon-correct
(source/authority earns own line); heuristic MANNER candidates → likely
merge-with-matrix is canon-correct (manner-adverbial conforms to matrix).
Ambiguous cases (neither indicator) route to discourse-context review.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from validators.parsing.conllu_query import load_conllu
from validators.parsing.line_mapping import build_line_map, book_paths


SOURCE_AUTHORITY_INDICATORS = {
    "spirit", "power", "will", "workings", "faith",
    "commandment", "covenant",
}

MANNER_INDICATORS = {
    "word", "time", "memory", "plainness", "manner", "custom",
}


BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]


def classify(np_head_lemma: str) -> tuple[str, str]:
    """Return (classification, suggested_disposition) per canon heuristic."""
    if np_head_lemma in SOURCE_AUTHORITY_INDICATORS:
        return ("SOURCE-indicator", "split-likely-correct")
    if np_head_lemma in MANNER_INDICATORS:
        return ("MANNER-indicator", "merge-likely-correct")
    return ("ambiguous", "discourse-context-needed")


def scan_book(book_id: str) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)

    findings = []
    for sent in sentences:
        for tok in sent.tokens:
            if tok.lemma.lower() != "according":
                continue
            np_head = sent.by_id(tok.head)
            if np_head is None:
                continue
            # NP-head attaches to matrix predication via obl or advmod
            if np_head.deprel not in ("obl", "advmod"):
                continue
            matrix = sent.by_id(np_head.head) if np_head.head else None
            if matrix is None:
                continue
            np_line = line_map.get((sent.sent_id, np_head.id))
            matrix_line = line_map.get((sent.sent_id, matrix.id))
            if np_line is None or matrix_line is None:
                continue
            if np_line == matrix_line:
                continue  # already same-line; not a candidate
            classification, disposition = classify(np_head.lemma.lower())
            findings.append({
                "book": book_id,
                "sent_id": sent.sent_id,
                "matrix_form": matrix.form,
                "matrix_lemma": matrix.lemma,
                "matrix_line": matrix_line,
                "np_head_form": np_head.form,
                "np_head_lemma": np_head.lemma,
                "np_line": np_line,
                "classification": classification,
                "suggested_disposition": disposition,
                "bucket": "REVIEW-REQUIRED",
                "v2_path": str(v2_path),
            })
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book")
    ap.add_argument("--classification", choices=["SOURCE-indicator", "MANNER-indicator", "ambiguous"],
                    help="Filter by heuristic classification")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    book_ids = [args.book] if args.book else BOOKS
    all_v: list[dict] = []
    for bid in book_ids:
        try:
            vs = scan_book(bid)
        except FileNotFoundError as e:
            print(f"[skip] {bid}: {e}", file=sys.stderr)
            continue
        all_v.extend(vs)

    if args.classification:
        all_v = [v for v in all_v if v["classification"] == args.classification]

    from collections import Counter
    by_cls = Counter(v["classification"] for v in all_v)

    print("=" * 72)
    print('EP-1 UD-query — "according to" PP cross-line candidates (BofM corpus)')
    print("=" * 72)
    print(f"Books scanned: {len(book_ids)}")
    print(f"REVIEW-REQUIRED candidates: {len(all_v)}")
    print()
    print("By heuristic classification (NOT decision-gating per canon §5 EP-1):")
    for cls in ("SOURCE-indicator", "MANNER-indicator", "ambiguous"):
        n = by_cls.get(cls, 0)
        print(f"  {cls:20s} {n:3d}")
    print()

    if all_v and args.verbose:
        for v in all_v[:30]:
            print(f"  [{v['book']}] sent={v['sent_id']} "
                  f"matrix={v['matrix_form']!r} (lemma={v['matrix_lemma']}) L{v['matrix_line']}"
                  f" / NP={v['np_head_form']!r} (lemma={v['np_head_lemma']}) L{v['np_line']}"
                  f"  [{v['classification']}: {v['suggested_disposition']}]")
        if len(all_v) > 30:
            print(f"  ... +{len(all_v) - 30} more")

    print(f"\nRESULT: violations={len(all_v)} review={len(all_v)}")
    sys.exit(1 if all_v else 0)


if __name__ == "__main__":
    main()
