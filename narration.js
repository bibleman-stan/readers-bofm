/**
 * Narration module for bomreader.com — Pre-generated Audio Player
 *
 * Plays pre-generated MP3 chapter audio with synchronized line highlighting.
 * Audio files are generated offline using ElevenLabs TTS and stored in audio/.
 * Each chapter has an MP3 file and a JSON timing manifest.
 *
 * Architecture:
 *   1. User clicks "Listen" → loads audio/<book>-<chapter>.mp3 + .json
 *   2. HTML5 Audio element handles playback (works on all devices)
 *   3. Timing manifest maps timestamps to line indices for highlighting
 *   4. Speed control via Audio.playbackRate (0.75x–2x)
 *   5. Persistent bottom-bar player with mini + expanded views
 */

const NARRATION = (() => {
  const SPEEDS = [0.75, 1, 1.25, 1.5, 2];
  const AUDIO_BASE = 'audio/';
  const VOICE = 'samuel';  // active voice: 'samuel', 'tony', etc.

  // Map bookId → subfolder inside audio/
  const BOOK_FOLDERS = {
    '1nephi':          '01-1_Nephi',
    '2nephi':          '02-2_Nephi',
    'jacob':           '03-Jacob',
    'enos':            '04-Enos',
    'jarom':           '05-Jarom',
    'omni':            '06-Omni',
    'words-of-mormon': '07-Words_of_Mormon',
    'mosiah':          '08-Mosiah',
    'alma':            '09-Alma',
    'helaman':         '10-Helaman',
    '3nephi':          '11-3_Nephi',
    '4nephi':          '12-4_Nephi',
    'mormon':          '13-Mormon',
    'ether':           '14-Ether',
    'moroni':          '15-Moroni',
  };

  // ── State ──
  let audioEl = null;          // HTML5 Audio element
  let manifest = null;         // timing manifest for current chapter
  let currentSpeed = 1;
  let playing = false;
  let highlightTimer = null;   // requestAnimationFrame ID
  let currentLineIdx = -1;     // currently highlighted line index
  let savedTextMode = null;    // saved text mode to restore when narration stops

  // ── Helpers ──

  /**
   * Determine the current book ID and chapter number from the URL/DOM.
   * Returns { bookId, chapter } or null.
   */
  function getCurrentChapter() {
    // Try hash: #enos-1, #1nephi-3, etc.
    const hash = window.location.hash.replace('#', '');
    if (hash) {
      const m = hash.match(/^(.+?)-(\d+)$/);
      if (m) return { bookId: m[1], chapter: parseInt(m[2]) };
      // Single-chapter books: #enos-1 or just the book loaded
    }

    // Try visible chapter element
    const activeBook = document.querySelector('.book-content[style*="display: block"]')
                    || document.querySelector('.book-content:not([style*="display: none"])');
    if (!activeBook) return null;

    const activeChapter = activeBook.querySelector('.chapter-content[style*="display: block"]')
                       || activeBook.querySelector('.chapter-content:not([style*="display: none"])');
    if (!activeChapter) return null;

    const id = activeChapter.id || '';
    const m = id.match(/^ch-(.+)-(\d+)$/);
    if (m) return { bookId: m[1], chapter: parseInt(m[2]) };

    return null;
  }

  function getChapterLabel() {
    const ch = getCurrentChapter();
    if (!ch) return 'Unknown';
    const bookMap = {
      '1nephi': '1 Nephi', '2nephi': '2 Nephi', 'jacob': 'Jacob',
      'enos': 'Enos', 'jarom': 'Jarom', 'omni': 'Omni',
      'words-of-mormon': 'Words of Mormon', 'mosiah': 'Mosiah',
      'alma': 'Alma', 'helaman': 'Helaman', '3nephi': '3 Nephi',
      '4nephi': '4 Nephi', 'mormon': 'Mormon', 'ether': 'Ether',
      'moroni': 'Moroni'
    };
    return (bookMap[ch.bookId] || ch.bookId) + ' ' + ch.chapter;
  }

  // ── Audio loading ──

  async function loadChapterAudio() {
    const ch = getCurrentChapter();
    if (!ch) {
      console.warn('Narration: cannot determine current chapter');
      return false;
    }

    const folder = BOOK_FOLDERS[ch.bookId] || ch.bookId;
    const mp3Url = `${AUDIO_BASE}${folder}/${ch.bookId}-${ch.chapter}-${VOICE}.mp3`;
    const jsonUrl = `${AUDIO_BASE}${folder}/${ch.bookId}-${ch.chapter}-${VOICE}.json`;

    updatePlayerState('loading', 'Loading audio...');

    try {
      // Load manifest
      const resp = await fetch(jsonUrl);
      if (!resp.ok) {
        console.warn(`Narration: no audio for ${ch.bookId}-${ch.chapter} (${resp.status})`);
        updatePlayerState('error', 'No audio available for this chapter');
        return false;
      }
      manifest = await resp.json();
      console.log('Narration: loaded manifest,', manifest.lines.length, 'timed segments,',
                  manifest.duration + 's total');

      // Load audio
      if (!audioEl) {
        audioEl = new Audio();
        audioEl.preload = 'auto';

        // Wire up events
        audioEl.addEventListener('ended', onAudioEnded);
        audioEl.addEventListener('error', onAudioError);
        audioEl.addEventListener('canplay', () => {
          console.log('Narration: audio ready to play');
        });
      }

      audioEl.src = mp3Url;
      audioEl.playbackRate = currentSpeed;
      audioEl.load();

      return true;
    } catch (e) {
      console.error('Narration: failed to load audio:', e);
      updatePlayerState('error', 'Failed to load audio');
      return false;
    }
  }

  // ── Playback ──

  async function startPlayback() {
    if (playing) return;

    showPlayer();

    // Load audio if needed (different chapter or first play)
    const ch = getCurrentChapter();
    if (!ch) return;

    const expFolder = BOOK_FOLDERS[ch.bookId] || ch.bookId;
    const expectedSrc = `${AUDIO_BASE}${expFolder}/${ch.bookId}-${ch.chapter}-${VOICE}.mp3`;
    if (!audioEl || !audioEl.src.endsWith(expectedSrc)) {
      const ok = await loadChapterAudio();
      if (!ok) return;
    }

    // Switch to sense-line mode for accurate line highlighting.
    // The manifest lineIndex maps to individual .line elements, not .line-para.
    // The app IIFE doesn't expose textMode globally, so we use the toggleLines
    // window function and detect current mode from body classes.
    if (!document.body.classList.contains('show-lines')) {
      // Save what mode we're in: 'parry' if show-parry, else 'verses'
      savedTextMode = document.body.classList.contains('show-parry') ? 'parry' : 'verses';
      // Cycle to lines mode via the global toggle
      if (typeof window.toggleLines === 'function') {
        // toggleLines cycles: verses→lines→parallels→verses
        // If in verses mode (0), one call gets us to lines (1)
        // If in parry mode (2), two calls cycle through verses→lines
        if (savedTextMode === 'parry') {
          window.toggleLines(); // parry → verses
        }
        window.toggleLines(); // verses → lines
      }
    }

    try {
      await audioEl.play();
      playing = true;
      updatePlayerState('playing');
      startHighlightLoop();
      bindChapterClick();
    } catch (e) {
      console.error('Narration: play failed:', e);
      updatePlayerState('error', 'Playback failed');
    }
  }

  function pausePlayback() {
    if (!audioEl) return;
    audioEl.pause();
    playing = false;
    updatePlayerState('paused');
    stopHighlightLoop();
  }

  function resumePlayback() {
    if (!audioEl) return;
    audioEl.play();
    playing = true;
    updatePlayerState('playing');
    startHighlightLoop();
  }

  function stopPlayback() {
    if (audioEl) {
      audioEl.pause();
      audioEl.currentTime = 0;
    }
    playing = false;
    manifest = null;
    currentLineIdx = -1;
    clearHighlight();
    stopHighlightLoop();
    unbindChapterClick();
    updatePlayerState('stopped');
    // Restore text mode if we changed it
    restoreTextMode();
  }

  function restoreTextMode() {
    if (savedTextMode === null) return;
    if (typeof window.toggleLines !== 'function') { savedTextMode = null; return; }
    // Currently in lines mode (1). Cycle back to the saved mode.
    if (savedTextMode === 'verses') {
      // lines → parallels → verses: two toggles
      window.toggleLines(); // lines → parallels
      window.toggleLines(); // parallels → verses
    } else if (savedTextMode === 'parry') {
      // lines → parallels: one toggle
      window.toggleLines(); // lines → parallels
    }
    savedTextMode = null;
  }

  function togglePlayPause() {
    if (!playing && (!audioEl || audioEl.paused)) {
      if (audioEl && audioEl.src && audioEl.currentTime > 0) {
        resumePlayback();
      } else {
        startPlayback();
      }
    } else {
      pausePlayback();
    }
  }

  function onAudioEnded() {
    playing = false;
    currentLineIdx = -1;
    clearHighlight();
    stopHighlightLoop();
    updatePlayerState('stopped');
  }

  function onAudioError(e) {
    console.error('Narration: audio error', e);
    playing = false;
    stopHighlightLoop();
    updatePlayerState('error', 'Audio playback error');
  }

  // ── Seeking ──

  function seekRelative(seconds) {
    if (!audioEl) return;
    audioEl.currentTime = Math.max(0, Math.min(audioEl.currentTime + seconds, audioEl.duration || 0));
    updateProgress();
  }

  function seekToFraction(frac) {
    if (!audioEl || !audioEl.duration) return;
    audioEl.currentTime = frac * audioEl.duration;
    updateProgress();
  }

  function setSpeed(speed) {
    currentSpeed = speed;
    if (audioEl) audioEl.playbackRate = speed;
    updateSpeedDisplay();
  }

  function cycleSpeed() {
    const idx = SPEEDS.indexOf(currentSpeed);
    const next = SPEEDS[(idx + 1) % SPEEDS.length];
    setSpeed(next);
  }

  // ── Click-to-seek on lines ──

  /**
   * Given a DOM element (a .line, .line-para, or .pericope-header),
   * determine its lineIndex within the chapter by walking the same
   * tree that findLineElement uses, but in reverse.
   * Returns the manifest line index, or -1 if not found.
   */
  function getLineIndexFromElement(targetEl) {
    const activeBook = document.querySelector('.book-content[style*="display: block"]')
                    || document.querySelector('.book-content:not([style*="display: none"])');
    if (!activeBook) return -1;

    const activeChapter = activeBook.querySelector('.chapter-content[style*="display: block"]')
                       || activeBook.querySelector('.chapter-content:not([style*="display: none"])');
    if (!activeChapter) return -1;

    const isSenseLineMode = document.body.classList.contains('show-lines');
    let idx = 0;

    for (const child of activeChapter.children) {
      if (typeof child.classList === 'undefined') continue;
      const classes = child.classList;

      if (classes.contains('pericope-header')) {
        if (child === targetEl || child.contains(targetEl)) return idx;
        idx++;
        continue;
      }

      if (classes.contains('verse')) {
        if (isSenseLineMode) {
          const senseLines = Array.from(child.querySelectorAll(':scope > .line'));
          const lines = senseLines.filter(el => el.className.trim() === 'line');
          for (const line of lines) {
            if (line === targetEl || line.contains(targetEl)) return idx;
            idx++;
          }
        } else {
          const para = child.querySelector('.line-para');
          if (para) {
            if (para === targetEl || para.contains(targetEl)) return idx;
            idx++;
          }
        }
      }
    }
    return -1;
  }

  /**
   * Seek audio to the start of a specific manifest line index.
   * If audio isn't loaded yet, loads it first.
   */
  async function seekToLine(manifestIdx) {
    if (!manifest || manifestIdx < 0 || manifestIdx >= manifest.lines.length) return;

    const entry = manifest.lines[manifestIdx];

    // If audio isn't loaded, load it first
    if (!audioEl || !audioEl.src) {
      const ok = await loadChapterAudio();
      if (!ok) return;
    }

    audioEl.currentTime = entry.start;

    // If not playing, start playback from this point
    if (!playing) {
      try {
        await audioEl.play();
        playing = true;
        showPlayer();
        updatePlayerState('playing');
        startHighlightLoop();
      } catch (e) {
        console.error('Narration: play from line failed:', e);
      }
    }

    // Force immediate highlight update
    currentLineIdx = -1; // reset so updateHighlight picks up new position
    updateHighlight();
    updateProgress();
  }

  /**
   * Delegated click handler for chapter content.
   * Clicking a line while narration is active seeks to that line.
   */
  function onChapterClick(e) {
    // Only respond when we have a manifest loaded (narration is active)
    if (!manifest) return;

    // Walk up from click target to find a .line, .line-para, or .pericope-header
    let el = e.target;
    while (el && el !== e.currentTarget) {
      const cl = el.className?.trim?.() || '';
      if (cl === 'line' || cl === 'line-para' || el.classList?.contains('pericope-header')) {
        break;
      }
      el = el.parentElement;
    }
    if (!el || el === e.currentTarget) return;

    const lineIdx = getLineIndexFromElement(el);
    if (lineIdx < 0) return;

    // Find the manifest entry for this lineIndex
    const manifestIdx = manifest.lines.findIndex(l => l.lineIndex === lineIdx);
    if (manifestIdx < 0) return;

    e.preventDefault();
    seekToLine(manifestIdx);
  }

  let chapterClickBound = false;

  function bindChapterClick() {
    if (chapterClickBound) return;
    const activeBook = document.querySelector('.book-content[style*="display: block"]')
                    || document.querySelector('.book-content:not([style*="display: none"])');
    if (!activeBook) return;

    const activeChapter = activeBook.querySelector('.chapter-content[style*="display: block"]')
                       || activeBook.querySelector('.chapter-content:not([style*="display: none"])');
    if (!activeChapter) return;

    activeChapter.addEventListener('click', onChapterClick);
    chapterClickBound = true;

    // Add class so CSS can show pointer cursors
    document.body.classList.add('narration-clickable');
  }

  function unbindChapterClick() {
    if (!chapterClickBound) return;
    document.body.classList.remove('narration-clickable');
    // We leave the listener attached since chapter may change;
    // the handler checks manifest !== null before acting
    chapterClickBound = false;
  }

  // ── Line highlighting ──

  function startHighlightLoop() {
    stopHighlightLoop();
    function tick() {
      if (!playing || !manifest) return;
      updateHighlight();
      updateProgress();
      highlightTimer = requestAnimationFrame(tick);
    }
    highlightTimer = requestAnimationFrame(tick);
  }

  function stopHighlightLoop() {
    if (highlightTimer) {
      cancelAnimationFrame(highlightTimer);
      highlightTimer = null;
    }
  }

  function updateHighlight() {
    if (!audioEl || !manifest) return;

    const t = audioEl.currentTime;

    // Find which line we're in
    let newIdx = -1;
    for (let i = 0; i < manifest.lines.length; i++) {
      const line = manifest.lines[i];
      if (t >= line.start && t < line.end) {
        newIdx = i;
        break;
      }
    }

    if (newIdx === currentLineIdx) return;
    currentLineIdx = newIdx;

    // Clear old highlight
    clearHighlight();

    if (newIdx < 0) return;

    const lineInfo = manifest.lines[newIdx];

    // Check if this is a pericope — only highlight if pericopes are visible
    if (lineInfo.type === 'pericope') {
      const sectionsOn = document.getElementById('sections-pill')?.classList.contains('active-sections');
      if (!sectionsOn) return; // don't highlight hidden pericopes
    }

    // Find the DOM element to highlight
    const el = findLineElement(lineInfo);
    if (el) {
      el.classList.add('narration-active');
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  /**
   * Find the DOM element corresponding to a timing manifest line entry.
   * Uses lineIndex which maps to the order of .line and .pericope-header elements
   * within the visible chapter.
   */
  function findLineElement(lineInfo) {
    const activeBook = document.querySelector('.book-content[style*="display: block"]')
                    || document.querySelector('.book-content:not([style*="display: none"])');
    if (!activeBook) return null;

    const activeChapter = activeBook.querySelector('.chapter-content[style*="display: block"]')
                       || activeBook.querySelector('.chapter-content:not([style*="display: none"])');
    if (!activeChapter) return null;

    const isSenseLineMode = document.body.classList.contains('show-lines');

    // Build an ordered list of highlightable elements matching the generation order
    let idx = 0;
    for (const child of activeChapter.children) {
      if (typeof child.classList === 'undefined') continue;
      const classes = child.classList;

      if (classes.contains('pericope-header')) {
        if (idx === lineInfo.lineIndex) return child;
        idx++;
        continue;
      }

      if (classes.contains('verse')) {
        if (isSenseLineMode) {
          // Sense-line mode: each .line is a separate item
          const senseLines = Array.from(child.querySelectorAll(':scope > .line'));
          // Filter to actual .line (not .line-para, .line-parry)
          const lines = senseLines.filter(el => {
            const cl = el.className.trim();
            return cl === 'line';
          });
          for (const line of lines) {
            if (idx === lineInfo.lineIndex) return line;
            idx++;
          }
        } else {
          // Prose mode: use .line-para
          const para = child.querySelector('.line-para');
          if (para) {
            if (idx === lineInfo.lineIndex) return para;
            idx++;
          }
        }
      }
    }

    return null;
  }

  function clearHighlight() {
    document.querySelectorAll('.narration-active').forEach(
      e => e.classList.remove('narration-active')
    );
  }

  // ════════════════════════════════════════════════════════════════
  // UI — Bottom-bar media player
  // ════════════════════════════════════════════════════════════════

  let playerEl = null;
  let miniBarEl = null;
  let expandedEl = null;
  let isExpanded = false;

  function injectCSS() {
    const style = document.createElement('style');
    style.id = 'narration-styles';
    style.textContent = `
      /* ── Active line highlight ── */
      .narration-active {
        background: rgba(100, 180, 255, 0.15);
        border-radius: 3px;
        transition: background 0.2s ease;
      }
      body.light-mode .narration-active {
        background: rgba(50, 120, 200, 0.1);
      }

      /* ── Toolbar listen button ── */
      #narration-controls {
        display: flex;
        gap: 6px;
        align-items: center;
        margin-left: 8px;
      }
      #narration-btn {
        background: rgba(100, 150, 200, 0.2);
        color: #9ab;
        border: 1px solid rgba(100, 150, 200, 0.3);
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 0.82em;
        cursor: pointer;
        white-space: nowrap;
        transition: background 0.2s, border-color 0.2s;
      }
      #narration-btn:hover {
        background: rgba(100, 150, 200, 0.35);
        border-color: rgba(100, 150, 200, 0.5);
      }
      body.light-mode #narration-btn {
        color: #5a6a7a;
        background: rgba(90, 106, 122, 0.1);
        border-color: rgba(90, 106, 122, 0.25);
      }

      /* ── Bottom player ── */
      #narration-player {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        transform: translateY(100%);
        transition: transform 0.3s ease;
      }
      #narration-player.visible {
        transform: translateY(0);
      }

      /* ── Mini bar ── */
      .narr-mini {
        background: #1a1d22;
        border-top: 1px solid rgba(100, 150, 200, 0.2);
        padding: 8px 12px;
        display: flex;
        align-items: center;
        gap: 10px;
        cursor: pointer;
        min-height: 52px;
        position: relative;
      }
      body.light-mode .narr-mini {
        background: #e8e4dc;
        border-top-color: rgba(90, 106, 122, 0.25);
      }

      .narr-mini-info { flex: 1; min-width: 0; }
      .narr-mini-title {
        font-size: 0.82em; font-weight: 600; color: #d4d0c8;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
      }
      body.light-mode .narr-mini-title { color: #3a3630; }
      .narr-mini-subtitle { font-size: 0.7em; color: #7a8a9a; margin-top: 1px; }
      body.light-mode .narr-mini-subtitle { color: #8a8a8a; }

      .narr-mini-progress {
        position: absolute; top: 0; left: 0; height: 2px;
        background: #5a9abf; transition: width 0.3s ease;
      }
      body.light-mode .narr-mini-progress { background: #4a7a9a; }

      /* ── Player buttons ── */
      .narr-btn {
        background: none; border: none; color: #9ab; cursor: pointer;
        padding: 6px; border-radius: 50%; display: flex; align-items: center;
        justify-content: center; transition: background 0.15s, color 0.15s;
        -webkit-tap-highlight-color: transparent;
      }
      .narr-btn:hover { background: rgba(100, 150, 200, 0.15); color: #bcd; }
      .narr-btn:active { background: rgba(100, 150, 200, 0.25); }
      body.light-mode .narr-btn { color: #5a6a7a; }
      body.light-mode .narr-btn:hover { background: rgba(90, 106, 122, 0.1); color: #3a4a5a; }

      .narr-btn-play { width: 40px; height: 40px; }
      .narr-btn-play svg { width: 22px; height: 22px; }
      .narr-btn-skip { width: 32px; height: 32px; }
      .narr-btn-skip svg { width: 18px; height: 18px; }
      .narr-btn-close { width: 28px; height: 28px; }
      .narr-btn-close svg { width: 14px; height: 14px; }

      /* ── Expanded panel ── */
      .narr-expanded {
        background: #1a1d22;
        border-top: 1px solid rgba(100, 150, 200, 0.15);
        padding: 16px 20px 12px; display: none;
      }
      body.light-mode .narr-expanded {
        background: #e8e4dc;
        border-top-color: rgba(90, 106, 122, 0.2);
      }
      #narration-player.expanded .narr-expanded { display: block; }
      #narration-player.expanded .narr-mini { display: none; }

      .narr-exp-header {
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 14px; gap: 8px;
      }
      .narr-exp-header-btns {
        display: flex; align-items: center; gap: 2px; flex-shrink: 0;
      }
      .narr-exp-title { font-size: 0.95em; font-weight: 600; color: #d4d0c8; }
      body.light-mode .narr-exp-title { color: #3a3630; }
      .narr-exp-verse { font-size: 0.78em; color: #7a8a9a; margin-top: 2px; }

      .narr-progress-container {
        width: 100%; height: 4px; background: rgba(100, 150, 200, 0.15);
        border-radius: 2px; margin-bottom: 8px; cursor: pointer; position: relative;
      }
      .narr-progress-fill {
        height: 100%; background: #5a9abf; border-radius: 2px;
        transition: width 0.15s ease; position: relative;
      }
      .narr-progress-fill::after {
        content: ''; position: absolute; right: -5px; top: -3px;
        width: 10px; height: 10px; background: #7cb8d4; border-radius: 50%;
        opacity: 0; transition: opacity 0.15s;
      }
      .narr-progress-container:hover .narr-progress-fill::after { opacity: 1; }
      body.light-mode .narr-progress-container { background: rgba(90, 106, 122, 0.15); }
      body.light-mode .narr-progress-fill { background: #4a7a9a; }

      .narr-progress-labels {
        display: flex; justify-content: space-between;
        font-size: 0.68em; color: #5a6a7a; margin-bottom: 12px;
      }

      .narr-transport {
        display: flex; align-items: center; justify-content: center;
        gap: 20px; margin-bottom: 14px;
      }
      .narr-transport .narr-btn-play {
        width: 48px; height: 48px;
        background: rgba(100, 150, 200, 0.15); border-radius: 50%;
      }
      .narr-transport .narr-btn-play svg { width: 26px; height: 26px; }

      .narr-settings {
        display: flex; align-items: center; justify-content: center;
        gap: 8px; border-top: 1px solid rgba(100, 150, 200, 0.1);
        padding-top: 10px;
      }
      body.light-mode .narr-settings { border-top-color: rgba(90, 106, 122, 0.15); }

      .narr-setting-label {
        font-size: 0.7em; color: #5a6a7a; text-transform: uppercase;
        letter-spacing: 0.05em; margin-right: 4px;
      }

      .narr-speed-btn {
        background: rgba(100, 150, 200, 0.12);
        border: 1px solid rgba(100, 150, 200, 0.2);
        border-radius: 12px; color: #9ab; font-size: 0.75em;
        padding: 2px 10px; cursor: pointer; font-family: inherit;
        transition: all 0.15s;
      }
      .narr-speed-btn:hover {
        background: rgba(100, 150, 200, 0.25);
        border-color: rgba(100, 150, 200, 0.4);
      }
      .narr-speed-btn.active {
        background: rgba(90, 155, 190, 0.3);
        border-color: #5a9abf; color: #bcd;
      }
      body.light-mode .narr-speed-btn {
        background: rgba(90, 106, 122, 0.08);
        border-color: rgba(90, 106, 122, 0.2); color: #5a6a7a;
      }
      body.light-mode .narr-speed-btn.active {
        background: rgba(70, 120, 150, 0.15);
        border-color: #4a7a9a; color: #3a4a5a;
      }

      .narr-collapse-btn {
        background: none; border: none; color: #7a8a9a;
        cursor: pointer; padding: 4px; font-size: 0.8em;
      }

      body.narration-player-active { padding-bottom: 60px; }
      body.narration-player-expanded { padding-bottom: 220px; }

      /* ── Clickable lines when narration is active ── */
      body.narration-clickable .line,
      body.narration-clickable .line-para,
      body.narration-clickable .pericope-header {
        cursor: pointer;
        transition: background 0.15s ease;
      }
      body.narration-clickable .line:hover,
      body.narration-clickable .line-para:hover {
        background: rgba(100, 180, 255, 0.08);
        border-radius: 3px;
      }
      body.light-mode.narration-clickable .line:hover,
      body.light-mode.narration-clickable .line-para:hover {
        background: rgba(50, 120, 200, 0.06);
      }

      /* ── Mini speed button ── */
      .narr-mini-speed {
        background: rgba(100, 150, 200, 0.12);
        border: 1px solid rgba(100, 150, 200, 0.2);
        border-radius: 10px; color: #9ab; font-size: 0.68em;
        padding: 1px 7px; cursor: pointer; font-family: inherit;
        white-space: nowrap; transition: all 0.15s;
        min-width: 32px; text-align: center;
      }
      .narr-mini-speed:hover {
        background: rgba(100, 150, 200, 0.25);
        border-color: rgba(100, 150, 200, 0.4);
      }
      body.light-mode .narr-mini-speed {
        background: rgba(90, 106, 122, 0.08);
        border-color: rgba(90, 106, 122, 0.2); color: #5a6a7a;
      }
    `;
    document.head.appendChild(style);
  }

  // ── SVG Icons ──
  const ICONS = {
    play: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>',
    pause: '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>',
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    chevDown: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="6 9 12 15 18 9"/></svg>',
  };

  const ICON_RW = `<svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
    <path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/>
    <text x="9.5" y="15.5" font-size="7.5" font-weight="700" font-family="sans-serif" text-anchor="middle">10</text>
  </svg>`;
  const ICON_FF = `<svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
    <path d="M12 5V1l5 5-5 5V7c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6h2c0 4.42-3.58 8-8 8s-8-3.58-8-8 3.58-8 8-8z"/>
    <text x="14" y="15.5" font-size="7.5" font-weight="700" font-family="sans-serif" text-anchor="middle">10</text>
  </svg>`;

  function buildPlayer() {
    playerEl = document.createElement('div');
    playerEl.id = 'narration-player';

    // Build speed buttons
    const speedBtns = SPEEDS.map(s =>
      `<button class="narr-speed-btn${s === currentSpeed ? ' active' : ''}" data-speed="${s}">${s}x</button>`
    ).join('');

    playerEl.innerHTML = `
      <div class="narr-mini">
        <div class="narr-mini-progress" id="narr-mini-prog"></div>
        <div class="narr-mini-info" id="narr-mini-info-click">
          <div class="narr-mini-title" id="narr-mini-title">Loading...</div>
          <div class="narr-mini-subtitle" id="narr-mini-sub">Narration</div>
        </div>
        <button class="narr-mini-speed" id="narr-mini-speed" title="Change speed">${currentSpeed}x</button>
        <button class="narr-btn narr-btn-skip" id="narr-mini-rw" title="Back 10s">${ICON_RW}</button>
        <button class="narr-btn narr-btn-play" id="narr-mini-play" title="Play/Pause">${ICONS.play}</button>
        <button class="narr-btn narr-btn-skip" id="narr-mini-ff" title="Forward 10s">${ICON_FF}</button>
        <button class="narr-btn narr-btn-close" id="narr-mini-close" title="Stop">${ICONS.close}</button>
      </div>
      <div class="narr-expanded">
        <div class="narr-exp-header">
          <div>
            <div class="narr-exp-title" id="narr-exp-title">Loading...</div>
            <div class="narr-exp-verse" id="narr-exp-verse"></div>
          </div>
          <div class="narr-exp-header-btns">
            <button class="narr-collapse-btn" id="narr-collapse" title="Minimize">${ICONS.chevDown}</button>
            <button class="narr-btn narr-btn-close" id="narr-exp-close" title="Close player">${ICONS.close}</button>
          </div>
        </div>
        <div class="narr-progress-container" id="narr-prog-bar">
          <div class="narr-progress-fill" id="narr-prog-fill" style="width: 0%"></div>
        </div>
        <div class="narr-progress-labels">
          <span id="narr-prog-current">0:00</span>
          <span id="narr-prog-total">0:00</span>
        </div>
        <div class="narr-transport">
          <button class="narr-btn narr-btn-skip" id="narr-exp-rw" title="Back 10s">${ICON_RW}</button>
          <button class="narr-btn narr-btn-play" id="narr-exp-play" title="Play/Pause">${ICONS.play}</button>
          <button class="narr-btn narr-btn-skip" id="narr-exp-ff" title="Forward 10s">${ICON_FF}</button>
        </div>
        <div class="narr-settings">
          <span class="narr-setting-label">Speed</span>
          ${speedBtns}
        </div>
      </div>
    `;
    document.body.appendChild(playerEl);
    expandedEl = playerEl.querySelector('.narr-expanded');

    // ── Event listeners ──
    document.getElementById('narr-mini-info-click').addEventListener('click', () => toggleExpand(true));
    document.getElementById('narr-mini-play').addEventListener('click', (e) => { e.stopPropagation(); togglePlayPause(); });
    document.getElementById('narr-mini-rw').addEventListener('click', (e) => { e.stopPropagation(); seekRelative(-10); });
    document.getElementById('narr-mini-ff').addEventListener('click', (e) => { e.stopPropagation(); seekRelative(10); });
    document.getElementById('narr-mini-speed').addEventListener('click', (e) => { e.stopPropagation(); cycleSpeed(); });
    document.getElementById('narr-mini-close').addEventListener('click', (e) => { e.stopPropagation(); stopPlayback(); hidePlayer(); });

    document.getElementById('narr-exp-play').addEventListener('click', togglePlayPause);
    document.getElementById('narr-exp-rw').addEventListener('click', () => seekRelative(-10));
    document.getElementById('narr-exp-ff').addEventListener('click', () => seekRelative(10));
    document.getElementById('narr-collapse').addEventListener('click', () => toggleExpand(false));
    document.getElementById('narr-exp-close').addEventListener('click', () => toggleExpand(false));

    // Speed buttons
    expandedEl.querySelectorAll('.narr-speed-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        setSpeed(parseFloat(btn.dataset.speed));
      });
    });

    // Progress bar seek
    document.getElementById('narr-prog-bar').addEventListener('click', (e) => {
      const rect = e.currentTarget.getBoundingClientRect();
      seekToFraction((e.clientX - rect.left) / rect.width);
    });
  }

  function toggleExpand(expand) {
    isExpanded = expand;
    if (expand) {
      playerEl.classList.add('expanded');
      document.body.classList.add('narration-player-expanded');
      document.body.classList.remove('narration-player-active');
      // Click outside to collapse
      setTimeout(() => document.addEventListener('click', onClickOutsidePlayer, true), 0);
    } else {
      playerEl.classList.remove('expanded');
      document.body.classList.remove('narration-player-expanded');
      document.body.classList.add('narration-player-active');
      document.removeEventListener('click', onClickOutsidePlayer, true);
    }
  }

  function onClickOutsidePlayer(e) {
    if (!isExpanded || !playerEl) return;
    // If the click landed inside the expanded player, ignore it
    if (playerEl.contains(e.target)) return;
    toggleExpand(false);
  }

  function showPlayer() {
    if (!playerEl) buildPlayer();
    playerEl.classList.add('visible');
    document.body.classList.add('narration-player-active');
  }

  function hidePlayer() {
    if (playerEl) playerEl.classList.remove('visible', 'expanded');
    document.body.classList.remove('narration-player-active', 'narration-player-expanded');
    document.removeEventListener('click', onClickOutsidePlayer, true);
    isExpanded = false;
    restoreTextMode();
  }

  // ── UI updates ──

  function formatTime(s) {
    if (!s || isNaN(s)) return '0:00';
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return m + ':' + (sec < 10 ? '0' : '') + sec;
  }

  function updatePlayerState(state, text) {
    if (!playerEl) return;

    const miniPlay = document.getElementById('narr-mini-play');
    const expPlay = document.getElementById('narr-exp-play');
    const miniTitle = document.getElementById('narr-mini-title');
    const expTitle = document.getElementById('narr-exp-title');
    const label = getChapterLabel();

    const playIcon = ICONS.play;
    const pauseIcon = ICONS.pause;

    switch (state) {
      case 'loading':
        miniTitle.textContent = text || 'Loading...';
        expTitle.textContent = text || 'Loading...';
        break;
      case 'playing':
        miniTitle.textContent = label;
        expTitle.textContent = label;
        miniPlay.innerHTML = pauseIcon;
        expPlay.innerHTML = pauseIcon;
        break;
      case 'paused':
        miniTitle.textContent = label + ' (paused)';
        expTitle.textContent = label;
        miniPlay.innerHTML = playIcon;
        expPlay.innerHTML = playIcon;
        break;
      case 'stopped':
        miniTitle.textContent = label;
        expTitle.textContent = label;
        miniPlay.innerHTML = playIcon;
        expPlay.innerHTML = playIcon;
        break;
      case 'error':
        miniTitle.textContent = text || 'Error';
        expTitle.textContent = text || 'Error';
        break;
    }

    // Toolbar button
    const toolbarBtn = document.getElementById('narration-btn');
    if (toolbarBtn) {
      if (state === 'playing') toolbarBtn.textContent = 'Playing';
      else if (state === 'paused') toolbarBtn.textContent = 'Paused';
      else if (state === 'loading') toolbarBtn.textContent = 'Loading...';
      else toolbarBtn.textContent = 'Listen';
    }
  }

  function updateProgress() {
    if (!playerEl || !audioEl) return;

    const current = audioEl.currentTime || 0;
    const total = audioEl.duration || 0;
    const pct = total > 0 ? (current / total * 100) : 0;

    // Current verse from manifest
    let verseLabel = '';
    if (manifest && currentLineIdx >= 0 && currentLineIdx < manifest.lines.length) {
      verseLabel = manifest.lines[currentLineIdx].verse || '';
    }

    // Mini bar
    const miniProg = document.getElementById('narr-mini-prog');
    const miniSub = document.getElementById('narr-mini-sub');
    if (miniProg) miniProg.style.width = pct + '%';
    if (miniSub) miniSub.textContent = verseLabel ? ('Verse ' + verseLabel) : formatTime(current);

    // Expanded
    const expVerse = document.getElementById('narr-exp-verse');
    const progFill = document.getElementById('narr-prog-fill');
    const progCurrent = document.getElementById('narr-prog-current');
    const progTotal = document.getElementById('narr-prog-total');
    if (expVerse) expVerse.textContent = verseLabel ? ('Verse ' + verseLabel) : '';
    if (progFill) progFill.style.width = pct + '%';
    if (progCurrent) progCurrent.textContent = formatTime(current);
    if (progTotal) progTotal.textContent = formatTime(total);
  }

  function updateSpeedDisplay() {
    if (expandedEl) {
      expandedEl.querySelectorAll('.narr-speed-btn').forEach(btn => {
        const s = parseFloat(btn.dataset.speed);
        btn.classList.toggle('active', s === currentSpeed);
      });
    }
    // Update mini speed button
    const miniSpeed = document.getElementById('narr-mini-speed');
    if (miniSpeed) miniSpeed.textContent = currentSpeed + 'x';
  }

  // ── Toolbar button (entry point) ──

  function initToolbarButton() {
    const controls = document.createElement('div');
    controls.id = 'narration-controls';

    const btn = document.createElement('button');
    btn.id = 'narration-btn';
    btn.textContent = 'Listen';
    btn.title = 'Listen to this chapter';
    btn.addEventListener('click', () => {
      if (playing) {
        showPlayer();
        toggleExpand(true);
      } else {
        startPlayback();
      }
    });
    controls.appendChild(btn);

    const controlsRow = document.querySelector('.controls-row');
    if (controlsRow) {
      const searchBtn = controlsRow.querySelector('.search-icon-btn');
      if (searchBtn && searchBtn.nextSibling) {
        // Insert Listen after search icon (between search and layers)
        controlsRow.insertBefore(controls, searchBtn.nextSibling);
      } else {
        controlsRow.appendChild(controls);
      }
    }
  }

  // ── Initialize ──

  function init() {
    injectCSS();
    initToolbarButton();
  }

  // ── Public API ──
  return {
    init,
    play: startPlayback,
    pause: pausePlayback,
    resume: resumePlayback,
    stop: stopPlayback,
    setSpeed,
    seekToLine,
    get isPlaying() { return playing; },
    get isPaused() { return audioEl && audioEl.paused; },
    get currentLine() { return currentLineIdx >= 0 && manifest ? manifest.lines[currentLineIdx] : null; },
  };
})();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => NARRATION.init());
} else {
  NARRATION.init();
}
