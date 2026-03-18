# 09 — Bugs Fixed & Historical Decisions

## Bugs Fixed

### Chapter revert bug (Feb 28)
Symptom: Chapter snaps back to 1 on scroll. Cause: `hashchange` race condition with boolean flag. Fix: `lastHashWeSet` string comparison.

### Scroll stutter on load (Feb 28)
Symptom: Layout fights on book switch. Cause: CSS transitions firing on initial load. Fix: `.transitions-enabled` class added 300ms after DOMContentLoaded.

### Navigation race — "2 Ne → 33 goes to 1 Ne 1" (Mar 1)
Cause: `buildChapterGrid()` creates buttons before async book load. Callback overwrites with ch 1. Fix: `pendingChapter` variable.

### "he spoken to you" 1 Ne 17:45 (Mar 1)
Cause: `fix_participles()` 60-char regex window crossed clause boundaries. Fix: Tightened to 30-char with `[^;.]`.

### Scroll dismissing panels (Mar 1)
Fix: Scroll handler checks `anyPanelOpen`, returns early. Click on `#scripture-content` closes panels.

### Layers panel won't dismiss on desktop (Mar 1)
Fix: Document-level click-outside handler + Escape key.

### Incorrect Isaiah pericope titles (Mar 1)
2 Ne 13 labeled "Suffering Servant" (should be Isaiah 3). Rewrote all Isaiah/Malachi entries.

### KJV diff false hits (Mar 2)
Cause: word-level diff compared "Lord," ≠ "Lord" (punctuation attached). Fix: `normalize_for_diff()` strips all non-alpha.

### Authentic text bug in TTS (Mar 14)
`parse_chapter()` called `get_text_from_element(el, use_modern=True)` — TTS was reading modernized text instead of authentic BofM text. Fix: changed to `use_modern=False`.

### Colab Drive persistence (Mar 18)
First generation run completed all 33 chapters but cache was on ephemeral VM. Runtime disconnected, all files lost. Fix: Cache + output now on Google Drive. Chapter-level skip + immediate copy.

## Key Design Decisions Made

### Text presentation
- Sense-lines only (no prose/verse toggle) for Reading Edition
- No indentation — all flush left
- Wrap indent CSS-only
- Punctuation wrapped in `.punct` spans for opacity hiding

### Swap system
- Longest-first matching prevents nested swaps
- `data-orig`/`data-mod` attributes, JS toggles textContent
- `.swap` (visible) vs `.swap-quiet` (no decoration) distinction
- TTS reads `data-orig` (authentic text), not `data-mod` (modern)

### Audio
- Samuel voice only (Sister M rejected for hallucination)
- Pre-generated via ElevenLabs, not browser TTS
- Per-line caching on Google Drive
- Voice settings baked into cache key

### Visual layers
- Existing layers use word/phrase level (color, underline, ::after)
- Parallel layer uses LINE level (indentation, ::before labels) — no collision
- Parallel "lite" filter: 619 of 1,530 structures (60% reduction)
- Parry-style clean scholarly indentation, not colored backgrounds

### UI
- Thin persistent topbar replaced complex collapsible toolbar
- Bottom sheet for settings
- Full-screen picker overlay
- Old code archived for future Studying Edition

---
*Last updated: 2026-03-18*
