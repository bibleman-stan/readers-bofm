#!/usr/bin/env python3
"""
Detect §7.3 trigger #1 (closed-list extension) and related canon
extensions in staged canon changes. Used by the commit-msg hook to
block commits that introduce extensions without audit evidence.

Closes the gap: pre-commit hook gates regressions vs baseline (mechanical
violation count), but does NOT detect "new closed-list extension being
committed" (yesterday's emotion-class smuggling precedent).

This script:
1. Reads staged canon diffs (private/01-method/colometry-canon.md and
   pericope-canon.md).
2. Detects §7.3-trigger patterns in the additions.
3. Checks the proposed commit message (passed as argv[1]) for audit-
   evidence keywords AND for negation-guards that would falsify them.
4. Exits 0 if no extension OR extension + audit evidence present.
5. Exits 1 if extension detected without audit evidence.

Override: commit with --no-verify (explicit Stan-authorized bypass).

Usage (called from commit-msg hook):
    python3 validators/check_canon_extensions.py <commit-msg-file>
"""

import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CANON_FILES = [
    "private/01-method/colometry-canon.md",
    "private/01-method/pericope-canon.md",
]


# ---------------------------------------------------------------------------
# Canon-extension patterns (anchored to + lines in the diff)
# ---------------------------------------------------------------------------

# (a) New rule section: "### Rule NN — title"
NEW_RULE_RE = re.compile(r"^### Rule \d+\b")

# (b) New merge-override: "#### M1." through "#### M9."
NEW_MERGE_OVERRIDE_RE = re.compile(r"^#### M\d+\.")

# (c) New §1 principle / sub-clause with explicit "(added DATE)" provenance
NEW_DATED_PRINCIPLE_RE = re.compile(r"^### .+\(added 20\d\d-\d\d-\d\d")

# (c-bis) Catch-all: any new H3 heading that isn't structural (§-numbered,
# Rule N, Mn., or Part I/II/III). Catches new principle subsections like
# "### Mission", "### Container-Not-Originator" without requiring the
# explicit "(added DATE)" marker (most edits won't carry it).
# Ported from tanakh-reader 2026-04-28 (their c-bis).
NEW_PRINCIPLE_HEADING_RE = re.compile(
    r"^### (?!§|Rule\s+\d+|M\d+\.|Part\s+[IVX]+)[A-Z]"
)

# (d) Closed-list verb-class table row — "| Class | *examples* | Yes/No |"
CLOSED_LIST_TABLE_ROW_RE = re.compile(r"^\|\s*[A-Z][^|]+\|.+\|\s*(?:Yes|No)\s*\|\s*$")

# (e) New §7.3 trigger entry — numbered bold trigger in mandatory-audit list
NEW_TRIGGER_ENTRY_RE = re.compile(r"^\s*\d+\.\s+\*\*[A-Z][^*]+\*\*\s+—")

# (f) New SCOPE-exclusion bullet under existing rule (— *new exclusion*)
NEW_SCOPE_EXCLUSION_RE = re.compile(r"^-\s+\*\*[A-Z][^*]+\*\*\s+—")

# (g) New bullet item with bolded label (any sub-list addition under a rule).
# Looser than (f) — doesn't require em-dash; catches more bullet-list
# extensions. Ported from tanakh-reader 2026-04-28.
NEW_BULLET_LABEL_RE = re.compile(r"^-\s+\*\*[A-Z][^*]{2,}\*\*")


# ---------------------------------------------------------------------------
# Commit-message gate keywords
# ---------------------------------------------------------------------------

# Audit-evidence keywords — at least one must appear if extension detected.
#
# IMPORTANT (lesson from tanakh-reader 2026-04-28): bare "audit" is too loose
# — it false-passes messages like "fake commit without audit evidence"
# (substring match catches the negation). Require either a strong-signal
# keyword (specific section ref, named pattern) OR an audit phrase that
# includes a completion verb / verdict word.
AUDIT_KEYWORDS = [
    "hostile audit",
    "trigger #",
    "§7.3",
    "§7",
    "retract",
    "retracted",
    "post-codification",
    "post-detection",
    "corpus-fit",
    "§8 update log",
    "§8 entry",
    "update log",
    "stan-authorized",
    "stan-direct",
    # Audit + completion-verb phrases (paired so bare "audit" doesn't false-pass)
    "audit complete",
    "audit completed",
    "audit passed",
    "audit verified",
    "audit verdict",
    "audit clean",
    "audit ok",
    "audit done",
    "audit found",
    "audit run",
    "audit dispatched",
    "ran audit",
    "ran the audit",
    "completed audit",
    "performed audit",
]

# Negation guards — if any of these appear, fail regardless of any audit
# keyword. Defends against "fake commit without audit evidence" et al.
# Ported from tanakh-reader 2026-04-28.
NEGATION_PATTERNS = [
    "no audit",
    "without audit",
    "needs audit",
    "needs an audit",
    "audit pending",
    "audit later",
    "skip audit",
    "skipped audit",
    "no §7",
    "no trigger",
    "no update log",
    "todo: audit",
    "todo audit",
    "fake commit",
]

# Audit-skippable signals (per canon §7.3 skip-safe categories) — if message
# explicitly claims skip-safe AND the change is plausibly cosmetic, allow.
SKIP_SAFE_KEYWORDS = [
    "typo fix",
    "typo",
    "formatting",
    "defensibility-capture",
    "cross-reference update",
    "cross-ref update",
    "audit-skippable",
    "skip-safe",
]


def get_canon_diff() -> str:
    """Get the staged diff for canon files."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--unified=0"] + CANON_FILES,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return result.stdout
    except Exception:
        return ""


def detect_extensions(diff: str) -> list[tuple[str, str]]:
    """Return list of (trigger-name, matched-line) tuples found in diff
    additions. Uses elif-chained de-duplication so a single line doesn't
    double-trigger between (c)/(c-bis) and (f)/(g)."""
    indicators = []
    for line in diff.split("\n"):
        if not line.startswith("+") or line.startswith("+++"):
            continue
        body = line[1:].rstrip()
        if not body.strip():
            continue
        if NEW_RULE_RE.match(body):
            indicators.append(("new-rule", body[:80]))
        if NEW_MERGE_OVERRIDE_RE.match(body):
            indicators.append(("new-merge-override", body[:80]))
        if NEW_DATED_PRINCIPLE_RE.match(body):
            indicators.append(("new-dated-principle", body[:80]))
        elif NEW_PRINCIPLE_HEADING_RE.match(body):
            indicators.append(("new-principle-heading", body[:80]))
        if CLOSED_LIST_TABLE_ROW_RE.match(body):
            indicators.append(("closed-list-table-row", body[:80]))
        if NEW_TRIGGER_ENTRY_RE.match(body):
            indicators.append(("new-trigger-entry", body[:80]))
        if NEW_SCOPE_EXCLUSION_RE.match(body):
            indicators.append(("new-scope-exclusion", body[:80]))
        elif NEW_BULLET_LABEL_RE.match(body):
            indicators.append(("new-bullet-label", body[:80]))
    return indicators


def has_audit_evidence(message: str) -> bool:
    """True if message contains a positive audit-evidence signal AND no
    negation guard (e.g., "without audit") is present."""
    msg_lower = message.lower()
    if any(neg in msg_lower for neg in NEGATION_PATTERNS):
        return False
    return any(k in msg_lower for k in AUDIT_KEYWORDS)


def has_skip_safe_claim(message: str) -> bool:
    msg_lower = message.lower()
    if any(neg in msg_lower for neg in NEGATION_PATTERNS):
        return False
    return any(k in msg_lower for k in SKIP_SAFE_KEYWORDS)


def main():
    if len(sys.argv) != 2:
        print("Usage: check_canon_extensions.py <commit-msg-file>", file=sys.stderr)
        return 0  # don't block on usage errors
    msg_path = Path(sys.argv[1])
    if not msg_path.exists():
        return 0
    message = msg_path.read_text(encoding="utf-8", errors="replace")

    # Skip empty / merge / squash messages
    if not message.strip() or message.startswith("Merge ") or message.startswith("Squashed "):
        return 0

    diff = get_canon_diff()
    if not diff:
        return 0  # no canon changes staged

    indicators = detect_extensions(diff)
    if not indicators:
        return 0  # no extension detected

    if has_audit_evidence(message):
        print(f"[canon-extension-check] Detected {len(indicators)} extension indicator(s); audit evidence found in commit message. PASS.")
        return 0

    if has_skip_safe_claim(message):
        print(f"[canon-extension-check] Detected {len(indicators)} extension indicator(s); commit claims skip-safe. Allowing -- verify the claim is accurate.")
        return 0

    # Extension detected, no audit evidence, no skip-safe claim -> BLOCK
    print()
    print("=" * 72, file=sys.stderr)
    print("CANON EXTENSION DETECTED -- AUDIT EVIDENCE REQUIRED", file=sys.stderr)
    print("=" * 72, file=sys.stderr)
    print(file=sys.stderr)
    print("Per canon §7.3 trigger #1 (and related), this commit introduces", file=sys.stderr)
    print("canon extensions that require an adversarial audit per the", file=sys.stderr)
    print("Pre-commit Adversarial-Audit Discipline (CLAUDE.md).", file=sys.stderr)
    print(file=sys.stderr)
    print("Detected extension indicators:", file=sys.stderr)
    for trigger, line in indicators[:10]:
        print(f"  [{trigger}] {line}", file=sys.stderr)
    if len(indicators) > 10:
        print(f"  ... and {len(indicators) - 10} more", file=sys.stderr)
    print(file=sys.stderr)
    print("To proceed, the commit message MUST contain ONE of:", file=sys.stderr)
    print("  - An audit-evidence keyword: 'hostile audit', 'audit dispatched',", file=sys.stderr)
    print("    'audit complete', 'trigger #', 'post-codification', '§7.3',", file=sys.stderr)
    print("    '§8 update log'. (Bare 'audit' alone no longer passes -- pair it", file=sys.stderr)
    print("    with a completion verb to confirm the audit actually ran.)", file=sys.stderr)
    print("  - A skip-safe claim (e.g., 'typo fix', 'cross-reference update',", file=sys.stderr)
    print("    'defensibility-capture', 'audit-skippable') if change qualifies", file=sys.stderr)
    print("    per canon §7.3 audit-skippable categories.", file=sys.stderr)
    print("  - 'stan-authorized' or 'stan-direct' if Stan explicitly directed", file=sys.stderr)
    print("    the change without audit (rare).", file=sys.stderr)
    print(file=sys.stderr)
    print("Negation guards: phrases like 'no audit', 'without audit', 'audit", file=sys.stderr)
    print("pending', 'todo: audit', 'fake commit' fail the gate regardless of", file=sys.stderr)
    print("any positive keyword present.", file=sys.stderr)
    print(file=sys.stderr)
    print("To bypass entirely (Stan-only, explicit decision):", file=sys.stderr)
    print("    git commit --no-verify -m '...'", file=sys.stderr)
    print(file=sys.stderr)
    print("Reformulate the commit message OR run the audit and document its", file=sys.stderr)
    print("verdict in the message before retrying.", file=sys.stderr)
    print("=" * 72, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
