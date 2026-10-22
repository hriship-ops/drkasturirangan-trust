// mobile-hislife.js
// Stacks the absolute-positioned timeline elements sequentially on mobile,
// eliminating the large gaps created by the 1440px desktop canvas layout.
// Runs after window load so image heights are known.

(function () {
  'use strict';

  if (window.innerWidth > 768) return;

  // Cancel fit-canvas.js zoom — it applies 0.27 scale via inline style.
  // CSS zoom:1!important may not override it in Chrome<128 where zoom was non-standard.
  function clearZoom() {
    var w = document.querySelector('.hl-wrap');
    if (w && w.style.zoom) w.style.zoom = '';
  }
  clearZoom();
  window.addEventListener('resize', clearZoom, { passive: true });

  function reflow() {
    var wrap = document.querySelector('.hl-wrap');
    if (!wrap) return;
    clearZoom(); // ensure zoom is clear before measuring offsetHeights

    // Explicitly hide placeholder screenshots that create duplicate photos
    // (CSS attribute selector may not fire on first paint if stylesheet is cached old)
    ['screenshot-2026-07-03-at-12-20-08-pm',
     'screenshot-2026-07-03-at-12-35-50-pm',
     'screenshot-2026-07-15-at-11-45-42-pm'].forEach(function (name) {
      var img = wrap.querySelector('img[src*="' + name + '"]');
      if (img) img.style.display = 'none';
    });

    // Classes that stack vertically (content elements)
    var STACK = ['hl-hline', 'hl-year', 'hl-event', 'hl-photo', 'hl-bbtext', 'hl-band'];
    // Classes repositioned to match their nearest content companion
    var DECO  = ['hl-dot', 'hl-vline', 'hl-bbline'];

    function getCls(el) {
      var all = STACK.concat(DECO);
      for (var i = 0; i < all.length; i++) {
        if (el.classList.contains(all[i])) return all[i];
      }
      return null;
    }

    // Collect all timeline elements (those with inline style.top, not display:none)
    var items = [];
    var ch = Array.prototype.slice.call(wrap.children);
    ch.forEach(function (el) {
      if (!el.style.top) return;          // hero elements: CSS-positioned, no inline top
      if (window.getComputedStyle(el).display === 'none') return; // hidden by CSS
      var top = parseInt(el.style.top);
      if (isNaN(top)) return;
      var cls = getCls(el);
      if (!cls) return;
      items.push({ el: el, origTop: top, cls: cls });
    });
    items.sort(function (a, b) { return a.origTop - b.origTop; });

    // Build band map: each hl-band covers origTop .. origTop+517
    var bands = [];
    items.forEach(function (i) {
      if (i.cls === 'hl-band') bands.push(i);
    });

    function inBand(origTop) {
      for (var i = 0; i < bands.length; i++) {
        var b = bands[i];
        if (origTop > b.origTop && origTop < b.origTop + 517) return b;
      }
      return null;
    }

    // Spacing: [before, after] px for each class
    var SP = {
      'hl-hline':  [16, 4],
      'hl-year':   [4,  6],
      'hl-event':  [0,  10],
      'hl-photo':  [10, 10],
      'hl-bbtext': [0,  12],
      'hl-band':   [0,  0]
    };

    var y = 360; // start below hero (portrait ends ~136, subtitle ends ~340)

    // First pass: stack content elements
    items.forEach(function (item) {
      var cls = item.cls;
      if (DECO.indexOf(cls) >= 0) return;   // skip decorative
      if (cls === 'hl-band')      return;   // positioned by content inside it

      var sp = SP[cls];
      y += sp[0];

      // Open the band if this is the first content element inside it
      var band = inBand(item.origTop);
      if (band && !band.el._moStart) {
        band.el._moStart = y + 8;             // 8px gap below whatever came before (e.g. year label)
        band.el.style.top = band.el._moStart + 'px';
        y += 8 + 20;                          // advance into band, with 20px internal top padding
      }

      item.el.style.top = y + 'px';

      var h = item.el.offsetHeight;
      if (h < 10) h = 60; // fallback if image not loaded

      y += h + sp[1];

      // Stretch band to contain this element and advance y past band bottom
      if (band) {
        band.el._moEnd = y + 32;
        band.el.style.height = (band.el._moEnd - band.el._moStart) + 'px';
        y = band.el._moEnd; // next element starts after the band, not inside it
      }
    });

    // Second pass: position decorative elements at their nearest companion's new top
    items.forEach(function (item) {
      if (DECO.indexOf(item.cls) < 0) return;
      var best = null, bestD = 999999;
      items.forEach(function (other) {
        if (DECO.indexOf(other.cls) >= 0 || other.cls === 'hl-band') return;
        var d = Math.abs(other.origTop - item.origTop);
        if (d < bestD) { bestD = d; best = other; }
      });
      if (best) item.el.style.top = best.el.style.top;
    });

    // Reposition publisher link near the last photo
    var pubLink = wrap.querySelector('.hl-pub-link');
    if (pubLink) {
      var lastPhoto = null;
      items.forEach(function (i) { if (i.cls === 'hl-photo') lastPhoto = i; });
      if (lastPhoto) {
        pubLink.style.top = (parseInt(lastPhoto.el.style.top) + lastPhoto.el.offsetHeight + 12) + 'px';
      }
    }

    // Set wrapper height definitively (not min-height — overflow:hidden clips beyond this)
    wrap.style.height = (y + 80) + 'px';
  }

  // Run after images are loaded so offsetHeight is accurate
  if (document.readyState === 'complete') {
    reflow();
  } else {
    window.addEventListener('load', reflow);
  }
})();
