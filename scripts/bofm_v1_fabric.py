#!/usr/bin/env python3
"""BoFM v1 — OUR FABRIC. Clause-atoms derived from the UD parse (stanza CoNLL-U)
the way sblgnt_v1_fabric does from lowfat: each token attaches to the nearest
ancestor that heads a clause; clause-atoms are emitted in surface order. This is
the English instantiation of the mechanical-first v1 (no foreign-language layer,
no reconciler — the parse is over the display text itself).

A token HEADS a clause when its UD relation to its parent is clause-level:
  root, advcl(:relcl), acl(:relcl), ccomp, csubj(:pass), parataxis, and a
  coordinate (conj) whose head-word is a VERB/AUX (coordinated finite verbs
  split). xcomp (open complement, e.g. "began to teach") BINDS to its governor.

Usage (needs atu-method on PYTHONPATH):
  PYTHONPATH=../atu-method .venv/Scripts/python.exe scripts/bofm_v1_fabric.py 1nephi 0 2
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from atu_method.parsing.conllu_query import load_conllu  # noqa: E402

CONLLU = REPO / "data" / "parses" / "ensemble" / "stanza"

# A clause-atom head is a clause that STANDS as its own ATU. Complements (ccomp:
# "I know that X" — canon R17 complement integrity) and adnominal/relative clauses
# (acl, acl:relcl: "the record which I make" — canon R19) BIND to their governor by
# default, so they are NOT heads here; the canon appliers refine the exceptions
# (recitative/declarative complements split; non-restrictive relatives split).
CLAUSE_RELS = {"root", "advcl", "csubj", "parataxis"}


def _i(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


# advcl marks that introduce a FRAME (temporal/conditional/concessive) — these
# bind to their main clause (incomplete alone, fail the bidirectional test).
# Participial advcls (no mark, "having...") are also frames. Only CAUSAL (because)
# and PURPOSE (to/that) advcls break per canon R6/R7 (and R29 re-binds bare "to").
_FRAME_MARKS = {"when", "before", "after", "while", "whilst", "until", "as",
                "if", "unless", "though", "although", "since", "whereas"}


def is_clause_head(tok, by_id=None):
    base = (tok.deprel or "").split(":")[0]
    # advcl: a frame (temporal/conditional/concessive/participial) BINDS; only a
    # causal/purpose advcl breaks (canon R6/R7). This is the single biggest fix
    # for corpus-wide over-splitting (audit 2026-05-22: ~3k of 6039 advcl splits).
    if base == "advcl" and by_id is not None:
        mk = next((c.form.lower() for c in by_id.values()
                   if _i(c.head) == _i(tok.id) and (c.deprel or "") == "mark"), None)
        return not (mk is None or mk in _FRAME_MARKS)
    # AICTP frame (Hebrew B5 / canon R1): "(it) came to pass [that] X" is a
    # semantically-empty narrative frame — bare "And it came to pass" fails the
    # bidirectional ATU test, so the main clause it introduces (parsed as a
    # parataxis under "came...to pass") BINDS to it as one ATU. The rule-count
    # doesn't reward this (canon gap), but the bidirectional test mandates it.
    if base == "parataxis" and by_id is not None:
        h = by_id.get(_i(tok.head))
        if h is not None and (h.lemma or "").lower() == "come" and any(
                _i(c.head) == _i(h.id) and (c.lemma or "").lower() == "pass"
                and (c.deprel or "").split(":")[0] == "xcomp"
                for c in by_id.values()):
            return False
    if base in CLAUSE_RELS:
        return True
    if base == "conj" and tok.upos in ("VERB", "AUX"):
        # Hebrew B7 (bare wayyiqtol pair / hendiadys): a coordinated verb with NO
        # complements of its own (shares the head's arguments) is a hendiadys-like
        # PAIR -> bind ("saw and heard", "quake and tremble", "heard nor seen"). A
        # conjunct that carries its OWN object/oblique/subject is a distinct
        # predication -> split ("came ... and dwelt upon a rock"). Bareness is the
        # discriminator the canon §3.5.2 M1 test needs, ported from Tanakh B7.
        if by_id is not None:
            # N=2 vs N>=3 cliff (canon §3.5.2): bind ONLY a 2-member pair; an
            # N>=3 polysyndetic chain splits (each member its own beat) even if bare.
            n_conj = sum(1 for c in by_id.values()
                         if _i(c.head) == _i(tok.head)
                         and (c.deprel or "").split(":")[0] == "conj"
                         and c.upos in ("VERB", "AUX"))
            own_args = any(_i(c.head) == _i(tok.id)
                           and (c.deprel or "").split(":")[0] in
                           ("nsubj", "obj", "iobj", "obl", "ccomp", "xcomp", "advcl", "csubj")
                           for c in by_id.values())
            if n_conj == 1 and not own_args:
                return False   # N=2 bare pair (B7 + cliff) -> bind (hendiadys)
        return True            # N>=3 chain, or conjunct with own complement -> split
    # R19 (canon §3): a relative clause SPLITS when CATAPHORIC (head is a forward-
    # pointing PRON/DET — "those who", "whoso", "all which") and BINDS when
    # anaphoric (PROPN head) or ambiguous (NOUN head -> bind by default). So
    # acl:relcl is a clause-head iff its modified head is PRON/DET.
    if (tok.deprel or "") == "acl:relcl" and by_id is not None:
        head = by_id.get(_i(tok.head))
        if head is not None and head.upos in ("PRON", "DET"):
            return True
    return False


def clause_atoms(sent):
    """Return [[tok,...], ...] — tokens grouped by nearest clause-head ancestor,
    clause-atoms in surface order, tokens within each in surface order."""
    by_id = {_i(t.id): t for t in sent.tokens if _i(t.id) is not None}

    def head_of(tok):
        cur, seen = tok, set()
        while cur is not None and _i(cur.id) not in seen:
            seen.add(_i(cur.id))
            if is_clause_head(cur, by_id) or _i(cur.head) in (0, None):
                return _i(cur.id)
            cur = by_id.get(_i(cur.head))
        return _i(tok.id)

    groups = {}
    for t in sent.tokens:
        if _i(t.id) is None:        # skip multiword-token ranges (e.g. "5-6")
            continue
        groups.setdefault(head_of(t), []).append(t)
    atoms = sorted(groups.values(), key=lambda ts: _i(ts[0].id))
    for ts in atoms:
        ts.sort(key=lambda t: _i(t.id))
    return atoms


def _text(ts):
    out = []
    for t in ts:
        out.append(t.form)
    return " ".join(out)


def emit_surface(sent):
    """Surface-ORDER display lines (ported from the GNT engine): a line is a
    maximal run of surface-consecutive tokens sharing one clause-atom id, so the
    rendered text == source order even when a clause is discontinuous. This is
    the PURE-METHOD initial segmentation — derived only from the UD parse, with
    zero dependence on the hand-edited v2-mine breaks."""
    atoms = clause_atoms(sent)
    lid = {}
    for i, ts in enumerate(atoms):
        for t in ts:
            lid[_i(t.id)] = i
    toks = sorted((t for t in sent.tokens if _i(t.id) is not None),
                  key=lambda t: _i(t.id))
    lines, cur, cur_lid = [], [], None
    for t in toks:
        li = lid[_i(t.id)]
        if li != cur_lid and cur:
            lines.append(cur); cur = []
        cur.append(t); cur_lid = li
    if cur:
        lines.append(cur)
    return [_text(ts) for ts in lines]


def main():
    book = sys.argv[1] if len(sys.argv) > 1 else "1nephi"
    lo = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    hi = int(sys.argv[3]) if len(sys.argv) > 3 else lo + 1
    sents = load_conllu(str(CONLLU / f"{book}.conllu"))
    for sid in range(lo, hi):
        if sid >= len(sents):
            break
        sent = sents[sid]
        print(f"=== {book} sent {sid} (surface-order pure-method ATU lines) ===")
        for line in emit_surface(sent):
            print(f"  {line}")
        print()


if __name__ == "__main__":
    main()
