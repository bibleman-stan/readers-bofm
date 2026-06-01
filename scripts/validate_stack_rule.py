"""Validate the §2.2 parallel-stack rule on the 17 Path A regression verses
plus the 7 named anchors. Compares the mechanical-with-rule output (baseline
UD + BYPASS_OVERRIDES=1) against the deployed override AND yardstick gold.

Output: per-verse mechanical lines + arbiter + verdict (match / equivalent /
regression / improvement).

Run:  py -3 scripts/validate_stack_rule.py
"""
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OVR = REPO / "data" / "text-files" / "v2-adjudicated" / "overrides.json"
YARDSTICK = REPO / "private" / "substrate" / "emode-substrate" / "bofm-atu-gold-yardstick.json"
RECENT = REPO / "data" / "parses" / "audit" / "ud-pilot-report-pathA.json"

NAMED = ["moroni 4:3", "moroni 5:2", "words-of-mormon 1:8", "alma 13:30",
         "alma 29:17", "alma 7:13", "alma 7:22", "helaman 5:8"]


def regen_verse(book, ch, v):
    env = {**os.environ, "BOFM_BYPASS_OVERRIDES": "1",
           "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.run(
        ["py", "-3", str(REPO / "scripts" / "bofm_generate.py"), book, str(ch)],
        capture_output=True, text=True, env=env, encoding="utf-8", errors="replace",
    )
    out = proc.stdout or ""
    lines, in_verse = [], False
    marker = f"{ch}:{v}"
    import re
    next_ref = re.compile(r"^\s*\d+:\d+\s*$")
    for line in out.splitlines():
        if line.strip() == marker:
            in_verse = True; continue
        if in_verse:
            if next_ref.match(line):
                break
            if line.strip():
                lines.append(line.rstrip())
    return lines


def main():
    pa_report = json.loads(RECENT.read_text(encoding="utf-8")) if RECENT.exists() else {}
    regression_refs = [r["ref"] for r in pa_report.get("regressions_vs_arbiter", [])]
    all_refs = list(dict.fromkeys(NAMED + regression_refs))

    overrides = json.loads(OVR.read_text(encoding="utf-8"))
    ys = json.loads(YARDSTICK.read_text(encoding="utf-8")) if YARDSTICK.exists() else []
    ys_by_ref = {e["ref"]: e["gold_lines"] for e in ys}

    print(f"=== Validating §2.2 stack rule on {len(all_refs)} verses ===\n")
    summary = {"match_yardstick": 0, "match_override": 0,
               "over_split_vs_arbiter": 0, "under_split_vs_arbiter": 0,
               "different": 0, "no_arbiter": 0}
    by_book_cache = {}
    for ref in all_refs:
        book, cv = ref.rsplit(" ", 1)
        ch, v = (int(x) for x in cv.split(":"))
        if book not in by_book_cache:
            by_book_cache[book] = {}
        mech = regen_verse(book, ch, v)
        arb_label, arb, kind = None, None, None
        if ref in ys_by_ref:
            arb_label, arb = "yardstick", ys_by_ref[ref]
        elif ref in overrides:
            arb_label, arb = "override", overrides[ref]
        if arb is None:
            kind = "no_arbiter"
            summary["no_arbiter"] += 1
        elif mech == arb:
            kind = f"match_{arb_label}"
            summary[f"match_{arb_label}"] = summary.get(f"match_{arb_label}", 0) + 1
        elif len(mech) > len(arb):
            kind = "over_split_vs_arbiter"
            summary["over_split_vs_arbiter"] += 1
        elif len(mech) < len(arb):
            kind = "under_split_vs_arbiter"
            summary["under_split_vs_arbiter"] += 1
        else:
            kind = "different"
            summary["different"] += 1
        print(f"--- {ref} ({kind}, arbiter={arb_label}) ---")
        print(f"  mech ({len(mech)} lines):")
        for ln in mech:
            print(f"    {ln[:140]}")
        if arb:
            print(f"  arbiter ({len(arb)} lines):")
            for ln in arb:
                print(f"    {ln[:140]}")
        print()

    print(f"=== SUMMARY ===")
    for k, n in summary.items():
        print(f"  {k}: {n}")


if __name__ == "__main__":
    main()
