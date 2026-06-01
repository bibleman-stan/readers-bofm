"""Apply v2-spray survivors to overrides.json + yardstick.json.

Reads a spray-output JSON (from a Workflow run, see build_spray_workflow.py).
For each survivor:
  1. Revalidates parity against v0 master (defensive — gate-passed survivors
     shouldn't fail, but a parity guard is cheap insurance).
  2. Writes to overrides.json (deployed).
  3. Writes to bofm-atu-gold-yardstick.json (regression substrate, genre
     auto-tagged from matrix predicate or 'SPRAY_<class>').
  4. Runs twin-flag scan (same as sync_gold) — surfaces parallel-verbatim
     verses lacking gold, the symmetry lock-down.

Run (single or multiple chunk outputs):
  py -3 scripts/apply_spray_survivors.py path/to/spray-output.json
  py -3 scripts/apply_spray_survivors.py chunk0.json chunk1.json chunk2.json

Survivors from all inputs are concatenated; later entries override earlier.

Failures HALT with a per-verse diagnostic. No partial writes.
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OVERRIDES = REPO / "data" / "text-files" / "v2-adjudicated" / "overrides.json"
YARDSTICK = REPO / "private" / "substrate" / "emode-substrate" / "bofm-atu-gold-yardstick.json"

sys.path.insert(0, str(REPO / "scripts"))
from sync_gold import load_v0_book, find_twins, normalize, BOOK_TO_V0


def infer_genre(matrix):
    if not matrix:
        return "SPRAY_PARALLEL_STACK"
    m = matrix.lower()
    if any(k in m for k in ("ask thee", "petition", "we ask", "bless", "sanctify")):
        return "LITURGICAL"
    if any(k in m for k in ("i would", "ye should", "command", "covenant")):
        return "COVENANT"
    if any(k in m for k in ("i know", "i declare", "i say", "i testify", "verily")):
        return "DOCTRINAL"
    if any(k in m for k in ("came to pass", "it came", "and they", "did go")):
        return "NARRATIVE"
    return "SPRAY_PARALLEL_STACK"


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    spray_paths = [Path(p) for p in sys.argv[1:]]
    for sp in spray_paths:
        if not sp.exists():
            print(f"Not found: {sp}")
            sys.exit(1)

    survivors = []
    for sp in spray_paths:
        result = json.loads(sp.read_text(encoding="utf-8"))
        if "result" in result and isinstance(result.get("result"), dict):
            result = result["result"]
        chunk_survivors = result.get("survivors", [])
        print(f"Loaded {sp.name}")
        print(f"  Class: {result.get('class', '(unknown)')}")
        print(f"  Survivors: {len(chunk_survivors)}")
        print(f"  Counts: {result.get('counts', {})}")
        survivors.extend(chunk_survivors)
    print(f"\nTotal survivors across {len(spray_paths)} file(s): {len(survivors)}")

    if not survivors:
        print("No survivors to apply — exiting.")
        return

    v0_cache = {}
    failures = []
    validated = []
    for s in survivors:
        ref = s["ref"]
        book, cv = ref.rsplit(" ", 1)
        c, v = (int(x) for x in cv.split(":"))
        if book not in BOOK_TO_V0:
            failures.append((ref, f"unknown book '{book}'")); continue
        if book not in v0_cache:
            v0_cache[book] = load_v0_book(book)
        src = v0_cache[book].get((c, v))
        if src is None:
            failures.append((ref, "verse not in v0 source")); continue
        lines = s.get("proposed_lines") or []
        reconstructed = normalize(" ".join(lines))
        master = normalize(src)
        if reconstructed != master:
            failures.append((ref, f"parity fail (len {len(reconstructed)} vs {len(master)})"))
            continue
        validated.append({
            "ref": ref, "book": book, "ch": c, "v": v,
            "lines": lines,
            "source_text": src,
            "genre": infer_genre(s.get("matrix")),
            "matrix": s.get("matrix"),
            "n_beats": s.get("n_beats"),
            "confidence": s.get("confidence"),
        })

    if failures:
        print(f"\n{len(failures)} parity FAILURE(S) on survivors — no writes performed:")
        for ref, why in failures:
            print(f"  {ref}: {why}")
        sys.exit(2)

    v0_index = []
    for book in BOOK_TO_V0:
        if book not in v0_cache:
            v0_cache[book] = load_v0_book(book)
        for (c, v), text in v0_cache[book].items():
            v0_index.append(((book, c, v), text))

    overrides = json.loads(OVERRIDES.read_text(encoding="utf-8")) if OVERRIDES.exists() else {}
    yardstick = json.loads(YARDSTICK.read_text(encoding="utf-8")) if YARDSTICK.exists() else []
    ys_by_ref = {e["ref"]: e for e in yardstick}

    print(f"\n--- Applying {len(validated)} survivor(s) ---")
    twins_to_review = []
    for entry in validated:
        ref = entry["ref"]
        overrides[ref] = entry["lines"]
        ys_by_ref[ref] = {"ref": ref, "genre": entry["genre"], "gold_lines": entry["lines"]}
        print(f"  ok  {ref:30s} ({len(entry['lines'])} lines, genre={entry['genre']}, conf={entry['confidence']})")
        twins = find_twins(ref, entry["source_text"], v0_index)
        for twin_ref, j in twins:
            twin_gold = ys_by_ref.get(twin_ref)
            if twin_gold is None or twin_gold.get("gold_lines") != overrides.get(twin_ref):
                twins_to_review.append((ref, twin_ref, j, twin_gold is not None))

    OVERRIDES.write_text(json.dumps(overrides, indent=2) + "\n", encoding="utf-8")
    yardstick_sorted = sorted(ys_by_ref.values(), key=lambda e: e["ref"])
    YARDSTICK.parent.mkdir(parents=True, exist_ok=True)
    YARDSTICK.write_text(json.dumps(yardstick_sorted, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {OVERRIDES.relative_to(REPO)} ({len(overrides)} entries)")
    print(f"Wrote {YARDSTICK.relative_to(REPO)} ({len(yardstick_sorted)} entries)")

    if twins_to_review:
        print(f"\n--- TWIN FLAG ({len(twins_to_review)} pair(s)) ---")
        for own, twin, j, has_gold in twins_to_review:
            status = "has gold (verify symmetric)" if has_gold else "NO GOLD YET"
            print(f"  {own}  ~  {twin}  (Jaccard {j})  [{status}]")
        print("\n^^ review for parallel-verbatim symmetric ATU treatment.")
    print("\nNext: py -3 build_book.py --all   (regen HTML, bump sw.js)")


if __name__ == "__main__":
    main()
