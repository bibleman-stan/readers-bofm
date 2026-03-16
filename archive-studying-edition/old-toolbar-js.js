/* Archive: Old Toolbar JavaScript State Machine
   Removed during Reading Edition redesign. Reference implementation for planned Studying Edition.

   Key responsibilities:
   - Manages toolbar expand/collapse states
   - Handles scroll-driven auto-collapse/expand
   - Touch tracking for drag gestures
   - Dynamic spacer height calculation
   - Panel management (settings, nav, background)
   - First-visit hint with MutationObserver
   - Click-outside-to-dismiss handlers

   Approximate line count: ~250 lines (structure provided, not production code)
*/

class ToolbarController {
  constructor() {
    this.toolbar = document.getElementById('reading-toolbar');
    this.spacer = document.getElementById('toolbar-spacer');
    this.collapsedSummary = document.querySelector('.collapsed-summary');
    this.toolbarTitle = document.getElementById('toolbar-title');
    this.content = document.querySelector('.toolbar-content');

    this.state = 'collapsed'; // collapsed, expanded, hidden
    this.lastScrollY = 0;
    this.scrollDirection = null;
    this.isDragging = false;
    this.touchStartY = 0;
    this.toolbarHeight = 0;
    this.firstVisit = !localStorage.getItem('toolbar-visited');

    this.bookButtons = document.querySelectorAll('.book-btn');
    this.pillButtons = document.querySelectorAll('.pill-btn');
    this.textModeButtons = document.querySelectorAll('.text-mode-btn');
    this.panels = document.querySelectorAll('.toolbar-panel');

    this.init();
  }

  /* ========== Initialization ========== */

  init() {
    // Calculate and set initial spacer height
    this.initSpacer();

    // Attach event listeners
    this.attachEventListeners();

    // Show first-visit hint with MutationObserver
    if (this.firstVisit) {
      this.showFirstVisitHint();
    } else {
      this.collapsedSummary.classList.remove('hint-visible');
    }

    // Initial state: collapsed on page load
    this.setState('collapsed');

    // Responsive: recalculate spacer on window resize
    window.addEventListener('resize', () => this.initSpacer());
  }

  // Dynamic spacer calculation
  // Prevents toolbar from overlapping content when expanded
  initSpacer() {
    if (!this.toolbar) return;

    const rect = this.toolbar.getBoundingClientRect();

    // When expanded, spacer height = toolbar height
    // When collapsed, spacer height = summary bar height (~48px)
    if (this.state === 'expanded') {
      this.toolbarHeight = rect.height;
      this.spacer.style.height = this.toolbarHeight + 'px';
    } else {
      this.spacer.style.height = '48px'; // summary bar height
    }
  }

  /* ========== Event Listeners ========== */

  attachEventListeners() {
    // Collapsed summary click to expand
    this.collapsedSummary.addEventListener('click', () => {
      this.manualExpand();
    });

    // Book button clicks
    this.bookButtons.forEach(btn => {
      btn.addEventListener('click', (e) => this.handleBookSelect(e));
    });

    // Pill buttons
    this.pillButtons.forEach(btn => {
      btn.addEventListener('click', (e) => this.handlePillButtonClick(e));
    });

    // Text mode selector (radio-style)
    this.textModeButtons.forEach(btn => {
      btn.addEventListener('click', (e) => this.handleTextModeChange(e));
    });

    // Scroll listener for auto-collapse/expand
    window.addEventListener('scroll', () => this.handleScroll(), { passive: true });

    // Touch tracking for toolbar drag
    this.toolbar.addEventListener('touchstart', (e) => this.handleTouchStart(e), { passive: true });
    this.toolbar.addEventListener('touchmove', (e) => this.handleTouchMove(e), { passive: true });
    this.toolbar.addEventListener('touchend', () => this.handleTouchEnd());

    // Click outside panels to dismiss
    document.addEventListener('click', (e) => this.handleClickOutside(e));

    // Escape key to collapse toolbar
    document.addEventListener('keydown', (e) => this.handleEscapeKey(e));

    // Content area tap-to-toggle on mobile
    document.getElementById('content').addEventListener('click', (e) => {
      this.handleContentTap(e);
    });
  }

  /* ========== State Management ========== */

  setState(newState) {
    // Valid states: 'collapsed', 'expanded', 'hidden'
    if (newState === this.state) return;

    this.toolbar.classList.remove('toolbar-collapsed', 'toolbar-expanded', 'toolbar-hidden');

    switch (newState) {
      case 'collapsed':
        this.toolbar.classList.add('toolbar-collapsed');
        this.content.style.display = 'none';
        this.spacer.style.height = '48px';
        break;

      case 'expanded':
        this.toolbar.classList.add('toolbar-expanded');
        this.content.style.display = 'block';
        this.initSpacer(); // Recalculate spacer for expanded content
        break;

      case 'hidden':
        this.toolbar.classList.add('toolbar-hidden');
        break;
    }

    this.state = newState;
  }

  manualExpand() {
    // User explicitly tapped the summary bar
    this.setState('expanded');
    this.lastScrollY = window.scrollY;
    localStorage.setItem('toolbar-visited', 'true');
  }

  manualCollapse() {
    // User explicitly dismissed the toolbar
    this.setState('collapsed');
    this.lastScrollY = window.scrollY;
  }

  /* ========== Scroll Handler ========== */

  handleScroll() {
    const currentScrollY = window.scrollY;

    // Determine scroll direction
    if (currentScrollY > this.lastScrollY) {
      this.scrollDirection = 'down';
    } else if (currentScrollY < this.lastScrollY) {
      this.scrollDirection = 'up';
    }

    // Auto-collapse on scroll down (only if expanded)
    if (this.scrollDirection === 'down' && this.state === 'expanded') {
      if (currentScrollY - this.lastScrollY > 50) { // Threshold: 50px
        this.manualCollapse();
      }
    }

    // Auto-expand on scroll up (only if collapsed)
    if (this.scrollDirection === 'up' && this.state === 'collapsed') {
      if (this.lastScrollY - currentScrollY > 30) { // Threshold: 30px
        // Don't auto-expand if near top of page
        if (currentScrollY > 100) {
          // Only hint, don't auto-expand to avoid jarring UX
          // this.manualExpand();
        }
      }
    }

    this.lastScrollY = currentScrollY;
  }

  /* ========== Touch Tracking ========== */

  handleTouchStart(e) {
    this.touchStartY = e.touches[0].clientY;
    this.isDragging = true;
    this.toolbar.classList.add('toolbar-dragging');
  }

  handleTouchMove(e) {
    // Could implement toolbar drag/swipe here
    // For now, just track movement
  }

  handleTouchEnd() {
    this.isDragging = false;
    this.toolbar.classList.remove('toolbar-dragging');
    this.touchStartY = 0;
  }

  /* ========== Book Selection ========== */

  handleBookSelect(e) {
    const bookId = e.target.dataset.book;

    // Update active button
    this.bookButtons.forEach(btn => btn.classList.remove('active'));
    e.target.classList.add('active');

    // Navigate to book (implementation depends on routing system)
    this.navigateToBook(bookId);

    // Auto-collapse after selection on mobile
    if (window.innerWidth < 768) {
      setTimeout(() => this.manualCollapse(), 300);
    }
  }

  navigateToBook(bookId) {
    // Placeholder: integrate with your routing system
    // e.g., window.location.hash = `#${bookId}/1`;
  }

  /* ========== Pill Button Handlers ========== */

  handlePillButtonClick(e) {
    const btn = e.target.closest('.pill-btn');

    if (btn.classList.contains('aid-toggle')) {
      this.toggleAid();
    } else if (btn.classList.contains('sections-toggle')) {
      this.toggleSections();
    } else if (btn.classList.contains('about-pill-btn')) {
      this.showAboutPanel();
    } else if (btn.classList.contains('gear-btn')) {
      this.togglePanel('settings-panel');
    }
  }

  toggleAid() {
    // Toggle display of modern word aids in text
    // Class: .verse-aid
    document.body.classList.toggle('show-aid');
  }

  toggleSections() {
    // Toggle display of section headers
    // Class: .section-header
    document.body.classList.toggle('show-sections');
  }

  showAboutPanel() {
    // Open about/info dialog
    // Placeholder implementation
  }

  /* ========== Text Mode Handler ========== */

  handleTextModeChange(e) {
    const btn = e.target.closest('.text-mode-btn');
    const mode = parseInt(btn.dataset.mode);

    // Update active button
    this.textModeButtons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    // Apply text mode
    this.applyTextMode(mode);
  }

  applyTextMode(mode) {
    // Remove all text mode classes
    document.body.classList.remove('show-lines', 'show-parry', 'show-prose');

    // Mode 0: Prose (running text, .line-para visible)
    // Mode 1: Sense Lines (poetic formatting, .line visible) - default
    // Mode 2: Parry Parallels (structural analysis, .line-parry visible)

    switch (mode) {
      case 0:
        document.body.classList.add('show-prose');
        break;
      case 1:
        document.body.classList.add('show-lines');
        break;
      case 2:
        document.body.classList.add('show-parry');
        break;
    }

    // Persist user preference
    localStorage.setItem('text-mode', mode.toString());
  }

  /* ========== Panel Management ========== */

  togglePanel(panelId) {
    const panel = document.getElementById(panelId);

    // Close other panels
    this.panels.forEach(p => {
      if (p.id !== panelId) {
        p.classList.remove('active');
      }
    });

    // Toggle target panel
    panel.classList.toggle('active');

    // Expand toolbar if not already expanded
    if (this.state === 'collapsed') {
      this.setState('expanded');
    }
  }

  /* ========== Click Outside to Dismiss ========== */

  handleClickOutside(e) {
    // Close panels if click is outside toolbar
    if (!this.toolbar.contains(e.target) && !e.target.closest('.toolbar-panel')) {
      this.panels.forEach(panel => panel.classList.remove('active'));
    }
  }

  /* ========== Keyboard Handling ========== */

  handleEscapeKey(e) {
    if (e.key === 'Escape') {
      // Collapse toolbar
      this.manualCollapse();

      // Close any open panels
      this.panels.forEach(panel => panel.classList.remove('active'));
    }
  }

  /* ========== Content Tap Handler ========== */

  handleContentTap(e) {
    // On mobile, tapping the content area collapses the toolbar if expanded
    // Only if user isn't interacting with a button or input
    if (e.target.tagName !== 'BUTTON' && e.target.tagName !== 'INPUT' && this.state === 'expanded') {
      // Optionally: only collapse if tapping above toolbar spacer area
      if (e.clientY > 100) { // Below collapsed summary height
        this.manualCollapse();
      }
    }
  }

  /* ========== First-Visit Hint ========== */

  showFirstVisitHint() {
    const hint = document.getElementById('toolbar-hint');
    if (!hint) return;

    // Show hint when content loads
    setTimeout(() => {
      hint.style.display = 'block';
    }, 500);

    // Monitor toolbar for user interaction (using MutationObserver)
    const observer = new MutationObserver(() => {
      if (this.state === 'expanded') {
        hint.style.display = 'none';
        observer.disconnect();
      }
    });

    observer.observe(this.toolbar, {
      attributes: true,
      attributeFilter: ['class']
    });

    // Auto-hide hint after 8 seconds
    setTimeout(() => {
      hint.style.display = 'none';
      observer.disconnect();
    }, 8000);

    // Dismiss button
    const dismissBtn = hint.querySelector('.hint-dismiss');
    if (dismissBtn) {
      dismissBtn.addEventListener('click', () => {
        hint.style.display = 'none';
        observer.disconnect();
      });
    }
  }

  /* ========== Update Title ========== */

  updateTitle(bookName, chapter) {
    if (this.toolbarTitle) {
      this.toolbarTitle.textContent = `${bookName} ${chapter}`;
    }
  }
}

/* ========== Initialization ========== */

// Create controller when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.toolbarController = new ToolbarController();
});

/* ========== Helper Functions ========== */

// Utility: Update toolbar title on page change
function updateToolbarDisplay(bookName, chapter) {
  if (window.toolbarController) {
    window.toolbarController.updateTitle(bookName, chapter);
  }
}

// Utility: Programmatically navigate to book
function selectBook(bookId) {
  const btn = document.querySelector(`[data-book="${bookId}"]`);
  if (btn) {
    btn.click();
  }
}

// Utility: Set text mode programmatically
function setTextMode(mode) {
  if (window.toolbarController) {
    window.toolbarController.applyTextMode(mode);
  }
}
