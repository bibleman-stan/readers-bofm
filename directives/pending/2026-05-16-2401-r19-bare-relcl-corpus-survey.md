# R19 bare-`relcl` corpus-wide survey — Option ε from 2206

## Context

The 2206 parse-coverage gap audit (`directives/replies/2026-05-16-2206-r19-parse-coverage-gap-audit.md`) surfaced **340 bare `relcl` tokens corpus-wide** (8% of all relative-clause arcs). Heavy concentration in 2 Nephi (21%), Helaman (25%), Mosiah (14%); 0% in 9 books. Pattern A (labeling inconsistency `relcl` vs `acl:relcl`) dominates.

Before deciding whether to extend R19 to accept bare `relcl` as input (Option γ — which would trip §7.3 trigger #1+#2 per 2203 precedent), need corpus-wide evidence on what proportion of the 340 cases are legitimate restrictive relatives that would benefit from R19 routing.

This directive runs that survey. **Diagnostic only; no validator extension yet.**

## Items

1. **Extract all 340 bare `relcl` tokens** from `data/parses/llm-direct/`. Per token capture:
   - Verse reference (book + chapter + verse)
   - Head token (form + lemma + UPOS)
   - Rel-root token (form + lemma + UPOS)
   - Clause-context (the verse text fragment containing the head + rel-root + 2-3 surrounding tokens)
   - The parse fragment showing the bare `relcl` deprel

2. **Dispatch single Sonnet pass** classifying each case as one of:
   - **legitimate-relative-mis-labeled**: genuine restrictive relative clause; should have been `acl:relcl`; would be correctly handled by R19's routing if accepted
   - **non-relative-construction**: parser mis-label on something that is NOT a relative clause (e.g., paratactic conjunction, appositive, ccomp); should NOT enter R19 routing
   - **ambiguous**: surface-features could go either way

   Per `feedback_model_selection_frugality` Sonnet is right for structured per-instance classification. 340 calls, ~5-10 min wall-time.

3. **Report aggregate + per-book breakdown:**
   - Total counts per classification (legitimate / non-relative / ambiguous)
   - Per-book breakdown — does 2 Nephi's high bare-`relcl` rate skew toward legitimate or non-relative?
   - Head-UPOS breakdown of the legitimate-relative cases (PROPN / PRON / DET / NOUN / other) — informs what R19's routing would do with them if accepted

4. **Surface intervention recommendation per directive:**
   - If **>85% legitimate**: Option γ (validator extension to accept `acl:relcl OR relcl`) becomes viable; would still need its own §7.3 audit per 2203 precedent, but the corpus evidence justifies the audit overhead
   - If **<50% legitimate**: Option β (per-case override for the legitimate subset) is safer; ~170-case JSON, larger than the 8-case Isaiah override but still manageable
   - If **50-85% legitimate**: Stan-decision; the cost-benefit of validator extension vs per-case override depends on Stan's read

5. **Diagnostic only.** No validator changes. No parser re-runs. No JSON override built (that's a downstream directive if Option β path).

## Reporting

Reply at `directives/replies/2026-05-16-2401-r19-bare-relcl-corpus-survey.md`:

- Aggregate classification distribution
- Per-book breakdown table
- Head-UPOS breakdown of legitimate-relative cohort
- 10-15 representative examples per classification (especially "non-relative-construction" cases — those are the audit's main concern about Option γ)
- Intervention recommendation per Item 4

## Audit triggers

Diagnostic scan. No rule change, no validator change, no parser change. **Audit-skippable per §7.4.**

If/when Option γ is pursued, that's a separate §7.3 trigger #1+#2 audit per 2203 precedent.

## Cost note

340 Sonnet calls; modest. Per `feedback_model_selection_frugality` Sonnet-tier appropriate for structured classification within defined rubric.
