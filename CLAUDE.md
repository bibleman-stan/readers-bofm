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
| `handoffs/10-colometry.md` | Sense-line theory and editorial methodology — READ THIS CAREFULLY |

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

This is the intellectual heart of the project. Read `docs/10-colometry.md` in full. Key principles:

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
  --verse-num-display: none;
  --punct-opacity: 0;
  --font-size: 17px;
}
```

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
