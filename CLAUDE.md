# BOM Reader — Claude Code Instructions

A web-based colometric reading edition of the Book of Mormon at **bomreader.com**, designed for ESL readers, children, and newcomers. Each line on the page is an atomic thought unit (ATU); the modern-mode pill toggles archaic→modern in place (`hath`→`has`, `unto`→`to`); optional audio narration per chapter. Reference implementation for the gnt-reader / tanakh-reader siblings (same UX shell, same swap-system, same ATU rhythm; KJV is the unifying English voice across siblings).

---

## Orientation reads

**MANDATORY at every wake (including short pings; compaction-resume runs from scratch):**
1. This CLAUDE.md
2. `private/01-method/colometry-canon.md` — at least §0/§1/§2 (framework pointers) + §3 Quick-Reference + §3.5 Precedence Hierarchy
3. The most recent session folder's `pending.md` if present
4. `git log --oneline -10`

**CONSULT-ON-TRIGGER:**
- `data/syntax-reference/ud-taxonomy.md` §7 — any Layer 1 mechanical-rule work or validator design.
- `validators/README.md` — writing or modifying a validator.
- `../atu-method/docs/apparatus.md` + `../atu-method/docs/architecture.md` — cross-corpus migration work, sibling-reader port, or work where the picture matters more than the phase list. Picture-shaped: what the user sees on bomreader.com / gnt-reader.com / tanakh-reader.com when done.
- `../atu-method/docs/framework.md` — methodology, rule-design, autonomy-boundary. Authoritative cross-corpus body; per-repo canon §0/§1/§2 are pointer-only.
- `../atu-method/docs/change-protocol.md` — any canon revision.
- `../atu-method/docs/glossary.md` — ambiguous term (ATU, M1–M4, J1–J5, N=2 adjudication, etc.).

**Self-report before first substantive response:** one line per mandatory file read; pending-item disposition (each = executing-now / retired-with-rationale / re-deferred-with-concrete-trigger; "awaiting Stan direction" / "until Stan re-surfaces" are drift not defers); red flags. Silent skip = orientation failure.

**Compaction-resume protocol.** Per [`../atu-method/memories/feedback_compaction_resume_protocol.md`](../atu-method/memories/feedback_compaction_resume_protocol.md) (cross-corpus shared discipline): when resuming from a compaction event, the FIRST action after the mandatory orientation reads is to read the last 20-30 user↔assistant back-and-forth turns from the session JSONL verbatim. Report the re-read as part of the orientation self-report. Don't write wrap artifacts / session-notes / full-transcript dumps; surface state inline. `pending.md` only for extended multi-cycle hand-offs.

**Directive-queue protocol.** Per [`../atu-method/memories/feedback_directive_protocol.md`](../atu-method/memories/feedback_directive_protocol.md) (cross-corpus shared discipline): on wake, after mandatory orientation reads, check `directives/pending/` for files in commit-order. Process each in turn: read directive, execute items per their reporting + audit-trigger guidance, write reply at `directives/replies/<same-name>.md`, move processed directive to `directives/processed/<same-name>.md`, commit + push per directive (or per coherent batch). Surface processed work + any new Stan-decisions in chat after the session.

---

## Editorial discipline (highest-violation surface)

### Stan-flagged verse = class-investigation directive

When Stan flags a problem at a specific verse, that's a directive to investigate the rule set, NOT patch the verse. Right shape:

1. Diagnose: what's the underlying class/pattern Stan's intuition is responding to?
2. **Audit yourself FIRST** — walk M1 / M2 / M3 / M4 / J1–J5 / formula-integrity / R-rules / EP-rules / N=2 / N=3+ explicitly against the actual canon. Pay attention to **explicit exclusions** (e.g., M1 §1.5 excludes sequential narrative bonding; R17 SCOPE excludes direct discourse). If the framework's existing answer is "split, this is excluded," that's a real answer — not a gap.
3. Only if step 2 finds a real gap, investigate corpus-wide for the pattern's frequency + variants.
4. **New rules trigger §7.3 mandatory-audit** — ≥2 parallel adversarial agents BEFORE any validator infrastructure. NO scanner / applier / closed-list entry until the rule passes. Building infrastructure first is the "fake rule" failure mode.
5. If audit holds: codify with WHY/HOW WE KNOW/SCOPE per canon §6 defensibility-capture, build the validator with UD signature, apply mechanically corpus-wide.
6. If audit fails or framework already answers: report Stan the actual framework answer; offer Category B per-verse editorial-judgment fallback ONLY if genuinely needed.

**Never offer Option A / Option B menus on rule-derivative cases.** Per `feedback_no_eyeball_offers` + `feedback_no_fake_dilemmas`: when canon resolves it, apply. When canon has a gap, investigate the gap, don't manufacture a menu.

**Audit the audit's editorial-defensible-split exceptions.** When a hostile-audit agent returns a verdict with "Cat B / editorial concern / editorially-defensible-split exception" sub-items, each item's REASONING must itself be canon-checked before being treated as a legitimate carve-out. Audits are intermediate analysis, not canon-authority. Failure mode 2026-05-12 (hit twice in one session): audit α flagged Alma 28:14 for "chiastic structure," Alma 7:8 for "doctrinal weight," 2 Ne 20:6 for "Isaiah quotation register," and Alma 60:30 for "length backstop." Three of the four are exactly the bandwagon failure modes the canon explicitly rejects as forces: chiastic-as-justification = `feedback_rhetoric_bandwagon` rejected Hebrew-parallelism framework; Isaiah-register / source-text colometric tradition = apparatus.md "external editorial overlays are calibration evidence only, never piped into candidate-generation"; length backstop = canon §6 "atomic-thought test is the gate, not line length." I let all three pass through as carve-outs because I treated α's editorial framing as authoritative. Stan's correction (verbatim): *"NO NO NO NO!!!!!"*. **Discipline going forward:** when an audit returns editorial-defensible-split exceptions, run each through the same canon-checking the Stan-flagged-verse Step 2 prescribes — §1 (no editorial overlay has force), apparatus.md "what the apparatus is NOT" (external overlays = calibration only), §6 (length is not a gate), and the bandwagon/punctuation memories. Only carve-outs grounded in NAMED canon rules survive. (Codified as `feedback_audit_outputs_need_canon_check`.)

### Anchor in BoFM EME grammar via UD parse, not modern intuition

BoFM is in KJV-style Early Modern English with documented archaic constructions (Skousen 2009): nominative-absolute "they having", flat compound predicates, distinctive subordination, archaic complementizer "for to". Before agreeing OR disagreeing with an editorial intuition sourced from modern reading habits, check the UD parse: `data/text-files/v2-mine/...` corresponding `.conllu` (or run a query via `atu_method.conllu_query` / similar). Modern reading turbo-charges false-positive splits at archaic constructions that the UD signature would protect.

### Editorial-call structure

When Stan names a verse with a specific desired partition or proposes a fix: line 1 = "Got it — [Stan's reading]"; line 2-N = the diff. **NO leading analytical defense of an alternative.** Analysis is value-add ONLY when Stan asks "what should it be?" or "explain what's going on there."

### Class-fix vs instance-fix

Same FP class in 2+ rules OR 2+ validators OR 2+ verses in one session = engine-level fix at `validators/_shared/*` / `scripts/apply_*.py` / canon rule extension. Per-verse / per-validator guard the second time = whack-a-mole. **Stan's mantra: *swat the bug class, not the instance.***

### Grammar constrains; atomic-thought determines

Cross-corpus discipline per `../atu-method/memories/feedback_grammar_constrains_not_determines.md` + `framework.md §1.2` tail + new Factor A in `feedback_three_anti_default_factors.md`. BoFM-specific instantiation: Layer 1 vetoes are R9/R11/R13a/R10; complement-integrity rules are R17/R26; formula-integrity rules are R1/R18/R23; restrictive-relative bonds are R19 closed-list. Determination is via J1–J5 + the bidirectional atomic-thought test.

### The atomic-thought test is bidirectional — BoFM-specific implications

Cross-corpus discipline at `framework.md §1.1` + `../atu-method/memories/feedback_atu_test_is_bidirectional.md`. Anaphoric reference fails the test; cataphoric reference passes. BoFM-specific implications:
- **R1 AICTP merge is principle-rooted, not just formula-integrity-rooted.** *"And it came to pass [after these things]"* is anaphoric — the *these things* references undefined prior narrative. R1's merge mandate flows from the bidirectional test failing standalone, deepening R1's defensibility.
- **J5 SCOPE narrows.** J5 substantive-adjunct test requires referential self-containment. Deictic-pointer adjuncts (e.g., bare "after these things" without on-line antecedent) don't qualify and must merge.
- **Length is NOT the criterion.** A long line whose subject pronoun lacks on-line antecedent still fails. A short cataphoric line (*"Behold, the Lord cometh"*) can stand.
- **When auditing a Stan-flagged verse:** run BOTH forward closure AND backward referential-self-containment. Fail in EITHER direction = atomic-thought failure.
- **Cite §1.1 bidirectional, not M3/M4, when invoking.** Backward-anaphoric failure is caught at test-level, not at merge-override-level. M3 (forward-dangling head) and M4 (symmetric fragmentation) are §1.5 mechanisms; backward-anaphoric is upstream of both.

See `feedback_atu_test_is_bidirectional.md` for full discipline. Cross-cutting connection to `feedback_grammar_constrains_not_determines` (grammar = constraint; bidirectional atomic-thought = determination).

**Precedence clarification (added 2026-05-13 via gnt-reader sibling lesson):** the bidirectional test is canon §1.1 INFORMATIONAL DIAGNOSTIC, not a mechanical PRECEDENCE OVERRIDE. It INFORMS human audit judgment and DEEPENS the defensibility of canon-mandated decisions, but it DOES NOT serve as a validator trigger on its own — validators must fire on canon-encoded UD signatures (R/M/EP rules), NOT on bidirectional-test outcome. Mechanical authority comes from canon's encoded rules; bidirectional is a refinement of the determination engine, not a parallel determination authority.

### Rhetoric and ATU — BoFM worked examples

Cross-corpus discipline + figure→disposition table at `../atu-method/memories/feedback_rhetoric_figures_constrain_atu.md` + `framework.md §1.3a` + Factor A in `feedback_three_anti_default_factors.md`. The figure's default is a HYPOTHESIS; atomic-thought confirms or overrides. BoFM-specific worked examples surfaced 2026-05-13:

- `"hardness of HEARTS / blindness of MINDS"` — formally hendiadys-shaped but each NP has its own distinct sub-referent modifier → atomic-thought-test passes for each → SPLIT despite hendiadys surface
- `"commandments of God, / and his statutes, according to the law of Moses"` — formally J1 surface but unified under shared framing PP → MERGE (M1 hendiadys absorbs)

### Camera-angle diagnostic is DEPRECATED

Cross-corpus discipline at `../atu-method/memories/feedback_camera_angle_diagnostic_demote.md` + `framework.md §1.3` caveat. Treat invocations of camera-angle as a warning signal for bandwagon/aesthetic reasoning; use the bidirectional atomic-thought test instead. BoFM worked example: Alma 31:11 *"to preach the word unto them"* — YES argument leaned on camera-angle (motion-event vs preaching-event); NO argument leaned on bidirectional ATU failure + R7 canon SCOPE; NO carried.

### Use the UD layer FIRST. Agents are a last resort for corpus questions.

The BoFM Macula-equivalent already exists: full-corpus UD parses at `data/parses/ensemble/stanza/*.conllu`, queried via `validators/parsing/conllu_query.py` + `validators/parsing/line_mapping.py` (which gives v2-mine-line-of-each-token). Every active canon rule has a UD validator at `validators/colometry/validate_rule_*_ud.py`. The infrastructure for "find all tokens X whose head Y sits on a different ATU line, optionally filtered by deprel/upos/lemma" is **already built**.

**Before dispatching ANY agent for a corpus pattern survey, the answer is almost always a 30-50 line Python script using this infrastructure.** It returns deterministic results instantly — no FP filtering, no agent tokens, no wall-clock minutes. Per `feedback_scripts_before_agents` + `feedback_check_existing_tooling`.

Agent dispatch on a corpus question is only correct when:
- The pattern genuinely requires per-instance judgment the UD signature can't encode (e.g., restrictive vs non-restrictive relative clause without a discourse-tracked entity).
- You've ALREADY run the UD query and need agents to triage REVIEW-REQUIRED residuals.

When tempted to dispatch a survey agent, the test is: "Can I write the UD query in 30 lines?" If yes, **write it**. If you can't even articulate the UD signature, that's the signal to first study the pattern, not to substitute agent-grep for the missing signature.

**Failure mode this section codifies (hit 2026-05-12):** Stan flagged Alma 31:5. I dispatched 4 parallel grep agents to survey the corpus when the existing `validate_rule_17_ud.py` already has an inline comment marking the exact gap I was surveying for. The right move was a 50-line UD query, not 4 agents × ~80 sec each + ~80k tokens. Stan's correction: *"we created a macula-like layer, correct? is that not the syntactic mapping that should allow you to be triaging and manipulating the text mechanically instantly instead of these costly waves of agents."*

### Adversarial-audit discipline (pre-implementation)

Cross-corpus discipline at `../atu-method/docs/change-protocol.md §7.3` (12 mandatory-audit triggers) + `../atu-method/memories/feedback_rule_proposal_gates.md` (four-gate pre-proposal checklist). Before non-trivial implementation (new validator with classification logic, new rule subsection, new closed-list extension, new shared helper, OR ANY edit to `../atu-method/atu_method/*`): FIRST tool call ≥2 parallel Agent adversarial dispatches OR explicit `Audit-skippable: <named-trivial-class>`. Canon-touching commit messages require `Audit-skippable per §7.3 ([reason])` OR `Audit dispatched: [evidence]`; commit-msg hook enforces.

### Apply causes regression

Revert the apply → root-cause why → fix the apply → re-attempt with integrity gate verified post-apply. Do NOT build downstream-recovery tools first. Cluster-agent "pass" reports don't substitute for the integrity gate.

### Stan-escalation phrasing ("WHY are you still doing this", "stop wasting my time", "you screwed up again", "did i or did i not say...")

STOP iterating on the surface fix. Frame-reset to class level. Ask: what's the COMMON pattern across recent attempts that I've been treating as separate instances? The escalation is a signal that the loop has run too long; the meta-pattern is what needs the answer, not another surface iteration.

### Proactive open-item surfacing

Every deferred item must be visible in chat (per `feedback_decisions_in_chat_not_files.md` — chat is the decision surface; pending.md is status-tracker only). Periodically re-examine whether held items have become canon/code/precedent-derivable as the method matures. If yes, surface "I previously needed your input on X; canon now resolves it via Y; applying unless you say stop" — don't re-defer derivable items.

---

## Source file rules

`data/text-files/v2-mine/` is the canonical source. Hand-edited by Stan, one ATU per line. **Sacred.**

NEVER alter punctuation (post-1830 editorial overlay, canonical to LDS text). NEVER add, remove, or change words. NEVER apply ad-hoc / novel changes without Stan approval. ALWAYS preserve verse-refs. The ONLY editorial tool is where lines break.

**Rule-derivative changes are different and do NOT require per-item approval.** When a settled mechanical rule in canon (Category A: R1, R5–R7, R9–R23, R26, R28, EP-1/3/4/5, M-overrides per §3 Quick-Reference) fires unambiguously via its validator or a clean trigger match, applying that rule IS the approval. STRONG-MERGE-CANDIDATE / STRONG-SPLIT-CANDIDATE validator tags are application-ready. Only `REVIEW-REQUIRED` items need per-item editorial judgment.

---

## Methodology stack

Three forces operating simultaneously: **generative** (atomic thought drives line creation; J1–J5 structural justifications), **subtractive** (Layer 1 syntax + complement + formula integrity trigger merges; M1–M4 merge-overrides), **diagnostic** (single-image / camera-angle as tiebreaker). Authoritative body: [`../atu-method/docs/framework.md`](../atu-method/docs/framework.md). BoFM-specific rule detail: `private/01-method/colometry-canon.md` §5.

**Categories** (autonomy boundary per `../atu-method/docs/framework.md` §2):
- **Category A** (Mechanical, mandatory) — rule firing IS the approval; auto-apply.
- **Category B** (Editorial, judgment-required) — flag and discuss with Stan.
- **Category C** (Theological / textual-critical) — hand-curation only.

**No editorial overlay has interpretive force.** Punctuation is preserved for fidelity but is post-1830 editorial overlay; never used as break/merge evidence (per `feedback_punctuation_not_evidence`).

---

## Pipeline & files

**Source → render pipeline:**

| Tier | Directory | Engine |
|---|---|---|
| v0 | `data/text-files/v0-bofm-original/` | 2020 LDS base text, never edited |
| v1 | `data/text-files/v1-skousen-breaks/` | Skousen sense-line precursor, input only |
| v2 | `data/text-files/v2-mine/` | Stan + Claude hand-edited, single source of truth |

`build_book.py --all` → `books/*.html` per line: `wrap_punctuation(fix_participles(apply_swaps(line, swap_list)))`. After source text changes, bump `sw.js` cache version (`bomreader-vXX` → `+1`).

**Swap system** (reference implementation, ported to siblings via `../atu-method/atu_method/swaps/`): archaic words wrapped `<span class="swap" data-orig="archaic" data-mod="modern">archaic</span>`. `.swap` (dotted underline, vocabulary modernization) + `.swap.swap-quiet` (no decoration, high-frequency grammar words). TTS reads `data-orig` (authentic text), NEVER `data-mod`.

**Audio** (Samuel voice `ddDFRErfhdc2asyySOG5`, `eleven_multilingual_v2`, ~100k chars/month). Pipeline: `colab/samuel_pipeline.ipynb` with Drive persistence (cache on ephemeral VM = lost files). 1 Nephi complete; 2 Nephi ch 1–5 only; Enos complete.

---

## Validators & mechanical gates

Layer 1 = generic English-grammar break-legality (`data/syntax-reference/ud-taxonomy.md` §7) — permission/prohibition. Layer 3 = BoFM editorial methodology (canon §5) — operates within L1's permitted space. Mixing the two is a regression.

**Validator findings = work queue, not review queue.** STRONG-MERGE / STRONG-SPLIT → mechanical apply (Category A). REVIEW-REQUIRED → per-item judgment. Walking Stan through verse-level confirmations on rule-derivative changes is the inverted-discipline failure mode.

**Mechanical gates:**
- `validators/run_all.py --baseline-check` blocks regressions vs `validators/.baseline.json`. Wired as `.git/hooks/pre-commit` via `bash validators/hooks/install.sh`.
- `validators/check_canon_extensions.py` detects canon-extension patterns in staged diffs; requires audit-evidence keyword (`Audit dispatched`, `hostile audit`, `§7.3`, etc.) or skip-safe claim (`Audit-skippable per §7.3 (...)`) in the commit message. Wired as `.git/hooks/commit-msg`.

**Bypass:** `git commit --no-verify` = Stan-only explicit override. New validators stage `--update-baseline` in the same commit. Canon commits include the audit-status declaration substring or fail the hook.

---

## Canon-to-git policy

`private/` is gitignored EXCEPT a tracked-exception family: `private/01-method/colometry-canon.md`, `private/01-method/pericope-canon.md`, and everything under `private/01-method/scholarship/` (per-rule scholarly-grounding companion documents — added 2026-05-16, parallel to readers-gnt). All tracked via `git add -f` so the public repo shows current canon state AND its defensibility surface to any future scholar.

- Dropbox is the sole versioning substrate for canon micro-refinement history.
- Git tracks publicly-published canon state — the form a scholar would weigh on its merits.
- Per-rule defensibility surface (citations, rationale, empirical-validation evidence) lives in `scholarship/r{N}.md` per `atu-method/docs/rule-template.md`. When future §5 work touches a rule with inline scholarly citations, MOVE them to scholarship/ rather than deleting — see `private/01-method/scholarship/README.md`.
- Other `private/` files (session folders, research notes, sub-method docs) stay gitignored and unversioned in git.

---

## Default decisions (do NOT surface as menus to Stan)

| Decision point | Standing answer |
|---|---|
| Corpus pattern survey / "how many instances of X in BoFM" | UD query script against `data/parses/ensemble/stanza/*.conllu` via `validators/parsing/conllu_query.py`. ~30-50 lines, instant, deterministic. NEVER dispatch agents to grep the corpus for syntactic patterns — the Macula-equivalent already exists. |
| Adversarial audit on non-trivial implementation | ≥2 parallel Agent dispatches in one message, OR `Audit-skippable: <named-trivial-class>`. Never sequential. |
| Extending existing validator vs creating new | Extension. New = explicit justification with substantive criterion (per `feedback_check_existing_tooling`). |
| Same FP class in 2+ rules/validators/verses in session | STOP. Engine-level / canon-level fix. No more per-instance guards. |
| Apply causes regression | Revert → root-cause → fix → re-apply with integrity gate. NEVER build recovery tools first. |
| Commit attempt fails | Diagnose `git log -3` + `git status --short` BEFORE retry. Use `git commit -m "$(cat <<'EOF'...EOF)"` (NEVER `-F /dev/stdin` — Linux-only). Never run two `git commit` in parallel — they race on HEAD lock. |
| "Should I commit now or wait?" | Commit substantive work proactively; status claims AFTER commit (per `feedback_commit_workflow`). |
| Cascade rebuild after pipeline change | Parallel cluster agents; never one agent on 15 books. |
| Per-item judgment work at corpus scale | Parallel cluster-Opus dispatch; never hand-pass. |
| Stan asks "explain what's going on there" / "what is the correct approach" | Diagnose the rule-set gap. Do NOT propose Option A / Option B menus on the surface verse. |
| Stan names a verse with a desired partition | "Got it — [reading]" + diff. No leading analytical defense. |

When outside this table, surface. When inside, dispatch the standing answer and report the result.

**Corpus clusters** (for cluster-cascade routing): Small Plates (1 Ne, 2 Ne, Jacob, Enos, Jarom, Omni, WofM) / Mosian Era (Mosiah, Alma 1–44) / War Narrative (Alma 45–63, Helaman) / 3 Nephi–4 Nephi / Mormon–Ether–Moroni. Threshold: any batch ≥25 surgical fixes spanning 3+ clusters MUST be split.

**Agent model routing (Stan-prime-directive 2026-05-15 per `feedback_model_selection_frugality`):** match the tier to the task — *"don't blow thru opus tokens for a haiku or sonnet task."* **Set `model:` explicitly on every Agent dispatch.** Haiku for mechanical lookups / one-shot extractions / running existing scripts. Sonnet (the default) for per-case judgment with a clear rubric — corpus surveys with classification, structured audits with codified canon checks, multi-cluster per-case sweeps. Opus only when the rubric ITSELF is the question — hostile adversarial scope-scrutiny, signature design for new mechanical rules, methodology/discipline work, cross-corpus shared-infrastructure edits. Before every dispatch: *"could a smaller model with a tight rubric handle this?"* If yes, downshift.

---

## Git workflow

All work on `main`. **Commit AND push autonomously after any clean commit on main** (Stan blanket-authorized 2026-05-11; SSH transport `bibleman-windows-desktop` key, silent pushes). Sequence: `git commit` → if exit 0 → `git push origin main` → THEN report.

**Confirm BEFORE push:** force-pushes (`--force` / `--force-with-lease`); pushes to non-main; pushes containing agent-applied bulk corpus changes Stan hasn't diff-reviewed.

**Tree-state self-check before commit (mandatory):** `git status --short`. If unrelated work is staged, separate it before committing — commit titles must describe actual scope. Either ask first, commit separately, or `git stash --keep-index`.

**Agent commit discipline:** when briefing committing agents, mandate targeted `git add <specific-path>` per file. Never `git add -A` (sweeps parallel uncommitted work, misattributes — per `feedback_agent_git_add_discipline`).
