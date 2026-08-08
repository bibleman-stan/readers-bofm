#!/usr/bin/env python3
"""Quality meter — the 'measurably better' gate for an autonomous v2 deploy.

The canon validators catch canon-conformance but NOT over-merge, and the bidir gate is
Stanza-circular. So before deploying a re-segmented corpus we need an INDEPENDENT defect-delta:
diff a candidate v2 against a baseline, isolate the verses whose ATU segmentation CHANGED
(text-identical, only breaks move = parity-safe), and emit a package for LLM-adjudication
(verse + old vs new segmentation + the bidirectional-test criteria). `tally()` then consumes
per-change verdicts (improvement | regression | neutral) → net + by-genre, so the deploy gate
is "candidate measurably BEATS baseline" — never merely "candidate is different".

Usage:
  python3 quality_meter.py --candidate <v2dir> --baseline <v2dir|git:HEAD> [--out package.json]
  (then an LLM-adjudication agent classifies package.json; feed verdicts back to tally().)
"""
import argparse, json, re, sys, glob, os
from pathlib import Path

V2_DEFAULT = Path(__file__).resolve().parent.parent.parent / "data" / "text-files" / "v2"
_REF = re.compile(r"^\d+:\d+$")

# coarse genre buckets by book id (for by-genre defect deltas)
GENRE = {"1nephi":"narrative","2nephi":"doctrinal","jacob":"sermon","enos":"narrative",
         "mosiah":"narrative","alma":"narrative","helaman":"narrative","3nephi":"mixed",
         "4nephi":"narrative","mormon":"narrative","ether":"narrative","moroni":"sermon"}


def _bookid(fname):
    # 09-alma-2020-sb-v2.txt -> alma ; 01-1_nephi-... -> 1nephi
    stem = os.path.basename(fname).split("-2020-sb")[0]
    return stem.split("-", 1)[1].replace("_", "") if "-" in stem else stem


def load_corpus(d):
    """{(bookid, 'c:v'): [lines]} for every verse in a v2 dir."""
    out = {}
    for f in glob.glob(str(Path(d) / "*-v2.txt")) or glob.glob(str(Path(d) / "*.txt")):
        bk = _bookid(f); cur = None
        for ln in open(f, encoding="utf-8"):
            s = ln.rstrip("\n").strip()
            if _REF.match(s):
                cur = (bk, s); out[cur] = []
            elif cur and s:
                out[cur].append(s)
    return out


def _alnum(lines):
    return re.sub(r"[^a-z0-9]", "", " ".join(lines).lower())


def changed_verses(candidate, baseline):
    """[{ref, genre, old, new}] for verses whose segmentation differs. Asserts text-identical
    (parity) on every change — a non-parity change is a BUG, reported as such, not a quality delta."""
    cand, base = load_corpus(candidate), load_corpus(baseline)
    changes, parity_violations = [], []
    for key in sorted(set(cand) & set(base)):
        if cand[key] == base[key]:
            continue
        if _alnum(cand[key]) != _alnum(base[key]):
            parity_violations.append(key); continue
        bk, cv = key
        changes.append({"ref": f"{bk} {cv}", "genre": GENRE.get(bk, "other"),
                        "old": base[key], "new": cand[key]})
    return changes, parity_violations


def tally(verdicts):
    """verdicts: {ref: 'improvement'|'regression'|'neutral'}. Returns the deploy-gate summary."""
    from collections import Counter
    c = Counter(verdicts.values())
    net = c["improvement"] - c["regression"]
    return {"improvement": c["improvement"], "regression": c["regression"],
            "neutral": c["neutral"], "net": net,
            "VERDICT": "DEPLOY" if (net > 0 and c["regression"] == 0) else "HOLD"}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", default=str(V2_DEFAULT))
    ap.add_argument("--baseline", required=True, help="a v2 dir (git:HEAD not yet supported)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    changes, parity = changed_verses(a.candidate, a.baseline)
    print(f"changed verses: {len(changes)} | parity violations (MUST be 0): {len(parity)}")
    if parity:
        print("  !! PARITY VIOLATIONS:", parity)
    from collections import Counter
    print("  by genre:", dict(Counter(ch["genre"] for ch in changes)))
    for ch in changes[:8]:
        print(f"  - {ch['ref']} [{ch['genre']}]: {len(ch['old'])} -> {len(ch['new'])} lines")
    if a.out:
        Path(a.out).write_text(json.dumps(changes, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"wrote adjudication package -> {a.out}")
