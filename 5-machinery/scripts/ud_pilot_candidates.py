"""Build UD-correction candidate payloads for the 50-verse pilot.

For each verse:
  - flag class + detail (from audit/stanza-anomalies.json)
  - source text (v0 master)
  - baseline Stanza CoNLL-U sentence blocks (one or more)
  - baseline error count for each sentence (from validate-helper)
  - deployed override lines (if any, from overrides.json) — used as the
    "compare-against" target for the downstream-effect audit lens

Run:  py -3 5-machinery/scripts/ud_pilot_candidates.py
Out:  data/parses/audit/ud-pilot-candidates.json
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
PILOT = REPO / "data" / "parses" / "audit" / "candidates-PARALLEL_THAT_ASYMMETRY-pilot.json"
ANOM = REPO / "data" / "parses" / "audit" / "stanza-anomalies.json"
OVR = REPO / "data" / "text-files" / "v2-adjudicated" / "overrides.json"
CACHE = REPO / "data" / "parses" / "v0-cache"
OUT = REPO / "data" / "parses" / "audit" / "ud-pilot-candidates.json"

sys.path.insert(0, str(REPO / "5-machinery" / "scripts"))
from ud_validate_helper import validate_per_sent
from ud_pilot_extract_baseline import emit_sentence, ID, HEAD, DEPREL, UPOS, LEMMA, FORM


def main():
    pilot = json.loads(PILOT.read_text(encoding="utf-8"))
    anom = json.loads(ANOM.read_text(encoding="utf-8"))["verses"]
    ovr = json.loads(OVR.read_text(encoding="utf-8"))
    baseline_path = REPO / "data" / "parses" / "audit" / "ud-pilot-baseline.conllu"
    baseline_errs, _, _ = validate_per_sent(baseline_path)

    by_book = {}
    out = []
    for cand in pilot:
        book = cand["book"]
        if book not in by_book:
            by_book[book] = json.loads((CACHE / f"{book}.json").read_text(encoding="utf-8"))
        cv = f"{cand['ch']}:{cand['v']}"
        sents = by_book[book].get(cv) or []
        conllu_blocks = []
        sent_ids = []
        for si, toks in enumerate(sents):
            text = " ".join((t[FORM] or "") for t in toks)
            sid = f"{book}_{cv.replace(':','_')}_s{si}"
            conllu_blocks.append(emit_sentence(sid, text, toks))
            sent_ids.append(sid)
        flags = [f for f in anom.get(cand["ref"], {}).get("flags", [])
                 if f["class"] == "PARALLEL_THAT_ASYMMETRY"]
        out.append({
            "ref": cand["ref"],
            "book": book, "ch": cand["ch"], "v": cand["v"],
            "source_text": cand["source_text"],
            "flag_detail": flags[0]["detail"] if flags else "",
            "sent_ids": sent_ids,
            "baseline_errors": {sid: baseline_errs.get(sid, 0) for sid in sent_ids},
            "baseline_conllu": "\n\n".join(conllu_blocks),
            "deployed_lines": cand["deployed_lines"],
            "deployed_override": ovr.get(cand["ref"]),
        })

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(REPO)}: {len(out)} candidates")
    print(f"  Total baseline sentences: {sum(len(c['sent_ids']) for c in out)}")
    print(f"  Total baseline errors: {sum(sum(c['baseline_errors'].values()) for c in out)}")
    print(f"  Have deployed override: {sum(1 for c in out if c['deployed_override'])}")


if __name__ == "__main__":
    main()
