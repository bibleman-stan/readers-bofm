# BOM Reader — Handoff Documentation

This directory contains structured project documentation organized by domain. Each file is independently readable and covers one aspect of the project. When starting a new session, read all files to get full context.

## Files

| # | File | Covers |
|---|------|--------|
| 01 | `01-project-overview.md` | Architecture, key files, book metadata, CSS variables, body classes |
| 02 | `02-text-editorial.md` | Source text pipeline, editorial principles, swap system, intertextual markup |
| 03 | `03-audio-voice.md` | Voice decisions, ElevenLabs config, audio inventory, Colab pipeline, narration.js |
| 04 | `04-ui-ux.md` | Current UI structure, navigation, scroll behavior, known UI issues |
| 05 | `05-build-pipeline.md` | build_book.py, data layers, pericopes, Hebrew poetry, KJV diff, Firebase |
| 06 | `06-deployment-infra.md` | GitHub Pages, service worker, git workflow, security alerts |
| 07 | `07-pending-tasks.md` | Prioritized task list — immediate, when credits reset, bugs, low priority |
| 08 | `08-future-plans.md` | Spanish fork, Studying Edition, Read Along, shelved ideas |
| 09 | `09-bugs-fixed.md` | Historical bug fixes, key design decisions |
| 10 | `10-colometry.md` | Sense-line theory, settled principles, competing theories, "behold" analysis, review process |
| 11 | `11-research-ideas.md` | Potential papers: colometric stylometry, functional translation, sense-lines as silent commentary |
| 12 | `12-reformatter-rules.md` | Mechanical reformatter rules (M0-M10), editorial rules (E1-E11), calibration data, -eth conjugation, script thresholds |
| 13 | `13-preliminary-linguistic-data.md` | Quantified colometric metrics by book: AICTP rates, voice markers, structural metrics, preliminary voice taxonomy |

## Update Protocol

When updating these docs, **append a dated update block** at the bottom of the relevant file(s):

```markdown
---
### Update — 2026-MM-DD
- What changed
- What was decided
- New state
```

This preserves history so anyone reading the file can trace how things evolved.

## Two-AI Workflow (How This Project Is Managed)

This project uses two AI tools with distinct roles. Stan is the link between them.

| Tool | Role | File Access |
|------|------|-------------|
| **Claude Code** (VSCode) | File edits, commits, colometry review, build pipeline | Full repo access |
| **Claude.ai chat** | UI/UX design, brainstorming, research, mobile access | None — docs only |

**Sync protocol:** When Claude.ai reaches a decision, Stan carries it to Claude Code for implementation. When Claude Code makes changes, Stan updates Claude.ai with the relevant diff or summary. The handoff docs in this folder are the shared ground truth — kept current by Claude Code at the end of every session.

**To initialize a Claude.ai session:** Upload all files in this `handoffs/` folder to a Claude.ai Project, then paste the system prompt from `00-index.md` → "Claude.ai System Prompt" section below.

## Claude.ai System Prompt

```
You are a design and brainstorming partner for bomreader.com, a web reading
app for the Book of Mormon. The attached handoff documents are your complete
project context — read all of them before responding.

Your role in this workflow:
- UI/UX design, feature brainstorming, research discussions, ideation
- You cannot read or edit files directly — Stan is the bridge between you
  and Claude Code (the VSCode extension that handles all file/code/commits)
- When we reach decisions, Stan will carry them to Claude Code for implementation
- When Claude Code makes changes, Stan will bring you the relevant updates

Key constraint: never suggest changes to the canonical source text files
(data/text-files/v2-mine/) directly — those go through Claude Code with
Stan's explicit approval.

Start by confirming you've read the handoffs and tell me your understanding
of the current state of the project.
```

## AI Workflow

**Primary tool:** Claude Code (VSCode extension) — file reads/edits, git commits, colometry review, build pipeline. Stan pushes to GitHub.

**Mobile/brainstorming:** Claude.ai chat — accessible on phone for design, research threads, ideation. Use Claude.ai Projects with key handoff docs uploaded (especially `10-colometry.md`) for persistent context. Conversations can be moved into the Project later from desktop.

**COWORK deprecated** as of 2026-03-19. Claude Code covers all its GitHub capabilities with better project memory.

**Session continuity:** Handoff docs are the memory layer between sessions. Claude Code updates these at session end; Stan pushes. Each new session: read CLAUDE.md + all handoffs, then proceed.

**Obsidian vault:** Pointed at repo root (`C:\Users\bibleman\repos\readers-bofm`). `.obsidian/` is gitignored. "Show all file types" enabled so `.txt` source files are visible alongside `.md` handoffs.

## Old Handoff Files
The following files in the repo root are superseded by this directory:
- `COWORK-HANDOFF.md` — comprehensive but monolithic, covers Feb 28 - Mar 16
- `COWORK-HANDOFF-KJV.md` — KJV diff fix notes
- `HANDOFF.md` — Mar 18 session state

These can be kept for historical reference or deleted.
