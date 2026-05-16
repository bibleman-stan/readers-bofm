# Resolve REVIEW-REQUIRED prototype (R19 starter)

## Context

Vault-Claude and Stan identified that the manual-editorial-review bottleneck is the slowest part of the workflow, and that many REVIEW-REQUIRED cases are "Claude could have decided this given full context" — the validator's deterministic logic punts where a second-pass LLM with broader context would resolve cleanly.

This directive starts a contained prototype: build `scripts/resolve_review_required.py` and run it against ~20-30 R19 REVIEW cases. Don't auto-apply yet — first round is "show Stan what the resolver would have done." Stan spot-audits; we iterate on calibration; we decide later whether to enable auto-apply or scale to other rules.

Architectural framing: this extends BoFM's existing Stanza+LLM ensemble pattern (already established in the parsing pipeline) to validator-output resolution. Not new architecture; new application of an established pattern.

Why R19 first: R19 REVIEW backlog is the largest in BoFM (586 cases — `thing` 339, `word` 191, `time` 56, plus smaller buckets). Highest leverage for testing the resolver's calibration; provides diverse case shapes for sampling.

## Items

1. **Build the prototype.** `scripts/resolve_review_required.py`:
   - Reads R19 validator's REVIEW-REQUIRED output from the most recent run (or runs the validator fresh)
   - For each REVIEW finding, assembles context for the resolver: (a) the full §5 R19 canon entry — statement + closed lists + Examples + Exclusions + Scope; (b) any `private/01-method/scholarship/r19.md` content if it exists; (c) parse fragment for the candidate span + 2 adjacent verses before and 2 after
   - Sends to Sonnet (per `feedback_model_selection_frugality` — Sonnet for per-instance judgment within defined rules; this is structured work with a clear rubric, not novel-rule-design)
   - Asks Sonnet: "Given R19's full criteria, can you resolve this case (STRONG-MERGE / STRONG-SPLIT / GENUINE-REVIEW-REQUIRED)? Include reasoning + your confidence (high/medium/low)."
   - Captures verdict + reasoning + confidence per case

2. **Scope: 20-30 R19 REVIEW cases.** Sample diversely — include high-volume lemmas (`thing`, `word`, `time`) plus medium-volume + low-volume. Don't cherry-pick easy cases; aim for representative distribution.

3. **Output: human-auditable report.** Markdown table at `directives/replies/2026-05-16-1700-resolve-review-required-prototype.md`:
   - Columns: verse reference; original validator verdict (REVIEW-REQUIRED with reason); Sonnet's proposed verdict; Sonnet's reasoning (one short sentence); Sonnet's confidence rating
   - Format such that Stan can scan and spot-audit quickly

4. **DO NOT auto-apply.** This round is read-only diagnostic. No commits to `v2-mine`. No changes to validator output state. The point is to see what the resolver WOULD have done; Stan audits before we commit to enabling auto-resolution.

5. **Surface calibration concerns.** As you build the resolver, you'll encounter design choices (how much context to include; how to phrase the prompt to Sonnet; what counts as "high confidence"). Surface those choices + your reasoning in the reply. If you find R19 has specific edge cases where the resolver seems systematically biased, name them.

## Reporting

Reply at `directives/replies/2026-05-16-1700-resolve-review-required-prototype.md`:
- The 5-column per-case table per Item 3
- Design-choice surfacing per Item 5
- Per-rule observations: any pattern in where Sonnet succeeds vs struggles?
- Calibration recommendation: if the prototype works, what confidence threshold would enable auto-apply with low false-positive risk?

Stan reviews the report, spot-audits, identifies blind-spot patterns. Next iteration based on findings; possible next steps: extend to other high-volume rules; enable auto-apply on high-confidence cases; refine the LLM prompt; abandon if the resolver's quality doesn't justify the architecture.

## Audit triggers

None for this round. Tooling/scripts work; not canon-touching, not validator-modifying. Audit-skippable per §7.4 (infrastructure prototype; no rule scope change; output is diagnostic only).

If/when the resolver moves to auto-apply mode in a later iteration, that's a different conversation that may trip §7.3 trigger #10 (discipline-shifting addition that shapes how the apparatus is operated).
