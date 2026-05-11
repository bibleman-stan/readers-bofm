#!/usr/bin/env python3
"""
Validate Rule 18a (Patriarch-Deity-Triad Fixed Formula) across the BoFM corpus.

R18a: The deity-triad formula `God of Abraham ... Isaac ... Jacob` (with any
attested distribution variant: full, partially-distributed, compressed) MUST
appear whole on a single v2-mine line. The triad functions as a single fixed
referring expression to YHWH; severing it across lines fractures a unitary
deity-reference.

Exclusion: "Abraham, Isaac, and Jacob" lacking the "God of" anchor is a
coordinate personal-name list (R18a does not fire; governed by default
coordinate-NP-object merge per canon §1.9 scope).

Detection: per verse-block, find the spanning sequence "God of Abraham" ...
"Isaac" ... "Jacob" (any order-preserving match with arbitrary intervening
tokens). If matched and the match spans multiple non-empty content lines
within the same verse block, flag as violation.

Exit code: 0 if zero violations, 1 if violations found.
"""

import argparse
import re
import sys
from pathlib import Path


# Pattern: "God of Abraham" anchor + later "Isaac" + later "Jacob"
# Non-greedy intervening content allowed. Case-insensitive.
TRIAD_PATTERN = re.compile(
    r"\bGod\s+of\s+Abraham\b.{0,200}?\bIsaac\b.{0,200}?\bJacob\b",
    re.IGNORECASE | re.DOTALL,
)


def parse_verse_blocks(content: str):
    """
    Yield (block_start_line_num, block_text, line_offsets_within_block).
    Blocks are blank-line-separated runs in v2-mine files.
    Each block_text retains its newlines so offset math is straightforward.
    line_offsets_within_block: list of (relative_line_num, char_start, char_end).
    """
    lines = content.splitlines(keepends=True)
    block_start = None
    buf = []
    line_offsets = []
    char_pos = 0
    line_idx = 0
    for i, line in enumerate(lines, start=1):
        if line.strip() == "":
            if buf:
                yield block_start, "".join(buf), line_offsets
                buf = []
                line_offsets = []
                char_pos = 0
                block_start = None
            continue
        if not buf:
            block_start = i
            char_pos = 0
            line_idx = 0
        line_offsets.append((line_idx, char_pos, char_pos + len(line)))
        char_pos += len(line)
        line_idx += 1
        buf.append(line)
    if buf:
        yield block_start, "".join(buf), line_offsets


def find_line_for_offset(line_offsets, offset):
    for rel_idx, start, end in line_offsets:
        if start <= offset < end:
            return rel_idx
    return -1


# R18a predicate-completion extension: detect bare-predicate lines orphaned
# from a triad-subject on the immediately-prior line.
# A "bare predicate" is a line starting with a finite-verb auxiliary or
# predicate verb without a leading subject or connective.
PREDICATE_LEAD_RE = re.compile(
    r"^\s*(did|doth|do|shall|will|would|hath|have|hast|may|might|must|"
    r"protect|deliver|yield(?:eth|s)?|sav(?:e|eth|es)?|bless(?:eth|es)?|"
    r"come(?:th|s)?|go(?:eth|es)?)\s+\w+",
    re.IGNORECASE,
)
LEADING_CONNECTIVE_RE = re.compile(
    r"^\s*(and|or|but|for|because|that|which|who|whoso|whosoever|when|"
    r"while|if|though|unless|until|to|in|on|at|of|with|by|from|upon)\b",
    re.IGNORECASE,
)


def _line_ends_in_comma_or_semicolon(line: str) -> bool:
    stripped = line.rstrip()
    return stripped.endswith(",") or stripped.endswith(";")


def _is_orphan_predicate_line(line: str) -> bool:
    """Detect a bare-predicate line lacking subject + connective.

    Catches cases like "did deliver them out of bondage." where the
    grammatical subject sits on the prior line (predicate-completion
    fragmenting per R18a sub-rule).
    """
    if LEADING_CONNECTIVE_RE.match(line):
        return False
    return bool(PREDICATE_LEAD_RE.match(line))


def scan_file(path: Path) -> list[dict]:
    violations = []
    content = path.read_text(encoding="utf-8")
    for block_start, block_text, line_offsets in parse_verse_blocks(content):
        # Cache block lines indexed by relative position for predicate-completion lookup.
        block_lines = block_text.splitlines()
        for match in TRIAD_PATTERN.finditer(block_text):
            start_rel = find_line_for_offset(line_offsets, match.start())
            end_rel = find_line_for_offset(line_offsets, match.end() - 1)
            if start_rel != end_rel:
                # Triad itself split across lines (the base R18a violation).
                violations.append({
                    "file": path.name,
                    "kind": "triad-split",
                    "start_line_num": block_start + start_rel,
                    "end_line_num": block_start + end_rel,
                    "matched_text": match.group(0).replace("\n", " / ").strip(),
                })
                continue
            # Triad fits on one line. Check predicate-completion extension:
            # is the immediately-following non-empty block line a bare predicate?
            triad_line = block_lines[start_rel] if start_rel < len(block_lines) else ""
            if not _line_ends_in_comma_or_semicolon(triad_line):
                continue
            next_rel = start_rel + 1
            if next_rel >= len(block_lines):
                continue
            next_line = block_lines[next_rel]
            if _is_orphan_predicate_line(next_line):
                violations.append({
                    "file": path.name,
                    "kind": "predicate-completion-orphan",
                    "start_line_num": block_start + start_rel,
                    "end_line_num": block_start + next_rel,
                    "matched_text": (triad_line.strip()[:60] + " / " +
                                     next_line.strip()[:60]),
                })
    return violations


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--v2-dir",
        default="c:/Users/bibleman/repos/readers-bofm/data/text-files/v2-mine",
    )
    args = ap.parse_args()

    v2_dir = Path(args.v2_dir)
    if not v2_dir.exists():
        print(f"ERROR: {v2_dir} not found", file=sys.stderr)
        sys.exit(2)

    all_violations = []
    files = sorted(v2_dir.glob("*-v2.txt"))
    for path in files:
        all_violations.extend(scan_file(path))

    print("=" * 72)
    print("Rule 18a (Patriarch-Deity-Triad) validator")
    print("=" * 72)
    print(f"Files scanned: {len(files)}")
    print(f"Violations found: {len(all_violations)}")
    print()

    for v in all_violations:
        kind = v.get("kind", "triad-split")
        if kind == "triad-split":
            label = "triad split across lines"
        elif kind == "predicate-completion-orphan":
            label = "predicate-completion: triad-subject orphaned from bare predicate"
        else:
            label = kind
        print(
            f"[DEVIATION]  {v['file']}:{v['start_line_num']}-{v['end_line_num']} "
            f"-- {label}:"
        )
        print(f"    {v['matched_text'][:160]}")
        print()

    if not all_violations:
        print("No violations found. Rule 18a compliance is clean.")

    print(f"\nRESULT: violations={len(all_violations)} status={'FAIL' if all_violations else 'CLEAN'}")
    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
