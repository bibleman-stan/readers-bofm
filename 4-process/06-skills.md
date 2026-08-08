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

## User-level — available here and everywhere

| Skill | Fires when |
|---|---|
| `jsonl` | `JSONL: <workspace>` — read back another repo's Claude session transcript. This is loop ⓪ in [`00-improvement-loops.md`](00-improvement-loops.md): the channel by which a session here sees what `atu-method`, `atu-nlp-wiki` and `meta-wiki` decided. It is user-level **by design** — a tool for connecting repos must work from all of them, not just one. |
| `safe-scripting` | Any regex-heavy or multi-line script. Write it to a file and run the file; never a bash heredoc. |
| `transcribe-video` | Turning a video URL into a citable transcript note. |
| `zotero` / `zotero-cleanup` | Creating and repairing bibliography entries. |

## Which level does a new skill belong to?

**Repo-level** if it names this corpus, this pipeline, or these gates —
`bofm-rebreak-at-scale` is meaningless anywhere else.

**User-level** if the procedure would serve any workspace, and especially if it
*connects* workspaces. A connective tool placed inside one repo works in one
direction only.

**Candidate for promotion:** `repoint-paths-safely` is currently repo-level, but
nothing in its procedure is BoFM-specific — every trap it records (bare
references without a trailing slash, a checker's own skip-list, files-scanned
dropping silently, archives that must not be rewritten) applies to `atu-method`
and the sibling reader repos, which have the same validator shape and have
already suffered the same failure. Its worked examples are local; its rules are
not. Moving it up would cost nothing and cover four more repos.

## Related

- [`00-improvement-loops.md`](00-improvement-loops.md) — loop ② is "a paid-for lesson becomes a skill"; this page is its output register
- [`../CLAUDE.md`](../CLAUDE.md) — what is read *every* turn, deliberately kept short
