# BofM Colometry — Operating Canon

**Version:** 2.0 (2026-04-19 rewrite)
**Predecessor:** `archive/colometry-canon-v1-retired-2026-04-19.md` — retained for reference, no longer authoritative.

---

## How to use this document

This canon serves two distinct audiences, and the sections are organized accordingly.

**If you are a HUMAN** (Stan, a collaborator, a scholar reading to understand the method):
- Read **Part I — Method** (§0 Purpose, §1 Framework, §2 Categories A/B/C). This explains *what* we are doing and *why*.
- Read **Part III — Process** (§7 Change Protocol) to understand how the canon evolves; see `git log -- private/01-method/colometry-canon.md` for per-change rationale.
- Consult **Part II — Operating Rules** only for a specific rule's detail (§5) when reviewing an editorial decision.

**If you are a ROBOT** (a Claude agent, a validator, an automated sweep applying rules):
- Read **Part II — Operating Rules** (§3 Quick-Reference, §4 Layer 1 Pointers, §5 Rule Detail, §6 Validator Suite). This is your work queue and reference.
- Read **Part I §1 "The Framework"** once to understand the gate/criterion/diagnostics — it governs rule priority when multiple fire.
- Read **Part I §2 "Autonomy Boundary"** to know when to apply vs. flag.
- Validator output is a **work queue**, not a review queue. `STRONG-*-CANDIDATE` tags are application-ready Category A by default; `REVIEW-REQUIRED` items are the only flags that need per-item editorial judgment.

**If you are updating this document**: read Part III §7 Change Protocol first.

---

# Part I — Method (for humans understanding what we are doing)

## 0. Purpose and Stance

### Mission

**We are revealing atomic thought units (ATUs) — units of meaning the reader can process discretely.** Each line on the page renders one ATU; each ATU is a span the reader can take in before needing the next. ("ATU" is a descriptive label for the unit this method reveals; see Pragmatic Stance below — we do not claim a cognitive-theoretic grounding.) We are not doing English typography. We are not revealing rhetorical parallelism (Parry is a separate layer that may overlap with ours but is not our target). We are not prescribing oral delivery. We are formatting the text so that an ESL reader, a child, or a newcomer can take the scripture one atomic thought at a time.

### Origin

**Stan's premise:** *"Humans think, compose, and deconstruct (read and hear) in atomic thought units (ATUs) — units that correspond to how ideas are generated, encoded, and recovered."* This is the working hypothesis that drives the project.

**Intellectual lineage.** Royal Skousen's demonstration that the Book of Mormon could be reduced to sense-lines (*The Earliest Text*, 2009/2022) was the trigger for what this method now formalizes as the ATU. **This project is the parent** — Skousen's foundational work was on the BofM corpus. The sibling GNT Reader project is the analogical extension ("what is true for the Book of Mormon is likely true for the Greek New Testament, and perhaps any text"). The methodology itself — framework, rules, structural justifications, merge-overrides — emerged from hands-on editorial experimentation across all 15 books. It was not derived from scholarly framework.

### Method

**The mission is sense-driven. The method is syntax-constrained.** These are different things and they belong in different parts of this document.

The method leads with syntax (§1 "Syntax Forbids Splits") not because syntax is primary to the mission, but because **syntactic violation is fatal while sense ambiguity is recoverable within the permitted space.** A break that violates English grammar is always wrong no matter how strong the sense argument; a sense judgment inside the permitted space can be revisited by editorial review. Leading with syntax preserves the discipline that lets sense work — it doesn't demote the mission.

Novel rules can and do originate from sense-driven observation (Alma 22:15's speech-act-after-frame is one such case). The method accommodates this: sense proposes, syntax filters, the combination becomes a rule. But every break that survives to the corpus must be affirmable by English syntax. This is the non-negotiable operational floor.

### Pragmatic stance

This methodology is a set of conventions that reflect what we are trying to reveal. It is not derived from a cognitive theory; we are not claiming otherwise. Later work may investigate why it works. For now, we operate it honestly as what it is: a consistently-applied editorial practice grounded in English syntax, tested against the corpus, and refined by validator sweeps.

### Ground

Every rule here cites an English grammatical fact (anchored in Universal Dependencies labels — see [`data/syntax-reference/ud-taxonomy.md`](../../data/syntax-reference/ud-taxonomy.md) — and in traditional grammar vocabulary from CGEL / Quirk et al.). Rules that cannot be grounded in English syntax are editorial principles and labeled as such.

### Scope

This canon governs where lines break in the v2-mine source texts. It does not govern punctuation (canonical LDS text, untouched), words (never added, removed, or altered), or layout beyond break positions.

---

## 1. The Framework — Proposition-First, Syntax-Constrained

The framework is: **each proposition splits by default, unless syntax forbids.** Substantive adjuncts (slot-fillers in narrative frames) count as atomic thought units (ATUs) and also earn their own lines. Image sharpens ambiguous cases. (Equivalently at the operational level: at any candidate boundary the default is merge — see §1 Decision Procedure step 1 — and a split is licensed only when a proposition or structural-justification boundary is identified. The two phrasings are scope-distinct: "splits by default" generates the proposition-level inventory; "merge by default" is the per-location heuristic. Same procedure, different vantage points.)

### The Generative Principle

**Each proposition splits by default.** A proposition is the prototypical ATU — a complete predication (subject + finite verb + complement) that the reader can process as a single cognitive bite. Propositions drive line breaks. There is no positive requirement to break beyond this; there is no positive requirement to merge beyond this. The question at every candidate location is: *is this a proposition boundary?*

"Proposition" also includes the five structural-justification cases (below) — non-predicated units that function as atomic thoughts via formal-structural recoverability. These are the only non-strict-predication units that qualify.

### Syntax Forbids Splits — three closed-list ways

Syntax does not generate breaks. Syntax only vetoes them. A split that proposition-first would generate is forbidden when one of these three applies:

1. **Layer 1 mid-phrase prohibitions.** Splits mid-predication, mid-phrase, or mid-lexical-unit — line-final CCONJ, DET, AUX+pending V, ADP+pending NP, V+DO split, fixed multi-word unit, vocative unit, etc. See [`data/syntax-reference/ud-taxonomy.md`](../../data/syntax-reference/ud-taxonomy.md) §7 Break Legality Reference.

2. **Layer 3 complement integrity (Rules 17, 26).** When the matrix verb's or adjective's valence is unsatisfied without its clausal complement — *he said that X*, *it is expedient that X*. The matrix is grammatically incomplete on its own; the complement must merge.

3. **Layer 3 formula integrity (Rules 1, 18, 23).** Lexicalized multi-word frames (*And it came to pass*, *it is expedient that*, date colophons, fixed idioms) function as single units. Never break inside the frame.

These are the "unless" clauses of "split each proposition unless syntax forbids."

### Image Sharpens Ambiguous Proposition Boundaries

**Single image / camera angle.** When proposition-first is ambiguous (e.g., a short participial absolute that could read as continuation of the prior frame or as its own frame), ask: does the mind's eye reposition between candidate frames? Camera-angle shift → SPLIT. No shift → MERGE. This is a tiebreaker for ambiguous cases, not a primary generator.

### The Five Structural Justifications (Closed List)

Non-predicated units that function as atomic thoughts via formal-structural recoverability. The reader can reconstruct "who did what" because formal markers in the text make the missing predicate recoverable.

1. **Formally-marked parallel series.** Members connected by formal markers (*and also*, *nor*, correlative particles, polysyndetic *and*) where the shared predicate is recoverable from the parallel structure. Each member earns its own beat.

 **Compound list break signals.** In a compound list governed by one preposition or verb, bare *"and [noun]"* items are compound objects and stay merged. A break inside a compound list is justified only when one of these signals is present:
 1. **Elided auxiliary + stacked participles** — each is an implied predication (covered by the primary justification 1 rule above)
 2. **Possessive restart** — *"and his"* appearing after items without possessive, OR changing from one possessor to another. *Repeated identical possessive* (*"and his X, and his Y, and his Z"*) is formulaic and does NOT alone justify stacking. Only a possessive RESTART justifies a break.
 3. **Demonstrative** — *"and that/this/these"* signals a new specified noun phrase
 4. **Relative clause attached** — *"which is/who was"* adds a predication to the item

 Without one of these signals, bare *"and [noun]"* items merge. The possessive-restart vs. repeated-possessive distinction is a corpus-specific trap (king-lists and inheritance-lists frequently trigger false-positive stacking without this test).

 **M1 bonded-pair precedence inside compound lists.** When a compound-list item is itself an M1 bonded pair (cognate / intensification / hendiadys — *"mercy and long-suffering,"* *"goodness and long-suffering,"* *"wickedness and abominations,"* *"statutes and judgments"*), the bonded pair is the item — the pair treats as one atomic unit within the larger series. None of the four compound-list break signals (including possessive restart) reaches inside a bonded pair to split it. Corpus already handles this uniformly (Helaman 14, Ether 14, Mosiah 8, Moroni 15).

2. **Portrait accumulation.** A set of attributes building one mental picture, sharing a copular or attributive frame from context ("full of grace and mercy and truth"). Applies only when the stack IS the portrait, not when it is a catalogue.

3. **Speech-act announcement.** Complete communicative predication introducing direct discourse ("And Aaron said unto the king:"). Announcement and quoted content are separate cognitive frames.

 **Named pattern — Verily formula.** *"Verily I say unto you"* and *"Verily, verily, I say unto you"* are invariant speech-act announcements in the BofM (32 instances total, all in 3 Nephi). The formula stands on its own line; the content clause (typically *that*-introduced) leads the next line.
 - **Test:** formula + content clause = two lines. Formula + short complete answer (*"Verily I say unto you, Nay"*, *"they have their reward"*, *"even as I am"*) = one line (the answer IS the content, not a separable clause).
 - **Corpus application:** 3 corpus splits — 3 Ne 11:23 (formula + *that*-clause), 3 Ne 27:9 (formula + *that*-clause), 3 Ne 27:21 (formula + doctrinal statement). 22 instances already correctly protected. 7 "PROTECTED-COMPLETE" (formula + short answer) correctly merged.

 **Named pattern — *saith the Lord* parenthetical.** The BofM-archaic formula *"saith the Lord"* (and epithet variants: *of Hosts, God of Hosts, God Almighty, God, that hath mercy on thee*) inserted mid-prophecy earns its own line. Flanking material is already direct first-person divine speech; the tag is parenthetical authentication, not a predicative proposition. Extends the speech-act announcement principle from utterance onset (introducing speech, colon-marked) to mid-utterance (interrupting ongoing speech for oracle-authority stamp) — same cognitive principle (announcement ≠ content, each is its own frame), applied at a different position.
 - **Diagnostic.** (a) Surrounding material is direct first-person divine speech (*"I will..."*, *"my word..."*). (b) The *saith the Lord* phrase can be removed without breaking grammatical flow. (c) The phrase functions as oracle-authority stamp (retrospective or mid-utterance speaker attribution). All three hold → own line.
 - **SCOPE exclusions:** *saith the Lord that [content]* → Rule 17 speech-indirect (*that*-complement merges, not parenthetical); *thus saith the Lord, [content]* → direct-discourse introduction (existing justification 3 announcement handling); first-person speech without *saith* attribution → no special handling; ordinary prophecy flow.
 - **Corpus application:** ~54 corpus instances across 1 Ne, 2 Ne, Jacob, Helaman, 3 Ne, Mormon, Ether stacked as own lines. ~38 mid-line instances total: ~6 SCOPE-excluded (intro+colon, Lord-of-vineyard parable referent, extended divine appellation), ~3 deferred (mid-line with competing Rule 17 conflicts requiring case judgment), ~26 split as Category-A applications under this rule (1 Ne 17:53, 22:24; 2 Ne 6:11, 6:13, 13:1, 13:2; Jacob 2:5, 2:30, 2:33; Hel 13:10-32, 15:16-17 across two batches; 3 Ne 22:1, 22:8, 23:1, 24:1-17, 25:1; Mormon 8:20; Ether 4:7).

4. **Classical commata.** Short fragmentary utterances carrying full communicative weight (*"Yea."*, *"If not so,"*). Typically 1-3 words; brevity + isolation = deliberate emphasis.

5. **Substantive adjunct as own focus.** A fronted or trailing adjunct (temporal PP, locative PP, causal PP, etc.) that (a) is grammatically peripheral to the matrix predication's core truth AND (b) carries substantial content — enough that the reader processes it as an independent focus rather than background — earns its own line. These are the "slot-fillers" in narrative frames: AICTP projects who-did-what + when + where + why, and a substantive filling of a slot is its own focus-unit.

 **Grammatical grounding:** English treats peripheral adjuncts as syntactically detachable — they can front, trail, or be omitted without breaking the matrix. When the content is substantial, the detachability becomes cognitively active.

 **Test:** can the adjunct be paraphrased as its own "when/where/why/how" clause answering a question the matrix leaves open? If yes, it is a slot-filler and earns its own line.

 **Example (canonical):** *Alma 52:18* — *"And it came to pass that Moroni did arrive with his army at the land of Bountiful, / in the latter end of the twenty and seventh year of the reign of the judges over the people of Nephi."* The temporal PP is a 15-word filling of the AICTP "when" slot — substantive own focus, earns its own line. Not a proposition, but a slot-filler.

 **Pattern: year-formula temporal PPs.** Phrases of the form *"in the Nth year of the reign of the judges"* or *"in the Nth year of X"* reliably earn their own line when they follow a matrix predication (Alma 9:464, Helaman 536, 3 Nephi 915, Ether 2151 all resolve this way). They are substantive (typically 10-15 words), peripheral, and clearly answer the "when" slot.

 **Exclusion: degree quantifiers.** Short PPs that modify the **degree** of a predicate (*"in some degree,"* *"in great measure,"* *"in part"*) do NOT pass the slot-paraphrase test — they modify how-much, not when/where/why. They are predicate modifiers, not slot-fillers. Do not treat them as substantive adjuncts earning their own line.

The list is extensible only by worked example + adversarial validation. A proposed sixth justification must demonstrate (a) that it is a genuinely distinct instance of the same generating principle — formal structure in the text enables cognitive recovery of the full predication, or substantive content independently warrants own focus — and (b) that it survives an adversarial challenge.

### The Four Merge-Override Conditions (Closed List)

**Symmetric counterpart to structural justifications.** Where structural justifications describe cases where the default (merge under propositions-first) is overridden to produce a split, merge-overrides describe cases where an apparent split-trigger is itself overridden — returning the members to one line. The default is still merge; these overrides catch cases where naive application of split-triggers would fragment a unit that should stay whole.

**Generating principle:** Even when a line looks like it could pass the structural prong (formal markers present), merge wins when the resulting fragments would fail on more basic grounds — the chunk is not actually two propositions, the clause nucleus would be ruptured, the fragment cannot stand as atomic thought, or the cognitive prong itself fails.

**Strict-application caveat — rejection ≠ split license.** When a merge-override (M1–M4) does NOT apply to a given case, that does not automatically mean the case should split. It just means THAT override doesn't fire. The default behavior is still determined by the generative principle (proposition-first) and by other applicable rules (other merge-overrides, syntactic vetoes, structural justifications). Do not reason: "M1 rejected → must split." Reason instead: "M1 rejected → apply remaining analysis." Each merge-override's absence is silent, not authorizing.

The list is extensible only by worked example + adversarial validation, same rule as the structural justifications.

#### M1. Gorgianic Bonded Pair

**Definition:** N=2 coordinate members joined by *and* / *or* where the pair functions as a single unified hendiadys or bonded rhetorical image — not two independent propositions. Even under formal *and*-linkage (which would normally trigger structural justification 1), if the pair is bonded, merge.

**Test:** Can the two members be paraphrased as a single unified image or hendiadys? Do they carry shared rhetorical weight without independent predicative force?

**BofM canonical cases:**
- *"weeping and gnashing of teeth"* (judgment passages) — one image of suffering
- *"weeping, and wailing, and gnashing of teeth"* (Alma 40:13) — the full formulaic triad, bonded
- *"grace and mercy"* / *"grace and truth"* — paired divine attributes
- *"faith and repentance"* (Alma 13:14-ish cases) — paired soteriological acts
- *"heaven and earth"* — cosmic pair
- *"dust and ashes"* — humility formula
- *"flesh and blood"* — mortality formula
- *"soul and body"* — anthropological pair
- *"repent and believe"* (2 Ne 1603, 4692) — hendiadic soteriological response

**BoFM-corpus bonded verb pairs (closed list).** Where the canonical-cases list above covers paired nouns and one canonical verb pair, the corpus exhibits a stable closed list of additional verb pairs treated as M1 bonded — true synonymy, cognate-acts, or hendiadys (one act named twice for emphasis):

| Pair | Type | Corpus citations |
|------|------|------------------|
| repent + believe | paired soteriological response | 2 Ne 1603, 4692 (canonical) |
| weep + gnash | suffering manifestation | inferred from nominal hendiadys *"weeping and gnashing of teeth"*; no verbal N=2 corpus instance |
| fight + quarrel | synonymous discord | corpus-attested |
| bless + sanctify | liturgical synonymy | Moroni 4:3, 5:2 (sacrament prayer) |
| fear + tremble | cognate emotional+somatic state | 1 Ne 16:28, 2 Ne 1:25 |
| murmur + complain | synonymous discontent verbalization | 1 Ne 17:48 |
| hunger + thirst | cognate appetitive (verbal) | 3 Ne 12:6 |

**N=2-only caveat.** M1 verb-pair protection fires ONLY on N=2 verb-coordination (two coordinated finite verbs or two coordinated participles under shared aux). It does NOT fire on:
- N=3+ chains (Justification 1 wins per the N=3+ cliff — Helaman 3:16 precedent)
- Nominal occurrences (*"weeping and gnashing of teeth"* is a nominal compound, not a verbal pair — the *weep+gnash* listing above is verbal-extrapolated from the nominal hendiadys, not corpus-attested as a verbal N=2)
- Mixed-class coordinates (one finite + one participial, or one verb + one noun)

**CRITICAL DISTINCTION — what M1 does NOT cover.** M1 covers true synonymy / cognate acts / hendiadys (one act named twice for emphasis). It does NOT cover:
- **Sequential narrative bonding** — *draw + smite* (draw weapon, then strike), *torture + bind* (sequential cruelties), *stone + cast out* (sequential persecution), *take + come* (sequential travel), *creep + slay* (sequential assassination), *lifted + crucified + buried* (passion sequence)
- **Distinct speech acts** — *preach + prophesy* (a prophet does both as distinct activities), *exhort + preach*, *pray + supplicate* (the latter dropped 2026-05-10 per Wave 6 audit; only attestation was the N=6 list at Moroni 6:9 — same shape as the rejected *preach+exhort* and *preach+prophesy*)
- **Rhetorical/thematic clustering** that names sequential or distinct actions

Per `feedback_rhetoric_bandwagon.md` and `feedback_rhetorical_force.md`, rhetorical/narrative bonding is NOT structural-rule territory — sequential distinct actions split per the generative principle even when they form a recognizable rhetorical figure.

**Detector reference.** `validators/colometry/validate_polysyndetic_verb_chain_ud.py` `M1_BONDED_VERB_PAIRS` set + `is_m1_bonded` function. The list is extensible only by worked corpus example + adversarial validation, same rule as the structural justifications.

**Tie-breaker when M1 and structural justification 1 both seem to apply (N=2 formally-marked pair):**
- If each member has a distinct non-synonymous finite verb → structural justification 1 wins (SPLIT). Example: two members with genuinely different actions.
- If the two members are semantically synonymous, cognate, or intensification variants → M1 wins (MERGE). Example: *"repent and believe"* (synonymous soteriological pair under shared imperative force).
- If the members are bonded-pair nouns/adjectives (not verbs) with unified rhetorical weight → M1 wins (MERGE).

This tie-breaker is the canonical specific case of the cross-cutting **N=2 Adjudication Principle** (see §1, after the Decision Procedure). The same merge-vs-split logic applies to Rule 12 extended N=2 compound verbs and Rule 17 two-member *that*-series.

**Asymmetric-modifier sub-clause.** When an M1-candidate bonded pair has one member carrying a PP modifier or relative clause the other lacks (*"repentance and faith on the Lord Jesus Christ,"* *"signs and wonders among the people,"* *"gold and silver of great worth"*), M1 still wins → MERGE if the modifier attaches semantically to the pair AS A UNIT (answering "in/on what?" where the modifier's referent is the joint object of both members). SPLIT only if the modifier scopes over only one member to the exclusion of the other, producing genuinely distinct predicative force (rare — requires explicit contrastive signal like *"repentance from sins and faith in Christ"* where the two members point to different referents).

- **Joint-attachment test.** Paraphrase with the modifier distributed to both members: *"repentance on the Lord Jesus Christ and faith on the Lord Jesus Christ"*. If the paraphrase preserves meaning (both members naturally take the modifier), joint-attachment holds → MERGE. If the paraphrase distorts meaning (one member doesn't naturally take the modifier), asymmetric scoping → SPLIT.
- **Corpus applications:** Mosiah 18:7 *"only through repentance / and faith on the name of the Lord God Omnipotent"* → MERGE (both repentance and faith are "on the name of the Lord"). Alma 37:33 *"Preach unto them repentance, / and faith on the Lord Jesus Christ;"* → MERGE (both repentance and faith aimed at Christ).
- **WHY:** modifiers attaching to a bonded pair typically scope jointly; treating one member as carrying the modifier and the other as bare introduces a false asymmetry and fragments the hendiadic unity. **HOW WE KNOW:** corpus survey surfaced 2 instances of the *repentance-and-faith-on-[Lord]* pattern currently split; both merge cleanly under joint-attachment. **SCOPE:** N=2 M1-candidate pairs where one member has a PP/relative modifier; joint-attachment test adjudicates; explicitly contrastive signals preserve split.

**Grammatical grounding:** CGEL Ch. 14 on coordination of semantically-bonded pairs; classical hendiadys.

#### M2. Verb-Object Clause-Nucleus Bond

Covered by existing **Rule 17 (Complement Integrity)**. A governing verb or adjective requiring a clausal complement forms one integrated predication with its complement. The matrix verb alone does not carry complete predication. See §5 Rule 17 for full treatment including the six-class verb list, exceptions, and delete-test diagnostic.

M2 is named here for cross-canon consistency with GNT's merge-override framework; operationally it's Rule 17 territory.

#### M3. Bare-Governor Indivisibility

**Definition:** A head word — participial adjective (*full, mighty, great* functioning predicatively), governing participle (*having, being, telling, desirous, instructed*), or discourse particle standing alone — cannot stand on its own line without at least one complement, object, or dependent. The bare governor fails the atomic-thought test because it is grammatical machinery awaiting content, not a complete predication.

**Test:** Can the isolated head-word be read as a complete thought? Or does the reader's attention dangle forward, expecting completion on the next line?

**BofM canonical cases:**
- Participial frame + pending complement: *"telling them / that there could be no atonement..."* → bare "telling them" awaits its that-clause complement (merge)
- Adjectival frame + pending infinitive: *"were desirous / to throw me into the depths of the sea"* → "desirous" requires its to-infinitive complement (merge)
- Bare discourse particles: *"Wherefore,"* / *"Therefore,"* / *"And now,"* alone on their own line WITHOUT following content — fails M3 unless explicitly licensed by Rule 20 Exemption (c) as a sentence connective with its content merged on the next line.

**Contrast with speech-intro (structural justification 3):** Finite speech-act formulas (*"said unto them:"*, *"declared:"*, *"cried:"* with colon) ARE complete speech-act predications — the speech act itself is the content. Bare participial frames (*"telling"* without complement, *"saying"* without following speech) are not; they await content.

**Contrast with Rule 21 (participial absolute):** A full participial absolute ("X having Y-ed,") with its own subject + participle + optional complement IS a complete predication and earns its own line. M3 catches BARE participial heads WITHOUT the subject-bearing absolute structure.

**Grammatical grounding:** CGEL Ch. 4 on finite vs. non-finite predications; complement requirements of governors. Bare governors lack the obligatory arguments their semantic class requires.

##### M3 extension — Bare trailing participial heads

**Triggering case.** Alma 32:1: *"And it came to pass that they did go forth, / and began to preach the word of God unto the people, / entering into their synagogues, and into their houses;"* — the third line is a bare participial head (*"entering"*) with PP complements but no own subject; it inherits the matrix subject *"they"* from two lines up. Under the foundational atomic-thought test, the line is not a complete unit standing on its own — it is grammatical machinery awaiting matrix anchoring.

**Rule.** Bare trailing participial heads (subject-inheriting; no own-named subject; in adjunct position relative to a matrix predication) are M3 cases — they merge with their matrix predication. Same shape as M3's existing *"telling them / that there could be no atonement..."* MERGE precedent, extended from leading-participial-with-pending-complement to trailing-participial-with-pending-subject-anchor.

**Four structural carve-outs (these stay own-line):**

1. **Stack-cap.** Adjacent participials stay own-line when the stacking IS the rhetorical structure: N≥3 adjacent participials, OR N≥2 with the same -ing lemma (anaphoric repetition: *"having... having... having..."*), OR merged-line would exceed 130 characters. Evaluate stack depth on the **full verse-context window** (include leading "and"-prefixed and capitalized participials), not a narrow line-pair window. Canonical cases: 2 Ne 1:10 (5-deep *"having..."* enumeration), Mosiah 15:9 (Christ's intercessory acts), Alma 7:23 (virtue-list embedding), Alma 13:29 (faith/hope/love triad), Helaman 4:12 (sin-list).

2. **Coord-list member.** When the participial is a parallel beat in an open coordinate list of participial-fronted lines (each member co-equal, not modifying), the participial earns its own beat. Diagnostic: prev N≥2 lines are also participial-fronted with parallel structure (not just adjacent — parallel). Canonical cases: Alma 4:13 *"feeding the hungry"* inside *imparting / succoring / feeding / suffering*; Mosiah 21:13 *"submitting themselves"* inside *subjecting / submitting / driven / burdened*.

3. **Antecedent-locality fail.** When the nearest preceding NP that supplies the participial subject is NOT the matrix subject — instead it is inside a PP, a relative clause, or other oblique position — the participial is not subject-inheriting from the matrix in the relevant sense; it modifies the embedded NP. Diagnostic: nearest preceding NP is object of preposition (*"concerning Giddianhi, demanding..."*), or subject of an embedded relative clause, or fronted between matrix subject and verb. Canonical cases: Ether 13:21, 3 Ne 3:11, 3 Ne 20:25, Helaman 11:23.

4. **Fronted-position participial.** When the participial precedes the matrix verb (placed between subject and finite verb, or fronted before the subject), it is fronted-circumstantial — backward-merging would split subject from predicate. Diagnostic: the next non-blank line begins with *therefore* / *wherefore* / *then* + finite verb, or the matrix subject sits between the participial and the finite verb. Helaman 11:23 is the canonical case.

**Length backstop:**

5. **Merged-line > 130 characters → REVIEW-REQUIRED.** Cases where applying the merge would produce a line exceeding ~130 characters route to human review rather than auto-apply. This catches the catalog-precedent catastrophe (Jarom 1:8's 199-character merge, where the matrix predicate is buried far back behind a long *"rich in X, and in Y..."* coordinate-NP catalog) and the Rule-17-bound-complement long merges.

**No editorial carve-outs.** A prior draft of this extension proposed three editorial carve-outs (theological / Christological appositive, antithetic / paired parallelism, gerund-as-noun) as named categories with hand-curated verse-lists. These were retired as a category fudge inconsistent with the project's stated mission — see §0 Mission objective (3): the project seeks to *expose* rhetorical and theological structure that has been obscured, not to preserve it on doctrinal-weight grounds. The discriminator for ATU-status is the atomic-thought test, not the doctrinal weight of the content. Each former carve-out resolves cleanly under the general rule:

- *Christological / theological participials* (former list: Mosiah 15:2 *"being the Father and the Son"*, etc.) — each case is evaluated as ATU on its merits. Mosiah 15:2's *"being the Father and the Son"* is its own predication-equivalent (subject + predicate-nominative) → own line under the *general rule*, not because it is theological. Theology is irrelevant to the test.
- *Antithetic / paired participials* (former list: Mosiah 18:21, Alma 9:22, 2 Ne 2:23) — each member is its own predication. Already covered by the generative principle (each proposition splits) and the Parallel-List Uniformity Principle (§1). The "antithetic" naming was a redundant description.
- *Gerund-as-noun* (former list: Enos 1:23, 2 Ne 13:24, Alma 32:43) — these are not participial verbs at all; they are deverbal nouns inside coordinate noun-lists. The participial-merge rule should not type-match on them in the first place. This is a validator type-detection issue, not a canon-level carve-out.

The validator implementation may include syntactic precision-checks for gerund-as-noun shapes (to avoid the rule firing on non-participials) and may flag verses where editorial review is warranted, but these are implementation concerns; the canon does not name them as exception categories.

**WHY / HOW WE KNOW / SCOPE.** WHY: bare trailing participial heads without resumptive structure fail the foundational atomic-thought test — they are non-finite grammatical machinery that requires matrix anchoring to become a complete unit. HOW WE KNOW: corpus survey + 5 parallel hand-walks classified the merge population, and a mission-alignment audit retired the editorial carve-outs as inconsistent with §0 Mission objective (3). SCOPE: applies only to trailing/adjunct-position participials with no own-named subject and no resumptive structure; absolute phrases with own subject (Rule 21) unchanged; M3's leading-participial-with-pending-complement cases unchanged.

**Cross-rule precedence.** Rule 21 (participial absolute) wins when the participial has its own named subject — the participial absolute is a complete predication. M3 extension only catches BARE participials without subject. Rule 17 (complement integrity) and Rule 19 (anaphoric relative) post-merge re-splits are honored — if the merged line contains a Rule-17-bound that-clause that should split or a Rule-19 anaphoric relative, those rules fire afterward. Length-cap (guard 5) applies regardless of the other guards.

**Implementation.** `validators/colometry/validate_participial_phrases.py` implements the 4 structural guards + length backstop. Cases that the prior carve-out lists protected are now re-evaluated case-by-case against the atomic-thought test; some remain own-line as ATUs in their own right (general rule, not as named exceptions), others merge per the rule.

#### M4. Fragmented Atomic Thought-Unit

**Definition:** If splitting a line would produce fragments that individually fail the atomic-thought test, merge. This is the inverse of the cognitive prong: the cognitive prong requires each resulting chunk to be its own atomic thought for a split to proceed; if any resulting fragment fails that test, the split is blocked.

**Test:** Read each proposed resulting line aloud as a standalone unit. Does it constitute one focused-attention chunk with bounded information? If any resulting line fails, the split is over-fragmenting.

**Scope discipline — prospective not retroactive.** M4 fires ONLY when evaluating a PROPOSED split. It is evaluated by reading each of the two proposed fragments as standalone units; if either fails atomic-thought, the proposed split is blocked → MERGE. **M4 is NOT a retrospective merge generator.** When an existing split shows both fragments individually passing atomic-thought, M4 does not fire, even if the two events are causally, narratively, or rhetorically linked. "Narrative completion" and "atomic-thought failure" are different tests; conflating them is the documented failure mode behind three reverts in commit `6baf7d7`: Alma 47:24 stab+fall, 1 Ne 5:4 tarry+perish, Ether 14:29 approach+defeat. The operational rule: ask *"does THIS line, alone, constitute one focused-attention chunk?"* — not *"would merging produce a more complete narrative beat?"* The former fires M4 when appropriate; the latter is aesthetic reasoning outside M4's scope.

**BofM canonical cases:**
- Trailing prepositional modifiers orphaned from their predicate: *"...he spake, / to your condemnation."* (short trailing PP with no independent image) — fails M4.
- Dangling discourse particles: *"alla"* alone on a line without a complete clause.
- Orphaned appositives separated from their head noun when the appositive alone has no independent image.
- **"Yea, even X" emphatic appositive (partial-adoption sub-rule):** a short emphatic appositive introduced by *"yea, even"* that lacks independent predicative weight — merely reinforces the preceding clause's referent. Sweep classifiers:
 - **3-condition test** for mechanical merge: (1) line starts with *"yea, even"*, (2) line contains no finite verb (no independent predication), (3) preceding line is a complete clause. All three hold → MERGE.
 - **Exclusion clause:** when the *"yea, even X"* appositive contains a **year-formula temporal reference** (e.g., *"in the Nth year of the reign of the judges"*) or a **proper-noun entity** (named character, place, people, or government/institutional body), the appositive is a substantive slot-filler under **structural justification #5 (substantive adjunct as own focus)**, not an M4 fragment. KEEP SPLIT. Canonical case — Alma 50:23 *"...than in the days of Moroni, yea, even at this time, in the twenty and first year of the reign of the judges"* — the year-formula trailing appositive is exactly the substantive slot-filler that justification #5 protects. Justification #5 wins over M4 when the appositive carries substantive temporal, entity, or institutional content.
 - **Sweep results:** 182 corpus instances of *"yea, even"* line-starts. **53 net applied** across 10 books (1 Ne, 2 Ne, Jacob, Mosiah, Alma, Helaman, 3 Ne, Mormon, Ether, Moroni). **69 KEEP-SPLIT** (line has own finite verb → independent predication, not M4 fragment). **59 REVIEW-REQUIRED** (ambiguous — per-item judgment). Adoption threshold ≥80% not met (68% clean categorization); sub-rule remains **heuristic-trigger-for-review**, not mechanical-apply. The 53 applied merges each passed the 3-condition test individually plus the exclusion check.

**This is the adversarial-auditor's primary over-split detection rule.** Corpus audit enumerated 211 M4 candidates: 23 HIGH-confidence, 126 MEDIUM, 62 LOW. Follow-up sweep surfaced 182 *"yea, even"* line-starts total (the HIGH subset was a conservative filter).

**Precedence over structural justifications — critical refinement.** M4 fires ONLY when splitting produces a fragment that **fails** the atomic-thought test. A fragment that PASSES atomic-thought via another structural justification's cognitive prong does NOT fail. Specifically:
- **Formally-marked parallel series (justification 1):** members of a 3+ member series pass cognitive-prong via shared-predicate recovery. M4 does NOT fire on series members. Example: Alma 8:7 *"their lands, and their cities, and their villages, yea, even all their small villages"* is a 4-member catalog; the yea-even member is a parallel-series beat, not an M4 fragment. Decision procedure: justification 1 cognitive-prong passes → M4 does not block → STACK.
- **Substantive adjunct (justification 5):** substantial adjuncts (year-formulas, proper-noun entities, institutional bodies) earn own lines. M4 does NOT fire on these. Example: Alma 50:23 year-formula PP; Alma 60:14 *"the slothfulness of our government"* (institutional body). KEEP SPLIT.

**Parallel interaction with Rule 12 compound-verb extension.** Rule 12's shared-auxiliary merge also defers to justification 1 when the coordinated participles are members of a 3+ member parallel series. Example: Helaman 3:16 6-verb cascade *"murdered, plundered, and hunted, and driven forth, and slain, and scattered"* — shared aux *"have been"* normally triggers Rule 12 merge, but 6-member parallel series passes cognitive-prong, so justification 1 wins → STACK. Same logic for Mosiah 27:35 participial series (striving/confessing/publishing/explaining).

**Unified principle:** merge-overrides (M1–M4) and Rule 12 compound-verb merge block split-triggers ONLY when splitting would produce true atomic-thought failure. Fragments that pass atomic-thought via a structural justification's cognitive prong are not M4 fragments; the structural justification wins.

**Extensibility note:** new M4 sub-patterns can be promoted to named status when corpus audit surfaces 10+ instances with unified structural signature AND sweep passes ≥80% clean categorization. Patterns that hit the first threshold but not the second (like *"yea, even X"*) remain trigger-for-review sub-patterns — useful as validator input, not as mechanical-apply rules.

### Summary: the four forces

| Force | Direction | Role |
|-------|-----------|------|
| Propositions (+ 5 structural justifications, including substantive adjunct) | GENERATIVE | Default split at every proposition or justified non-proposition boundary |
| Syntax (Layer 1 + Rule 17/26 + Rule 1/18/23) | SUBTRACTIVE | Forbids some splits the generative principle would produce |
| Merge-overrides (M1–M4) | SUBTRACTIVE | Block split-triggers when resulting fragments fail on more basic grounds |
| Image (camera angle) | DIAGNOSTIC | Sharpens ambiguous boundaries |

### The Complete Framework — Decision Procedure

Putting generative, subtractive, and diagnostic forces together, the full editorial decision procedure is:

1. **Default:** merge (propositions share one predicate; atomic-thought test applies at the predication level).
2. **Split-trigger fires** (any of: proposition boundary; one of structural justifications 1–5): tentative split.
3. **Syntax veto** (Layer 1 mid-phrase prohibition; Rule 17 / Rule 26 complement integrity; Rule 1 / Rule 18 / Rule 23 formula integrity): blocks the split → **merge**.
4. **Merge-override fires** (M1 gorgianic pair, M2 clause-nucleus bond, M3 bare-governor, M4 fragmented fragment): blocks the split → **merge**. **When split-trigger and merge-override both fire on the same line, merge-override wins.** The merge-override list is the mechanism that prevents split-triggers from producing non-atomic or bonded-pair fragments.
5. **Image diagnostic** (camera angle): sharpens cases where 1–4 leave room for editorial judgment.

The framework is a default-merge with two closed lists of exceptions — five structural justifications (add splits beyond propositions) and four merge-overrides (block splits that would fragment unity) — plus the syntax-subtractive veto and the image diagnostic.

**Breath retired entirely.** What started as a "fourth criterion" alongside atomic thought (oral-delivery fit) was retired when empirical work showed it was doing cognitive-chunking under oral-delivery cover. **Breath is not foundational and not pragmatically relevant to any aspect of the method.** The cognitive-chunking work it was informally doing — flagging long single-proposition lines with substantial adjuncts — is fully absorbed by structural justification #5 (substantive adjunct as own focus). Earlier "atomic breath unit" framing in CLAUDE.md / handoffs / rules-audit.md was never load-bearing in pragmatic application and has been dropped as residue.

### Application Order — explicit step-by-step

**Purpose.** The Decision Procedure above gives the high-level 5-step ordering. This subsection makes the step-internal ordering explicit so that rule application is provably deterministic — two appliers following the canon converge on the same output regardless of which rule they check first within a step.

**Provenance.** Parallel hostile audits on rule-application reversibility found the canon is commutative in 8 of 9 tested corpus constructions, with one load-bearing gap (Rule 10 × justification 1 at N=3+ object lists, codified in §5 Rule 10). The remaining residual is cosmetic. This subsection consolidates the audits' findings.

**Step 0 — Input filter.** Punctuation is never a break signal (see below). Versification is never a break signal (see below). R28 authorial asymmetry (see below — the §1 *Authorial Asymmetry Principle*; distinct from §5 *Rule 28 — Speech-Act Announcement After Frame*, which is unrelated) governs batch-sweep discipline — filters what counts as a candidate signal *before* generative evaluation begins. None of the three operate within the per-location procedure; they operate upstream of it.

**Step 1 — Syntax veto (Three Closed-List Ways).** At most one fires per location (commutative within-step). The three classes:
- **Layer 1 mid-phrase prohibitions** (Rules 9, 11, 12 simple-aux, 13a) — generic English grammar; a violation is MALFORMED (hard-fatal) and outranks any Layer-3 output.
- **Complement-integrity rules** (Rules 17, 26) — verb/adjective + *that*-clause or infinitive complement stay together.
- **Formula/vocative-integrity rules** (Rules 1 AICTP, 15 vocative, 18 fixed idiom, 23 date colophon) — protected multi-word units.

Within this step, when both a Layer 1 and a Layer 3 rule could apply, Layer 1 wins. Scattered precedence notes in §5 (Rule 17 trumps Rule 19; Rule 27 vs Rule 7 for compound *insomuch that*; Rule 22 × Rule 15 in vocative environment) adjudicate intra-Layer-3 conflicts; these are listed in each rule's text.

**Step 2 — Split-trigger (generative).** Proposition-first split, plus structural justifications 1-5. **Multiple justifications firing are co-compatible — they all agree on SPLIT; no adjudication needed.** N=2 Adjudication Principle governs coordinate-pair cases (see below). Helaman 3:16 precedent governs N=3+ (justification 1 always wins over merge-rules at N=3+ for coordinate *predications*, with the Rule 10 object-list exception — see §5 Rule 10). R28 authorial asymmetry acts at Step 0; justification 1 does not override authorial asymmetry within a series.

**Step 3 — Merge-override (subtractive).** M1 gorgianic pair, M2 clause-nucleus bond (Rule 17 territory), M3 bare-governor indivisibility, M4 fragmented atomic thought-unit. Specialized merge rules (Rule 10 V+DO, Rule 12 extended compound-verb, Rule 22 REFERENCING default, Rule 27 *insomuch that* 3-condition) operate within this step as aliases or specializations of the M1-M4 generic classes. **Multiple merge-overrides firing are co-compatible — they all agree on MERGE; no adjudication needed.** M4's precedence refinements (§1 M4 section) govern M4 vs. justifications 1/5. Step 3 wins over Step 2 when both fire on the same location (per Decision Procedure step 4).

**Step 4 — Editorial-pattern and image tiebreaker.** EP-1 through EP-5 and the image diagnostic fire only when Steps 1-3 leave the decision open. EPs and image are co-equal tiebreakers, not generators or vetoes. When an EP-rule and a structural justification would both apply to the same location, **the justification (Step 2) wins before the EP is consulted** — EPs are strictly post-hoc for cases Steps 1-3 under-determine.

**Proposed rules (27, 28) apply at their named step when their conditions fire.** "Proposed" status gates corpus-wide sweep confidence (see §7 Proposed-rule adoption protocol), not per-instance authority within the procedure.

**Commutativity guarantee.** With the above step-internal rules stated explicitly, the canon is provably deterministic for all rule-pair contentions the corpus has surfaced. The one residual gap (Rule 10 × justification 1 N=3+) is closed by Rule 10's own N=3+ coordinate object-list precedence sub-clause. No other known non-commutative rule pair exists.

### N=2 Adjudication Principle

**The problem this solves.** Several canon rules mandate MERGE for N=2 coordinate constructions — M1 gorgianic pair, Rule 12 extended compound-verb under shared auxiliary, Rule 17 two-member *that*-series. Simultaneously, structural justification 1 (formally-marked parallel series) mandates SPLIT when each member earns its own atomic beat. At N=2 both rules can fire on the same construction; before this principle, the canon adjudicated only M1 (at §1 Gorgianic Bonded Pair tie-breaker), leaving Rule 12 and Rule 17 two-member silent. The silence produced real errors — Alma 24:10 compound-verb under shared *hath* (*"hath forgiven us... and taken away the guilt"*) sat under Rule 12 extended's merge mandate while its fragments each pass atomic-thought as distinct non-synonymous actions.

**The principle.** When a merge-mandating rule (M1, Rule 12 extended, Rule 17 two-member *that*-series) and a split-mandating rule (structural justification 1) both fire on the same N=2 coordinate construction:

- **Bonded / synonymous / cognate / intensification variants → merge wins.** The two members form a single unified image, action, or proposition under one cognitive chunk. Examples: *"repent and believe"* (M1 synonymous imperatives), *"weeping and gnashing of teeth"* (M1 canonical), *"know that X, and that X-restated"* (Rule 17 two-member synonymous *that*-clauses).
- **Distinct non-synonymous → split wins.** Each member is its own atomic beat per structural justification 1. Examples: *"hath forgiven us of X and taken away Y"* (Rule 12 extended with distinct non-synonymous verbs — Alma 24:10), *"know that they are of Israel, / and that they speak forth revelation"* (Rule 17 two-member distinct propositions).

**Diagnostic.** Apply the M1 verb-synonymy test (§1 Gorgianic Bonded Pair tie-breaker): *can the two members be paraphrased as a single unified image or proposition without loss of content?* If yes → merge. If the paraphrase requires dropping semantic content unique to one member → split.

**Applies to.** M1 N=2 pairs; Rule 12 extended N=2 compound verbs under shared auxiliary; Rule 17 two-member *that*-series; future canon additions where a merge-rule and structural justification 1 both fire at N=2.

**Does NOT apply to appositional constructions.** Rule 22 (divine title appositives — *"Jesus Christ, the Son of God"*) and Rule 15 (vocative + close appositive — *"O God, the Eternal Father"*) are NOT adjudicated by the N=2 Principle's synonymy test. Appositives are semantically synonymous by definition — the second member re-names the first — so the synonymy test would mechanically fire "merge" on every appositive. Rule 22's formal-anchor diagnostic (INTRODUCING vs. REFERENCING) and Rule 15's vocative indivisibility are the correct adjudications for these cases. The N=2 Principle reaches only *and/or*-coordinated pairs where the two members are SEMANTICALLY DISTINCT CANDIDATES for unification — not re-naming appositives.

**Does not apply at N=3+.** The Helaman 3:16 precedent (six-verb cascade *"murdered, plundered, and hunted, and driven forth, and slain, and scattered"*) establishes that at N=3+ formally-marked parallel series, structural justification 1 wins regardless of whether a merge-rule is also firing — cognitive-prong is formally recoverable from the series itself, and merge-rules defer. The N=2 vs. N=3+ cliff is principled: two items invite bonding (doublet reading); three or more invite cataloguing (series reading).

**Scope of the N=3+ cliff.** The cliff applies to coordinate **predications** — compound verbs under shared auxiliary (Rule 12 extended), coordinate *that*-clauses (Rule 17 two-member series extended), coordinate finite clauses. It does NOT apply to coordinate **objects** under a single shared verb — those are governed by justification 1's compound-list-break-signals sub-rule (at §1 structural justification 1), whose default is to merge bare *"and [noun]"* items unless one of the four break-signals fires. See §5 Rule 10 Scope for the canonical object-list case (Mosiah 18:7).

**Why one principle, not three.** M1's existing tie-breaker, Rule 12 extended's silent N=2 case, and Rule 17 two-member *that*-series all face the same adjudication question. Promoting it to a named cross-cutting principle (a) avoids re-stating the same logic in three places, (b) makes future N=2 rule-conflicts discoverable rather than silent, and (c) gives a uniform diagnostic for new N=2 constructions that may surface in future canon work.

### Punctuation is not a break signal

The canonical LDS text's punctuation is preserved for fidelity but has **no deterministic role** in line-break decisions. Periods, commas, semicolons, colons, em-dashes, and question marks mark orthographic and grammatical pauses in the printed text, but they do not encode the atomic-thought boundaries we are revealing. A break may coincide with a punctuation mark, but the mark does not license the break — syntax does.

**Test.** If the only reason you can cite for a break is "there's a comma here" or "the sentence ends," the break is not affirmed. Find the syntactic feature or merge.

**Why this matters.** Punctuation in the 1829 text and its descendants was added by editors (Oliver Cowdery, John Gilbert, and later revisers including Skousen) and has been revised multiple times across printings. It does not derive from the original oral/dictated register, and it reflects editorial decisions we are not trying to preserve or privilege. Treating punctuation as authoritative would import nineteenth- and twentieth-century editorial punctuation conventions as if they were part of the text's structure — which is exactly the "impose, not reveal" failure mode this methodology is designed to avoid.

**Practical consequence.** A long sentence with multiple commas is not a multi-line signal; it is a one-clause signal to examine for atomic-thought boundaries on syntactic grounds. A semicolon is not a forced break. An em-dash is not a forced split (Rule 22 covers the specific interpolation case syntactically, independent of the dash itself).

**What we DO preserve.** Every punctuation mark from the canonical LDS text stays in place. We do not alter, add, or remove punctuation. Line breaks are the only editorial tool.

### Versification is not a break signal

BofM verse divisions were imposed by Orson Pratt in 1879 — editorial overlay, same status as punctuation. No break versification imposes is canonical. If a cross-verse merge case is identified, flag Category B.

### Parallel-List Uniformity Principle

When a multi-verse list of parallel members exists with a shared explicit frame, list members receive uniform line-treatment regardless of their individual syntactic shape. Per-construction rules (e.g., Rule 7 finite-purpose-*that* split) yield to the list-uniformity principle within the list's scope.

**Trigger.** All four conditions must hold:
1. **Multi-verse list, N≥3 members.** Two-member coordinate cases are governed by §1 N=2 Adjudication Principle; isolated occurrences aren't a list.
2. **Shared explicit frame.** A repeated lexical anchor introduces each member: *"And to another,"* / *"And again, to another,"* / *"Wo unto X,"* / *"Blessed are they who,"* / *"If ye do X / If ye do not."*
3. **Parallel members.** Each list-item is the same kind of thought (a gift bestowed, a curse pronounced, a beatitude declared, a conditional outcome).
4. **Authorial-symmetric.** Members do NOT have the finite-verb-count or predicative-head-count asymmetries that §1 R28 Authorial Asymmetry Principle protects.

**Default direction — merge.** Each member's frame + content stays on one line per member. The atomic-thought unit at the list scale is *one bestowal / one pronouncement / one outcome* per member; a frame-fragment alone (*"And again, to another,"*) is not a self-standing atomic thought.

**Why merge wins as the default direction:**
- **Atomic-thought test.** Frame-fragments alone fail it; gifts/pronouncements as units pass it.
- **Anti-Lowth (§0 Mission).** Split-dominant treatment with repeated visible frames IS the parallelism-display layout the project's stance opposes — *"we are formatting the text... not revealing rhetorical parallelism."*
- **Audience.** ESL readers and read-aloud delivery favor one-line-per-member rhythm; per-gift fragmentation across two lines disrupts the list cadence.
- **Descriptive over interpretive.** Merge describes each member as a unit; split imposes a frame-content rhythmic structure on a syntactic surface that doesn't demand it.

**Mechanical signature.**
- Detect shared frame via repeated leading lexical pattern across N≥3 verses.
- Identify dominant treatment among members (count: how many members are 1-line, how many 2-line?).
- Bring outliers in line with dominant treatment; default-merge if no clear dominance OR if applying default-merge passes the atomic-thought test for each member.

**SCOPE — does NOT apply to:**
- N=2 coordinate cases (governed by §1 N=2 Adjudication Principle).
- Authorial-asymmetric series (§1 R28 takes precedence — preserve mechanism-count differences; do not flatten variation).
- Lists without a repeated explicit frame (narrative sequences without lexical anchor).
- Within-verse coordinate predications (governed by Helaman 3:16 precedent — justification 1 wins over merge-rules at N=3+).

**Interaction with Rule 7.** Rule 7 (finite purpose-*that* breaks before *that*) yields to this principle when the purpose-*that* is a list member in an otherwise-merged list. The Rule 7 short-line exception (line 474) is the mechanical channel: in parallel-list context, the short-line exception fires whenever the list's dominant treatment is merge.

**WHY / HOW WE KNOW / SCOPE summary.** WHY: same-pattern-different-treatment in a multi-verse list violates atomic-thought consistency at the list-scale and the project's anti-Lowth stance. HOW WE KNOW: Moroni 10:8-17 spiritual-gifts list — 3 outliers (vv 9, 12, 13 split via Rule 7 default) against 6 conforming members (vv 10, 11a, 11b, 14, 15, 16 merged). Stance B merge-dominant emerged after walking through atomic-thought / anti-Lowth / audience tests. SCOPE: as above.

### Authorial asymmetry overrides editorial symmetry

When a passage contains a serial construction (wo/blessed series, positive/negative conditional pair, beatitude chain, interrogative chain) and the author treats members asymmetrically — expanded mechanism for some, compact for others — **preserve the authorial asymmetry**. Do not pressure compact members to expand, or expanded members to compress, in order to achieve uniform line-treatment across the series.

**Test.** Count the finite verbs, elided verbs, and predicative heads in each member of the series. If counts differ between members in the received prose text, the asymmetry is authorial and the line-structure reflects it. If counts match but editorial line-treatment diverges, that is editorial drift and should converge.

**BofM-attested trigger contexts:**
- **Wo/blessed series with asymmetric member expansion.** Canonical case — 2 Nephi 9:27-38: 9:30 (*"wo to the rich"*) expands to 6 lines with full mechanism (despise poor / persecute meek / hearts upon treasures / treasure is god / treasure shall perish); 9:31-37 are compact 2-line *"Wo unto X, for Y"* treatments; 9:38 closes with an embedded triad (*"return to God, and behold his face, and remain in their sins"*). The asymmetry is authorial. A uniformity sweep asking "are all Wos treated the same?" would illegitimately pressure compression of 9:30 or expansion of 9:31-37 — R28 forbids that.
- **Matthean-parallel Sermon at the Temple.** 3 Nephi 12-14 parallels Matthew 5-7 but with authorial expansions and compressions (3 Nephi 12:1-2 adds a doubled *"blessed are they who shall believe in your words"* preface absent from Matt 5; 12:11-12 expands the persecution/reward discourse). Editorial parallelism-pressure to conform 3 Nephi to Matthean line structure would violate 3 Nephi's distinctive authorial shape.
- **Positive/negative conditional pairs.** *"If ye do X... but if ye do not..."* constructions sometimes have asymmetric treatment across the two halves.

**SCOPE.** Does NOT apply to same-rule-uniformly-applied cases — the `feedback_application_consistency_vs_rule_coverage` discipline governs those (same rule, inconsistent application). R28 governs the distinct failure mode: **imposed uniform structure where the author wrote variation**. The author's finite-verb count, elided-verb count, and predicative-head count per member is the authoritative signal.

**Distinction from §0 Mission.** §0 establishes the general text-honoring posture ("we are formatting the text... not revealing rhetorical parallelism"). R28 names a specific operational guardrail at the split-trigger level: don't symmetrize what the author wrote asymmetrically. §0 is the stance; R28 is the enforcement mechanism against this one failure mode.

**Cross-reference.** Sibling rule at GNT canon §3.7 "Textual asymmetry overrides editorial symmetry" (Matt 25:35-36 positive vs. 42-43 negative as canonical case there). BofM corpus evidence from 2 Ne 9:27-38 and 3 Ne 12:1-12.

**WHY / HOW WE KNOW / SCOPE summary.** WHY: authors' structural choices carry information editorial symmetry-pressure would erase. HOW WE KNOW: BofM-attested cases of authorial asymmetry confirmed at 2 Ne 9:27-38 and 3 Ne 12:1-12. SCOPE: serial constructions where editorial uniformity-pressure could impose structure the author didn't write.

---

## 2. Autonomy Boundary — Categories A / B / C

Every proposed change falls into one of three categories:

- **Category A — Editorial slippage.** Suboptimal break with no theological or rhetorical stakes. Apply confidently.
- **Category B — Rhetorical shape.** The break changes how the speaker builds an argument. Flag and ask before applying.
- **Category C — Theological weight.** Break placement carries a doctrinal implication. Flag and discuss before touching.

**Mechanical-rule authority.** When a settled mechanical rule's UD signature fires unambiguously and the rule's heuristics resolve without ambiguity, the change is **Category A by default**. The canon IS the approval — no per-item flagging is required. Bump to Category B only when rhetorical weight is independently implicated (e.g., breaking a covenant formula, altering a prophetic rhythm). Bump to Category C only when theological weight is independently implicated. Default-bumping mechanical hits to B out of caution is a failure mode — it inverts the canon's authority and creates unnecessary friction.

**Default:** when uncertain between mechanical and non-mechanical, treat as mechanical if the UD signature is clean. When uncertain between A and B/C on editorial/rhetorical grounds, treat as Category B. A false Category A on rhetorical grounds (applying a change that warranted discussion) costs more than a false Category B (flagging something straightforward). A false Category B on mechanical grounds (flagging a clean rule hit for review) costs Stan's time and compounds across sessions.

**Scope/precedence/closed-list diagnostic.** Canon additions that include ANY of the following are **Category B by default**, regardless of how they are framed in the commit message:
- A scope claim (*"rule X applies to / does not apply to Y"*)
- A precedence claim (*"rule A trumps rule B"*, *"X wins over Y when both fire"*)
- A closed-list extension (adding a verb class, adding a named category, adding a SCOPE-exclusion item)
- A named-category carve-out (introducing a new gating category, even if cross-referenced to an existing rule)

This diagnostic catches the failure mode where a canon change is self-framed as "documenting existing practice" or "scope clarification" but substantively asserts a new judgment. Examples of the misclassification this prevents: Gap 1-A (compound-list × M1 precedence, initially framed as Low-tier "documenting practice" — actually Category B scope-claim); Rule 17 topic-PP extension (initially framed as "refinement" — actually Category B closed-list expansion). §7 Change Protocol's mandatory-audit trigger list operationalizes this diagnostic for commit-time discipline.

---

# Part II — Operating Rules (for robots applying the method)

## 3. Quick-Reference Rule Table

| # | Name | Type | Trigger (UD signature) | Action |
|---|------|------|------------------------|--------|
| 1 | AICTP formula integrity | Mechanical | `expl(came, it)` + token sequence *"And it came to pass"* | Keep whole; line ends at or after "that" per Rule 16 |
| 5 | Equivalence "or" as appositive | Mechanical | `cc(conj, or)` where *that is to say* could substitute | MERGE |
| 6 | Causal clauses break | Mechanical | `advcl` with `mark` = *because* | BREAK before *because* |
| 7 | Purpose clauses break | Mechanical | `advcl` with `mark` = *that* + `aux` = MODAL (*may, might, shall, should*) | BREAK before *that* |
| 9 | Line-final CCONJ forbidden | **Layer 1** → [ud-taxonomy §7](../../data/syntax-reference/ud-taxonomy.md) | Line-final token POS = `CCONJ` | Move to lead next line |
| 10 | V + DO split forbidden | Mechanical | Line-final `VERB` with `obj` on following line (bare NP continuation) | MERGE |
| 11 | Line-final DET (article) forbidden | **Layer 1** → [ud-taxonomy §7](../../data/syntax-reference/ud-taxonomy.md) | Line-final token POS = `DET` | MERGE forward |
| 12 | Line-final AUX forbidden | **Layer 1** → [ud-taxonomy §7](../../data/syntax-reference/ud-taxonomy.md) | Line-final `AUX` with `aux` relation to VERB on next line | MERGE forward |
| 13a | Line-final ADP (preposition) forbidden | **Layer 1** → [ud-taxonomy §7](../../data/syntax-reference/ud-taxonomy.md) | Line-final POS = `ADP` or `case` relation pending | MERGE forward (exceptions: phrasal-verb particles, stranded prepositions in relatives) |
| 15 | Vocative indivisible | Mechanical | Multi-word vocative phrase (INTJ *O* + NOUN chain, tagged `vocative`) | Keep whole |
| 16 | AICTP dangling "that" | Mechanical | *that* after AICTP would be line-final | BREAK before *that* |
| 17 | Complement integrity | Mechanical | `ccomp(V, clause)` with `mark(clause, that)` where V ∈ {causative, aspectual, speech-indirect, cognition, volition, FEF} | MERGE across boundary |
| 18 | Fixed idiom integrity | Mechanical | Token sequence matches fixed-idiom list | Never break inside |
| 19 | Relative clauses — cataphoric vs anaphoric | Mechanical + judgment | `acl:relcl(head, clause)` — judgment on information-advancement | Cataphoric → BREAK; anaphoric → MERGE |
| 20 | No-anchor rule | Mechanical | Line lacks any of: finite VERB, infinitive, predicative participle, independently predicated substantive | Line is invalid; merge or restructure |
| 21 | Participial absolute integrity | Mechanical | Subject-bearing participial clause (form: X having Y-ed / X being Y) | Earns own line |
| 22 | Divine title appositives | Editorial | Appositional divine-title NP after a named referent | INTRODUCING (formal anchor present) → STACK SPLIT; REFERENCING (default) → MERGE |
| 23 | Date colophon integrity | Mechanical | Token sequence *"in the Nth year of the reign of the judges"* | Keep whole |
| 26 | Adjective + "that" complement stays | Mechanical | `ccomp` of `ADJ` predicate with `mark` = *that* | MERGE |
| 27 *(proposed)* | "Insomuch that" binding | Mechanical + judgment | `advcl` with `mark` = *insomuch that* | Default SPLIT; MERGE only if result ≤8 words AND subject-continuity AND no camera-angle shift |
| 28 *(proposed)* | Speech-act announcement after frame | Mechanical | Main-clause speech VERB with `nsubj` separated from direct discourse by intervening `advcl` | Speech-tag earns its own line |
| EP-1 | "According to" manner vs. source | Editorial | PP headed by *according to* | Manner (HOW) → MERGE; source/authority (BY WHAT) → SPLIT |
| EP-3 | Inverted predicate | Editorial | Predicate-fronted copular construction | Earns own line |
| EP-4 | Title/role + domain | Editorial | Title-NP + headed `nmod` domain PP | Keep together |
| EP-5 | Virtue/vice lists | Editorial | Stacked moral qualities | Examine for parallel; apply pattern if detected; else merge |

**Guidelines** (useful tendencies, not strict rules): line length as signal; vocative splitting nuances; fronted adverbials; line reordering (rare). (Compound list break signals are now a named sub-rule under structural justification 1 — no longer in this guideline list.)

---

## 3.5. Precedence Hierarchy

When two or more rules fire on the same v2-mine location, the following precedence resolves them. Higher tiers win over lower tiers; within a tier, more specific rules win over more general ones. Detectors should encode this hierarchy by filtering candidates that match higher-tier rules out of lower-tier buckets.

**TIER 0 — Input filters** (operate before split/merge analysis)
- Punctuation is not a break signal (see §1)
- Versification is not a break signal (see §1)
- **R28 Authorial Asymmetry** — preserves asymmetric series before any uniformity sweep (see §1)
- **Parallel-List Uniformity** — multi-verse list with shared frame settles uniform treatment (see §1; e.g., Moroni 10:8-17 spiritual gifts)

**TIER 1 — Layer 1 syntax vetoes** (generic English; hard-fatal)
- **R9** Line-final CCONJ forbidden — REQUIRED-MERGE
- **R11** Line-final DET (article) forbidden — REQUIRED-MERGE
- **R12** Line-final AUX seeking main verb forbidden (simple case) — REQUIRED-MERGE
- **R13a** Line-final ADP seeking object forbidden — REQUIRED-MERGE
- **R10** V + DO bond — REQUIRED-MERGE

Layer 1 violations are MALFORMED, not editorial. Always wins. *Note:* R12 simple-case is the within-predication AUX+verb bond; it does NOT apply BETWEEN coordinate members of a polysyndetic chain that share AUX (see Tier 5 / Justification 1 below; Helaman 3:16 precedent).

**TIER 2 — Indivisibility / formula / vocative**
- **R1** AICTP formula integrity (most specific — closed token sequence)
- **R16** AICTP dangling "that" (couples to R1)
- **R23** Date colophon integrity
- **R18** Fixed idiom integrity
- **R15** Vocative indivisibility (wins over R22 inside vocative environment; wins over R17 when vocative on matrix line)

Lexicalized closed-list units. Triggers leave no room for proposition-level analysis inside the frame.

**TIER 3 — Complement integrity**
- **R26** Adjective + that complement (most specific — direct ADJ head)
  - Wins over R7 when matrix lemma ∈ {expedient, needful, necessary, possible, desirous, impossible, wisdom, meet}
- **R17** Verb + complement (six closed verb classes + topic-PP extension)
  - Yields to R26 when ADJ is the direct head; wins over R19 when both apply
  - Yields to **J3 (speech-act announcement)** when the ccomp body is ≥8 word tokens under a short speech-tag (see §5 R17 speech-indirect long-complement exception)
  - Yields to **J1 (formally-marked parallel that-series)** at N≥3 — coordinate that-clauses under one matrix verb fall under Justification 1 stacking
  - Other named exceptions (§5 R17): direct discourse, AICTP-that, purpose-that, divine recitativum

Matrix predication is grammatically incomplete without complement.

**TIER 4 — Default-merge precedence over split-triggers (M-overrides)**
- **M1** Gorgianic Bonded Pair (N=2 synonymy/cognate/hendiadys merge)
  - True synonymy only; sequential narrative bonding is NOT M1 (see §1 M1 SCOPE)
- **M2** = R17 (alias)
- **M3** Bare-Governor Indivisibility (extension: bare trailing participials)
- **M4** Fragmented atomic thought-unit
  - Does NOT fire on members of justification-1 series at N≥3 or justification-5 substantive adjuncts (§1 M4 SCOPE)

Split-trigger fires but resulting fragment fails atomic-thought.

**TIER 5 — Split-triggers (generative principle + structural justifications)**
- **Generative principle:** each proposition splits by default (see §1)
- **Justification 1:** formally-marked parallel series — at N≥3 wins over Tier 4 merge-overrides (Helaman 3:16 cliff). At N=2, see Tier 6 N=2 adjudication.
  - Compound-list break-signals govern object-lists
  - Polysyndetic verb-chains: each member earns own beat, even with shared AUX (R12 protects WITHIN one predication, not BETWEEN coordinate members)
- **Justification 2:** portrait accumulation
- **Justification 3:** speech-act announcement (incl. *saith the Lord* parenthetical)
- **Justification 4:** classical commata
- **Justification 5:** substantive adjunct as own focus
- **R6** Causal "because" — yields to "because of NP" PP-construction (advcl head must be VERB or ADJ); fronted-because routes to REVIEW
- **R7** Purpose finite "that + MODAL"
  - Yields to **R27** when compound mark is *insomuch that*
  - Yields to **R26** when matrix is ADJ in the {expedient, needful, necessary, possible, desirous, impossible, wisdom, meet} class
  - Yields to **result-clause reading** when *so/such* (as advmod or amod) scopes the matrix's modifier AND the *that*-clause is in advcl-result attachment (consecutive consequence). Surface presence of *so/such* alone is not sufficient — *such great X (NP) that ye may Y* is genuine R7 purpose.
  - Yields to **Parallel-List Uniformity** within multi-verse lists (e.g., Moroni 10:8-17)
- **R19** Cataphoric vs anaphoric "that"/which
  - Cataphoric STRONG-SPLIT requires PRON or DET head (generic forward-pointer)
  - PROPN head → STRONG-MERGE (anaphoric, named referent)
  - NOUN head → REVIEW (ambiguous without discourse context)
  - Yields to R17 when both apply
- **R21** Participial absolute (subject-bearing)
- **R22** Divine title appositive INTRODUCING (yields to R15 in vocative env)
- **R27** *Insomuch that* consecutive (3-condition test for merge: rc≤8 words, subject continuity, no camera shift)
- **R28** Speech-act announcement after intervening frame

These GENERATE breaks. Each yields to higher tiers when those fire.

**TIER 6 — N=2 adjudication** (cross-cuts Tier 4 vs Tier 5)

When a coordinate construction has exactly 2 members, apply the M1 verb-synonymy paraphrase test:
- Synonymous / cognate / intensification → merge (Tier 4 wins)
- Distinct non-synonymous → split (Tier 5 wins)

Applies to: M1 pairs, R12 N=2 compound-verb under shared AUX, R17 N=2 that-series.
Does NOT apply to: appositives (R22, R15+appositive).

At **N≥3** the test is moot — Justification 1 wins over merge-rules unconditionally (Helaman 3:16 cliff).

**TIER 7 — Editorial tiebreakers** (post-hoc only; fire after Tiers 1-6 settle)
- **EP-1** *according to* manner vs source
- **EP-3** Inverted predicate
- **EP-4** Title + domain
- **EP-5** Virtue/vice lists
- Single-image / camera-angle diagnostic (image-test)

**TIER 8 — Structural fallback**
- **R20** No-anchor: every line must carry an anchor; failures resolve via merge or restructure
  - Exemptions: single-line verses, speech-intro prefixes, sentence-connectives, lines passing any structural justification (J1-J5)

Floor-check after all generative/subtractive rules have fired.

### 3.5.1 Sub-hierarchy: the "that"-cluster

The "that" complementizer is the most-collided token in the canon. Six rules can fire on a "that"-clause; precedence is most-specific-first:

1. **R1 / R16** AICTP "that" — token sequence "And it came to pass that"
2. **R26** ADJ + that complement — head_upos == ADJ, or head copular+ADJ
3. **R17** VERB + that — head_upos == VERB, lemma ∈ governor classes
4. **R27** Insomuch that — advcl with mark "insomuch that" (multi-token MWE)
5. **R7** Purpose advcl + modal — advcl with mark "that" + modal aux
6. **R19** Relative "that"/which — acl:relcl

Detectors should test in this order; the first match wins.

### 3.5.2 N=2 vs N=3+ cliff

The N=2 Adjudication Principle and the N≥3 Justification-1 cliff (Helaman 3:16 precedent) are load-bearing across M1, R12, R17, and the polysyndetic-verb-chain detector. Any rule operating on a coordinate construction must distinguish the two cases:

- **N=2:** apply the M1 synonymy test (Tier 6 above)
- **N≥3:** Justification 1 wins; each member earns its own beat regardless of shared AUX

---

## 4. Layer 1 Reference Pointers

Data tables that belong to generic English grammar live in the Layer 1 reference, not here. This section holds the cross-references.

### 4.1 The "That"-Taxonomy

Authoritative table: [`data/syntax-reference/ud-taxonomy.md`](../../data/syntax-reference/ud-taxonomy.md) **Part 4 — The "That"-Taxonomy in UD Terms**. Maps each grammatical type of *that* to its UD signature, CGEL vocabulary, and the rule that fires.

**Quick orientation:**
- Complementizer (verb/adj/noun complement, extraposed subject) → Rules 17, 26, 19, 1/16/18
- Relative pronoun → Rule 19 (content-dependent)
- Adverbial subordinator (purpose) → Rule 7 (BREAK before *that*)
- Adverbial subordinator (result, *insomuch that*) → Rule 27 proposed (conditional)
- Demonstrative → not clause-introducing, no colometric rule applies

### 4.2 Line-Final POS Prohibitions

See [`data/syntax-reference/ud-taxonomy.md`](../../data/syntax-reference/ud-taxonomy.md) **§7 Break Legality Reference** — rows for `CCONJ` (Rule 9), `DET` (Rule 11), `AUX` (Rule 12), `ADP` (Rule 13a), all marked `REQUIRED-MERGE` per generic English grammar. Validator: `validators/syntax/validate_line_final_tokens.py`.

---

*BofM-specific data (Rule 17 verb classes, Rule 18 fixed-idiom list, Rule 19 which-clause tree) now lives inline in §5 with the rules themselves. The five structural justifications live in §1 "The Five Structural Justifications (Closed List)" as core methodology, not reference data.*

---

## 5. The Rules (Detail)

*Each rule below follows the operational template specified in [`atu-method/docs/rule-template.md`](../../atu-method/docs/rule-template.md) — MISRA-style with RFC 2119 normative keywords. Rationale, grammatical-grounding citations, audit-trail narratives, and corpus-empirics histories are extracted to the per-rule scholarship companion in [`atu-method/scholarship/bofm/`](../../atu-method/scholarship/bofm/) (cross-referenced from each rule's Implementation block).*

<!-- ===== R1 ===== -->
### R1: AICTP Formula Integrity

**Status:** Active
**Category:** A (Mechanical, mandatory)
**Decidability:** Surface-pattern
**Layer:** 3

**Rule.** The fixed extraposition formula *And it came to pass* (and its closed-list variants, §AICTP-Variants) MUST be kept whole on a single v2-mine line. No line break MAY occur internal to the formula's token sequence. The formula's trailing subordinator *that* — when present — couples to R16 (dangling-*that*), which governs the break placement at the formula's right edge. R1 governs only the formula-internal span.

**UD signature.**
~~~yaml
trigger:
  surface_pattern: AICTP_VARIANTS
  ud_anchor: { relation: expl, head: { lemma: come }, dependent: { lemma: it } }
action: KEEP_WHOLE
~~~

**Closed lists** (machine-readable).
~~~yaml
AICTP_VARIANTS:
  - "And it came to pass"
  - "And now it came to pass"
  - "And it shall come to pass"
~~~

**Scope.** The formula's token-sequence span, beginning at *And* (or *And now*) and ending at *pass*. Trailing-*that* boundary handling is delegated to R16. Layer 3 editorial rule; supersedes Layer 1 mid-phrase prohibitions only at the formula-internal level (no Layer 1 break could occur inside the formula because the formula contains no eligible split-point — but R1 codifies the indivisibility for editorial sweep purposes).

**Exclusions (closed list — each cites dominating rule).**
1. Trailing *that* placement (whether *that* line-leads vs. line-trails) → R16 (couples to R1; R16 forces break before *that*).
2. AICTP followed by a substantive temporal/locative/causal slot-filler PP earning its own line → J5 (substantive adjunct as own focus; AICTP integrity is preserved, and the slot-filler simply follows on its own line).

**Precedence.** §3.5 Tier 1 (most specific — closed token sequence). Wins over all subtractive vetoes and merge-overrides at the formula-internal level. Couples to R16 at the formula's right edge.

**Examples.**

- *Compliant:* "And it came to pass that in the seventh year of the reign of the judges, / there were about three thousand five hundred souls..." (formula whole on one line; trailing *that* leads its content per R16)
- *Compliant (variant):* "And now it came to pass that..." (variant form preserved whole)
- *Compliant (J5 slot-filler):* "And it came to pass that Moroni did arrive with his army at the land of Bountiful, / in the latter end of the twenty and seventh year of the reign of the judges over the people of Nephi." (Alma 52:18; AICTP-that whole on line 1, substantive temporal PP own-lines per J5)
- *Non-compliant:* "And it came to / pass that..." (formula severed)
- *Non-compliant:* "And it came / to pass that..." (formula severed)
- *Excluded by R16:* "And it came to pass / that in the seventh year..." (break before *that* is R16's domain, not an R1 violation; R1 governs only the formula-internal span up through *pass*)

**Implementation.**

- Validator: [`validators/colometry/validate_rule_01_ud.py`](../../../../readers-bofm/validators/colometry/validate_rule_01_ud.py)
- Applier: (none — surface-pattern keep-whole; corpus is hand-authored at this granularity, validator reports violations)
- Closed-list definitions: §AICTP-Variants (in BoFM canon, supplementary section)
- Audit trail: `readers-bofm/private/audit-trail/R1.md` (to be populated during BoFM canon migration)
- Scholarship: [`atu-method/scholarship/bofm/R1.md`](atu-method/scholarship/bofm/R1.md)

<!-- ===== R5 ===== -->
### R5: Equivalence "Or" as Appositive

**Status:** Active
**Category:** B (Editorial, judgment-required) — the substitution test is the discriminator and is not mechanically decidable for the general case; the validator routes corpus-attested patterns to STRONG-MERGE-CANDIDATE vs REVIEW-REQUIRED on a UD-detectable heuristic.
**Decidability:** UD-pattern for the STRONG branch (same-UPOS + short-conjunct heuristic); Discourse-context-needed for the REVIEW branch.
**Layer:** 3

**Rule.** A coordinating *or* connecting two semantically equivalent reformulations (the second restating the first in other words) is appositive — NOT a disjunction — and the two conjuncts together with the linking *or* MUST occupy a single v2-mine line. When the substitution test (replace *or* with *that is to say* or *in other words*; meaning preserved) succeeds, the construction is equivalence-*or* and MUST merge. When the substitution test fails, the *or* marks a genuine disjunction (two distinct alternatives) and the existing line treatment MUST be preserved (the rule does not fire). Cases where the substitution test is not mechanically decidable from UD signature alone MUST be routed to REVIEW-REQUIRED; the applier MUST NOT auto-merge REVIEW-bucket findings.

**UD signature.**
```yaml
trigger_equivalence_or:
  relation: cc
  form: or                     # surface form (case-insensitive); cc token's form
  attaches_to: second_conjunct_head
  second_conjunct_head:
    deprel: conj
    head: first_conjunct
  conjuncts_on_different_lines: true   # rule only fires when split
action: REVIEW                          # bucketed below by heuristic

heuristic_strong_merge:
  same_upos: true              # first_conjunct.upos == second_conjunct.upos
  any_of:
    - both_conjuncts_short_le_4_content_tokens
    - second_conjunct_short_le_4_content_tokens   # asymmetric-short second = canonical BoFM signal
  action: MERGE_COORDINATE_MEMBERS    # STRONG-MERGE-CANDIDATE bucket; auto-apply NOT authorized — see Category B

heuristic_review_required:
  conditions: cross-UPOS OR both_conjuncts_long
  action: REVIEW                # REVIEW-REQUIRED bucket; needs substitution-test editorial judgment
```

**Closed lists** (machine-readable).
```yaml
SHORT_CONJUNCT_THRESHOLD: 4    # non-PUNCT tokens in the conjunct's UD subtree

SUBSTITUTION_PROBES:           # used by human reviewer applying the substitution test
  - "that is to say"
  - "in other words"

# The rule has no closed-list lemma inventory; the conj-or surface form is the trigger.
# Bucketing into STRONG vs REVIEW is driven entirely by the structural heuristic.
```

**Scope.** Applies to a coordinating *or* tagged with UD `cc` whose head is a `conj` token, when the two conjuncts (the first being the head of the second's `conj` relation, the second being the head of the `cc` attachment) currently sit on different v2-mine lines. The rule governs MERGE candidacy only — when conjuncts already share a line the rule does not fire. The rule operates over the second-conjunct head's UD subtree (not its surface span) for the conjunct-size measurement; the SHORT_CONJUNCT_THRESHOLD counts non-PUNCT tokens.

**Exclusions (closed list — each cites dominating rule).**

1. Genuine disjunction (*or* marks two distinct alternatives, not a restatement; substitution test fails) → out of scope; existing line treatment preserved. Distinguished from equivalence-*or* by the substitution-test diagnostic in the rule statement.
2. Cross-UPOS conjuncts (e.g., NOUN-or-VERB, ADJ-or-PROPN) → REVIEW-REQUIRED bucket; cross-category coordination is rarely equivalence and almost always requires editorial judgment.
3. Both conjuncts long (each > `SHORT_CONJUNCT_THRESHOLD` content tokens) → REVIEW-REQUIRED bucket; long equivalence pairs are rare in BoFM and the substitution test cannot be confirmed from UD signature alone.
4. *Or*-coordinations functioning as compound objects under a shared verb or preposition (J1 compound-list members) → §1.4 J1 governs the head-and-object analysis; if the compound list reads as J1 series, R5 yields. The N=3+ cliff (§1.9) does not engage R5 because R5 fires only on N=2 *or*-pairs.
5. *Or*-coordinations inside a fixed idiom or formula → R18 governs.
6. *Or*-coordinations whose first conjunct ends at a Layer-1-prohibited line-final position (CCONJ, DET, AUX, ADP) → R9 / R11 / R12 / R13a Layer-1 vetoes win; the merge happens for the higher-tier reason and R5 is moot.

**Precedence.** §3.5 Tier 4 (default-merge precedence over split-triggers, M-override family). Yields to all Tier 1 (Layer 1) syntactic vetoes that would merge for an independent reason. Yields to Tier 2 (R18 fixed idiom, R15 vocative) inside their respective frames. Within Tier 4, R5 is parallel to M1 but operates on a different coordinator (*or* rather than *and*) and a different semantic relation (appositive equivalence rather than gorgianic bonded pair); the two rules do not collide on the same N=2 pair.

*Note:* §3.5 currently lists Tier 4 by M-override IDs (M1–M4) and does not enumerate R5; the precedence-consistency check during the BoFM canon migration will reconcile R5's tier placement. R5's operational behavior is structurally a Tier 4 merge-override (an apparent split-trigger — coordination on *or* — is overridden when the conjuncts are equivalence-related and the second restates the first).

**Examples.**

- *Compliant (STRONG-MERGE-CANDIDATE — same-UPOS, asymmetric-short second conjunct):* "and they have a part in the first resurrection, or have eternal life, being redeemed by the Lord" (Mosiah 15:24) — *or have eternal life* restates *have a part in the first resurrection*; substitution test passes (*that is to say, have eternal life*).
- *Compliant (STRONG-MERGE-CANDIDATE — same-UPOS, both short):* "the rod of iron, or the word of God" — *or the word of God* names the rod's referent; substitution test passes.
- *Non-compliant (R5 violation — equivalence-or split):* "and they have a part in the first resurrection, / or have eternal life" (the equivalence reformulation severed from its first conjunct).
- *Excluded — genuine disjunction:* "that he may live or die" — *or* marks two alternatives; substitution (*that is to say, die*) fails; R5 does not fire; existing line treatment preserved.
- *Excluded — cross-UPOS, routed to REVIEW:* a NOUN-or-VERB coordination requires editorial judgment of whether one names the other; UD signature alone cannot resolve.
- *Excluded — J1 compound-object reading:* an *or*-coordination functioning as a compound object under a shared verb falls under J1 compound-list-break-signals; R5 yields.

**Implementation.**

- Validator: [`validators/colometry/validate_rule_05_ud.py`](../../../../readers-bofm/validators/colometry/validate_rule_05_ud.py)
- Applier: not yet implemented (Category B status — STRONG-MERGE-CANDIDATE bucket awaits per-instance editorial confirmation via the substitution test before merge is applied)
- Closed-list / threshold definitions: `SHORT_CONJUNCT_THRESHOLD = 4` in validator source
- Bucketing logic: STRONG = same-UPOS ∧ (both-short ∨ second-short); REVIEW = otherwise
- Audit trail: `readers-bofm/private/audit-trail/R5.md` (to be populated during BoFM canon migration)
- Scholarship: [`atu-method/scholarship/bofm/R5.md`](atu-method/scholarship/bofm/R5.md)

<!-- ===== R6 ===== -->
### R6: Causal Clauses Break

**Status:** Active
**Category:** A (Mechanical, mandatory)
**Decidability:** UD-pattern
**Layer:** 3

**Rule.** A finite causal clause MUST be split from its matrix when the clause is in `advcl` attachment to a matrix VERB or ADJ head, is marked by the subordinator *because*, and the *because*-clause is NOT inside a clausal complement (`ccomp`) under a Rule-17 governor. The break MUST be inserted before the *because* mark. Non-clausal *because of* + NP prepositional constructions are NOT in scope and MUST NOT be split by this rule. Fronted-*because* (causal clause preceding the matrix) MUST be routed to REVIEW rather than mechanically split.

**UD signature.**
```yaml
trigger:
  relation: advcl
  head: { upos_in: [VERB, ADJ] }
  mark: { lemma: because }
  position: trailing   # because-clause follows the matrix
action: SPLIT_BEFORE_MARK
```

**Closed lists** (machine-readable).
```yaml
CAUSAL_MARK_LEMMAS:
  - because

# Rule 17 governor classes (defined at canon §Verb-Classes-R17).
# When a because-clause sits inside a ccomp under any verb in this set,
# R6 yields to R17's complement-integrity mandate.
R17_GOVERNOR_CLASSES:
  - causative      # cause, suffer, permit, command, grant
  - aspectual      # begin, cease, continue
  - speech         # say, speak, declare, testify, swear, proclaim, tell, ...
  - cognition      # know, believe, perceive, remember, understand, suppose, ...
  - volition       # wish, desire, hope, long, trust, pray, seek
  - FEF            # it was their lot to, it is expedient to
```

**Scope.** Finite *because*-clauses in trailing `advcl` attachment to a VERB or ADJ matrix head. The `advcl` head MUST be a VERB or ADJ; constructions where *because* heads a PP-equivalent (*"because of NP"*) fall outside this signature and are out of scope.

**Exclusions (closed list — each cites dominating rule).**

1. *Because of NP* PP-construction — *because* heads a prepositional construction (*"because of their wickedness"*); the `advcl` head is not a finite VERB/ADJ and no embedded subject + finite verb is present → out of scope (no R6 split)
2. Fronted-*because*: causal clause precedes the matrix predication (*"Because they had hardened their hearts, the Lord did smite them"*) → REVIEW-REQUIRED (break direction differs from trailing-because; not auto-applied)
3. *Because*-clause inside `ccomp` under an R17 governor (e.g., *"Do not suppose, because it has been spoken concerning restoration, that ye shall be restored..."* — Alma 41:10): the matrix + ccomp complement-integrity bond wins; splitting on the embedded causal would sever the R17 matrix from its *that*-complement → R17 (yields per §3.5 Tier 3 precedence over Tier 5)
4. Short-line context where the combined line passes the atomic-thought test → MAY merge under M4 (fragmented atomic thought-unit)

*Note on Exclusion 3 — Rule 17 precedence guard.* The check is structural: when the causal `advcl` attaches inside an enclosing `ccomp` whose `ccomp` head lemma is in `R17_GOVERNOR_CLASSES`, R17's complement-integrity bond between the R17 governor and its *that*-complement takes priority. Applying R6 inside such a configuration produces a Rule-17 violation (matrix governor severed from its *that*-complement across the embedded because-clause). The detector MUST traverse the parent chain of the *because*-advcl to verify no enclosing R17-governed ccomp before firing.

**Precedence.** §3.5 Tier 5. Yields to R17 (when the *because*-clause is inside a `ccomp` under an R17-class governor), to §1.12 Parallel-List Uniformity (within multi-verse parallel lists), and to M4 (short-line atomic-thought merge).

**Examples.**

- *Compliant (SPLIT):* "they did murmur against their father / because he had brought them out of the land"
- *Compliant (out of scope — because-of-NP PP, no split):* "because of their iniquities the Lord did chasten them" (PP-construction; no finite embedded clause)
- *Non-compliant (R6 violation — trailing finite because-clause not split):* "they did murmur against their father because he had brought them out of the land" (one line — matrix and causal frame not separated)
- *Excluded by R17 (no R6 split):* "Do not suppose, / because it has been spoken concerning restoration, / that ye shall be restored..." would violate R17 by severing *suppose* from its *that*-complement; correct treatment merges per R17 → "Do not suppose, because it has been spoken concerning restoration, that ye shall be restored..." (Alma 41:10; R6 yields)
- *Excluded by REVIEW (fronted-because):* "Because they had hardened their hearts, ..." — break direction differs; routed to REVIEW

**Implementation.**

- Validator: [`validators/colometry/validate_rule_06_ud.py`](../../../../readers-bofm/validators/colometry/validate_rule_06_ud.py)
- Applier: [`validators/apply_rule_06_ud.py`](../../../../readers-bofm/validators/apply_rule_06_ud.py)
- Closed-list definitions: in validator source (`CAUSAL_MARK_LEMMAS`, R17 governor classes per `validate_rule_17_ud.py`)
- Audit trail: `readers-bofm/private/audit-trail/R6.md` (to be populated during BoFM canon migration)
- Scholarship: [`atu-method/scholarship/bofm/R6.md`](atu-method/scholarship/bofm/R6.md)

<!-- ===== R7 ===== -->
### R7: Purpose Clauses Break

**Status:** Active
**Category:** A (Mechanical, mandatory)
**Decidability:** UD-pattern
**Layer:** 3

**Rule.** A finite purpose clause MUST be split from its matrix when the clause is in `advcl` attachment to a matrix VERB, is marked by the simple subordinator *that*, and contains a modal auxiliary (`may`, `might`, `shall`, `should`, `will`, `would`, `can`, `could`, `must`). The break MUST be inserted before the *that* mark. Non-finite infinitival purpose adjuncts (*to + VERB + complement*, without subject or modal) are NOT in scope and MUST NOT be split from their matrix motion verb by this rule.

**UD signature.**
```yaml
trigger:
  relation: advcl
  head: { upos: VERB }
  mark: { lemma: that }
  aux: { lemma_in: MODAL_AUX_LEMMAS }
action: SPLIT_BEFORE_MARK
```

**Closed lists** (machine-readable).
```yaml
MODAL_AUX_LEMMAS:
  - may
  - might
  - shall
  - should
  - will
  - would
  - can
  - could
  - must

RULE_26_HEAD_LEMMAS:
  - expedient
  - needful
  - necessary
  - wisdom        # NOUN-as-predicate
  - possible
  - desirous
  - impossible
  - better
  - well
  - requisite

RESULT_DEGREE_MARKERS:
  - so
  - such
```

**Scope.** Finite *that* + MODAL purpose clauses with VERB matrix head. Non-finite infinitival purpose adjuncts (bare *to + VERB*) are out of scope and merge with their matrix motion verb. Matrix ADJ or NOUN-as-predicate heads are out of scope (route to R26).

**Exclusions (closed list — each cites dominating rule).**

1. Compound subordinator *insomuch that* — the mark is the compound, not simple *that*; consecutive-result semantics → R27
2. Matrix head lemma in `RULE_26_HEAD_LEMMAS` (ADJ predicate or NOUN-as-predicate *wisdom*) — the LLM annotation is likely mistagged; structural truth is ccomp/acl complement-integrity → R26
3. Consecutive-result construction: matrix's modifier (ADJ or ADV) carries `advmod` or `amod` dependent in `RESULT_DEGREE_MARKERS`, AND the *that*-clause is in `advcl` attachment as the consequence (*"so numerous that they could not be numbered"*, *"such great force that the city was destroyed"*) — result-clause reading governs; no R7 split
4. Idiomatic *even so that* result connector — pre-mark token sequence *even ... so* in the preceding 3 tokens → result-clause reading
5. Multi-verse list with parallel-list uniformity scope (e.g., Moroni 10:8-17) → §1.12 Parallel-List Uniformity wins
6. Short-line context where the combined line passes the atomic-thought test → MAY merge under M4 (fragmented atomic thought-unit)

*Note on Exclusion 3 discriminator:* Surface presence of *so/such* alone is not sufficient. The discriminator is the UD attachment. *Such great X (NP) that ye may Y* — where *such* attaches as `det` to the head noun, not as `advmod`/`amod` scoping a modifier — is genuine R7 purpose territory, not consecutive-result.

**Precedence.** §3.5 Tier 5. Yields to R27 (insomuch-that compound mark), R26 (matrix ADJ/NOUN-as-predicate complement), result-clause reading (so/such as advmod/amod scoping matrix modifier), and §1.12 Parallel-List Uniformity (multi-verse parallel lists).

**Examples.**

- *Compliant (SPLIT):* "he went forth among the people / that he might preach the word of God unto them"
- *Compliant (non-finite infinitive merges, NOT R7):* "he has gone to the land of Ishmael, to teach the people of Lamoni" (Alma 22:4)
- *Non-compliant (R7 violation — finite purpose clause not split):* "he went forth among the people that he might preach the word of God unto them" (one line — matrix and purpose-frame not separated)
- *Excluded by R27:* "And he did minister unto them, / insomuch that his whole household were converted unto the Lord" (Alma 22:23) — compound subordinator *insomuch that*; R27's 3-condition test governs
- *Excluded by R26:* "if it were possible that our first parents..." — matrix is ADJ `possible` in RULE_26_HEAD_LEMMAS; structural truth is ccomp complement-integrity → MERGE
- *Excluded by result-clause reading:* "so numerous that they could not be numbered" — *so* scopes *numerous* as `advmod`; consecutive consequence, not purpose

**Implementation.**

- Validator: [`validators/colometry/validate_rule_07_ud.py`](../../../../readers-bofm/validators/colometry/validate_rule_07_ud.py)
- Applier: [`validators/apply_rule_07_ud.py`](../../../../readers-bofm/validators/apply_rule_07_ud.py)
- Closed-list definitions: in validator source (`MODAL_AUX_LEMMAS`, `RULE_26_HEAD_LEMMAS`, `RESULT_DEGREE_MARKERS`)
- Audit trail: `readers-bofm/private/audit-trail/R7.md` (to be populated during BoFM canon migration)
- Scholarship: [`atu-method/scholarship/bofm/R7.md`](atu-method/scholarship/bofm/R7.md)

<!-- ===== R9 ===== -->
### R9: Never End a Line on a Conjunction

**Status:** Active
**Category:** A (Mechanical, mandatory)
**Decidability:** Surface-pattern (UD-confirmable)
**Layer:** 1 (generic English grammar)

**Rule.** A v2-mine line MUST NOT end on a coordinating conjunction (`CCONJ`). When the line-final token is tagged `CCONJ`, that token MUST be moved to lead the next line.

**UD signature.**
```yaml
trigger:
  line_final_token: { upos: CCONJ }
action: MERGE_FORWARD
```

**Scope.** Generic English-grammatical fact, not a BoFM-specific editorial decision. Applies to every line where the final token's UPOS is `CCONJ`. Coordinating conjunctions (`and`, `or`, `nor`, `but`, `for`, `yet`, `so`) stranded at line end create the expectation of a following member and therefore violate the atomic-thought test.

**Exclusions.**
1. CCONJ within fixed multi-word units → R18 keeps the unit whole; R9 does not fire on conjunctions inside the protected span.
2. CCONJ that is the LAST token of the entire verse with no following line → handled by terminal-position discipline (not R9 territory).

**Precedence.** §3.5 Tier 1 (Layer 1 syntax veto; MALFORMED-class). Wins over all Tier 2+ generative rules at the same location.

**Examples.**
- Compliant: `"the heavens and the earth / and all things therein"` (the `and` leads the new line)
- Non-compliant: `"the heavens and the earth and /\n all things therein"` (line-final `and`; MALFORMED)
- Excluded: `"He died in old age, / having fulfilled all his days,"` (no line-final CCONJ; R9 does not fire)

**Implementation.**
- Layer 1 reference: [`data/syntax-reference/ud-taxonomy.md §7`](../../../../readers-bofm/data/syntax-reference/ud-taxonomy.md) row: *line-final `CCONJ`* → `REQUIRED-MERGE`
- Validator: `validators/syntax/validate_line_final_tokens.py`
- Applier: (none — surface-pattern Layer-1; corpus is hand-authored at this granularity, validator reports MALFORMED on violations)
- Audit trail: `private/audit-trail/R9.md`
- Scholarship: `atu-method/scholarship/bofm/R9.md`

<!-- ===== R10 ===== -->
### R10: Never Split Verb from Direct Object

**Status:** Active
**Category:** A (Mechanical, mandatory)
**Decidability:** UD-pattern
**Layer:** 1

**Rule.** A transitive verb and its direct object MUST appear on the same v2-mine line. When a line ends on a `VERB` whose `obj` relation points to a bare noun-phrase head on the immediately following line, the two lines MUST be merged. Intervening adverbials or prepositional phrases attached to the verb MUST remain with the verb, not the object.

**UD signature.**
```yaml
trigger:
  line_final_token: { upos: VERB }
  next_line_head:
    relation: obj
    head_ref: line_final_token   # the obj dependent of the verb on the prior line
    upos: [NOUN, PROPN, PRON]
    shape: bare_NP               # determiner + noun + optional PP/relative; not a new clause
  excludes:
    - { next_line_shape: complete_clause_with_finite_verb }   # Subject-NP continuation → R20
    - { next_line_shape: relative_clause_on_complete_NP }      # "Which"-clause decision tree / Class P
    - { coordinate_object_series: { n: ">=2", shared_verb: true } }   # J1 compound-list signals govern
action: MERGE_FORWARD
```

**Closed lists** (machine-readable).
```yaml
BARE_NP_SHAPES:
  - determiner + noun
  - determiner + noun + PP
  - determiner + noun + relative_clause
  - bare_noun
  - bare_PROPN
  - bare_PRON
```

**Scope.** Line-final transitive `VERB` whose `obj` dependent heads the next v2-mine line as a bare noun-phrase continuation of the same predication. The rule fires on the verb-object syntactic bond only; it does not govern verb-complement (clausal) bonds (R17 territory) or verb-PP-complement bonds (R17 topic-PP extension territory).

**Exclusions (closed list — each cites dominating rule).**

1. Already-complete clauses followed by a relative clause (next line begins a relative on a complete antecedent NP) → R19 / Class P "Which"-clause decision tree governs
2. Subject-NP continuations with their own predication (next line is a new finite clause whose subject NP appears to be an object of the prior verb but actually heads a new predication) → R20 territory (no-anchor / restructure)
3. Parallel coordinate object series at N≥2 under a shared verb — bare *"and [noun]"* compound objects do NOT individually trigger R10 against the shared verb. The §1.4 J1 compound-list-break-signals sub-rule governs: bare coordinate items MERGE with the shared verb unless one of the four break signals fires (elided-auxiliary + stacked participles; possessive restart; demonstrative; attached relative clause). Per framework §1.9, the N=3+ cliff is scoped to coordinate **predications**, NOT coordinate **objects** under a single shared verb
4. The third (or final) item in a compound object list carrying a trailing PP modifier — when the modifier attaches semantically to the joint object-set, M1 asymmetric-modifier sub-clause (framework §1.5 M1) keeps the modified item bonded with its co-objects; R10 still merges the entire object-set with the shared verb
5. Verb-complement clausal bonds (matrix verb + `ccomp` / `xcomp`) → R17 governs (complement integrity)
6. Verb-PP obligatory-complement bonds (speech-class verbs + topic-PP; experience verbs + *of*-PP) → R17 topic-PP / experience-of-PP extensions govern

**Precedence.** §3.5 Tier 1 (Layer 1 syntax veto). Wins over all Tier 3+ generative rules (R10 violations are MALFORMED, not editorial). Coordinates with R9, R11, R12, R13a as the closed-list Layer 1 mid-phrase prohibitions.

**Examples.**

- *Compliant:* "have you sufficiently retained in remembrance the captivity of your fathers?" (Alma 5:6 — V *retained* + bare DO *the captivity of your fathers* on one line)
- *Compliant (compound object — J1 sub-rule, R10 still binds):* "preach unto them repentance, and redemption, and faith on the Lord" (Mosiah 18:7 — shared verb *preach unto them* binds the three bare *"and [noun]"* objects; no break-signals fire; the third item's trailing PP *on the Lord* attaches to the joint object-set per M1 asymmetric-modifier; one line)
- *Non-compliant (violates R10):* "have you sufficiently retained in remembrance / the captivity of your fathers?" (V severed from bare-NP DO)
- *Excluded by R19 / Class P:* "the brass plates / which Lehi obtained" (next line is a relative clause on a complete antecedent NP, not a bare DO continuation)
- *Excluded by R20:* "[matrix predication ending in V] / [new finite clause whose NP would otherwise look like an object]" (next line carries its own finite predication — R20 territory, not R10)
- *Excluded by R17:* "He caused / that his servants should stand forth" (the next line begins a *that*-clause `ccomp` of the matrix VERB *caused* — complement integrity governs, not V+DO)

**Implementation.**

- Validator: [`validators/colometry/validate_rule_10_ud.py`](../../../../readers-bofm/validators/colometry/validate_rule_10_ud.py) (UD-pattern); [`validators/colometry/validate_rule_10_verb_do_split.py`](../../../../readers-bofm/validators/colometry/validate_rule_10_verb_do_split.py) (surface heuristic)
- Applier: [`validators/apply_rule_10_ud.py`](../../../../readers-bofm/validators/apply_rule_10_ud.py)
- Closed-list definitions: `BARE_NP_SHAPES` in validator source
- Audit trail: `readers-bofm/private/audit-trail/R10.md` (to be populated during BoFM canon migration)
- Scholarship: [`atu-method/scholarship/bofm/R10.md`](atu-method/scholarship/bofm/R10.md)

<!-- ===== R11 ===== -->
### R11: Never End a Line on an Article (Determiner)

**Status:** Active
**Category:** A (Mechanical, mandatory)
**Decidability:** Surface-pattern (UD-confirmable)
**Layer:** 1 (generic English grammar)

**Rule.** A v2-mine line MUST NOT end on a determiner (`DET`). When the line-final token is tagged `DET`, that token MUST be moved to lead the next line (with its head noun phrase).

**UD signature.**
```yaml
trigger:
  line_final_token: { upos: DET }
action: MERGE_FORWARD
```

**Scope.** Generic English-grammatical fact. A determiner alone at line end strands its head noun on the next line, creating an incomplete NP and failing the atomic-thought test at the line boundary.

**Exclusions.**
1. DET within a fixed multi-word unit → R18 keeps the unit whole.
2. Determiner-pronoun uses where the DET stands alone as a referent (rare in BoFM-English) → context-dependent, route to REVIEW.

**Precedence.** §3.5 Tier 1 (Layer 1 syntax veto; MALFORMED-class). Wins over all Tier 2+ generative rules at the same location.

**Examples.**
- Compliant: `"He gathered together / the people of his land"` (DET `the` leads the new line)
- Non-compliant: `"He gathered together the /\n people of his land"` (line-final `the`; MALFORMED)
- Excluded: `"He saw the sun rise"` (no line-final DET; R11 does not fire)

**Implementation.**
- Layer 1 reference: [`data/syntax-reference/ud-taxonomy.md §7`](../../../../readers-bofm/data/syntax-reference/ud-taxonomy.md) row: *line-final `DET`* → `REQUIRED-MERGE`
- Validator: `validators/syntax/validate_line_final_tokens.py`
- Applier: (none — surface-pattern Layer-1)
- Audit trail: `private/audit-trail/R11.md`
- Scholarship: `atu-method/scholarship/bofm/R11.md`

<!-- ===== R12 ===== -->
### R12: Never Split Auxiliary from Main Verb

**Status:** Active
**Category:** A (Mechanical, mandatory)
**Decidability:** UD-pattern
**Layer:** 1 (simple AUX+V profile) / 3 (compound-verb-under-shared-auxiliary extension)

**Rule.** R12 has two operational profiles, both of which MUST be honored.

(a) **Simple AUX+V profile (Layer 1).** A line MUST NOT end on a token whose UPOS is `AUX` when that token has an `aux` relation to a `VERB` head on the following line. The two lines MUST be merged. Equivalently: a finite auxiliary MUST NOT be stranded from its main verb across a line boundary. This profile is generic English grammar and is enforced by the Layer 1 break-legality table.

(b) **Compound-verb-under-shared-auxiliary extension (Layer 3).** When a modal+auxiliary cluster (e.g., *could have*, *would have*, *shall have*, *had*, *hath*, *have been*) scopes via ellipsis over two or more coordinated participles distributed across line boundaries, the line carrying the dangling coordinated participle MUST be merged with the line carrying its shared auxiliary, subject to the N=2 adjudication below. The coordinated participles form one compound predicate under one shared auxiliary; stranding a coordinated participle from its shared auxiliary is forbidden.

**UD signatures.**
```yaml
trigger_simple_aux_v:
  relation: aux
  head: { upos: VERB }                       # main verb on line N+1
  dependent: { upos: AUX, line_position: line_final }   # AUX line-final on line N
action: MERGE_FORWARD

trigger_compound_verb_shared_aux:
  line_N:
    contains: { upos: AUX, lemma_in: MODAL_AUX_R12 }
    line_final: { upos: VERB, verbform_in: [Part, Ger] }   # past or -ing participle
  line_N_plus_1:
    starts_with: { upos: CCONJ, lemma: and }
    next: { upos: VERB, verbform_in: [Part, Ger] }
    contains_no: { dep_in: [nsubj, nsubj:pass] }
    contains_no_finite_verb: true
action: MERGE_FORWARD
```

**Closed lists** (machine-readable).
```yaml
MODAL_AUX_R12:
  modals:
    - may
    - might
    - shall
    - should
    - will
    - would
    - can
    - could
    - must
  perfect_have:
    - have
    - has
    - hath
    - hast
    - had
    - having
  be_aux:
    - is
    - are
    - was
    - were
    - art
    - am
    - be
    - been
    - being
  do_aux:
    - do
    - does
    - doth
    - did
  # Modal+aux clusters that scope as a unit over coordinated participles:
  # e.g. "could have", "would have", "shall have", "might have been"
  scope_clusters:
    - "<modal> have"
    - "<modal> have been"
    - "had"
    - "hath"
    - "have"
```

**Scope.** Profile (a) applies to every line-final `AUX` with an outgoing `aux` relation to a main `VERB` on the following line — independent of corpus register; it is generic English grammar. Profile (b) applies to BoFM-archaic compound-verb constructions where a single modal+auxiliary cluster on line N scopes elliptically across an *and*-coordinated participle on line N+1 that has neither its own subject nor its own finite verb. The dangling-participle line is structurally a coordinated participle, not a coordinate clause.

**Exclusions (closed list — each cites dominating rule).**

1. Line N+1 introduces an overt subject NP (`nsubj` or `nsubj:pass`) ahead of its verb → coordinate clause, not shared-auxiliary ellipsis; profile (b) does NOT fire (governed by J1).
2. Line N+1 contains its own finite verb (modal aux, perfect aux, or finite main verb) → coordinate finite clause; profile (b) does NOT fire (governed by J1).
3. Line N is a verse-header line (`\d+:\d+`) or other non-text line → out of scope.
4. Phrasal-verb particles tagged `compound:prt` are not auxiliaries — line-final particles are governed by Layer 1's compound:prt row, not this rule.
5. Archaic verb forms (*goeth*, *giveth*, *hath* as main lexical verb) misparsed as `AUX` when functioning as full lexical `VERB` — confirm via dependency direction before merging; out of scope when the token is the predication's main verb.

**Precedence.** §3.5 Tier 1 (Layer 1 syntactic veto) for profile (a). §3.5 Tier 4 (merge-overrides) for profile (b), governed by §3.5 Tier 6 N=2 adjudication when exactly two participles share the auxiliary. Wins over J1 at N=2 when the participles satisfy the M1 verb-synonymy test; yields to J1 at N≥3 unconditionally (§3.5.2 cliff). The N≥3 cliff is the same precedent across M1, R12, and R17.

**N=2 sub-rule (coordinated participles under shared auxiliary).** When profile (b) fires on exactly two coordinated participles under one shared modal+auxiliary, apply the §1.9 N=2 Adjudication Principle / M1 verb-synonymy test:

- Synonymous / cognate / intensification variants (*"rose and went"*, *"tried and failed"*, *"came and saw"*) → MERGE.
- Distinct non-synonymous actions, each with its own object or independent predicative force → SPLIT per J1 (each participle is its own atomic beat under the shared auxiliary).

At N≥3 coordinated participles under one shared auxiliary, J1 wins unconditionally (Helaman 3:16 six-verb-cascade precedent).

**Examples.**

- *Compliant — profile (a) MERGE:* "the people which shall / be brought to pass" → "the people which shall be brought to pass" (line-final `shall` with `aux` to following `brought`; merged).
- *Compliant — profile (b) MERGE (N=2, synonymous/cognate, Alma 12:26):* "could have gone forth and partaken of the tree of life" (one line; *could have* scopes over both participles; line 2 of the pre-merge state had no subject and no finite verb).
- *Compliant — profile (b) SPLIT (N=2, distinct non-synonymous, Alma 24:10):* "hath forgiven us of those our many sins and murders which we have committed, / and taken away the guilt from our hearts" (shared *hath* scopes over *forgiven* and *taken away*; the two actions are distinct non-synonymous with distinct objects; each earns its own atomic beat per J1).
- *Compliant — profile (b) SPLIT at N≥3 (Helaman 3:16 cliff):* coordinated participles at N≥3 under one shared auxiliary split into N lines, one per participle.
- *Non-compliant — profile (a) violation:* "could have / gone forth and partaken" (line-final *have* stranded from its participle; merge required).
- *Non-compliant — profile (b) violation:* "could have gone forth / and partaken of the tree of life" (dangling coordinated participle stranded from shared *could have*; subject and finite verb absent from line 2; merge required at N=2 cognate).
- *Excluded by Exclusion 1 (J1 governs):* "could have gone forth / and they partaken of the tree of life" (line N+1 introduces overt subject *they*; coordinate clause, not shared-auxiliary ellipsis).

**Implementation.**

- Validator (profile a): [`validators/syntax/validate_line_final_tokens.py`](../../../../readers-bofm/validators/syntax/validate_line_final_tokens.py) — checks line-final `AUX` with pending `aux` relation per Layer 1 break-legality table.
- Validator (profile b): [`validators/syntax/validate_rule_12_compound_verb.py`](../../../../readers-bofm/validators/syntax/validate_rule_12_compound_verb.py) — detects line-N modal+aux + line-final participle followed by line-N+1 *and* + bare participle without subject or finite verb.
- Layer 1 break-legality table: [`data/syntax-reference/ud-taxonomy.md` §7](../../../../readers-bofm/data/syntax-reference/ud-taxonomy.md) — rows *line-final `AUX` with pending `aux` relation* and *line-final participle followed by coordinated participle under shared modal+aux*, both marked `REQUIRED-MERGE`.
- Closed-list definitions: in validator source (`MODAL_AUX_PATTERN`, `PAST_PARTICIPLES`).
- Audit trail: `readers-bofm/private/audit-trail/R12.md` (to be populated during BoFM canon migration).
- Scholarship: [`atu-method/scholarship/bofm/R12.md`](atu-method/scholarship/bofm/R12.md).

<!-- ===== R13a ===== -->
### R13a: Never End a Line on a Preposition Seeking Its Object

**Status:** Active
**Category:** A (Mechanical, mandatory)
**Decidability:** Surface-pattern (UD-confirmable)
**Layer:** 1 (generic English grammar)

**Rule.** A v2-mine line MUST NOT end on an adposition (`ADP`) that has a pending `case` relation to an object on the following line. When the line-final token is tagged `ADP` and its object-NP is on the next line, the `ADP` MUST be moved to lead the next line (joined with its object).

**UD signature.**
```yaml
trigger:
  line_final_token: { upos: ADP, pending_case: true }
action: MERGE_FORWARD
```

**Scope.** Generic English-grammatical fact. A preposition alone at line end strands its object on the next line, fragmenting the PP and failing the atomic-thought test.

**Exclusions.**
1. **Phrasal-verb particles tagged `compound:prt`** — these are part of the verb's lexical structure, not prepositions seeking an object. R13a does not fire.
2. **Stranded prepositions in relative clauses** — *"the man whom he spake of"* — the `of` is grammatically licensed as stranded; R13a does not fire when UD parse marks the ADP as stranded.
3. ADP within a fixed multi-word unit → R18 keeps the unit whole.

**Precedence.** §3.5 Tier 1 (Layer 1 syntax veto; MALFORMED-class). Wins over all Tier 2+ generative rules at the same location.

**Examples.**
- Compliant: `"He sat down / on the throne"` (ADP `on` leads the new line with its NP)
- Non-compliant: `"He sat down on /\n the throne"` (line-final `on`; MALFORMED)
- Excluded (phrasal-particle): `"He gave up / and departed"` (`up` here is `compound:prt`, part of the verb)
- Excluded (stranded relative): `"the man whom he spake of, / who came from afar"` (stranded `of` in relative clause)

**Implementation.**
- Layer 1 reference: [`data/syntax-reference/ud-taxonomy.md §7`](../../../../readers-bofm/data/syntax-reference/ud-taxonomy.md) row: *line-final `ADP` with pending `case` relation* → `REQUIRED-MERGE`
- Validator: `validators/syntax/validate_line_final_tokens.py`
- Applier: (none — surface-pattern Layer-1)
- Audit trail: `private/audit-trail/R13a.md`
- Scholarship: `atu-method/scholarship/bofm/R13a.md`

<!-- ===== R15 ===== -->
### R15: Vocative Units Are Indivisible

**Status:** Active
**Category:** A (Mechanical, mandatory)
**Decidability:** UD-pattern
**Layer:** 3

**Rule.** A true vocative — a multi-word direct-address unit identifiable by the UD `vocative` relation — MUST occupy its own v2-mine line and MUST NOT contain an internal line break. The vocative MUST NOT be merged with the matrix clause that follows or precedes it. NP-object uses of phrases that are lexically vocative-shaped (e.g., *my brethren*, *my son*) but function as the syntactic object of a verb or preposition fall outside R15's scope and are not governed by this rule.

**UD signature.**
```yaml
trigger_internal_split:
  relation: vocative
  span: { contains_line_break: true }
action: KEEP_WHOLE

trigger_matrix_merge:
  relation: vocative
  span: { shares_line_with: matrix_clause }
  true_vocative_confirmed: true
action: SPLIT_BEFORE_SUBJECT
```

**Closed lists** (machine-readable).
```yaml
TRUE_VOCATIVE_CONFIRMERS:
  second_person_pronouns: [ye, thee, thou, you, thy, thine, your, yours, yourselves, thyself]
  imperative_verbs: [remember, hearken, hear, give, consider, behold, repent, come, listen, learn, know]

VOCATIVE_LEXICAL_SHAPES:
  - "O <NOUN/PROPN>"
  - "O <NOUN/PROPN> <NOUN/PROPN>"  # e.g., "O Lord God"
  - "(my|our) <kin_or_audience_noun>"  # e.g., "my son", "my brethren", "my people"
  - "<PROPN_address>"  # bare proper-name address

KIN_OR_AUDIENCE_NOUNS:
  - son
  - sons
  - daughter
  - brother
  - brethren
  - sister
  - sisters
  - people
  - beloved
  - friend
  - friends
```

**True-vocative test.** A vocative-shaped phrase is a true vocative WHEN the same predication contains a second-person pronoun from `TRUE_VOCATIVE_CONFIRMERS.second_person_pronouns` OR an imperative verb from `TRUE_VOCATIVE_CONFIRMERS.imperative_verbs`. Bare proper-name address (*"Moroni, ..."*) requires the same confirmer. Absent any confirmer, the phrase is treated as NP-object and falls outside R15.

**Scope.** Applies to multi-word direct-address constituents tagged with the UD `vocative` relation in v2-mine lines, including bare proper-name addresses confirmed by the true-vocative test. The rule governs (a) prohibition of internal line breaks within the vocative span, and (b) prohibition of same-line merger with the surrounding matrix clause. Single-word interjections without a following nominal addressee (e.g., *behold*) fall outside R15.

**Exclusions (closed list — each cites dominating rule).**
1. NP-object uses of vocative-shaped phrases (the phrase is the syntactic object of a matrix verb or preposition; no second-person or imperative confirmer in the predication) → out of scope; R10 (V+DO bond) governs the head-object relation.
2. Vocative + close divine-title appositive within a vocative environment (e.g., *"O God, the Eternal Father"*) → R15 still wins; the appositive joins the vocative as one indivisible address unit. (R22's INTRODUCING stack-split does not fire inside a vocative environment.)
3. Speech-tag introductions terminating in a colon (*"saying:"* followed by directly-quoted address) → J3 (speech-act announcement) governs the speech-tag break; R15 still governs the vocative occurring within the quoted material.

**Precedence.** §3.5 Tier 2. Wins over R22 in vocative environment. Wins over R17 when a true vocative sits on the matrix line (the matrix-complement merge yields to R15's own-line mandate for the vocative).

**Examples.**

- *Compliant:* "O Lord God, / how long wilt thou suffer..." (vocative own line; main clause on next line)
- *Compliant:* "My son, / I would that ye should make a proclamation..." (vocative own line; matrix follows)
- *Compliant (vocative + appositive bonded — R22 yields):* "O God, the Eternal Father," (Moroni 4:3, 5:2 sacrament prayer; appositive merged into vocative unit)
- *Non-compliant (matrix merge):* "My sons, I would that ye should remember..." (vocative merged with main clause on one line)
- *Non-compliant (internal split):* "O Lord / God" (vocative split internally — always forbidden)
- *Excluded — NP-object:* "I spake unto my brethren, saying:" (*my brethren* is prepositional object of *unto*; no second-person or imperative confirmer in the predication; R15 does not apply)
- *Excluded — NP-object:* "I went unto my brethren," (*my brethren* is prepositional object; no confirmer; R15 does not apply)
- *Excluded by J3 (speech-tag colon governs the tag break; R15 still governs the vocative inside the quoted material):* "And he said unto them: / O ye people of Nephi, hearken unto my words." (the colon-terminated tag yields to J3; the vocative *"O ye people of Nephi,"* still earns its own line per R15)

**Implementation.**

- Validator: [`validators/colometry/validate_rule_15_vocative.py`](../../../../readers-bofm/validators/colometry/validate_rule_15_vocative.py)
- Applier: [`validators/apply_rule_15_vocative_splits.py`](../../../../readers-bofm/validators/apply_rule_15_vocative_splits.py)
- Closed-list definitions: §Vocative-Confirmers-R15 (in BoFM canon, supplementary section)
- Audit trail: `readers-bofm/private/audit-trail/R15.md` (to be populated during BoFM canon migration)
- Scholarship: [`atu-method/scholarship/bofm/R15.md`](atu-method/scholarship/bofm/R15.md)

<!-- ===== R16 ===== -->
### R16: Dangling "That" After AICTP

**Status:** Active
**Category:** A (Mechanical, mandatory)
**Decidability:** Surface-pattern
**Layer:** 3

**Rule.** When the fixed extraposition formula *And it came to pass* (R1, §AICTP-Variants) is immediately followed by the subordinator *that* introducing the extraposed content clause, *that* MUST NOT be line-final. A line break SHALL be inserted before *that* whenever the formula and its content cannot share a single line without violating the atomic-thought test; *that* MUST then lead the content clause on the next line. The formula's internal span (through *pass*) remains whole per R1.

**UD signature.**
~~~yaml
trigger:
  surface_pattern: AICTP_VARIANTS  # see R1 §AICTP-Variants
  ud_anchor: { relation: expl, head: { lemma: come }, dependent: { lemma: it } }
  mark: { lemma: that, position: immediately_following_pass }
  condition: that_would_be_line_final
action: SPLIT_BEFORE_MARK
~~~

**Closed lists** (machine-readable).
~~~yaml
AICTP_VARIANTS:  # inherited from R1
  - "And it came to pass"
  - "And now it came to pass"
  - "And it shall come to pass"
~~~

**Scope.** The right-edge boundary of an AICTP token-sequence (R1) when the formula is followed by subordinator *that*. R16 governs ONLY the placement of the break relative to *that*: *that* leads its content clause, never trails the formula. R1 governs the formula-internal span; R16 governs the formula-to-content seam. When AICTP content is short enough to keep AICTP-*that*-content all on one line under the atomic-thought test, no R16 break is required.

**Exclusions (closed list — each cites dominating rule).**
1. AICTP not followed by *that* (formula stands as scene-marker without an extraposed clause) → no R16 trigger; R1 keep-whole alone applies.
2. *That* in an AICTP-adjacent position but governed by a different rule (e.g., the *that* belongs to a higher-level R17 complement of an embedded matrix verb rather than to AICTP itself) → R17 governs that *that*; R16's trigger requires direct linear adjacency *pass that*.
3. AICTP followed by a substantive temporal/locative/causal PP that earns its own line BEFORE the *that*-clause → J5 (substantive adjunct as own focus); R16 still places the *that*-break, but the J5 slot-filler is on its own line per J5's mandate.

**Precedence.** §3.5 Tier 2 (couples to R1). Inherits R1's Tier-2 indivisibility status; together R1+R16 form the canonical AICTP line shape. Wins over R17 and R19 when both could apply to the *that* immediately following AICTP — the AICTP-coupling is most specific (§3.5.1 sub-hierarchy: "R1 / R16 AICTP *that*" is the first match in the *that*-cluster).

**Examples.**

- *Compliant (short content; one line):* "And it came to pass that I, Nephi, returned to my tent." (formula + *that* + short content all on one line; R16's break trigger does not fire because *that* is not line-final)
- *Compliant (long content; R16 break before *that*):* "And it shall come to pass / that whosoever shall believe on the Son of God, the same shall have everlasting life" (R16 break before *that* so *that* leads its content clause)
- *Non-compliant (R16 violation — *that* line-trails the formula):* "And it came to pass that / whosoever shall believe on the Son of God..." (the formula's *that* is stranded line-final; reader's attention dangles forward expecting "that what?")
- *Non-compliant (R1 violation — formula severed):* "And it came / to pass that whosoever..." (this is an R1 violation of the formula-internal span; R16 does not separately fire because R1 takes precedence at the formula-internal level)
- *Excluded by R17:* "And it came to pass that he said unto them that they should depart" (the second *that* is governed by R17 speech-class complement-integrity, not R16; R16 governs only the *that* immediately following *pass*)

**Implementation.**

- Validator: [`validators/colometry/validate_rule_16_aictp_dangling_that.py`](../../../../readers-bofm/validators/colometry/validate_rule_16_aictp_dangling_that.py) (also at `validate_rule_16_ud.py`)
- Applier: (none — surface-pattern split-before; corpus is hand-authored at this granularity, validator reports violations)
- Closed-list definitions: §AICTP-Variants (inherited from R1)
- Audit trail: `readers-bofm/private/audit-trail/R16.md` (to be populated during BoFM canon migration)
- Scholarship: [`atu-method/scholarship/bofm/R16.md`](atu-method/scholarship/bofm/R16.md)

<!-- ===== R17 ===== -->
### R17: Complement Integrity

**Status:** Active
**Category:** A (Mechanical, mandatory)
**Decidability:** UD-pattern
**Layer:** 3

**Rule.** A matrix verb's clausal complement MUST be on the same v2-mine line as the matrix verb when the verb's lemma belongs to one of the six closed verb classes (§Verb-Classes-R17) and the complement is marked by *that*, *whether*, *if*, a WH-word, or an infinitival *to*. Speech-class verbs additionally require their obligatory topic-PP complement (*of*/*concerning*/*unto*/*against*) on the same line. Experience verbs (`repent`, `partake`, `forgive`) require their obligatory *of*-PP complement on the same line.

**UD signatures.**
```yaml
trigger_clausal:
  relation: [ccomp, xcomp]
  head: { upos: VERB, lemma_in: GOVERNING_LEMMAS_R17 }
  mark: { lemma_in: [that, whether, if, "WH-*"] }
action: MERGE_MATRIX_AND_COMPLEMENT

trigger_topic_pp:
  relation: obl
  head: { upos: VERB, lemma_in: SPEECH_CLASS_R17 }
  case: { lemma_in: [of, concerning, unto, against] }
action: MERGE_VERB_AND_TOPIC_PP

trigger_experience_of_pp:
  relation: obl
  head: { upos: VERB, lemma_in: [repent, partake, forgive] }
  case: { lemma: of }
action: MERGE_VERB_AND_OF_PP
```

**Closed lists** (defined at §Verb-Classes-R17):

- `GOVERNING_LEMMAS_R17` — six closed verb classes:
  - **Causative:** `cause`, `suffer`, `permit`, `command`, `grant`
  - **Aspectual:** `begin`, `cease`, `continue`
  - **Speech-indirect:** `say`, `speak`, `declare`, `testify`, `swear`, `proclaim`, `tell`, `confess`, `rehearse`, `preach`, `answer`, `cry`, `beseech`, `ask`, `plead`
  - **Cognition:** `know`, `believe`, `perceive`, `remember`, `understand`, `hear`, `see`, `suppose`, `imagine`, `forget`, `think`
  - **Volition:** `wish`, `desire`, `hope`, `long`, `trust`, `pray`, `seek`
  - **FEF-extraposition:** `it was their lot to`, `it is expedient to`, copular extraposition patterns
- `SPEECH_CLASS_R17` — subset of GOVERNING_LEMMAS_R17 taking obligatory topic-PP: `speak`, `declare`, `preach`, `testify`, `prophesy`, `bear record`, `bear testimony`, `bear witness`, `say`, `cry`, `write`
- `PETITION_FRAME_VERBS` — speech- and volition-class verbs whose modal-aux *that*-complement reads ambiguously between content and purpose: `cry`, `pray`, `beseech`, `ask`, `seek`, `plead`

**Scope.** Matrix VERB head only. ADJ head → R26 territory. NOUN head → out of scope (no R17-equivalent for NOUN-headed ccomp).

**Exclusions (closed list — each cites dominating rule).**

1. Direct discourse (colon-terminated speech-tag) → J3 (speech-act announcement)
2. AICTP-that → R16
3. Purpose-that with modal under non-cognitive motion verb → R7
4. Parallel that-series at N≥3 → J1 (per N=3+ cliff)
5. Meta-announcement (BE-verb + predicate-noun + appositive-that) — *that*-clause is appositive to the noun, not complement of the verb
6. Direct divine speech with recitativum-*that* (*saith the Lord, that [first-person content]*) → J3
7. Speech-indirect long-complement: matrix lemma in `{say, speak, tell, declare}` AND ccomp body ≥8 word tokens → J3 (long-complement exception)
8. Petition-frame ambiguity: matrix lemma in `PETITION_FRAME_VERBS` AND ccomp body has modal aux (`may`, `might`, `will`, `would`, `shall`, `should`, `can`, `could`, `must`) → REVIEW-REQUIRED (not auto-applied)
9. Vocative on matrix line → R15 (vocative-aware filter — vocative wins; matrix's complement merge yields to R15's own-line mandate for the vocative)

**Precedence.** §3.5 Tier 3. Yields to R26 (when ADJ is direct head). Wins over R19 (when both apply on a *that*-clause).

**N=2 sub-rule (coordinate that-series).** When R17 governor takes exactly 2 coordinate *that*-complements (e.g., *"declared unto them that they were a people who were under him, and that they were a free people"*), apply the M1 synonymy test (§1.9 N=2 Adjudication Principle):

- Synonymous / cognate / restatement → MERGE both *that*-clauses with the matrix.
- Distinct non-synonymous (each member with its own finite verb) → MERGE first *that*-clause with the matrix; SPLIT second per J1.

The sub-rule fires only when the matrix governor is in `GOVERNING_LEMMAS_R17`. Out-of-list matrix verbs (e.g., `wondereth`, `marveleth`) fall outside R17 territory entirely.

**Examples.**

- Compliant: *"He caused that his servants should stand forth"* (causative + that-clause merged)
- Compliant: *"I say unto you that the time shall come"* (speech-indirect + that-clause merged)
- Compliant (topic-PP): *"Nephi spake of the things which he had seen"* (speech + obligatory of-PP merged)
- Compliant (experience of-PP): *"he hath forgiven us of those our many sins"* (experience verb + of-PP merged; Alma 24:10)
- Non-compliant (violates R17): *"He caused / that his servants should stand forth"* (matrix severed from complement)
- Excluded by J3: *"And he said unto them: / Take what ye need..."* (colon-marked direct discourse)
- Excluded by long-complement exception (split is correct): *"said unto them / that they were a hard-hearted and a stiffnecked people"* (Alma 9:31; ccomp body ≥8 words)

**Implementation.**

- Validator: [`validators/colometry/validate_rule_17_ud.py`](../../../readers-bofm/validators/colometry/validate_rule_17_ud.py)
- Applier: [`validators/apply_rule_17_ud.py`](../../../readers-bofm/validators/apply_rule_17_ud.py)
- Verb-class definitions: §Verb-Classes-R17 (in BoFM canon, supplementary section)
- Audit trail: `readers-bofm/private/audit-trail/R17.md` (to be populated during BoFM canon migration)
- Scholarship: [`atu-method/scholarship/bofm/R17.md`](atu-method/scholarship/bofm/R17.md)

---


<!-- ===== R18 ===== -->
### R18: Fixed Idiom Integrity

**Status:** Active
**Category:** A (Mechanical, mandatory)
**Decidability:** Surface-pattern
**Layer:** 3

**Rule.** A token sequence matching any member of the closed list §Fixed-Idioms-R18 MUST be kept whole on a single v2-mine line. No line break MAY occur internal to a matched idiom's token sequence, regardless of resulting line length.

**UD signature.**
~~~yaml
trigger:
  surface_pattern: FIXED_IDIOMS_R18
  match: contiguous_token_sequence
action: KEEP_WHOLE
~~~

**Closed lists** (machine-readable).
~~~yaml
FIXED_IDIOMS_R18:
  - "put to death"
  - "from time to time"
  - "prevailed upon"
  - "put an end to"
  - "one with another"
  - "it is expedient that"
  - "insomuch as"
~~~

Date-colophon formulas are governed by R23 (sister rule, same KEEP_WHOLE logic; separate closed list of year-formula patterns).

**Scope.** Multi-word lexicalized expressions in the BoFM register that function as single lexical items. The closed list is the operational inventory; surface-token match against the v2-mine line stream is the detection mechanism. Idiom-internal token order is fixed; no inflectional or word-order variants are recognized as members.

**Exclusions (closed list — each cites dominating rule).**
1. *And it came to pass [that]* and its variants → R1 (sister formula-integrity rule with its own closed list and right-edge R16 coupling).
2. Date-colophon formulas (*"in the Nth year of the reign of the judges"*) → R23 (sister formula-integrity rule with its own closed list).
3. *insomuch that* (distinct subordinator from *insomuch as*) → R27 (consecutive-result subordinator with its own 3-condition merge test, not a fixed idiom).
4. *it is expedient that* matched as ADJ predicate complement frame governing a clausal complement → R26 governs the predicate+complement merge at the matrix-clausal level; R18's KEEP_WHOLE applies to the formula's internal token sequence, R26 governs the matrix+ccomp boundary.

**Precedence.** §3.5 Tier 2. Indivisibility tier; wins over all subtractive vetoes and merge-overrides at the formula-internal level. Coexists with R1, R15, R16, R23 in Tier 2 (each governs a distinct closed-list span).

**Examples.**

- *Compliant:* "they should be put to death" (idiom whole on one line)
- *Compliant:* "they did meet together from time to time" (idiom whole on one line)
- *Compliant:* "and they spake one with another" (idiom whole on one line)
- *Compliant:* "it is expedient that ye should keep the commandments" (formula whole on one line; matrix+ccomp merge governed by R26)
- *Non-compliant:* "they should be put / to death" (idiom severed)
- *Non-compliant:* "from time / to time" (idiom severed)
- *Non-compliant:* "it is expedient / that ye should keep the commandments" (formula severed)
- *Excluded by R1:* "And it came to pass that..." (governed by R1's AICTP_VARIANTS closed list, not R18).
- *Excluded by R23:* "in the seventh year of the reign of the judges" (date-colophon — governed by R23).
- *Excluded by R27:* "he did labor insomuch that his strength returned" (compound subordinator *insomuch that* is R27 territory; R18 covers only *insomuch as*).

**Implementation.**

- Validator (surface-pattern): [`validators/colometry/validate_rule_18_fixed_idioms.py`](../../../../readers-bofm/validators/colometry/validate_rule_18_fixed_idioms.py)
- Validator (UD-query): [`validators/colometry/validate_rule_18_ud.py`](../../../../readers-bofm/validators/colometry/validate_rule_18_ud.py)
- Applier: (none — surface-pattern keep-whole; corpus is hand-authored at this granularity, validators report violations)
- Closed-list definitions: §Fixed-Idioms-R18 (in BoFM canon, supplementary section)
- Audit trail: `readers-bofm/private/audit-trail/R18.md` (to be populated during BoFM canon migration)
- Scholarship: [`atu-method/scholarship/bofm/R18.md`](atu-method/scholarship/bofm/R18.md)

<!-- ===== R19 ===== -->
### R19: Cataphoric "That"/Relative Clauses Break; Anaphoric Merge

**Status:** Active
**Category:** A (Mechanical, mandatory) for the PROPN and PRON/DET branches; B (Editorial, judgment-required) for the NOUN branch routed to REVIEW
**Decidability:** Mixed — UD-pattern for PROPN-head and PRON/DET-head branches; Discourse-context-needed for NOUN-head branch (routed to REVIEW-REQUIRED)
**Layer:** 3

**Rule.** A relative clause (UD `acl:relcl`) or non-complement *that*-clause (UD `acl`) attached to a head noun-phrase MUST be classified by the head token's UPOS and treated as follows. When the head UPOS is **PROPN**, the relative is anaphoric and the relative MUST be merged onto the head's line. When the head UPOS is **PRON** or **DET**, the relative is cataphoric and a line break MUST be inserted before the relative pronoun (*which*, *that*, *who*, *whoso*, *whatsoever*). When the head UPOS is **NOUN**, the case MUST be routed to REVIEW-REQUIRED — mechanical resolution is not authorized. Expletive *it* in cleft constructions (*"that it is by his grace"*) and result/purpose clauses with new predication (*"that it is good"*) are NOT anaphoric regardless of surface anaphor-like material; these route per Exclusions below. When a *that*-clause is the complement of a Rule 17 governing verb, R17 wins and R19 MUST NOT fire.

**UD signature.**
```yaml
trigger_anaphoric_propn:
  relation: [acl:relcl, acl]
  head: { upos: PROPN }
  excludes: { relation_at_head: ccomp }   # R17 wins
action: MERGE_HEAD_AND_DEPENDENT

trigger_cataphoric_pron_det:
  relation: [acl:relcl, acl]
  head: { upos: [PRON, DET] }
  excludes: { relation_at_head: ccomp }   # R17 wins
action: SPLIT_BEFORE_RELATIVE

trigger_noun_head_ambiguous:
  relation: [acl:relcl, acl]
  head: { upos: NOUN }
  excludes: { relation_at_head: ccomp }   # R17 wins
action: REVIEW

trigger_predicative_identifier:
  relation: [acl:relcl, acl]
  head: { upos: NOUN }
  mark: { lemma: which }
  relative_body_pattern: "(is|was|are|were|became) + classifier-NP"
  semantic_role: predicative-identifier   # classifies/identifies head; advances no new action
action: MERGE_HEAD_AND_DEPENDENT
```

**Closed lists** (machine-readable).
```yaml
ANAPHORIC_UPOS:
  - PROPN

CATAPHORIC_UPOS:
  - PRON
  - DET

REVIEW_UPOS:
  - NOUN

PREDICATIVE_IDENTIFIER_COPULAS:
  - is
  - was
  - are
  - were
  - became
```

The `CATAPHORIC_UPOS` set captures the generic forward-pointer heads characteristic of BoFM-English: *those*, *whoso*, *whatsoever*, *all*, *any*, *every*, *this*, *that*, *these*. Membership is determined by the UD parser's UPOS tag, not by a lexical list.

**Scope.** Non-complement *that*-clauses and relative clauses (`acl:relcl` or `acl`) attached to a noun-phrase head. The rule fires on the head token's UPOS only; lemma membership is not consulted. The unified "which"-clause decision tree (predicative-identifier MERGE, completing-predication MERGE, non-restrictive-relative-introducing-new-info SPLIT, cataphoric-advancing SPLIT, anaphoric-backward-referring MERGE) operates as a sub-rule of the three UPOS branches above: predicative-identifier and completing-predication patterns under NOUN heads are MERGE; all other NOUN-head cases route to REVIEW pending discourse-context resolution.

**Exclusions (closed list — each cites dominating rule).**

1. Complement of a Rule 17 governing verb (matrix VERB lemma in `GOVERNING_LEMMAS_R17`; `ccomp` relation at the head) → R17 wins; *that*-clause merges with matrix per complement integrity
2. Complement of a Rule 26 predicate (ADJ or NOUN-as-predicate head in `RULE_26_HEAD_LEMMAS`) → R26 wins; *that*-clause merges with predicate
3. AICTP *that* (token sequence "And it came to pass that") → R1 / R16 win
4. Purpose finite *that* + MODAL (advcl + modal aux) → R7
5. Compound subordinator *insomuch that* → R27
6. Fixed-idiom contexts (*it is expedient that*, etc., per Rule 18 fixed-idiom list) → R18 wins
7. Expletive *it* in cleft constructions (*"that it is by his grace"*) — structural placeholder, NOT anaphoric; routes per other applicable rules
8. Result/purpose clauses with new predication (*"that it is good"*) — cataphoric semantics override anaphor-like surface form; the relative-pronoun head test does not apply
9. Cross-line attachments where the relative is NOT adjacent to its head (gap > 1 v2 line) → REVIEW-REQUIRED (parser ambiguity guard)
10. Merged-line length > 130 characters → REVIEW-REQUIRED (length backstop, per applier convention)

**Precedence.** §3.5 Tier 5. Yields to R1/R16 (AICTP), R17 (complement integrity), R26 (predicate complement), R7 (purpose + modal), R18 (fixed idiom), R27 (insomuch-that). Per §3.5.1 "that"-cluster sub-hierarchy, R19 is the residual-relative branch — the most-specific-first detection order routes R1/R16, R26, R17, R27, and R7 ahead of R19. R19 fires only on `acl:relcl` (and non-complement `acl`) attachments after all complement / formulaic / purposive readings have been excluded.

**Examples.**

- *Compliant (cataphoric SPLIT, PRON head):* "I say unto you / that the good shepherd doth call you" — *that*-clause advances new image and new action under a generic forward-pointing head
- *Compliant (cataphoric SPLIT, DET head):* "those / which shall keep my commandments" — *those* is a generic forward-pointer; relative introduces qualifying predication
- *Compliant (anaphoric MERGE, PROPN head):* "the brass plates which Lehi obtained" — *Lehi* is a named referent; relative is backward-pointing characterization
- *Compliant (anaphoric MERGE, established discourse):* "The Spirit hath not said unto me that this should be the case" — *this* and *the case* both point back; merge
- *Compliant (predicative-identifier MERGE, NOUN head sub-rule):* "commandment which is the word of God" — *which is + classifier-NP* names/classifies the head without advancing new action
- *Non-compliant (R19 violation — cataphoric not split):* "I say unto you that the good shepherd doth call you" (one line — generic frame not separated from new image)
- *Non-compliant (R19 violation — anaphoric improperly split):* "Adam / which was the first man" (PROPN head; anaphoric relative wrongly broken from named referent)
- *Excluded by R17 (complement integrity wins):* "He caused that his servants should stand forth" — *that*-clause is the `ccomp` of the causative VERB *cause*; R17 governs the merge, R19 does not fire
- *Excluded by R26:* "if it were possible that our first parents..." — matrix is ADJ *possible* in `RULE_26_HEAD_LEMMAS`; R26 governs the merge
- *Routed to REVIEW (NOUN head, ambiguous):* "records which were engraven upon the plates of brass" — anaphoricity depends on whether *plates of brass* was established earlier in the passage; mechanical resolution not authorized

**Implementation.**

- Validator: [`validators/colometry/validate_rule_19_ud.py`](../../../../readers-bofm/validators/colometry/validate_rule_19_ud.py)
- Applier (anaphoric MERGE branch): [`validators/apply_rule_19_ud_merge.py`](../../../../readers-bofm/validators/apply_rule_19_ud_merge.py)
- Closed-list definitions: `ANAPHORIC_UPOS`, `CATAPHORIC_UPOS` in validator source
- Applier filters: adjacency gap = 1, merged-line length ≤ 130 characters (Jarom-1:8-style catastrophe guard)
- Audit trail: `readers-bofm/private/audit-trail/R19.md` (to be populated during BoFM canon migration)
- Scholarship: [`atu-method/scholarship/bofm/R19.md`](atu-method/scholarship/bofm/R19.md)

<!-- ===== R20 ===== -->
### R20: No-Anchor Rule

**Status:** Active
**Category:** B (Editorial, judgment-required) — violation diagnosis is mechanical; remediation (MERGE_FORWARD vs. restructure) requires per-case judgment
**Decidability:** UD-pattern
**Layer:** 3

**Rule.** Every v2-mine line MUST carry at least one thought-marking anchor. An anchor is one of: a finite `VERB`, an infinitival `VERB`, a `VERB` participle functioning predicatively on the line, or a substantive head independently predicated on the line via an attached `cop` or own predicate. A line containing zero anchors MUST be remediated by merging forward with the next line, unless the line satisfies one of the four exemptions in §Exemptions below. Bare noun-phrases that continue a prior line's predicate as object continuations or appositional extensions do NOT count as anchors regardless of their nominal content.

**UD signature.**
```yaml
trigger:
  line: { anchor_count: 0 }
  excludes:
    - { exemption: single_line_verse }
    - { exemption: speech_intro_prefix }
    - { exemption: standalone_sentence_connective }
    - { exemption: passes_structural_justification }  # any of J1-J5
action: MERGE_FORWARD  # default remediation
# When MERGE_FORWARD would violate another rule, or when the line's role
# requires restructure rather than merge, action is REVIEW.
```

**Closed lists** (machine-readable).
```yaml
ANCHOR_KINDS:
  - finite_VERB              # tensed verb with nsubj or imperative
  - infinitival_VERB         # to-infinitive heading its own predication on the line
  - predicative_participle   # VERB participle functioning as predicate of the line
  - substantive_with_cop     # NP head with attached cop / own predicate on the line

NON_ANCHOR_NOMINALS:
  - object_continuation       # bare NP continuing prior line's verb's obj
  - apposition_extension      # bare NP appositional to prior line's NP
  - coordinate_object_member  # bare "and [NP]" member of a compound object list

STANDALONE_SENTENCE_CONNECTIVES:
  - Wherefore
  - And now
  - Therefore
  - Now
  - Yea
  - Behold
```

The `STANDALONE_SENTENCE_CONNECTIVES` list captures discourse connectives that legitimately occupy their own line in BoFM register as scene-setters, even though they carry no verbal anchor. Membership is constrained to corpus-attested cases.

**Scope.** Every v2-mine line is in scope. The rule operates after all generative split-triggers (Tier 5) and merge-overrides (Tier 4) have settled — it is a floor-check that catches lines produced by the upstream pipeline (or by hand-editing) that lack predicative content. The rule does NOT govern line content beyond anchor presence; lines with one or more anchors are not further constrained by R20.

**Exemptions (closed list — each cites dominating rule or framework justification).**

1. **Single-line verses** — verses whose v2-mine representation is exactly one line are atomic by definition and pass R20 regardless of internal anchor count. → out of scope
2. **Speech-intro prefixes** — short colon-terminated or paratactically-introducing speech tags (e.g., bare *saying:*, *and he said:*) — the speech-act announcement IS the predication, even when the surface anchor is elided → J3
3. **Standalone sentence connectives** — discourse connectives from `STANDALONE_SENTENCE_CONNECTIVES` legitimately occupy their own line as scene-setting beats → J3 / J5
4. **Lines passing any structural justification** — lines without a verbal anchor that nevertheless pass one of the five structural justifications via formal-structural recoverability (parallel-series member with elided shared predicate, portrait-accumulation stack-member, classical comma, substantive adjunct as own focus) → J1 / J2 / J3 / J4 / J5

**Precedence.** §3.5 Tier 8. Floor-check that fires after all Tier 1-7 rules have settled. Yields to every upstream tier when an upstream rule's output places a no-anchor line on the page — R20 then either remediates by MERGE_FORWARD or routes to REVIEW when remediation would violate an upstream rule.

**Examples.**

- *Compliant (finite VERB anchor):* "And he did minister unto them" — anchor: finite `VERB` *minister* with `nsubj` *he*
- *Compliant (predicative participle anchor):* "I, Nephi, having been born of goodly parents" — anchor: predicative participle *born* (the participial-absolute predication; R21 territory)
- *Compliant (substantive-with-cop anchor):* "the records were of great worth" — anchor: NP *the records* + attached `cop` *were*
- *Compliant (exemption — single-line verse):* a verse rendered as exactly one v2-mine line, even if it contains no surface VERB → out of scope per Exemption 1
- *Compliant (exemption — standalone connective):* "Wherefore" on its own line introducing a new discourse beat → Exemption 3 (J3 / J5)
- *Compliant (exemption — J1 series member):* "and the brass plates," as a member of a parallel object series under an elided shared predicate → Exemption 4 (J1 compound-list)
- *Non-compliant (zero anchors, no exemption applies):* "and also her mistress, the queen, and the king," as a standalone line — three bare NPs in object-continuation of a prior line's verb; no anchor; no exemption fires → MERGE_FORWARD with the next line OR restructure per editorial review
- *Non-compliant (zero anchors, mid-stream):* a bare prepositional phrase line like "in the wilderness" not functioning as a J5 substantive adjunct on its own focus → MERGE_FORWARD with its matrix line

**Implementation.**

- Validator: [`validators/syntax/validate_rule_20_ud.py`](../../../../readers-bofm/validators/syntax/validate_rule_20_ud.py)
- Applier: not implemented (remediation is per-case editorial — R20 violations route to MERGE_FORWARD candidate or REVIEW; no auto-applier)
- Closed-list definitions: `ANCHOR_KINDS`, `STANDALONE_SENTENCE_CONNECTIVES` in validator source
- Audit trail: `readers-bofm/private/audit-trail/R20.md` (to be populated during BoFM canon migration)
- Scholarship: [`atu-method/scholarship/bofm/R20.md`](atu-method/scholarship/bofm/R20.md)

<!-- ===== R21 ===== -->
### R21: Participial Absolute Integrity

**Status:** Active
**Category:** A (Mechanical, mandatory)
**Decidability:** UD-pattern
**Layer:** 3

**Rule.** A participial absolute — a subject-bearing participial clause of the form *"X having Y-ed"* or *"X being Y"* — MUST occupy its own v2-mine line, distinct from its matrix predication. The participial absolute is identified by the UD pattern of an `nsubj`-bearing non-finite VERB (participial form, no finite `aux`) attached as an adjunct (`advcl`, `acl`, or `parataxis`) to a matrix clause. The matrix's own subject and finite predication MUST appear on the following line. The participial absolute MUST NOT be split internally; subject, participle, and any complement of the participial remain on the one shared line.

**UD signature.**
```yaml
trigger:
  relation: [advcl, acl, parataxis]
  head:
    upos: VERB
    feats: { VerbForm: [Part, Ger] }     # participial / gerundive form
    has_finite_aux: false                 # no finite auxiliary in the participial clause
  required_dependent:
    relation: nsubj
    upos: [PROPN, PRON, NOUN]            # subject of the participial — what makes it absolute
  matrix:
    has_distinct_nsubj: true              # matrix carries its own subject (or co-referent restart)
action: STAND_OWN_LINE
```

*Note on action code.* The standard `§Action-Codes` table in [`atu-method/docs/rule-template.md`](atu-method/docs/rule-template.md) does not include a code for "the matched span MUST occupy its own line, with breaks both before and after the span." `STAND_OWN_LINE` is the proposed extension for this operational effect; it covers R21 and parallels the conceptually similar effect of `STACK_LIST_MEMBERS` (each member earns its own line) but for a single-span case rather than a series. Per §Action-Codes, new codes require a meta-template change — flagged for migration-batch ratification. Pending ratification, implementers may treat the action as the conjunction of `SPLIT_BEFORE_SUBJECT` (before the participial's own subject) and `SPLIT_BEFORE_SUBJECT` (before the matrix's resumptive subject) — but the unified `STAND_OWN_LINE` code is preferred for operational clarity.

**Diagnostic — paraphrase test.** The participial clause MUST pass the finite-paraphrase test: rewriting *"X having Y-ed"* → *"X had Y-ed"* (or *"X being Y"* → *"X was Y"*) MUST yield a complete sentence that can stand alone. A failed paraphrase indicates the construction is not an absolute and routes elsewhere (see Exclusions).

**Scope.** Subject-bearing participial clauses functioning as absolute adjuncts to a matrix predication. The participial's subject is morphologically present in the text (named NP, PROPN, or non-elided PRON). The matrix clause has its own subject (or a restart of the participial's subject) and its own finite verb.

**Exclusions (closed list — each cites dominating rule).**

1. Bare participial without its own subject (subject-inheriting from matrix) — out of scope; routes to M3 (bare-governor indivisibility, framework §1.5 M3) including M3's bare-trailing-participial extension.
2. Bare participial-heading frames awaiting clausal complement (*"telling them / that there could be no atonement..."*) — out of scope; routes to M3 (bare-governor indivisibility) until the complement is resolved.
3. Vocative attached to or interleaved with the participial absolute (*"O Lord, thou having..."* shape) — R15 wins on the vocative's own-line mandate; the participial absolute remains own-line per R21, with R15 governing the vocative's boundary.
4. Participial absolute whose subject is the divine title in a stack-split INTRODUCING context — R22 governs the stack treatment of the divine-title head; R21 still places the participial absolute on its own line, but R22's STACK SPLIT for the appositive operates on the head NP before R21's own-line treatment of the whole absolute.
5. Date-colophon participials embedded in a date-colophon formula (*"in the Nth year of the reign of the judges, the X having Y-ed..."*) — R23 (date colophon integrity) wins on the formula's KEEP_WHOLE mandate; R21's own-line treatment yields within the colophon's protected span.

**Precedence.** §3.5 Tier 5. Yields to R15 (vocative environment), R23 (date-colophon integrity). Wins over M3 (M3 covers BARE participials only; subject-bearing participials are R21's territory by SCOPE distinction, not by tier ordering — the two rules partition the participial space rather than collide). Coexists with R17 / R26 / R19 / R7 / R27 on the matrix clause's separate operational treatment (R21 governs the absolute; the matrix's own complement / purpose / relative / consecutive analysis proceeds independently on the matrix line).

**Examples.**

- *Compliant (own line, participial absolute):* "I, Nephi, having been born of goodly parents, / therefore I was taught somewhat in all the learning of my father" (1 Ne 1:1) — "I, Nephi, had been born of goodly parents" passes the finite-paraphrase test.
- *Compliant (own line, participial absolute with matrix-restart):* "And yet, I being over-zealous to inherit the land of our fathers, / collected as many as were desirous to go up to possess the land" (Mos 9:3) — "I was over-zealous to inherit the land of our fathers" passes the finite-paraphrase test; matrix verb *collected* takes the participial's subject as restart.
- *Non-compliant (R21 violation — participial absolute merged with matrix):* "I, Nephi, having been born of goodly parents was taught somewhat in all the learning of my father" (one line) — the participial absolute is grammatically independent and MUST be set off.
- *Non-compliant (R21 violation — participial absolute split internally):* "I, Nephi, / having been born of goodly parents, / therefore I was taught..." — the subject and its participle MUST stay on the one absolute line.
- *Excluded by M3 (bare participial — no own subject):* "telling them / that there could be no atonement..." — *telling* has no morphological subject in its clause; M3 governs.
- *Excluded by R15 (vocative environment):* "O Lord, thou having delivered me..." — vocative *"O Lord"* takes its own line per R15; R21 places the *"thou having delivered me"* absolute on its own following line.

**Implementation.**

- Validator: (not yet implemented — Category A but applier deferred; filename follows the validate_rule_{id}_ud.py / apply_rule_{id}_ud.py convention)
- Applier: (not yet implemented — Category A but applier deferred; filename follows the validate_rule_{id}_ud.py / apply_rule_{id}_ud.py convention)
- Closed-list definitions: none — R21 fires on UD-feature pattern, not on a lexical closed list
- Audit trail: `readers-bofm/private/audit-trail/R21.md` (to be populated during BoFM canon migration)
- Scholarship: [`atu-method/scholarship/bofm/R21.md`](atu-method/scholarship/bofm/R21.md)

<!-- ===== R22 ===== -->
### R22: Divine Title Appositives

**Status:** Active
**Category:** B (Editorial, judgment-required) — for INTRODUCING detection. Once a case is classified INTRODUCING via a formal anchor (closed-list), the stack-split action is mechanical.
**Decidability:** UD-pattern + Discourse-context-needed
**Layer:** 3

**Rule.** A divine-title appositive — an appositional NP whose head lemma is in `DIVINE_TITLE_HEADS` and which appears as `appos` to a divine-name referent — MUST be split onto its own line (STACK SPLIT) when the construction is INTRODUCING, and MUST remain merged with its referent on one line (REFERENCING default) otherwise. A construction is INTRODUCING when AT LEAST ONE of the three closed-list formal anchors (§Formal-Anchors-R22) is present. When R22 and R15 (Vocative Indivisibility) both fire on the same span — i.e., the divine-title appositive sits inside a vocative environment — R15 wins and the appositive MUST merge into the vocative as one indivisible address unit. Within a single unified rhetorical passage, repeated invocations of the same divine-title appositive MUST receive uniform treatment; oscillation between STACK and MERGE within one passage is forbidden.

**UD signature.**
```yaml
trigger_introducing:
  relation: appos
  head: { upos: PROPN, lemma_in: DIVINE_NAME_REFERENTS }
  dependent: { upos: [NOUN, PROPN], lemma_in: DIVINE_TITLE_HEADS }
  formal_anchor: { any_of: FORMAL_ANCHORS_R22 }
  vocative_environment: false
action: STACK_LIST_MEMBERS

trigger_referencing:
  relation: appos
  head: { upos: PROPN, lemma_in: DIVINE_NAME_REFERENTS }
  dependent: { upos: [NOUN, PROPN], lemma_in: DIVINE_TITLE_HEADS }
  formal_anchor: { any_of: FORMAL_ANCHORS_R22 }
  vocative_environment: false
  match_condition: no_anchor_present
action: MERGE_HEAD_AND_DEPENDENT
```

**Closed lists** (machine-readable).
```yaml
DIVINE_NAME_REFERENTS:
  # Proper-name heads that may carry a divine-title appositive
  - Jesus
  - Christ
  - "Jesus Christ"
  - God
  - Lord
  - Father
  - Messiah
  - Redeemer
  - Savior

DIVINE_TITLE_HEADS:
  # Head lemmas of the appositional NP recognized as divine titles
  - Son          # "Son of God", "Son of the living God", "Son of Righteousness"
  - Father       # "Eternal Father", "Heavenly Father"
  - Lamb         # "Lamb of God"
  - Holy         # "Holy One of Israel"
  - Almighty
  - Redeemer
  - Savior
  - Messiah
  - King         # "King of kings", "King of heaven"
  - Lord         # "Lord of hosts", "Lord God Omnipotent"
  - Christ
  - Creator
  - Maker

FORMAL_ANCHORS_R22:
  # The three closed-list formal anchors that trigger INTRODUCING classification.
  # AT LEAST ONE must be present in the surrounding context for STACK SPLIT to fire.

  formal_naming_formula:
    # Surface patterns introducing a name + title pairing as an act of naming
    patterns:
      - "his name shall be called <X>, <title>"
      - "they shall call his name <X>, <title>"
      - "his name shall be <X>, <title>"
      - "thou shalt call his name <X>, <title>"
      - "and he shall be called <X>, <title>"

  first_occurrence_context:
    # The named-plus-titled identity is being revealed for the first time in the
    # current pericope/discourse window. Discourse-context-needed; validator emits
    # REVIEW unless a first-occurrence anchor token is co-present (e.g., a verb
    # of revelation/showing/manifesting in the matrix).
    revelation_verbs:
      - show
      - reveal
      - manifest
      - make known
      - declare unto
      - prophesy of

  prophetic_proclamation_frame:
    # Surrounding frame establishes prophetic / revelatory authority
    speech_tags:
      - "Thus saith the Lord"
      - "Behold, I say unto you"
      - "the word of the Lord came"
      - "I beheld"             # vision-frame
      - "the angel said unto"  # angelic-announcement frame
      - "an angel of the Lord"
```

**Formal-anchor test.** A divine-title appositive is INTRODUCING (STACK SPLIT) WHEN at least one anchor from `FORMAL_ANCHORS_R22` is present in the same predication or in the immediately governing speech-tag/frame. Absent any anchor, the construction is REFERENCING and MERGE is the default. The formal_naming_formula anchor and the prophetic_proclamation_frame anchor are surface-detectable; the first_occurrence_context anchor requires discourse tracking and the validator emits REVIEW-REQUIRED when no surface anchor is present but the case may be first-occurrence.

**Vocative-environment filter.** Before applying the INTRODUCING vs REFERENCING test, check whether the divine-title appositive sits in a vocative environment (the head of the appositional construction is itself the head of a UD `vocative`-tagged span, OR the surrounding predication satisfies R15's true-vocative test). If yes, R22 MUST NOT fire — R15 wins and the appositive remains within the vocative as one indivisible address unit.

**Scope.** Applies to appositional NPs (UD `appos` relation) whose head is a divine-name referent in `DIVINE_NAME_REFERENTS` and whose appositional dependent has a head lemma in `DIVINE_TITLE_HEADS`. Both narrative third-person uses (*"his name shall be Jesus Christ, the Son of God"*) and possessive-framed uses (*"Christ, the Holy One of Israel"*) are in scope. Single-token name-with-title compounds without an `appos` relation (e.g., *"Lord God Omnipotent"* as one unitary title) fall outside R22 — they are governed by R18 (fixed-idiom integrity) when the compound is lexicalized.

**Exclusions (closed list — each cites dominating rule).**

1. Divine-title appositive within a vocative environment (head of `appos` is also head of a `vocative`-tagged span, OR matrix predication satisfies R15's true-vocative test) → R15 (vocative indivisibility wins; appositive merges into vocative as one unit).
2. Single-token compound title without `appos` relation (e.g., *"Lord God Omnipotent"*, *"Lord of Sabaoth"* parsed as one lexicalized NP) → R18 (fixed-idiom integrity).
3. AICTP-frame-internal appositive (the appositional span occurs inside the AICTP token sequence) → R1 (AICTP integrity — the token sequence stays whole).
4. Date-colophon-frame-internal appositive (rare; the appositive occurs inside a date-colophon span) → R23 (date colophon integrity).
5. Same-passage repeated invocation already settled as MERGE earlier in the passage → boundary-case discipline (uniform treatment within one rhetorical beat; the first instance's classification governs subsequent instances in the same passage).
6. Same-passage repeated invocation already settled as STACK earlier in the passage → boundary-case discipline (uniform treatment; first instance governs).

**Precedence.** §3.5 Tier 5. Yields to R15 in vocative environment. Yields to R1/R18/R23 when the appositive falls inside a Tier-2 lexicalized closed-list span. Does NOT engage the §1.9 N=2 Adjudication Principle — appositional constructions are explicitly excluded from §1.9 (the synonymy test would mechanically fire "merge" on every appositive, which is the inverse of the rule's INTRODUCING/REFERENCING discrimination).

**Examples.**

- *Compliant (STACK — formal naming formula anchor):* "his name shall be Jesus Christ, / the Son of God" (2 Ne 25:19)
- *Compliant (STACK — prophetic proclamation frame anchor):* (a first-occurrence revelatory frame where the title appositive earns its own line)
- *Compliant (MERGE — REFERENCING default, no anchor):* "I am a disciple of Jesus Christ, the Son of God" (3 Ne 5:13)
- *Non-compliant (STACK split fired without any formal anchor):* "I am a disciple of Jesus Christ, / the Son of God" (REFERENCING context; the stack split is wrong because no anchor licenses it)
- *Non-compliant (MERGE retained despite formal naming formula anchor):* "his name shall be Jesus Christ, the Son of God" (the formal naming formula licenses STACK; merging is the violation)
- *Excluded by R15 (vocative environment):* "O God, the Eternal Father," (Moroni 4:3, 5:2 sacrament prayers; appositive merges into vocative as one indivisible address unit)
- *Excluded by R18 (fixed idiom):* "Lord God Omnipotent" (single lexicalized compound, no `appos` relation)
- *Excluded by uniform-treatment discipline:* a second invocation of *"Jesus Christ, the Son of God"* within the same rhetorical passage that opened with the MERGE-treatment must MERGE; the boundary case forbids oscillation within one passage.

**Implementation.**

- Validator: (not yet implemented — Category B; filename follows the validate_rule_{id}_ud.py convention)
- Applier: (not yet implemented — Category B; filename follows the validate_rule_{id}_ud.py convention)
- Closed-list definitions: §Divine-Title-Closed-Lists-R22 (in BoFM canon, supplementary section — to be created during validator implementation)
- Audit trail: `readers-bofm/private/audit-trail/R22.md` (to be populated during BoFM canon migration)
- Scholarship: [`atu-method/scholarship/bofm/R22.md`](atu-method/scholarship/bofm/R22.md)

<!-- ===== R23 ===== -->
### R23: Date Colophon Integrity

**Status:** Active
**Category:** A (Mechanical, mandatory)
**Decidability:** Surface-pattern
**Layer:** 3

**Rule.** A token sequence matching any member of the closed list §Date-Colophons-R23 MUST be kept whole on a single v2-mine line. No line break MAY occur internal to a matched date-colophon span, regardless of resulting line length. When the matched span occupies its own line as a fronted or trailing temporal adjunct of an adjacent matrix predication, that own-line treatment is licensed by J5 (substantive adjunct as own focus) and does not affect R23's internal-indivisibility mandate.

**UD signature.**
~~~yaml
trigger:
  surface_pattern: DATE_COLOPHONS_R23
  match: contiguous_token_sequence
  anchor: { form_lower: "in", followed_by: { form_lower: "the", within: 1 } }
  spine: { ordinal_or_number_word_within: 4, then: { form_lower: "year" } }
action: KEEP_WHOLE
~~~

**Closed lists** (machine-readable).
~~~yaml
DATE_COLOPHONS_R23:
  - "in the <ordinal> year of the reign of the judges"
  - "in the <ordinal> year of the reign of king <name>"
  - "in the <ordinal> year since Lehi left Jerusalem"
ORDINAL_FORMS_R23:
  - first
  - second
  - third
  - fourth
  - fifth
  - sixth
  - seventh
  - eighth
  - ninth
  - tenth
  - eleventh
  - twelfth
  - thirteenth
  - fourteenth
  - fifteenth
  - sixteenth
  - seventeenth
  - eighteenth
  - nineteenth
  - twentieth
  - twenty
  - thirtieth
  - thirty
  - fortieth
  - forty
  - fiftieth
  - fifty
  - sixtieth
  - sixty
  - seventieth
  - seventy
  - eightieth
  - eighty
  - ninetieth
  - ninety
  - hundredth
  - hundred
NUMBER_WORDS_R23:
  - one
  - two
  - three
  - four
  - five
  - six
  - seven
  - eight
  - nine
  - ten
  - eleven
  - twelve
  - thirteen
  - fourteen
  - fifteen
  - sixteen
  - seventeen
  - eighteen
  - nineteen
  - twenty
  - thirty
  - forty
  - fifty
  - sixty
  - seventy
  - eighty
  - ninety
  - hundred
COMPOUND_ORDINAL_PATTERN:
  - "<number-word> and <ordinal>"   # e.g., "forty and second"
~~~

The closed list admits compound-ordinal variants of the form *"<number-word> and <ordinal>"* (e.g., *"forty and second year"*, *"twenty and seventh year"*). The detector spine — *in the [number-word and] <ordinal> year* — anchors all variants.

**Scope.** Multi-word date-colophon formulas in the BoFM register that timestamp narrative events. Operational boundary: the matched span begins at the anchor token *in* and ends at the formula's final token (*judges*, *king <name>*, or the token following *since*). Span-internal token order is fixed; no inflectional, ellipsis, or word-order variants are recognized as members. R23 governs the formula's internal indivisibility only; the formula's external boundary (whether it earns its own line as a fronted/trailing temporal PP) is governed by J5.

**Exclusions (closed list — each cites dominating rule).**

1. Non-date temporal PPs (*"in those days"*, *"in the days of"*, *"at that time"*) — not date-colophon formulas; governed by general PP break legality (Layer 1) and J5 at the line-boundary level.
2. Bare *"the Nth year"* anaphoric references without the *in the* anchor and without the *of the reign* / *since* continuation — surface-pattern does not match; outside R23's closed list.
3. AICTP formula's leftward token span (*And it came to pass*) when adjacent to a date-colophon → R1 (governs the AICTP span; R23 governs the date-colophon span; the two formulas coexist on the same line under their respective KEEP_WHOLE mandates, separated by the trailing-*that* per R16).
4. *it is expedient that* and other fixed idioms when adjacent to a date-colophon → R18 (governs the idiom span; R23 governs the date-colophon span; coexist on the same line).
5. Own-line placement of the date-colophon as a fronted temporal adjunct (e.g., *"in the forty and second year of the reign of the judges, / they came down..."*) → J5 (substantive adjunct as own focus; R23's internal-indivisibility mandate is preserved, the J5 own-line treatment applies at the formula's external boundary).

**Precedence.** §3.5 Tier 2. Indivisibility tier; wins over all subtractive vetoes and merge-overrides at the formula-internal level. Coexists with R1, R15, R16, R18 in Tier 2 (each governs a distinct closed-list span).

**Examples.**

- *Compliant:* "in the forty and second year of the reign of the judges" (formula whole on one line)
- *Compliant:* "in the seventh year of the reign of king Mosiah" (formula whole on one line)
- *Compliant:* "in the eighth year since Lehi left Jerusalem" (variant formula whole on one line)
- *Compliant (J5 own-line):* "And it came to pass / in the forty and ninth year of the reign of the judges, / there was continual peace established in the land" (R1 governs AICTP span; R23 keeps date-colophon whole; J5 earns it its own line)
- *Non-compliant:* "in the forty and second year / of the reign of the judges" (formula severed)
- *Non-compliant:* "in the seventh year of the reign / of king Mosiah" (formula severed)
- *Non-compliant:* "in the eighth year / since Lehi left Jerusalem" (variant formula severed)
- *Excluded by R1:* "And it came to pass / in the forty and second year of the reign of the judges..." (left-boundary break is between R1's span and R23's span, not internal to either)
- *Excluded by J5:* the date-colophon as its own line (the own-line is a J5 license, not an R23 violation; R23 cares only about internal indivisibility)

**Implementation.**

- Validator (surface-pattern): [`validators/colometry/validate_rule_23_date_colophon.py`](../../../../readers-bofm/validators/colometry/validate_rule_23_date_colophon.py)
- Validator (UD-query): [`validators/colometry/validate_rule_23_ud.py`](../../../../readers-bofm/validators/colometry/validate_rule_23_ud.py)
- Applier: (none — surface-pattern keep-whole; corpus is hand-authored at this granularity, validators report violations)
- Closed-list definitions: §Date-Colophons-R23 (in BoFM canon, supplementary section)
- Audit trail: `readers-bofm/private/audit-trail/R23.md` (to be populated during BoFM canon migration)
- Scholarship: [`atu-method/scholarship/bofm/R23.md`](atu-method/scholarship/bofm/R23.md)

<!-- ===== R26 ===== -->
### R26: Adjective (or NOUN-as-Predicate) + "That" Complement Stays Together

**Status:** Active
**Category:** A (Mechanical, mandatory)
**Decidability:** UD-pattern
**Layer:** 3

**Rule.** A predicate complement-taker's clausal *that*-complement MUST be on the same v2-mine line as its predicate head when the head lemma belongs to one of the two closed lists below. The ADJ-predicate sub-class fires when the head UPOS is `ADJ` and the lemma is in `R26_ADJ_PREDICATES`. The NOUN-as-predicate sub-class fires when the head UPOS is `NOUN`, the lemma is in `R26_NOUN_PREDICATES`, and the head bears a copular dependent (`cop`) plus an `acl` *that*-clause. When the LLM annotator tags the *that*-clause as `advcl` but the matrix head lemma is in either closed list, the annotation MUST be overridden and treated as `ccomp` (ADJ branch) or `acl` (NOUN branch) for purposes of this rule.

**UD signature.**
```yaml
trigger_adj_predicate:
  relation: ccomp
  head: { upos: ADJ, lemma_in: R26_ADJ_PREDICATES }
  mark: { lemma: that }
action: MERGE_HEAD_AND_DEPENDENT

trigger_noun_as_predicate:
  relation: acl
  head: { upos: NOUN, lemma_in: R26_NOUN_PREDICATES }
  cop: { lemma_in: [be] }
  mark: { lemma: that }
action: MERGE_HEAD_AND_DEPENDENT
```

**Closed lists** (machine-readable).
```yaml
R26_ADJ_PREDICATES:
  - possible
  - expedient
  - desirous
  - necessary
  - needful
  - impossible
  - better
  - well
  - requisite

R26_NOUN_PREDICATES:
  - wisdom
```

**Scope.** Predicate complement-taker frames of the form *it is X that Y* (and minor inversions, e.g., *X it is that Y*) where X is the head lemma. The rule governs the outer boundary between the predicate head and its *that*-clause. Internal structure of the *that*-clause is evaluated separately. Matrix VERB heads are out of scope (route to R17). Matrix NOUN heads not in `R26_NOUN_PREDICATES` are out of scope.

**Exclusions (closed list — each cites dominating rule).**

1. AICTP *that* — token sequence "And it came to pass that" → R1 / R16
2. Vocative on matrix line — vocative wins its own-line mandate → R15
3. Compound subordinator *insomuch that* — mark is the compound, not simple *that* → R27
4. Direct discourse (colon-terminated speech-tag introducing the *that*-clause as quotation onset) → J3
5. *for*-infinitive frame instead of finite *that*-complement (e.g., *it is meet for X to Y*) — not a R26 trigger; out of scope
6. Head lemma in `R26_NOUN_PREDICATES` used as noun-modifier rather than predicate (no `cop` dependent on the head) — out of scope; R26 does not fire

**Precedence.** §3.5 Tier 3. Wins over R7 (purpose) and R17 (verb-complement) when the matrix head is ADJ in `R26_ADJ_PREDICATES` or NOUN in `R26_NOUN_PREDICATES`. Yields to Tier 1 (Layer 1 mid-phrase prohibitions), Tier 2 (R1 / R16 AICTP, R15 vocative, R18 fixed idiom, R23 date colophon), and J3 direct-discourse onset.

**Examples.**

- *Compliant (ADJ predicate, MERGE):* "if it were possible that our first parents..."
- *Compliant (ADJ predicate, MERGE):* "it is expedient that ye should know the things..."
- *Compliant (NOUN-as-predicate, MERGE):* "it is wisdom in God that these things should be shown unto you..."
- *Non-compliant (R26 violation):* "if it were possible / that our first parents..." (matrix predicate severed from *that*-complement)
- *Excluded by R7 (matrix VERB, out of R26 scope):* "he went forth among the people / that he might preach the word of God" — matrix is VERB; R7 governs
- *Excluded by R17 (matrix VERB, out of R26 scope):* "I say unto you that the time shall come" — matrix is VERB in R17 governing class
- *Excluded by R15 (vocative wins):* a vocative on the matrix line keeps the vocative on its own atomic-thought unit per R15
- *Excluded (out of scope — for-infinitive frame):* *it is meet for X to Y* — non-finite *for*-infinitive, not a finite *that*-complement; R26 does not fire

**Implementation.**

- Validator: [`validators/colometry/validate_rule_07_ud.py`](../../../../readers-bofm/validators/colometry/validate_rule_07_ud.py) (R26 routing applied via `RULE_26_HEAD_LEMMAS` set + `is_rule_26_class` filter — Rule 7 detector routes R26-class matches away from R7)
- Applier: shares R7 applier pipeline; R26-class matches resolve to MERGE rather than SPLIT
- Closed-list definitions: in validator source (`RULE_26_HEAD_LEMMAS`)
- Audit trail: `readers-bofm/private/audit-trail/R26.md` (to be populated during BoFM canon migration)
- Scholarship: [`atu-method/scholarship/bofm/R26.md`](atu-method/scholarship/bofm/R26.md)

<!-- ===== R27 ===== -->
### R27: "Insomuch That" Binding

**Status:** Proposed
**Category:** A (Mechanical, mandatory)
**Decidability:** UD-pattern
**Layer:** 3

**Rule.** A consecutive-result clause introduced by the compound subordinator *insomuch that* attaching as `advcl` to its matrix MUST be split from the matrix by default. The merge MAY be applied only when **all three** conditions hold: (1) the result clause is ≤ 8 non-PUNCT word tokens; (2) the result clause's subject is co-referential with the matrix subject (`nsubj` of advcl equals `nsubj` of matrix, or the result-clause subject is elided and co-referential); and (3) no camera-angle shift occurs across the boundary (single-image diagnostic passes). When any condition fails, the break MUST be inserted before the *insomuch that* mark.

**UD signature.**
```yaml
trigger:
  relation: advcl
  mark: { lemma_in: INSOMUCH_THAT_MARK_PATTERNS }
default_action: SPLIT_BEFORE_MARK
merge_action: MERGE_HEAD_AND_DEPENDENT  # gated by all three conditions
merge_conditions:
  - word_count: { subtree: result_clause, exclude_punct: true, max: 8 }
  - subject_continuity: { nsubj_advcl: { equals_or_elided_coref: nsubj_matrix } }
  - camera_angle_shift: false
```

**Closed lists** (machine-readable).
```yaml
INSOMUCH_THAT_MARK_PATTERNS:
  # Compound subordinator; UD tokenizes in two patterns
  # Pattern A: insomuch=ADV/advmod + that=SCONJ/mark, both children of advcl head
  # Pattern B: insomuch=ADV/mark + that=SCONJ/fixed(head=insomuch)
  # Plus rare single-MWE token form
  - "insomuch that"
  - "insomuch + that"

CO_REF_PRONOUNS:
  - he
  - she
  - they
  - it
  - i
  - we
  - his
  - her
  - their
  - its
  - my
  - our
  - him
  - them
  - us
  - me
  # archaic BofM second-person
  - ye
  - thee
  - thou
  - thy
  - thine

ELIDED_SUBJECT_VERBS:
  - did
  - was
  - were
  - had
  - could
  - might
  - would
  - shall
  - will
  - hath
  - doth
  - art
  - am
  - are
  - began
  - fell
  - came
  - went
  - cried
  - spake
  - led
  - brought
  - felt
  - smote
  - became

EXPLETIVE_THERE_VERBS:
  - was
  - were
  - is
  - are
  - arose
  - came
  - stood
  - dwelt
  - shall
  - never
  - had
  - hath
  - began
```

**Scope.** Compound subordinator *insomuch that* in `advcl` attachment to its matrix. Simple `mark=that` cases are outside R27 territory (route to R7, R17, R19, or R26 per the §3.5.1 *that*-cluster precedence). The rule governs the OUTER boundary between the result clause and its matrix only; once that boundary is resolved, internal structure of the result clause is evaluated separately against J1–J5 (framework §1.4) — notably J5 (fronted substantive temporals/locatives/causals) and J1 (parallel series within the result) can license breaks INSIDE the merged unit.

**Exclusions (closed list — each cites dominating rule).**

1. Expletive-*there* + new-entity semantic subject (*there were many slain*, *there were thousands converted*) — condition 2 evaluated against the semantic subject (NP following *there were*); new-entity semantic subjects fail condition 2 → default SPLIT (per this rule's own expletive-*there* sub-clause)
2. Chained *insomuch that* clauses without coordinating conjunction — each subordinator introduces a fresh finite predication with its own degree-specification; default SPLIT each, applying the 3-condition merge test pairwise against the immediate antecedent (per this rule's own chained-*insomuch* sub-clause; canonical case Alma 24:2)
3. Result-clause internal structure firing J5 substantive adjunct or J1 parallel series — those breaks fire INSIDE the merged unit and are NOT excluded from R27; R27's outer-boundary verdict (merge) stands → framework `§1.4`
4. Layer 1 mid-phrase prohibition firing on the merge target (line-final CCONJ / DET / AUX / ADP after merge) → R9 / R10 / R11 / R12 / R13a (Tier 1 always wins)
5. AICTP closed token sequence overlap → R1 (Tier 2)

**Sub-clauses (operational).**

- **Expletive-*there* sub-clause.** When the result clause begins with expletive *there* + BE-verb (*there was*, *there were*, *there is*, *there are*, *there came*), condition 2 is evaluated against the **semantic subject** (the NP following the BE-verb), not the expletive. New-entity semantic subjects fail condition 2 → default SPLIT. Rare continuing-entity semantic subjects (*there was the same man as before*) MAY pass condition 2; in those cases condition 1 (word count) is typically decisive.

- **Chained *insomuch that* sub-clause.** When two or more *insomuch that* clauses chain asyndetically (no coordinating conjunction between them), default SPLIT each. The 3-condition merge test still applies pairwise — each *insomuch that* against its immediate antecedent, not against the top-level matrix. Camera angle typically shifts with each degree-intensification, so chained instances rarely pass all three conditions pairwise.

**Precedence.** §3.5 Tier 5. Wins over R7 when the subordinator is the compound *insomuch that* (R7's UD signature requires simple `mark=that`; the compound subordinator is its own mark, and the modal in *insomuch that + MODAL* belongs to consecutive-result semantics rather than purposive telic semantics). Yields to Tier 1 Layer 1 syntax vetoes (R9, R10, R11, R12, R13a), Tier 2 indivisibility/formula (R1, R15, R16, R18, R23), and Tier 0 input filters.

**Examples.**

- *Compliant (SPLIT — default):* "And he did minister unto them, / insomuch that his whole household were converted unto the Lord." (Alma 22:23) — result clause 9 words, new subject, camera shift
- *Compliant (SPLIT — chained insomuch):* "And their hatred became exceedingly sore against them, / even insomuch that they began to rebel against their king, / insomuch that they would not that he should be their king" (Alma 24:2) — three lines, each atomic
- *Compliant (MERGE — all three conditions hold):* "...insomuch that they were sore amazed" — result clause ≤8 words, subject elided and co-referential, no camera shift
- *Non-compliant (R27 violation — default SPLIT not applied where conditions fail):* "And he did minister unto them insomuch that his whole household were converted unto the Lord" — matrix and consecutive-result frame collapsed despite condition 1 failure (9 words) and condition 2 failure (new subject)
- *Excluded by expletive-*there* sub-clause (default SPLIT):* "...insomuch that there were many slain" — condition 2 evaluated against semantic subject *many slain* (new entity) → fails
- *Excluded by R7 yields-to:* none — when the compound mark is *insomuch that*, R27 governs (R7 yields, per §3.5 Tier 5)

**Implementation.**

- Validator (UD): [`validators/colometry/validate_rule_27_ud.py`](../../../../readers-bofm/validators/colometry/validate_rule_27_ud.py)
- Validator (regex precursor): [`validators/colometry/validate_rule_27_insomuch_that.py`](../../../../readers-bofm/validators/colometry/validate_rule_27_insomuch_that.py)
- Applier: [`validators/apply_rule_27_ud.py`](../../../../readers-bofm/validators/apply_rule_27_ud.py)
- Closed-list definitions: in validator source (`CO_REF_PRONOUNS`, `ELIDED_SUBJECT_VERBS`, `NEW_NP_STARTERS`, `EXPLETIVE_THERE_VERBS`)
- Audit trail: `readers-bofm/private/audit-trail/R27.md` (to be populated during BoFM canon migration)
- Scholarship: [`atu-method/scholarship/bofm/R27.md`](atu-method/scholarship/bofm/R27.md)

<!-- ===== R28 ===== -->
### R28: Speech-Act Announcement After Frame

**Status:** Active
**Category:** A (Mechanical, mandatory)
**Decidability:** UD-pattern
**Layer:** 3

**Rule.** A speech verb's matrix predication (subject + finite speech verb + colon-introduced quote) MUST be split from a preceding scene-setting adverbial frame when (a) the speech verb's lemma is in `SPEECH_LEMMAS_R28`, (b) the verb carries an `nsubj` dependent, and (c) the verb has an `advcl` sibling (or direct `advcl` dependent) whose mark lemma is in `FRAME_MARK_LEMMAS`. The break MUST be inserted before the leftmost non-PUNCT token of the speech-clause subtree that follows the rightmost advcl-subtree token on the line; any trailing frame-closing comma stays on the frame line. Participial speech-continuation advcl (`saying`-headed) and result/comparative advcl MUST NOT trigger this rule.

**UD signature.**
```yaml
trigger:
  relation: advcl                # advcl as sibling-of or dependent-of the speech verb
  head: { upos: VERB, lemma_in: SPEECH_LEMMAS_R28 }
  head_deps: { nsubj: required }
  mark: { lemma_in: FRAME_MARK_LEMMAS }
action: SPLIT_BEFORE_SUBJECT
```

**Closed lists** (machine-readable).
```yaml
SPEECH_LEMMAS_R28:
  - say
  - speak
  - declare
  - cry
  - answer

FRAME_MARK_LEMMAS:
  - after
  - when
  - while
  - before
  - since
  - until
  - because
  - though
  - although
  - lest
  - except

ADVCL_EXCLUDED_LEMMAS:        # participial speech-continuation, not a frame
  - say                       # surface form "saying"

RESULT_MARK_LEMMAS:           # consequence-not-frame when speech precedes advcl
  - that
  - insomuch
  - until
```

**Scope.** Same-line co-occurrence of a matrix speech-VERB (with `nsubj`) and a genuine scene-setting frame-advcl on a single v2-mine line. The detector compares the v2-mine line of the speech VERB to the line of the advcl root; only same-line co-occurrence (verb_line == advcl_line) is in scope. Speech verbs as parataxis dependents of the AICTP "pass" verb are in scope — Rule 28 applies regardless of whether the speech verb is the sentence root or a parataxis dependent.

**Exclusions (closed list — each cites dominating rule).**

1. Participial speech-continuation `, saying:` — advcl lemma in `ADVCL_EXCLUDED_LEMMAS`; not a scene-setting frame → out of scope.
2. Comparative `as if` advcl (both *as* and *if* present as marks) — comparative clause, not a scene frame → out of scope.
3. Result-direction inversion: speech verb token id < advcl token id AND mark lemma in `RESULT_MARK_LEMMAS` — the advcl is a consequence of the speech act, not a frame preceding it → out of scope.
4. Bare `aux:pass` participial advcl without temporal/locative mark AND without true-absolute construction (own `nsubj` differing from the matrix `nsubj`) — manner-circumstantial, not a frame → out of scope.
5. No-clean-split-col case: speech-tag structurally inside (or before) the advcl on the line, with no non-PUNCT speech-only token following `advcl_end_id` → REVIEW-REQUIRED (not auto-applied).
6. Direct discourse already on its own line (verb_line ≠ advcl_line) — already conformant; no split needed.

**Precedence.** §3.5 Tier 5. Co-instantiates J3 (speech-act announcement) at the matrix-predication level. No yields-to relationships against higher-tier rules are known to fire on the same trigger.

**Examples.**

- *Compliant (SPLIT):* "And it came to pass that after Aaron had expounded these things unto him, / the king said:" (Alma 22:15) — frame *after Aaron had expounded these things unto him,* ends with comma on the frame line; matrix *the king said:* begins the next line.
- *Compliant (saith-the-Lord parenthetical authentication-stamp):* "for I have a great work to do, / saith the Lord" — speech tag on its own line after intervening matrix.
- *Non-compliant (R28 violation — frame and speech-tag merged):* "And it came to pass that after Aaron had expounded these things unto him, the king said:" (single line — frame and announcement on the same v2-mine line).
- *Excluded by Exclusion 1 (saying-continuation, MERGE):* "he spake unto them, saying:" — *saying* is a participial speech-continuation marker, not a scene-setting frame.
- *Excluded by Exclusion 3 (result-direction inversion):* "I did speak many words unto them, / that they were pacified" — speech verb precedes advcl and mark is *that* (result); the advcl is the consequence of the speech act, not its frame.
- *Excluded by Exclusion 4 (manner-circumstantial passive):* "being filled with the Spirit, he spake" — bare `aux:pass` participial advcl without temporal/locative mark and without distinct own-subject; manner-circumstantial, not a frame → out of R28 scope.
- *Excluded by Exclusion 5 (REVIEW-REQUIRED):* "Ye cannot say, when ye are brought to that awful crisis," (Alma 34:34) — speech-tag is structurally inside the advcl; no clean split column.

**Implementation.**

- Validator: [`validators/colometry/validate_rule_28_ud.py`](../../../../readers-bofm/validators/colometry/validate_rule_28_ud.py)
- Applier: [`validators/apply_rule_28_ud.py`](../../../../readers-bofm/validators/apply_rule_28_ud.py)
- Closed-list definitions: in validator source (`SPEECH_LEMMAS`, `FRAME_MARK_LEMMAS`, `ADVCL_EXCLUDED_LEMMAS`, `RESULT_MARK_LEMMAS`)
- Char-offset emission: detector emits `split_col` via `build_line_map_full`; applier inserts the break before `split_col` (T1.1 char-offset pattern).
- Audit trail: `readers-bofm/private/audit-trail/R28.md` (to be populated during BoFM canon migration)
- Scholarship: [`atu-method/scholarship/bofm/R28.md`](atu-method/scholarship/bofm/R28.md)

<!-- ===== EP-1 ===== -->
### EP-1: "According To" Manner vs. Source

**Status:** Active
**Category:** B (Editorial, judgment-required)
**Decidability:** Discourse-context-needed
**Layer:** 3

**Rule.** When a PP headed by *according to* attaches to a matrix predication as `obl` or `advmod` and Tiers 1-6 leave the break decision open, the PP's semantic function SHOULD determine the break:

- *Manner* reading (the PP answers HOW the action was done — describing the mechanism, style, measure, or conformity of the act) → MERGE the PP with its matrix predication.
- *Source / authority* reading (the PP answers BY WHAT POWER or FROM WHAT SOURCE the action occurs — naming an independent locus of authorization, divine commission, or external warrant) → SPLIT the PP onto its own line.

When the reading is genuinely ambiguous between manner and source/authority and no discourse cue resolves it, the case SHOULD route to REVIEW and MUST NOT be auto-applied. EP-1 is a Category B editorial tiebreaker; it does not authorize mechanical application without per-case judgment.

**UD signature.**
~~~yaml
trigger:
  relation: [obl, advmod]
  case: { lemma: "according to" }  # multi-word preposition
  head: { upos: [VERB, AUX] }
action: REVIEW
~~~

*Note:* The UD signature identifies *candidate* locations only. The manner-vs-source disambiguation is not mechanically decidable from the parse — it requires reading the PP's complement against the matrix predication's discourse frame. The validator surfaces candidates; an editor applies the diagnostic.

**Diagnostic (per-case judgment).**

1. **Substitute test.** Paraphrase the PP with "in the manner of X" (manner reading) vs. "by the authority of X" / "as authorized by X" (source reading). The paraphrase that preserves meaning identifies the function.
2. **Complement-noun class.** Source/authority readings cluster on complement nouns naming an agent, faculty, or warrant (*the Spirit*, *the workings of the Spirit*, *the power of God*, *the spirit which is in me*, *the feelings of his heart*). Manner readings cluster on complement nouns naming a standard, measure, or instruction (*his word*, *their faith*, *his memory*, *my plainness*, *their time*).
3. **Independence test.** Can the *according to* PP stand as an independent theological/factual assertion the matrix presupposes? If yes → source. If the PP only specifies HOW the matrix predication unfolds → manner.

If diagnostic 1-3 do not converge, route to REVIEW.

**Closed lists** (machine-readable; non-exhaustive — heuristic, not gating).
~~~yaml
SOURCE_AUTHORITY_INDICATORS:
  # Complement-NP heads that typically signal source/authority reading
  - spirit
  - power
  - will
  - workings
  - faith        # context-sensitive: "manifest according to their faith" is manner-mechanism, "given according to their faith" is source
  - commandments
  - covenant

MANNER_INDICATORS:
  # Complement-NP heads that typically signal manner reading
  - word
  - time
  - memory
  - plainness
  - manner
  - custom
~~~

*Closed lists are heuristic indicators that focus editorial attention; they are NOT decision-gating. A SOURCE_AUTHORITY_INDICATORS hit MAY still be a manner reading in context, and vice versa. The diagnostic above is the authoritative test.*

**Scope.** PPs surface-headed by the multi-word preposition *according to* (or its closed orthographic variants — *according unto* in archaic register), attaching to a matrix predication via `obl` or `advmod`. EP-1 fires only when Tiers 1-6 (Layer 1 vetoes, formula/vocative integrity, complement integrity, merge-overrides, split-triggers, N=2 adjudication) have not already settled the break. EP-1 is a Tier 7 post-hoc editorial tiebreaker, not a generator or veto.

**Exclusions (closed list — each cites dominating rule).**

1. *According to* PP inside a vocative environment → R15 (vocative indivisibility wins).
2. *According to* PP inside an AICTP formula span → R1 (formula integrity wins; PP follows formula on its own line if substantive, per J5).
3. *According to* PP that itself constitutes a J5 substantive adjunct slot-filler (its own when/where/why frame, fronted or trailing) → J5 (Tier 5 split-trigger wins before EP-1 is consulted).
4. *According to* PP coordinated as one member of a J1 formally-marked parallel series → J1 (Tier 5).
5. *According to* PP whose complement is a bare proper noun naming a textual reference (*according to the record of Alma*) and the PP attaches as parenthetical attribution → out of scope; treated under J3 / Rule 22-class textual-attribution patterns rather than EP-1.

**Precedence.** §3.5 Tier 7. Fires only after Tiers 1-6 settle. Yields to all higher tiers without exception (Tier 7 is post-hoc by construction — see §3.5 and §1.8 Step 4). No EP-1 cross-rule precedence is asserted within Tier 7; EP-1 and the other EP-rules / image-test are co-equal tiebreakers within the tier.

**Examples.**

- *Compliant (manner — MERGE):* "spoke unto them, according to his word." (PP specifies HOW the speaking conformed — manner adverbial, manner-mechanism reading, merge with matrix.)
- *Compliant (manner — MERGE):* "proceed with mine own prophecy, according to my plainness." (PP specifies the style of delivery — manner.)
- *Compliant (manner — MERGE):* "the king answered him not for the space of an hour, according to their time." (PP specifies the measure standard — manner-conformity reading.)
- *Compliant (source — SPLIT):* "it whispereth me, / according to the workings of the Spirit of the Lord." (PP names the source of the whispering — independent theological assertion, own line.)
- *Compliant (source — SPLIT):* "I give unto you a prophecy, / according to the spirit which is in me." (PP names the prophetic authorization — source.)
- *Compliant (source — SPLIT):* "had spoken unto all his household, / according to the feelings of his heart and the Spirit of the Lord." (PP names the dual source — own line.)
- *Ambiguous → REVIEW:* "manifest unto the children of men, according to their faith." (Reading 1: manner-mechanism — faith is the mechanism by which manifestation occurs. Reading 2: source — faith is the warrant. Diagnostic 1-3 do not cleanly converge; route to REVIEW.)
- *Excluded by J5:* "according to the workings of the Spirit of the Lord, / it whispereth me..." (Fronted-PP substantive temporal/causal slot-filler; J5 wins at Tier 5 before EP-1 is consulted.)
- *Excluded by R15:* "O Lord God, according to thy will, / hear my prayer." (PP inside vocative environment; R15 vocative integrity wins.)
- *Non-compliant (manner mis-split):* "spoke unto them, / according to his word." (Manner reading split as if source — punctuation-artifact break; mechanism-not-warrant test should have merged.)

**Implementation.**

- Validator: (not yet implemented) [to be implemented — surfaces *according to* PP candidates; emits REVIEW-REQUIRED for editorial disposition].
- Applier: none (Category B; auto-applier MUST NOT exist for EP-1; editorial-judgment required per-case).
- Closed-list definitions: §EP-1-Indicators (in BoFM canon, supplementary section — heuristic indicators only).
- Audit trail: `readers-bofm/private/audit-trail/EP-1.md` (to be populated during BoFM canon migration).
- Scholarship: [`atu-method/scholarship/bofm/EP-1.md`](atu-method/scholarship/bofm/EP-1.md).

---


<!-- ===== EP-3 ===== -->
### EP-3: Inverted Predicate

**Status:** Active
**Category:** B (Editorial, judgment-required)
**Decidability:** Discourse-context-needed
**Layer:** 3

**Rule.** When a copular construction surfaces with its predicate complement (ADJ, NOUN, or participial) fronted before its subject — producing the marked word-order *Pred + Cop + Subj* rather than the default *Subj + Cop + Pred* — and Tiers 1-6 leave the break decision open, the inverted predicate construction SHOULD earn its own line (SPLIT before the inverted predicate, or render the whole inverted construction as a single own-line ATU when the construction is short and bonded). Cases where the inversion is the rhetorical device SHOULD be revealed by the line break; cases where the inversion is grammatically forced (e.g., interrogative inversion, presentational *there is*) MUST NOT be treated as EP-3 candidates. When the inversion's rhetorical force is genuinely indeterminate, the case SHOULD route to REVIEW and MUST NOT be auto-applied. EP-3 is a Category B editorial tiebreaker; it does not authorize mechanical application without per-case judgment.

**UD signature.**
~~~yaml
trigger:
  relation: [cop]
  head: { upos: [ADJ, NOUN, VERB] }   # the predicate complement, fronted
  subject:
    relation: nsubj
    linear_order: after_head           # subject follows the predicate-head in surface order
action: REVIEW
~~~

*Note:* The UD signature identifies *candidate* locations only. The rhetorical-device-vs-grammatical-inversion disambiguation is not mechanically decidable from the parse — it requires reading the inversion against the matrix's discourse frame and against the inventory of grammatically-forced inversions in the corpus's register. The validator surfaces candidates; an editor applies the diagnostic.

**Diagnostic (per-case judgment).**

1. **Normal-order paraphrase test.** Re-order the construction to default *Subj + Cop + Pred* (e.g., *"Great is my joy"* → *"My joy is great"*; *"Blessed are they who repent"* → *"They who repent are blessed"*). If the paraphrase loses rhetorical emphasis, marked focus, or formulaic resonance, the inversion is the device — EP-3 fires. If the paraphrase reads as natural or equivalent, the inversion is grammatically incidental and EP-3 does NOT fire.
2. **Formulaic-frame check.** The inverted predicate often instantiates a recognized formula type (beatitude *"Blessed are…"*, woe *"Wo unto…"* in copular variants, exclamatory *"Great is…"* / *"Marvelous are…"*, prophetic *"Cursed is…"*). When the construction matches a formula type, EP-3 fires by default.
3. **Grammatical-forcing exclusion.** Confirm the inversion is NOT one of: interrogative inversion (*"Is it not…"*), presentational *there is/are* construction, conditional-protasis inversion (*"Were it not for…"*), or a relative-clause-internal inversion driven by extraction. These are syntactically obligatory rather than rhetorically marked; EP-3 does NOT fire.

If diagnostic 1-3 do not converge, route to REVIEW.

**Closed lists** (machine-readable; non-exhaustive — heuristic, not gating).
~~~yaml
EP_3_FORMULAIC_PREDICATES:
  # Predicate heads that, when fronted in a copular construction, typically signal an EP-3 inversion
  - blessed
  - cursed
  - great
  - greater
  - holy
  - marvelous
  - wonderful
  - mighty
  - awful
  - long              # "long was the time…"
  - better
  - good

EP_3_GRAMMATICAL_FORCING_EXCLUSIONS:
  # Surface patterns whose inversion is grammatically forced — NOT EP-3 territory
  - interrogative_inversion       # "Is it not…", "Are ye not…"
  - presentational_there          # "There is a God", "There are many"
  - conditional_protasis          # "Were it not for…", "Had I not…"
  - relative_internal_inversion   # extraction-driven within a relative clause
~~~

*Closed lists are heuristic indicators that focus editorial attention; they are NOT decision-gating. A fronted predicate not in `EP_3_FORMULAIC_PREDICATES` MAY still be an EP-3 inversion. The diagnostic above is the authoritative test.*

**Scope.** Copular constructions in v2-mine where the predicate complement (ADJ, NOUN, or participial) surfaces in linear position before its subject NP, and where the inversion is not one of the closed-list grammatically-forced patterns. EP-3 fires only when Tiers 1-6 (Layer 1 vetoes, formula/vocative integrity, complement integrity, merge-overrides, split-triggers, N=2 adjudication) have not already settled the break. EP-3 is a Tier 7 post-hoc editorial tiebreaker, not a generator or veto.

**Exclusions (closed list — each cites dominating rule).**

1. Inverted predicate inside a vocative environment → R15 (vocative indivisibility wins).
2. Inverted predicate inside an AICTP formula span → R1 (formula integrity wins).
3. Inverted predicate inside a fixed idiom → R18 (idiom integrity wins).
4. Inverted predicate as one member of a J1 formally-marked parallel series at N≥3 → J1 (Tier 5 wins; e.g., a stacked beatitude chain receives J1 list-uniformity treatment, not per-member EP-3).
5. Inverted predicate inside a J3 speech-act announcement span when the announcement formula already mandates its own-line treatment → J3.
6. Grammatically-forced inversions (`EP_3_GRAMMATICAL_FORCING_EXCLUSIONS` — interrogative, presentational *there is*, conditional protasis, relative-internal extraction-driven inversion) → out of scope; EP-3 does not fire.

**Precedence.** §3.5 Tier 7. Fires only after Tiers 1-6 settle. Yields to all higher tiers without exception (Tier 7 is post-hoc by construction — see §3.5 and §1.8 Step 4). No EP-3 cross-rule precedence is asserted within Tier 7; EP-3 and the other EP-rules / image-test are co-equal tiebreakers within the tier.

**Examples.**

- *Compliant (formulaic inversion — own-line ATU):* "Blessed are ye if ye shall give heed unto the words of these twelve." (Fronted predicate adjective *blessed* + copula + subject; beatitude formula; the inversion is the rhetorical device; the whole inverted construction stands as a single own-line ATU.)
- *Compliant (formulaic inversion — own-line ATU):* "Cursed is he that putteth his trust in man." (Fronted *cursed* + copula + subject + restrictive relative; prophetic-curse formula; own line.)
- *Compliant (exclamatory inversion — own-line ATU):* "Great are the reasons which we have to mourn." (Fronted *great* + copula + subject + relative; the marked order carries the exclamatory emphasis; normal-order paraphrase *"the reasons which we have to mourn are great"* loses the emphatic force.)
- *Compliant (introducing SPLIT):* "Great is my joy, / for I have seen the Lord." (Inverted predicate construction earns its own line; the trailing *for*-clause splits per its own grounds — proposition boundary.)
- *Excluded by R15:* "O Lord God, blessed is thy name." (Inverted predicate inside vocative environment; R15 vocative integrity wins — vocative and copular-predicate render together as one vocative-anchored line per R15's treatment.)
- *Excluded by R1:* "And it came to pass that great were the trials of the people." (Inverted predicate inside AICTP formula span; R1 formula integrity wins — AICTP stays whole.)
- *Excluded by J1 (N≥3 stack):* A 9-member beatitude chain (e.g., 3 Nephi 12:3-11 Sermon-at-Bountiful beatitudes) → each *"Blessed are…"* member earns its own line per J1 (Tier 5 stack-uniformity), not per per-member EP-3 invocation. The list-uniformity treatment is the operative rule; EP-3 would have produced the same outcome but J1's precedence is what governs the stack.
- *Excluded by grammatical forcing:* "Is it not so?" (Interrogative inversion; not rhetorical predicate-fronting; EP-3 does not fire.)
- *Excluded by grammatical forcing:* "There is a God in heaven." (Presentational *there is* construction; EP-3 does not fire.)
- *Non-compliant (inversion mis-merged into trailing matter):* "great is my joy for I have seen the Lord." (Inverted predicate run together with a distinct trailing proposition; the inversion should anchor its own line.)
- *Ambiguous → REVIEW:* "long was the way which they had taken" (mid-narrative; ambiguous whether *long* is marked-focus rhetorical inversion or a grammatically unremarkable descriptive copula; diagnostic 1-3 do not cleanly converge — route to REVIEW.)

**Implementation.**

- Validator: (not yet implemented) [to be implemented — surfaces predicate-fronted copular candidates; filters `EP_3_GRAMMATICAL_FORCING_EXCLUSIONS`; emits REVIEW-REQUIRED for editorial disposition].
- Applier: none (Category B; auto-applier MUST NOT exist for EP-3; editorial-judgment required per-case).
- Closed-list definitions: §EP-3-Indicators (in BoFM canon, supplementary section — heuristic indicators only).
- Audit trail: `readers-bofm/private/audit-trail/EP-3.md` (to be populated during BoFM canon migration).
- Scholarship: [`atu-method/scholarship/bofm/EP-3.md`](atu-method/scholarship/bofm/EP-3.md).

---


<!-- ===== EP-4 ===== -->
### EP-4: Title/Role Stays With Its Domain

**Status:** Active
**Category:** B (Editorial, judgment-required)
**Decidability:** UD-pattern
**Layer:** 3

**Rule.** When a title or role NOUN (e.g., *king*, *high priest*, *chief judge*, *ruler*, *teacher*, *governor*) heads a noun phrase modified by a PP naming the jurisdictional, institutional, or geographic domain over which the title applies, and Tiers 1-6 leave the break decision open, the title-NP and its domain PP SHOULD remain on the same v2-mine line. A break between title and domain MUST NOT be introduced on the basis of punctuation alone, line-length pressure, or local PP-trailing convention; the title's reference is incomplete without the domain. When the PP is itself a J5 substantive adjunct (its own when/where/why frame) or when discourse context shifts the PP from defining the title to predicating an independent claim about the role-holder, the case SHOULD route to REVIEW.

**UD signature.**
~~~yaml
trigger:
  relation: nmod
  head: { upos: NOUN, lemma_in: TITLE_ROLE_LEMMAS_EP4 }
  case: { lemma_in: [over, of, in, unto] }
action: REVIEW
~~~

*Note:* The UD signature identifies *candidate* locations only. The disambiguation between domain-defining nmod (MERGE) and substantive-adjunct PP (yields to J5 / SPLIT) requires reading the PP against the matrix's discourse frame; the validator surfaces candidates and emits REVIEW for editorial disposition.

**Diagnostic (per-case judgment).**

1. **Reference-completion test.** Strip the PP. Does the bare title-NP refer unambiguously to a known entity in the discourse? If NO — the bare title would dangle (e.g., *"high priest"* without specifying *"over the church"* leaves the reference open) — the PP is domain-defining → MERGE.
2. **Domain-headword class.** Domain-defining PPs cluster on complement nouns naming a jurisdiction (*the land*, *the people*, *the church*, *the Nephites*, *Zarahemla*), a body governed (*the people of the church*, *that people*), or a relational scope (*us*, *them*, *thy brethren*). When the headword names a domain-of-authority entity, the PP is domain-defining → MERGE.
3. **Independence test.** Can the PP stand as its own substantive when/where/why frame answering a question the matrix predication leaves open? If yes → J5 wins at Tier 5 (yields to J5 before EP-4 is consulted). If the PP only completes the title's reference → MERGE.

If diagnostic 1-3 do not converge, route to REVIEW.

**Closed lists** (machine-readable).
~~~yaml
TITLE_ROLE_LEMMAS_EP4:
  # Title / role nouns whose reference is canonically completed by a domain PP
  - king
  - queen
  - priest          # incl. compound "high priest"
  - judge           # incl. compound "chief judge"
  - ruler
  - teacher
  - governor
  - captain
  - prophet         # context-sensitive: "prophet of the Lord" is domain-defining; "prophet in Israel" may be J5
  - high_priest     # multi-word compound
  - chief_judge     # multi-word compound
  - chief_captain   # multi-word compound

DOMAIN_HEADWORD_INDICATORS:
  # Complement-NP heads that typically signal a domain-defining PP (heuristic)
  - land
  - people
  - church
  - city
  - kingdom
  - tribe
  - host
  - army
~~~

*Closed lists are operational focus-points. `TITLE_ROLE_LEMMAS_EP4` is the gating list for whether EP-4 even applies to a candidate; `DOMAIN_HEADWORD_INDICATORS` is heuristic — a hit raises confidence the PP is domain-defining, but the diagnostic above remains authoritative.*

**Scope.** Title- or role-headed noun phrases (head lemma ∈ TITLE_ROLE_LEMMAS_EP4) with an attached `nmod` PP whose head case-marker is *over*, *of*, *in*, or *unto*. EP-4 fires only when Tiers 1-6 (Layer 1 vetoes, formula/vocative integrity, complement integrity, merge-overrides, split-triggers, N=2 adjudication) have not already settled the break. EP-4 is a Tier 7 post-hoc editorial tiebreaker, not a generator or veto.

**Exclusions (closed list — each cites dominating rule).**

1. Title-NP inside a vocative environment (*"O thou king over the land, hear me"*) → R15 (vocative indivisibility wins).
2. Title-NP inside an AICTP formula span → R1 (formula integrity wins).
3. Domain PP that is itself a J5 substantive adjunct (its own when/where/why frame, fronted or trailing) → J5 (Tier 5 split-trigger wins before EP-4 is consulted).
4. Title-NP coordinated as one member of a J1 formally-marked parallel series of titles (*"a king and a ruler over us"*) → J1 governs the series; EP-4 governs each title's bond with the shared domain PP.
5. Title-NP appositive to a named referent introducing the title (Rule 22 INTRODUCING shape, formal anchor present) → R22 STACK SPLIT applies to the appositive; EP-4 still governs the title's bond with its own domain PP within that line.
6. PP that does not name a domain but predicates an action / relation independent of the title (*"the king who reigned over the Lamanites"* — the *over* PP modifies *reigned*, not *king*) → out of scope; the PP attaches to the matrix verb, not to the title noun.

**Precedence.** §3.5 Tier 7. Fires only after Tiers 1-6 settle. Yields to all higher tiers without exception (Tier 7 is post-hoc by construction — see §3.5 and §1.8 Step 4). No EP-4 cross-rule precedence is asserted within Tier 7; EP-4 and the other EP-rules / image-test are co-equal tiebreakers within the tier.

**Examples.**

- *Compliant (domain-defining — MERGE):* "Now Alma did not grant unto him the office of being high priest over the church," (PP completes the title's reference — without *"over the church"*, the bare *"high priest"* dangles. Domain-defining; merge.)
- *Compliant (domain-defining — MERGE):* "who was made king over the land of Zarahemla;" (PP names the jurisdictional domain; domain-defining; merge.)
- *Compliant (domain-defining — MERGE):* "and Orihah was anointed to be king over the people." (PP names the body governed; merge.)
- *Compliant (domain-defining — MERGE):* "that the chief judge over the land of Ammonihah and many of their teachers and their lawyers went in unto the prison" (chief judge + domain PP merged; subject of matrix verb.)
- *Compliant (domain-defining — MERGE):* "I am Alma, and am the high priest over the church of God throughout the land." (Title + domain PP merged; nested *throughout the land* is part of the domain specification.)
- *Compliant (J1 series, each title bonded to shared domain — MERGE within member):* "he has thought to make himself a king and a ruler over us," (Two coordinate titles share one domain PP; J1 governs the coordinate-title series but EP-4 keeps the shared *over us* bonded to the title cluster.)
- *Excluded by R15:* "O thou king over the land, / hear my prayer." (Title-NP inside vocative environment; R15 indivisibility wins.)
- *Excluded by J5:* "In the eighth year of the reign of the judges over the people of Nephi, / Alma went forth..." (Fronted year-formula + role-PP cluster is a J5 substantive adjunct slot-filler; J5 wins at Tier 5 before EP-4 is consulted.)
- *Excluded (out of scope — PP attaches to matrix verb):* "the king reigned over the Lamanites for many years." (PP *over the Lamanites* attaches to *reigned* — matrix verb's `obl` — not to *king* as `nmod`; EP-4 does not apply.)
- *Non-compliant (domain split as punctuation-artifact):* "Alma was the high priest / over the church of God." (Bare *"high priest"* dangles; the domain PP completes the title's reference. The break is a punctuation-artifact or line-length-pressure split, not warranted by grammar.)

**Implementation.**

- Validator: (not yet implemented) [to be implemented — surfaces title-NP + domain-PP candidates; emits REVIEW-REQUIRED for editorial disposition].
- Applier: none (Category B; auto-applier MUST NOT exist for EP-4; editorial-judgment required per-case).
- Closed-list definitions: §EP-4-Title-Role-Lemmas (in BoFM canon, supplementary section).
- Audit trail: `readers-bofm/private/audit-trail/EP-4.md` (to be populated during BoFM canon migration).
- Scholarship: [`atu-method/scholarship/bofm/EP-4.md`](atu-method/scholarship/bofm/EP-4.md).

---


<!-- ===== EP-5 ===== -->
### EP-5: Virtue/Vice Lists

**Status:** Active
**Category:** B (Editorial, judgment-required)
**Decidability:** Discourse-context-needed
**Layer:** 3

**Rule.** When a line contains a stack of coordinated moral-quality NPs or ADJs (virtue list or vice list) and Tiers 1-6 leave the break decision open, the editor SHOULD first examine the stack for a formally-marked rhetorical parallel pattern (dual / triadic / crescendo / antithetic pairing). When a parallel pattern is detected and the stack qualifies under J1's formally-marked parallel series, the members SHOULD each receive their own line per J1 (Tier 5 stacking). When no parallel pattern is detected, the stack SHOULD MERGE as a single compound-list complement of its governing predicate. Genuinely ambiguous cases (pattern weakly attested, member count or marker irregular) SHOULD route to REVIEW and MUST NOT be auto-applied. EP-5 is a Category B editorial tiebreaker; it does not authorize mechanical application without per-case judgment.

**UD signature.**
~~~yaml
trigger:
  relation: conj
  head: { upos: [NOUN, ADJ], lemma_in: MORAL_QUALITY_LEMMAS_EP5 }
  members:
    upos_in: [NOUN, ADJ]
    lemma_in: MORAL_QUALITY_LEMMAS_EP5
    count: ">=2"
action: REVIEW
~~~

*Note:* The UD signature identifies *candidate* stacks only. The parallel-pattern detection is not mechanically decidable from the parse — it requires reading the stack for rhythmic / structural shape (dual, triadic, crescendo, antithetic). The validator surfaces candidates; an editor applies the diagnostic. When the diagnostic resolves "parallel pattern detected" cleanly, the resulting action is `STACK_LIST_MEMBERS` per J1; when it resolves "no pattern" cleanly, the resulting action is `MERGE_COORDINATE_MEMBERS`; otherwise the action remains `REVIEW`.

**Diagnostic (per-case judgment).**

1. **Pattern-detection scan.** Read the stack aloud. Does a formally-marked rhythmic shape emerge — e.g., a dual pair (*faith and hope*), a fixed triad (*faith, hope, and charity*), a crescendo (*patience, mercy, and long-suffering*), an antithetic pairing (*meek and lowly*, *chastity and virtue*)? Formal markers include: repeated possessive (*his X, his Y, his Z*), repeated demonstrative, repeated preposition introducing each member, or canonical liturgical / formulaic ordering (e.g., the *faith / hope / charity* triad is corpus-attested and pre-coded).
2. **Member-count check.** At N=2, apply the §1.9 N=2 Adjudication Principle before reaching EP-5: synonymous / cognate pairs merge (M1); distinct non-synonymous pairs may split (J1) but typically merge as compound-object lists under EP-5's default-merge unless a parallel pattern is independently marked. At N≥3 with a marked pattern, J1 wins per the N=3+ cliff (§1.9) — EP-5 only confirms the J1 stacking, it does not override.
3. **Frame-uniformity check.** Are all members governed by a shared predicate or shared frame (single verb, single preposition, single possessor)? If so, the stack is a compound-list complement and the default is MERGE unless a marked parallel pattern fires J1.

If diagnostics 1-3 do not converge — pattern is weakly attested, members are mixed-class, frame is irregular — route to REVIEW.

**Closed lists** (machine-readable; non-exhaustive — heuristic, not gating).
~~~yaml
MORAL_QUALITY_LEMMAS_EP5:
  # Virtue-class lemmas (heuristic indicators of a virtue-list candidate)
  - faith
  - hope
  - charity
  - love
  - patience
  - long-suffering
  - meekness
  - lowliness
  - humility
  - diligence
  - mercy
  - virtue
  - chastity
  - temperance
  - knowledge
  - godliness
  - kindness
  # Vice-class lemmas (heuristic indicators of a vice-list candidate)
  - pride
  - envy
  - hatred
  - malice
  - lying
  - deceit
  - wickedness
  - iniquity
  - whoredom
  - murder

FORMULAIC_VIRTUE_TRIADS:
  # Corpus-attested fixed triads whose members each earn own line under J1
  - [faith, hope, charity]
~~~

*Closed lists are heuristic indicators that focus editorial attention; they are NOT decision-gating. A `MORAL_QUALITY_LEMMAS_EP5` hit MAY still resolve to MERGE under the no-pattern default, and a stack of non-listed lemmas MAY still qualify for J1 stacking if a parallel pattern is independently attested. The diagnostic above is the authoritative test.*

**Scope.** Coordinate stacks of NPs or ADJs naming moral qualities (virtues or vices), attaching under a shared governing predicate (verb, preposition, or possessor), where the stack functions as the compound complement of that governor. EP-5 fires only when Tiers 1-6 (Layer 1 vetoes, formula/vocative integrity, complement integrity, merge-overrides, split-triggers, N=2 adjudication) have not already settled the break. EP-5 is a Tier 7 post-hoc editorial tiebreaker, not a generator or veto.

**Exclusions (closed list — each cites dominating rule).**

1. Virtue/vice stack inside a vocative environment → R15 (vocative indivisibility wins).
2. Virtue/vice stack inside an AICTP formula span → R1 (formula integrity wins).
3. Virtue/vice stack at N≥3 with formally-marked parallel structure (repeated possessive, repeated demonstrative, repeated preposition, polysyndetic *and*) → J1 (Tier 5 wins before EP-5 is consulted; EP-5 only confirms J1's stacking direction). The N=3+ cliff (§1.9) makes this unconditional.
4. Virtue/vice N=2 pair governed by §1.9 N=2 Adjudication — synonymy/cognate test resolves before EP-5 fires (synonymous → M1 merge; distinct → J1 split / EP-5 confirms).
5. Virtue/vice stack that is itself a member of a higher-level J1 series (e.g., a triad inside a larger catalogue) → the higher-level J1 governs the outer split; EP-5 governs only the internal disposition of the stack treated as a single member.
6. Virtue/vice stack appearing in a multi-verse parallel list with a shared explicit frame (Parallel-List Uniformity Principle, §1.12) → list-uniformity governs; EP-5 yields.

**Precedence.** §3.5 Tier 7. Fires only after Tiers 1-6 settle. Yields to all higher tiers without exception (Tier 7 is post-hoc by construction — see §3.5 and §1.8 Step 4). When a parallel pattern is detected at N≥3, J1 (Tier 5) has already settled the outcome via the N=3+ cliff (§1.9); EP-5 confirms rather than generates. No EP-5 cross-rule precedence is asserted within Tier 7; EP-5 and the other EP-rules / image-test are co-equal tiebreakers within the tier.

**Examples.**

- *Compliant (formulaic triad — STACK per J1, EP-5 confirms):*
  ~~~
  And see that ye have
  faith,
  hope,
  and charity,
  ~~~
  (Alma 7:24 context; the *faith / hope / charity* fixed triad is corpus-attested with formal triadic shape — J1 stacks at the N=3+ cliff; EP-5 confirms the parallel-pattern reading.)
- *Compliant (no pattern — MERGE):* "for he hath neither faith, hope, nor charity;" (Moroni 10:21 — same triad lemmas appear in a single-line listing inside a negative-existential frame; the stack functions as a compound complement of *hath neither*, no separate rhythmic shape, default merge.)
- *Compliant (no pattern — MERGE):* "full of patience, mercy, and long-suffering," (Alma 9:26 — virtue-stack triad attached as compound complement of *full of*; no member earns independent predicative weight; merge.)
- *Compliant (crescendo pattern — STACK per J1, EP-5 confirms):*
  ~~~
  yea, nourish the tree as it beginneth to grow,
  by your faith
  with great diligence,
  and with patience,
  ~~~
  (Alma 32:41 context — each member introduced by repeated preposition *with* / *by* forms a formally-marked parallel series; J1 stacks; EP-5 confirms.)
- *Ambiguous → REVIEW:* "and his matchless power, and his wisdom, and his patience," (Mosiah 4:6 — repeated possessive *his* is a J1 marker, but the stack mixes attribute classes (power / wisdom / patience) under a single divine-attribute frame; whether the formal possessive-repetition triggers J1 stacking or the unified frame triggers EP-5 merge requires editorial judgment.)
- *Excluded by R15:* "O Lord God, give me faith, hope, and charity, / hear my prayer." (Stack inside vocative environment; R15 vocative integrity wins; EP-5 not consulted.)
- *Excluded by R1:* "And it came to pass that he was full of faith and hope and charity that..." (Stack inside AICTP formula span; R1 wins; EP-5 not consulted.)
- *Excluded by §1.9 N=2:* "having faith and hope" (N=2 cognate pair; §1.9 routes to M1 synonymy test before EP-5 fires; M1 merges as bonded pair.)

**Implementation.**

- Validator: (not yet implemented) [to be implemented — surfaces virtue/vice coordinate-stack candidates; emits REVIEW-REQUIRED for editorial disposition with optional pattern-classification hint].
- Applier: none (Category B; auto-applier MUST NOT exist for EP-5; editorial-judgment required per-case).
- Closed-list definitions: §EP-5-Indicators (in BoFM canon, supplementary section — heuristic indicators only).
- Audit trail: `readers-bofm/private/audit-trail/EP-5.md` (to be populated during BoFM canon migration).
- Scholarship: [`atu-method/scholarship/bofm/EP-5.md`](atu-method/scholarship/bofm/EP-5.md).

---


---

## 6. Validator Suite

Validators live in two subfolders reflecting the Layer 1 / Layer 3 split (restructured 2026-04-19):

**Layer 1 — Syntax validators** at `validators/syntax/` (generic English grammar checks; violations tagged `[MALFORMED]` — hard grammatical failures):

| Validator | Covers |
|-----------|--------|
| `validate_line_final_tokens.py` | Rules 9, 11, 12, 13a (line-final POS prohibitions — migrated to Layer 1; simple-aux Rule 12 cases) |
| `validate_rule_12_compound_verb.py` | Rule 12 compound-participle-shared-auxiliary case (extension to simple-aux check) |

**Layer 3 — Colometry validators** at `validators/colometry/` (BofM-specific editorial-rule checks; violations tagged `[DEVIATION]` — editorial-policy deviations):

| Validator | Covers |
|-----------|--------|
| `validate_rule_10_verb_do_split.py` | Rule 10 |
| `validate_rule_15_vocative.py` | Rule 15 (vocative own-line, true-vocative-vs-NP-object discriminator) |
| `validate_rule_16_aictp_dangling_that.py` | Rule 16 |
| `validate_rule_17_complement_integrity.py` | Rule 17 |
| `validate_rule_18_fixed_idioms.py` | Rule 18 |
| `validate_rule_19_ud.py` | Rule 19 (UD-only; regex retired 2026-05-10 per parity-test READY-TO-RETIRE-REGEX) |
| `validate_rule_23_date_colophon.py` | Rule 23 |
| `validate_rule_27_insomuch_that.py` | Rule 27 |
| `validate_rule_28_speech_act_after_frame.py` | Rule 28 |
| `validate_canon_retirement_residue.py` | Carry-forward-inertia residue (active references to retired/withdrawn/rescinded canon items) |

**Audit dashboard.** `validators/run_all.py` runs all validators above and reports per-rule conformance counts. Modes: default (report-only), `--baseline-check` (compare to `validators/.baseline.json`; exit 1 on regression), `--update-baseline` (capture current state).

**Pre-commit + commit-msg hooks.** `validators/hooks/pre-commit` runs the dashboard's baseline-check on canon/corpus/validator commits. `validators/hooks/commit-msg` runs `validators/check_canon_extensions.py` to detect §7.3 trigger #1 patterns and require audit-evidence in the message. Install both via `bash validators/hooks/install.sh`.

See `validators/README.md` for the error-class convention and philosophy.

### Gold-Standard Regression Fixtures

After any pipeline-changing pass (new rule, reformatter update, build script change, mechanical sweep), verify output against these five chapters before committing. Each fixture is chosen for diagnostic specificity: if a chapter breaks, it identifies which rule class regressed.

| Fixture | Register | Primary rules tested |
|---|---|---|
| **1 Nephi 1** (20 vv, 98 lines) | Narrative | Rule 1 AICTP integrity + dangling-*that* variant (8 AICTP instances) |
| **2 Nephi 8** (25 vv, 116 lines) | Poetic / Isaiah | Parallelism cola preservation, Rule 15 vocative, short-line integrity |
| **Alma 7** (27 vv, 159 lines) | Sermonic | Rule 17 complement integrity (highest *that*-lead density in candidate set) |
| **Alma 42** (31 vv, 136 lines) | Doctrinal argumentative | Periodic sentences, parentheticals, merge-override triggers |
| **Moroni 7** (48 vv, 215 lines) | Extended rhetorical | Rule 17 at scale, anaphoric address headers, rhetorical questions |

**Verification procedure:** diff the rebuilt `books/*.html` for each fixture chapter against the committed baseline after any pipeline change. Any line-count delta or content delta requires inspection before the commit lands.

**Next candidate on the bench:** Alma 22 (dialogue register, 35 vv) — add as sixth fixture if a dialogue-specific rule is formalized.

### Validator design constraint — no length caps on merge candidates

Merge validators and sweep scripts must not reject a candidate merge because the resulting line would exceed N characters. The atomic-thought test is the gate, not line length. A long correctly-merged line is evidence that the original text contains a long single thought. Length is diagnostic (may trigger Category B/C review for unusually long results) but is never a mechanical gate. This overrides any intuition to add "safety" character caps. (Stan 2026-04-17 directive, recovered from handoffs 2026-04-22.)

**Validator output is a work queue, not a review queue.** When a colometry validator categorizes instances as `STRONG-MERGE-CANDIDATE`, `STRONG-SPLIT-CANDIDATE`, or similar unambiguous labels, those items are **application-ready** — Category A by default per §2 "Mechanical-rule authority." Apply them mechanically. The only items that require per-item editorial judgment are those the validator itself flags as `REVIEW-REQUIRED` (heuristic-ambiguous — e.g., Rule 27's expletive-*there* cases prior to the 2026-04-19 PM refinement). Do not invert this discipline by treating the entire output as "candidates for review" — that replicates the failure mode §2 warns against.

---

# Part III — Process and Meta (for canon maintenance)

## 7. Change Protocol

Proposals to change an existing rule, add a new rule, or cull a rule must:

1. **State the English syntactic fact.** If you cannot cite it (UD label + CGEL/Quirk vocabulary), the proposal is insufficient.
2. **Provide corpus evidence.** Worked examples from the actual text — not hypotheticals.
3. **Survive adversarial audit.** For proposals matching any of the following **mandatory-audit triggers**, an adversarial audit (hostile agent or equivalent external skeptical review) MUST be dispatched and its findings must be reflected in the commit. Skipping audit on a triggered proposal is a protocol violation.

 **Mandatory-audit triggers (12 categories):**
 1. **New named rules / sub-clauses / categories** — including precedence cross-references between rules (e.g., "Rule A trumps Rule B at X"). Shape-matches feel-tests, enumerated lists, and subjective carve-outs particularly.
 2. **Rule status promotions** — *proposed* → settled. Removes the hedge; stakes increase.
 3. **Spot-check-based proposals** — any canon claim resting on <full-corpus-sweep evidence. Claims like "I checked 30 instances and the pattern is uniform" MUST be verified by a full-corpus classification before codification.
 4. **Reclassification of canon-recorded Category B/C items** — once a verse, rule, or item is recorded as Category B/C in canon prose or pending.md, subsequent sessions cannot silently reclassify it under a different rule-framing.
 5. **Rule deletions or SCOPE narrowings that retire live applications** — retiring a rule is as high-stakes as adding one; audit prevents discarding legitimate work.
 6. **Mechanical signature / validator changes under settled rules** — adding a verb class to a closed-list UD signature, refining a UD trigger, or changing validator conditions silently expands or contracts rule coverage.
 7. **Corpus sweeps ≥5 instances under a settled rule** — a sweep asserts "the rule fires cleanly here" N times; the collective scope-claim needs audit even when individual instances are Category A.
 8. **Canonical example additions to settled rules** — examples shape rule interpretation; a poorly-chosen example silently redefines the rule.
 9. **Meta-rule changes to §7 Change Protocol itself** — changes to this protocol MUST be audited (this very trigger codified 2026-04-23 after hostile audit caught the blind-spot in an earlier 6-trigger draft).
 10. **Discipline-shifting memory file additions** — new `feedback_*.md` or `project_*.md` files that shape how Claude approaches canon work are behaviorally-governing, not just observations; they need the same scrutiny as canon.
 11. **Cross-project imports** (GNT ↔ BofM) **or recoveries from retired canon** (v1, handoffs) — provenance from a sibling project or older version is not validation; the imported claim must have BofM corpus evidence independent of its source.
 12. **Corpus-fit verification — post-codification AND post-detection**.
 - **(a) Post-codification (original).** When a new rule, sub-clause, or named pattern is codified, the rule is **not "closed" until a corpus-wide goal-fit audit has confirmed (i) all eligible instances conform OR (ii) all residuals are explicitly enumerated** in pending.md. Codifications based on partial-corpus evidence are vulnerable to undercount; the canon's empirical "HOW WE KNOW" claim must be verified against full-corpus reality. **Audit-required:** any codification where the initial sweep was partial. **Audit-skippable:** rules whose initial codification WAS the full-corpus sweep (the sweep IS the audit). Run within the codifying session if practical, or as the FIRST item of the next session — not deferred indefinitely.
 - **(b) Post-detection.** This trigger ALSO fires when Stan-eyeball or any audit surfaces a violation of an **existing** (settled) rule. Application drift accumulates on long-codified rules through ongoing corpus modifications and prior partial-sweep gaps. When a violation is detected, schedule a same-rule full-corpus re-sweep within the same session if practical, or as the next session's first task. Goal-fit failures cluster — finding one of a shape elsewhere is the predictable outcome of partial-sweep history.
 - **Audit dimensions to consider**: goal-fit (does corpus implement codified rules), application-consistency on **formulaic phrases** (AICTP, "Yea verily," etc.), application-consistency on **parallel-list constructions** (gifts list, beatitudes, wo-series, blessed-series, conditional pairs — see §1 Parallel-List Uniformity Principle), self-consistency (cross-references, defensibility triplets), smuggling (judgment-handoff failure mode). Dispatch in parallel by default.
 - **Precedents.**
 - 2026-04-25 saith-the-Lord: codified with HOW WE KNOW claiming "19 corpus instances all stacked"; sweep found ~38 instances, ~26 not yet split — empirical undercount. Drove (a).
 - 2026-04-26 Alma 27:1: Stan caught Rule 17 cognition-class violation on a settled rule (cognition + parenthetical-adverbial separation); re-sweep found 4 siblings (Mosiah 20:6, 22:15, Alma 47:12, 49:22), all the same AICTP-bracketed *when X found that Y* shape. Drove (b).
 - 2026-04-26 Moroni 10:8-17 gifts list: Stan caught parallel-list inconsistency (vv 9, 12, 13 split where vv 10, 11, 14-16 merged); drove the **parallel-list audit dimension** addition.

 **Audit dispatch protocol — parallel by default.** When a proposal triggers multiple audit dimensions (e.g., fake-rule test + corpus-full-sweep + scope-test), dispatch all in a single message with multiple Agent tool calls. Sequential only when audit A's verdict determines whether audit B should run. Parallelization substantially reduces friction; codified 2026-04-23 after demonstrating 3 parallel audits completed in ~26 seconds each vs. ~80+ seconds sequential.

 **Audit-skippable categories (all must hold for the proposal to bypass audit):**
 - Category A mechanical corpus edits per already-codified rules (sweep-scale ≥5 still triggers #7 regardless)
 - Typo fixes, cross-reference updates that don't assert precedence, internal formatting cleanups
 - Deletions of items already reverted in the same session (audit-trail cleanup)
 - Defensibility-capture additions (WHY/HOW WE KNOW/SCOPE) to already-settled rules without changing the rule's scope

 **Efficacy note.** 5/5 audits this session produced material findings: 3 fake-rule prevents (Stab-commata, doctrinal-weight bump, EP-6), 1 reclassification-dodge catch (1 Ne 19:5), 1 reversed provisional-reject (R28). The discipline's qualitative value is established; a per-item catch-rate statistic would require randomized controls we don't have. Skip the statistics; keep the discipline.
4. **Apply uniformly.** If the rule fires in one place, run the validator or equivalent sweep to catch every instance. Sedimented inconsistency is the primary failure mode.
5. **Defensibility capture (prospective only from GNT cross-project directive).** Every new rule, sub-rule, or merge-override added to the canon must carry three elements:
 - **WHY** — the editorial reason the rule exists (what failure mode does it prevent, what pattern does it reveal)
 - **HOW WE KNOW** — corpus evidence + adversarial validation (worked examples, sweep counts, audit findings)
 - **SCOPE** — where the rule applies, where it doesn't (named exclusions, interaction with other rules)
 This is a prospective meta-rule; retroactive audit of older rules is optional, not required. The purpose is to ensure each new rule is documented well enough that a future reviewer can judge whether it earns its place.
6. **Re-evaluate deferred items when the rule-set changes.** When a rule is adopted or refined, any corpus item previously classified as `REVIEW-REQUIRED` or `deferred-editorial` must be re-evaluated against the updated rule-set before being carried forward as still requiring Stan's judgment. Carrying forward stale classifications wastes session time and hides cases the current rule-set now handles cleanly.
7. **Update this canon.** Edit the relevant rule section to its new state. Per-change rationale (audit-dispatch evidence, retraction precedent, scope claim) lives in the commit message, which is the durable audit trail; the canon prose itself reads as the current method. Never edit history silently.

**Self-consistency audit trigger.** When a session adds ≥2 new canon subsections, rules, or merge-overrides, run a light self-consistency audit before wrap: check that (a) all new cross-references resolve, (b) no new rule contradicts an existing rule, (c) all three defensibility elements (WHY/HOW WE KNOW/SCOPE) are present for each addition. Short pass; catches stale cross-refs and incompatibilities cheaply.

### Proposed-rule adoption protocol

A rule labeled *proposed* is a rule awaiting corpus verification. "Proposed" is a testable state, not a hedging license.

**Adoption criteria.** A proposed rule is adopted when its first corpus sweep produces **≥80% clean categorization** — i.e., 80%+ of matched instances resolve to unambiguous SPLIT or MERGE decisions without heuristic ambiguity. Ambiguous residue (`REVIEW-REQUIRED`) ≥20% signals the rule needs refinement before adoption.

**Sweep-then-decide workflow.**
1. Write validator implementing the rule's conditions.
2. Run against full corpus.
3. If clean ≥80% → apply clean decisions mechanically (Category A per §2), remove "proposed" label; capture the adoption evidence (sweep counts, audit verdicts) in the commit message.
4. If clean <80% → identify the ambiguity pattern, refine the rule with an explicit sub-clause, re-run.
5. Repeat until clean ≥80%, then adopt.

**Do not flag clean categorizations for per-item review.** A proposed rule whose conditions are met is as authoritative as an adopted rule on those specific instances; the "proposed" label only gates corpus-wide sweep confidence, not per-instance application.

---

## 8. Update history

For per-change audit trail, see `git log -- private/01-method/colometry-canon.md` (commit messages contain rationale, audit-dispatch evidence, and retraction precedents). For verbatim discussion logs, see the JSONL session transcripts at `~/.claude/projects/.../*.jsonl`. The canon prose above is the current method; this canon does not maintain a chronological narrative log inside itself.

---

*End of canon.*
