"""
Rule 17 (Complement Integrity) — UD-query implementation.

Phase 0 prototype using validators/parsing/conllu_query.py + line_mapping.py.

UD signature (per canon §3):
    ccomp(V, clause) where mark(clause) = 'that' and V.lemma in governing-verb set.

Violation: V and the 'that' mark sit on different v2-mine lines. The line
break should be removed (MERGE across boundary).

Why this is cleaner than the regex implementation:
  - LEMMA collapses surface morphology (saith/said/saying/sayest -> say).
  - ccomp distinguishes complement clauses from advcl/acl:relcl/parataxis,
    so the regex's exception filters (purpose 'that they might', AICTP,
    'that is' appositive, 'so X that Y' result, resumptive-after-if,
    relative 'that which has been', aspectual bare-finite) do not need
    individual handling — UD assigns each a non-ccomp deprel.

Comparison target: validators/colometry/validate_rule_17_complement_integrity.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running as a script from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from validators.parsing.conllu_query import load_conllu
from validators.parsing.line_mapping import build_line_map, book_paths


# Governing-verb lemmas, by class. Matches canon §5 Rule 17.
CAUSATIVE = {"cause", "suffer", "permit", "command", "grant"}
ASPECTUAL = {"begin", "cease", "continue"}
SPEECH = {
    "say", "speak", "declare", "testify", "swear", "proclaim",
    "tell", "confess", "rehearse", "preach", "answer", "cry",
}
COGNITION = {
    "know", "believe", "perceive", "remember", "understand", "hear",
    "see", "suppose", "imagine", "forget", "think",
}
VOLITION = {"wish", "desire", "hope", "long", "trust", "pray", "seek"}

GOVERNING_LEMMAS = CAUSATIVE | ASPECTUAL | SPEECH | COGNITION | VOLITION

# Directive-petition matrix verbs whose "that"-complement with a modal aux
# reads ambiguously between content (UD ccomp) and purpose (UD advcl).
# When matrix lemma is in this set AND the ccomp body has a modal aux,
# bucket as REVIEW-REQUIRED instead of STRONG-MERGE-CANDIDATE.
DIRECTIVE_PETITION = {"cry", "pray", "beseech", "ask", "seek"}

# Modal aux lemmas that mark the ambiguity. Lemma 'will' covers will/would;
# lemma 'shall' covers shall/should; etc.
MODAL_AUX_LEMMAS = {"will", "shall", "may", "can", "must", "might", "should", "would", "could"}


def lemma_class(lemma: str) -> str:
    if lemma in CAUSATIVE: return "causative"
    if lemma in ASPECTUAL: return "aspectual"
    if lemma in SPEECH: return "speech"
    if lemma in COGNITION: return "cognition"
    if lemma in VOLITION: return "volition"
    return "unknown"


def categorize(sent, ccomp_root, head) -> str:
    """Return 'STRONG-MERGE-CANDIDATE' or 'REVIEW-REQUIRED'.

    REVIEW-REQUIRED when matrix is a directive-petition verb AND the
    ccomp body has a modal aux — that combination reads ambiguously
    between content and purpose, and may indicate an advcl-purpose
    mistagged as ccomp by the LLM annotator.
    """
    if head.lemma in DIRECTIVE_PETITION:
        for aux in sent.aux_of(ccomp_root):
            if aux.lemma in MODAL_AUX_LEMMAS:
                return "REVIEW-REQUIRED"
    return "STRONG-MERGE-CANDIDATE"


# All 15 BofM books in the corpus.
BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]


def scan_book(book_id: str, *, verbose: bool = False) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)

    violations = []
    for sent in sentences:
        for ccomp in sent.find(deprel="ccomp"):
            head = sent.head_of(ccomp)
            if head is None:
                continue
            # Rule 17 governs VERB complements; ccomp of a noun (e.g. the noun
            # "desire" + that-clause) is a separate pattern not currently
            # codified. Surface those cases via a different signature if
            # canon ever adds a rule.
            if head.upos != "VERB":
                continue
            if head.lemma not in GOVERNING_LEMMAS:
                continue
            mark = sent.mark_of(ccomp)
            if mark is None or mark.lemma != "that":
                continue
            head_line = line_map.get((sent.sent_id, head.id))
            mark_line = line_map.get((sent.sent_id, mark.id))
            if head_line is None or mark_line is None:
                continue
            if head_line == mark_line:
                continue  # already merged; not a violation
            violations.append({
                "book": book_id,
                "sent_id": sent.sent_id,
                "head_id": head.id,
                "head_form": head.form,
                "head_lemma": head.lemma,
                "head_class": lemma_class(head.lemma),
                "head_line": head_line,
                "mark_line": mark_line,
                "v2_path": str(v2_path),
                "bucket": categorize(sent, ccomp, head),
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

    print("=" * 72)
    print("Rule 17 UD-query — BofM corpus")
    print("=" * 72)
    print(f"Books scanned: {len(book_ids)}")
    print(f"Violations:    {len(all_violations)}")
    strong = [v for v in all_violations if v["bucket"] == "STRONG-MERGE-CANDIDATE"]
    review = [v for v in all_violations if v["bucket"] == "REVIEW-REQUIRED"]
    print(f"  STRONG-MERGE-CANDIDATE: {len(strong)}")
    print(f"  REVIEW-REQUIRED:        {len(review)}")
    print()

    if all_violations:
        by_class: dict[str, list] = {}
        for v in all_violations:
            by_class.setdefault(v["head_class"], []).append(v)

        for cls in sorted(by_class):
            items = by_class[cls]
            n_strong = sum(1 for v in items if v["bucket"] == "STRONG-MERGE-CANDIDATE")
            n_review = len(items) - n_strong
            print(f"--- {cls.upper()} ({len(items)}: {n_strong} strong, {n_review} review) ---")
            for v in items[:8]:
                tag = "[R]" if v["bucket"] == "REVIEW-REQUIRED" else "   "
                print(f"  {tag} [{v['book']}] sent={v['sent_id']} "
                      f"{v['head_form']!r} (lemma={v['head_lemma']}) "
                      f"line {v['head_line']} -> mark on line {v['mark_line']}")
            if len(items) > 8:
                print(f"      ... +{len(items) - 8} more")
            print()

    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
