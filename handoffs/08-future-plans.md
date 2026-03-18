# 08 — Future Plans & Shelved Ideas

## MAJOR: Spanish Fork
Raw data available in `data/spa/` — official LDS Spanish translation of entire scripture canon in JSON format.

### Requirements Identified:
- **Big lift:** Sense-lining 6,604 BofM verses (currently paragraph format). Algorithmic first pass at Spanish clause boundaries could get 70-80%, then manual refinement.
- **Carries over as-is:** parallel/Hebrew poetry layer (structural), pericope placement, intertext locations, geography layer, entire UI architecture
- **Needs Spanish-specific work:** translated UI strings, Spanish swap lexicon (LDS translation has some archaic forms), translated pericope titles, Reina-Valera parallel for diff layer
- **Architectural decision not yet made:** true fork (separate site) vs in-app language toggle

### Status: Not actively in progress. Filed as major future project.

## MAJOR: Studying Edition
The current Reading Edition forces sense-line mode only. A future "Studying Edition" would restore:
- Three-layer text toggle (prose, sense lines, Parry parallels)
- Expanded toolbar with layer controls always visible
- More scholarly features

### Archived Code
`archive-studying-edition/` contains:
- Old toolbar HTML, CSS, JS
- Three-layer text mode documentation
- Preserved for future use

## SHELVED: Read Along (Speech Recognition)
Extracted to `readalong.html` as standalone beta. Browser speech recognition is Chrome-only, intermittent, accuracy issues with archaic English. "Kind of works but not really yet."

## SHELVED: Voice Variety
Original plan was to alternate Samuel and Sister M voices across books. Sister M rejected due to multilingual model hallucination. Currently all-Samuel. Could revisit with:
- A different female voice
- English-only model (`eleven_turbo_v2_5`)
- More careful testing before bulk generation

## SHELVED: Intertextual Italics
Tried `font-style: italic` on `.quote-bible` class. Stan rejected the visual result. The markup exists for the toggle-activated quotation layer but won't have always-on visual treatment.

## ON ICE: Annotations (Firebase)
Firebase-backed user annotation system exists in `annotations.js`. Functional but not actively developed. The pencil icon was removed from the topbar ("feature on ice").

## ON ICE: localStorage Persistence
Settings (text size, light mode, aid toggle state) reset on page load. No localStorage implementation yet.

---
*Last updated: 2026-03-18*
