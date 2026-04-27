# BOM Reader — Claude Code Instructions

Read this file completely before doing anything in this repo. It is your orientation document for every session.

---

## What This Project Is

A web-based reading app for the Book of Mormon at **bomreader.com**, designed for ESL readers, children, and newcomers. Text is presented in sense-line (cola) format — each line is a natural breath unit for read-aloud delivery. Archaic words can be toggled to modern equivalents. Multiple study layers (deity references, biblical quotations, geography, Hebrew poetry) can be overlaid. Audio narration per chapter.

- **Repo:** github.com/bibleman-stan/readers-bofm (public)
- **Hosting:** GitHub Pages from main branch
- **Stack:** Vanilla HTML/CSS/JS single-page app, Python 3 build scripts
- **Local dev:** `python -m http.server 8000` (file:// won't work)
- **User:** Stan (thebibleman77@gmail.com)

---

## Read the Handoff Docs First

Before any substantive work, read the handoffs directory in order. Each file is independently readable:

| File | Covers |
|------|--------|
| `handoffs/00-index.md` | Index and update protocol |
| `handoffs/01-project-overview.md` | Architecture, key files, book metadata, CSS variables |
| `handoffs/02-text-editorial.md` | Source text pipeline, editorial principles, swap system |
| `handoffs/03-audio-voice.md` | Voice decisions, ElevenLabs config, Colab pipeline |
| `handoffs/04-ui-ux.md` | UI structure, navigation, scroll behavior, known issues |
| `handoffs/05-build-pipeline.md` | build_book.py, data layers, pericopes, Hebrew poetry |
| `handoffs/06-deployment-infra.md` | GitHub Pages, service worker, git workflow |
| `handoffs/07-pending-tasks.md` | Prioritized task list |
| `handoffs/08-future-plans.md` | Spanish fork, Studying Edition, shelved ideas |
| `handoffs/09-bugs-fixed.md` | Historical bug fixes and key design decisions |
| `handoffs/14-operational-protocols.md` | "Work smarter" patterns: parallel dispatch, two-phase pipeline, find-the-class fixes — READ THIS CAREFULLY |

---

## Session bookend protocol (revised 2026-04-20 — overseer deprecated)

**The overseer system is deprecated as of 2026-04-20.** Do NOT read or update `private/OVERSEER-DIRECTIONS.md` or files under `overseer-workspace/` — those remain as historical archive but are no longer authoritative. Stan is the direct authority.

### Session folder convention (clarified 2026-04-20 PM via cross-project directive)

**A session = one Claude Code JSONL session**, not a calendar day. A compaction-wake starts a new session — create a new folder with a new descriptor even if the calendar date matches a pre-compaction folder. Multiple folders sharing a date with different descriptors is correct.

Each session has its own folder at `private/YYYY-MM-DD-brief_description/` where `YYYY-MM-DD` is the **session start date** (not today's date if the session crossed midnight) and `brief_description` distinguishes the session from others on the same date.

Contents:
- `transcript.md` — verbatim user + assistant text, generated from JSONL at session end (skip tool-use and tool-result entries for readability)
- `session-notes.md` — narrative summary of the session arc: what happened, why, what was decided
- `decisions.md` — key decisions made, one paragraph each with rationale
- `pending.md` — explicit carry-forward items for the next session

### CHECK-IN at session start

**MANDATORY (read every wake):**
1. This `CLAUDE.md` in full
2. `private/01-method/colometry-canon.md` — especially §0 Mission, §1 Framework, §2 Autonomy Boundary, §5 Rule detail
3. The most recent session folder under `private/YYYY-MM-DD-*/` — specifically its `pending.md` (carry-forward state) and `session-notes.md` (prior-session context)
4. `git log --oneline -10`

**CONSULT-ON-TRIGGER:**
- `data/syntax-reference/ud-taxonomy.md` §7 Break Legality Reference — **trigger:** any Layer 1 mechanical-rule work or validator design.
- `validators/README.md` — **trigger:** writing or modifying a validator.
- `C:\vaults-nano\my_brain\00_Inbox\claude-brainstorming.md` — **trigger:** Stan references a mobile-inbox item.

**Self-report** before first substantive response: one-line-per-file confirmation of what you read, with any red flags surfaced.

### At session end (WRAP-UP)

Produce four files in the current session folder:
1. `transcript.md` — dispatch a JSONL-filter agent (see `/chats/` path printed at session start; Claude Code writes JSONL per session)
2. `session-notes.md` — narrative summary
3. `decisions.md` — key decisions with rationale
4. `pending.md` — carry-forward for next session

Commit any code/corpus changes before wrapping. Session folder files live in gitignored `private/` so they don't need committing. Canon changes require `git add -f private/01-method/colometry-canon.md` per §Canon-to-git policy below.

**Self-consistency audit trigger (added 2026-04-22 from GNT cross-project directive):** If the session added **≥2 new canon subsections/rules/merge-overrides**, run a light self-consistency audit before wrap — check that new cross-references resolve, no contradictions with existing rules, all three defensibility elements (WHY/HOW WE KNOW/SCOPE per canon §7) are present. Short pass. See canon §7 for the full trigger description.

**Carry-forward discipline (added 2026-04-22):** Anything noted as "defer to future session" anywhere in the session's documentation MUST get a corresponding line in `pending.md`. Canon §8 notes, session-notes narratives, and agent reports do not survive session boundaries — only `pending.md` does. If you say "defer," write it to `pending.md`.

### Compaction-resume

Compaction is a session boundary. When resuming from a compaction summary, still execute the full CHECK-IN protocol above. Compaction gives context but does not exercise the orientation muscles — silent skip is a check-in failure. Per the session folder convention: a compaction-wake creates a NEW session folder with a new descriptor, even if the calendar date matches the pre-compaction folder.

### Canon-to-git policy (adopted 2026-04-20 PM from cross-project directive)

**`private/` is gitignored EXCEPT for two tracked exceptions: `private/01-method/colometry-canon.md` and `private/01-method/pericope-canon.md`.** Both canons are tracked via `git add -f` so the public repo shows their current form to any future scholar or collaborator reading the method docs. Colometry governs LINE breaks (within-verse cola); pericope governs SECTION breaks (multi-verse natural-unit boundaries).

- **Dropbox is the sole versioning substrate** for the canon. Micro-refinement history lives in Dropbox's sync, not git.
- **Git tracks only publicly-published canon state** — the form a scholar would read, weighed on its merits, not wading through micro-commit history.
- When the canon changes, update the tracked file via `git add -f private/01-method/colometry-canon.md` in the same commit as any code/corpus changes that accompany it.
- Other files under `private/` (session folders, research notes, sub-method docs) stay gitignored and unversioned in git. They live in Dropbox only.

**Rationale:** the target audience for the tracked canon is a future scholar reading the final-form method doc. Micro-commit granularity obscures the method; a single tracked current-state file exposes it clearly.

---

## Key Files

| File | Purpose |
|------|---------|
| `index.html` | Main app shell — ALL CSS, HTML, JS inline (~4220 lines) |
| `build_book.py` | Converts sense-line .txt sources → HTML fragments (~1090 lines) |
| `senseline_reformat_v8.py` | 19-pass automated sense-line reformatter |
| `narration.js` | Audio playback module (~1050 lines) |
| `sw.js` | Service worker — bump version on every change |
| `books/*.html` | Generated HTML fragments, one per book |
| `data/text-files/v2-mine/` | **Canonical source text files — see rules below** |
| `data/text-files/v1-skousen-breaks/` | Skousen sense-line formatting (input only) |
| `data/text-files/v0-bofm-original/` | 2020 LDS base text (reference only) |

---

## CRITICAL: Source File Rules

The files in `data/text-files/v2-mine/` are the canonical source. These are Stan's hand-edited sense-line files. They are sacred.

**NEVER:**
- Alter punctuation (punctuation belongs to the canonical LDS text)
- Add, remove, or change words
- Apply **ad-hoc / novel** changes (changes not derived from a settled rule in `private/01-method/colometry-canon.md`) without Stan's explicit approval

**ALWAYS:**
- Present ad-hoc / novel proposed changes for review before touching any canonical file
- Save the original before any new upload could overwrite it
- Make line-break changes only — the only editorial tool is where lines break

**Rule-derivative changes are different and do NOT require per-item approval.** When a settled mechanical rule in the canon (Rules 1, 7, 9, 10, 11, 12, 13a, 15, 16, 17, 18, 19, 20, 21, 23, 26, 27, 28, etc.) fires unambiguously against the corpus — via its validator or a clean trigger match that the rule's UD signature catches — applying that rule IS the approval. The canon is the agreement. Rule-derivative changes on mechanical triggers are Category A by default and apply without per-item flagging.

**Validator output is a work queue, not a review queue.** `STRONG-MERGE-CANDIDATE` and `STRONG-SPLIT-CANDIDATE` tags are application-ready. Only `REVIEW-REQUIRED` items (those the validator itself flags as heuristic-ambiguous) need per-item editorial judgment. Don't invert this discipline by treating clean mechanical hits as "candidates for review" — that's the over-cautious failure mode, and it creates toilsome friction for Stan who already authorized the rule.

Do not work on copies of v2-mine files; edit them directly when applying rule-derivative changes. Git and the canonical-LDS-text punctuation-preservation rule are the safeguards, not file-copy rituals.

---

## Sense-Line Editorial Methodology

This is the intellectual heart of the project. The full methodology canon lives at `private/01-method/colometry-canon.md` (gitignored). Key principles:

### The Foundational Test
**Each line must be an atomic thought, an atomic breath unit, or ideally both.**

This overrides all other rules. A line that passes this test is valid. A line that fails it needs revision.

- **Atomic thought:** the reader can process this line as a single unit of meaning without needing the next line to resolve it
- **Atomic breath unit:** the line can be delivered in one breath at natural reading pace

### The Image Test
Each line should paint a single image or picture in the mind. If a line contains two distinct images, it's a candidate for splitting. If a line contains no complete image, it may need merging with its neighbor.

### Grammar Reveals Structure — It Doesn't Create It
Line breaks follow grammatical structure that already exists in the text. Breaking at causal clauses ("because"), purpose clauses ("that they might"), relative clauses, and parallel structures makes visible what is already encoded. The breaks are descriptive, not interpretive.

### Verb Breaks
Breaking *on* verbs (giving each verb its own line) is often correct — verbs are where the action is. Each verb is a frame, an image, a moment.

### Settled Rules (examples)

Full settled-rules list authoritative at `private/01-method/colometry-canon.md` §Settled Rules. The canon has greater depth (WHY/HOW/SCOPE per rule, precedent cases, diagnostic tests). Fresh-read the canon before any editorial or rule work. Representative examples for orientation:

1. **AICTP integrity** — "And it came to pass that" stays on one line; never break mid-phrase. "Dangling that" variant: break BEFORE "that" so it leads the next line.
2. **Never end a line on a conjunction or article** — "and," "or," "but," "nor," "the," "a," "an" dangling at line end is always wrong. Move to lead the next line.
3. **Vocative units are indivisible** — "O Lord God," and "O Lord our God," stay whole; never split mid-address.
4. **Complement Integrity (Rule 17, generalized 2026-04-17)** — causative, aspectual, speech (indirect), cognition, volition, and FEF verbs require their "that"-clause complement on the same line. Six explicit exceptions live in the canon.

### Three Categories for Proposed Changes

- **Category A — Editorial slippage:** suboptimal break, no theological or rhetorical stakes. Propose confidently.
- **Category B — Rhetorical shape:** changing the break changes how the speaker builds an argument. Flag and ask before proposing.
- **Category C — Theological weight:** break placement makes a doctrinal point. Flag and discuss before touching.

### What Never Changes
- Punctuation (always canonical LDS text)
- Words (never add, remove, or alter)
- Only line break positions change

---

## Build Pipeline

After any source text changes:

```bash
python3 build_book.py --all
```

This rebuilds all `books/*.html` fragments from the v2 source files. Also bump the service worker cache version in `sw.js` — find `bomreader-vXX` and increment XX.

The pipeline per line: `wrap_punctuation(fix_participles(apply_swaps(line, swap_list)))`

### Swap System
Archaic words are wrapped in `<span class="swap" data-orig="archaic" data-mod="modern">archaic</span>`. Two classes:
- `.swap` — visible dotted underline (vocabulary modernization)
- `.swap.swap-quiet` — no decoration (high-frequency grammar words: thee, hath, unto)

TTS audio reads `data-orig` (authentic text), NOT `data-mod` (modern). Never change this.

---

## Git Workflow

- All work on `main` branch
- Stan pushes from his local machine — Claude Code cannot push (403 proxy error)
- Bump service worker cache version with every CSS/JS/HTML change
- Audio files (.mp3) are committed directly to repo (no LFS)
- **Security alert:** Google API key exposed at `annotations.js` line 26 — needs restriction in Google Cloud Console

---

## Audio Pipeline

- **Voice:** Samuel only (`ddDFRErfhdc2asyySOG5`), `eleven_multilingual_v2` model
- **Credits:** ElevenLabs, ~100k chars/month
- **Pipeline:** `colab/samuel_pipeline.ipynb` — parameterized, has Google Drive persistence
- **CRITICAL:** Always use Drive persistence. Cache on ephemeral VM = lost files.
- TTS reads authentic BofM text (`data-orig`), NOT modernized swaps
- Audio inventory: 1 Nephi complete, 2 Nephi ch 1-5 only, Enos complete

---

## Pending Tasks (Priority Order)

1. Generate 2 Nephi ch 25-33 audio (~49k chars) when credits reset
2. Test audio playback on bomreader.com for 2 Ne 1-5
3. Fix audio-highlight sync drift (pericope headers throw off lineIndex count)
4. Fix 1 Ne 6:1 verse text
5. Fix KJV diff display (currently destroys sense-line formatting when toggled)
6. Fix build_kjv_diff.py hardcoded paths (lines 334, 348)
7. Light mode CSS verification for new UI elements
8. Surface book introductions (currently hidden in settings-panel-old)
9. Restrict Google API key in Google Cloud Console

---

## Book Inventory

| ID | Name | Chapters | Audio |
|----|------|----------|-------|
| `1nephi` | 1 Nephi | 22 | ✅ Complete |
| `2nephi` | 2 Nephi | 33 | ⚠️ Ch 1-5 only |
| `jacob` | Jacob | 7 | ❌ None |
| `enos` | Enos | 1 | ✅ Complete |
| `jarom` | Jarom | 1 | ❌ None |
| `omni` | Omni | 1 | ❌ None |
| `words-of-mormon` | Words of Mormon | 1 | ❌ None |
| `mosiah` | Mosiah | 29 | ❌ None |
| `alma` | Alma | 63 | ❌ None |
| `helaman` | Helaman | 16 | ❌ None |
| `3nephi` | 3 Nephi | 30 | ❌ None |
| `4nephi` | 4 Nephi | 1 | ❌ None |
| `mormon` | Mormon | 9 | ❌ None |
| `ether` | Ether | 15 | ❌ None |
| `moroni` | Moroni | 10 | ❌ None |

---

## UI Architecture (Post-Mar 16 Redesign)

- **Thin persistent topbar** (44px): book/chapter name left, Modern pill + Search + Settings right
- **Full-screen picker:** opens on tap of book/chapter in topbar
- **Bottom sheet:** settings (modern words, listen, section headings, text size, light mode)
- **Hash routing:** `#bookId` or `#bookId-chapterNumber` (e.g. `#alma-45`)
- **Two entry points:** `index.html` (main SPA) and `books/index.html` (alternate view) — CSS changes must be applied to both
- **Sense-lines only** for Reading Edition — `applyTextMode(1)` forced on load

### CSS Variables
```css
:root {
  --line-height: 2.35;
  --wrap-indent: 0.75em;
  --verse-gap: 2px;
  --punct-opacity: 0;
  --font-size: 17px;
}
```

Verse-number visibility is controlled by a body class (`body.hide-verse-num` hides them) toggled from the bottom settings sheet, not by a CSS variable. Default state: visible. Persisted to localStorage as `bomreader-verse-num`. Punctuation visibility is similarly controlled by `body.hide-punct` (default: hidden); the `--punct-opacity` variable above is the older mechanism and may be retired in the future.

---

## Known Issues

- Audio-highlight sync drift after pericope headers (lineIndex mismatch)
- KJV diff layer destroys sense-line formatting when toggled
- Light mode CSS unverified for new topbar/picker/sheet elements
- Book introductions inaccessible (hidden in old panel)
- Google API key exposed in annotations.js

---

## Agent dispatch — match model to task

When dispatching subagents via the Agent tool:
- **Haiku** — mechanical work: file moves, glob/ls formatting, reference lookups, yes/no checks against file content, corpus-wide pattern scans with defined rules
- **Sonnet** — templated/narrow: scanner runs with defined rules, quick consistency checks, documentation updates following a template, cross-project consistency checks once both sides are stable
- **Opus** — reasoning-heavy: multi-angle adversarial audits, methodology synthesis, restructuring major documents, novel rule design, anything where the judgment IS the work product

When in doubt, Sonnet is the right default. Stan shouldn't have to think about this — you make the call.

**Parallelization default (added 2026-04-23).** When multiple audits are independent, dispatch them in parallel — one message with multiple Agent tool calls. Sequential only when audit A's verdict determines whether audit B should run. This substantially reduces audit friction (demonstrated 2026-04-23: 3 parallel audits at ~26 seconds each vs. ~80+ seconds sequential). Applies equally to non-audit subagent dispatches when they are independent.

## Pre-commit adversarial-audit discipline (added 2026-04-23)

**Before any commit that includes `git add -f private/01-method/colometry-canon.md`, check whether the change matches a mandatory-audit trigger per canon §7.3.** The 11 triggers are listed in canon §7; re-read them when uncertain. If the change matches any trigger, audit evidence (hostile-agent dispatch + verdict + application) must be present in the commit message or the canon §8 Update Log entry.

**Audit-skippable.** Canon edits that do NOT match any trigger (typo fixes, cross-reference updates without precedence claims, deletions of same-session reverts, defensibility-capture additions to already-settled rules without scope changes, Category A mechanical corpus edits that are not part of a ≥5-instance sweep) proceed without audit.

**When uncertain.** Dispatch the audit. The cost of a false-positive audit (Stan reads a no-op audit result) is small; the cost of a false-negative audit (fake rule commits) is large.

**Mechanical gates installed (2026-04-26 / 2026-04-27):**
- `validators/run_all.py --baseline-check` runs all syntax/colometry validators against the corpus and blocks commits introducing regressions vs `validators/.baseline.json`. Wired as `.git/hooks/pre-commit` via `bash validators/hooks/install.sh`.
- `validators/check_canon_extensions.py` analyzes staged canon diffs for §7.3 trigger #1 patterns (new closed-list rows, new rule sections, new merge-overrides, new dated principles, new trigger entries, new SCOPE-exclusion bullets) and requires the commit message to contain audit-evidence keywords (`audit`, `hostile audit`, `trigger #`, `§7.3`, `post-codification`, `post-detection`, `corpus-fit`, `RETRACT`, `§8 update log`) — or skip-safe claim (`typo fix`, `cross-reference update`, `defensibility-capture`, `audit-skippable`) — or `stan-authorized` / `stan-direct`. Wired as `.git/hooks/commit-msg`. Closes the gap that `--baseline-check` can't catch (new closed-list extensions don't necessarily increase any rule's existing violation count). Bypass: `git commit --no-verify` (Stan-only).

**Self-test to run pre-commit** (faster than trigger-list scan):
- Does this change include a scope claim, a precedence claim, a closed-list extension, or a named-category carve-out? → audit.
- Does this change rest on spot-check evidence rather than a full-corpus classification? → audit.
- Does this change reclassify or delete previously-settled canon content? → audit.
- Did this session codify a new rule, sub-clause, or named pattern, AND has the corpus-fit sweep NOT yet been run on the full corpus (per canon §7.3 trigger #12, added 2026-04-25)? → run goal-fit + application-consistency audits before commit, OR enumerate residuals in pending.md as next-session FIRST item. The codifying sweep saw what the codifier looked at; the goal-fit sweep finds what they didn't.
- If no to all four → probably skip-safe.

This discipline is codified in canon §2 (scope/precedence/closed-list/carve-out = Category B diagnostic) and canon §7.3 (mandatory-audit trigger list). See also the `feedback_rhetoric_bandwagon` memory's named-category-carve-out and biased-spot-check sub-patterns.

---

## Update Protocol

When updating handoff docs, append a dated block at the bottom of the relevant file:

```markdown
---
### Update — 2026-MM-DD
- What changed
- What was decided
- New state
```

Never overwrite history — always append.

---

## What Stan Does / What Claude Does

**Stan:**
- Makes all final editorial decisions on line breaks
- Reviews all proposed changes before they touch canonical files
- Pushes to GitHub
- Has final say on all Category B and C colometry decisions

**Claude Code:**
- **Mechanical passes:** find and APPLY rule-derivative changes (dangling conjunctions per Rule 9, complement-integrity merges per Rule 17, insomuch-that binding per Rule 27, etc.). Canon is authority; no per-item flagging needed for clean mechanical hits.
- **Ad-hoc / novel proposals:** present in clear before/after format for Stan's review. These are Category B/C changes, not rule-derivative.
- **Apply approved changes directly to canonical files.** File-copy rituals are not the safeguard — the safeguards are the punctuation-preservation rule, the words-never-change rule, git history, and the rule-derivative vs. ad-hoc distinction.
- Run build pipeline after source text changes (`python3 build_book.py --all` + bump `sw.js` cache version).
- Never alter punctuation, words, or structure — line breaks only
- **Colometry review partner:** on request, agree/challenge/suggest on Stan's edits using the settled rules and category framework
- **Handoff maintenance:** after any session where decisions are made, principles are refined, or new patterns identified, update the relevant handoff file (append dated block, never overwrite history)
- **"Do an update" means:** update ALL relevant handoffs, memory files, research files, and any other documentation so that a fresh session can resume with full context
- **Hedging discipline:** do not ask for confirmation on rule-derivative actions Stan has already implicitly authorized by adopting the rule. "Yes that's fine" after clear prior direction is a friction cost that compounds across a session. If the rule says to do X and conditions are unambiguous, do X.

---

## Connected Resources

### Academic Vault
Stan's academic Obsidian vault at `C:\vaults-nano\my_brain\` contains his OTC dissertation materials, bibliographic records (332 sources), scholar hub notes (~230), and 838 zettels. The vault's `CLAUDE.md` has full orientation. Read it for context when work touches Hebrew poetry, oral tradition, stylometry, or the FEF paper.

The BOM Reader `research/` folder is symlinked into the vault at `10_Projects/BOM-Reader-Research/`. Files live in the vault; the repo path is a symlink. The folder is gitignored.

### Two-AI Workflow
Claude Code (this tool) handles file access, commits, mechanical analysis. Claude.ai chat handles brainstorming, design, paper strategy. Stan bridges between them. Handoff docs and research files are the shared ground truth — keep them current so either AI can spin up with full context.
