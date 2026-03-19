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

## Old Handoff Files
The following files in the repo root are superseded by this directory:
- `COWORK-HANDOFF.md` — comprehensive but monolithic, covers Feb 28 - Mar 16
- `COWORK-HANDOFF-KJV.md` — KJV diff fix notes
- `HANDOFF.md` — Mar 18 session state

These can be kept for historical reference or deleted.
