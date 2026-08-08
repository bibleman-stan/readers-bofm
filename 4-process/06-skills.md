# Skills available in a readers-bofm session

A **skill** is a written-down procedure that loads when its trigger fires, instead
of sitting in `CLAUDE.md` and costing context on every turn. `CLAUDE.md` is what
gets read *every* time; a skill is read *when needed*.

They live at two levels, and only one of them is visible in this repo's folder —
which is why this page exists.

| level | path | loads |
|---|---|---|
| **user** | `~/.claude/skills/` | in **every** workspace Stan opens |
| **repo** | `readers-bofm/.claude/skills/` | only in a session working here |

## Repo-level — specific to this corpus

| Skill | Fires when |
|---|---|
| `bofm-rebreak-at-scale` | Applying a segmentation change to the whole corpus and shipping it — a mass re-break, a v2-spray, a UD-correction sweep. Encodes the script chain and its mandatory gates in order. |
| `repoint-paths-safely` | Moving or renaming anything other files point at. Encodes five defects paid for on 2026-08-06/07, including the two that blinded a gate silently. |
| `read-session-jsonl` | `JSONL: <workspace>` — read back what a sibling session decided. Loop ⓪ in [`00-improvement-loops.md`](00-improvement-loops.md). Uses `scripts/dump_session_tail.py` in this repo. |

## User-level — available here and everywhere

| Skill | Fires when |
|---|---|
| `safe-scripting` | Any regex-heavy or multi-line script. Write it to a file and run the file; never a bash heredoc. |
| `transcribe-video` | Turning a video URL into a citable transcript note. |
| `zotero` / `zotero-cleanup` | Creating and repairing bibliography entries. |

## Which level does a new skill belong to?

**Stan's rule, 2026-08-07: "a skill is specific to each claude — put YOURS in
YOUR .claude skills bucket."** A skill is the *agent's* procedure, not a shared
library. Each Claude carries its own, in its own repo's `~/.claude/skills/`, tuned
to what that Claude works on.

So the default is **repo-level**, including for procedures that look generic. Two
sessions needing the same capability each write their own version against their
own machinery — `read-session-jsonl` here calls this repo's
`scripts/dump_session_tail.py`; the `atu-method` Claude has its own.

That is deliberately *not* DRY, and the trade is explicit: some parallel effort in
exchange for each Claude's procedure staying legible, self-contained, and
independently editable. The thing DRY would buy — one shared copy — is exactly
what produced two competing `jsonl/` and `read-jsonl/` skills at user level on
the day this was written.

**User-level** stays for genuinely tool-shaped, agent-independent procedure with
no repo machinery behind it: `safe-scripting`, `zotero`, `transcribe-video`.

## Related

- [`00-improvement-loops.md`](00-improvement-loops.md) — loop ② is "a paid-for lesson becomes a skill"; this page is its output register
- [`../CLAUDE.md`](../CLAUDE.md) — what is read *every* turn, deliberately kept short
