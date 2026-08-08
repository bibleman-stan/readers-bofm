#!/usr/bin/env python3
"""Editorial-review-candidate flag (the participial-density / over-length tripwire).

NOT a binding rule and NOT an auto-edit. It surfaces rendered ATU lines that MIGHT be
over-merged on a thought-unit basis -- specifically lines that pack multiple
subordinate participial elaborations ("...sparing their lives, and delivering them,
and softening the hearts, and doing all things...", Helaman 12:2) -- for the v3
editorial pass to adjudicate as a one-thought-vs-several question.

Why a flag and not a rule: whether such a line is ONE thought (the manner of a single
matrix action) or SEVERAL is a thought-unit judgment no UD feature carries. The
mechanical layer binds the dependent participials (correct by the ATU bar -- they
can't stand alone) and refuses to guess the thought-boundary from a syntactic proxy
(predication / object / count / tense are all clausal-or-poetic, not ATU). This flag
is the bridge: it routes the genuine candidates to a human call, so over-merges
surface instead of hiding, without anything auto-splitting on the wrong grounds.

Run: PYTHONIOENCODING=utf-8 PYTHONPATH=../atu-method .venv/Scripts/python.exe \
        5-machinery/scripts/flag_review_candidates.py [--min-part N] [--min-words N] [--show K]
"""
import sys
import scripts.bofm_generate as G
import scripts.bofm_bidir_gate as B

BOOKS = ['1nephi', '2nephi', 'jacob', 'enos', 'jarom', 'omni', 'words-of-mormon',
         'mosiah', 'alma', 'helaman', '3nephi', '4nephi', 'mormon', 'ether', 'moroni']

CLAUSAL = ('conj', 'advcl', 'parataxis')


def _i(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _participials(seg_toks):
    """Subordinate participial adjuncts bound into this line: a clausal-deprel VERB
    that is a present participle (-ing, lemma != form, excludes base-form 'bring'/
    'sing') OR carries a having/being aux (perfect/passive participle)."""
    by = {_i(t.id): t for _sx, t in seg_toks if _i(t.id) is not None}
    out = []
    for _sx, t in seg_toks:
        if t.upos != 'VERB' or (t.deprel or '').split(':')[0] not in CLAUSAL:
            continue
        form = (t.form or '').lower()
        lemma = (t.lemma or '').lower()
        is_present = form.endswith('ing') and lemma and lemma != form
        has_part_aux = any(_i(c.head) == _i(t.id) and (c.deprel or '').startswith('aux')
                           and (c.form or '').lower() in ('having', 'being')
                           for _s, c in seg_toks)
        if is_present or has_part_aux:
            out.append(form)
    return out


def main():
    args = sys.argv[1:]

    def opt(name, default):
        return int(args[args.index(name) + 1]) if name in args else default
    min_part = opt('--min-part', 2)
    min_words = opt('--min-words', 50)
    show = opt('--show', 40)

    rows = []
    for bk in BOOKS:
        v = G.read_v0(bk)
        p = G.parse_book(bk)
        for key in sorted(v.keys()):
            lines = G.verse_atu_lines(v[key], p[key])
            mapped = B.map_lines_to_tokens(v[key], p[key], lines)
            for ln, seg in mapped:
                words = len((ln or '').split())
                parts = _participials(seg)
                if len(parts) >= min_part or words >= min_words:
                    rows.append((len(parts), words, bk, key[0], key[1], parts, ln))

    rows.sort(key=lambda r: (r[0], r[1]), reverse=True)
    print(f"Editorial-review candidates (>= {min_part} participial members OR >= {min_words} words): {len(rows)}")
    print(f"(diagnostic only -- nothing is edited; for the v3 thought-unit pass)\n")
    for nparts, words, bk, c, vs, parts, ln in rows[:show]:
        print(f"  [{nparts}p {words}w] {bk} {c}:{vs}")
        print(f"      participials: {parts}")
        print(f"      {ln[:140]}")
    if len(rows) > show:
        print(f"\n  ... +{len(rows) - show} more (raise --show to see them)")


if __name__ == "__main__":
    main()
