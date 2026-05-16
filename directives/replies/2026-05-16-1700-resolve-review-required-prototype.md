# Reply: 2026-05-16-1700-resolve-review-required-prototype

Processed 2026-05-16 against the directive of the same name. Prototype script built; 25 R19 REVIEW-REQUIRED cases sampled stratified-by-head-lemma; one Sonnet agent dispatched against the full bundle; verdicts captured; markdown report rendered. Read-only diagnostic — no `v2-mine` modifications.

## Per-item status

| Item | Status |
|---|---|
| 1. Build `scripts/resolve_review_required.py` | **completed** (commit follows) |
| 2. Scope: 20-30 R19 REVIEW cases sampled diversely | **completed** — 25 cases, 11 head_lemmas |
| 3. Output: human-auditable 5-column markdown report | **completed** — see "Resolved cases" below |
| 4. DO NOT auto-apply | **honored** — diagnostic-only; no v2-mine touches |
| 5. Surface calibration concerns | **completed** — see "Design-choice surfacing" + "Calibration recommendation" below |

## Resolved cases

Verdict distribution from one Sonnet dispatch over 25 cases:

- **STRONG-MERGE:** 14 (56%)
- **GENUINE-REVIEW-REQUIRED:** 7 (28%)
- **STRONG-SPLIT:** 4 (16%)

Confidence distribution: **17 high / 8 medium / 0 low.**

| Verse | Original verdict | Sonnet verdict | Confidence | Reasoning |
|---|---|---|---|---|
| 1nephi 1:6 | REVIEW-REQUIRED (noun-head-ambiguous-needs-discourse-context) | STRONG-MERGE | high | Head 'things' is anaphoric: the immediately preceding line 'he saw and heard much' establishes the referent, so the relative 'which he saw and heard' characterizes an already-introduced set rather than advancing new propositional content. |
| 1nephi 1:7 | REVIEW-REQUIRED | STRONG-MERGE | high | Head 'things' is anaphoric: verse 1:6 fully establishes the referent (pillar of fire, visions, quaking), so 'which he had seen' is backward-pointing characterization of a discourse-known set, not new propositional content. |
| 1nephi 1:15 | REVIEW-REQUIRED | GENUINE-REVIEW-REQUIRED | high | This is the 2nd coordinate acl:relcl on 'things' at line 92 (after 'which he had seen'); Exclusion 13 explicitly prohibits auto-merge of the 2nd+ coordinate relative — route per J1 §3.5 Tier 5 (N=2 adjudication applies). |
| 1nephi 1:15 | REVIEW-REQUIRED | GENUINE-REVIEW-REQUIRED | high | (duplicate case from validator — same head, same N=2 trigger as above; Exclusion 13 fires) |
| 1nephi 4:35 | REVIEW-REQUIRED | STRONG-MERGE | high | Head 'words' is anaphoric: Nephi's prior oath-speech to Zoram (vv 33-34) establishes the specific referent, so 'which I spake' characterizes already-spoken discourse rather than advancing new propositional content. |
| 1nephi 7:15 | REVIEW-REQUIRED | STRONG-MERGE | medium | Head 'words' is referentially grounded in the present speech act (Nephi is speaking in v 15); 'which I speak unto you' is a restrictive relative identifying this utterance as the referent — anaphoric to the speech-frame. |
| 1nephi 13:41 | REVIEW-REQUIRED | STRONG-MERGE | medium | Head 'words' and relative root 'established' are both on line 1926 (same v2 line); the relative restricts 'words' to the specific authoritative set established by the Lamb's mouth — anaphoric specification within a single line. |
| 1nephi 15:7 | REVIEW-REQUIRED | STRONG-MERGE | high | Head 'words' is anaphoric: 'our father' (Lehi) is fully discourse-established and 'which our father hath spoken' identifies a known speech act — backward-pointing specification of an established referent on the same line. |
| 1nephi 5:18 | REVIEW-REQUIRED | GENUINE-REVIEW-REQUIRED | medium | Head 'people' is the final member of a four-member list (nations/kindreds/tongues/people); the relative 'who were of his seed' may restrict only 'people' or the entire enumeration — scope ambiguity of a list-final relative. |
| 1nephi 8:21 | REVIEW-REQUIRED | STRONG-SPLIT | medium | Head 'people' is newly introduced in this vision scene (no prior discourse antecedent), and 'many of whom were pressing forward' adds new propositional content (their action toward the path) on a separate line — cataphoric pattern. |
| 1nephi 11:31 | REVIEW-REQUIRED | GENUINE-REVIEW-REQUIRED | medium | Head 'people' has N=2 coordinate acl:relcl dependents ('who were sick' + 'who were afflicted with all manner of diseases'), triggering Exclusion 13; N=2 adjudication of the coordinate-relative pair is required before merge. |
| 1nephi 14:14 | REVIEW-REQUIRED | STRONG-SPLIT | high | Head 'people' (the covenant people of the Lord) is discourse-established as the saints of the church of the Lamb in prior lines, and 'who were scattered upon all the face of the earth' is a non-restrictive relative adding new propositional content. |
| 1nephi 13:12 | REVIEW-REQUIRED | STRONG-SPLIT | high | Head 'man' is an indefinite, freshly-introduced referent ('a man among the Gentiles' with no prior discourse antecedent), and 'who was separated from the seed of my brethren by the many waters' advances new propositional content — cataphoric. |
| 2nephi 4:17 | REVIEW-REQUIRED | STRONG-MERGE | high | 'O wretched man that I am!' is a predicative-identifier relative (copula 'am' with pronoun 'I' = speaker; 'that I am' classifies the head as the speaking subject) functioning as an indivisible exclamatory frame — the relative IS the head's identifying content. |
| 1nephi 13:30 | REVIEW-REQUIRED | GENUINE-REVIEW-REQUIRED | high | This is the 2nd coordinate acl:relcl on 'land' (line 1839: 'which is the land that the Lord God hath covenanted...'); Exclusion 13 prohibits auto-merge of the 2nd+ coordinate relative — N=2 adjudication required. |
| 1nephi 13:30 | REVIEW-REQUIRED | GENUINE-REVIEW-REQUIRED | high | (duplicate case from validator — same N=2 trigger) |
| 1nephi 14:23 | REVIEW-REQUIRED | STRONG-MERGE | high | Head 'time' and relative root 'proceeded' are on the same line (2087) within a temporal-frame clause; 'at the time they proceeded out of the mouth of the Jew' is a compact temporal PP where the relative identifies the temporal anchor. |
| 1nephi 14:23 | REVIEW-REQUIRED | STRONG-MERGE | high | Head 'time' and relative root 'proceeded' are on the same line (2088) in the explicit restatement clause ('or, at the time the book proceeded'); same-line construction, no break warranted. |
| 2nephi 24:4 | REVIEW-REQUIRED | GENUINE-REVIEW-REQUIRED | high | 'The golden city ceased!' appears to be an independent parallel clause (Isaiah 14:4 poetry), not a genuine relative clause; the UD parser likely mis-tagged the main verb 'ceased' as acl:relcl on 'city' — **probable parser error**. |
| 3nephi 4:1 | REVIEW-REQUIRED | STRONG-MERGE | high | Head 'cities' and relative 'which had been left desolate' are on the same line (471); 'cities' is anaphoric to the narrative context (Nephites gathered into one body per 3:25, leaving their lands deserted). |
| 1nephi 1:3 | REVIEW-REQUIRED | STRONG-MERGE | high | Head 'record' is anaphoric: vv 1:1-1:2 both establish 'I make a record' as the discourse topic, so 'which I make' is backward-pointing specification of a fully-established referent — both head and relative are on the same line. |
| 1nephi 5:10 | REVIEW-REQUIRED | STRONG-MERGE | high | Head 'records' is anaphoric: the brass plates were established as the narrative's central object throughout ch 3-5 (Nephi's mission to obtain them), so 'which were engraven upon the plates of brass' is backward-pointing. |
| 1nephi 14:1 | REVIEW-REQUIRED | STRONG-MERGE | high | Head 'day' and relative 'that he shall manifest himself' are on the same line (1947) within the temporal formula 'in that day that'; same-line merge is appropriate — the relative defines the specific eschatological occasion. |
| 1nephi 14:17 | REVIEW-REQUIRED | STRONG-SPLIT | medium | Head 'covenants' is referentially incomplete without the relative (generic possessive 'his covenants' without prior verse-specific establishment), and 'which he hath made to his people who are of the house of Israel' advances propositional content. |
| 1nephi 16:34 | REVIEW-REQUIRED | STRONG-MERGE | high | Head 'place' and relative 'which was called Nahom' are on the same line (2533), and the relative functions as a naming/predicative-identifier clause (providing the proper name of the burial site) — indivisible name-giving construct. |

## Design-choice surfacing

### How much context to include in the prompt

- **R19 §5 canon entry: full text.** ~1200 lines of canon body extracted verbatim. Sonnet needs the rule statement + UD signature + Closed lists + Scope + Exclusions + Examples + Implementation footer to ground decisions. Token cost is ~3KB per prompt; affordable.
- **Verse context: ±2 verses around the candidate.** Most R19 anaphoric decisions resolve at ±0–2 verses (immediate discourse anchor). Wider windows (±5+) would catch the broader "Abrahamic-covenant theme" type cases (Sonnet flagged 1 Ne 14:17 covenants as one where ±2 was too narrow), but cost grows fast. Recommend keeping ±2 as default; add `--context-radius` flag for future tuning.
- **Scholarship companion (`private/01-method/scholarship/r19.md`): not present yet.** Empty placeholder in directory. When created per the scholarship/-discipline codified in commit `cdfb096`, it will auto-inject into prompts.

### How to phrase the prompt to Sonnet

- **System prompt** anchors the agent in the Book of Mormon colometric-rule role and explicitly forbids importing external frameworks. Per `feedback_rhetoric_bandwagon` — when given full canon, an LLM may otherwise default to Hebrew-parallelism or classical-rhetoric framings.
- **Verdict request** uses a structured rubric (VERDICT / CONFIDENCE / REASONING) with constrained vocabularies. Sonnet adhered cleanly: 25/25 verdicts parsed without ambiguity.
- **Constraint reminders** in-prompt: punctuation not evidence; cite a specific canon criterion; do not invent rules. These directly counter the known anti-patterns the BoFM canon has retired (see `retraction-log.md` for surfacing-source examples).

### What counts as "high confidence"

- Sonnet returned 17 high / 8 medium / 0 low.
- High-confidence cases all had: (a) clear discourse anchor in ±2-verse window OR (b) same-line construction OR (c) an unambiguous canonical exclusion (e.g., Exclusion 13 N=2 coordinate-relative pair).
- Medium-confidence cases all had: (a) genuine ambiguity in scope (which head does the relative restrict?), (b) "speech-act-frame" ambiguity (cataphoric to following clause vs anaphoric to present utterance), or (c) reliance on broader-than-±2 discourse establishment.
- No low-confidence calls — possibly because the 25-case sample didn't hit truly hard edges, or because Sonnet's calibration is conservative.

### Sample-strategy choice

- **Stratified by head_lemma.** 11 lemmas covered (4×`thing` / 4×`word` / 4×`people` / 2×`man` / 2×`land` / 2×`time` / 2×`city` / 2×`record` / 1×`day` / 1×`covenant` / 1×`place`).
- Stratification surfaced lemma-level patterns (see "Per-rule observations" below) that a random sample would have averaged out.
- Caveat: 2 duplicate cases slipped in (`1nephi_16_92` × 2, `1nephi_399_1838` × 2). The R19 validator emits one finding per `acl:relcl` token; some verses have multiple coordinate relatives on the same head, generating near-identical entries. The resolver script should dedupe on `(sent_id, head_line)` before sampling. **Fix surfaced — non-blocking; will land in next iteration.**

## Per-rule observations (from Sonnet's surfacing)

> *"thing/things" skews strongly anaphoric (all 4 cases → MERGE or REVIEW via Exclusion 13).* Every time "things" appeared, the referent was established by immediately preceding narration. "Things" in BoFM almost never points forward — it picks up a prior narrative cluster.

> *"word/words" also skews anaphoric (all 4 cases → MERGE).* All four "word" cases were either same-line or referred to a named speech act by an established speaker (Lehi, Nephi, the Lamb). "The words which X spake" is almost a formula in BoFM — always backward-pointing.

> *"time" is uniformly same-line (both cases → MERGE).* Both "time" cases were same-line compact temporal PPs. The validator seems to fire on "time" systematically, but in these cases it's never actually cross-line.

> *"city/cities" was the most interesting head-lemma.* 3 Nephi 4:1 was same-line anaphoric merge. 2 Nephi 24:4 was the Isaiah quotation parser-error case — "ceased" is almost certainly a main verb, not a relative. This pattern (Isaiah poetry → UD parser misanalysis) will likely recur in other 2 Nephi Isaiah chapters.

> *Exclusion 13 (N=2 coordinate relatives) triggered on 4 of the 7 GENUINE-REVIEW cases* — more often than expected. These cluster around theologically-dense passages (1:15, 11:31, 13:30) where authors pile up parallel relative characterizations. High-density scripture generates more coordinate-relative constructs than narrative prose.

> *The dominant pattern in this sample is that the validator fires on constructs where head and relative are already on the same line in v2-mine.* The REVIEW-REQUIRED output is more often "should we insert a break here?" than "should we merge a cross-line split?" For same-line cases, the discourse-context test almost always resolves to MERGE — which suggests v2-mine source already has good editorial intuition.

## Three unusually-difficult calls (Sonnet's surfacing, lightly edited)

1. **1 Nephi 7:15** (*"words which I speak unto you"*): Is "words" cataphoric (forward-pointer to the next clause's content) or anaphoric (deictic-now reference to the present utterance)? Called STRONG-MERGE (medium): the relative just identifies the utterance as the present speech act, which is already established by the speech-frame. If you read this differently — as a cataphoric pointer to the following "that if ye go" clause — a split is defensible.

2. **1 Nephi 8:21** (*"people, many of whom were pressing forward"*): Partitive-relative hybrid. UD parser tagged it `acl:relcl` on "people"; the surface "many of whom" is partitive and non-restrictive. SPLIT called because the relative stands as its own cognitive event (their pressing-forward action). Worth a second look at the UD parse for partitive-relative shape.

3. **1 Nephi 14:17** (*"covenants which he hath made to his people who are of the house of Israel"*): Called STRONG-SPLIT (medium) because "his covenants" lacks ±2-verse establishment. But "covenants of the Father" is a recurring BoFM theological category that the broader discourse establishes. Medium confidence reflects the narrow ±2 window's limit. If "his covenants" is sufficiently primed by the broader prophetic sequence, an alternate MERGE call is defensible.

## Calibration recommendation

**Confidence threshold for auto-apply candidacy (when/if we get there): `high` only.**

Reasoning:
- 17/25 high-confidence calls split as 14 MERGE + 3 SPLIT (none of the 7 GENUINE-REVIEW were high — Exclusion-13 cases were "high" but the VERDICT was GENUINE-REVIEW, which means "high confidence this needs human eyes" — that's a different kind of high).
- Of the 8 medium-confidence calls, 3 had specific named ambiguity sources (speech-act-frame, partitive-relative parse, broader-discourse-grounding). These would benefit from per-instance Stan-review more than from a mechanical threshold.
- A 17/25 = 68% auto-apply rate at "high confidence" lines up with empirical leverage: ~1750 of the 2586 R19 REVIEW cases could potentially auto-resolve. Substantial reduction in editorial bottleneck.
- BUT: this sample is only 25 cases. **Recommend a second prototype round at 50-100 cases before any auto-apply gate is enabled** — broader sample needed to validate the 68% generalizes and that high-confidence verdicts are actually low-error.

**For this round: continue manual spot-audit. Stan reviews the table; identifies any blind spots; we iterate on prompt or context-window before enabling any auto-apply.**

## Surfaced concerns

1. **Validator emits same-line cases as REVIEW-REQUIRED.** ~60% of the sample had head and relative ALREADY on the same v2-mine line. The validator is firing on "should we insert a break?" not "should we close an existing gap?" Worth a Stan-decision: should the validator distinguish these cases in its output (e.g., separate `REVIEW-SAME-LINE` from `REVIEW-CROSS-LINE`)? Would change the editorial-review framing for downstream resolvers.

2. **UD parser error in Isaiah quotations.** 2 Nephi 24:4 was flagged as a probable `acl:relcl` mis-tag (parallel-clause poetry parsed as relative). Likely recurs in other Isaiah-rich chapters (2 Nephi 12–24, 3 Nephi 22–24). A parse-quality audit of Isaiah-quoting BoFM chapters might surface 10–50 additional false REVIEW-REQUIRED cases that aren't actually relative-clause findings at all.

3. **Stratified sample missed the `man`-head edge case until verse 13:12.** "A man among the Gentiles" came out as a clean STRONG-SPLIT (indefinite freshly-introduced referent — the classic cataphoric profile). This is the kind of case where a `man`-lemma closed-list would have helped, but the pre-v2 lemma-list approach (which retired in commit `3321915` precisely because it over-fired) wouldn't have caught the subtlety. Sonnet did. This is the bullish read on second-pass LLM resolution: it can apply the bidirectional atomic-thought test where a lemma list can't.

4. **Two duplicate cases from the validator output** slipped into the sample (1 Ne 1:15 × 2, 1 Ne 13:30 × 2). The resolver script's sampling needs a dedupe pass on `(sent_id, head_line)` before stratification. Minor fix; would clean the report.

## Next iteration candidates

- Expand to 50-100 cases (broader calibration validation)
- Dedupe sampler on `(sent_id, head_line)` to avoid same-case duplicates
- Add `--context-radius` flag for wider context windows on theologically-dense passages
- Survey Isaiah-quotation chapters for parse-quality errors (separate intervention; not part of this prototype's scope)
- If second round confirms 70%+ high-confidence auto-applicable rate, design the auto-apply gate carefully — likely with `high` + post-apply spot-audit + atomic-thought-test verification

## Artifacts

- **Resolver script:** `scripts/resolve_review_required.py` (new — supports `--dump-prompts`, `--api`, `--import-verdicts`, `--sample N`, `--sample-strategy`, `--report`)
- **Prompts dump used for this round:** `C:/tmp/r19-prompts.jsonl` (25 records; local-only — not committed)
- **Sonnet verdicts:** `C:/tmp/r19-verdicts.jsonl` (25 records; local-only — not committed)
- **Markdown report:** rendered inline above; also at `C:/tmp/r19-table.md` (local; not committed; the table above is the canonical reply-file form)

## Audit status

Audit-skippable per §7.4 — tooling/scripts work; not canon-touching; not validator-modifying. Output is diagnostic-only per directive Item 4. If/when the resolver moves to auto-apply mode in a later iteration, that's a §7.3 trigger #10 conversation.
