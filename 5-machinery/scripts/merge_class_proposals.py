"""Merge all spray-output chunks for a class into one survivors-format JSON.

Run:  py -3 5-machinery/scripts/merge_class_proposals.py CLASS_TAG   (e.g. PDS, LDA, BDD)
"""
import glob
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
AUDIT = REPO / "data" / "parses" / "audit"


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    tag = sys.argv[1]
    out_path = AUDIT / f"merged-survivors-{tag}.json"
    survivors = []
    for p in sorted(glob.glob(str(AUDIT / f"spray-output-{tag}-chunk*.json"))):
        d = json.loads(Path(p).read_text(encoding="utf-8"))
        if "result" in d and isinstance(d.get("result"), dict):
            d = d["result"]
        for prop in d.get("proposals", []):
            survivors.append({
                "ref": prop["ref"],
                "sent_ids": prop["sent_ids"],
                "baseline_errors": {},
                "deployed_lines": [],
                "deployed_override_present": False,
                "edit_groups": [{
                    "group_id": 1,
                    "edits": [{"sent_id": e["sent_id"], "token": e["token"],
                               "column": e["column"], "baseline": e["baseline"], "new": e["new"]}
                              for e in prop["edits"]],
                    "rationale": prop.get("reasoning", ""),
                }],
                "reasoning": prop.get("reasoning", ""),
            })
    out_path.write_text(json.dumps({"class": tag, "survivors": survivors,
                                    "counts": {"survivors": len(survivors)}}, indent=2),
                        encoding="utf-8")
    print(f"  {tag}: {len(survivors)} proposals merged -> {out_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
