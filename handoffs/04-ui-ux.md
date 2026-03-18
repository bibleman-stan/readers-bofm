# 04 — UI/UX Design

## Current UI Structure (post-Mar 16 redesign)

### Thin Persistent Top Bar (`.topbar`)
44px fixed bar with backdrop blur:
- **Left:** Book name + chapter (e.g., "2 Nephi · Chapter 1") — tap opens full-screen picker
- **On landing:** Shows "bomreader.com"
- **Right:** "Modern" pill button, Search icon, Settings (hamburger) icon

### Progress Line (`.progress-line`)
2px bar at very top showing scroll position (0-100%).

### Full-Screen Book/Chapter Picker (`.picker`)
Opens when tapping book/chapter in topbar:
- Vertical list of all 15 books
- Tap a book row to expand chapter number pills
- Built dynamically from `bookMeta` via `buildPicker()`

### Bottom Sheet (`.sheet`)
Slides up from bottom when tapping settings hamburger:
- Modern words toggle (iOS-style switch)
- Listen toggle (starts narration)
- Section headings toggle
- Text size selector (S / M / L)
- Light mode toggle
- Refresh content / Save for offline buttons
- Backdrop scrim behind sheet

### Landing Page (`.landing`)
Shown when no hash (initial visit):
- Title, tagline, description
- Book grid (all 15 books as clickable cards)
- "Learn more about the features" link

### About Page
Full-page feature guide. Shows when clicking header link. Toolbar stays functional.

### Text Mode
Sense-lines are the ONLY mode for the Reading Edition. `applyTextMode(1)` forced on load. Three-layer data (prose, sense lines, Parry parallels) still exists in HTML for future Studying Edition.

## Navigation

### Hash Routing
`#bookId` or `#bookId-chapterNumber` (e.g., `#alma-45`)

### Swipe Navigation
Touch: 60px min horizontal, <500ms, <80px vertical drift. Left=next, Right=previous chapter.

### Floating Chapter Arrows
Fixed mid-screen edge buttons for desktop navigation. Also keyboard arrow keys.

### Scroll Behavior
- Toolbar collapses on scroll-down past 80px (20px dead zone)
- Expands on scroll-up
- Freezes while any panel is open
- 400ms cooldown after state changes
- Back-to-top button after 600px scroll

## Previous UI (pre-Mar 16) — ARCHIVED
The old complex floating toolbar with its ~250-line scroll state machine was removed. Preserved in `archive-studying-edition/`:
- `old-toolbar.html`, `old-toolbar-css.css`, `old-toolbar-js.js`
- `text-mode-system.md` — three-layer text mode documentation

## Known Issues

### Toolbar stuck-open on mobile (POSSIBLY RESOLVED)
Pre-Mar 16 issue: toolbar occasionally gets "pegged open" on mobile. The Mar 16 redesign replaced the entire toolbar mechanism, which likely resolved this. Not confirmed — worth checking if Stan reports it again.

### Light mode CSS
New topbar, picker, sheet, and landing page elements need light mode override verification. Key color mapping:

| Element | Dark | Light |
|---------|------|-------|
| Background | `#1a1a1a` | `#f5f0e8` |
| Text | `#d4d0c8` | `#3a3630` |
| Toolbar bg | `rgba(28,31,36,0.95)` | `#e8e4dc` |
| Links | `#7cafc2` | `#4a7a9e` |

### Book introductions
Previously in `#background-panel`, now in hidden `settings-panel-old` div. Need to be made accessible (via About page or picker).

## Swap Underline Styling
- `.swap` — dotted underline, opacity 0.55 (bumped from 0.4 on Mar 18 per Stan's feedback)
- `.swap.swap-quiet` — no decoration
- `.aid-active .swap` — solid blue color, no underline
- Light mode: different color values with `!important`

---
*Last updated: 2026-03-18*
