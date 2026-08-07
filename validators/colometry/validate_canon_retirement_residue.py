#!/usr/bin/env python3
"""
Detect carry-forward-inertia residue: active references to retired/
withdrawn/rescinded canon items in canon, CLAUDE.md, and docs/.

Triggered by Stan's 2026-04-27 catch (sibling-project GNT-Claude precedent
applied to BofM): when one canon section retires/withdraws/rescinds
something, references in OTHER sections often persist, contradicting the
retirement. The reactive cleanup ("oh, residue") is what this validator
prevents from going unnoticed.

Approach:
  1. Hardcoded list of retired terms with their retirement markers.
  2. Scan canon + CLAUDE.md + docs/ for occurrences of each term.
  3. Filter out:
     - Lines within retirement notices (contain "retired"/"withdrawn"/etc.).
     - Lines in §8 / §10 Update Log entries (historical record).
     - Lines explicitly qualified ("withdrawn doctrinal-weight bump").
  4. Report remaining as RESIDUE candidates.

Maintenance: when adding a new retirement to the canon, add a corresponding
entry to RETIRED_TERMS below. The validator catches future residue without
relying on Claude's memory.

Exit code: 0 if zero residue; 1 if residue found.

Usage:
    python3 validate_canon_retirement_residue.py
    python3 validate_canon_retirement_residue.py --verbose
"""

import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

# Files to scan
SCAN_PATHS = [
    REPO_ROOT / "1-method" / "colometry-canon.md",
    REPO_ROOT / "1-method" / "pericope-canon.md",
    REPO_ROOT / "CLAUDE.md",
] + sorted((REPO_ROOT / "3-project").glob("*.md"))


# Retired/withdrawn/rescinded canon items.
# Each entry: (search-pattern, retirement-date, brief-note).
# Patterns are case-insensitive regex; should match the term as it would
# appear in active prose.
RETIRED_TERMS = [
    {
        "pattern": r"\bbreath\s+(?:test|unit|tests|units)\b",
        "term": "breath test/unit",
        "retired": "2026-04-19 PM (full retirement scope confirmed 2026-04-27)",
        "note": "Retired as named diagnostic; not foundational; not pragmatically relevant.",
    },
    {
        "pattern": r"atomic[\s-]+breath",
        "term": "atomic breath (foundational test)",
        "retired": "2026-04-27 (residue from 2026-04-19 retirement)",
        "note": "CLAUDE.md/handoffs framing; never load-bearing in pragmatic application.",
    },
    {
        "pattern": r"doctrinal[\s-]+weight\s+(?:bump|candidate|candidates|category|categor)",
        "term": "doctrinal-weight (category)",
        "retired": "2026-04-23 AM (hostile audit)",
        "note": "Enumerated-list category masquerading as mechanical; failed identifiability test.",
    },
    {
        "pattern": r"\bstab[\s-]?commata\b",
        "term": "stab-commata register",
        "retired": "2026-04-22 (post-audit)",
        "note": "SCOPE exclusions consumed the domain; named BofM passages handled by justification 1.",
    },
    {
        "pattern": r"\bEP[\s-]?6\b",
        "term": "EP-6 Exception/Save Clause",
        "retired": "2026-04-23 PM (hostile audit)",
        "note": "70% counterexample rate against spot-check-derived prediction.",
    },
    {
        "pattern": r"\bemotion[\s-]?class\b|\bEMOTION_VERBS\b",
        "term": "emotion-class extension to Rule 17",
        "retired": "2026-04-26 PM (hostile audit)",
        "note": "5 of 8 verbs had zero corpus instances; direct contradiction with line 655 SCOPE sharpening.",
    },
    {
        "pattern": r"\bWayyehi\b",
        "term": "Wayyehi terminology (Hebrew-parallelism import)",
        "retired": "2026-04-22 (Stan rejection of Hebrew-parallelism imports)",
        "note": "Patterns exist as AICTP-family variants; Hebrew-derived labels rejected per feedback_rhetoric_bandwagon.",
    },
    # Add new entries here when retiring/withdrawing/rescinding canon items.
]


# Markers indicating a line is RETIREMENT CONTEXT (mention of the retired
# term in a discussion of the retirement itself — these are legitimate, not
# residue).
RETIREMENT_MARKERS_RE = re.compile(
    r"\b(retired|retire|retires|withdrawn|withdraw|rescinded|rescind|RETRACT(?:ED)?|REJECT(?:ED)?|deprecated|deleted|RETIRED|WITHDRAWN|RESCINDED)\b",
    re.IGNORECASE,
)

# §8 / §10 Update Log entries are historical record — references to retired
# terms there are legitimate. Match Update Log section markers.
UPDATE_LOG_MARKERS_RE = re.compile(
    r"^(?:## (?:8|10)\.\s+Update Log|### \d{4}-\d{2}-\d{2}|See `archive/|Prior history)",
    re.IGNORECASE,
)


def is_retirement_context_line(line: str) -> bool:
    """Line is retirement-context if it contains a retirement marker."""
    return bool(RETIREMENT_MARKERS_RE.search(line))


def find_update_log_ranges(lines: list[str]) -> list[tuple[int, int]]:
    """Return (start_line, end_line) ranges for §8/§10 Update Log sections.
    These are historical record; references inside them are legitimate."""
    ranges = []
    in_log = False
    log_start = 0
    for i, line in enumerate(lines):
        if re.match(r"^## (?:8|10)\.\s+Update Log", line):
            in_log = True
            log_start = i
        elif in_log and re.match(r"^## \d+\.\s+", line):
            # New §N. section; log ends here
            ranges.append((log_start, i - 1))
            in_log = False
    if in_log:
        ranges.append((log_start, len(lines) - 1))
    return ranges


# Files that are retirement-context in their ENTIRETY. The retraction log's whole
# job is to name what was retired and why, so every mention in it is historical
# record — the same exemption find_update_log_ranges() already grants to §8/§10
# Update Log sections, applied at file scope.
#
# It moved from the repo root into the scanned doc tree on 2026-08-07 and so
# entered this validator's glob for the first time, producing 14 instant
# "violations". Those were an artefact of the move, not new residue: this
# validator has never been meant to police the retraction log.
#
# Matched against Path.name — BARE FILENAMES ONLY, never a path. (A mechanical
# repoint briefly rewrote this to "2-evidence/retraction-log.md", which silently
# disabled the exemption: path.name is never a path, so nothing matched and the
# 14 false positives came back.)
WHOLE_FILE_RETIREMENT_CONTEXT = {"retraction-log.md"}


def scan_file(path: Path) -> list[dict]:
    """Find residue references in path."""
    if not path.exists():
        return []
    if path.name in WHOLE_FILE_RETIREMENT_CONTEXT:
        return []
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    log_ranges = find_update_log_ranges(lines)

    def in_log(i):
        return any(start <= i <= end for start, end in log_ranges)

    residue = []
    for entry in RETIRED_TERMS:
        pat = re.compile(entry["pattern"], re.IGNORECASE)
        for i, line in enumerate(lines):
            if not pat.search(line):
                continue
            if is_retirement_context_line(line):
                continue
            if in_log(i):
                continue
            residue.append({
                "file": path.relative_to(REPO_ROOT),
                "line": i + 1,
                "term": entry["term"],
                "retired": entry["retired"],
                "text": line.rstrip(),
            })
    return residue


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    print("=" * 72)
    print("Canon-retirement residue validator")
    print("=" * 72)
    print()
    print(f"Scanning {len(SCAN_PATHS)} files for active references to "
          f"{len(RETIRED_TERMS)} retired terms...")
    print()

    all_residue = []
    for path in SCAN_PATHS:
        all_residue.extend(scan_file(path))

    if not all_residue:
        print("Files scanned: " + str(len(SCAN_PATHS)))
        print("Violations found: 0")
        print()
        print("No residue. All retired terms are confined to retirement notices "
              "and §8/§10 Update Log entries.")
        return 0

    print(f"Files scanned: {len(SCAN_PATHS)}")
    print(f"Violations found: {len(all_residue)}")
    print()

    if args.verbose:
        for r in all_residue:
            print(f"[DEVIATION]  {r['file']}:{r['line']} [{r['term']}]")
            print(f"    {r['text'][:120]}")
            print(f"    Retired: {r['retired']}")
            print()
    else:
        # Group by term
        by_term = {}
        for r in all_residue:
            by_term.setdefault(r["term"], []).append(r)
        for term, rs in by_term.items():
            print(f"  {term}: {len(rs)} residue reference{'s' if len(rs) != 1 else ''}")
            for r in rs[:3]:
                print(f"    {r['file']}:{r['line']}")
            if len(rs) > 3:
                print(f"    ... +{len(rs) - 3} more")
            print()
        print("Re-run with --verbose for full context.")

    print("Each violation is an active reference to a term that was retired/")
    print("withdrawn/rescinded in canon. Either:")
    print("  (a) Update the line to reflect the retirement (preferred), OR")
    print("  (b) Mark the line as retirement-context if it discusses the")
    print("      retirement itself (not as if the term were active).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
