# Documentation map — readers-bofm

Numbers are for things you **read**, in roughly the order you'd want them.
`scripts/`, `validators/`, `data/`, `books/`, `audio/` stay unnumbered because
they are things that **run** — the same split `atu-method` uses.

## The five places

| | holds | read it when |
|---|---|---|
| [`../1-method/`](../1-method/) | the ATU method for BoFM — canon, rules, scholarship | you need to know what a line is *supposed* to be |
| [`../2-evidence/`](../2-evidence/) | measurements of the deployed corpus; the retraction log | you want to know what the text *actually does* |
| **`3-project/`** (here) | what the product is — text, audio, UI, glossary, history | you're changing the edition |
| [`../4-process/`](../4-process/) | how work gets done — pipeline, gates, protocols, loops | you're about to change something and want to not break it |
| [`../Pending-Decisions.md`](../Pending-Decisions.md) | what needs Stan's ruling | always, first |

Cross-corpus methodology lives in `../../atu-method/` and is authoritative for
canon questions. The theory and scholarship behind it live in
`~/work/atu-nlp-wiki/`.

## This folder — the product

| # | File | Covers |
|---|---|---|
| 01 | [`01-overview.md`](01-overview.md) | Architecture, key files, book metadata, CSS variables, body classes |
| 02 | [`02-text-editorial.md`](02-text-editorial.md) | Source text pipeline, editorial principles, swap system, intertextual markup |
| 03 | [`03-audio-voice.md`](03-audio-voice.md) | Voice decisions, ElevenLabs config, audio inventory, Colab pipeline, narration.js |
| 04 | [`04-ui-ux.md`](04-ui-ux.md) | UI structure, navigation, scroll behaviour, known issues |
| 05 | [`05-future-plans.md`](05-future-plans.md) | Spanish fork, Studying Edition, Read Along, shelved ideas |
| 06 | [`06-bugs-fixed.md`](06-bugs-fixed.md) | Historical bug fixes, key design decisions |
| 07 | [`07-glossary.md`](07-glossary.md) | Grammatical vocabulary — AICTP, the atomic-thought test, complement clauses, FEF |
| 08 | [`08-reformatter-rules.md`](08-reformatter-rules.md) | Mechanical reformatter rules (M0–M10), editorial rules (E1–E11), calibration, -eth conjugation |
| 09 | [`09-linguistic-data.md`](09-linguistic-data.md) | Quantified colometric metrics by book: AICTP rates, voice markers, structural metrics |

## Next door — [`4-process/`](../4-process/)

| # | File | Covers |
|---|---|---|
| 00 | [`00-improvement-loops.md`](../4-process/00-improvement-loops.md) | How this work is supposed to get better at itself — five loops, which turn and which don't |
| 01 | [`01-pipeline-and-gates.md`](../4-process/01-pipeline-and-gates.md) | The corpus pipeline end to end, every gate, and the failure classes **nothing** catches. Read the blind spots twice. |
| 02 | [`02-operational-protocols.md`](../4-process/02-operational-protocols.md) | Shell and commit discipline; parallel dispatch; two-phase pipeline changes |
| 03 | [`03-build-pipeline.md`](../4-process/03-build-pipeline.md) | `build_book.py`, data layers, pericopes, Hebrew poetry, KJV diff |
| 04 | [`04-deployment-infra.md`](../4-process/04-deployment-infra.md) | GitHub Pages, service worker, git workflow |
| 05 | [`05-pending-tasks.md`](../4-process/05-pending-tasks.md) | Prioritised task list |

## Renumbering note (2026-08-07)

Files were renumbered contiguously when `4-process/` split off. Two different
files both carried a `12-` prefix before this, which is the kind of thing that
makes a folder feel arbitrary. Old numbers 10 and 11 were already vacant —
`10-colometry.md` migrated into `1-method/colometry-canon.md`.

## Update protocol

When updating these docs, **append a dated update block** at the bottom of the
relevant file rather than silently rewriting it — the same discipline the
retraction log follows.
