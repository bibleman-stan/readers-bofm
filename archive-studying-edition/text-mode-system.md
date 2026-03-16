# Three-Layer Text Mode System

This document describes the three-layer text mode system embedded in the verse HTML files. While the Reading Edition displays only Mode 1 (Sense Lines) by default, all three layers remain in the data, enabling future restoration without structural changes.

## Overview

Each verse in the source files (`books/*.html`) contains three parallel representations of the text:

| Mode | Layer | CSS Class | Format | Purpose |
|------|-------|-----------|--------|---------|
| **0** | Prose | `.line-para` | Running text | Modern paragraph reading |
| **1** | Sense Lines | `.line` | Poetic cola/line breaks | Poetic structure emphasis (current default) |
| **2** | Parry Parallels | `.line-parry` | Parallel segment markers | Donald Parry's structural analysis |

All three layers coexist in the HTML. The `applyTextMode()` function controls which is visible via CSS classes on the document body.

## HTML Structure Example

```html
<div class="verse" data-verse="1:1">
  <!-- Mode 0: Prose layer -->
  <div class="line-para">
    I, Nephi, having been born of goodly parents, therefore I was
    taught somewhat in all the learning of my father; and having seen
    many afflictions in the course of my days, nevertheless, having
    been highly favored of the Lord in all my days, yea, having had a
    great knowledge of the goodness and the mysteries of God, therefore
    I make a record of my proceedings in my days.
  </div>

  <!-- Mode 1: Sense Lines layer -->
  <div class="line">
    I, Nephi,<br>
    having been born of goodly parents,<br>
    therefore I was taught somewhat<br>
    in all the learning of my father;<br>
    <br>
    and having seen many afflictions<br>
    in the course of my days,<br>
    nevertheless, having been highly favored of the Lord<br>
    in all my days,<br>
    <br>
    yea, having had a great knowledge<br>
    of the goodness and the mysteries of God,<br>
    therefore I make a record<br>
    of my proceedings in my days.
  </div>

  <!-- Mode 2: Parry Parallels layer -->
  <div class="line-parry">
    <span class="parry-a">I, Nephi, having been born of goodly parents,</span>
    <span class="parry-b">therefore I was taught somewhat in all the learning of my father;</span>
    <span class="parry-a">and having seen many afflictions in the course of my days,</span>
    <span class="parry-b">nevertheless, having been highly favored of the Lord in all my days,</span>
    <span class="parry-a">yea, having had a great knowledge of the goodness and the mysteries of God,</span>
    <span class="parry-b">therefore I make a record of my proceedings in my days.</span>
  </div>
</div>
```

## CSS Classes

### Display Control Classes

Applied to `<body>` to show/hide layers:

```css
/* Show Prose mode (.line-para visible, others hidden) */
body.show-prose .line-para { display: block; }
body.show-prose .line { display: none; }
body.show-prose .line-parry { display: none; }

/* Show Sense Lines mode (.line visible, others hidden) - DEFAULT */
body.show-lines .line-para { display: none; }
body.show-lines .line { display: block; }
body.show-lines .line-parry { display: none; }

/* Show Parry Parallels mode (.line-parry visible, others hidden) */
body.show-parry .line-para { display: none; }
body.show-parry .line { display: none; }
body.show-parry .line-parry { display: block; }
```

### Layer Classes

Used to target content within each mode:

- `.line-para` — Prose paragraph text
- `.line` — Sense line formatted text (with `<br>` tags for line breaks)
- `.line-parry` — Parallel segment text with markers (`.parry-a`, `.parry-b`, etc.)

### Parry Parallel Markers

When in Mode 2, parallel segments are marked with classes for styling:

```css
.parry-a { /* First element of parallel pair - e.g., chiasmus A part */ }
.parry-b { /* Second element of parallel pair - e.g., chiasmus B part */ }
.parry-center { /* Center element in concentric structure */ }
```

## JavaScript Function

### applyTextMode(mode)

Switches between text modes:

```javascript
/**
 * Apply text mode to the current reading
 * @param {number} mode - 0 (Prose), 1 (Lines), or 2 (Parry)
 */
function applyTextMode(mode) {
  // Remove all mode classes
  document.body.classList.remove('show-prose', 'show-lines', 'show-parry');

  // Apply selected mode
  switch (mode) {
    case 0:
      document.body.classList.add('show-prose');
      break;
    case 1:
      document.body.classList.add('show-lines');
      break;
    case 2:
      document.body.classList.add('show-parry');
      break;
  }

  // Persist user preference
  localStorage.setItem('text-mode', mode.toString());
}
```

### Load User Preference

On page load, restore the user's last-selected text mode:

```javascript
function restoreTextMode() {
  const saved = localStorage.getItem('text-mode');
  const mode = saved ? parseInt(saved) : 1; // Default to Mode 1
  applyTextMode(mode);
}

document.addEventListener('DOMContentLoaded', restoreTextMode);
```

## Current State (Reading Edition)

In the Reading Edition, only Mode 1 (Sense Lines) is exposed to users. The toolbar UI for switching modes is hidden, and all other layers remain display:none in the CSS.

```css
/* Reading Edition: only Sense Lines visible */
.line { display: block; }
.line-para { display: none; }
.line-parry { display: none; }
```

## Future Integration (Studying Edition)

To restore full text mode functionality:

1. **UI** — Restore the three-button text mode selector in the toolbar (from `old-toolbar.html`)
2. **CSS** — Apply the mode-based display classes (from `old-toolbar-css.css`)
3. **JavaScript** — Wire up the `applyTextMode()` function and mode persistence (from `old-toolbar-js.js`)
4. **Data** — No changes needed; all three layers already exist in `books/*.html`

The three-layer system is designed for backward compatibility: adding the Studying Edition features requires only UI/JS changes, not data restructuring.

## Data Completeness

All verse HTML files contain complete three-layer markup:

- Book files: `mnt/readers-bofm/books/*.html`
- Example: `/books/1nephi.html` contains `.line`, `.line-para`, and `.line-parry` for every verse
- Verification: Search for `.line-parry` class in any book file to confirm presence

## Performance Considerations

- **Multiple layers**: Keeping three layers in DOM increases HTML size (~3x text per verse)
- **CSS-based switching**: Using `display: none` vs. `display: block` is fast; no DOM manipulation needed
- **localStorage persistence**: Mode preference stored locally; no server roundtrip
- **Mobile optimization**: Consider lazy-loading alternate modes or using CSS containment for performance

## References

- **Donald E. Parry** — Structured text analysis and chiasmus identification
- **Poetic structure** — Use of cola (short phrases) to reveal parallel thought units
- **Prose reading** — Traditional paragraph-based comprehension
