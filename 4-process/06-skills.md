# Skills in this project

A **skill** is a written-down procedure that loads when its trigger fires, instead
of sitting in `CLAUDE.md` and costing context on every turn. `CLAUDE.md` is read
*every* time; a skill is read *when needed*.

## The rule — skills live in this folder

**Stan, 2026-08-07:** *"Any skill you create for this project must live in
`./.claude/skills/<skill-name>/SKILL.md` — inside THIS folder. Do NOT write it to
`%USERPROFILE%\.claude\skills\` (the global bucket), and do NOT write it to a
parent directory's `.claude/`. Never symlink a skill to a target outside this
folder. If you think a skill genuinely belongs at the global or parent level, ask
before creating it there."*

**The reason is portability, not taste.** `~/.claude/` is *machine state*. Copy or
clone this folder to another machine and anything living there stays behind — the
skill does not error, it **silently vanishes**. A skill inside the project travels
with it: committed if this is a git repo, carried along by a plain folder copy if
not.

## This project's skills

`.claude/skills/`

| Skill | Fires when |
|---|---|
| `bofm-rebreak-at-scale` | Applying a segmentation change to the whole corpus and shipping it — a mass re-break, a v2-spray, a UD-correction sweep. Encodes the script chain and its mandatory gates in order. |
| `repoint-paths-safely` | Moving or renaming anything other files point at. Encodes the defects paid for on 2026-08-06/07, including the ones that blinded a gate silently. |
| `jsonl` | `JSONL: <workspace>` — read back what a sibling session decided. Loop ⓪ in [`00-improvement-loops.md`](00-improvement-loops.md). Ships with `.claude/skills/jsonl/read_jsonl.py`; `scripts/dump_session_tail.py` does the same job from the command line. |

## Also available, from the global bucket

These load in every workspace and were **not** created for this project, so they
stay where they are. Listed here only so the inventory is complete — a session
here can use them, but they will not travel with this folder.

`safe-scripting` · `zotero` · `zotero-cleanup` · `transcribe-video` ·
`atu-audit-tier` · `atu-compaction-resume`

Never edit or delete these from a session working here. They are shared machine
state and other workspaces depend on them; flag a problem rather than fixing it in
place.

## Getting this wrong

Worth keeping, because the location question was answered three different ways in
one evening before it was settled, and the arguments that felt strongest were the
wrong ones:

- *"It connects several repos, so it belongs above them."* Argued twice for the
  JSONL reader. Wrong both times — a skill's home is decided by **who owns it**,
  not by how many things it touches.
- *"One shared copy avoids duplication."* True, and beaten by portability: a
  shared copy that does not survive `git clone` has not avoided anything.
- The per-repo model does risk parallel versions — two sessions did ship
  competing JSONL readers on the same day. The fix for that is **loop ⓪, read
  before you build**, not hoisting the skill somewhere it cannot travel.

## Related

- [`00-improvement-loops.md`](00-improvement-loops.md) — loop ② is "a paid-for lesson becomes a skill"; this page is its register
- [`../CLAUDE.md`](../CLAUDE.md) — what is read *every* turn, deliberately kept short
