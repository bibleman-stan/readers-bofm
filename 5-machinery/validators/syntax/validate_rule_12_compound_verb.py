#!/usr/bin/env python3
"""
Validate Rule 12 (compound-verb extension) across the BofM corpus.

Rule 12 extension (added 2026-04-20):
When a modal+auxiliary (could have, would have, shall have, had, hath, etc.)
scopes over two or more coordinated participles, the participles form one
compound predicate. Splitting a coordinated participle from its shared
auxiliary strands the dangling participle.

Detection pattern:
- Line N ends with a past participle or -ing participle
- Line N contains a modal+aux pattern earlier in the line
- Line N+1 begins with "and" + another participle (no explicit subject NP)
- Line N+1 has no finite verb of its own (bare participle only)

Anti-pattern exceptions (skip merge):
- Line N+1 starts with "and [NP subject] [finite verb]"
- Line N+1 contains a finite verb after the initial participle
- Line N is a verse header (\\d+:\\d+)

Output: violations with file + line number + context.
Exit code: 0 if zero violations, 1 if violations found.

Usage:
    python3 validate_rule_12_compound_verb.py
    python3 validate_rule_12_compound_verb.py --verbose
    python3 validate_rule_12_compound_verb.py --apply
"""

import argparse
import re
import sys
from pathlib import Path

# -------------------------------------------------------------------------
# Modal+aux patterns that can scope over coordinated participles
# -------------------------------------------------------------------------
MODAL_AUX_PATTERN = re.compile(
    r"\b(?:could|would|should|shall|might|must|can|may|will|did|do|does|doth"
    r"|has|had|hath|have|hast|having|been|being|were|was|are|is|art|am)"
    r"(?:\s+(?:have|had|been|be))?\b",
    re.IGNORECASE,
)

# -------------------------------------------------------------------------
# Past-participle word list (common archaic + modern forms)
# -------------------------------------------------------------------------
PAST_PARTICIPLES = {
    "gone", "taken", "given", "seen", "heard", "spoken", "done", "been",
    "come", "brought", "sent", "made", "known", "found", "set", "put",
    "said", "told", "wrought", "prepared", "established", "appointed",
    "delivered", "preserved", "destroyed", "slain", "smitten", "beheld",
    "become", "arisen", "risen", "fallen", "eaten", "drunken", "drunk",
    "partaken", "received", "granted", "imparted", "endowed", "commanded",
    "confessed", "testified", "declared", "proclaimed", "rehearsed", "sworn",
    "promised", "taught", "retained", "obtained", "forgotten", "remembered",
    "witnessed", "observed", "perceived", "suffered", "permitted", "caused",
    "inspired", "gathered", "assembled", "consecrated", "anointed", "ordained",
    "baptized", "cleansed", "purified", "sanctified", "blessed", "cursed",
    "judged", "condemned", "justified", "redeemed", "saved", "lost",
    "hardened", "softened", "broken", "healed", "filled", "emptied",
    "lifted", "cast", "thrown", "driven", "led", "followed", "stopped",
    "ceased", "continued", "begun", "begotten", "conceived", "born",
    "dead", "written", "built", "stood", "fallen", "held", "left",
    "read", "sold", "bought", "thought", "sought", "fought", "caught",
    "taught", "brought", "felt", "kept", "slept", "wept", "crept",
    "dwelt", "knelt", "leapt", "swept", "meant", "lent", "bent", "spent",
    "sent", "rent", "went", "kept", "met", "set", "let", "cut", "put",
    "shut", "hit", "bit", "spit", "split", "spread", "shed", "fled",
    "bled", "bred", "fed", "led", "read", "sped", "pled",
    # -ed forms that commonly appear
    "united", "divided", "scattered", "scattered", "covered", "opened",
    "closed", "raised", "loosed", "bound", "freed", "forgiven", "chosen",
    "appointed", "anointed", "called", "named", "numbered", "sealed",
    "written", "recorded", "spoken", "written", "confirmed", "strengthened",
    "confounded", "scattered", "gathered", "stirred", "moved", "revealed",
    "manifested", "shown", "shewn", "proven", "proved", "convicted",
    "converted", "humbled", "exalted", "filled", "endowed", "changed",
    "transformed", "renewed", "restored", "returned", "departed", "arrived",
    "passed", "walked", "traveled", "journeyed", "sojourned", "tarried",
    "remained", "continued", "abode", "dwelt", "lived", "died", "risen",
    "awakened", "appeared", "vanished", "departed", "entered", "descended",
    "ascended", "went", "came", "arrived", "passed", "crossed",
}

# -ing participles: detect by suffix (conservative — require modal on same line)
ING_SUFFIX_PATTERN = re.compile(r"\b\w+ing\b$", re.IGNORECASE)

# -------------------------------------------------------------------------
# Subject-NP pronouns / determiners — if line N+1 has one of these between
# "and" and the participle, it's a new clause (anti-pattern)
# -------------------------------------------------------------------------
SUBJECT_WORDS = {
    "i", "he", "she", "it", "we", "ye", "they", "thou",
    "the", "a", "an", "his", "her", "their", "our", "my", "thy",
    "this", "that", "these", "those", "all", "many", "some",
    "nephi", "jacob", "lehi", "mosiah", "alma", "moroni", "mormon",
    "helaman", "samuel", "amulek", "ammon", "anti",
}

# Finite auxiliaries that indicate a new clause (anti-pattern)
FINITE_AUX = {
    "was", "were", "is", "are", "am", "be", "been", "being",
    "had", "hath", "hast", "have", "has",
    "did", "do", "does", "doth", "dost",
    "will", "would", "shall", "should", "could", "might", "must", "may", "can",
}


def strip_punct(word: str) -> str:
    """Strip leading/trailing punctuation from a word token."""
    return re.sub(r"^[\"'(,;:!?)\[\]]+|[\"'(,;:!?)\[\]]+$", "", word).lower()


def get_last_word_clean(line: str) -> str:
    """Return the last non-punctuation word of a line, lowercased."""
    words = line.rstrip().split()
    if not words:
        return ""
    return strip_punct(words[-1])


def line_ends_with_participle(line: str) -> bool:
    """Return True if the line ends with a known past participle or -ing word."""
    last = get_last_word_clean(line)
    if not last:
        return False
    if last in PAST_PARTICIPLES:
        return True
    # -ed ending (most past participles) — but not "and", "the", etc.
    if last.endswith("ed") and len(last) > 4:
        return True
    # -ing ending
    if last.endswith("ing") and len(last) > 5:
        return True
    # -en ending (common archaic past participles: fallen, broken, taken, etc.)
    if last.endswith("en") and len(last) > 4:
        return True
    return False


def line_has_modal_aux(line: str) -> bool:
    """Return True if the line contains a modal+auxiliary construction."""
    return bool(MODAL_AUX_PATTERN.search(line))


def next_line_starts_with_and_participle(line: str) -> tuple[bool, str]:
    """
    Return (True, participle_word) if the line starts with
    'and <participle>' where participle is a past/ing participle.
    Conservative: only match if no subject NP between 'and' and participle.
    """
    stripped = line.strip()
    m = re.match(r"^and\s+(\S+)", stripped, re.IGNORECASE)
    if not m:
        return False, ""
    second_word = strip_punct(m.group(1))
    if not second_word:
        return False, ""

    # Anti-pattern: second word is a subject pronoun/determiner → new clause
    if second_word in SUBJECT_WORDS:
        return False, ""

    # Check if second word is a participle
    if second_word in PAST_PARTICIPLES:
        return True, second_word
    if second_word.endswith("ed") and len(second_word) > 4:
        return True, second_word
    if second_word.endswith("ing") and len(second_word) > 5:
        return True, second_word
    if second_word.endswith("en") and len(second_word) > 4:
        return True, second_word

    return False, ""


def next_line_has_finite_verb(line: str) -> bool:
    """
    Return True if the next line contains a finite verb after the initial
    'and <participle>' — indicating it's not a bare dangling participle.
    """
    stripped = line.strip()
    # Remove leading "and <word>"
    remainder = re.sub(r"^and\s+\S+\s*", "", stripped, flags=re.IGNORECASE)
    words = remainder.split()
    for word in words:
        w = strip_punct(word)
        if w in FINITE_AUX:
            return True
        # -eth, -est archaic finite verb forms
        if w.endswith("eth") or w.endswith("est"):
            return True
    return False


def scan_file(path: Path) -> list[dict]:
    """Scan one v2-mine file for Rule 12 compound-verb violations."""
    violations = []
    lines = path.read_text(encoding="utf-8").splitlines()

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip blank lines
        if not stripped:
            continue

        # Skip verse header lines
        if re.match(r"^\d+:\d+$", stripped):
            continue

        # Line N must contain a modal+aux
        if not line_has_modal_aux(line):
            continue

        # Line N must end with a participle
        if not line_ends_with_participle(line):
            continue

        # Skip if line ends with sentence-terminating punctuation
        if stripped[-1] in ".!?":
            continue

        # Get next non-blank line
        next_idx = i + 1
        while next_idx < len(lines) and not lines[next_idx].strip():
            next_idx += 1
        if next_idx >= len(lines):
            continue

        next_line = lines[next_idx]
        next_stripped = next_line.strip()

        # Skip if next line is a verse header
        if re.match(r"^\d+:\d+$", next_stripped):
            continue

        # Line N+1 must start with "and <participle>"
        starts_with_and_pp, participle_word = next_line_starts_with_and_participle(next_line)
        if not starts_with_and_pp:
            continue

        # Anti-pattern: next line has its own finite verb
        if next_line_has_finite_verb(next_line):
            continue

        violations.append(
            {
                "file": path.name,
                "path": path,
                "line_num": i + 1,        # 1-based line number of line N
                "next_line_num": next_idx + 1,  # 1-based line number of line N+1
                "participle_word": participle_word,
                "line": line.rstrip(),
                "next_line": next_line.rstrip(),
                "next_line_raw_idx": next_idx,  # 0-based for apply
            }
        )

    return violations


def apply_merges(violations: list[dict]) -> tuple[int, int]:
    """
    Merge line N+1 upward into line N for each violation.
    Returns (merges_applied, skipped).
    Processes files grouped together, applying merges from bottom up
    so line indices remain valid.
    """
    # Group by file path
    by_file: dict[Path, list[dict]] = {}
    for v in violations:
        by_file.setdefault(v["path"], []).append(v)

    merges_applied = 0
    skipped = 0

    for path, file_violations in by_file.items():
        lines = path.read_text(encoding="utf-8").splitlines()
        # Process in reverse order so indices stay valid
        for v in sorted(file_violations, key=lambda x: x["next_line_raw_idx"], reverse=True):
            n_idx = v["line_num"] - 1          # 0-based index of line N
            next_idx = v["next_line_raw_idx"]  # 0-based index of line N+1

            # Verify lines still match (in case of overlapping violations)
            if n_idx >= len(lines) or next_idx >= len(lines):
                print(f"  SKIP (index out of range): {path.name}:{v['line_num']}")
                skipped += 1
                continue

            current_line_n = lines[n_idx].rstrip()
            current_next = lines[next_idx].rstrip()

            if current_line_n != v["line"] or current_next != v["next_line"]:
                print(f"  SKIP (line mismatch — already merged?): {path.name}:{v['line_num']}")
                skipped += 1
                continue

            # Merge: append next_line content to line N with a space
            merged = current_line_n + " " + current_next.lstrip()
            lines[n_idx] = merged
            # Remove next_line
            del lines[next_idx]
            merges_applied += 1
            print(f"  MERGED: {path.name}:{v['line_num']}")
            print(f"    WAS: {current_line_n}")
            print(f"    +  : {current_next}")
            print(f"    NOW: {merged}")

        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return merges_applied, skipped


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--apply", action="store_true",
                        help="Apply mechanical merges to canonical files")
    parser.add_argument(
        "--v2-dir",
        default="c:/Users/bibleman/repos/readers-bofm/data/text-files/v2",
    )
    args = parser.parse_args()

    v2_dir = Path(args.v2_dir)
    if not v2_dir.exists():
        print(f"ERROR: {v2_dir} not found", file=sys.stderr)
        sys.exit(2)

    all_violations = []
    files = sorted(v2_dir.glob("*-v2.txt"))
    for path in files:
        violations = scan_file(path)
        all_violations.extend(violations)

    # Report
    print("=" * 72)
    print("Rule 12 compound-verb validator — BofM v2-mine corpus")
    print("Detects: modal+aux scoping over split coordinated participles")
    print("=" * 72)
    print(f"Files scanned: {len(files)}")
    print(f"Candidates found: {len(all_violations)}")
    print()

    if all_violations:
        for v in all_violations:
            print(f"[MALFORMED]  {v['file']}:{v['line_num']} — "
                  f"coordinated participle {v['participle_word']!r} split from shared auxiliary")
            print(f"    N:   {v['line'][:100]}")
            print(f"    N+1: {v['next_line'][:100]}")
            print()

    if args.apply and all_violations:
        print("--- Applying merges ---")
        merges_applied, skipped = apply_merges(all_violations)
        print()
        print(f"Merges applied: {merges_applied}")
        print(f"Skipped:        {skipped}")
    elif not args.apply and all_violations:
        print("(Run with --apply to apply mechanical merges)")

    if not all_violations:
        print("No violations found. Rule 12 compound-verb is clean.")

    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
