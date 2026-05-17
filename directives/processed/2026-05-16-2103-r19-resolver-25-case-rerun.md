# R19 resolver — re-run the first-round 25-case bundle for agreement scoring

## Context

The first-round resolver prototype (commit `eb821f6`) dispatched ONE Sonnet agent against 25 R19 REVIEW cases. The report at `directives/replies/2026-05-16-1700-resolve-review-required-prototype.md` captured one verdict + one confidence per case.

This directive is a **cheap robustness check**: re-run the SAME 25 cases through Sonnet 2 more times (independent runs) and report whether the verdicts agree across all 3 runs. This is distinct from the second-round directive's agreement-scoring (which runs NEW cases 3× each); here we're testing resolver self-consistency on data we already have one verdict for.

The value is calibration insight at low cost. If the 25 cases show high agreement across re-runs, it strengthens confidence that the first-round high-confidence rate is real. If agreement is lower than the stated confidence ratings suggest, it surfaces a calibration concern before we scale to 50-100 cases.

## Why this runs independently

- Doesn't depend on the SAME-LINE / CROSS-LINE restructure (`2026-05-16-2100-r19-output-restructure.md`) — the 25 cases are already sampled; subtype can be retroactively annotated from the new labels once they land
- Doesn't depend on the second-round directive (`2026-05-16-2101-r19-resolver-second-round.md`) — different sample, different question
- Can be processed immediately after the output-restructure directive (or in parallel) without sequencing concerns

## Items

1. **Reuse the existing 25-case bundle** that was dispatched in commit `eb821f6`. Don't re-sample — use the exact same case identifiers (verse reference + head_lemma + relative-clause-root token) so re-run verdicts pair cleanly with first-round verdicts.

2. **Re-dispatch 2 additional Sonnet runs** against the same 25-case bundle with the same prompt + same context-assembly used in the first round. Independent runs (separate API calls; no cross-run context).

3. **Capture per-case**: run 2 verdict + confidence + brief reasoning; run 3 verdict + confidence + brief reasoning.

4. **Generate agreement report** at `directives/replies/2026-05-16-2103-r19-resolver-25-case-rerun.md`. Columns:
   - Verse reference
   - Original validator verdict (with SAME-LINE / CROSS-LINE subtype retroactively annotated if the prior directive has landed; otherwise omit and document)
   - Run 1 verdict + confidence (from first-round report — copy in, don't re-run)
   - Run 2 verdict + confidence (new)
   - Run 3 verdict + confidence (new)
   - **Agreement classification**: `unanimous` / `majority-2-1` / `split-1-1-1`
   - **Confidence-agreement classification**: do confidence ratings agree across the 3 runs? (e.g., 3× high, or high/medium/high — surface the pattern)
   - Notes: any case where the reasoning across runs cited different rule elements (e.g., one run invoked Exclusion 13, another didn't) — that's signal about which cases are genuinely structurally ambiguous

5. **Analysis** in the report:
   - **Top-line agreement rate**: what % of cases are unanimous across 3 runs?
   - **Confidence-vs-agreement correlation**: do the cases the resolver labeled high-confidence in run 1 actually have unanimous-agreement across all 3 runs? Or does some "high confidence" mask underlying instability? This is the key calibration question.
   - **Verdict-flip cases**: for any case where verdict flipped across runs (e.g., MERGE → SPLIT → MERGE), surface the case with full reasoning from each run. These are the most informative cases for understanding resolver failure modes.
   - **Implications for second-round directive (2101)**: does this data change the recommended sample-size or stratification for the 50-100 second round?

## Reporting

Full report per Item 4 + analysis per Item 5. Smaller than first-round report since we're not re-computing verdicts from scratch — just adding 2 runs × 25 cases = 50 new Sonnet calls + the agreement analysis.

Per-item completion status (completed with commit hash / blocked / proposed-for-Stan-review).

## Audit triggers

Read-only diagnostic. No v2-mine modifications. No rule changes. No validator changes. No new sampling.

**Audit-skippable per §7.4** (infrastructure prototype iteration on existing data; no rule scope change; output is calibration-data only).

## Cost note

50 additional Sonnet calls (2 runs × 25 cases). Small. Per `feedback_model_selection_frugality` this is the right tier and the right use of the multiplier — measuring self-consistency on cases we already have one verdict for is a cheap and high-leverage diagnostic.
