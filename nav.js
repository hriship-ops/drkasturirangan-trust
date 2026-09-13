// Mobile nav: sub-menu toggle for dropdowns
document.querySelectorAll('.nav-links > li > a').forEach(function(link) {
  link.addEventListener('click', function(e) {
    if (window.innerWidth > 620) return;
    var li = this.closest('li');
    if (!li.querySelector('.nav-dropdown')) return;
    e.preventDefault();
    var wasOpen = li.classList.contains('nav-sub-open');
    document.querySelectorAll('.nav-links > li').forEach(function(l) {
      l.classList.remove('nav-sub-open');
    });
    if (!wasOpen) li.classList.add('nav-sub-open');
  });
});
