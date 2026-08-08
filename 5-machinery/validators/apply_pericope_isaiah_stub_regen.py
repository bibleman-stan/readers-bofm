#!/usr/bin/env python3
"""
Sweep #2 from the 2026-04-27 pericope canon v0.1 → v1.0 audit:
Apply title-shape regeneration to the "Quoting Isaiah" content-less stubs
identified by the corpus-fit audit agent.

Per canon §4 quotation-block shape: "[content description] (Isa N:M-N)"
— source citation alone is insufficient; needs a content marker.

This is a one-shot mechanical script for the 2026-04-27 audit's sweep #2.

Usage:
    python3 5-machinery/validators/apply_pericope_isaiah_stub_regen.py            # dry-run
    python3 5-machinery/validators/apply_pericope_isaiah_stub_regen.py --apply    # apply
"""

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = REPO_ROOT / "data" / "pericope_index.json"

# Replacements from the audit agent's per-stub content-marker generation.
# Each entry: (book, chapter, verse) -> new_title.
# The new titles conform to canon §4: 4-10 word title proper + source
# citation in trailing parentheses; simple present active; descriptive
# non-doctrinal; incipit or theme markers.
REPLACEMENTS = {
    ("2nephi", "9", 50): "Come, Buy Wine and Milk Without Money (Isa 55:1–2)",
    ("mosiah", "12", 21): "Abinadi Quotes Isaiah on Good Tidings of Peace (Isa 52:7–10)",
    ("3nephi", "16", 18): "Watchmen Sing as the Lord Brings Again Zion (Isa 52:8–10)",
    ("3nephi", "20", 36): "Awake, O Zion — Put On Thy Beautiful Garments (Isa 52:1–3, 6–7, 11–15)",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    with open(INDEX_PATH, encoding="utf-8") as f:
        index = json.load(f)

    edits = []
    for (book, ch, verse), new_title in REPLACEMENTS.items():
        if book not in index or ch not in index[book]:
            print(f"  SKIP (not found): {book} {ch}:{verse}")
            continue
        for p in index[book][ch]:
            if p["verse"] == verse:
                old = p["title"]
                if args.apply:
                    p["title"] = new_title
                edits.append((book, ch, verse, old, new_title))
                break

    print(f"Stub regenerations: {len(edits)}")
    for book, ch, verse, old, new in edits:
        print(f"  {book} {ch}:{verse}")
        print(f"    BEFORE: {old}")
        print(f"    AFTER:  {new}")

    if args.apply:
        with open(INDEX_PATH, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"\nApplied {len(edits)} title regenerations to data/pericope_index.json")
    else:
        print("\nDRY RUN. Re-run with --apply to apply.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
