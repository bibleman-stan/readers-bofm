"""
Rule 27 ("Insomuch That" Binding) — UD-query implementation.

UD signature (per canon §3 / §5 Rule 27):
    advcl with mark = 'insomuch that' (compound SCONJ, likely tokenized as
    two tokens: 'insomuch' + 'that'; or occasionally a single MWE token).

Default action: SPLIT.
MERGE only when ALL THREE conditions hold:
    1. Result clause ≤ 8 words (subtree word count, excluding PUNCT)
    2. Subject continuity (nsubj of advcl ≈ nsubj of matrix, or elided)
    3. No camera-angle shift — NOT mechanically determinable → REVIEW.

Bucket logic (parallel to existing regex validator):
  STRONG-SPLIT-CANDIDATE  — currently MERGED, cond 1 or 2 fails → should split.
  STRONG-SPLIT-CORRECT    — currently split, cond 1 or 2 fails → split is right.
  STRONG-MERGE-CANDIDATE  — currently split, cond 1+2 hold → review for merge.
  STRONG-MERGE-CORRECT    — currently merged, cond 1+2 hold → merge is defensible.
  REVIEW-REQUIRED         — subject-continuity is ambiguous.

The UD version replaces the regex 'before_insomuch' heuristic with proper
deprel/lemma detection of the compound subordinator.

Detection strategy:
  1. Find all 'advcl' tokens.
  2. For each advcl, collect its mark(s).
  3. If any mark has lemma 'insomuch' — OR the mark-sequence preceding 'that'
     contains 'insomuch' — treat as insomuch-that binding.
  4. Also check for a single 'mark' token with form/lemma 'insomuch that'
     (MWE tokenization).

Word-count strategy (Cond 1):
  Count only non-PUNCT tokens in the advcl subtree that sit on the SAME
  v2-mine line as the 'insomuch' mark token, excluding the 'insomuch' and
  'that' tokens themselves.  This mirrors the regex validator's approach of
  measuring only the text after 'insomuch that' on the same v2 line, rather
  than the full syntactic subtree which may span several continuation lines.

  Two tokenization patterns occur in the corpus:
    Sig-A: insomuch=ADV/advmod + that=SCONJ/mark, both children of advcl head.
    Sig-B: insomuch=ADV/mark + that=SCONJ/fixed(head=insomuch), insomuch child
           of advcl head.
  Both are handled by _is_insomuch_that(); the word-count fix applies to both.
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

# Co-referential pronouns that pass subject-continuity check
CO_REF_PRONOUNS = {
    "he", "she", "they", "it", "i", "we",
    "his", "her", "their", "its", "my", "our",
    "him", "them", "us", "me",
    # archaic BofM second-person
    "ye", "thee", "thou", "thy", "thine",
}

# Elided-subject verbs (first word of result clause with no explicit subject)
ELIDED_SUBJECT_VERBS = {
    "did", "was", "were", "had", "could", "might", "would",
    "shall", "will", "hath", "doth", "art", "am", "are",
    "began", "fell", "came", "went", "cried", "spake",
    "led", "brought", "felt", "smote", "became",
}

# New-NP starters → subject shift
NEW_NP_STARTERS = {
    "the", "a", "an", "all", "many", "no", "every", "some",
    "this", "these", "those", "that", "yea", "also", "even",
}

# Expletive-there verbs (canon §5 Rule 27)
EXPLETIVE_THERE_VERBS = {
    "was", "were", "is", "are", "arose", "came", "stood", "dwelt",
    "shall", "never", "had", "hath", "began",
}


def _is_insomuch_that(sent, advcl_tok) -> bool:
    """
    Return True if the advcl has an insomuch-that compound subordinator.

    Handles three tokenizations:
      (a) Single mark token with lemma/form containing 'insomuch'
      (b) Two mark tokens: one lemma='insomuch', one lemma='that'
      (c) One mark='that' preceded by an advmod/fixed token lemma='insomuch'
    """
    marks = sent.dependents_of(advcl_tok, deprel="mark")

    # Case (a): single token with insomuch in lemma/form
    for m in marks:
        if "insomuch" in (m.lemma or "").lower():
            return True
        if "insomuch" in (m.form or "").lower():
            return True

    # Case (b): two mark tokens — one is 'insomuch', one is 'that'
    mark_lemmas = {(m.lemma or "").lower() for m in marks}
    if "insomuch" in mark_lemmas and "that" in mark_lemmas:
        return True

    # Case (c): mark='that' + fixed/advmod sibling 'insomuch'
    if "that" in mark_lemmas:
        for sibling in sent.dependents_of(advcl_tok, deprel="fixed"):
            if "insomuch" in (sibling.lemma or "").lower():
                return True
        for sibling in sent.dependents_of(advcl_tok, deprel="advmod"):
            if "insomuch" in (sibling.lemma or "").lower():
                return True

    return False


# Forms to exclude from result-clause word count (the subordinator itself)
_INSOMUCH_THAT_FORMS = {"insomuch", "that"}


def _result_word_count(sent, advcl_tok, line_map: dict, sent_id: str,
                       mark_line: int) -> int:
    """Count result-clause content words.

    Counts non-PUNCT tokens in the advcl subtree that sit on the *same*
    v2-mine line as the 'insomuch' mark token (mark_line), excluding the
    'insomuch' and 'that' tokens themselves.

    Rationale: the regex validator measures only the text after 'insomuch that'
    on the same v2-mine line (line N).  The full syntactic subtree spans
    continuation lines that the regex never sees, inflating the UD count.
    Restricting to mark_line tokens makes Cond 1 comparable across both
    detectors.
    """
    count = 0
    for t in sent.subtree(advcl_tok):
        if t.upos == "PUNCT":
            continue
        if (t.form or "").lower() in _INSOMUCH_THAT_FORMS:
            continue
        if (t.lemma or "").lower() in _INSOMUCH_THAT_FORMS:
            continue
        if line_map.get((sent_id, t.id)) != mark_line:
            continue
        count += 1
    return count


def _subject_continuity(sent, advcl_tok, matrix_tok,
                        line_map: dict | None = None,
                        sent_id: str | None = None,
                        mark_line: int | None = None) -> str:
    """
    Returns 'continuous', 'shift', or 'ambiguous'.

    Checks whether the result clause shares a subject with the matrix.
    Strategy: look for nsubj of advcl_tok; compare to nsubj of matrix.
    Fall back to first-word heuristic from the subtree when no explicit nsubj.

    When line_map / sent_id / mark_line are supplied, the heuristic fallback
    restricts to tokens on mark_line only.  This prevents matrix-line discourse
    particles (e.g. "yea," attached as advcl children) from being mistaken for
    the first word of the result clause.
    """
    # Find explicit nsubj of result clause
    result_subjects = sent.dependents_of(advcl_tok, deprel="nsubj")
    # Also accept nsubj:pass (passive)
    result_subjects += sent.dependents_of(advcl_tok, deprel="nsubj:pass")

    if result_subjects:
        subj = result_subjects[0]
        lemma = (subj.lemma or "").lower()
        if lemma in CO_REF_PRONOUNS:
            return "continuous"
        # New full-NP subject
        return "shift"

    # No explicit nsubj → check first word of subtree (heuristic)
    subtree = sorted(sent.subtree(advcl_tok), key=lambda t: t.id)
    # Skip the 'insomuch' / 'that' mark tokens at the front
    # Also restrict to mark_line if we have the mapping (avoids pre-mark
    # discourse tokens like "yea," that attach to advcl but sit on the
    # matrix line)
    def _on_mark_line(t) -> bool:
        if line_map is None or sent_id is None or mark_line is None:
            return True
        return line_map.get((sent_id, t.id)) == mark_line

    content_tokens = [
        t for t in subtree
        if "insomuch" not in (t.lemma or "").lower()
        and (t.lemma or "").lower() != "that"
        and t.upos != "PUNCT"
        and _on_mark_line(t)
    ]
    if not content_tokens:
        return "ambiguous"

    first = content_tokens[0]
    first_lemma = (first.lemma or "").lower()
    first_form = (first.form or "").lower()

    # Expletive-there: new-entity semantic subject → shift (canon §5 R27)
    if first_lemma == "there":
        second_content = content_tokens[1] if len(content_tokens) > 1 else None
        if second_content:
            sec_lemma = (second_content.lemma or "").lower()
            if sec_lemma in EXPLETIVE_THERE_VERBS:
                return "shift"

    if first_lemma in CO_REF_PRONOUNS or first_form in CO_REF_PRONOUNS:
        return "continuous"

    if first_lemma in NEW_NP_STARTERS:
        return "shift"

    # Title-case non-pronoun → likely named subject
    if first.form and first.form[0].isupper() and first_lemma not in CO_REF_PRONOUNS:
        return "shift"

    if first_lemma in ELIDED_SUBJECT_VERBS:
        return "continuous"

    return "ambiguous"


def scan_book(book_id: str) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)

    results = []
    for sent in sentences:
        for advcl_tok in sent.find(deprel="advcl"):
            if not _is_insomuch_that(sent, advcl_tok):
                continue

            matrix_tok = sent.head_of(advcl_tok)
            if matrix_tok is None:
                continue

            # Line of the insomuch-that mark token (first mark in subtree)
            # Sig-A: insomuch is advmod child of advcl; Sig-B: insomuch is mark.
            marks = sent.dependents_of(advcl_tok, deprel="mark")
            advmods = sent.dependents_of(advcl_tok, deprel="advmod")
            # Find the 'insomuch' token (leftmost among mark + advmod children)
            insomuch_marks = [
                m for m in (marks + advmods)
                if "insomuch" in (m.lemma or "").lower()
                or "insomuch" in (m.form or "").lower()
            ]
            if not insomuch_marks:
                # fallback to first mark
                insomuch_marks = marks if marks else []

            if not insomuch_marks:
                continue

            mark_tok = min(insomuch_marks, key=lambda t: t.id)
            matrix_line = line_map.get((sent.sent_id, matrix_tok.id))
            mark_line = line_map.get((sent.sent_id, mark_tok.id))
            if matrix_line is None or mark_line is None:
                continue

            # Determine current state: SPLIT (mark on different line from matrix)
            # or MERGED (mark on same line as matrix)
            state = "SPLIT" if mark_line != matrix_line else "MERGED"

            # Condition 1: count only same-line tokens (excluding insomuch/that)
            rc_words = _result_word_count(
                sent, advcl_tok, line_map, sent.sent_id, mark_line
            )
            cond1 = rc_words <= 8

            # Condition 2: pass line context so heuristic ignores pre-mark tokens
            subj = _subject_continuity(
                sent, advcl_tok, matrix_tok,
                line_map=line_map, sent_id=sent.sent_id, mark_line=mark_line,
            )
            cond2_holds = (subj == "continuous")
            cond2_ambiguous = (subj == "ambiguous")

            # Condition 3: always requires human review (camera angle)

            # Categorize
            if cond2_ambiguous:
                bucket = "REVIEW-REQUIRED"
            elif state == "SPLIT":
                if cond1 and cond2_holds:
                    bucket = "STRONG-MERGE-CANDIDATE"
                else:
                    bucket = "STRONG-SPLIT-CORRECT"
            else:  # MERGED
                if cond1 and cond2_holds:
                    bucket = "STRONG-MERGE-CORRECT"
                else:
                    bucket = "STRONG-SPLIT-CANDIDATE"

            results.append({
                "book": book_id,
                "sent_id": sent.sent_id,
                "matrix_form": matrix_tok.form,
                "matrix_line": matrix_line,
                "mark_line": mark_line,
                "state": state,
                "rc_words": rc_words,
                "cond1": cond1,
                "subj_continuity": subj,
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
            print(f"{bid}: {len(recs)} instances found")

    cats: dict[str, list] = {
        "STRONG-SPLIT-CANDIDATE": [],
        "STRONG-SPLIT-CORRECT": [],
        "STRONG-MERGE-CANDIDATE": [],
        "STRONG-MERGE-CORRECT": [],
        "REVIEW-REQUIRED": [],
    }
    for r in all_results:
        cats[r["bucket"]].append(r)

    split_recs = [r for r in all_results if r["state"] == "SPLIT"]
    merged_recs = [r for r in all_results if r["state"] == "MERGED"]

    print("=" * 72)
    print('Rule 27 UD-query — "Insomuch That" Binding — BofM corpus')
    print("=" * 72)
    print(f"Books scanned:              {len(book_ids)}")
    total = len(all_results)
    print(f"Total instances:            {total}")
    pct = lambda n: f" ({round(100*n/total)}%)" if total else ""
    print(f"  Currently split:   {len(split_recs):3d}{pct(len(split_recs))}")
    print(f"  Currently merged:  {len(merged_recs):3d}{pct(len(merged_recs))}")
    print()
    print("Buckets:")
    for name, items in cats.items():
        print(f"  {name:30s}  {len(items):3d}")
    print()

    def show_samples(label: str, items: list[dict], n: int = 5):
        if not items:
            return
        print(f"--- {label} (up to {n} samples) ---")
        for r in items[:n]:
            print(f"  [{r['book']}] sent={r['sent_id']}  state={r['state']}")
            print(f"    matrix: {r['matrix_form']!r} line {r['matrix_line']}")
            print(f"    mark:   'insomuch that' line {r['mark_line']}")
            print(f"    rc_words={r['rc_words']}  subj={r['subj_continuity']}")
            print(f"    text: {r['sent_text']}")
            print()

    show_samples("STRONG-SPLIT-CANDIDATE", cats["STRONG-SPLIT-CANDIDATE"])
    show_samples("STRONG-MERGE-CANDIDATE", cats["STRONG-MERGE-CANDIDATE"])
    show_samples("STRONG-SPLIT-CORRECT",   cats["STRONG-SPLIT-CORRECT"])
    show_samples("STRONG-MERGE-CORRECT",   cats["STRONG-MERGE-CORRECT"])
    show_samples("REVIEW-REQUIRED",        cats["REVIEW-REQUIRED"])

    has_candidates = (
        cats["STRONG-SPLIT-CANDIDATE"] or cats["STRONG-MERGE-CANDIDATE"]
    )
    _strong_27 = len(cats["STRONG-SPLIT-CANDIDATE"]) + len(cats["STRONG-MERGE-CANDIDATE"])
    _review_27 = len(cats["REVIEW-REQUIRED"])
    print(f"RESULT: violations={_strong_27} strong={_strong_27} review={_review_27}")
    sys.exit(1 if has_candidates else 0)


if __name__ == "__main__":
    main()
