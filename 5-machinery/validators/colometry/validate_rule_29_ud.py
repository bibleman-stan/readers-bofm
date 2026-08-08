"""
Rule 29 (Bare Infinitival Orphan Integrity) — UD-query implementation.

Canon §5 R29: a v2-mine line beginning with an infinitival `to`+VERB merges
with the line carrying the infinitival's governor when the governor is on the
immediately-preceding line (gap=1). A bare infinitival has a matrix-controlled
unexpressed subject; severed from its governor it is subject-gapped and
forward-incomplete — it cannot stand as an ATU. Governor POS is immaterial
(VERB / NOUN / ADJ all qualify).

R29 is the GENERAL rule of which R7 SCOPE-merge (motion-verb + purpose-INF)
and R17's `to`-INF complement are narrower slices. This validator covers the
residual — governors not already in R7 MOTION_VERBS or R17 GOVERNING_LEMMAS.

UD signature (per canon §5 R29):
    mark:        lemma=to, line-initial (char-col 0 of its v2-mine line)
    infinitival: upos=VERB, deprel in {xcomp, advcl, acl}
    governor:    upos in {VERB, NOUN, ADJ}
    gap = 1      governor on immediately-preceding line

Buckets:
    STRONG-MERGE-CANDIDATE — gap=1, n_parallel=1, governor POS clean
    REVIEW-REQUIRED        — gap>1 OR n_parallel>=2

Parse-error guards (per §7.3 audit 2026-05-14, UD-verification audit):
    - governor line itself line-initial `to`/`and to`/`or to` (stacked-infinitive
      artifact — real governor is upstream) -> skip
    - governor upos in PRON/PROPN/AUX (UD mis-attachment) -> skip
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from validators.parsing.conllu_query import load_conllu
from validators.parsing.line_mapping import build_line_map_full, book_paths


# Exclusion-6 routing: governors already covered by the narrower slices.
R17_GOVERNING_LEMMAS = {
    "cause", "suffer", "permit", "command", "grant",
    "begin", "cease", "continue",
    "say", "speak", "declare", "testify", "swear", "proclaim",
    "tell", "confess", "rehearse", "preach", "answer", "cry",
    "know", "believe", "perceive", "remember", "understand", "hear",
    "see", "suppose", "imagine", "forget", "think",
    "wish", "desire", "hope", "long", "trust", "pray", "seek",
    "observe", "endeavor", "attempt",
    "beseech", "ask", "plead",
}
R7_MOTION_VERBS = {
    "go", "come", "depart", "return", "journey", "travel",
    "ascend", "descend", "march", "run", "walk", "flee",
    "retreat", "arise", "rise", "hasten", "pass", "wander",
    "tarry", "stay", "remain", "abide", "sit",
    "gather", "assemble", "lift", "fall",
}

GOVERNOR_POS_OK = {"VERB", "NOUN", "ADJ"}
INFINITIVAL_DEPRELS = ("xcomp", "advcl", "acl")

# Co-orphaned-prefix sub-variant (Cat B — surface only, never auto-apply).
# Finite-verb xpos tags — a line carrying one of these has independent
# predication and is NOT a bare orphan. (feats VerbForm=Fin is unreliable
# in this parse; xpos is the robust signal per §7.3 audit 2026-05-14.)
FINITE_VERB_XPOS = {"MD", "VBZ", "VBD", "VBP"}
# Correlative / comparative lemmas — a line carrying one of these is part of
# a comparative/result correlative construction (`so X as to Y`, `than to V`,
# `as if to V`, `whether to X or to Y`), NOT a co-orphaned-prefix orphan.
CORRELATIVE_LEMMAS = {
    "as", "than", "rather", "whether", "so", "such", "if",
    "both", "either", "neither",
}

BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]


def _collect_conj(sent, tid: int, acc: set) -> None:
    for t in sent.tokens:
        if t.deprel == "conj" and t.head == tid and t.upos == "VERB":
            acc.add(t.id)
            _collect_conj(sent, t.id, acc)


def _n_parallel(sent, inf, gov) -> int:
    """Count parallel infinitival members sharing this governor.

    max of (xcomp/advcl/acl + to-mark siblings under the same governor)
    and (conj-chained infinitival VERBs off this infinitive).
    """
    siblings = set()
    for t in sent.tokens:
        if t.upos == "VERB" and t.deprel in INFINITIVAL_DEPRELS:
            tg = sent.head_of(t)
            if tg is not None and tg.id == gov.id:
                tm = sent.mark_of(t)
                if tm is not None and tm.lemma == "to":
                    siblings.add(t.id)
    conj = {inf.id}
    _collect_conj(sent, inf.id, conj)
    return max(len(siblings), len(conj))


def _line_starts_infinitival(line_text: str) -> bool:
    """True if the line begins with `to`/`and to`/`or to` (stacked-infinitive guard)."""
    stripped = line_text.lstrip().lower()
    return (
        stripped.startswith("to ")
        or stripped.startswith("and to ")
        or stripped.startswith("or to ")
    )


def scan_book(book_id: str) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    lmf = build_line_map_full(v2_path, conllu_path)
    line_map = {k: v[0] for k, v in lmf.items()}
    col_map = {k: v[1] for k, v in lmf.items()}

    with open(v2_path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")

    violations = []
    for sent in sentences:
        for deprel in INFINITIVAL_DEPRELS:
            for inf in sent.find(deprel=deprel):
                if inf.upos != "VERB":
                    continue
                mark = sent.mark_of(inf)
                if mark is None or mark.lemma != "to":
                    continue
                gov = sent.head_of(inf)
                if gov is None:
                    continue
                # Exclusion 4: PRON/PROPN/AUX governor — UD mis-attachment.
                if gov.upos not in GOVERNOR_POS_OK:
                    continue
                mark_line = line_map.get((sent.sent_id, mark.id))
                mark_col = col_map.get((sent.sent_id, mark.id))
                gov_line = line_map.get((sent.sent_id, gov.id))
                if mark_line is None or gov_line is None or mark_col is None:
                    continue
                if mark_line == gov_line:
                    continue  # already merged; not a violation
                # Exclusion 6: already covered by R7 / R17 narrower slices.
                if gov.upos == "VERB" and (
                    gov.lemma in R17_GOVERNING_LEMMAS or gov.lemma in R7_MOTION_VERBS
                ):
                    continue
                # Exclusion 3: governor line itself line-initial infinitival
                # (stacked-infinitive parse artifact — real governor upstream).
                gov_idx = gov_line - 1
                if 0 <= gov_idx < len(lines) and _line_starts_infinitival(lines[gov_idx]):
                    continue

                gap = abs(mark_line - gov_line)
                n_par = _n_parallel(sent, inf, gov)

                if mark_col != 0:
                    # Co-orphaned-prefix sub-variant (canon §5 R29 Cat-B note):
                    # the infinitival 'to' is mid-line, preceded by other
                    # material on the orphan line. Per §7.3 audit 2026-05-14
                    # this is NOT mechanically decidable to Cat-A confidence
                    # (the leading PP may be a co-orphan dative, a `for`-NP-to-V
                    # infinitival subject, a J5 substantive adjunct, or an EP-1
                    # source-PP — semantic disambiguation). SURFACE as REVIEW
                    # only; NEVER auto-apply. Candidate filter: orphan line has
                    # no finite verb + no correlative lemma.
                    orphan_idx = mark_line - 1
                    orphan_toks = [
                        t for t in sent.tokens
                        if line_map.get((sent.sent_id, t.id)) == mark_line
                    ]
                    if any(t.xpos in FINITE_VERB_XPOS for t in orphan_toks):
                        continue  # line has independent predication — not a bare orphan
                    if any(t.lemma.lower() in CORRELATIVE_LEMMAS for t in orphan_toks):
                        continue  # comparative/result correlative construction
                    if gap != 1:
                        continue  # candidate detector is gap=1 only
                    bucket, reason = "REVIEW-REQUIRED", "co-orphaned-prefix-CatB"
                elif gap == 1 and n_par == 1:
                    bucket, reason = "STRONG-MERGE-CANDIDATE", None
                elif n_par >= 3:
                    bucket, reason = "REVIEW-REQUIRED", "J1-N3-parallel-series"
                elif n_par == 2:
                    bucket, reason = "REVIEW-REQUIRED", "N2-parallel-adjudication"
                else:  # gap > 1, n_par == 1
                    bucket, reason = "REVIEW-REQUIRED", "multi-line-gap"

                violations.append({
                    "book": book_id,
                    "sent_id": sent.sent_id,
                    "gov_form": gov.form,
                    "gov_lemma": gov.lemma,
                    "gov_pos": gov.upos,
                    "gov_line": gov_line,
                    "mark_line": mark_line,
                    "inf_form": inf.form,
                    "deprel": deprel,
                    "gap": gap,
                    "n_parallel": n_par,
                    "bucket": bucket,
                    "review_reason": reason,
                    "v2_path": str(v2_path),
                })
    return violations


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book")
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
        if args.verbose:
            print(f"{bid}: {len(vs)} violations")

    strong = [v for v in all_v if v["bucket"] == "STRONG-MERGE-CANDIDATE"]
    review = [v for v in all_v if v["bucket"] == "REVIEW-REQUIRED"]

    print("=" * 72)
    print("Rule 29 UD-query — Bare Infinitival Orphan Integrity (BofM corpus)")
    print("=" * 72)
    print(f"Books scanned: {len(book_ids)}")
    print(f"STRONG-MERGE-CANDIDATE: {len(strong)}")
    print(f"REVIEW-REQUIRED:        {len(review)}")
    if review:
        from collections import Counter
        by_reason = Counter(v["review_reason"] for v in review)
        for reason, n in sorted(by_reason.items()):
            print(f"    {reason}: {n}")
    print()

    if strong:
        from collections import Counter
        by_pos = Counter(v["gov_pos"] for v in strong)
        print(f"STRONG by governor POS: {dict(by_pos)}")
        print()
        for v in strong[:20]:
            print(f"  [{v['book']}] sent={v['sent_id']} "
                  f"gov={v['gov_form']!r} (lemma={v['gov_lemma']}, {v['gov_pos']}) L{v['gov_line']}"
                  f" / to-{v['inf_form']} L{v['mark_line']}")
        if len(strong) > 20:
            print(f"  ... +{len(strong) - 20} more")

    print(f"\nRESULT: violations={len(all_v)} strong={len(strong)} review={len(review)}")
    sys.exit(1 if all_v else 0)


if __name__ == "__main__":
    main()
