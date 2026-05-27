#!/usr/bin/env python3
"""Isaiah-inheritance GOLD ORACLE for the BoFM reader.

The BoFM quotes ~25 Isaiah chapters. tanakh-reader has BHSA-anchored (gold) ATU
segmentation of KJV-Isaiah; readers-bofm has data/kjv_diff_index.json mapping each
BoFM-Isaiah verse -> its KJV-Isaiah ref + a word-level diff (equal/insert/delete,
transforming KJV-text INTO BoFM-text). We PROJECT the gold KJV-Isaiah ATU line-breaks
through the diff onto the BoFM wording -> a gold ATU segmentation for the BoFM-Isaiah
verses, inherited (not parsed). This is both (a) gold structure for those chapters and
(b) a yardstick: compare the deployed v2 BoFM segmentation against it to measure the
fabric's break quality on gold.

Usage: PYTHONIOENCODING=utf-8 python scripts/isaiah_oracle.py [--write] [--measure]
"""
import json
import re
import sys
import collections
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KJV_DIFF = REPO / "data" / "kjv_diff_index.json"
TANAKH_ISA = Path(r"C:\Users\bibleman\repos\readers-tanakh\data\text-files\v2\eng-kjv\23-isaiah")
V2 = REPO / "data" / "text-files" / "v2"
OUT = REPO / "research" / "isaiah-gold"

# bookname (kjv_diff key, e.g. "2nephi") -> v2 file ("02-2_nephi-2020-sb-v2.txt")
V2FILE = {b.name.split("-")[1].replace("_", ""): b for b in V2.glob("*-v2.txt")}


def _norm(w):
    """match key: lowercase, strip surrounding punctuation (keep internal apostrophe)."""
    return re.sub(r"^\W+|\W+$", "", w.lower())


def _words(text):
    return [w for w in re.split(r"\s+", text.strip()) if w]


def gold_isa_lines(kjv_ref):
    """Return the gold KJV-Isaiah ATU lines (list of str) for e.g. 'Isa 2:2'."""
    m = re.match(r"Isa\w*\s+(\d+):(\d+)", kjv_ref)
    if not m:
        return None
    ch, v = int(m.group(1)), int(m.group(2))
    f = TANAKH_ISA / f"isaiah-{ch:02d}.txt"
    if not f.exists():
        return None
    lines, cur, grab = f.read_text(encoding="utf-8").splitlines(), [], False
    for ln in lines:
        s = ln.rstrip()
        if re.fullmatch(r"\d+:\d+", s.strip()):
            if grab:
                break
            grab = (s.strip() == f"{ch}:{v}")
            continue
        if grab and s.strip():
            cur.append(s.strip())
    return cur or None


def project(diff, gold_lines):
    """Project gold KJV ATU line-breaks onto the BoFM wording via the diff.
    Returns (bofm_lines, ok): bofm_lines = inherited ATU lines; ok=alignment succeeded."""
    # gold KJV words with their ATU-line id
    gold_w = [(w, lid) for lid, ln in enumerate(gold_lines) for w in _words(ln)]
    gp = 0
    out_words = []   # (bofm_word, line_id)
    cur_lid = 0
    for seg in diff:
        typ, segwords = seg["type"], _words(seg["text"])
        if typ == "equal":
            for w in segwords:
                if gp < len(gold_w) and _norm(w) == _norm(gold_w[gp][0]):
                    cur_lid = gold_w[gp][1]; gp += 1
                else:  # tolerant resync: scan ahead a few for a match
                    for k in range(gp, min(gp + 4, len(gold_w))):
                        if _norm(w) == _norm(gold_w[k][0]):
                            cur_lid = gold_w[k][1]; gp = k + 1; break
                out_words.append((w, cur_lid))
        elif typ == "delete":   # KJV-only: advance gold pointer, no BoFM word
            for w in segwords:
                if gp < len(gold_w) and _norm(w) == _norm(gold_w[gp][0]):
                    cur_lid = gold_w[gp][1]; gp += 1
        elif typ == "insert":   # BoFM-only: ride the current line
            for w in segwords:
                out_words.append((w, cur_lid))
    if not out_words:
        return None, False
    # group consecutive words by line id
    bofm_lines, buf, last = [], [], out_words[0][1]
    for w, lid in out_words:
        if lid != last and buf:
            bofm_lines.append(" ".join(buf)); buf = []
        buf.append(w); last = lid
    if buf:
        bofm_lines.append(" ".join(buf))
    ok = gp >= len(gold_w) - 2   # consumed (nearly) all gold words = aligned
    return bofm_lines, ok


def build():
    d = json.load(open(KJV_DIFF, encoding="utf-8"))
    inherited = {}   # (book, chap, verse) -> bofm gold lines
    stats = collections.Counter()
    for book, chaps in d.items():
        for ch, verses in chaps.items():
            for v, info in verses.items():
                ref = info.get("kjv_ref", "")
                if "Isa" not in ref:
                    continue
                stats["isa_verses"] += 1
                gl = gold_isa_lines(ref)
                if not gl:
                    stats["no_gold"] += 1; continue
                lines, ok = project(info["diff"], gl)
                if lines and ok:
                    inherited[(book, int(ch), int(v))] = lines
                    stats["projected_ok"] += 1
                else:
                    stats["align_fail"] += 1
    return inherited, stats


def deployed_lines(book, chap, verse):
    """Current v2 BoFM ATU lines for a verse."""
    f = V2FILE.get(book)
    if not f or not f.exists():
        return None
    cur, grab = [], False
    for ln in f.read_text(encoding="utf-8").splitlines():
        s = ln.rstrip()
        if re.fullmatch(r"\d+:\d+", s.strip()):
            if grab:
                break
            grab = (s.strip() == f"{chap}:{verse}")
            continue
        if grab and s.strip():
            cur.append(s.strip())
    return cur or None


def _breakset(lines):
    """Set of break positions = cumulative word counts at each internal line end."""
    pos, breaks, n = [], set(), 0
    for ln in lines:
        n += len(_words(ln)); breaks.add(n)
    breaks.discard(n)   # final end is not an internal break
    return breaks


def measure(inherited):
    tp = fp = fn = verses = 0
    worst = []
    for (book, ch, v), gold in inherited.items():
        dep = deployed_lines(book, ch, v)
        if not dep:
            continue
        # only compare when word counts match (same text) — else skip (text mismatch)
        if sum(len(_words(l)) for l in gold) != sum(len(_words(l)) for l in dep):
            continue
        verses += 1
        gb, db = _breakset(gold), _breakset(dep)
        tp += len(gb & db); fp += len(db - gb); fn += len(gb - db)
        if gb != db:
            worst.append((book, ch, v, len(gb - db), len(db - gb)))
    prec = tp / (tp + fp) if tp + fp else 0
    rec = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0
    return dict(verses=verses, tp=tp, fp=fp, fn=fn, precision=prec, recall=rec, f1=f1), worst


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    inh, stats = build()
    print("BUILD:", dict(stats))
    if "--write" in sys.argv:
        OUT.mkdir(parents=True, exist_ok=True)
        by_book = collections.defaultdict(dict)
        for (b, c, v), lines in inh.items():
            by_book[b][f"{c}:{v}"] = lines
        for b, vmap in by_book.items():
            (OUT / f"{b}-isaiah-gold.json").write_text(
                json.dumps(vmap, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"wrote {len(by_book)} books to {OUT}")
    if "--measure" in sys.argv:
        m, worst = measure(inh)
        print("\nMEASURE (deployed v2 BoFM-Isaiah vs inherited gold):")
        print(f"  verses compared: {m['verses']}")
        print(f"  break precision={m['precision']:.3f} recall={m['recall']:.3f} F1={m['f1']:.3f}")
        print(f"  (tp={m['tp']} fp={m['fp']} fn={m['fn']}; fp=fabric over-split, fn=fabric over-merge)")
        worst.sort(key=lambda x: x[3] + x[4], reverse=True)
        print("  worst verses (book ch:v  missed-breaks/extra-breaks):")
        for b, c, v, miss, extra in worst[:12]:
            print(f"    {b} {c}:{v}  fn={miss} fp={extra}")
