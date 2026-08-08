"""Extract baseline Stanza CoNLL-U for the 50-verse UD-pilot manifest.

Reads candidates-PARALLEL_THAT_ASYMMETRY-pilot.json + v0-cache/<book>.json,
emits a single CoNLL-U file with one sentence block per Stanza sentence per
pilot verse. Sentence IDs encode `book ch:v sN` so the gate output can be
mapped back to the verse.

Run:
  py -3 5-machinery/scripts/ud_pilot_extract_baseline.py
Out:
  data/parses/audit/ud-pilot-baseline.conllu
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
PILOT = REPO / "data" / "parses" / "audit" / "candidates-PARALLEL_THAT_ASYMMETRY-pilot.json"
CACHE = REPO / "data" / "parses" / "v0-cache"
OUT = REPO / "data" / "parses" / "audit" / "ud-pilot-baseline.conllu"

ID, HEAD, DEPREL, UPOS, LEMMA, FORM, START, END = range(8)


def emit_sentence(sent_id, text, toks):
    out = [f"# sent_id = {sent_id}", f"# text = {text}"]
    for t in toks:
        misc = "_"
        out.append("\t".join([
            str(t[ID]), t[FORM] or "_", t[LEMMA] or "_", t[UPOS] or "_",
            "_", "_", str(t[HEAD]), t[DEPREL] or "_", "_", misc,
        ]))
    return "\n".join(out)


def main():
    pilot = json.loads(PILOT.read_text(encoding="utf-8"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    by_book = {}
    blocks = []
    for cand in pilot:
        book = cand["book"]
        if book not in by_book:
            by_book[book] = json.loads((CACHE / f"{book}.json").read_text(encoding="utf-8"))
        cv = f"{cand['ch']}:{cand['v']}"
        sents = by_book[book].get(cv) or []
        for si, toks in enumerate(sents):
            text = " ".join((t[FORM] or "") for t in toks)
            sid = f"{book}_{cv.replace(':','_')}_s{si}"
            blocks.append(emit_sentence(sid, text, toks))
    OUT.write_text("\n\n".join(blocks) + "\n\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(REPO)}: {len(blocks)} sentence blocks across {len(pilot)} verses")


if __name__ == "__main__":
    main()
