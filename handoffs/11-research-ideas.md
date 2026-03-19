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

## 4. Mormon's Paragraph Structure: Long Framers as Compositional Units

### The Idea
When sense-line breaks are applied to Mormon's abridgment (Mosiah onward), a distinctive pattern emerges that is absent from the Small Plates: **long, unbreakable framing lines followed by shorter expansionist detail lines.** The framing lines are often massive wayyehi constructions or complex temporal/spatial setups that resist breaking because the entire frame is one atomic image. The detail lines that follow are shorter, more digestible, and unpack the frame.

Example (Mosiah 24:15):
```
And now it came to pass that the burdens which were laid upon Alma and his brethren were made light;
yea, the Lord did strengthen them
that they could bear up their burdens with ease,
and they did submit cheerfully and with patience
to all the will of the Lord.
```

The first line is the frame — heavy, dense, scene-setting. The subsequent lines are the expansion — shorter, accumulative, building the theological point.

### The Hypothesis
These long framing lines may correspond to **Mormon's actual compositional paragraphs** — the units in which he thought and wrote. Each framer represents a place where Mormon picked up his stylus and began a new thought-block. The shorter lines within are the internal structure of that thought-block.

If this is true, the sense-line analysis may be recovering a layer of textual structure that the LDS versification system (imposed in 1879 by Orson Pratt) obscured. Pratt's verse breaks were made on different criteria — roughly by sentence or clause — and may not align with Mormon's compositional units.

### What to Test
1. **Framer identification**: Define "long framer" quantitatively — perhaps lines above a certain character/word threshold that begin with a discourse marker (wayyehi, "And now," "And thus," "Therefore," "Behold")
2. **Verse boundary alignment**: Do framers consistently appear at verse boundaries, or do they sometimes fall mid-verse? If mid-verse, the versification is cutting across Mormon's paragraphs.
3. **Framer complexity growth**: Do Mormon's framers get longer or more syntactically complex as Mosiah progresses? This would reflect increasing editorial burden as he synthesizes multiple source records (Zeniff, Alma, Limhi) and manages parallel timelines.
4. **Comparison with Small Plates**: Confirm that Nephi's text does NOT exhibit this long-framer pattern — that he builds from short units upward rather than dropping in a heavy frame and unpacking downward. This would establish the pattern as a Mormon-specific compositional signature.
5. **Source record transitions**: Do framer characteristics change when Mormon shifts between source records? If the framers when he's abridging Zeniff feel different from the framers when he's abridging Alma, that suggests the source material's own structure is leaking through Mormon's editorial voice.

### Implications
- If the framers recover a genuine compositional structure, this could motivate a "re-paragraphed" presentation of Mormon's text that organizes by framer units rather than Pratt's verses
- This would be an entirely new way to visualize the Book of Mormon's structure — one derived from the text's own rhetoric rather than imposed by 19th-century editorial convention
- It's also another independent line of evidence for the text having genuine compositional structure (whether ancient or otherwise) — mechanical or random text wouldn't produce this systematic pattern

### Connection to Idea #1
This is a sub-hypothesis within the colometric stylometry framework. The "long framer + short expansion" pattern is itself a colometric signature — it shows up in the line-length distribution as a bimodal pattern (a cluster of long lines and a cluster of short lines) that would be absent from, say, Nephi's more uniformly distributed line lengths.

### Status
Observational. The pattern is visible in the edited Mosiah text. Needs quantitative confirmation before any claims can be made. A good first step would be plotting first-line-of-verse lengths across the entire corpus, colored by attributed author.

---

*Created: 2026-03-18*
