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
# Subordinators stanza often tags as advmod (ADV) rather than `mark`, esp. fronted
# temporal/relative adverbs — used to recognize a subordinated advcl by lemma.
_SUBORD_ADV = {"when", "after", "before", "while", "whilst", "until", "since",
               "whereas", "where", "whensoever", "whithersoever", "wherein"}


def is_clause_head(tok, by_id=None):
    base = (tok.deprel or "").split(":")[0]
    # advcl: a MARKED adverbial clause is subordinate and cannot stand alone, so it
    # BINDS -- this holds for every mark, not just temporal/conditional frames:
    # causal "because", purpose/result "that"/"so"/"insomuch", concessive
    # "though", temporal "when/after/while". The prior R6/R7 causal/purpose BREAK
    # manufactured the stranded "because thou art merciful," / "that they might
    # take it away" fragments the bidirectional audit flagged (338 "that" + 70
    # "because"). An UNMARKED advcl splits ONLY if it is a finite clause with its
    # OWN subject (an asyndetic parallel colon, e.g. Hebrew-poetry "the Lord shall
    # comfort Zion // he will comfort her waste places"); a subjectless unmarked
    # advcl is participial ("having seen many afflictions") -> bind.
    if base == "advcl" and by_id is not None:
        # A clause is subordinated if it carries a subordinator. stanza tags these
        # inconsistently -- "because"/"that"/"if" as `mark`, but fronted temporal
        # "when"/"after"/"before" often as `advmod` (ADV) -- so detect by deprel
        # OR by subordinator lemma, not by `mark` alone (else "And when the Jews
        # heard these things" splits as a fronted-frame fragment).
        subordinated = any(
            _i(c.head) == _i(tok.id) and (
                (c.deprel or "") == "mark"
                or c.upos == "SCONJ"
                or ((c.deprel or "").split(":")[0] == "advmod"
                    and (c.lemma or c.form or "").lower() in _SUBORD_ADV))
            for c in by_id.values())
        if subordinated:
            return False   # marked/subordinated clause -> bind
        own_subj = any(_i(c.head) == _i(tok.id)
                       and (c.deprel or "").split(":")[0] in ("nsubj", "csubj")
                       for c in by_id.values())
        return own_subj    # unmarked: finite parallel colon splits, participial binds
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
        # Coordinate finite verbs: a conjunct BINDS iff it has NO SUBJECT of its
        # own. A subjectless conjunct shares (gaps) the head's subject — it is a
        # subjectless predicate that cannot stand alone as one thought ("and heard
        # much", "and dwelt upon a rock", "and stoned, and slain", "and spake unto
        # his children"), so it must bind regardless of what objects/obliques it
        # carries or how long the chain is. A conjunct with its OWN overt subject
        # is an independent predication ("he came, and they departed") -> split.
        #
        # This is the EARNED port of Hebrew B7: B7 binds on incompleteness/bareness
        # of the member, NOT on count. Hebrew has no N>=3 cliff — wayyiqtol chains
        # split per COMPLETE predication. The BoFM §3.5.2 count cliff (N=2 binds /
        # N>=3 splits) and the own_args gate were unvalidated proxies that the
        # 5-genre bidirectional audit + the Hebrew mechanism both falsify (they
        # manufactured bare-fragment lines). Discriminator = own-subject, ported
        # from B7 bareness + R12 shared-ellipsis. Errs toward bind (safer).
        if by_id is not None:
            own_subj = any(_i(c.head) == _i(tok.id)
                           and (c.deprel or "").split(":")[0] in ("nsubj", "csubj")
                           for c in by_id.values())
            if not own_subj:
                return False   # subjectless conjunct (gapped subject) -> bind
        return True            # own overt subject -> independent predication -> split
    # Relative clause (acl:relcl) always BINDS to its antecedent. A relativizer-
    # headed clause ("whom he hath chosen", "which I make", "that follow after
    # righteousness") opens with a relative pronoun bound to its antecedent and
    # CANNOT stand alone (fails the bidirectional forward test) -- this holds for
    # restrictive AND non-restrictive relatives alike (", who were a stiffnecked
    # people" is just as much a relativizer fragment). Hebrew B3 / Greek
    # restrictive-ὅς converge here. The prior R19 cataphoric exception (split when
    # the antecedent is PRON/DET, "those whom...") manufactured the 921 stranded-
    # relative fragments the audit flagged, so it is retired. acl:relcl is never a
    # clause-head; it falls through to bind.
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
