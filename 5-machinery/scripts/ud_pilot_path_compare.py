"""Compare Path A (no-Opus, mechanical only) vs Path B (Opus-gated) for the
UD-correction v2 pilot.

Path A: v2 Sonnet proposals -> validate.py delta-gate -> ATU regen -> 3-way diff
Path B: v2 Sonnet proposals -> Opus audits -> validate.py -> ATU regen -> 3-way diff

The Path A - Path B delta is the empirical question: did Opus kill proposals
the mechanical path would have passed? Broken down by lens.

Run:  py -3 5-machinery/scripts/ud_pilot_path_compare.py <v2_output_json> <audit_output_json>
Out:  data/parses/audit/ud-pilot-path-compare.json
"""
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
AUDIT_DIR = REPO / "data" / "parses" / "audit"


def run_harness(survivors_path, scratch_dir, report_path):
    """Run the harness with a custom scratch dir + report-path override."""
    env = {**os.environ,
           "UD_PILOT_SCRATCH": str(scratch_dir),
           "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.run(
        ["py", "-3", str(REPO / "5-machinery" / "scripts" / "ud_pilot_harness.py"), str(survivors_path)],
        capture_output=True, text=True, env=env, encoding="utf-8", errors="replace",
    )
    print(proc.stdout)
    if proc.returncode != 0:
        print(f"  harness stderr: {proc.stderr}")
    default_report = AUDIT_DIR / "ud-pilot-report.json"
    if default_report.exists():
        default_report.rename(report_path)
    return json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else None


def to_survivors_json(proposals, out_path):
    """Wrap a proposals list as a survivors-format JSON the harness expects."""
    fmt = {"class": "UD_CORRECTION", "survivors": [
        {"ref": p["ref"], "sent_ids": p["sent_ids"],
         "baseline_errors": p["baseline_errors"],
         "deployed_lines": p["deployed_lines"],
         "deployed_override_present": p.get("deployed_override_present", False),
         "edit_groups": [{"group_id": 1, "edits": [
             {"sent_id": e["sent_id"], "token": e["token"],
              "column": e["column"], "baseline": e["baseline"], "new": e["new"]}
             for e in p["edits"]
         ], "rationale": p.get("reasoning", "")}],
         "reasoning": p.get("reasoning", "")}
        for p in proposals
    ]}
    out_path.write_text(json.dumps(fmt, indent=2), encoding="utf-8")


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    v2_path = Path(sys.argv[1])
    audit_path = Path(sys.argv[2])

    v2 = json.loads(v2_path.read_text(encoding="utf-8"))
    if "result" in v2 and isinstance(v2.get("result"), dict): v2 = v2["result"]
    v2_proposals = v2.get("proposals", [])

    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if "result" in audit and isinstance(audit.get("result"), dict): audit = audit["result"]
    opus_survivors = audit.get("survivors", [])
    opus_killed = audit.get("killed", [])

    print(f"=== INPUT ===")
    print(f"  v2 Sonnet proposals: {len(v2_proposals)}")
    print(f"  Opus survivors:      {len(opus_survivors)}")
    print(f"  Opus killed:         {len(opus_killed)}")

    path_a_proposals = v2_proposals
    path_b_proposals = [{"ref": s["ref"], "sent_ids": s["sent_ids"],
                          "baseline_errors": s["baseline_errors"],
                          "deployed_lines": s["deployed_lines"],
                          "deployed_override_present": s.get("deployed_override_present", False),
                          "edits": s["edits"], "reasoning": s.get("reasoning", "")}
                         for s in opus_survivors]

    pa_survivors = AUDIT_DIR / "ud-pilot-pathA-survivors.json"
    pb_survivors = AUDIT_DIR / "ud-pilot-pathB-survivors.json"
    to_survivors_json(path_a_proposals, pa_survivors)
    to_survivors_json(path_b_proposals, pb_survivors)

    print(f"\n=== PATH A: mechanical only (validate + 3-way on all v2 proposals) ===")
    pa_report = run_harness(pa_survivors, Path(r"C:\tmp\ud_pilot_A"),
                             AUDIT_DIR / "ud-pilot-report-pathA.json")
    print(f"\n=== PATH B: Opus-gated (validate + 3-way on Opus-survivors) ===")
    pb_report = run_harness(pb_survivors, Path(r"C:\tmp\ud_pilot_B"),
                             AUDIT_DIR / "ud-pilot-report-pathB.json")

    pa_gated = {d["ref"] for d in (pa_report or {}).get("named_anchor_diffs", []) +
                                    (pa_report or {}).get("yardstick_arbited_diffs", []) +
                                    (pa_report or {}).get("override_arbited_diffs", []) +
                                    (pa_report or {}).get("no_verdict_bundle", [])}
    pb_gated = {d["ref"] for d in (pb_report or {}).get("named_anchor_diffs", []) +
                                    (pb_report or {}).get("yardstick_arbited_diffs", []) +
                                    (pb_report or {}).get("override_arbited_diffs", []) +
                                    (pb_report or {}).get("no_verdict_bundle", [])}

    opus_kills_passing_mechanical = [k for k in opus_killed if k["ref"] in pa_gated]

    delta_by_lens = {"over_edit_only": [], "downstream_only": [], "both": []}
    for k in opus_kills_passing_mechanical:
        oe = k.get("over_edit_verdict") == "kill"
        ds = k.get("downstream_verdict") == "kill"
        bucket = "both" if (oe and ds) else ("over_edit_only" if oe else "downstream_only")
        delta_by_lens[bucket].append({
            "ref": k["ref"],
            "edits": k["edits"],
            "over_edit_reasoning": (k.get("over_edit_reasoning") or "")[:400],
            "downstream_reasoning": (k.get("downstream_reasoning") or "")[:400],
        })

    pa_regs = (pa_report or {}).get("regressions_vs_arbiter", [])
    pb_regs = (pb_report or {}).get("regressions_vs_arbiter", [])

    out = {
        "input": {
            "v2_proposals": len(v2_proposals),
            "opus_survivors": len(opus_survivors),
            "opus_killed": len(opus_killed),
        },
        "path_a": {
            "gated_survivors": (pa_report or {}).get("gated_survivors_count", 0),
            "regressions_vs_arbiter": len(pa_regs),
            "yardstick_arbited": len((pa_report or {}).get("yardstick_arbited_diffs", [])),
            "override_arbited": len((pa_report or {}).get("override_arbited_diffs", [])),
            "no_verdict": len((pa_report or {}).get("no_verdict_bundle", [])),
        },
        "path_b": {
            "gated_survivors": (pb_report or {}).get("gated_survivors_count", 0),
            "regressions_vs_arbiter": len(pb_regs),
            "yardstick_arbited": len((pb_report or {}).get("yardstick_arbited_diffs", [])),
            "override_arbited": len((pb_report or {}).get("override_arbited_diffs", [])),
            "no_verdict": len((pb_report or {}).get("no_verdict_bundle", [])),
        },
        "opus_delta_substantive": {
            "kills_that_passed_mechanical": len(opus_kills_passing_mechanical),
            "by_lens": {k: len(v) for k, v in delta_by_lens.items()},
            "detail": delta_by_lens,
        },
        "path_a_regressions": pa_regs,
        "path_b_regressions": pb_regs,
    }
    out_path = AUDIT_DIR / "ud-pilot-path-compare.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"\n=== PATH A vs PATH B COMPARISON written to {out_path.relative_to(REPO)} ===")
    print(f"  Path A gated survivors: {out['path_a']['gated_survivors']}")
    print(f"  Path B gated survivors: {out['path_b']['gated_survivors']}")
    print(f"  Path A regressions vs arbiter: {out['path_a']['regressions_vs_arbiter']}")
    print(f"  Path B regressions vs arbiter: {out['path_b']['regressions_vs_arbiter']}")
    print(f"  Opus kills that mechanical would have passed: {out['opus_delta_substantive']['kills_that_passed_mechanical']}")
    print(f"  By lens: {out['opus_delta_substantive']['by_lens']}")


if __name__ == "__main__":
    main()
