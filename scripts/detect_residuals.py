#!/usr/bin/env python3
"""Flag verses whose MECHANICAL ATU output carries a genuine fragment -- the
parse-substrate residual that the binding rules can't fix because the parse itself
is garbled (subject severed from predicate, verbless quote, stranded relative). These
are the targets for the v2 LLM-adjudication layer (data/text-files/v2-adjudicated/).

It deliberately does NOT flag the gate's false-positive-prone classes
(stranded-coordinate / over-merge-multi-clause), which fire on legitimate
coordinator-led beats and AICTP binds. It flags the GENUINE-fragment classes
(mid-phrase-fracture, verbless-fragment, infinitive/participial-orphan,
stranded-relative, stranded-subordinate) -- a line that is not a complete thought
because the parse mis-segmented it.

Run: PYTHONIOENCODING=utf-8 PYTHONPATH=../atu-method .venv/Scripts/python.exe -m scripts.detect_residuals [--json out.json]
"""
import json
import sys
import scripts.bofm_generate as G
import scripts.bofm_bidir_gate as B

BOOKS = ['1nephi', '2nephi', 'jacob', 'enos', 'jarom', 'omni', 'words-of-mormon',
         'mosiah', 'alma', 'helaman', '3nephi', '4nephi', 'mormon', 'ether', 'moroni']

# genuine-fragment classes (a line that isn't a complete thought) -- adjudicate.
# EXCLUDED: stranded-coordinate, over-merge-multi-clause (detector false positives on
# legitimate coordinator-led beats / AICTP binds; not parse garble).
FRAGMENT_CLASSES = {
    "mid-phrase-fracture", "verbless-fragment", "infinitive-orphan",
    "participial-orphan", "stranded-relative", "stranded-subordinate",
}


def main():
    flagged = {}   # "book c:v" -> {classes, lines}
    for b in BOOKS:
        v = G.read_v0(b)
        p = G.parse_book(b)
        for key in sorted(v.keys()):
            lines = G.deployed_atu_lines(b, key[0], key[1], v[key], p[key])
            rows = B.map_lines_to_tokens(v[key], p[key], lines)
            classes = [cl for cl in B.classify(rows) if cl in FRAGMENT_CLASSES]
            if classes:
                flagged[f"{b} {key[0]}:{key[1]}"] = {
                    "classes": sorted(set(classes)),
                    "verse": v[key],
                    "current": lines,
                }

    print(f"Residual verses flagged for adjudication: {len(flagged)}")
    from collections import Counter
    cc = Counter(c for f in flagged.values() for c in f["classes"])
    for cl, n in cc.most_common():
        print(f"   {cl:<24} {n}")

    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(flagged, fh, indent=1, ensure_ascii=False)
        print(f"\nwrote {out}")
    else:
        print("\nfirst 15:")
        for ref in list(flagged)[:15]:
            print(f"   {ref}  {flagged[ref]['classes']}")


if __name__ == "__main__":
    main()
