# Parse-coverage gap audit — 2 Nephi 7-8 + Mosiah 14

## Context

The 2102 Isaiah parser-scan reply (`directives/replies/2026-05-16-2102-isaiah-quotation-parser-scan.md`) surfaced an implausible finding: **2 Nephi 7-8 (= Isaiah 50-51) and Mosiah 14 (= Isaiah 53) returned 0 `acl:relcl` tokens.**

This is implausible for chapters with extensive restrictive-relative constructions in MT and LXX traditions — "he that walketh in darkness," "him that justifieth me," "he was despised and rejected of men," "a man of sorrows" and similar. Either the parser is missing these constructions, or the English KJV-style rendering in v2-mine uses different surface syntax than expected.

BoFM-Claude (2102 reply) proposed two possible causes:
1. **Pattern A**: the parser produced parses where these relatives use a different deprel (e.g., `acl` without `:relcl`, or `nsubj`-based fronting)
2. **Pattern B**: the parses themselves have arc gaps (the parser failed to produce any arc for the construction)

A third possibility worth checking:
3. **Pattern C**: rendering anomaly — the English text in v2-mine doesn't actually contain the relatives expected from MT/LXX (translation choice; KJV-style English uses different surface syntax)

Independent of the R19 work, this is a parse-quality issue worth bounding. If it generalizes, it affects every validator that consumes `acl:relcl` (R19 most directly; possibly others). This directive scopes the issue WITHOUT proposing intervention — Stan needs to see the data before deciding intervention shape.

## Items

1. **Audit the UD parse for 2 Nephi 7-8 + Mosiah 14.** For each chapter:
   - Confirm the parse exists in `data/parses/llm-direct/` (or wherever R19 sources from)
   - Extract ALL deprel arcs (not just `acl:relcl`) for the chapter
   - Identify candidate restrictive-relative constructions in the English v2-mine text — manual scan + LLM-assisted enumeration (target shapes: "he that…", "him that…", "those who…", "a man of…", "the one who…", "they that…")
   - For each candidate: check what deprel the parser actually assigned to the construction

2. **Classify per-candidate by Pattern A / B / C:**
   - **Pattern A (misassigned deprel)**: parser tagged the construction with `acl` (no `:relcl`), `nsubj`, `nmod`, or another deprel. Surface count + 3-5 examples with parse fragments.
   - **Pattern B (arc gap)**: parser failed to produce any arc for the construction (head exists but no acl/acl:relcl/nmod arc points to it). Surface count + 3-5 examples with parse fragments.
   - **Pattern C (rendering anomaly)**: the English text in v2-mine doesn't actually contain the relative — the KJV-style rendering uses different surface syntax (e.g., direct nominalization, participial phrase, prepositional rendering). Surface count + 3-5 examples with verse references and what the KJV-style rendering looks like.

3. **Scope estimate beyond 2 Ne 7-8 + Mos 14**: sample-check ONE chapter from each Isaiah-quoting cluster that DID return `acl:relcl` cases (e.g., 1 Ne 22 = Isaiah 49, 2 Ne 17 = Isaiah 7, 3 Ne 22 = Isaiah 54). Does the same gap pattern appear there at lower rates, or is it specific to the two flagged chapters?

4. **Don't fix anything.** Diagnostic only. No parser re-runs, no manual overrides, no validator changes.

5. **Propose intervention shapes** (for Stan-decision; do NOT recommend or rank):
   - **Option α**: re-parse the flagged chapters with a different model/config
   - **Option β**: manual override list for missing-relative cases
   - **Option γ**: validator-level acceptance of `acl` (without `:relcl`) as R19-eligible input when surrounding context matches expected restrictive-relative shape
   - **Option δ**: rendering review — if Pattern C dominates, the gap may not be a parser issue at all; the v2-mine rendering's syntactic shape may need editorial review
   - **Option ε**: something else surfaced by the audit data

   Surface the data; let Stan judge.

## Reporting

Reply at `directives/replies/2026-05-16-2206-r19-parse-coverage-gap-audit.md`:
- Per-chapter candidate count
- Pattern A / B / C breakdown per chapter with examples
- Scope estimate beyond the two flagged chapters
- Proposed intervention shapes (Options α-ε) with the data each option would draw on
- Don't recommend an intervention — surface options + data + reasoning per option

## Audit triggers

Diagnostic scan. No rule change. No validator change. No parser change. Audit-skippable per §7.4.

If/when an intervention is selected (Options α-ε), that's a separate directive with its own audit trigger assessment.

## Parallelism note

Runs independently of 2201 (spot-audit prep) and 2203 (parser-suspect pre-filter). 2203 in particular addresses the OTHER class of parse issue (misclassification within `acl:relcl` cases); this directive addresses the gap class (cases that should have been `acl:relcl` but weren't tagged). Different problems, parallel resolutions.
