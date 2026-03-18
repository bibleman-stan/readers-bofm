# 03 — Audio & Voice Generation

## Current Voice: Samuel Only
- **Voice ID:** `ddDFRErfhdc2asyySOG5`
- **Model:** `eleven_multilingual_v2`
- All books mapped to Samuel in `narration.js`

### Decision History
- **Samuel** — Nigerian-accented English. Active since initial audio work. No hallucination issues.
- **Sister M** (`iJpuSZDxZSBJHFSeavba`) — **REJECTED.** Used `eleven_multilingual_v2` model which hallucinated random Hindi/Urdu-sounding phonemes interspersed with the narration. All Sister M audio was generated, deployed, then removed.
- **Tony** (`lRf3yb6jZby4fn3q3Q7M`) — Shelved. "Put on the shelf for now."
- **Lester** (`LBN8aWETnm9oOSBzmFQR`) — Generated for Enos but not deployed.

### IMPORTANT: If Samuel hallucination occurs
Switch to `eleven_turbo_v2_5` (English-only model). The multilingual model is the hallucination risk.

## ElevenLabs API
- **Key:** `c6b285e4b3751352d714f85a3ee92292f277de246b7ca46bf181338ed2155425`
- **Credits:** EXHAUSTED as of Mar 18, 2026. Waiting on monthly reset.
- **Billing cycle:** Monthly (exact date unknown — Stan said "next month")

### Voice Settings (baked into cache key)
```python
VOICE_SETTINGS = {
    'stability': 0.50,
    'similarity_boost': 0.75,
    'style': 0.35,
    'use_speaker_boost': True,
}
```

## Audio Inventory

### What Exists (all Samuel voice):
| Book | Chapters | Status |
|------|----------|--------|
| 1 Nephi | 1-22 | ✅ Complete |
| 2 Nephi | 1-5 | ⚠️ Partial — ch 6-33 need generation |
| Enos | 1 | ✅ Complete |

### What Needs Generation:
| Book | Chapters | Est. Characters |
|------|----------|----------------|
| 2 Nephi 6-33 | 28 ch | ~165,000 |
| Jacob | 7 ch | ~47,500 |
| Jarom | 1 ch | ~3,900 |
| Omni | 1 ch | ~7,350 |
| Words of Mormon | 1 ch | ~4,600 |
| Mosiah | 29 ch | ~164,400 |
| Alma | 63 ch | ~443,200 |
| Helaman | 16 ch | ~106,700 |
| 3 Nephi | 30 ch | ~172,900 |
| 4 Nephi | 1 ch | ~10,300 |
| Mormon | 9 ch | ~48,600 |
| Ether | 15 ch | ~84,700 |
| Moroni | 10 ch | ~31,700 |
| **TOTAL** | | **~1,290,850** |

### Credit Budget Strategy
~100k credits/month. Best next batch: **Jacob (47k) + Jarom (4k) + Omni (7k) + Words of Mormon (5k) = ~63k chars**. Fills the gap between 1 Nephi and Mosiah with ~37k buffer.

## File Structure
```
audio/{XX-Book_Name}/{bookid}-{ch}-{voicename}.mp3
audio/{XX-Book_Name}/{bookid}-{ch}-{voicename}.json
```
Example: `audio/01-1_Nephi/1nephi-1-samuel.mp3`

### Folder Mapping (in narration.js)
```javascript
const BOOK_FOLDERS = {
  '1nephi': '01-1_Nephi',
  '2nephi': '02-2_Nephi',
  'jacob':  '03-Jacob',
  'enos':   '04-Enos',
  // ... etc
};
```

## Colab Pipeline

### Canonical Notebook
`colab/samuel_pipeline.ipynb` — parameterized for any book. **Has Google Drive persistence.**

### DEPRECATED (do not use)
- `colab/sister_m_pipeline.ipynb` — Sister M voice, hallucination issues
- `colab/bom_reader_voices_v1.ipynb` — original notebook, no Drive persistence
- `colab/gen_2nephi.py` — small script, assumes notebook context

### Drive Persistence (CRITICAL — learned the hard way)
Previous generation lost ~2 hours of output when Colab runtime disconnected because cache was on the ephemeral VM. Now fixed with three layers:

1. **Per-line cache on Google Drive** at `MyDrive/bom-reader-audio/cache/samuel/`. Each TTS API call is cached by SHA256 of text+voice+settings. Re-runs of the same text cost zero credits.
2. **Chapter-level skip** — Cell 6 checks Drive for existing MP3+JSON before generating. Completed chapters are skipped entirely on re-run.
3. **Immediate copy** — each chapter's MP3+JSON copied to Drive right after generation, before moving to next chapter.

Output folder: `MyDrive/bom-reader-audio/output/{bookid}_{voicename}/`

### How to Generate a New Book
1. Open `samuel_pipeline.ipynb` from GitHub in Colab
2. Click "Copy to Drive"
3. Find & Replace the API key placeholder with actual key
4. Edit Cell 2: change `BOOK_ID`, `BOOK_NAME`, `TOTAL_CHAPTERS`
5. "Run all" — Drive mount will prompt for auth
6. Output goes to Google Drive automatically
7. Cell 7 creates zip and triggers download
8. Extract to `audio/{XX-Book_Name}/` in repo
9. Commit and push

### Colab Gotchas
- **Find & Replace is the only reliable way to edit cells** — Monaco editor API changes may not propagate to runtime
- **Always check [NEW] vs [cache] tags** — if you expect new generation but see all [cache], the text didn't change
- **File casing** — narration.js uses lowercase voice names. Ensure downloaded files match.

## narration.js

### Voice Mapping
```javascript
const BOOK_VOICES = {
  '1nephi': 'samuel',
  '2nephi': 'samuel',
  // ... all books → 'samuel'
};
function voiceFor(bookId) { return BOOK_VOICES[bookId] || 'samuel'; }
```
Used in 3 places: `loadChapterAudio()`, `startPlayback()`, `hasAudio()`

### Audio-Highlight Sync Drift (KNOWN BUG)
The line highlight drifts from actual spoken text during playback. Root cause: `findLineElement()` walks DOM nodes counting lines, but pericope headers occupy a `lineIndex` slot in HTML without a corresponding manifest entry. The `lineIndex` values drift after any pericope header.

**Fix approach (not yet implemented):** Either skip pericope headers in the line count, or include them as zero-duration entries in the JSON manifest.

**To debug:** Play audio on bomreader.com, note the exact verse where sync drifts, compare manifest timestamps against DOM line indices at that point.

### Timing Manifest Format
```json
{
  "book": "enos",
  "chapter": 1,
  "voice": { "provider": "elevenlabs", "voice_id": "...", ... },
  "duration": 429.104,
  "lines": [
    { "start": 0.0, "end": 2.345, "type": "line",
      "text": "Behold, it came to pass...",
      "verse": "1:1", "lineIndex": 0 }
  ]
}
```

## Mistakes & Lessons Learned (Mar 18)
1. **First Colab run completed all 33 2 Nephi chapters but cache was on ephemeral VM.** Runtime disconnected before zip download. All files lost. ~197k credits wasted.
2. **Second run succeeded with Drive persistence.** But credits ran out at Ch 33 line 69/87 — last ~18 lines got silent placeholders.
3. **Sister M voice hallucinated non-English phonemes** throughout the generated audio. Entire Sister M effort (~197k more credits) was wasted.
4. **Total credit waste:** approximately 400k characters across two failed approaches.
5. **Lesson:** ALWAYS use Drive persistence. ALWAYS test one chapter before bulk generation. NEVER use multilingual model without testing for hallucination first.

---
*Last updated: 2026-03-18*
