/* ARUNA — pengelola tema terang/gelap.
   Catatan: snippet inline di <head> sudah memasang data-theme lebih awal
   agar tidak terjadi kedipan tema (FOUC). File ini menangani toggle-nya. */
(function () {
  "use strict";

  var KEY = "aruna-theme";

  function current() {
    return document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
  }

  function apply(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    try { localStorage.setItem(KEY, theme); } catch (e) { /* privat mode */ }
    document.dispatchEvent(new CustomEvent("aruna:themechange", { detail: { theme: theme } }));
  }

  function init() {
    var btns = document.querySelectorAll("[data-theme-toggle]");
    btns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        apply(current() === "dark" ? "light" : "dark");
      });
    });

    // Ikuti perubahan preferensi sistem jika pengguna belum memilih manual
    var mq = window.matchMedia("(prefers-color-scheme: dark)");
    mq.addEventListener("change", function (e) {
      var saved = null;
      try { saved = localStorage.getItem(KEY); } catch (err) {}
      if (!saved) {
        document.documentElement.setAttribute("data-theme", e.matches ? "dark" : "light");
        document.dispatchEvent(new CustomEvent("aruna:themechange", { detail: { theme: e.matches ? "dark" : "light" } }));
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
