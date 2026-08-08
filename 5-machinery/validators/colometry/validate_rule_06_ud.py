"""
Rule 6 (Causal Clauses Break) — UD-query implementation.

UD signature (per canon §3):
    advcl with mark = 'because'

A causal advcl introduced by 'because' should begin on its OWN line — the
break falls BEFORE 'because'. Violation: the 'because' mark token and the
matrix predicate (the head of the advcl) sit on the SAME v2-mine line
(no break exists before 'because').

Buckets:
    STRONG-SPLIT-CANDIDATE — matrix and 'because' on the same line.
    (No REVIEW tier — the UD signature is unambiguous per canon §5 Rule 6.
     The canon's only exception is "short-line contexts where the combined
     line passes the atomic-thought test," which requires human review; those
     cases are captured as REVIEW-REQUIRED when the combined line is short.)

Short-line exception: if the advcl subtree + matrix are together ≤10 content
words, route to REVIEW-REQUIRED (short combined line may pass atomic-thought
test per Rule 6 exception).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from validators.parsing.conllu_query import load_conllu, Sentence, Token
from validators.parsing.line_mapping import build_line_map_full, book_paths

# ---------------------------------------------------------------------------
# Rule 17 precedence guard (canon §3.5 Tier 1 > Tier 3).
# If the advcl is nested inside a ccomp whose head is a Rule-17 governing verb,
# complement-integrity wins and R6 must not produce a STRONG-SPLIT candidate.
# Governor list imported from the R17 validator (source of truth).
# ---------------------------------------------------------------------------
from validators.colometry.validate_rule_17_ud import GOVERNING_LEMMAS as _R17_GOVERNING_LEMMAS


def _inside_r17_ccomp(sent: Sentence, advcl_tok: Token) -> bool:
    """Return True if the advcl_tok's because-clause is structurally subordinate
    to a Rule-17 complement-integrity relationship, meaning Rule 17 takes
    Tier-1 precedence over R6's Tier-3 split.

    Two patterns are guarded:

    Pattern A — advcl nested inside a ccomp:
        Walk the ancestor chain of advcl_tok.  If any link is
        current.deprel == 'ccomp' with a R17-governor head, R17 wins.

    Pattern B — advcl is a sibling of a ccomp under a R17-governor head:
        The advcl's direct head is a R17-governing verb AND that same verb
        has a ccomp dependent marked with 'that'.  The because-clause is an
        intervening modifier between the governor and its complement; splitting
        it severs the governor+ccomp bond (the Alma 41:10 pattern).
    """
    # Pattern A: walk ancestors
    current = advcl_tok
    while True:
        parent = sent.head_of(current)
        if parent is None:
            break
        if current.deprel == "ccomp":
            if parent.lemma.lower() in _R17_GOVERNING_LEMMAS:
                return True
        current = parent

    # Pattern B: advcl head is R17 governor AND has a ccomp+that sibling
    head = sent.head_of(advcl_tok)
    if head is not None and head.lemma.lower() in _R17_GOVERNING_LEMMAS:
        for sibling in sent.dependents_of(head):
            if sibling.deprel == "ccomp" and sibling.id != advcl_tok.id:
                sibling_mark = sent.mark_of(sibling)
                if sibling_mark is not None and sibling_mark.lemma.lower() == "that":
                    return True

    return False

BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]

# Combined content-word count at or below which we flag REVIEW rather than STRONG.
SHORT_LINE_THRESHOLD = 10


def content_count(sent: Sentence, tok: Token) -> int:
    """Count non-PUNCT tokens in subtree of tok."""
    return sum(1 for t in sent.subtree(tok) if t.upos != "PUNCT")


_FINITE_XPOS = {"MD", "VBZ", "VBD", "VBP"}


def is_elided_this_matrix(sent: Sentence, matrix: Token, line_map: dict) -> bool:
    """M4-fragment exclusion (canon §5 R6 Exclusion 5 / R7 Exclusion 7, codified 2026-05-15).

    True if `matrix` is the elided-predicate `(and|or) (all) this` coordinate-PRON
    fragment that R6/R7 yield to per §1.5 M4 (fragmented-atomic-thought-unit).

    Signature (narrow lexical closed-list — `this`-PRON only):
      - matrix is PRON with lemma `this`, deprel=`conj`
      - matrix's head is VERB/AUX on a PRIOR line (elided-predicate coordinate)
      - matrix's line begins with CCONJ (and/or/nor/but) — fragment marker

    The elided-predicate signal is the `conj`-of-VERB-on-prior-line attachment.
    Finite-verb absence on the matrix line is NOT required — when the merge is
    already applied, the line will contain the subordinator-clause's finite verb,
    but the matrix portion (the `(and|or) (all) this` prefix) is still the
    elided-predicate fragment.
    """
    if matrix.upos != "PRON" or matrix.lemma != "this":
        return False
    if matrix.deprel != "conj":
        return False
    head = sent.head_of(matrix)
    if head is None or head.upos not in ("VERB", "AUX"):
        return False
    matrix_line = line_map.get((sent.sent_id, matrix.id))
    head_line = line_map.get((sent.sent_id, head.id))
    if matrix_line is None or head_line is None or head_line >= matrix_line:
        return False
    line_toks_np = [t for t in sent.tokens
                    if line_map.get((sent.sent_id, t.id)) == matrix_line
                    and t.upos != "PUNCT"]
    if not line_toks_np:
        return False
    first = min(line_toks_np, key=lambda t: t.id)
    if first.upos != "CCONJ":
        return False
    return True


def scan_book(book_id: str, *, verbose: bool = False) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map_full = build_line_map_full(v2_path, conllu_path)
    line_map = {k: v[0] for k, v in line_map_full.items()}

    findings = []
    for sent in sentences:
        # Find all advcl tokens
        for advcl_tok in sent.find(deprel="advcl"):
            # Check for a 'mark' dependent with lemma/form 'because'
            mark = sent.mark_of(advcl_tok)
            if mark is None:
                continue
            if mark.lemma.lower() != "because" and mark.form.lower() != "because":
                continue

            # Rule 6 targets verbal causal clauses.  "because of NP" constructions
            # parse as advcl with a NOUN head (e.g. "because of their faith" →
            # advcl head = faith/NOUN).  These are PP-equivalents, not finite
            # subordinate clauses, and do not warrant a break under Rule 6.
            # Filter: advcl head must be VERB or ADJ.
            if advcl_tok.upos not in {"VERB", "ADJ"}:
                continue

            # Audit-driven filter (2026-05-10): "because of NP" leaks through
            # when the parser tags a gerund/nominalization as VERB. If the
            # advcl head has a 'case' dependent with form/lemma 'of', this is
            # a "because of" PP-equivalent, not a finite causal clause.
            has_of_case = any(
                d.deprel == "case" and (d.form.lower() == "of" or d.lemma.lower() == "of")
                for d in sent.dependents_of(advcl_tok)
            )
            if has_of_case:
                continue

            # The matrix is the head of the advcl
            matrix = sent.head_of(advcl_tok)
            if matrix is None:
                continue

            # M4-fragment exclusion (canon §5 R6 Exclusion 5, codified 2026-05-15):
            # when matrix is the elided-predicate `(and|or) (all) this` coordinate-PRON
            # fragment, R6's split-mandate yields to §1.5 M4 (fragmented-atomic-thought-unit).
            if is_elided_this_matrix(sent, matrix, line_map):
                continue

            matrix_line = line_map.get((sent.sent_id, matrix.id))
            because_line = line_map.get((sent.sent_id, mark.id))

            if matrix_line is None or because_line is None:
                continue
            if matrix_line != because_line:
                continue  # already split — no violation

            # Audit-driven filter (2026-05-10): fronted causal clauses.
            # "(For/And now,) because X, they Y" — the natural break is
            # AFTER the fronted clause, not before "because". Detect:
            # mark token id < matrix token id (because precedes matrix).
            # The current detector flags these because they're on the same
            # line, but the right action would be to break after the advcl
            # subtree, not before the mark. Bucket as REVIEW.
            because_fronted = mark.id < matrix.id

            # Both on the same line — violation.
            # Measure combined length for short-line exception.
            advcl_size = content_count(sent, advcl_tok)
            matrix_size = content_count(sent, matrix)
            combined = advcl_size + matrix_size  # rough (may double-count matrix deps)

            # Rule 17 precedence guard (canon §3.5 Tier 1 > Tier 3):
            # if the because-advcl sits inside a ccomp under a R17 governor,
            # complement integrity wins — demote to REVIEW-REQUIRED.
            inside_r17 = _inside_r17_ccomp(sent, advcl_tok)

            if inside_r17:
                bucket = "REVIEW-REQUIRED"
                review_reason = "r17-ccomp-precedence"
            elif because_fronted:
                bucket = "REVIEW-REQUIRED"
                review_reason = "fronted-because-needs-break-after"
            elif combined <= SHORT_LINE_THRESHOLD:
                bucket = "REVIEW-REQUIRED"
                review_reason = "short-combined-line"
            else:
                bucket = "STRONG-SPLIT-CANDIDATE"
                review_reason = None

            # Char-offset of the 'because' mark token within its v2-mine line.
            # Applier splits before this column — no regex needed.
            mark_line_col = line_map_full.get((sent.sent_id, mark.id))
            split_col = mark_line_col[1] if mark_line_col is not None else None

            findings.append({
                "book": book_id,
                "sent_id": sent.sent_id,
                "matrix_id": matrix.id,
                "matrix_form": matrix.form,
                "matrix_lemma": matrix.lemma,
                "because_id": mark.id,
                "matrix_line": matrix_line,
                "because_line": because_line,
                "combined_size": combined,
                "bucket": bucket,
                "review_reason": review_reason,
                "split_col": split_col,
                "v2_path": str(v2_path),
                "sent_text": sent.text,
            })

    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book", help="single book id (default: all)")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    book_ids = [args.book] if args.book else BOOKS

    all_findings: list[dict] = []
    for bid in book_ids:
        try:
            fs = scan_book(bid, verbose=args.verbose)
        except FileNotFoundError as e:
            print(f"[skip] {bid}: {e}", file=sys.stderr)
            continue
        all_findings.extend(fs)
        if args.verbose:
            print(f"{bid}: {len(fs)} findings")

    strong = [f for f in all_findings if f["bucket"] == "STRONG-SPLIT-CANDIDATE"]
    review = [f for f in all_findings if f["bucket"] == "REVIEW-REQUIRED"]

    print("=" * 72)
    print("Rule 6 UD-query — Causal clauses break — BofM corpus")
    print("=" * 72)
    print(f"Books scanned:          {len(book_ids)}")
    print(f"Total findings:         {len(all_findings)}")
    print(f"  STRONG-SPLIT-CANDIDATE: {len(strong)}")
    print(f"  REVIEW-REQUIRED:        {len(review)}")
    print()

    if all_findings:
        print("--- STRONG-SPLIT-CANDIDATE (first 8) ---")
        for f in strong[:8]:
            print(f"  [{f['book']}] sent={f['sent_id']} "
                  f"matrix='{f['matrix_form']}' (lemma={f['matrix_lemma']}) "
                  f"line {f['matrix_line']} — 'because' on same line "
                  f"(combined~{f['combined_size']} words)")
            if args.verbose:
                print(f"    text: {f['sent_text'][:120]}")
        if len(strong) > 8:
            print(f"  ... +{len(strong) - 8} more")
        print()

        print("--- REVIEW-REQUIRED (first 8) ---")
        for f in review[:8]:
            print(f"  [{f['book']}] sent={f['sent_id']} "
                  f"matrix='{f['matrix_form']}' (lemma={f['matrix_lemma']}) "
                  f"line {f['matrix_line']} — combined~{f['combined_size']} words "
                  f"[{f['review_reason']}]")
            if args.verbose:
                print(f"    text: {f['sent_text'][:120]}")
        if len(review) > 8:
            print(f"  ... +{len(review) - 8} more")

    print(f"RESULT: violations={len(all_findings)} strong={len(strong)} review={len(review)}")
    sys.exit(1 if all_findings else 0)


if __name__ == "__main__":
    main()
