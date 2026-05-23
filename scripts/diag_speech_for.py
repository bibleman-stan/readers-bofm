#!/usr/bin/env python3
"""Diagnostic: size the two Alma-32:5-class mechanical-break mechanisms.

M1 (EME causal 'for'): an advcl whose mark is 'for' (stanza tags causal 'for' as
SCONJ/mark) and that has its OWN SUBJECT -> an independent explanatory clause
(causal coordinator = Hebrew ki), currently BOUND by the marked-advcl rule, should
SPLIT.

M2 (direct-speech ccomp): a ccomp whose head is a verbum dicendi -> quoted discourse,
not an integrated complement. Currently BOUND (R17 complement integrity), should
RELEASE its internal clause-heads. Only counts ccomp that actually CONTAIN internal
clause structure (>=1 conj-VERB / advcl / parataxis descendant) -- a one-clause
quotation is already a single ATU.

Run: PYTHONIOENCODING=utf-8 PYTHONPATH=../atu-method .venv/Scripts/python.exe -m scripts.diag_speech_for
"""
import scripts.bofm_generate as G

BOOKS = ['1nephi','2nephi','jacob','enos','jarom','omni','words-of-mormon',
         'mosiah','alma','helaman','3nephi','4nephi','mormon','ether','moroni']

VERBA_DICENDI = {'say', 'speak', 'cry', 'answer', 'command', 'declare', 'exhort',
                 'ask', 'tell', 'reply', 'utter', 'proclaim', 'preach'}


def _i(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def children(tok, by):
    return [c for c in by.values() if _i(c.head) == _i(tok.id)]


def has_own_subj(tok, by):
    return any((c.deprel or '').split(':')[0] in ('nsubj', 'csubj') for c in children(tok, by))


def for_mark(tok, by):
    return any((c.form or '').lower() == 'for' and ((c.deprel or '') == 'mark' or c.upos == 'SCONJ')
               for c in children(tok, by))


def has_internal_clause(tok, by):
    """Any descendant that would be a clause-head if released (conj-VERB/advcl/parataxis)."""
    for c in by.values():
        # descendant of tok?
        cur, seen, isdesc = c, set(), False
        while cur is not None and _i(cur.id) not in seen:
            seen.add(_i(cur.id))
            if _i(cur.head) == _i(tok.id):
                isdesc = True; break
            cur = by.get(_i(cur.head))
        if not isdesc:
            continue
        base = (c.deprel or '').split(':')[0]
        if base == 'advcl' or base == 'parataxis' or (base == 'conj' and c.upos in ('VERB', 'AUX')):
            return True
    return False


def main():
    m1, m2 = [], []
    for book in BOOKS:
        p = G.parse_book(book)
        for (ch, vs), sents in p.items():
            for sent in sents:
                by = {_i(t.id): t for t in sent if t.upos != 'PUNCT' and _i(t.id) is not None}
                for t in by.values():
                    base = (t.deprel or '').split(':')[0]
                    if base == 'advcl' and for_mark(t, by) and has_own_subj(t, by):
                        m1.append((book, ch, vs, t.form))
                    if base == 'ccomp':
                        h = by.get(_i(t.head))
                        if h is not None and (h.lemma or '').lower() in VERBA_DICENDI \
                           and has_internal_clause(t, by):
                            m2.append((book, ch, vs, t.form, h.form))
    print(f'M1  EME causal-for advcl w/ own subject (currently bound -> should split): {len(m1)}')
    for r in m1[:20]:
        print(f'    {r[0]:<14} {r[1]}:{r[2]:<3} for ... {r[3]}')
    if len(m1) > 20:
        print(f'    ... +{len(m1)-20} more')
    print()
    print(f'M2  speech-verb ccomp w/ internal clauses (currently bound -> should release): {len(m2)}')
    for r in m2[:20]:
        print(f'    {r[0]:<14} {r[1]}:{r[2]:<3} {r[4]}->ccomp({r[3]})')
    if len(m2) > 20:
        print(f'    ... +{len(m2)-20} more')


if __name__ == '__main__':
    main()
