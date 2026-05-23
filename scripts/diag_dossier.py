#!/usr/bin/env python3
"""Reusable before/after audit-dossier generator.

Usage:
  # render the CURRENT working-tree segmentation to a file:
  ... python -m scripts.diag_dossier render <out.txt>
  # merge a BEFORE + AFTER render into a side-by-side audit file:
  ... python -m scripts.diag_dossier merge <before.txt> <after.txt> <out.txt>

REF list = the genre-spread audit sample (edit REFS to retarget). Workflow:
  render after.txt ; git stash ; render before.txt ; git stash pop ; merge ...
"""
import re
import sys
import scripts.bofm_generate as G

def _build_refs(per_book=4):
    """Genre/book-spread sample of M1 (for-causal) + M2 (direct-speech) candidates,
    capped per book, so the dossier's changed-set is rich enough to audit."""
    from scripts.diag_speech_for import (BOOKS, for_mark, has_own_subj, _i,
                                         has_internal_clause, VERBA_DICENDI)
    refs = [('alma', 32, 5)]  # the showcase target always first
    for book in BOOKS:
        m1n = m2n = 0
        p = G.parse_book(book)
        for (ch, vs) in sorted(p.keys()):
            for sent in p[(ch, vs)]:
                by = {_i(t.id): t for t in sent if t.upos != 'PUNCT' and _i(t.id) is not None}
                for t in by.values():
                    base = (t.deprel or '').split(':')[0]
                    if m1n < per_book and base == 'advcl' and for_mark(t, by) and has_own_subj(t, by):
                        if (book, ch, vs) not in refs:
                            refs.append((book, ch, vs)); m1n += 1
                    if m2n < per_book and base == 'ccomp':
                        h = by.get(_i(t.head))
                        if h is not None and (h.lemma or '').lower() in VERBA_DICENDI and has_internal_clause(t, by):
                            if (book, ch, vs) not in refs:
                                refs.append((book, ch, vs)); m2n += 1
    return refs


REFS = _build_refs()


def render(out_path):
    cache = {}
    with open(out_path, 'w', encoding='utf-8') as f:
        for bk, ch, vs in REFS:
            if bk not in cache:
                cache[bk] = (G.read_v0(bk), G.parse_book(bk))
            v, p = cache[bk]
            key = (ch, vs)
            f.write(f'### {bk} {ch}:{vs}\n')
            if key not in v:
                f.write('  | NOT FOUND\n\n'); continue
            for ln in G.verse_atu_lines(v[key], p[key]):
                f.write('  | ' + ln + '\n')
            f.write('\n')


def _parse(fn):
    blocks, cur = {}, None
    for line in open(fn, encoding='utf-8'):
        m = re.match(r'### (.+)', line)
        if m:
            cur = m.group(1).strip(); blocks[cur] = []
        elif cur and line.strip().startswith('|'):
            blocks[cur].append(line.rstrip('\n'))
    return blocks


def merge(before_fn, after_fn, out_fn):
    b, a = _parse(before_fn), _parse(after_fn)
    out, changed = [], 0
    for r in b:
        ch = b[r] != a.get(r, [])
        changed += ch
        out.append(f'### {r}')
        out.append(f'  BEFORE ({len(b[r])} ATUs):')
        out += ['  ' + l for l in b[r]]
        out.append(f'  AFTER ({len(a.get(r, []))} ATUs)' + ('  <-- CHANGED' if ch else '  (no change)') + ':')
        out += ['  ' + l for l in a.get(r, [])]
        out.append('')
    with open(out_fn, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
    print(f'{len(b)} verses; changed={changed} -> {out_fn}')


if __name__ == '__main__':
    if sys.argv[1] == 'render':
        render(sys.argv[2])
    elif sys.argv[1] == 'merge':
        merge(sys.argv[2], sys.argv[3], sys.argv[4])
