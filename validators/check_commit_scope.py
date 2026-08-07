#!/usr/bin/env python3
"""
Detect cross-category staging-scope leaks in commits.

Codified 2026-05-16 per Stan-directive item 4 from
``directives/processed/2026-05-16-1500-pending-decisions.md`` — the
structural-discipline response to the recurring "audio files sweep into
a canon-prose commit" failure mode observed twice in one session
(commits ``0b9d5e9`` and ``f3822d3`` before reset).

Failure mode: files staged from category X (e.g., ``audio/``) sweep into
a commit whose message describes only category Y (e.g., canon work). The
classic shape: audio MP3s pre-staged by the audio workflow get pulled
into a canon-prose commit because the staging step ran ``git add -A`` /
because the working-tree state changed between ``git status`` and
``git commit``.

This script:
  1. Lists staged files (``git diff --cached --name-only``)
  2. Classifies each into a category (audio / canon / validator / script
     / web / data / corpus / scholarship / doc / other)
  3. If MULTIPLE categories are staged, checks that the commit message
     MENTIONS every staged category (substring match against an alias
     list per category)
  4. Exits 0 if scope is consistent; 1 with a clear block message
     otherwise

Override (in commit message):
  - Add ``category-skip: <cat1>,<cat2>`` to explicitly waive specific
    categories for this commit (intentional cross-category work).

Bypass entirely (Stan-only): ``git commit --no-verify``.

Usage (called from commit-msg hook):
    python3 validators/check_commit_scope.py <commit-msg-file>
"""

import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# Path classification — first matching predicate wins
# ---------------------------------------------------------------------------

def _is_audio(p: str) -> bool:
    return p.startswith("audio/")

def _is_canon(p: str) -> bool:
    return p in (
        "private/01-method/colometry-canon.md",
        "private/01-method/pericope-canon.md",
    )

def _is_scholarship(p: str) -> bool:
    return p.startswith("private/01-method/scholarship/")

def _is_corpus(p: str) -> bool:
    return p.startswith("data/text-files/")

def _is_validator(p: str) -> bool:
    return p.startswith("validators/")

def _is_script(p: str) -> bool:
    return p.startswith("scripts/")

def _is_web(p: str) -> bool:
    return p in ("build_book.py", "index.html", "sw.js") or p.startswith("books/")

def _is_data(p: str) -> bool:
    return p.startswith("data/") and not _is_corpus(p)

def _is_doc(p: str) -> bool:
    return (
        p.startswith("docs/")
        or p == "CLAUDE.md"
        or p == "README.md"
        or p.startswith("directives/")
        or p == ".gitignore"
        or p == "retraction-log.md"
        or (p.endswith(".md") and "/" not in p)
    )


CATEGORIES = [
    ("audio", _is_audio),
    ("canon", _is_canon),
    ("scholarship", _is_scholarship),
    ("corpus", _is_corpus),
    ("validator", _is_validator),
    ("script", _is_script),
    ("web", _is_web),
    ("data", _is_data),
    ("doc", _is_doc),
]


# Aliases — substring tokens that count as "mentioning" the category in
# the commit message. Tokens are matched case-insensitively as substrings
# (no word-boundary anchoring) to keep the check forgiving.
CATEGORY_ALIASES: dict[str, list[str]] = {
    "audio": ["audio", "samuel", "mp3", "elevenlabs", "tts"],
    "canon": [
        "canon", "rule", "§5", "§7", "§3", "§1",
        "R1", "R5", "R6", "R7", "R9", "R10", "R11", "R12", "R13",
        "R15", "R16", "R17", "R18", "R19", "R20", "R21", "R22",
        "R23", "R26", "R27", "R28", "R29",
        "M1", "M2", "M3", "M4", "EP-", "J1", "J2", "J3", "J4", "J5",
    ],
    "scholarship": ["scholarship"],
    "corpus": [
        "corpus", "v2-mine", "v2 mine", "v0-bofm", "v1-skousen",
        "lds-scriptures", "parry", "text-files",
    ],
    "validator": [
        "validator", "alignment-script", "alignment script", "pre-commit",
        "hook", "baseline", "applier", "check_", "run_all",
    ],
    "script": ["script", "scripts/"],
    "web": [
        "build_book", "index.html", "sw.js", "books/", "service worker",
        "cache", "html", "rebuild", "swap",
    ],
    "data": [
        "data/", "data ", "index.json", "geo_index", "contextual_glosses",
        "search_index", "stem_index", "hardy", "intertext",
    ],
    "doc": [
        "doc", "readme", "handoff", "directive", ".gitignore",
        "retraction-log", "claude.md",
    ],
}


def classify(path: str) -> str:
    for name, pred in CATEGORIES:
        if pred(path):
            return name
    return "other"


def get_staged_files() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return [p.strip() for p in result.stdout.splitlines() if p.strip()]
    except Exception:
        return []


def strip_comment_lines(message: str) -> str:
    """Drop ``# ...`` comment lines that git includes from commit templates;
    they could spuriously satisfy the mention check."""
    out = []
    for line in message.splitlines():
        if line.lstrip().startswith("#"):
            continue
        out.append(line)
    return "\n".join(out)


def message_mentions(message_lower: str, category: str) -> bool:
    for alias in CATEGORY_ALIASES.get(category, [category]):
        if alias.lower() in message_lower:
            return True
    return False


def parse_category_skip(message_lower: str) -> set[str]:
    """Parse ``category-skip: audio,scripts`` waiver from message."""
    m = re.search(r"category-skip:\s*([a-z, ]+)", message_lower)
    if not m:
        return set()
    return {c.strip() for c in m.group(1).split(",") if c.strip()}


def main() -> int:
    if len(sys.argv) != 2:
        return 0
    msg_path = Path(sys.argv[1])
    if not msg_path.exists():
        return 0
    message_raw = msg_path.read_text(encoding="utf-8", errors="replace")

    if (
        not message_raw.strip()
        or message_raw.startswith("Merge ")
        or message_raw.startswith("Squashed ")
    ):
        return 0

    message = strip_comment_lines(message_raw)
    message_lower = message.lower()

    files = get_staged_files()
    if not files:
        return 0

    by_category: dict[str, list[str]] = {}
    for f in files:
        cat = classify(f)
        by_category.setdefault(cat, []).append(f)

    # Don't gate on uncategorized files alone — they're informational
    cats = set(by_category.keys())
    cats.discard("other")

    # Single-category commits (or only "other" paths) pass silently
    if len(cats) <= 1:
        return 0

    # Multi-category: each must be mentioned (or category-skip-waived)
    skipped = parse_category_skip(message_lower)
    missing: list[str] = []
    for cat in sorted(cats):
        if cat in skipped:
            continue
        if not message_mentions(message_lower, cat):
            missing.append(cat)

    if not missing:
        cat_list = ", ".join(sorted(cats))
        print(f"[commit-scope-check] Multi-category commit ({cat_list}); all mentioned. PASS.")
        return 0

    # ---- BLOCK ----
    print()
    print("=" * 72, file=sys.stderr)
    print("CROSS-CATEGORY STAGING DETECTED -- COMMIT MESSAGE SCOPE MISMATCH", file=sys.stderr)
    print("=" * 72, file=sys.stderr)
    print(file=sys.stderr)
    print(f"Staged files span {len(cats)} categories:", file=sys.stderr)
    for cat in sorted(cats):
        n = len(by_category[cat])
        sample = by_category[cat][0]
        suffix = f"  (+{n-1} more)" if n > 1 else ""
        print(f"  [{cat:<12}] {sample}{suffix}", file=sys.stderr)
    print(file=sys.stderr)
    print(f"Commit message does NOT mention: {', '.join(missing)}", file=sys.stderr)
    print(file=sys.stderr)
    print("Likely cause: files from another category (often audio/) were", file=sys.stderr)
    print("staged in parallel with this commit's intended scope.", file=sys.stderr)
    print(file=sys.stderr)
    print("To proceed, choose one:", file=sys.stderr)
    print("  - Unstage the off-scope files:", file=sys.stderr)
    print("      git restore --staged <path>     # then commit separately", file=sys.stderr)
    print("  - Update the commit message to mention each missing category:", file=sys.stderr)
    for cat in missing:
        sample_alias = CATEGORY_ALIASES.get(cat, [cat])[0]
        print(f"      '{cat}'  (any of: {', '.join(CATEGORY_ALIASES.get(cat, [cat])[:5])})", file=sys.stderr)
    print("  - Add an explicit waiver line to the commit message:", file=sys.stderr)
    print(f"      category-skip: {','.join(missing)}", file=sys.stderr)
    print(file=sys.stderr)
    print("Bypass entirely (Stan-only, explicit): git commit --no-verify", file=sys.stderr)
    print("=" * 72, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
