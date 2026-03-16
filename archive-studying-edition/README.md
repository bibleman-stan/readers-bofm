# Archive: Studying Edition UI Components

This folder preserves code and documentation for features planned in a future "Book of Mormon - Studying Edition." These components were removed during a major UI redesign that simplified the toolbar from a complex collapsible interface to a thin persistent top bar.

## What's Preserved

- **old-toolbar.html** — HTML structure of the collapsible toolbar system
- **old-toolbar-css.css** — Styling for the expandable toolbar and its sub-panels
- **old-toolbar-js.js** — JavaScript state machine for toolbar interaction and auto-collapse/expand
- **text-mode-system.md** — Documentation of the three-layer text mode system (Prose, Sense Lines, Parry Parallels)

## Planned Features for Studying Edition

The Studying Edition would restore and enhance:

1. **Text Mode Toggles** — Switch between:
   - Prose mode: running text (`.line-para`)
   - Sense lines: poetic/cola formatting (`.line`)
   - Parry parallels: Donald Parry's structural analysis (`.line-parry`)

2. **Parry Parallel Lines** — Visual indicators showing Parry's parallel structure relationships across the text

3. **Multi-Panel Toolbar** — Expandable toolbar with:
   - Book/chapter selector grid (15 books)
   - Control buttons: Modern/Original words toggle, Text mode selector, Sections toggle
   - Sub-panels: Settings, Navigation, Background (book introductions)

4. **Study Layers** — Additional interactive annotation and analysis features

## Current State

The Reading Edition (current default) uses only Sense Line mode (Mode 1). However, all three text layers remain in the verse HTML files (`books/*.html`), enabling future restoration of the full text mode system without data changes.

The toolbar was simplified to reduce cognitive load and improve mobile usability, but this archive preserves the interaction patterns and code for future use.
