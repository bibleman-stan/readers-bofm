# R19 Isaiah parser cases — Option A + Option D (per 2203 audit consensus)

## Context

The 2203 directive (parser-suspect pre-filter, Option E) was REJECTED by both parallel Opus audits. Reply at `directives/replies/2026-05-16-2203-r19-parser-suspect-prefilter.md` documents the convergent findings:

- S1 (`head_upos in {VERB, PRON, AUX}`) collides with R19's existing CATAPHORIC_UPOS closed list — would route 897 currently-mechanical-apply cases to PARSER-SUSPECT
- S3 (`head_form == rel_root_form`) catches Alma 21:18, a canon §5 R19 explicit MERGE example
- Signal set enumerated from 7-case sample → 1,111 corpus hits → ~1% clean rate (fails §7.8 ≥80% adoption test)

Both audits converged on the path forward: **Option A (per-case override JSON, 7-15 entries) + Option D (resolver-skeptical-mode prompt for Isaiah-quoting chapters).** Both audit-clear; neither trips §7.3 triggers.

This directive implements both. Together they address the 2102 Isaiah-scan inventory (7 probable parser errors + 1 ambiguous) WITHOUT canon-rule-extension risk.

## Items

### Option A — per-case override JSON

1. **Build override JSON** at `data/r19-parser-overrides.json` with the 8 cases from the 2102 reply:
   - 2 Ne 24:4 (`city/ceased` — same-word predicative-identifier pattern in lyric poetry)
   - 2 Ne 24:12 (`thou/weaken` — pronoun matrix subject; relative is exclamatory)
   - 2 Ne 17:23 (`were/be` — VERB head; result-clause not relative)
   - 2 Ne 24:19 (`thrust/go` — participial-verb head)
   - 2 Ne 23:17 (`Medes/regard` — Hebrew-parallel limb)
   - 2 Ne 24:2 (`captives/captives` — same-word circular)
   - 3 Ne 23:6 (`scriptures/not` — PART rel_root)
   - 2 Ne 24:26 (`hand/out` — ADP rel_root, ambiguous)

   Schema per entry:
   ```json
   {
     "<book>_<chapter>_<verse>_<token_id>": {
       "original_deprel": "acl:relcl",
       "override_action": "skip-r19" | "treat-as-NOUN-head" | "treat-as-PRON-head",
       "reason": "<one-sentence per-case rationale from 2102 reply>"
     }
   }
   ```

   The `override_action` field determines how R19 handles the case: `skip-r19` means the case is excluded from R19 routing entirely; `treat-as-NOUN-head` routes to REVIEW; `treat-as-PRON-head` routes to STRONG-SPLIT. **Per-case override_action surfaced for Stan-review in the reply BEFORE writing — don't ship action values without Stan-confirmation.**

2. **R19 validator consults the override** before applying its standard classification path. Implementation in `validators/colometry/validate_rule_19_ud.py`: lookup `<book>_<chapter>_<verse>_<token_id>` key; if present, apply `override_action`; otherwise proceed with normal routing.

3. **Document the override mechanism** in R19 validator docstring + canon §5 R19 prose. This is a per-case data layer, not a rule-scope change.

### Option D — resolver Isaiah skeptical-mode prompt

4. **Update `scripts/resolve_review_required.py`** to add an Isaiah-chapter detection check. When the case's verse falls in:
   - 1 Ne 20-22 (Isaiah 48-49)
   - 2 Ne 7-8 (Isaiah 50-51)
   - 2 Ne 12-24 (Isaiah 2-14)
   - 2 Ne 27 (Isaiah 29)
   - Mosiah 14 (Isaiah 53)
   - 3 Ne 22-24 (Isaiah 54 + Malachi)

   Prepend a skeptical-mode preamble to the Sonnet prompt:

   > This case is in an Isaiah-quoting chapter. The UD parser sometimes mis-classifies Hebrew-style parallelism as `acl:relcl` when the construction is actually parallel exclamatory limbs without a relative pronoun. Before applying R19 logic, verify the relative-clause structure is genuine (look for an actual relative pronoun + restrictive modification of the head NP). If the construction is Hebrew-parallel-limb rather than restrictive relative, return GENUINE-REVIEW-REQUIRED with reasoning "probable Hebrew-parallelism parser mis-classification."

5. **Document the skeptical-mode addition** in the resolver script's module docstring + a brief mention in R19 canon §5 prose under the resolver-handling section.

### Verification

6. **Run validator fresh** with overrides loaded. Before/after counts:
   - 8 override cases: confirm they're routed per `override_action` instead of normal R19 path
   - Other 2580 REVIEW cases: confirm unchanged disposition (override layer should ONLY affect the 8 listed cases)

7. **Run resolver against 5 Isaiah-chapter REVIEW cases** (sampled) with skeptical-mode active. Confirm Sonnet receives + considers the preamble; surface the verdicts vs what the non-skeptical mode would have produced.

## Reporting

Reply at `directives/replies/2026-05-16-2400-r19-isaiah-option-a-plus-d.md`:

- **Per-case override_action proposals for Stan-review** (Item 1 — required BEFORE shipping)
- Override JSON commit hash + validator-load verification
- Resolver script update commit hash
- Canon prose excerpts (Items 3 + 5)
- Before/after counts (Item 6)
- 5-case skeptical-mode comparison (Item 7)
- Any 9th case discovered during build that should also go in the override list

## Audit triggers

- **Option A (per-case override)**: per-case data layer; no rule scope change; no new closed list; no new rule. **Audit-skippable per §7.4.**
- **Option D (resolver prompt addition)**: prompt-engineering on existing resolver; no validator code change; no rule scope change. **Audit-skippable per §7.4.**

Per the 2203 audit precedent: these are intentionally the low-§7-burden paths. The rejected Option E carried §7.3 triggers; A + D do not.

## Note on 8th case

2 Ne 24:26 (`hand/out`) was classified as AMBIGUOUS in the 2102 reply — the relative IS genuine; only the parser's ADP root assignment is wrong. The R19 routing should NOT skip this case (it's a real relative); the override might route to `treat-as-NOUN-head` instead. Surface in the per-case override_action proposals for Stan-review.
