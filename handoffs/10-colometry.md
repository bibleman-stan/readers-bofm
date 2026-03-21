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
