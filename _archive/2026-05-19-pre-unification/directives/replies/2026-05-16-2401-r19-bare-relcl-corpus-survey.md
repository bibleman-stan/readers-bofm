# Reply: 2026-05-16-2401-r19-bare-relcl-corpus-survey

Processed 2026-05-16. Extracted all 339 bare `relcl` tokens corpus-wide; Sonnet single-pass classified each as `legitimate-relative-mis-labeled` / `non-relative-construction` / `ambiguous`. Read-only diagnostic per directive Item 5.

## Per-item status

| Item | Status |
|---|---|
| 1. Extract 339 bare `relcl` tokens | **completed** — [`scripts/extract_bare_relcl.py`](../../scripts/extract_bare_relcl.py) (new); output at `C:/tmp/bare-relcl.jsonl` |
| 2. Sonnet single-pass classification | **completed** — agent `a4c78af5df2e6da08`; output at `C:/tmp/bare-relcl-classified.jsonl` |
| 3. Aggregate + per-book + head-UPOS breakdown | **completed** below |
| 4. Intervention recommendation per directive thresholds | **completed** below |
| 5. Diagnostic only; no fixes | **honored** |

## Aggregate classification (339 cases)

| Classification | Count | % |
|---|---:|---:|
| **legitimate-relative-mis-labeled** | **320** | **94.4%** |
| ambiguous | 12 | 3.5% |
| non-relative-construction | 7 | 2.1% |

**94.4% legitimate ≫ 85% threshold for Option γ viability per the directive's Item 4 framing.**

## Per-book breakdown

| Book | Total | Legit | Legit% | NonRel | Ambig |
|---|---:|---:|---:|---:|---:|
| 1 Nephi | 45 | 44 | 98% | 0 | 1 |
| 2 Nephi | 104 | 96 | 92% | 4 | 4 |
| Mosiah | 73 | 66 | 90% | 2 | 5 |
| Alma | 18 | 18 | 100% | 0 | 0 |
| Helaman | 86 | 83 | 97% | 1 | 2 |
| 3 Nephi | 13 | 13 | 100% | 0 | 0 |
| **Total** | **339** | **320** | **94%** | **7** | **12** |

(Nine books returned 0 bare `relcl` cases corpus-wide; confirmed in 2206.)

2 Nephi and Mosiah carry all 6 non-relative cases — 2 Nephi unsurprisingly (Isaiah-quotation register), Mosiah more curiously. Helaman and 3 Nephi are essentially clean.

## Head-UPOS breakdown of the legitimate cohort (N=320)

If Option γ accepts bare `relcl` for R19 routing, the head-UPOS distribution determines what disposition each case would receive:

| Head UPOS | Count | % | R19 routing if accepted |
|---|---:|---:|---|
| **NOUN** | 205 | 64% | → REVIEW-REQUIRED (joins the existing 2586-case REVIEW bucket) |
| **PRON** | 93 | 29% | → STRONG-SPLIT (immediate auto-apply candidates) |
| **PROPN** | 16 | 5% | → STRONG-MERGE (immediate auto-apply candidates) |
| **ADJ-as-nominal** | 6 | 2% | → falls outside current UPOS dispatch; would need ADJ branch added OR fall-through to REVIEW |

**Key implication for scope of Option γ:**
- **109 of the 320 legitimate cases would auto-apply** (93 STRONG-SPLIT + 16 STRONG-MERGE) — Category A mechanical apply. Substantial impact.
- **205 NOUN-head cases** would enter the existing REVIEW pipeline; no immediate apply, but visible to the resolver and to Option-A overrides going forward.
- **6 ADJ-as-nominal cases** (mainly "as many as" / "few" / "righteous" used as nominal heads) would need explicit handling — either an ADJ branch in the UPOS dispatch or a fallback to REVIEW.

## Edge cases the directive flagged (audit's main concern about Option γ)

### Non-relative-construction (7 cases — full enumeration)

| Verse | Fragment | Type |
|---|---|---|
| 2 Ne 8:10 | "a way for the ransomed to pass over" | Infinitival complement mis-tagged |
| 2 Ne 8:18 | "none to guide her" | Infinitival modifier mis-tagged |
| 2 Ne 10:15 (×2) | "for this cause that my covenants may be fulfilled" | Purpose subordinator mis-tagged |
| Mosiah 7:28 | "did they do which brought down the wrath of God" | VERB-head advcl/ccomp mis-tag |
| Mosiah 28:10 | "no one to confer the kingdom upon" | Infinitival complement mis-tagged |
| Helaman 13:38 | "ye have sought... which thing is contrary" | Resumptive nominal — refers back to entire preceding clause |

**Of these 7, one is particularly concerning under Option γ**: 2 Ne 8:18 *"none to guide her"* has `head_upos=PRON`. Under naive Option γ (deprel filter extension only), R19 would route this to STRONG-SPLIT — a **false-positive auto-apply**. The other 6 land safely (NOUN/PROPN heads → REVIEW or MERGE bucket; either way no false-apply).

### Ambiguous (12 cases) — wrong-arc-head dominates

8 of 12 ambiguous cases have **wrong-arc-head problems** (parser attached to VERB or COP instead of the surrounding NOUN). Examples:
- 2 Ne 12:6 "who art thou that... that hath stretched forth the heavens" — `head_upos=COP`
- 2 Ne 10:15 "may be fulfilled which I have made" — `head_upos=VERB`; correct antecedent is NOUN `covenants`
- Mosiah 8:16 "possess the power of God which no man can" — `head_upos=VERB`; correct antecedent is NOUN `power`

Under Option γ, these would have `head_upos=VERB` or `COP` which is **outside R19's UPOS dispatch table (PROPN/PRON/DET/NOUN)**. They'd fall through to whatever R19's default is. If the validator's else-branch routes to REVIEW, these wouldn't auto-apply; if it skips, they wouldn't enter the routing at all.

## Intervention recommendation (per directive Item 4)

**The 94.4% legitimate rate clears the directive's Option-γ-viability threshold (>85%). Recommend pursuing Option γ as a follow-on directive with a §7.3 audit per the 2203 precedent**, structured to specifically address the 3 edge classes the survey surfaced:

### What the §7.3 audit would need to address

1. **The 1 false-apply case from non-relative-construction** (2 Ne 8:18 "none to guide her", PRON-head):
   - **Mitigation**: extend the override mechanism (Option A from 2400) to also accept "treat-as-skip" entries for non-relative cases. Pre-populate with this 1 case + the others surfaced.
   - OR: narrow Option γ to bare `relcl` only when head_upos in {NOUN, PROPN} (skip PRON/DET extension). Trades scope (~109 → ~16 auto-apply cases) for safety.
2. **The 8 wrong-arc-head ambiguous cases** (VERB/COP heads):
   - These would naturally fall outside R19's UPOS dispatch and into the validator's default branch. Explicitly: add a `head_upos in {VERB, COP, AUX, ADP}` → SKIP branch that routes these to REVIEW with a `wrong-arc-head` reason tag, so the resolver knows to consult the surrounding NOUN context.
3. **The 6 ADJ-as-nominal cases**: add an ADJ-head branch to UPOS dispatch (would route to REVIEW per the conservative-default policy), OR explicit skip with `non-standard-head-upos` reason.
4. **Cross-validator scope** (carried over from 2203 + 2206): if R19 expands to bare `relcl`, the 4 other validators that consume `acl:relcl` (`validate_frame_predication_merges_ud.py`, `validate_severed_complement_ud.py`, `validate_rule_17_ud.py`, `validate_rule_21_ud.py`) would need a coordinated decision about whether they also expand. Stan-decision.

### Alternative path (per directive)

If the §7.3 audit overhead isn't worth the 109-case auto-apply leverage, **Option β (per-case override JSON for the 109 PRON+PROPN-head subset)** is the safer non-§7.3 alternative. The 109 entries would be larger than the 8-case Isaiah override (drafted in 2400), but still manageable as a data-layer artifact.

**Cost framing**:

| Option | Auto-apply yield | §7.3 audit needed | Cross-validator coordination |
|---|---:|---|---|
| γ (validator extension) | 109 cases | Yes (trigger #1+#2) | Yes |
| β (per-case override) | 109 cases | No | No |
| Do nothing | 0 cases | No | No |

Option β nets the same auto-apply yield as Option γ at lower overhead, but with a larger ongoing data-layer maintenance footprint as new bare-`relcl` cases accumulate. Option γ is the cleaner long-term solution but requires §7.3 clearance.

## Surfaced concerns

1. **The non-standard `relcl` deprel is uneven across the corpus**: Helaman 25%, 2 Nephi 21%, Mosiah 14%, 1 Nephi 11% vs 3 Nephi 2%, Alma 1%, and 9 books at 0%. Audit β from 2206 hypothesized batch-parser-version anomaly; the per-book pattern is consistent with that — possibly different books were processed with different Stanza versions or different LLM-overlay configurations.
2. **The 7 non-relative cases cluster into 3 sub-patterns**: infinitival complement mis-tags (3 cases), purpose-subordinator mis-tags (2 cases, single verse), and a resumptive nominal (1 case) plus a VERB-head ccomp/advcl mis-tag (1 case). All are structurally recognizable — could be detected by additional structural signals if Stan wants narrow-targeted exclusion rules.
3. **The 8 wrong-arc-head ambiguous cases are a parser-quality signal independent of R19**. Cross-validator coordination would benefit from a corpus-level "wrong-arc-head" annotation (similar to the override mechanism from 2400) visible to all consumers.
4. **The 6 ADJ-as-nominal cases are EME-canonical** ("as many as", "few that", "righteous which") and represent a structural pattern R19's current UPOS dispatch doesn't formally address. Adding an ADJ branch is a small UPOS-dispatch refinement; it could be done independently of Option γ as a non-§7.3 change since it's the conservative-default-to-REVIEW shape.

## Audit status

Audit-skippable per §7.4 (diagnostic scan only; no rule change, no validator change, no parser change).

**Option γ specifically would trip §7.3 trigger #1 (new sub-category in validator dispatch — expanding which deprels R19 considers) + trigger #2 (the set of accepted deprels is a closed list).** That audit would need to address the 3 edge classes above plus the cross-validator coordination question. The 2203 audit precedent applies.

## Artifacts

- **Extractor:** [`scripts/extract_bare_relcl.py`](../../scripts/extract_bare_relcl.py) (new; uses validators/parsing UD infra; line-mapped to v2-mine for verse refs)
- **Raw extraction:** `C:/tmp/bare-relcl.jsonl` (339 records; local)
- **Sonnet classification:** `C:/tmp/bare-relcl-classified.jsonl` (339 records with classification + rationale; local)
- **This reply**

## Cost note

339 Sonnet classifications in a single dispatch. ~6 minutes wall-time. Modest. Per `feedback_model_selection_frugality` Sonnet is correct tier for structured classification within a defined rubric.
