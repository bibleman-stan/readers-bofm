"""Merge all 8 fullclass UD-correction chunk outputs into one survivors-format
JSON the harness scripts (ud_apply_to_scratch.py / ud_pilot_harness.py) accept.

Run:  py -3 scripts/merge_fullclass_proposals.py
Out:  data/parses/audit/ud-fullclass-merged-survivors.json
"""
import glob
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PILOT_CAND = REPO / "data" / "parses" / "audit" / "ud-correction-fullclass-candidates.json"
OUT = REPO / "data" / "parses" / "audit" / "ud-fullclass-merged-survivors.json"


def main():
    cand_by_ref = {c["ref"]: c for c in json.loads(PILOT_CAND.read_text(encoding="utf-8"))}

    survivors = []
    for path in sorted(glob.glob(str(REPO / "data" / "parses" / "audit" / "spray-output-UD-fullclass-*.json"))):
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        if "result" in d and isinstance(d.get("result"), dict):
            d = d["result"]
        for p in d.get("proposals", []):
            c = cand_by_ref.get(p["ref"], {})
            survivors.append({
                "ref": p["ref"],
                "sent_ids": p["sent_ids"],
                "baseline_errors": c.get("baseline_errors", {}) if c else {},
                "deployed_lines": c.get("deployed_lines", []) if c else [],
                "deployed_override_present": False,
                "edit_groups": [{
                    "group_id": 1,
                    "edits": [
                        {"sent_id": e["sent_id"], "token": e["token"],
                         "column": e["column"], "baseline": e["baseline"], "new": e["new"]}
                        for e in p["edits"]
                    ],
                    "rationale": p.get("reasoning", ""),
                }],
                "reasoning": p.get("reasoning", ""),
            })

    fmt = {"class": "UD_CORRECTION_FULLCLASS", "survivors": survivors,
           "counts": {"survivors": len(survivors)}}
    OUT.write_text(json.dumps(fmt, indent=2), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(REPO)}: {len(survivors)} merged proposals")
    n_edits = sum(len(s["edit_groups"][0]["edits"]) for s in survivors)
    print(f"Total individual edits across proposals: {n_edits}")


if __name__ == "__main__":
    main()
