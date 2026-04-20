#!/usr/bin/env python3
"""
Validate Rule 27 ("Insomuch That" Binding) across the BofM corpus.

Rule 27: "insomuch that" is a consecutive (result) subordinator.
Default is SPLIT (break before "insomuch that").
MERGE only when ALL THREE conditions hold:
  1. Result clause <= 8 words
  2. Subject continuity (matrix subject = result clause subject, or elided/co-referential)
  3. No camera-angle shift (single-image diagnostic passes)

Condition 3 is never mechanically determinable — all instances flagged REQUIRES-REVIEW
for that condition regardless. Conditions 1 and 2 drive the primary categorization.

Categories:
  STRONG-MERGE-CANDIDATE  — currently split,  cond 1+2 hold  → should probably merge
  STRONG-SPLIT-CORRECT    — currently split,  cond 1 or 2 fails → split is defensible
  STRONG-SPLIT-CANDIDATE  — currently merged, cond 1 or 2 fails → should probably split
  STRONG-MERGE-CORRECT    — currently merged, cond 1+2 hold   → merge is defensible
  REVIEW-REQUIRED         — condition 2 is ambiguous

Exit code: 0 if no STRONG-*-CANDIDATE instances, 1 otherwise.

Usage:
    python3 validate_rule_27_insomuch_that.py
    python3 validate_rule_27_insomuch_that.py --verbose
"""

import argparse
import re
import sys
from pathlib import Path

V2_DIR = Path("c:/Users/bibleman/repos/readers-bofm/data/text-files/v2-mine")

# Tokenizer — split on whitespace, strip punctuation for counting
_PUNCT_RE = re.compile(r"[^\w']+")


def word_count(text: str) -> int:
    """Count words in text, stripping leading/trailing punctuation per token."""
    tokens = text.split()
    count = 0
    for t in tokens:
        cleaned = _PUNCT_RE.sub("", t)
        if cleaned:
            count += 1
    return count


# Result-clause length: from first word after "insomuch that" to end-of-line
# or sentence terminator (period, semicolon, exclamation). "insomuch" and
# "that" themselves excluded.
SENTENCE_END_RE = re.compile(r"[.;!]")


def result_clause_words(result_text: str) -> int:
    """
    Count result-clause content words.
    result_text: everything after 'insomuch that' to end of available text.
    Stops at first sentence terminator.
    """
    # Truncate at first sentence terminator
    m = SENTENCE_END_RE.search(result_text)
    if m:
        result_text = result_text[: m.start()]
    return word_count(result_text)


# Subject-continuity heuristic
# Pronouns that are likely co-referential with the preceding subject:
CO_REF_PRONOUNS = {
    "he", "she", "they", "it", "i",
    "his", "her", "their", "its", "my",
    "him",  # accusative but co-ref with prior subject in result
    "we", "our",
}

# Articles/determiners that introduce a NEW noun phrase (likely new subject):
NEW_NP_STARTERS = {
    "the", "a", "an", "all", "many", "no", "every", "some", "this", "these",
    "those", "that", "yea", "also", "even",
}

# Name-initial capitals — heuristic: result clause starts with Title-case word
# that is NOT a pronoun → probable new subject NP
TITLE_CASE_RE = re.compile(r"^[A-Z][a-z]")


# Expletive-*there* sub-clause (canon §5 Rule 27, added 2026-04-19 PM):
# When the result clause begins with expletive "there" + BE/arise/come/stand/
# dwell verb, condition 2 is evaluated against the semantic subject (the NP
# after "there was/were"), not the expletive itself. New-entity semantic
# subjects (typical — "there were many slain", "there arose a great storm")
# fail condition 2 → default SPLIT. Rare continuing-entity cases are handled
# by Stan's spot-check; we default-fail condition 2 for all expletive-there.
EXPLETIVE_THERE_VERBS = {
    "was", "were", "is", "are",
    "arose", "came", "stood", "dwelt",
    "shall",  # "there shall be" — future tense expletive
    "never",  # "there never was known..." (3 Ne 8:25)
    "had",    # rare passive-expletive variant
    "hath",
    "began",  # "there began to be..."
}


def subject_continuity(result_first_word: str, matrix_line: str,
                         result_second_word: str = "") -> str:
    """
    Returns 'continuous', 'shift', or 'ambiguous'.

    result_first_word: first content word of the result clause (lowercase).
    matrix_line: the full text of the preceding clause line.
    result_second_word: second token of the result clause (for expletive-there
        detection — if first word is "there" and second is a BE/arise verb,
        default to 'shift' per canon §5 Rule 27 expletive-*there* sub-clause).
    """
    rfw = result_first_word.lower().rstrip(",.;:'\"")
    rsw = result_second_word.lower().rstrip(",.;:'\"") if result_second_word else ""
    if not rfw:
        return "ambiguous"

    # Expletive-*there* sub-clause — evaluate against semantic subject.
    # Default: new-entity semantic subject → FAIL condition 2 → SHIFT.
    if rfw == "there" and rsw in EXPLETIVE_THERE_VERBS:
        return "shift"

    # Co-referential pronoun → likely continuous
    if rfw in CO_REF_PRONOUNS:
        return "continuous"

    # New NP starter (article/det) → likely shift
    if rfw in NEW_NP_STARTERS:
        return "shift"

    # Title-case non-pronoun → proper name, likely new subject
    if TITLE_CASE_RE.match(result_first_word) and rfw not in CO_REF_PRONOUNS:
        return "shift"

    # Verb-first (elided subject, implied continuation) → treat as continuous
    # Common archaic verbs at clause start: "did", "was", "were", "had", "could"
    ELIDED_SUBJECT_VERBS = {"did", "was", "were", "had", "could", "might", "would",
                             "shall", "will", "hath", "doth", "art", "am", "are",
                             "began", "fell", "came", "went", "cried", "spake",
                             "led", "brought", "felt", "smote"}
    if rfw in ELIDED_SUBJECT_VERBS:
        return "continuous"

    return "ambiguous"


# ──────────────────────────────────────────────────────────────────────────────

INSOMUCH_THAT_RE = re.compile(r"\binsomuch\s+that\b", re.IGNORECASE)


def scan_file(path: Path, verbose: bool = False) -> list[dict]:
    """
    Scan one v2-mine file for all 'insomuch that' instances.
    Returns a list of record dicts, one per instance.
    """
    results = []
    lines = path.read_text(encoding="utf-8").splitlines()

    for i, line in enumerate(lines):
        # Skip blank lines and verse headers
        if not line.strip() or re.match(r"^\d+:\d+$", line.strip()):
            continue

        # Look for "insomuch that" on this line
        m = INSOMUCH_THAT_RE.search(line)
        if not m:
            continue

        # Determine break state
        # SPLIT: "insomuch that" leads this line (possibly with "yea," prefix)
        # MERGED: "insomuch that" appears mid-line (after other content)
        before_insomuch = line[: m.start()].strip()

        # "yea, insomuch that..." still counts as a SPLIT-line (the "yea," is a
        # discourse particle that accompanies the insomuch-that clause, not the
        # matrix clause)
        # We consider it SPLIT if before_insomuch is empty or is only "yea,"
        # or other short discourse particles.
        DISCOURSE_PARTICLES = re.compile(
            r"^(yea,?|nay,?|behold,?|verily,?|yea\s+verily,?)\s*$", re.IGNORECASE
        )
        if not before_insomuch or DISCOURSE_PARTICLES.match(before_insomuch):
            state = "SPLIT"
            matrix_line = lines[i - 1].rstrip() if i > 0 else ""
        else:
            state = "MERGED"
            matrix_line = before_insomuch  # the part before "insomuch that"

        # Extract result-clause text (everything after "insomuch that")
        result_raw = line[m.end():].strip()

        # Condition 1: result clause word count
        rc_words = result_clause_words(result_raw)
        cond1 = rc_words <= 8

        # Condition 2: subject continuity
        # Get first two words of result clause (2nd needed for expletive-there)
        result_tokens = result_raw.split()
        first_result_word = result_tokens[0] if result_tokens else ""
        second_result_word = result_tokens[1] if len(result_tokens) > 1 else ""
        subj = subject_continuity(first_result_word, matrix_line,
                                   second_result_word)
        cond2_holds = subj == "continuous"
        cond2_ambiguous = subj == "ambiguous"

        # Condition 3: always REQUIRES-REVIEW (camera-angle, not mechanical)
        cond3_note = "REQUIRES-REVIEW"

        # Categorize
        if cond2_ambiguous:
            category = "REVIEW-REQUIRED"
        elif state == "SPLIT":
            if cond1 and cond2_holds:
                category = "STRONG-MERGE-CANDIDATE"
            else:
                category = "STRONG-SPLIT-CORRECT"
        else:  # MERGED
            if cond1 and cond2_holds:
                category = "STRONG-MERGE-CORRECT"
            else:
                category = "STRONG-SPLIT-CANDIDATE"

        results.append({
            "file": path.name,
            "line_num": i + 1,
            "state": state,
            "category": category,
            "rc_words": rc_words,
            "cond1": cond1,
            "subj_continuity": subj,
            "cond2_holds": cond2_holds,
            "cond3_note": cond3_note,
            "line": line.rstrip(),
            "matrix_line": matrix_line,
            "result_raw": result_raw,
        })

        if verbose:
            print(
                f"  {category:30s}  {path.name}:{i+1}  "
                f"words={rc_words}  subj={subj}  "
                f"{line.strip()[:80]!r}"
            )

    return results


def print_category_block(label: str, records: list[dict], max_show: int = 20):
    if not records:
        return
    print(f"\n{label} (first {min(max_show, len(records))} of {len(records)}):")
    print("-" * 72)
    for r in records[:max_show]:
        tag = "[DEVIATION]" if "CANDIDATE" in r["category"] else "[INFO]"
        print(f"  {tag}  {r['file']}:{r['line_num']}")
        if r["state"] == "SPLIT" and r["matrix_line"]:
            print(f"    matrix:  {r['matrix_line'][:100]}")
        print(f"    line:    {r['line'].strip()[:100]}")
        print(f"    Words: {r['rc_words']:2d}  "
              f"Cond1({'PASS' if r['cond1'] else 'FAIL'})-"
              f"Cond2({r['subj_continuity']})-"
              f"Cond3(review)")
        print()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show per-instance details during scan")
    parser.add_argument(
        "--v2-dir",
        default=str(V2_DIR),
        help="Directory containing v2-mine canonical files",
    )
    args = parser.parse_args()

    v2_dir = Path(args.v2_dir)
    if not v2_dir.exists():
        print(f"ERROR: {v2_dir} not found", file=sys.stderr)
        sys.exit(2)

    files = sorted(v2_dir.glob("*-v2.txt"))
    if not files:
        print(f"ERROR: No *-v2.txt files found in {v2_dir}", file=sys.stderr)
        sys.exit(2)

    all_records: list[dict] = []
    for path in files:
        recs = scan_file(path, verbose=args.verbose)
        all_records.extend(recs)

    # Tally
    split_recs   = [r for r in all_records if r["state"] == "SPLIT"]
    merged_recs  = [r for r in all_records if r["state"] == "MERGED"]
    total = len(all_records)

    cats = {
        "STRONG-MERGE-CANDIDATE": [],
        "STRONG-SPLIT-CORRECT":   [],
        "STRONG-SPLIT-CANDIDATE": [],
        "STRONG-MERGE-CORRECT":   [],
        "REVIEW-REQUIRED":        [],
    }
    for r in all_records:
        cats[r["category"]].append(r)

    # ── Report header ────────────────────────────────────────────────────────
    print()
    print('Rule 27 ("Insomuch That" Binding) — BofM v2-mine corpus')
    print("=" * 56)
    print(f"Total instances found: {total}  (expected ~175)")
    split_pct  = round(100 * len(split_recs)  / total) if total else 0
    merged_pct = round(100 * len(merged_recs) / total) if total else 0
    print(f"  Currently split:  {len(split_recs):3d}  ({split_pct}%)")
    print(f"  Currently merged: {len(merged_recs):3d}  ({merged_pct}%)")
    print()
    print("Categorization:")
    print(f"  STRONG-MERGE-CANDIDATE: {len(cats['STRONG-MERGE-CANDIDATE']):3d}"
          "   [currently split but 3-condition test suggests MERGE]")
    print(f"  STRONG-SPLIT-CORRECT:   {len(cats['STRONG-SPLIT-CORRECT']):3d}")
    print(f"  STRONG-SPLIT-CANDIDATE: {len(cats['STRONG-SPLIT-CANDIDATE']):3d}"
          "   [currently merged but conditions fail — suggests SPLIT]")
    print(f"  STRONG-MERGE-CORRECT:   {len(cats['STRONG-MERGE-CORRECT']):3d}")
    print(f"  REVIEW-REQUIRED:        {len(cats['REVIEW-REQUIRED']):3d}")

    # ── Per-category detail blocks ────────────────────────────────────────────
    print_category_block("STRONG-MERGE-CANDIDATE", cats["STRONG-MERGE-CANDIDATE"])
    print_category_block("STRONG-SPLIT-CANDIDATE", cats["STRONG-SPLIT-CANDIDATE"])
    print_category_block("STRONG-SPLIT-CORRECT",   cats["STRONG-SPLIT-CORRECT"])
    print_category_block("STRONG-MERGE-CORRECT",   cats["STRONG-MERGE-CORRECT"])
    print_category_block("REVIEW-REQUIRED",        cats["REVIEW-REQUIRED"])

    # ── Exit code ─────────────────────────────────────────────────────────────
    has_candidates = (
        len(cats["STRONG-MERGE-CANDIDATE"]) > 0
        or len(cats["STRONG-SPLIT-CANDIDATE"]) > 0
    )
    sys.exit(1 if has_candidates else 0)


if __name__ == "__main__":
    main()
