"""
Rule 7 (Purpose Clauses Break) — UD-query implementation.

UD signature (per canon §3):
    advcl with mark='that' and aux ∈ {may, might, shall, should, will, would, ...}

Action: BREAK before 'that'.

Violation: the matrix and the 'that' mark sit on the SAME v2-mine line
(no break) — the purpose clause hasn't been split off.

This rule existed previously only as an exception filter inside the regex
Rule 17 validator. As a first-class detector it closes a gap in mechanical
coverage: cases where a purpose clause never got its own line.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from validators.parsing.conllu_query import load_conllu
from validators.parsing.line_mapping import build_line_map_full, book_paths


MODAL_AUX_LEMMAS = {
    "will", "shall", "may", "can", "must",
    "might", "should", "would", "could",
}

# Filter: matrix-class adjectives that route to Rule 26 (ADJ + that ccomp),
# not Rule 7 advcl-purpose. When the advcl head's parent is one of these,
# the LLM annotation likely misclassified what should be ccomp.
RULE_26_HEAD_LEMMAS = {"expedient", "needful", "necessary", "wisdom", "meet"}

# Filter: result-clause / consecutive-result degree markers ("so X that Y",
# "such X that Y"). When one of these adverbs scopes the matrix verb's
# modifier, the that-clause is consequence not purpose.
RESULT_DEGREE_MARKERS = {"so", "such"}


BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]


def _preceding_tokens(sent, target_id: int, n: int) -> list:
    """Return the n tokens immediately preceding target_id in id order."""
    return [t for t in sent.tokens if target_id - n <= t.id < target_id]


def is_insomuch_that(sent, mark) -> bool:
    """Filter: 'insomuch that' is Rule 27 territory, not Rule 7."""
    for t in _preceding_tokens(sent, mark.id, 4):
        if t.lemma.lower() == "insomuch" or t.form.lower() == "insomuch":
            return True
    return False


def is_even_so_that(sent, mark) -> bool:
    """Filter: 'even so that' is an idiomatic result connector."""
    preceding = _preceding_tokens(sent, mark.id, 3)
    forms = [t.form.lower() for t in preceding]
    return "even" in forms and "so" in forms


def is_result_so_X_that(sent, head, mark) -> bool:
    """Filter: 'so X that Y' / 'such X that Y' — consecutive result, not purpose.

    Detect when the matrix head has an `advmod` or `amod` dependent (or one
    of its dependents has) with form/lemma in {so, such}.
    """
    # Walk dependents of head looking for so/such advmod
    for child in sent.dependents_of(head):
        if child.deprel in ("advmod", "amod") and child.form.lower() in RESULT_DEGREE_MARKERS:
            return True
        # Also one level deeper — "so numerous that" has 'so' as advmod of 'numerous'
        for grandchild in sent.dependents_of(child):
            if grandchild.deprel == "advmod" and grandchild.form.lower() in RESULT_DEGREE_MARKERS:
                return True
    return False


def is_rule_26_class(sent, head, advcl) -> bool:
    """Filter: matrix is expedient/needful/necessary etc. — Rule 26 ccomp territory.

    Rule 26 governs ADJ + that complement; the advcl tagging is likely wrong.
    """
    if head.lemma.lower() in RULE_26_HEAD_LEMMAS:
        return True
    # The advcl may be attached to a copular construction where 'expedient'
    # is the predicate ADJ. Walk up: head_of(head) might be 'be' with
    # 'expedient' as xcomp/cop's subject.
    parent = sent.head_of(head)
    if parent is not None and parent.lemma.lower() in RULE_26_HEAD_LEMMAS:
        return True
    return False


def is_moroni_gifts_list(book_id: str, line_num: int, v2_path: Path) -> bool:
    """Filter: Moroni 10:8-17 spiritual-gifts list — list-uniformity precedence
    per canon §3. The list dominant treatment governs, not Rule 7 default.
    """
    if book_id != "moroni":
        return False
    # Find the verse-number markers for 10:8 through 10:17 in v2-mine
    in_range = False
    try:
        with open(v2_path, encoding="utf-8") as f:
            for ln, raw in enumerate(f, start=1):
                stripped = raw.strip()
                if stripped == "10:8":
                    in_range = True
                if stripped == "10:18":
                    in_range = False
                if ln == line_num:
                    return in_range
    except OSError:
        pass
    return False


def scan_book(book_id: str) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map_full = build_line_map_full(v2_path, conllu_path)
    line_map = {k: v[0] for k, v in line_map_full.items()}

    violations = []
    review = []
    for sent in sentences:
        for advcl in sent.find(deprel="advcl"):
            mark = sent.mark_of(advcl)
            if mark is None or mark.lemma != "that":
                continue
            modals = [a for a in sent.aux_of(advcl) if a.lemma in MODAL_AUX_LEMMAS]
            if not modals:
                continue
            head = sent.head_of(advcl)
            if head is None:
                continue
            head_line = line_map.get((sent.sent_id, head.id))
            mark_line = line_map.get((sent.sent_id, mark.id))
            if head_line is None or mark_line is None:
                continue
            if head_line != mark_line:
                continue  # split already exists; no violation

            # Filters per audit findings (2026-05-10):
            skip_reason = None
            if is_insomuch_that(sent, mark):
                skip_reason = "insomuch-that-Rule-27"
            elif is_even_so_that(sent, mark):
                skip_reason = "even-so-that-result-connector"
            elif is_result_so_X_that(sent, head, advcl):
                skip_reason = "so-X-that-result-clause"
            elif is_rule_26_class(sent, head, advcl):
                skip_reason = "Rule-26-expedient-class-ccomp"
            elif is_moroni_gifts_list(book_id, head_line, v2_path):
                skip_reason = "Moroni-10-gifts-list-uniformity"

            # Char-offset of the 'that' mark token within its v2-mine line.
            # Applier splits before this column — no regex needed.
            mark_line_col = line_map_full.get((sent.sent_id, mark.id))
            split_col = mark_line_col[1] if mark_line_col is not None else None

            entry = {
                "book": book_id,
                "sent_id": sent.sent_id,
                "head_form": head.form,
                "head_lemma": head.lemma,
                "advcl_form": advcl.form,
                "modal": modals[0].form,
                "line": head_line,
                "split_col": split_col,
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
            print(f"{bid}: {len(vs)} STRONG, {len(rev)} REVIEW (filtered)")

    print("=" * 72)
    print("Rule 7 UD-query — BofM corpus (purpose-clause missing-break)")
    print("=" * 72)
    print(f"Books scanned: {len(book_ids)}")
    print(f"STRONG-SPLIT-CANDIDATE: {len(all_violations)}")
    print(f"REVIEW (filtered):      {len(all_review)}")
    print()

    for v in all_violations[:20]:
        print(f"  [{v['book']}] sent={v['sent_id']} "
              f"matrix={v['head_form']!r} (lemma={v['head_lemma']}) "
              f"+ that {v['modal']} {v['advcl_form']}  on line {v['line']}")
    if len(all_violations) > 20:
        print(f"  ... +{len(all_violations) - 20} more")

    if all_review and args.verbose:
        print()
        print("--- REVIEW (filtered out per audit) ---")
        by_reason: dict[str, list] = {}
        for v in all_review:
            by_reason.setdefault(v["skip_reason"], []).append(v)
        for reason, items in sorted(by_reason.items()):
            print(f"  {reason}: {len(items)}")

    print(f"RESULT: violations={len(all_violations)} strong={len(all_violations)} review={len(all_review)}")
    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
