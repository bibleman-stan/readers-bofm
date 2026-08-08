#!/usr/bin/env python3
"""
Validate Rule 15 (Vocative Units Are Indivisible — own-line prescriptive)
across the BofM corpus.

Rule 15 (tightened 2026-04-26): true vocatives earn their own line. The
vocative may not be merged with the main clause that follows. Splitting
the vocative INTERNALLY remains forbidden.

True vocative test:
- Direct address to a 2nd-person audience.
- Surrounded by 2nd-person pronouns (ye, thee, thou, you, thy, thine) OR
  imperative verbs (remember, hearken, give ear, consider, marvel not, behold).
- Often preceded by a transitional frame (And now, Yea, Behold, Wherefore,
  And again, O).
- NOT NP-object: 'I went unto my brethren', 'I spake unto my brethren',
  'the seed of my brethren' — Rule 15 doesn't apply.

Output: lines where a true vocative is followed on the same line by a main
clause (i.e., merged when it should be on its own line).

Exit code: 0 if zero violations, 1 if violations found.

Usage:
    python3 validate_rule_15_vocative.py
    python3 validate_rule_15_vocative.py --verbose
"""

import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
CORPUS_DIR = REPO_ROOT / "data" / "text-files" / "v2"

# Vocative phrases. Each pattern matches a phrase that may serve as a vocative.
# Disambiguation from NP-object happens via context (2nd-person pronouns,
# imperatives, transitional frames) on the same line.
VOCATIVE_PHRASES = [
    r"my brethren",
    r"my beloved brethren",
    r"my son",
    r"my sons",
    r"my beloved son",
    r"my friends",
    r"my kindred",
    r"my people",
    r"my fellow servants",
    r"my children",
    r"my daughters",
    r"my brother",
    r"my sister",
    r"my brothers",
    r"my sisters",
    r"my fellow laborers",
    r"O ye Nephites",
    r"O ye Lamanites",
    r"O ye gentiles",
    r"O ye men",
    r"O ye people",
    r"O ye children",
    r"O house of Israel",
    r"O Lord",
    r"O Lord God",
    r"O Lord our God",
    r"O Lord God Almighty",
    r"O God",
    r"O Father",
    r"O ye my people",
]

# Build a single regex matching any vocative + comma + space + word.
# This finds candidates where the vocative is followed by more content on
# the same line.
VOC_ALT = "|".join(VOCATIVE_PHRASES)
# (?i) case-insensitive; allow optional 'O ' prefix on lowercase 'my'-vocatives
# Pattern: word boundary, vocative, optional comma+space, then non-empty rest
VOC_MERGED_RE = re.compile(
    r"(?P<voc>(?:^|[\s,])((?:O[, ]+)?(?:" + VOC_ALT + r")))\s*,\s+(?P<rest>\S.*)$",
    re.IGNORECASE,
)

# True-vocative signal patterns — if any of these occur in the same line,
# the candidate is a TRUE vocative (not an NP-object).
SECOND_PERSON_RE = re.compile(
    r"\b(ye|thee|thou|thy|thine|your|yourself|yourselves)\b", re.IGNORECASE
)
IMPERATIVE_OPENERS_RE = re.compile(
    r"\b(remember|hearken|give ear|consider|marvel(?:l)?ed?|marvel(?:l)?\s|behold|repent|cry|return|come unto|hear ye|listen|wo unto|blessed are)\b",
    re.IGNORECASE,
)
# Transitional frames that often precede a true vocative.
TRANSITIONAL_FRAME_RE = re.compile(
    r"^\s*(And now|Yea|Behold|Wherefore|And again|Therefore|And ye|And thou|But|For|Now)[\s,]",
    re.IGNORECASE,
)
# I-perspective volitional/declarative — also often signals true vocative.
I_VOLITIONAL_RE = re.compile(
    r"\bI\s+(would|say|exhort|desire|beseech|pray|fear|rejoice|marvel)\b",
    re.IGNORECASE,
)

# NP-object disqualifiers — if these patterns appear before the vocative-shaped
# phrase, it's an NP-object, not a true vocative.
NP_OBJECT_LEFT_CONTEXT_RE = re.compile(
    r"\b(unto|with|of|among|to|for|by|upon|against|over|behind|before|after|over|seeing|loved|persuade|spake to|spake unto|went to|went unto|commanded|sent|hath sent|preach unto|preached unto|teach|preached|spake|cried unto|rebuked|exhort|exhorted)\s*$",
    re.IGNORECASE,
)


def is_true_vocative(line: str, voc_start: int) -> bool:
    """Decide whether the matched vocative-shaped phrase is a TRUE vocative
    or an NP-object. Returns True if true vocative."""
    left = line[:voc_start]
    right = line[voc_start:]

    # Disqualifier: NP-object preceding preposition/verb-of-motion/etc.
    if NP_OBJECT_LEFT_CONTEXT_RE.search(left):
        return False

    # Qualifier: 2nd-person pronoun present in line
    if SECOND_PERSON_RE.search(line):
        return True

    # Qualifier: imperative shape
    if IMPERATIVE_OPENERS_RE.search(right):
        return True

    # Qualifier: transitional frame opening the line + I-volitional pattern
    if TRANSITIONAL_FRAME_RE.match(line) and I_VOLITIONAL_RE.search(line):
        return True

    # Qualifier: line starts with the vocative directly (capital), strong signal
    # of address-opening.
    line_lstripped = line.lstrip()
    if line_lstripped[:1].isupper() and any(
        line_lstripped.lower().startswith(v.lower())
        or line_lstripped.lower().startswith("o " + v.lower())
        for v in VOCATIVE_PHRASES
    ):
        # Address-opening (e.g., "My son, I would..."). True vocative.
        return True

    return False


def scan_file(path: Path):
    """Return list of (line_no, line, vocative_phrase) violations."""
    violations = []
    with open(path, encoding="utf-8") as f:
        for i, raw in enumerate(f, start=1):
            line = raw.rstrip("\n")
            for m in VOC_MERGED_RE.finditer(line):
                voc_start = m.start("voc")
                voc_phrase = m.group("voc").strip(", \t")
                rest = m.group("rest").strip()
                # Filter out pure-punctuation tails or trailing single
                # appositive elaboration that's still "vocative-only" semantically.
                if re.match(r"^[\W_]+$", rest):
                    continue
                # Filter out "<voc>, <voc>" appositive vocatives extending
                # the same vocative (e.g., "O Lord, my God,") — those are
                # legitimately on one line as one extended vocative unit.
                if any(
                    re.match(r"^(my|O |of )", rest, re.IGNORECASE)
                    and re.search(r"^[\w ,']{0,40},\s*$", rest)
                    for _ in [None]
                ):
                    continue
                if is_true_vocative(line, voc_start):
                    violations.append((i, line, voc_phrase))
                    break  # one violation per line is enough
    return violations


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    print("=" * 72)
    print("Rule 15 (Vocative Units — own-line prescriptive) validator")
    print("=" * 72)
    print()

    files = sorted(CORPUS_DIR.glob("*-v2.txt"))
    total = 0
    for path in files:
        violations = scan_file(path)
        if not violations:
            continue
        if args.verbose:
            for line_no, line, voc in violations:
                print(f"[DEVIATION]  {path.name}:{line_no}")
                print(f"    {line[:120]}")
                print(f"    Vocative: {voc}")
                print()
        total += len(violations)

    print(f"Files scanned: {len(files)}")
    print(f"Violations found: {total}")
    print()

    if total == 0:
        print("No violations found. Rule 15 (vocative own-line) compliance is clean.")
        return 0

    if not args.verbose:
        print(
            "Re-run with --verbose to see each violation. Each is a true vocative "
            "merged with its main clause on the same line; per Rule 15, true "
            "vocatives earn their own line."
        )
    return 1


if __name__ == "__main__":
    sys.exit(main())
