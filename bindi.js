/* bindi.js — apply Figma-exact amber dot positions after font load.
   Offsets are from the heading element's top-left, taken directly from
   Figma "Home Page Re" (1505:386). Re-applied on every font-ready event
   so a late-loading Afacad never leaves CSS fallback values in place. */
(function () {
  var DOTS = [
    { sel: '.hero-headline',   left: -14, top: 3 },
    { sel: '.about-heading',   left:   3, top: 5 },
    { sel: '.stories-heading', left: -12, top: 0 },
  ];

  function apply() {
    DOTS.forEach(function (d) {
      var el = document.querySelector(d.sel);
      if (!el) return;
      el.style.setProperty('--bindi-top',  d.top  + 'px');
      el.style.setProperty('--bindi-left', d.left + 'px');
    });
  }

  document.fonts.ready.then(apply);
})();
