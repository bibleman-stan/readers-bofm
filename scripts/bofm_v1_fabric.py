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

CLAUSE_RELS = {"root", "advcl", "acl", "ccomp", "csubj", "parataxis"}


def _i(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def is_clause_head(tok):
    base = (tok.deprel or "").split(":")[0]
    if base in CLAUSE_RELS:
        return True
    if base == "conj" and tok.upos in ("VERB", "AUX"):
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
            if is_clause_head(cur) or _i(cur.head) in (0, None):
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
