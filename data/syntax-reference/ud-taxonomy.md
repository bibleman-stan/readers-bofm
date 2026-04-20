# Universal Dependencies — Colometry Reference

**Purpose:** The standard vocabulary our canon rules cite when grounding in English syntax. Every rule in `private/01-method/colometry-canon.md` should map to one or more entries here. This document is the common floor.

**Standard:** Universal Dependencies v2 (universaldependencies.org). CC BY-SA.

**Scope:** This doc is restricted to the POS tags and dependency relations that matter for sense-line line-break decisions. It is not a complete UD reference.

---

## How to use this document

- **Rule authors**: cite the UD label your rule operates on ("Rule 7 fires on `advcl` with `mark` = *that* + AUX modal")
- **Scanner authors**: filter parsed corpus by these labels to find candidate instances
- **Reviewers**: disambiguate surface-form collisions (the word "that" can be `SCONJ`/`mark` or `PRON`/`nsubj` or `DET` — different categories trigger different rules)

---

## Part 1 — Part-of-Speech Tags (POS)

### Open-class (content words)

| POS | Description | BofM examples | Colometry relevance |
|-----|-------------|---------------|---------------------|
| `VERB` | Lexical verb | *ministered, repent, behold* (imperative), *believe, spake* | Carrier of predication. Verb-on-a-line is often its own beat (Rule 10). |
| `NOUN` | Common noun | *house, people, Spirit, commandments* | Portrait-building (Rule §2 unless-2). |
| `PROPN` | Proper noun | *Nephi, Zarahemla, Lamoni, God* (theologized) | Portrait anchors, geographical/personal. |
| `ADJ` | Adjective | *wicked, righteous, great, eternal* | Portrait-accumulation candidate. |
| `ADV` | Adverb | *exceedingly, surely, indeed, mightily* | Modifier; usually non-splitting. |

### Closed-class (function words)

| POS | Description | BofM examples | Colometry relevance |
|-----|-------------|---------------|---------------------|
| `AUX` | Auxiliary verb | *do, did, hath, shall, will, may, might, should, would, must, can, could, art, is, were* | **Critical for Rule 7 (purpose clauses with modals) and Rule 17 (complement integrity).** |
| `PRON` | Pronoun | *he, thou, ye, they, we, it; that* (demonstrative); *which, who, whom, that* (relative) | Disambiguates "that" — pronominal vs. subordinator. |
| `DET` | Determiner | *the, a, an, this, that, these, those, his, their* | Rule 20: line-final `DET` is a dangling-article violation. |
| `SCONJ` | Subordinating conjunction | *that, because, if, when, after, before, since, while, although, unless, until, lest, whereas, insomuch* | **Primary break signal.** Rule 7, Rule 16, Rule 27 proposed all operate on SCONJ. |
| `CCONJ` | Coordinating conjunction | *and, or, but, nor, yet, for (causal), so (result)* | Rule 9: line-final `CCONJ` is a dangling-conjunction violation. |
| `ADP` | Adposition (preposition) | *unto, upon, into, through, against, of, by, from, with, to* (prepositional) | Rule 12: line-final `ADP` is a dangling-preposition violation. |
| `PART` | Particle | *to* (infinitive marker), *not, no* | `to` + `VERB` = infinitive phrase (non-finite purpose — candidate for merge). |
| `INTJ` | Interjection | *yea, behold, lo, O* (vocative), *amen, alas, wo* | Discourse openers. Often earn their own line when load-bearing. |
| `PUNCT` | Punctuation | *. , ; : -- ?* | Canonical. Never used as break-signal alone. |

---

## Part 2 — Dependency Relations (the meat)

Dependency relations describe the **grammatical function** one token plays relative to another. In UD, every token has exactly one head and one relation label.

### Core argument relations

These link a predicate (usually a verb) to its arguments.

| Relation | Description | BofM example | Colometry relevance |
|----------|-------------|--------------|---------------------|
| `nsubj` | Nominal subject | "*he* ministered" — `nsubj(ministered, he)` | Subject continuity test (Rule 27 merge condition). |
| `obj` | Direct object | "he taught *the people*" — `obj(taught, people)` | Complement of transitive verb; usually same line. |
| `iobj` | Indirect object | "he gave *them* knowledge" — `iobj(gave, them)` | Same line as giving verb. |
| `ccomp` | **Clausal complement** | "he said *that he would go*" — `ccomp(said, go)` | **Rule 17 territory.** A full clause filling the object slot of a saying/thinking/perception verb. MERGE with matrix. |
| `xcomp` | Open clausal complement | "he began *to preach*" — `xcomp(began, preach)` | Subject-shared non-finite complement. Usually MERGE. |
| `csubj` | Clausal subject | "*that he came* is known" — `csubj(known, came)` | Rare; typically extraposed (see `expl` below). |

### Clausal modifier relations

These link a clause to what it modifies. **Most break-signal rules operate here.**

| Relation | Description | BofM example | Colometry relevance |
|----------|-------------|--------------|---------------------|
| `advcl` | **Adverbial clause modifier** | "he came *that he might teach*" (purpose); "he ministered *insomuch that his household were converted*" (result); "*when Aaron had expounded*, the king said" (temporal) | **Primary break category.** Rule 7 (purpose), Rule 27 proposed (insomuch-that result), temporal-adverbial splits. |
| `acl` | Adnominal clause (general) | "the fact *that he came*" — `acl(fact, came)` | Appositive noun-complement "that"-clauses. MERGE with head noun. |
| `acl:relcl` | **Relative clause** specifically | "the man *that I saw*" — `acl:relcl(man, saw)` | **Rule 19 territory.** Cataphoric (advances the argument) → SPLIT; anaphoric (backward-referring) → MERGE. |

### Function-word relations (the labels on "that," "and," etc.)

These tell you **what role a function word is playing**. The single most important disambiguation in our corpus.

| Relation | Description | BofM example | Colometry relevance |
|----------|-------------|--------------|---------------------|
| `mark` | Marker — introduces a subordinate clause | *that* in "he said *that*..."; *because*, *if*, *when*, *after*, *although*, *lest*, *insomuch that* | **The "that" disambiguator.** `mark` on "that" = subordinator (Rule 7 / 17 / 27 territory). |
| `cc` | Coordinating conjunction marker | *and, or, but, nor, yet* between coordinates | Flags coordination structure (Rule §2 unless-1). |
| `conj` | Conjunct — second/later member of a coordination | "fire *and* brimstone" — `conj(fire, brimstone)` with `cc(brimstone, and)` | Identifies series members. Enables formally-marked parallel detection. |
| `expl` | Expletive (dummy "it" / "there") | "*It* came to pass that X" — `expl(came, it)`; "*there* were many" | **AICTP signature.** Identifies extraposed-subject constructions (Rule 16). |

### Other useful relations

| Relation | Description | BofM example | Colometry relevance |
|----------|-------------|--------------|---------------------|
| `nmod` | Nominal modifier (of a noun) | "the land *of Ishmael*" — `nmod(land, Ishmael)` | Non-splitting; stays with head noun. |
| `amod` | Adjectival modifier | "*great* iniquity" — `amod(iniquity, great)` | Non-splitting. |
| `advmod` | Adverbial modifier | "*greatly* marveled" — `advmod(marveled, greatly)` | Non-splitting. |
| `det` | Determiner relation | "*the* king" — `det(king, the)` | Rule 20: `det` cannot be line-final. |
| `case` | Case-marking preposition/postposition | "*unto* them" — `case(them, unto)` | Rule 12: `case` cannot be line-final (dangling-preposition check). |
| `aux` | Auxiliary-of relation | "*hath* gone" — `aux(gone, hath)`; "*may* receive" — `aux(receive, may)` | Modal detection for purpose-clause identification. |
| `discourse` | Discourse element | "*Yea*, I will" — `discourse(will, yea)`; "*Behold*..." | Identifies interjections; often line-initial. |
| `parataxis` | Parataxis — loose juxtaposition | "he said *X* — *`parataxis`* if untagged as `ccomp`" | Speech-attribution signature when direct discourse follows. |
| `punct` | Punctuation attachment | — | Canonical, never break-signal alone. |

---

## Part 3 — Rule-to-UD Mapping (what this unlocks)

The current canon's rules, mapped to their UD signatures:

| Rule | Name | UD signature | Notes |
|------|------|--------------|-------|
| 1 | AICTP integrity | Sequence `"And"/"it"/"came"/"to"/"pass"/"that"` with `expl(came, it)` + `mark(VERB, that)` | Fixed idiom; identity via token sequence + expletive. |
| 7 | Purpose clauses break | `advcl(matrix, subordinate)` with `mark(subordinate, that)` + `aux(subordinate, MODAL)` | MODAL = *may, might, shall, should* (archaic purpose marking). BREAK before subordinate. |
| 9 | Line-final CCONJ forbidden | Last token on line has POS = `CCONJ` | Pure POS check. Move CCONJ to lead next line. |
| 10 | V + DO split | Line-final `VERB` with `obj(VERB, NEXT_NOUN)` on following line | Flag when verb and its direct object are line-separated without warrant. |
| 11 | Line-final AUX forbidden | Last token on line has POS = `AUX` with `aux`-relation to a VERB on the following line | Pure POS+dep check. |
| 12 | Line-final ADP forbidden | Last token on line has POS = `ADP` or relation = `case` | Dangling preposition. |
| 13a | Line-final bare PART forbidden | Last token on line has POS = `PART` (esp. infinitive *to*) | Flag infinitive-marker stranding. |
| 16 | AICTP dangling "that" | `expl(came, it)` + `mark(CONTENT, that)` where *that* would be line-final | Break BEFORE *that*, lead next line. |
| 17 | Complement integrity | `ccomp(matrix, subordinate)` with `mark(subordinate, that)` | MERGE across line boundary. |
| 18 | Fixed idioms | Token-sequence identity (hardcoded list) | Idiom-level check; no UD needed. |
| 19 | Relative clauses | `acl:relcl(head, clause)` — cataphoric vs. anaphoric determined by whether clause advances argument | Content-dependent; UD identifies relative; judgment determines break. |
| 20 | Line-final DET forbidden | Last token on line has POS = `DET` | Pure POS check. |
| 21 | Vocative integrity | `vocative(VERB, NOUN)` + optional `O` as `INTJ` preceding | "O Lord God" stays whole. |
| 22 | Em-dash / interpolation | `punct(VERB, --)` bounding a `parataxis` or `dislocated` element | Sharpened diagnostic per 2026-04-18 work. |
| 23 | Date colophon integrity | Token sequence: *in the Nth year of the reign of the judges* | Idiom-level; no UD. |
| 26 | Speech-verb indirect discourse | `ccomp(speech_verb, clause)` with `mark(clause, that)` | Sub-case of Rule 17. |
| 27 *(proposed)* | "Insomuch that" binding | `advcl(matrix, result)` with `mark(result, "insomuch that")` + `nsubj`-continuity + word-count ≤ 8 | See canon Rule 27 when drafted. |
| 28 *(proposed)* | Speech-act announcement after frame | Main-clause speech `VERB` with `nsubj` separated from direct discourse by an intervening `advcl` (temporal/locative/causal) | See canon Rule 28 when drafted. |
| EP-4 | Extraposition of "expedient" / "needful" | `expl(copula, it)` + `csubj:extraposed(copula, CLAUSE)` + predicate = *expedient / needful / requisite* | Mirror of AICTP for non-temporal expedition frames. |

---

## Part 4 — The "That"-Taxonomy in UD Terms

Our previous "that"-type confusion resolves cleanly in UD. The surface word *that* takes multiple labels depending on grammatical function:

| Grammatical type | POS | Dependency role | Example | Canon rule |
|------------------|-----|-----------------|---------|------------|
| Complementizer (verb complement) | `SCONJ` | `mark` attaching to the clause's head VERB, which is `ccomp` of matrix | "he said *that* X" | Rule 17 → MERGE |
| Complementizer (adjective complement) | `SCONJ` | `mark` attaching to a clause that is `ccomp` of an `ADJ` predicate | "I am glad *that* X" | Rule 17 → MERGE |
| Complementizer (noun complement / appositive) | `SCONJ` | `mark` attaching to a clause that is `acl` of a head NOUN | "the fact *that* X" | Rule 19 (anaphoric) → MERGE |
| Complementizer (extraposed subject) | `SCONJ` | `mark` attaching to a clause that is `csubj` of a copula or equivalent, with `expl(copula, it)` | "It is expedient *that* X"; "It came to pass *that* X" | Rules 1 / 16 / EP-4 → BREAK BEFORE |
| Relative pronoun | `PRON` | `nsubj` or `obj` inside an `acl:relcl` | "the man *that* I saw" | Rule 19 (content-dependent) |
| Adverbial subordinator (purpose) | `SCONJ` | `mark` attaching to the head of an `advcl` with modal | "*that* he may receive" | Rule 7 → BREAK BEFORE |
| Adverbial subordinator (result — correlative) | `SCONJ` (within compound "insomuch that") | `mark` attaching to the head of an `advcl` | "*insomuch that* X were converted" | Rule 27 proposed → conditional |
| Demonstrative | `DET` or `PRON` | `det` or standalone | "*that* man"; "I know *that*" | N/A (not clause-introducing) |

---

## Part 5 — What UD Does Not Solve

Honest limits of this framework for our purposes:

1. **Archaic English parsing**: parsers trained on modern English may mis-tag *thou, thee, hath, wherefore, yea, behold*. Expect ~5-10% token-level error on archaic corpora. Spot-checking against hand-analysis is non-negotiable before trusting validator output.

2. **Compound subordinators**: *insomuch that*, *in order that*, *so that* may be split by the parser into separate tokens with separate labels. Pre-processing (token-merging) or post-processing (pattern-matching for multi-token SCONJ compounds) is required.

3. **Biblical register / KJV dialect**: archaic verb forms (*goeth, giveth, hath, art*) may tag as `VERB` instead of `AUX`, and archaic pronouns (*thee, thou, ye*) may tag inconsistently. Manual correction passes needed.

4. **Semantic judgments UD does not make**: Rule 19's cataphoric/anaphoric distinction is semantic, not syntactic — UD tells us it's a relative clause, not whether it's information-advancing. Rule 27's "camera-angle shift" is likewise semantic. These rules need UD + editorial judgment, not UD alone.

5. **Rule 22 (em-dash interpolations)**: UD attaches punctuation as `punct`; the interpolation semantics requires additional diagnostics beyond UD alone.

---

## Part 6 — References

- Universal Dependencies home: universaldependencies.org
- UD v2 POS tags: universaldependencies.org/u/pos/
- UD v2 dependency relations: universaldependencies.org/u/dep/
- English UD treebanks (training data for parsers): EWT, GUM, ParTUT
- Primary parsers that output UD: spaCy (en_core_web_trf), Stanza (Stanford)
- Authoritative grammars that map cleanly onto UD:
  - Huddleston & Pullum, *Cambridge Grammar of the English Language* (CGEL, 2002) — primary reference for the "that"-taxonomy in Part 4
  - Quirk, Greenbaum, Leech, Svartvik, *Comprehensive Grammar of the English Language* (CGE, 1985) — secondary reference

---

## Part 7 — Break Legality Reference

This table is a break-legality filter, not a break-doctrine. It catalogs where English grammar permits or forbids line breaks — not where we choose to break. Editorial decisions (when to take a permitted break, when to merge a permitted split) belong in the colometry canon at `private/01-method/colometry-canon.md`.

| UD signature | Legality | CGEL § |
|---|---|---|
| Line-last POS = `CCONJ` (*and, or, but, nor, yet, so, for*) | `REQUIRED-MERGE` | Ch. 15 §1 |
| Line-last POS = `DET` (*the, a, an, this, these, his, their*) | `REQUIRED-MERGE` | Ch. 5 §7 |
| Line-last POS = `AUX` with `aux` relation to VERB on following line | `REQUIRED-MERGE` | Ch. 3 §1 |
| Line-last participle (VERB) with coordinated participle on following line sharing earlier modal+aux via ellipsis (line N+1 starts with `cc` = *and* + participle, lacks `nsubj` and finite verb) | `REQUIRED-MERGE` | Ch. 14 §2 |
| Line-last POS = `ADP` with `case` relation to NP on following line | `REQUIRED-MERGE` | Ch. 7 §1 |
| Line-last POS = `PART` (infinitive marker *to*) with `xcomp` VERB on following line | `REQUIRED-MERGE` | Ch. 14 §3 |
| Line-last POS = `PART`/`ADV` (negator *not/no/neither/nor*) with scope constituent on following line | `REQUIRED-MERGE` | Ch. 9 §3 |
| Line-last `VERB` with `obj` (direct object NP) on following line | `REQUIRED-MERGE` | Ch. 4 §2 |
| Line-last `VERB` with `ccomp` clausal complement on following line | `REQUIRED-MERGE` | Ch. 4 §3 |
| Line-last `VERB` with `xcomp` open complement on following line | `REQUIRED-MERGE` | Ch. 4 §3 |
| Line-last copular `VERB`/`AUX` with predicate complement (`nsubj:pass` / `xcomp`) on following line | `REQUIRED-MERGE` | Ch. 4 §4 |
| Line-last `ADJ` (class-II: *expedient, needful, possible*) with `ccomp` complement on following line | `REQUIRED-MERGE` | Ch. 16 §4 |
| Line-last NP (`nsubj`) with its `VERB` head on following line (single-clause subject–predicate) | `REQUIRED-MERGE` | Ch. 2 §1 |
| Mid-compound-proper-name split (multi-token `PROPN` sequence) | `REQUIRED-MERGE` | Ch. 5 §14 |
| Mid-fixed-idiom split (hardcoded token sequence, `fixed` relation) | `REQUIRED-MERGE` | Ch. 17 §1 |
| Mid-compound-preposition split (*in spite of, in order that, so that* — multi-token `SCONJ`/`ADP`) | `REQUIRED-MERGE` | Ch. 7 §7 |
| Mid-phrasal-verb split (`compound:prt` particle separated from its verb) | `REQUIRED-MERGE` | Ch. 16 §7 |
| Mid-vocative-unit split (`vocative` relation, multi-word address) | `REQUIRED-MERGE` | Ch. 17 §4 |
| Subject + participle split within participial absolute (`nsubj` + `acl`/`advcl` participle) | `REQUIRED-MERGE` | Ch. 15 §7 |
| Token + trailing punctuation split (`punct` attaching backward to preceding token) | `REQUIRED-MERGE` | Ch. 20 §1 |
| Leading punctuation (opening quote/bracket) + following token split | `REQUIRED-MERGE` | Ch. 20 §1 |
| `parataxis` boundary between main clauses (no conjunction) | `PERMITTED-EITHER` | Ch. 15 §1 |
| `conj` boundary between main clauses with `cc` marker | `PERMITTED-EITHER` | Ch. 15 §2 |
| `advcl` boundary, finite, purpose subtype (*that + modal, so that, in order that*) | `PERMITTED-EITHER` | Ch. 14 §11 |
| `advcl` boundary, finite, result subtype (*so that, insomuch that, such that*) | `PERMITTED-EITHER` | Ch. 14 §11 |
| `advcl` boundary, finite, cause subtype (*because, since, for, as*) | `PERMITTED-EITHER` | Ch. 14 §11 |
| `advcl` boundary, finite, condition subtype (*if, unless, whether, provided that*) | `PERMITTED-EITHER` | Ch. 14 §11 |
| `advcl` boundary, finite, concession subtype (*although, though, even though, while*) | `PERMITTED-EITHER` | Ch. 14 §11 |
| `advcl` boundary, finite, time subtype (*when, after, before, while, until, since, once*) | `PERMITTED-EITHER` | Ch. 14 §11 |
| `acl:relcl` non-restrictive relative clause (comma-set) | `PERMITTED-EITHER` | Ch. 12 §1 |
| `appos` NP boundary | `PERMITTED-EITHER` | Ch. 17 §1 |
| `parataxis` speech-frame ↔ direct discourse boundary (colon-set) | `PERMITTED-EITHER` | Ch. 11 §3 |
| `advcl`/`acl` participial absolute boundary (*nsubj + participle*, whole absolute complete) | `PERMITTED-EITHER` | Ch. 15 §7 |
| Free adjunct participle boundary (`advcl` with participial head, no overt subordinator) | `PERMITTED-EITHER` | Ch. 15 §6 |
| `acl:relcl` restrictive relative clause | `PERMITTED-EITHER` | Ch. 12 §1 |
| Non-finite purpose adjunct / `xcomp` / gerund complement (whole non-finite clause complete on prior line) | `PERMITTED-EITHER` | Ch. 14 §3 |
| Fronted short adverbial (*in the beginning, therefore, nevertheless*) | `PERMITTED-EITHER` | Ch. 8 §5 |
| Coordinate NPs with `cc` marker (`conj` relation, noun-level) | `PERMITTED-EITHER` | Ch. 15 §4 |
