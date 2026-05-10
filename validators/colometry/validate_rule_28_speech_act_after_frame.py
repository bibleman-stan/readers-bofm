#!/usr/bin/env python3
"""
Validate Rule 28 (Speech-Act Announcement After Frame) — BofM v2-mine corpus.

Rule 28 (PROPOSED): When a speech verb's main-clause subject+verb is separated
from the direct discourse it introduces by an intervening adverbial frame
(temporal, locative, causal), the speech-act tag earns its own line.

Canonical example (Alma 22:15):
    And it came to pass that after Aaron had expounded these things unto him,  ← AICTP + temporal frame
    the king said:                                                              ← speech-tag on own line
    What shall I do...                                                          ← direct discourse

Two classifications:
  PASS              — speech-tag already on its own line, preceded by adverbial frame
  POTENTIAL-VIOLATION — speech-tag merged into the adverbial frame line

Exit code: 0 if no POTENTIAL-VIOLATION found, 1 otherwise.

Usage:
    python3 validate_rule_28_speech_act_after_frame.py
    python3 validate_rule_28_speech_act_after_frame.py --verbose
"""

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Speech verbs that introduce direct discourse (colon-terminated)
# ---------------------------------------------------------------------------
SPEECH_VERBS_RE = re.compile(
    r"\b(?:said|answered|spake|spoke|cried|replied|declared|exclaimed|"
    r"proclaimed|commanded|testified|saith|cried)\b\s*:",
    re.IGNORECASE,
)

# Speech-tag line: line that ends with a speech verb + colon (possibly trailing space)
SPEECH_TAG_LINE_RE = re.compile(
    r"\b(?:said|answered|spake|spoke|cried|replied|declared|exclaimed|"
    r"proclaimed|commanded|testified|saith)\s*:\s*$",
    re.IGNORECASE,
)

# Adverbial-frame subordinators — conservative list, whole-word match.
# "before" excluded: nearly always a locative preposition in BofM
#   ("before the king", "before them") not a temporal subordinator.
# "because" requires a following subject (not "of") to distinguish
#   causal clause ("because he sinned") from prepositional ("because of X").
ADVCL_SUBORDINATORS_RE = re.compile(
    r"\b(?:after|when|while|since|as)\b"
    r"|"
    r"\bbecause\s+(?!of\b)",  # causal clause only, not "because of"
    re.IGNORECASE,
)

# A line with an adverbial frame ends with a comma (clause continues)
# and contains one of the subordinators above.

# Merged-violation pattern: a single line containing BOTH an adverbial-frame
# subordinator AND a colon-terminated speech verb.
# Example: "And now when Aaron heard this, his heart began to rejoice, and he said:"
# "before" excluded (see note above).
MERGED_VIOLATION_RE = re.compile(
    r"(?:"
    r"\b(?:after|when|while|since|as)\b"
    r"|"
    r"\bbecause\s+(?!of\b)"  # causal clause, not "because of"
    r")"
    r".*\b(?:said|answered|spake|spoke|cried|replied|declared|exclaimed|"
    r"proclaimed|commanded|testified|saith)\s*:",
    re.IGNORECASE,
)


def is_verse_number(line: str) -> bool:
    """Return True if line is just a verse reference like '22:15'."""
    return bool(re.match(r"^\s*\d+:\d+\s*$", line))


def is_advcl_frame_line(line: str) -> bool:
    """
    Return True if this line looks like an adverbial frame:
    ends with a comma AND contains a subordinating conjunction.
    Conservative: require both conditions.
    """
    stripped = line.rstrip()
    if not stripped.endswith(","):
        return False
    return bool(ADVCL_SUBORDINATORS_RE.search(stripped))


def scan_file(path: Path, verbose: bool = False) -> tuple[list[dict], list[dict]]:
    """
    Scan one v2-mine file.

    Returns (pass_instances, violations) where each entry is a dict.
    """
    pass_instances = []
    violations = []

    lines = path.read_text(encoding="utf-8").splitlines()
    n = len(lines)

    for i, line in enumerate(lines):
        stripped = line.rstrip()

        # Skip blank lines and verse-number lines
        if not stripped or is_verse_number(stripped):
            continue

        # --- Case 2: POTENTIAL-VIOLATION candidate ---
        # Check FIRST (before PASS): a line with BOTH a subordinator AND a
        # colon-terminated speech verb is a merged violation.
        # Example: "And now when Aaron heard this, ..., and he said:"
        # Such a line also matches SPEECH_TAG_LINE_RE, so must be classified
        # here before the PASS branch can fire.
        if MERGED_VIOLATION_RE.search(stripped) and stripped.rstrip().endswith(":"):
            violations.append(
                {
                    "file": path.name,
                    "line_num": i + 1,
                    "line": stripped,
                }
            )
            if verbose:
                print(
                    f"VIOLATION  {path.name}:{i+1}  {stripped[:90]!r}"
                )
            continue  # Classified; skip PASS check

        # --- Case 1: PASS candidate ---
        # Line N is a speech-tag-only line (ends with speech-verb + colon).
        # Check line N-1 for adverbial frame.
        if SPEECH_TAG_LINE_RE.search(stripped):
            # Find the previous non-blank, non-verse-number line
            prev_idx = i - 1
            while prev_idx >= 0 and (
                not lines[prev_idx].strip() or is_verse_number(lines[prev_idx])
            ):
                prev_idx -= 1

            if prev_idx >= 0:
                prev_line = lines[prev_idx].rstrip()
                if is_advcl_frame_line(prev_line):
                    pass_instances.append(
                        {
                            "file": path.name,
                            "line_num": i + 1,
                            "speech_tag": stripped,
                            "frame_line": prev_line,
                            "frame_line_num": prev_idx + 1,
                        }
                    )
                    if verbose:
                        print(
                            f"PASS  {path.name}:{prev_idx+1}/{i+1}  "
                            f"{prev_line[:70]!r} / {stripped!r}"
                        )

    return pass_instances, violations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", "-v", action="store_true", help="Show each match as found")
    parser.add_argument(
        "--v2-dir",
        default="c:/Users/bibleman/repos/readers-bofm/data/text-files/v2-mine",
        help="Directory containing v2-mine canonical files",
    )
    args = parser.parse_args()

    v2_dir = Path(args.v2_dir)
    if not v2_dir.exists():
        print(f"ERROR: {v2_dir} not found", file=sys.stderr)
        sys.exit(2)

    all_pass: list[dict] = []
    all_violations: list[dict] = []

    files = sorted(v2_dir.glob("*-v2.txt"))
    for path in files:
        p, v = scan_file(path, verbose=args.verbose)
        all_pass.extend(p)
        all_violations.extend(v)

    total_speech_tags = len(all_pass) + len(all_violations)

    # Count all speech-tag+colon instances (pass + violation)
    # Violations are merged lines so are also speech-tag instances
    total_with_frame = len(all_pass) + len(all_violations)
    total_without_frame = 0  # tracked separately below

    # Re-scan to count bare speech-tag lines without advcl frame (for stats)
    bare_speech_tags = 0
    for path in files:
        lines = path.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            stripped = line.rstrip()
            if not stripped or is_verse_number(stripped):
                continue
            if SPEECH_TAG_LINE_RE.search(stripped):
                prev_idx = i - 1
                while prev_idx >= 0 and (
                    not lines[prev_idx].strip() or is_verse_number(lines[prev_idx])
                ):
                    prev_idx -= 1
                if prev_idx < 0:
                    bare_speech_tags += 1
                    continue
                prev_line = lines[prev_idx].rstrip()
                if not is_advcl_frame_line(prev_line):
                    bare_speech_tags += 1

    total_speech_tags_all = len(all_pass) + len(all_violations) + bare_speech_tags

    print()
    print("Rule 28 (Speech-Act Announcement After Frame) — BofM v2-mine corpus")
    print("=" * 72)
    print(f"Files scanned:                     {len(files)}")
    print(f"Total speech-tag+colon instances:  {total_speech_tags_all}")
    print(f"  With preceding adverbial frame:  {total_with_frame}")
    print(f"    [PASS]:               {len(all_pass):4d}  (already split — speech-tag on own line)")
    print(f"    [POTENTIAL-VIOLATION]:{len(all_violations):4d}  (currently merged — should split)")
    print(f"  Without preceding frame:{bare_speech_tags:4d}  (not Rule 28 territory)")
    print()

    if all_violations:
        print("POTENTIAL-VIOLATION instances:")
        print("-" * 72)
        for v in all_violations:
            print(f"  [{v['file']}:{v['line_num']}]")
            print(f"    {v['line']}")
        print()
    else:
        print("POTENTIAL-VIOLATION instances: none found.")
        print()

    print("PASS instances (sample, first 10):")
    print("-" * 72)
    for p in all_pass[:10]:
        print(f"  [{p['file']}:{p['frame_line_num']}/{p['line_num']}]")
        print(f"    frame:  {p['frame_line']}")
        print(f"    tag:    {p['speech_tag']}")
    if not all_pass:
        print("  (none detected)")
    print()

    print(f"RESULT: violations={len(all_violations)} strong={len(all_violations)} review=0")
    sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
