# Book of Mormon Reader's Edition — Cowork Handoff

**Last updated:** 2026-02-28
**Session:** Major rebuild integrating display settings, bug fixes, and deep linking

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
| `senseline_reformat_v7.py` | 16-pass automated sense-line reformatter (editorial tool) |
| `booklist.txt` | Maps book IDs to source filenames |
| `books/*.html` | Generated HTML fragments, one per book (loaded via fetch) |
| `CNAME` | Domain config for bomreader.com |
| `display-settings-v5.html` | Design prototype for the settings panel (reference only, not deployed) |

### Source Text Files

The `.txt` source files listed in `booklist.txt` (e.g., `01-1_nephi-stan-v1.txt`) are NOT in the repo. They live separately (previously in an Obsidian vault at `C:\vaults-nano\gospel\11-Readers_BofM\`). To regenerate books from source, these files need to be in the repo root or the path updated.

However, all 15 book HTML fragments in `books/` are already built and current.

### How Content Gets Built

1. Sense-line source file (`.txt`) with verse markers and line breaks
2. `senseline_reformat_v7.py` applies 16 mechanical passes (optional — for new/revised books)
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

## Known Future Work

- **Study tab layers** are partially implemented (deity highlighting works, intertextual quotations work for marked books). Isaiah parallels and covenant promises are stubbed.
- **Some books may need sense-line review** — the wrap indent feature means previously over-broken lines can now be rejoined.
- **Source .txt files** should probably be added to the repo or a known location for reproducible builds.
- **localStorage persistence** for reader settings is mentioned in the design but not yet implemented.
- **The `display-settings-v5.html` prototype** can be deleted from the repo when no longer needed as reference.

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
