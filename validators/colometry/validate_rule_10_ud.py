"""
Rule 10 (V + DO split forbidden) — UD-query implementation.

UD signature (per canon §3):
    line-final VERB whose obj on the following line (bare NP continuation).

Action: MERGE.

Detection: a token with deprel=obj where the obj's line > head VERB's line.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from validators.parsing.conllu_query import load_conllu
from validators.parsing.line_mapping import build_line_map, book_paths


BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]


def is_coordinate_list_scope(sent, head, obj) -> bool:
    """Filter: obj is shared across a coordinate verb series (N=3+ compound),
    or head verb is one of multiple verbs sharing this object via conj.

    Canon §5 Rule 10 SCOPE: coordinate-list under shared verb is a separate
    pattern (justification 1). Don't merge across the list structure.
    """
    # If head has ≥2 conj children that are themselves VERBs, this is N=3+
    # compound territory.
    verb_conjs = [c for c in sent.dependents_of(head, deprel="conj") if c.upos == "VERB"]
    if len(verb_conjs) >= 2:
        return True
    # If obj has a conj sibling (another obj/xcomp under same head verb),
    # this is a coordinate-object list.
    obj_conjs = [c for c in sent.dependents_of(obj, deprel="conj")]
    if obj_conjs:
        return True
    return False


def is_speech_frame(sent, head) -> bool:
    """Filter: 'saying:' / 'said:' speech-frame followed by direct discourse.

    Rule 28 territory — speech-act-after-frame licenses the split.
    """
    if head.lemma not in {"say", "speak"}:
        return False
    # Look for a colon punctuation after the head, before any obj
    for child in sent.dependents_of(head, deprel="punct"):
        if child.form == ":":
            return True
    # Also check siblings: punct may attach elsewhere
    for t in sent.tokens:
        if t.upos == "PUNCT" and t.form == ":" and head.id < t.id < head.id + 5:
            return True
    return False


def scan_book(book_id: str) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)

    violations = []
    review = []
    for sent in sentences:
        for obj in sent.find(deprel="obj"):
            head = sent.head_of(obj)
            if head is None or head.upos != "VERB":
                continue
            head_line = line_map.get((sent.sent_id, head.id))
            obj_line = line_map.get((sent.sent_id, obj.id))
            if head_line is None or obj_line is None:
                continue
            gap = obj_line - head_line
            if gap <= 0 or gap > 3:
                continue

            # Audit-driven filters (2026-05-10):
            skip_reason = None
            if gap > 1:
                # Audit recommended gap=1 only as STRONG; gap=2,3 -> REVIEW
                skip_reason = f"gap-{gap}-needs-review"
            elif is_coordinate_list_scope(sent, head, obj):
                skip_reason = "coordinate-list-scope-exclusion"
            elif is_speech_frame(sent, head):
                skip_reason = "speech-frame-Rule-28"

            entry = {
                "book": book_id,
                "sent_id": sent.sent_id,
                "head_form": head.form,
                "head_lemma": head.lemma,
                "obj_form": obj.form,
                "head_line": head_line,
                "obj_line": obj_line,
                "v2_path": str(v2_path),
            }
            if skip_reason:
                entry["skip_reason"] = skip_reason
                review.append(entry)
            else:
                violations.append(entry)
    return violations, review


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    book_ids = [args.book] if args.book else BOOKS
    all_violations: list[dict] = []
    all_review: list[dict] = []
    for bid in book_ids:
        try:
            vs, rev = scan_book(bid)
        except FileNotFoundError as e:
            print(f"[skip] {bid}: {e}", file=sys.stderr)
            continue
        all_violations.extend(vs)
        all_review.extend(rev)
        if args.verbose:
            print(f"{bid}: {len(vs)} STRONG, {len(rev)} REVIEW")

    print("=" * 72)
    print("Rule 10 UD-query — V+DO split (BofM corpus)")
    print("=" * 72)
    print(f"Books scanned: {len(book_ids)}")
    print(f"STRONG-MERGE-CANDIDATE: {len(all_violations)}")
    print(f"REVIEW (filtered):      {len(all_review)}")
    print()

    for v in all_violations[:20]:
        print(f"  [{v['book']}] sent={v['sent_id']} "
              f"VERB {v['head_form']!r} (line {v['head_line']}) -> "
              f"obj {v['obj_form']!r} (line {v['obj_line']})")
    if len(all_violations) > 20:
        print(f"  ... +{len(all_violations) - 20} more")

    if all_review and args.verbose:
        print()
        print("--- REVIEW (filtered) ---")
        by_reason: dict[str, int] = {}
        for v in all_review:
            by_reason[v["skip_reason"]] = by_reason.get(v["skip_reason"], 0) + 1
        for reason, n in sorted(by_reason.items()):
            print(f"  {reason}: {n}")

    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
