"""
Apply polysyndetic verb-chain STRONG-SPLIT-CANDIDATE findings.

For each finding: split before 'and|or|nor <member_form>' on the shared line,
where member_form is the conj VERB whose split should be inserted.

Re-runs the detector internally for fresh line numbers.

Usage:
    python validators/apply_polysyndetic_verb_chain_ud.py            # dry-run
    python validators/apply_polysyndetic_verb_chain_ud.py --apply    # write

Each --apply run writes a transaction log to validators/.tx/ so the changes
can be reversed in 30 seconds if a pre-commit regression check fires:

    python validators/rollback.py --latest
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from validators.colometry.validate_polysyndetic_verb_chain_ud import (  # noqa: E402
    scan_book, BOOKS,
)
from validators.tx_log import TxLog  # noqa: E402


COORDINATORS = ["and", "or", "nor"]


def find_split_position(line: str, member_form: str) -> int | None:
    """Find char index where 'and|or|nor <member_form>' begins on the line.
    Returns None if not exactly one match (ambiguous or absent)."""
    for coord in COORDINATORS:
        pattern = re.compile(
            rf"\b{coord}\s+{re.escape(member_form)}\b",
            re.IGNORECASE,
        )
        matches = list(pattern.finditer(line))
        if len(matches) == 1:
            return matches[0].start()
    return None


def main() -> int:
    apply_mode = "--apply" in sys.argv
    by_file: dict[Path, list[tuple[int, int]]] = {}
    skipped: list[tuple[str, int, str]] = []

    total_strong = 0
    for book_id in BOOKS:
        try:
            findings, _ = scan_book(book_id)
        except FileNotFoundError:
            continue
        for f in findings:
            total_strong += 1
            v2_path = Path(f["v2_path"])
            line_idx = f["shared_line"] - 1
            with open(v2_path, encoding="utf-8") as fh:
                lines = fh.read().split("\n")
            if line_idx < 0 or line_idx >= len(lines):
                skipped.append((book_id, f["shared_line"], "out-of-range"))
                continue
            line = lines[line_idx]
            split_at = find_split_position(line, f["split_before_form"])
            if split_at is None:
                skipped.append(
                    (book_id, f["shared_line"],
                     f"no-unique-and-{f['split_before_form']!r}")
                )
                continue
            by_file.setdefault(v2_path, []).append((line_idx, split_at))

    plan_count = sum(len(items) for items in by_file.values())
    print(f"Polysyndetic verb-chain STRONG: {total_strong}")
    print(f"Plannable splits:                {plan_count}")
    print(f"Skipped (ambiguous/absent):      {len(skipped)}")
    if skipped:
        print()
        for s in skipped[:15]:
            print(f"  {s}")
        if len(skipped) > 15:
            print(f"  ... +{len(skipped) - 15} more")
    print()

    if not apply_mode:
        for v2_path, items in list(by_file.items())[:5]:
            print(f"--- {v2_path.name} ({len(items)} planned) ---")
            with open(v2_path, encoding="utf-8") as fh:
                lines = fh.read().split("\n")
            for line_idx, split_at in sorted(set(items))[:3]:
                line = lines[line_idx]
                left = line[:split_at].rstrip()
                right = line[split_at:].lstrip()
                print(f"  line {line_idx + 1}: split @ pos {split_at}")
                print(f"    -> {left[-60:] if len(left) > 60 else left!r}")
                print(f"    -> {right[:60]!r}")
        print("\n(dry run -- pass --apply to write)")
        return 0

    tx = TxLog("polysyndetic_verb_chain")
    total_applied = 0
    for v2_path, items in by_file.items():
        with open(v2_path, encoding="utf-8") as fh:
            content = fh.read()
        lines = content.split("\n")
        # Apply in reverse line order; dedupe in case of repeats per line
        unique_items = sorted(set(items), key=lambda x: (x[0], x[1]), reverse=True)
        for line_idx, split_at in unique_items:
            if line_idx >= len(lines):
                continue
            line = lines[line_idx]
            if split_at >= len(line):
                continue
            left = line[:split_at].rstrip()
            right = line[split_at:].lstrip()
            # Record BEFORE the mutation so indices are still valid
            tx.record_split(str(v2_path), line_idx, line, left, right)
            lines[line_idx] = left
            lines.insert(line_idx + 1, right)
            total_applied += 1
        with open(v2_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        print(f"  {v2_path.name}: {len(unique_items)} splits applied")
    print(f"\nTotal polysyndetic splits applied: {total_applied}")

    if total_applied:
        tx_path = tx.commit()
        print(f"\nTransaction log: {tx_path}")
        print("To undo: python validators/rollback.py --latest")

    return 0


if __name__ == "__main__":
    sys.exit(main())
