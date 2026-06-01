"""Validate-gate the 499 fullclass UD-correction proposals.

Steps:
  1. Extract baseline Stanza CoNLL-U for all 499 verses' sentences.
  2. Run validate.py on baseline and on corrected CoNLL-U (already written to
     scratch by ud_apply_to_scratch.py).
  3. Per survivor: if ANY of its sentences has corrected_errors > baseline_errors,
     mark as gate-failed (delta gate).
  4. Write gated survivors → ud-fullclass-gated-survivors.json.

Run:  py -3 scripts/fullclass_validate_gate.py
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRATCH = Path(r"C:\tmp\ud_fullclass\v0-cache")
MERGED = REPO / "data" / "parses" / "audit" / "ud-fullclass-merged-survivors.json"
OUT_GATED = REPO / "data" / "parses" / "audit" / "ud-fullclass-gated-survivors.json"
BASELINE_CONLLU = REPO / "data" / "parses" / "audit" / "ud-fullclass-baseline.conllu"

sys.path.insert(0, str(REPO / "scripts"))
from ud_pilot_extract_baseline import emit_sentence, FORM
from ud_validate_helper import validate_per_sent


def main():
    merged = json.loads(MERGED.read_text(encoding="utf-8"))
    survivors = merged["survivors"]
    print(f"Loaded {len(survivors)} merged proposals")

    cache_by_book = {}
    blocks = []
    for sv in survivors:
        ref = sv["ref"]
        book, cv = ref.rsplit(" ", 1)
        c, v = (int(x) for x in cv.split(":"))
        if book not in cache_by_book:
            cache_by_book[book] = json.loads(
                (REPO / "data" / "parses" / "v0-cache" / f"{book}.json").read_text(encoding="utf-8"))
        sents = cache_by_book[book].get(f"{c}:{v}") or []
        for si, toks in enumerate(sents):
            sid = f"{book}_{c}_{v}_s{si}"
            text = " ".join((t[FORM] or "") for t in toks)
            blocks.append(emit_sentence(sid, text, toks))

    BASELINE_CONLLU.write_text("\n\n".join(blocks) + "\n\n", encoding="utf-8")
    print(f"Wrote baseline CoNLL-U: {BASELINE_CONLLU} ({len(blocks)} sentences)")

    print("Running validate.py on baseline...")
    baseline_errs, baseline_total, _ = validate_per_sent(BASELINE_CONLLU)
    print(f"  Baseline total errors: {baseline_total}")
    print(f"  Baseline sentences with errors: {len(baseline_errs)}")

    print("Running validate.py on corrected...")
    corrected_path = SCRATCH / "ud-pilot-corrected.conllu"
    corrected_errs, corrected_total, _ = validate_per_sent(corrected_path)
    print(f"  Corrected total errors: {corrected_total}")
    print(f"  Corrected sentences with errors: {len(corrected_errs)}")
    print(f"  Total error delta: {corrected_total - baseline_total} ({'+' if corrected_total > baseline_total else ''})")

    gated_pass = []
    gated_fail = []
    for sv in survivors:
        failed = False
        for sid in sv["sent_ids"]:
            b = baseline_errs.get(sid, 0)
            c = corrected_errs.get(sid, 0)
            if c > b:
                failed = True
                break
        if failed:
            gated_fail.append(sv["ref"])
        else:
            gated_pass.append(sv)

    print(f"\nGate results:")
    print(f"  Pass: {len(gated_pass)}")
    print(f"  Fail (introduces new validator errors): {len(gated_fail)}")
    if gated_fail[:10]:
        print(f"  Failed sample: {gated_fail[:10]}")

    out = {"class": "UD_CORRECTION_FULLCLASS_GATED", "survivors": gated_pass,
           "gate_failed_refs": gated_fail,
           "counts": {"gate_pass": len(gated_pass), "gate_fail": len(gated_fail),
                      "baseline_total_errors": baseline_total,
                      "corrected_total_errors": corrected_total}}
    OUT_GATED.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT_GATED.relative_to(REPO)}")


if __name__ == "__main__":
    main()
