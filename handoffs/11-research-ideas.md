# 11 — Research Ideas & Potential Publications

This document tracks ideas for academic papers, conference presentations, or research projects that emerge from the BOM Reader editorial work. These are not commitments — they're seeds worth preserving.

---

## 1. Colometric Stylometry: Authorial Voice Signatures in Sense-Line Decisions

### The Idea
When an editor breaks Book of Mormon text into sense-lines (cola), the break decisions are responsive to the underlying rhetorical structure of the text. Different authorial voices in the Book of Mormon appear to produce different colometric profiles — different typical line lengths, different ratios of short staccato lines to long flowing ones, different frequencies of parallelism, different relationships between line breaks and clause boundaries.

If these differences are measurable and systematic, they constitute an **independent line of evidence for multiple authorship** that doesn't depend on vocabulary, word frequency, or any of the traditional stylometric features. It's a new channel of data entirely.

### Why This May Be Original
- **Stylometry** on the Book of Mormon has been done extensively (Hilton, Larsen, Rencher, Schaalje, Fields) — but always on raw text features (word frequency, vocabulary richness, clause length, noncontextual word patterns)
- **Colometry** in biblical studies has a long history (Muilenburg, Kugel, O'Connor, Fokkelman) — but applied to Hebrew poetry, not to a modern English text translated from an ancient source
- **Nobody appears to have combined the two** — using editorial sense-line decisions as a stylometric signal. The BOM Reader project may be the first real-world dataset where thousands of colometric judgments have been made across a complete multi-author text by a single editor

### What the Data Might Show
Observable differences that emerged during the BOM Reader editorial process:

- **Nephi's narrative** (1 Nephi 1-7, 16-18): longer lines, flowing cadence, memoir-like. Lines tend to carry full clauses. Wayyehi formulas frequent.
- **Nephi's visions** (1 Nephi 11-14): shorter, more uniform lines. Cinematic quality — "I looked / and beheld X" pattern. Stichometric.
- **Lehi's blessings** (2 Nephi 1-4): warm, expansive, accumulative. Clauses build on each other. Lines allow subordinate phrases to attach.
- **Jacob's sermons** (2 Nephi 6-10, Jacob 2-3): tighter, more percussive. "Wo" sequences. More frequent breaks within verses. Prophetic register.
- **Nephi's theological discourse** (2 Nephi 25-33): dense, self-referential. Lines carry heavy doctrinal propositions. Different from his narrative voice.
- **Mormon's abridgment** (Mosiah onward): longer "weighted" lines, more information per line, enjambment across multiple lines before resolution. The "historian's pace."
- **King Benjamin's speech** (Mosiah 2-5): liturgical, psalm-like. Tight vertical structure. Lines designed for communal oral delivery — different from both Nephi's personal voice and Mormon's editorial voice.
- **Abinadi's trial** (Mosiah 12-16): confrontational, staccato in places, with long theological builds. Shifts between short prophetic declarations and extended Christological argument.
- **Isaiah quotation blocks** (2 Nephi 12-24): Hebrew poetic structure forcing shorter cola even in English. Half-colon strophes. Different from any Book of Mormon author's native voice.

### Methodological Approach
1. **Establish the dataset**: The BOM Reader v2 text files contain ~6,600 verses of editorially determined sense-line breaks made by a single editor (Stan), ensuring consistent editorial judgment across the corpus
2. **Measure colometric features per section/author**:
   - Mean and median line length (characters, words)
   - Line length variance / standard deviation
   - Short-line frequency (lines under N words)
   - Long-line frequency (lines over N words)
   - Lines-per-verse ratio
   - Break-at-conjunction frequency
   - Break-at-subordinator frequency
   - Parallelism density (lines that mirror adjacent lines)
3. **Compare across attributed authorial sections**: Nephi (narrative), Nephi (vision), Nephi (discourse), Lehi, Jacob, Enos, Mormon (narrative), Mormon (editorial comment), Benjamin, Abinadi, Alma, Jesus (3 Nephi), Moroni
4. **Statistical analysis**: Cluster analysis, PCA, or discriminant analysis to see if colometric profiles group by attributed author
5. **Control**: Compare against a null hypothesis of random or mechanical breaking (the v8 reformatter output) to show that editorial decisions carry authorial signal that mechanical rules don't

### Potential Venues
- **Interpreter: A Journal of Latter-day Saint Faith and Scholarship** — would reach the LDS scholarly audience
- **Maxwell Institute** (BYU) — if framed as textual criticism rather than apologetics
- **Digital Humanities conferences** (DH2027, etc.) — the methodology would interest the computational stylometry community regardless of the religious content
- **Journal of Book of Mormon Studies** — direct fit

### What's Needed to Pursue This
- [ ] Export line-length data per verse from the v2 text files (Python script)
- [ ] Map each verse to its attributed author/speaker (need an authorship attribution index)
- [ ] Run basic descriptive statistics to see if the differences are visually obvious before doing formal analysis
- [ ] Literature review: confirm nobody has done this (check Interpreter, JBMS, Maxwell Institute publications, DH conference proceedings)
- [ ] Decide on framing: faith-compatible scholarship? Neutral computational humanities? Both audiences?

### Existing Evidence from the BOM Reader Audit (Mar 18, 2026)

A systematic audit of the entire Small Plates corpus (1 Nephi through Words of Mormon — 1,690 verses, ~8,000+ line breaks) was conducted using the "atomic image" test: does each line present a complete, standalone mental image? The audit found **1 genuine merge candidate** across all seven books (1 Nephi 19:21 — a "must needs be" split from its complement clause, fixed).

This result is itself data. It means:
1. The editorial decisions are internally consistent across thousands of break points
2. The rules were formalized *after* the editorial work, yet the text already conformed — the editorial ear was applying coherent principles before they were articulated
3. The consistency holds across different authorial voices (Nephi narrative, Nephi vision, Lehi, Jacob, Enos, Jarom, Omni) — which means the *differences* between voices that emerge from the line-length data are real rhetorical differences, not artifacts of inconsistent editing

This is critical for the colometric stylometry argument: if the editing were sloppy, the colometric profiles wouldn't mean anything. The audit establishes that the dataset is clean.

### The Gemini Control Experiment (Mar 18, 2026)

An external audit was attempted via Google Gemini, which produced a sophisticated theoretical framework (correctly synthesizing published colometric and stylometric scholarship) but **hallucinated every single specific example** it provided. When asked for verse-by-verse merge candidates, Gemini fabricated plausible-sounding critiques that didn't match the actual text. Every "specific" recommendation it made was either a false positive when checked against the real lines or applied a syntactic rule (e.g., "never end on a preposition") that the image test correctly overruled (e.g., phrasal verb particles like "grafted in" are complete images).

This is useful methodological evidence: it shows that the BOM Reader's editorial decisions survive scrutiny that generic NLP-style rules cannot replicate. The editorial judgment is operating at a level that requires understanding the *meaning* of the text, not just its syntax.

### Connection to the "Behold" Typology
Stan's three-type "behold" classification (deictic, mirative, logical-connective) from the Mar 14 email could be a sub-study within this larger project. If different authors use "behold" in different functional proportions, and those proportions are visible in the colometric decisions (which type tends to get its own line vs. which type merges), that's another authorial fingerprint.

---

## 2. The "Functional Translation" Question and Colometric Evidence

### The Idea
The Gemini conversation about "fighting like dragons" surfaced the functional translation model — the idea that Joseph Smith received conceptual impressions and rendered them in his own 1820s English idiom. If the Book of Mormon's underlying source text had different authors with different rhetorical styles, and if those styles are detectable through colometric analysis of the English translation, that has implications for the translation model.

Specifically: if a single translator (Joseph Smith) produced a text that contains measurably different rhetorical "shapes" corresponding to different claimed authors, either (a) the translator was deliberately varying his style to simulate multiple voices (sophisticated literary forgery), or (b) the underlying source material actually had different rhetorical signatures that survived the translation process (consistent with a functional translation of genuinely multi-authored source material).

This doesn't "prove" anything, but it sharpens the question in a way that's academically interesting.

### Status
Speculative. Depends entirely on whether idea #1 produces measurable differences. If the colometric profiles don't cluster by author, this line of argument doesn't exist. If they do, it becomes a genuine contribution to the translation model debate.

---

## 3. Sense-Line Formatting as "Silent Commentary"

### The Idea
A shorter, more accessible paper about the editorial philosophy behind the BOM Reader — how sense-line breaking functions as an interpretive layer that guides the reader's experience without adding words. The "silent commentary" concept: every line break is an implicit claim about where a thought begins and ends, what deserves emphasis, what belongs together, and what is separate.

This could be a practical/pedagogical paper rather than a research paper — aimed at Sunday School teachers, seminary instructors, or anyone who reads the Book of Mormon aloud.

### Status
Could be written anytime. Doesn't require statistical analysis. The colometry handoff doc (10-colometry.md) already contains most of the theoretical framework.

---

## 4. Front-End Frames (FEFs): Emergent Compositional Units in Mormon's Abridgment

### The Idea
When the atomic-image breaking rules are applied consistently across the entire Book of Mormon, a distinctive pattern emerges in Mormon's abridgment (Mosiah onward) that is absent from the Small Plates: **long, irreducible framing lines followed by shorter expansionist detail lines.** These "Front-End Frames" (FEFs) are not a rule imposed on the text — they are what *emerges* when consistent breaking criteria meet a particular authorial construction style.

### Why FEFs Are Emergent, Not Imposed
The editor's (Stan's) instinct was to *break* these lines, applying the same atomic-image test used everywhere. The text *resisted*. FEFs are long because they are genuinely irreducible — every syntactic element is bound to every other element, and no break point exists that wouldn't orphan a verb from its object, a frame from its content, or a temporal clause from its main verb. The editor reluctantly accepted the long lines, then noticed the pattern they created. This sequence — reluctant acceptance → pattern recognition → theoretical articulation — is methodologically important. The FEF hypothesis was not designed first and then confirmed; it was discovered through the editorial process.

This means: if the pattern is measurable, it's a property of the *text*, not of the editor's preferences.

### The Pattern
The framing lines are often massive wayyehi constructions or complex temporal/spatial setups that resist breaking because the entire frame is one atomic image. The detail lines that follow are shorter, more digestible, and unpack the frame.

Example (Mosiah 24:15):
```
And now it came to pass that the burdens which were laid upon Alma and his brethren were made light;
yea, the Lord did strengthen them
that they could bear up their burdens with ease,
and they did submit cheerfully and with patience
to all the will of the Lord.
```

The first line is the frame — heavy, dense, scene-setting. The subsequent lines are the expansion — shorter, accumulative, building the theological point.

Compare with how Nephi constructs the same kind of moment (1 Nephi 1:6-7):
```
And it came to pass as he prayed unto the Lord,
there came a pillar of fire
and dwelt upon a rock before him;
and he saw and heard much;
and because of the things which he saw and heard
he did quake and tremble exceedingly.
```

Nephi's wayyehi line is short: "And it came to pass as he prayed unto the Lord," — then the *details* build upward in roughly equal-length lines. The construction is additive, not top-heavy. Mormon drops a heavy ceiling; Nephi builds a staircase.

This pattern was first noticed during editorial review of Mosiah (Mar 18, 2026) and is visible throughout the screenshot of Mosiah 24:15-18 where Mormon's framers run nearly the full screen width while the expansion lines are half that length or less.

### The Hypothesis
These long framing lines may correspond to **Mormon's actual compositional paragraphs** — the units in which he thought and wrote. Each framer represents a place where Mormon picked up his stylus and began a new thought-block. The shorter lines within are the internal structure of that thought-block.

If this is true, the sense-line analysis may be recovering a layer of textual structure that the LDS versification system (imposed in 1879 by Orson Pratt) obscured. Pratt's verse breaks were made on different criteria — roughly by sentence or clause — and may not align with Mormon's compositional units.

### Paper Structure: "This Is a Thing" / "What It Could Mean"

**Part 1 — The phenomenon (theory-neutral):** FEFs exist. Definition, data, distribution across attributed authors. Measurable, replicable, no presuppositions about text origin. The term FEF is deliberately theory-neutral — it describes what appears on the page, not why it's there. This section can be accepted by any reader regardless of their position on the Book of Mormon.

**Part 2 — Interpretive significance:** Note the structural parallel to Hebrew circumstantial clause + wayyiqtol constructions. Crucially: this parallel was discovered independently — English readability criteria produced structures that match Hebrew narrative conventions, not the other way around. Then present interpretive options without choosing:
- If the text is translated from a Hebrew-influenced source, FEFs may be structural fossils of the source language surviving through translation
- If the text is 19th-century composition, FEFs may reflect deep absorption of KJV narrative conventions (which themselves reflect Hebrew structure)
- Either way, the pattern is *systematic* and *author-differentiated*, which is the interesting finding regardless of origin
- The fact that a single 19th-century author (if that's the explanation) maintained distinct FEF profiles for different fictional narrators is itself a remarkable literary achievement worth documenting

This framing avoids the apologetics trap while still allowing faith-compatible readers to draw their own conclusions.

### What to Test
1. **Framer identification**: FEFs are now formally defined (see 10-colometry.md) with four criteria: position, discourse marker, irreducibility, expansion. No longer just "long lines" — specifically lines that resist breaking because of syntactic mutual dependence
2. **Verse boundary alignment**: Do framers consistently appear at verse boundaries, or do they sometimes fall mid-verse? If mid-verse, the versification is cutting across Mormon's paragraphs.
3. **Framer complexity growth**: Do Mormon's framers get longer or more syntactically complex as Mosiah progresses? This would reflect increasing editorial burden as he synthesizes multiple source records (Zeniff, Alma, Limhi) and manages parallel timelines.
4. **Comparison with Small Plates**: Confirm that Nephi's text does NOT exhibit this long-framer pattern — that he builds from short units upward rather than dropping in a heavy frame and unpacking downward. This would establish the pattern as a Mormon-specific compositional signature.
5. **Source record transitions**: Do framer characteristics change when Mormon shifts between source records? If the framers when he's abridging Zeniff feel different from the framers when he's abridging Alma, that suggests the source material's own structure is leaking through Mormon's editorial voice.
6. **Grammatical categorization of irreducibility**: Categorize *why* each FEF resists breaking. Is it a stacked prepositional chain? A temporal clause nested inside a wayyehi? A participial phrase that can't detach from its subject? A relative clause that binds actor to action? If different attributed authors produce FEFs that are irreducible for *different grammatical reasons*, that's another dimension of the authorial fingerprint beyond simple line length.
7. **Construction-type frequency by author**: Quantify the distribution of construction types (participials, prepositional phrases, conditional frames, relative clauses, compound verbs) across attributed authorial sections. If Mormon's FEFs are dominated by temporal+spatial stacking while Nephi's long lines (when they occur) are dominated by compound verbs, that's a measurable structural difference that connects colometry to syntax in a way traditional stylometry doesn't capture.

### Implications
- If the framers recover a genuine compositional structure, this could motivate a "re-paragraphed" presentation of Mormon's text that organizes by framer units rather than Pratt's verses
- This would be an entirely new way to visualize the Book of Mormon's structure — one derived from the text's own rhetoric rather than imposed by 19th-century editorial convention
- It's also another independent line of evidence for the text having genuine compositional structure (whether ancient or otherwise) — mechanical or random text wouldn't produce this systematic pattern

### Three Registers Within Mormon's Text
The Mosiah edits reveal not just a two-part pattern (FEF + expansion) but potentially three distinct colometric registers operating simultaneously:

1. **Mormon's narrative FEFs** — long, heavy, irreducible framing lines. Temporal+spatial+actor stacking. The "ceiling drop."
2. **Mormon's expansion lines** — shorter, accumulative detail lines that unpack the FEF. The "downward build."
3. **Quoted divine/angelic speech** — short, staccato, imperative. "Blessed art thou, / because of thy exceeding faith." "Alma, / arise and stand forth." "This is my church, / and I will establish it." One image per line, command-length utterances.

This is significant because it suggests Mormon is *preserving* a register difference when he quotes the Lord or an angel — he doesn't flatten divine speech into his own editorial cadence. The same editor (Mormon) is producing two different colometric patterns depending on whether he's narrating or quoting. If this is measurable, it shows the text has internal voice-switching that operates at the rhetorical structure level, not just the vocabulary level.

### Connection to Idea #1
This is a sub-hypothesis within the colometric stylometry framework. The "long framer + short expansion" pattern is itself a colometric signature — it shows up in the line-length distribution as a bimodal pattern (a cluster of long lines and a cluster of short lines) that would be absent from, say, Nephi's more uniformly distributed line lengths.

### Status
Observational. The pattern is visible in the edited Mosiah text. Needs quantitative confirmation before any claims can be made. A good first step would be plotting first-line-of-verse lengths across the entire corpus, colored by attributed author.

---

## 5. Intertextual Bleed: Jaredite Influence on Mosiah's Final Chapters

### The Observations

Two verses in the closing chapters of Mosiah suggest that Mormon's (or Mosiah's) knowledge of the Jaredite record is actively shaping the Nephite narrative at that point — and that this influence is detectable in the text:

**Mosiah 28:19** — Mormon signals his intention to write a Jaredite history. He never does. This unfulfilled editorial intention may explain why Moroni later takes up the task himself (the book of Ether). If Mormon planned to write it but didn't get to it, Moroni's decision to include Ether isn't arbitrary — it's completing his father's stated project.

**Mosiah 29:7** — Mosiah warns about the dangers of kings, specifically the danger of a king leading the people into destruction. The argument has *some* Nephite precedent — the wicked king Noah episode that Mosiah recently became aware of through the Limhi/Zeniff records. But the *scale* of the warning in Mosiah 29 seems to exceed what Noah alone would warrant (Noah was a local ruler of a breakaway colony, not a king over all the Nephites). The Jaredite record provides a far more dramatic precedent, which Mosiah had just finished translating. The Jaredite history is essentially a case study in how wicked kings destroy nations. Mosiah's political argument in chapter 29 reads as if he's applying lessons from the Jaredite record to Nephite governance — a real-time policy application of translated ancient history.

### Why This Matters
- It suggests the Jaredite record was not just a curiosity but actively influenced Nephite political thought at the moment of its translation
- It creates a narrative thread from Mosiah 28 (translation) → Mosiah 29 (application) → Ether (Moroni completing Mormon's project) that spans the entire second half of the Book of Mormon
- It's a test of internal consistency: if Joseph Smith were composing freely, there's no obvious reason to plant an unfulfilled editorial intention in Mosiah 28 that gets resolved by a different character hundreds of pages later in Ether

### Status
Observation stage. Needs a close reading of Mosiah 28-29 alongside the Jaredite king narratives in Ether to document the specific parallels. Could be a standalone short paper or a section within a larger study of Mormon's editorial awareness.

---

*Created: 2026-03-18*
