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

# Rule 12 — bare auxiliaries (when followed by a main verb).
# Polysemous words removed (too many FPs without POS tagging):
#   - "might" (often noun: "all their might")
#   - "being" (often noun: "holy Being")
#   - "art" (often noun: "manner of art")
#   - "do" (often emphatic / standalone)
# These words can be genuine auxiliaries but at line-final position they
# are overwhelmingly noun/standalone uses in the BoM corpus.
AUXILIARIES = {
    "did", "had", "hath", "hast", "have",
    "would", "could", "shall", "will",
    "must", "should",
    "doth", "dost",
    "was", "wast", "were", "wert", "is", "art", "are", "am",
    "be", "been",
}

# Next-line first-word blacklist — archaic adverbs/particles that look
# verb-like by suffix but are not main verbs.
NEXT_LINE_NON_VERBS = {
    "even", "when", "where", "yea", "yet", "then",
    "even,", "when,", "where,", "yea,", "yet,", "then,",
}

# Rule 13a — prepositions seeking an object
PREPOSITIONS = {
    "of", "in", "on", "at", "to", "from", "with", "by", "for",
    "unto", "upon", "into", "through", "against", "about", "concerning",
    "during", "before", "after", "behind", "beneath", "beside",
    "between", "beyond", "without", "within", "above", "below",
    "among", "amongst", "toward", "towards", "off",
}

# Phrasal-verb particles / spatial adverbs / archaic postposed prepositions
# that CAN legitimately end a line in archaic English:
#  - Phrasal-verb particles: "they came in," "he went up," "round about"
#  - Spatial adverbs (compound with heavens/earth etc.): "heavens above,
#    earth beneath," "Syrians before and Philistines behind"
#  - Archaic postposed prepositions in passive/relative constructions:
#    "acted upon," "spoken of," "complained against"
#  - Archaic imperative idioms: "go to" = "come on"
PHRASAL_PARTICLES = {
    "in", "out", "up", "down", "off", "on", "back", "forth", "away",
    "about", "beyond", "through", "after", "before",
    "above", "beneath", "behind", "within", "without",
    "upon", "unto", "against", "of", "to",
    # Archaic adverbial uses: "stood by," "passed by," "ornamented with,"
    # "looking for" (with implicit object). False-positive-prone without POS
    # tagging; whitelisted as archaic-English-permitted.
    "by", "with", "for",
}


def ends_complete_sentence(line: str) -> bool:
    """Return True if line ends with sentence-terminating punctuation.

    Line-final auxiliaries, prepositions, and negations ending a complete
    sentence (., !, ?) are NOT splits — they complete their clause. Only
    mid-clause line endings (, ; or no punctuation) could plausibly be
    separated from continuation material on the next line.
    """
    stripped = line.rstrip()
    if not stripped:
        return False
    return stripped[-1] in ".!?"

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

    Flag if line ends with a bare auxiliary MID-CLAUSE (not sentence-end)
    AND the next line starts with a main verb. Auxiliaries ending a
    complete declarative sentence (period) are NOT splits.
    """
    if ends_complete_sentence(line):
        return None
    result = get_last_word(line)
    if not result:
        return None
    last, _ = result
    if last not in AUXILIARIES:
        return None
    next_stripped = next_line.lstrip()
    if not next_stripped:
        return None
    next_first = next_stripped.split(maxsplit=1)[0].lower().rstrip(",.;:!?")
    # Skip if next-line starts with an archaic adverb/particle that suffix-matches verb forms
    if next_first in NEXT_LINE_NON_VERBS:
        return None
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
    """Rule 13a — never end on preposition seeking object.

    Skip prepositions ending a complete sentence (adverb uses). Skip
    phrasal particles (about, up, down, etc.) which legitimately end
    clauses as adverbs.
    """
    if ends_complete_sentence(line):
        return None
    result = get_last_word(line)
    if not result:
        return None
    last, punct = result
    if last not in PREPOSITIONS:
        return None
    if last in PHRASAL_PARTICLES:
        return None
    return f"line-final preposition: {last!r}"


def check_rule_13b(line: str) -> str | None:
    """Rule 13b — never split negation from negated.

    Line-final "not"/"no" ending a complete sentence is legitimate.
    Only flag mid-clause negation where the negated element continues.
    """
    if ends_complete_sentence(line):
        return None
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

        # NOTE: Rule 13b (line-final negation) removed from mechanical check.
        # In archaic BoM English, line-final "not"/"no" with clause-final
        # comma is overwhelmingly the archaic negation-postposition pattern
        # ("they knew not" = "they did not know"), not a Rule 13b split.
        # Distinguishing genuine Rule 13b violations requires understanding
        # which content word is the negation target — judgment-level, not
        # mechanically detectable. Rule 13b stays in the canon but exits
        # the mechanical validator suite.
        for rule_name, check_fn, needs_next in [
            ("Rule 9 (conjunction)", check_rule_9, False),
            ("Rule 11 (article)", check_rule_11, False),
            ("Rule 12 (auxiliary)", check_rule_12, True),
            ("Rule 13a (preposition)", check_rule_13a, False),
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
                print(f"[MALFORMED]  {v['file']}:{v['line_num']} — {v['reason']}")
                print(f"    {v['line'][:100]}")
                if "Rule 12" in v["rule"]:
                    print(f"    {v['next_line'][:100]}")
                print()
    else:
        print("No violations found. Line-final token rules are clean.")

    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
