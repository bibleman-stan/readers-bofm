/**
 * Narration module for bomreader.com
 * Uses Kokoro.js (browser-based neural TTS) to read sense-line formatted text
 * with a British voice and natural pacing between lines.
 *
 * Architecture:
 *   1. On first play, loads ~80MB ONNX model (cached by browser after first load)
 *   2. Reads the current chapter verse-by-verse, line-by-line
 *   3. Adds ~180ms pauses between sense-lines, longer pauses between verses
 *   4. Highlights the line currently being read
 *   5. Respects swap state (reads modern or archaic text for TTS clarity)
 *   6. Provides a persistent bottom-bar media player (mini + expanded)
 */

const NARRATION = (() => {
  // ── Configuration ──
  const MODEL_ID = 'onnx-community/Kokoro-82M-v1.0-ONNX';
  // Detect WebGPU support — async GPU inference won't block main thread
  const USE_WEBGPU = typeof navigator !== 'undefined' && !!navigator.gpu;
  const MODEL_OPTS = USE_WEBGPU
    ? { dtype: 'fp32', device: 'webgpu' }
    : { dtype: 'q8', device: 'wasm' };
  const VOICES = {
    'bm_george':  'George (British male)',
    'bf_emma':    'Emma (British female)',
    'am_adam':    'Adam (American male)',
    'af_sarah':   'Sarah (American female)',
  };
  const DEFAULT_VOICE = 'bm_george';
  const LINE_PAUSE_MS = 180;
  const VERSE_PAUSE_MS = 500;
  const PERICOPE_PAUSE_MS = 900;
  const SPEEDS = [0.75, 1, 1.25, 1.5, 2];

  // ── State ──
  let tts = null;
  let loading = false;
  let playing = false;
  let paused = false;
  let abortController = null;
  let currentVoice = DEFAULT_VOICE;
  let currentSpeed = 1;
  let audioContext = null;
  let currentSourceNode = null;  // for stopping mid-utterance

  // Playback tracking
  let lines = [];
  let cursor = 0;           // current line index
  let seekTarget = -1;      // set to jump to a specific line

  // ── Helpers ──

  /** Yield to the browser event loop so the UI stays responsive */
  function yieldToMain() {
    return new Promise(resolve => setTimeout(resolve, 0));
  }

  function sleep(ms, signal) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(resolve, ms);
      if (signal) {
        signal.addEventListener('abort', () => {
          clearTimeout(timer);
          reject(new DOMException('Aborted', 'AbortError'));
        });
      }
    });
  }

  /**
   * Extract the readable text from a line element.
   * Always uses data-mod for TTS (modernized text is clearer for listeners).
   */
  function getLineText(el) {
    const clone = el.cloneNode(true);
    clone.querySelectorAll('.swap, .swap-quiet').forEach(span => {
      const mod = span.getAttribute('data-mod');
      if (mod) span.textContent = mod;
    });
    clone.querySelectorAll('.verse-num, .parry-label-spacer, .parry-label').forEach(el => el.remove());
    let text = clone.textContent.trim();
    text = text.replace(/\s+/g, ' ');
    return text;
  }

  /**
   * Get the verse number string from a verse element (e.g. "1:3").
   */
  function getVerseNum(el) {
    const verseDiv = el.closest('.verse');
    if (!verseDiv) return '';
    const numEl = verseDiv.querySelector('.verse-num');
    return numEl ? numEl.textContent.trim() : '';
  }

  /**
   * Gather all lines to read for the current chapter.
   * FIX: Look inside the visible .chapter-content, not .book-content directly.
   */
  function gatherLines() {
    const result = [];

    // Find the currently visible book content
    const activeBook = document.querySelector('.book-content[style*="display: block"]')
                    || document.querySelector('.book-content:not([style*="display: none"])');
    if (!activeBook) return result;

    // Find the visible chapter within the book
    const activeChapter = activeBook.querySelector('.chapter-content[style*="display: block"]')
                       || activeBook.querySelector('.chapter-content:not([style*="display: none"])');
    if (!activeChapter) return result;

    const isSenseLineMode = document.body.classList.contains('show-lines');

    const children = activeChapter.children;
    for (const child of children) {
      // Pericope header
      if (child.classList.contains('pericope-header')) {
        const mainEl = child.querySelector('.pericope-main');
        if (mainEl) {
          result.push({
            element: child,
            text: mainEl.textContent.trim(),
            type: 'pericope',
            verseNum: ''
          });
        }
        continue;
      }

      // Verse
      if (child.classList.contains('verse')) {
        const verseNumEl = child.querySelector('.verse-num');
        const vn = verseNumEl ? verseNumEl.textContent.trim() : '';

        if (isSenseLineMode) {
          const senseLines = child.querySelectorAll(':scope > .line');
          senseLines.forEach(line => {
            const text = getLineText(line);
            if (text) {
              result.push({ element: line, text, type: 'line', verseNum: vn });
            }
          });
        } else {
          const para = child.querySelector('.line-para');
          if (para) {
            const text = getLineText(para);
            if (text) {
              result.push({ element: para, text, type: 'verse', verseNum: vn });
            }
          }
        }
        // Verse boundary marker
        if (result.length > 0 && result[result.length - 1].type !== 'verse-gap') {
          result.push({ element: null, text: '', type: 'verse-gap', verseNum: '' });
        }
      }
    }

    return result;
  }

  /**
   * Get chapter label from the visible chapter element.
   */
  function getChapterLabel() {
    const activeBook = document.querySelector('.book-content[style*="display: block"]')
                    || document.querySelector('.book-content:not([style*="display: none"])');
    if (!activeBook) return 'Unknown';
    const activeChapter = activeBook.querySelector('.chapter-content[style*="display: block"]')
                       || activeBook.querySelector('.chapter-content:not([style*="display: none"])');
    if (!activeChapter) return 'Unknown';
    // Extract from ID like "ch-1nephi-1"
    const id = activeChapter.id || '';
    const m = id.match(/^ch-(.+)-(\d+)$/);
    if (m) {
      const bookMap = {
        '1nephi': '1 Nephi', '2nephi': '2 Nephi', 'jacob': 'Jacob',
        'enos': 'Enos', 'jarom': 'Jarom', 'omni': 'Omni',
        'words-of-mormon': 'Words of Mormon', 'mosiah': 'Mosiah',
        'alma': 'Alma', 'helaman': 'Helaman', '3nephi': '3 Nephi',
        '4nephi': '4 Nephi', 'mormon': 'Mormon', 'ether': 'Ether',
        'moroni': 'Moroni'
      };
      return (bookMap[m[1]] || m[1]) + ' ' + m[2];
    }
    return 'Chapter';
  }

  // ── Audio playback ──

  async function playAudio(rawAudio, signal) {
    if (!audioContext) {
      audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioContext.state === 'suspended') {
      await audioContext.resume();
    }

    // Extract samples — handle various kokoro-js return formats
    let samples = rawAudio.audio || rawAudio.data;
    const sampleRate = rawAudio.sampling_rate || 24000;

    // Debug logging
    console.log('Narration playAudio:', {
      type: typeof samples,
      constructor: samples?.constructor?.name,
      length: samples?.length,
      sampleRate,
      audioCtxState: audioContext.state,
      rawKeys: Object.keys(rawAudio || {})
    });

    if (!samples || samples.length === 0) {
      console.warn('Narration: empty audio samples, skipping');
      return;
    }

    // Ensure we have a plain Float32Array (some ONNX backends return views)
    if (!(samples instanceof Float32Array)) {
      samples = new Float32Array(samples);
    }

    const buffer = audioContext.createBuffer(1, samples.length, sampleRate);
    buffer.getChannelData(0).set(samples);

    return new Promise((resolve, reject) => {
      const source = audioContext.createBufferSource();
      source.buffer = buffer;
      source.playbackRate.value = currentSpeed;
      source.connect(audioContext.destination);
      source.onended = () => {
        currentSourceNode = null;
        resolve();
      };
      currentSourceNode = source;
      source.start(0);

      if (signal) {
        signal.addEventListener('abort', () => {
          try { source.stop(); } catch(e) {}
          currentSourceNode = null;
          reject(new DOMException('Aborted', 'AbortError'));
        });
      }
    });
  }

  // ── Model loading ──

  async function ensureModel(progressCallback) {
    if (tts) return;
    if (loading) return;

    loading = true;
    console.log('Narration: loading model, device:', USE_WEBGPU ? 'webgpu' : 'wasm');
    try {
      const { KokoroTTS } = await import(
        /* webpackIgnore: true */
        'https://cdn.jsdelivr.net/npm/kokoro-js@1/+esm'
      );

      tts = await KokoroTTS.from_pretrained(MODEL_ID, {
        ...MODEL_OPTS,
        progress_callback: (progress) => {
          if (progressCallback) progressCallback(progress);
        }
      });
    } catch(e) {
      console.error('Narration: failed to load TTS model:', e);
      throw e;
    } finally {
      loading = false;
    }
  }

  // ── Generating indicator (pulsing dot on mini bar while WASM works) ──

  function showGeneratingIndicator(show) {
    const sub = document.getElementById('narr-mini-sub');
    const title = document.getElementById('narr-mini-title');
    if (!sub) return;
    if (show) {
      sub.textContent = 'Generating...';
      if (title) title.style.opacity = '0.6';
    } else {
      if (title) title.style.opacity = '1';
      // sub will be updated by updateProgress()
    }
  }

  // ── Highlight management ──

  function highlightLine(el) {
    document.querySelectorAll('.narration-active').forEach(
      e => e.classList.remove('narration-active')
    );
    if (el) {
      el.classList.add('narration-active');
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  function clearHighlight() {
    document.querySelectorAll('.narration-active').forEach(
      e => e.classList.remove('narration-active')
    );
  }

  // ── Main playback loop ──

  async function startPlayback() {
    if (playing) return;
    playing = true;
    paused = false;
    abortController = new AbortController();
    const signal = abortController.signal;

    showPlayer();
    updatePlayerState('loading');

    try {
      await ensureModel((progress) => {
        if (progress.status === 'downloading' || progress.status === 'progress') {
          const pct = progress.progress ? Math.round(progress.progress) : 0;
          updatePlayerState('loading', `Loading voice model... ${pct}%`);
        }
      });

      lines = gatherLines();
      console.log('Narration: gathered', lines.length, 'items,',
        lines.filter(l => l.type === 'line' || l.type === 'verse').length, 'speakable lines');
      if (lines.length === 0) {
        console.warn('Narration: no lines found to read');
        stopPlayback();
        return;
      }

      updatePlayerState('playing');
      console.log('Narration: starting playback, voice:', currentVoice,
        'device:', USE_WEBGPU ? 'webgpu' : 'wasm');

      // ── Pre-generation pipeline ──
      // Generate next line's audio while current line plays to minimize gaps.
      let nextAudioCache = null;   // { index, audio } for the next speakable line
      let nextGenPromise = null;   // in-flight generation promise

      /** Pre-generate audio for the next speakable line after `fromIndex` */
      function pregenNext(fromIndex) {
        // Find next speakable item
        let ni = fromIndex + 1;
        while (ni < lines.length && (lines[ni].type === 'verse-gap')) ni++;
        if (ni >= lines.length || signal.aborted) return;
        const nextItem = lines[ni];
        if (!nextItem.text) return;

        console.log('Narration: pre-generating line', ni);
        nextGenPromise = tts.generate(nextItem.text, { voice: currentVoice })
          .then(audio => {
            nextAudioCache = { index: ni, audio };
            nextGenPromise = null;
          })
          .catch(() => { nextGenPromise = null; });
      }

      /** Get audio for an item — use cache if available, otherwise generate */
      async function getAudio(index, text) {
        // Check if we pre-generated this one
        if (nextAudioCache && nextAudioCache.index === index) {
          console.log('Narration: cache HIT for line', index);
          const audio = nextAudioCache.audio;
          nextAudioCache = null;
          return audio;
        }
        // Wait for in-flight pre-gen if it's for this index
        if (nextGenPromise) {
          showGeneratingIndicator(true);
          await nextGenPromise;
          showGeneratingIndicator(false);
          if (nextAudioCache && nextAudioCache.index === index) {
            console.log('Narration: cache HIT (waited) for line', index);
            const audio = nextAudioCache.audio;
            nextAudioCache = null;
            return audio;
          }
        }
        // Generate fresh (first line, or cache miss after seek)
        showGeneratingIndicator(true);
        await yieldToMain();
        const t0 = performance.now();
        const audio = await tts.generate(text, { voice: currentVoice });
        console.log('Narration: generated fresh in', Math.round(performance.now() - t0), 'ms');
        showGeneratingIndicator(false);
        return audio;
      }

      for (cursor = (seekTarget >= 0 ? seekTarget : 0); cursor < lines.length; cursor++) {
        if (signal.aborted) break;
        seekTarget = -1;

        // Handle pause
        while (paused && !signal.aborted) {
          await sleep(100, signal);
        }

        // Check for seek (invalidate pre-gen cache)
        if (seekTarget >= 0) {
          nextAudioCache = null;
          cursor = seekTarget - 1;
          seekTarget = -1;
          continue;
        }

        const item = lines[cursor];

        if (item.type === 'verse-gap') {
          await sleep(VERSE_PAUSE_MS / currentSpeed, signal);
          continue;
        }

        // Update player UI
        updateProgress();

        if (item.type === 'pericope') {
          await sleep(PERICOPE_PAUSE_MS / currentSpeed, signal);
          highlightLine(item.element);
          const audio = await getAudio(cursor, item.text);
          await yieldToMain();
          // Start pre-generating next while pericope plays
          pregenNext(cursor);
          await playAudio(audio, signal);
          await sleep(PERICOPE_PAUSE_MS / currentSpeed, signal);
          continue;
        }

        // Regular line or verse
        highlightLine(item.element);
        const audio = await getAudio(cursor, item.text);
        await yieldToMain();
        // Start pre-generating next line while this one plays
        pregenNext(cursor);
        await playAudio(audio, signal);

        if (item.type === 'line') {
          await sleep(LINE_PAUSE_MS / currentSpeed, signal);
        }
      }
    } catch (e) {
      if (e.name !== 'AbortError') {
        console.error('Narration error:', e);
        updatePlayerState('error', e.message);
        return;
      }
    } finally {
      playing = false;
      paused = false;
      clearHighlight();
      if (!abortController?.signal.aborted) {
        // Finished naturally
        updatePlayerState('stopped');
      }
    }
  }

  function pausePlayback() {
    paused = true;
    // Stop current audio immediately
    if (currentSourceNode) {
      try { currentSourceNode.stop(); } catch(e) {}
      currentSourceNode = null;
    }
    updatePlayerState('paused');
  }

  function resumePlayback() {
    if (!playing) {
      // Restart from current cursor
      seekTarget = cursor;
      startPlayback();
    } else {
      paused = false;
      updatePlayerState('playing');
    }
  }

  function stopPlayback() {
    if (abortController) {
      abortController.abort();
    }
    if (currentSourceNode) {
      try { currentSourceNode.stop(); } catch(e) {}
      currentSourceNode = null;
    }
    playing = false;
    paused = false;
    clearHighlight();
    updatePlayerState('stopped');
  }

  /**
   * Skip forward or backward by verse.
   * direction: +1 (forward) or -1 (backward)
   */
  function skipByVerse(direction) {
    if (lines.length === 0) return;

    let target = cursor;
    if (direction > 0) {
      // Find next verse-gap, then skip past it
      while (target < lines.length && lines[target].type !== 'verse-gap') target++;
      while (target < lines.length && lines[target].type === 'verse-gap') target++;
      if (target >= lines.length) target = lines.length - 1;
    } else {
      // Go back: find previous verse-gap, then the start of that verse
      target = Math.max(0, target - 1);
      while (target > 0 && lines[target].type !== 'verse-gap') target--;
      if (target > 0) {
        target--; // step before the gap
        while (target > 0 && lines[target].type !== 'verse-gap') target--;
        if (lines[target].type === 'verse-gap') target++;
      }
    }

    seekTarget = target;
    // If paused or stopped, we need to restart
    if (paused) {
      cursor = target;
      resumePlayback();
    } else if (playing) {
      // Abort current audio to trigger seek
      if (currentSourceNode) {
        try { currentSourceNode.stop(); } catch(e) {}
      }
    }
    updateProgress();
  }

  function setSpeed(speed) {
    currentSpeed = speed;
    // Update currently playing audio if any
    if (currentSourceNode) {
      currentSourceNode.playbackRate.value = speed;
    }
    updateSpeedDisplay();
  }

  function setVoice(voice) {
    currentVoice = voice;
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
      }
      body.light-mode .narr-mini {
        background: #e8e4dc;
        border-top-color: rgba(90, 106, 122, 0.25);
      }

      .narr-mini-info {
        flex: 1;
        min-width: 0;
      }
      .narr-mini-title {
        font-size: 0.82em;
        font-weight: 600;
        color: #d4d0c8;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      body.light-mode .narr-mini-title { color: #3a3630; }

      .narr-mini-subtitle {
        font-size: 0.7em;
        color: #7a8a9a;
        margin-top: 1px;
      }
      body.light-mode .narr-mini-subtitle { color: #8a8a8a; }

      /* Progress thin bar at top of mini player */
      .narr-mini-progress {
        position: absolute;
        top: 0;
        left: 0;
        height: 2px;
        background: #5a9abf;
        transition: width 0.3s ease;
      }
      body.light-mode .narr-mini-progress {
        background: #4a7a9a;
      }

      /* ── Player buttons ── */
      .narr-btn {
        background: none;
        border: none;
        color: #9ab;
        cursor: pointer;
        padding: 6px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.15s, color 0.15s;
        -webkit-tap-highlight-color: transparent;
      }
      .narr-btn:hover { background: rgba(100, 150, 200, 0.15); color: #bcd; }
      .narr-btn:active { background: rgba(100, 150, 200, 0.25); }
      body.light-mode .narr-btn { color: #5a6a7a; }
      body.light-mode .narr-btn:hover { background: rgba(90, 106, 122, 0.1); color: #3a4a5a; }

      .narr-btn-play {
        width: 40px;
        height: 40px;
      }
      .narr-btn-play svg { width: 22px; height: 22px; }
      .narr-btn-skip svg { width: 18px; height: 18px; }

      .narr-btn-close {
        width: 28px;
        height: 28px;
      }
      .narr-btn-close svg { width: 14px; height: 14px; }

      /* ── Expanded panel ── */
      .narr-expanded {
        background: #1a1d22;
        border-top: 1px solid rgba(100, 150, 200, 0.15);
        padding: 16px 20px 12px;
        display: none;
      }
      body.light-mode .narr-expanded {
        background: #e8e4dc;
        border-top-color: rgba(90, 106, 122, 0.2);
      }
      #narration-player.expanded .narr-expanded { display: block; }
      #narration-player.expanded .narr-mini { display: none; }

      .narr-exp-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 14px;
      }
      .narr-exp-title {
        font-size: 0.95em;
        font-weight: 600;
        color: #d4d0c8;
      }
      body.light-mode .narr-exp-title { color: #3a3630; }

      .narr-exp-verse {
        font-size: 0.78em;
        color: #7a8a9a;
        margin-top: 2px;
      }

      /* Progress bar */
      .narr-progress-container {
        width: 100%;
        height: 4px;
        background: rgba(100, 150, 200, 0.15);
        border-radius: 2px;
        margin-bottom: 8px;
        cursor: pointer;
        position: relative;
      }
      .narr-progress-fill {
        height: 100%;
        background: #5a9abf;
        border-radius: 2px;
        transition: width 0.3s ease;
        position: relative;
      }
      .narr-progress-fill::after {
        content: '';
        position: absolute;
        right: -5px;
        top: -3px;
        width: 10px;
        height: 10px;
        background: #7cb8d4;
        border-radius: 50%;
        opacity: 0;
        transition: opacity 0.15s;
      }
      .narr-progress-container:hover .narr-progress-fill::after {
        opacity: 1;
      }
      body.light-mode .narr-progress-container { background: rgba(90, 106, 122, 0.15); }
      body.light-mode .narr-progress-fill { background: #4a7a9a; }

      .narr-progress-labels {
        display: flex;
        justify-content: space-between;
        font-size: 0.68em;
        color: #5a6a7a;
        margin-bottom: 12px;
      }

      /* Transport controls */
      .narr-transport {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin-bottom: 14px;
      }
      .narr-transport .narr-btn-play {
        width: 48px;
        height: 48px;
        background: rgba(100, 150, 200, 0.15);
        border-radius: 50%;
      }
      .narr-transport .narr-btn-play svg { width: 26px; height: 26px; }

      /* Settings row */
      .narr-settings {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        border-top: 1px solid rgba(100, 150, 200, 0.1);
        padding-top: 10px;
      }
      body.light-mode .narr-settings { border-top-color: rgba(90, 106, 122, 0.15); }

      .narr-setting-group {
        display: flex;
        align-items: center;
        gap: 6px;
      }
      .narr-setting-label {
        font-size: 0.7em;
        color: #5a6a7a;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }

      .narr-speed-btn {
        background: rgba(100, 150, 200, 0.12);
        border: 1px solid rgba(100, 150, 200, 0.2);
        border-radius: 12px;
        color: #9ab;
        font-size: 0.75em;
        padding: 2px 10px;
        cursor: pointer;
        font-family: inherit;
        transition: all 0.15s;
      }
      .narr-speed-btn:hover {
        background: rgba(100, 150, 200, 0.25);
        border-color: rgba(100, 150, 200, 0.4);
      }
      .narr-speed-btn.active {
        background: rgba(90, 155, 190, 0.3);
        border-color: #5a9abf;
        color: #bcd;
      }
      body.light-mode .narr-speed-btn {
        background: rgba(90, 106, 122, 0.08);
        border-color: rgba(90, 106, 122, 0.2);
        color: #5a6a7a;
      }
      body.light-mode .narr-speed-btn.active {
        background: rgba(70, 120, 150, 0.15);
        border-color: #4a7a9a;
        color: #3a4a5a;
      }

      .narr-voice-select {
        background: rgba(100, 150, 200, 0.12);
        border: 1px solid rgba(100, 150, 200, 0.2);
        border-radius: 12px;
        color: #9ab;
        font-size: 0.75em;
        padding: 2px 8px;
        font-family: inherit;
        cursor: pointer;
      }
      body.light-mode .narr-voice-select {
        background: rgba(90, 106, 122, 0.08);
        border-color: rgba(90, 106, 122, 0.2);
        color: #5a6a7a;
      }

      /* Collapse button (down chevron) */
      .narr-collapse-btn {
        background: none;
        border: none;
        color: #7a8a9a;
        cursor: pointer;
        padding: 4px;
        font-size: 0.8em;
      }

      /* Loading state */
      .narr-loading-text {
        font-size: 0.75em;
        color: #7a8a9a;
        text-align: center;
        padding: 4px 0;
      }

      /* Body padding when player is visible */
      body.narration-player-active {
        padding-bottom: 60px;
      }
      body.narration-player-expanded {
        padding-bottom: 220px;
      }
    `;
    document.head.appendChild(style);
  }

  // ── SVG Icons ──
  const ICONS = {
    play: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>',
    pause: '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>',
    skipBack: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14"/><path d="M4 12l8-7v14l8-7v14V5z"/></svg>',
    skipFwd: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14"/><path d="M20 12l-8-7v14l-8-7v14V5z"/></svg>',
    rewind10: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12.5 3C7.81 3 4 6.81 4 11.5h2c0-3.59 2.91-6.5 6.5-6.5s6.5 2.91 6.5 6.5-2.91 6.5-6.5 6.5c-1.68 0-3.21-.64-4.36-1.69l1.42-1.42C10.63 15.44 11.54 16 12.5 16c2.76 0 5-2.24 5-5s-2.24-5-5-5V3z"/><text x="9" y="14" font-size="8" font-weight="bold" font-family="sans-serif">10</text></svg>',
    forward10: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M11.5 3v3c2.76 0 5 2.24 5 5s-2.24 5-5 5c-.96 0-1.87-.56-2.94-1.11l1.42-1.42C10.63 15.44 11.54 16 12.5 16c2.76 0 5-2.24 5-5s-2.24-5-5-5V3z"/><path d="M11.5 3C6.81 3 4 6.81 4 11.5h2c0-3.59 2.91-6.5 6.5-6.5V3z" opacity="0"/><text x="7.5" y="14" font-size="8" font-weight="bold" font-family="sans-serif">10</text></svg>',
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
    chevDown: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="6 9 12 15 18 9"/></svg>',
    speaker: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/></svg>',
  };

  // Simple rewind/forward icons with "10" text
  const ICON_RW = `<svg viewBox="0 0 24 24" fill="currentColor" style="width:18px;height:18px">
    <path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/>
    <text x="9.5" y="15.5" font-size="7.5" font-weight="700" font-family="sans-serif" text-anchor="middle">10</text>
  </svg>`;
  const ICON_FF = `<svg viewBox="0 0 24 24" fill="currentColor" style="width:18px;height:18px">
    <path d="M12 5V1l5 5-5 5V7c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6h2c0 4.42-3.58 8-8 8s-8-3.58-8-8 3.58-8 8-8z"/>
    <text x="14" y="15.5" font-size="7.5" font-weight="700" font-family="sans-serif" text-anchor="middle">10</text>
  </svg>`;

  function buildPlayer() {
    playerEl = document.createElement('div');
    playerEl.id = 'narration-player';

    // ── Mini bar ──
    miniBarEl = document.createElement('div');
    miniBarEl.className = 'narr-mini';
    miniBarEl.innerHTML = `
      <div class="narr-mini-progress" id="narr-mini-prog"></div>
      <div class="narr-mini-info" id="narr-mini-info-click">
        <div class="narr-mini-title" id="narr-mini-title">Loading...</div>
        <div class="narr-mini-subtitle" id="narr-mini-sub">Kokoro TTS</div>
      </div>
      <button class="narr-btn narr-btn-skip" id="narr-mini-rw" title="Back one verse">${ICON_RW}</button>
      <button class="narr-btn narr-btn-play" id="narr-mini-play" title="Play/Pause">${ICONS.play}</button>
      <button class="narr-btn narr-btn-skip" id="narr-mini-ff" title="Forward one verse">${ICON_FF}</button>
      <button class="narr-btn narr-btn-close" id="narr-mini-close" title="Stop">${ICONS.close}</button>
    `;
    playerEl.appendChild(miniBarEl);

    // ── Expanded panel ──
    expandedEl = document.createElement('div');
    expandedEl.className = 'narr-expanded';

    // Build speed buttons
    const speedBtns = SPEEDS.map(s =>
      `<button class="narr-speed-btn${s === currentSpeed ? ' active' : ''}" data-speed="${s}">${s}x</button>`
    ).join('');

    // Build voice select
    const voiceOpts = Object.entries(VOICES).map(([id, name]) =>
      `<option value="${id}"${id === currentVoice ? ' selected' : ''}>${name}</option>`
    ).join('');

    expandedEl.innerHTML = `
      <div class="narr-exp-header">
        <div>
          <div class="narr-exp-title" id="narr-exp-title">Loading...</div>
          <div class="narr-exp-verse" id="narr-exp-verse"></div>
        </div>
        <button class="narr-collapse-btn" id="narr-collapse" title="Collapse">${ICONS.chevDown}</button>
      </div>
      <div class="narr-progress-container" id="narr-prog-bar">
        <div class="narr-progress-fill" id="narr-prog-fill" style="width: 0%"></div>
      </div>
      <div class="narr-progress-labels">
        <span id="narr-prog-current">—</span>
        <span id="narr-prog-total">—</span>
      </div>
      <div class="narr-transport">
        <button class="narr-btn narr-btn-skip" id="narr-exp-rw" title="Back one verse">${ICON_RW}</button>
        <button class="narr-btn narr-btn-play" id="narr-exp-play" title="Play/Pause">${ICONS.play}</button>
        <button class="narr-btn narr-btn-skip" id="narr-exp-ff" title="Forward one verse">${ICON_FF}</button>
      </div>
      <div class="narr-settings">
        <div class="narr-setting-group">
          <span class="narr-setting-label">Speed</span>
          ${speedBtns}
        </div>
        <div class="narr-setting-group">
          <span class="narr-setting-label">Voice</span>
          <select class="narr-voice-select" id="narr-voice-sel">${voiceOpts}</select>
        </div>
      </div>
    `;
    playerEl.appendChild(expandedEl);
    document.body.appendChild(playerEl);

    // ── Event listeners ──

    // Mini bar: info area → expand
    document.getElementById('narr-mini-info-click').addEventListener('click', () => toggleExpand(true));

    // Mini bar controls
    document.getElementById('narr-mini-play').addEventListener('click', (e) => {
      e.stopPropagation();
      togglePlayPause();
    });
    document.getElementById('narr-mini-rw').addEventListener('click', (e) => {
      e.stopPropagation();
      skipByVerse(-1);
    });
    document.getElementById('narr-mini-ff').addEventListener('click', (e) => {
      e.stopPropagation();
      skipByVerse(1);
    });
    document.getElementById('narr-mini-close').addEventListener('click', (e) => {
      e.stopPropagation();
      stopPlayback();
      hidePlayer();
    });

    // Expanded controls
    document.getElementById('narr-exp-play').addEventListener('click', togglePlayPause);
    document.getElementById('narr-exp-rw').addEventListener('click', () => skipByVerse(-1));
    document.getElementById('narr-exp-ff').addEventListener('click', () => skipByVerse(1));
    document.getElementById('narr-collapse').addEventListener('click', () => toggleExpand(false));

    // Speed buttons
    expandedEl.querySelectorAll('.narr-speed-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const speed = parseFloat(btn.dataset.speed);
        setSpeed(speed);
        expandedEl.querySelectorAll('.narr-speed-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });

    // Voice select
    document.getElementById('narr-voice-sel').addEventListener('change', (e) => {
      setVoice(e.target.value);
    });

    // Progress bar click-to-seek
    document.getElementById('narr-prog-bar').addEventListener('click', (e) => {
      if (lines.length === 0) return;
      const rect = e.currentTarget.getBoundingClientRect();
      const pct = (e.clientX - rect.left) / rect.width;
      const target = Math.floor(pct * lines.length);
      seekTarget = Math.max(0, Math.min(target, lines.length - 1));
      if (paused) {
        cursor = seekTarget;
        resumePlayback();
      }
      updateProgress();
    });
  }

  function toggleExpand(expand) {
    isExpanded = expand;
    if (expand) {
      playerEl.classList.add('expanded');
      document.body.classList.add('narration-player-expanded');
      document.body.classList.remove('narration-player-active');
    } else {
      playerEl.classList.remove('expanded');
      document.body.classList.remove('narration-player-expanded');
      document.body.classList.add('narration-player-active');
    }
  }

  function showPlayer() {
    if (!playerEl) buildPlayer();
    playerEl.classList.add('visible');
    document.body.classList.add('narration-player-active');
  }

  function hidePlayer() {
    if (playerEl) {
      playerEl.classList.remove('visible', 'expanded');
    }
    document.body.classList.remove('narration-player-active', 'narration-player-expanded');
    isExpanded = false;
  }

  function togglePlayPause() {
    if (loading) return;
    if (!playing) {
      startPlayback();
    } else if (paused) {
      resumePlayback();
    } else {
      pausePlayback();
    }
  }

  function updatePlayerState(state, text) {
    if (!playerEl) return;

    const miniPlay = document.getElementById('narr-mini-play');
    const expPlay = document.getElementById('narr-exp-play');
    const miniTitle = document.getElementById('narr-mini-title');
    const expTitle = document.getElementById('narr-exp-title');
    const label = getChapterLabel();

    switch (state) {
      case 'loading':
        miniTitle.textContent = text || 'Loading voice model...';
        expTitle.textContent = text || 'Loading voice model...';
        miniPlay.innerHTML = ICONS.pause;
        expPlay.innerHTML = ICONS.pause;
        break;
      case 'playing':
        miniTitle.textContent = label;
        expTitle.textContent = label;
        miniPlay.innerHTML = ICONS.pause;
        expPlay.innerHTML = ICONS.pause;
        miniPlay.title = 'Pause';
        expPlay.title = 'Pause';
        break;
      case 'paused':
        miniTitle.textContent = label + ' (paused)';
        expTitle.textContent = label;
        miniPlay.innerHTML = ICONS.play;
        expPlay.innerHTML = ICONS.play;
        miniPlay.title = 'Resume';
        expPlay.title = 'Resume';
        break;
      case 'stopped':
        miniTitle.textContent = label;
        expTitle.textContent = label;
        miniPlay.innerHTML = ICONS.play;
        expPlay.innerHTML = ICONS.play;
        miniPlay.title = 'Play';
        expPlay.title = 'Play';
        break;
      case 'error':
        miniTitle.textContent = 'Error: ' + (text || 'unknown');
        expTitle.textContent = 'Error';
        break;
    }

    // Also update the toolbar button
    const toolbarBtn = document.getElementById('narration-btn');
    if (toolbarBtn) {
      if (state === 'loading') {
        toolbarBtn.textContent = text || 'Loading...';
      } else if (state === 'playing') {
        toolbarBtn.textContent = 'Playing';
      } else if (state === 'paused') {
        toolbarBtn.textContent = 'Paused';
      } else {
        toolbarBtn.textContent = 'Listen';
      }
    }
  }

  function updateProgress() {
    if (!playerEl || lines.length === 0) return;

    // Calculate progress
    const total = lines.filter(l => l.type !== 'verse-gap').length;
    const done = lines.slice(0, cursor).filter(l => l.type !== 'verse-gap').length;
    const pct = total > 0 ? (done / total * 100) : 0;

    // Current verse label
    const currentItem = lines[cursor];
    const verseLabel = currentItem?.verseNum || '';

    // Update mini bar
    const miniProg = document.getElementById('narr-mini-prog');
    const miniSub = document.getElementById('narr-mini-sub');
    if (miniProg) miniProg.style.width = pct + '%';
    if (miniSub) miniSub.textContent = verseLabel ? ('Verse ' + verseLabel) : 'Kokoro TTS';

    // Update expanded
    const expVerse = document.getElementById('narr-exp-verse');
    const progFill = document.getElementById('narr-prog-fill');
    const progCurrent = document.getElementById('narr-prog-current');
    const progTotal = document.getElementById('narr-prog-total');
    if (expVerse) expVerse.textContent = verseLabel ? ('Verse ' + verseLabel) : '';
    if (progFill) progFill.style.width = pct + '%';
    if (progCurrent) progCurrent.textContent = verseLabel || '—';
    if (progTotal) progTotal.textContent = total + ' lines';
  }

  function updateSpeedDisplay() {
    if (!expandedEl) return;
    expandedEl.querySelectorAll('.narr-speed-btn').forEach(btn => {
      const s = parseFloat(btn.dataset.speed);
      btn.classList.toggle('active', s === currentSpeed);
    });
  }

  // ── Toolbar button (entry point) ──

  function initToolbarButton() {
    const controls = document.createElement('div');
    controls.id = 'narration-controls';

    const btn = document.createElement('button');
    btn.id = 'narration-btn';
    btn.textContent = 'Listen';
    btn.title = 'Listen to this chapter (British voice, Kokoro TTS)';
    btn.addEventListener('click', () => {
      if (loading) return;
      if (playing) {
        // Show/expand the player
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
      if (searchBtn) {
        controlsRow.insertBefore(controls, searchBtn);
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
    setVoice,
    setSpeed,
    get isPlaying() { return playing; },
    get isPaused() { return paused; },
    get isLoaded() { return !!tts; },
  };
})();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => NARRATION.init());
} else {
  NARRATION.init();
}
