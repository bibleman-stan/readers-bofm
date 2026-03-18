# BOM Reader — Session Handoff (March 18, 2026)

## UNPUSHED COMMITS — User must push before anything else
There are **3 unpushed commits** on main:
1. `21b57e3` — Switch all books to Samuel voice, drop Sister M (narration.js + sw.js v61)
2. `0e78a9e` — Add 2 Nephi Sister M audio (33 chapters) — NOW SUPERSEDED
3. `b2a6509` — Replace 2 Nephi Sister M with Samuel ch 1-5, remove Sister M files

**Push these immediately** — the voice mapping won't work on production until pushed.

---

## PROJECT OVERVIEW
- **Site**: bomreader.com (Book of Mormon Reading Edition)
- **Repo**: github.com/bibleman-stan/readers-bofm
- **Hosting**: GitHub Pages
- **User**: Stan (thebibleman77@gmail.com)
- **Service worker**: Cache version currently `bomreader-v61`

---

## CURRENT STATE OF AUDIO

### What exists (Samuel voice, all working):
| Book | Chapters | Status |
|------|----------|--------|
| 1 Nephi | 1-22 (all) | ✅ Complete |
| 2 Nephi | 1-5 only | ⚠️ Partial (ch 6-33 need generation) |
| Enos | 1 (all) | ✅ Complete |

### What needs generation (all Samuel voice):
| Book | Chapters | Est. Characters | Priority |
|------|----------|----------------|----------|
| 2 Nephi 6-33 | 28 ch | ~165,000 | High |
| Jacob | 7 ch | ~47,500 | High |
| Jarom | 1 ch | ~3,900 | Medium |
| Omni | 1 ch | ~7,350 | Medium |
| Words of Mormon | 1 ch | ~4,600 | Medium |
| Mosiah | 29 ch | ~164,400 | Later |
| Alma | 63 ch | ~443,200 | Later |
| Helaman | 16 ch | ~106,700 | Later |
| 3 Nephi | 30 ch | ~172,900 | Later |
| 4 Nephi | 1 ch | ~10,300 | Later |
| Mormon | 9 ch | ~48,600 | Later |
| Ether | 15 ch | ~84,700 | Later |
| Moroni | 10 ch | ~31,700 | Later |
| **TOTAL** | | **~1,290,850** | |

### Credit budget strategy (100k monthly):
Best use of next 100k credits: **Jacob (47k) + Jarom (4k) + Omni (7k) + Words of Mormon (5k) = ~63k chars**. This fills the gap between 1 Nephi and Mosiah with ~37k buffer.

---

## VOICE CONFIGURATION

### Decision: Samuel only (no Sister M)
- Sister M voice used `eleven_multilingual_v2` model which hallucinated random Hindi/Urdu-sounding phonemes
- All books now mapped to Samuel in `narration.js`
- Samuel voice ID: `ddDFRErfhdc2asyySOG5`
- Model: `eleven_multilingual_v2` (same model, but Samuel doesn't hallucinate)
- **IMPORTANT**: If hallucination happens with Samuel too, switch to `eleven_turbo_v2_5` (English-only model)

### ElevenLabs API Key
- Key ID: `c6b285e4b3751352d714f85a3ee92292f277de246b7ca46bf181338ed2155425`
- Credits: **EXHAUSTED** — waiting on monthly reset
- GitHub flagged this key as exposed in `annotations.js` line 26 (separate Google API key). User should restrict it in Google Cloud Console.

---

## COLAB PIPELINE

### Updated notebooks (both have Google Drive persistence):
- `colab/samuel_pipeline.ipynb` — Samuel voice, parameterized for any book
- `colab/sister_m_pipeline.ipynb` — Sister M voice (DEPRECATED, do not use)

### Drive persistence architecture (CRITICAL — learned the hard way):
1. **Per-line cache on Google Drive** at `MyDrive/bom-reader-audio/cache/samuel/`
2. **Chapter-level skip** — completed chapters detected on Drive, skipped on re-run
3. **Immediate copy** — each chapter's MP3+JSON copied to Drive right after generation
4. Output folder: `MyDrive/bom-reader-audio/output/{bookid}_{voicename}/`

### How to run a new book:
1. Open `samuel_pipeline.ipynb` from GitHub in Colab
2. Click "Copy to Drive"
3. Find & Replace the API key placeholder
4. Edit Cell 2: change `BOOK_ID`, `BOOK_NAME`, `TOTAL_CHAPTERS`
5. Hit "Run all" — Drive mount will prompt for auth
6. Output goes to Google Drive automatically
7. Download zip from Cell 7, or grab files directly from Drive

---

## FILE STRUCTURE

### Key files:
- `index.html` — Main app (single-page, all CSS inline)
- `books/index.html` — Book reading view (separate CSS)
- `narration.js` — Audio playback module with voice mapping
- `sw.js` — Service worker (cache versioning)
- `build_book.py` — Rebuilds book HTML from v2 text sources
- `data/text-files/v2-mine/` — User's line-break edited text sources

### Audio folder convention:
```
audio/{XX-Book_Name}/{bookid}-{ch}-{voicename}.mp3
audio/{XX-Book_Name}/{bookid}-{ch}-{voicename}.json
```
Example: `audio/01-1_Nephi/1nephi-1-samuel.mp3`

### narration.js voice lookup:
```javascript
const BOOK_VOICES = { '1nephi': 'samuel', '2nephi': 'samuel', ... };
function voiceFor(bookId) { return BOOK_VOICES[bookId] || 'samuel'; }
```
Used in 3 places: `loadChapterAudio()`, `startPlayback()`, `hasAudio()`

---

## RECENT CSS CHANGES

### Committed and live:
- `.swap` dotted underline opacity bumped from 0.4 to 0.55 (blue brightness increase) in `index.html`

### Tried and reverted:
- `.quote-bible { font-style: italic; }` — user didn't like the look, reverted
- Sister M voice — hallucination issues, reverted to Samuel

---

## PENDING TASKS (prioritized)

### Immediate (next session):
1. **User must push** the 3 unpushed commits
2. **Test 2 Nephi 1-5 audio** on bomreader.com after push — verify Samuel plays correctly

### When credits reset:
3. **Generate 2 Nephi 6-33** with Samuel via Colab pipeline (~165k chars)
4. **Generate Jacob, Jarom, Omni, Words of Mormon** (~63k chars total)
5. Both above may not fit in one 100k credit cycle — prioritize accordingly

### Lower priority / ongoing:
6. **Light mode CSS verification** — new UI elements may need light mode overrides
7. **Audio-highlight sync drift** — known issue from earlier sessions
8. **1 Ne 6:1 verse text edit** — needs text fix and audio re-patch
9. **GitHub secrets alert** — Google API key in `annotations.js:26` should be restricted
10. **Intertextual markup** — `.quote-bible` exists for some verses but coverage is incomplete; Isaiah block quotes in 2 Ne 12-24 have zero `.quote-bible` markup despite being 100% quotation. Revisit if italics or other visual treatment is desired later.

---

## EDITORIAL PRINCIPLES (for text line-breaking)

- **Wayyehi rule**: "And it came to pass that" stays on one line as a fixed formula
- **"Expedient that"**: treated as single idiom, don't break at "that"
- **Rhetorical address**: "And now, O king," kept as one unit
- **Rebuild command**: `python3 build_book.py --all` regenerates all 15 book HTML files from v2 text sources

---

## TRUST NOTE
Stan is frustrated — rightly so. Two tranches of ElevenLabs credits were burned because the first Colab run didn't persist to Google Drive. The Drive persistence fix is now in place and proven, but trust has been damaged. The next session should be precise, careful, and not waste anything. Always commit without being asked. Always verify before bulk operations. Always use Drive persistence for any Colab work.
