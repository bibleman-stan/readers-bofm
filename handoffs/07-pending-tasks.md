# 07 — Pending Tasks

## IMMEDIATE (do first in next session)

### 1. Push unpushed commits
Three commits on main waiting to be pushed. Voice mapping and audio files.

### 2. Test 2 Nephi 1-5 audio
After push, verify Samuel plays correctly on bomreader.com for 2 Ne 1-5.

## WHEN CREDITS RESET

### 3. Generate remaining 2 Nephi (ch 6-33)
~165,000 chars. Use `samuel_pipeline.ipynb` with Drive persistence. Configure: `BOOK_ID='2nephi'`, `TOTAL_CHAPTERS=33`. The skip logic will skip ch 1-5 (already on Drive from previous run) and generate 6-33.

### 4. Generate Jacob, Jarom, Omni, Words of Mormon
~63,000 chars total. Fits in one credit cycle with buffer. After 2 Nephi is done (if credits remain) or in the following month.

### 5. Continue through remaining books
Mosiah (164k), Alma (443k), Helaman (107k), 3 Nephi (173k), 4 Nephi (10k), Mormon (49k), Ether (85k), Moroni (32k). At 100k/month this is roughly 13 months of generation.

## BUGS TO FIX

### 6. Audio-highlight sync drift
Line highlight drifts from spoken text during playback. Pericope headers throw off `lineIndex` count. See 03-audio-voice.md for debugging approach.

### 7. 1 Ne 6:1 verse text edit
Needs text fix in source file and audio re-patch.

### 8. KJV diff display
Toggling KJV diff layer destroys sense-line formatting. Proposed fix: show diff as annotation below verse, don't hide verse-normal.

### 9. build_kjv_diff.py hardcoded paths
Lines 334 and 348 reference old session paths. Need relative paths + rebuild.

## EDITORIAL / LOW PRIORITY

### 10. "Behold" vs "Lo" methodology
Stan's linguistic framework for sense-line breaking. Test on Alma 5 or 2 Ne 4:15-35. See 02-text-editorial.md.

### 11. rebreak.py uncommitted changes
396-line diff, unclear if WIP. Check and commit or discard.

### 12. Light mode CSS verification
New UI elements (topbar, picker, sheet, landing) need light mode override verification.

### 13. Book introductions accessibility
Previously in background panel, now hidden. Need to surface in About page or picker.

### 14. GitHub secrets alert
Google API key in `annotations.js:26` — restrict in Google Cloud Console.

### 15. Parry alignment as sense-line diagnostic
Use Parry break-points to identify sense-lines that merit revision. 209 split candidates in 2 Nephi alone.

---
*Last updated: 2026-03-18*
