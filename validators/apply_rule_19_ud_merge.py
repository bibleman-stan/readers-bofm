"""
Apply Rule 19 STRONG-MERGE-CANDIDATE findings (PROPN head, anaphoric).

Per canon §5 Rule 19: relative clauses attached to PROPN heads (Adam, Joseph,
Christ, etc.) are anaphoric — the entity is already established by name. The
relative clause is backward-pointing characterization, not new-information.
MERGE the relative clause back onto the head line.

Detector: validate_rule_19_ud.py (v2 UPOS-gated heuristic, audit 95% TP).

Filters applied here (defensive over the audit's 95% TP rate):
- Adjacency: only gap=1 (head_line + 1 == rel_line)
- Length cap: combined merged line <= 130c (Jarom-1:8-style catastrophe guard)

Skips:
- Non-adjacent gap (multi-line relative attachments — likely parse complexity)
- Over-length (catalog-merge prevention)

Re-runs the detector internally for fresh line numbers.

Usage:
    python validators/apply_rule_19_ud_merge.py            # dry-run
    python validators/apply_rule_19_ud_merge.py --apply    # write merges

Each --apply run writes a transaction log to validators/.tx/ for rollback:
    python validators/rollback.py --latest
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from validators.colometry.validate_rule_19_ud import scan_book, BOOKS  # noqa: E402
from validators.tx_log import TxLog  # noqa: E402

LENGTH_CAP = 130


def main() -> int:
    apply_mode = "--apply" in sys.argv
    by_file: dict[Path, list[tuple[int, int]]] = {}
    skipped: list[tuple[str, int, str]] = []

    total_merge = 0
    for book_id in BOOKS:
        try:
            findings = scan_book(book_id)
        except FileNotFoundError:
            continue
        merge = [f for f in findings if f.get("bucket") == "STRONG-MERGE"]
        total_merge += len(merge)
        for f in merge:
            head_line = f["head_line"]
            rel_line = f["rel_line"]
            # Resolve v2_path via book_paths
            from validators.parsing.line_mapping import book_paths
            v2_path = book_paths(f["book"])[0]

            if rel_line - head_line != 1:
                skipped.append(
                    (book_id, head_line, f"non-adjacent-gap-{rel_line - head_line}")
                )
                continue

            with open(v2_path, encoding="utf-8") as fh:
                lines = fh.read().split("\n")
            head_idx = head_line - 1
            rel_idx = rel_line - 1
            if head_idx >= len(lines) or rel_idx >= len(lines):
                skipped.append((book_id, head_line, "out-of-range"))
                continue
            cur = lines[head_idx].rstrip()
            nxt = lines[rel_idx].strip()
            merged_len = len(cur) + 1 + len(nxt)
            if merged_len > LENGTH_CAP:
                skipped.append(
                    (book_id, head_line, f"over-cap-{merged_len}c")
                )
                continue

            by_file.setdefault(v2_path, []).append((head_idx, rel_idx))

    plan_count = sum(len(items) for items in by_file.values())
    print(f"Rule 19 STRONG-MERGE detected:    {total_merge}")
    print(f"Plannable merges (gap=1, <=130c): {plan_count}")
    print(f"Skipped:                          {len(skipped)}")
    if skipped:
        print()
        for s in skipped[:15]:
            print(f"  {s}")
        if len(skipped) > 15:
            print(f"  ... +{len(skipped) - 15} more")
    print()

    if not apply_mode:
        for v2_path, items in by_file.items():
            print(f"--- {v2_path.name} ({len(items)} planned) ---")
            with open(v2_path, encoding="utf-8") as fh:
                lines = fh.read().split("\n")
            for head_idx, rel_idx in sorted(items)[:3]:
                cur = lines[head_idx].rstrip()
                nxt = lines[rel_idx].strip()
                merged = cur + " " + nxt
                print(f"  lines {head_idx + 1}-{rel_idx + 1}:")
                print(f"    -> {merged[:110]}")
        print("\n(dry run -- pass --apply to write)")
        return 0

    tx = TxLog("rule_19_merge_ud")
    total_applied = 0
    for v2_path, items in by_file.items():
        with open(v2_path, encoding="utf-8") as fh:
            content = fh.read()
        lines = content.split("\n")
        unique_items = sorted(set(items), key=lambda x: x[0], reverse=True)
        for head_idx, rel_idx in unique_items:
            if head_idx >= len(lines) or rel_idx >= len(lines):
                continue
            cur = lines[head_idx]
            nxt = lines[rel_idx]
            merged = cur.rstrip() + " " + nxt.strip()
            tx.record_merge(str(v2_path), head_idx, cur, nxt, merged)
            lines[head_idx] = merged
            del lines[rel_idx]
            total_applied += 1
        with open(v2_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        print(f"  {v2_path.name}: {len(unique_items)} merges applied")
    print(f"\nTotal Rule 19 STRONG-MERGE applied: {total_applied}")

    if total_applied:
        tx_path = tx.commit()
        print(f"\nTransaction log: {tx_path}")
        print("To undo: python validators/rollback.py --latest")

    return 0


if __name__ == "__main__":
    sys.exit(main())
