# Pending decisions from recent BoFM work

## Context

BoFM completed substantial readiness-arc work: Group C canon-prose updates (0 DRIFT across 28 rules); retraction-log JSONL research; alignment-script bug fixes; alignment-script protocol updates + scholarship/ directory + 2 navigability READMEs (commit `cdfb096`). Several items now need Stan-decision or surface-for-Stan review.

## Items

1. **Retraction-log inline surface.** The 11-entry draft from your JSONL research is currently uncommitted at repo root. Surface each entry inline in chat with: (a) proposed Factor classification (A/B/C/structural); (b) date; (c) commit hash if available; (d) what was retracted; (e) what surfaced it. Particularly highlight the Stab-commata and doctrinal-weight entries where source attribution was corrected from "Stan correction" to hostile-audit caught — Stan needs to verify those re-attributions per entry. Don't commit; surface for Stan to either approve, edit, or call out specific corrections.

2. **R17 topic-PP / experience-of-PP triggers.** Stan recommends LEAVE canon describe-as-is. Don't build validator triggers unless you can name specific BoFM verses (from corpus scans) where the missing triggers would catch real merges currently being missed. If you have candidates, surface 3+ verses with reasoning; otherwise confirm hold and document the gap as describe-only in canon.

3. **JSON cleanup proposal** (you asked: "Want me to proceed with the deletes or investigate geo_index first?"). Stan answer: investigate `geo_index.json` consumers first; if confirmed orphan, delete both `contextual_glosses_2nephi.json` and `geo_index.json`. If `geo_index.json` has any reference (even commented-out), surface findings before deletion.

4. **Audio-file commit discipline.** You flagged twice this session that audio process pre-stages files between `git status --short` and commit, sweeping audio into canon commits. Stan needs a structural recommendation, not a one-line fix. Propose 2-3 options with tradeoffs: (a) add audio paths to `.gitignore` so they can't sweep into canon commits; (b) separate working tree for audio vs canon; (c) explicit pre-commit hook that checks for non-canon-related staged files; (d) staging-discipline change (always `git add <specific-path>`, never `-A`). Surface options + your read of which is best for Stan to decide.

5. **scripts/README survey.** If not yet done in commit `cdfb096`, survey the 36 scripts in `scripts/`. Categorize: active pipeline tools (regular use) vs archival/diagnostic/one-off scripts. Propose categorization for Stan review BEFORE writing `scripts/README.md`. If already done in cdfb096, surface what was done; if partial, complete it.

## Reporting

Per item: completed (commit hash) / proposed-for-Stan-review / blocked (reason).

For #1: surface entries inline; no commit. For #4: surface options + recommendation. For #5: propose categorization before writing.

## Audit triggers

None of these items trip §7.3 mandatory-audit triggers (no new rules, no scope claims, no closed-list extensions). Audit-skippable per §7.4 for any §5 canon edits that result.
