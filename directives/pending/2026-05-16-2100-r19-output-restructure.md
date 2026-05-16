# R19 validator-output restructure — SAME-LINE vs CROSS-LINE distinction

## Context

The resolver prototype (commit `eb821f6`) surfaced a structural finding: ~60% of sampled R19 REVIEW-REQUIRED cases are already same-line in `v2-mine`. The validator's current REVIEW-REQUIRED output is collapsing two structurally-different editorial questions into one bucket:

- **REVIEW-SAME-LINE** — "verify this existing merge is correct" (the head is already on the same line as the relative clause in v2-mine; validator is asking whether the merge holds)
- **REVIEW-CROSS-LINE** — "should we close this split?" (the head and relative clause are on different lines in v2-mine; validator is asking whether to merge)

These have different risk profiles, different editorial-attention requirements, and different safety profiles for any future auto-apply gate. Collapsing them in the output schema makes the resolver's verdicts harder to interpret and Stan's spot-audits less efficient.

This directive restructures the R19 validator's output to surface the distinction BEFORE the next resolver round consumes the data — otherwise the second round bakes the muddled framing into 50-100 cases of calibration data.

## Items

1. **Update the R19 validator** to compute SAME-LINE vs CROSS-LINE status for each REVIEW-REQUIRED case at output time. The check is mechanical: compare the head token's line-index against the relative-clause-root token's line-index in `v2-mine`; same line = REVIEW-SAME-LINE, different lines = REVIEW-CROSS-LINE.

2. **Update the output schema** to carry the distinction. Whatever the existing JSON / Markdown / CSV shape is, add a field (e.g., `review_subtype: same-line | cross-line`) or split the verdict tag itself (`REVIEW-REQUIRED` → `REVIEW-SAME-LINE` | `REVIEW-CROSS-LINE`). Choose the shape that's least disruptive to downstream consumers (the resolver script, any baseline-check, any reporting). Surface the choice in the reply if there's a non-obvious tradeoff.

3. **Run the validator fresh** and capture before/after counts: how many of the current 586 R19 REVIEW backlog cases fall into each subtype. Distribution should roughly match the resolver prototype's ~60% same-line / ~40% cross-line, but the exact numbers are useful calibration data.

4. **Update §5 R19 canon prose** to document the SAME-LINE vs CROSS-LINE distinction in the validator's output behavior. This is a labeling refinement (no rule scope change), but the canon should describe what the validator actually outputs.

5. **Edge cases**: if any REVIEW-REQUIRED case doesn't fit cleanly into either subtype (e.g., multi-line relative clause spanning the head's line + adjacent lines), document it. Don't shoehorn — surface the edge case so we can decide whether it deserves a third subtype or some other framing.

## Reporting

Per item: completed (commit hash) / proposed-for-Stan-review / blocked (reason).

Specifically: the before/after subtype distribution numbers, the chosen output-schema shape (and why), any edge cases surfaced under Item 5.

## Audit triggers

This is a labeling refinement on existing REVIEW cases, not a rule-scope change. No new closed list, no new rule, no new trigger; the validator continues to flag the same set of cases — only the output label is refined. **Audit-skippable per §7.4** (the rule's scope is unchanged; this is output-schema clarification matching what the resolver already observed in v2-mine).

If, while implementing, you discover the SAME-LINE/CROSS-LINE distinction implies a hidden rule-scope question (e.g., "should the validator stop firing on already-same-line cases since they're already merged?"), STOP and surface that as a proposed-for-Stan-review item rather than acting on it. That would be a different conversation.

## Why this lands first

The second-round directive (50-100 cases, agreement scoring) depends on the new output framing being in place. Running 50-100 cases under the old muddled framing wastes Sonnet calls and produces calibration data we'd want to redo.

Sequence: this directive (restructure) → Stan reviews + triggers next directive → second round runs under correct framing.
