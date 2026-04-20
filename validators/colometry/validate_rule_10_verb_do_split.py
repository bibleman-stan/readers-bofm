#!/usr/bin/env python3
"""
Validate Rule 10 (Never Split Verb from Direct Object) across the BofM corpus.

Rule 10: A governing verb and its bare direct-object noun phrase stay on
the same line. When a prep-phrase or adverbial intervenes ("retained in
remembrance the captivity of your fathers"), the verb + PP + DO are one
unit. Do not break at "in remembrance / the captivity."

Detection heuristic: find lines that begin with a determiner + noun head
and contain NO finite-verb-in-main-clause, where the preceding line ends
with a verb or prep-phrase that would govern the DO.

This is a known-imperfect heuristic. The validator flags candidates for
review; false positives are expected (restrictive relatives, appositive
NPs, compound-object continuations with parallel structure). A human
reviews before applying merges.

Exclusion patterns (added 2026-04-19 after corpus review confirmed all 13
original candidates were false positives):

  1. SUBORDINATOR_THAT_RE  — "that" + pronoun on N+1 → subordinate clause,
     not a DO (e.g. "that ye suffer none of these things").
  2. RELATIVE_PRONOUN_START_RE — N+1 starts with which/who/whose/whom →
     relative-clause continuation, not a DO.
  3. COORDINATE_START_RE — N+1 starts with and/but/or/nor/yet → coordinate
     continuation, not a DO.
  4. EXISTENTIAL_START_RE — N+1 starts with "there was/were/..." →
     existential construction, not a DO.
  5. CATAPHORIC_IT_END_RE — Line N ends with it/this/these/those AND N+1
     starts with that/which → cataphoric placeholder; Rule 17 territory.
  6. APPOSITIVE_NP_RE — N+1 is "the Son of God" / "the Almighty" style
     appositive (article + short title NP, no verb at all after stripping
     relative markers) where the preceding line already contains its own DO.

Exit code: 0 if zero violations, 1 if violations found.
"""

import argparse
import re
import sys
from pathlib import Path

# Determiners that commonly start a direct-object NP
DETERMINERS = r"(?:the|a|an|this|that|these|those|his|her|their|our|your|my)"

# Line N+1 pattern: starts with determiner + noun, is short-ish, no main verb
# The pattern identifies a bare-NP line that might be a DO continuation
BARE_DO_START_RE = re.compile(rf"^{DETERMINERS}\s+\w+", re.IGNORECASE)

# Very-rough main-verb indicators. Lines containing ONLY these as verb-like
# forms are likely NPs with relative clauses (permitted), not predications.
# If a line has a verb NOT inside "which/who/that [be-form]" or inside an
# appositive, it's more likely to be its own predication.
# Heuristic: check if line contains a finite verb outside of relative clauses.
# Conservative: flag only if the line has NO obvious verb at all.
FINITE_VERB_FORMS_RE = re.compile(
    r"\b(?:is|are|was|were|be|been|being|am|hath|hast|do|does|did|doth|have|has|had|will|shall|would|could|should|might|must|may|can)\b"
    r"|(?:[a-z]+eth)\b"
    r"|(?:[a-z]+ed)\b"
    r"|(?:[a-z]+ing)\b",
    re.IGNORECASE,
)

# Common relative/appositive markers on the line — if present, the line may
# be a relative/appositive structure, not a DO
RELATIVE_MARKERS_RE = re.compile(r"\b(?:which|who|whose|whom|that)\s+(?:is|are|was|were|hath|hast|had|has|did|do|does)\b", re.IGNORECASE)

# Line N patterns that suggest it ends with a verb or PP (so the next-line
# bare NP could be its DO)
# - ends with a common verb form (before punctuation)
# - ends with a prep phrase (prep + NP)
VERB_OR_PP_END_RE = re.compile(
    r"\b(?:"
    r"have|has|hath|had|hast|"
    r"see|saw|seen|"
    r"hear|heard|"
    r"give|gave|given|giveth|"
    r"take|took|taken|taketh|"
    r"make|made|maketh|"
    r"find|found|findeth|"
    r"know|knew|known|knoweth|"
    r"declare|declared|declareth|"
    r"speak|spake|spoken|speaketh|"
    r"teach|taught|teacheth|"
    r"preach|preached|preacheth|"
    r"remember|remembered|remembereth|"
    r"retained|retaineth|"
    r"receive|received|receiveth|"
    r"behold|beheld|beholdeth|"
    r"obtain|obtained|obtaineth|"
    r"bring|brought|"
    r"send|sent|"
    r"establish|established|"
    r"build|built|"
    r"destroy|destroyed|"
    r"slay|slew|slain|"
    r"smite|smote|smitten|"
    r"deliver|delivered|"
    r"preserve|preserved"
    r")\b\s*(?:in|on|unto|with|upon|into|through|for|of|among|by|before|after|against)\s+\w+(?:\s+\w+)*[,;:]?\s*$",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Exclusion patterns — added 2026-04-19
# ---------------------------------------------------------------------------

# Pattern 1: "that" used as subordinator (followed by a pronoun subject)
SUBORDINATOR_THAT_RE = re.compile(
    r"^that\s+(?:ye|thou|he|she|it|we|they|you|I|thee|thy|thine)\b",
    re.IGNORECASE,
)

# Pattern 2 (part of cataphoric check): "that" or "which" opening a clause
# after a cataphoric "it/this/these/those" on Line N
CATAPHORIC_IT_END_RE = re.compile(
    r"\b(?:it|this|these|those)\b[,.;]?\s*$",
    re.IGNORECASE,
)

# Pattern 3/6: relative pronouns that start a relative-clause continuation
RELATIVE_PRONOUN_START_RE = re.compile(
    r"^(?:which|who|whose|whom)\b",
    re.IGNORECASE,
)

# Pattern 4: coordinating conjunction at start of N+1
COORDINATE_START_RE = re.compile(
    r"^(?:and|but|or|nor|yet)\b",
    re.IGNORECASE,
)

# Pattern 7: existential "there was/were/..." construction
EXISTENTIAL_START_RE = re.compile(
    r"^there\s+(?:was|were|is|are|came|stood|dwelt)\b",
    re.IGNORECASE,
)

# Additional: "that" + proper noun / "the Lord" type (subordinator introducing
# direct-speech citation, e.g. "that thus saith the Lord God")
SUBORDINATOR_THAT_LORD_RE = re.compile(
    r"^that\s+(?:thus|so|the\s+Lord|all|none|no\b)",
    re.IGNORECASE,
)

# Pattern 8: relative "that" + finite verb (not covered by SUBORDINATOR_THAT_RE
# which only tests pronoun subjects). E.g. "that has brought", "that are".
# RELATIVE_MARKERS_RE already strips these but the resulting bare NP can still
# pass the FINITE_VERB check — so skip at the N+1-start level instead.
RELATIVE_THAT_VERB_RE = re.compile(
    r"^that\s+(?:is|are|was|were|hath|hast|had|has|have|did|do|does|doth|"
    r"shall|will|would|could|should|might|must|may|can)\b",
    re.IGNORECASE,
)

# Pattern 9: appositive NP continuation — N+1 is a short NP with no verb at all
# after a proper name or title on Line N. Detected by: N ends with a proper
# name-like token (capitalized word) or comma after a name, AND N+1 has no
# finite verb whatsoever (even after stripping relatives).
# Implemented as: if no_relative has no finite verb AND N contains a proper
# name immediately before end-of-line punctuation — handled via the existing
# finite-verb check, which should already catch this. BUT the Helaman:2656
# case slips through because VERB_OR_PP_END_RE matches "of Jesus Christ," via
# "of" as a preposition after "know". Add a check: if Line N ends with a
# proper noun (capitalized word + comma/semicolon), the next-line bare NP is
# almost certainly an appositive.
ENDS_WITH_PROPER_NOUN_RE = re.compile(
    r"\b[A-Z][a-z]+[,;]\s*$"
)


def scan_file(path: Path) -> list[dict]:
    """Scan one v2-mine file for Rule 10 violations."""
    violations = []
    lines = path.read_text(encoding="utf-8").splitlines()

    for i in range(len(lines) - 1):
        line = lines[i]
        next_line = lines[i + 1]

        if not line.strip() or re.match(r"^\d+:\d+$", line.strip()):
            continue
        if not next_line.strip() or re.match(r"^\d+:\d+$", next_line.strip()):
            continue

        # Line N+1 must start with determiner + noun
        if not BARE_DO_START_RE.match(next_line.lstrip()):
            continue

        # Line N+1 must not have a main-clause finite verb
        # Heuristic: remove relative-clause content, then check for remaining verbs
        next_stripped = next_line.lstrip().rstrip()
        # Remove relative/appositive clauses "which is/are X" "who was/were X"
        no_relative = RELATIVE_MARKERS_RE.sub("", next_stripped)

        # If there's any remaining finite-verb-like form, the line has its own
        # predication and is not a bare DO
        if FINITE_VERB_FORMS_RE.search(no_relative):
            continue

        # Line N should end with verb or PP (making the next-line NP a plausible DO)
        if not VERB_OR_PP_END_RE.search(line):
            continue

        # Filter: skip if line N ends with colon (direct discourse)
        if line.rstrip().endswith(":"):
            continue

        # -------------------------------------------------------------------
        # Exclusion checks (2026-04-19)
        # -------------------------------------------------------------------

        # Pattern 1 & variants: "that" as subordinator or relative pronoun
        if SUBORDINATOR_THAT_RE.match(next_stripped):
            continue
        if SUBORDINATOR_THAT_LORD_RE.match(next_stripped):
            continue
        # Pattern 8: relative "that" + finite verb (e.g. "that has brought")
        if RELATIVE_THAT_VERB_RE.match(next_stripped):
            continue

        # Pattern 3/6: relative-clause continuation (which/who/whose/whom)
        if RELATIVE_PRONOUN_START_RE.match(next_stripped):
            continue

        # Pattern 4: coordinate continuation
        if COORDINATE_START_RE.match(next_stripped):
            continue

        # Pattern 7: existential construction on N+1 OR on Line N itself
        if EXISTENTIAL_START_RE.match(next_stripped):
            continue
        if EXISTENTIAL_START_RE.match(line.lstrip()):
            continue

        # Pattern 2/5: cataphoric "it/this/these/those" on Line N +
        #              "that/which" opening Line N+1
        if CATAPHORIC_IT_END_RE.search(line) and re.match(
            r"^(?:that|which)\b", next_stripped, re.IGNORECASE
        ):
            continue

        # Pattern 9: appositive NP — Line N ends with a proper noun (capitalized
        # word before comma/semicolon). N+1 is then an appositive, not a DO.
        if ENDS_WITH_PROPER_NOUN_RE.search(line.rstrip()):
            continue

        violations.append(
            {
                "file": path.name,
                "line_num": i + 1,
                "line": line.rstrip(),
                "next_line": next_line.rstrip(),
            }
        )

    return violations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
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

    print("=" * 72)
    print("Rule 10 (Verb + Direct Object) validator — BofM v2-mine corpus")
    print("=" * 72)
    print(f"Files scanned: {len(files)}")
    print(f"Candidate violations: {len(all_violations)}")
    print()

    if all_violations:
        for v in all_violations:
            print(f"[DEVIATION]  {v['file']}:{v['line_num']}")
            print(f"    {v['line'][:100]}")
            print(f"    {v['next_line'][:100]}")
            print()

    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
