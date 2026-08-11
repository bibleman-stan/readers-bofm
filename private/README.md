# private/ — layout and conventions

**This folder is gitignored and Dropbox-backed** (via directory junction to `C:\Users\bibleman\Dropbox\bom-reader-private`). It holds pre-publication material, methodology scripts, and active working documents that should not land in the public repository.

## Subdirectory layout

| Subdir | Purpose |
|---|---|
| `01-method/` | Methodology canon and its audit trail — the colometric rule set, rules audit, literature comparison |
| `02-research/` | Paper drafts, outlines, bibliography, strategy notes, research ideas |
| `03-sessions/` | Dated session artifacts — one subdirectory per session (e.g. `2026-04-15-rule20-class-p-relatives/`) |
| `05-scripts/` | BofM methodology scripts — scanners, audit tools, merge appliers — that haven't been promoted to public `5-machinery/scripts/` |

Numbering leaves gaps for future categories (04, 06, etc.) without renaming existing folders. Empty placeholder directories are not created — add a numbered folder when actual content needs a home.

## Root-level files

- `OVERSEER-DIRECTIONS.md` — live coordination file between this project and its sibling. Read on session start; update before session end.
- `README.md` — this file.

## Cross-project parallel

The GNT side has a parallel layout at `readers-gnt/private/`. This symmetry lets the overseer port insights between projects without translating file locations.

## When creating new files

- **Methodology refinements** → `01-method/colometry-canon.md` (the canon) or a new file in `01-method/`
- **Paper drafts, bibliography, strategy** → `02-research/`
- **Session-specific findings** → `03-sessions/[YYYY-MM-DD]-[topic-slug]/`
- **Cross-project traffic** → `OVERSEER-DIRECTIONS.md`
- **Anything unclear** → drop at `private/` root; the next overseer pass will file it

## Reorganization history

- **2026-04-13:** Initial `private/` structure created during cross-project reorg led by overseer. Paper drafts moved from committed `docs/`, research material from `research/`, scripts rescued from `/tmp/`.
- **2026-04-16:** Restructured to numbered folders. `docs/` renamed to `01-method/`, `papers/` split into `01-method/` (methodology docs) and `02-research/` (paper drafts), `sessions/` renamed to `03-sessions/`, `5-machinery/scripts/` renamed to `05-scripts/`. Empty placeholder directories (`affordances/`, `audits/`, `comparisons/`, `red-team/`, `scans/`) removed.
