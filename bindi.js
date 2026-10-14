/* bindi.js — amber dot positions after font load.
   Hero + Stories: Figma-exact hardcoded offsets (large dots, browser diffs negligible).
   About: Range-measured — centers the 10px dot on the first character's ink bounds,
   so it tracks the "I" correctly in Firefox, Safari and Chrome. */
(function () {

  /* Large dots: fixed Figma offsets from heading element top-left. */
  var FIXED = [
    { sel: '.hero-headline',   left: -14, top: 3 },
    { sel: '.stories-heading', left: -12, top: 0 },
  ];

  /* Find the first text node inside an element. */
  function firstTextNode(el) {
    var walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null, false);
    return walker.nextNode();
  }

  function apply() {
    /* Fixed offsets for hero and stories. */
    FIXED.forEach(function (d) {
      var el = document.querySelector(d.sel);
      if (!el) return;
      el.style.setProperty('--bindi-left', d.left + 'px');
      el.style.setProperty('--bindi-top',  d.top  + 'px');
    });

    /* Range-measured for about: center the 10px dot on the "I" glyph. */
    var about = document.querySelector('.about-heading');
    if (about) {
      var tn = firstTextNode(about);
      if (tn) {
        var range = document.createRange();
        range.setStart(tn, 0);
        range.setEnd(tn, 1);
        var charRect = range.getBoundingClientRect();
        var elRect   = about.getBoundingClientRect();
        /* Center of glyph relative to heading element. */
        var cx = charRect.left + charRect.width  / 2 - elRect.left;
        var cy = charRect.top  + charRect.height / 2 - elRect.top;
        /* Bindi is 10×10 — place its centre on the glyph centre. */
        about.style.setProperty('--bindi-left', (cx - 5) + 'px');
        about.style.setProperty('--bindi-top',  (cy - 5) + 'px');
      }
    }
  }

  document.fonts.ready.then(apply);
  /* Fallback: Firefox sometimes resolves fonts.ready before web fonts paint. */
  setTimeout(apply, 300);
})();
