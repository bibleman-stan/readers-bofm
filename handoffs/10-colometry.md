# 10 — Colometry, Sense-Lines & Line-Breaking Theory

This document captures the editorial methodology behind how Book of Mormon text is broken into sense-lines (cola). This is the intellectual heart of the Reading Edition — the line-breaking decisions determine how the text reads, breathes, and communicates.

## What Colometry Means in This Project

"Colometry" refers to dividing text into cola (singular: colon) — short sense-units that each carry one clause, phrase, or breath-group. In biblical scholarship, colometry has a long history in the study of Hebrew poetry (Psalms, Proverbs, prophetic oracles). We apply the same principle to Book of Mormon prose, treating it as a performed text that benefits from visible phrasing.

The goal is not poetry formatting — it's **legibility for oral delivery**. Each line should be a natural breath unit that a reader (or listener, or ESL learner) can process as a single thought.

## Three Layers of Source Text

| Layer | Folder | Origin | Status |
|-------|--------|--------|--------|
| v0 | `data/text-files/v0-bofm-original/` | 2020 BofM base text, paragraph format | Reference only |
| v1 | `data/text-files/v1-skousen-breaks/` | Royal Skousen's sense-line formatting | Input to reformatter |
| v2 | `data/text-files/v2-mine/` | Stan's hand-edited revision | **Canonical source** |

v2 is the authoritative text. Everything else is history. When Stan edits a v2 file, that becomes the new truth. HTML is rebuilt from v2 via `build_book.py`.

## The Reformatter (senseline_reformat_v8.py)

A 19-pass automated tool that takes Skousen's v1 breaks and applies mechanical rules to split or merge lines. Key passes include conjunction splits, subordinate clause breaks, list-stacking for parallel triads, and length-based rebalancing.

**The reformatter is a starting point, not the final word.** Stan hand-edits the v2 output. The reformatter's thresholds were tuned iteratively (v7→v8) to reduce over-splitting and leave semantic decisions to the human editor.

### Known v8 Threshold Decisions
- M6 (according-to split): raised from >58 to >72 chars
- M8 (", and [pronoun]"): widened from 45-70 to 60-90
- M9 (subject-predicate at modal): raised from >70 to >85
- M10 (long-line pattern): raised from >70 to >90
- M15 (passive+prep): raised from ≥50 to ≥65
- M18: NEW in v8 — list-stacking for parallel triads
- 70-90 char range deliberately left unsplit (semantic preference over mechanical splitting)
- M0 em-dash word attachment behavior differs from Stan's v2 in some cases
- M12 in+gerund may over-split at 53 chars

## Settled Principles

These are editorial rules established through discussion and applied consistently.

### 1. The Wayyehi Rule
**"And it came to pass that" stays on one line as a fixed formula — never break it.**

This is the Book of Mormon's signature narrative formula (Hebrew *wayyehi*). It functions as a single discourse marker, not a compound clause. Breaking it mid-phrase ("And it came to pass / that...") destroys the formulaic quality and creates a false enjambment.

Applied to all variants: "And it came to pass," "And it came to pass that," "And now it came to pass that," etc.

### 2. "Expedient That" as Fixed Idiom
**"It is expedient that" stays together — don't break at "that."**

Normally we break at "that" clauses. But "expedient that" functions as a single idiomatic unit, like "it came to pass that." The "that" is part of the idiom, not a subordinating conjunction introducing a new clause.

Example (2 Ne 25:16): "I say unto you that it is expedient that ye should keep the law of Moses as yet" — "expedient that" stays on one line.

Applied in 2 Ne 9:28, 9:48, 25:16 and elsewhere.

### 3. Rhetorical Address Formulas
**"And now, O king," stays as one unit.**

When the text uses a direct address formula (vocative), keep the address together. The break comes after the address, before the content of what's being said.

Example (Mosiah 12:13):
```
And now, O king,
what great evil hast thou done,
or what great sins have thy people committed,
that we should be condemned of God or judged of this man?
```

The address "And now, O king," is a single rhetorical unit. But when a second address appears in the same passage, it can be broken differently if the syntax warrants it: "and thou, O king, / hast not sinned" — here the address is interrupted by the predicate.

### 4. Circumstantial Clause Pairing
**Paired circumstantial phrases describing the same condition should stay on one line.**

Example (Mosiah 15:24):
```
and these are they that have died before Christ came,
in their ignorance, not having salvation declared unto them.
```

"In their ignorance" and "not having salvation declared unto them" are two descriptions of the same circumstance — they didn't know because nobody told them. Splitting them onto separate lines gives "in their ignorance" undue weight and breaks the pairing.

### 5. Equivalence Restated After a Break
**When "or" introduces a restatement/equivalence, keep it with the restated material.**

Example (Mosiah 15:24):
```
and they have a part in the first resurrection,
or have eternal life, being redeemed by the Lord.
```

"Or have eternal life" restates "part in the first resurrection" — they mean the same thing. The participial phrase "being redeemed by the Lord" attaches naturally to "eternal life" as its grounding. The break falls after "resurrection," and the restatement + explanation flow together on the second line.

### 6. Line Length as a Signal, Not a Rule
Short, staccato lines create emphasis and slow the reader down. Long lines create flow and momentum. Neither is wrong — the question is always whether the rhythm serves the rhetoric.

Abinadi's trial speeches (Mosiah 12-15) benefit from shorter, more rhythmic lines because the content is confrontational and prophetic. Lehi's blessings (2 Ne 1-4) can sustain longer lines because the tone is pastoral and expansive.

There's no hard character count threshold. The reformatter uses 70-90 chars as a guideline, but editorial judgment overrides.

## Unsettled / In Progress

### The "Behold" Question (from Stan's email, Mar 14)

Stan identified three functional types of "behold" in Book of Mormon text:

1. **Deictic** (pointing) — "Behold, I have dreamed a dream." Directs attention to something specific.
2. **Mirative** (surprise/discovery) — "And behold, they were gone." Marks unexpected information.
3. **Logical-connective** — "For behold, if the knowledge of the goodness of God..." Introduces an argument or explanation.

Each type may warrant different line-break treatment. Type C especially is interesting — it might benefit from being joined to the clause it introduces rather than standing alone.

"Lo" is distinct from "behold" — appears ~5-10 times, almost exclusively in Isaiah quotation blocks. Decision needed on whether "lo" in Isaiah follows our rules or defers to Isaiah's poetic structure.

**Status: UNPURSUED.** The three-type distinction hasn't been tested yet.

**Action items:**
- Test on Alma 5 or 2 Nephi 4:15-35
- Evaluate whether Type C benefits from line-joining vs standalone break
- Decide how "and behold" vs standalone "behold" affects placement
- Decide whether "lo" in Isaiah blocks follows our rules or defers to Isaiah's own structure

### Parry Parallel Alignment as Diagnostic

Donald Parry's Hebrew parallelism analysis identifies break-points within the text for parallel structures (chiasmus, synonymous parallelism, etc.). In 2 Nephi alone, 78% of Parry's structures have break-points that fall inside our sense-lines rather than between them.

This creates a diagnostic opportunity: Parry's parallel break-points can flag sense-lines that might benefit from revision. If we split a sense-line at a point Parry identifies as a parallel boundary, we improve both the reading flow and the Parry-style visual rendering.

**308 split candidates** identified across the canon by `parry_split_candidates.py`. ~98 high/medium-confidence splits were applied (semicolon breaks, comma+conjunction patterns) in the Mar 2 session. Remaining candidates are lower confidence and need editorial review.

### Isaiah Block Quotation Treatment (2 Ne 12-24)

These chapters are nearly 100% verbatim Isaiah quotation. The current sense-line breaking follows our general principles, but there's a question about whether Isaiah's own poetic structure should take precedence over our mechanical rules.

Isaiah was originally Hebrew poetry with its own colometric conventions — parallelism, chiastic structures, strophic divisions. Our English sense-lines may or may not align with the underlying Hebrew cola. No decision has been made about whether to privilege Isaiah's poetic structure in these chapters.

## Competing Theories / Tensions

### Mechanical vs Semantic Breaking
The reformatter applies syntactic/length rules. The editor applies semantic judgment. These don't always agree. The current resolution: mechanical rules handle the bulk, editorial override handles the exceptions. The v8 reformatter was deliberately loosened (raised thresholds) to reduce over-splitting, pushing more decisions to the editor.

### Read-Aloud vs Visual Scanning
Sense-lines optimized for oral delivery (natural breath pauses) may differ from lines optimized for visual scanning (clear clause boundaries). For example, a parenthetical aside might be best read aloud as part of a longer breath but visually benefits from its own line. The project prioritizes oral delivery — bomreader.com was built for read-aloud and ESL use.

### Skousen's Breaks vs Stan's Breaks
Royal Skousen's sense-line formatting (v1) reflects a particular scholarly approach to the text. Stan's revisions (v2) sometimes merge Skousen's breaks (especially for very short fragments) and sometimes add new ones. The divergences aren't systematic — they reflect case-by-case editorial judgment.

### Consistency vs Context
Should the same syntactic pattern always get the same break treatment? Or should context (rhetorical register, speaker identity, emotional tone) override? Current practice leans toward context — Abinadi's trial speeches get different treatment than Nephi's narrative transitions, even when the syntax is similar.

## Review Process

1. Stan edits v2-mine text files locally
2. Claude runs `git diff` on the changed file to see the edits
3. Claude categorizes each edit as merge (joining lines) or break (splitting)
4. Claude evaluates against the settled principles above
5. After approval: `python3 build_book.py --all` to rebuild HTML
6. Service worker cache version bumped
7. If audio exists for changed chapters, audio must be regenerated via Colab pipeline (changed lines invalidate cache)

---
*Created: 2026-03-18*
