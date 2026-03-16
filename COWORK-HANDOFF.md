# Book of Mormon Reader's Edition — Cowork Handoff

**Last updated:** 2026-03-16
**Sessions covered:** Feb 28 (initial build) → Feb 28 evening (v8 reformatter) → Mar 1 (layers, pericope, polish, About page) → Mar 1 evening (Isaiah pericopes, two-tier headers, Hebrew Poetry layer, UI fixes) → Mar 2 (nav bug fixes, Parry-style CSS, KJV diff fix, reference cleanup) → Mar 2 evening (Read Along extraction, archaic word swaps expansion) → Mar 16 (major UI redesign: thin persistent bar, landing page, bottom sheet)

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
| `index.html` | Main app shell — all CSS, HTML, JS in one file | ~4220 |
| `readalong.html` | **Standalone beta** — Read Along mic/speech tool (extracted from index.html Mar 2) | ~420 |
| `archive-studying-edition/` | Preserved old toolbar, text-mode toggle, Parry parallel UI code for future Studying Edition | — |
| `build_book.py` | Converts sense-line `.txt` sources into HTML book fragments | ~1090 |
| `build_parallel_index.py` | Parses Parry parallelism data into JSON index (lite filter) | ~300 |
| `books/*.html` | Generated HTML fragments, one per book (15 total, loaded via fetch) | varies |
| `data/pericope_index.json` | Master section headers index (710 entries across 15 books) | ~75KB |
| `data/hardy_intertext.json` | Biblical reference data for quotation/allusion layers | ~226KB |
| `data/hardy_phrase_index.json` | Phrase-level match data for highlighting | ~202KB |
| `data/kjv_diff_index.json` | KJV parallel passage diff data | ~402KB |
| `data/geo_index.json` | Geographic reference data | ~93KB |
| `data/parallel_index.json` | Hebrew Poetry parallel structures (619 lite structures) | varies |
| `data/parry-parallels-full.txt` | Donald Parry's full parallelism dataset (14,544 lines) | ~590KB |
| `data/pericope_*.json` | Individual pericope files per book (15 files, source for master) | varies |
| `data/spa/*.json` | Spanish LDS scripture library (entire canon, JSON verse format) | varies |
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

### Thin Persistent Top Bar (`.topbar`)
A 44px fixed bar at the top with backdrop blur:
- **Left side:** Book name + chapter (e.g., "1 Nephi · Chapter 1") — tap opens the full-screen book/chapter picker
- **On landing page:** Shows "bomreader.com" instead of book/chapter
- **Right side:** Search icon + Settings (hamburger) icon
- CSS custom properties for theming: `--bg`, `--accent`, `--text-dim`, `--text-faint`, `--border`, etc.

### Progress Line (`.progress-line`)
A 2px bar at the very top of the viewport showing scroll position (0–100%).

### Full-Screen Book/Chapter Picker (`.picker`)
Opens when tapping the book/chapter in the topbar:
- Vertical list of all 15 books
- Tap a book row to expand its chapter numbers
- Chapter numbers shown as small clickable pills
- Built dynamically from `bookMeta` object via `buildPicker()`

### Bottom Sheet (`.sheet`)
Slides up from bottom when tapping the settings icon:
- **Modern words** toggle (iOS-style switch)
- **Listen** toggle (starts narration)
- **Section headings** toggle
- **Text size** selector (S / M / L buttons)
- **Light mode** toggle
- **Refresh content** and **Save for offline** utility buttons
- Backdrop scrim (`.sheet-scrim`) behind the sheet

### Landing Page (`.landing`)
Shown when no hash is present (initial visit):
- Title: "The Book of Mormon — Reading Edition"
- Tagline and description paragraph
- Book grid with all 15 books as clickable cards (built from `bookMeta` via `buildLandingBooks()`)
- "Learn more about the features" link → About page

### Text Mode
Sense lines are now the ONLY text mode for the Reading Edition. `applyTextMode(1)` is forced on load. The three-layer data (prose `.line-para`, sense lines `.line`, Parry parallels `.line-parry`) still exists in `books/*.html` for future Studying Edition use. See `archive-studying-edition/text-mode-system.md`.

### Content Area (`#scripture-content`)
Contains:
- `#landing` — landing page (shown when no hash)
- `#about-page` — full feature guide (hidden by default)
- `#book-content-container` — where book HTML fragments get injected

### Preserved but Hidden
- `#settings-panel-old` — the old toolbar settings panel, kept with `display:none` for future Studying Edition reference
- All verse rendering infrastructure (`.verse`, `.line`, `.swap`, `.punct`, `.deity`, `.gloss`, `.pericope`, annotations) remains unchanged

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
| `show-parallels` | Hebrew Poetry parallel structure layer active |
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
- `selectAllLayers()` / `clearAllLayers()` — check/uncheck all 7 layer checkboxes
- `updateLayersPill()` — toggles `active-layers` class on pill if any layer is checked
- Sections toggle is **independent** of the layers panel (it's a top-level pill)

---

## build_book.py — Build Pipeline

### Swap System (Longest-First Sorting)

Processing order in `apply_swaps()`:
1. **AICTP_SWAPS** (32 entries) — "And it came to pass" variants, literal string replacement
2. **COMPOUND_SWAPS** (45 pairs) — Multi-word phrases like "save it be" → "unless"
3. **SIMPLE_SWAPS** (161 pairs) — Single-word archaic → modern
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

### Archaic Word Swaps Expansion (Mar 2 evening)

**New SIMPLE_SWAPS (5 words, 10 entries with capitalized variants):**
- `aught` → "anything" (2 occurrences)
- `nay` → "no" (44 occurrences)
- `privily` → "secretly" (4 occurrences)
- `wist` → "knew" (2 occurrences)
- `notwithstanding` → "despite this" (67 occurrences)

**New COMPOUND_SWAPS — bowels (6 patterns, 8 occurrences):**
Context-sensitive — figurative uses (seat of emotion) → "depths of mercy" / "heart is filled with"; literal uses → "body" / "womb":
```python
("bowels of mercy", "depths of mercy")
("bowels are filled with compassion", "heart is filled with compassion")
("bowels are filled with mercy", "heart is filled with mercy")
("bowels may be filled with mercy", "heart may be filled with mercy")
("offspring of thy bowels", "offspring of thy body")
("bowels of my mother", "womb of my mother")
```

**New COMPOUND_SWAPS — loins (12 patterns, 34 occurrences):**
Context-sensitive — figurative uses (lineage/descendants) → "lineage"; literal uses (body part) → "waist":
```python
("fruit of my loins", "fruit of my lineage")
("fruit of thy loins", "fruit of thy lineage")
("fruit of his loins", "fruit of his lineage")
("fruit of the loins", "fruit of the lineage")
("seed of thy loins", "seed of thy lineage")
("spokesman of thy loins", "spokesman of thy lineage")
("about my loins", "about my waist")
("about his loins", "about his waist")
("about their loins", "about their waist")
("about her loins", "about her waist")
("of his loins", "of his waist")
("of their loins", "of their waist")
```

**Total new swaps across the canon:** 161 occurrences (aught 2 + nay 44 + privily 4 + wist 2 + notwithstanding 67 + bowels 8 + loins 34). All 15 books rebuilt and verified.

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
Loads 6 JSON files into globals:
1. `hardy_intertext.json` → `_INTERTEXT_INDEX`
2. `hardy_phrase_index.json` → `_PHRASE_INDEX`
3. `kjv_diff_index.json` → `_KJV_DIFF_INDEX`
4. `geo_index.json` → `_GEO_INDEX`
5. `pericope_index.json` → `_PERICOPE_INDEX`
6. `parallel_index.json` → `_PARALLEL_INDEX`

All graceful — missing files print warning but don't break.

### Pericope Integration in gen_chapter()
```python
par_map = build_parallel_map(bid, ch_num, ch_verses)
for v in ch_verses:
    pericope_title = get_pericope(bid, v['chapter'], v['verse'])
    if pericope_title:
        p.append(format_pericope_header(pericope_title))
    p.append(gen_verse(v, swap_list, book_id=bid, parallel_map=par_map))
```

### Per-Verse Enrichment in gen_verse()
Each verse goes through:
1. Apply word swaps to all lines
2. Inject intertext references (quotations/allusions) with phrase-level highlighting
3. Apply geography highlighting and categorization
4. Add KJV diff parallel passages with strikethrough/bold markup
5. Inject parallel structure data attributes (`data-parallel-group`, `data-parallel-level`) on matched lines
6. Wrap with verse number and line spans

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

**710 total sections** across 15 books. Individual source files: `data/pericope_*.json`

### Two-Tier Header System (Mar 1 evening)

Titles can contain two-tier formatting and parenthetical scripture references:
- `"Main Title: Subtitle Detail"` → splits on colon into main + subtitle lines
- `"Title (Isaiah 2:1-5)"` → extracts parenthetical as a third reference line
- Plain titles with no colon or parens render as single-line headers

`format_pericope_header()` in `build_book.py` generates three CSS classes:
- `.pericope-two-tier` — has main + subtitle (+ optional ref)
- `.pericope-with-ref` — single title + scripture reference
- Plain `.pericope-header` — single line, no extras

### CSS
```css
.pericope-header {
  display: none;
  font-size: 0.88em; font-weight: 600; color: #9ab;
  letter-spacing: 0.03em; margin: 1.8em 0 0.5em 0;
  padding: 0 0 6px 0; border-bottom: 1px solid rgba(154,170,187,0.2);
  font-style: normal; line-height: 1.5;
}
body.show-sections .pericope-header { display: block; }
body.show-sections .pericope-header.pericope-two-tier,
body.show-sections .pericope-header.pericope-with-ref {
  display: flex; flex-direction: column; gap: 1px;
}
.pericope-main { font-weight: 600; letter-spacing: 0.03em; color: #9ab; }
.pericope-sub { font-weight: 400; font-style: italic; font-size: 0.9em; color: rgba(154,170,187,0.7); }
.pericope-ref { font-weight: 400; font-style: normal; font-size: 0.82em; color: rgba(154,170,187,0.5); }
```

### Isaiah/Malachi Pericope Revisions (Mar 1 evening)
Rewrote pericope entries for the dense biblical-quotation sections:
- **2 Nephi 12–24** (Isaiah 2–14): 49 entries replacing 10 sparse/incorrect ones
- **2 Nephi 27** (Isaiah 29): 9 entries replacing 4 generic ones
- **3 Nephi 22–25** (Isaiah 54 + Malachi 3–4): 18 new entries from zero
- Fixed incorrect titles (e.g., "Suffering Servant" was on ch 13 = Isaiah 3, not Isaiah 53)
- Total pericope count: 648 → 710

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

## Hebrew Poetry / Parallel Structure Layer (Mar 1 evening)

### Overview
A new layer that highlights Hebraic parallel structures (chiasmus, synonymous parallelism, antithetical parallelism, etc.) using data from Donald Parry's analysis of the Book of Mormon.

### Data Pipeline
1. **Source:** `data/parry-parallels-full.txt` — 14,544 lines, 1,530 labeled structures across all 15 books
2. **Parser:** `build_parallel_index.py` applies a "lite" filter:
   - Chiasmus structures ≤3 levels deep
   - Simple synonymous, simple alternate, antithetical, and contrasting ideas (all depths)
   - Post-processing dedup removes subset/duplicate structures
   - Result: **619 structures** (60% reduction from full dataset)
3. **Output:** `data/parallel_index.json` keyed `book_id → chapter → [{type, lines: [{verse, level, text_fragment}]}]`

### Build Integration
- `build_parallel_map()` in `build_book.py` fuzzy-matches Parry's text fragments against sense-lines using word-overlap scoring with first-word bonus
- `gen_verse()` injects `data-parallel-group="p12-0"` and `data-parallel-level="A"` attributes on matching `<span class="line">` elements
- 2 Nephi build produces 402 tagged lines across 142 matched structures

### CSS — Parry-Style Clean Scholarly Indentation (Mar 2)
All existing layers work at word/phrase level (text color, underline, `::after` pseudo-elements). The parallel layer uses LINE-level properties (indentation, labels) to avoid collision.

**Design:** Matches Donald Parry's published format — clean cascading indentation with lowercase italic letter labels, no background colors or decorative borders. Purely structural.

```css
body.show-parallels [data-parallel-level] {
  position: relative;
  padding-left: 2em;           /* base indent for label space */
}
body.show-parallels [data-parallel-level]::before {
  content: attr(data-parallel-level);
  text-transform: lowercase;   /* A→a, B→b, etc. */
  color: inherit;              /* matches text color, not rainbow */
  opacity: 0.45;
  font-style: italic;
  font-weight: 400;
}
/* Progressive indentation: A=2em, B=3.5em, C=5em, D=6.5em, E=8em */
```

Previous iterations tried colored backgrounds + colored letter labels per level — user rejected these as too noisy/decorative compared to Parry's clean academic style.

### Current State
- ✅ Parser complete, generates 619 lite structures
- ✅ Build pipeline injects `data-parallel-group` and `data-parallel-level` attributes on matched sense-lines
- ✅ CSS: Parry-style cascading indentation with lowercase labels (Mar 2)
- ✅ Layers panel toggle ("Hebrew Poetry" under "Literary" group)
- ✅ All 15 books rebuilt with parallel markup (Mar 2)

### Alignment Analysis
- **22% of structures** (32/143 in 2 Nephi) have perfect sense-line alignment — all Parry break-points coincide with existing sense-line breaks
- **78% have mismatches** — Parry wants line breaks inside our sense-lines (209 split candidates in 2 Nephi)
- **Possible approach:** Use Parry's break-points as a diagnostic to identify sense-lines that merit revision; as sense-lines get refined, Parry-style rendering coverage increases organically

---

## Spanish Language Data (Mar 1 evening)

### What's Available
`data/spa/` contains the official LDS Spanish translation of the entire scripture canon in JSON format (not just Book of Mormon — includes Bible, D&C, Pearl of Great Price).

### Structure
```json
{
  "volume_title": "Book of Mormon",
  "book_title": "1 Nephi",
  "book_title_short": "1-ne",
  "chapters": [
    {
      "chapter_number": 1,
      "verses": [
        {
          "verse_number": 1,
          "scripture_text": "Yo, Nefi, nací de buenos padres..."
        }
      ]
    }
  ]
}
```

### Status
Raw data only — filed as a future MAJOR fork. Key requirements identified:
- **Sense-lining** is the big lift (6,604 BofM verses are paragraph-style, not sense-lined). Algorithmic first pass at Spanish clause boundaries could get 70–80%, then manual refinement.
- **Carries over as-is:** parallel/Hebrew poetry layer (structural), pericope placement, intertext locations, geography layer, entire UI architecture
- **Needs Spanish-specific work:** translated UI strings, Spanish swap lexicon (the LDS translation has some archaic forms), translated pericope titles, Reina-Valera parallel for the diff layer
- **Architectural decision:** true fork (separate site) vs. in-app language toggle

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

### Layers panel won't dismiss on desktop (Mar 1 evening)
**Symptom:** On desktop, the layers panel covers most of the screen. The old click-to-dismiss was only on `#scripture-content`, leaving nothing to click.
**Cause:** Click handler was scoped too narrowly — only the scripture content area, not the full document.
**Fix:** Added document-level click-outside handler with exclusions for panels, toggle buttons, and book buttons. Also added Escape key handler for desktop UX.
```javascript
document.addEventListener('click', function(e) {
  // Checks if any panel is open
  // Excludes clicks inside panels, on toggle buttons, on book buttons
  // Closes all panels if click was outside
});
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') { /* close any open panels */ }
});
```

### Incorrect pericope titles for Isaiah chapters (Mar 1 evening)
**Symptom:** 2 Nephi 13 was labeled "Suffering Servant" (which is Isaiah 53), but 2 Ne 13 actually maps to Isaiah 3 (judgment on Jerusalem). Multiple other entries were similarly wrong or missing entirely.
**Fix:** Rewrote all Isaiah/Malachi pericope entries with correct content mapping. See "Isaiah/Malachi Pericope Revisions" section above.

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
- **Layers panel groups**: Divine Voice, Biblical Roots, Setting, Literary. Sections is a top-level pill, not in layers.
- **About page replaces content area** (not a dropdown), toolbar stays functional for navigation.
- **Layer visual channel separation:** Existing layers (deity, quotations, allusions, geography, KJV diff) all work at word/phrase level (text color, underline, `::after`). The parallel layer uses LINE-level properties (indentation + letter labels via `::before`) — no visual collision when all layers are active simultaneously.
- **Parallel "lite" filter:** Parry's full dataset (1,530 structures) is too dense. Lite = chiasmus ≤3 deep + simple couplets = 619 structures (60% reduction).
- **Two-tier pericope headers** for Isaiah/Malachi sections provide main title, subtitle, and scripture cross-reference on separate lines.

---

## Pending / Known Issues

1. ~~**Rebuild all books**~~ — ✅ Done (Mar 2). All 15 books rebuilt with parallel layer + corrected KJV diff data.
2. ~~**Hebrew Poetry visual rendering**~~ — ✅ Done (Mar 2). Parry-style clean cascading indentation with lowercase labels. See Hebrew Poetry section.
3. ~~**KJV diff layer styling**~~ — ✅ Done (Mar 2). Deletions now muted red (`rgba(200, 110, 110, 0.7)`), insertions warm gold (`#d4a855`). Light-mode variants included.
4. **Parry as sense-line diagnostic** — Use Parry's parallel break-points to flag sense-lines that might benefit from revision (209 split candidates identified in 2 Nephi alone). Improving sense-line alignment would organically increase Parry-style rendering coverage.
5. **Spanish fork** — Major future project. Raw data in `data/spa/`. Needs sense-lining, UI translation, swap lexicon, Reina-Valera diff layer.
6. **localStorage persistence** — Not implemented. Settings reset on page load.
7. ~~**Navigation bug (2 Ne → 33)**~~ — ✅ Fixed (Mar 2). Three sub-fixes: toggleSettings now closes nav-panel, pendingChapter cleared on book click, switchBook callback guards nav-panel re-open.
8. **Reformatter v8 refinement** — M0 em-dash and M12 in+gerund thresholds could be adjusted.

## Mar 2 Session Summary

### Navigation Bug Fixes
Three root causes identified and fixed in `index.html`:
- `toggleSettings()` now closes `nav-panel` when opening settings
- `onBookBtnClick()` clears `pendingChapter` at top (prevents stale chapter from previous book)
- `switchBook()` callback checks whether layers/background/settings panels are open before re-showing nav-panel

### KJV Diff False Hit Fix
**Problem:** `build_kjv_diff.py` word-level diff was comparing "Lord," ≠ "Lord" (punctuation attached to tokens), causing 65% of delete→insert pairs to be false hits (crossing out a word and replacing with the same word).
**Fix:** Added `normalize_for_diff()` function that strips trailing punctuation before comparison. Regenerated `data/kjv_diff_index.json` — same 323 verses with differences but now clean diffs.
**Verification:** 2 Ne 12:19 "Lord" now correctly shows as equal text instead of ~~Lord,~~ **Lord**

### Inline Reference Removal
Removed the `[data-source]::after` CSS content rule that displayed inline scripture references (e.g., "— Isaiah 2:1") at end of verses. Now redundant with pericope headers providing that context. The `data-source` attributes remain in HTML for potential future tooltip use.

### Hebrew Poetry CSS Rewrite
Replaced colored backgrounds + rainbow letter labels with Parry-style clean scholarly indentation: lowercase italic letters inheriting text color at 45% opacity, progressive padding-left per level, no backgrounds.

### Sense-Line Splits from Parry Alignment
Ran `parry_split_candidates.py` to identify sense-lines where Parry's parallel fragments suggest a split. Found 308 candidates; applied ~98 high/medium-confidence splits (semicolon breaks, comma+conjunction) across 1 Nephi, 2 Nephi, Mosiah, and Alma source files.

### Chiasmus Prime Notation
Added `add_chiasmus_primes()` to `build_parallel_index.py`. For chiasmus structures (A,B,C,B,A), the return side now displays as a', b', c' instead of a, b, c. Algorithm finds the deepest point (center of chiasm) and primes everything after it.

### Default Landing Page
Changed init behavior: no hash → show About page; hash present → honor deep link. Removed auto-loading 1 Nephi on startup. `showAboutPage()` clears URL hash with `history.replaceState()`.

### KJV Partial-Chapter Parallel Mappings (Mar 2 late)
Extended `build_kjv_diff.py` with `PARTIAL_PARALLELS` for verse-range quotations that don't span a full chapter:
- **Mosiah 14** = Isaiah 53 (full chapter, was missing from `PARALLEL_CHAPTERS`)
- **Mosiah 12:21-24** = Isaiah 52:7-10
- **3 Nephi 16:18-20** = Isaiah 52:8-10
- **3 Nephi 20:36-45** = Isaiah 52:1-3, 52:6-7, 52:11-15
- **2 Nephi 6:6-7** = Isaiah 49:22-23
- **2 Nephi 6:16-18** = Isaiah 49:24-26
- **2 Nephi 8:24-25** = Isaiah 52:1-2
- **2 Nephi 9:50-51** = Isaiah 55:1-2
- **2 Nephi 30:9-15** = Isaiah 11:4-9

Total KJV diff coverage: 551 verses (up from ~420).

Also added pericope section headers for newly mapped quotation passages (e.g., "Quoting Isaiah (Isa 52:8–10)" before 3 Ne 16:18). Changed `has_diff` check so ALL verses with KJV parallel data get `has-kjv-diff` class, not just those with actual textual differences.

### All 15 Books Rebuilt
Ran `build_book.py --all booklist.txt --out books/` — all books now have expanded KJV parallel data, corrected diffs, parallel layer markup, and sense-line improvements.

### Read Along Feature Extraction (Mar 2 evening)
The mic/Read Along feature (~280 lines of JS + CSS) was extracted from `index.html` into a standalone `readalong.html` file. The main app no longer has any speech recognition code.

**What was removed from `index.html`:**
- CSS: `.pill-btn.active-mic`, `@keyframes mic-pulse`, `.ra-word-active`, `.ra-line-active`, `.ra-word-done` + light-mode variants (~34 lines)
- HTML: `<button id="mic-pill">` from controls row, Mic feature card from About page
- JS: Entire Read Along IIFE — `SpeechRecognition` setup, `buildWordMap()`, `teardownWordMap()`, `highlightWord()`, `processSpeech()`, Levenshtein matching, `showChapter` wrapper (~270 lines)

**What `readalong.html` provides:**
- Standalone single-file tool with its own book grid, chapter selector, and status indicator
- Loads the same `books/*.html` fragments via fetch (same content, just a different shell)
- Full speech recognition with fuzzy Levenshtein matching, word-by-word highlighting, line tracking, auto-scroll
- "← Back to the Reading Edition" link to `index.html`
- Marked as BETA with a red tag in the header
- Could live at `bomreader.com/readalong` or eventually become its own repo

**Why extracted:** The feature "kind of works but not really yet" — browser speech recognition is inconsistent (Chrome-only, intermittent timeouts, accuracy issues with archaic English). Keeping it separate lets the main reader stay stable while the Read Along tool can be iterated on independently.

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

---

## Mar 13–14 Sessions: Narration System + Voice Exploration + Sense-Line Review

**Last updated:** 2026-03-14
**Sessions covered:** Mar 13 (narration rewrite, ElevenLabs pipeline) → Mar 13 evening (voice comparison, UX enhancements) → Mar 14 (authentic text fix, Samuel re-generation, Mosiah sense-line review)

---

### ElevenLabs TTS Pipeline (Colab Notebook)

The narration system was rebuilt from scratch, moving from browser-based Kokoro.js TTS to pre-generated audio using the ElevenLabs API.

**Colab Notebook:** `bom_reader_voices` at https://colab.research.google.com/drive/15bW7Y1p8eGsL-ODf6pGb4Nn7DTp-Cpnj

**Cell structure:**

| Cell | # | Purpose |
|------|---|---------|
| 1 | [varies] | Install dependencies (pydub, beautifulsoup4, requests) |
| 2 | [varies] | Clone repo + set configuration (API key, default voice, model, pause timing) |
| 3 | [20] | **Core functions** — all HTML parsing, TTS calls, caching, stitching (~200 lines) |
| 4 | [9] | Quick test — generates 5 lines for voice preview |
| 5 | [21] | **Full generation** — currently configured for Enos with Samuel voice |
| 6 | [22] | **Download** — copies output to voice-labeled filenames and triggers browser download |

**Configuration (Cell 2):**
```python
ELEVENLABS_API_KEY = "sk_d38fb8e3ceaf4ca8304ccef240d231025e0afb0d150168ba"
VOICE_ID = "GBc0W7zMgpvEFBEHSpqS"    # Hector the Protector (default/unused)
MODEL_ID = "eleven_multilingual_v2"    # Best for accented English
LINE_PAUSE_MS = 180    # 180ms between sense-lines
VERSE_PAUSE_MS = 500   # 500ms between verses
```

**Voice IDs:**

| Voice | ElevenLabs ID | Status | Enos Stats |
|-------|---------------|--------|------------|
| Samuel | `ddDFRErfhdc2asyySOG5` | **Active** — current production voice | 429.1s / 6706 KB (authentic text) |
| Tony | `lRf3yb6jZby4fn3q3Q7M` | **Shelved** — "put on the shelf for now" | 386.7s / 6043 KB |
| Lester | `LBN8aWETnm9oOSBzmFQR` | Generated but not deployed | 360.8s / 5639 KB |

**Per-line audio caching:**
- Cache dir: `audio_cache/` in Colab runtime
- Cache key: SHA256 hash of `json.dumps({text, voice_id, model_id, settings})`
- Changing ANY of these invalidates the cache for that line
- Cached lines show `[cache]` in output; fresh lines show `[NEW]`
- Re-running is cheap — only changed lines hit the API

**Critical code path — text extraction:**

The `get_text_from_element(el, use_modern=False)` function in Cell 3 controls whether TTS reads authentic Book of Mormon text (`data-orig` values like "brethren", "unto", "thy") or modernized reading edition text (`data-mod` values like "brothers", "to", "your").

The default parameter `use_modern=False` was set correctly, BUT `parse_chapter()` was explicitly calling it with `use_modern=True`, overriding the default. **This was the root cause of the "brothers vs brethren" bug.**

**THE FIX (applied Mar 14):** Changed the call site in `parse_chapter()`:
```python
# BEFORE (bug):
text = get_text_from_element(line_el, use_modern=True)
# AFTER (fix):
text = get_text_from_element(line_el, use_modern=False)
```

**Stan's stated preference:** "I want to use our modified sense-lines, but I do NOT want to use our archaic language for the voice script. I want the authentic wording of the Book of Mormon." This means:
- Sense-line BREAKS come from the reading edition (the HTML structure)
- TTS TEXT uses original Book of Mormon wording (data-orig), NOT modernized swaps (data-mod)

**Colab editing lessons learned:**
1. **Monaco editor API changes are unreliable** — edits save to the notebook file but may not update the live runtime cell. The "Review remote changes" dialog is a symptom.
2. **Use Colab's Find & Replace (Ctrl+H)** for reliable multi-instance edits — it updates both the notebook AND the runtime.
3. **Always verify output** before downloading — check the printed voice ID, character count, and look for [NEW] vs [cache] tags to confirm text actually changed.

---

### Narration Player (narration.js)

**File:** `narration.js` (~1050 lines)
**Architecture:** IIFE module (`const NARRATION = (() => { ... })()`) attached to window

**Key features added in Mar 13–14 sessions:**

1. **Voice-prefixed file paths** — Audio files are now `audio/{book}-{chapter}-{voice}.mp3` instead of `audio/{book}-{chapter}.mp3`. The `VOICE` constant (currently `'samuel'`) controls which voice files load.
   ```javascript
   const VOICE = 'samuel';  // active voice: 'samuel', 'tony', etc.
   const mp3Url = `${AUDIO_BASE}${ch.bookId}-${ch.chapter}-${VOICE}.mp3`;
   ```

2. **Click-to-seek** — Users can click any sense-line during playback to jump to that point in the audio. Uses `getLineIndexFromElement()` to map DOM elements back to manifest line indices.

3. **Mini speed control** — Collapsed player bar shows a speed button that cycles through 0.75x/1x/1.25x/1.5x/2x.

4. **Collapse/close buttons** — Mini player can be collapsed to a thin bar or closed entirely.

5. **Persistent bottom-bar player** — Full media controls with play/pause, skip forward/back, progress bar, speed control. Expands/collapses between mini and full views.

**Audio file naming convention:**
```
audio/enos-1-samuel.mp3      # Enos chapter 1, Samuel voice
audio/enos-1-samuel.json     # Timing manifest for above
audio/enos-1-lester.mp3      # Enos chapter 1, Lester voice (if generated)
```

**Timing manifest format (JSON):**
```json
{
  "book": "enos",
  "chapter": 1,
  "voice_id": "ddDFRErfhdc2asyySOG5",
  "lines": [
    {
      "start": 0.0,
      "end": 2.345,
      "type": "line",
      "text": "Behold, it came to pass that I, Enos,...",
      "verse": "1:1",
      "lineIndex": 0
    }
  ]
}
```

**Current audio inventory:**
- `audio/enos-1-samuel.mp3` (6706 KB, 429.1s) — Samuel voice, authentic BofM text ✅
- `audio/enos-1-samuel.json` — timing manifest ✅
- No other books/chapters have audio yet

**Service worker:** `sw.js` cache version is `bomreader-v31`

---

### HTML Swap Element System (for TTS text extraction)

The HTML book files use swap spans to provide both authentic and modernized text:

```html
<span class="swap swap-quiet" data-orig="unto" data-mod="to">unto</span>
<span class="swap swap-quiet" data-orig="brethren" data-mod="brothers">brethren</span>
<span class="swap swap-quiet" data-orig="Behold, it came to pass that" data-mod="Then behold,">Behold, it came to pass that</span>
```

- `data-orig` = authentic Book of Mormon text (what displays by default, what TTS reads)
- `data-mod` = modernized reading edition text (shown when "Aid" toggle is ON)
- `class="swap"` = visible swap (shows tooltip/highlight)
- `class="swap swap-quiet"` = quiet swap (no visible indicator, just for Aid toggle)

**For TTS:** `get_text_from_element(el, use_modern=False)` extracts the displayed text as-is (since `data-orig` is the default innerHTML). When `use_modern=True`, it replaces swap spans with their `data-mod` values before extracting text.

---

### Sense-Line Review Process

**Stan's canonical source files** live in:
```
data/text-files/v2-mine/01-1_nephi-2020-sb-v2.txt
data/text-files/v2-mine/02-2_nephi-2020-sb-v2.txt
...
data/text-files/v2-mine/08-mosiah-2020-sb-v2.txt  (most recently edited)
...
data/text-files/v2-mine/15-moroni-2020-sb-v2.txt
```

**File format:** Plain text with verse markers and one sense-line per line:
```
5:15
may seal you his,
that you may be brought to heaven,
that ye may have everlasting salvation and eternal life,
through the wisdom, and power,
and justice, and mercy
of him who created all things, in heaven and in earth,
who is God above all.
Amen.
```

**Review methodology — how Stan and Claude review sense-lines together:**

Stan makes manual edits to the v2-mine text files on his local machine, then asks Claude to review them. The review process:

1. Claude runs `git diff` on the changed text file to see exact edits
2. Claude categorizes each edit as a "merge" (joining short lines together) or "break" (splitting a line into multiple)
3. Claude evaluates each edit against these principles:
   - **Merges are good when:** items are short parallel fragments that read as a single breath ("Abraham, and Isaac, and Jacob" belongs together)
   - **Breaks are good when:** a line combines distinct units that deserve separation (geographic lists, clause boundaries at semicolons)
   - Lines should be natural breath units for read-aloud delivery
   - Parallel structures should be mirrored across lines
   - Don't over-split short phrases; don't under-split long compound lines
4. Claude provides a brief assessment of each change with reasoning

**Most recent review (Mar 14):** Mosiah chapters 5 and 7 — four edits:
- 5:15: Merged 4 short parallel items ("wisdom / power / justice / mercy") into 2 lines of paired items ✓
- 7:7: Merged 3 short parallel clauses ("taken / bound / committed to prison") into 1 line ✓
- 7:19: Merged "God of Abraham / Isaac / Jacob" into 1 line ✓
- 7:21: Broke 2 lines into 3 — separating cities/lands at natural pause points ✓

**Build pipeline after editing text files:**
```bash
# 1. Edit text files in data/text-files/v2-mine/
# 2. Rebuild HTML:
python3 build_book.py --all booklist.txt --out books/
# 3. If audio exists for changed chapters, regenerate via Colab
```

**rebreak.py** — A utility script in the repo root for automated sense-line rebalancing:
- Examines lines >78 chars for potential splits
- Examines lines <25 chars for potential consolidation
- Uses grammatical break-point patterns (subordinate clauses, conjunctions, prepositional phrases)
- Has uncommitted changes (396-line diff) — appears to be actively iterated on

---

### Pending Tasks and Next Steps

**Immediate:**
1. ~~Samuel Enos generation with authentic text~~ ✅ Done (429.1s / 6706 KB)
2. ~~Download Samuel files~~ ✅ Done (enos-1-Samuel.mp3 + enos-1-Samuel.json)
3. **Files need proper casing** — repo has `enos-1-samuel.mp3` (lowercase) but Colab downloaded `enos-1-Samuel.mp3` (capital S). `narration.js` VOICE constant is lowercase `'samuel'`. Need consistency.
4. **Mosiah text file changes need to be built** — `data/text-files/v2-mine/08-mosiah-2020-sb-v2.txt` has 4 uncommitted sense-line edits. Need `python3 build_book.py mosiah --out books/` then commit.
5. **rebreak.py has uncommitted changes** — 396-line diff, unclear if WIP or ready to commit.

**Voice exploration (shelved):**
- Tony (`lRf3yb6jZby4fn3q3Q7M`) is shelved per Stan's request
- Lester (`LBN8aWETnm9oOSBzmFQR`) was generated but not deployed
- Samuel is the active voice going forward
- Previous "bad" Lester files (which were actually Tony's voice due to the Monaco editor bug) were downloaded but should be discarded

**Audio expansion:**
- Only Enos chapter 1 has audio currently
- To add more chapters/books: configure Cell 5 in Colab with new BOOK_ID/CHAPTER, run generation
- Each chapter takes ~3-5 minutes for 140 lines at ~$0.02-0.05 in API credits
- Audio files go in `audio/` directory with voice-prefixed naming

**Ongoing sense-line work:**
- Stan is actively reviewing/editing Mosiah text files
- The review process is collaborative: Stan edits → Claude reviews the diff → iterate
- `rebreak.py` automates common patterns but Stan hand-edits for editorial judgment
- Parry parallel data (619 structures) can serve as a diagnostic for misaligned sense-lines

---

### Voice Settings (ElevenLabs)

```python
VOICE_SETTINGS = {
    "stability": 0.50,
    "similarity_boost": 0.75,
    "style": 0.35,
    "use_speaker_boost": True,
}
```

These settings are baked into the cache key — changing them invalidates all cached lines.

---

### Known Gotchas

1. **Colab Find & Replace is the only reliable way to edit cells** — don't trust Monaco editor API changes to propagate to the runtime.
2. **Always check [NEW] vs [cache] tags in generation output** — if you expect text changes but see all [cache], the text didn't actually change (runtime still has old function definitions).
3. **The `use_modern` parameter has TWO locations** — the function default AND the call site in `parse_chapter()`. Both must agree. The call site takes precedence.
4. **"Saving failed" in Colab** is harmless — doesn't affect running code or downloads. Fix with File → Save a copy in Drive.
5. **Audio file casing** — `narration.js` uses lowercase voice names. Colab downloads may have different casing. Ensure files match what the JS expects.
6. **Service worker caching** — after deploying new audio or code changes, bump the cache version in `sw.js` (currently `bomreader-v31`).

---

### Git Status (as of Mar 14 end of session)

**Uncommitted changes:**
- `data/text-files/v2-mine/08-mosiah-2020-sb-v2.txt` — 4 sense-line edits (merges + break in ch 5, 7)
- `rebreak.py` — 396-line diff (automated rebalancing tool updates)

**Recent commits (Mar 14):**
```
be5c28a new-voice
782684b voice
44c9677 voices
6eefc36 narration-update
767dfd2 Bump service worker cache to v27 for narration updates
```

**All narration.js and sw.js changes are committed.** The audio files (enos-1-samuel.mp3/json) are committed.

---

### Email Task Queue (from Stan's "Hey Claude" emails, Mar 14)

These are pending tasks Stan sent to himself as notes for Claude. Read the full emails for details — search `from:thebibleman77@gmail.com` in Gmail.

**1. Audio-highlight sync drift (HIGH PRIORITY)**
- **Email subject:** "Hey Claude" (3:47 PM, message ID `19cede3bb627b5a6`)
- **Problem:** Samuel's Enos audio gets out of sync with the highlighted sense-line at some point during playback. The line highlight drifts from the actual spoken text.
- **Likely cause:** The timing manifest (`enos-1-samuel.json`) was generated with authentic BofM text, but the `lineIndex` values in the manifest may not match the DOM line indices that `narration.js` counts (pericope headers, verse gaps, and other non-speakable elements affect the count). Investigate `findLineElement()` in narration.js and compare its line-walking logic against the manifest's `lineIndex` values.
- **To debug:** Play the audio on bomreader.com, note the exact verse/line where sync drifts, then compare manifest timestamps against DOM line indices at that point.

**2. Toolbar stuck open on mobile (HIGH PRIORITY)**
- **Email subject:** "Hey Claude" (3:52 PM, message ID `19cede89de083b16`)
- **Problem:** After the tap-to-toggle toolbar was introduced, the floating top banner occasionally gets "pegged open" on mobile — can't scroll past it.
- **Likely cause:** The scroll handler and tap-to-toggle state machine have a race condition. The toolbar's collapsed/expanded state gets stuck. Check the scroll freeze logic (which pauses collapse while panels are open) and the tap-to-toggle handler interaction.
- **Related to email #3 below** — the tap-to-toggle was a design change requested earlier the same day.

**3. Tap-to-toggle toolbar redesign (MEDIUM — may be already partially done)**
- **Email subject:** "Hey Claude — UI change: tap-to-toggle the floating top banner on bomreader.com" (9:10 AM, message ID `19cec783d4a55f1f`)
- **Request:** Redesign toolbar visibility to be purely tap-based — tap anywhere to hide, tap again to show. Completely decouple from scroll direction. No scroll-up/scroll-down auto-show/hide logic at all.
- **Has screenshot attachment** — read the full email for the detailed spec and screenshot.
- **Note:** This was likely partially implemented (commits `fcd7921` "tap-to-toggle toolbar" and others), which is what introduced the stuck-open bug (#2 above).

**4. "Behold" vs. "Lo" sense-line methodology (LOW PRIORITY — research/methodology)**
- **Email subject:** "Hey Claude — Methodology note: 'Behold' vs. 'Lo' as sense-line break triggers in the Book of Mormon" (6:25 AM, message ID `19cebe1412bf1438`)
- **Content:** A detailed linguistic working note establishing three functional types of "behold" (deictic, mirative, logical-connective) and how each should affect sense-line breaking decisions. "Lo" is distinct — appears only ~5-10 times, almost exclusively in Isaiah quotation blocks.
- **Action items from the email:**
  - Apply the three "behold" type distinctions to a test passage (suggested: Alma 5 or 2 Nephi 4:15–35)
  - Evaluate whether type C (logical-connective "behold", e.g., "For behold...") benefits from indentation rather than a full line break
  - Decide how "and behold" vs. standalone "behold" affects break placement
  - Decide whether "lo" in Isaiah blocks follows our rules or defers to Isaiah's own poetic structure

**5–8. Older emails (Mar 13 evening — most likely already addressed):**
- Archaic word filter false hits on verbs (Mosiah 1:8, 2:9) — likely fixed in commits `42addb3`, `430d302`
- AICTP double-that construction (Mosiah 1:9) — likely fixed in commit `832082b`
- Pericope header verse ranges + thematic breaks — likely done in commit `c7f7486`
- "can you read this" test email — ignore

---

## Mar 16 Redesign Notes

### What Changed
- **Removed:** Complex collapsible floating toolbar (`#reading-toolbar`) with its ~250-line scroll state machine, book grid, controls row, pill buttons, and multi-panel system
- **Added:** Thin persistent top bar (44px), full-screen book/chapter picker overlay, bottom sheet for settings, landing page, progress line
- **Simplified:** Text mode is now sense-lines only (no verse/prose/parallels toggle). `applyTextMode(1)` forced on load.
- **Preserved:** All verse rendering, search system (with stem matching, charts, boolean queries), annotations (Firebase), narration, swipe navigation, keyboard shortcuts, offline/service worker support

### Archive
Old UI code preserved in `archive-studying-edition/` folder:
- `old-toolbar.html` — HTML skeleton of the removed toolbar
- `old-toolbar-css.css` — Removed CSS styles
- `old-toolbar-js.js` — Removed JS state machine
- `text-mode-system.md` — Documentation of the three-layer text system
- `README.md` — Overview and rationale

### Known Issues / TODO
- Light mode CSS needs verification for new topbar, picker, sheet, and landing page elements
- Narration integration: Listen button was previously in `.controls-row`, now in bottom sheet `#listen-toggle-row` — needs verification
- Book introductions (previously in `#background-panel`) are in hidden `settings-panel-old` div — need to be made accessible (via About page or picker)
- Lower priority: About page color accuracy, generate 2 Nephi 6-33 audio, 1 Ne 6:1 verse text edit and audio patch
