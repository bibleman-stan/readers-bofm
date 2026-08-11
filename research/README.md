# research/ — third-party sources (payloads untracked, this manifest tracked)

Nothing here is committed except this file. **This repo is public**, so what
lands in it is a publication decision, not a filing one.

**Our own analysis does not live here.** It goes in the numbered tiers. Nine
files were moved out on 2026-08-10:

| Moved to | Files |
|---|---|
| `1-method/` | `binding-layer-design.md`, `gold-primitive-binding-design.md`, `v2-llm-adjudication-design.md` |
| `2-evidence/` | `per-book-syntactic-patterns.md`, `colometric_metrics.csv` |
| `3-project/mockups/` | `book-introductions.html`, `fef-whitespace-mockup.html`, `gloss_preview.html`, `swap-style-preview.html` |

They had been invisible to git under a blanket `research/` ignore — no history,
no diffs, no recovery.

## Copyrighted — may never be committed

| File | Source |
|---|---|
| `GrantHardy_2023_BiblicalQuotationsAll_TheAnnotatedBookofMor.pdf` | Grant Hardy, *The Annotated Book of Mormon* (Oxford, 2023) |
| `Marschall-2023.pdf` | Marschall 2023 |

## Derived from copyrighted sources — undecided, deliberately left here

These are extractions of Hardy's apparatus rather than our own observations. A
complete extraction of another scholar's annotation set is a different question
from a metric we computed ourselves, and committing it to a public repo would
publish it. **Pending Stan's decision; do not move without it.**

- `hardy_biblical_references.json`, `hardy_biblical_references.xlsx`
- `allusion_extractions_all.json`, `allusion_extractions_batch1_2.json`
- `allusion_analysis.xlsx`
- `bom_geographic_verses.xlsx` — provenance unconfirmed; grouped here rather than
  published on an assumption

`carmack-pos/` and `isaiah-gold/` are empty.

## Why this file exists

A blanket ignore leaves nothing behind when a directory's contents go missing.
On 2026-08-10 two Greek corpora were found absent from `readers-gnt` with no
deletion trace; the validators that needed them had been returning zero and
reporting success. A tracked manifest makes absence detectable.
