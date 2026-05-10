"""
Apply compound_coord_ud STRONG-MERGE-CANDIDATE findings to v2-mine.

Compound coordinate argument under shared verb (e.g., line N ends with NP+
comma, line N+1 starts with "and|or also <DET>..."): the second conjunct
fails own-proposition test and should rejoin the head per criterion 1
(atomic-thought) + N=2 adjudication.

UD-driven (vs apply_compound_coord.py regex): detector identifies the conj
via UD `conj` deprel and applies the antimetabole-mirror filter to keep
chiastic mirror pairs in REVIEW (1 Ne 22:7-8 Jews/Gentiles canonical case).

Re-runs the detector internally for fresh line numbers (corpus may have
shifted from earlier appliers in the same session).

Usage:
    python validators/apply_compound_coord_ud.py            # dry-run
    python validators/apply_compound_coord_ud.py --apply    # write merges

Each --apply run writes a transaction log to validators/.tx/ for rollback:
    python validators/rollback.py --latest
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from validators.colometry.validate_compound_coord_ud import scan_book, BOOKS  # noqa: E402
from validators.tx_log import TxLog  # noqa: E402

LENGTH_CAP = 130


def main() -> int:
    apply_mode = "--apply" in sys.argv
    by_file: dict[Path, list[tuple[int, int]]] = {}
    skipped: list[tuple[str, int, str]] = []

    total_strong = 0
    for book_id in BOOKS:
        try:
            findings = scan_book(book_id)
        except FileNotFoundError:
            continue
        strong = [f for f in findings if f.get("bucket") == "STRONG-MERGE-CANDIDATE"]
        total_strong += len(strong)
        for f in strong:
            v2_path = Path(f["v2_path"])
            head_line = f["head_line"]
            conj_line = f["conj_line"]

            # Defensive: only merge adjacent lines (the canonical compound-
            # coord shape). Non-adjacent findings might span scaffolding lines
            # or indicate a parse issue.
            if conj_line != head_line + 1:
                skipped.append(
                    (book_id, head_line, f"non-adjacent-{head_line}-to-{conj_line}")
                )
                continue

            by_file.setdefault(v2_path, []).append((head_line - 1, conj_line - 1))

    plan_count = sum(len(items) for items in by_file.values())
    print(f"compound_coord STRONG-MERGE detected: {total_strong}")
    print(f"Plannable merges:                     {plan_count}")
    print(f"Skipped:                              {len(skipped)}")
    if skipped:
        print()
        for s in skipped[:15]:
            print(f"  {s}")
        if len(skipped) > 15:
            print(f"  ... +{len(skipped) - 15} more")
    print()

    # Filter by length cap (combined ≤ LENGTH_CAP) — prevents catalog-merge
    # catastrophes (Jarom 1:8-style 199c merges).
    over_cap: list[tuple[str, int, int]] = []
    plan_after_cap: dict[Path, list[tuple[int, int]]] = {}
    for v2_path, items in by_file.items():
        with open(v2_path, encoding="utf-8") as fh:
            lines = fh.read().split("\n")
        for head_idx, conj_idx in items:
            if head_idx >= len(lines) or conj_idx >= len(lines):
                continue
            cur = lines[head_idx].rstrip()
            nxt = lines[conj_idx].strip()
            merged_len = len(cur) + 1 + len(nxt)
            if merged_len > LENGTH_CAP:
                over_cap.append((v2_path.name, head_idx + 1, merged_len))
                continue
            plan_after_cap.setdefault(v2_path, []).append((head_idx, conj_idx))

    cap_count = sum(len(items) for items in plan_after_cap.values())
    print(f"After length-cap (<={LENGTH_CAP}c):       {cap_count}")
    print(f"Over-cap (REVIEW):                    {len(over_cap)}")
    if over_cap:
        print()
        for c in over_cap[:5]:
            print(f"  {c[0]}:{c[1]} merged_len={c[2]}")
        if len(over_cap) > 5:
            print(f"  ... +{len(over_cap) - 5} more")
    print()

    if not apply_mode:
        for v2_path, items in plan_after_cap.items():
            print(f"--- {v2_path.name} ({len(items)} planned) ---")
            with open(v2_path, encoding="utf-8") as fh:
                lines = fh.read().split("\n")
            for head_idx, conj_idx in sorted(items)[:3]:
                cur = lines[head_idx].rstrip()
                nxt = lines[conj_idx].strip()
                merged = cur + " " + nxt
                print(f"  lines {head_idx + 1}-{conj_idx + 1}:")
                print(f"    -> {merged[:110]}")
        print("\n(dry run -- pass --apply to write)")
        return 0

    tx = TxLog("compound_coord_ud")
    total_applied = 0
    for v2_path, items in plan_after_cap.items():
        with open(v2_path, encoding="utf-8") as fh:
            content = fh.read()
        lines = content.split("\n")
        # Apply in reverse line order so indices remain valid
        unique_items = sorted(set(items), key=lambda x: x[0], reverse=True)
        for head_idx, conj_idx in unique_items:
            if head_idx >= len(lines) or conj_idx >= len(lines):
                continue
            cur = lines[head_idx]
            nxt = lines[conj_idx]
            merged = cur.rstrip() + " " + nxt.strip()
            tx.record_merge(str(v2_path), head_idx, cur, nxt, merged)
            lines[head_idx] = merged
            del lines[conj_idx]
            total_applied += 1
        with open(v2_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        print(f"  {v2_path.name}: {len(unique_items)} merges applied")
    print(f"\nTotal compound_coord merges applied: {total_applied}")

    if total_applied:
        tx_path = tx.commit()
        print(f"\nTransaction log: {tx_path}")
        print("To undo: python validators/rollback.py --latest")

    return 0


if __name__ == "__main__":
    sys.exit(main())
