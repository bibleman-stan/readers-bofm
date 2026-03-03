# KJV Diff Fix — Handoff Notes

## What's been done
1. **Punctuation normalization fixed** in `build_kjv_diff.py` line 138-141:
   - Changed `normalize_for_diff()` from stripping only trailing punctuation to stripping ALL non-alpha characters
   - Old: `re.sub(r'[.,;:!?\-—]+$', '', word).lower()`
   - New: `re.sub(r'[^a-zA-Z]', '', word).lower()`
   - This fixes false diffs like "commandments!" vs "commandments--" showing as changes

2. **Hardcoded paths found** in `build_kjv_diff.py` lines 334 and 348:
   - They reference `/sessions/compassionate-dreamy-faraday/mnt/readers-bofm/data/`
   - Need to be changed to relative paths: `data/lds-scriptures.txt` and `data/kjv_diff_index.json`

## What still needs to be done

### 1. Fix hardcoded paths and rebuild KJV diff index
- Fix lines 334 and 348 in `build_kjv_diff.py` to use relative paths
- Run `python3 build_kjv_diff.py` to regenerate `data/kjv_diff_index.json`

### 2. Fix KJV diff display — preserve sense-line formatting
The current behavior when KJV diff layer is toggled ON:
- CSS hides `.verse-normal` lines (the sense-line formatted text)
- CSS shows `.verse-diff` as inline (one long paragraph blob)
- This **destroys the sense-line formatting** which is the core reading experience

The fix should change the CSS in `index.html` (around lines 1002-1008):
```css
/* Current (broken): */
body.show-kjv-diff .has-kjv-diff .verse-normal { display: none !important; }
body.show-kjv-diff .has-kjv-diff .verse-diff { display: inline !important; }

/* Better approach: keep sense-lines visible, show diff as annotation below verse */
body.show-kjv-diff .has-kjv-diff .verse-diff { display: block !important; }
/* DON'T hide verse-normal — keep sense-lines visible */
```

The diff text should appear as a subtle annotation below the sense-line text, not replace it.
Style it with smaller font, muted background, or collapsed by default with expand-on-click.

### 3. Rebuild all books
- `python3 build_book.py --all booklist.txt --out books/`

### 4. Commit
- Files to commit: `build_kjv_diff.py`, `data/kjv_diff_index.json`, `index.html`, `books/*.html`

## Recent completed work (this session)
- Parallel matching quality: 1052→535 clean entries (stop-words, first-label, gap, level-adjacency filters)
- 1 Nephi 20-21 pericopes with Isaiah 48-49 references
- 314 new section headers across 42 sparse chapters (849→1073 total)
- Floating chapter arrows on desktop + keyboard arrow key navigation
- All committed as `0b673fd`
