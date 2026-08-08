#!/usr/bin/env python3
"""Stats: AICTP ("(and) it came to pass ...") frame — the "that"-form vs the
"and"-form of the main clause it introduces.

AICTP frame = a verb lemma 'come' with an xcomp 'pass' ("came to pass"). In Hebrew
this is wayhi + temporal frame; the main clause attaches via waw-consecutive (KJV
"and") OR is rendered with "that" -- ONE Hebrew construction, split only by English
translation. So both forms should bind to the frame as one ATU (the frame alone is
semantically empty).

  that-form: main clause is a PARATAXIS child of the frame verb  (currently BINDS, R1/AICTP)
  and-form : main clause is a CONJ (VERB, own subject) child     (currently SPLITS)
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
    that_form = []   # parataxis main clause
    and_form = []    # conj-VERB main clause with own subject
    for b in BOOKS:
        p = G.parse_book(b)
        for (c, vs), sents in p.items():
            for sent in sents:
                by = {_i(t.id): t for t in sent if _i(t.id) is not None}
                # find AICTP frame verbs
                for f in sent:
                    if (f.lemma or "").lower() != "come":
                        continue
                    if not any(_i(x.head) == _i(f.id) and (x.lemma or "").lower() == "pass"
                               and (x.deprel or "").split(":")[0] == "xcomp" for x in by.values()):
                        continue
                    # children of the frame verb
                    for ch in by.values():
                        if _i(ch.head) != _i(f.id):
                            continue
                        base = (ch.deprel or "").split(":")[0]
                        has_subj = any(_i(g.head) == _i(ch.id)
                                       and (g.deprel or "").split(":")[0] in ("nsubj", "csubj")
                                       for g in by.values())
                        if base == "parataxis":
                            that_form.append((b, c, vs))
                        elif base == "conj" and ch.upos in ("VERB", "AUX") and has_subj:
                            and_form.append((b, c, vs, ch.form))
    print(f'AICTP "that"-form (parataxis main clause, currently BINDS): {len(that_form)}')
    print(f'AICTP "and"-form  (conj main clause w/ own subject, currently SPLITS): {len(and_form)}')
    print()
    print('and-form examples (currently split off from the empty frame):')
    seen = set()
    for b, c, vs, form in and_form:
        if (b, c, vs) in seen:
            continue
        seen.add((b, c, vs))
        if len(seen) <= 20:
            print(f'   {b:<14} {c}:{vs:<3} (and ... {form})')
    print(f'   ... ({len(seen)} distinct verses)')


if __name__ == "__main__":
    main()
