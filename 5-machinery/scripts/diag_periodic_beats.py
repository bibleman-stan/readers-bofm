#!/usr/bin/env python3
"""Diagnostic: size the periodic-participial-beat class corpus-wide.

Class A (would SPLIT, currently BIND): a subjectless participial clause-atom
head (aux having/being/been; deprel advcl/conj/parataxis) that bears a LEADING
COORDINATOR (cc and/but/or/nor; adversative-additive advmod
nevertheless/yet/howbeit/notwithstanding; discourse INTJ yea). These open a
new periodic beat -- e.g. 1Ne1:1 favored(and) / had(yea).

Class B (would BIND, currently SPLIT): a FINITE parataxis/conj atom WITH its own
subject whose HEAD is a subjectless participial ground -- e.g. 1Ne1:1
make->had. The finite consequence belongs in the participial ground's beat.

Run: PYTHONIOENCODING=utf-8 PYTHONPATH=../atu-method .venv/Scripts/python.exe 5-machinery/scripts/diag_periodic_beats.py
"""
import sys
import scripts.bofm_generate as G

BOOKS = ['1nephi','2nephi','jacob','enos','jarom','omni','words-of-mormon',
         'mosiah','alma','helaman','3nephi','4nephi','mormon','ether','moroni']

LEAD_CC = {'and','but','or','nor'}
LEAD_ADVMOD = {'nevertheless','yet','howbeit','notwithstanding'}
LEAD_INTJ = {'yea'}
# Periodic participial GROUND signature: the gerund-participle aux 'having'
# ("having been born/seen/had") or 'being' ("being stricken"). NOT bare 'been'
# -- that also heads finite present-perfect passives ("I have been chosen and
# consecrated"), which are gapped coordination and must BIND, not split.
PART_AUX = {'having','being'}


def is_participial(tok, by):
    """Has an aux child in PART_AUX and no own subject."""
    kids = [c for c in by.values() if int(c.head) == int(tok.id)]
    has_part_aux = any(c.deprel.startswith('aux') and c.form.lower() in PART_AUX for c in kids)
    has_subj = any(c.deprel in ('nsubj','nsubj:pass','csubj') for c in kids)
    return has_part_aux and not has_subj


def has_own_subj(tok, by):
    return any(int(c.head) == int(tok.id) and c.deprel in ('nsubj','nsubj:pass','csubj')
               for c in by.values())


def leading_coord(tok, by):
    """Return the leading-coordinator TOKEN if this atom-head bears one, else None."""
    best = None
    for c in by.values():
        if int(c.head) != int(tok.id):
            continue
        f = c.form.lower()
        hit = ((c.deprel == 'cc' and f in LEAD_CC)
               or (c.deprel == 'advmod' and f in LEAD_ADVMOD)
               or (c.deprel == 'discourse' and f in LEAD_INTJ))
        if hit and (best is None or (c.start or 0) < (best.start or 0)):
            best = c
    return best


def line_initial_starts(verse_text, sents, lines):
    """Char-start offset of the first content token of each rendered line."""
    import scripts.bofm_bidir_gate as B
    mapped = B.map_lines_to_tokens(verse_text, sents, lines)
    starts = set()
    for _ln, seg in mapped:
        cs = [t.start for _sx, t in seg if t.start is not None]
        if cs:
            starts.add(min(cs))
    return starts


def main():
    changeA = []   # (book, ch, vs, form, deprel, coord) -- not currently line-initial
    alreadyA = 0   # structural pattern present but already broken there
    classB = []
    for book in BOOKS:
        try:
            p = G.parse_book(book)
            v0 = G.read_v0(book)
        except Exception as e:
            print(f'  !! {book}: {e}', file=sys.stderr); continue
        for (ch, vs), sents in p.items():
            by_all = {}
            for sent in sents:
                for t in sent:
                    if t.upos != 'PUNCT':
                        by_all[int(t.id)] = t
            # candidate atoms in this verse
            candsA, candsB = [], []
            for t in by_all.values():
                if t.deprel not in ('advcl','conj','parataxis'):
                    continue
                coord = leading_coord(t, by_all)
                if is_participial(t, by_all) and coord is not None:
                    candsA.append((t, coord))
                if t.deprel in ('parataxis','conj') and has_own_subj(t, by_all):
                    h = by_all.get(int(t.head))
                    if h is not None and is_participial(h, by_all):
                        candsB.append((t, h))
            if not candsA and not candsB:
                continue
            lines = G.verse_atu_lines(v0[(ch, vs)], sents)
            starts = line_initial_starts(v0[(ch, vs)], sents, lines)
            for t, coord in candsA:
                # would the rule add a break here? only if coord token isn't line-initial
                if coord.start is not None and coord.start in starts:
                    alreadyA += 1
                else:
                    changeA.append((book, ch, vs, t.form, t.deprel, coord.form))
            for t, h in candsB:
                classB.append((book, ch, vs, t.form, t.deprel, h.form))

    print(f'Class A change-set (participial + leading coordinator, NOT already broken): {len(changeA)}')
    print(f'   (+{alreadyA} structural matches already line-initial -> no change)')
    for r in changeA:
        print(f'   {r[0]:<14} {r[1]}:{r[2]:<3} {r[4]:<10} {r[3]:<12} lead={r[5]}')
    print()
    print(f'Class B (finite own-subj atom w/ participial head -> would BIND, now SPLIT): {len(classB)}')
    for r in classB:
        print(f'   {r[0]:<14} {r[1]}:{r[2]:<3} {r[4]:<10} {r[3]:<12} head={r[5]}')


if __name__ == '__main__':
    main()
