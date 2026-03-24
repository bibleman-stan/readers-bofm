# 07 — Pending Tasks

## IMMEDIATE (do first in next session)

### 1. Generate 2 Nephi 25-33 with Samuel
~49,400 chars. Stan has ~100k credits available. Use `samuel_pipeline.ipynb`. Configure `BOOK_ID='2nephi'`, `TOTAL_CHAPTERS=33`. Skip logic will handle ch 1-5 (already exist). Need to set start chapter or let it skip to 25.

### 2. Test audio playback on bomreader.com
Verify Samuel plays correctly for 2 Ne 1-5 (currently deployed) and any newly generated chapters.

## WHEN MORE CREDITS AVAILABLE

### 3. Generate remaining 2 Nephi (ch 6-24)
~116,000 chars. The Isaiah quotation chapters (12-24). May fit in same credit cycle as #1 if budget allows.

### 4. Generate Jacob, Jarom, Omni, Words of Mormon
~63,000 chars total. Fills the gap between 1 Nephi and Mosiah.

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
### Update — 2026-03-18
- Mosiah editorial work begun — sense-line revisions applied to chapters 4 and 15 as first pass, demonstrating newly articulated colometry principles
- Remaining Mosiah chapters (1-3, 5-14, 16-29) still need systematic editorial review

---
*Last updated: 2026-03-18*

---
### Update — 2026-03-19
- Alma editorial review begun: Stan making manual line-break decisions on Alma canonical file
- Claude Code reviewed commits to Alma ch 1-2 (commit 72a4c44); key feedback:
  - Parallel anaphora being flattened in several merges (gold/silver, flocks/wives/children) — worth revisiting
  - Rule 5 violation at 2:11 ("or the people of God" should stay with "Nephites")
  - "inasmuch as it was possible" (1:32) is a restricting qualifier — should stay with main clause
  - Strong choices: both/both/both stacking (1:30), simile break (2:27), participial absolute (1:33)
- `amongst → among` added as quiet swap (14 occurrences); build_book.py updated

---
*Last updated: 2026-03-19*

---
### Update — 2026-03-21
- Alma 1-5 editorial review COMPLETE (FEF pass, sermonic breaks, consistency audit)
- Granular over-break scrub of 1 Ne through Alma 5 COMPLETE (43 flags, 40 fixed, 0.25% error rate, rubric validated)
- FEF consistency pass applied across 1 Ne, 2 Ne, Jacob, Mosiah, Alma 1-5
- Alma 6-63 FEF/mechanical pre-break pass IN PROGRESS
- Helaman through Moroni still needs FEF/mechanical pass + editorial review
- "abase → humble" and "amongst → among" swaps added to build_book.py
- First Alma contextual gloss added (5:27 walked/halakh)
- Book introductions HTML saved to data/book-introductions.html
- Reformatter rules extracted to handoffs/12-reformatter-rules.md
- External vault content consolidated into repo, vault deleted
- All HTML rebuilt and cache at v66
- Multiple commits queued for Stan to push

---
*Last updated: 2026-03-21*

---
### Update — 2026-03-21 (second entry)
- Full-corpus FEF mechanical scrub COMPLETE: 178 fixes across all 15 books (Alma 6-63, Helaman through Moroni)
- All books now have a clean mechanical floor; manual editorial decisions remain for Alma 6+ through Moroni
- Colometric analysis script created (`scripts/colometric_analysis.py`) and CSV generated (`research/colometric_metrics.csv`) — quantitative data ready for paper
- research/ folder established and gitignored (pre-publication materials: CSVs, paper notes, PDFs, analysis outputs)
- Service worker cache now at v70 (was v66 in earlier entry)
- Repo structure cleanup complete (scripts consolidated, dead files removed, colab cleaned)

---
*Last updated: 2026-03-21*

---
### Update — 2026-03-22–24
- Full-corpus AICTP merge pass COMPLETE (all 15 books)
- Anaphoric clause audit COMPLETE (Rule 19 refined, 3 fixes)
- Escalatory appositive pass COMPLETE (28 stacks identified, 9 new breaks applied)
- Punctuation-dependency audit COMPLETE (11 cases, 7 merged, 3 restored, 1 already correct)
- Divine title appositive pass COMPLETE (38 identified, 6 newly stacked)
- "after the manner of" swap removed
- "Harlots" paper idea created in academic vault (Article Ideas folder)
- Remaining: Stan's manual editorial pass on Alma 6+; "Jesus Christ, the Son of God" introducing/referencing calls in context (flagged for future dedicated review); Helaman-Moroni manual editorial pass; remaining ESL structural speed bumps from Tier 1 list

---
*Last updated: 2026-03-24*
