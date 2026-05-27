#!/usr/bin/env python3
"""Apply the Isaiah-inheritance GOLD segmentation to the deployed BoFM-Isaiah verses.

For each high-confidence BoFM-Isaiah verse (text matches the inherited gold), RE-BREAK
the EXISTING v2 verse text at the gold break positions. Text-preserving: the sacred BoFM
words/punctuation are untouched; only line-breaks move (to the BHSA-anchored gold). This
takes the ~25 quoted Isaiah chapters from fabric F1 0.561 toward gold.

DRY-RUN by default (prints before/after + artifact report). `--apply` writes the v2 files
(after backing up to research/isaiah-gold/backup/). Reversible.

Usage: PYTHONIOENCODING=utf-8 python scripts/apply_isaiah_gold.py [--apply]
"""
import re
import sys
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import isaiah_oracle as O

REPO = Path(__file__).resolve().parent.parent
BACKUP = REPO / "research" / "isaiah-gold" / "backup"


def _words(t):
    return [w for w in re.split(r"\s+", t.strip()) if w]


_LINE_FINAL_FORBID = {"and", "or", "but", "nor", "for", "the", "a", "an"}


def _reconcile_line_final(lines):
    """HYBRID polish: keep gold idea-unit breaks but respect the BoFM canon Rule-9
    line-final discipline — a line must not END on a coordinating conjunction or article
    (BoFM leads with the connective). Slide any stranded line-final forbidden token to the
    START of the next line. Lexical (no parse needed); covers the CCONJ/article cases."""
    out = [list(_words(l)) for l in lines]
    changed = True
    while changed:
        changed = False
        for i in range(len(out) - 1):
            if out[i] and re.sub(r"\W+$", "", out[i][-1].lower()) in _LINE_FINAL_FORBID:
                tok = out[i].pop()
                out[i + 1].insert(0, tok)
                changed = True
    return [" ".join(w) for w in out if w]


def _rebreak(v2_lines, gold_lines):
    """Re-break the v2 verse text at the gold break positions. Returns (new_lines, ok,
    artifact). Text-preserving: regroups the v2 whitespace-words at gold word-boundaries."""
    v2w = _words(" ".join(v2_lines))
    gw_per_line = [len(_words(l)) for l in gold_lines]
    if sum(gw_per_line) != len(v2w):
        return None, False, None
    # break positions (cumulative word counts, internal only)
    breaks, n = [], 0
    for c in gw_per_line[:-1]:
        n += c; breaks.append(n)
    # artifact check: a break adjacent to an em-dash-glued token (e.g. "eyes--lest")
    artifact = any("--" in v2w[b - 1] or (b < len(v2w) and "--" in v2w[b]) for b in breaks)
    out, start = [], 0
    for b in breaks + [len(v2w)]:
        out.append(" ".join(v2w[start:b])); start = b
    if "--no-reconcile" not in sys.argv:
        out = _reconcile_line_final(out)
    return out, True, artifact


def run(apply=False):
    inh, _ = O.build()
    changes = []   # (book, ch, v, old_lines, new_lines, artifact)
    skip_textmismatch = skip_nochange = 0
    for (book, ch, v), gold in sorted(inh.items()):
        dep = O.deployed_lines(book, ch, v)
        if not dep:
            continue
        new, ok, artifact = _rebreak(dep, gold)
        if not ok:
            skip_textmismatch += 1
            continue
        if new == dep:
            skip_nochange += 1
            continue
        changes.append((book, ch, v, dep, new, artifact))
    arts = [c for c in changes if c[5]]
    print(f"Isaiah-gold deploy DRY-RUN: {len(changes)} verses would re-break "
          f"({len(arts)} with em-dash artifact); skipped {skip_textmismatch} text-mismatch, "
          f"{skip_nochange} already-gold.")
    print("\n=== sample before/after (first 3 clean) ===")
    for book, ch, v, old, new, art in [c for c in changes if not c[5]][:3]:
        print(f"\n  {book} {ch}:{v}")
        print("   BEFORE:");  [print("     |", l) for l in old]
        print("   AFTER (gold):"); [print("     |", l) for l in new]
    if arts:
        print("\n=== em-dash-artifact verses (held back from --apply) ===")
        for book, ch, v, old, new, art in arts[:6]:
            print(f"  {book} {ch}:{v}  e.g. -> {' | '.join(new)[:90]}")
    if apply:
        BACKUP.mkdir(parents=True, exist_ok=True)
        # group clean (non-artifact) changes by file
        byfile = {}
        for book, ch, v, old, new, art in changes:
            if art:
                continue   # hold artifact verses for manual review
            byfile.setdefault(O.V2FILE[book], {})[(ch, v)] = new
        for f, vmap in byfile.items():
            shutil.copy2(f, BACKUP / f.name)
            _rewrite_verses(f, vmap)
        print(f"\nAPPLIED to {len(byfile)} files ({sum(len(m) for m in byfile.values())} "
              f"clean verses); backups in {BACKUP}. Artifact verses left unchanged.")


def _rewrite_verses(f, vmap):
    """Rewrite file f, replacing the lines of verses in vmap with their new line lists."""
    out, cur_key, buf_replaced = [], None, False
    lines = f.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        s = lines[i]
        m = re.fullmatch(r"(\d+):(\d+)", s.strip())
        if m:
            cur_key = (int(m.group(1)), int(m.group(2)))
            out.append(s)
            if cur_key in vmap:
                i += 1
                # consume old content lines (until next marker or blank-then-marker)
                old_block = []
                while i < len(lines) and not re.fullmatch(r"\d+:\d+", lines[i].strip()):
                    old_block.append(lines[i]); i += 1
                # preserve a trailing blank line if the old block ended with one
                trailing_blank = old_block and old_block[-1].strip() == ""
                out.extend(vmap[cur_key])
                if trailing_blank:
                    out.append("")
                continue
        else:
            out.append(s)
        i += 1
    f.write_text("\n".join(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    run(apply="--apply" in sys.argv)
