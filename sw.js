// Service Worker for bomreader.com
// Strategy: cache app shell eagerly, cache books lazily (on first open),
// with option to pre-cache all books at once via message from page.

const CACHE_NAME = 'bomreader-v46';

// App shell — cached on install
const SHELL_ASSETS = [
  './',
  './index.html',
  './narration.js',
];

// All book fragments — cached lazily or on demand
const BOOK_IDS = [
  '1nephi','2nephi','jacob','enos','jarom','omni','words-of-mormon',
  'mosiah','alma','helaman','3nephi','4nephi','mormon','ether','moroni'
];
const BOOK_URLS = BOOK_IDS.map(id => `./books/${id}.html`);

// Install: cache the app shell
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(SHELL_ASSETS))
  );
  self.skipWaiting();
});

// Activate: clean old caches, then tell all open tabs to refresh
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
     .then(() => self.clients.matchAll({ type: 'window' }))
     .then(clients => {
       clients.forEach(client => client.postMessage({ type: 'SW_UPDATED' }));
     })
  );
});

// Fetch: cache-first for books and shell, network-first for fonts (so updates come through)
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Google Fonts: cache-first (they rarely change)
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    event.respondWith(
      caches.match(event.request).then(cached => {
        if (cached) return cached;
        return fetch(event.request).then(response => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          }
          return response;
        });
      })
    );
    return;
  }

  // Same-origin: network-first for HTML and JS (so updates come through), cache-first for everything else
  if (url.origin === self.location.origin) {
    const isAppCode = url.pathname.endsWith('.html') || url.pathname.endsWith('.js')
                   || url.pathname === '/' || url.pathname.endsWith('/');
    if (isAppCode) {
      // Network-first: try fresh copy, fall back to cache for offline
      event.respondWith(
        fetch(event.request).then(response => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          }
          return response;
        }).catch(() => caches.match(event.request))
      );
    } else {
      // Cache-first for static assets (fonts, data, images, audio)
      event.respondWith(
        caches.match(event.request).then(cached => {
          if (cached) return cached;
          return fetch(event.request).then(response => {
            if (response.ok) {
              const clone = response.clone();
              caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
            }
            return response;
          });
        })
      );
    }
    return;
  }

  // Everything else: network only
  event.respondWith(fetch(event.request));
});

// Message handler: pre-cache all books on demand
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'CACHE_ALL_BOOKS') {
    const port = event.ports[0];
    caches.open(CACHE_NAME).then(async cache => {
      let done = 0;
      for (const url of BOOK_URLS) {
        try {
          // Check if already cached
          const existing = await cache.match(url);
          if (!existing) {
            await cache.add(url);
          }
          done++;
          if (port) port.postMessage({ type: 'PROGRESS', done, total: BOOK_URLS.length });
        } catch (err) {
          done++;
          if (port) port.postMessage({ type: 'PROGRESS', done, total: BOOK_URLS.length, error: url });
        }
      }
      if (port) port.postMessage({ type: 'COMPLETE', cached: BOOK_URLS.length });
    });
  }

  // Flush entire cache and reload fresh
  if (event.data && event.data.type === 'FLUSH_CACHE') {
    const port = event.ports[0];
    caches.delete(CACHE_NAME).then(() => {
      // Re-create cache with shell
      return caches.open(CACHE_NAME).then(cache => cache.addAll(SHELL_ASSETS));
    }).then(() => {
      if (port) port.postMessage({ type: 'FLUSH_COMPLETE' });
    });
  }

  // Report which books are currently cached
  if (event.data && event.data.type === 'CHECK_CACHE') {
    const port = event.ports[0];
    caches.open(CACHE_NAME).then(async cache => {
      let cachedCount = 0;
      for (const url of BOOK_URLS) {
        const existing = await cache.match(url);
        if (existing) cachedCount++;
      }
      if (port) port.postMessage({ type: 'CACHE_STATUS', cached: cachedCount, total: BOOK_URLS.length });
    });
  }
});
