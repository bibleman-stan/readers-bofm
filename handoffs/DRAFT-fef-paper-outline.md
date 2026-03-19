# DRAFT Paper Outline

## Working Title
**"And It Came to Pass": A Re-examination of the Role and Significance of Front-End Frames in the Book of Mormon**

### Alternative Subtitles (for consideration)
- "Colometric Evidence for Distinct Compositional Architectures in a Multi-Voice Text"
- "How Sense-Line Analysis Reveals Structural Patterns Invisible in Standard Formatting"
- "Emergent Compositional Units from Editorial Colometry"

---

## Target Venues (in order of fit)
1. **Interpreter: A Journal of Latter-day Saint Faith and Scholarship** — reaches the BofM scholarly audience directly; open access
2. **Journal of Book of Mormon Studies** (Maxwell Institute) — more academic framing, peer-reviewed
3. **Digital Humanities Quarterly** or DH conference proceedings — methodology emphasis, secular framing, reaches computational humanities audience
4. **Literary and Linguistic Computing** / **Digital Scholarship in the Humanities** — if the quantitative analysis is strong enough

---

## I. Introduction: A Reading Edition and an Unexpected Discovery

### The BOM Reader Project
- Brief description: a web-based reading edition (bomreader.com) that presents the Book of Mormon in sense-line (colometric) format — each line is a natural breath unit for oral delivery
- Purpose was practical, not scholarly: make the text more accessible to ESL readers, children, and newcomers
- No theoretical agenda at the outset — the goal was readability, not structural analysis

### The Editorial Method
- Consistent criteria applied across the entire text by a single editor: the "atomic image / atomic breath" test
- Each line must be a complete, standalone mental image or a natural breath unit — ideally both
- When they conflict, editorial judgment decides which criterion governs, informed by the rhetorical register of the passage
- The method is editorial, not algorithmic — though an automated reformatter (v8) handles initial mechanical passes, the final line-break decisions are human

### The Unexpected Pattern
- When applied consistently across the corpus, the criteria produced markedly different results in different sections of the text
- In the Small Plates (1 Nephi through Words of Mormon), lines are relatively uniform in length, building additively from short units
- In Mormon's abridgment (Mosiah onward), a distinctive pattern emerged: long, irreducible framing lines followed by shorter expansion lines
- This pattern was not designed or sought — it was discovered through the editorial process, initially resisted by the editor, and only theorized after it became too consistent to ignore
- We call these long irreducible framing lines "Front-End Frames" (FEFs)

### What This Paper Does
- Defines FEFs precisely and theory-neutrally
- Presents quantitative evidence that FEFs distribute differently across attributed authorial sections
- Notes the structural parallel to Hebrew narrative conventions (discovered independently, not presupposed)
- Considers interpretive implications without adjudicating the text's origin
- Proposes FEF analysis as a new tool for colometric and stylometric investigation of multi-voice texts

---

## II. Previous and Adjacent Work

### Stylometric Studies of the Book of Mormon
- Hilton (wordprint studies, "Voices in the Book of Mormon" 2024)
- Larsen, Rencher, Schaalje (statistical authorship analysis)
- Fields (criticism of stylometric methods applied to BofM)
- Key point: all previous stylometric work measures features *in* the text (word choice, function word frequency, vocabulary richness). None measures features *between* the lines — the structural architecture of how ideas are packaged.

### Colometric Studies in Biblical Scholarship
- Lowth (Hebrew parallelism, 1753) → Kugel → Berlin → Watson
- Muilenburg (rhetorical criticism, "beyond form criticism")
- Fokkelman (major structural analysis of Hebrew poetry and narrative)
- Marschall (Pauline colometry — breath-unit cola, Gorgianic redundancy figures)
- Key point: colometry has a rich tradition in biblical studies but has never been applied to the Book of Mormon, and has rarely been connected to stylometric questions (who wrote this?) as opposed to rhetorical questions (how does this work?).

### The "And It Came to Pass" Literature
- Frequency criticism: Mark Twain's joke and its scholarly descendants — the phrase as evidence of literary clumsiness or single authorship
- Apologetic responses: the phrase as Hebrew wayyehi, a legitimate narrative convention
- What's missing: nobody has examined *what happens structurally when the phrase is treated as a discourse marker rather than verbal filler* — what it introduces, how the introduction relates to what follows, and whether that relationship varies by attributed author

### Book of Mormon Formatting Editions
- Skousen's *Earliest Text* (recovering original English dictation)
- Hardy's *Maxwell Institute Study Edition* (modern paragraphing, some poetic formatting)
- Key point: both make editorial formatting decisions but neither applies a consistent, rule-based colometric methodology across the entire text and then measures what emerges. Skousen's breaks are textual-critical; Hardy's are readability-oriented. Neither is designed to reveal structural patterns at the macro level.

### Oral Textual Criticism (Broader Theoretical Context)
- Brief note connecting to OTC as a developing methodology (Stan's dissertation work)
- Colometry tells us where the oral units are; OTC tells us why they're there
- The BOM Reader project is a practical demonstration of colometric analysis at scale — the data source for the present paper
- Not developed in full here (that's the dissertation), but acknowledged as the theoretical umbrella

---

## III. Methodology: The Atomic-Image Test and Its Application

### The Foundational Principle
- **Each line must be an atomic thought, an atomic breath unit, or ideally both.**
- "Atomic thought" = a single processable unit of meaning; the reader doesn't need the next line to understand this one
- "Atomic breath unit" = deliverable in one breath at natural reading pace
- Syntax tells you where thoughts *can* be separated; rhetoric and breath tell you where they *should* be

### Settled Editorial Rules (applied consistently across the corpus)
- The wayyehi rule: "And it came to pass that" as a fixed formula, never broken
- Framing devices (we'atta, "for behold," "wherefore," speech introductions) attach to their content
- Qualifying phrases: escalation earns its own line; restriction stays with its predicate
- Syntactic bond rules: verb-object, article, preposition (seeking object), auxiliary-verb bonds are never severed
- Phrasal verb particles and stranded relative clause prepositions are NOT danglers — they complete their constructions
- Vocative splitting: command vocatives stand alone; appeal vocatives stay with the request

### Validation: The Small Plates Audit
- Systematic audit of 1,690 verses across 7 books using the above criteria
- Result: 1 genuine merge candidate found (1 Nephi 19:21, "must needs be" split from complement clause)
- This establishes the dataset is clean: editorial decisions are internally consistent across thousands of break points
- The Gemini control experiment: an external AI audit produced sophisticated theoretical synthesis but hallucinated every specific recommendation — demonstrating that the editorial decisions require semantic understanding, not just syntactic pattern-matching

### What Emerges: Two Distinct Construction Patterns
- In the Small Plates: relatively uniform line lengths, additive construction ("staircase building")
- In Mormon's abridgment: bimodal distribution — long irreducible framers + short expansion lines ("ceiling drop + downward build")
- This difference is not imposed by the editor — it's what the same criteria produce when applied to text with different underlying compositional architecture

---

## IV. Defining Front-End Frames

### The Formal Definition
A Front-End Frame (FEF) is a line that meets all four criteria:
1. **Position**: Opens a verse or verse-block
2. **Discourse marker**: Begins with wayyehi, we'atta, "Wherefore," "Therefore," "For behold," "Behold," "Nevertheless," "And thus," "But behold," "Now," or a speech introduction formula
3. **Irreducibility**: Binds syntactically to at least one dependent element such that no break point exists without orphaning frame from content
4. **Expansion**: Is followed by two or more shorter lines that unpack the frame

### Why "Irreducibility" Is the Key Criterion
- A line can be long because it contains a list or compound predicate — that's breakable
- An FEF is long because every element is syntactically dependent on every other element
- The frame suspends resolution until the main verb arrives
- Everything between the discourse marker and the main verb resolution is part of the suspension
- The editor's instinct was to break these lines; the text resisted; the irreducibility is a property of the text, not the editor's preference

### Examples
- Mosiah 24:15 (FEF + expansion in detail)
- 1 Nephi 1:6-7 (same kind of moment, constructed differently — staircase vs ceiling drop)
- Additional examples from Mosiah 25-29

### Why the Term "FEF" Rather Than "Wayyehi Construction"
- "Wayyehi" presupposes Hebrew substrate and enters the apologetics lane
- "FEF" describes what appears on the page — theory-neutral, measurable, replicable
- Anyone can see an FEF regardless of their position on text origin
- The Hebrew parallel becomes an observation within the paper rather than a presupposition of the framework
- FEF also captures non-wayyehi framing constructions (we'atta, "wherefore," speech introductions) that exhibit the same structural behavior

---

## V. Quantitative Analysis

### Data Source
- The BOM Reader v2 text files: ~6,600 verses of editorially determined sense-line breaks made by a single editor
- All books, all chapters, consistent criteria

### Metrics
- Mean and median line length (characters, words) per attributed authorial section
- Line length variance / standard deviation
- FEF frequency (lines meeting all four criteria) per section
- FEF length distribution by section
- Expansion-line-to-FEF ratio by section
- First-line-of-verse length distribution, colored by attributed author
- Bimodality coefficient for line-length distributions (testing the "ceiling drop + short expansion" vs "uniform staircase" hypothesis)

### Attributed Authorial Sections
- Nephi (narrative chapters)
- Nephi (vision chapters — 1 Nephi 11-14)
- Nephi (discourse — 2 Nephi 25-33)
- Lehi (blessings — 2 Nephi 1-4)
- Jacob (sermons)
- Mormon (narrative abridgment)
- Mormon (editorial comment)
- King Benjamin (Mosiah 2-5)
- Abinadi (Mosiah 12-16)
- Quoted divine/angelic speech (across all sections)
- [Others as the analysis extends beyond Mosiah]

### Predicted Results
- Mormon's sections show bimodal line-length distribution (FEF cluster + expansion cluster)
- Nephi's narrative sections show more uniform distribution
- Nephi's vision sections show shorter, more uniform lines (stichometric)
- Benjamin's speech shows tight, liturgical line structure
- Divine speech shows shortest lines across all sections
- FEF frequency is significantly higher in Mormon's abridgment than in Small Plates material

### Three Registers Within Mormon's Text
- FEFs (long, heavy, irreducible — temporal+spatial+actor stacking)
- Expansion lines (shorter, accumulative detail)
- Quoted divine/angelic speech (short, staccato, imperative)
- If measurable, this shows Mormon preserves register differences when quoting — he doesn't flatten divine speech into his own editorial cadence

---

## VI. The Hebrew Parallel — and Why It Matters That It Was Discovered Independently

### FEFs and Wayyiqtol + Circumstantial Protasis
- Hebrew narrative backbone: wayehi [temporal] [circumstantial participial]... [main verb]
- Hebrew grammarians treat the protasis as one unit — don't break it
- The atomic-image rule arrived at the same conclusion from the English side independently

### Methodological Significance of Independent Discovery
- The criteria were developed for English readability, not Hebrew grammar
- The structures emerged from applying those English criteria, then were recognized as matching Hebrew conventions
- This is convergent evidence — two independent analytical approaches arriving at the same structural conclusion
- Much stronger than starting from Hebrew and looking for it in English (which would be circular)

### Interpretive Options (presented neutrally)
1. If the text is translated from a Hebrew-influenced source → FEFs may be structural fossils surviving through translation
2. If the text is 19th-century composition → FEFs may reflect deep absorption of KJV narrative conventions (which themselves reflect Hebrew structure)
3. Either way, the pattern is systematic and author-differentiated — the interesting finding regardless of origin
4. If one person created this text, maintaining distinct FEF profiles for different fictional narrators is itself a remarkable literary achievement

### What the Paper Does NOT Claim
- Does not claim FEFs prove ancient Hebrew authorship
- Does not claim FEFs disprove 19th-century composition
- Does not adjudicate the Book of Mormon's historical claims
- Claims only that FEFs exist, are measurable, vary by attributed author, and parallel documented Hebrew narrative conventions — all of which is demonstrable regardless of one's position on text origin

---

## VII. Implications and Future Directions

### For Book of Mormon Studies
- A new analytical lens: colometric stylometry as an independent channel of evidence for multiple authorship (or extraordinary literary craft — both are interesting)
- Potential for "re-paragraphing" Mormon's text by FEF units rather than Pratt's 1879 versification, recovering compositional structure the versification obscured
- The FEF-aware pre-breaking concept: programmatic detection of irreducible framers as a tool for future editorial work

### For Stylometric Methodology Generally
- Traditional stylometry measures what's *in* the text (vocabulary). Colometric stylometry measures what's *between* the lines (structural architecture). These are independent channels that could be applied to any multi-author text.
- If both traditional stylometry (Hilton) and colometric stylometry cluster the same attributed authors together, that's convergent validation from independent methods.

### For Colometric Studies
- Demonstrates that editorial colometry at scale can produce structurally significant, quantifiable findings — not just aesthetic formatting
- The FEF definition is transferable: it could be applied to other texts where discourse markers introduce complex framing constructions (Hebrew Bible narrative, Homeric epic, Qur'anic narrative)

### For Oral Textual Criticism
- FEFs are the colometric signature of what OTC would call "mnemonic load-bearing walls" — the points in an oral text where the architecture is densest and most resistant to simplification
- The BOM Reader project demonstrates at scale what OTC proposes in theory: that colometric analysis can recover oral-compositional structure
- Full development of this connection is outside the scope of this paper but is the subject of a separate, larger research program

### For the "And It Came to Pass" Discussion
- Reframes the phrase from verbal filler or formulaic tic to **structural discourse marker** with measurable consequences for the text's architecture
- The phrase doesn't just mark time — it initiates FEFs that organize Mormon's compositional units
- The degree to which it does this varies by attributed author — another datum for the stylometric argument

---

## VIII. Conclusion

- Summary of findings: FEFs defined, measured, shown to vary by author, paralleling Hebrew conventions, discovered independently through English-side criteria
- The term FEF is offered as a theory-neutral analytical tool for future work
- The BOM Reader project demonstrates that consistent editorial colometry applied at scale can reveal structural patterns invisible in standard formatting
- These patterns are interesting whether one reads the Book of Mormon as ancient translation or 19th-century composition — the structural analysis stands independent of that debate
- Future work: extend the quantitative analysis beyond Mosiah, apply FEF detection to other corpora, develop the connection to oral transmission criticism

---

## Appendices (as needed)

### A. Complete FEF Inventory (Mosiah chapters analyzed)
Table of every FEF identified, with verse reference, line text, discourse marker type, grammatical reason for irreducibility, and expansion line count.

### B. Line-Length Distribution Plots
Histograms and box plots comparing attributed authorial sections.

### C. The Atomic-Image Editorial Methodology
Full statement of the editorial rules used in the BOM Reader project, for replicability.

### D. The Small Plates Audit Results
Summary statistics demonstrating internal consistency of the editorial dataset.

---

*Draft outline created: 2026-03-18*
*Status: Outline stage. Quantitative analysis not yet performed. Needs line-length data extraction, statistical analysis, and visualization before drafting can begin.*
