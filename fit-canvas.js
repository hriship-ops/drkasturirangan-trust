/* fit-canvas.js — scale 1440px-fixed canvases to fit narrower viewports.
   Add class="fit-canvas" to the 1440px wrapper element (not nav or footer).
   Uses CSS zoom so footer follows naturally and no height JS is needed.
   Hislife sidebar: position:fixed top is corrected for zoom via MutationObserver. */
(function () {
  'use strict';
  var CANVAS_W = 1440;
  var HL_NAV_TOP = 101; // px, matches .hl-year-col.is-fixed { top: 101px }

  function applyZoom() {
    var vw = document.documentElement.clientWidth;
    var scale = Math.min(1, vw / CANVAS_W);
    document.querySelectorAll('.fit-canvas').forEach(function (el) {
      el.style.zoom = scale < 1 ? scale : '';
    });
    fixHlSidebarTop(scale);
  }

  function fixHlSidebarTop(scale) {
    var nav = document.getElementById('hl-year-nav');
    if (!nav || !nav.classList.contains('is-fixed') || scale >= 1) return;
    var needed = Math.round(HL_NAV_TOP / scale) + 'px';
    if (nav.style.top !== needed) nav.style.top = needed;
  }

  function watchHlSidebar() {
    var nav = document.getElementById('hl-year-nav');
    if (!nav) return;
    new MutationObserver(function () {
      var vw = document.documentElement.clientWidth;
      var scale = Math.min(1, vw / CANVAS_W);
      fixHlSidebarTop(scale);
    }).observe(nav, { attributes: true, attributeFilter: ['class', 'style'] });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      applyZoom();
      watchHlSidebar();
    });
  } else {
    applyZoom();
    watchHlSidebar();
  }
  window.addEventListener('resize', applyZoom, { passive: true });
})();
