# 01 — Project Overview & Architecture

## What This Is
A web-based reading app for the Book of Mormon (bomreader.com). Designed for ESL readers, children, and newcomers. Text is presented in sense-line (cola) format — each line is a natural breath unit for read-aloud delivery. Archaic words can be toggled to modern equivalents. Multiple study layers (deity references, biblical quotations, geography, etc.) can be overlaid. Audio narration per chapter.

## Core Details
- **Site:** bomreader.com
- **Repo:** github.com/bibleman-stan/readers-bofm (public)
- **Hosting:** GitHub Pages
- **Stack:** Vanilla HTML/CSS/JS single-page app, Python 3 build scripts, Google Fonts (Literata), dark theme default
- **Local dev:** `python -m http.server 8000` (file:// won't work — books load via fetch)
- **User:** Stan (thebibleman77@gmail.com)

## Key Files

| File | Purpose |
|------|---------|
| `index.html` | Main app shell — ALL CSS, HTML, JS inline in one file (~4220 lines) |
| `books/index.html` | Alternate book reading view with its own separate inline CSS |
| `narration.js` | Audio playback module (~1050 lines, IIFE on window.NARRATION) |
| `sw.js` | Service worker for offline caching |
| `build_book.py` | Converts sense-line .txt sources → HTML book fragments (~1090 lines) |
| `senseline_reformat_v8.py` | 19-pass automated sense-line reformatter (~32K) |
| `readalong.html` | Standalone beta Read Along mic/speech tool (extracted from index.html) |
| `books/*.html` | Generated HTML fragments, one per book (15 total, loaded via fetch) |
| `data/` | JSON data indexes for all layers (intertext, geography, pericopes, parallels, KJV diff) |

## Two Entry Points (important)
- **`index.html`** — The main SPA. Landing page, book picker, settings bottom sheet, all layers. Loads book HTML fragments via fetch into `#book-content-container`.
- **`books/index.html`** — An older/alternate reading view with its own CSS. Both are live and both need CSS changes applied when styling is updated. They share the same `books/*.html` fragments.

## How Content Gets Built
1. Sense-line source files in `data/text-files/v2-mine/` (Stan's hand-edited)
2. Optionally: `senseline_reformat_v8.py` applies 19 mechanical passes (for new/revised books)
3. `build_book.py` applies archaic word swaps, injects intertext/geo/pericope layers, wraps punctuation, generates HTML
4. Output: `books/{BOOKID}.html` as fragments
5. `index.html` loads fragments via `fetch('books/' + bookId + '.html')`
6. Rebuild all: `python3 build_book.py --all`

## Book Metadata

| ID | Abbrev | Name | Chapters |
|----|--------|------|----------|
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

## CSS Variable System
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

## Body Classes (state management)

| Class | Purpose |
|-------|---------|
| `aid-active` | Modern word swaps shown |
| `show-sections` | Pericope section headers visible |
| `show-deity` | Deity/Christ highlighting |
| `show-spirit` | Holy Spirit highlighting |
| `sources-quotations` | Biblical quotation layer |
| `sources-allusions` | Biblical allusion layer |
| `show-kjv-diff` | KJV parallel layer |
| `show-geo` | Geography layer |
| `show-parallels` | Hebrew Poetry parallel structures |
| `light-mode` | Light theme |

## Hash Routing
Format: `#bookId` or `#bookId-chapterNumber` (e.g., `#alma-45`)

---
*Last updated: 2026-03-18*

---
### Update — 2026-03-21
- Major repo cleanup: root reduced from ~40 files to ~11 (scripts moved to `scripts/`, dead files deleted)
- Scripts consolidated into `scripts/` folder: senseline_reformat_v8.py, build_kjv_diff.py, colometric_analysis.py, and 12 others
- `colab/` cleaned: sister_m_pipeline, 2nephi_sister_m, bom_reader_voices_v1, gen_2nephi all deleted; only `samuel_pipeline.ipynb` remains
- `data/` split: production data stays in repo; `research/` folder created for pre-publication materials (PDFs, analysis spreadsheets, paper notes)
- `research/` is gitignored — local only, not tracked in repo
- Old root-level handoff files deleted (COWORK-HANDOFF.md, COWORK-HANDOFF-KJV.md, HANDOFF.md)
- External Obsidian vault (C:\vaults-nano\gospel\11-Readers_BofM) deleted after extracting unique content into repo
- Service worker cache at v70

---
*Last updated: 2026-03-21*
