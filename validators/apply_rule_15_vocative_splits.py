#!/usr/bin/env python3
"""
Apply Rule 15 vocative-merged → vocative-own-line splits to the corpus.

Driven by the validate_rule_15_vocative.py findings: each violation is a
TRUE vocative followed on the same line by a main clause. The fix is to
split the line at the vocative-comma.

This is a one-shot mechanical script for the 2026-04-26 vocative sweep.
For ongoing detection use validate_rule_15_vocative.py.

Usage:
    python3 validators/apply_rule_15_vocative_splits.py            # dry-run
    python3 validators/apply_rule_15_vocative_splits.py --apply    # actually edit
"""

import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = REPO_ROOT / "data" / "text-files" / "v2-mine"

# Same vocative + true-vocative-test as the validator. Re-imported here so
# this script is independent.
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
    r"my beloved brother",
    r"O ye Nephites",
    r"O ye Lamanites",
    r"O ye gentiles",
    r"O ye men",
    r"O ye people",
    r"O ye children",
    r"O ye my people",
    r"O house of Israel",
    r"O Lord",
    r"O Lord God",
    r"O Lord our God",
    r"O Lord God Almighty",
    r"O God",
    r"O Father",
    r"O my brethren",
    r"O my beloved son",
    r"O my beloved",
    r"O thou child of hell",
]

VOC_ALT = "|".join(VOCATIVE_PHRASES)
VOC_MERGED_RE = re.compile(
    r"(?P<voc>(?:^|[\s,])((?:O[, ]+)?(?:" + VOC_ALT + r")))(?P<voc_tail>(?:,\s*(?:[A-Z][a-z]+))?)\s*,\s+(?P<rest>\S.*)$",
    re.IGNORECASE,
)

SECOND_PERSON_RE = re.compile(
    r"\b(ye|thee|thou|thy|thine|your|yourself|yourselves)\b", re.IGNORECASE
)
IMPERATIVE_OPENERS_RE = re.compile(
    r"\b(remember|hearken|give ear|consider|marvel(?:l)?ed?|marvel(?:l)?\s|behold|repent|cry|return|come unto|hear ye|listen|wo unto|blessed are|be of good cheer|be faithful|pray for)\b",
    re.IGNORECASE,
)
TRANSITIONAL_FRAME_RE = re.compile(
    r"^\s*(And now|Yea|Behold|Wherefore|And again|Therefore|And ye|And thou|But|For|Now|O|My)[\s,]",
    re.IGNORECASE,
)
I_VOLITIONAL_RE = re.compile(
    r"\bI\s+(would|say|exhort|desire|beseech|pray|fear|rejoice|marvel|judge|speak|write|recommend|command|wish|will praise|will return|have|thank|come|cannot|do|can)\b",
    re.IGNORECASE,
)
NP_OBJECT_LEFT_CONTEXT_RE = re.compile(
    r"\b(unto|with|of|among|to|for|by|upon|against|over|behind|before|after|seeing|loved|persuade|spake to|spake unto|went to|went unto|commanded|sent|hath sent|preach unto|preached unto|teach|preached|spake|cried unto|rebuked|exhort|exhorted|love|trust)\s*$",
    re.IGNORECASE,
)


def is_true_vocative(line: str, voc_start: int) -> bool:
    left = line[:voc_start]
    right = line[voc_start:]
    if NP_OBJECT_LEFT_CONTEXT_RE.search(left):
        return False
    if SECOND_PERSON_RE.search(line):
        return True
    if IMPERATIVE_OPENERS_RE.search(right):
        return True
    if TRANSITIONAL_FRAME_RE.match(line) and I_VOLITIONAL_RE.search(line):
        return True
    line_lstripped = line.lstrip()
    if line_lstripped[:1].isupper() and any(
        line_lstripped.lower().startswith(v.lower())
        or line_lstripped.lower().startswith("o " + v.lower())
        for v in VOCATIVE_PHRASES
    ):
        return True
    return False


def split_line_at_vocative(line: str) -> str | None:
    """If line has a true vocative followed by main clause, return the
    split version (two lines joined with \\n). Otherwise return None."""
    for m in VOC_MERGED_RE.finditer(line):
        voc_start = m.start("voc")
        rest = m.group("rest").strip()
        if re.match(r"^[\W_]+$", rest):
            continue
        # Skip if rest itself starts with another vocative-form (appositive
        # extension like "O Lord, my God, ..." — those legitimately stay)
        if re.match(
            r"^(?:my|O )(?:brethren|beloved|son|people|Lord|God|Father|kindred|sisters?|brothers?|children|daughters)",
            rest,
            re.IGNORECASE,
        ):
            continue
        if is_true_vocative(line, voc_start):
            # Split point: position right after the vocative-tail comma.
            split_pos = m.end("voc_tail") + 1  # +1 to include the comma
            # Find the actual comma+space boundary
            # voc_tail may be empty if vocative is bare (no proper-name follow-up)
            # The match's `voc_tail` ends right before the ", " separator
            # Look for the next ", " after voc_tail
            tail_end = m.end("voc_tail")
            # Find the comma starting at tail_end
            comma_idx = line.find(",", tail_end)
            if comma_idx == -1:
                continue
            return line[: comma_idx + 1] + "\n" + line[comma_idx + 1:].lstrip()
    return None


def process_file(path: Path, apply: bool):
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    edits = 0
    for i, line in enumerate(lines, start=1):
        stripped = line.rstrip("\n")
        result = split_line_at_vocative(stripped)
        if result is None:
            new_lines.append(line)
            continue
        edits += 1
        # Preserve trailing newline
        for sub in result.split("\n"):
            new_lines.append(sub + "\n")

    if apply and edits:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

    return edits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="Actually write changes to files. Default is dry-run.")
    args = ap.parse_args()

    files = sorted(CORPUS_DIR.glob("*-v2.txt"))
    total = 0
    for path in files:
        edits = process_file(path, args.apply)
        if edits:
            print(f"  {path.name}: {edits} vocative split{'s' if edits != 1 else ''}")
            total += edits

    print()
    if args.apply:
        print(f"Applied {total} vocative-own-line splits.")
    else:
        print(f"DRY RUN: {total} candidate splits found. Run with --apply to commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
