"""
Rule 21 (Participial Absolute Integrity) — UD-query implementation.  Layer 3.

Canon §3 UD signature:
    Subject-bearing participial clause — "X having Y-ed" / "X being Y":
        nsubj(PART_TOK, SUBJ_TOK)   where PART_TOK.feats[VerbForm] == 'Part'
    and the participial's deprel places it in a semi-independent clause
    position (advcl, csubj, parataxis, root — NOT acl/acl:relcl which mark
    relative clauses, and NOT xcomp which marks open complement).

Violation (STRONG-SPLIT-CANDIDATE):
    The participial-absolute clause (SUBJ_TOK + PART_TOK + subtree) shares
    a v2-mine line with a SEPARATE matrix predication.  Detection: the nsubj
    of the participial sits on the same line as a finite VERB that is NOT in
    the participial's subtree.

Why a separate detector from the M3-extension validator:
    M3-extension (validate_participial_phrases.py) targets BARE participials
    WITHOUT their own subject — merge candidates.  This rule targets
    SUBJECT-BEARING participial absolutes that are already own-line or
    should be — split candidates.  The UD signature is the discriminator:
    nsubj present → Rule 21; nsubj absent → M3 extension.

Common BofM patterns:
    "I, Nephi, having been born of goodly parents, therefore I was taught..."
    "Enos, knowing his father had been a just man..."
    "this being the case, they were moved with compassion"
    "And it came to pass, Ammon being the chief spokesman..."

Interaction with M3 canon note:
    "Rule 21 (participial absolute) wins when the participial has its own
    named subject" — M3 extension §1 cross-rule precedence.  This validator
    is the Rule 21 side of that pair.
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

# UD deprels where a participial head can form an absolute clause
# (semi-independent adverbial or clause-initial position).
# Excludes acl/acl:relcl (relative clause modifier) and xcomp (open complement).
ABSOLUTE_DEPRELS = {
    "advcl",       # adverbial clause — canonical participial-absolute position
    "csubj",       # clausal subject
    "parataxis",   # loosely appended clause
    "root",        # sentence root (some BofM parses have non-finite roots)
    "nsubj",       # rare: participial as nominal-clause subject
    "dep",         # catch-all dependency for unclear attachments
}


# Non-finite auxiliary lemmas that mark BofM participial absolutes.
# "having" introduces perfect participials ("having done X");
# "being" introduces present/passive participials ("being a just man").
# These are the canonical forms cited in Rule 21 (canon §5).
NON_FINITE_AUX_LEMMAS = {"have", "be", "do"}
NON_FINITE_AUX_FORMS = {"having", "being"}

# Subordinating conjunction lemmas that introduce FINITE adverbial clauses
# (NOT participial absolutes).
FINITE_SCONJ_LEMMAS = {
    "as", "when", "after", "before", "until", "while", "since",
    "though", "although", "if", "except", "because", "for",
    "whereby", "wherefore", "insomuch", "inasmuch",
}

# Relative pronouns that introduce finite relative clauses (not absolutes)
RELATIVE_PRON_LEMMAS = {"who", "whom", "whose", "which", "what", "whosoever",
                         "whoso", "whatsoever", "that"}


def _has_finite_marker(sent: Sentence, head_tok: Token) -> bool:
    """Return True if the clause headed by head_tok is finite (NOT a participial absolute).

    Finite markers:
    1. SCONJ 'mark' dependent with a finite-subordinator lemma
       ('as/when/after/while/because/...')
    2. Relative-pronoun nsubj (whosoever/whoso/who/which/that) — relative clause
    3. Explicit Mood=Ind on head or its auxiliaries
    4. No non-finite aux ("having"/"being") in its DIRECT children —
       if the clause has neither a non-finite aux NOR a SCONJ marker,
       the clause is ambiguous; we do NOT flag it (conservative: false-negative
       is safer than false-positive for STRONG-SPLIT-CANDIDATE).
    """
    children = sent.dependents_of(head_tok)

    # (1) SCONJ mark → finite subordinate clause
    for c in children:
        if c.deprel == "mark":
            if c.upos == "SCONJ" and c.lemma.lower() in FINITE_SCONJ_LEMMAS:
                return True
            # ADP used as temporal subordinator ('after', 'before' tagged ADP)
            if c.upos in ("ADP", "SCONJ") and c.lemma.lower() in FINITE_SCONJ_LEMMAS:
                return True

    # (2) Relative-pronoun nsubj → relative clause
    for c in children:
        if c.deprel in ("nsubj", "nsubj:pass"):
            if c.upos in ("PRON",) and c.lemma.lower() in RELATIVE_PRON_LEMMAS:
                return True

    # (3) Explicit Mood on head verb
    mood = head_tok.feats.get("Mood", "")
    vf = head_tok.feats.get("VerbForm", "")
    if mood in ("Ind", "Imp", "Sub") or vf == "Fin":
        return True

    # (4) AUX with Mood=Ind (finite aux like "had", "was" in "after X had done")
    for c in children:
        if c.upos == "AUX":
            aux_mood = c.feats.get("Mood", "")
            aux_vf = c.feats.get("VerbForm", "")
            aux_tense = c.feats.get("Tense", "")
            if aux_mood in ("Ind", "Imp", "Sub") or aux_vf == "Fin":
                return True
            # "had/has/have/is/was/were/are" without Mood features but recognizable
            if c.lemma.lower() in ("have", "be") and aux_tense in ("Past", "Pres"):
                return True
            if c.form.lower() in ("had", "has", "was", "were", "is", "are", "am",
                                   "will", "shall", "would", "should", "could",
                                   "might", "must", "can", "did", "does", "do"):
                return True

    # (5) SCONJ mark on head_tok itself — 'that' as purpose/content subordinator
    #     ('that they be not stained', 'that it be buried') is a purpose clause, not absolute
    for c in children:
        if c.deprel == "mark" and c.upos == "SCONJ":
            return True  # any SCONJ mark = finite/subord clause, not participial absolute

    return False


def _has_nonfinite_aux(sent: Sentence, head_tok: Token) -> bool:
    """Return True if the clause has a non-finite auxiliary 'having' or 'being'
    as a direct child — the canonical BofM participial-absolute marker.

    Only these forms reliably mark a participial absolute in BofM prose.
    Absence of this marker means we cannot confidently classify as absolute.
    """
    children = sent.dependents_of(head_tok)
    return any(
        c.upos == "AUX" and c.form.lower() in NON_FINITE_AUX_FORMS
        for c in children
    )


def _is_participial_absolute(sent: Sentence, part_tok: Token) -> bool:
    """Return True if part_tok is a NON-FINITE participial in absolute-clause
    position AND has its own nsubj dependent.

    Strict criteria for BofM:
      • UPOS = VERB
      • deprel in ABSOLUTE_DEPRELS (advcl, csubj, parataxis, ...)
      • has nsubj (or nsubj:pass) dependent
      • has a NON-FINITE auxiliary ('having' / 'being') in direct children
        OR is itself tagged VerbForm=Part
      • does NOT have a finite marker (SCONJ subordinator, relative pronoun,
        finite auxiliary like had/was/were/is/are/did)

    The non-finite-aux requirement is the conservative precision gate:
    it restricts the detector to the canonical "X having Y-ed" and "X being Y"
    forms (Rule 21 explicitly names these), avoiding false positives on
    plain finite adverbial clauses that lack explicit VerbForm tags.
    """
    # Must be a VERB
    if part_tok.upos != "VERB":
        return False

    # Must be in an absolute-clause deprel position (not relative clause)
    if part_tok.deprel not in ABSOLUTE_DEPRELS:
        return False

    # Must have its own nsubj dependent
    children = sent.dependents_of(part_tok)
    has_nsubj = any(c.deprel in ("nsubj", "nsubj:pass") for c in children)
    if not has_nsubj:
        return False

    # Conservative precision gate: require either a non-finite aux OR VerbForm=Part
    # to ensure we are targeting genuine participial absolutes.
    has_nonfinite_aux = _has_nonfinite_aux(sent, part_tok)
    vf = part_tok.feats.get("VerbForm", "")
    is_part = (vf == "Part") or has_nonfinite_aux
    if not is_part:
        return False

    # Must NOT be a finite clause
    if _has_finite_marker(sent, part_tok):
        return False

    return True


def _matrix_finite_verbs_outside_subtree(
    sent: Sentence,
    part_tok: Token,
    subtree_ids: set[int],
    line_map: dict,
    line_of_part: int,
) -> list[Token]:
    """Return finite VERBs on the same v2-mine line as part_tok
    that are NOT inside the participial's subtree."""
    result = []
    for tok in sent.tokens:
        if tok.id in subtree_ids:
            continue
        ln = line_map.get((sent.sent_id, tok.id))
        if ln != line_of_part:
            continue
        if tok.upos != "VERB":
            continue
        # Must be finite (not the participle itself)
        vf = tok.feats.get("VerbForm", "")
        mood = tok.feats.get("Mood", "")
        if vf == "Part" or vf == "Ger":
            continue
        # Plain VERB without explicit VerbForm=Part is treated as finite
        result.append(tok)
    return result


def scan_book(book_id: str, *, verbose: bool = False) -> list[dict]:
    v2_path, conllu_path = book_paths(book_id)
    sentences = load_conllu(conllu_path)
    line_map = build_line_map(v2_path, conllu_path)

    candidates = []
    for sent in sentences:
        for part_tok in sent.tokens:
            if not _is_participial_absolute(sent, part_tok):
                continue

            line_of_part = line_map.get((sent.sent_id, part_tok.id))
            if line_of_part is None:
                continue

            subtree = sent.subtree(part_tok)
            subtree_ids = {t.id for t in subtree}

            # Find the nsubj for display
            nsubj_tok = next(
                (t for t in sent.dependents_of(part_tok) if t.deprel == "nsubj"),
                None,
            )

            # Check whether the participial shares its line with a separate
            # matrix finite predication — that's the violation
            matrix_verbs = _matrix_finite_verbs_outside_subtree(
                sent, part_tok, subtree_ids, line_map, line_of_part
            )

            if not matrix_verbs:
                # Absolute is already own-line; conforming
                continue

            # Determine the matrix verb's line for gap check
            matrix_verb = matrix_verbs[0]
            matrix_line = line_map.get((sent.sent_id, matrix_verb.id))

            subtree_text = " ".join(t.form for t in subtree)[:80]
            nsubj_form = nsubj_tok.form if nsubj_tok else "?"

            candidates.append({
                "book": book_id,
                "sent_id": sent.sent_id,
                "part_id": part_tok.id,
                "part_form": part_tok.form,
                "part_lemma": part_tok.lemma,
                "part_deprel": part_tok.deprel,
                "nsubj_form": nsubj_form,
                "part_line": line_of_part,
                "matrix_verb_form": matrix_verb.form,
                "matrix_verb_lemma": matrix_verb.lemma,
                "matrix_line": matrix_line,
                "subtree_text": subtree_text,
                "v2_path": str(v2_path),
                "bucket": "STRONG-SPLIT-CANDIDATE",
            })

    return candidates


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book", help="single book id (default: all)")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    book_ids = [args.book] if args.book else BOOKS

    all_candidates: list[dict] = []
    for bid in book_ids:
        try:
            vs = scan_book(bid, verbose=args.verbose)
        except FileNotFoundError as e:
            print(f"[skip] {bid}: {e}", file=sys.stderr)
            continue
        all_candidates.extend(vs)
        if args.verbose:
            print(f"{bid}: {len(vs)} split candidates")

    print("=" * 72)
    print("Rule 21 (Participial Absolute Integrity) UD-query — BofM corpus")
    print("=" * 72)
    print(f"Books scanned:          {len(book_ids)}")
    print(f"STRONG-SPLIT-CANDIDATE: {len(all_candidates)}")
    print()

    for v in all_candidates[:30]:
        print(f"  [{v['book']}] sent={v['sent_id']} line {v['part_line']:5d}  "
              f"nsubj={v['nsubj_form']!r} + part={v['part_form']!r} "
              f"(deprel={v['part_deprel']})")
        print(f"      matrix verb: {v['matrix_verb_form']!r} on same line")
        print(f"      subtree: {v['subtree_text']}")

    if len(all_candidates) > 30:
        print(f"  ... +{len(all_candidates) - 30} more")

    sys.exit(1 if all_candidates else 0)


if __name__ == "__main__":
    main()
