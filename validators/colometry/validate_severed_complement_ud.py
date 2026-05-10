"""
Validate severed complement-spanning-frame patterns — UD-query implementation.

UD signature:
  A `ccomp` clause headed by a speech/cognition verb V, where inside the ccomp:
    - an advcl or adverbial modifier (advcl/obl) sits on a DIFFERENT v2-mine
      line than the ccomp root (the matrix predication of the complement)
    - the advcl/obl subtree ends one v2-mine line and the ccomp root starts
      the next line (so the frame/advcl was severed from its own matrix clause)

The regex pattern (validate_severed_complement.py) matched:
  line N: `…that (when|after|before|as|while|until|if|because|since|
            though|although)…,`
  line N+1: subject-pronoun or common-NP lead (matrix predication)

UD translation:
  - The triggering verb V has a `ccomp` child (complement clause root = CR)
  - CR has an `advcl` child whose MARK lemma is one of the temporal/conditional
    subordinators above
  - advcl sits on line N; CR sits on line N+1 (or later)
  - V.lemma in SPEECH | COGNITION (matches the regex's implicit assumption
    that this is a complement-governor context)

Why UD is cleaner:
  - DEPREL `ccomp` scopes the search to complement clauses; the regex matched
    any occurrence of 'that (when|after|…)' regardless of syntactic context,
    producing false positives where 'that' is a relative pronoun.
  - The `advcl` + mark-lemma pattern explicitly encodes the frame+matrix
    structure rather than approximating it with surface word-order.
  - LEMMA normalization eliminates the need for PRED_LEAD_RE's wordlist of
    subject/demonstrative openers.

Paired regex validator: validators/colometry/validate_severed_complement.py
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

SPEECH = {
    "say", "speak", "declare", "testify", "swear", "proclaim",
    "tell", "confess", "rehearse", "preach", "answer", "cry",
}
COGNITION = {
    "know", "believe", "perceive", "remember", "understand", "hear",
    "see", "suppose", "imagine", "forget", "think",
}
GOVERNING_LEMMAS = SPEECH | COGNITION

# Temporal/conditional subordinators that introduce a frame inside a complement
FRAME_MARKS = {
    "when", "after", "before", "as", "while", "until",
    "if", "because", "since", "though", "although",
}


def scan_book(book_id: str) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)

    violations = []
    for sent in sentences:
        for ccomp in sent.find(deprel="ccomp"):
            # Governor must be a speech/cognition verb
            head = sent.head_of(ccomp)
            if head is None or head.upos != "VERB":
                continue
            if head.lemma not in GOVERNING_LEMMAS:
                continue
            # Inside the ccomp, look for advcl children of the ccomp root
            for advcl in sent.dependents_of(ccomp, deprel="advcl"):
                mark = sent.mark_of(advcl)
                if mark is None:
                    continue
                if mark.lemma not in FRAME_MARKS:
                    continue
                # The advcl (frame) and the ccomp root (matrix predication)
                # must sit on different lines
                advcl_line = line_map.get((sent.sent_id, advcl.id))
                ccomp_line = line_map.get((sent.sent_id, ccomp.id))
                if advcl_line is None or ccomp_line is None:
                    continue
                if advcl_line == ccomp_line:
                    continue  # frame and matrix already merged; no violation
                # Frame must appear BEFORE the ccomp root (line N < line N+1)
                if advcl_line >= ccomp_line:
                    continue
                # Bucket: multi-line gaps are REVIEW-REQUIRED
                gap = ccomp_line - advcl_line
                bucket = "STRONG-MERGE-CANDIDATE" if gap == 1 else "REVIEW-REQUIRED"
                violations.append({
                    "book": book_id,
                    "sent_id": sent.sent_id,
                    "governor_form": head.form,
                    "governor_lemma": head.lemma,
                    "advcl_form": advcl.form,
                    "mark_lemma": mark.lemma,
                    "ccomp_form": ccomp.form,
                    "advcl_line": advcl_line,
                    "ccomp_line": ccomp_line,
                    "bucket": bucket,
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

    print("=" * 72)
    print("Severed complement-spanning-frame — UD-query")
    print("=" * 72)
    print(f"Books scanned: {len(book_ids)}")
    print(f"Violations:    {len(all_violations)}")
    print(f"  STRONG-MERGE-CANDIDATE: {len(strong)}")
    print(f"  REVIEW-REQUIRED:        {len(review)}")
    print()

    if all_violations:
        print("Sample (first 10):")
        for v in all_violations[:10]:
            tag = "[R]" if v["bucket"] == "REVIEW-REQUIRED" else "   "
            print(f"  {tag} [{v['book']}] sent={v['sent_id']}  "
                  f"gov={v['governor_form']!r}({v['governor_lemma']})  "
                  f"mark={v['mark_lemma']!r}  "
                  f"frame-line={v['advcl_line']} ccomp-line={v['ccomp_line']}")

    print(f"RESULT: violations={len(all_violations)} strong={len(strong)} review={len(review)}")
    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
