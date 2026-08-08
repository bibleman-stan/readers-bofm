"""Audit corpus-wide for the three complement-integrity gaps R17 doesn't cover.

UD signatures:
    [N-INF]  NOUN head + infinitival child (acl/xcomp where child is VERB
             with VerbForm=Inf OR mark "to"), split across v2-mine lines.
    [COMP]   Comparative-degree head (Degree=Cmp OR lemma in
             {more,less,greater,better,rather}) + child whose mark.lemma
             == "than", split across v2-mine lines.
    [RELCL]  NOUN head + acl:relcl child (restrictive relative; UD
             distinguishes acl:relcl from plain acl), split across
             v2-mine lines.

For each match: emit (book, sent_id, head_line, child_line, head_form,
child_form, surface_snippet). Counts per book + corpus total.

Run from repo root:
    py -3 5-machinery/scripts/audit_complement_integrity_gaps.py
"""
from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from validators.parsing.conllu_query import load_conllu, Sentence, Token
from validators.parsing.line_mapping import build_line_map, book_paths

BOOKS = [
    "1nephi", "2nephi", "jacob", "enos", "jarom", "omni",
    "words-of-mormon", "mosiah", "alma", "helaman",
    "3nephi", "4nephi", "mormon", "ether", "moroni",
]

COMP_LEMMAS = {"more", "less", "greater", "better", "rather", "worse"}


def _line_of(line_map: dict, sent: Sentence, tok: Token) -> int | None:
    return line_map.get((sent.sent_id, tok.id))


def _has_feature(tok: Token, feat: str, val: str) -> bool:
    if not tok.feats:
        return False
    parts = tok.feats.split("|") if isinstance(tok.feats, str) else []
    for p in parts:
        if "=" in p:
            k, v = p.split("=", 1)
            if k == feat and v == val:
                return True
    return False


def find_noun_infinitival(sent: Sentence, line_map: dict) -> list[dict]:
    """NOUN head + acl/xcomp child whose subtree is infinitival.

    PUNCT-exclusion fix (2026-05-13, class-fix sweep): UD parsers attach
    head-line-end punctuation to the child verb via `deprel=punct`. That
    punctuation token would sit at head_line, falsely placing the child
    subtree onto head_line and suppressing the legitimate split detection
    (head_line == child_line short-circuit). Excluding PUNCT from the
    subtree-min calculation honors `feedback_punctuation_not_evidence`:
    routing must rest on grammar, not punctuation placement.
    """
    hits = []
    for tok in sent.tokens:
        if tok.upos != "NOUN":
            continue
        for child in sent.dependents_of(tok):
            if child.deprel not in ("acl", "xcomp"):
                continue
            # Child should be a VERB heading an infinitival
            if child.upos != "VERB":
                continue
            # Infinitival = VerbForm=Inf OR has "to" marker
            is_inf = _has_feature(child, "VerbForm", "Inf")
            mark_to = False
            for m in sent.dependents_of(child, deprel="mark"):
                if (m.lemma or m.form).lower() == "to":
                    mark_to = True
                    break
            if not (is_inf or mark_to):
                continue
            head_line = _line_of(line_map, sent, tok)
            # Pick the leftmost non-PUNCT token of the child subtree to
            # determine child_line. PUNCT is post-1830 editorial overlay,
            # not adjudication evidence (per feedback_punctuation_not_evidence).
            subtree = sent.subtree(child)
            child_lines = [_line_of(line_map, sent, t) for t in subtree if t.upos != "PUNCT"]
            child_lines = [l for l in child_lines if l is not None]
            if not child_lines or head_line is None:
                continue
            child_line = min(child_lines)
            if head_line == child_line:
                continue
            hits.append({
                "head_line": head_line, "child_line": child_line,
                "head_lemma": tok.lemma or tok.form,
                "head_form": tok.form, "child_form": child.form,
                "sent_id": sent.sent_id,
            })
    return hits


def find_comparative_tail(sent: Sentence, line_map: dict) -> list[dict]:
    """Comparative head + child with mark.lemma == 'than', split across lines."""
    hits = []
    for tok in sent.tokens:
        is_comp = (
            _has_feature(tok, "Degree", "Cmp")
            or (tok.lemma or tok.form).lower() in COMP_LEMMAS
        )
        if not is_comp:
            continue
        # Look downward for a child whose mark is "than"
        for child in sent.dependents_of(tok):
            mark = sent.mark_of(child)
            if mark is None:
                continue
            if (mark.lemma or mark.form).lower() != "than":
                continue
            head_line = _line_of(line_map, sent, tok)
            mark_line = _line_of(line_map, sent, mark)
            if head_line is None or mark_line is None:
                continue
            if head_line == mark_line:
                continue
            hits.append({
                "head_line": head_line, "child_line": mark_line,
                "head_lemma": (tok.lemma or tok.form).lower(),
                "head_form": tok.form, "child_form": mark.form,
                "sent_id": sent.sent_id,
            })
    return hits


def find_np_relcl(sent: Sentence, line_map: dict) -> list[dict]:
    """NOUN head + acl:relcl child, split across lines.

    PUNCT-exclusion fix (2026-05-12): UD parsers attach the comma at
    head-line-end to the relative's verb as `punct`. That makes the
    relative's subtree include a token at head_line, falsely triggering
    the forward-only filter. Exclude PUNCT tokens from subtree-min.
    """
    hits = []
    for tok in sent.tokens:
        if tok.upos not in ("NOUN", "PROPN"):
            continue
        for child in sent.dependents_of(tok):
            if child.deprel != "acl:relcl":
                continue
            head_line = _line_of(line_map, sent, tok)
            subtree = sent.subtree(child)
            child_lines = [_line_of(line_map, sent, t) for t in subtree if t.upos != "PUNCT"]
            child_lines = [l for l in child_lines if l is not None]
            if not child_lines or head_line is None:
                continue
            child_line = min(child_lines)
            if head_line == child_line:
                continue
            # Skip if a punctuation mark "," directly precedes the relative
            # token on the prior line (non-restrictive heuristic).
            # Better: rely on acl:relcl being restrictive by UD convention.
            hits.append({
                "head_line": head_line, "child_line": child_line,
                "head_lemma": tok.lemma or tok.form,
                "head_form": tok.form, "child_form": child.form,
                "sent_id": sent.sent_id,
                "head_upos": tok.upos,
            })
    return hits


def scan_book(book_id: str):
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)

    out = {"N-INF": [], "COMP": [], "RELCL": []}
    for sent in sentences:
        out["N-INF"] += find_noun_infinitival(sent, line_map)
        out["COMP"] += find_comparative_tail(sent, line_map)
        out["RELCL"] += find_np_relcl(sent, line_map)
    return out


def main():
    grand = {"N-INF": [], "COMP": [], "RELCL": []}
    per_book = {}

    for book in BOOKS:
        try:
            r = scan_book(book)
        except Exception as exc:
            print(f"[err] {book}: {exc}", file=sys.stderr)
            continue
        per_book[book] = {k: len(v) for k, v in r.items()}
        for k in grand:
            for h in r[k]:
                h["book"] = book
                grand[k].append(h)

    # Counts
    print("=" * 72)
    print(f"{'BOOK':18s} | {'N-INF':>6s} | {'COMP':>5s} | {'RELCL':>6s}")
    print("-" * 72)
    totals = Counter()
    for book in BOOKS:
        c = per_book.get(book, {})
        n = c.get("N-INF", 0); cm = c.get("COMP", 0); r = c.get("RELCL", 0)
        totals["N-INF"] += n; totals["COMP"] += cm; totals["RELCL"] += r
        print(f"{book:18s} | {n:>6d} | {cm:>5d} | {r:>6d}")
    print("-" * 72)
    print(f"{'TOTAL':18s} | {totals['N-INF']:>6d} | {totals['COMP']:>5d} | {totals['RELCL']:>6d}")
    print()

    # Top-lemma summary
    for category in ("N-INF", "COMP", "RELCL"):
        lemmas = Counter(h["head_lemma"].lower() for h in grand[category])
        top = lemmas.most_common(8)
        print(f"[{category}] top head-lemmas: {top}")
    print()

    # Sample evidence per category (first 10)
    for category in ("N-INF", "COMP", "RELCL"):
        print(f"--- {category} sample (first 10) ---")
        for h in grand[category][:10]:
            print(f"  {h['book']:14s} sent={h['sent_id']:>4s} "
                  f"head={h['head_form']!r:>16s} (L{h['head_line']}) "
                  f"-> child={h['child_form']!r} (L{h['child_line']}) "
                  f"head_lemma={h['head_lemma']}")
        print()


if __name__ == "__main__":
    main()
