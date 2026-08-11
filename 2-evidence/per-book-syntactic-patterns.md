# Per-book EME syntactic patterns

Catalogue of distinctive Early Modern English syntactic patterns observed during UD annotation of the BoFM corpus. These are publication-grade observations about authorial signature, oral-tradition substrate, and stylistic distinctiveness.

Source: agent-led UD annotation runs, 2026-05-09. Each book's annotator-agent flagged constructions they considered non-obvious; this file aggregates and organizes them.

---

## 1 Nephi
*(annotation pending — Wave 3)*

## 2 Nephi
*(annotation pending — Wave 3)*

## Jacob

- **Fronted-object auxiliary inversion**: "for a long time will I lay up", "my vineyard will I cause" — fronted obj/obl with subject-aux inversion. Notably common in Jacob's vineyard parable (Jacob 5).
- **Causative+passive chains**: "cause to be burned", "cause to be gathered" — handled with xcomp + aux:pass embedding.
- **Absolute participials**: "he knowing that I had faith", "we being a lonesome people" — nominative-absolute as advcl.
- **Optative/jussive with Mood=Sub**: "not my will be done", "let that be a sign", "thy will be done" — voluntative subjunctive markers.
- **"like as it were"**: archaic comparative cluster — like=SCONJ mark, as=fixed, were=Mood=Sub.
- **EME -eth verbs**: cometh, remembereth, striketh, cleaveth, ascendeth, knoweth, beholdest, deniest, goest — VBZ with Person features.

## Enos

- **Anacolutha (opening)**: "I, Enos, knowing my father that he was a just man" — nominative-absolute participial as csubj of "pass" rather than finite root.
- **Deeply nested conditionals**: extreme stacking of advcls in the long-petition sentence (sent 14 of annotation): "if it should so be that... should fall... be destroyed... Lamanites should not be destroyed, that the Lord God would preserve... even if it so be..."
- **Optative chains**: "blessed be the name", attached as conj of matrix verbs.
- **Emphatic `did` constructions**: heavy use of `did + bare-verb` past-tense affirmative.
- **`save it was/be`** archaic exception: tagged SCONJ ("except"), introducing advcl.

## Jarom

- **Comparative inversion**: "than were they of the Nephites" — `they` as predicative head with cop `were`; classic post-aux subject in comparative.
- **`as many as` fused-relative**: "as many as believed" — `many` as nsubj of main verb, qualified by acl:relcl beginning at `as`.
- **`neither did they blaspheme`** — `neither` as ADV (per spec §5), not CCONJ.
- **`making all manner of tools`** — long participial advcl with `yea` discourse introducing appositive weapon list.
- **`long-suffering`** tokenization — three tokens (`long`, `-`, `suffering`); `-` is PUNCT HYPH; `long` amod; `suffering` NOUN head.

## Omni

- **Anacolutha across sentence boundaries**: sentences continue across semicolon/em-dash, each parsed with multiple roots; e.g. sent 7's "passed away" with `away` compound:prt.
- **Resumptive `he would not suffer`** — `conj` of root, not new root, signals oral-tradition repetition.
- **Double `had had` pluperfect** — first AUX, second VERB root.
- **Absolute participial constructions**: "their leader being a strong and mighty man" — `leader` structural head, `being` cop of predicate nominals.
- **`Inasmuch as`** treated as fixed ADV+SCONJ compound.

## Words of Mormon

- **Anacolutha (sent 4)**: "the things ... pleasing me" and "my fathers knowing" are absolute nominative participials; root is `pleasing`, not a finite verb.
- **Sentence-boundary continuations**: semicolon/dash anacoluthon across multiple `sent_id`s; each parsed as complete as possible with `came` as root in both.
- **AICTP frame** with `expl`/`xcomp`/`ccomp` structure (sent 11).
- **MWT `cannot`** — span row left fully underscored per spec; sub-tokens annotated as `can` (AUX) + `not` (PART advmod).

## Mosiah
*(annotation pending — Wave 3)*

## Alma
*(Alma 30 done; rest pending — Wave 3)*

Alma 30 patterns:
- AICTP frame heavily used
- "Behold," sentence-initial INTJ discourse
- Korihor's anti-Christ argumentation: complex relative clauses, topicalization ("these things which ye call prophecies")
- Formal inversion: "neither were the dead of the Nephites numbered" (stanza misanalyzed; LLM corrected)

## Helaman

- **Heavy AICTP density** — hundreds of instances. Distinctive marker of Mormon's narrative style as compiler.
- **Oath formulas**: "as surely as the Lord liveth" — advcl with `liveth` as VERB VBZ.
- **EME perfect**: `hath done/loved/spoken` — `hath`=AUX VBZ + VBN.
- **`save it were/be`** subjunctive exception — `save`=SCONJ mark, `it`=expl, `were`=AUX Mood=Sub.
- **Multi-word ADP fixed chains**: `because of`, `according to`, `from among`, `like unto`.
- **`bringeth to pass`** — `to`=ADP case, `pass`=NOUN obj (idiom).
- **Correlative `as many as`** — `as`=ADV on `many`, second `as`=SCONJ mark.
- **`insomuch that`** advcl — `insomuch`=ADV advmod, `that`=SCONJ mark.

## 3 Nephi
*(annotation pending — Wave 3)*

## 4 Nephi

- **Inverted "thus did ... year pass"** (multiple sents) — year=nsubj, pass=root, did=aux. Distinctive 4 Nephi temporal-frame pattern.
- **Heavy `save it were`** clauses — exception construction, advcl with `save`=SCONJ mark, `it`=nsubj, `were`=VERB root.
- **`-ites` tokenization quirk** — stanza split "-ites" into `-`(PUNCT) + `ites`(NOUN); annotated as-is.
- **Nominal-list fragments**: "Jacobites, and Josephites, and Zoramites;" — root is one of the proper nouns; rest are `conj`.
- **AICTP fragments without closing main clause** — parenthetical kept as `parataxis` on `came`; sentence structurally open.

## Mormon (book)

- **Three parallel jussive clauses** (sent 287): `may...grant`, `may...remember`, `may...bless` — Mood=Opt on each.
- **`hath made`** — archaic 3sg perfect: `hath`=AUX VBZ, `made`=VERB VBN in acl:relcl.
- **`yea, even`** appositive marker — `yea`=INTJ discourse, `even`=ADV advmod.
- **`are according to the prayers`** — `are` is VERB root (existential/predicative copula), not AUX; `according to` = ADP+fixed.

## Ether

- **Multi-word subordinators** (distinctive!): "save it were", "as though", "after that", "insomuch that" — both tokens as SCONJ/ADV marking the subordinate verb.
- **`save it were X`** archaic exception (very common): `save`=SCONJ mark→`were`(advcl), `it`=nsubj, X=nsubj:pass.
- **Inverted copular predicates** "so [ADJ] was/were [NP]": ADJ=root, cop=AUX, NP=nsubj, result `that`-clause=advcl on ADJ.
- **`as if he had no life`** — as+if both SCONJ mark→had(advcl).
- **Coriantumr/Shiz battle sequences**: heavy use of compound:prt (smote off, raised up, smitten down).
- **Closing "Whether...or..."** advcl pattern (Ether 15): mattereth=root, both alternatives marked.

## Moroni

- **Elliptical gift-list items** (sents 169-175): with no overt verb, gift noun or beneficiary pronoun "another" serves as root; purpose `that`-clauses are advcl dependents. Consistent across all 7 items — a stylistic signature.
- **`then is his grace sufficient`** — subject-verb inversion in consequent clause; `sufficient`(ADJ)=head with `is` as cop.
- **`did I not declare ... like as one crying from the dead`** — embedded direct speech with emphatic `did`-inversion ("did I not declare"); `like as` fixed comparative.
- **Double `that`** — "that that which I have written is true" — SCONJ ccomp marker + PRON fused-relative head.
- **`quick and dead`** — archaic "quick" (= "living"); both ADJ substantivized as nmod objects.

---

## Cross-cutting observations

1. **AICTP density varies**: Helaman, 3 Nephi (forthcoming), Alma show heavy use; Jacob and Moroni use it less. Plausible authorial-signature variable.

2. **Multi-word subordinators are an Ether specialty**: "save it were", "as though", "after that", "insomuch that" all common. Other books use these but Ether's density is higher.

3. **Anacolutha cluster in shorter intercalary books**: Enos, Omni, Words of Mormon all show heavy anacoluthic structure (clauses continue across sentence boundaries, fragmentary nominative-absolute participials). Plausibly reflects the abridged/abbreviated nature of these books.

4. **Optative/jussive with Mood=Opt** appears notably in Jacob and Mormon's closing prayers/blessings. May be a closure-marker.

5. **Fronted-object aux-inversion is a Jacob signature** ("for a long time will I lay up"). Especially common in the vineyard parable; less common elsewhere.

6. **Korihor's speech (Alma 30)** has distinctive complex relative-clause stacking and topicalization ("these things which ye call prophecies, which ye say are handed down by holy prophets, behold, they are foolish traditions") — anti-Christ rhetorical style is syntactically distinguishable from the surrounding narrative.

---

## Updates needed

- Wave 3 (1/2/3 Nephi, Mosiah, Alma rest) will add patterns from those books.
- Patterns for spot-checked corrections also belong here as they're discovered.

Sources to cross-reference for academic publication:
- Skousen's textual-criticism work (variant readings)
- Hardy's annotated editions (intertextuality)
- Existing FEF stylometry literature
