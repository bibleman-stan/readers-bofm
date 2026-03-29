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

## II. Previous and Adjacent Work (BIFURCATED — March 2026 revision)

**Critical note:** The original literature review drew exclusively from Hebrew *poetic* colometry. But the BofM is mostly prose. The method itself demonstrated this — applied uniformly, it produced poetry-like cola for Isaiah, liturgical stacking for Benjamin, and the prose FEF/expansion pattern for Mormon. The tool differentiated genres without being told to. The literature review must therefore draw on TWO traditions: poetic colometry (for the syntactic principle) and prose discourse analysis (for the structural model).

### Stream A — Poetic Colometry (syntactic criterion for line division)
- Lowth (Hebrew parallelism, 1753) → Kugel → Berlin → Watson
- Muilenburg (rhetorical criticism, "beyond form criticism")
- **Cloete** (*Versification and Syntax in Jeremiah 2–25*, 1989) — the key figure: syntax governs colometry. The reformatter is Cloete's method automated.
- Fokkelman (Hebrew poetry and narrative structure)
- Marschall (Pauline colometry — breath-unit cola; precedent for applying colometry to non-poetry)
- Key point: this stream establishes the *principle* (syntax governs line division) but was built for poetry. It cannot explain why FEFs behave as they do in prose.

### Stream B — Hebrew Prose Discourse Analysis (NEW — structural model)
- **Niccacci** (*The Syntax of the Verb in Classical Hebrew Prose*, 1990) — foreground (wayyiqtol mainline) vs. background (circumstantial clauses, offline comments). FEFs ARE Niccacci's circumstantial protasis in English clothing. The FEF-frame/expansion-line architecture IS Niccacci's background/foreground distinction.
- **Longacre** (*Joseph: A Story of Divine Providence*, 1989) — discourse grammar applied to Hebrew narrative; routine/peak narrative model. The three-register finding (FEF/expansion/divine speech) maps onto Longacre's tripartite system (background/foreground/direct speech).
- **Alter** (*The Art of Biblical Narrative*, 1981 — NOT the poetry book) — prose rhythm, type-scenes, "purposeful reticence." Divine speech compressing shorter than narrative prose is a recognized Hebrew property.
- Key point: this stream provides the theoretical home for what FEFs actually are — discourse-level foreground/background transitions in narrative prose, not poetic cola.

### Stream C — Kunstprosa (art prose)
- Norden's concept of structurally patterned prose that is not verse
- The register most BofM text occupies: not poetry, not flat prose, but orally shaped narrative with structural conventions
- This gives terminological permission to apply colometric analysis to prose without claiming the prose is poetry
- Arabic *saj'* (rhymed prose) as cross-linguistic parallel for Semitic Kunstprosa

### Stylometric Studies of the Book of Mormon
- Hilton (wordprint studies, "Voices in the Book of Mormon" 2024)
- Larsen, Rencher, Schaalje (statistical authorship analysis)
- Fields (criticism of stylometric methods applied to BofM)
- Key point: all previous stylometric work measures features *in* the text (word choice, function word frequency, vocabulary richness). None measures features *between* the lines — the structural architecture of how ideas are packaged.

### The "And It Came to Pass" Literature
- Frequency criticism: Mark Twain's joke and its scholarly descendants
- Apologetic responses: the phrase as Hebrew wayyehi
- What's missing: nobody has examined *what happens structurally when the phrase is treated as a discourse marker rather than verbal filler*

### Book of Mormon Formatting Editions
- Skousen's *Earliest Text* — textual-critical breaks, not colometric
- Hardy's *Maxwell Institute Study Edition* — readability-oriented, not rule-based
- **Key transmission history point:** The Original Manuscript was dictated without punctuation. Punctuation added by printer Gilbert (1830). Versification by Pratt (1879). Every structural layer readers see today was added by someone other than the author(s) or translator. The colometric recovery project works on a literally unpunctuated dictated text — methodologically identical to what text critics do with unpunctuated manuscripts (DSS, early papyri). This is not a metaphor.

### Oral Textual Criticism (Broader Theoretical Context)
- Brief note connecting to OTC as a developing methodology
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

### The Three-Layer Methodology Model
- **Layer 1 — Mechanical syntax** (reformatter M0–M10): purely Cloetean. Syntax governs colometry. Handles ~74% of corpus adequately. This is what syntax alone can do.
- **Layer 2 — Discourse-level structure** (FEF recognition, speech attribution, register identification): Niccacci/Longacre territory. Recognizes foreground/background transitions that syntax alone misses. This is where human judgment adds something the reformatter cannot.
- **Layer 3 — Rhetorical and theological interpretation** (escalatory appositives, virtue list pivots, divine title stacking): Alter territory — the art in the prose.
- The reformatter (Layer 1) applying Cloete's syntax-governs-colometry principle *broke FEFs that shouldn't be broken*. The FEF framework (Layer 2), informed by prose discourse analysis, *preserved them*. This is documented evidence that prose discourse analysis outperforms syntactic colometry on a measurable task.

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

## VI. The Hebrew Prose Parallel — and Why It Matters That It Was Discovered Independently

**Note: This section has been rewritten to frame the parallel in terms of prose discourse analysis (Niccacci/Longacre) rather than poetic colometry.**

### FEFs as Niccacci's Circumstantial Protasis
- Not just a structural resemblance: a functional correspondence
- Niccacci's foreground/background distinction: wayyiqtol mainline = foreground (events advancing the narrative); circumstantial clauses = background (setting, description, explanation)
- FEF frames ARE background; expansion lines beginning with the main verb ARE foreground
- The three-register model (FEF / expansion / divine speech) maps onto Niccacci's tripartite prose system (background / foreground / direct speech, which he treats as a distinct discourse level)
- This is not "these look alike" — it's "the same functional discourse architecture appears in both, independently identified"

### The Retroversion Test (proposed)
- 50 representative FEF breaks retroversioned into Biblical Hebrew
- Test whether English-side breaks fall at natural Hebrew clause boundaries
- If correspondence is high for FEF breaks and wayyiqtol boundaries, that's the strongest version of the convergence argument
- Not convergence with *poetic* Hebrew structure — convergence with *prose* Hebrew discourse structure (the correct claim)

### Methodological Significance of Independent Discovery
- The criteria were developed for English readability, not Hebrew grammar
- The structures emerged from applying those English criteria, then were recognized as matching Hebrew conventions
- This is convergent evidence — two independent analytical approaches arriving at the same structural conclusion
- Much stronger than starting from Hebrew and looking for it in English (which would be circular)

### Genre-Neutrality as Methodological Validation
- The method applied a single criterion uniformly across the corpus
- The OUTPUT differentiated genres: Isaiah → poetry-like cola; Benjamin → liturgical stacking; Mormon → prose FEF/expansion; 4 Nephi → chronicle compression; Nephi's visions → cinematic stichometry
- The Isaiah blocks are the positive control: the method CAN detect poetry when poetry is present — which makes it significant that it DOESN'T detect poetry in Mormon's narrative
- The tool said "this isn't poetry." Niccacci and Longacre describe what it detected instead.
- This is a defense against the "you found what you were looking for" objection: you weren't looking for genre differentiation. You were looking for readable line breaks. Genre differentiation fell out as a byproduct.

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
*Major revision: 2026-03-29 — Prose discourse reframing (Niccacci/Longacre/Cloete), bifurcated lit review, three-layer methodology model, genre-neutrality finding, transmission history argument, retroversion test proposal*
*Status: Outline stage. Quantitative analysis not yet performed. Needs line-length data extraction, statistical analysis, and visualization before drafting can begin. Priority reading: Niccacci and Longacre before drafting Sections II, IV, and VI.*
