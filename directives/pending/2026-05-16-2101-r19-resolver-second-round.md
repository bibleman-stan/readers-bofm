# R19 resolver — second round (50-100 cases + agreement scoring)

## Context

The first-round resolver prototype (commit `eb821f6`) showed strong calibration on 25 R19 REVIEW cases: 0 low-confidence, 68% high-confidence, 72% of cases got a non-REVIEW verdict (56% MERGE / 16% SPLIT). Reply at `directives/replies/2026-05-16-1700-resolve-review-required-prototype.md`.

Two things are needed before any auto-apply gate is considered:

1. **Calibration generalization** — does the 68% high-confidence rate hold on a larger, more diverse sample? 25 cases is too small to set a confidence threshold for downstream gating.
2. **Resolver self-consistency** — when the same case is run through Sonnet multiple times, do the verdicts agree? Disagreement across runs is real signal: the cases where the resolver is internally inconsistent are likely the genuinely-ambiguous ones, regardless of any single run's stated confidence.

This directive runs the second-round prototype under the new SAME-LINE / CROSS-LINE framing landed by the prior directive (`2026-05-16-2100-r19-output-restructure.md`). Still read-only diagnostic — no auto-apply, no v2-mine modifications.

## Items

1. **Confirm prior directive landed.** If `directives/pending/2026-05-16-2100-r19-output-restructure.md` has not been processed (no commit, file still in pending/), STOP. This directive depends on the SAME-LINE / CROSS-LINE distinction being live in the validator output.

2. **Sample 50-100 R19 REVIEW cases**, stratified by:
   - **SAME-LINE vs CROSS-LINE subtype** (the new distinction) — aim for proportional stratification matching the validator's actual subtype distribution from the prior directive's before/after counts. Don't over-sample either subtype; the goal is representative calibration data, not balanced classification training.
   - **head_lemma** (same as first round: include high-volume `thing`, `word`, `time`, plus medium and low-volume lemmas for diversity)
   - **Optional**: book-position diversity (don't sample only from Alma; spread across 1 Nephi → Moroni for genre / discourse-mode variety)

3. **Agreement scoring: run each case through Sonnet 3 times.** Same prompt, same context (per the first-round directive's context-assembly), three independent runs. Capture all 3 verdicts + all 3 confidence ratings + brief reasoning per run.

4. **Output: agreement-aware report** at `directives/replies/2026-05-16-2101-r19-resolver-second-round.md`. Columns:
   - Verse reference
   - Original validator verdict (including new SAME-LINE / CROSS-LINE subtype)
   - Run 1 verdict + confidence
   - Run 2 verdict + confidence
   - Run 3 verdict + confidence
   - **Agreement classification**: `unanimous` (all 3 same verdict) / `majority` (2 same, 1 different) / `split` (all 3 different — likely rare given 3 verdict options, but flag if it happens)
   - Notes column for any case where the reasoning across runs revealed something interesting (e.g., one run cited Exclusion 13 and another didn't)

5. **Calibration analysis** in the report:
   - **By subtype**: high-confidence rate on SAME-LINE cases vs CROSS-LINE cases. Hypothesis (from first-round structural finding): SAME-LINE may be easier (resolver is verifying an existing merge that's already structurally licensed) and CROSS-LINE may be harder. If this hypothesis holds, that's load-bearing for differential auto-apply thresholds.
   - **By agreement**: unanimous-high-confidence cases are the strongest auto-apply candidates; agreement-disagreement-confidence-disagreement cases are the genuine-REVIEW cohort even if any single run claimed high confidence.
   - **Calibration recommendation**: what confidence threshold + agreement gate would enable safe auto-apply? Don't enable it yet; just surface the data + recommendation.

6. **Surface patterns**: anything the larger sample reveals that the 25-case first round couldn't show. Examples to watch for: lemma-level patterns at finer resolution; book-position effects; SAME-LINE / CROSS-LINE differential behavior; any systematic resolver biases.

## Reporting

Full report per Item 4 + analysis per Items 5 + 6. Sized appropriately — first-round report was ~600 lines for 25 cases; second-round will scale roughly linearly with case count.

Per-item completion status (completed with commit hash / blocked / proposed-for-Stan-review).

## Audit triggers

Read-only diagnostic. No v2-mine modifications. No rule changes. No closed-list additions. No validator infrastructure changes (the SAME-LINE / CROSS-LINE distinction is landed by the prior directive; this directive only consumes it).

**Audit-skippable per §7.4** (infrastructure prototype iteration; no rule scope change; output is diagnostic only).

Same conditional as the first-round directive: if/when this work moves to auto-apply mode in a later iteration, that's a different conversation that may trip §7.3 trigger #10 (discipline-shifting addition that shapes how the apparatus is operated).

## Cost note

3 Sonnet runs × 50-100 cases = 150-300 Sonnet calls. Per `feedback_model_selection_frugality`, this is the right tier for the work (structured judgment within defined rules, not novel-rule-design). The agreement-scoring use case justifies the multiplier — it's not redundant, it's measuring resolver self-consistency. Surface the actual cost in the reply.
