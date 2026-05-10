"""
Apply Rule 7 STRONG-SPLIT-CANDIDATE findings to v2-mine.

For each STRONG: matrix and 'that' mark sit on the same v2-mine line.
Insert a line break before 'that <modal>' in that line.

Re-runs the detector internally to get fresh line numbers (corpus may
have shifted from earlier appliers in the same session).

Usage:
    python validators/apply_rule_07_ud.py            # dry-run
    python validators/apply_rule_07_ud.py --apply    # write
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from validators.colometry.validate_rule_07_ud import scan_book, BOOKS  # noqa: E402


def find_split_position(line: str, modal: str) -> int | None:
    """Find char index where the 'that' mark introducing a modal-bearing
    clause begins. Subject pronoun typically sits between 'that' and the
    modal ('that they might be faithful'), so we locate 'that' as a word
    and match the one whose following ~50 chars contain the modal."""
    that_pat = re.compile(r"\bthat\b", re.IGNORECASE)
    matches = list(that_pat.finditer(line))
    if not matches:
        return None
    if len(matches) == 1:
        return matches[0].start()
    modal_pat = re.compile(rf"\b{re.escape(modal)}\b", re.IGNORECASE)
    candidates = [m for m in matches if modal_pat.search(line[m.start():m.start() + 60])]
    if len(candidates) == 1:
        return candidates[0].start()
    return None  # genuinely ambiguous


def main() -> int:
    apply_mode = "--apply" in sys.argv
    by_file: dict[Path, list[tuple[int, str]]] = {}
    skipped: list[tuple[str, int, str]] = []

    total_strong = 0
    for book_id in BOOKS:
        try:
            strong, _ = scan_book(book_id)
        except FileNotFoundError:
            continue
        total_strong += len(strong)
        for v in strong:
            v2_path = Path(v["v2_path"])
            with open(v2_path, encoding="utf-8") as f:
                lines = f.read().split("\n")
            line_idx = v["line"] - 1
            if line_idx < 0 or line_idx >= len(lines):
                skipped.append((book_id, v["line"], "out-of-range"))
                continue
            line = lines[line_idx]
            split_at = find_split_position(line, v["modal"])
            if split_at is None:
                skipped.append((book_id, v["line"], f"ambiguous-that-{v['modal']!r}"))
                continue
            by_file.setdefault(v2_path, []).append((line_idx, str(split_at)))

    plan_count = sum(len(items) for items in by_file.values())
    print(f"Rule 7 STRONG-SPLIT detected: {total_strong}")
    print(f"Plannable splits:             {plan_count}")
    print(f"Skipped (ambiguous):          {len(skipped)}")
    print()

    if skipped:
        print("--- skipped ---")
        for s in skipped[:10]:
            print(f"  {s}")
        if len(skipped) > 10:
            print(f"  ... +{len(skipped) - 10} more")
        print()

    if not apply_mode:
        # Show preview of first 5 splits per file
        preview = 0
        for v2_path, items in by_file.items():
            print(f"\n--- {v2_path.name} ({len(items)} planned) ---")
            with open(v2_path, encoding="utf-8") as f:
                lines = f.read().split("\n")
            for line_idx, split_at in sorted(items)[:3]:
                pos = int(split_at)
                line = lines[line_idx]
                left = line[:pos].rstrip()
                right = line[pos:].lstrip()
                print(f"  line {line_idx + 1}: split @ pos {pos}")
                print(f"    -> {left[-60:] if len(left) > 60 else left!r}")
                print(f"    -> {right[:60]!r}")
                preview += 1
                if preview >= 12:
                    break
            if preview >= 12:
                break
        print("\n(dry run — pass --apply to write)")
        return 0

    # Apply
    total_applied = 0
    for v2_path, items in by_file.items():
        with open(v2_path, encoding="utf-8") as f:
            content = f.read()
        lines = content.split("\n")
        # Apply in reverse line order to preserve indices
        for line_idx, split_at in sorted(items, key=lambda x: x[0], reverse=True):
            pos = int(split_at)
            line = lines[line_idx]
            left = line[:pos].rstrip()
            right = line[pos:].lstrip()
            lines[line_idx] = left
            lines.insert(line_idx + 1, right)
            total_applied += 1
        with open(v2_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"  {v2_path.name}: {len(items)} splits applied")
    print(f"\nTotal Rule 7 splits applied: {total_applied}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
