#!/usr/bin/env python3
"""Size the bare-present-participle-chain class: coordinator-led present participles
("...and delivering them, and softening the hearts, ...doing all things") that
currently BIND (Class A is scoped to having/being periodic grounds, so these slip
through). The question is whether parallel participial adjuncts are separate beats.
"""
import scripts.bofm_generate as G

BOOKS = ['1nephi', '2nephi', 'jacob', 'enos', 'jarom', 'omni', 'words-of-mormon',
         'mosiah', 'alma', 'helaman', '3nephi', '4nephi', 'mormon', 'ether', 'moroni']


def _i(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def main():
    members = 0
    verses = set()
    examples = []
    for b in BOOKS:
        p = G.parse_book(b)
        for (c, vs), sents in p.items():
            for s in sents:
                by = {_i(t.id): t for t in s if t.upos != 'PUNCT' and _i(t.id) is not None}
                for t in by.values():
                    if (t.deprel or '').split(':')[0] not in ('conj', 'advcl', 'parataxis'):
                        continue
                    if t.upos != 'VERB' or not (t.form or '').lower().endswith('ing'):
                        continue
                    kids = [k for k in by.values() if _i(k.head) == _i(t.id)]
                    has_aux = any((k.deprel or '').startswith('aux')
                                  and (k.form or '').lower() in ('having', 'being') for k in kids)
                    has_subj = any((k.deprel or '').split(':')[0] in ('nsubj', 'csubj') for k in kids)
                    has_cc = any((k.deprel or '') == 'cc' for k in kids)
                    if (not has_aux) and (not has_subj) and has_cc:
                        members += 1
                        verses.add((b, c, vs))
                        if len(examples) < 22:
                            examples.append((b, c, vs, t.form))
    print(f'bare-present-participle conjuncts w/ leading coordinator (currently BIND): {members}')
    print(f'distinct verses: {len(verses)}')
    for r in examples:
        print(f'   {r[0]:<14} {r[1]}:{r[2]:<3} (and ... {r[3]})')


if __name__ == '__main__':
    main()
