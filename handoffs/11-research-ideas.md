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
- **Thought experiment (shelved for post-editing):** After all editorial re-breaks are complete, create an alternative versification scheme where only FEFs receive verse numbers — effectively recovering Mormon's compositional paragraphs as the structural unit rather than Pratt's 1879 verse divisions. This would be a concrete, visual demonstration of how FEF-based segmentation differs from conventional versification. Even if never published as a "real" versification, the comparison between FEF-based and Pratt-based verse boundaries would be powerful data for the paper — showing exactly where the two systems agree and diverge.

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

## 6. Colometry as Text-Critical Diagnostic: When Sense-Lines Expose Textual Problems

### The Idea

When you break text into atomic images, you are forced to ask of every phrase: "Does this image cohere? Does this element belong in this sequence?" This is a question that traditional reading — flowing through paragraphs — can gloss over, because the eye keeps moving. But when each line must stand as a complete, defensible image, incoherences become visible.

This means colometric analysis may function as an **independent text-critical diagnostic** — a way of surfacing textual problems (scribal errors, formulaic intrusions, harmonizations) that traditional text criticism identifies through manuscript comparison but that colometry identifies through *semantic pressure*. The editor tries to make the line work as an image, and the line *won't work*, because the text is corrupt or disturbed at that point.

### Case Study: Alma 2:25 — "Flocks" vs. "Families"

The first concrete example emerged during editorial work on Alma 2. In Alma 2:25, spies report that Nephites are "fleeing before them with their flocks, and their wives, and their children, towards our city." Royal Skousen's *Analysis of Textual Variants* (Part Three, pp. 1629-1630) addresses this, confirming that the Original Manuscript reads "flocks" and defending it as the *lectio difficilior* — the harder reading that a scribe would be tempted to smooth to "families."

What struck Stan during colometric editing: when you try to break this into sense-lines, "their flocks, and their wives, and their children" creates a list where one element (flocks) is semantically incongruent with the other two (wives, children). The image doesn't cohere — you're seeing livestock mixed with human dependents in what is supposed to be a single "refugee caravan" image. The colometric editor's instinct is to pause and ask: *is this really one image, or is something wrong with the text?*

The Gemini conversation surfaced a plausible counterargument to Skousen's *lectio difficilior* defense:

1. **Formulaic overextension**: "Flocks, wives, and children" is a standard Pentateuchal baggage-list formula (cf. Genesis 47:1). A scribe — or even the original dictator — might have instinctively inserted "flocks" because the formula was ingrained, regardless of whether flocks were actually present in this tactical context.

2. **Absence in the parallel**: In Alma 2:27, when the same force arrives for battle, "flocks" disappear from the description. If flocks were a defining characteristic of the refugee flight in v. 25, their absence two verses later is either a narrative inconsistency or evidence that "flocks" was a formulaic intrusion in v. 25 that the text itself doesn't sustain.

3. **Lectio difficilior protecting a manifest error**: The counterargument is that *lectio difficilior* can sometimes protect an error rather than an original reading. If a word is "difficult" because it's a contextually inappropriate formulaic slip, then the "easier" reading may be what the author intended.

### The Broader Principle

This case illustrates something generalizable: **colometric editing creates semantic pressure that exposes textual disturbances**. When you must assign every phrase to an atomic image, formulaic intrusions, harmonizations, and scribal errors become visible because they break the image coherence.

This is directly analogous to how OTC's mnemonic density scoring works on Gospel material. OTC asks: "Does the mnemonic architecture cohere at this point?" If a passage that should be high-density (oral ridge) suddenly drops in density, that's a signal of editorial intervention. Colometry asks the parallel question: "Does the image cohere at this point?" If a line that should present one atomic image contains a semantically incongruent element, that's a signal of textual disturbance.

### Potential Paper: "Colometry as Text-Critical Tool"

A paper could:

1. **Define the method**: Colometric editing as a form of "semantic stress testing" — applying image-coherence pressure to every phrase and documenting where the text resists
2. **Catalog cases**: Systematically collect instances across the BOM Reader editorial process where colometric editing flagged a phrase as problematic, then check whether Skousen's ATV addresses the same passage. Cases where colometry independently flags what manuscript evidence also flags would be strong validation.
3. **Test against controls**: Apply the same colometric pressure to passages where the text is stable (no manuscript variants) and confirm that the method does NOT flag false positives in clean text. The Small Plates audit (1 fix in 1,690 verses) is already evidence of low false-positive rate.
4. **Propose colometric text-critical criterion**: Just as OTC proposes "mnemonic-architecture preservation" as a new text-critical criterion, this paper would propose "image-coherence under colometric pressure" as another. Where *lectio difficilior* asks "which reading is harder?", the colometric criterion asks "which reading produces a coherent atomic image?"
5. **Engage Skousen directly**: The BOM Reader project and Skousen's Critical Text Project are working on the same text from different angles. Cases where they converge (both flag the same passage) or diverge (colometry flags something Skousen doesn't, or vice versa) would be mutually illuminating.

### Connection to OTC

This paper idea connects to the dissertation in two ways:

1. It demonstrates that colometric analysis has **diagnostic power** beyond readability — it can detect textual disturbances. This strengthens OTC's Chapter 9 argument that colometry is not just aesthetic formatting but a genuine analytical tool.
2. It establishes a new text-critical criterion that complements OTC's mnemonic-preservation criterion. Together they form a family of "structural coherence" criteria that operate where traditional text-critical tools (stemmatic analysis, scribal-tendency analysis) are blind — at the level of the text's internal architecture rather than its external transmission history.

### Status

One case study identified (Alma 2:25). More will likely emerge as Alma through Moroni editorial work continues. Worth collecting cases systematically before deciding whether there's enough for a standalone paper.

### Methodology Note

Important: not every colometric "bump" is a textual problem. Sometimes an image is deliberately complex or jarring. The method requires distinguishing between (a) text that is hard to break because it's *dense* (legitimate complexity — leave it alone) and (b) text that is hard to break because an element *doesn't belong* (possible corruption — investigate). The Alma 2:25 case is type (b): "flocks" doesn't belong in a list of human dependents in a military context, and the parallel in v. 27 confirms its absence.

---

## 7. The BOM Reader as Unintentional Pilot Study for OTC

### Background: Stan's Dissertation

Stan is developing a doctoral dissertation proposing **Oral Transmission Criticism (OTC)** as a new critical method for detecting, measuring, and analyzing oral-mnemonic architecture in ancient texts. The prospectus (v7.1, "Oral Transmission Criticism: A New Method for Detecting Mnemonic Architecture in Ancient Texts, with Calibration Against Arab-Islamic Transmission and Application to Early Christian Gospels") frames OTC as the corrected fulfillment of Form Criticism's original promise — a neo-Form Criticism that supplies the empirical rigor the original method lacked.

OTC's core insight: oral traditions that successfully preserve material across transmission chains do so through specific, identifiable, and quantifiable textual mechanisms — phonetic patterning, formulaic repetition, structural parallelism, ellipsis, grammatical shifts — that function as mnemonic scaffolding. These mechanisms are not hypothetical; they are documented and measurable in traditions where oral preservation is historically attested (Arab-Islamic materials serve as the calibration standard).

The dissertation proceeds: (1) calibrate against Arab-Islamic materials where mnemonic engineering is undisputed, (2) develop a diagnostic toolkit (mnemonic density scoring, retroversion as "mnemonic archaeology," directionality testing, cross-textual inverse predictions), (3) apply to Gospel material showing Mark preserves Aramaic-substrate mnemonic architecture, John preserves Greek-native mnemonic architecture, and Matthew/Luke systematically literize (remove mnemonic features).

### The Colometry Connection

Chapter 9 of the prospectus ("Colometry as Independent Corroboration — and Evidence of Convergence") argues that colometric scholarship is already approaching OTC's territory without possessing the framework to articulate what it's finding. The key passage from the prospectus:

> "Colometric scholars can feel that these structures mean something beyond rhetorical ornamentation — that the segmentation patterns reflect something fundamental about how the texts were composed and used — but without a mnemonic-functional framework, the observation has nowhere to go. The data is accumulating; the interpretive paradigm is missing. OTC provides that paradigm."

And:

> "The côlon is not merely a rhetorical unit but a memory unit; the period is a mnemonic chunk sized for human working memory; and the Gorgianic figures colometric scholars catalog are redundancy mechanisms serving the same functional role as formulaic repetition in Qur'anic saj'. Colometry tells us where the oral units are. OTC tells us why the units are there."

The relationship is symbiotic: colometry gives OTC empirical precision about unit boundaries; OTC gives colometry the functional explanatory framework it currently lacks.

### How the BOM Reader Project Functions as OTC Pilot

The BOM Reader project was not designed as an OTC test. It was designed as a reading edition. But the editorial process forced Stan to confront exactly the questions OTC is designed to answer — and the results constitute a live, documented, large-scale demonstration of colometric analysis producing structurally significant findings.

**What the BOM Reader demonstrates:**

1. **Consistent colometric criteria applied at scale produce author-differentiated results.** The atomic-image/atomic-breath test was applied uniformly across 1,690+ verses in the Small Plates and hundreds more in Mosiah. Different attributed authors produce measurably different colometric profiles — not because the criteria changed, but because the underlying rhetorical architecture is different. This is exactly the capability OTC needs colometry to have.

2. **FEFs are the colometric analogue of OTC's "oral ridges."** OTC predicts that oral-traditional material will have zones of high mnemonic density (preserved sayings, formulaic constructions) and zones of low density (connective narrative tissue). The BOM Reader found exactly this pattern: FEFs (high density, irreducible, resistant to editorial simplification) followed by expansion lines (lower density, more flexible, breakable by standard rules). The terminology is different — "FEF" vs "oral ridge" — but the structural phenomenon is the same: points where the text's architecture is load-bearing and cannot be simplified without destroying the structure.

3. **The three-register discovery (FEF / expansion / divine speech) demonstrates that colometric analysis can detect voice-switching within a single editor's work.** Mormon produces two different colometric patterns depending on whether he's narrating or quoting the Lord. This is directly analogous to what OTC would look for in Gospel material: can the method detect when Mark is preserving oral-traditional sayings versus composing narrative framing? If colometric analysis can detect this kind of register switching in the Book of Mormon, it can plausibly detect it in other texts.

4. **The FEF-Hebrew parallel was discovered independently.** English readability criteria (atomic image / atomic breath) produced structures that match Hebrew narrative conventions (wayyiqtol + circumstantial protasis). This convergence was not sought — it was noticed after the editorial decisions were already made. OTC's prospectus argues that when an independent scholarly tradition produces results that a new method would have predicted, this constitutes strong evidence that both are detecting real phenomena rather than generating artifacts. The BOM Reader's FEF discovery is a concrete instance of exactly this kind of independent convergence.

5. **The audit methodology demonstrates that colometric datasets can be validated.** The Small Plates audit (1,690 verses, 1 fix needed) and the Gemini control experiment (hallucinated every specific recommendation) together show that (a) the editorial decisions are internally consistent and (b) they cannot be replicated by generic syntactic rules — they require semantic understanding. This matters for OTC because it establishes that human editorial colometry is a reliable analytical instrument, not a subjective impressionistic exercise.

### What This Means for the Dissertation

The BOM Reader work cannot go in the dissertation directly — the dissertation is about OTC applied to Gospels, calibrated against Arab-Islamic materials. But it strengthens the dissertation in several indirect ways:

1. **Credentialing.** Stan is not just theorizing about colometry in Chapter 9; he has actually performed large-scale editorial colometry on a complete multi-author text. This is unusual — most colometric scholars work on individual passages or pericopes, not entire books.

2. **Methodology demonstration.** The BOM Reader shows that the colometric approach described in the prospectus (applying consistent segmentation criteria, measuring what emerges, comparing across attributed authors) actually *works* — it produces differentiated results, it reveals structural patterns, and it can be validated through systematic audit.

3. **The FEF-aware pre-breaking concept.** If FEFs can be detected programmatically in the Book of Mormon, the same detection logic could be applied to Gospel texts — identifying likely mnemonic load-bearing constructions in Mark, for example, before human analysis begins. This is a practical tool that could emerge from the BOM Reader project and feed directly into OTC's toolkit.

### Publication Strategy: How the Two Projects Feed Each Other

**Option A: BOM Reader colometric stylometry paper published first.** This establishes Stan's colometric credentials and demonstrates the methodology working on a non-Gospel text. The FEF concept is introduced. When the dissertation drops, the colometric chapter (Ch. 9) can cite the published paper as demonstrating that the method works at scale.

**Option B: Conference paper at DH or SBL.** Introduce FEFs as a general concept at a digital humanities or biblical studies conference, with the BOM as the demonstration case. This positions Stan at the colometry/orality intersection before the dissertation is defended.

**Option C: Methodological appendix.** The BOM Reader work is documented as a "methods development" appendix to the dissertation, showing how the colometric instincts that inform Chapter 9 were developed through practical editorial work.

**Option D: Post-dissertation research program.** OTC + colometric stylometry gets applied to Hebrew Bible, Homeric, and other corpora after the dissertation establishes the theoretical framework. The BOM Reader is the proof-of-concept that the method works at scale, and its codebase (v8 reformatter, FEF-aware pre-breaker, line-length analysis scripts) becomes transferable tooling.

These options are not mutually exclusive. A conference paper (B) could precede a journal article (A), which could be cited in the dissertation (C), which could lead to a research program (D).

### The Key Intellectual Chain

```
OTC (theory of how texts work orally)
  → Colometry (method for making oral structure visible on the page)
    → FEFs (emergent pattern that colometry reveals)
      → Colometric Stylometry (FEFs vary by author = authorial fingerprint)
        → Independent convergence with Hebrew narrative conventions
```

Each link feeds the next. The BOM Reader project is building the middle three links at industrial scale. The dissertation provides the first link (OTC as theoretical framework) and applies the whole chain to a different corpus (Gospels). Together they make a unified research program in which colometric analysis — grounded in OTC's functional explanatory framework — becomes a general tool for recovering oral-compositional structure in ancient texts.

### Critical Self-Assessment

**Risk:** Confirmation bias. Stan developed the FEF hypothesis while editing the same text the hypothesis describes. A skeptic could argue the editing shaped the data to fit the theory.

**Defense:** (1) The editing rules were established before the FEF pattern was noticed — the text resisted breaking under rules that were articulated for other reasons. (2) The Small Plates audit shows the rules are consistently applied even where they don't produce FEFs, establishing that the rules are not designed to create the pattern. (3) The pre-edit and post-edit versions of Mosiah should both show the FEF pattern (just more pronounced after editing), confirming that editing clarified rather than created the signal. (4) If someone else applies the same four-criterion FEF definition to the same text, they should get the same results — the definition is replicable.

**Risk:** The BOM is a religiously contested text. Using it as a colometric demonstration case could be perceived as apologetics regardless of framing.

**Defense:** (1) The FEF definition is theory-neutral. (2) The paper presents interpretive options without choosing. (3) The "JS absorbed KJV patterns" explanation is given equal weight. (4) The interesting finding is the author-differentiation, which is remarkable regardless of text origin. (5) Publishing in a DH venue rather than an LDS venue signals methodological intent.

### The Discovery Sequence as Methodological Shield

The order in which insights emerged is itself evidence against confirmation bias. The sequence was:

1. **Goal:** Make a readable edition. No research agenda. No hypothesis about authorial voices or Hebrew structures.
2. **Method:** Apply "one image per line / one breath per line" consistently across the entire text. The criteria were articulated for readability, not for detecting anything.
3. **Resistance:** Certain lines in Mormon's text refused to break. The editor's instinct was to break them — shorter lines are easier to read. The text wouldn't let him. Every break point orphaned something.
4. **Reluctant acceptance:** The long lines were accepted not because they were desired but because no valid break existed under the established criteria.
5. **Pattern recognition:** After accepting dozens of these irreducible long lines, the editor noticed they clustered at verse openings and were followed by shorter expansion lines. The FEF pattern was *noticed*, not designed.
6. **Hebrew parallel:** Only after the FEF pattern was named and defined did the structural parallel to Hebrew wayyiqtol + circumstantial protasis become apparent. The parallel was recognized, not sought.
7. **Theory articulation:** The FEF hypothesis, the three-register model, and the connection to OTC all came *after* the editorial decisions were already made and committed to the repository. Git history documents this sequence.

This matters because the standard criticism of pattern-finding in texts is "you found what you were looking for." The discovery sequence shows the opposite: Stan found what he wasn't looking for, tried to make it go away (by breaking the lines), failed, and only then recognized what the text was showing him.

The git commit history is the evidence trail. The editorial rules (10-colometry.md) were formalized on Mar 18. The Mosiah edits applying those rules were committed the same day. The FEF hypothesis was articulated *after* the edits, not before. A skeptic can verify this by examining the commit timestamps.

### Visualization as Display, Not Argument

A critical distinction for the paper: bomreader.com is a *display*, not an *argument*. The website shows text formatted according to transparent, articulable, testable criteria. It does not tell the reader what to conclude. When a reader opens Mosiah 24:15 and sees a long framing line followed by shorter expansion lines, they are seeing the text — not an interpretation of the text.

This matters because the "fitting data to thesis" objection assumes the researcher is selecting or shaping which data to present. But bomreader.com presents *all* the data — every verse of every book, formatted by the same rules. The FEF pattern is visible because it's there, not because unfavorable data has been hidden.

The paper's evidence comes in three complementary forms:

1. **The website itself** — the text displayed according to the editorial criteria. Anyone can look at any chapter and see the colometric structure. This is the raw data, publicly accessible, fully transparent.
2. **Quantitative analysis** — line-length distributions, FEF frequency, construction-type categorization, author-differentiated profiles. Charts and graphs that measure what the page shows. These are testable and replicable.
3. **The editorial criteria** — formally defined, documented in the colometry handoff, applicable by anyone to the same text. If someone else applies the four-criterion FEF definition and gets different results, that's a legitimate challenge. If they get the same results, that's replication.

None of these three forms of evidence requires the reader to accept a prior conclusion. They display, they measure, and they define. The reader draws their own conclusions.

### OTC's "Mnemonic Load-Bearing Walls" Concept

In OTC terminology, FEFs function as **mnemonic load-bearing walls** — structural elements that cannot be removed without the entire passage losing its organizational coherence. Just as a structural engineer can identify which walls in a building are load-bearing by testing what happens when you try to remove them (the building collapses), the colometric editor identifies FEFs by testing what happens when you try to break them (the image fragments, the syntax orphans, the meaning collapses).

This connects directly to OTC's diagnostic approach: the method doesn't start by assuming what's mnemonic — it applies consistent criteria and observes which elements resist simplification. Resistance to simplification *is* the diagnostic signal. Elements that resist editorial breaking are the elements doing the most structural work in the text's oral architecture.

The BOM Reader editorial process is performing exactly this diagnostic — applying consistent "simplification pressure" (the atomic-image test) to every line of text and noting where the text pushes back. FEFs are the pushback zones. In OTC terms, they're the oral ridges — the highest points of mnemonic density — made visible through colometric analysis.

---

*Created: 2026-03-18*
