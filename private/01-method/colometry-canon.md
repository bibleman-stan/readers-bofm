# BofM Colometry — Operating Canon

**Version:** 2.0 (2026-04-19 rewrite)
**Predecessor:** `archive/colometry-canon-v1-retired-2026-04-19.md` — retained for reference, no longer authoritative.

---

## How to use this document

This canon serves two distinct audiences, and the sections are organized accordingly.

**If you are a HUMAN** (Stan, a collaborator, a scholar reading to understand the method):
- Read **Part I — Method** (§0 Purpose, §1 Framework, §2 Categories A/B/C). This explains *what* we are doing and *why*.
- Read **Part III — Process** (§7 Change Protocol, §8 Update Log) to understand how the canon evolves.
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

**We are revealing sense-lines — atomic thoughts the reader can process as discrete units.** Each line is a unit of meaning the reader can take in before needing the next. We are not doing English typography. We are not revealing rhetorical parallelism (Parry is a separate layer that may overlap with ours but is not our target). We are not prescribing oral delivery. We are formatting the text so that an ESL reader, a child, or a newcomer can take the scripture one atomic thought at a time.

### Origin

**Stan's premise:** *"Humans think, compose, and deconstruct (read and hear) in sense-lines — atomic thought-units that correspond to how ideas are generated, encoded, and recovered."* This is the working hypothesis that drives the project.

**Intellectual lineage.** Royal Skousen's demonstration that the Book of Mormon could be reduced to sense-lines (*The Earliest Text*, 2009/2022) was the trigger. **This project is the parent** — Skousen's foundational work was on the BofM corpus. The sibling GNT Reader project is the analogical extension ("what is true for the Book of Mormon is likely true for the Greek New Testament, and perhaps any text"). The methodology itself — framework, rules, structural justifications, merge-overrides — emerged from hands-on editorial experimentation across all 15 books. It was not derived from scholarly framework.

### Method

**The mission is sense-driven. The method is syntax-constrained.** These are different things and they belong in different parts of this document.

The method leads with syntax (§1 "The Gate") not because syntax is primary to the mission, but because **syntactic violation is fatal while sense ambiguity is recoverable within the permitted space.** A break that violates English grammar is always wrong no matter how strong the sense argument; a sense judgment inside the permitted space can be revisited by editorial review. Leading with syntax preserves the discipline that lets sense work — it doesn't demote the mission.

Novel rules can and do originate from sense-driven observation (Alma 22:15's speech-act-after-frame is one such case). The method accommodates this: sense proposes, syntax filters, the combination becomes a rule. But every break that survives to the corpus must be affirmable by English syntax. This is the non-negotiable operational floor.

### Pragmatic stance

This methodology is a set of conventions that reflect what we are trying to reveal. It is not derived from a cognitive theory; we are not claiming otherwise. Later work may investigate why it works. For now, we operate it honestly as what it is: a consistently-applied editorial practice grounded in English syntax, tested against the corpus, and refined by validator sweeps.

### Ground

Every rule here cites an English grammatical fact (anchored in Universal Dependencies labels — see [`data/syntax-reference/ud-taxonomy.md`](../../data/syntax-reference/ud-taxonomy.md) — and in traditional grammar vocabulary from CGEL / Quirk et al.). Rules that cannot be grounded in English syntax are editorial principles and labeled as such.

### Scope

This canon governs where lines break in the v2-mine source texts. It does not govern punctuation (canonical LDS text, untouched), words (never added, removed, or altered), or layout beyond break positions.

---

## 1. The Framework — Proposition-First, Syntax-Constrained

The framework is: **each proposition splits by default, unless syntax forbids.** Substantive adjuncts (slot-fillers in narrative frames) count as atomic thought units and also earn their own lines. Image sharpens ambiguous cases.

### The Generative Principle

**Each proposition splits by default.** A proposition is the atomic thought-unit — a complete predication (subject + finite verb + complement) that the reader can process as a single cognitive bite. Propositions drive line breaks. There is no positive requirement to break beyond this; there is no positive requirement to merge beyond this. The question at every candidate location is: *is this a proposition boundary?*

"Proposition" also includes the four structural-justification cases (below) — non-predicated units that function as atomic thoughts via formal-structural recoverability. These are the only non-strict-predication units that qualify.

### Syntax Forbids Splits — three closed-list ways

Syntax does not generate breaks. Syntax only vetoes them. A split that proposition-first would generate is forbidden when one of these three applies:

1. **Layer 1 mid-phrase prohibitions.** Splits mid-predication, mid-phrase, or mid-lexical-unit — line-final CCONJ, DET, AUX+pending V, ADP+pending NP, V+DO split, fixed multi-word unit, vocative unit, etc. See [`data/syntax-reference/ud-taxonomy.md`](../../data/syntax-reference/ud-taxonomy.md) §7 Break Legality Reference.

2. **Layer 3 complement integrity (Rules 17, 26).** When the matrix verb's or adjective's valence is unsatisfied without its clausal complement — *he said that X*, *it is expedient that X*. The matrix is grammatically incomplete on its own; the complement must merge.

3. **Layer 3 formula integrity (Rules 1, 18, 23).** Lexicalized multi-word frames (*And it came to pass*, *it is expedient that*, date colophons, fixed idioms) function as single units. Never break inside the frame.

These are the "unless" clauses of "split each proposition unless syntax forbids."

### Image Sharpens Ambiguous Proposition Boundaries

**Single image / camera angle.** When proposition-first is ambiguous (e.g., a short participial absolute that could read as continuation of the prior frame or as its own frame), ask: does the mind's eye reposition between candidate frames? Camera-angle shift → SPLIT. No shift → MERGE. This is a tiebreaker for ambiguous cases, not a primary generator.

### The Four Structural Justifications (Closed List)

Non-predicated units that function as atomic thoughts via formal-structural recoverability. The reader can reconstruct "who did what" because formal markers in the text make the missing predicate recoverable.

1. **Formally-marked parallel series.** Members connected by formal markers (*and also*, *nor*, correlative particles, polysyndetic *and*) where the shared predicate is recoverable from the parallel structure. Each member earns its own beat.

    **Compound list break signals (added 2026-04-22, recovered from v1 canon).** In a compound list governed by one preposition or verb, bare *"and [noun]"* items are compound objects and stay merged. A break inside a compound list is justified only when one of these signals is present:
    1. **Elided auxiliary + stacked participles** — each is an implied predication (covered by the primary justification 1 rule above)
    2. **Possessive restart** — *"and his"* appearing after items without possessive, OR changing from one possessor to another. *Repeated identical possessive* (*"and his X, and his Y, and his Z"*) is formulaic and does NOT alone justify stacking. Only a possessive RESTART justifies a break.
    3. **Demonstrative** — *"and that/this/these"* signals a new specified noun phrase
    4. **Relative clause attached** — *"which is/who was"* adds a predication to the item

    Without one of these signals, bare *"and [noun]"* items merge. The possessive-restart vs. repeated-possessive distinction is a corpus-specific trap (king-lists and inheritance-lists frequently trigger false-positive stacking without this test).

    **Semantic grouping principle (added 2026-04-22, recovered from v1 canon §8).** When splitting a compound list, breaks fall at SEMANTIC domain boundaries, not arbitrary coordinate positions. Named BofM semantic pairings that should stay together (even when the surrounding list breaks):
    - Material-culture pairs: *gold + silver*, *copper + brass*, *iron + steel*, *swords + cimeters*, *bread + water*, *milk + honey*
    - Social-scope pairs: *women + children*, *flocks + herds*
    - Moral/judgment triads: *murder + plunder + steal*, *whoredoms + abominations*, *power + wisdom + understanding*
    - Catastrophe pairs: *famine + pestilence*
    - Legal/covenant triads: *statutes + judgments + commandments*

    These are BofM-attested bonded semantic units. They merge as pairs/triads even when a longer list around them stacks. Extends M1 (gorgianic pair) from theological doublets to material/social/moral semantic domains.

2. **Portrait accumulation.** A set of attributes building one mental picture, sharing a copular or attributive frame from context ("full of grace and mercy and truth"). Applies only when the stack IS the portrait, not when it is a catalogue.

3. **Speech-act announcement.** Complete communicative predication introducing direct discourse ("And Aaron said unto the king:"). Announcement and quoted content are separate cognitive frames.

    **Named pattern — Verily formula (added 2026-04-22 from GNT cross-project Amen-formula §3.6).** *"Verily I say unto you"* and *"Verily, verily, I say unto you"* are invariant speech-act announcements in the BofM (32 instances total, all in 3 Nephi). The formula stands on its own line; the content clause (typically *that*-introduced) leads the next line.
    - **Test:** formula + content clause = two lines. Formula + short complete answer (*"Verily I say unto you, Nay"*, *"they have their reward"*, *"even as I am"*) = one line (the answer IS the content, not a separable clause).
    - **Currently applied (2026-04-22):** 3 corpus splits — 3 Ne 11:23 (formula + *that*-clause), 3 Ne 27:9 (formula + *that*-clause), 3 Ne 27:21 (formula + doctrinal statement). 22 instances already correctly protected. 7 "PROTECTED-COMPLETE" (formula + short answer) correctly merged.

4. **Classical commata.** Short fragmentary utterances carrying full communicative weight (*"Yea."*, *"If not so,"*). Typically 1-3 words; brevity + isolation = deliberate emphasis.

5. **Substantive adjunct as own focus.** *(added 2026-04-19 PM, replacing the retired "breath" diagnostic)* A fronted or trailing adjunct (temporal PP, locative PP, causal PP, etc.) that (a) is grammatically peripheral to the matrix predication's core truth AND (b) carries substantial content — enough that the reader processes it as an independent focus rather than background — earns its own line. These are the "slot-fillers" in narrative frames: AICTP projects who-did-what + when + where + why, and a substantive filling of a slot is its own focus-unit.

    **Grammatical grounding:** English treats peripheral adjuncts as syntactically detachable — they can front, trail, or be omitted without breaking the matrix. When the content is substantial, the detachability becomes cognitively active.

    **Test:** can the adjunct be paraphrased as its own "when/where/why/how" clause answering a question the matrix leaves open? If yes, it is a slot-filler and earns its own line.

    **Example (canonical):** *Alma 52:18* — *"And it came to pass that Moroni did arrive with his army at the land of Bountiful, / in the latter end of the twenty and seventh year of the reign of the judges over the people of Nephi."* The temporal PP is a 15-word filling of the AICTP "when" slot — substantive own focus, earns its own line. Not a proposition, but a slot-filler.

    **Pattern: year-formula temporal PPs.** Phrases of the form *"in the Nth year of the reign of the judges"* or *"in the Nth year of X"* reliably earn their own line when they follow a matrix predication (Alma 9:464, Helaman 536, 3 Nephi 915, Ether 2151 all resolve this way). They are substantive (typically 10-15 words), peripheral, and clearly answer the "when" slot.

    **Exclusion: degree quantifiers.** Short PPs that modify the **degree** of a predicate (*"in some degree,"* *"in great measure,"* *"in part"*) do NOT pass the slot-paraphrase test — they modify how-much, not when/where/why. They are predicate modifiers, not slot-fillers. Do not treat them as substantive adjuncts earning their own line.

The list is extensible only by worked example + adversarial validation. A proposed sixth justification must demonstrate (a) that it is a genuinely distinct instance of the same generating principle — formal structure in the text enables cognitive recovery of the full predication, or substantive content independently warrants own focus — and (b) that it survives an adversarial challenge.

### The Four Merge-Override Conditions (Closed List)

**Symmetric counterpart to structural justifications.** Where structural justifications describe cases where the default (merge under propositions-first) is overridden to produce a split, merge-overrides describe cases where an apparent split-trigger is itself overridden — returning the members to one line. The default is still merge; these overrides catch cases where naive application of split-triggers would fragment a unit that should stay whole.

**Generating principle:** Even when a line looks like it could pass the structural prong (formal markers present), merge wins when the resulting fragments would fail on more basic grounds — the chunk is not actually two propositions, the clause nucleus would be ruptured, the fragment cannot stand as atomic thought, or the cognitive prong itself fails.

**Strict-application caveat — rejection ≠ split license (added 2026-04-22 from GNT cross-project directive).** When a merge-override (M1–M4) does NOT apply to a given case, that does not automatically mean the case should split. It just means THAT override doesn't fire. The default behavior is still determined by the generative principle (proposition-first) and by other applicable rules (other merge-overrides, syntactic vetoes, structural justifications). Do not reason: "M1 rejected → must split." Reason instead: "M1 rejected → apply remaining analysis." Each merge-override's absence is silent, not authorizing.

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

**Tie-breaker when M1 and structural justification 1 both seem to apply (N=2 formally-marked pair):**
- If each member has a distinct non-synonymous finite verb → structural justification 1 wins (SPLIT). Example: two members with genuinely different actions.
- If the two members are semantically synonymous, cognate, or intensification variants → M1 wins (MERGE). Example: *"repent and believe"* (synonymous soteriological pair under shared imperative force).
- If the members are bonded-pair nouns/adjectives (not verbs) with unified rhetorical weight → M1 wins (MERGE).

**Grammatical grounding:** CGEL Ch. 14 on coordination of semantically-bonded pairs; classical hendiadys.

**M1 SPLIT-counterpart — passionate-enumerative register (stab-commata, added 2026-04-22 from retired v1 canon §8 + GNT cross-project convergence).** Where M1 fires on **calm unified** N=2 pairs to produce MERGE, the inverse register triggers STACK. **Stab-commata enumerations**: items serially enumerated in catalogs of judgment, casualty rolls, vice/virtue stacks, or passionate rhetorical sweeps where each item carries independent rhetorical weight earn their own lines. Test: would reading the items together in pairs dilute their individual force? If yes, stack individually.

- **Named BofM registers where stab-commata fires:** Alma 5 interrogative chain ("Have ye" sequences), Alma 32 whosoever chains, 2 Ne 4 Nephi's psalm, Mormon 6 casualty rolls, Mosiah 11-17 Abinadi indictment chains, Helaman 13 / 3 Ne 9 woe formulas, 2 Ne 13:18-23 Isaiah ornaments catalog.
- **Cross-language convergence (v1 finding):** GNT Marschall's rhetorical-treatise method independently identified the same register (stab-commata stacking in classical rhetorical catalogs). Two methodologies converge.
- **Interaction with M1:** M1 and stab-commata are complementary — same coordinate structure, opposite register reading. M1 fires when the pair reads as unified bonded image; stab-commata fires when the enumeration reads as sequential rhetorical blows. Read register before applying.
- **SCOPE exclusions (added 2026-04-22 post-audit):** stab-commata does NOT fire when (a) the series is a bonded pair already resolved by M1 (calm unified hendiadys wins over stab-commata reading for N=2), (b) items are short bare nouns without independent predicative or imagistic force (*"gold and silver and precious things"* is a compound DO catalog, not stab-commata enumeration — covered by the compound-list-break-signals rule above), or (c) the series is the formally-marked parallel type already handled by structural justification 1 with recoverable shared predicate (justification 1 covers; no need for stab-commata). Stab-commata is specifically the passionate-enumerative register where each member carries independent predicative or imagistic weight AND the passage rhetoric is indicting / lamenting / escalating. If those register conditions aren't present, don't invoke stab-commata.

#### M2. Verb-Object Clause-Nucleus Bond

Covered by existing **Rule 17 (Complement Integrity)**. A governing verb or adjective requiring a clausal complement forms one integrated predication with its complement. The matrix verb alone does not carry complete predication. See §5 Rule 17 for full treatment including the six-class verb list, exceptions, and delete-test diagnostic.

M2 is named here for cross-canon consistency with GNT's merge-override framework; operationally it's Rule 17 territory.

#### M3. Bare-Governor Indivisibility

**Definition:** A head word — participial adjective (*full, mighty, great* functioning predicatively), governing participle (*having, being, telling, desirous, instructed*), or discourse particle standing alone — cannot stand on its own line without at least one complement, object, or dependent. The bare governor fails the atomic-thought test because it is grammatical machinery awaiting content, not a complete predication.

**Test:** Can the isolated head-word be read as a complete thought? Or does the reader's attention dangle forward, expecting completion on the next line?

**BofM canonical cases:**
- Participial frame + pending complement: *"telling them / that there could be no atonement..."* → bare "telling them" awaits its that-clause complement (merge — applied 2026-04-20)
- Adjectival frame + pending infinitive: *"were desirous / to throw me into the depths of the sea"* → "desirous" requires its to-infinitive complement (merge — applied 2026-04-20)
- Bare discourse particles: *"Wherefore,"* / *"Therefore,"* / *"And now,"* alone on their own line WITHOUT following content — fails M3 unless explicitly licensed by Rule 20 Exemption (c) as a sentence connective with its content merged on the next line.

**Contrast with speech-intro (structural justification 3):** Finite speech-act formulas (*"said unto them:"*, *"declared:"*, *"cried:"* with colon) ARE complete speech-act predications — the speech act itself is the content. Bare participial frames (*"telling"* without complement, *"saying"* without following speech) are not; they await content.

**Contrast with Rule 21 (participial absolute):** A full participial absolute ("X having Y-ed,") with its own subject + participle + optional complement IS a complete predication and earns its own line. M3 catches BARE participial heads WITHOUT the subject-bearing absolute structure.

**Grammatical grounding:** CGEL Ch. 4 on finite vs. non-finite predications; complement requirements of governors. Bare governors lack the obligatory arguments their semantic class requires.

#### M4. Fragmented Atomic Thought-Unit

**Definition:** If splitting a line would produce fragments that individually fail the atomic-thought test, merge. This is the inverse of the cognitive prong: the cognitive prong requires each resulting chunk to be its own atomic thought for a split to proceed; if any resulting fragment fails that test, the split is blocked.

**Test:** Read each proposed resulting line aloud as a standalone unit. Does it constitute one focused-attention chunk with bounded information? If any resulting line fails, the split is over-fragmenting.

**BofM canonical cases:**
- Trailing prepositional modifiers orphaned from their predicate: *"...he spake,  / to your condemnation."* (short trailing PP with no independent image) — fails M4.
- Dangling discourse particles: *"alla"* alone on a line without a complete clause.
- Orphaned appositives separated from their head noun when the appositive alone has no independent image.
- **"Yea, even X" emphatic appositive (tested 2026-04-20, partial adoption):** a short emphatic appositive introduced by *"yea, even"* that lacks independent predicative weight — merely reinforces the preceding clause's referent. Sweep classifiers:
  - **3-condition test** for mechanical merge: (1) line starts with *"yea, even"*, (2) line contains no finite verb (no independent predication), (3) preceding line is a complete clause. All three hold → MERGE.
  - **Exclusion clause (2026-04-20 PM, adversarial-audit refinement):** when the *"yea, even X"* appositive contains a **year-formula temporal reference** (e.g., *"in the Nth year of the reign of the judges"*) or a **proper-noun entity** (named character, place, people, or government/institutional body), the appositive is a substantive slot-filler under **structural justification #5 (substantive adjunct as own focus)**, not an M4 fragment. KEEP SPLIT. The Alma 50:23 over-merge (*"...than in the days of Moroni, yea, even at this time, in the twenty and first year of the reign of the judges"*) was caught by adversarial audit and reverted — the year-formula trailing appositive is exactly the substantive slot-filler that justification #5 protects. Justification #5 wins over M4 when the appositive carries substantive temporal, entity, or institutional content.
  - **Sweep results (Agent Eta, 2026-04-20):** 182 corpus instances of *"yea, even"* line-starts. **54 STRONG-MERGE applied** initially, **1 reverted post-audit** (Alma 50:23 per exclusion clause above) → **53 net applied** across 10 books (1 Ne, 2 Ne, Jacob, Mosiah, Alma, Helaman, 3 Ne, Mormon, Ether, Moroni). **69 KEEP-SPLIT** (line has own finite verb → independent predication, not M4 fragment). **59 REVIEW-REQUIRED** (ambiguous — per-item judgment). Adoption threshold ≥80% not met (68% clean categorization); sub-rule remains **heuristic-trigger-for-review**, not mechanical-apply. The 53 applied merges each passed the 3-condition test individually plus the exclusion check.

**This is the adversarial-auditor's primary over-split detection rule.** Corpus audit (2026-04-20, run by Agent Delta) enumerated 211 M4 candidates: 23 HIGH-confidence, 126 MEDIUM, 62 LOW. The Eta follow-up sweep surfaced 182 *"yea, even"* line-starts total (Delta's HIGH subset was a conservative filter).

**Precedence over structural justifications — critical refinement (2026-04-20 PM).** M4 fires ONLY when splitting produces a fragment that **fails** the atomic-thought test. A fragment that PASSES atomic-thought via another structural justification's cognitive prong does NOT fail. Specifically:
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

**Breath as a named diagnostic was retired 2026-04-19 PM.** Rationale: in a reading edition with optional audio narration, "breath" was doing cognitive-chunking work dressed up as oral-delivery theory. The actual cases breath was handling — long single-proposition lines with substantial adjuncts — are more accurately captured by structural justification #5 (substantive adjunct as own focus). This grounds the split in English grammar (peripheral adjunct detachability) rather than a fictional physical-breath constraint.

### Punctuation is not a break signal

The canonical LDS text's punctuation is preserved for fidelity but has **no deterministic role** in line-break decisions. Periods, commas, semicolons, colons, em-dashes, and question marks mark orthographic and grammatical pauses in the printed text, but they do not encode the atomic-thought boundaries we are revealing. A break may coincide with a punctuation mark, but the mark does not license the break — syntax does.

**Test.** If the only reason you can cite for a break is "there's a comma here" or "the sentence ends," the break is not affirmed. Find the syntactic feature or merge.

**Why this matters.** Punctuation in the 1829 text and its descendants was added by editors (Oliver Cowdery, John Gilbert, and later revisers including Skousen) and has been revised multiple times across printings. It does not derive from the original oral/dictated register, and it reflects editorial decisions we are not trying to preserve or privilege. Treating punctuation as authoritative would import nineteenth- and twentieth-century editorial punctuation conventions as if they were part of the text's structure — which is exactly the "impose, not reveal" failure mode this methodology is designed to avoid.

**Practical consequence.** A long sentence with multiple commas is not a multi-line signal; it is a one-clause signal to examine for atomic-thought boundaries on syntactic grounds. A semicolon is not a forced break. An em-dash is not a forced split (Rule 22 covers the specific interpolation case syntactically, independent of the dash itself).

**What we DO preserve.** Every punctuation mark from the canonical LDS text stays in place. We do not alter, add, or remove punctuation. Line breaks are the only editorial tool.

---

## 2. Autonomy Boundary — Categories A / B / C

Every proposed change falls into one of three categories:

- **Category A — Editorial slippage.** Suboptimal break with no theological or rhetorical stakes. Apply confidently.
- **Category B — Rhetorical shape.** The break changes how the speaker builds an argument. Flag and ask before applying.
- **Category C — Theological weight.** Break placement carries a doctrinal implication. Flag and discuss before touching.

**Mechanical-rule authority (added 2026-04-19 PM).** When a settled mechanical rule's UD signature fires unambiguously and the rule's heuristics resolve without ambiguity, the change is **Category A by default**. The canon IS the approval — no per-item flagging is required. Bump to Category B only when rhetorical weight is independently implicated (e.g., breaking a covenant formula, altering a prophetic rhythm). Bump to Category C only when theological weight is independently implicated. Default-bumping mechanical hits to B out of caution is a failure mode — it inverts the canon's authority and creates unnecessary friction.

**Default:** when uncertain between mechanical and non-mechanical, treat as mechanical if the UD signature is clean. When uncertain between A and B/C on editorial/rhetorical grounds, treat as Category B. A false Category A on rhetorical grounds (applying a change that warranted discussion) costs more than a false Category B (flagging something straightforward). A false Category B on mechanical grounds (flagging a clean rule hit for review) costs Stan's time and compounds across sessions.

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

**Guidelines** (useful tendencies, not strict rules): line length as signal; vocative splitting nuances; fronted adverbials; line reordering (rare). (Compound list break signals promoted 2026-04-22 from Guideline to named sub-rule under structural justification 1 — no longer in this guideline list.)

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

*BofM-specific data (Rule 17 verb classes, Rule 18 fixed-idiom list, Rule 19 which-clause tree) now lives inline in §5 with the rules themselves. The four structural justifications live in §1 "The Criterion — Atomic Thought" as core methodology, not reference data.*

---

## 5. The Rules (Detail)

Each rule below follows the template:
- **Grammatical basis** — the English syntactic fact
- **UD signature** — the mechanical trigger
- **Diagnostic** — the test a scanner or human applies
- **Exceptions** — closed list
- **Example(s)** — from the corpus

### Rule 1 — AICTP Formula Integrity

**Grammatical basis.** *And it came to pass* is a fixed extraposition formula: dummy subject *it*, verb *came*, prepositional phrase *to pass*, and (usually) subordinator *that* introducing the extraposed content clause.

**UD signature.** Token sequence matching *"And it came to pass"* with `expl(came, it)`.

**Diagnostic.** Formula is indivisible. Applies to all variants: *And it came to pass*, *And now it came to pass*, *And it shall come to pass*.

**Exceptions.** None.

**Example.** "And it came to pass that in the seventh year of the reign of the judges, / there were about three thousand five hundred souls..."

### Rule 5 — Equivalence "Or" as Appositive

**Grammatical basis.** Coordinating conjunction *or* can mark either genuine disjunction (two alternatives) or equivalence (restatement in other words). Equivalence-*or* functions appositively.

**UD signature.** `cc(conj, or)`.

**Diagnostic.** Substitute *that is to say* or *in other words* for *or*. If the meaning is unchanged, it is equivalence — MERGE. If it breaks, it is disjunction — keep separated.

**Examples.**
- Equivalence (MERGE): "and they have a part in the first resurrection, or have eternal life, being redeemed by the Lord" (Mosiah 15:24) — *that is to say, have eternal life* works.
- Disjunction (SPLIT): "that he may live or die" — genuine alternative.

### Rule 6 — Causal Clauses Break

**Grammatical basis.** *Because* is a subordinating conjunction introducing an adverbial cause clause. Causal clauses are explanatory frames distinct from the action they explain.

**UD signature.** `advcl` with `mark` = *because*.

**Diagnostic.** Break before *because*.

**Exception.** Short-line contexts where combined line passes atomic-thought and breath tests may merge.

**Example.** "they did murmur against their father / because he had brought them out of the land."

### Rule 7 — Purpose Clauses Break

**Grammatical basis.** Finite purpose clauses introduced by *that* + modal (*may, might, shall, should*) are adverbial telic modifiers — new frames distinct from the action they motivate.

**UD signature.** `advcl` with `mark` = *that* and `aux` = MODAL.

**Diagnostic.** Break before *that*.

**Scope clarification.** Rule 7 targets **finite** purpose clauses only. **Non-finite infinitival purpose adjuncts** (*to + VERB + complement*, without subject or modal) are lighter and typically MERGE with their matrix motion verb (established 2026-04-19 at Alma 22:4).

**Exceptions.** Short-line contexts where combined line passes atomic-thought and breath tests may merge.

**Examples.**
- Finite (SPLIT): "he went forth among the people / that he might preach the word of God unto them."
- Infinitive (MERGE): "he has gone to the land of Ishmael, to teach the people of Lamoni." (Alma 22:4)

### Rule 9 — Never End a Line on a Conjunction

**Migrated to Layer 1** (2026-04-19). This is a generic English grammatical fact, not a BofM-specific editorial call. See [`data/syntax-reference/ud-taxonomy.md` §7](../../data/syntax-reference/ud-taxonomy.md) row: *line-final `CCONJ`* → `REQUIRED-MERGE`. Validator: `validators/syntax/validate_line_final_tokens.py`.

### Rule 10 — Never Split Verb from Direct Object

**Grammatical basis.** A transitive verb and its direct object form a single predication unit. Intervening adverbials or prepositional phrases belong with the verb, not with the object.

**UD signature.** Line-final `VERB` with `obj(VERB, NEXT_NOUN)` on the following line (bare NP continuation).

**Diagnostic.** Is the following line a bare NP (determiner + noun + optional PP/relative) that is the syntactic direct object of a verb on the prior line? If yes, MERGE.

**Scope — NOT covered by Rule 10:**
- Already-complete clauses followed by a relative (use "Which"-clause decision tree or Class P)
- Subject-NP continuations with their own predication (Rule 20 territory)
- Parallel coordinate object series (structural justification #1)

**Example.** "have you sufficiently retained in remembrance / the captivity of your fathers?" → MERGE (Alma 5:6).

**Validator.** `validators/colometry/validate_rule_10_verb_do_split.py`.

### Rule 11 — Never End a Line on an Article

**Migrated to Layer 1** (2026-04-19). Generic English grammar. See [`data/syntax-reference/ud-taxonomy.md` §7](../../data/syntax-reference/ud-taxonomy.md) row: *line-final `DET`* → `REQUIRED-MERGE`. Validator: `validators/syntax/validate_line_final_tokens.py`.

### Rule 12 — Never Split Auxiliary from Main Verb (extended 2026-04-20: compound-verb case)

**Migrated to Layer 1** (2026-04-19). Generic English grammar. See [`data/syntax-reference/ud-taxonomy.md` §7](../../data/syntax-reference/ud-taxonomy.md) rows: *line-final `AUX` with pending `aux` relation* → `REQUIRED-MERGE`; *line-final participle followed by coordinated participle under shared modal+aux* → `REQUIRED-MERGE` (added 2026-04-20).

**Extension — compound verb under shared auxiliary.** When a modal+auxiliary (*could have*, *would have*, *shall have*, etc.) scopes over two or more coordinated participles — *"could have [gone forth] and [partaken]"*, *"would have [tried] and [failed]"* — the auxiliary scopes across the *and*, and the coordinated participles form **one compound predicate**, not two independent predications. Never strand a coordinated participle from its shared auxiliary.

**Diagnostic:** if line N ends with a participle whose finite auxiliary is earlier in the line, and line N+1 begins with *"and [participle]"* with no subject and no finite verb of its own, the participle on N+1 is sharing the auxiliary from N via ellipsis. This is one compound verb → MERGE.

**Canonical example — Alma 12:26:** *"could have gone forth / and partaken of the tree of life"* — *"could have"* scopes over both participles; line 2 has no subject, no finite verb, only the dangling coordinate participle. Merge to one line. (Applied 2026-04-20.)

**Grammatical grounding:** CGEL Ch. 14 §2 on coordination of verb phrases under shared auxiliary. Standard English pseudo-coordination / hendiadic coordination.

Validator: `validators/syntax/validate_line_final_tokens.py` (to be extended with compound-verb check; currently covers simple AUX+V only).

### Rule 13a — Never End a Line on a Preposition Seeking Its Object

**Migrated to Layer 1** (2026-04-19). Generic English grammar. See [`data/syntax-reference/ud-taxonomy.md` §7](../../data/syntax-reference/ud-taxonomy.md) row: *line-final `ADP` with pending `case` relation* → `REQUIRED-MERGE`. Exceptions (phrasal-verb particles tagged `compound:prt`; stranded prepositions in relative clauses) are noted in the Layer 1 table. Validator: `validators/syntax/validate_line_final_tokens.py`.

### Rule 15 — Vocative Units Are Indivisible

**Grammatical basis.** Multi-word vocative addresses function as single direct-address units. Splitting them mid-address severs the addressee.

**UD signature.** `vocative` relation chain containing optional `INTJ` (*O*) + `NOUN`/`PROPN` sequence.

**Diagnostic.** Keep whole. The vocative may stand as its own line; it may not be split internally.

**Example.** "O Lord God, / how long wilt thou suffer..." is correct. "O Lord / God" is always wrong.

### Rule 16 — Dangling "That" After AICTP

**Grammatical basis.** The *that* following AICTP introduces the extraposed content clause; it is a subordinator leading its clause, not a tail of the formula.

**UD signature.** `expl(came, it)` + `mark(content, that)` where *that* would be line-final.

**Diagnostic.** Break BEFORE *that*.

**Example.** "And it shall come to pass / that whosoever shall believe on the Son of God..."

### Rule 17 — Complement Integrity

**Grammatical basis.** Verbs and predicative adjectives requiring a clausal complement (a *that*-clause or infinitive) form one integrated predication with their complement. The matrix verb alone does not express a complete thought.

**UD signature.** `ccomp(V, clause)` with `mark(clause, that)` where V belongs to one of six closed-list verb classes (table below).

**Diagnostic.** Matrix verb and its *that*-clause complement stay on the same line. When combined length exceeds a natural line, prefer an alternative restructuring over a mid-predication break.

**Verb classes in scope:**

| Class | Examples | Merges with complement |
|-------|----------|------------------------|
| Causative | *caused that, suffered that, permitted that, commanded that, granted that* | Yes |
| Aspectual | *began to, ceased to, continued to* | Yes (infinitive/gerund) |
| Speech (indirect discourse) | *said that, declared that, testified that, swore that, spake that, proclaimed that, told that, confessed that, rehearsed that* | Yes |
| Cognition | *knew that, believed that, perceived that, remembered that, saw that, heard that, understood that, supposed that* | Yes |
| Volition | *desired that, willed that, wished that, intended that* | Yes |
| FEF extraposition | *it was their lot to have fallen, it is expedient to do X* | Yes (infinitive) |

**Exceptions — complement integrity does NOT apply:**
- Direct discourse (colon or "saying:" after speech verb → voice shift)
- AICTP (Rule 16 forces break before *that*)
- Purpose *that* (Rule 7)
- Formally-marked parallel "that"-series (merge frame + first; stack remainder)
- Meta-announcement (BE-verb + predicate noun + appositive *that* → the *that* clause is appositive to the noun, not complement of the verb)
- Direct divine speech with recitativum *that* (*saith the Lord, that [first-person content]*)

**Delete-test diagnostic.** Remove any intervening noun phrase. If the sentence still reads as "[subject] [verb] that X," the *that* clause is a complement — MERGE. If the deletion breaks the sentence, the *that* clause is appositive to a noun — DNM (do not merge).

**Precedence with Rule 19.** Rule 17 trumps Rule 19 when both apply. A *that*-clause that is both cataphoric AND the complement of a Rule 17 verb gets MERGED — complement integrity wins. Rule 19 governs cataphoric *that*-clauses in non-complement positions (appositives, adjuncts, free-standing elaborations).

**Parallel "*that*"-series (three-tier expansion, added 2026-04-22 from git-log recovery).** When a speech/cognition verb takes multiple coordinate *that*-complements:
- **Two-member coordinate series**: merge frame + first *that*-clause; stack second as parallel beat. Example: *"declared unto them that they were a people who were under him, / and that they were a free people"* — frame with first, stack second.
- **Three-or-more-member coordinate series**: merge frame + first; stack remaining as polysyndetic parallel series (structural justification 1). Example: Mormon 7:5 three-fold *that*-series — frame + first on one line, two remaining members stacked.
- **Direct divine speech with recitativum *that***: *"saith the Lord, that [first-person content]"* — the *that* functions as a recitativum marker equivalent to direct-discourse colon. Keep split (like speech-act announcement).

**Example (causative).** "He caused that his servants should stand forth" — MERGE.
**Example (speech indirect).** "I say unto you that the time shall come" — MERGE.

### Rule 18 — Fixed Idiom Integrity

**Grammatical basis.** Multi-word lexicalized expressions function as single lexical items.

**UD signature.** Token sequence matching the fixed-idiom list below.

**Diagnostic.** Never break inside a fixed idiom regardless of line length.

**Fixed-idiom list:**
- *put to death*
- *from time to time*
- *prevailed upon*
- *put an end to*
- *one with another*
- *it is expedient that* (also the full AICTP family per Rule 1)
- *insomuch as* (distinct from *insomuch that* — Rule 27 proposed)
- Date-colophon formulas (Rule 23)

**Validator.** `validators/colometry/validate_rule_18_fixed_idioms.py`.

### Rule 19 — Cataphoric "That" Clauses Break; Anaphoric Merge

**Grammatical basis.** Non-complement *that*-clauses and relative clauses can be either information-advancing (cataphoric — introducing new referent, image, or proposition) or information-resolving (anaphoric — backward-pointing to already-established content). The distinction is semantic, not syntactic.

**UD signature.** `acl` or `acl:relcl` attached to a NOUN head, NOT in a `ccomp` position (else Rule 17 takes precedence).

**Diagnostic — sharpened.** A *that*-clause is anaphoric (MERGE) ONLY when BOTH subject AND predicate are backward-pointing. If subject points back but predicate introduces new content, the clause is cataphoric enough to SPLIT.

**Refinement.** Expletive *it* in cleft constructions (*"that it is by his grace"*) is NOT anaphoric — it is a structural placeholder. Result/purpose clauses with new predication (*"that it is good"*) are cataphoric.

**Unified "which"-clause decision tree:**

| Pattern | Example | Action |
|---------|---------|--------|
| Predicative identifier (which is X, where X classifies/names) | "commandment which is the word of God" | MERGE |
| Class P (completing-predication relative) | "the thing / which shall come" | MERGE |
| Non-restrictive relative introducing new info/action | "the atonement, / which was prepared from the foundation of the world" | SPLIT |
| Cataphoric relative advancing the argument | "the Son, / which he sent unto them" | SPLIT |
| Anaphoric relative backward-referring | *this* + *the case* both point back | MERGE |

**Examples.**
- Cataphoric (SPLIT): "I say unto you / that the good shepherd doth call you" — new image, new action.
- Anaphoric (MERGE): "The Spirit hath not said unto me that this should be the case" — *this* and *the case* both point back.

**Validator architecture note (added 2026-04-20).** Rule 19's mechanical validation is **partial by design**. The classification tree has three tiers of validator-tractability:

1. **STRONG-MERGE (mechanical):** short anaphoric relatives (≤3 words in clause body, no proper nouns, no substantive predicates) — validator applies directly.
2. **STRONG-MERGE-PREDICATIVE-IDENTIFIER (mechanical, added 2026-04-20):** relatives matching `which (is|was|are|were|became) + classifier` that classify/identify the head noun without advancing new action. Validator applies directly. Implements the "Predicative identifier" row of the decision tree.
3. **REVIEW-REQUIRED (judgment + discourse context):** cases where distinguishing anaphoric from cataphoric requires knowing whether an entity has been introduced earlier in the passage. Example: *"records which were engraven upon the plates of brass"* — if *"plates of brass"* was established earlier in the book, this is anaphoric (merge); if newly introduced, cataphoric (split). **A line-pair regex scanner cannot see prior discourse context and cannot resolve these.** Resolution requires either (a) Phase 2 corpus parsing with discourse-entity tracking, or (b) per-item editorial review.

Pre-Phase-2, REVIEW-REQUIRED items are the honest output of the validator — they are not "the rule isn't tight enough"; they are "the rule is tight but the diagnostic the validator can run doesn't have the information needed to classify some cases." This is a rule-infrastructure gap, not a rule-clarity gap.

### Rule 20 — No-Anchor Rule

**Grammatical basis.** Every independent line must carry a thought-marking anchor — a finite verb, an infinitive, a participle standing as predicate, or a substantive head independently predicated on the line.

**UD signature.** Line contains at least one: `VERB` (finite), `VERB` (infinitive), predicative `VERB` participle, or NP with its own `cop` / predicate attached.

**Diagnostic.** Count anchors. If zero, the line fails.

**Critical clarification.** A "substantive head" does NOT include bare NPs that continue a prior clause's predicate as list objects or appositional extensions. A line like "and also her mistress, the queen, and the king," fails the anchor test even though it contains nouns — those nouns are objects of the previous line's verb.

**Exemptions.**
- (a) Single-line verses — atomic by definition
- (b) Speech-intro prefixes
- (c) Standalone sentence connectives (*Wherefore*, *And now*, *Therefore*)
- (d) Lines that fail the anchor test but pass one of the four structural justifications (§1 "The Criterion — Atomic Thought")

**Corpus status (2026-04-13).** 28,683 lines scanned; 5 unanchored (99.98% compliance).

### Rule 21 — Participial Absolute Integrity

**Grammatical basis.** A participial absolute — a subject-bearing participial clause of the form "X having Y-ed" or "X being Y" — constitutes a grammatically independent predication. It is not a dangling modifier.

**UD signature.** Subject (`nsubj`) + participle (`VERB` in participial form) + optional complement, without finite auxiliary.

**Diagnostic.** Can the participial clause be rewritten as a finite sentence — "X was Y" or "X had Y-ed" — that stands alone? If yes, it earns its own line.

**Example (own line).** "I, Nephi, having been born of goodly parents, / therefore I was taught..." (1 Ne 1:1) — "I, Nephi, had been born of goodly parents" stands alone.

**Example (merge).** "And yet, I being over-zealous to inherit the land of our fathers, collected as many as were desirous..." (Mos 9:3) — "collected" has no resumptive subject; participial is the subject of the main verb.

### Rule 22 — Divine Title Appositives

**Grammatical basis.** Divine title appositives (*"Jesus Christ, the Son of God"*) function either as INTRODUCING (prophetic/revelatory naming) or REFERENCING (already-established identity as name unit).

**UD signature.** NP with appositional NP containing divine-title vocabulary.

**Diagnostic — requires formal anchor for STACK SPLIT.** INTRODUCING (stack) earns a split ONLY when one of three formal anchors is present:
1. **Formal naming formula:** "his name shall be called [X], [title]" / "and they shall call his name [X], [title]"
2. **First-occurrence context:** identity revealed for the first time in the passage
3. **Prophetic proclamation frame:** "Thus saith the Lord," "Behold, I say unto you," recorded vision, angel's announcement

**REFERENCING (default, MERGE).** Already-established identity used as a name unit.

**Boundary case.** Repeated invocations within one passage settle on ONE treatment throughout. Do not oscillate within a unified rhetorical beat.

**Example (STACK — first occurrence):** "his name shall be Jesus Christ, / the Son of God" (2 Ne 25:19).
**Example (MERGE — referential):** "I am a disciple of Jesus Christ, the Son of God" (3 Ne 5:13).

### Rule 23 — Date Colophon Integrity

**Grammatical basis.** Date-colophon formulas (*"in the Nth year of the reign of the judges"*) are fixed lexicalized expressions. Same logic as Rule 18.

**UD signature.** Token sequence match.

**Diagnostic.** Keep whole.

**Validator.** `validators/validate_rule_23_date_colophon.py`.

### Rule 26 — Adjective + "That" Complement Stays Together

**Grammatical basis.** Some adjectives (*possible, expedient, desirous, necessary, needful, impossible*) require a clausal complement. The predicate is incomplete without it.

**UD signature.** `ccomp(ADJ, clause)` with `mark(clause, that)`.

**Diagnostic.** MERGE.

**Distinction.** Verbs of speaking/perceiving may be complete without specifying content ("he said"). Adjectives in this class cannot ("it is expedient" → expedient WHAT?).

**Example.** "if it were possible that our first parents..." — MERGE.

### Rule 27 — "Insomuch That" Binding *(proposed 2026-04-19)*

**Grammatical basis.** *Insomuch that* is a consecutive (result) subordinator — etymologically "in + so much + that," functionally analogous to Latin *adeo...ut* / Greek *ὥστε*. It retroactively assigns a degree reading to the main verb: the main action was done to such an extent that the result followed. Binding is intermediate — tighter than pure purpose clauses (Rule 7), looser than correlative *so...that*.

**UD signature.** `advcl` with `mark` containing compound subordinator *insomuch that* (may require pre-merge of multi-token SCONJ).

**Diagnostic.** Default SPLIT. MERGE only when **all three** conditions hold:
1. Result clause ≤ 8 words
2. Subject continuity between matrix and result clause (`nsubj` of result = `nsubj` of matrix, or elided and co-referential)
3. No camera-angle shift (single-image diagnostic passes across the boundary)

**Expletive-*there* sub-clause (added 2026-04-19 PM).** When the result clause begins with expletive *there* + BE-verb (*there was*, *there were*, *there is*, *there are*, *there came*), condition 2 is evaluated against the **semantic subject** (the NP following *there were*), not the expletive. New-entity semantic subjects (e.g., *there were many slain*, *there were thousands converted*) fail condition 2 → default **SPLIT**. Rare continuing-entity semantic subjects (*there was the same man as before*) may pass condition 2; in those cases condition 1 (word count) is typically decisive.

**Chained *insomuch that* sub-clause (added 2026-04-19 PM).** When two or more *insomuch that* clauses chain asyndetically (no coordinating conjunction between them), default **SPLIT** each — each consecutive subordinator introduces a fresh finite predication with its own degree-specification of the preceding clause. The 3-condition merge test still applies pairwise (each *insomuch that* against its immediate antecedent, not against the top-level matrix), but in practice chained instances rarely pass all three conditions pairwise because the camera angle shifts with each degree-intensification. Canonical example — Alma 24:2: *"And their hatred became exceedingly sore against them, / even insomuch that they began to rebel against their king, / insomuch that they would not that he should be their king"* — three lines, each atomic.

**Example (SPLIT — default).** "And he did minister unto them, / insomuch that his whole household were converted unto the Lord." (Alma 22:23) — result 9 words, new subject, camera shift.

**Corpus status (2026-04-19).** 175 instances total, 125 split (71%), 50 merged (29%). First sweep pending with refined condition 2.

### Rule 28 — Speech-Act Announcement After Frame *(proposed 2026-04-19)*

**Grammatical basis.** When a speech verb's main-clause subject+verb is separated from the direct discourse it introduces by an intervening adverbial frame (temporal, locative, causal), the speech-act tag is an independent predication and a new camera angle. The frame sets scene; the speech-act is the discrete communicative event.

**UD signature.** Main-clause `VERB` of speech (*said, answered, cried, spake*) with `nsubj` and `parataxis` or `ccomp` relation to direct discourse, separated from the discourse by an intervening `advcl` (temporal/locative/causal).

**Diagnostic.** Speech-act tag earns its own line.

**Example.** "And it came to pass that after Aaron had expounded these things unto him, / the king said:" (Alma 22:15).

### EP-1 — "According To" Manner vs. Source

**Grammatical basis.** The preposition *according to* can head either a manner adverbial (HOW something was done) or a source/authority adverbial (BY WHAT POWER something was done). The two readings have different rhetorical weight.

**UD signature.** PP headed by *according to* attaching as `obl` or `advmod`.

**Diagnostic.** Manner (HOW) → MERGE. Source/authority (BY WHAT) → SPLIT.

**Examples.**
- Manner (MERGE): "spoke unto them, according to his word."
- Source (SPLIT): "it whispereth me, / according to the workings of the Spirit of the Lord."

**Note.** This rule requires judgment — editorial principle, not purely mechanical.

### EP-3 — Inverted Predicate

**Grammatical basis.** Fronted predicate constructions (*"great is my joy,"* *"blessed are they"*) invert the normal SVO order for rhetorical emphasis. The inversion is the device.

**UD signature.** Copular construction with predicate fronted before subject.

**Diagnostic.** Break before the inverted predicate. Test: rephrase in normal word order; if emphasis is lost, the inversion earns its own line.

### EP-4 — Title/Role Stays With Its Domain

**Grammatical basis.** Titles and role designations require a domain PP to complete their reference (*"high priest over the church"*, *"king over the land"*). Splitting title from domain leaves the title ambiguous.

**UD signature.** Title NOUN with `nmod` PP domain.

**Diagnostic.** Keep title + domain together.

### EP-5 — Virtue/Vice Lists

**Grammatical basis.** Stacked moral qualities may exhibit rhetorical parallel patterns (dual, triadic, crescendo). When a pattern is detected, line breaks should reveal it. When no pattern is detected, default to merge.

**UD signature.** Coordinated NPs or ADJs in moral-quality semantic class.

**Diagnostic.** Examine for detectable rhythmic pattern. If pattern detected, line breaks make it visible. If no pattern, merge.

**Note.** Editorial principle — requires judgment.

---

## 6. Validator Suite

Validators live in two subfolders reflecting the Layer 1 / Layer 3 split (restructured 2026-04-19):

**Layer 1 — Syntax validators** at `validators/syntax/` (generic English grammar checks; violations tagged `[MALFORMED]` — hard grammatical failures):

| Validator | Covers |
|-----------|--------|
| `validate_line_final_tokens.py` | Rules 9, 11, 12, 13a (line-final POS prohibitions — migrated to Layer 1) |

**Layer 3 — Colometry validators** at `validators/colometry/` (BofM-specific editorial-rule checks; violations tagged `[DEVIATION]` — editorial-policy deviations):

| Validator | Covers |
|-----------|--------|
| `validate_rule_17_complement_integrity.py` | Rule 17 |
| `validate_rule_16_aictp_dangling_that.py` | Rule 16 |
| `validate_rule_10_verb_do_split.py` | Rule 10 |
| `validate_rule_18_fixed_idioms.py` | Rule 18 |
| `validate_rule_23_date_colophon.py` | Rule 23 |

See `validators/README.md` for the error-class convention and philosophy.

### Gold-Standard Regression Fixtures (added 2026-04-22 from GNT cross-project §4)

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
3. **Survive adversarial audit.** Either run the proposal past a skeptical agent, or document why no skeptical agent is needed.
4. **Apply uniformly.** If the rule fires in one place, run the validator or equivalent sweep to catch every instance. Sedimented inconsistency is the primary failure mode.
5. **Defensibility capture (prospective only, added 2026-04-22 from GNT cross-project directive).** Every new rule, sub-rule, or merge-override added to the canon must carry three elements:
   - **WHY** — the editorial reason the rule exists (what failure mode does it prevent, what pattern does it reveal)
   - **HOW WE KNOW** — corpus evidence + adversarial validation (worked examples, sweep counts, audit findings)
   - **SCOPE** — where the rule applies, where it doesn't (named exclusions, interaction with other rules)
   This is a prospective meta-rule; retroactive audit of older rules is optional, not required. The purpose is to ensure each new rule is documented well enough that a future reviewer can judge whether it earns its place.
6. **Re-evaluate deferred items when the rule-set changes.** When a rule is adopted or refined, any corpus item previously classified as `REVIEW-REQUIRED` or `deferred-editorial` must be re-evaluated against the updated rule-set before being carried forward as still requiring Stan's judgment. Carrying forward stale classifications wastes session time and hides cases the current rule-set now handles cleanly.
7. **Update this canon.** Append a dated entry to §8 Update Log and add/modify the relevant rule section. Never edit history silently.

**Self-consistency audit trigger.** When a session adds ≥2 new canon subsections, rules, or merge-overrides, run a light self-consistency audit before wrap: check that (a) all new cross-references resolve, (b) no new rule contradicts an existing rule, (c) all three defensibility elements (WHY/HOW WE KNOW/SCOPE) are present for each addition. Short pass; catches stale cross-refs and incompatibilities cheaply.

### Proposed-rule adoption protocol (added 2026-04-19 PM)

A rule labeled *proposed* is a rule awaiting corpus verification. "Proposed" is a testable state, not a hedging license.

**Adoption criteria.** A proposed rule is adopted when its first corpus sweep produces **≥80% clean categorization** — i.e., 80%+ of matched instances resolve to unambiguous SPLIT or MERGE decisions without heuristic ambiguity. Ambiguous residue (`REVIEW-REQUIRED`) ≥20% signals the rule needs refinement before adoption.

**Sweep-then-decide workflow.**
1. Write validator implementing the rule's conditions.
2. Run against full corpus.
3. If clean ≥80% → apply clean decisions mechanically (Category A per §2), remove "proposed" label, append adoption entry to §8 Update Log.
4. If clean <80% → identify the ambiguity pattern, refine the rule with an explicit sub-clause, re-run.
5. Repeat until clean ≥80%, then adopt.

**Do not flag clean categorizations for per-item review.** A proposed rule whose conditions are met is as authoritative as an adopted rule on those specific instances; the "proposed" label only gates corpus-wide sweep confidence, not per-instance application.

---

## 8. Update Log

### 2026-04-22 — Hidden-Decision-Point Sweep Additions (7 parallel agents)

Parallel doc-audit sweeps across handoffs, retired v1 canon, git log, and session history surfaced 22 findings. Following the adoption protocol, today's session codified the high-confidence subset and corpus-applied the clean Category A hits.

**Canon additions:**
- **§3 structural justification 3 — Named pattern: Verily formula** (BofM calque of GNT's Amen-formula). 32 corpus instances, all in 3 Nephi. 3 applied splits (3 Ne 11:23, 27:9, 27:21); 22 already protected; 7 correctly merged as formula+short-answer.
- ~~**§1 structural justification 1 — Triad symmetry constraint** (recovered from handoffs E3)~~ **REVERTED post-audit 2026-04-22** (commit `4e3b88f`): handoffs E3 is a reformatter-tool rule, not editorial methodology.
- **§1 structural justification 1 — Compound list break signals** (recovered from v1): four-signal test (elided-aux, possessive-restart, demonstrative, relative attached); possessive-restart vs. repeated-possessive distinction named.
- **§1 structural justification 1 — Semantic grouping principle** (recovered from v1 §8): named BofM semantic pairs (gold+silver, swords+cimeters, women+children, statutes+judgments+commandments, etc.) extend M1 to material/social/moral domains.
- **§1 M1 counterpart — Stab-commata register** (triple-surfaced: recovered from v1 §8, flagged in git-log commits, flagged as forgotten cross-pollination). Passionate-enumerative register STACKS; named BofM passages (Alma 5 interrogative chain, Mormon 6 casualty rolls, Helaman 13 / 3 Ne 9 woe formulas, etc.).
- **§1 M4 "yea, even X" sub-pattern exclusion** — already landed 2026-04-20 PM; reinforced today.
- **§1 Merge-overrides strict-application caveat** — "rejection ≠ split license" (from GNT cross-project directive).
- ~~**§1 Punctuation section — Em-dash convention** (recovered from handoffs M0)~~ **REVERTED post-audit 2026-04-22** (commit `4e3b88f`): directly contradicts §1 "Punctuation is not a break signal." Also reformatter-tool rule, not editorial methodology.
- ~~**§5 Rule 13b** (new editorial-principle entry, recovered from commit `491917342`)~~ **REVERTED post-audit 2026-04-22** (commit `4e3b88f`): was deliberately removed from mechanical suite; re-adding unnecessary.
- ~~**§5 Rule 17 — Restrictive-vs-content-clause *that* disambiguation** (recovered from handoffs M7)~~ **REVERTED post-audit 2026-04-22** (commit `4e3b88f`): handoffs M7 is reformatter heuristic, not editorial rule.
- **§5 Rule 17 — Parallel *that*-series three-tier expansion** (recovered from git-log commit `b04cae9d`): two-member / three-or-more / direct-divine-recitativum handling.
- **§6 Gold-standard regression fixtures** (GNT §4 import): 1 Nephi 1, 2 Nephi 8, Alma 7, Alma 42, Moroni 7 — diff check after any pipeline change.
- **§6 Validator design constraint — no length caps** (recovered from handoffs 14): atomic-thought is the gate, not line length.
- **§7 Change Protocol additions:** defensibility capture (WHY/HOW WE KNOW/SCOPE prospective-only), self-consistency audit trigger (≥2 additions → audit), re-evaluate-deferred-items-when-rules-change step.

**Corpus applications (6 edits):**
- 3 Nephi 11:23, 27:9, 27:21 — Verily formula splits (Rule 17 complement-integrity interaction with structural justification 3)
- Alma 47:24 — cause-consequence beat (stab + fall) merged per M4 ad-hoc invocation
- 1 Nephi 5:4 — counterfactual condition + consequence merged per M4
- Ether 14:29 — approach + defeat merged per M4

**Rejected / deferred:**
- **Agent-proposed "Wayyehi variant FEF pattern" labeling REJECTED** (Stan 2026-04-22): Hebrew-parallelism terminology imports are resisted per memory `feedback_rhetoric_bandwagon`. The patterns exist ("it was their lot," "as it happened that") but are treated as AICTP-family variants without Hebrew-derived labels.
- **"Behold" three-type typology** (deictic/mirative/logical-connective): UNPURSUED from v1, carried forward. Deferred to pending.md.
- **Q1/Q2 Subordinating-vs-Coordinating diagnostic** from v1 §4: added to canon, then **REVERTED post-audit 2026-04-22** (commit `4e3b88f`): signatures mostly redundant with existing rules (Rule 10 V+DO, 13a ADP, 17 complement, 20 anchor). Consolidated diagnostic added structure without new content.
- **Syntactic Affirmation Test formalization** (from git-log commits `2f4af560`, `108ebf10`): added to canon, then **REVERTED post-audit 2026-04-22** (commit `4e3b88f`): redundant with existing §1 "Syntax forbids splits" principle.
- **R28 Textual-Asymmetry Override** (from GNT): evaluate applicability to BofM archaic English; deferred.
- **Nested resumptive *that* pattern** (4 v1-flagged instances): requires Stan's judgment per original deferral; re-surfaced in pending.md.
- **Exception/Save clause punchline test** (handoffs E8): moderate-frequency pattern; deferred.

### 2026-04-20 — Merge-Override Conditions Imported from GNT Canon

Cross-canon methodological alignment with sibling GNT Reader project. Per cross-canon audit at `readers-gnt/private/03-sessions/2026-04-20-foundational-reframing-and-layer-1/cross-canon-audit.md` (§M1 recommendation).

**Canon additions:**
- **Origin block** (§0) — Stan's premise statement + Skousen credit + BofM-as-parent-project note.
- **The Four Merge-Override Conditions (§1)** — M1 Gorgianic Bonded Pair, M2 Verb-Object Clause-Nucleus Bond (= existing Rule 17), M3 Bare-Governor Indivisibility, M4 Fragmented Atomic Thought-Unit. Symmetric counterpart to structural justifications; blocks split-triggers when resulting fragments fail on basic grounds.
- **The Complete Framework decision procedure (§1)** — formalized override-precedence: split-trigger fires, syntax veto blocks, merge-override blocks, image diagnostic sharpens. Four-force summary table (was three).
- **"Yea, even X" emphatic appositive sub-pattern** — documented under M4 as codifiable sub-rule pending Stan authorization. Corpus audit surfaced 18 HIGH-confidence instances.

**Corpus sweeps applied (Category A per mechanical-rule authority):**
- **M1 Gorgianic pairs**: 4 merges — 2 Ne 24:9 *repent-and-believe*, 2 Ne 26:8 *repent-and-believe*, Alma 14:7 *faith-and-repentance*, Alma 40:13 *weeping-and-wailing-and-gnashing*.
- **M3 Bare-governor / Rule 17 complement-integrity**: 4 merges — Alma 30:17 + 30:18 (*telling them that...*), 1 Ne 17:48 (*desirous to throw...*), 2 Ne 18:11 (*instructed me that...*).
- **N=2 Unified Rhetorical Force**: 7 merges — 1 Ne 16:10, 2 Ne 5:30, 2 Ne 8:1, 2 Ne 8:2, 2 Ne 7:7, Ether 12:36, Ether 12:41 (petition-promise doublets + single-imperative-two-coordinate-NP patterns).

**Corpus audits produced (no auto-apply, Stan-reviewable):**
- M4 over-split audit: 211 candidates (23 HIGH, 126 MEDIUM, 62 LOW). See session folder.
- Validator editorial-overlay audit: 10 validators reviewed, 18 heuristics classified (11 DEFENSIBLE, 5 REACHING-FOR-CONVENIENCE, 2 SEDIMENTING-THE-FAILURE). See `private/2026-04-20-canon-v2-and-rule-12-19-sweeps/validator-editorial-overlay-audit.md`.

**Deferred:**
- Helaman 1:22 (the *"and did spread / insomuch that they began to cover..."* candidate) — agent flagged as M3 but is more properly Rule 27 "insomuch that" territory; defer until Rule 27 re-sweep.
- R28 Textual-Asymmetry Override from GNT canon — noted as opportunity but not yet imported; defer to future session.

### 2026-04-19 — Canon v2.0 Rewrite

Rewrote canon from scratch in response to:
- 5 adversarial audits (cognitive, grammatical, PhD-committee, consistency+comprehensiveness, 4-criteria hierarchy) converging on: scholarly framing doesn't match operational reality; restructure 4-criteria into 1+1+2.
- UD taxonomy import establishing common grammatical vocabulary (`data/syntax-reference/ud-taxonomy.md`).
- Alma 22 dialogue surfacing: infinitive-of-purpose vs. finite purpose clause distinction (Rule 7 narrowed); speech-act announcement after adverbial frame (Rule 28 proposed); insomuch-that binding taxonomy (Rule 27 proposed); that-taxonomy clarification across all rules.

**Changes from v1.0:**
- Shelved scholarly framing (Chafe, Kintsch, Cowan, dictation hypothesis, cognitive-cycle prose). Not rejected — removed from operating canon. Future scholarly paper will argue theoretical grounding separately.
- Restructured 4-criteria hierarchy to 1+1+2 (gate + criterion + two diagnostics).
- Added UD signatures to every rule.
- Added "That"-taxonomy reference table.
- Rule 7 narrowed to finite purpose clauses only; infinitive-of-purpose merges with matrix motion verb.
- Added Rule 27 (proposed): Insomuch-that binding.
- Added Rule 28 (proposed): Speech-act announcement after frame.
- Compressed from 1459 lines to operating-length.

### 2026-04-19 (PM) — Three-Layer Architecture

Separated generic English grammatical facts (Layer 1) from BofM-specific editorial methodology (Layer 3), with validators (Layer 2) rearchitected to match.

**Changes:**
- **Layer 1 created**: `data/syntax-reference/ud-taxonomy.md` §7 "Break Legality Reference" — 37-row shape-capped table with columns `UD signature | Legality | CGEL §`. 20 `REQUIRED-MERGE` entries, 17 `PERMITTED-EITHER`, 0 `REQUIRED-BREAK`. No prose, no examples, no exceptions — the shape cap IS the scope-creep discipline.
- **Layer 1 prose draft deleted**: `data/syntax-reference/english-break-rules.md` (my first draft was 230 prose-heavy lines; adversarial audit called it "a second canon under a different name"; distilled to shape-capped table and deleted).
- **Rules 9, 11, 12, 13a migrated to Layer 1**: detailed sections in canon §5 replaced with one-line pointers to ud-taxonomy §7. Canon Quick-Reference table (§3) marks these four as `Layer 1 →`.
- **Rules that stayed in canon** (despite audit initially proposing their migration): 10, 15, 17, 19, 20, 21, 26. Their operational meat is BofM-specific (verb-class lists, anchor-exemption taxonomy, cataphoric/anaphoric diagnostic). Only the structural kernel is generic English; that kernel is referenced in the UD taxonomy doc and cited from the canon rule.
- **Validator folders split**: `validators/syntax/` (Layer 1) and `validators/colometry/` (Layer 3). `validate_line_final_tokens.py` → syntax/. All others → colometry/. Error classes: `[MALFORMED]` (syntax — hard grammatical failure) vs `[DEVIATION]` (colometry — editorial-policy deviation). Used `git mv` to preserve file history.
- **Corpus baseline established before migration**: all validators clean except Rule 12 (1 pre-existing violation at Helaman 2:2180 — *art/sparing*) and Rule 10 (13 candidate flags across Mosiah, Alma, Helaman, 3 Nephi, Ether, Moroni). Pre-existing, not migration-introduced.
- **Side finding**: `validate_line_final_tokens.py` has a pre-existing exit-code bug (reports violations but exits 0). Filed for follow-up.

**Why this matters.** The audit's core insight: Layer 1 must be a permission/prohibition SURFACE, not a rival canon. Honest posture: we maintain a syntax vocabulary doc with a break-legality table; the canon is our editorial delta; validators enforce each layer separately with distinct error classes. This prevents the "inventing a doctrine" failure mode the adversarial audits keep flagging.

**Adversarial audits this session (5 total):** cognitive-science grounding; grammatical theory; PhD committee defensibility; consistency+comprehensiveness; 4-criteria hierarchy coherence; three-layer architecture. Convergent findings: scholarly framing doesn't match operational reality (→ shelved — see 2026-04-19 AM entry); criterion-first vs syntax-first framing needed (pending decision); Layer 1 must be shape-capped (implemented).

### Prior history

See `archive/colometry-canon-v1-retired-2026-04-19.md` Section 10 for the full pre-rewrite update log (2026-03 through 2026-04-18).

---

*End of canon.*
