# 12 — Reformatter Rules & Calibration Data

This document preserves the detailed mechanical rule specifications, calibration data, and known limitations of the sense-line reformatter pipeline. Originally developed during the `senseline_reformat_v8.py` era and the earlier `assemble_all.py` build system.

These rules document the *mechanical* layer of sense-line processing. The *editorial* layer — human judgment about breath, meaning, and rhetoric — is documented in `10-colometry.md`.

---

## PART 1: MECHANICAL RULES (M0–M10)

Applied in order by the reformatter script. Deterministic — same input produces same output.

---

### M0. Em Dash Trailing Word Reattachment

**Trigger:** A line ends with `--[word][optional punctuation]`.

**Action:** Strip the trailing word from the current line. Prepend it to the next line.

**Why:** Skousen's convention keeps the word after `--` on the same line. Stan's convention treats `--` as a hard break — the word after it launches the next thought, so it belongs on the next line.

```
BEFORE: which they had obtained--how
        merciful the Lord had been in warning us

AFTER:  which they had obtained--
        how merciful the Lord had been in warning us
```

**Scope:** 37 instances in 2 Nephi. 100% mechanical.

---

### M1. AICTP Gets Its Own Line

**"And it came to pass that"** and its variants are always isolated on their own line.

**Trigger:** Line starts with any of these formulas AND total line length > 42 characters:
- `And it came to pass that`
- `And now it came to pass that`
- `For it came to pass that`
- `Wherefore it came to pass that`
- `And it came to pass,`
- `And it came to pass` (without "that")

**Action:** Split after the formula. The formula becomes its own line; the remainder starts the next line.

**Exception:** AICTP + very short clause that totals ≤ 42 chars stays merged.

**Note:** Post-FEF discovery (March 2026), many of these mechanical AICTP splits are now recognized as incorrect — AICTP + temporal/date + main clause should remain merged as FEFs. See `10-colometry.md` for the FEF framework that supersedes this rule in editorial review.

---

### M2. "Behold" as Mid-Line Hinge — Always Split

**Trigger:** "behold" appears mid-line (not within the first 15 characters), preceded by a comma, semicolon, or em dash.

**Action:** Split before "behold." The punctuation mark stays with the left side.

**Minimum halves:** Both sides must be ≥15 characters.

---

### M3. "Yea," Never Trails — Always Launches

**Trigger:** `, yea,` or `--yea,` appears mid-line with ≥10 chars preceding it.

**Action:** Split before "yea,". The comma or em dash stays with the left side.

---

### M4. "Insomuch that" Always Starts Its Own Line

**Trigger:** "insomuch that" appears mid-line with ≥10 chars preceding it.

**Action:** Split before "insomuch."

---

### M5. Vocative Split

**Trigger:** Line begins with `O` + address term AND line > 40 chars AND remainder ≥ 15 chars.

**Action:** The vocative address becomes its own line.

**Address terms:** my beloved brethren, my brethren, my sons, my son, my people, Lord, house of Israel, ye people, captive daughter of Zion.

---

### M6. "According to" Split on Long Lines

**Trigger:** Line > 58 characters AND contains `, according to`.

**Action:** Split before "according to." The comma stays with the left side.

**Note:** Threshold raised from >58 to >72 in v8.

---

### M7. Speech Verb + Content Word Split

**Trigger:** Line ≥ 48 characters AND contains a speech/communication verb followed (optionally through a recipient phrase) by a content-launching word.

**Speech verbs:** spake, spoke, speak, spoken, said, say, saith, rehearsed, testified, testify, prophesy, prophesied, preached, taught, teach, told, cried, declared, witnessed, witnessing, written, write, showed, show, sufficeth me to say, made known.

**Content-launching words:** `concerning`, `how`, `that` (+ subject pronoun/determiner only), `all things what`, `all things that`.

**Critical distinction for "that":** Only split when "that" introduces a **content clause** (followed by a subject pronoun or determiner: he, she, they, ye, I, we, it, the, a, there, this, my, his, our, thy, their, no, not, as, when, if, all, from). Do NOT split when "that" is **restrictive** (followed by a verb: "unto him that rejecteth," "them that fight"). Restrictive "that" = "the one(s) who."

---

### M8. ", and [Subject Pronoun]" Split

**Trigger:** Line is 45–70 characters AND contains `, and` followed by a subject pronoun (I, he, she, they, we, ye, it, thou) AND both halves ≥ 18 chars.

**Triad guard:** If the line contains 2+ instances of `, and`, it's a list — skip it entirely.

**Note:** Range widened from 45-70 to 60-90 in v8.

---

### M9. Subject-Predicate Split at Modal Verbs

**Trigger:** Line > 70 characters AND contains a modal verb (shall, will, should, would, must, can, could, may, might) where the subject phrase to its left is ≥ 30 characters.

**Guards (all must pass):**
- Left side ≥ 30 chars (genuinely long subject)
- Right side ≥ 20 chars
- No comma within 5 chars before the modal
- No "that" within 10 chars before (it's inside a that-clause)
- No speech verb within 15 chars before (reported speech)
- No "save" or "if" within 10 chars before (conditional clause)

**Note:** Threshold raised from >70 to >85 in v8.

---

### M10. Split Long Lines (>70 chars) by Pattern Priority

**Trigger:** Any line still > 70 characters after M0–M9.

**Action:** Scan for break candidates in priority order. Take the first matching pattern that leaves both halves ≥ 18 chars (left) and ≥ 15 chars (right). If multiple matches, prefer closest to center.

**Priority order:**

| Priority | Pattern | Break position |
|----------|---------|---------------|
| 1 | `: ` (speech colon) | After colon |
| 2 | `; ` (semicolon) | After semicolon |
| 3 | `--` (em dash) | After dash |
| 4 | `, and ` | Before "and" |
| 5 | `, that ` | Before "that" |
| 6 | `, which ` | Before "which" |
| 7 | `, but ` | Before "but" |
| 8 | `, for ` | Before "for" |
| 9 | `, because` | Before "because" |
| 10 | `, even ` | Before "even" |
| 11 | `, save ` | Before "save" |
| 12 | `, [prep/conj]` | Before word |

Full list for priority 12: unto, upon, from, in, to, or, nor, neither, until, after, before, lest, saith, according.

**For lines still > 70 after comma-patterns:** bare `that` + content word.

**For lines still > 75:** Non-comma prepositional patterns and fallback any-comma.

**Recursive:** If either half is still > 70 chars, apply the same process again.

---

### M11. Indentation

**Everything is flush left (margin-left: 0). No exceptions.**

---

## PART 2: EDITORIAL RULES (Human Review)

These require judgment about meaning, rhetoric, and breath. Applied during manual review of script output.

- **E1. Dual Length Check** — Over ~75 chars: decide case-by-case. Under ~20 chars: orphan check.
- **E2. Phrasal Verb Reunion** — Rejoin split phrasal verbs (bring out, come forth, cast out, etc.)
- **E3. Triad Symmetry** — A triad is one line or three lines, never two.
- **E4. Temporal Setup / Main Action Boundary** — Temporal/conditional setup gets its own line when followed by a new subject.
- **E5. Compound Objects Sharing a Verb** — "And" joining two things acted on (not two actions) stays together.
- **E6. Orphaned Participles** — Never split participle from complement ("Believing that ye shall receive" stays together).
- **E7. Restrictive vs. Non-Restrictive "Which"** — Restrictive (no comma, identifies): stays with noun. Non-restrictive (comma, describes): can be its own line. *Note: this has been significantly refined — see `10-colometry.md` "which" clause working hypothesis for the current extended-adjective vs. genuine-subordinate-clause distinction.*
- **E8. Exception/Save Clauses** — When the exception IS the punchline, own line. When it completes a negation in one breath, keep together.
- **E9. Stacked Participial Phrases** — Each "having..." gets its own line when stacked in parallel.
- **E10. Emotional Hinge Insertions** — "To his great astonishment," gets own line when it marks a shift.
- **E11. Final Phrases That Carry Theological Weight** — Give punchlines room to land.

---

## PART 3: CALIBRATION DATA

Statistical profile from 2 Nephi script processing (33 chapters, 779 verses):

**Before (Skousen):**
- Total lines: 3,251
- Median: 46 chars
- Over 70: 240 (7.4%)
- Over 75: 113 (3.5%)

**After (Script v5, all 11 mechanical rules):**
- Total lines: 3,460
- Median: 43 chars
- Over 70: 88 (2.5%)
- Over 75: 14 (0.4%)

**Changes:** 205 of 779 verses modified (26%).

**Breakdown by rule (approximate):**
- M0 (em dash reattachment): 37
- M1 (AICTP): 11
- M2 (behold hinge): ~2
- M3 (yea trailing): ~5
- M5 (vocative): ~6
- M6 (according-to): ~11
- M7 (speech+content): ~18
- M8 (and+pronoun): ~14
- M9 (subject-predicate): ~19
- M10 (long-line splits): ~82

Reference profile from 1 Nephi editorial work:
- Median line length: 45 characters
- Sweet spot: 25–75 characters per line

### Per-Book Corpus Stats (from full assembly, Feb 2026)

| Book | Verses | Chapters | Swaps |
|------|--------|----------|-------|
| 1 Nephi | 618 | 22 | (pre-existing, hand-refined) |
| 2 Nephi | 779 | 33 | 1,868 |
| Jacob | 203 | 7 | 577 |
| Enos | 27 | 1 | 64 |
| Jarom | 15 | 1 | 36 |
| Omni | 30 | 1 | 59 |
| Words of Mormon | 18 | 1 | 28 |
| Mosiah | 785 | 29 | 1,474 |
| Alma | 1,975 | 63 | 4,327 |
| Helaman | 497 | 16 | 1,360 |
| 3 Nephi | 785 | 30 | 1,847 |
| 4 Nephi | 49 | 1 | ~100 |
| Mormon | 227 | 9 | 535 |
| Ether | 433 | 15 | 943 |
| Moroni | 162 | 10 | 429 |

---

## PART 4: KNOWN SCRIPT LIMITATIONS

These patterns the script cannot reliably handle. Always check during review.

### L1. Temporal/Conditional Clause Boundaries Without Punctuation
"and had we remained in Jerusalem / we should also have perished" — subject change signals a clause boundary but there's no comma or keyword to trigger on. Too few instances with too many false positives.

### L2. Restrictive "that" After Question Words
"What could have been done more to my vineyard that I have not done in it?" — "that" = "which" (restrictive), but the content-clause heuristic sees "I" after "that" and thinks it's a content clause. Rare enough to stay editorial.

### L3. Lines 76–80 with No Clean Break
About 14 lines per book in this range have no comma, no modal after a long subject, no discourse keyword. These are genuinely single breath-units (especially Isaiah poetry). The script leaves them alone.

---

## PART 5: -ETH VERB CONJUGATION

The build pipeline handles 281 distinct -eth verb forms (archaic → modern). The complete table is maintained in `build_book.py`. Key design decisions:

**Fallback logic** for unknown -eth forms:
1. Exclusion check — skip if word is in NOT_ETH_VERBS (beneath, teeth, Nazareth, ordinals, etc.)
2. Strip -eth to get stem
3. Stem ending in -i → replace -i with -ies (crieth → cries)
4. Stem ending in double consonant → drop one consonant, add -s (putteth → puts)
5. Stem ending in -s, -sh, -ch, -x, -z → add -es (searcheth → searches)
6. Stem ending in silent-e pattern → add -s (cometh → comes)
7. Default → add -s

**Irregular past tense table** (126 entries) used by "did + verb" compound swap logic. When the script encounters "did [verb]", it looks up the verb to produce simple past form. Maintained in `build_book.py`.

---

## PART 6: SCRIPT CONFIGURATION THRESHOLDS

| Parameter | v5 Default | v8 Adjusted | Description |
|-----------|-----------|-------------|-------------|
| AICTP merge max | 42 | 42 | AICTP stays merged if total ≤ this |
| Vocative min line | 40 | 40 | Vocative split only on lines > this |
| Speech-content min line | 48 | 48 | M7 only on lines ≥ this |
| And-pronoun range | 45–70 | 60–90 | M8 only in this range |
| According-to threshold | 58 | 72 | M6 splits above this |
| Subject-predicate min line | 70 | 85 | M9 only on lines > this |
| Subject-predicate min left | 30 | 30 | Left half must be ≥ this |
| Long-line threshold | 70 | 70 | M10 triggers above this |
| Non-comma prep threshold | 75 | 75 | Non-comma prep patterns only > this |
| Min left half (M10) | 18 | 18 | M10 break rejected if left < this |
| Min right half (M10) | 15 | 15 | M10 break rejected if right < this |

Thresholds were calibrated against 1 Nephi editorial work and validated on 2 Nephi. v8 adjustments deliberately loosened several thresholds to reduce over-splitting and push more decisions to editorial review.

---

## PART 7: EDGE CASES & BUGS (Historical)

1. **Silent-e stems in -eth fallback:** cometh → stem "com" → "coms" (wrong). Fixed: added to KNOWN_ETH.
2. **Double consonant stems:** putteth → stem "putt" → "putts" (wrong). Fixed: strip one consonant.
3. **Non-verb -eth words:** "teeth", "thirtieth", "Nazareth" matched verb pattern. Fixed: NOT_ETH_VERBS exclusion set.
4. **Stem ending in -i:** crieth → "cris" (wrong). Fixed: replace -i with -ies.
5. **Past participle after "had":** "had beheld" → "had saw" (wrong). Fixed: post-processing pass swaps to participle form.

---
*Extracted from external vault `C:\vaults-nano\gospel\11-Readers_BofM\0-Framework\` on 2026-03-21. Original files: sense-line-editorial-guide-v2.md, bofm-production-reference.v3.md.*
