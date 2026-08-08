#!/usr/bin/env python3
"""
Validate Rule 17 (Complement Integrity) across the BofM corpus.

Rule 17: A governing verb keeps its clausal complement on the same line when
the verb's predication is semantically incomplete without that complement.

Verb classes covered:
- Causative: cause(d), suffer(ed), permit(ted), command(ed), grant(ed)
- Aspectual: begin/began, cease(d), continue(d)
- Speech (indirect discourse): say/said/saith/sayest/spake/spoken, declare(d),
  testify/testified, swear/swore/sware, proclaim(ed), tell/told, confess(ed),
  rehearse(d), preach(ed), answer(ed)
- Cognition: know/knew/knoweth/knowest, believe(d)/believeth/believest,
  perceive(d), remember(ed), understand/understood/understandeth, hear/heard
- Volition: wish/wished, desire(d)/desireth/desirest, hope(d), long(ed),
  trust(ed), pray(ed)
- FEF extraposition: handled separately (it was X to Y pattern)

Output: lines in v2-mine files where a governing verb + intervening object ends
with comma on line N, and line N+1 begins with "that " — flag as Rule 17
merge candidates. Exception filters applied to reduce false positives.

Exit code: 0 if zero violations, 1 if violations found.

Usage:
    python3 validate_rule_17_complement_integrity.py
    python3 validate_rule_17_complement_integrity.py --verbose
"""

import argparse
import re
import sys
from pathlib import Path

# Governing verbs — lowercase, match whole word at end of line (before comma)
CAUSATIVE_VERBS = {
    "cause", "caused", "causeth",
    "suffer", "suffered", "suffereth",
    "permit", "permitted",
    "command", "commanded", "commandeth",
    "grant", "granted", "granteth",
}

ASPECTUAL_VERBS = {
    "began", "begin", "beginneth",
    "cease", "ceased", "ceaseth",
    "continue", "continued", "continueth",
}

SPEECH_VERBS = {
    "say", "said", "saith", "sayest", "saying",
    "spake", "spoken", "speak", "speakest", "speaketh",
    "declare", "declared", "declareth",
    "testify", "testified", "testifieth",
    "swear", "swore", "sware",
    "proclaim", "proclaimed",
    "tell", "told", "telleth",
    "confess", "confessed", "confesseth",
    "rehearse", "rehearsed",
    "preach", "preached", "preacheth",
    "answer", "answered", "answereth",
    "cry", "cried", "crieth",  # prophetic-cry sense
}

COGNITION_VERBS = {
    "know", "knew", "known", "knoweth", "knowest",
    "believe", "believed", "believeth", "believest",
    "perceive", "perceived", "perceiveth",
    "remember", "remembered", "remembereth", "rememberest",
    "understand", "understood", "understandeth",
    "hear", "heard", "heareth",
    "see", "saw", "seen", "seeth",  # cognitive sense only — filtered
    "suppose", "supposed", "supposeth",
    "imagine", "imagined",
    "forget", "forgat", "forgotten",
    "think", "thought", "thinketh",
}

VOLITION_VERBS = {
    "wish", "wished", "wisheth",
    "desire", "desired", "desireth", "desirest",
    "hope", "hoped",
    "long", "longed",
    "trust", "trusted",
    "pray", "prayed", "prayeth", "prayest",
    "seek", "sought", "seeketh",
}

ALL_GOVERNING_VERBS = (
    CAUSATIVE_VERBS | ASPECTUAL_VERBS | SPEECH_VERBS | COGNITION_VERBS | VOLITION_VERBS
)

# Exception filters — these indicate the "that" should STAY split

# AICTP formula (Rule 16): "it came to pass that" — break preserved
AICTP_RE = re.compile(
    r"\b(?:it (?:came|shall come|had come) to pass|as it happened)\b", re.IGNORECASE
)

# Purpose clause (Rule 7): "that they might / that ye may / that the curse might / that X should be"
# Broadened 2026-04-27 to catch noun-subject purpose clauses + broader modal list.
PURPOSE_RE = re.compile(
    r"^that\s+"
    # Subject: pronoun OR noun-phrase up to ~5 words before the modal
    r"(?:"
    r"(?:they|ye|he|she|we|you|I|it|thou|all|none|whoso|whosoever|none|some|those|these)"
    r"|(?:(?:the|a|an|my|thy|his|her|their|our|your|this|that|these|those|much|all|any|no)\s+)?"
    r"(?:[a-zA-Z][\w'-]*(?:\s+(?:and|of|in|to|the|a|an|my|thy|his|her|their|our|your)\s+[a-zA-Z][\w'-]*)*\s+){1,5}?"
    r")"
    # Modals: modern + archaic 2nd-person -est forms
    r"(?:might|may|should|would|could|must|shall|will|wilt|shalt|canst|cans|mayst|mayest|mightest|wouldst|wouldest|shouldst|shouldest|couldst|couldest)\s+(?:not\s+)?\b",
    re.IGNORECASE,
)

# "That is" appositive resumption — "well did he say that... that is, if..."
THAT_IS_APPOSITIVE_RE = re.compile(r"^that\s+is\s*,", re.IGNORECASE)

# Resumptive-that after intervening "if"-clause: prior line ends with comma
# after an if-protasis content; next line opens with "that" resuming the
# main complement. E.g., "thou hast said, that if ye do X, / that thou wilt Y"
RESUMPTIVE_AFTER_IF_RE = re.compile(r"\bif\b[^,]+,\s*$", re.IGNORECASE)

# "So X that Y" result clause — "so great was their fear that they fell to the earth"
# Result clauses are not purpose but mimic the pattern; they're not Rule 17 territory either.
SO_RESULT_RE = re.compile(
    r"\bso\s+(?:great|long|much|many|sore|exceeding|exceedingly|that|fast|loud|terrible|fierce)\b",
    re.IGNORECASE,
)

# Meta-announcement (BE-verb copular + predicate noun + "that"):
# Trigger is BE-verb on prior line. Check: does prior line's main verb resolve
# to a form of BE followed by a predicate noun?
META_BE_COPULA_RE = re.compile(
    r"\b(?:is|was|are|were|be|been|being|am)\s+(?:the|a|an|my|his|her|their|our|your|this|these|that|those|[A-Z])",
    re.IGNORECASE,
)

# Recitativum direct divine speech: "saith the Lord..., that [first-person]"
# Check: prior line has "saith the Lord/God/Lamb/Holy One/prophet" + first-person
# content on current line ("I will", "I know", "I have", "my", etc.)
DIVINE_SAITH_RE = re.compile(
    r"\bsaith\s+(?:the\s+)?(?:Lord|God|Lamb|Holy One|prophet)", re.IGNORECASE
)
FIRST_PERSON_DIVINE_RE = re.compile(r"^that\s+I\b", re.IGNORECASE)

# Relative-clause containment: if the final governing-verb-candidate is inside
# a relative clause ("that which has been spoken," "which he did say"), it's
# not the main predicate. Heuristic: line contains "that which has been" or
# "which has been" or "which was" before the final verb.
VERB_IN_RELATIVE_RE = re.compile(
    r"\b(?:that which|which) (?:has|have|had|was|were|is|are) been\b",
    re.IGNORECASE,
)

# Aspectual filter: "began/ceased/continued" alone is a finite verb
# ("the world began"), not aspectual. Aspectual construction requires "to V"
# or "V-ing" on same line. If "began to/ceased to/continued to" is present on
# line, it's aspectual; bare "began" at line end without "to" is finite.
ASPECTUAL_FOLLOWED_BY_TO_RE = re.compile(
    r"\b(?:began|begin|beginneth|cease|ceased|ceaseth|continue|continued|continueth)\s+to\b",
    re.IGNORECASE,
)


def tokenize_last_verb(line: str) -> str | None:
    """Extract the last governing verb from a line. Scans the whole line, not
    just the last word — handles cases like 'I rejoice exceedingly' where an
    adverb follows the verb. Filters NP-context false positives where the
    candidate is preceded by a determiner (their fear, the fear, etc.)."""
    stripped = line.rstrip().rstrip(",.;:!?\"'")
    words = stripped.split()
    if not words:
        return None

    # Walk from rightmost word back; find last governing-verb-candidate
    # whose preceding word is NOT a determiner (those would make it a noun).
    DETERMINERS = {
        "the", "a", "an", "my", "thy", "his", "her", "their", "our", "your",
        "this", "that", "these", "those", "much", "great", "any", "all",
        "no", "some", "every", "such", "exceeding", "exceedingly",
    }
    for i in range(len(words) - 1, -1, -1):
        candidate = re.sub(r"[^\w]", "", words[i].lower())
        if candidate not in ALL_GOVERNING_VERBS:
            continue
        # Check preceding word — if determiner-class, it's a noun, skip.
        if i > 0:
            prev = re.sub(r"[^\w]", "", words[i - 1].lower())
            if prev in DETERMINERS:
                continue
        return candidate
    return None


def is_purpose_clause(line: str) -> bool:
    """Detect purpose clauses ('that they might', 'that ye may', 'that the
    curse might be taken', etc.). Also catches result clauses ('so great...
    that they fell') via SO_RESULT_RE on the prior line."""
    return bool(PURPOSE_RE.match(line.lstrip()))


def is_so_result_clause(prior_line: str) -> bool:
    """Detect 'so X that Y' result clauses where the prior line has 'so + adjective'."""
    return bool(SO_RESULT_RE.search(prior_line))


def is_that_is_appositive(line: str) -> bool:
    """Detect 'that is, ...' appositive resumption."""
    return bool(THAT_IS_APPOSITIVE_RE.match(line.lstrip()))


def is_resumptive_after_if(prior_line: str) -> bool:
    """Detect resumptive-that pattern after an intervening 'if'-clause:
    prior line ends with an if-protasis; current that-line is the main
    complement resumption."""
    return bool(RESUMPTIVE_AFTER_IF_RE.search(prior_line))


def is_aictp(line: str) -> bool:
    """Detect AICTP formula."""
    return bool(AICTP_RE.search(line))


def is_meta_announcement(prior_line: str) -> bool:
    """Detect BE-verb copular construction suggesting meta-announcement."""
    return bool(META_BE_COPULA_RE.search(prior_line))


def is_divine_recitativum(prior_line: str, that_line: str) -> bool:
    """Detect 'saith the Lord, that I [first-person divine]' recitativum pattern."""
    return bool(DIVINE_SAITH_RE.search(prior_line)) and bool(
        FIRST_PERSON_DIVINE_RE.match(that_line.lstrip())
    )


def is_direct_discourse_intro(prior_line: str) -> bool:
    """Detect direct discourse with colon or 'saying:'."""
    stripped = prior_line.rstrip()
    return stripped.endswith(":") or stripped.endswith("saying,")


def verb_class(verb: str) -> str:
    """Classify a verb by its Rule 17 class."""
    if verb in CAUSATIVE_VERBS:
        return "causative"
    if verb in ASPECTUAL_VERBS:
        return "aspectual"
    if verb in SPEECH_VERBS:
        return "speech"
    if verb in COGNITION_VERBS:
        return "cognition"
    if verb in VOLITION_VERBS:
        return "volition"
    return "unknown"


def scan_file(path: Path, verbose: bool = False) -> list[dict]:
    """Scan one v2-mine file for Rule 17 violations."""
    violations = []
    lines = path.read_text(encoding="utf-8").splitlines()

    for i in range(len(lines) - 1):
        line = lines[i]
        next_line = lines[i + 1]

        # Skip blank lines and verse-number lines
        if not line.strip() or re.match(r"^\d+:\d+$", line.strip()):
            continue

        # Must end with comma (indirect discourse signal)
        if not line.rstrip().endswith(","):
            continue

        # Must have a governing verb at line end
        verb = tokenize_last_verb(line)
        if not verb:
            continue

        # Next line must start with "that "
        if not next_line.lstrip().lower().startswith("that "):
            continue

        # Apply exception filters
        reason_to_skip = None
        cls = verb_class(verb)

        # Exception 0 (§2.2 parallel-subordinator-stack license): if the
        # current verse contains >=2 lines beginning with "that ", the next-
        # line "that" is a §2.2 stack-member ATU (framework §2.2 explicitly
        # overrides §2.1 default for repeated-subordinator stacks). Skip.
        verse_start = i
        while verse_start > 0 and not re.match(r"^\d+:\d+$", lines[verse_start].strip()):
            verse_start -= 1
        verse_end = i + 1
        while verse_end < len(lines) - 1 and not re.match(r"^\d+:\d+$", lines[verse_end + 1].strip()):
            verse_end += 1
        that_led = sum(1 for j in range(verse_start, verse_end + 1)
                       if lines[j].lstrip().lower().startswith("that "))
        if that_led >= 2:
            reason_to_skip = "§2.2-parallel-stack-license"

        # Exception 1: Direct discourse (colon or "saying:")
        if is_direct_discourse_intro(line):
            reason_to_skip = "direct-discourse-intro"

        # Exception 2: AICTP formula
        elif is_aictp(line):
            reason_to_skip = "AICTP-rule-16"

        # Exception 3: Purpose clause (that they might / that ye may / that the curse might be)
        elif is_purpose_clause(next_line):
            reason_to_skip = "purpose-clause-rule-7"

        # Exception 3b: "So X that Y" result clause — not a Rule 17 complement
        elif is_so_result_clause(line):
            reason_to_skip = "so-X-that-Y-result-clause"

        # Exception 3c: "That is, ..." appositive resumption — not Rule 17 ccomp
        elif is_that_is_appositive(next_line):
            reason_to_skip = "that-is-appositive"

        # Exception 3d: Resumptive that after if-clause — main complement
        # was already attached; this is a continuation, not a new ccomp split
        elif is_resumptive_after_if(line):
            reason_to_skip = "resumptive-that-after-if-clause"

        # Exception 4: Verb is inside a "that which has been [verb]" relative
        # clause — it's not the main governing predicate. E.g., "go contrary
        # to that which has been spoken, / ..."
        elif VERB_IN_RELATIVE_RE.search(line):
            reason_to_skip = "verb-in-relative-clause"

        # Exception 5: Aspectual verb without "to" on same line — bare
        # "began" etc. is finite intransitive ("the world began"), not the
        # Rule 17 aspectual construction ("began to V").
        elif cls == "aspectual" and not ASPECTUAL_FOLLOWED_BY_TO_RE.search(line):
            reason_to_skip = "aspectual-bare-finite-not-aspectual"

        # Exception 6: Divine recitativum
        elif is_divine_recitativum(line, next_line):
            reason_to_skip = "recitativum-divine-speech"

        if reason_to_skip:
            if verbose:
                print(
                    f"SKIP {path.name}:{i+1} [{reason_to_skip}] "
                    f"{line.strip()[:60]!r} / {next_line.strip()[:40]!r}"
                )
            continue

        # Flag as violation
        violations.append(
            {
                "file": path.name,
                "line_num": i + 1,
                "verb": verb,
                "verb_class": verb_class(verb),
                "line": line.rstrip(),
                "next_line": next_line.rstrip(),
            }
        )

    return violations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", "-v", action="store_true", help="Show skipped exceptions")
    parser.add_argument(
        "--v2-dir",
        default="c:/Users/bibleman/repos/readers-bofm/data/text-files/v2",
        help="Directory containing v2-mine canonical files",
    )
    args = parser.parse_args()

    v2_dir = Path(args.v2_dir)
    if not v2_dir.exists():
        print(f"ERROR: {v2_dir} not found", file=sys.stderr)
        sys.exit(2)

    all_violations = []
    files = sorted(v2_dir.glob("*-v2.txt"))
    for path in files:
        violations = scan_file(path, verbose=args.verbose)
        all_violations.extend(violations)

    # Report
    print("=" * 72)
    print("Rule 17 (Complement Integrity) validator — BofM v2-mine corpus")
    print("=" * 72)
    print(f"Files scanned: {len(files)}")
    print(f"Violations found: {len(all_violations)}")
    print()

    if all_violations:
        # Group by verb class
        by_class: dict[str, list] = {}
        for v in all_violations:
            by_class.setdefault(v["verb_class"], []).append(v)

        for cls in sorted(by_class):
            print(f"--- {cls.upper()} verbs ({len(by_class[cls])} violations) ---")
            for v in by_class[cls]:
                print(f"[DEVIATION]  {v['file']}:{v['line_num']} [{v['verb']}]")
                print(f"    {v['line'][:100]}")
                print(f"    {v['next_line'][:100]}")
                print()

    else:
        print("No violations found. Rule 17 compliance is clean.")

    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
