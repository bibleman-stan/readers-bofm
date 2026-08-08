#!/usr/bin/env python3
"""Dump the recent back-and-forth from another workspace's session transcript.

Backs the `JSONL: <workspace>` command. Claude Code writes every session to
    ~/.claude/projects/<cwd-slug>/<session-uuid>.jsonl
where the slug is the working directory with separators replaced by dashes
(C:\\Users\\bibleman\\repos\\atu-method -> c--Users-bibleman-repos-atu-method).

These transcripts are the durable record: the context window degrades at
compaction, the JSONL does not.

Merged 2026-08-07 from two independently-built versions — readers-bofm's
scripts/dump_session_tail.py and a user-level one — after each session shipped
the same tool the same day without seeing the other. Keeps the flag interface,
adds --grep and gzipped-archive reading.

Emits only user/assistant prose. Tool calls, tool results, sidechain (subagent)
turns and system reminders are dropped — noise when reconstructing a conversation.

    python read_jsonl.py readers-bofm
    python read_jsonl.py atu-nlp-wiki --turns 40
    python read_jsonl.py bofm --list
    python read_jsonl.py bofm --grep marschall
"""

import argparse
import datetime
import gzip
import io
import json
import os
import re
import sys
from pathlib import Path

PROJECTS = Path(os.path.expanduser("~")) / ".claude" / "projects"
ARCHIVE = Path(os.path.expanduser("~")) / ".claude" / "jsonl-archive"


def resolve(name: str) -> Path:
    """Friendly name -> project dir. Exact slug, then suffix, then substring."""
    if not PROJECTS.exists():
        sys.exit(f"no project store at {PROJECTS}")
    dirs = [d for d in PROJECTS.iterdir() if d.is_dir()]
    key = name.lower().strip().rstrip("/")
    for pick in ([d for d in dirs if d.name.lower() == key],
                 [d for d in dirs if d.name.lower().endswith("-" + key)]):
        if len(pick) == 1:
            return pick[0]
    part = [d for d in dirs if key in d.name.lower()]
    if len(part) == 1:
        return part[0]
    if len(part) > 1:
        opts = "\n  ".join(sorted(d.name for d in part))
        sys.exit(f"'{name}' matches several workspaces:\n  {opts}")
    opts = "\n  ".join(sorted(d.name.replace("c--Users-bibleman-", "")
                              for d in dirs))
    sys.exit(f"no workspace matching '{name}'. Available:\n  {opts}")


def sessions(d: Path) -> list:
    """Session files newest-first: live store plus any gzipped archive."""
    out = list(d.glob("*.jsonl"))
    arch = ARCHIVE / d.name
    if arch.exists():
        out += list(arch.glob("*.jsonl.gz"))
    return sorted(out, key=lambda p: p.stat().st_mtime, reverse=True)


def opener(p: Path):
    if p.suffix == ".gz":
        return io.TextIOWrapper(gzip.open(p, "rb"), encoding="utf-8",
                                errors="replace")
    return io.open(p, encoding="utf-8", errors="replace")


def turns(path: Path) -> list:
    """(timestamp, role, text) for real conversation turns only."""
    out = []
    with opener(path) as fh:
        for line in fh:
            if '"message"' not in line:
                continue
            try:
                o = json.loads(line)
            except ValueError:
                continue
            if o.get("isSidechain"):
                continue
            m = o.get("message") or {}
            if m.get("role") not in ("user", "assistant"):
                continue
            c = m.get("content")
            if isinstance(c, str):
                text = c
            elif isinstance(c, list):
                text = "\n".join(b.get("text", "") for b in c
                                 if isinstance(b, dict)
                                 and b.get("type") == "text")
            else:
                continue
            text = text.strip()
            if not text:
                continue
            if text.startswith("<") and "system-reminder" in text[:200]:
                continue
            out.append((o.get("timestamp", "")[:19].replace("T", " "),
                        m["role"], text))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace")
    # 12, not 30: these files run to tens of megabytes, and a wide dump buries
    # the answer while eating the context needed to act on it.
    ap.add_argument("--turns", type=int, default=12)
    ap.add_argument("--session")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--grep")
    ap.add_argument("--max-chars", type=int, default=3000)
    args = ap.parse_args()

    d = resolve(args.workspace)
    files = sessions(d)
    if not files:
        sys.exit(f"no session files in {d}")

    if args.list:
        print(f"{d.name} — {len(files)} session(s), newest first\n")
        for p in files[:20]:
            ts = datetime.datetime.fromtimestamp(p.stat().st_mtime)
            print(f"  {p.stem[:36]:38} {ts:%Y-%m-%d %H:%M}  "
                  f"{len(turns(p)):>5} turns"
                  + ("  [archived]" if p.suffix == ".gz" else ""))
        return 0

    path = files[0]
    if args.session:
        hit = [p for p in files if args.session in p.name]
        if not hit:
            sys.exit(f"no session matching '{args.session}' in {d.name}")
        path = hit[0]

    rows = turns(path)
    if args.grep:
        rx = re.compile(args.grep, re.I)
        rows = [r for r in rows if rx.search(r[2])]
        if not rows:
            sys.exit(f"no turns matching /{args.grep}/ in {path.stem}")

    shown = rows[-args.turns:]
    print("=" * 78)
    print(f"{d.name}  ·  session {path.stem[:36]}")
    print(f"{len(rows)} turns total; showing last {len(shown)}"
          + (f" matching /{args.grep}/" if args.grep else ""))
    print("=" * 78)
    for ts, role, text in shown:
        print(f"\n[{ts}] {'STAN' if role == 'user' else 'CLAUDE'}")
        if len(text) > args.max_chars:
            # Truncation is lossy in a direction: the END of a long assistant
            # message is where the recommendation and open questions live.
            print(text[:args.max_chars])
            print(f"… [+{len(text) - args.max_chars} chars cut from the END — "
                  f"re-run with a higher --max-chars if this one matters]")
        else:
            print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
