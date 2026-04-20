#!/usr/bin/env python3
"""
Validate Rule 19 (Anaphoric Relative / Class P) across the BofM corpus.

Rule 19: Relative clauses can be either cataphoric (information-advancing,
SPLIT) or anaphoric (backward-pointing, MERGE) or Class P (completing-
predication, MERGE). The distinction is semantic.

Detection: Line N ends with a bare NP; Line N+1 starts with a relative pronoun
(which, whereof, whereby, wherein, wherefrom, whereunto, whereon, whereat, who,
whose, whom, that as relative).

Classification:
  STRONG-MERGE: anaphoric + Class P signals — short clause, no proper nouns,
      no substantive new predicates, mostly pronouns and common verbs.
  PROBABLE-CATAPHORIC-KEEP-SPLIT: proper nouns, long clause, new substantive
      content.
  REVIEW-REQUIRED: ambiguous.

Error class: [DEVIATION]
Exit: 1 on candidates, 0 on clean.

Usage:
    PYTHONIOENCODING=utf-8 python3 validate_rule_19_anaphoric_relative.py
    PYTHONIOENCODING=utf-8 python3 validate_rule_19_anaphoric_relative.py --apply
    PYTHONIOENCODING=utf-8 python3 validate_rule_19_anaphoric_relative.py --verbose
"""

import argparse
import re
import sys
from pathlib import Path

V2_DIR = Path("c:/Users/bibleman/repos/readers-bofm/data/text-files/v2-mine")

# --- Detection patterns ---

# Line N ends with a bare NP tail (determiner/possessive + noun + optional comma)
NP_TAIL_RE = re.compile(
    r"\b(?:the|these|those|his|her|their|our|your|my|a|an|this)\s+\w+[,]?\s*$",
    re.IGNORECASE,
)

# Line N+1 starts with a relative pronoun.
# NOTE: "that" is intentionally excluded here — "that" clauses are ambiguous
# (purpose, result, complement, relative) and are already covered by Rules 7,
# 17, 26, 27. This scanner targets *wh*-relative pronouns only.
REL_PRONOUN_RE = re.compile(
    r"^\s*(?:which|whereof|whereby|wherein|wherefrom|whereunto|whereon|whereat|"
    r"who|whose|whom)\b",
    re.IGNORECASE,
)

# --- Classification heuristics ---

# Proper nouns: capitalized word NOT at start of line (after trimming leading "which/who/...")
# and NOT common false-positives (I, Lord — actually Lord is a proper noun we DO want to catch)
PROPER_NOUN_RE = re.compile(r"(?<!\A)\b[A-Z][a-z]{1,}\b")

# Substantive new predicates — verbs beyond the common backward-pointing set
COMMON_VERBS_RE = re.compile(
    r"\b(?:is|are|was|were|be|been|being|hath|have|had|has|did|do|does|done)\b",
    re.IGNORECASE,
)

# Relative pronoun strip — remove the leading rel pronoun to inspect the clause body
REL_STRIP_RE = re.compile(
    r"^\s*(?:which|whereof|whereby|wherein|wherefrom|whereunto|whereon|whereat|"
    r"who|whose|whom)\s+",
    re.IGNORECASE,
)

# AICTP — if line N contains this, skip (Rule 16 governs)
AICTP_RE = re.compile(
    r"\b(?:it (?:came|shall come|had come) to pass|as it happened)\b",
    re.IGNORECASE,
)

# Verse-number lines
VERSE_NUM_RE = re.compile(r"^\d+:\d+\s*$")

# Known-fixed case: Alma 12:28 (already merged — skip if we somehow see it)
KNOWN_FIXED = {
    ("09-alma-2020-sb-v2.txt", "concerning the things"),  # heuristic guard
}

# Conjunction openers on line N — if line starts with "And" / "But" / "Or" + NP
# these are fine to flag

# Words considered pronouns for anaphoric test
PRONOUNS = {
    "he", "she", "it", "they", "we", "i", "him", "her", "them", "us", "me",
    "his", "her", "its", "their", "our", "my", "your", "ye", "thee", "thou",
    "which", "who", "whom", "whose", "what",
}


def strip_leading_rel(text: str) -> str:
    """Remove the leading relative pronoun from a relative clause."""
    return REL_STRIP_RE.sub("", text).strip()


def find_proper_nouns(clause_body: str) -> list[str]:
    """Find proper nouns in the clause body (after stripping relative pronoun)."""
    # Remove line-leading position bias — only mid-clause capitals
    words = clause_body.split()
    proper = []
    for w in words:
        clean = re.sub(r"[^\w]", "", w)
        if not clean:
            continue
        # Capital, length >= 2, not a common false positive
        if (
            clean[0].isupper()
            and len(clean) >= 2
            and clean.lower() not in {
                "the", "a", "an", "and", "but", "or", "nor",
                "i",  # pronoun I
                "lord", "god",  # we'll let these through as proper nouns (they ARE new content-signals)
            }
        ):
            proper.append(clean)
    return proper


def classify_relative_clause(rel_line: str, next_next_line: str | None) -> tuple[str, str]:
    """
    Classify the relative clause line as STRONG-MERGE, PROBABLE-CATAPHORIC, or REVIEW-REQUIRED.

    Returns (category, reason).
    """
    clause_body = strip_leading_rel(rel_line)
    word_count = len(clause_body.split())

    # 1. Proper nouns in clause body → cataphoric
    proper_nouns = find_proper_nouns(clause_body)
    if proper_nouns:
        return (
            "PROBABLE-CATAPHORIC-KEEP-SPLIT",
            f"proper nouns in clause: {proper_nouns[:3]}",
        )

    # 2. Word count > 8 → lean cataphoric (may carry substantive info)
    if word_count > 8:
        return (
            "PROBABLE-CATAPHORIC-KEEP-SPLIT",
            f"clause too long ({word_count} words) to be purely anaphoric",
        )

    # 3. Check for substantive new predicates (non-common verbs)
    # Strip common verbs and pronouns — see if anything substantive remains
    words_lower = {re.sub(r"[^\w]", "", w).lower() for w in clause_body.split() if w}
    non_common = words_lower - PRONOUNS - {
        # common verbs
        "is", "are", "was", "were", "be", "been", "being", "hath", "have", "had",
        "has", "did", "do", "does", "done", "shall", "will", "would", "could",
        "should", "might", "may", "can",
        # prepositions / articles
        "the", "a", "an", "of", "in", "to", "for", "at", "by", "from", "with",
        "on", "unto", "into", "upon", "among", "before", "after", "between",
        "through", "throughout", "against", "about", "over", "under",
        # connectives
        "and", "but", "or", "nor", "not", "no", "yea", "also", "even",
        # relative-pronoun leftovers
        "which", "whereof", "whereby", "wherein", "who", "whose", "whom", "that",
        "wherein", "whereat", "wherefrom", "whereunto", "whereon",
        # common content words that ARE backward-pointing in BofM formulaic style
        "appointed", "given", "spoken", "written", "said", "commanded",
        "promised", "prepared", "ordained", "written",
    }

    # Remove short function words (len <= 2)
    non_common = {w for w in non_common if len(w) > 2}

    if len(non_common) >= 2:
        # Multiple substantive words not in our backward-pointing list
        return (
            "REVIEW-REQUIRED",
            f"substantive new words in clause: {sorted(non_common)[:5]}",
        )
    elif len(non_common) == 1:
        # Single substantive word — borderline
        return (
            "REVIEW-REQUIRED",
            f"one substantive new word: {sorted(non_common)}",
        )

    # 4. Short clause, no proper nouns, no substantive new content → STRONG-MERGE
    return (
        "STRONG-MERGE",
        f"short ({word_count}w), no proper nouns, no new substantive predicates",
    )


def scan_file(path: Path, verbose: bool = False) -> list[dict]:
    """Scan one v2-mine file for Rule 19 anaphoric-relative violations."""
    candidates = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    for i in range(len(lines) - 1):
        line = lines[i]
        next_line = lines[i + 1]

        # Skip blank lines and verse-number lines
        stripped = line.strip()
        if not stripped or VERSE_NUM_RE.match(stripped):
            continue

        # Skip AICTP lines (Rule 16 governs)
        if AICTP_RE.search(line):
            continue

        # Line N must match NP-tail pattern
        if not NP_TAIL_RE.search(line):
            continue

        # Line N+1 must start with a relative pronoun
        if not REL_PRONOUN_RE.match(next_line):
            continue

        # Get line N+2 for context (continuation check)
        next_next = lines[i + 2] if i + 2 < len(lines) else None

        # Classify
        category, reason = classify_relative_clause(next_line, next_next)

        candidates.append(
            {
                "file": path.name,
                "path": path,
                "line_num": i + 1,  # 1-indexed
                "line": line.rstrip(),
                "rel_line": next_line.rstrip(),
                "next_next": next_next.rstrip() if next_next else "",
                "category": category,
                "reason": reason,
            }
        )

    return candidates


def apply_strong_merges(candidates: list[dict]) -> list[dict]:
    """
    For STRONG-MERGE candidates: merge line N+1 upward into line N.
    Groups by file, applies all merges in one pass per file.
    Returns list of applied merges.
    """
    # Group by file
    by_file: dict[Path, list[dict]] = {}
    for c in candidates:
        if c["category"] == "STRONG-MERGE":
            by_file.setdefault(c["path"], []).append(c)

    applied = []
    for path, merges in by_file.items():
        # Sort by line_num descending so that applying from bottom up
        # preserves line indices for earlier merges
        merges_sorted = sorted(merges, key=lambda x: x["line_num"], reverse=True)

        text_lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

        for m in merges_sorted:
            idx = m["line_num"] - 1  # 0-indexed line N
            rel_idx = idx + 1        # 0-indexed line N+1

            if rel_idx >= len(text_lines):
                continue

            # Determine merged text: line N (stripped of trailing newline) +
            # " " + rel_line content (stripped), preserving original line ending
            line_n = text_lines[idx].rstrip("\r\n")
            line_rel = text_lines[rel_idx].rstrip("\r\n").lstrip()
            eol = "\n"

            merged = line_n + " " + line_rel + eol

            text_lines[idx] = merged
            # Remove rel_line (line N+1)
            del text_lines[rel_idx]

            applied.append(m)

        path.write_text("".join(text_lines), encoding="utf-8")

    return applied


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", "-v", action="store_true", help="Show extra detail")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply STRONG-MERGE fixes to v2-mine files",
    )
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

    all_candidates = []
    files = sorted(v2_dir.glob("*-v2.txt"))
    for path in files:
        candidates = scan_file(path, verbose=args.verbose)
        all_candidates.extend(candidates)

    # Partition
    strong_merge = [c for c in all_candidates if c["category"] == "STRONG-MERGE"]
    cataphoric = [c for c in all_candidates if c["category"] == "PROBABLE-CATAPHORIC-KEEP-SPLIT"]
    review = [c for c in all_candidates if c["category"] == "REVIEW-REQUIRED"]

    # Report header
    print("=" * 72)
    print("Rule 19 (Anaphoric Relative / Class P) validator — BofM v2-mine")
    print("[DEVIATION] error class")
    print("=" * 72)
    print(f"Files scanned:                  {len(files)}")
    print(f"Total candidates:               {len(all_candidates)}")
    print(f"  STRONG-MERGE:                 {len(strong_merge)}")
    print(f"  PROBABLE-CATAPHORIC (keep):   {len(cataphoric)}")
    print(f"  REVIEW-REQUIRED:              {len(review)}")
    print()

    # Apply merges if requested
    applied = []
    if args.apply and strong_merge:
        applied = apply_strong_merges(strong_merge)
        print(f"Applied {len(applied)} STRONG-MERGE fix(es).")
        print()

    # --- STRONG-MERGE section ---
    print("=" * 72)
    print(f"STRONG-MERGE candidates ({len(strong_merge)})")
    print("=" * 72)
    for c in strong_merge:
        tag = "[APPLIED]" if args.apply else "[DEVIATION]"
        print(f"{tag}  {c['file']}:{c['line_num']}")
        print(f"    BEFORE line {c['line_num']}: {c['line'][:90]}")
        print(f"    BEFORE line {c['line_num']+1}: {c['rel_line'][:90]}")
        print(f"    AFTER merge:  {c['line'].rstrip()} {c['rel_line'].lstrip()}"[:110])
        print(f"    Reason: {c['reason']}")
        print()

    # --- PROBABLE-CATAPHORIC section ---
    print("=" * 72)
    print(f"PROBABLE-CATAPHORIC-KEEP-SPLIT ({len(cataphoric)}) — sample (up to 5)")
    print("=" * 72)
    for c in cataphoric[:5]:
        print(f"  {c['file']}:{c['line_num']}  [{c['reason']}]")
        print(f"    {c['line'][:80]}")
        print(f"    {c['rel_line'][:80]}")
        print()

    # --- REVIEW-REQUIRED section (full list) ---
    print("=" * 72)
    print(f"REVIEW-REQUIRED ({len(review)}) — full list")
    print("=" * 72)
    for c in review:
        print(f"[DEVIATION]  {c['file']}:{c['line_num']}")
        print(f"    {c['line'][:80]}")
        print(f"    {c['rel_line'][:80]}")
        print(f"    Reason: {c['reason']}")
        print()

    if not all_candidates:
        print("No Rule 19 anaphoric-relative candidates found. Corpus clean.")

    sys.exit(1 if all_candidates else 0)


if __name__ == "__main__":
    main()
