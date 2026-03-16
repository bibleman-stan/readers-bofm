// ═══════════════════════════════════════════════════════════════════
// ANNOTATIONS MODULE — User notes & tags anchored to verse IDs
//
// Requires Firebase JS SDK (loaded via CDN in index.html):
//   firebase-app-compat.js, firebase-auth-compat.js, firebase-firestore-compat.js
//
// Data model (Firestore):
//   Collection: annotations/{docId}
//     userId:     string
//     verseId:    string  (e.g. "1nephi.1.1")
//     note:       string
//     tags:       string[]
//     visibility: string  ("private")  — future: "public"
//     createdAt:  timestamp
//     updatedAt:  timestamp
//
//   Collection: userMeta/{uid}
//     tags:       string[]   — deduplicated list of all tags this user has used
// ═══════════════════════════════════════════════════════════════════

var ANNOTATIONS = (function() {
  'use strict';

  // ── Firebase config — MUST be replaced with your project's config ──
  var firebaseConfig = {
    apiKey: '',
    authDomain: '',
    projectId: '',
    storageBucket: '',
    messagingSenderId: '',
    appId: ''
  };

  var db = null;
  var auth = null;
  var currentUser = null;
  var chapterAnnotations = {};   // verseId → annotation doc
  var userTags = [];             // all tags this user has ever used
  var modalOpen = false;

  // ── Init ──
  function init() {
    if (!firebaseConfig.apiKey) {
      console.warn('[Annotations] Firebase not configured — annotations disabled.');
      hideAnnotationUI();
      return;
    }
    if (typeof firebase === 'undefined') {
      console.warn('[Annotations] Firebase SDK not loaded.');
      hideAnnotationUI();
      return;
    }

    // Initialize Firebase (if not already)
    if (!firebase.apps.length) {
      firebase.initializeApp(firebaseConfig);
    }
    db = firebase.firestore();
    auth = firebase.auth();

    // Auth state listener
    auth.onAuthStateChanged(function(user) {
      currentUser = user;
      updateAuthUI();
      if (user) {
        loadUserTags();
      } else {
        chapterAnnotations = {};
        userTags = [];
        clearAnnotationIndicators();
      }
    });

    // Show sign-in button
    showAnnotationUI();
  }

  // ── Auth ──
  function signIn() {
    if (!auth) return;
    var provider = new firebase.auth.GoogleAuthProvider();
    auth.signInWithPopup(provider).catch(function(err) {
      console.error('[Annotations] Sign-in failed:', err);
    });
  }

  function signOut() {
    if (!auth) return;
    auth.signOut();
  }

  function updateAuthUI() {
    var btn = document.getElementById('annotation-auth-btn');
    if (!btn) return;
    if (currentUser) {
      btn.textContent = '✎';
      btn.title = 'Signed in as ' + (currentUser.displayName || currentUser.email) + ' — click to manage annotations';
      btn.onclick = function() { openAnnotationDashboard(); };
    } else {
      btn.textContent = '✎';
      btn.title = 'Sign in to annotate';
      btn.onclick = function() { signIn(); };
    }
  }

  function showAnnotationUI() {
    var btn = document.getElementById('annotation-auth-btn');
    if (btn) btn.style.display = '';
  }

  function hideAnnotationUI() {
    var btn = document.getElementById('annotation-auth-btn');
    if (btn) btn.style.display = 'none';
  }

  // ── Load annotations for a chapter ──
  function loadChapterAnnotations(bookId, chapter) {
    if (!db || !currentUser) return;
    var prefix = bookId + '.' + chapter + '.';
    chapterAnnotations = {};

    db.collection('annotations')
      .where('userId', '==', currentUser.uid)
      .where('verseId', '>=', prefix)
      .where('verseId', '<=', prefix + '\uf8ff')
      .get()
      .then(function(snapshot) {
        snapshot.forEach(function(doc) {
          var data = doc.data();
          data._id = doc.id;
          chapterAnnotations[data.verseId] = data;
        });
        applyAnnotationIndicators(bookId);
      })
      .catch(function(err) {
        console.error('[Annotations] Failed to load:', err);
      });
  }

  // ── Load user's tag vocabulary ──
  function loadUserTags() {
    if (!db || !currentUser) return;
    db.collection('userMeta').doc(currentUser.uid).get()
      .then(function(doc) {
        if (doc.exists && doc.data().tags) {
          userTags = doc.data().tags;
        } else {
          userTags = [];
        }
      })
      .catch(function(err) {
        console.error('[Annotations] Failed to load tags:', err);
      });
  }

  // ── Save / update user's tag vocabulary ──
  function updateUserTags(newTags) {
    if (!db || !currentUser) return;
    // Merge new tags into existing set
    var tagSet = {};
    userTags.forEach(function(t) { tagSet[t] = true; });
    newTags.forEach(function(t) {
      var normalized = t.trim().toLowerCase();
      if (normalized) tagSet[normalized] = true;
    });
    userTags = Object.keys(tagSet).sort();

    db.collection('userMeta').doc(currentUser.uid).set({
      tags: userTags
    }, { merge: true });
  }

  // ── Save annotation ──
  function saveAnnotation(verseId, note, tags) {
    if (!db || !currentUser) return Promise.reject('Not signed in');
    var normalizedTags = tags.map(function(t) { return t.trim().toLowerCase(); }).filter(Boolean);

    var existing = chapterAnnotations[verseId];
    var docData = {
      userId: currentUser.uid,
      verseId: verseId,
      note: note,
      tags: normalizedTags,
      visibility: 'private',
      updatedAt: firebase.firestore.FieldValue.serverTimestamp()
    };

    var promise;
    if (existing && existing._id) {
      promise = db.collection('annotations').doc(existing._id).update(docData);
    } else {
      docData.createdAt = firebase.firestore.FieldValue.serverTimestamp();
      promise = db.collection('annotations').add(docData);
    }

    return promise.then(function(ref) {
      if (ref && ref.id) docData._id = ref.id;
      else if (existing) docData._id = existing._id;
      chapterAnnotations[verseId] = docData;
      updateUserTags(normalizedTags);
      return docData;
    });
  }

  // ── Delete annotation ──
  function deleteAnnotation(verseId) {
    if (!db || !currentUser) return Promise.reject('Not signed in');
    var existing = chapterAnnotations[verseId];
    if (!existing || !existing._id) return Promise.resolve();

    return db.collection('annotations').doc(existing._id).delete().then(function() {
      delete chapterAnnotations[verseId];
    });
  }

  // ── Visual indicators on annotated verses ──
  function applyAnnotationIndicators(bookId) {
    // Clear existing indicators
    clearAnnotationIndicators();
    // Add dots to annotated verses
    var bookEl = document.getElementById('book-' + bookId);
    if (!bookEl) return;
    var verseNums = bookEl.querySelectorAll('.verse-num');
    verseNums.forEach(function(vn) {
      var ref = vn.textContent.trim();  // e.g. "1:3"
      var parts = ref.split(':');
      if (parts.length !== 2) return;
      var verseId = bookId + '.' + parts[0] + '.' + parts[1];
      if (chapterAnnotations[verseId]) {
        var dot = document.createElement('span');
        dot.className = 'annotation-dot';
        dot.title = 'You have a note on this verse';
        vn.parentElement.insertBefore(dot, vn);
      }
    });
  }

  function clearAnnotationIndicators() {
    document.querySelectorAll('.annotation-dot').forEach(function(el) { el.remove(); });
  }

  // ── Annotation modal ──
  function openModal(verseId, verseSummary) {
    if (!currentUser) { signIn(); return; }
    modalOpen = true;

    var existing = chapterAnnotations[verseId] || {};
    var overlay = document.getElementById('annotation-overlay');
    if (!overlay) {
      overlay = createModalHTML();
      document.body.appendChild(overlay);
    }

    document.getElementById('annotation-verse-ref').textContent = formatVerseId(verseId);
    document.getElementById('annotation-verse-preview').textContent = verseSummary || '';
    document.getElementById('annotation-note').value = existing.note || '';
    document.getElementById('annotation-tags-input').value = (existing.tags || []).join(', ');
    document.getElementById('annotation-delete-btn').style.display = existing._id ? '' : 'none';

    // Store current verseId on the overlay
    overlay.dataset.verseId = verseId;

    overlay.style.display = 'flex';
    setTimeout(function() {
      overlay.classList.add('open');
      document.getElementById('annotation-note').focus();
    }, 10);

    // Build tag autocomplete
    buildTagAutocomplete();
  }

  function closeModal() {
    modalOpen = false;
    var overlay = document.getElementById('annotation-overlay');
    if (overlay) {
      overlay.classList.remove('open');
      setTimeout(function() { overlay.style.display = 'none'; }, 200);
    }
  }

  function createModalHTML() {
    var overlay = document.createElement('div');
    overlay.id = 'annotation-overlay';
    overlay.innerHTML =
      '<div class="annotation-modal">' +
        '<div class="annotation-header">' +
          '<span id="annotation-verse-ref" class="annotation-ref"></span>' +
          '<button class="annotation-close" onclick="ANNOTATIONS.closeModal()">&times;</button>' +
        '</div>' +
        '<div id="annotation-verse-preview" class="annotation-preview"></div>' +
        '<label class="annotation-label">Note</label>' +
        '<textarea id="annotation-note" class="annotation-textarea" rows="4" placeholder="Write your thoughts..."></textarea>' +
        '<label class="annotation-label">Tags <span style="opacity:0.5; font-size:0.85em;">(comma-separated)</span></label>' +
        '<div style="position:relative;">' +
          '<input id="annotation-tags-input" class="annotation-input" type="text" placeholder="e.g. faith, prayer, covenant" autocomplete="off">' +
          '<div id="annotation-tag-suggestions" class="annotation-suggestions"></div>' +
        '</div>' +
        '<div class="annotation-actions">' +
          '<button id="annotation-delete-btn" class="annotation-btn annotation-btn-danger" onclick="ANNOTATIONS.handleDelete()">Delete</button>' +
          '<button class="annotation-btn annotation-btn-save" onclick="ANNOTATIONS.handleSave()">Save</button>' +
        '</div>' +
      '</div>';

    // Close on backdrop click
    overlay.addEventListener('click', function(e) {
      if (e.target === overlay) closeModal();
    });

    // Tag autocomplete
    overlay.querySelector('#annotation-tags-input').addEventListener('input', function() {
      buildTagAutocomplete();
    });

    return overlay;
  }

  function buildTagAutocomplete() {
    var input = document.getElementById('annotation-tags-input');
    var container = document.getElementById('annotation-tag-suggestions');
    if (!input || !container) return;

    var val = input.value;
    var parts = val.split(',');
    var currentPart = (parts[parts.length - 1] || '').trim().toLowerCase();

    container.innerHTML = '';
    if (!currentPart || currentPart.length < 1) return;

    var matches = userTags.filter(function(t) {
      return t.indexOf(currentPart) === 0 && t !== currentPart;
    }).slice(0, 6);

    if (matches.length === 0) return;

    matches.forEach(function(tag) {
      var div = document.createElement('div');
      div.className = 'annotation-suggestion';
      div.textContent = tag;
      div.addEventListener('mousedown', function(e) {
        e.preventDefault();
        parts[parts.length - 1] = ' ' + tag;
        input.value = parts.join(',') + ', ';
        container.innerHTML = '';
        input.focus();
      });
      container.appendChild(div);
    });
  }

  function handleSave() {
    var overlay = document.getElementById('annotation-overlay');
    var verseId = overlay.dataset.verseId;
    var note = document.getElementById('annotation-note').value.trim();
    var tagsStr = document.getElementById('annotation-tags-input').value;
    var tags = tagsStr.split(',').map(function(t) { return t.trim(); }).filter(Boolean);

    if (!note && tags.length === 0) {
      // Nothing to save — treat as delete if existing
      if (chapterAnnotations[verseId]) {
        handleDelete();
      } else {
        closeModal();
      }
      return;
    }

    saveAnnotation(verseId, note, tags).then(function() {
      closeModal();
      // Re-apply indicators for current book
      var parts = verseId.split('.');
      applyAnnotationIndicators(parts[0]);
    }).catch(function(err) {
      console.error('[Annotations] Save failed:', err);
    });
  }

  function handleDelete() {
    var overlay = document.getElementById('annotation-overlay');
    var verseId = overlay.dataset.verseId;

    deleteAnnotation(verseId).then(function() {
      closeModal();
      var parts = verseId.split('.');
      applyAnnotationIndicators(parts[0]);
    }).catch(function(err) {
      console.error('[Annotations] Delete failed:', err);
    });
  }

  function formatVerseId(verseId) {
    // "1nephi.3.7" → "1 Nephi 3:7"
    var parts = verseId.split('.');
    var bookId = parts[0];
    var meta = window.bookMeta ? window.bookMeta[bookId] : null;
    var bookName = meta ? meta.name : bookId;
    return bookName + ' ' + parts[1] + ':' + parts[2];
  }

  // ── Tag search / dashboard ──
  function openAnnotationDashboard() {
    var overlay = document.getElementById('annotation-dashboard');
    if (!overlay) {
      overlay = createDashboardHTML();
      document.body.appendChild(overlay);
    }
    overlay.style.display = 'flex';
    setTimeout(function() { overlay.classList.add('open'); }, 10);

    // Load all annotations
    loadAllAnnotations();
  }

  function closeDashboard() {
    var overlay = document.getElementById('annotation-dashboard');
    if (overlay) {
      overlay.classList.remove('open');
      setTimeout(function() { overlay.style.display = 'none'; }, 200);
    }
  }

  function createDashboardHTML() {
    var overlay = document.createElement('div');
    overlay.id = 'annotation-dashboard';
    overlay.className = 'annotation-overlay-base';
    overlay.innerHTML =
      '<div class="annotation-dashboard-panel">' +
        '<div class="annotation-header">' +
          '<span class="annotation-ref">My Annotations</span>' +
          '<button class="annotation-close" onclick="ANNOTATIONS.closeDashboard()">&times;</button>' +
        '</div>' +
        '<div class="annotation-dashboard-auth">' +
          '<span id="annotation-user-name"></span>' +
          '<button class="annotation-btn annotation-btn-small" onclick="ANNOTATIONS.signOut(); ANNOTATIONS.closeDashboard();">Sign out</button>' +
        '</div>' +
        '<div style="padding: 0 16px 8px;">' +
          '<input id="annotation-search-input" class="annotation-input" type="text" placeholder="Filter by tags (space = AND, -tag = NOT)" autocomplete="off">' +
        '</div>' +
        '<div id="annotation-dashboard-count" style="padding: 0 16px 8px; font-size: 0.8em; color: #888;"></div>' +
        '<div id="annotation-dashboard-results" class="annotation-dashboard-results"></div>' +
      '</div>';

    overlay.addEventListener('click', function(e) {
      if (e.target === overlay) closeDashboard();
    });

    // Search input
    var searchInput = overlay.querySelector('#annotation-search-input');
    searchInput.addEventListener('input', function() {
      filterDashboard(this.value);
    });

    return overlay;
  }

  var allAnnotations = [];

  function loadAllAnnotations() {
    if (!db || !currentUser) return;
    var nameEl = document.getElementById('annotation-user-name');
    if (nameEl) nameEl.textContent = currentUser.displayName || currentUser.email || '';

    db.collection('annotations')
      .where('userId', '==', currentUser.uid)
      .orderBy('updatedAt', 'desc')
      .get()
      .then(function(snapshot) {
        allAnnotations = [];
        snapshot.forEach(function(doc) {
          var data = doc.data();
          data._id = doc.id;
          allAnnotations.push(data);
        });
        filterDashboard(document.getElementById('annotation-search-input').value);
      })
      .catch(function(err) {
        console.error('[Annotations] Dashboard load failed:', err);
      });
  }

  function filterDashboard(query) {
    var q = (query || '').trim().toLowerCase();
    var terms = q.split(/\s+/).filter(Boolean);

    var filtered = allAnnotations.filter(function(ann) {
      if (terms.length === 0) return true;
      return terms.every(function(term) {
        if (term.charAt(0) === '-') {
          var neg = term.slice(1);
          return !ann.tags.some(function(t) { return t === neg; });
        }
        return ann.tags.some(function(t) { return t === term; }) ||
               ann.note.toLowerCase().indexOf(term) !== -1;
      });
    });

    renderDashboardResults(filtered);
  }

  function renderDashboardResults(results) {
    var container = document.getElementById('annotation-dashboard-results');
    var countEl = document.getElementById('annotation-dashboard-count');
    if (!container) return;

    countEl.textContent = results.length + ' annotation' + (results.length !== 1 ? 's' : '');
    container.innerHTML = '';

    if (results.length === 0) {
      container.innerHTML = '<div style="text-align:center; color:#666; padding:2em;">No annotations found.</div>';
      return;
    }

    results.forEach(function(ann) {
      var card = document.createElement('div');
      card.className = 'annotation-result-card';

      var ref = document.createElement('div');
      ref.className = 'annotation-result-ref';
      ref.textContent = formatVerseId(ann.verseId);

      var note = document.createElement('div');
      note.className = 'annotation-result-note';
      note.textContent = ann.note || '(no note)';

      var tagsDiv = document.createElement('div');
      tagsDiv.className = 'annotation-result-tags';
      (ann.tags || []).forEach(function(t) {
        var chip = document.createElement('span');
        chip.className = 'annotation-tag-chip';
        chip.textContent = t;
        tagsDiv.appendChild(chip);
      });

      card.appendChild(ref);
      if (ann.note) card.appendChild(note);
      if (ann.tags && ann.tags.length) card.appendChild(tagsDiv);

      // Click to navigate
      card.addEventListener('click', function() {
        closeDashboard();
        var parts = ann.verseId.split('.');
        if (typeof window.switchBook === 'function' && typeof window.hideWelcome === 'function') {
          window.hideWelcome();
          window._pendingVerseScroll = { bookId: parts[0], chapter: parseInt(parts[1]), verse: parseInt(parts[2]) };
          window.switchBook(parts[0], parseInt(parts[1]));
          // Poll for verse element
          var attempts = 0;
          var checker = setInterval(function() {
            attempts++;
            var verseRef = parts[1] + ':' + parts[2];
            var allVerses = document.querySelectorAll('#book-' + parts[0] + ' .verse-num');
            for (var i = 0; i < allVerses.length; i++) {
              if (allVerses[i].textContent.trim() === verseRef) {
                var verseDiv = allVerses[i].closest('.verse');
                if (verseDiv) {
                  verseDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
                  verseDiv.style.transition = 'background 0.3s';
                  verseDiv.style.background = 'rgba(124,175,194,0.15)';
                  setTimeout(function() { verseDiv.style.background = ''; }, 2000);
                }
                clearInterval(checker);
                window._pendingVerseScroll = null;
                return;
              }
            }
            if (attempts >= 40) { clearInterval(checker); window._pendingVerseScroll = null; }
          }, 100);
        }
      });

      container.appendChild(card);
    });
  }

  // ── Verse click handler — opens annotation modal on verse-num tap ──
  function handleVerseClick(e) {
    if (!currentUser && !firebaseConfig.apiKey) return;

    var verseNum = e.target.closest('.verse-num');
    if (!verseNum) return;

    var ref = verseNum.textContent.trim();  // e.g. "3:7"
    var parts = ref.split(':');
    if (parts.length !== 2) return;

    // Determine current book
    var bookEl = verseNum.closest('.book-content');
    if (!bookEl) return;
    var bookId = bookEl.id.replace('book-', '');

    var verseId = bookId + '.' + parts[0] + '.' + parts[1];

    // Get a text preview
    var verseDiv = verseNum.closest('.verse');
    var preview = '';
    if (verseDiv) {
      preview = verseDiv.textContent.replace(ref, '').trim().substring(0, 120);
    }

    openModal(verseId, preview);
  }

  // ── Public API ──
  return {
    init: init,
    signIn: signIn,
    signOut: signOut,
    openModal: openModal,
    closeModal: closeModal,
    handleSave: handleSave,
    handleDelete: handleDelete,
    handleVerseClick: handleVerseClick,
    loadChapterAnnotations: loadChapterAnnotations,
    openAnnotationDashboard: openAnnotationDashboard,
    closeDashboard: closeDashboard,
    get isModalOpen() { return modalOpen; },
    get currentUser() { return currentUser; }
  };
})();

// Auto-init on DOM ready
document.addEventListener('DOMContentLoaded', function() {
  ANNOTATIONS.init();

  // Listen for verse-num clicks on the book content container
  var container = document.getElementById('book-content-container');
  if (container) {
    container.addEventListener('click', ANNOTATIONS.handleVerseClick);
  }
});
