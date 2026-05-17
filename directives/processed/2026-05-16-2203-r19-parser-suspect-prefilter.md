# R19 parser-suspect pre-filter — Option E for Isaiah parser errors

## Context

The 2102 reply (`directives/replies/2026-05-16-2102-isaiah-quotation-parser-scan.md`) surfaced 7 probable UD parser errors in 180 `acl:relcl` tokens across Isaiah-quoting BoFM chapters (4% error rate; 5 of 8 anomalies concentrated in 2 Nephi 24 = Isaiah 14).

Stan-decision: **Option E (validator pre-filter on structural signals).** Adds inline checks in `validate_rule_19_ud.py` routing specific parser-error signatures to a new `PARSER-SUSPECT` subtype BEFORE the rule's normal classification. Catches 5 of 7 errors + the 1 ambiguous case mechanically; remaining 2 (Hebrew-parallel limb without surface signal — 2 Ne 23:17, 2 Ne 24:4) still flow to LLM resolution via the resolver.

This adds a new subtag joining `same-line` / `cross-line`. **Trips §7.3 trigger #1 (new named sub-category) AND trigger #2 (closed-list-based — the structural-signal set is effectively a closed list of error signatures).** Requires ≥2 parallel adversarial agents BEFORE implementation per CLAUDE.md adversarial-audit discipline.

## Items

1. **Pre-build adversarial audit (≥2 parallel Sonnet agents).** Each agent receives:
   - The 2102 reply documenting the 7 probable-error cases + their structural signals
   - The proposed pre-filter logic:
     - `head_upos in {VERB, PRON, AUX}` → PARSER-SUSPECT
     - `rel_root_upos in {PART, ADP}` → PARSER-SUSPECT
     - `head_form == rel_root_form` (same-word circular attachment) → PARSER-SUSPECT
   - The corpus context (R19 validator scope; cross-rule interactions with other validators that consume `acl:relcl`)

   And probes for:
   - **False-positive risk**: legitimate constructions that match the signals (e.g., participial heads tagged VERB but functioning nominally; pronominal heads with restrictive relatives in dialectal English; `rel_root_upos=PART` for legitimate negation-fronting)
   - **False-negative risk**: known parser-error shapes NOT caught by the signals (the 2 Hebrew-parallel cases are already known; others?)
   - **Cross-rule interactions**: validators outside R19 that consume `acl:relcl` and might be affected (audit dependency graph)
   - **Corpus-wide impact**: extrapolate from Isaiah scan; how many additional cases corpus-wide would the signals catch?

2. **If audit clears (no must-fix findings)**: proceed to implementation. If audit surfaces must-fix findings: STOP and surface specifics for Stan-review.

3. **Implementation in `validators/colometry/validate_rule_19_ud.py`**:
   - Add the three pre-filter checks BEFORE the existing same-line / cross-line classification
   - Route matching cases to a new `review_subtype: 'parser-suspect'` value (alongside existing `'same-line'`, `'cross-line'`, `None`)
   - PARSER-SUSPECT cases do NOT get same-line / cross-line classification (they're routed before that branch)
   - Update validator docstring + module-level comment to document the new branch

4. **Run validator fresh.** Capture before/after subtype counts including the new PARSER-SUSPECT cohort. Compare to Isaiah-scan extrapolation (expected: 7-15 cases corpus-wide; signals may catch additional cases outside the Isaiah-quoting chapters).

5. **Update §5 R19 canon prose** to document the parser-suspect routing as a third subtype. Match the format used for the same-line / cross-line distinction in the 2100 update.

6. **Update resolver script** (`scripts/resolve_review_required.py`) to handle the new subtype. PARSER-SUSPECT cases should either: (a) be excluded from resolver runs entirely (skip with logged reason), or (b) get a skeptical-mode prompt instructing Sonnet to verify parser correctness before applying R19 logic. **Your judgment on which path** — surface reasoning in the reply.

## Reporting

Reply at `directives/replies/2026-05-16-2203-r19-parser-suspect-prefilter.md`:
- Audit findings + cross-agent agreement (Item 1)
- Implementation commit hash (Items 3-6)
- Before/after subtype counts (Item 4)
- Canon prose excerpt (Item 5)
- Resolver-script handling decision + reasoning (Item 6)
- Any cases routed to PARSER-SUSPECT that the audit-agents flagged as borderline — these are candidates for follow-up review

## Audit triggers

**§7.3 trigger #1 (new named sub-category) + trigger #2 (closed-list-based — the structural-signal set).** ≥2 parallel adversarial agents BEFORE implementation per CLAUDE.md.

The new `parser-suspect` subtype itself is audit-skippable per §7.4 once the signal-set is audit-cleared (it's a structural-signal closed list, not a rule-scope change).
