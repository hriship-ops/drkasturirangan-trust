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

  // Close when clicking outside the nav
  document.addEventListener('click', function (e) {
    if (!navLinks.classList.contains('nav-open')) return;
    if (hamburger.contains(e.target) || navLinks.contains(e.target)) return;
    closeAll();
  });

  // Clear sub-menus whenever the main nav closes
  hamburger.addEventListener('click', function () {
    // After the inline onclick runs, check if nav just closed
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
