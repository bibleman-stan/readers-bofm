---
name: jsonl
description: Read back the recent back-and-forth from another workspace's Claude session transcript, verbatim. Fires on "JSONL: <workspace>" (e.g. "JSONL: atu-method", "JSONL: meta-wiki", "JSONL: atu-nlp-wiki"), and on any request to see what was said, decided, promised, or found in a sibling session — including "what did we decide over in X", "catch up on the X session", and recovering intent lost to compaction.
---

# Reading a sibling session's transcript

Stan works across four Claude workspaces — this one, `atu-method`,
`atu-nlp-wiki`, and `meta-wiki` — and decisions made in one routinely govern work
here. **"JSONL: atu-method" means: go read the last several exchanges over there
and come back on the same page.**

This is **loop ⓪** in [`4-process/00-improvement-loops.md`](../../../4-process/00-improvement-loops.md):
the channel by which a session here can see the rest of the ecosystem. Not a
convenience — a session that cannot see its siblings will rebuild what one of
them already has, or act on a fact another one already disproved.

## Why the transcript, not memory or a summary

Claude Code writes every session to JSONL at
`~/.claude/projects/<cwd-slug>/<session-uuid>.jsonl`, where the slug is the
working directory with separators replaced by dashes
(`C:\Users\bibleman\repos\atu-method` → `c--Users-bibleman-repos-atu-method`).

**The context window degrades at compaction; the JSONL does not.** It is the
durable record and the only place a promise made in another session survives
verbatim. A claim about what was said in a prior session is a state claim about a
file on disk — read it, never reconstruct it.

## Do this

```
py -3 scripts/dump_session_tail.py atu-method            # last 12 exchanges
py -3 scripts/dump_session_tail.py meta-wiki 8 3000      # 8 exchanges, 3000-char cap
py -3 scripts/dump_session_tail.py --list                # what workspaces exist
py -3 scripts/dump_session_tail.py --path <file.jsonl>   # an exact transcript
```

`scripts/dump_session_tail.py` lives in this repo and travels with it. A copy of
the equivalent (`read_jsonl.py`) sits beside this file. Either fuzzy-matches the
workspace name, picks the most recently modified transcript, and emits only
user/assistant prose — tool calls, tool results, command echoes and system
reminders are stripped, because they are noise when reconstructing a conversation.

## Reading it well

**Start narrow, then widen.** Default to ~8–12 messages at a moderate cap. These
files run to tens of megabytes; a wide dump with a high cap buries the answer and
eats the context needed to act on it.

**Truncation is lossy in a specific direction.** Long assistant messages are cut
at the cap, and the *end* of such a message is where the recommendation and the
open questions live. If a truncated message looks load-bearing, re-run it alone
at a much higher cap rather than guessing.

**Hunt for the seam.** The useful content is usually a *decision* — "still yours
to decide", "queued in Pending-Decisions", "recommendation: (a)". Those govern
work here. Name them explicitly rather than summarising the exchange.

**A sibling's assistant messages are claims, not facts.** They were written by a
session that may have been wrong, and its state claims have aged. Re-verify
anything load-bearing against disk and git in *this* turn.

## Read BEFORE you build, not after

The sharpest lesson this skill exists to carry, learned 2026-08-07:

- Two sessions shipped the same JSONL reader on the same day without seeing each
  other, producing competing `jsonl/` and `read-jsonl/` skills with different
  instructions and different scripts.
- Later the same evening, this session "fixed" six paths that a sibling commit
  had just corrected — because it never ran `git log -3`. One command would have
  shown the commit sitting directly behind it with the answer in its subject.

**Reading a sibling once is not the same as reading it before you act.** Before
changing anything touched by another workspace, check `git log` in this repo and
the sibling's transcript — in that order, and first.

## After reading

Say what the other session decided, what it left open, and what that means here.
If it queued something for Stan, check whether this repo's
[`Pending-Decisions.md`](../../../Pending-Decisions.md) already carries it — an
item living in only one repo's queue is precisely the file-back gap loop ⓪ exists
to close.
