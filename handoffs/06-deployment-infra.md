# 06 — Deployment & Infrastructure

## Hosting
- **GitHub Pages** from `main` branch
- **Domain:** bomreader.com (CNAME file in repo root)
- **Repo:** github.com/bibleman-stan/readers-bofm (public)

## Service Worker (sw.js)
- Strategy: cache app shell eagerly, cache books lazily (on first open)
- Option to pre-cache all books at once via message from page
- **Current version:** `bomreader-v62`
- **Versioning:** Every CSS/JS/HTML change requires a cache version bump. Version jumped from v31 (Mar 14) to v61 (Mar 18) due to rapid iteration — this is normal.
- Users need hard refresh (Ctrl+Shift+R) or wait for SW update cycle to see changes

## Git Workflow
- All work on `main` branch (no feature branches)
- Stan pushes from his local machine (sandbox can't push — gets 403 proxy error)
- Commits should be made proactively without being asked
- Audio files (large MP3s) are committed directly to the repo (no LFS)

## UNPUSHED COMMITS (as of Mar 18 evening)
Three commits need pushing:
1. `21b57e3` — Switch all books to Samuel voice
2. `0e78a9e` — Add 2 Nephi Sister M audio (superseded by next commit)
3. `b2a6509` — Replace Sister M with Samuel ch 1-5

## Security Alerts
- **GitHub secrets alert:** Google API key in `annotations.js` line 26. Needs restriction in Google Cloud Console.
- **ElevenLabs API key** is in the Colab notebooks (not in the committed repo code — only in "Copy to Drive" versions with Find & Replace applied).

## Offline Support
- Service worker caches app shell on install
- "Save for offline" button in bottom sheet pre-caches all book HTML fragments
- Audio files cached on first play

---
### Update — 2026-03-18
- Cache version bumped from v61 to v62 after Mosiah HTML rebuild
- Additional unpushed commits: structured handoff docs creation, colometry handoff, Mosiah text edits, and HTML rebuild

---
*Last updated: 2026-03-18*
