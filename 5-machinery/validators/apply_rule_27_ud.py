"""
Apply Rule 27 findings to v2-mine.

Two modes:
  (default) STRONG-SPLIT mode  — split before 'insomuch that' on merged lines
  --merge                       — join split lines back to matrix clause

Re-runs the detector internally for fresh line numbers each time.

Usage:
    python 5-machinery/validators/apply_rule_27_ud.py                 # dry-run splits
    python 5-machinery/validators/apply_rule_27_ud.py --apply         # write splits
    python 5-machinery/validators/apply_rule_27_ud.py --merge         # dry-run merges
    python 5-machinery/validators/apply_rule_27_ud.py --merge --apply # write merges

Each --apply run writes a transaction log to 5-machinery/validators/.tx/ so changes
can be reversed quickly:

    python 5-machinery/validators/rollback.py --latest
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from validators.colometry.validate_rule_27_ud import scan_book, BOOKS  # noqa: E402
from validators.parsing.line_mapping import book_paths                  # noqa: E402
from validators.tx_log import TxLog                                     # noqa: E402


# Match "insomuch that" with optional comma between (used by split mode)
INSOMUCH_THAT_PATTERN = re.compile(r"\binsomuch\b\s*(?:,\s*)?that\b", re.IGNORECASE)


def find_split_position(line: str) -> int | None:
    """Find char index where 'insomuch that' begins (for split mode)."""
    matches = list(INSOMUCH_THAT_PATTERN.finditer(line))
    if len(matches) != 1:
        return None
    return matches[0].start()


# ---------------------------------------------------------------------------
# Split mode (STRONG-SPLIT-CANDIDATE)
# ---------------------------------------------------------------------------

def run_split(apply_mode: bool) -> int:
    """Plan and optionally apply STRONG-SPLIT-CANDIDATE findings."""
    by_file: dict[Path, list[tuple[int, int]]] = {}  # {v2_path: [(line_idx, split_at), ...]}
    skipped: list[tuple[str, int, str]] = []

    total_strong = 0
    for book_id in BOOKS:
        try:
            findings = scan_book(book_id)
        except FileNotFoundError:
            continue
        v2_path, _ = book_paths(book_id)
        for f in findings:
            if f.get("bucket") != "STRONG-SPLIT-CANDIDATE":
                continue
            total_strong += 1

            line_num = f.get("matrix_line") or f.get("line") or f.get("insomuch_line")
            if line_num is None:
                skipped.append((book_id, 0, "no-line-in-finding"))
                continue
            line_idx = line_num - 1

            with open(v2_path, encoding="utf-8") as fh:
                lines = fh.read().split("\n")
            if line_idx < 0 or line_idx >= len(lines):
                skipped.append((book_id, line_num, "out-of-range"))
                continue
            line = lines[line_idx]
            split_at = find_split_position(line)
            if split_at is None:
                skipped.append((book_id, line_num, "no-insomuch-that-on-line"))
                continue
            by_file.setdefault(v2_path, []).append((line_idx, split_at))

    plan_count = sum(len(items) for items in by_file.values())
    print(f"Rule 27 STRONG-SPLIT detected: {total_strong}")
    print(f"Plannable splits:              {plan_count}")
    print(f"Skipped:                       {len(skipped)}")
    if skipped:
        print()
        for s in skipped[:10]:
            print(f"  {s}")
    print()

    if not apply_mode:
        for v2_path, items in by_file.items():
            print(f"--- {v2_path.name} ({len(items)} planned) ---")
            with open(v2_path, encoding="utf-8") as fh:
                lines = fh.read().split("\n")
            for line_idx, split_at in sorted(items)[:3]:
                line = lines[line_idx]
                left = line[:split_at].rstrip()
                right = line[split_at:].lstrip()
                print(f"  line {line_idx + 1}: split @ pos {split_at}")
                print(f"    -> {left[-60:] if len(left) > 60 else left!r}")
                print(f"    -> {right[:60]!r}")
        print("\n(dry run — pass --apply to write)")
        return 0

    total_applied = 0
    for v2_path, items in by_file.items():
        with open(v2_path, encoding="utf-8") as fh:
            content = fh.read()
        lines = content.split("\n")
        for line_idx, split_at in sorted(items, key=lambda x: x[0], reverse=True):
            line = lines[line_idx]
            left = line[:split_at].rstrip()
            right = line[split_at:].lstrip()
            lines[line_idx] = left
            lines.insert(line_idx + 1, right)
            total_applied += 1
        with open(v2_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        print(f"  {v2_path.name}: {len(items)} splits applied")
    print(f"\nTotal Rule 27 splits applied: {total_applied}")
    return 0


# ---------------------------------------------------------------------------
# Merge mode (STRONG-MERGE-CANDIDATE)
# ---------------------------------------------------------------------------

def run_merge(apply_mode: bool) -> int:
    """Plan and optionally apply STRONG-MERGE-CANDIDATE findings.

    Each finding has:
      matrix_line  — 1-based line number of the matrix clause (line N)
      mark_line    — 1-based line number of the 'insomuch that ...' clause (line N+1)

    We merge by joining line N and line N+1 with a single space, producing:
      "...matrix clause insomuch that result clause"

    Only findings where mark_line == matrix_line + 1 are applied.
    Non-adjacent cases (gap > 1) are skipped with reason "non-adjacent".
    """
    # Map v2_path -> list of matrix line_idx (0-based)
    by_file: dict[Path, list[int]] = {}
    skipped: list[tuple[str, int, str]] = []
    preview_recs: list[dict] = []   # kept for dry-run output regardless of file grouping

    total_strong = 0
    for book_id in BOOKS:
        try:
            findings = scan_book(book_id)
        except FileNotFoundError:
            continue
        v2_path, _ = book_paths(book_id)
        for f in findings:
            if f.get("bucket") != "STRONG-MERGE-CANDIDATE":
                continue
            total_strong += 1

            matrix_line = f.get("matrix_line")
            mark_line = f.get("mark_line")
            if matrix_line is None or mark_line is None:
                skipped.append((book_id, 0, "missing-line-fields"))
                continue

            # Adjacency check: the split insomuch-that line must immediately
            # follow the matrix line in the source file.
            if mark_line != matrix_line + 1:
                skipped.append((book_id, matrix_line,
                                 f"non-adjacent (matrix={matrix_line} mark={mark_line})"))
                continue

            matrix_idx = matrix_line - 1   # 0-based

            # Store for preview even before file dedup
            preview_recs.append({
                "book": book_id,
                "v2_path": v2_path,
                "matrix_idx": matrix_idx,
                "matrix_line": matrix_line,
                "mark_line": mark_line,
                "sent_text": f.get("sent_text", ""),
                "rc_words": f.get("rc_words", "?"),
                "subj": f.get("subj_continuity", "?"),
            })
            by_file.setdefault(v2_path, []).append(matrix_idx)

    plan_count = sum(len(set(idxs)) for idxs in by_file.values())
    print(f"Rule 27 STRONG-MERGE detected:  {total_strong}")
    print(f"Plannable merges (gap=1):       {plan_count}")
    print(f"Skipped:                        {len(skipped)}")
    if skipped:
        print()
        print("--- skipped ---")
        for s in skipped[:10]:
            print(f"  {s}")
        if len(skipped) > 10:
            print(f"  ... +{len(skipped) - 10} more")
    print()

    if not apply_mode:
        # Show up to 8 sample merges with before/after text
        print("--- dry-run preview (up to 8 samples) ---")
        shown = 0
        seen_paths: dict[Path, list[str]] = {}
        for rec in preview_recs:
            v2_path = rec["v2_path"]
            if v2_path not in seen_paths:
                with open(v2_path, encoding="utf-8") as fh:
                    seen_paths[v2_path] = fh.read().split("\n")
            lines = seen_paths[v2_path]
            a_idx = rec["matrix_idx"]
            b_idx = a_idx + 1
            if b_idx >= len(lines):
                continue
            a = lines[a_idx].rstrip()
            b = lines[b_idx].strip()
            merged = a + " " + b
            print(f"  [{rec['book']}] line {rec['matrix_line']}+{rec['mark_line']}"
                  f"  rc_words={rec['rc_words']}  subj={rec['subj']}")
            print(f"    matrix:  {a[-80:] if len(a) > 80 else a!r}")
            print(f"    + insomuch: {b[:80]!r}")
            print(f"    merged:  {merged[-100:] if len(merged) > 100 else merged!r}")
            print()
            shown += 1
            if shown >= 8:
                break

        print(f"(dry run — pass --apply to write {plan_count} merges)")
        return 0

    # --- Apply ---
    tx = TxLog("rule_27_merge")
    total_applied = 0
    for v2_path, items in by_file.items():
        with open(v2_path, encoding="utf-8") as fh:
            content = fh.read()
        lines = content.split("\n")
        # Reverse order so higher line indices don't shift lower ones
        for line_idx in sorted(set(items), reverse=True):
            if line_idx + 1 >= len(lines):
                continue
            a = lines[line_idx].rstrip()
            b = lines[line_idx + 1].strip()
            merged = a + " " + b
            # Record before mutating (indices still valid at this point)
            tx.record_merge(str(v2_path), line_idx, lines[line_idx], lines[line_idx + 1], merged)
            lines[line_idx] = merged
            del lines[line_idx + 1]
            total_applied += 1
        with open(v2_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        print(f"  {v2_path.name}: {len(set(items))} merges applied")

    print(f"\nTotal Rule 27 merges applied: {total_applied}")

    if total_applied:
        tx_path = tx.commit()
        print(f"\nTransaction log: {tx_path}")
        print("To undo: python 5-machinery/validators/rollback.py --latest")

    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    merge_mode = "--merge" in sys.argv
    apply_mode = "--apply" in sys.argv

    if merge_mode:
        return run_merge(apply_mode)
    else:
        return run_split(apply_mode)


if __name__ == "__main__":
    sys.exit(main())
