# 05 — Build Pipeline & Data Layers

## build_book.py

### Processing Pipeline Per Line
```python
def process_line(line, swap_list):
    return wrap_punctuation(fix_participles(apply_swaps(line, swap_list)))
```

### Data Loading
Loads 6 JSON files into globals:
1. `hardy_intertext.json` → intertext index (quotations/allusions)
2. `hardy_phrase_index.json` → phrase-level match data
3. `kjv_diff_index.json` → KJV parallel passage diffs
4. `geo_index.json` → geographic references
5. `pericope_index.json` → section headers (710 entries)
6. `parallel_index.json` → Hebrew Poetry structures (619 lite)

All graceful — missing files print warning but don't break.

### Per-Verse Enrichment (gen_verse)
Each verse goes through:
1. Apply word swaps to all lines
2. Inject intertext references with phrase-level highlighting
3. Apply geography highlighting and categorization
4. Add KJV diff parallel passages with strikethrough/bold markup
5. Inject parallel structure data attributes
6. Wrap with verse number and line spans

### Rebuild Command
```bash
python3 build_book.py --all
```

## Pericope (Section Headers) System

### Data
`pericope_index.json` — 710 entries across 15 books.
Keyed: `book_id → chapter (string) → [{verse: int, title: string}]`

### Two-Tier Headers
Titles can have main title, subtitle (split on colon), and parenthetical scripture reference:
- `.pericope-two-tier` — main + subtitle
- `.pericope-with-ref` — title + reference
- Plain `.pericope-header` — single line

### Isaiah/Malachi Revisions (Mar 1)
Rewrote all entries for 2 Ne 12-24, 2 Ne 27, 3 Ne 22-25. Total: 648 → 710 entries.

## Hebrew Poetry / Parallel Structure Layer

### Data Pipeline
1. Source: `data/parry-parallels-full.txt` (14,544 lines, 1,530 structures)
2. Parser: `build_parallel_index.py` applies "lite" filter (chiasmus ≤3 deep + simple couplets)
3. Output: 619 structures (60% reduction)

### Build Integration
- Fuzzy-matches Parry's text fragments against sense-lines
- Injects `data-parallel-group` and `data-parallel-level` attributes
- CSS: Parry-style cascading indentation with lowercase italic labels

### Chiasmus Prime Notation
Return side of chiasmus displays as a', b', c' (primes after the deepest point).

### Alignment Gap
22% of structures have perfect sense-line alignment. 78% have mismatches. Parry's break-points can serve as a diagnostic for sense-lines that merit revision.

## KJV Diff Layer

### Coverage
551 verses with KJV parallel data. Includes:
- Full chapter parallels (2 Ne 12-24 = Isaiah 2-14, etc.)
- Partial parallels (Mosiah 14 = Isaiah 53, 3 Ne 16:18-20 = Isaiah 52:8-10, etc.)

### Known Issue
When KJV diff layer is toggled ON, CSS hides `.verse-normal` and shows `.verse-diff` as inline paragraph blob — **destroys sense-line formatting**. Fix proposed but not implemented: show diff as annotation below verse, don't hide sense-lines.

### build_kjv_diff.py
- Has hardcoded paths from old session that need fixing to relative paths
- Punctuation normalization was fixed (strips all non-alpha before comparison)

## Firebase Annotations System
- `annotations.js` connects to Firebase for user annotations (verse notes)
- **SECURITY:** Google API key exposed at `annotations.js` line 26. GitHub flagged it. Key should be restricted in Google Cloud Console to the bomreader.com domain.
- System exists but not deeply documented — built before Claude's involvement.

---
*Last updated: 2026-03-18*

---
### Update — 2026-03-21
- build_book.py "notwithstanding" context-sensitive swap updated: "a" and "an" moved from determiner list to clause-subject list to prevent false swap inside "notwithstanding a/an" constructions
- Service worker cache bumped to v70
- scripts/ folder created and build helper scripts consolidated there (build_kjv_diff.py, build_geo_index.py, etc. — build_book.py remains at root as the primary build entry point)

---
*Last updated: 2026-03-21*
