# Reply: 2026-05-16-1500-pending-decisions

Processed 2026-05-16 against the BoFM directive of the same name. Most items had already been executed in-session during the readiness-arc follow-up batch (commits `fdf2c78` → `cdfb096`) — this reply records per-item status and surfaces the Item 4 audio-discipline options for Stan's structural decision.

## Per-item status

### Item 1 — Retraction-log inline surface

**Status: completed in-session, NO commit (per directive instruction).**

Surfaced inline in chat: all 11 entries with proposed Factor classifications, dates, commit hashes, and surfacing-source attribution. Two date corrections + two surfacing-source corrections were specifically flagged for Stan-verification:

- **J6**: date `2026-04-??` → **2026-05-10** (proposed + rejected same day, no commit; JSONL evidence at session `5e934fd5` lines 59694-59708)
- **Stab-commata**: date `2026-04-??` → **2026-04-23** (commit `f883eab`); surfacing source corrected from "Stan correction" → **hostile audit**
- **Doctrinal-weight**: date `2026-04-25` → **2026-04-23** (commit `1ea0d68`); surfacing source corrected from "Stan correction" → **hostile audit**
- **EP-6**: date `2026-04-??` → **2026-04-23** (commit `13f8859`); same hostile-audit session

Pattern surfaced: **three of four hostile-audit-caught entries clustered on 2026-04-23** — stab-commata (05:18) + doctrinal-weight (18:32) + EP-6 (18:53) + 1 Ne 19:5 reclass (`d8fd16f` 18:56) = four-catch session culminating in audit-discipline systematization (`cc555b8` 19:36 same evening). Suggested Stan-call: group as one "2026-04-23 hostile-audit session" entry, or keep separate per-retraction.

[`retraction-log.md`](../../retraction-log.md) carries the full draft text; untracked, awaiting Stan-verification before commit.

### Item 2 — R17 topic-PP / experience-of-PP triggers

**Status: confirmed HOLD; gap documented describe-only in canon (commit `42ee139`).**

No corpus scan on hand at this point. Per Stan-directive *"don't build validator triggers unless you can name specific BoFM verses ..."*, holding. The canon §5 R17 entry was updated in commit `42ee139` (Group C canon-prose updates) to explicitly document topic-PP and experience-of-PP as canon-prose intent — with the `_intent` suffix in UD signatures and a "NOT yet implemented in validator" annotation. Current canon prose:

> Speech-class verbs (canon-prose intent) require their obligatory topic-PP complement (*of*/*concerning*/*unto*/*against*) on the same line. Experience verbs (`repent`, `partake`, `forgive`) require their obligatory *of*-PP complement on the same line. The validator does NOT currently fire on these obl branches — topic-PP and experience-of-PP merges remain Category B editorial enforcement, awaiting future codification.

Should a future corpus scan surface candidate merges, the trigger codification would land via §7.3 mandatory-audit per protocol.

### Item 3 — JSON cleanup

**Status: completed (commit `82624fe`).**

Investigation confirmed `geo_index.json` had zero consumers (build script existed but no fetch/load reference in `build_book.py`, `index.html`, or validators). Stan subsequently authorized broader cleanup in chat: *"delete the contextual_glosses and geo_index; those were ideas we have abandoned for this project."* Implemented:

- Deleted: `data/contextual_glosses.json` (2013 lines), `data/contextual_glosses_2nephi.json` (385 lines), `data/geo_index.json` (2471 lines), `scripts/build_geo_index.py` (163 lines)
- Stripped dead code: `build_book.py` (-274 lines: 5 gloss functions + 3 call sites + 1 dead branch in `apply_phrase_highlights`); `index.html` (-141 lines: `.gloss` CSS + `.gloss-popover` JS handler)
- 7 books/*.html regenerated without gloss markup
- `.gitignore` cleaned; `sw.js` cache bumped v245 → v246

Net diff: **-5442 lines.**

### Item 4 — Audio-file commit discipline

**Status: PROPOSED-FOR-STAN-REVIEW. Three options + recommendation below.**

Diagnosis: the failure mode is that staged files appear in the working tree between my `git status --short` check and my subsequent `git commit`. Path-scope `git add <specific-paths>` is necessary but insufficient — files staged by parallel processes (Stan's audio workflow downloading MP3s from Colab/Drive into the working tree) can still slip in if my staged-set check is stale by the time of commit.

Worth noting: I succeeded at this discipline in 4 of 6 commits this session (`fdf2c78`, `cacfac1`, `82624fe`, `cdfb096`) using path-scope add + immediate commit. The two failures (`f3822d3` reset to `3321915`, plus an earlier audio-sweep in `0b9d5e9`) both involved gaps between status-check and commit.

**Option A — Pre-commit hook: staging-scope vs commit-message check**

Add a hook that compares staged paths to commit-message text. If staged files span multiple "categories" without the message mentioning each, fail with a clear message.

Categories: `canon` (private/01-method/colometry-canon.md), `audio` (audio/), `validator` (validators/), `script` (scripts/), `web` (build_book.py, index.html, sw.js, books/), `data` (data/, excluding text-files/), `doc` (handoffs/, README.md, *.md at root).

- **Pros**: Mechanical; impossible to bypass without `--no-verify`. Catches the failure regardless of who/what staged the files. Self-documenting hook output explains the violation.
- **Cons**: Heuristic categorization could false-positive on legitimate cross-cutting commits (feature work spanning canon + validator + scripts). Would need a `category-skip:` escape clause in commit messages.

**Option B — Claude discipline: mandatory `git diff --cached --stat` immediately before commit**

Update CLAUDE.md to require: between `git add <paths>` and `git commit`, run `git diff --cached --stat` and verify the staged-file list matches the commit's stated scope. If mismatched, reset and re-stage.

- **Pros**: Zero infrastructure; relies only on Claude discipline; combines with existing `feedback_agent_git_add_discipline`.
- **Cons**: Discipline-only. Claude has already failed this discipline twice in this session (`0b9d5e9`, `f3822d3`). A discipline that has failed under stress isn't a structural fix.

**Option C — Audio process commits its own work immediately**

Update the audio generation workflow (`scripts/generate_audio.py` per CLAUDE.md, or Stan's Colab→local handoff) to commit + push audio files immediately upon arrival in working tree. Audio never accumulates as unstaged/untracked between sessions.

- **Pros**: Source-of-truth fix; eliminates the race entirely; audio commits stay self-describing ("Add Alma 62 Samuel audio") and never mix with canon work.
- **Cons**: Requires modifying the audio workflow (in Stan's hand or in the script). Possible UX friction if Stan prefers to download audio in batches before committing.

**Recommendation: Option A (pre-commit hook) as the structural primary; Option B as documented backup discipline.**

Reasoning:
- Option B alone has demonstrably failed under load — Stan's framing *"structural recommendation, not a one-line fix"* explicitly points away from discipline-only solutions
- Option C is cleanest in principle but requires touching a workflow I can't observe (Stan's audio process). If Stan confirms the audio workflow is `scripts/generate_audio.py`, I can prototype the self-commit extension; otherwise it's a Stan-side change
- Option A is fully under my control to implement, tests the right invariant (committed-scope = stated-scope), and works regardless of cause (Claude error / Stan parallel work / race condition)
- Combine: implement A as backstop; codify B as standing discipline; defer C pending Stan's audio-workflow disclosure

Estimated implementation effort for Option A: ~80 lines of bash (similar shape to existing `validators/hooks/check_canon_extensions.sh`), installed via the existing hooks-install path. Awaiting Stan-decision before building.

### Item 5 — scripts/ survey

**Status: completed (commit `cdfb096`); 4 Stan-questions surfaced in chat; awaiting Stan-confirmation before file moves.**

Surveyed 16 scripts (directive said "36" — actual count is 16). Categorized:

- **Active build pipeline (8):** `build_search_index.py`, `build_stem_index.py`, `build_kjv_diff.py`, `build_parallel_index.py`, `build_parry_index_v2.py`, `build_phrase_index.py`, `enrich_hardy_data.py`, `generate_audio.py`
- **Active utility module (1):** `bom_abbreviations.py` (imported by 3 other scripts)
- **Allusion pipeline — uncertain (3):** `extract_all_allusions.py`, `build_allusion_analysis.py`, `analyze_allusions.py`
- **Likely archive (4):** `colometric_analysis.py`, `audit_complement_integrity_gaps.py`, `senseline_reformat_v8.py`, `split_parry.py`

Four Stan-questions surfaced in chat:
1. `build_allusion_analysis.py` and `analyze_allusions.py` — still in active workflow, or stale?
2. `colometric_analysis.py` — periodic re-run, or one-time research output?
3. `audit_complement_integrity_gaps.py` — archive, or migrate to a future `validators/audits/` class?
4. `senseline_reformat_v8.py` + `split_parry.py` — confirm archive?

`scripts/archive/` directory created (commit `cdfb096`) with stub README per Tanakh-template. No `git mv` operations performed pending Stan-confirmation of the categorization.

## Surfaced concerns

1. **Inaccurate directive count.** The directive cited "36 scripts in `scripts/`" but actual count is 16. Vault-Claude may have been looking at GNT or Tanakh by mistake, or `scripts/` count has changed since the directive was written. Worth verifying.

2. **Hostile-audit-driven retractions need source-attribution discipline.** Items 3-5 of retraction-log Item 1 were originally drafted with "Stan correction" as the surfacing-source default. Git evidence shows all three (stab-commata, doctrinal-weight, EP-6) were hostile-audit-caught. This isn't lying-to-self — they were uncertainty markers when the source was unknown — but the correction matters: it preserves the precedent value (hostile-audit catches accrue toward systematic-audit-discipline codification, which the four-catch session on 2026-04-23 explicitly drove).

3. **Audio commit discipline is the open structural item.** Items 1-3 and 5 are completed or surfaced; only Item 4 (audio-discipline) remains as a pending Stan-decision before any infrastructure work. Recommend treating Item 4 as the highest-priority follow-up since the same failure mode could recur on any future canon-touching commit.

## Next actions Stan-side

- **Item 1**: verify the date + source-attribution corrections; approve or edit `retraction-log.md`; trigger commit when ready
- **Item 4**: choose between A / B / C / combinations; if A, authorize the pre-commit hook implementation
- **Item 5**: answer the 4 categorization questions so script archival can proceed
