"""End-to-end harness for the UD-correction pilot.

Steps:
  1. Apply survivors' edit_groups to a scratch v0-cache.
  2. Validate the corrected CoNLL-U via UD tools; per-sentence delta gate
     (corrected_errors[sid] <= baseline_errors[sid]).
  3. Regenerate ATU output for pilot verses via bofm_generate.py pointed at
     the scratch cache with BOFM_BYPASS_OVERRIDES=1 (so we measure what the
     CORRECTED UD produces through the binding rules alone — apples-to-
     apples vs the deployed override version).
  4. Three-way diff per verse: corrected-UD ATU vs deployed override (8a57e33)
     vs yardstick gold (where present).

Arbiter hierarchy:
  yardstick gold > shipped override (de-facto gold for audit-named) > NO VERDICT

Run:  py -3 5-machinery/scripts/ud_pilot_harness.py <survivors_json>
Out:  data/parses/audit/ud-pilot-report.json
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
SCRATCH = Path(os.environ.get("UD_PILOT_SCRATCH", r"C:\tmp\ud_pilot"))
PILOT_CAND = REPO / "data" / "parses" / "audit" / "ud-pilot-candidates.json"
YARDSTICK = REPO / "private" / "substrate" / "emode-substrate" / "bofm-atu-gold-yardstick.json"
REPORT = REPO / "data" / "parses" / "audit" / "ud-pilot-report.json"

NAMED_ANCHORS = {"moroni 4:3", "words-of-mormon 1:8", "alma 13:30", "alma 29:17",
                 "alma 7:13", "alma 7:22", "helaman 5:8"}

sys.path.insert(0, str(REPO / "5-machinery" / "scripts"))
from ud_validate_helper import validate_per_sent


def normalize(s):
    return re.sub(r"\s+", " ", s or "").strip()


def regen_atu_for(book, ch, v, scratch_cache_dir):
    env = {**os.environ,
           "BOFM_V0_CACHE_DIR": str(scratch_cache_dir),
           "BOFM_BYPASS_OVERRIDES": "1",
           "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.run(
        ["py", "-3", str(REPO / "5-machinery" / "scripts" / "bofm_generate.py"), book, str(ch)],
        capture_output=True, text=True, env=env, encoding="utf-8", errors="replace",
    )
    out = proc.stdout or ""
    lines, ref_marker = [], f"{ch}:{v}"
    in_verse = False
    next_ref = re.compile(r"^\s*\d+:\d+\s*$")
    for line in out.splitlines():
        if line.strip() == ref_marker:
            in_verse = True; continue
        if in_verse:
            if next_ref.match(line):
                break
            if line.strip():
                lines.append(line.rstrip())
    return lines


def three_way(corrected, override, yardstick):
    """Returns dict with all three + verdict (where arbiter present)."""
    out = {"corrected": corrected, "override": override, "yardstick": yardstick}
    if yardstick is not None:
        out["arbiter"] = "yardstick"
        out["corrected_vs_arbiter"] = "match" if corrected == yardstick else "differ"
        out["override_vs_arbiter"] = "match" if override == yardstick else "differ"
    elif override is not None:
        out["arbiter"] = "override-de-facto"
        out["corrected_vs_arbiter"] = "match" if corrected == override else "differ"
    else:
        out["arbiter"] = "none"
        out["corrected_vs_arbiter"] = "no-verdict"
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    survivors_path = Path(sys.argv[1])

    SCRATCH.mkdir(parents=True, exist_ok=True)
    print(f"=== STEP 1: apply survivors to {SCRATCH}/v0-cache ===")
    scratch_cache = SCRATCH / "v0-cache"
    apply_proc = subprocess.run(
        ["py", "-3", str(REPO / "5-machinery" / "scripts" / "ud_apply_to_scratch.py"),
         str(survivors_path), str(scratch_cache)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    print(apply_proc.stdout)
    if apply_proc.returncode != 0:
        print("Apply failed:", apply_proc.stderr); sys.exit(2)

    print("=== STEP 2: validate-gate (delta vs baseline) ===")
    corrected_conllu = scratch_cache / "ud-pilot-corrected.conllu"
    cand_data = json.loads(PILOT_CAND.read_text(encoding="utf-8"))
    baseline_errs_by_sid = {}
    for c in cand_data:
        for sid, n in c["baseline_errors"].items():
            baseline_errs_by_sid[sid] = n
    corrected_errs, total_corrected, _ = validate_per_sent(corrected_conllu)
    baseline_total = sum(baseline_errs_by_sid.values())
    print(f"  Baseline total: {baseline_total} errors")
    print(f"  Corrected total: {total_corrected} errors")
    delta_failures = []
    for sid in baseline_errs_by_sid:
        b = baseline_errs_by_sid.get(sid, 0)
        c = corrected_errs.get(sid, 0)
        if c > b:
            delta_failures.append({"sent_id": sid, "baseline": b, "corrected": c})
    print(f"  Sentences failing delta-gate: {len(delta_failures)}")

    survivors_raw = json.loads(survivors_path.read_text(encoding="utf-8"))
    if "result" in survivors_raw and isinstance(survivors_raw.get("result"), dict):
        survivors_raw = survivors_raw["result"]
    survivors = survivors_raw.get("survivors", [])
    failed_sids = {f["sent_id"] for f in delta_failures}
    gated_survivors, gate_killed = [], []
    for sv in survivors:
        if any(sid in failed_sids for sid in sv["sent_ids"]):
            gate_killed.append(sv["ref"])
        else:
            gated_survivors.append(sv)
    print(f"  Gate killed: {len(gate_killed)}")
    print(f"  Gated survivors: {len(gated_survivors)}")

    print("=== STEP 3: regenerate ATU + three-way diff ===")
    ys = json.loads(YARDSTICK.read_text(encoding="utf-8")) if YARDSTICK.exists() else []
    ys_by_ref = {e["ref"]: e["gold_lines"] for e in ys}
    cand_by_ref = {c["ref"]: c for c in cand_data}

    diffs, regressions = [], []
    for sv in gated_survivors:
        ref = sv["ref"]
        book, cv = ref.rsplit(" ", 1)
        ch, v = (int(x) for x in cv.split(":"))
        corrected_lines = regen_atu_for(book, ch, v, scratch_cache)
        override = cand_by_ref[ref].get("deployed_override")
        yardstick_gold = ys_by_ref.get(ref)
        diff = three_way(corrected_lines, override, yardstick_gold)
        diff["ref"] = ref
        diff["is_named_anchor"] = ref in NAMED_ANCHORS
        diff["matches_baseline_deployed"] = corrected_lines == cand_by_ref[ref]["deployed_lines"]
        diffs.append(diff)
        if diff["arbiter"] in ("yardstick", "override-de-facto") and diff["corrected_vs_arbiter"] == "differ":
            regressions.append(diff)

    report = {
        "baseline_total_errors": baseline_total,
        "corrected_total_errors": total_corrected,
        "delta_gate_failures": delta_failures,
        "workflow_survivors": len(survivors),
        "gate_killed_count": len(gate_killed),
        "gate_killed_refs": gate_killed,
        "gated_survivors_count": len(gated_survivors),
        "named_anchor_diffs": [d for d in diffs if d["is_named_anchor"]],
        "yardstick_arbited_diffs": [d for d in diffs if d["arbiter"] == "yardstick"],
        "override_arbited_diffs": [d for d in diffs if d["arbiter"] == "override-de-facto"],
        "no_verdict_bundle": [d for d in diffs if d["arbiter"] == "none"],
        "regressions_vs_arbiter": regressions,
    }
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\n=== REPORT written to {REPORT.relative_to(REPO)} ===")
    print(f"  Named-anchor three-ways: {len(report['named_anchor_diffs'])}")
    print(f"  Yardstick-arbited: {len(report['yardstick_arbited_diffs'])}")
    print(f"  Override-arbited: {len(report['override_arbited_diffs'])}")
    print(f"  No-verdict bundle: {len(report['no_verdict_bundle'])}")
    print(f"  Regressions vs arbiter: {len(regressions)}")


if __name__ == "__main__":
    main()
