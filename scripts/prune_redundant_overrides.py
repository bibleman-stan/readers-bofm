"""Identify and prune overrides now mechanically reproducible.

For each override entry: regen the verse with BOFM_BYPASS_OVERRIDES=1 (no
override applied) and compare against the override's stored lines. If
mechanical output == override lines, the override is redundant — the new
§2.2 stack rule (or other shipped rules) reproduces it without help.

Reports per-override status. Prunes only on --apply flag.

Run:
  py -3 scripts/prune_redundant_overrides.py            # dry run, report only
  py -3 scripts/prune_redundant_overrides.py --apply    # prune redundant
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OVR = REPO / "data" / "text-files" / "v2-adjudicated" / "overrides.json"


def regen_book(book):
    """{ch:v -> [lines]} for a whole book with BYPASS_OVERRIDES=1."""
    env = {**os.environ, "BOFM_BYPASS_OVERRIDES": "1",
           "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.run(
        ["py", "-3", str(REPO / "scripts" / "bofm_generate.py"), book],
        capture_output=True, text=True, env=env, encoding="utf-8", errors="replace",
    )
    out = proc.stdout or ""
    by_ref = {}
    cur, lines = None, []
    ref_re = re.compile(r"^\s*(\d+):(\d+)\s*$")
    for line in out.splitlines():
        m = ref_re.match(line)
        if m:
            if cur is not None:
                by_ref[cur] = lines
            cur = f"{m.group(1)}:{m.group(2)}"; lines = []
        elif cur is not None and line.strip():
            lines.append(line.rstrip())
    if cur is not None:
        by_ref[cur] = lines
    return by_ref


def normalize(s):
    return re.sub(r"\s+", " ", s).strip()


def main():
    apply_changes = "--apply" in sys.argv
    overrides = json.loads(OVR.read_text(encoding="utf-8"))
    print(f"Loaded {len(overrides)} overrides")

    by_book = {}
    for ref in overrides:
        book = ref.rsplit(" ", 1)[0]
        by_book.setdefault(book, []).append(ref)

    redundant, kept, diff = [], [], []
    for book, refs in sorted(by_book.items()):
        print(f"\nRegenerating {book}...")
        mech = regen_book(book)
        for ref in refs:
            cv = ref.rsplit(" ", 1)[1]
            ovr_lines = overrides[ref]
            mech_lines = mech.get(cv) or []
            ovr_norm = [normalize(l) for l in ovr_lines]
            mech_norm = [normalize(l) for l in mech_lines]
            if ovr_norm == mech_norm:
                redundant.append(ref)
            else:
                kept.append(ref)
                if len(mech_norm) != len(ovr_norm):
                    diff.append((ref, len(ovr_norm), len(mech_norm)))

    print(f"\n=== SUMMARY ===")
    print(f"  Redundant (mech == override): {len(redundant)}")
    print(f"  Kept (mech != override):      {len(kept)}")
    print(f"  Line-count diff sample (first 10):")
    for ref, ol, ml in diff[:10]:
        print(f"    {ref}: override {ol} lines, mech {ml} lines")

    if apply_changes and redundant:
        for ref in redundant:
            del overrides[ref]
        OVR.write_text(json.dumps(overrides, indent=2) + "\n", encoding="utf-8")
        print(f"\nPruned {len(redundant)} redundant overrides.")
        print(f"overrides.json: {len(overrides)} entries remaining")
    elif redundant:
        print(f"\nDry run — re-run with --apply to prune.")


if __name__ == "__main__":
    main()
