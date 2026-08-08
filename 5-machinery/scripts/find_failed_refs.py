"""Identify candidates that didn't return from a class's chunked Workflow.

Compares the original candidate manifest against the union of returned refs
across all chunks (proposals + no_corrections). Outputs failed-refs candidate
JSON for re-launch.

Run:  py -3 5-machinery/scripts/find_failed_refs.py CLASS_TAG   (PDS|LDA|BDD)
Out:  data/parses/audit/failed-refs-{CLASS}-enriched.json
"""
import glob
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
AUDIT = REPO / "data" / "parses" / "audit"

CLASS_TO_FULL = {
    "PDS": "PUNCTUATION_DRIVEN_SPLIT",
    "LDA": "LONG_DISTANCE_ATTACHMENT",
    "BDD": "BIGRAM_DEPREL_DIVERGENCE",
}


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    tag = sys.argv[1]
    full = CLASS_TO_FULL[tag]
    enriched = json.loads((AUDIT / f"candidates-{full}-enriched.json").read_text(encoding="utf-8"))
    all_refs = {c["ref"] for c in enriched}
    returned = set()
    for p in glob.glob(str(AUDIT / f"spray-output-{tag}-chunk*.json")):
        d = json.loads(Path(p).read_text(encoding="utf-8"))
        if "result" in d and isinstance(d.get("result"), dict):
            d = d["result"]
        for x in d.get("proposals", []):
            returned.add(x["ref"])
        nc = d.get("no_corrections", [])
        if isinstance(nc, list):
            for x in nc:
                if isinstance(x, dict) and "ref" in x:
                    returned.add(x["ref"])
    failed = all_refs - returned
    failed_cands = [c for c in enriched if c["ref"] in failed]
    out_path = AUDIT / f"failed-refs-{tag}-enriched.json"
    out_path.write_text(json.dumps(failed_cands, indent=2), encoding="utf-8")
    print(f"{tag}: {len(all_refs)} total, {len(returned)} returned, {len(failed)} failed")
    print(f"  Wrote {out_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
