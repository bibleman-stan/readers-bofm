"""Enrich a candidates JSON (from audit_to_candidates.py) with baseline_conllu
+ sent_ids per candidate. Generic across any anomaly class.

Run:  py -3 scripts/enrich_class_candidates.py CLASS_NAME
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AUDIT = REPO / "data" / "parses" / "audit"
CACHE = REPO / "data" / "parses" / "v0-cache"

sys.path.insert(0, str(REPO / "scripts"))
from ud_pilot_extract_baseline import emit_sentence, FORM


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    cls = sys.argv[1]
    in_path = AUDIT / f"candidates-{cls}.json"
    out_path = AUDIT / f"candidates-{cls}-enriched.json"
    candidates = json.loads(in_path.read_text(encoding="utf-8"))
    by_book = {}
    enriched = []
    for c in candidates:
        book = c["book"]
        if book not in by_book:
            by_book[book] = json.loads((CACHE / f"{book}.json").read_text(encoding="utf-8"))
        sents = by_book[book].get(f"{c['ch']}:{c['v']}") or []
        sent_ids = []
        blocks = []
        for si, toks in enumerate(sents):
            sid = f"{book}_{c['ch']}_{c['v']}_s{si}"
            sent_ids.append(sid)
            text = " ".join((t[FORM] or "") for t in toks)
            blocks.append(emit_sentence(sid, text, toks))
        enriched.append({**c, "sent_ids": sent_ids,
                         "baseline_conllu": "\n\n".join(blocks)})
    out_path.write_text(json.dumps(enriched, indent=2), encoding="utf-8")
    print(f"Wrote {out_path.relative_to(REPO)}: {len(enriched)} enriched candidates")


if __name__ == "__main__":
    main()
