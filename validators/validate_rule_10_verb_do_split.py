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
            print(f"  {v['file']}:{v['line_num']}")
            print(f"    {v['line'][:100]}")
            print(f"    {v['next_line'][:100]}")
            print()

    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
