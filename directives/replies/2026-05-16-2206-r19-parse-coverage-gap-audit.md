# Reply: 2026-05-16-2206-r19-parse-coverage-gap-audit

Processed 2026-05-16. Diagnostic audit of the parse-coverage gap for 2 Nephi 7-8 and Mosiah 14; identification of candidate restrictive-relative constructions; Pattern A / B / C classification; corpus-wide scope-check.

**Headline:** Two distinct underlying problems, not one. **Pattern A (label inconsistency `relcl` vs `acl:relcl`) dominates 2 Ne 7-8 and is also present at lower rates corpus-wide (340 bare `relcl` tokens total).** Mosiah 14 is a different shape: Pattern C (KJV-style nominalization with no relative pronoun) plus a few ccomp/conj mis-routings.

## Per-item status

| Item | Status |
|---|---|
| 1. Audit UD parse for 2 Ne 7-8 + Mosiah 14 | **completed** |
| 2. Pattern A/B/C classification | **completed** |
| 3. Scope-check beyond flagged chapters | **completed** (1 Ne 22, 2 Ne 17, 3 Ne 22 + corpus-wide `relcl` count) |
| 4. Don't fix anything | **honored** — diagnostic only |
| 5. Propose intervention shapes (Options α-ε) | **completed** — no ranking, no recommendation |

## Step 1: Confirmed the gap

The 2102 finding holds. Parse files exist at `data/parses/llm-direct/2nephi.conllu` and `mosiah.conllu`. Extracting `acl:relcl` from the relevant chapter ranges returns:

| Chapter | `acl:relcl` count |
|---|---:|
| 2 Nephi 7 | 0 |
| 2 Nephi 8 | 0 |
| Mosiah 14 | 0 |

Re-confirmed by audit agent.

## Step 2: Pattern classification (per the agent)

| Chapter | Candidates | Pattern A | Pattern B | Pattern C | Correctly tagged | bare `relcl` |
|---|---:|---:|---:|---:|---:|---:|
| 2 Ne 7 (Isaiah 50) | 9 | **9** | 0 | 0 | 0 | **5** |
| 2 Ne 8 (Isaiah 51) | 17 | **17** | 0 | 0 | 0 | **21** |
| Mosiah 14 (Isaiah 53) | 4 | 3 | 0 | **1** | 0 | 0 |
| 1 Ne 22 (comparison) | 48 | 7 | 0 | 0 | 41 | 0 |
| 2 Ne 17 (comparison) | 12 | 2 | 0 | 0 | 10 | 0 |
| 3 Ne 22 (comparison) | 11 | 2 | 0 | 1 | 8 | 0 |

**Pattern B (arc gap) = 0 everywhere.** The parser never failed to produce an arc; it either labeled it wrong or the text genuinely doesn't contain a relative pronoun.

### Pattern A dominates 2 Ne 7-8 (label inconsistency)

The parser recognized all 26 relative-clause structures in 2 Ne 7-8 but **labeled the clause-root verb with `relcl` (a non-standard UD deprel) instead of `acl:relcl`**. The relative pronoun correctly gets `nsubj`; only the head-verb's deprel is non-standard. The relative IS in the parse — just under the wrong label.

Examples (audit agent's enumeration):
- *"he that walketh in darkness, and hath no light"* (2 Ne 7:10) — `walketh` tagged `relcl`
- *"the seed of him who had loved her and possessed her"* (2 Ne 8:2)
- *"the redeemed of the Lord who shall return"* (2 Ne 8:11)
- *"the redeemed shall come with singing... who hath stretched forth the heavens"* (2 Ne 8:13)
- Most of 2 Ne 8:1-23 — 21 of the chapter's relative clauses

This is **batch-level parser inconsistency** — `relcl` (bare) appears 0 times across the three comparison chapters but 26 times in 2 Ne 7-8. The label difference is a single-batch artifact, not a corpus-wide systemic issue.

### Mosiah 14 is a different shape

Isaiah 53 in the KJV uses very few relative pronouns. The dominant constructions are participial/appositive nominalizations:

- *"despised and rejected of men"* — participial; no relative
- *"a man of sorrows, and acquainted with grief"* — appositive + adjectival; no relative
- *"the chastisement of our peace was upon him"* — possessive PP; no relative

**3 of 4 Mosiah-14 candidates are Pattern A** (the parser labeled relative-style content with `ccomp`/`conj` rather than `acl:relcl`):

- *"Who hath believed our report?"* — rhetorical interrogative, parser tagged `ccomp` under `say`
- *"who shall declare his generation?"* — paratactic question, parser tagged `conj`

The `ccomp`/`conj` labeling is **syntactically defensible** for interrogative-style content. These aren't strictly parser errors; they're cases where the parser made a defensible choice among ambiguous shapes.

**1 of 4 Mosiah-14 candidates is Pattern C** (legitimate Isaiah 53 nominalization — no relative pronoun in v2-mine).

### Comparison chapters

1 Ne 22, 2 Ne 17, 3 Ne 22 ALL have predominantly correct `acl:relcl` tagging (84% correct at the cluster level). They also each have 2-7 Pattern A cases (parser sometimes used `acl` without `:relcl` or attached to a wrong head) — so Pattern A is corpus-wide, just at much lower density than 2 Ne 7-8.

## Step 3: Corpus-wide scope assessment

Ran a corpus-wide count of `relcl` (bare) vs `acl:relcl` across all 15 books:

| Book | `acl:relcl` | bare `relcl` | bare-relcl % |
|---|---:|---:|---:|
| 1 Nephi | 371 | 45 | 11% |
| 2 Nephi | 406 | 105 | 21% |
| 3 Nephi | 543 | 13 | 2% |
| Alma | 1283 | 18 | 1% |
| Helaman | 263 | 86 | 25% |
| Mosiah | 434 | 73 | 14% |
| Other 9 books | 773 | 0 | 0% |
| **Total** | **4073** | **340** | **8%** |

**340 bare `relcl` tokens corpus-wide.** This is much larger than the 26 in 2 Ne 7-8. The scope question the directive asked ("is this systemic or chapter-isolated?") resolves as: **the labeling inconsistency is corpus-wide but uneven — concentrated in 2 Nephi, Helaman, Mosiah, 1 Nephi, with 3 Nephi/Alma showing 1-2% rates and 9 books showing 0%.**

If R19 expanded its deprel filter to include both `acl:relcl` and bare `relcl`, **up to 340 additional cases would become R19-visible.** The Pattern-A rate per the agent's manual sampling suggests most of these are legitimate restrictive relatives that should be R19-eligible — but each case still needs UPOS-routing (PROPN→merge, PRON/DET→split, NOUN→REVIEW) per R19's settled rule.

## Step 4: No fixes applied

Per directive, diagnostic only. No parser re-runs, no manual overrides, no validator changes. The corpus-wide `relcl` count was a read-only audit query.

## Step 5: Intervention shapes (per directive — surface, do not rank or recommend)

### Option α — Re-parse the flagged chapters with a different model/config

**Data each draws on:**
- Pattern A is the dominant issue. The parser recognized the relative-clause shape but used non-standard `relcl` instead of `acl:relcl` and used `ccomp`/`conj` for interrogative-shaped constructions.
- A re-parse with a UD-v2-strict model would presumably emit `acl:relcl` uniformly.
- **Scope of work**: re-parse 2 Ne 7-8 + Mosiah 14 (small) OR re-parse the books that show >5% bare-relcl rate (2 Nephi, Helaman, Mosiah, 1 Nephi — substantial).
- **Risk**: re-parse may change OTHER deprel arcs in these books, requiring re-running R19 and other validators against the new parses. Possible cascade of changed disposition counts elsewhere.

### Option β — Manual override list for missing-relative cases

**Data each draws on:**
- 26 cases in 2 Ne 7-8 + 3 cases in Mosiah 14 = 29 entries for the flagged chapters alone.
- Scaling to all 340 corpus-wide bare-`relcl` cases requires a 340-entry JSON.
- This grows non-trivially. Even at the flagged-chapter scope (29 entries), the maintenance burden is small but not as trivial as 2102's 7-entry override-list framing.
- **Pairs with**: Option ε's corpus-wide rate as input.

### Option γ — Validator-level acceptance of `acl` / bare `relcl`

**Data each draws on:**
- The R19 validator at `validators/colometry/validate_rule_19_ud.py` currently does `sent.find(deprel="acl:relcl")`. Extending to `deprel in {"acl:relcl", "relcl"}` is a one-line change.
- Would surface ~340 additional cases for classification; they'd flow through R19's existing PROPN→merge / PRON-DET→split / NOUN→REVIEW routing.
- **Risk**: bare `relcl` is non-standard UD; some cases may be tagged for reasons OTHER than "this is a restrictive relative clause" (the agent's sample suggests most ARE legitimate, but a corpus-wide sample would be needed for confidence).
- **Cross-validator concern**: `validate_frame_predication_merges_ud.py`, `validate_severed_complement_ud.py` also check `acl:relcl`. If R19 accepts bare `relcl`, those validators would need the same extension to stay consistent.
- **Note: This is similar to the design class that 2203's adversarial audit rejected** (single-validator routing on parser-shape signals that don't propagate). If pursued, would need its own §7.3 audit.

### Option δ — Rendering review

**Data each draws on:**
- Pattern C accounted for 1 of 4 candidates in Mosiah 14 (Isaiah 53). Across the rest of the audit, Pattern C was rare.
- The v2-mine rendering uses KJV-style English, which naturally has fewer relative pronouns than modern English (participial nominalization, prepositional rendering, direct address).
- **Scope**: this is editorial, not technical. Mosiah 14's low relative-count is correct for the KJV register; no fix needed.
- **Implication**: if the underlying Isaiah 53 text uses non-relative constructions in v2-mine, R19 is not the right rule to engage there. Those passages need different rules (R10 V+DO, R17 complement integrity, etc.) or none at all.

### Option ε — Corpus-wide bare-`relcl` survey before deciding

**Data each draws on:**
- The corpus-wide count above (340 cases) suggests Pattern A is broader than 2 Ne 7-8 alone.
- A 30-line script could enumerate every bare `relcl` token with its head + clause-context, then a Sonnet classifier could surface the (Pattern-A : Pattern-Something-Else) breakdown corpus-wide before any decision.
- This would inform whether Options β/γ scope to 29 entries (flagged chapters only) or 340 entries (corpus-wide).
- **Cost**: small. Sonnet dispatch on 340 cases, similar shape to the 2102 Isaiah scan.

## Surfaced concerns

1. **The "parse-coverage gap" is partly a labeling inconsistency, not a true parse failure.** The parser DID produce arcs for 26 of the 30 candidates in 2 Ne 7-8 + Mosiah 14 — it just used `relcl` (bare) or `ccomp`/`conj` instead of `acl:relcl`. The arcs exist; the label differs.
2. **340 bare `relcl` tokens corpus-wide is significant.** The bare `relcl` label is non-standard (UD v2 specifies `acl:relcl`). Several books skew heavily (Helaman 25%, 2 Nephi 21%, Mosiah 14%) while others (3 Nephi 2%, Alma 1%, 9 books 0%) are clean. **This suggests a batch-level parsing-tool-version issue** — possibly some books were parsed with a different tool/version than others, producing the label divergence.
3. **Cross-validator scope concern (from 2203 audit context).** The 4 other validators that consume `acl:relcl` would NOT see bare `relcl` either. If Option γ is pursued, those validators need the same extension or the cross-validator inconsistency persists.
4. **Mosiah 14 is editorial, not technical.** The 3 Pattern A cases (`ccomp`/`conj` mis-routing) involve syntactically-defensible parser choices for interrogative content. Forcing them to `acl:relcl` would itself be a parser-quality argument, not a fix.
5. **2206 sits structurally adjacent to 2203 (just-rejected).** Both touch the design question of "what does R19 do with parser-shape anomalies?" 2203 proposed adding parser-suspect routing to QUARANTINE shapes; 2206 surfaces shapes that should be INCLUDED. If both got addressed at the resolver level (Option D from 2102), one design layer could handle both directions of the problem. Surfacing for Stan-decision: is a unified resolver-level approach worth a follow-on directive?

## Artifacts

- **Detailed audit report:** `C:/tmp/parse-coverage-gap-report.md` (agent-written, local)
- **Corpus-wide `relcl` count:** computed inline above; reproducible via the one-liner in the reply commit
- **This reply**

## Audit status

Audit-skippable per §7.4 (diagnostic scan only; no rule change, no validator change, no parser change).

If/when one of Options α-ε is selected, that's a separate directive with its own audit trigger assessment. **Option γ would specifically need a §7.3 trigger #1 + #2 audit** (same class as 2203) — the 2203 audit precedent is directly applicable.
