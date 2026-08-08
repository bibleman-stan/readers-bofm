#!/usr/bin/env python3
"""Dump the tail of a Claude Code session transcript as verbatim user/assistant text.

Claude Code writes every session to JSONL under
    ~/.claude/projects/<cwd-slug>/<session-uuid>.jsonl
where <cwd-slug> is the working directory with separators replaced by dashes,
e.g. C:\\Users\\bibleman\\repos\\atu-method -> c--Users-bibleman-repos-atu-method

These transcripts are the durable record — the context window degrades at
compaction, the JSONL does not. This script is how you read one back.

Usage:
    py -3 scripts/dump_session_tail.py <workspace> [n] [cap]
    py -3 scripts/dump_session_tail.py atu-method 12 4000
    py -3 scripts/dump_session_tail.py --list          # show known workspaces
    py -3 scripts/dump_session_tail.py --path <file.jsonl> [n] [cap]

  workspace  fuzzy match against project-directory names (e.g. "atu-method",
             "meta-wiki", "atu-nlp-wiki"). Picks the most recently modified
             transcript when a workspace has several.
  n          how many messages from the end (default 12)
  cap        truncate any single message to this many chars (default 4000)

Only `user` and `assistant` text is emitted — tool calls and tool results are
skipped, as are local-command echoes and system reminders, which are noise when
you are reconstructing a conversation.
"""
import json
import sys
from pathlib import Path

PROJECTS = Path.home() / ".claude" / "projects"
SKIP_PREFIXES = ("<local-command", "<command-name>", "<command-message>",
                 "Caveat:", "<system-reminder>", "<task-notification>")


def find_transcript(workspace: str) -> Path:
    if not PROJECTS.is_dir():
        sys.exit(f"no project directory at {PROJECTS}")
    cands = [d for d in PROJECTS.iterdir()
             if d.is_dir() and workspace.lower() in d.name.lower()]
    if not cands:
        sys.exit(f"no workspace matching {workspace!r}. Try --list.")
    # prefer the most specific name, then the most recent transcript in it
    cands.sort(key=lambda d: len(d.name))
    files = [f for d in cands for f in d.glob("*.jsonl")]
    if not files:
        sys.exit(f"workspace {cands[0].name} has no .jsonl transcripts")
    return max(files, key=lambda f: f.stat().st_mtime)


def messages(path: Path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("type") not in ("user", "assistant"):
                continue
            content = (d.get("message") or {}).get("content")
            parts = []
            if isinstance(content, str):
                parts.append(content)
            elif isinstance(content, list):
                for b in content:
                    if isinstance(b, dict) and b.get("type") == "text":
                        parts.append(b.get("text", ""))
            txt = "\n".join(p for p in parts if p and p.strip())
            if not txt.strip() or txt.lstrip().startswith(SKIP_PREFIXES):
                continue
            out.append((d["type"], d.get("timestamp", ""), txt))
    return out


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if args[0] == "--list":
        for d in sorted(PROJECTS.iterdir()):
            n = len(list(d.glob("*.jsonl"))) if d.is_dir() else 0
            if n:
                print(f"  {d.name}  ({n} transcript{'s' if n > 1 else ''})")
        return 0
    if args[0] == "--path":
        path, args = Path(args[1]), args[2:]
    else:
        path, args = find_transcript(args[0]), args[1:]
    n = int(args[0]) if args else 12
    cap = int(args[1]) if len(args) > 1 else 4000

    msgs = messages(path)
    print(f"### {path}")
    print(f"### {len(msgs)} text messages; showing last {n}\n")
    for kind, ts, txt in msgs[-n:]:
        if len(txt) > cap:
            txt = txt[:cap] + f"\n[... truncated, {len(txt)} chars total ...]"
        print(f"\n{'=' * 78}\n[{kind.upper()}] {ts}\n{'=' * 78}\n{txt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
