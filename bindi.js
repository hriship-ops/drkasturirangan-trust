/* bindi.js — amber dot positions after font load.
   Hero + Stories: Figma-exact hardcoded offsets.
   About: horizontal position measured via Range so the 10px dot correctly
   tracks the "I" glyph across Chrome, Firefox and Safari (which all render
   Afacad with slightly different left-side bearings). */
(function () {

  function applyFixed(sel, left, top) {
    var el = document.querySelector(sel);
    if (!el) return;
    el.style.setProperty('--bindi-left', left + 'px');
    el.style.setProperty('--bindi-top',  top  + 'px');
  }

  function applyAbout() {
    var el = document.querySelector('.about-heading');
    if (!el) return;

    /* Find first text node (skip any element children). */
    var walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null, false);
    var tn = walker.nextNode();
    if (!tn) { applyFixed('.about-heading', 3, -8); return; }

    var range = document.createRange();
    range.setStart(tn, 0);
    range.setEnd(tn, 1);
    var charRect = range.getBoundingClientRect();
    var elRect   = el.getBoundingClientRect();

    /* Left edge of the "I" glyph relative to the heading element. */
    var glyphLeft = charRect.left - elRect.left;

    /* Figma: dot left edge = "I" left edge + 2px (dot sits just inside the
       "I" left edge, not centred on it, so the "I" appears in the dot's
       left portion). glyphLeft tracks per-browser font bearing differences. */
    var left = glyphLeft + 2;

    el.style.setProperty('--bindi-left', left + 'px');
    /* -8px gives a hair gap above the cap height. */
    el.style.setProperty('--bindi-top',  '-12px');
  }

  function apply() {
    applyFixed('.hero-headline',   -14, 3);
    applyFixed('.stories-heading', -12, 0);
    applyAbout();
  }

  document.fonts.ready.then(apply);
  /* Fallback: some browsers resolve fonts.ready before the web font paints. */
  setTimeout(apply, 300);
})();
