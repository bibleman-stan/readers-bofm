# Book of Mormon Reader's Edition — Cowork Handoff

**Last updated:** 2026-03-01
**Sessions covered:** Feb 28 (initial build) → Feb 28 evening (v8 reformatter) → Mar 1 (layers, pericope, polish, About page)

---

## What This Project Is

A web-based reading app for the Book of Mormon designed for ESL readers, children, and newcomers. It presents the text in sense-line (cola) format — each line is a natural breath unit for read-aloud delivery. Archaic words can be toggled to modern equivalents. Multiple study layers (deity references, biblical quotations, geography, etc.) can be overlaid. Hosted at **bomreader.com** via GitHub Pages.

**Repo:** `readers-bofm` (GitHub)
**Stack:** Vanilla HTML/CSS/JS single-page app, Python 3 build scripts, Google Fonts (Literata), dark theme default
**Local dev:** `python -m http.server 8000` (file:// won't work because books load via fetch)

---

## Architecture

### Key Files

| File | Purpose | Lines |
|------|---------|-------|
| `index.html` | Main app shell — all CSS, HTML, JS in one file | ~2533 |
| `build_book.py` | Converts sense-line `.txt` sources into HTML book fragments | ~962 |
| `books/*.html` | Generated HTML fragments, one per book (15 total, loaded via fetch) | varies |
| `data/pericope_index.json` | Master section headers index (648 entries across 15 books) | ~66KB |
| `data/hardy_intertext.json` | Biblical reference data for quotation/allusion layers | ~226KB |
| `data/hardy_phrase_index.json` | Phrase-level match data for highlighting | ~202KB |
| `data/kjv_diff_index.json` | KJV parallel passage diff data | ~402KB |
| `data/geo_index.json` | Geographic reference data | ~93KB |
| `data/pericope_*.json` | Individual pericope files per book (15 files, source for master) | varies |
| `senseline_reformat_v8.py` | 19-pass automated sense-line reformatter (current) | ~32K |
| `booklist.txt` | Maps book IDs → source filenames for `build_book.py --all` | |
| `CNAME` | Domain config for bomreader.com | |

### Source Text Files

In `text-files/` with three stages:

| Folder | Contents |
|--------|----------|
| `text-files/v0-bofm-original/` | 2020 BofM base text (paragraph format), 15 books |
| `text-files/v1-skousen-breaks/` | Skousen sense-line formatting (reformatter input) |
| `text-files/v2-mine/` | Stan's revised sense-lines (WIP, may not be fully in sync) |

### How Content Gets Built

1. Sense-line source file (`.txt`) with verse markers and line breaks
2. `senseline_reformat_v8.py` applies 19 mechanical passes (optional — for new/revised books)
3. `build_book.py` applies archaic word swaps, injects intertext/geo/pericope layers, wraps punctuation, generates HTML
4. Output goes to `books/BOOKID.html` as a fragment (`<div id="book-BOOKID" class="book-content">`)
5. `index.html` loads fragments via `fetch('books/' + bookId + '.html')`

**Rebuild all books:**
```bash
python3 build_book.py --all booklist.txt --out books/
```

---

## Current UI Structure

### Header
```html
<a href="#" onclick="showAboutPage(); return false;">
  <h1>The Book of Mormon <span class="subtitle">Reading Edition</span></h1>
</a>
```
- Title is one line: "The Book of Mormon" in full size, "Reading Edition" on a second line in smaller (0.48em) italic muted text
- Clicking opens the About page (full-page feature guide in the content area)
- Tight spacing: `margin-bottom: 0.4em`, subtitle has `margin-top: 0.15em`

### Floating Toolbar (`#reading-toolbar`)
Sticky toolbar with multiple sub-components:

1. **Collapsed summary bar** (`#collapsed-summary`) — shown when toolbar collapses on scroll, displays current book + chapter
2. **Book grid** (`#book-grid`) — 15 book abbreviation buttons + "About [Book Name]" pill
3. **Settings panel** (`#settings-panel`) — typography controls (uses `.visible` class, not display)
4. **Navigation panel** (`#nav-panel`) — chapter number grid (shown on book tap)
5. **Controls row** (`.controls-row`) — pill buttons: Aid · Verses · Sections · Layers · ⚙
6. **Layers panel** (`#layers-panel`) — checkbox toggles grouped by category
7. **Background panel** (`#background-panel`) — book introductions with expandable `<details>` sections

### Content Area (`#scripture-content`)
Contains:
- `#about-page` — full feature guide (hidden by default, shown by clicking header)
- `#book-content-container` — where book HTML fragments get injected

### Pill Button Active States

| Button | ID | Active Class | Color |
|--------|-----|-------------|-------|
| Aid | `aid-pill` | `active-aid` | `#27ae60` (green) |
| Verses | `verses-pill` | `active-verses` | `#c9a368` (gold) |
| Sections | `sections-pill` | `active-sections` | `#9ab` (blue-gray) |
| Layers | `layers-pill` | `active-layers` | `#7cb8e4` (blue) |
| About [Book] | `about-pill` | `active-bg` | `#ccc` |

### Layers Panel Groups

| Group | Layer | Checkbox ID | Color | Body Class |
|-------|-------|------------|-------|------------|
| Divine Voice | God's Presence | `deity-check` | `#c0392b` | `show-deity` |
| Divine Voice | The Holy Spirit | `spirit-check` | `#888` | `show-spirit` |
| Biblical Roots | Direct Quotations | `quotations-check` | `#7cb8e4` | `sources-quotations` |
| Biblical Roots | Echoes & Allusions | `allusions-check` | `#8aabbf` | `sources-allusions` |
| Biblical Roots | KJV Parallels | `kjv-diff-check` | `#6ba3d6` | `show-kjv-diff` |
| Setting | Geography | `geo-check` | `#b5854a` | `show-geo` |

### Settings Panel Defaults

| Setting | Default | CSS Variable |
|---------|---------|-------------|
| Continuous flow | ON (checked) | `--verse-num-display: none; --verse-gap: 2px` |
| Hide punctuation | ON (checked) | `--punct-opacity: 0` |
| Wrap indent | ON (checked) | `--wrap-indent: 0.75em` |
| Text size | Medium | `--font-size: 17px` |
| Text density | Normal | `--letter-spacing: 0; --word-spacing: 0` |
| Line spacing | Airy | `--line-height: 2.35` |
| Light mode | OFF | `body.light-mode` class |

---

## CSS Variable System

```css
:root {
  --line-height: 2.35;      /* tight: 1.55, normal: 1.75, airy: 2.35 */
  --wrap-indent: 0.75em;    /* 0.75em when on, 0em when off */
  --verse-gap: 2px;         /* 2px in flow mode, 12px in verse mode */
  --verse-num-display: none; /* none to hide, inline to show */
  --punct-opacity: 0;       /* 0 to hide, 1 to show */
  --font-size: 17px;        /* 15px small, 17px medium, 20px large */
  --letter-spacing: 0em;    /* compact: -0.015em, normal: 0, spacious: 0.02em */
  --word-spacing: 0em;      /* compact: -0.03em, normal: 0, spacious: 0.06em */
  --content-padding: 18px;  /* compact: 10px, normal: 18px, spacious: 26px */
}
```

---

## Key Body Classes

| Class | Purpose |
|-------|---------|
| `aid-active` | Modern word swaps shown |
| `hide-punct` | Punctuation hidden via opacity |
| `show-sections` | Pericope section headers visible |
| `show-deity` | Deity/Christ highlighting active |
| `show-spirit` | Holy Spirit highlighting active |
| `sources-quotations` | Biblical quotation layer active |
| `sources-allusions` | Biblical allusion layer active |
| `show-kjv-diff` | KJV parallel layer active |
| `show-geo` | Geography layer active |
| `light-mode` | Light theme active |
| `toolbar-collapsed` | Toolbar hidden on scroll-down |
| `transitions-enabled` | CSS transitions active (added 300ms after load) |

---

## JavaScript Architecture

### State Variables
```javascript
var aidOn = false;           // Reading aid toggle
var versesOn = false;        // Verse numbers toggle
var deityLayerOn = false;    // Deity highlighting
var spiritLayerOn = false;   // Spirit highlighting
var currentBook = '1nephi';  // Current book ID
var currentChapterMap = {};  // { bookId: chapterNum }
var loadedBooks = {};        // { bookId: true } — tracks fetched books
var pendingChapter = null;   // Chapter selected before async book load completes
var lastHashWeSet = '';      // Prevents circular hashchange handling
```

### Navigation Flow
1. User taps book button → `onBookBtnClick(bookId)`
2. If single-chapter book → `switchBook(bookId)` directly
3. If same book → toggle chapter grid
4. If new book → `switchBook(bookId)` → `loadBook()` (async fetch) → callback
5. Callback checks `pendingChapter` (if user clicked chapter during load)
6. `showChapter(bookId, chNum)` → hides about page, shows chapter div, updates hash, scrolls to top

### Hash Routing
Format: `#bookId` or `#bookId-chapterNumber` (e.g., `#alma-45`)
Pattern: `/^([a-z0-9-]+?)(?:-(\d+))?$/`
- Set on `showChapter()`, listened via `hashchange`
- `lastHashWeSet` prevents infinite loops

### Scroll Handler
- Toolbar collapses on scroll-down past 80px (20px dead zone)
- Expands on scroll-up
- **Freezes while any panel is open** (layers, nav, background, settings)
- 400ms cooldown after state changes
- Back-to-top button appears after 600px

### Scripture Content Click Handler
- If any panel is open → `closeAllPanels()` (click-to-dismiss)
- If no panel open and scrolled past 80px → collapse toolbar

### Swipe Navigation
- Touch-based: 60px min horizontal, <500ms, <80px vertical drift
- Left swipe = next chapter, Right swipe = previous chapter
- Disabled on toolbar elements, inputs, buttons

### About Page
- `showAboutPage()` — hides book content, shows feature guide, scrolls to top
- `hideAboutPage()` — restores book content
- Auto-hides when any chapter is navigated to (`showChapter()` calls `hideAboutPage()`)
- Contains feature cards for all pill buttons and all layers with color swatches

### Panel Management
```javascript
function closeAllPanels() {
  // Closes: nav-panel, layers-panel, background-panel
  // Removes active classes from: layers-pill, about-pill, settings-panel, gear-btn
}
```

### Layer Functions
- `selectAllLayers()` / `clearAllLayers()` — check/uncheck all 6 layer checkboxes
- `updateLayersPill()` — toggles `active-layers` class on pill if any layer is checked
- Sections toggle is **independent** of the layers panel (it's a top-level pill)

---

## build_book.py — Build Pipeline

### Swap System (Longest-First Sorting)

Processing order in `apply_swaps()`:
1. **AICTP_SWAPS** (32 entries) — "And it came to pass" variants, literal string replacement
2. **COMPOUND_SWAPS** (27 pairs) — Multi-word phrases like "save it be" → "unless"
3. **SIMPLE_SWAPS** (151 pairs) — Single-word archaic → modern
4. **ETH_SWAPS** (167 known + fallback rule) — Verbs ending in -eth
5. **DID verb conjugation** — "did VERB" → past tense
6. **THOU-EST conjugation** — "Thou verb_est" → "You base"

All swaps output: `<span class="swap" data-orig="archaic" data-mod="modern">archaic</span>`

### Context-Sensitive Swaps
- `"exceedingly"` → `"very"` (default) or `"greatly"` (with emotion/intensity verbs — ~30 specific combinations)
- `"save"` → `"unless"` (when not followed by pronouns/objects)
- `"meet"` → `"fitting"` (only after is/was/be)
- `"mine"` → `"my"` (only when not preceded by a/the)
- `"account"` → `"record"` (only when not followed by of/for)

### Notable Compound Swaps (added in Mar 1 session)
```python
("things of naught", "worthless things")
("thing of naught", "worthless thing")
("set at naught", "disregarded")
("setteth at naught", "disregards")
("asunder", "apart")
("apparel", "clothing")
```

### Processing Pipeline Per Line
```python
def process_line(line, swap_list):
    return wrap_punctuation(fix_participles(apply_swaps(line, swap_list)))
```

### fix_participles() — Post-Swap Correction
```python
def fix_participles(text):
    for wrong, right in [('saw','seen'),('spoke','spoken'),('broke','broken')]:
        text = re.sub(r'(\bhad\b[^;.]{0,30}?)data-mod="'+re.escape(wrong)+'"', ...)
        text = re.sub(r'(\bhave\b[^;.]{0,30}?)data-mod="'+re.escape(wrong)+'"', ...)
    return text
```
- 30-char window (tightened from 60 to prevent cross-clause errors)
- `[^;.]` excludes clause boundaries

### Data Loading (`load_intertext()`)
Loads 5 JSON files into globals:
1. `hardy_intertext.json` → `_INTERTEXT_INDEX`
2. `hardy_phrase_index.json` → `_PHRASE_INDEX`
3. `kjv_diff_index.json` → `_KJV_DIFF_INDEX`
4. `geo_index.json` → `_GEO_INDEX`
5. `pericope_index.json` → `_PERICOPE_INDEX`

All graceful — missing files print warning but don't break.

### Pericope Integration in gen_chapter()
```python
for v in ch_verses:
    pericope_title = get_pericope(bid, v['chapter'], v['verse'])
    if pericope_title:
        p.append(f'<div class="pericope-header">{pericope_title}</div>')
    p.append(gen_verse(v, swap_list, book_id=bid))
```

### Per-Verse Enrichment in gen_verse()
Each verse goes through:
1. Apply word swaps to all lines
2. Inject intertext references (quotations/allusions) with phrase-level highlighting
3. Apply geography highlighting and categorization
4. Add KJV diff parallel passages with strikethrough/bold markup
5. Wrap with verse number and line spans

---

## Pericope (Section Headers) System

### Data Structure
`pericope_index.json` keyed: `book_id → chapter (string) → array of {verse: int, title: string}`

Example:
```json
{
  "1nephi": {
    "1": [
      {"verse": 1, "title": "Lehi's World and Family"},
      {"verse": 5, "title": "A Father's Prayer, A Prophet's Call"}
    ]
  }
}
```

**648 total sections** across 15 books. Individual source files: `data/pericope_*.json`

### CSS
```css
.pericope-header {
  display: none;
  font-size: 0.88em;
  font-weight: 600;
  color: #9ab;
  letter-spacing: 0.03em;
  margin: 1.4em 0 0.4em 0;
  padding: 0 0 4px 0;
  border-bottom: 1px solid rgba(154, 170, 187, 0.2);
  font-style: italic;
}
body.show-sections .pericope-header { display: block; }
body.light-mode .pericope-header { color: #5a7a8a; border-bottom-color: rgba(90, 106, 122, 0.2); }
```

---

## About Page

Full-page feature guide, displayed in `#scripture-content` when user clicks the header title. The toolbar stays fully functional (pinned) so users can navigate while the About page is visible.

**Content sections:**
1. About This Edition — what sense-line formatting is, who it's for
2. The Toolbar Buttons — feature cards for Aid, Verses, Sections, Layers, Settings (with pill-demo styled elements matching real UI)
3. The Layers — feature cards for all 6 layers with color swatches
4. Other Features — covenant italics, book intros, swipe navigation
5. Design Philosophy

**Entry/exit:**
- `showAboutPage()` — hides `#book-content-container`, shows `#about-page`, scrolls to top
- `hideAboutPage()` — reverses. Called automatically by `showChapter()`
- "← Back to reading" link at bottom

---

## Light Mode

Toggle: `body.light-mode` class. All light-mode overrides use `!important`.

Key color mapping:
| Element | Dark | Light |
|---------|------|-------|
| Background | `#1a1a1a` | `#f5f0e8` |
| Text | `#d4d0c8` | `#3a3630` |
| Toolbar bg | `#2a2a2a` | `#e8e4dc` |
| Book btn | `#3a3a3a` | `#e8eaef` |
| Active book btn | `#4a6070` | `#d0dae8` |
| Links | `#7cafc2` | `#4a7a9e` |

Pattern: target elements with `body.light-mode .element` or `body.light-mode span[style*="color: #VALUE"]` for inline styles.

---

## Bug Fixes Applied

### Chapter revert bug (Feb 28)
**Symptom:** Chapter snaps back to 1 on scroll.
**Cause:** `hashchange` race condition with boolean flag.
**Fix:** Replaced flag with `lastHashWeSet` string comparison.

### Scroll stutter on load (Feb 28)
**Symptom:** Layout fights on book switch.
**Cause:** CSS transitions firing on initial load (hundreds of elements).
**Fix:** `.transitions-enabled` class added 300ms after DOMContentLoaded.

### Navigation race condition — "2 Ne → 33 goes to 1 Ne 1" (Mar 1)
**Symptom:** Tapping a chapter before async book load completes uses wrong book/chapter.
**Cause:** `buildChapterGrid()` creates buttons immediately but `loadBook()` is async. Callback overwrites with ch 1.
**Fix:** `pendingChapter` variable stores user's chapter choice; callback checks it.

### "he spoken to you" in 1 Ne 17:45 (Mar 1)
**Symptom:** `fix_participles()` incorrectly changed "spoke" → "spoken" across a clause boundary.
**Cause:** 60-char regex window crossed semicolons. "ye have heard" matched "have" from wrong clause.
**Fix:** Tightened to 30-char window with `[^;.]` character class.

### Scroll dismissing open panels (Mar 1)
**Symptom:** Scrolling while layers panel is open closes it.
**Fix:** Scroll handler checks `anyPanelOpen` and returns early without collapsing. Click handler on `#scripture-content` closes panels on tap-outside.

---

## Reformatter v8 Details

### Threshold Changes from v7 → v8
| Pass | What | v7 | v8 |
|------|------|----|----|
| M6 | according-to split | >58 | >72 |
| M8 | ", and [pronoun]" | 45–70 | 60–90 |
| M9 | subject-predicate at modal | >70 | >85 |
| M10 | long-line pattern split | >70 | >90 |
| M10 | no-comma prep patterns | >75 | >100 |
| M15 | passive+prep split | ≥50 | ≥65 |

### New Pass: M18 List-Stacking
Automatically stacks parallel triads (3+ ", and X" items) vertically.

### Known v8 Differences from Stan's v2
1. M0 em-dash word attachment behavior differs
2. M12 in+gerund over-splitting at 53 chars
3. Some Skousen source splits below v8 thresholds
4. 70–90 char range left unsplit (semantic preference)

---

## Design Decisions

- **Sense-line breaks are editorial, not mechanical.** The reformatter handles common patterns but Stan hand-edits.
- **No indentation.** All lines flush left. Wrap indent is CSS-only.
- **Longest-first swap matching** prevents nested swaps.
- **Punctuation wrapped in `<span class="punct">`** for CSS opacity hiding without reflow.
- **Swap system uses `data-orig` / `data-mod` attributes.** JS toggles textContent. Aid toggle caches `data-orig-html` to preserve punct spans.
- **Book content is modular.** Each book is a self-contained HTML fragment injected into DOM.
- **Sections (pericope) are build-time injected** as `<div class="pericope-header">` — not runtime JS.
- **Layers panel groups**: Divine Voice, Biblical Roots, Setting. Sections is a top-level pill, not in layers.
- **About page replaces content area** (not a dropdown), toolbar stays functional for navigation.

---

## Pending / Known Issues

1. **Navigation bug (2 Ne → 33)** — `pendingChapter` fix is in code but may need verification after deploy. User reported it persisting; could have been a push timing issue.
2. **Scroll/panel dismiss** — Fix is in code (scroll handler freezes while panels open, click-outside dismisses). Needs verification after push.
3. **localStorage persistence** — Not implemented. Settings reset on page load.
4. **`booklist.txt` paths** — Still point to old filenames; need updating to match `text-files/` structure.
5. **`display-settings-v5.html`** — Design prototype, can be deleted when no longer needed.
6. **Reformatter v8 refinement** — M0 em-dash and M12 in+gerund thresholds could be adjusted.

---

## Book Metadata Quick Reference

| ID | Abbreviation | Name | Chapters |
|----|-------------|------|----------|
| `1nephi` | 1 Ne | 1 Nephi | 22 |
| `2nephi` | 2 Ne | 2 Nephi | 33 |
| `jacob` | Jac | Jacob | 7 |
| `enos` | Eno | Enos | 1 |
| `jarom` | Jar | Jarom | 1 |
| `omni` | Omn | Omni | 1 |
| `words-of-mormon` | WoM | Words of Mormon | 1 |
| `mosiah` | Mos | Mosiah | 29 |
| `alma` | Alm | Alma | 63 |
| `helaman` | Hel | Helaman | 16 |
| `3nephi` | 3 Ne | 3 Nephi | 30 |
| `4nephi` | 4 Ne | 4 Nephi | 1 |
| `mormon` | Morm | Mormon | 9 |
| `ether` | Eth | Ether | 15 |
| `moroni` | Moro | Moroni | 10 |
