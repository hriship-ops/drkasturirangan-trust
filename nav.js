(function () {
  'use strict';

  var hamburger = document.querySelector('.nav-hamburger');
  var navLinks  = document.querySelector('.nav-links');
  if (!hamburger || !navLinks) return;

  function isMobile() {
    return getComputedStyle(hamburger).display !== 'none';
  }

  function closeAll() {
    navLinks.classList.remove('nav-open');
    hamburger.setAttribute('aria-expanded', 'false');
    navLinks.querySelectorAll('.nav-sub-open').forEach(function (li) {
      li.classList.remove('nav-sub-open');
    });
  }

  // Close when tapping/clicking outside the nav.
  // iOS Safari doesn't fire 'click' on non-interactive elements (divs, sections),
  // so we listen on both 'touchstart' and 'click' and deduplicate with a flag.
  var _justClosed = false;
  function handleOutside(e) {
    if (_justClosed) return;
    if (!navLinks.classList.contains('nav-open')) return;
    var path = e.composedPath ? e.composedPath() : [];
    var inNav = path.length
      ? path.some(function (el) { return el === hamburger || el === navLinks; })
      : (hamburger.contains(e.target) || navLinks.contains(e.target));
    if (inNav) return;
    _justClosed = true;
    closeAll();
    setTimeout(function () { _justClosed = false; }, 300);
  }
  document.addEventListener('touchstart', handleOutside, { passive: true });
  document.addEventListener('click', handleOutside);

  // Clear sub-menus whenever the main nav closes
  hamburger.addEventListener('click', function () {
    setTimeout(function () {
      if (!navLinks.classList.contains('nav-open')) {
        navLinks.querySelectorAll('.nav-sub-open').forEach(function (li) {
          li.classList.remove('nav-sub-open');
        });
      }
    }, 0);
  });

  // Sub-menu toggle on mobile tap
  navLinks.querySelectorAll('li > a').forEach(function (link) {
    link.addEventListener('click', function (e) {
      if (!isMobile()) return;
      var li = this.closest('li');
      if (!li.querySelector('.nav-dropdown')) return;
      e.preventDefault();
      var wasOpen = li.classList.contains('nav-sub-open');
      navLinks.querySelectorAll('li').forEach(function (l) {
        l.classList.remove('nav-sub-open');
      });
      if (!wasOpen) li.classList.add('nav-sub-open');
    });
  });
})();
