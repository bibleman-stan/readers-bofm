#!/usr/bin/env python3
"""
Validate M4-BoFM-1 (Subject-Orphan Predicate Completion) across the BoFM corpus.

M4-BoFM-1: When a v2-mine line whose content is a subject NP (closed-list-
eligible shape) terminates in `,` or `;`, AND the immediately-next line is
a bare finite predicate (auxiliary or main-verb lead, no leading connective,
no independent subject), the predicate-line MUST be merged onto the
subject-line as a single ATU. Codified 2026-05-11 as BoFM corpus
instantiation of framework M4 (canon §5 M4-BoFM-1).

This is a surface-pattern detector (Stage 1). A UD-aware Stage 2 filter
is recommended for future precision improvement but the surface heuristic
with explicit SCOPE-exclusions catches the corpus instances at acceptable
precision for the Cat A application sweep.

SCOPE-exclusions implemented as surface patterns:
- R15 vocative on line A (`O Lord,` lead)
- J3 speech-act parenthetical on line A (`saith X` tail)
- J5 save-clause on line B (`save ...` lead)
- R21 participial absolute on line B (`being|having` lead)
- Leading connective on line B (and|or|but|for|because|that|which|...)
- Length-backstop: merged > 130 chars -> REVIEW (not auto-merge)

Exit code: 0 if zero violations, 1 if violations found.
"""

import argparse
import re
import sys
from pathlib import Path


# Auxiliary or finite main-verb predicate-lead patterns (line B start)
PREDICATE_LEAD_RE = re.compile(
    r"^\s*(?:did|doth|do|shall|will|would|wilt|hath|have|hast|"
    r"may|might|must|can|could|cannot|art|is|was|were|be|been)\s+\w+",
    re.IGNORECASE,
)

# Finite main-verb lead (no auxiliary)
MAIN_VERB_LEAD_RE = re.compile(
    r"^\s*(?:came|cometh|went|spake|said|gave|took|brought|made|sent|"
    r"deliver(?:ed|eth)?|protect(?:ed|s)?|yield(?:ed|eth|s)?|sav(?:e|ed|eth|es)?|"
    r"bless(?:ed|eth|es)?|come(?:th|s)?|go(?:eth|es)?|repent(?:ed|eth|s)?|"
    r"perish(?:ed|eth|es)?|prosper(?:ed|eth|s)?|fall(?:eth|en|s)?|"
    r"ris(?:e|en|eth|es)?|stand(?:eth|s|ing)?|sit(?:teth|s|ting)?|"
    r"dwell(?:eth|ed|s)?|caus(?:e|ed|eth|es)?|"
    r"appointed|assembled|departed|drew|fled|gathered|labored|murmur(?:ed|eth)?|"
    r"reign(?:ed|eth)?|return(?:ed|s)?|suffered)\s+\w+",
    re.IGNORECASE,
)

# Leading connectives that BLOCK firing (line B is a coordinate/subordinate
# clause, not an orphan predicate)
LEADING_CONNECTIVE_RE = re.compile(
    r"^\s*(?:and|or|but|for|because|that|which|who|whoso|whosoever|when|"
    r"while|if|though|unless|until|to|in|on|at|of|with|by|from|upon|nor|"
    r"yet|so|then|therefore|wherefore|notwithstanding)\b",
    re.IGNORECASE,
)

# R21 participial-absolute lead (line B starts with participial)
PARTICIPIAL_LEAD_RE = re.compile(
    r"^\s*(?:being|having|saying|seeing|knowing|believing|hearing|"
    r"finding|coming|going|speaking|teaching|preaching)\s+\w+",
    re.IGNORECASE,
)

# J5 save-clause lead
SAVE_CLAUSE_LEAD_RE = re.compile(r"^\s*save\b", re.IGNORECASE)

# R15 vocative-only line A (bare `O X,` style)
VOCATIVE_ONLY_RE = re.compile(r"^\s*O\s+(?:Lord|God|Father|Jesus|Christ|Israel|my\s+\w+)[,]?\s*$")

# J3 speech-act parenthetical (line A ends with `saith X`)
J3_SPEECH_TAG_RE = re.compile(
    r"saith\s+(?:the\s+)?(?:Lord|God|Father|prophet|Spirit|Lord\s+of\s+Hosts)\s*[,;]?\s*$",
    re.IGNORECASE,
)


LENGTH_BACKSTOP = 130


def _line_ends_in_comma_or_semicolon(line: str) -> bool:
    stripped = line.rstrip()
    return stripped.endswith(",") or stripped.endswith(";")


def _is_orphan_predicate_line(line: str) -> bool:
    """Detect bare-predicate line: auxiliary or main-verb lead, no connective,
    no participial, no save-clause."""
    if LEADING_CONNECTIVE_RE.match(line):
        return False
    if PARTICIPIAL_LEAD_RE.match(line):
        return False
    if SAVE_CLAUSE_LEAD_RE.match(line):
        return False
    return bool(PREDICATE_LEAD_RE.match(line) or MAIN_VERB_LEAD_RE.match(line))


def _is_blocked_line_a(line: str) -> bool:
    """SCOPE-exclusions on line A: bare vocative, J3 speech-tag tail."""
    if VOCATIVE_ONLY_RE.match(line):
        return True
    if J3_SPEECH_TAG_RE.search(line):
        return True
    return False


VERSE_NUM_RE = re.compile(r"^\s*\d+:\d+\s*$")


def parse_verse_blocks(content: str):
    """Yield (block_start_line_num, block_lines) for v2-mine verse blocks."""
    lines = content.splitlines()
    block_start = None
    buf: list[tuple[int, str]] = []
    for i, line in enumerate(lines, start=1):
        if line.strip() == "":
            if buf:
                yield buf[0][0], [t[1] for t in buf]
                buf = []
            continue
        if not buf:
            block_start = i
        buf.append((i, line))
    if buf:
        yield buf[0][0], [t[1] for t in buf]


def scan_file(path: Path) -> list[dict]:
    violations = []
    content = path.read_text(encoding="utf-8")
    for block_start, block_lines in parse_verse_blocks(content):
        # Skip verse-marker lines from analysis
        content_indices = [i for i, ln in enumerate(block_lines) if not VERSE_NUM_RE.match(ln)]
        for idx_pos, i in enumerate(content_indices):
            if idx_pos + 1 >= len(content_indices):
                continue
            line_a = block_lines[i]
            j = content_indices[idx_pos + 1]
            line_b = block_lines[j]

            if not _line_ends_in_comma_or_semicolon(line_a):
                continue
            if _is_blocked_line_a(line_a):
                continue
            if not _is_orphan_predicate_line(line_b):
                continue

            merged = line_a.rstrip() + " " + line_b.lstrip()
            kind = "subject-orphan-predicate"
            if len(merged) > LENGTH_BACKSTOP:
                kind = "subject-orphan-predicate-LONG-REVIEW"

            violations.append({
                "file": path.name,
                "kind": kind,
                "start_line_num": block_start + i,
                "end_line_num": block_start + j,
                "matched_text": (line_a.strip()[:70] + " / " + line_b.strip()[:70]),
                "merged_length": len(merged),
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
    print("M4-BoFM-1 (Subject-Orphan Predicate Completion) validator")
    print("=" * 72)
    print(f"Files scanned: {len(files)}")
    print(f"Violations found: {len(all_violations)}")
    print()

    review_long = [v for v in all_violations if v["kind"].endswith("LONG-REVIEW")]
    apply_clean = [v for v in all_violations if not v["kind"].endswith("LONG-REVIEW")]

    print(f"  STRONG-MERGE-CANDIDATE (length OK): {len(apply_clean)}")
    print(f"  REVIEW-REQUIRED (merged > {LENGTH_BACKSTOP} chars): {len(review_long)}")
    print()

    for v in all_violations:
        print(
            f"[{v['kind']}]  {v['file']}:{v['start_line_num']}-{v['end_line_num']} "
            f"(merged_len={v['merged_length']})"
        )
        print(f"    {v['matched_text'][:160]}")
        print()

    print(f"RESULT: violations={len(all_violations)} status={'FAIL' if all_violations else 'CLEAN'}")
    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
