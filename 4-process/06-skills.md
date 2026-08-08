# Skills available in a readers-bofm session

A **skill** is a written-down procedure that loads when its trigger fires, instead
of sitting in `CLAUDE.md` and costing context on every turn. `CLAUDE.md` is what
gets read *every* time; a skill is read *when needed*.

**They all live in one portfolio at `~/.claude/skills/`.** Stan's rule, 2026-08-07:
*"skills are skills; you move it to .claude; they can serve the project but
they're only you."* A skill belongs to Claude, not to a project — so it lives in
Claude's own home directory and loads in every workspace, including this one.

This repo's `.claude/` therefore holds settings and worktrees but **no skills**.
That is deliberate, and it is why this page exists: nothing in the repo folder
would otherwise tell you what a session here can actually do.

## The portfolio

| Skill | Fires when |
|---|---|
| `bofm-rebreak-at-scale` | Applying a segmentation change to the whole corpus and shipping it — a mass re-break, a v2-spray, a UD-correction sweep. Encodes the script chain and its mandatory gates in order. |
| `repoint-paths-safely` | Moving or renaming anything other files point at. Encodes the defects paid for on 2026-08-06/07, including the ones that blinded a gate silently. |
| `jsonl` | `JSONL: <workspace>` — read back what a sibling session decided. Loop ⓪ in [`00-improvement-loops.md`](00-improvement-loops.md). In this repo, `scripts/dump_session_tail.py` does the same job from the command line. |
| `atu-audit-tier` | The weekly atu-method machinery audit. |
| `atu-compaction-resume` | Recovering working state after a compaction or session resume. |
| `safe-scripting` | Any regex-heavy or multi-line script. Write it to a file and run the file; never a bash heredoc. |
| `transcribe-video` | Turning a video URL into a citable transcript note. |
| `zotero` / `zotero-cleanup` | Creating and repairing bibliography entries. |

Corpus-specific skills like `bofm-rebreak-at-scale` still live in the portfolio.
They *serve* this project; they *belong* to Claude. The distinction is the point
of the rule.

## Why one portfolio and not one per repo

I argued the opposite on 2026-08-07 — that each Claude should carry its own copy
in its own repo — and was wrong twice in the same evening. The record is worth
keeping, because the failure it produced is instructive.

**What one portfolio costs:** a skill written against this repo's machinery has to
stay general enough to be true elsewhere. `jsonl` names
`scripts/dump_session_tail.py` as *this repo's* command-line equivalent rather
than assuming it exists everywhere.

**What it buys:** one copy to improve. Within a single day, the per-repo model
produced two competing JSONL skills — `jsonl/` and `read-jsonl/`, different
instructions *and* different scripts — because two sessions built the same tool
without seeing each other. Merging them was the fix, and the merged skill's own
worked-outcomes section now carries that case: **reading a sibling once is not
the same as reading it before you build.**

## Related

- [`00-improvement-loops.md`](00-improvement-loops.md) — loop ② is "a paid-for lesson becomes a skill"; this page is its output register, and loop ⓪ is what should have prevented the duplicate
- [`../CLAUDE.md`](../CLAUDE.md) — what is read *every* turn, deliberately kept short
