#!/usr/bin/env python3
"""
Validate line-final token rules across the BofM corpus.

Covers five mechanical rules that share one structural test — the last
non-punctuation token on each line must not fall in a prohibited-class set:

- Rule 9:  Never end a line on a coordinating conjunction
           (and, or, but, nor, for, so, yet)
- Rule 11: Never end a line on an article (the, a, an)
- Rule 12: Never split auxiliary from main verb — flag line-final bare
           auxiliary (did, had, hath, would, could, shall, will, might,
           must, should, do, doth, hast, hath) if not followed by a
           main verb on the same line
- Rule 13a: Never end on a preposition seeking an object
            (of, in, on, at, to, from, with, by, for, unto, upon, into,
            through, against, about, concerning, during, before, after,
            behind, beneath, beside, between, beyond, without, within)
            — with phrasal-verb exceptions
- Rule 13b: Never split negation from negated (not, neither, no) at
            line end — usually forbidden

Output: violations grouped by rule, with file + line number + context.
Exit code: 0 if zero violations, 1 if violations found.

Usage:
    python3 validate_line_final_tokens.py
    python3 validate_line_final_tokens.py --verbose
"""

import argparse
import re
import sys
from pathlib import Path

# Rule 9 — coordinating conjunctions
# Only the clear coordinators. "yet" is polysemous (adverb "as yet," "not yet"
# — high FP rate); "for" and "so" are polysemous (preposition/subordinator
# vs. conjunction). Excluded from the prohibited list.
CONJUNCTIONS = {"and", "or", "but", "nor"}

# Rule 11 — articles
ARTICLES = {"the", "a", "an"}

# Rule 12 — bare auxiliaries (when followed by a main verb)
AUXILIARIES = {
    "did", "had", "hath", "hast", "have",
    "would", "could", "shall", "will",
    "might", "must", "should",
    "do", "doth", "dost",
    "was", "were", "is", "are", "be", "been", "being",
}

# Rule 13a — prepositions seeking an object
PREPOSITIONS = {
    "of", "in", "on", "at", "to", "from", "with", "by", "for",
    "unto", "upon", "into", "through", "against", "about", "concerning",
    "during", "before", "after", "behind", "beneath", "beside",
    "between", "beyond", "without", "within", "above", "below",
    "among", "amongst", "toward", "towards", "off",
}

# Phrasal-verb particles that CAN legitimately end a line
# (e.g., "they came in," "he went up,")
PHRASAL_PARTICLES = {"in", "out", "up", "down", "off", "on", "back", "forth", "away"}

# Rule 13b — negation
NEGATIONS = {"not", "no"}
# Note: "neither" and "nor" dangle at line-end are already Rule 9
# violations; skip here to avoid double-counting


def get_last_word(line: str) -> tuple[str, str] | None:
    """Return (last_word_lower, trailing_punctuation) or None if line is empty."""
    stripped = line.rstrip()
    # Split off trailing punctuation
    m = re.match(r"^(.*?)([,.;:!?\"')]*)$", stripped)
    if not m:
        return None
    content, punct = m.group(1), m.group(2)
    words = content.split()
    if not words:
        return None
    last = words[-1]
    # Strip any leading punctuation on the last word
    last = re.sub(r"^[\"'(]+", "", last)
    return last.lower(), punct


def check_rule_9(line: str) -> str | None:
    """Rule 9 — never end on coordinating conjunction."""
    result = get_last_word(line)
    if not result:
        return None
    last, _ = result
    if last in CONJUNCTIONS:
        return f"line-final conjunction: {last!r}"
    return None


def check_rule_11(line: str) -> str | None:
    """Rule 11 — never end on article."""
    result = get_last_word(line)
    if not result:
        return None
    last, _ = result
    if last in ARTICLES:
        return f"line-final article: {last!r}"
    return None


def check_rule_12(line: str, next_line: str) -> str | None:
    """Rule 12 — never split auxiliary from main verb.

    Flag if line ends with a bare auxiliary AND the next line starts with a
    main verb (typically past participle or base form). This is a heuristic —
    the validator flags ANY bare auxiliary at line end; false positives are
    expected for contexts where the auxiliary legitimately ends a clause.
    """
    result = get_last_word(line)
    if not result:
        return None
    last, _ = result
    if last not in AUXILIARIES:
        return None
    # Check if next line starts with a word that could be a main verb
    next_stripped = next_line.lstrip()
    if not next_stripped:
        return None
    next_first = next_stripped.split(maxsplit=1)[0].lower().rstrip(",.;:!?")
    # Heuristic: if next line starts with a verb-like word (past participle,
    # base form, -ing, -ed), flag. This is a soft flag — humans review.
    # Common BofM main-verb suffixes after auxiliary:
    verb_suffixes = ("ed", "en", "ing", "eth")
    # Also common base verbs that follow auxiliaries
    common_main_verbs = {
        "say", "said", "see", "seen", "go", "gone", "come", "come",
        "hear", "heard", "slay", "slain", "give", "given", "take", "taken",
        "make", "made", "do", "done", "know", "known", "bring", "brought",
        "cast", "put", "set", "speak", "spoken", "tell", "told",
        "write", "written", "read", "build", "built",
    }
    if (
        any(next_first.endswith(s) for s in verb_suffixes)
        or next_first in common_main_verbs
    ):
        return f"auxiliary {last!r} likely split from main verb {next_first!r}"
    return None


def check_rule_13a(line: str) -> str | None:
    """Rule 13a — never end on preposition seeking object."""
    result = get_last_word(line)
    if not result:
        return None
    last, punct = result
    if last not in PREPOSITIONS:
        return None
    # Phrasal-verb exception: some particles can legitimately end a line
    if last in PHRASAL_PARTICLES:
        return None
    return f"line-final preposition: {last!r}"


def check_rule_13b(line: str) -> str | None:
    """Rule 13b — never split negation from negated."""
    result = get_last_word(line)
    if not result:
        return None
    last, _ = result
    if last in NEGATIONS:
        return f"line-final negation: {last!r}"
    return None


def scan_file(path: Path) -> list[dict]:
    """Scan one v2-mine file for line-final token violations."""
    violations = []
    lines = path.read_text(encoding="utf-8").splitlines()

    for i, line in enumerate(lines):
        # Skip blank lines and verse-number-only lines
        if not line.strip() or re.match(r"^\d+:\d+$", line.strip()):
            continue

        next_line = lines[i + 1] if i + 1 < len(lines) else ""

        # Skip if next line is a verse-number line (not a real continuation)
        if re.match(r"^\d+:\d+$", next_line.strip()):
            continue
        # Skip blank-line-before-next-verse (end of verse)
        if not next_line.strip():
            continue

        for rule_name, check_fn, needs_next in [
            ("Rule 9 (conjunction)", check_rule_9, False),
            ("Rule 11 (article)", check_rule_11, False),
            ("Rule 12 (auxiliary)", check_rule_12, True),
            ("Rule 13a (preposition)", check_rule_13a, False),
            ("Rule 13b (negation)", check_rule_13b, False),
        ]:
            result = (
                check_fn(line, next_line) if needs_next else check_fn(line)
            )
            if result:
                violations.append(
                    {
                        "file": path.name,
                        "line_num": i + 1,
                        "rule": rule_name,
                        "reason": result,
                        "line": line.rstrip(),
                        "next_line": next_line.rstrip(),
                    }
                )

    return violations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument(
        "--v2-dir",
        default="c:/Users/bibleman/repos/readers-bofm/data/text-files/v2-mine",
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
    print("Line-final token validator — BofM v2-mine corpus")
    print("Covers Rules 9, 11, 12, 13a, 13b")
    print("=" * 72)
    print(f"Files scanned: {len(files)}")
    print(f"Violations found: {len(all_violations)}")
    print()

    if all_violations:
        # Group by rule
        by_rule: dict[str, list] = {}
        for v in all_violations:
            by_rule.setdefault(v["rule"], []).append(v)

        for rule in sorted(by_rule):
            print(f"--- {rule} ({len(by_rule[rule])} violations) ---")
            for v in by_rule[rule]:
                print(f"  {v['file']}:{v['line_num']} — {v['reason']}")
                print(f"    {v['line'][:100]}")
                if "Rule 12" in v["rule"]:
                    print(f"    {v['next_line'][:100]}")
                print()
    else:
        print("No violations found. Line-final token rules are clean.")

    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
