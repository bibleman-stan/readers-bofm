# 02 — Text & Editorial Work

## Source Text Pipeline

Three stages in `data/text-files/`:

| Folder | Contents |
|--------|----------|
| `v0-bofm-original/` | 2020 BofM base text (paragraph format) |
| `v1-skousen-breaks/` | Skousen sense-line formatting (reformatter input) |
| `v2-mine/` | **Stan's revised sense-lines** — the canonical source |

File naming: `01-1_nephi-2020-sb-v2.txt` through `15-moroni-2020-sb-v2.txt`

## File Format
Plain text, verse markers + one sense-line per line:
```
5:15
may seal you his,
that you may be brought to heaven,
that ye may have everlasting salvation and eternal life,
through the wisdom, and power,
and justice, and mercy
of him who created all things, in heaven and in earth,
who is God above all.
Amen.
```

## Editorial Principles (Sense-Line Breaking)

### Core Rules
- Lines should be natural breath units for read-aloud delivery
- Sense-line breaks are **editorial, not mechanical** — the reformatter handles common patterns but Stan hand-edits
- No indentation. All lines flush left. Wrap indent is CSS-only
- Parallel structures should be mirrored across lines
- Don't over-split short phrases; don't under-split long compound lines

### Specific Rules Established
- **Wayyehi rule:** "And it came to pass that" stays on one line as a fixed formula — never break it
- **"Expedient that":** treated as single idiom, don't break at "that"
- **Rhetorical address:** "And now, O king," kept as one unit
- **"And now, O king, / what great evil hast thou done"** — the address formula stays together, the question breaks after

### "Behold" vs "Lo" Methodology (from Stan's email, Mar 14 — UNPURSUED)
Stan wrote a detailed linguistic framework identifying three functional types of "behold":
1. **Deictic** (pointing) — "Behold, I have dreamed a dream"
2. **Mirative** (surprise) — "And behold, they were gone"
3. **Logical-connective** — "For behold, if the knowledge of the goodness of God..."

Each type may warrant different line-break treatment. "Lo" is distinct — appears ~5-10 times, almost exclusively in Isaiah quotation blocks.

**Action items (not yet done):**
- Test the three-type distinction on Alma 5 or 2 Ne 4:15-35
- Evaluate whether type C benefits from indentation vs full line break
- Decide how "and behold" vs standalone "behold" affects break placement
- Decide whether "lo" in Isaiah blocks follows our rules or defers to Isaiah's poetic structure

### Review Process
1. Stan edits v2-mine text files locally
2. Claude runs `git diff` on the changed file
3. Claude categorizes each edit as merge (joining lines) or break (splitting)
4. Claude evaluates against editorial principles
5. After approval: `python3 build_book.py --all` to rebuild HTML
6. If audio exists for changed chapters, regenerate via Colab

## Archaic Word Swap System

### Processing Order in build_book.py `apply_swaps()`:
1. **AICTP_SWAPS** (32) — "And it came to pass" variants
2. **COMPOUND_SWAPS** (45) — Multi-word phrases ("save it be" → "unless")
3. **SIMPLE_SWAPS** (161) — Single-word archaic → modern
4. **ETH_SWAPS** (167 + fallback) — Verbs ending in -eth
5. **DID verb conjugation** — "did VERB" → past tense
6. **THOU-EST conjugation** — "Thou verb_est" → "You base"

Output format: `<span class="swap" data-orig="archaic" data-mod="modern">archaic</span>`

### Two Swap Classes
- **`.swap`** — visible swap (dotted underline, hover shows source). For vocabulary modernization (notwithstanding→despite, afflictions→hardships)
- **`.swap.swap-quiet`** — no visible indicator. For high-frequency grammar words (thee→you, hath→has, unto→to)

### Context-Sensitive Swaps
- "exceedingly" → "very" (default) or "greatly" (with emotion/intensity verbs)
- "save" → "unless" (when not followed by pronouns/objects)
- "meet" → "fitting" (only after is/was/be)
- "bowels" — figurative → "depths of mercy" / "heart is filled with"; literal → "body"/"womb"
- "loins" — figurative (lineage) → "lineage"; literal → "waist"

### TTS Text Preference
Stan's stated rule: "I want our modified sense-lines, but I do NOT want modernized language for the voice. I want the authentic wording of the Book of Mormon." This means:
- Sense-line BREAKS come from the reading edition (HTML structure)
- TTS TEXT uses `data-orig` (authentic BofM wording), NOT `data-mod` (modernized swaps)
- Controlled by `get_text_from_element(el, use_modern=False)` in the Colab pipeline

## Intertextual Markup (.quote-bible)

### What Exists
476 `.quote-bible` spans across the books, concentrated in:
- 2 Nephi: 169 occurrences (narrative chapters, NOT the Isaiah block 12-24)
- 3 Nephi: 132 occurrences
- Mosiah: 87 occurrences

### Known Gap
The Isaiah block quotation chapters (2 Ne 12-24) have **zero** `.quote-bible` markup despite being 100% verbatim Isaiah. Same for 3 Ne 12-14 (Sermon on the Mount), Mosiah 14 (Isaiah 53). The markup only exists for shorter quotation phrases embedded in narrative.

### Design Decision
- Tried adding `font-style: italic` to `.quote-bible` — **Stan rejected it** (didn't look good)
- The `.quote-bible` markup remains in the HTML for the existing `sources-quotations` toggle layer
- Scope decision: only explicit/verbatim quotations, not allusions or echoes — "too much of a judgment call"

## rebreak.py
Utility script for automated sense-line rebalancing:
- Examines lines >78 chars for potential splits
- Examines lines <25 chars for potential consolidation
- Uses grammatical break-point patterns
- Status: has uncommitted changes (396-line diff from Mar 14) — unclear if WIP or ready

## Reformatter v8 Details
19-pass automated reformatter. Key threshold changes from v7:
- M6 (according-to split): >58 → >72
- M8 (", and [pronoun]"): 45-70 → 60-90
- M9 (subject-predicate at modal): >70 → >85
- M10 (long-line pattern): >70 → >90
- M15 (passive+prep): ≥50 → ≥65
- M18: NEW — list-stacking for parallel triads

---
### Update — 2026-03-18
- Applied sense-line edits to Mosiah chapters 4 and 15, adjusting line breaks per newly articulated colometry principles (see 10-colometry.md)
- Mosiah 15:15–18 ("how beautiful upon the mountains") restructured to break after the recurring phrase rather than mid-clause
- Mosiah 15:24 merged circumstantial clause pairing ("in their ignorance, not having salvation declared unto them" on one line)
- Mosiah 15:24 adjusted equivalence restatement ("or have eternal life, being redeemed by the Lord" grouped together)
- Rebuilt all HTML from updated Mosiah source text via `build_book.py --all`

---
### Update — 2026-03-19
- Added `amongst → among` as a quiet swap (no dotted underline) — 14 occurrences across the corpus
- Added to `QUIET_ARCHAICS` set in `build_book.py` (line ~33) and swap pair added near `betwixt → between` in the Isaiah archaic vocabulary section
- Rationale: "amongst" is a high-frequency archaic preposition equivalent to "among"; no visual decoration needed (same treatment as "unto", "thee", etc.)

---
*Last updated: 2026-03-19*

---
### Update — 2026-03-20
- Added `abase/abasing/abased → humble/humbling/humbled` as visible swap (dotted underline)
- One occurrence in corpus: Alma 4:13 "abasing themselves" → "humbling themselves"
- All inflected forms added defensively in "Full BofM archaic vocabulary" section of build_book.py
- Rationale: genuinely archaic, rare enough that readers would stumble; visible swap appropriate

---
*Last updated: 2026-03-20*

---
### Update — 2026-03-21
- Alma 5 editorial pass — sermonic voice breaks applied (parallel stacking, "I say unto you" isolation, vocative separation, rhetorical question isolation)
- "abase/abasing/abased → humble/humbling/humbled" visible swap confirmed (1 occurrence: Alma 4:13)
- First non-Isaiah contextual gloss added: Alma 5:27 "walked" — literary category, explains Hebrew halakh idiom
- FEF consistency pass: 1 Ne 1:4 genitive merge, Alma 4:5/4:6/4:9/4:11 temporal rebreaks, Jacob 2:14 vocative isolation
- Granular over-break scrub: 40 fixes across 1 Ne through Alma 5 (verb splits, dangling conjunctions, genitive orphans)

---
*Last updated: 2026-03-21*

---
### Update — 2026-03-21 (second entry)
- Full-corpus FEF mechanical scrub: 178 fixes across all 15 books (Alma 6-63, Helaman, 3 Nephi, 4 Nephi, Mormon, Ether, Moroni — the unedited books)
- "notwithstanding" context-sensitive swap fix in build_book.py: moved "a" and "an" from determiner list to clause-subject list to prevent false positive swaps inside "notwithstanding" constructions
- All 15 books rebuilt; service worker cache at v70

---
### Update — 2026-03-22–24
- 2026-03-22: FEF consistency pass continued — AICTP merge candidates fixed across 1 Ne (7), 2 Ne (7), Jacob (3), Alma-Moroni (17). Full corpus now consistent on wayyehi rule.
- 2026-03-23: Anaphoric clause audit — Rule 19 refined (expletive "it" in cleft constructions is cataphoric, not anaphoric; result clauses with new predication are cataphoric). 3 genuine violations fixed (Hel 14:27, 3 Ne 11:30, 3 Ne 23:12).
- 2026-03-23: Escalatory appositive pass — 9 breaks applied across Mosiah (3:19, 4:6, 5:15, 15:5, 18:2), 2 Nephi (9:19, 9:26), Mormon (7:7), Moroni (9:25). Rule 20 (polysyndeton + repeated possessive = stack) codified.
- 2026-03-23: Punctuation-dependency audit — 11 cases found where comma was sole basis for break. 7 manner adverbials merged back; 3 source/authority phrases correctly restored. Rule 21 (manner vs source/authority for "according to") codified. Principle established: punctuation must not have deterministic force.
- 2026-03-24: Divine title appositive pass — 6 INTRODUCING appositives stacked (2 Ne 25:19, Hel 14:12, 3 Ne 20:31, Morm 5:14, Ether 4:7, Mosiah 7:27). Rule 22 (introducing vs referencing) codified. 1 Ne 11:6 "the most high God" stacked.
- 2026-03-24: Alma 7:12 "according to the flesh" — merged back after punctuation principle applied. Manner adverbial, not source/authority.

---
*Last updated: 2026-03-24*

---
### Update — 2026-03-25–26
- Critical bug fix: `_fix_double_that` function was stripping 31 genuine purpose/content clause "that" across the corpus. Fixed with CLAUSE_STARTERS guard. Also removed paragraph-layer regex doing the same.
- Alma 10:13 merge, 10:17 vocative split, 10:19 appositive split
- Annotation system (Firebase) disabled — verse-num click handler removed
- 1 Ne 21:1 narrowing vocative split (Rule 23)
- Predictive mechanical breaks applied to entire corpus: Alma 12-63 (17), Helaman (4), 3 Nephi (11), Mormon (3), Ether (6), Moroni (1) — speech attributions, polysyndetic stacking, verb/content-clause breaks
- Definitional "which is" breaks: 5 applied (2 Ne 25:16, Jacob 7:7, Alma 12:27, Alma 18:13, 3 Ne 27:5) — Rule 24
- "And thus we see / that" editorial narrator breaks: 11 applied across 4 books — Rule 25
- Adjective + "that" complement merges: 19 fixed across 7 books (possible/expedient/desirous/necessary + "that") — Rule 26
- "Through" source/mechanism isolation: 10 fixes across 6 books (blood of the Lamb x3, his merits, faith on his name, through Christ, through Jesus Christ, etc.)
- Declaration verb/content breaks: 5 fixes (testified that, covenanted that, sworn that x2 parallel, covenant that)
- Alma 11-12 manual editorial pass: currency stacking, speech attributions, circumstantial frames, divine oath breaks
- Alma 13:28 virtue list pivot to match Mosiah 3:19 pattern
- Alma 7:12 "according to the flesh" merge (punctuation principle applied)

---
*Last updated: 2026-03-26*

---
### Update — 2026-03-28–29
- Navigation refactor implemented — hamburger menu, verse-level navigation with popover, standalone intro page, centered topbar. Multiple iterations to get layout right.
- Alma 12:1 and 12:3 parallel breaks at verb phrase | prepositional adjunct boundary.
- Verb + "that" audit completed — 131 instances tested, no verb-type rule found. Breaks governed by speech attribution, discourse formulas, and line length/breath (see 10-colometry.md for full analysis).

---
*Last updated: 2026-03-29*

---
### Update — 2026-03-29 (second entry)

#### Adversarial Methodology Audit — Major Reverts and Refinements

Conducted an adversarial review of all 26 colometric rules. Key findings:

**Rules reclassified into three tiers:** RULES (mechanical, reproducible), EDITORIAL PRINCIPLES (defensible but judgment-dependent), GUIDELINES (useful tendencies). See 10-colometry.md for full reclassification.

**Verb + "that" audit:** Tested 131 instances. No verb-type rule exists — the proposed "declarative vs perceptive" distinction was a pseudo-rule. Breaks are governed by speech attribution formulas, line length/breath, and the foundational test. The "I would that ye should [verb]" formula is 50/50 broken/merged — NOT a consistent pattern.

**Mechanical validation test:** Voice differentiation IS present in the text — 1.38 words/line spread between Abinadi (7.71) and Mormon Narrative (9.09). Standard deviation consistent across all sections (2.87-3.19), confirming the differentiation is in the TEXT, not in our editorial method.

**Compound list break signals — new grammatical criterion replacing Rule 20:**
Breaks within compound lists justified ONLY by grammatical signals:
1. Elided auxiliary + stacked participles (each is implied predication)
2. Possessive restart ("and his" after items without possessive)
3. Demonstrative ("and that/this/these")
4. Relative clause attached to the item

Without such signals, bare "and [noun]" items are compound objects of one grammatical act and MERGE.

**Reverts applied (editorial breaks that lacked grammatical justification):**
- Mosiah 4:6 — divine attribute stack (power/wisdom/patience/long-suffering) merged back. Abstract nouns, no structural signals.
- Mosiah 5:15 — divine attribute stack (wisdom/power/justice/mercy) merged back. Same.
- Mosiah 3:19 — "full of love" merged back with "submissive, meek, humble, patient." All predicate adjectives of one participle.
- Alma 13:28 — same virtue list pattern, merged back.
- Alma 7:10 — "a precious and chosen vessel" merged back with "she being a virgin." Both appositional noun phrases, same grammatical slot.
- Mosiah 18:2 — noun objects of "through" merged. Break retained at possessive restart ("and his resurrection").
- 2 Nephi 9:19 — break retained at demonstrative "that" ("and that lake of fire").
- 2 Nephi 9:26 — compound appositive merged after "that awful monster" frame.

**Retained breaks that pass grammatical tests:**
- Mosiah 15:5 passion verbs — elided auxiliary, each participle is implied predication
- Moroni 7:45 charity verbs — elided subject, each verb is independent predication
- Mosiah 18:2 at "and his resurrection" — possessive restart
- 2 Nephi 9:19 at "and that lake of fire" — demonstrative signal

**Methodological commitment:** Do not construct grammatical categories to justify editorial instincts. If a break can't be named in standard grammatical terms, it's an editorial decision — label it honestly.

---
*Last updated: 2026-03-29*
