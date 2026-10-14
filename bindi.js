/* bindi.js — anchor amber dots to the actual rendered first character.
   Uses Range.getBoundingClientRect() after fonts load so the position
   tracks the real cap-height instead of hardcoded guesses. */
(function () {
  // dotW: diameter of the dot (matches CSS width/height)
  // alignX:
  //   'left-of-char'   → bindi.left = charLeft + offsetX  (dot sits left of letter)
  //   'center-on-char' → bindi.center = charCenter + offsetX  (dot sits over letter)
  var DOTS = [
    { sel: '.hero-headline',   dotW: 32, alignX: 'left-of-char',   offsetX: -14 },
    { sel: '.about-heading',   dotW: 10, alignX: 'center-on-char', offsetX:   0 },
    { sel: '.stories-heading', dotW: 40, alignX: 'left-of-char',   offsetX: -14 },
  ];

  function firstCharRect(el) {
    for (var i = 0; i < el.childNodes.length; i++) {
      var n = el.childNodes[i];
      if (n.nodeType === 3 && n.textContent.trim()) {
        var r = document.createRange();
        r.setStart(n, 0);
        r.setEnd(n, 1);
        return r.getBoundingClientRect();
      }
    }
    return null;
  }

  function update() {
    DOTS.forEach(function (d) {
      var el = document.querySelector(d.sel);
      if (!el) return;
      var cr = firstCharRect(el);
      if (!cr) return;
      var er = el.getBoundingClientRect();

      var top      = cr.top  - er.top;
      var charLeft = cr.left - er.left;
      var left;

      if (d.alignX === 'center-on-char') {
        left = charLeft + cr.width / 2 - d.dotW / 2 + d.offsetX;
      } else {
        left = charLeft + d.offsetX;
      }

      el.style.setProperty('--bindi-top',  top  + 'px');
      el.style.setProperty('--bindi-left', left + 'px');
    });
  }

  document.fonts.ready.then(update);
  window.addEventListener('resize', update);
})();
