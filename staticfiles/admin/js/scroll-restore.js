// static/admin/js/sidebar-scroll-restore.js
(function () {
  var KEY = "jazzmin:sidebar:scrollY";

  function findSidebar() {
    // Jazzmin/AdminLTE bazen overlayScrollbars kullanır
    return document.querySelector(".main-sidebar .os-viewport") ||
           document.querySelector(".main-sidebar .sidebar") ||
           document.querySelector(".main-sidebar");
  }

  function save() {
    try {
      var el = findSidebar();
      if (!el) return;
      sessionStorage.setItem(KEY, String(el.scrollTop || 0));
    } catch (e) {}
  }

  function restore() {
    try {
      var el = findSidebar();
      if (!el) return false;
      var y = parseInt(sessionStorage.getItem(KEY) || "0", 10);
      if (y > 0) el.scrollTop = y;
      return true;
    } catch (e) { return false; }
  }

  // Yüklenince geri yükle (bazı temalarda DOM geç gelir; kısa retry yap)
  window.addEventListener("load", function () {
    var tries = 0;
    var iv = setInterval(function () {
      if (restore() || ++tries > 15) clearInterval(iv); // ~1.5s dene
    }, 100);
  });

  // Ayrılmadan önce kaydet
  window.addEventListener("beforeunload", save);

  // Sidebar içinde tıklanınca (navigasyon öncesi) konumu kaydet
  document.addEventListener("click", function (e) {
    if (e.target && e.target.closest(".main-sidebar")) save();
  }, true);

  // Kaydırdıkça ara ara kaydet (throttle)
  var lock = false;
  document.addEventListener("scroll", function () {
    var el = findSidebar();
    if (!el || !el.closest(".main-sidebar")) return;
    if (lock) return;
    lock = true;
    setTimeout(function(){ lock = false; save(); }, 200);
  }, true);
})();
