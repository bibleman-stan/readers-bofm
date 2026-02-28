# Book of Mormon Reader's Edition — Cowork Handoff

**Last updated:** 2026-02-28 (evening)
**Session:** Major rebuild integrating display settings, bug fixes, deep linking, and reformatter v8

---

## What This Project Is

A web-based reading app for the Book of Mormon designed for ESL readers, children, and newcomers. It presents the text in sense-line (cola) format — each line is a natural breath unit for read-aloud delivery. Archaic words can be toggled to modern equivalents. Hosted at bomreader.com via GitHub Pages.

**Repo:** `readers-bofm` (GitHub)
**Stack:** Vanilla HTML/CSS/JS, Python 3 build scripts, Google Fonts (Literata), dark theme default

---

## Architecture

### Key Files

| File | Purpose |
|------|---------|
| `index.html` | Main app shell — toolbar, tabs, settings, all JS, CSS |
| `build_book.py` | Converts sense-line `.txt` source files into HTML book fragments |
| `senseline_reformat_v7.py` | 18-pass automated sense-line reformatter (previous version) |
| `senseline_reformat_v8.py` | 19-pass reformatter — relaxed for CSS wrap-indent (current) |
| `booklist.txt` | Maps book IDs to source filenames |
| `books/*.html` | Generated HTML fragments, one per book (loaded via fetch) |
| `CNAME` | Domain config for bomreader.com |
| `display-settings-v5.html` | Design prototype for the settings panel (reference only, not deployed) |

### Source Text Files

Now organized in `text-files/` with three stages:

| Folder | Contents | Notes |
|--------|----------|-------|
| `text-files/v0-bofm-original/` | 2020 BofM base text (paragraph format) | 15 books, no sense-line breaks |
| `text-files/v1-skousen-breaks/` | Skousen sense-line formatting | Input to reformatter. ~42K total lines |
| `text-files/v2-mine/` | Stan's revised sense-lines (WIP) | ~45K lines. May not be fully in sync with deployed HTML |

The `booklist.txt` source filenames (e.g., `01-1_nephi-stan-v1.txt`) still point to old paths. The v1-skousen-breaks files are the reformatter input. 1 Nephi v2 is heavily hand-edited (+25% lines); other books' v2 files are ~5–8% growth (mostly reformatter output from v7).

All 15 book HTML fragments in `books/` are already built and current.

### How Content Gets Built

1. Sense-line source file (`.txt`) with verse markers and line breaks
2. `senseline_reformat_v8.py` applies 19 mechanical passes (optional — for new/revised books)
3. `build_book.py` applies archaic word swaps, wraps punctuation, generates HTML
4. Output goes to `books/BOOKID.html` as a fragment (`<div id="book-BOOKID" class="book-content">`)
5. `index.html` loads fragments via `fetch('books/' + bookId + '.html')`

---

## What Was Done in This Session (2026-02-28)

### 1. Moved Repo
From `C:\vaults-nano\gospel\11-Readers_BofM\readers-bofm` to `C:\Users\bibleman\repos\readers-bofm` (Cowork requires folders inside home directory).

### 2. build_book.py — CSS Class Output
Changed `gen_verse()` and `gen_chapter()` to output semantic CSS classes instead of inline styles:
- `<div class="verse">` instead of `<div style="margin-bottom: 20px;">`
- `<span class="verse-num">` instead of inline font-size/color
- `<span class="line">` instead of `display: block; margin-left: 0`
- `<div class="chapter-title">`, `.chapter-nav`, `.chapter-nav-link`, `.chapter-nav-disabled`

### 3. All 15 Book HTML Fragments — Converted
Used sed to convert all existing `books/*.html` from inline styles to the same CSS classes. No content changes — just style attribute → class attribute.

### 4. index.html — Major Rebuild
**New CSS variable system:**
```css
:root {
  --line-height: 2.35;
  --wrap-indent: 0.75em;
  --verse-gap: 2px;
  --verse-num-display: none;
  --punct-opacity: 0;
  --font-size: 17px;
  --letter-spacing: 0em;
  --word-spacing: 0em;
  --content-padding: 18px;
}
```

**New features:**
- **Gear icon** in toolbar opens a settings panel with:
  - Continuous flow toggle (hides verse numbers, squishes verse gap)
  - Hide punctuation toggle (opacity: 0, no reflow)
  - Wrap indent toggle (hanging indent for wrapped lines on mobile)
  - Text size: Small / Medium / Large
  - Text density: Compact / Normal / Spacious
  - Line spacing: Tight / Normal / Airy
- **Per-tab default profiles:**
  - Read tab: continuous flow ON, punct hidden, wrap indent ON, airy spacing (immersive)
  - Study tab: everything visible, normal spacing (analytical)
  - Each tab remembers its own overrides independently
- **Hash-based deep linking:** URLs like `bomreader.com/#enos-1` navigate to book/chapter. `showChapter()` sets the hash. `hashchange` listener enables back/forward.
- **Swap styling change:** Removed bold from `.aid-active .swap`. Now just green color + dotted underline (no bold).
- **Toggle bug fix:** On `DOMContentLoaded`, forces all `.swap` spans to `data-orig` text and sets `aidOn = false`.

**Preserved all existing functionality:**
- Deity/Father/Spirit highlighting layers
- Reading aid toggle (archaic ↔ modern words)
- Dynamic book loading via fetch
- Chapter grid navigation
- Dark/light mode (moved into settings panel)
- Layers panel (Study tab)
- Comment system, editorial layers, intertextual quotations, covenant markers
- All 15 book intro/background sections
- Back to top button

---

## Design Decisions to Know

- **Sense-line breaks are editorial, not mechanical.** The reformatter handles common patterns, but Stan hand-edits the output. Break for the ear, not the eye.
- **No indentation.** All lines flush left. The wrap indent is the ONLY indent and it's CSS-only (no markup change).
- **Longest-first lexicon matching** in `build_book.py` prevents nested swaps (e.g., "thou art" matched before "thou").
- **Punctuation is wrapped** in `<span class="punct">` so it can be hidden via CSS opacity without reflowing text.
- **The swap system uses `data-orig` and `data-mod` attributes.** JS toggles `.textContent` between them.
- **Book content is modular.** Each book is a self-contained HTML fragment that gets injected into the DOM.

---

## Bug Fixes Applied After Initial Rebuild (2026-02-28)

### Chapter revert bug
**Symptom:** Select a book, pick a chapter (e.g., 2 Nephi 9), start scrolling, and it snaps back to chapter 1.
**Root cause:** `showChapter()` sets `window.location.hash`, which fires `hashchange` asynchronously. The original boolean flag guard (`hashUpdating = true/false`) reset before the async event fired, so `handleHash()` always ran → called `switchBook()` → which called `showChapter(bookId, 1)` → chapter 1.
**Fix:** Replaced the flag with `lastHashWeSet` — a string that stores the hash we just set. `handleHash()` compares the current hash to this value and skips if they match. No race condition possible.

### Scroll fighting / layout stutter on load
**Symptom:** Brief lag when choosing a new book; scroll "fights" for a moment before working; toolbar doesn't stick immediately.
**Root cause:** CSS transitions on `.verse` (`margin-bottom 0.3s`) and `.punct` (`opacity 0.3s`) fired on every CSS variable change, including initial page load and book switches — hundreds of elements animating simultaneously. Also `scrollTo({behavior: 'smooth'})` competed with layout recalculation.
**Fix:** Moved transitions behind a `.transitions-enabled` class on `<body>` that gets added 300ms after `DOMContentLoaded`. Changed `scrollTo` to instant (removed `behavior: 'smooth'`). Transitions still animate smoothly when toggling settings via the gear panel.

---

## Reformatter v8 (2026-02-28 evening session)

### Why v8
The CSS wrap-indent feature (`--wrap-indent: 0.75em`) means lines in the 70–90 char range are no longer a problem on mobile — they wrap cleanly with a hanging indent. So the reformatter was doing a lot of splitting purely to avoid wrapping, creating unnecessary fragmentation. v8 relaxes the cosmetic thresholds while keeping all semantic passes intact.

### Threshold Changes from v7 → v8
| Pass | What it does | v7 | v8 |
|------|-------------|----|----|
| M6 | according-to split | >58 | >72 |
| M8 | ", and [pronoun]" split | 45–70 | 60–90 |
| M9 | subject-predicate at modal | >70 | >85 |
| M10 | long-line pattern split | >70 | >90 |
| M10 | no-comma prep patterns | >75 | >100 |
| M15 | passive+prep split | ≥50 | ≥65 |

### New Pass: M18 List-Stacking
Automatically stacks parallel triads vertically when 3+ ", and X" items appear in a line. E.g.:
```
and their skill was in the bow, and in the cimeter, and the ax.
```
becomes:
```
and their skill was in the bow,
and in the cimeter,
and the ax.
```
This codifies what Stan was doing by hand in v2 edits.

### Enos Test Run Results (v8 on v1-skousen input)
- 146 lines, mean 40.5, 0 lines over 90, 6 lines in 70–90 range (left alone)
- List-stacking correctly fired on 3 verses (1:20, 1:21, 1:23)
- Only 6 remaining differences from Stan's v2 hand edits (see below)

### Known v8 Differences from Stan's v2 (editorial, not bugs)
1. **M0 em-dash attachment:** v8 detaches trailing words from dashes (`man-- / for`), Stan's v2 keeps them glued (`man--for / he`). May want to revisit M0 behavior.
2. **M12 in+gerund over-splitting:** v8 still splits "in keeping" at 53 chars. Could add minimum line length to M12.
3. **M8 over-splitting short lines:** v8 splits "forgiven thee, / and thou shalt be blessed" at 52 chars (under new 60-char floor but M8 didn't trigger — this was from Skousen source). The Skousen source already had this split.
4. **Under-splitting 70–90 range:** v8 leaves "bring down with sorrow upon their own heads" (76 chars) and "should fall into transgression" (82 chars) unsplit. Stan's v2 broke these. These are semantic preference, not bugs.
5. **AICTP "that" placement:** v7 changed "that" to go with content line; Stan's v2 was from v1 which kept "that" with "And it came to pass that". v8 inherits v7's behavior.

---

## Known Future Work

- **Study tab layers** are partially implemented (deity highlighting works, intertextual quotations work for marked books). Isaiah parallels and covenant promises are stubbed.
- **Reformatter v8 refinement** — consider adjusting M0 (em-dash word attachment) and M12 (in+gerund minimum length) based on Enos test results.
- **Re-run v8 on all 15 books** to generate updated v2 files, then rebuild HTML fragments.
- **localStorage persistence** for reader settings is mentioned in the design but not yet implemented.
- **The `display-settings-v5.html` prototype** can be deleted from the repo when no longer needed as reference.
- **`booklist.txt` paths** need updating to point to `text-files/v1-skousen-breaks/` or wherever the canonical sources land.

---

## How to Test Locally

```bash
cd C:\Users\bibleman\repos\readers-bofm
python -m http.server 8000
```
Then open `http://localhost:8000` in a browser. The `file://` protocol won't work because books load via `fetch()`.

---

## Lexicon Quick Reference

The swap lexicon in `build_book.py` has ~193 compound + simple swaps plus ~260 -eth verb forms. Key context-sensitive entries:
- "exceedingly" → "very" (default) or "greatly" (with emotion/intensity verbs)
- "save" → "unless" (when not followed by pronouns/objects)
- "meet" → "fitting" (only after "is/was/be")
- "mine" → "my" (only when not preceded by "a/the")
- "account" → "record" (only when not followed by "of/for")
