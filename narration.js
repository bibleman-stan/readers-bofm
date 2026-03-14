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
 *   5. Respects swap state (reads modern or archaic text based on user toggle)
 */

const NARRATION = (() => {
  // ── Configuration ──
  const MODEL_ID = 'onnx-community/Kokoro-82M-v1.0-ONNX';
  const MODEL_OPTS = { dtype: 'q8', device: 'wasm' };
  const DEFAULT_VOICE = 'bm_george';   // British male
  const LINE_PAUSE_MS = 180;           // pause between sense-lines
  const VERSE_PAUSE_MS = 500;          // pause between verses
  const PERICOPE_PAUSE_MS = 900;       // pause before a section header

  // ── State ──
  let tts = null;
  let loading = false;
  let playing = false;
  let paused = false;
  let abortController = null;
  let currentVoice = DEFAULT_VOICE;
  let audioContext = null;

  // ── UI elements ──
  let btn = null;
  let progressEl = null;

  // ── Helpers ──

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
   * Extract the readable text from a line element, respecting swap state.
   * If swaps are "on" (modern), reads data-mod text; if "off", reads original.
   */
  function getLineText(el) {
    // Clone so we don't mutate the DOM
    const clone = el.cloneNode(true);

    // Check if Aid (modern language) is active — the global `aidOn` variable
    // is set by toggleAid() in the main script. When aid is on, .swap elements
    // already show data-mod text; .swap-quiet always show originals visually
    // but we want TTS to always read the modernized version for clarity.
    // So: always use data-mod for TTS (modern pronunciation is clearer for listeners).
    clone.querySelectorAll('.swap, .swap-quiet').forEach(span => {
      const mod = span.getAttribute('data-mod');
      if (mod) span.textContent = mod;
    });

    // Remove verse numbers, pericope labels, etc.
    clone.querySelectorAll('.verse-num, .parry-label-spacer').forEach(el => el.remove());

    // Get clean text
    let text = clone.textContent.trim();
    // Normalize whitespace
    text = text.replace(/\s+/g, ' ');
    return text;
  }

  /**
   * Gather all lines to read for the current chapter/view.
   * Returns an array of { element, text, type } objects.
   */
  function gatherLines() {
    const lines = [];

    // Find the currently visible book content
    const activeBook = document.querySelector('.book-content[style*="display: block"]')
                    || document.querySelector('.book-content:not([style*="display: none"])');
    if (!activeBook) return lines;

    // Determine if we're in sense-line mode or verse (prose) mode
    const isSenseLineMode = document.body.classList.contains('show-lines');

    // Walk through all children: pericope-headers and verses
    const children = activeBook.children;
    for (const child of children) {
      // Pericope header
      if (child.classList.contains('pericope-header')) {
        const mainEl = child.querySelector('.pericope-main');
        if (mainEl) {
          lines.push({
            element: child,
            text: mainEl.textContent.trim(),
            type: 'pericope'
          });
        }
        continue;
      }

      // Verse
      if (child.classList.contains('verse')) {
        if (isSenseLineMode) {
          // Read each sense-line separately
          const senseLines = child.querySelectorAll(':scope > .line');
          senseLines.forEach(line => {
            const text = getLineText(line);
            if (text) {
              lines.push({ element: line, text, type: 'line' });
            }
          });
        } else {
          // Prose mode: read the whole verse paragraph
          const para = child.querySelector('.line-para');
          if (para) {
            const text = getLineText(para);
            if (text) {
              lines.push({ element: para, text, type: 'verse' });
            }
          }
        }
        // Mark verse boundary
        if (lines.length > 0 && lines[lines.length - 1].type !== 'verse-gap') {
          lines.push({ element: null, text: '', type: 'verse-gap' });
        }
      }
    }

    return lines;
  }

  /**
   * Play a RawAudio object through the Web Audio API.
   * Returns a promise that resolves when playback completes.
   */
  async function playAudio(rawAudio, signal) {
    if (!audioContext) {
      audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    // Resume context if suspended (autoplay policy)
    if (audioContext.state === 'suspended') {
      await audioContext.resume();
    }

    // rawAudio should have .audio (Float32Array) and .sampling_rate
    const samples = rawAudio.audio || rawAudio.data;
    const sampleRate = rawAudio.sampling_rate || 24000;

    const buffer = audioContext.createBuffer(1, samples.length, sampleRate);
    buffer.getChannelData(0).set(samples);

    return new Promise((resolve, reject) => {
      const source = audioContext.createBufferSource();
      source.buffer = buffer;
      source.connect(audioContext.destination);
      source.onended = resolve;
      source.start(0);

      if (signal) {
        signal.addEventListener('abort', () => {
          source.stop();
          reject(new DOMException('Aborted', 'AbortError'));
        });
      }
    });
  }

  // ── Loading ──

  async function ensureModel(progressCallback) {
    if (tts) return;
    if (loading) return; // already loading

    loading = true;
    try {
      // Dynamic import of kokoro-js from CDN
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
    } finally {
      loading = false;
    }
  }

  // ── Highlight management ──

  function highlightLine(el) {
    // Remove previous highlights
    document.querySelectorAll('.narration-active').forEach(
      e => e.classList.remove('narration-active')
    );
    if (el) {
      el.classList.add('narration-active');
      // Scroll into view if needed
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

    updateButton('loading');

    try {
      // Load model (shows progress)
      await ensureModel((progress) => {
        if (progress.status === 'downloading' || progress.status === 'progress') {
          const pct = progress.progress ? Math.round(progress.progress) : 0;
          updateButton('loading', `Loading model... ${pct}%`);
        }
      });

      updateButton('playing');

      const lines = gatherLines();
      if (lines.length === 0) {
        console.warn('Narration: no lines found to read');
        stopPlayback();
        return;
      }

      for (let i = 0; i < lines.length; i++) {
        if (signal.aborted) break;

        // Handle pause
        while (paused && !signal.aborted) {
          await sleep(100, signal);
        }

        const item = lines[i];

        if (item.type === 'verse-gap') {
          await sleep(VERSE_PAUSE_MS, signal);
          continue;
        }

        if (item.type === 'pericope') {
          await sleep(PERICOPE_PAUSE_MS, signal);
          highlightLine(item.element);
          // Read section header
          const audio = await tts.generate(item.text, { voice: currentVoice });
          await playAudio(audio, signal);
          await sleep(PERICOPE_PAUSE_MS, signal);
          continue;
        }

        // Regular line or verse
        highlightLine(item.element);
        const audio = await tts.generate(item.text, { voice: currentVoice });
        await playAudio(audio, signal);

        // Pause between lines (shorter for sense-lines, longer for verse boundaries)
        if (item.type === 'line') {
          await sleep(LINE_PAUSE_MS, signal);
        }
      }
    } catch (e) {
      if (e.name !== 'AbortError') {
        console.error('Narration error:', e);
      }
    } finally {
      playing = false;
      paused = false;
      clearHighlight();
      updateButton('stopped');
    }
  }

  function pausePlayback() {
    paused = true;
    updateButton('paused');
  }

  function resumePlayback() {
    paused = false;
    updateButton('playing');
  }

  function stopPlayback() {
    if (abortController) {
      abortController.abort();
    }
    playing = false;
    paused = false;
    clearHighlight();
    updateButton('stopped');
  }

  // ── UI ──

  function updateButton(state, text) {
    if (!btn) return;
    btn.classList.remove('narration-loading', 'narration-playing', 'narration-paused');

    switch (state) {
      case 'loading':
        btn.classList.add('narration-loading');
        btn.innerHTML = text || '⏳ Loading...';
        btn.title = 'Loading TTS model...';
        break;
      case 'playing':
        btn.classList.add('narration-playing');
        btn.innerHTML = '⏸ Pause';
        btn.title = 'Pause narration';
        break;
      case 'paused':
        btn.classList.add('narration-paused');
        btn.innerHTML = '▶ Resume';
        btn.title = 'Resume narration';
        break;
      case 'stopped':
      default:
        btn.innerHTML = '🔊 Listen';
        btn.title = 'Listen to this chapter (British voice, Kokoro TTS)';
        break;
    }
  }

  function handleClick() {
    if (loading) return; // ignore clicks while model loads
    if (!playing) {
      startPlayback();
    } else if (paused) {
      resumePlayback();
    } else {
      pausePlayback();
    }
  }

  function handleStop() {
    stopPlayback();
  }

  /**
   * Initialize narration: inject button and CSS.
   */
  function init() {
    // Inject CSS for highlight and button
    const style = document.createElement('style');
    style.textContent = `
      .narration-active {
        background: rgba(100, 180, 255, 0.15);
        border-radius: 3px;
        transition: background 0.2s ease;
      }
      body.light-mode .narration-active {
        background: rgba(50, 120, 200, 0.1);
      }
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
      #narration-btn.narration-playing {
        background: rgba(100, 200, 100, 0.2);
        border-color: rgba(100, 200, 100, 0.4);
      }
      #narration-btn.narration-loading {
        opacity: 0.7;
        cursor: wait;
      }
      #narration-stop {
        background: rgba(200, 100, 100, 0.2);
        color: #c88;
        border: 1px solid rgba(200, 100, 100, 0.3);
        border-radius: 6px;
        padding: 4px 8px;
        font-size: 0.82em;
        cursor: pointer;
        display: none;
      }
      #narration-stop:hover {
        background: rgba(200, 100, 100, 0.35);
      }
      #narration-btn.narration-playing ~ #narration-stop,
      #narration-btn.narration-paused ~ #narration-stop {
        display: inline-block;
      }
      body.light-mode #narration-btn {
        color: #5a6a7a;
        background: rgba(90, 106, 122, 0.1);
        border-color: rgba(90, 106, 122, 0.25);
      }
      body.light-mode #narration-stop {
        color: #a55;
        background: rgba(200, 100, 100, 0.1);
        border-color: rgba(200, 100, 100, 0.25);
      }
    `;
    document.head.appendChild(style);

    // Create button container
    const controls = document.createElement('div');
    controls.id = 'narration-controls';

    btn = document.createElement('button');
    btn.id = 'narration-btn';
    btn.addEventListener('click', handleClick);
    updateButton('stopped');
    controls.appendChild(btn);

    const stopBtn = document.createElement('button');
    stopBtn.id = 'narration-stop';
    stopBtn.textContent = '⏹ Stop';
    stopBtn.title = 'Stop narration';
    stopBtn.addEventListener('click', handleStop);
    controls.appendChild(stopBtn);

    // Insert into the controls row (before the search/gear buttons)
    const controlsRow = document.querySelector('.controls-row');
    if (controlsRow) {
      const searchBtn = controlsRow.querySelector('.search-icon-btn');
      if (searchBtn) {
        controlsRow.insertBefore(controls, searchBtn);
      } else {
        controlsRow.appendChild(controls);
      }
    } else {
      // Fallback: float in bottom-right
      controls.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:9999;';
      document.body.appendChild(controls);
    }
  }

  // ── Public API ──
  return {
    init,
    play: startPlayback,
    pause: pausePlayback,
    resume: resumePlayback,
    stop: stopPlayback,
    setVoice(v) { currentVoice = v; },
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
