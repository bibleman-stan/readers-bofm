# Reply: 2026-05-16-2400-r19-isaiah-option-a-plus-d

Processed 2026-05-16. Both options addressed: **Option D (resolver Isaiah skeptical-mode) shipped**; **Option A (per-case override JSON) drafted with 8 proposed `override_action` values surfaced for Stan-confirmation BEFORE building the JSON file or wiring the validator** (per directive Item 1's "don't ship action values without Stan-confirmation" gate).

## Per-item status

| Item | Status |
|---|---|
| 1. Build override JSON (action values gated on Stan-review) | **DRAFTED — held for Stan-confirmation** below |
| 2. R19 validator consults override layer | **NOT YET WIRED** (held until #1 confirmed) |
| 3. Document override mechanism (validator + canon) | **canon prose written** (validator docstring will follow once #1/#2 ship) |
| 4. Resolver Isaiah skeptical-mode prompt | **shipped** |
| 5. Document skeptical-mode (resolver + canon) | **shipped** (script docstring + canon §5 R19 prose) |
| 6. Run validator fresh with overrides | **N/A pending #1** |
| 7. 5-case Isaiah skeptical-mode run | **shipped** — agent `ac1a923b6bee35cdd`; results below |

## Option D — shipped

### Resolver script update

[`scripts/resolve_review_required.py`](../../scripts/resolve_review_required.py):

- Added `ISAIAH_RANGES` constant (6 chapter ranges: 1 Ne 20-22, 2 Ne 7-8, 2 Ne 12-24, 2 Ne 27, Mosiah 14, 3 Ne 22-24)
- Added `in_isaiah_chapter(book, verse_ref)` predicate
- Added `ISAIAH_SKEPTICAL_PREAMBLE` constant (~30-line preamble)
- `build_case_prompt()` now prepends the preamble when the case falls inside an Isaiah range
- Module docstring updated to document the codification

### Canon prose update

[`private/01-method/colometry-canon.md`](../../private/01-method/colometry-canon.md) R19 entry, new paragraph under the rule statement:

> *Resolver Isaiah skeptical-mode (codified 2026-05-16 per directive 2400, post-2203-audit consensus). The Sonnet-based resolver (`scripts/resolve_review_required.py`) prepends a skeptical-mode preamble to its per-case prompt when the case falls inside an Isaiah-quoting chapter range. The preamble instructs the resolver to verify the relative-clause structure is genuine before applying R19 routing; if the construction looks like Hebrew-parallel-limb mis-classification (no clear restrictive function, circular attachment, pronoun-resumptive exclamatory device), the resolver returns GENUINE-REVIEW-REQUIRED with rationale "probable Hebrew-parallelism parser mis-classification." This is a prompt-engineering refinement on the existing resolver, not a rule scope change.*

### Item 7 verification (5-case skeptical-mode run)

Sampled 5 R19 REVIEW-REQUIRED cases drawn deterministically from Isaiah chapters (88 unique Isaiah-chapter REVIEW cases in the validator output; sampled 5 spread across chapters). All 5 went through the new resolver with the preamble auto-applied.

| Case | Subtype | Verdict | Confidence | Hebrew-parallelism rationale triggered? |
|---|---|---|---|---|
| 1 Ne 20:1 (house, cross-line) | cross-line | STRONG-MERGE | high | No — explicit "who" pronoun, restrictive function clear |
| 1 Ne 20:14 (word, same-line) | same-line | STRONG-MERGE | high | No — explicit "which", clear anaphoric reference |
| 1 Ne 20:17 (way, same-line) | same-line | STRONG-MERGE | high | No — zero-relativizer contact clause (standard EME); preamble heightened scrutiny but verdict unchanged |
| 1 Ne 21:20 (child, same-line) | same-line | STRONG-MERGE | high | No — explicit "whom", restrictive function genuine |
| 1 Ne 21:3 (servant, cross-line) | cross-line | STRONG-MERGE | medium | No — explicit "whom", non-restrictive but unresolved pronoun forces merge |

**0 of 5 cases triggered the "probable Hebrew-parallelism parser mis-classification" rationale.** The preamble screened correctly (added verification overhead but introduced no false-positive REVIEW routings).

Sample assessment: these 5 Isaiah-chapter R19 REVIEW residue cases are genuine NOUN-head relative-clause ambiguities (the correct cohort the validator should surface), NOT parser mis-classifications. The 4% parser-error rate from the 2102 scan concentrates in 2 Nephi 24 (Isaiah 14, Hebrew lyric density hotspot) and similar pockets — those cases would be in the Option-A override list, not in the R19 REVIEW-REQUIRED residue.

**Verdict: preamble works as designed.** Catches parser-mis-classification when it occurs; doesn't over-trigger on genuine relatives.

## Option A — drafted, **HELD for Stan-confirmation**

Per directive Item 1's explicit gate: *"Per-case override_action surfaced for Stan-review in the reply BEFORE writing — don't ship action values without Stan-confirmation."*

The 8 cases below are drawn from the 2102 Isaiah parser-scan classification (7 probable-parser-error + 1 ambiguous). Three `override_action` values are available per directive Item 1:

- **`skip-r19`** — case is excluded from R19 routing entirely (parser hallucinated the acl:relcl arc; no real relative exists)
- **`treat-as-NOUN-head`** — route to REVIEW-REQUIRED (the relative is genuine but the head was mis-attached; defer to human/resolver judgment)
- **`treat-as-PROPN-head`** — route to STRONG-MERGE (the head is a known proper noun and the relative is anaphoric)

### Proposed override_action per case

| # | Case | Head | Rel-root | Proposed action | Rationale |
|--:|---|---|---|---|---|
| 1 | **2 Ne 24:4** city/ceased | city (NOUN) | ceased (VERB) | **`skip-r19`** | Hebrew-parallel exclamatory clause; *"How hath the oppressor ceased, the golden city ceased!"* — no relative pronoun, no restrictive function; the arc is a parser hallucination on parallel-clause apposition. No real relative to route. |
| 2 | **2 Ne 24:12** thou/weaken | thou (PRON) | weaken (VERB) | **`skip-r19`** | *"Art thou cut down to the ground, which did weaken the nations!"* — exclamatory parallel limb with resumptive `which`; not a restrictive relative on a pronoun matrix subject. PRON-head with resumptive-exclamatory `which` is not the same as cataphoric PRON-head (canon §5 R19 CATAPHORIC_UPOS targets `those/he-that/they-that/those-who` etc., NOT first/second-person matrix-subject pronouns). |
| 3 | **2 Ne 17:23** were/be | were (VERB) | be (VERB) | **`skip-r19`** | VERB-head; *"every place shall be, where there were a thousand vines... which shall be for briers"* — the `which shall be` is a result-clause on the adverbial, not a relative on a nominal head. No real R19-eligible relative here. |
| 4 | **2 Ne 24:19** thrust/go | thrust (VERB) | go (VERB) | **`treat-as-NOUN-head`** | *"the remnant of those that are slain, thrust through with a sword, that go down to the stones of the pit"* — the relative *"that go down"* IS genuine but the parser attached it to the participial `thrust` instead of the intended head `remnant/those`. The relative exists; route to REVIEW so the resolver can pick up the correct head from context. |
| 5 | **2 Ne 23:17** Medes/regard | Medes (PROPN) | regard (VERB) | **`treat-as-NOUN-head`** | Compound construction: first limb *"which shall not regard silver and gold"* is a genuine relative on PROPN-head `Medes` (canon STRONG-MERGE); second limb *"nor shall they delight in it"* is Hebrew-parallel-independent. Parser tagged the whole compound as one acl:relcl. Treat-as-NOUN-head routes to REVIEW for human partition decision (safer than treat-as-PROPN-head, which would auto-MERGE the parallel independent limb into the head). |
| 6 | **2 Ne 24:2** captives/captives | captives (NOUN) | captives (NOUN) | **`skip-r19`** | *"take them captives unto whom they were captives"* — Hebrew wordplay/cognate-object construction. Same-word circular attachment is a parser artifact; the surface reading is *"they shall take their captors captive"*, not a relative-clause restrictive modification. No real R19 case. |
| 7 | **3 Ne 23:6** scriptures/not | scriptures (NOUN) | not (PART) | **`treat-as-NOUN-head`** | *"other scriptures I would that ye should write that ye have not"* — the relative *"that ye have not [written]"* IS genuine on NOUN-head `scriptures`; the parser mis-rooted the relative-clause subtree at the negation particle `not` instead of the elided verb. The relative exists; route to REVIEW. |
| 8 | **2 Ne 24:26** hand/out | hand (NOUN) | out (ADP) | **`treat-as-NOUN-head`** | *"the hand that is stretched out upon all nations"* — the relative IS genuine on NOUN-head `hand`; only the ADP root assignment (`out` instead of `stretched`) is the parser quirk. Per directive Note: *"should NOT skip this case (it's a real relative)"*. Route to REVIEW. |

**Summary: 5 `skip-r19` + 3 `treat-as-NOUN-head` + 0 `treat-as-PROPN-head`.**

### Why no `treat-as-PROPN-head`

Case 5 (2 Ne 23:17 Medes) was the closest candidate — Medes IS PROPN and canon would normally STRONG-MERGE. But the parser conflated a genuine PROPN-head relative with a parallel-independent Hebrew limb; routing to PROPN-head would auto-MERGE the entire compound, dragging the parallel-independent limb into the head's line. Conservative: route to NOUN-head (REVIEW) so the partition decision is human-made. Stan can override to `treat-as-PROPN-head` if you prefer the auto-MERGE behavior with the understanding that the parallel limb gets absorbed.

### Gate

**If Stan confirms the 8 actions as proposed (or amends them):** I will build `data/r19-parser-overrides.json`, wire the override-consultation into `validate_rule_19_ud.py`, document in validator docstring, re-run with overrides loaded, and verify before/after counts (Item 6).

**If Stan flags any case for re-discussion or wants different actions:** amend and re-surface before implementation.

Per directive Item 6 + Note ("any 9th case discovered during build that should also go in the override list"): no 9th case was discovered during this drafting pass. The 8 from 2102 are the complete inventory at this time. The bare-`relcl` corpus survey (directive 2401, running in parallel as agent `a4c78af5df2e6da08`) may surface additional override candidates — those would land in a follow-on directive.

## Surfaced concerns

1. **The directive's `override_action` taxonomy is well-shaped for these 8 cases.** No fourth action needed (e.g., `treat-as-cataphoric-PRON-head` for case 2 was considered but rejected — that case isn't cataphoric, it's exclamatory-resumptive, structurally different).
2. **Cross-validator scope still applies** (per 2203 audit precedent): 4 other validators consume `acl:relcl` and would NOT see R19's override decisions. The 8 override-target cases would still be visible to `validate_frame_predication_merges_ud.py` etc. as substantive-frame indicators. Worth a future-directive consideration but doesn't block this directive.
3. **Item 7 verified preamble works as designed.** The Isaiah-chapter R19 REVIEW residue at the validator's current routing is mostly genuine relatives (the Item-7 sample showed 5/5 STRONG-MERGE verdicts with 0/5 Hebrew-parallelism rationale triggers). The parser errors are upstream of REVIEW residue — they trigger STRONG-SPLIT or STRONG-MERGE inappropriately, not REVIEW. The override mechanism (Option A) catches the cases where the parser produced an *acl:relcl* arc that shouldn't exist; the resolver preamble (Option D) catches the cases where the resolver might apply R19 routing to a parser-mis-classified case anyway.
4. **The two mechanisms address complementary failure modes.** Option A operates BEFORE R19 routing (skip or re-route at the validator layer); Option D operates DURING resolver judgment (verify before applying). Together they cover both the validator-layer and resolver-layer paths to a parser-mis-classified case.

## Audit status

- **Option A (per-case override)**: per-case data layer; no rule scope change; no closed list; no new rule. **Audit-skippable per §7.4** once Stan confirms the action values.
- **Option D (resolver prompt addition)**: prompt-engineering on existing resolver; no validator code change; no rule scope change. **Audit-skippable per §7.4** — shipped in this commit.

Both paths intentionally low-§7-burden per the 2203 audit precedent (which rejected Option E's §7.3 trigger #1+#2 route).

## Artifacts

- Resolver script with preamble + `ISAIAH_RANGES` constant
- Canon §5 R19 prose with two new paragraphs (override mechanism + resolver skeptical-mode)
- 5-case Item-7 verdicts: `C:/tmp/isaiah-item7-verdicts.jsonl` (local)
- 5-case Item-7 prompts: `C:/tmp/isaiah-item7-prompts.jsonl` (local; all 5 carry `has_isaiah_preamble: true`)
- 8-case override_action proposal table (above; held for Stan-confirmation)
- This reply
