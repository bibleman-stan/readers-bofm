"""
Rule 20 (No-Anchor) — UD-query implementation.  Layer 1.

Canon §3 / §5 Rule 20:
    Every independent line must carry a thought-marking anchor:
      • finite VERB (including copular AUX serving as clause head)
      • infinitive (VerbForm=Inf)
      • predicative participle (VerbForm=Part in predicate deprel)
      • independently predicated substantive (NOUN/ADJ/PROPN/PRON with
        a 'cop' dependent on the same line)

Action on violation: MALFORMED — merge or restructure.

Structural-justification exemptions (canon §1, §5 Rule 20 exemption (d)):
    J1 formally-marked parallel-series member — the shared predicate is
       recoverable from the series frame; the line itself need not carry an anchor
    J2 portrait-accumulation stacks — attributive NPs building one image
    J3 vocative-only line — pure address to audience
    J4 classical commata — ≤3 non-PUNCT tokens; brevity = communicative weight
    J5 substantive adjunct — PP or NP filling the slot of a matrix frame

Plus canon-stated non-J exemptions:
    (a) Single-line verses  — whole-verse lines are atomic by definition
    (b) Speech-intro lines  — lines ending with ':' (colon)
    (c) Standalone sentence connectives (*Wherefore, Therefore, And now*, etc.)

Precision approach:
    The BofM corpus has ~28,683 content lines with only ~5 genuine Rule 20
    violations (canon §5 corpus status note).  The structural justifications
    legitimately license a large number of anchor-less lines (participial
    stacks, appositive NPs, PP adjuncts, etc.).

    This detector focuses on lines that:
      (A) contain NO token with UPOS in {VERB, AUX} at all, AND
      (B) the leading token is not a particle/connective/INTJ that signals
          a structurally-justified anchor-less line shape, AND
      (C) the line has >3 non-PUNCT tokens (J4 commata exemption), AND
      (D) does not end with ':' (speech-intro exemption), AND
      (E) the line is not pure PP (ADP-headed structure only — J5 adjunct).

    Lines satisfying A–E with no structural-justification marker are flagged
    MALFORMED.  False-positive bias is avoided over false-negative bias for
    this MALFORMED (hard-fatal) rule.

    Lines that have a VERB/AUX token are by definition anchored (the parse
    may under-assign VerbForm=Part when a word functions finitely; treating
    any VERB or AUX as an anchor is the conservative choice).

Layer:  1 (syntax, hard-fatal)
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

# Leading UPOS tokens that reliably signal a structurally-justified
# anchor-less line:
#   CCONJ  — J1 parallel-series member
#   ADV    — J4 connective / "yea" / "even" / fronted adverbial fragment
#   INTJ   — J4 exclamation / vocative "O" / "Wo"
#   SCONJ  — clause fragment (because/that/if as series member)
#   ADP    — J5 PP adjunct
#   DET    — appositive NP or J1 list object ("all the people of X")
#   PART   — negative particle "not" in series ("yea, even X, yea, not Y")
STRUCTURALLY_JUSTIFIED_LEADING_UPOS = {
    "CCONJ", "ADV", "INTJ", "SCONJ", "ADP", "DET", "PART",
}


# Standalone sentence connectives that pass canon exemption (c).
CONNECTIVE_LEMMAS = {
    "wherefore", "therefore", "nevertheless", "notwithstanding",
    "now", "yea", "behold", "verily", "thus", "hence", "howbeit",
    "whereupon", "wherewith",
}

# UD deprels that signal a participle is in predicate position
PREDICATIVE_PART_DEPRELS = {
    "csubj", "advcl", "xcomp", "acl", "ccomp", "root", "parataxis",
}


def _tokens_by_line(
    sentences: list[Sentence],
    line_map: dict[tuple[str, int], int],
) -> dict[int, list[tuple[Sentence, Token]]]:
    """Return {v2_line_num: [(sent, tok), ...]} in token order."""
    by_line: dict[int, list[tuple[Sentence, Token]]] = {}
    for sent in sentences:
        try:
            sent_id_int = int(sent.sent_id)
        except (ValueError, TypeError):
            sent_id_int = 0
        for tok in sent.tokens:
            ln = line_map.get((sent.sent_id, tok.id))
            if ln is None:
                continue
            by_line.setdefault(ln, []).append((sent_id_int, sent, tok))
    out: dict[int, list[tuple[Sentence, Token]]] = {}
    for ln, lst in by_line.items():
        lst.sort(key=lambda x: (x[0], x[2].id))
        out[ln] = [(s, t) for _, s, t in lst]
    return out


def _v2_content_lines(v2_path: Path) -> list[tuple[int, str]]:
    import re
    verse_re = re.compile(r"^\s*\d+:\d+\s*$")
    out = []
    with open(v2_path, encoding="utf-8") as f:
        for ln, raw in enumerate(f, start=1):
            stripped = raw.rstrip()
            if not stripped.strip():
                continue
            if verse_re.match(stripped):
                continue
            out.append((ln, stripped))
    return out


def _has_verb_or_aux(toks: list[Token]) -> bool:
    """Return True if any token is VERB or AUX — line is anchored."""
    return any(t.upos in ("VERB", "AUX") for t in toks)


def _has_cop_predication(toks: list[Token], pairs: list[tuple[Sentence, Token]]) -> bool:
    """Return True if any NOUN/ADJ/PROPN/PRON token has a 'cop' dependent
    within the same sentence (independently predicated substantive)."""
    for sent, tok in pairs:
        if tok.upos in ("NOUN", "ADJ", "PROPN", "PRON"):
            deps = sent.dependents_of(tok)
            if any(d.deprel == "cop" for d in deps):
                return True
    return False


def scan_book(book_id: str, *, verbose: bool = False) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)
    by_line = _tokens_by_line(sentences, line_map)
    content_lines = _v2_content_lines(v2_path)

    violations = []
    for line_num, line_text in content_lines:
        pairs = by_line.get(line_num)
        if not pairs:
            continue

        toks = [t for _, t in pairs]
        non_punct = [t for t in toks if t.upos != "PUNCT"]

        # J4 exemption: ≤3 non-PUNCT tokens
        if len(non_punct) <= 3:
            continue

        # Exemption (b): speech-intro (ends with colon)
        if line_text.rstrip().endswith(":"):
            continue

        # Exemption (c): only token is a standalone connective
        if len(non_punct) == 1 and non_punct[0].lemma.lower() in CONNECTIVE_LEMMAS:
            continue

        # Leading-UPOS structural-justification exemption:
        # If the first non-PUNCT token's UPOS is in the justified set,
        # the line is almost certainly a structurally-justified anchor-less line
        # (J1/J2/J3/J4/J5). Skip — false negatives here are editorial safety.
        if non_punct and non_punct[0].upos in STRUCTURALLY_JUSTIFIED_LEADING_UPOS:
            continue

        # Primary anchor check: any VERB or AUX token on the line
        if _has_verb_or_aux(toks):
            continue

        # Independently predicated substantive (cop check)
        if _has_cop_predication(toks, pairs):
            continue

        # Remaining lines have NO verbal/copular anchor and a "suspicious"
        # leading token (NOUN, PROPN, ADJ, PRON, NUM).
        # These are the genuine Rule 20 malformation candidates.
        violations.append({
            "book": book_id,
            "line_num": line_num,
            "line_text": line_text,
            "token_count": len(non_punct),
            "upos_list": [t.upos for t in non_punct],
            "lemma_list": [t.lemma for t in non_punct],
        })

    return violations


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book", help="single book id (default: all)")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    book_ids = [args.book] if args.book else BOOKS

    all_violations: list[dict] = []
    for bid in book_ids:
        try:
            vs = scan_book(bid, verbose=args.verbose)
        except FileNotFoundError as e:
            print(f"[skip] {bid}: {e}", file=sys.stderr)
            continue
        all_violations.extend(vs)
        if args.verbose:
            print(f"{bid}: {len(vs)} anchor-less lines (suspicious)")

    print("=" * 72)
    print("Rule 20 (No-Anchor) UD-query — BofM corpus")
    print("=" * 72)
    print(f"Books scanned:   {len(book_ids)}")
    print(f"MALFORMED lines: {len(all_violations)}")
    print()
    print("Note: exemptions applied -- J4 (<=3 tok), leading CCONJ/ADV/INTJ/SCONJ/ADP/DET/PART,")
    print("      speech-intro colons. Remaining items lack any VERB/AUX/cop anchor.")
    print()

    for v in all_violations[:30]:
        upos_str = " ".join(v["upos_list"][:8])
        text_preview = v["line_text"][:80]
        print(f"  [{v['book']}] line {v['line_num']:5d}  toks={v['token_count']:2d}  "
              f"upos=[{upos_str}]")
        print(f"      {text_preview}")
    if len(all_violations) > 30:
        print(f"  ... +{len(all_violations) - 30} more")

    print(f"RESULT: violations={len(all_violations)} malformed={len(all_violations)}")
    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
