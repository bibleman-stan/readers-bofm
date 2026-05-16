# Isaiah-quotation UD parser-error scan

## Context

The first-round R19 resolver report (commit `eb821f6`, reply at `directives/replies/2026-05-16-1700-resolve-review-required-prototype.md`) flagged 2 Nephi 24:4 as a probable UD parser error: poetry parallel-clause mis-tagged as `acl:relcl`. The likely cause is the parser misanalyzing Hebrew-style parallelism (which fronts grammatically-similar clauses without a relative pronoun) as English-style relative-clause structure.

If this misanalysis recurs systematically in Isaiah-quoting BoFM chapters, it represents an upstream parse-data quality issue affecting any validator that consumes `acl:relcl` (R19 most directly; possibly others). It's separate from the resolver-iteration workstream — that workstream addresses the validator's REVIEW-output framing; this workstream addresses the validator's INPUT data quality.

This directive bounds the scope of the parser-error issue before any intervention is decided. Diagnostic scan only; no fixes, no overrides.

## Items

1. **Scope the Isaiah-quoting chapters.** BoFM's primary Isaiah quotations:
   - **2 Nephi 12-24** (= Isaiah 2-14, with some intervening discourse)
   - **3 Nephi 22-24** (= Isaiah 54 + parts of Malachi 3-4; verify scope)
   - **Mosiah 14** (= Isaiah 53)
   - **Plus shorter Isaiah quotations scattered through 1 Nephi 20-22, 2 Nephi 7-8, 2 Nephi 27, and possibly others** — surface the full list in the report

   For each chapter in scope: extract every `acl:relcl` deprel from the UD parse output.

2. **Classify each `acl:relcl` case** in the scanned chapters:
   - **probable parser error** — Hebrew-style parallelism mis-tagged (no actual relative pronoun in the English text; parallel structure between two clauses; the second clause is independently complete rather than modifying a head)
   - **genuine relative clause** — actual relative pronoun present (*who*, *which*, *that* in restrictive use); second clause modifies a head noun
   - **ambiguous** — surface-features could go either way; document the specific ambiguity

3. **Report counts + full list of probable-error cases.** Per chapter: total `acl:relcl` count; probable-error count; genuine count; ambiguous count. Full per-verse list of probable-error cases with:
   - Verse reference
   - The English text fragment
   - The parse fragment showing the mis-tagged deprel
   - One-sentence rationale for the "probable error" classification (e.g., "no relative pronoun; second clause is grammatically independent; cf. Hebrew parallelism pattern")

4. **Don't fix anything.** Read-only diagnostic. No parser re-runs, no manual overrides, no validator exclusions. Stan needs to see the scope before deciding intervention shape.

5. **Propose intervention shapes** in the report (for Stan-decision):
   - **Option A**: per-chapter override list — maintain a small JSON of `(book, chapter, verse, token_id) → corrected deprel` overrides; validators consult before consuming
   - **Option B**: parser re-run with different model/config — investigate whether Stanza's Hebrew-trained UD parser or a different model handles these cases better
   - **Option C**: validator-level exclusion — R19 (and any other affected validator) skips Isaiah-quoting chapters entirely; rely on editorial review for those chapters
   - **Option D**: targeted prompt for the resolver itself — when the resolver sees an Isaiah-quoting chapter, instruct it to treat `acl:relcl` skeptically
   - **Option E**: something else surfaced by the scan
   - Don't recommend yet; surface the options + the data; let Stan judge

## Reporting

Full diagnostic report at `directives/replies/2026-05-16-2102-isaiah-quotation-parser-scan.md`.

Include scope (which chapters), method (how `acl:relcl` was extracted), the classification table, the full probable-error list, and the proposed intervention-shape options.

Estimated time: a few hours of scanning; size depends on `acl:relcl` density in Isaiah-quoting chapters (expected: dozens to low-hundreds of cases across the scoped chapters; probably 30-60% probable-error rate in the Isaiah-quoting subset, but that's a hypothesis the data will confirm or refute).

## Audit triggers

Diagnostic scan; no rule change; no validator code change; no parser change. **Audit-skippable per §7.4** (read-only diagnostic; output is information for Stan-decision).

If/when an intervention is selected (Items 5 options), that's a separate directive with its own audit trigger assessment.

## Parallelism note

This directive runs independently of the resolver-iteration directives (`2026-05-16-2100-r19-output-restructure.md` and `2026-05-16-2101-r19-resolver-second-round.md`). It can be processed in any order relative to those, including in parallel if BoFM-Claude judges that appropriate. Trigger order is Stan's call.
