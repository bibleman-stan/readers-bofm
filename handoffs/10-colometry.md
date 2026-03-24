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
5. **After any substantive line-break edits:** commit the source file changes, then rebuild all HTML via `python3 build_book.py --all`, bump the service worker cache version in `sw.js`, and commit the rebuilt HTML — so everything is ready for Stan to push via GitHub Desktop
6. If audio exists for changed chapters, audio must be regenerated via Colab pipeline (changed lines invalidate cache)

---
### Update — 2026-03-18

#### Foundational Principle Clarified

Through working review of Mosiah sense-lines, the overriding criterion for all line-break decisions was articulated more precisely:

**Each line must be an atomic thought, an atomic breath unit, or ideally both.**

This is the foundational test that all the settled principles below it are trying to serve. It should be read before the specific rules, not derived from them.

"Atomic thought" means the line holds a single processable unit of meaning — the reader doesn't need to carry it forward and resolve it against the next line to understand it.

"Atomic breath unit" means the line can be physically delivered in one breath at a natural reading pace — not gasping, not cutting a thought short.

When a line fails both tests it clearly needs revision. When it passes both it's valid regardless of what a syntactic rule might suggest. When they conflict — a line that is one breath but two thoughts, or one thought but too long for one breath — editorial judgment decides which criterion governs for that passage.

This principle also clarifies the relationship between syntactic attachment and rhetorical function: **syntax tells you where thoughts can be separated; rhetoric and breath tell you where they should be.** These usually agree; when they don't, breath and rhetoric govern.

#### Qualifying Phrases That Escalate vs. Restrict

A related distinction emerged from reviewing Mosiah 3:5 and 3:7:

A qualifying phrase that **restricts** the preceding claim tends to belong with it on the same line ("save it be," "except it were"). But a qualifying phrase that **escalates or intensifies** the preceding claim — pushing it to a further extreme — often earns its own line, because the escalation is itself a thought that benefits from its own arrest.

Example (Mosiah 3:7): "even more than man can suffer, / except it be unto death" — "except it be unto death" is not merely restricting; it is pushing the claim to its limit. The break honors that.

#### Fronted Adverbials as Intentional Rhetorical Positioning

Mosiah 3:5 — "that with power, / the Lord Omnipotent who reigneth" — initially flagged as a possible orphan fragment. On review: "with power" is a fronted adverbial, extracted from its natural post-verbal position ("shall come down with power") and placed before the subject for rhetorical effect. The fronting is the device — it announces the manner before the actor, building anticipation. The line break after it is grammatically and rhetorically accurate, not accidental.

General principle: short lines that appear to be orphan fragments may instead be fronted elements occupying a genuine clause-initial position. Check deep structure before proposing a merge.

#### Line Reordering as an Editorial Tool

The revision of Mosiah 15:9 established that **reordering lines within a verse** is a legitimate editorial move, not just changing where breaks fall. In the original v2, "having broken the bands of death" preceded "standing betwixt them and justice." The revised order places "standing betwixt them and justice" as the climactic statement of Christ's mediating function, with the subsequent participles ("having broken… taken upon… redeemed… satisfied") explaining the acts that constitute that function. This is the correct theological and rhetorical sequence: function stated, then grounded.

Reordering is more substantive than break adjustment and should be used sparingly, but it is the right tool when the logical or rhetorical arc of a verse requires it.

#### Three-Category Framework for Automated Review

When reviewing sense-lines systematically (book by book), proposed changes fall into three categories:

- **Category A — Editorial slippage:** Break placement is suboptimal by our own principles. No theological or rhetorical stakes. Safe to revise with review.
- **Category B — Rhetorical shape:** The arrangement reflects how a speaker builds argument or emphasis. Changing the break changes the rhetoric. Requires judgment about what the speaker is doing, not just syntactic tidiness.
- **Category C — Theological weight:** Break placement makes a doctrinal point, or a proposed change would flatten something intentional. Flag and discuss before touching.

Category A gets a confident proposal. B and C get a question first.

#### Punctuation Is Canonical — Never Touch It

Line breaks are editorial. Punctuation belongs to the canonical LDS text and is never altered, even when it might seem to affect how a line reads. This is moot in the default view (punctuation hidden via CSS) but the source files must preserve the canonical text exactly.

---
### Update — 2026-03-18 (evening)

#### Framing Devices Beyond Wayyehi

An external audit (via Gemini) confirmed and extended the wayyehi principle: **all discourse-framing constructions should be treated as atomic units with their content**, not broken away from it. This includes:

1. **Wayyehi + temporal/spatial clause** — already settled. "And it came to pass that X" stays together.
2. **We'atta / "And now"** — "And now, I Nephi, make an end" or "And now, my sons, I would that ye should" — the "And now" is a discourse pivot, not a standalone breath. It attaches to the clause it introduces.
3. **"For behold" / "Behold"** — a deictic pointer that frames what follows. "For behold, he hath the record of the Jews" is one unit. Don't orphan the pointer from the pointed-at.
4. **"Wherefore" / "Therefore"** — logical connectives that frame a conclusion. "Wherefore, men are free according to the flesh" is one atomic thought. Don't break after "Wherefore."
5. **Speech introduction formulas** — "And he said unto them:" or "And I, Nephi, said unto my father:" — the speech introduction is a framing device. It attaches to the first line of the speech unless the combined line is too long for one breath.

The general principle: **if a construction's function is to frame, introduce, or pivot to what comes next, it should not be severed from what comes next.** A frame without its content is an orphan. Content without its frame loses its rhetorical context.

#### Syntactic Bond Rules (from audit)

These rules prevent mechanical over-splitting:

- **Never split verb from direct object** — "I make / a record" → merge to "I make a record"
- **Never end a line on an article** (the, a, an) — always merge forward
- **Never end a line on a preposition that's still looking for its object** — "the power / of the Lamb" → merge. BUT phrasal verb particles are fine: "grafted in," "carried away," "cast off" are complete images because the particle completes the verb's meaning, not a prepositional phrase seeking an object. Similarly, stranded prepositions in relative clauses are fine: "the state...they are in" — the preposition has already connected back to its antecedent
- **Never split auxiliary from main verb** — "did / slay" → merge to "did slay"
- **Never split "not/neither/nor" from what they negate** — "neither sense / nor insensibility" → merge to "neither sense nor insensibility"

#### Vocative Splitting Rule

Vocatives (O, Wo) get nuanced treatment:

- **Vocative-as-command** → gets its own line: "Awake, my soul!" stands alone because it's a complete imperative.
- **Vocative-as-appeal** → stays with the request: "O Lord, wilt thou redeem my soul?" is one atomic cry. Don't orphan "O Lord" from the plea.
- **"Wo unto X who Y"** — merge when Y *defines* X ("Wo unto the murderer who deliberately killeth"); split when Y *elaborates* on X ("Wo unto the rich, / who are rich as to the things of the world").

---
### Update — 2026-03-18 (late evening)

#### Formal Definition: Front-End Frames (FEFs)

A **Front-End Frame** is a line that meets all four criteria:

1. **Position**: Opens a verse or verse-block (first line after a verse marker)
2. **Discourse marker**: Begins with one of: wayyehi ("And it came to pass"), we'atta ("And now"), "Wherefore," "Therefore," "For behold," "Behold," "Nevertheless," "And thus," "But behold," "Now," or a speech introduction formula
3. **Irreducibility**: Binds syntactically to at least one dependent element (temporal clause, spatial clause, participial phrase, relative clause, or object clause) such that no break point exists that wouldn't orphan either the frame or its content under the atomic-image rule
4. **Expansion**: Is followed by two or more shorter lines that unpack, elaborate, or detail the frame's content

The irreducibility criterion (3) is what distinguishes FEFs from merely long lines. A line can be long because it contains a list or compound predicate — that's breakable. An FEF is long because every element is syntactically dependent on every other element. The frame *suspends resolution* until the main verb arrives, and everything between the discourse marker and the main verb is part of the suspension.

#### FEFs and Hebrew Narrative Convention

FEFs have a structural analogue in Biblical Hebrew. The *wayyiqtol* chain that forms the backbone of Hebrew narrative typically begins with a circumstantial protasis — a front-loaded frame that establishes time, place, condition, and actor before the main verb resolves:

```
wayehi [temporal clause] [circumstantial participial clause]... [main verb]
```

Hebrew grammarians treat the protasis as one syntactic unit — you don't break it. The atomic-image rule independently arrived at the same conclusion from the English side: don't break until the image resolves.

This convergence is methodologically significant. The FEF pattern was not discovered by starting from Hebrew grammar and looking for it in English. It was discovered by applying an English readability criterion (atomic image / atomic breath) consistently across the text, noticing that certain lines *resisted* breaking, and then recognizing that the resistant structures match Hebrew narrative conventions.

This means: whether the Book of Mormon's source is ancient Hebrew-influenced text or 19th-century KJV-absorbed composition, the structural pattern is real and measurable. The FEF definition is theory-neutral — it describes what's on the page without presupposing an explanation.

#### FEF-Aware Pre-Breaking (Workflow Optimization)

The current v8 reformatter breaks at syntactic boundaries (commas, conjunctions, subordinators) with length thresholds. It doesn't recognize framing constructions, so it frequently breaks FEFs that then require manual re-merging.

An FEF-aware pre-breaker would:

1. **Detect the discourse marker** at the start of a verse
2. **Walk forward** looking for the main verb — the verb that the discourse marker introduces
3. **Protect everything between marker and main verb resolution** as one atomic unit — no breaking regardless of internal commas, participials, or relative clauses
4. **Apply normal v8 breaking rules only to the expansion lines** after the FEF resolves

This would reduce manual editing burden for unedited books (Alma through Moroni) by preserving FEFs automatically and focusing human review on the expansion lines where editorial judgment is genuinely needed.

#### Connection to Oral Transmission Criticism (OTC)

The colometric methodology documented in this file connects to a broader academic research program. Stan is developing Oral Transmission Criticism (OTC) as a doctoral dissertation — a new critical method for detecting oral-mnemonic architecture in ancient texts, calibrated against Arab-Islamic materials and applied to early Christian Gospels.

OTC's Chapter 9 argues that colometry tells us *where* oral units are; OTC tells us *why* they're there. The BOM Reader's colometric work is an unintentional pilot study demonstrating that consistent editorial colometric criteria applied at scale produce author-differentiated results — exactly the capability OTC needs colometry to have. FEFs are the colometric analogue of OTC's "oral ridges" (zones of high mnemonic density that resist editorial simplification).

The full intellectual chain: OTC (theory) → colometry (method) → FEFs (emergent pattern) → colometric stylometry (author differentiation) → independent convergence with Hebrew narrative conventions. See `11-research-ideas.md` § 6 for the detailed connection.

---
*Created: 2026-03-18*

---
### Update — 2026-03-20

#### Speech Attribution Formulas vs. FEFs

A distinction emerged from Alma 3:15-16 editorial work that clarifies FEF treatment:

**FEFs are the narrator's voice.** "For behold," "And now," "Wherefore," "Nevertheless" — these are the literary narrator (Mormon, Nephi, Alma) shaping discourse. They attach to what they introduce because narrator and content are continuous. The frame and its content belong to the same voice.

**Speech attribution formulas introduce a different voice.** "And again:" "Thus saith the Lord:" "He said:" — these are handoffs to quoted speech. The break between the attribution and the speech marks a *voice shift*. The colon is the textual signal. Rule: **attribution formula takes its own line; quoted content begins fresh on the next line.**

This is not FEF behavior — it's the opposite. FEFs bind forward; speech attributions *release* into a new voice.

#### The Literary Narrator vs. The Oracular Voice

The FEF/quotation asymmetry reveals a deeper pattern:

- **The narrator deploys FEFs** — orienting, reasoning, persuading, connecting. FEFs are markers of a literary mind at work. A narrator using "Wherefore" or "For behold" is signaling logical relationship and shaping the listener's expectations. This is composed rhetoric, not improvised speech.
- **Divine speech quotes short and compressed.** It doesn't need to orient you. It declares. The oracular voice resists elaboration — it pronounces, then stops.

This asymmetry — literary narrator vs. oracular divine voice — is theologically and stylistically significant. FEFs cluster in narrative voice; direct divine speech tends toward shorter, less-structured lines.

**Research implication:** FEF distribution across the text is potentially a marker of *narrative voice* specifically. Mapping FEF density could help distinguish narrator passages from embedded speeches, and narrator voice from divine voice, across the corpus. This is a dimension of the FEF paper worth developing: FEFs as markers of literary self-consciousness in the narrator, absent in the oracular.

#### Quotations Tend Toward Shorter Breaks

Observed pattern across Alma editorial work: direct speech — especially divine speech — tends to break into shorter, more reducible lines than narrative prose. This may reflect:
- Original delivery of quoted speech with more deliberate, measured cadence
- The oracular register resisting elaboration
- The narrator's literary shaping being absent inside the quotation

This is a working observation, not yet a settled rule. Track as editorial work continues into Alma.

---
*Last updated: 2026-03-20*

---
### Update — 2026-03-20 (second entry)

#### Coherence Is Primary: Resolving the Breath vs. Atomic Thought Tension

When breath unit length and coherence appear to conflict, **coherence wins**. This is not an exception to the foundational test — it's what the foundational test actually says.

A line that fails the atomic thought test cannot be rescued by being short. A fragment is not a breath unit in any meaningful sense — the reader has nowhere to land. "And now as many of the Lamanites and the Amlicites" is not a breath unit; it's a suspended quantifier waiting for resolution. Shortness without coherence is just a broken line.

The practical rule: **never break a line to solve a length problem if the break produces a fragment.** Length is a signal that something complex is happening — not always a problem to be solved by breaking. Sometimes the right response to a long line is to recognize that its length is irreducible.

#### Connection to FEF Principles

This resolves what might look like a tension between FEF rules and breath-unit concerns. They are the same principle operating at different syntactic levels:

- FEF rule: don't break the frame from its content (clause level)
- Coherence rule: don't break a subject from its defining relative clause (phrase level)

In both cases the unit resists breaking because every element is syntactically dependent on every other. The atomicity test independently arrives at the same conclusion as syntactic analysis: the unit is complete only when the meaning resolves.

**Skousen's breaks on defining relative clauses** (e.g., Alma 3:3 "And now as many of the Lamanites and the Amlicites / who had been slain upon the bank of the river Sidon") are therefore systematically wrong by this principle — not just awkward, but failures of the foundational test. The v2 merge is correct.

---
*Last updated: 2026-03-20*

---
### Update — 2026-03-20 (third entry)

#### FEF Is a Structural Property, Not an AICTP Rule

AICTP ("And it came to pass") constructions are high-frequency FEF candidates because "it came to pass" is always anticipatory — it never resolves without a following clause. But FEF irreducibility is not limited to AICTP. It is a **structural property** that appears in many construction types:

- **Genitive phrases:** "the ninth year / of the reign of the judges" — the head noun doesn't identify without its genitive
- **Verb + infinitive complement:** "began / to be lifted up" — "began" suspends until the infinitive resolves what was begun
- **Verb + object:** "did not grant / unto him the office" — the action is incomplete without its object and recipient
- **Participial frames:** "Alma, having seen the afflictions... / began to be sorrowful" — the participial suspends until the main verb lands
- **Defining relative clauses:** "as many of the Lamanites / who had been slain" — the referent is unidentified without the clause

**The unifying test is always the same:** can the reader land on this line as a complete unit of meaning? If not — regardless of *why* — the construction is irreducible and the break is wrong.

AICTP is the most visible carrier of this pattern because it is formulaic and frequent. But the colometric principle applies wherever a line fails the atomic thought test due to syntactic suspension, not just at AICTP markers.

---
*Last updated: 2026-03-20*

---
### Update — 2026-03-21

#### Refined FEF Temporal Frame Principle

Cross-book consistency audit (1 Ne through Alma 5) revealed that AICTP + temporal/date formulas were handled inconsistently: 1 Nephi broke *inside* the temporal reference (too early), while Alma merged *past* the temporal reference into the main clause (too late).

**The refined rule: complete the temporal/genitive reference on one line, then break before the main verb.**

The FEF frame ends where the temporal identification ends. "And it came to pass in the seventh year of the reign of the judges" is the frame. "There were about three thousand five hundred souls..." is the expansion. The frame can be long — that's fine. But the main verb is where expansion begins, and expansion earns its own line.

This principle is **structural, not authorial** — it operates the same way whether Nephi or Mormon is deploying it. AICTP suspends resolution the same way regardless of voice. This strengthens the case for AICTP as evidence of a Hebrew literary framing convention (wayyiqtol protasis), because the pattern holds uniformly across narrators rather than varying by author.

**Implication for colometric stylometry:** The "Mormonistic vs. Nephic" voice distinction does not live in how FEFs are *handled* (which should be uniform). It lives in FEF *density* (how often they appear), line length distribution in non-FEF passages, sermonic fragmentation patterns, and parallel stacking frequency.

#### Genre Awareness vs. Foundational Test

Alma 5 editorial work (Alma's sermon) prompted the question: should sermonic voice get different break treatment than narrative voice? The answer: **genre awareness is context, not a rule.** The foundational test (atomic thought + atomic breath unit) applies universally regardless of voice type. If applying the same test to sermonic material produces shorter, more fragmented lines, that's an *observation* about how Alma speaks — not a license to fragment *because* it's a sermon.

The guard against bias: never break or merge *because* of genre expectations. Apply the test, let the results fall, and interpret the pattern afterward.

---
*Last updated: 2026-03-21*

---
### Update — 2026-03-20 (fourth entry)

#### "Which" Relative Clauses: Open Question

Working through Alma 5, a genuine open question emerged about "which" relative clauses as break points.

The earlier principle (third entry, this update) settled that **defining relative clauses that leave the antecedent unidentifiable should not be broken** — "as many of the Lamanites / who had been slain" fails because the antecedent is a bare quantifier without the clause.

But the Alma 5 work revealed a different situation: cases where the line before "which" is already a complete syntactic unit, and the "which" clause adds substantial specification:

- `did not my father Alma believe in the words` / `which were delivered by the mouth of Abinadi?`
- `to stand before God to be judged according to the deeds` / `which have been done in the mortal body?`

In both cases the preceding line is syntactically complete — the "which" clause adds information rather than resolving an incomplete referent. Stan's instinct (confirmed) was to keep these broken. The "which" marks a genuine clausal boundary.

**Working distinction (from Alma 5:3 vs. 5:11/5:15):**

Alma 5:3 contains two "which" clauses that are correctly *merged* in v2:
- `the land which was in the borders of Nephi` — light verb, thin identifier, essentially "the Nephi-bordered land"
- `the land which was called the land of Mormon` — naming clause, another thin identifier

Alma 5:11 and 5:15 contain "which" clauses that are correctly *broken*:
- `words / which were delivered by the mouth of Abinadi` — passive verb + agent phrase; predicates something theologically substantial about the words
- `the deeds / which have been done in the mortal body` — locative predication adding real content

This is a **minimal pair** — same construction, different behavior. The distinguishing factor Stan articulated: sometimes "which" functions as an **extended adjective** (identifies/classifies the noun, thin predicate, merge tendency) and sometimes as a **genuine subordinate clause** (predicates new information, break legitimate).

**Operational test:** Does the "which" clause introduce genuinely new information, or does it merely identify which one? Identifier → merge. New predication → break legitimate.

This is consistent with v2 as already edited — the distinction was operating intuitively before it was theorized.

**Applies equally to "who" relative clauses.** The distinguishing factor is the construction type (relative pronoun introducing a clause), not the specific pronoun. Example: Alma 5:48 — `the Only Begotten of the Father, / full of grace and mercy, and truth` — the appositional phrase functions as an extended adjective completing the portrait, not a new predication. Same merge logic applies.

**Status: WORKING HYPOTHESIS.** Not yet fully settled. Continue tracking examples through Alma to confirm or complicate.

---
### Update — 2026-03-21 (second entry)

#### Granular Over-Break Scrub Validation

Full audit of 1 Nephi through Alma 5 (~17,000 lines): 43 over-breaks flagged, 40 fixed. Error rate 0.25%. All flags were Category A (editorial slippage). No new systemic patterns emerged. Rubric validated.

**Error types found:**
- Verb/complement splits (~20) — verb separated from its direct object or complement
- Dangling conjunctions/subordinators (~10) — "and," "but," "that" trailing at end of line
- Genitive orphans (~8) — head noun separated from its genitive phrase

All mechanical slippage, no rule failures. The existing rubric caught every case without needing new rules.

**Most common repeating pattern:** The "dangling that" after AICTP — "And it shall come to pass that" / [content] constructions where "that" trailed the previous line instead of leading the next. Fix: break BEFORE "that" so it leads the next line, not trail the previous.

**Isaiah chapters (2 Ne 12-24)** contributed disproportionately to 2 Nephi's flags, consistent with complex syntax processed mechanically before FEF principles existed.

---
*Last updated: 2026-03-21*

---
### Update — 2026-03-21 (third entry)

#### New Settled Rules from Alma Editorial Work & Full-Corpus Scrub

**Rule 15: Vocative units are indivisible.** Multi-word divine address formulas ("O Lord God," "O Lord our God,") stay whole on one line. The vocative can stand as its own line (consistent with Rule 3), but it must not be split mid-address. "O Lord" / "God" is always wrong; "O Lord God," / "how long wilt thou suffer..." is correct.

**Rule 16: "Dangling that" after AICTP.** When "And it shall come to pass that" ends a line with "that" trailing, the fix is to break BEFORE "that" so it leads the next line: "And it shall come to pass" / "that [content]." The subordinator "that" introduces a clause and must lead, not trail. This was the most common mechanical error across the corpus (~10 instances in Mosiah alone).

**Rule 17: "Caused that" complement integrity.** "Caused" requires its complement clause on the same line (or rebroken so "caused that" stays together). Same principle as "began to" — the governing verb needs its complement. "He caused" / "that his servants should..." fails; "he caused that his servants should stand forth" is correct.

**Rule 18: Fixed idiom integrity.** Certain multi-word expressions are indivisible: "put to death," "from time to time," "prevailed upon," "put an end to." Never break inside a fixed idiom regardless of line length.

**Rule 19: Cataphoric "that" clauses break; anaphoric "that" clauses merge.** A "that" clause earns its own line only if it introduces at least one new referent, image, or proposition (cataphoric — forward-pointing, new content). If its content is entirely backward-pointing — pronouns, demonstratives, "the case," "this thing," "the same" — it stays merged (anaphoric — resolving, no new content). Example: "I say unto you / there be many things to come" breaks because the content clause introduces new information. "The Spirit hath not said unto me that this should be the case" stays merged because "this" and "the case" are anaphoric back-references with zero new semantic content. This connects to the FEF framework: FEFs are cataphoric (forward-pointing, creating suspension); anaphoric back-references close down and resolve, having no independent energy to carry a line.

#### Settled Editorial Decisions (promoted from working hypothesis)

**"I say unto you" isolation pattern — SETTLED.** Isolated on its own line when introducing substantial content; merged when followed by a short response ("Nay," "Yea," "they are blessed"). This pattern is now consistent across Mosiah and Alma with no exceptions. It is not voice-dependent — it operates the same way in King Benjamin's speech, Abinadi's trial, and Alma's sermon.

**"According to" as causal break — EDITORIAL JUDGMENT.** "According to his faith / there was a mighty change wrought in his heart" (Alma 5:12) — Stan's decision to treat "according to" as functionally causal. Not codified as a universal rule, but defensible when "according to" is doing causal work (stating WHY something happened, not just HOW). Watch for more instances before generalizing.

---
*Last updated: 2026-03-21*

---
### Update — 2026-03-21 (fourth entry)

#### Full-Corpus Mechanical Scrub: Patterns & Insights

178 mechanical fixes applied across all 15 books (6,603 verses). The error types never changed from the initial validation set — the rubric scaled without requiring new rules.

**Error distribution by book (normalized observations):**
- **Alma 6-63** had the highest raw count (61 flags) but is also the longest book. The war chapters (43-63) and the geography chapter (22) were the densest error zones — complex military action sequences and geographic descriptions produce compound clauses the reformatter splits mechanically.
- **The small plates (Enos, Jarom, Omni, Words of Mormon)** were remarkably clean (9 flags total). These are the earliest-edited files and reflect Stan's editorial hand the most. The principles were being applied intuitively before they were codified.
- **Isaiah chapters (2 Ne 12-24)** contributed disproportionately to 2 Nephi's flags. Isaiah's Hebrew-poetry-in-KJV-English syntax doesn't follow the prose patterns the reformatter was built for. A future dedicated pass on Isaiah blocks may benefit from starting with Hebrew poetic structure rather than English prose rules.

**The six mechanical error types (complete list — no new types emerged across the full corpus):**
1. Dangling conjunctions/subordinators at line end ("and," "but," "nor," "that," "or," "even," "insomuch")
2. Verb separated from direct object or complement
3. Genitive noun separated from identifying "of/which/who/where" complement
4. "Began to" / "caused that" split from complement verb
5. Auxiliary/modal separated from main verb
6. Fixed idiom split ("put to death," "from time to time," "one with another," "prevailed upon")

**Stylometric observations from the scrub:**

- **"Caused that" is Mormon's construction.** Almost every "caused that" split occurred in large-plates material (Mosiah through Mormon and Ether). "Caused that [subject] should [verb]" is a distinctly Mormonistic way of expressing indirect causation. Nephi doesn't use it. This is a potential stylometric marker beyond FEF density — *construction type* frequency.
- **"Began to" splits cluster in narrative, not speech.** Every "began to" flag was in Mormon's narration or Ether's king-list chronicles. Embedded speeches (Alma's sermon, Benjamin's speech, Abinadi's trial) never triggered this error because their syntax is naturally shorter. Reinforces the voice distinction: Mormon's narrative generates longer, more complex lines; embedded speech is cleaner.
- **The "dangling that" after AICTP was the single most common pattern** (~25-30 instances corpus-wide). All from the reformatter splitting at a length or comma threshold without recognizing "that" as a subordinator. This is the strongest case for an FEF-aware pre-breaker in any future reformatter version.

**Reformatter implication:** The v8 reformatter was calibrated on 1-2 Nephi's measured prose. It doesn't anticipate how Mormon's war narrative piles up coordinated verbs, or how "caused that" constructions work, or that "it shall come to pass that" is structurally identical to the past-tense AICTP. A future v9 reformatter should protect these patterns.

---
*Last updated: 2026-03-21*

---
### Update — 2026-03-21 (fifth entry)

#### "Insomuch that" — Leading vs. Trailing Distinction

"Insomuch that" constructions have two distinct colometric behaviors depending on position:

**Trailing (result clause):** "they did smite them / insomuch that they did flee" — "insomuch that" introduces the result of the previous action. It leads a new line because it opens a new clause with new content (the result). The previous line is complete without it.

**Leading (degree modifier):** "insomuch that they could not be distinguished" — when "insomuch" modifies the degree of the preceding verb and the "that" clause is the specification of degree, it can merge with the preceding material if the combined line passes the atomic thought test.

The operational test: does "insomuch that" introduce a genuinely new event/result (break), or does it specify the degree of the same event (merge candidate)?

---
*Last updated: 2026-03-21*

---
### Update — 2026-03-22

#### Rule 19: Anaphoric vs. Cataphoric "that" Clauses

**Cataphoric "that" clauses (forward-pointing, new content) break; anaphoric "that" clauses (backward-pointing, resolving) merge.**

Test: does the "that" clause introduce at least one new referent, image, or proposition? If yes (cataphoric), it can break. If its content is entirely backward-pointing — pronouns, demonstratives, "the case," "this thing," "the same" — it merges.

Examples:
- "that the good shepherd doth call you" — new image, new action → **breaks** (cataphoric)
- "that this should be the case" — "this" and "the case" both point back → **merges** (anaphoric)
- "there be many things to come" — new referent, new temporal info → **breaks** (cataphoric)

This connects to the FEF framework: FEFs are cataphoric by nature (forward-pointing, creating suspension). Anaphoric back-references close down and resolve — they have no independent energy and merge with what precedes them.

#### Methodological Note: Syntactic vs. Structural Categories

Two distinct layers operate in sense-line decisions:

**Syntactic rules** (grammar-level): subject-verb binding, verb-object binding, conjunction placement, genitive completion, auxiliary-verb unity. These are non-negotiable — if the grammar says the break creates an incomplete parse, the break doesn't happen. Rules 1-18 are almost entirely syntactic. These produce the 0.25% error rate and are falsifiable by sentence diagramming.

**Structural decisions** (discourse-level): speech attribution isolation, vocative separation, parallel stacking for emphasis, causal breaks that separate cause from effect, sermonic pauses. These operate WITHIN the space syntactic rules leave open — where grammar permits a break, structural judgment decides whether to take it.

**The principle: sense-line breaks occur only where syntactic permission and structural motivation converge.** If the grammar says no, the break doesn't happen regardless of rhetorical appeal. If the grammar says yes but there's no structural reason, lines stay merged. No structural choice should ever override a syntactic rule.

This layered approach is what makes the method defensible: the syntactic rules are mechanical and replicable; the structural decisions are editorial but constrained by the syntactic floor.

---
*Last updated: 2026-03-22*

---
### Update — 2026-03-23

#### Rule 19 Refinement: Expletive "It" and Result Clauses Are Not Anaphoric

The initial formulation of Rule 19 (anaphoric "that" clauses merge; cataphoric break) was too broad. Corpus audit revealed false positives where "it" or "that" appeared to point backward but were actually introducing new content:

**Expletive "it" in cleft constructions:** "that it is by his grace" (Jacob 4:7) — the "it" is a structural placeholder in a cleft sentence ("it is X that Y"), not a referential pronoun pointing to a previously named thing. The predication ("by his grace") is genuinely new content. These are CATAPHORIC — they break correctly.

**Result/purpose clauses with new predication:** "that it is good" (Jacob 5:39) — "it" refers back to "the natural fruit," but "good" is NEW information — the discovery, the payoff of the action. When a backward-pointing pronoun is followed by a new predicate (quality, state, judgment), the clause carries enough new content to justify breaking.

**Sharpened test for Rule 19:** A "that" clause is anaphoric (merge) ONLY when BOTH the subject AND the predicate are backward-pointing. If the subject points back ("this," "it," "these things") but the predicate introduces new content ("is by his grace," "is good," "is because I have testified"), the clause is cataphoric enough to break.

Genuine anaphoric violations have predicates like "should be," "should be the case," "had not been written" — where the predicate adds no new image or information beyond what was already established.

**Confirmed violations fixed:** Helaman 14:27 ("that these things should be" — "these things" + "should be" = all backward), 3 Nephi 11:30 ("that such things should be done away" — "such things" + removal = all backward), 3 Nephi 23:12 ("that this thing had not been written" — "this thing" + "not written" = all backward).

---
*Last updated: 2026-03-23*

---
### Update — 2026-03-23 (second entry)

#### Rule 20: Polysyndeton + Repeated Possessive/Conjunction = Stack

When a series uses polysyndeton ("and X, and Y, and Z") rather than asyndeton or simple listing ("X, Y, and Z"), each "and" marks a deliberate rhetorical beat. Combined with repeated possessives ("and his X, and his Y"), the speaker is re-anchoring each item individually rather than compressing them into a catalogue.

**Stack (polysyndeton — each item gets its own line):**
- "and his matchless power, / and his wisdom, / and his patience, / and his long-suffering" — repeated "and his" marks each as distinct
- "but suffereth himself to be mocked, / and scourged, / and cast out, / and disowned" — each "and" introduces a new action/image

**Keep together (asyndeton/simple list — one line):**
- "gold and silver and precious things" — no escalation, same register
- "submissive, meek, humble, patient" — comma-separated catalogue in the same register (humility cluster), no repeated conjunction

**The test:** Does each "and" introduce a genuinely new image at a different register, or is the "and" just connecting equivalent items? If each conjunction marks a step up (or down) in theological/rhetorical weight, stack vertically. If the items are coordinate equivalents, keep together.

**Statistical value:** Polysyndetic escalation frequency is a measurable feature per attributed author. The pattern clusters in theologically dense passages (Benjamin's angel discourse, Abinadi, Jacob's sermon) and may correlate with prophetic/revelatory voice type vs. narrative voice type.

#### Escalatory Appositive Inventory Update

After applying Rule 20 across Mosiah, the corpus now has:
- 24 existing escalatory appositive stacks (19 original + 5 new Mosiah breaks)
- 5 remaining missed opportunities in 2 Nephi and Mormon/Moroni (to be reviewed in Stan's manual pass)

The pattern is concentrated in prophetic/revelatory speech — not in Mormon's narrative prose. This distribution is itself data for the colometric stylometry paper.

---
*Last updated: 2026-03-23*

---
### Update — 2026-03-23 (third entry)

#### Methodological Principle: Punctuation Must Not Have Deterministic Force

The commas, semicolons, colons, and dashes in the canonical text are editorial additions — added by the printer/publisher, not original to the translation event. They may corroborate a line-break decision grounded in grammar or rhetoric, but they CANNOT justify one by themselves.

**The test:** If a line break depends on a comma being present to make the case, remove the comma mentally and ask whether the break still holds on purely grammatical/rhetorical grounds. If not, the break is grounded in a 19th-century typesetter's judgment, not in the text's structure.

**Example:** Alma 7:12 — "that his bowels may be filled with mercy, / according to the flesh," was initially defended as a split because the comma after "mercy" seemed to mark "according to the flesh" as a non-restrictive modifier. But the comma is editorial, and syntactically "according to the flesh" is a manner adverbial modifying "filled" — identical to the subsequent "know according to the flesh" and "succor according to their infirmities," which were both correctly merged. Without the comma distinction, all three should be treated the same. The split was reversed.

**Implication:** This does NOT mean we ignore punctuation entirely — it's useful context and often reflects genuine clause boundaries. But it cannot be the SOLE basis for a break decision. Grammar, rhetorical structure, and the atomic thought test are primary; punctuation is secondary/corroborating.

---
*Last updated: 2026-03-23*

---
### Update — 2026-03-24

#### Rule 21: "According to" — Manner vs. Source/Authority

"According to" phrases split when they claim divine source or authority; they merge when they describe manner.

**Merge (manner — HOW the action is done):**
- "spoke unto them, according to his word" — per instructions
- "proceed with mine own prophecy, according to my plainness" — style of delivery
- "gave a genealogy, according to his memory" — how he recalled
- "manifest unto the children of men, according to their faith" — the mechanism

**Split (source/authority — BY WHAT POWER the action occurs):**
- "it whispereth me, / according to the workings of the Spirit of the Lord" — the Spirit is the source
- "had spoken unto all his household, / according to the feelings of his heart and the Spirit of the Lord" — dual source: personal feeling + divine Spirit
- "I give unto you a prophecy, / according to the spirit which is in me" — prophetic authorization

**The test:** Is the "according to" phrase answering HOW? (manner → merge) or BY WHAT AUTHORITY / FROM WHAT SOURCE? (authorization → split). Source/authority claims are independent theological assertions that earn their own line. Manner adverbials are embedded modifiers that stay with their verb.

**Connection to punctuation principle:** This distinction was discovered when the punctuation-dependency audit revealed that all "according to" breaks had been made at comma boundaries. Stripping the commas and testing on grammar alone revealed that some breaks were genuinely justified (source/authority) while others were punctuation artifacts (manner). The comma cannot be the basis — the function of the phrase must be.

---
*Last updated: 2026-03-24*

---
### Update — 2026-03-24 (second entry)

#### Rule 22: Divine Title Appositives — INTRODUCING vs. REFERENCING

Divine title appositive constructions ("Jesus Christ, the Son of God") are treated differently based on whether the speaker is INTRODUCING or REFERENCING the identity:

**INTRODUCING (stack):** The speaker is prophetically declaring, formally proclaiming, or revealing the identity for the first time in context. The appositive makes a theological claim — it escalates from name to title. Examples:
- "his name shall be Jesus Christ, / the Son of God." (2 Ne 25:19 — Nephi's naming prophecy)
- "that I am Jesus Christ, / the Son of God," (3 Ne 20:31 — Christ's self-declaration)
- "Christ was the God, / the Father of all things," (Mosiah 7:27 — Abinadi's Christological claim)
- "Hosanna to the Lord, / the most high God;" (1 Ne 11:6 — liturgical exclamation)

**REFERENCING (merge):** The speaker is using an already-established identity as a name unit. The audience already knows. The appositive identifies, doesn't escalate. Examples:
- "I am a disciple of Jesus Christ, the Son of God." (3 Ne 5:13)
- "in the name of Jesus Christ, the Son of the living God;" (Morm 9:29)
- "O God, the Eternal Father," (Moroni 4:3, 5:2 — liturgical formula)

**The test:** Is the speaker REVEALING identity (audience doesn't know, or the moment demands formal proclamation) or USING identity (audience already knows, name is formulaic)?

Corpus inventory: 38 divine title appositive constructions identified. 18 already stacked, 6 newly stacked (all INTRODUCING), 14 correctly merged (all REFERENCING).

---

### Update — 2026-03-24 (Alma 7–8 editorial session)

Three candidate rules emerged from manual review of Alma 7–8. Rules 20 and 21 are considered settled; Rule 22 is settled in principle but requires editorial judgment in application.

#### Rule 20: Inverted predicate constructions earn their own line.

When the predicate is fronted for emphasis — "great is my joy," "blessed are they," "marvelous are the works" — break before the inverted predicate. The inversion itself signals that the author is marking this as rhetorically weighted; the construction is a discrete image and a natural breath unit.

**Test:** Can you rephrase it in normal word order ("my joy is great") and the emphasis is lost? If yes, the inversion is doing rhetorical work and deserves its own line.

**Example (Alma 7:17):**
```
yea, concerning the things which I have spoken,
great is my joy.
```
Not: `yea, concerning the things which I have spoken, great is my joy.`

#### Rule 21: Title/role stays with its domain.

Never split a title or role designation from the prepositional phrase that completes it: "high priest over the church," "king over the land," "chief judge among the people," "captain over the armies." The title is semantically incomplete without its domain.

**Test:** Would the title alone be ambiguous or incomplete as a referent? If yes, keep title + domain on one line.

**Example (Alma 8:11):**
```
and we know that thou art high priest over the church
which thou hast established in many parts of the land,
```
Not: `and we know that thou art high priest / over the church which thou hast established...`

#### Rule 22: Virtue/vice lists — examine for parallel structure.

When a passage stacks moral qualities, exhortations, or enumerated items, examine the list for detectable parallel patterns before making line-break decisions. Common patterns to look for:

- **Dual parallels (2-beat pairs):** "women and children," "humble and submissive," "spiritual and temporal." These stay together as a unit unless the second element introduces genuinely new content.
- **Triadic parallels (3-beat triads):** "faith, hope, and charity." These stack vertically if each element carries enough weight, or stay merged if they function as a single compound concept.
- **Dual + expansion (2+1 pattern):** A paired doublet followed by a third element that expands or recontextualizes the pair. The expansion earns its own line.
- **Crescendo lists:** If the list items grow progressively longer, the lengthening may be deliberate — each item asks more of the reader. Do not normalize long lines to match short ones if the growing length tracks growing rhetorical weight.

**Test:** Is there a detectable rhythmic pattern (2-beat, 3-beat, escalating doublet)? If yes, line breaks should make it visible. If no pattern is detectable, default to the breath/image test per line. Do not impose parallelism that isn't there — but do not obscure it either.

**Example (Alma 7:23) — crescendo preserved:**
```
And now I would that ye should be humble,
and be submissive and gentle;
easy to be entreated;
full of patience and long-suffering;
being temperate in all things;
being diligent in keeping the commandments of God at all times;
asking for whatsoever things ye stand in need,
both spiritual and temporal;
always returning thanks unto God for whatsoever things ye do receive.
```
The list grows longer as the demands grow heavier. The longer lines earn their length.

---
*Last updated: 2026-03-24*
