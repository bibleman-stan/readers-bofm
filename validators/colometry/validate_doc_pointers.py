#!/usr/bin/env python3
"""
Detect broken file-path / cross-reference pointers in canon, CLAUDE.md,
and handoffs.

Triggered by 2026-04-27 detritus audit finding ~12 references to
`10-colometry.md` (a file that no longer exists; methodology was migrated
to `private/01-method/colometry-canon.md`).

Approach:
  1. For each .md file in scope, find file-path references using regex.
  2. Resolve each reference relative to the repo root, the source file's
     directory, AND a list of likely subdirs (validators/colometry/, data/,
     scripts/, colab/, etc.) -- since canon and handoffs frequently cite
     bare filenames whose home is a subdir.
  3. Flag references to files that don't exist anywhere checked.

Scope:
  - Canon (private/01-method/*.md)
  - CLAUDE.md
  - handoffs/*.md

Exit code: 0 if no broken pointers, 1 if any found.

Usage:
    python3 validate_doc_pointers.py
    python3 validate_doc_pointers.py --verbose
"""

import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

SCAN_PATHS = [
    REPO_ROOT / "private" / "01-method" / "colometry-canon.md",
    REPO_ROOT / "private" / "01-method" / "pericope-canon.md",
    REPO_ROOT / "CLAUDE.md",
] + sorted((REPO_ROOT / "handoffs").glob("*.md"))


# Subdirs to try when resolving bare filenames (canon §6 validator-table
# rows say `validate_rule_15_vocative.py`, not the full path).
SEARCH_SUBDIRS = [
    "",
    "validators",
    "validators/colometry",
    "validators/syntax",
    "data",
    "data/text-files/v2-mine",
    "data/syntax-reference",
    "scripts",
    "colab",
    "books",
]


# Regex patterns for file-path references in markdown:
#   - `path/to/file.ext` (backtick-wrapped)
#   - [text](path/to/file.ext) (markdown links)
#   - bare `file.md` mentions in narrative prose
PATH_RE = re.compile(
    r"`((?:[\w./\\-]+/)*[\w.-]+\.(?:md|py|html|js|json|txt|sh|ipynb))`"
    r"|"
    r"\]\(((?:[\w./\\-]+/)*[\w.-]+\.(?:md|py|html|js|json|txt|sh|ipynb))(?:#[\w-]+)?\)"
    r"|"
    r"\b((?:[\w-]+/)+[\w.-]+\.(?:md|py|html|js|json|txt|sh|ipynb))\b"
)


# Exact-match skip set
SKIP_PATHS = {
    # External sibling-project references
    "readers-gnt/handoffs/04-editorial-workflow.md",
    # Archive references
    "archive/colometry-canon-v1-retired-2026-04-19.md",
    "archive/colometry-canon-v1-archive.md",
    # Stan's vault paths
    "C:/vaults-nano/my_brain/00_Inbox/claude-brainstorming.md",
    # Synthetic / example paths in canon prose
    "example.md",
    "tmp/file.py",
    # Historical handoff references (described as deleted/superseded in handoffs/00)
    "10-colometry.md",
    "COWORK-HANDOFF.md",
    "COWORK-HANDOFF-KJV.md",
    "HANDOFF.md",
    # Gitignored Obsidian artifacts
    "Welcome.md",
    # Historical voice/audio pipeline references (decommissioned per handoffs/03)
    "readalong.html",
    "sister_m_pipeline.ipynb",
    "2nephi_sister_m.ipynb",
    "bom_reader_voices_v1.ipynb",
    "gen_2nephi.py",
    "colab/sister_m_pipeline.ipynb",
    "colab/bom_reader_voices_v1.ipynb",
    "colab/gen_2nephi.py",
    # Historical UI artifacts (described in handoffs/04 as pre-Mar 16 redesign)
    "old-toolbar.html",
    "old-toolbar-js.js",
    "text-mode-system.md",
    # Pre-publication / removed assets
    "data/book-introductions.html",
    # Historical-deletion references (file is described as deleted/superseded
    # in the same prose that names it)
    "data/syntax-reference/english-break-rules.md",  # canon §8 2026-04-19 PM "Layer 1 prose draft deleted"
    "assemble_all.py",  # handoffs/12 "originally developed during ... the earlier assemble_all.py build system"
    # Session-folder convention filenames (described in CLAUDE.md as a
    # pattern, not actual paths -- they live in gitignored session folders)
    "transcript.md",
    "session-notes.md",
    "session-notes-continuation.md",
    "decisions.md",
    "decisions-continuation.md",
    "pending.md",
}


# Prefix-match skips
SKIP_PREFIXES = (
    "C:/", "c:/", "/",
    "readers-",      # sibling projects
    "archive/",
    "private/",      # gitignored session folders, sub-method docs
)


# Memory files live external to the repo at
# C:\Users\bibleman\.claude\projects\...\memory\. Bare `feedback_*.md`
# references in canon/handoffs are correct as memory pointers.
MEMORY_FILE_RE = re.compile(r"^feedback_[\w-]+\.md$")


def is_allowed_skip(path_str: str) -> bool:
    if path_str in SKIP_PATHS:
        return True
    if path_str.startswith(SKIP_PREFIXES):
        return True
    if MEMORY_FILE_RE.match(path_str):
        return True
    return False


def resolve(ref: str, source_file: Path) -> Path | None:
    """Try repo-root, source-dir, and SEARCH_SUBDIRS. Return existing path or None."""
    rel = ref.replace("\\", "/")
    # Source-file directory first (relative imports within a doc tree)
    candidate = source_file.parent / rel
    if candidate.exists():
        return candidate
    # Repo root + each candidate subdir
    for sub in SEARCH_SUBDIRS:
        candidate = REPO_ROOT / sub / rel if sub else REPO_ROOT / rel
        if candidate.exists():
            return candidate
    return None


def scan_file(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    broken = []
    for i, line in enumerate(lines, start=1):
        for m in PATH_RE.finditer(line):
            ref = m.group(1) or m.group(2) or m.group(3)
            if not ref:
                continue
            if is_allowed_skip(ref):
                continue
            if resolve(ref, path) is not None:
                continue
            broken.append({
                "file": path.relative_to(REPO_ROOT),
                "line": i,
                "ref": ref,
                "context": line.strip()[:120],
            })
    return broken


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    print("=" * 72)
    print("Doc-pointer integrity validator")
    print("=" * 72)
    print()
    print(f"Scanning {len(SCAN_PATHS)} files for file-path references...")
    print()

    all_broken = []
    for path in SCAN_PATHS:
        all_broken.extend(scan_file(path))

    if not all_broken:
        print(f"Files scanned: {len(SCAN_PATHS)}")
        print("Violations found: 0")
        print()
        print("All file-path references resolve to existing files.")
        return 0

    print(f"Files scanned: {len(SCAN_PATHS)}")
    print(f"Violations found: {len(all_broken)}")
    print()

    by_ref = {}
    for b in all_broken:
        by_ref.setdefault(b["ref"], []).append(b)

    if args.verbose:
        for b in all_broken:
            print(f"[DEVIATION]  {b['file']}:{b['line']} -> {b['ref']}")
            print(f"    {b['context']}")
            print()
    else:
        for ref, bs in by_ref.items():
            print(f"  {ref}: {len(bs)} reference{'s' if len(bs) != 1 else ''}")
            for b in bs[:3]:
                print(f"    {b['file']}:{b['line']}")
            if len(bs) > 3:
                print(f"    ... +{len(bs) - 3} more")
            print()

    print("Each violation is a file-path reference that doesn't resolve.")
    print("Either (a) update to the correct path, OR (b) add to SKIP_PATHS")
    print("if the reference is intentional (external / archive / example).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
