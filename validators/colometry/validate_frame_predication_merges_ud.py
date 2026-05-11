"""
Validate frame+predication merge candidates — UD-query implementation.

UD signature:
  A temporal/locative frame clause (advcl or adverbial PP obl) on line N
  immediately followed on line N+1 by the matrix clause root (the main
  predication), where together they form one proposition.

Two UD sub-patterns covered:

  Pattern A — AICTP/temporal advcl frame:
    The matrix ROOT (or matrix VERB) has an `advcl` dependent whose subtree
    occupies line N; the matrix ROOT sits on line N+1.  The advcl mark lemma
    is a temporal/conditional subordinator OR the advcl lemma is "pass"
    (= "it came to pass" pattern).  Subject-continuity: the matrix subject
    is recoverable (nsubj on matrix or pro-drop).

  Pattern B — Substantive PP frame (locative/temporal obl):
    The matrix ROOT has an `obl` dependent that is itself headed by a
    temporal/locative preposition (in, after, during, within, throughout…).
    The obl subtree occupies line N; matrix ROOT is on line N+1.

The regex (validate_frame_predication_merges.py) used FRAME_LINE_RE to match
patterns like "it came to pass", "in the N year", "after they/I/he/we", etc.,
and PRED_LEAD_RE to confirm the next line starts a matrix predication.

Why UD is cleaner:
  - DEPREL `advcl` scopes to genuine adverbial-clause frames; the regex
    matched lines starting with specific opener words which frequently
    misfire on AICTP continuations that already have a matrix on the same line.
  - The `obl` + preposition pattern captures locative/temporal PPs without
    a hardcoded "in the N year / in the commencement / during" list.
  - Line-boundary crossing is computed directly from the line_map; the regex
    only detects the break by checking if the next line is a PRED_LEAD.

Distinct from Rule 28 (validate_rule_28_speech_act_after_frame.py):
  Rule 28 targets frame + colon-terminated speech-tag specifically.
  This validator targets the broader frame+matrix one-proposition pattern.

Paired regex validator: validators/colometry/validate_frame_predication_merges.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from validators.parsing.conllu_query import load_conllu, Sentence, Token
from validators.parsing.line_mapping import build_line_map, book_paths

BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]

# Temporal/conditional subordinators that mark a frame advcl
FRAME_MARKS = {
    "when", "after", "before", "as", "while", "until", "if",
    "because", "since", "though", "although", "whereas", "whereby",
    "wherefore", "inasmuch",
}

# AICTP-root lemma: "pass" in "it came to pass"
AICTP_ROOT_LEMMA = "pass"

# Temporal/locative prepositions for Pattern B (obl frame)
FRAME_PREPS = {
    "in", "after", "during", "within", "throughout", "at",
    "on", "upon", "before", "until", "since",
}

# Liturgical-formula filter (Category C — hostile-audit 2026-05-10):
# Sacred-formula PP frames ("In the name of Jesus Christ", etc.) must NOT
# auto-merge; they carry their own formulaic weight as Category C boundaries.
# Detection: Pattern B obl-PP where case lemma is "in" AND the obl head's
# form/lemma matches a deity or sacred-name token.
DEITY_SACRED_NAMES = {
    "jesus", "christ", "god", "lord", "father", "son",
    "holy", "ghost", "spirit",
}

# Matrix-completeness filter (hostile-audit 2026-05-10):
# Skip merge when the matrix ROOT is a copula ("be") that has no predicate
# complement (xcomp/ccomp/nsubj:pass/obj) on the same line — the proposition
# is grammatically open and continues on the next line.
# Operationally: matrix lemma in COPULA_LEMMAS AND no xcomp/ccomp dependent
# inside the matrix line.
COPULA_LEMMAS = {"be", "is", "was", "were", "am", "are"}


def _subtree_lines(sent: Sentence, root: Token, line_map: dict) -> set[int]:
    """Return the set of v2-mine lines occupied by the subtree of `root`."""
    lines = set()
    for t in sent.subtree(root):
        ln = line_map.get((sent.sent_id, t.id))
        if ln is not None:
            lines.add(ln)
    return lines


def _is_substantive_frame(sent: Sentence, frame_root: Token) -> bool:
    """Return True if the frame qualifies for Justification 5 own-line treatment.

    Per audit verdict on frame_predication_merges_ud (APPLY-WITH-FIXES): skip
    merge for frames with substantive content — these are J5 substantive
    adjuncts (year-formulas, multi-clause conditionals, etc.) and earn their
    own line per canon §1 Five Structural Justifications.

    A frame is substantive when ANY of:
    - >=8 word tokens (PUNCT excluded) — bulk threshold
    - contains a relative clause inside (acl/acl:relcl) — has internal
      predication
    - contains a coordinate stack of >=2 conj members — list-shaped
    - contains a purpose-adjunct child (advcl with modal aux) — embedded
      finite frame
    """
    subtree = list(sent.subtree(frame_root))
    word_tokens = [t for t in subtree if t.upos != "PUNCT"]
    if len(word_tokens) >= 8:
        return True
    for t in subtree:
        if t is frame_root:
            continue
        if t.deprel in ("acl", "acl:relcl"):
            return True
    conj_count = sum(1 for t in subtree if t.deprel == "conj")
    if conj_count >= 2:
        return True
    for t in subtree:
        if t is frame_root:
            continue
        if t.deprel == "advcl":
            for aux in sent.aux_of(t):
                if aux.upos == "AUX" and aux.lemma in {
                    "may", "might", "shall", "should", "will", "would",
                    "can", "could", "must",
                }:
                    return True
    return False


def _is_liturgical_formula(sent: Sentence, obl: Token, case_tokens: list) -> bool:
    """Return True if this Pattern B PP is a sacred/liturgical formula.

    Condition: case lemma is "in" AND the obl head's lowercased form or lemma
    appears in DEITY_SACRED_NAMES.  Catches "In the name of Jesus Christ" and
    similar.  Category C — must not auto-merge (hostile-audit 2026-05-10).
    """
    if not any(c.lemma == "in" for c in case_tokens):
        return False
    form_lc = obl.form.lower()
    lemma_lc = obl.lemma.lower()
    if form_lc in DEITY_SACRED_NAMES or lemma_lc in DEITY_SACRED_NAMES:
        return True
    # Also check immediate children of the obl for a deity name
    # (handles "In the name of Jesus Christ" where obl head is "name")
    for t in sent.dependents_of(obl):
        if t.form.lower() in DEITY_SACRED_NAMES or t.lemma.lower() in DEITY_SACRED_NAMES:
            return True
    return False


def _is_incomplete_matrix(sent: Sentence, matrix_root: Token,
                           matrix_lines: set[int], line_map: dict) -> bool:
    """Return True if the matrix clause is grammatically incomplete.

    Condition: matrix ROOT lemma is a copula (be/is/was/were) AND the matrix
    line contains no predicate complement (xcomp, ccomp) that would complete
    the proposition — meaning the copula is awaiting a predicate on a
    subsequent line.  (hostile-audit 2026-05-10: 2 Ne 4952/4953 case.)
    """
    if matrix_root.lemma not in COPULA_LEMMAS:
        return False
    # Look for xcomp or ccomp dependents on the same matrix line
    for dep in sent.dependents_of(matrix_root):
        if dep.deprel in ("xcomp", "ccomp"):
            dep_line = line_map.get((sent.sent_id, dep.id))
            if dep_line is not None and dep_line in matrix_lines:
                return False  # predicate complement IS present on this line
    return True  # copula with no predicate complement → incomplete


def _has_matrix_subject(sent: Sentence, matrix_root: Token) -> bool:
    """Return True if the matrix clause has a recoverable nsubj."""
    # Explicit nsubj
    for dep in sent.dependents_of(matrix_root):
        if dep.deprel in {"nsubj", "nsubj:pass", "expl"}:
            return True
    # Pro-drop: BofM uses "he/she/they/it" which UD parses as nsubj;
    # their absence (pro-drop in archaic style) still counts as subject-
    # continuous.  Return True for pro-drop tolerance.
    return True  # permissive: require explicit nsubj only via STRONG/REVIEW split


def _matrix_tokens_lines(sent: Sentence, matrix_root: Token,
                          frame_subtree_ids: set[int],
                          line_map: dict) -> set[int]:
    """Lines occupied by the matrix root's OWN tokens (excluding frame subtree)."""
    lines = set()
    for t in sent.tokens:
        if t.id in frame_subtree_ids:
            continue
        ln = line_map.get((sent.sent_id, t.id))
        if ln is not None:
            lines.add(ln)
    return lines


def scan_book(book_id: str) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)

    violations = []
    for sent in sentences:
        matrix_root = sent.root()
        if matrix_root is None:
            continue
        matrix_line = line_map.get((sent.sent_id, matrix_root.id))
        if matrix_line is None:
            continue

        # Pattern A: advcl frame under the matrix root
        for advcl in sent.dependents_of(matrix_root, deprel="advcl"):
            mark = sent.mark_of(advcl)
            is_frame_mark = mark is not None and mark.lemma in FRAME_MARKS
            is_aictp = advcl.lemma == AICTP_ROOT_LEMMA
            if not (is_frame_mark or is_aictp):
                continue
            frame_subtree = sent.subtree(advcl)
            frame_subtree_ids = {t.id for t in frame_subtree}
            frame_lines = set()
            for t in frame_subtree:
                ln = line_map.get((sent.sent_id, t.id))
                if ln is not None:
                    frame_lines.add(ln)
            if not frame_lines:
                continue
            frame_max_line = max(frame_lines)
            if frame_max_line >= matrix_line:
                continue  # frame not before matrix

            # KEY CONSTRAINT (matches regex is_frame_only):
            # The frame must occupy its own dedicated line — no tokens from
            # OUTSIDE the frame subtree should share that same line.
            # If other sentence tokens (matrix clause tokens) also appear on
            # frame_max_line, the two clauses are already co-present on one
            # line and this is not a fragmented-ATU violation.
            non_frame_lines = _matrix_tokens_lines(
                sent, matrix_root, frame_subtree_ids, line_map
            )
            if frame_max_line in non_frame_lines:
                continue  # frame line shared with matrix tokens → not isolated

            # Matrix lines for completeness filter
            matrix_lines = _matrix_tokens_lines(
                sent, matrix_root, frame_subtree_ids, line_map
            )

            gap = matrix_line - frame_max_line
            if gap != 1:
                bucket = "REVIEW-REQUIRED"
                review_reason = "non-adjacent-gap"
            elif _is_substantive_frame(sent, advcl):
                bucket = "REVIEW-REQUIRED"
                review_reason = "substantive-frame-J5"
            elif _is_incomplete_matrix(sent, matrix_root, matrix_lines, line_map):
                bucket = "REVIEW-REQUIRED"
                review_reason = "incomplete-matrix-copula"
            else:
                bucket = "STRONG-MERGE-CANDIDATE"
                review_reason = None
            violations.append({
                "book": book_id,
                "sent_id": sent.sent_id,
                "pattern": "A-advcl",
                "frame_form": advcl.form,
                "mark_lemma": mark.lemma if mark else "(aictp)",
                "matrix_form": matrix_root.form,
                "matrix_lemma": matrix_root.lemma,
                "frame_line": frame_max_line,
                "matrix_line": matrix_line,
                "bucket": bucket,
                "review_reason": review_reason,
                "v2_path": str(v2_path),
            })

        # Pattern B: substantive PP frame (obl with temporal/locative prep)
        for obl in sent.dependents_of(matrix_root, deprel="obl"):
            # obl is headed by a case/mark; check the case child
            case_tokens = sent.dependents_of(obl, deprel="case")
            if not case_tokens:
                continue
            if not any(c.lemma in FRAME_PREPS for c in case_tokens):
                continue
            frame_subtree = sent.subtree(obl)
            frame_subtree_ids = {t.id for t in frame_subtree}
            frame_lines = set()
            for t in frame_subtree:
                ln = line_map.get((sent.sent_id, t.id))
                if ln is not None:
                    frame_lines.add(ln)
            if not frame_lines:
                continue
            frame_max_line = max(frame_lines)
            if frame_max_line >= matrix_line:
                continue

            # Same isolation constraint as Pattern A
            non_frame_lines = _matrix_tokens_lines(
                sent, matrix_root, frame_subtree_ids, line_map
            )
            if frame_max_line in non_frame_lines:
                continue

            # Matrix lines for completeness filter
            matrix_lines_b = _matrix_tokens_lines(
                sent, matrix_root, frame_subtree_ids, line_map
            )

            gap = matrix_line - frame_max_line
            if gap != 1:
                bucket = "REVIEW-REQUIRED"
                review_reason = "non-adjacent-gap"
            elif _is_liturgical_formula(sent, obl, case_tokens):
                bucket = "REVIEW-REQUIRED"
                review_reason = "liturgical-formula-C"
            elif _is_substantive_frame(sent, obl):
                bucket = "REVIEW-REQUIRED"
                review_reason = "substantive-frame-J5"
            elif _is_incomplete_matrix(sent, matrix_root, matrix_lines_b, line_map):
                bucket = "REVIEW-REQUIRED"
                review_reason = "incomplete-matrix-copula"
            else:
                bucket = "STRONG-MERGE-CANDIDATE"
                review_reason = None
            case_lemma = next(
                (c.lemma for c in case_tokens if c.lemma in FRAME_PREPS), "?"
            )
            violations.append({
                "book": book_id,
                "sent_id": sent.sent_id,
                "pattern": "B-obl-pp",
                "frame_form": obl.form,
                "mark_lemma": case_lemma,
                "matrix_form": matrix_root.form,
                "matrix_lemma": matrix_root.lemma,
                "frame_line": frame_max_line,
                "matrix_line": matrix_line,
                "bucket": bucket,
                "review_reason": review_reason,
                "v2_path": str(v2_path),
            })

    return violations


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book", help="single book id (default: all)")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    book_ids = [args.book] if args.book else BOOKS

    all_violations = []
    for bid in book_ids:
        try:
            vs = scan_book(bid)
        except FileNotFoundError as e:
            print(f"[skip] {bid}: {e}", file=sys.stderr)
            continue
        all_violations.extend(vs)
        if args.verbose:
            print(f"{bid}: {len(vs)} violations")

    strong = [v for v in all_violations if v["bucket"] == "STRONG-MERGE-CANDIDATE"]
    review = [v for v in all_violations if v["bucket"] == "REVIEW-REQUIRED"]
    pat_a = [v for v in all_violations if v["pattern"] == "A-advcl"]
    pat_b = [v for v in all_violations if v["pattern"] == "B-obl-pp"]

    print("=" * 72)
    print("Frame+predication merge candidates — UD-query")
    print("=" * 72)
    print(f"Books scanned: {len(book_ids)}")
    print(f"Violations:    {len(all_violations)}")
    print(f"  Pattern A (advcl frame):    {len(pat_a)}")
    print(f"  Pattern B (obl-PP frame):   {len(pat_b)}")
    print(f"  STRONG-MERGE-CANDIDATE:     {len(strong)}")
    print(f"  REVIEW-REQUIRED:            {len(review)}")
    print()

    if all_violations:
        print("Sample (first 10):")
        for v in all_violations[:10]:
            tag = "[R]" if v["bucket"] == "REVIEW-REQUIRED" else "   "
            print(f"  {tag} [{v['book']}] sent={v['sent_id']}  "
                  f"pat={v['pattern']}  mark={v['mark_lemma']!r}  "
                  f"frame-line={v['frame_line']} matrix-line={v['matrix_line']}  "
                  f"matrix={v['matrix_form']!r}")

    print(f"RESULT: violations={len(strong)} strong={len(strong)} review={len(review)}")
    sys.exit(1 if strong else 0)


if __name__ == "__main__":
    main()
