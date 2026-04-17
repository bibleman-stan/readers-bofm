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

Also check `private/OVERSEER-DIRECTIONS.md` if present — local-only session directives (gitignored, Dropbox-backed). It carries active directives, the pointer to the full methodology canon, and a sync log. **Read it before starting substantive work, and update it before ending the session or committing — whichever comes first.** It contains its own documentation protocol; follow it. Session memory evaporates at compaction but that file survives, so treat it as the persistent write surface for anything the overseer needs to know about your session.

---

## Session bookend protocol (standing rule — CHECK-IN + WRAP-UP)

**Sessions have two mandatory bookends: a check-in at the start, a report at the end.** The overseer (cross-project Claude) cannot see your conversation — it only sees files you leave behind. The bookends are how the overseer stays oriented across sessions without having to guess or have Stan paste everything manually.

### CHECK-IN — at session start

When Stan signals start-of-session with phrases like **"hey, let's start a new session," "new session," "fresh start," "let's begin," "let's kick off,"** or any similar opening language — before you do any substantive work, read these files in this order:

1. **This CLAUDE.md file in full** — you may already be doing this on orientation, but confirm it.
2. **`private/OVERSEER-DIRECTIONS.md`** — active cross-project directives, sync log, documentation protocol. This is your primary coordination surface with the overseer.
3. **`private/README.md`** — subdirectory layout of `private/` so you know where to find things and where to write new files.
4. **`c:/Users/bibleman/repos/overseer-workspace/LANDSCAPE-MAP.md`** — one-glance snapshot of where the whole program is right now. Tells you what's hot, what's resolved, what's open. **Read this every session — it's the overseer's dip-in file and it's kept fresh.**
5. **`c:/Users/bibleman/repos/overseer-workspace/METHODOLOGY-TIMELINE.md`** — dated log of methodology state changes on both projects. Check this if you're going to touch any scan/audit/findings files from prior sessions — the timeline tells you what methodology state they reflect.
6. **`c:/Users/bibleman/repos/overseer-workspace/OPEN-QUESTIONS.md`** — unresolved threads that might intersect with whatever Stan is asking for. Skim for relevance.
7. **`private/01-method/colometry-canon.md`** — the methodology canon. Always fresh-read before any editorial or rule work. Rules evolve fast.
8. **`C:\vaults-nano\my_brain\00_Inbox\claude-brainstorming.md`** — Stan's mobile-to-desktop idea bridge. He voice-chats ideas with mobile Claude; they land here via Obsidian Sync. Rules of engagement (three Claudes may be reading this file — overseer + both trench Claudes — coordination matters):
   - **Read all unaddressed items** (those without a ✓ or ⏳ mark).
   - **Assess scope:** If clearly BofM-related (mentions BoM, BofM passage, bomreader), the BofM trench Claude handles it. If clearly GNT-related, the GNT trench Claude handles it. Cross-project, methodology-wide, or ambiguous items → the overseer handles (or you raise to Stan).
   - **If an item is in YOUR scope:** claim it by adding a line below Stan's text: `⏳ [claimed by bofm-trench YYYY-MM-DD]`. Work on it during the session.
   - **When done:** replace the ⏳ line with `✓ YYYY-MM-DD — [one-line disposition]. [pointer to commit/session-notes/canon section where the real record lives].`
   - **If an item is NOT in your scope:** do NOT touch it. Don't claim it, don't address it, don't delete or archive it. Mention it in your check-in to Stan only if it bears on what he's asking.
   - **Never delete items.** Archival is the overseer's job (moves ✓-annotated items to `claude-brainstorming-archive.md` in the same folder).
9. **`git log --oneline -10`** — see what's committed since the last session. Any commit you don't recognize is a state change you should understand before working.

**After reading:** send Stan a brief check-in message confirming orientation. Something like: "Checked in. Current state: [one-sentence summary]. Top 2-3 hot threads per LANDSCAPE-MAP: [...]. Anything specific you want me to focus on, or should I continue the queued work?" Keep this to 4-5 lines. The goal is to prove you read the files, not to summarize them exhaustively.

**Why this matters:** sessions that skip the check-in tend to propose things contradicting recent state, re-argue decisions already made, miss open questions that affect the current task, and waste Stan's time on corrections the overseer already wrote down. The overseer workspace and the OVERSEER-DIRECTIONS file are the cumulative state — reading them puts you in the same frame the overseer operates from.

### WRAP-UP REPORT — at session end

When Stan signals end-of-session with phrases like **"let's wrap it up for now," "wrap it up," "let's stop here," "that's enough for today," "commit and wrap,"** or any similar winding-down language — do these things BEFORE you commit or stop, in this order:

1. **Write session-dir notes for ANY substantive work, not just dialogues.** Create `private/sessions/[YYYY-MM-DD]-[topic-slug]/` and drop a notes file inside. This is **mandatory for any session that produced any ONE of the following** (not just dialogues):
   - **Methodology dialogue:** you were corrected on an approach, a rule refinement landed, a theoretical framing was articulated, an enthusiastic adoption was walked back → file name `dialogue-notes.md`
   - **Scanner class work:** new classes explored, applied, or retired; FP rates measured; false-positive filter tuning → file name `session-notes.md`
   - **Cross-validation findings:** cross-lens convergence, cross-agent agreement, retroactive validation of prior work → file name `session-notes.md`
   - **Multi-class corpus sweeps:** merges or splits applied across multiple classes or books; adversarial audit results → file name `session-notes.md`
   - **New theoretical framings or reframings:** like today's "v4 is methodology application, not hand editing" correction → file name `dialogue-notes.md` or `session-notes.md` as fits
   - **Any work whose reasoning the commit message can't fit in its 1000-character soft limit.** If your commit body is already 600+ characters and there's more you want to preserve, that's the signal to write session notes.

   **Heuristic: if the session produced something a future overseer session would want to read after it auto-loads LANDSCAPE-MAP and METHODOLOGY-TIMELINE, write the session notes.** The commit message is the pointer-summary; the session notes file is the reasoning archive. Both should exist for substantive work.

   **What the notes should contain** (regardless of which filename):
   - What you proposed, attempted, or discovered
   - Stan's pushback, refinements, or decisions
   - The reasoning chain (the *why* matters more than the *what* — the commit captures the *what*)
   - What was ultimately decided, applied, or retired
   - Any load-bearing phrases Stan used verbatim — they may become prospectus language and need to be preserved exactly
   - Cross-references to other workspace files (overseer-workspace briefings, sibling OVERSEER-DIRECTIONS updates, etc.) that this session affects or is affected by

   **The gap this rule is fixing:** on 2026-04-14, the BofM trench Claude ran a significant split-scanner inversion pass (Classes I/J/L + cross-lens convergence finding at Alma 19:2) with a thorough commit message but no session directory. That finding — Q8 empirical validation — is important enough that a future overseer session should find it by walking `private/sessions/` rather than grepping commit messages. Any substantive work deserves its own session directory.

2. **Update `private/OVERSEER-DIRECTIONS.md`** per its documentation protocol:
   - Transform any applied items from "Status: active" to "APPLIED [date] — commit [hash]" with a brief resolution note
   - Add any new findings to the "push FROM HERE" section for cross-project porting
   - Append a dated sync-log entry at the bottom summarizing: commit hashes, files touched, items closed, new items opened, anything surprising

3. **Send Stan a wrap-up report message** before committing. Something like: "Session wrap-up. Commits landing: [hashes]. Files touched: [list]. Items closed: [list]. New items opened: [list]. Dialogue notes written at [path] covering [topic]. Anything unsurprising elsewhere that the overseer should also know?" 4-8 lines. The goal is to give the overseer a one-message summary that captures everything important without requiring it to read the full diff.

4. **Then commit and stop.**

**Why this matters:** Stan's standing complaint about trench Claudes is that they forget to document, hit compaction, and lose progress. The wrap-up report is the single most important thing you do in a session — it's the handoff to the next session (same Claude or different Claude, doesn't matter). If you only have time for one thing at end-of-session, it's the wrap-up report. Commits can wait five minutes; a compacted context cannot be recovered.

### CONTEXT-AWARE SELF-DISCIPLINE — watch your own context usage

Compaction is your equivalent of Stan saying "wrap it up" — but unlike Stan's verbal signal, compaction is gradual and doesn't announce itself. The cost of hitting compaction mid-operation is real: aggregation steps get lost, reasoning chains get truncated, in-flight batch state evaporates. **Don't let it get down to "oh crap we just lost something beautiful."**

Apply these three thresholds to your own context meter and treat them as standing rules, not suggestions:

**At ~50% context remaining — informal checkpoint.** Don't stop working, but do these things cheaply:
- Save any in-flight batch state to a file (scanner output partial results, audit aggregations, anything you'd lose if compacted)
- Commit any WIP code changes even if the work isn't complete — commits are cheap insurance, working memory is not
- Add a dated entry to `private/OVERSEER-DIRECTIONS.md` sync log capturing "session so far" in one paragraph. If compaction happens unexpectedly after 50%, you've got a recoverable mid-session checkpoint.

**At ~40% context remaining — defensive wrap-up, proactively.** This matches the overseer's own threshold. Treat the 40% mark as equivalent to Stan saying "let's wrap it up for now," even if he hasn't said it. Execute the full WRAP-UP REPORT protocol above (dialogue-notes if applicable, OVERSEER-DIRECTIONS update, wrap-up message, commits). Don't start new major operations after this point — only finish what's already in progress. **Tell Stan you've hit 40% and are wrapping up** so he can decide whether to continue in a fresh session or stop for the night.

**At ~30% context remaining — hard stop.** If you're still working past 30%, you've already taken on too much risk. At this threshold: finish ONLY the wrap-up. Don't continue substantive work. Don't start any new operation even if it seems small. The runway between 30% and auto-compact is your margin for error — preserve it. Every minute past 30% is a minute closer to losing the wrap-up itself.

**Why these thresholds are conservative for trench Claudes:** execution work (corpus-wide scans, adversarial audits, merge applications, file reorganizations, stylometry runs) has more in-flight state than pure synthesis. A single compaction during an aggregation step can lose hours of work if the intermediate results only exist in working memory. The cost of triggering a checkpoint too early is low (you write some files and continue); the cost of triggering too late is "oh crap we just lost something beautiful" — Stan's phrasing, and the thing these thresholds are designed to prevent.

**When in doubt, write it down.** Files survive compaction; working memory does not. This is the same discipline the overseer applies to itself.

### Why BOTH bookends + context discipline matter

Check-in without wrap-up = you start oriented but leave nothing for the next session.
Wrap-up without check-in = you document cleanly but start from "what Stan just said" instead of "the full accumulated state."
Bookends without context discipline = you're great at planned wrap-ups but lose sessions when compaction sneaks up.
**All three together = the overseer has full and robust visibility, and compaction never costs you beautiful work.** Stan gets to work at the speed of direction-giving, not the speed of context-watching-and-rescue.

See `private/OVERSEER-DIRECTIONS.md` documentation protocol for additional details, including what counts as a "substantive methodology dialogue" worth capturing.

---

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
- Modify a canonical v2 file directly
- Alter punctuation (punctuation belongs to the canonical LDS text)
- Add, remove, or change words
- Apply changes without Stan's explicit approval

**ALWAYS:**
- Work on a copy: `cp data/text-files/v2-mine/FILE.txt /tmp/FILE-working.txt`
- Present proposed changes for review before touching any canonical file
- Save the original before any new upload could overwrite it
- Make line-break changes only — the only editorial tool is where lines break

---

## Sense-Line Editorial Methodology

This is the intellectual heart of the project. The full methodology reference is pointed to from `private/OVERSEER-DIRECTIONS.md` (local only). Key principles:

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

### Settled Rules

1. **Wayyehi rule:** "And it came to pass that" stays on one line — never break it mid-phrase
2. **Expedient that:** "It is expedient that" is a fixed idiom — don't break at "that"
3. **Rhetorical address formulas:** "And now, O king," stays as one unit
4. **Circumstantial clause pairing:** paired phrases describing the same condition stay together
5. **Equivalence restatement:** when "or" introduces a restatement, keep it with the restated material
6. **Causal clauses break:** "because" introduces a new line
7. **Purpose clauses break:** "that they might / that ye may" introduces a new line
8. **Framing devices attach:** "For behold," "Wherefore," "And now" attach to what they introduce — don't orphan the frame from its content
9. **Never end a line on a conjunction:** "and," "or," "but," "nor" dangling at line end is always wrong — move the conjunction to lead the next line
10. **Never split verb from direct object** on short phrases
11. **Never end a line on an article** (the, a, an)
12. **Never split auxiliary from main verb** ("did / slay" → merge to "did slay")
13. **Parallel structures stack vertically** — mirror parallel elements across lines to show rhetorical pattern
14. **Qualifying phrases that escalate** earn their own line; qualifying phrases that merely restrict tend to stay with what they qualify
15. **Vocative units are indivisible** — "O Lord God," and "O Lord our God," stay whole; never split mid-address
16. **"Dangling that" after AICTP** — break BEFORE "that" so it leads the next line: "And it shall come to pass" / "that [content]"
17. **"Caused that" complement integrity** — "caused" requires its complement clause; same as "began to" rule
18. **Fixed idiom integrity** — "put to death," "from time to time," "prevailed upon" are indivisible units
19. **Cataphoric "that" clauses break; anaphoric merge** — a "that" clause earns its own line only if it introduces new content (cataphoric). If it's entirely backward-pointing ("this," "the case," "the same"), it merges (anaphoric — no new semantic content to carry a line)

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
- Mechanical passes: find dangling conjunctions, long lines, orphan fragments
- Propose changes in clear before/after format
- Apply approved changes to working copies only
- Run build pipeline after approved changes
- Never touch canonical files without explicit approval
- Never alter punctuation, words, or structure — line breaks only
- **Colometry review partner:** on request, agree/challenge/suggest on Stan's edits using the settled rules and category framework
- **Handoff maintenance:** after any session where decisions are made, principles are refined, or new patterns identified, update the relevant handoff file (append dated block, never overwrite history)
- **"Do an update" means:** update ALL relevant handoffs, memory files, research files, and any other documentation so that a fresh session can resume with full context

---

## Connected Resources

### Academic Vault
Stan's academic Obsidian vault at `C:\vaults-nano\my_brain\` contains his OTC dissertation materials, bibliographic records (332 sources), scholar hub notes (~230), and 838 zettels. The vault's `CLAUDE.md` has full orientation. Read it for context when work touches Hebrew poetry, oral tradition, stylometry, or the FEF paper.

The BOM Reader `research/` folder is symlinked into the vault at `10_Projects/BOM-Reader-Research/`. Files live in the vault; the repo path is a symlink. The folder is gitignored.

### Two-AI Workflow
Claude Code (this tool) handles file access, commits, mechanical analysis. Claude.ai chat handles brainstorming, design, paper strategy. Stan bridges between them. Handoff docs and research files are the shared ground truth — keep them current so either AI can spin up with full context.
