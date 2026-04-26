# Pericope Canon — BofM Reader

*Hand-curated method document for BofM Reader section headers. Modeled on the colometry canon (`colometry-canon.md`). The two canons are parallel — colometry governs LINE breaks (within-verse cola formatting); this canon governs SECTION breaks (multi-verse natural-unit boundaries). Both share psycholinguistic grounding (atomic-thought at one scale; atomic-attention-bite at the other), the descriptive-over-interpretive stance, and mechanical-trigger-over-editor's-feel discipline.*

*Status: **v0.1 (2026-04-26)** — initial draft. Subject to corpus-fit testing; choices on open decisions made by Claude per Stan's "make a choice and we'll iterate" directive.*

---

## How to use this document

If you are an AI agent reviewing or editing pericope decisions: read §0 (mission), §1 (framework), §2 (categories) before doing any work. §3-§4 are reference. §5 is the detailed trigger reference. §6 is the change protocol. §7 is update log.

Each pericope decision must be defensible against §1's six closed-list triggers. Editorial-feel decisions that don't trace to a trigger are Category B (flag for Stan).

---

## 0. Purpose and Stance

### Mission

Pericope headers serve four purposes in the BofM Reader, in priority order:

1. **At-a-glance orientation.** A reader scrolls in, lands somewhere, and within ~2 seconds knows what story or argument they're in. Without this, the text is a wall to ESL readers and children — the project's stated audience.

2. **Topic-shift signaling for readers who can't detect shifts implicitly.** Native English-speaking adults who grew up in LDS culture detect scene changes from formulaic markers and cultural cues. ESL readers and kids don't have those antennae yet. Headers are explicit scaffolding for the topic-shift detection they don't have automated.

3. **Reading-bite indicator.** A pericope is a unit a reader can hold in attention without backtracking. It's a natural pause-and-resume point. This is also where audio narration could chunk listening sessions.

4. **Comprehension priming.** A title told before reading activates the mental schema needed. *"Lehi Prophesies but Jerusalem Rejects Him"* primes the reader to hear rejection-language; without that priming, the verses go past undecoded.

**Teaching is a byproduct, not a goal.** Headers should not make doctrinal assertions. But clear and accurate descriptive headers naturally lend themselves to teaching — that emerges from doing the descriptive job well, not from aiming at it.

### Stance

- **Descriptive over interpretive.** Headers describe what happens or what is taught; they do not interpret meaning, prescribe doctrine, or make theological claims.
- **The text already has structure; we expose it.** Pericope boundaries are detected from natural signals in the text (speaker shifts, scene changes, formula resets), not imposed by editorial preference for evenly-spaced sections.
- **Frequency is output, not target.** Long unbroken sermons or quotation blocks legitimately get few headers. Dense doctrinal stretches with rapid topic shifts get many. Both are correct if they reflect the text's actual structure.
- **Pericopes are NOT constrained to chapter boundaries.** Chapter divisions are LDS-editorial (Pratt 1879) and not original to the text. A pericope spans whatever range its triggers define, including across chapter boundaries when natural.

### Ground

Same audience-grounding as colometry canon §0:
- ESL readers
- Children and newcomers
- Read-aloud delivery (audio narration)

The Reading Edition is one resource among many, not the canonical scriptural text — readers are encouraged to consult the canonical 2020 LDS edition for study, doctrine, and discussion. Pericope headers are reading aids, not study apparatus.

### Scope

This canon governs the pericope/section header layer. It does NOT govern:
- Line breaks within verses (colometry canon)
- Verse numbering (LDS canonical)
- Chapter numbering (LDS canonical, Pratt 1879)
- Cross-references / footnotes (LDS canonical or future Studying Edition)
- Audio chapter boundaries (currently track LDS chapters; may eventually track pericopes)

---

## 1. The Framework — Trigger-First, Text-Driven

### The Generative Principle

**Each natural-unit boundary in the text earns a pericope header.** The text already has these boundaries: scenes change, speakers shift, genres transition, topics turn, addressees re-target, formal frames open and close. The pericope canon's job is to define WHICH of those signals trigger a header — not to impose every-N-verses, and not to depend on editor's-feel.

There is no positive requirement to break beyond this; there is no positive requirement to merge units beyond this. The question at every candidate location is: *does a trigger fire here?*

### The Six Triggers (Closed List)

A pericope boundary is licensed by ONE of the following triggers:

1. **Speaker shift** — narrator → quoted character; character A → character B; narrator → letter author.
2. **Genre shift** — narrative → embedded sermon; narrative → quoted scripture; sermon → letter; etc.
3. **Scene change (narrative)** — time skip, location shift, character group change.
4. **Topic shift (within stable speaker)** — new theme/argument within continuous speaker. Mechanical proxy: closed list of BofM transition markers (see §5).
5. **Addressee shift** — speaker continues but audience changes (*"And now, my brethren"* → *"And now, my son Helaman"*).
6. **Formal-frame boundary** — letter open/close, prayer formula, sacrament prayer, oath formula, formal address opening/closing.

Triggers 1, 2, 3, 6 are mechanically detectable from text features. Trigger 4 is the hardest — its mechanical proxy enumerates *candidates*, not commands; each instance requires Category B confirmation (see §2).

### What is NOT a trigger

- **Versification.** Chapter and verse numbers are LDS-editorial; they suggest, never compel. A pericope may span across a chapter boundary if its triggers do.
- **Length alone.** "It's been 20 verses since the last header" is not a trigger. If no other trigger fires, no header.
- **Paragraph appearance in source.** The 2020 LDS edition's paragraph indentations are typesetting choices, not authoritative pericope signals.
- **Editor's-feel.** *"This seems like a good place for a break"* without a trigger is over-structuring (cf. colometry canon's `feedback_over_structuring_disposition`).
- **Pure formula occurrence.** *"And it came to pass that"* appears 1,353 times in the BofM (per the application-consistency audit). It signals scene-change in some occurrences and intra-scene continuation in others. Formula occurrence is necessary-but-not-sufficient.

### Floor

**Three-verse minimum.** A pericope shorter than 3 verses is not a unit; it is a labeled verse and creates more cognitive friction than it removes. If a topic genuinely runs only 1-2 verses before shifting again, the surrounding text-flow is more important than marking the micro-shift; absorb into adjacent pericope.

### Ceiling

**None.** Long unbroken sermons (King Benjamin's discourse, Mosiah 2-5) and quotation blocks (Isaiah 2-14 in 2 Ne 12-24, ~13 chapters of continuous prophecy) legitimately span dozens of verses. Length is *output* of trigger-density, not a constraint we enforce.

### Cross-chapter pericopes

Pericopes are NOT constrained to chapter boundaries. When a unit naturally spans (e.g., Alma 8:32 → 9:5 if the topic continues), the pericope header appears once at the start and is not repeated at the chapter boundary. The chapter break still displays as a chapter break (the LDS chapter division is preserved as a navigation/reference aid), but it does not interrupt the pericope.

**Implementation note:** the `pericope_index.json` may need to evolve to support cross-chapter pericopes (e.g., a `spans_to: {chapter: N, verse: M}` field). v0.1 of the canon allows this; the index format follows.

---

## 2. Autonomy Boundary — Categories A / B / C

Every proposed pericope decision falls into one of three categories:

### Category A — Clean Trigger Fire

Mechanical signature is unambiguous; no editorial discretion required. Examples:
- Speaker shift with quoted-discourse colon (Mosiah 2:9 narrator → King Benjamin)
- Genre shift to quoted scripture (3 Ne 22:1 begins Isaiah 54)
- Formal-frame boundary (Moroni 4:1 sacrament-of-bread formula begins)
- Addressee shift with vocative re-target (Alma 38:1 Alma turns from Helaman to Shiblon)

**Apply directly.** No flagging; no discussion.

### Category B — Editorial Discretion Required

Multiple equally-accurate placements or titlings exist; mechanical signature is ambiguous or trigger 4 (topic-shift) is the only candidate fire. Examples:
- *"And now"* marker fires but the topic is continuous (intra-topic re-emphasis vs. genuine shift)
- Title could be action-summary or topic-statement; both legitimately work
- Pericope boundary could be at v. N or v. N+1 (gradient shift)

**Flag for Stan.** Provide candidate options with reasoning; Stan picks.

### Category C — Theological Weight

Boundary or scope of sacred text where placement carries doctrinal implication. Rare for pericopes since we avoid interpretation, but boundary cases exist:
- Breaking a Hebrew poetic unit in quoted Isaiah (where colon-structure carries semantic weight)
- Sectioning a sacrament prayer mid-formula
- Pericope boundary that creates apparent doctrinal claim (*"Christ Commands the Wicked to Repent"* implies Christ commanded only the wicked)

**Discuss before touching.**

### §2 closing instruction

When uncertain between A and B/C on editorial/rhetorical grounds, treat as Category B. The same default-to-B discipline as colometry §2.

---

## 3. Quick-Reference Trigger Table

| # | Trigger | Mechanical signature | Default category |
|---|---|---|---|
| 1 | Speaker shift | Punctuation: colon + leading capitalized speech; *"saith / said unto X:"* formula | A |
| 2 | Genre shift | Quotation block boundary (KJV-diff index hit); letter formula; sermon-frame open | A |
| 3 | Scene change | Time skip (*"after many days"*, *"in the Nth year"*); location shift; character group change | A or B (B when AICTP fires without scene shift) |
| 4 | Topic shift | BofM transition markers: *"And now," "And again," "Behold," "Yea behold," "Wherefore," "Therefore," "And now I would that," "Now I say unto you"* | **B by default** (marker = candidate, not command) |
| 5 | Addressee shift | Vocative re-target mid-discourse | A |
| 6 | Formal-frame boundary | Letter open/close formulas; prayer formulas; oath formulas; sacrament prayers | A |

---

## 4. Title Format Reference

### Length

**4-10 words for the title proper.** Verse-range trailer in *(vv. N-M)* or *(v. N)* format follows the title.

### Voice

**Simple present, active.**
- ✅ *"Nephi Returns to Get the Brass Plates"*
- ❌ *"Nephi Returned to Jerusalem"* (past tense — less immediate)
- ❌ *"The Brass Plates Are Recovered"* (passive — less direct)

### Per-genre shape (closed list)

| Genre | Shape | Example |
|---|---|---|
| **Narrative** | Action / event summary | *"Nephi Sneaks into the City and Finds Laban"* |
| **Sermon / discourse** | Topic statement (descriptive) | *"Faith Precedes Knowledge"* |
| **Letter** | Speaker + topic | *"Mormon Writes to Moroni on Infant Baptism"* |
| **Prophecy / quotation block** | Source citation + content marker | *"Isaiah on the Servant of the Lord (Isa 49)"* |
| **Formal address (open/close)** | Occasion + speaker | *"King Benjamin's Farewell Sermon Begins"* |

### What titles must NOT do

- **Make doctrinal assertions** (*"The True Sacrament Restored"* — interpretive)
- **Pre-resolve narrative tension** when stakes turn on the resolution (*"Nephi Decides to Kill Laban"* spoils the dramatic arc)
- **Replace the verses** (so concise the reader could read only the title and skip the text)
- **Use loaded interpretive language** (*"the abominable church of the devil"* as a header — quote framing without context loads bias)
- **Frame in reverse** (*"Children Not Condemned to Hell"* for a chapter affirming infant grace — the title is technically true but framed as the negation of the target doctrine; better: *"Little Children Are Saved Through Christ"*)

### Cross-reference for quotation blocks

When a pericope is itself a quotation of another scripture (3 Ne 22 = Isaiah 54), the title cites the source: *"Isaiah on the Servant of the Lord (Isa 49)"*. This serves the project's audience — readers who don't know the source-material relationship benefit from the citation; scholarly readers expect it.

---

## 5. The Triggers (Detail)

### Trigger 1 — Speaker Shift

**Signature.** Punctuation marker (colon + capitalized leading speech) OR *"saith / said unto X:"* formula. The shift may be:
- Narration → direct discourse (*"And he spake unto them, saying:"* opens a sermon)
- Speaker A → speaker B in dialogue
- Narration → embedded letter (*"And he wrote saying:"*)
- Direct discourse → narration (the close of a sermon, return to narrative voice)

**Title shape.** Action/event for narrative-side opening; speaker + topic for discourse-side opening.

**Example.** Mosiah 2:9 — narrator's setup ends; King Benjamin's address begins. Header: *"King Benjamin's Farewell Sermon Begins (vv. 9-15)"* (formal-address shape).

**Category A** by default. Mechanical signature is unambiguous.

### Trigger 2 — Genre Shift

**Signature.** Narrative footing → quoted scripture (Isaiah, Malachi, etc.); narrative → embedded letter; narrative → prayer; narrative → sermon. Detection sources:
- Quotation block boundaries: traceable via the existing `kjv_diff_index` (which already maps BofM verses to OT/NT source verses)
- Letter boundaries: opening/closing formulas (*"I write unto you"*, *"This letter is from..."*, *"Yours, X"*)
- Prayer boundaries: formula + voicing shift (*"O Lord God"*, *"Father in heaven"*)

**Title shape.** Source citation + content for quotation; speaker + topic for letter; topic statement for embedded sermon.

**Example.** 3 Ne 22:1 — Christ's discourse in 21 ends; Isaiah 54 quotation begins. Header: *"Isaiah on Zion's Restoration (Isa 54)"*.

**Category A** by default.

### Trigger 3 — Scene Change (Narrative)

**Signature.** Time skip (*"after many days"*, *"in the Nth year of the reign of the judges"*, *"on the morrow"*), location shift (*"and they went forth from..."*), character group change (one party departs, another enters).

**Note on AICTP.** *"And it came to pass that"* appears 1,353 times in the BofM. It is NOT a pericope-trigger by itself — many AICTP occurrences are intra-scene continuation. AICTP + an actual scene shift is the mechanical signature; AICTP alone is not.

**Title shape.** Action/event summary.

**Example.** Alma 8:1 — scene shifts from Alma's preaching tour to Alma traveling to Melek. Header: *"Alma Travels to Melek and Preaches"*.

**Category A** when scene shift is unambiguous; **Category B** when AICTP fires without clear shift.

### Trigger 4 — Topic Shift (Within Stable Speaker)

**Signature.** Mechanical proxy — closed list of BofM transition markers:
- *"And now,"*
- *"And again,"*
- *"Behold,"* (in announcement-position; not the deictic-mid-clause use)
- *"Yea, behold,"*
- *"Wherefore,"*
- *"Therefore,"*
- *"And now I would that,"*
- *"Now I say unto you,"*
- *"Now I would that ye should"*

**Discipline.** Marker occurrence is **necessary but not sufficient**. Each candidate is **Category B by default** — editorial confirmation required. Many marker-occurrences are intra-topic re-emphasis or rhetorical-amplification, not genuine topic-shifts.

**Test for confirmation.** Does the content AFTER the marker introduce a new theme/argument that the content BEFORE the marker did not address? If yes, topic-shift. If the post-marker content extends, restates, or amplifies the pre-marker content, no shift.

**Title shape.** Topic statement.

**Example (genuine shift).** Mosiah 4:9-10 King Benjamin states "Believe in God; believe that he is..." — a new injunction sequence opens with *"And now,"* shifting from the prior shame/repentance theme to belief-injunctions.

**Example (false fire).** Mosiah 4:11 *"And again I say unto you as I have said before..."* — the *"And again"* explicitly RESTATES; no shift.

### Trigger 5 — Addressee Shift

**Signature.** Vocative re-target mid-discourse — speaker remains the same, audience changes. Common BofM patterns:
- *"And now, my brethren"* → *"And now, my son Helaman"*
- *"O ye Nephites"* → *"O ye Lamanites"*
- *"And ye, my brethren"* → *"And thou, my son"*

**Title shape.** Speaker + new addressee + content (or just speaker + addressee for very short addresses).

**Example.** Alma 36 begins as Alma's address to Helaman; Alma 38:1 shifts to Shiblon (*"My son, give ear..."*); Alma 39:1 shifts to Corianton (*"And now, my son, I have somewhat..."*). Three separate pericopes, one per son.

**Category A.**

### Trigger 6 — Formal-Frame Boundary

**Signature.** Letter opening/closing formulas, prayer-formula opens/closes, sacrament-prayer boundaries, oath formulas, formal address opening/closing.

**Title shape.** Occasion + speaker for formal addresses; speaker + content for letters; named-formula for prayers.

**Examples.**
- Moroni 4:1 — sacrament-of-bread formula begins. Header: *"The Sacrament Prayer for the Bread"*.
- Moroni 5:1 — sacrament-of-wine formula begins. Header: *"The Sacrament Prayer for the Wine"*.
- Mosiah 2:9 — King Benjamin's farewell sermon opens with formal-address frame. Header: *"King Benjamin's Farewell Sermon Begins"*.

**Category A.**

---

## 6. Change Protocol

This canon adopts the colometry canon §7 change protocol by reference. The 12 mandatory-audit triggers (cf. colometry canon §7.3) apply equally to pericope canon changes. In particular:

- **Trigger #12 — Post-codification corpus-fit verification** is especially relevant for the initial v0.1→v1.0 cycle. The current `pericope_index.json` (1077 entries) was generated 2026-03 without a documented method; the v0.1 canon prescribes a corpus-wide re-sweep against the six triggers as the validation pass.

### v0.1 → v1.0 cycle plan

1. **Corpus-wide pericope re-sweep audit** — agent reads each chapter against the 6 triggers; classifies existing entries as CONFORMING / NON-CONFORMING / NEEDS-RE-TITLING; identifies missing entries (Moroni 1-5 cluster, etc.).
2. **Stan reviews findings** — picks Category B calls; signs off on scope.
3. **Mechanical pass applies the verdicts** — updates `pericope_index.json` with new/revised entries.
4. **v1.0 canon entry in §7** — locks in the v0.1→v1.0 transitions.

---

## 7. Update Log

### 2026-04-26 — v0.1 Initial Draft

Triggered by Stan's observation that the existing `pericope_index.json` (1077 entries, hand-curated 2026-03) is inconsistent in accuracy and frequency with no documented rule. Density variance: Moroni at 2.4 pericopes/chapter (Moroni 1-5 each have a single pericope spanning the whole chapter) vs. corpus norm of 4-5/chapter. Title style varies between action-summary, topic-statement, event-marker, and genitive-noun-phrase shapes with no apparent rule. The 2026-03-10 commit message *"fix LDS language, correct misattributed titles, fill gaps"* implies known accuracy issues that were partially patched but not systematically resolved.

**Choices made by Claude per Stan's "make a choice and we'll iterate" directive:**
- 6-trigger closed list (speaker shift, genre shift, scene change, topic shift, addressee shift, formal-frame boundary)
- Trigger 4 (topic-shift) mechanical proxy = closed list of BofM transition markers; each instance Category B by default
- 5-genre title shape variants (narrative/sermon/letter/prophecy/formal-address)
- Simple present active voice; 4-10 word band
- Lean gist over spoiler-prevention (per Stan: not a strong concern if other marks are hit)
- Cite source for quotation blocks (Isa 49) — serves the audience
- Pericopes NOT constrained to chapter boundaries (per Stan: chapter divisions are arbitrary editorial)
- 3-verse floor; no ceiling

**Open for v1.0 review:** all of the above. v0.1 is explicitly subject to revision after corpus-fit audit and Stan review.
