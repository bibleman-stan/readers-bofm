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
