/* ARUNA — kerangka bersama semua halaman aplikasi.
   Menyuntikkan: latar (blob + gelembung), sprite ikon Lucide, sidebar
   (desktop), dermaga navigasi bawah (mobile), sheet "Lainnya", dan toast.
   Halaman menandai dirinya lewat <body data-page="...">. */
(function () {
  "use strict";

  var PAGE = document.body.getAttribute("data-page") || "";
  // Halaman publik: hanya dapat latar + sprite + toast, tanpa navigasi aplikasi
  var BARE = PAGE === "landing" || PAGE === "login";

  /* ---------- Sprite ikon (Lucide, inline — tanpa CDN runtime) ---------- */
  var SPRITE =
    '<svg width="0" height="0" style="position:absolute" aria-hidden="true">' +
    '<symbol id="i-leaf" viewBox="0 0 24 24"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z" /> <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" /></symbol>' +
    '<symbol id="i-home" viewBox="0 0 24 24"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8" /> <path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /></symbol>' +
    '<symbol id="i-monitor" viewBox="0 0 24 24"><path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2" /></symbol>' +
    '<symbol id="i-steps" viewBox="0 0 24 24"><path d="M11 5h10" /> <path d="M11 12h10" /> <path d="M11 19h10" /> <path d="M4 4h1v5" /> <path d="M4 9h2" /> <path d="M6.5 20H3.4c0-1 2.6-1.925 2.6-3.5a1.5 1.5 0 0 0-2.6-1.02" /></symbol>' +
    '<symbol id="i-book" viewBox="0 0 24 24"><path d="M12 7v14" /> <path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z" /></symbol>' +
    '<symbol id="i-bot" viewBox="0 0 24 24"><path d="M12 8V4H8" /> <rect width="16" height="12" x="4" y="8" rx="2" /> <path d="M2 14h2" /> <path d="M20 14h2" /> <path d="M15 13v2" /> <path d="M9 13v2" /></symbol>' +
    '<symbol id="i-flask" viewBox="0 0 24 24"><path d="M14 2v6a2 2 0 0 0 .245.96l5.51 10.08A2 2 0 0 1 18 22H6a2 2 0 0 1-1.755-2.96l5.51-10.08A2 2 0 0 0 10 8V2" /> <path d="M6.453 15h11.094" /> <path d="M8.5 2h7" /></symbol>' +
    '<symbol id="i-cpu" viewBox="0 0 24 24"><path d="M12 20v2" /> <path d="M12 2v2" /> <path d="M17 20v2" /> <path d="M17 2v2" /> <path d="M2 12h2" /> <path d="M2 17h2" /> <path d="M2 7h2" /> <path d="M20 12h2" /> <path d="M20 17h2" /> <path d="M20 7h2" /> <path d="M7 20v2" /> <path d="M7 2v2" /> <rect x="4" y="4" width="16" height="16" rx="2" /> <rect x="8" y="8" width="8" height="8" rx="1" /></symbol>' +
    '<symbol id="i-user" viewBox="0 0 24 24"><circle cx="12" cy="8" r="5" /> <path d="M20 21a8 8 0 0 0-16 0" /></symbol>' +
    '<symbol id="i-bell" viewBox="0 0 24 24"><path d="M10.268 21a2 2 0 0 0 3.464 0" /> <path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326" /></symbol>' +
    '<symbol id="i-sun" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4" /> <path d="M12 2v2" /> <path d="M12 20v2" /> <path d="m4.93 4.93 1.41 1.41" /> <path d="m17.66 17.66 1.41 1.41" /> <path d="M2 12h2" /> <path d="M20 12h2" /> <path d="m6.34 17.66-1.41 1.41" /> <path d="m19.07 4.93-1.41 1.41" /></symbol>' +
    '<symbol id="i-moon" viewBox="0 0 24 24"><path d="M20.985 12.486a9 9 0 1 1-9.473-9.472c.405-.022.617.46.402.803a6 6 0 0 0 8.268 8.268c.344-.215.825-.004.803.401" /></symbol>' +
    '<symbol id="i-scale" viewBox="0 0 24 24"><circle cx="12" cy="5" r="3" /> <path d="M6.5 8a2 2 0 0 0-1.905 1.46L2.1 18.5A2 2 0 0 0 4 21h16a2 2 0 0 0 1.925-2.54L19.4 9.5A2 2 0 0 0 17.48 8Z" /></symbol>' +
    '<symbol id="i-thermo" viewBox="0 0 24 24"><path d="M14 4v10.54a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0Z" /></symbol>' +
    '<symbol id="i-wind" viewBox="0 0 24 24"><path d="M12.8 19.6A2 2 0 1 0 14 16H2" /> <path d="M17.5 8a2.5 2.5 0 1 1 2 4H2" /> <path d="M9.8 4.4A2 2 0 1 1 11 8H2" /></symbol>' +
    '<symbol id="i-gauge" viewBox="0 0 24 24"><path d="m12 14 4-4" /> <path d="M3.34 19a10 10 0 1 1 17.32 0" /></symbol>' +
    '<symbol id="i-flame" viewBox="0 0 24 24"><path d="M12 3q1 4 4 6.5t3 5.5a1 1 0 0 1-14 0 5 5 0 0 1 1-3 1 1 0 0 0 5 0c0-2-1.5-3-1.5-5q0-2 2.5-4" /></symbol>' +
    '<symbol id="i-drop" viewBox="0 0 24 24"><path d="M7 16.3c2.2 0 4-1.83 4-4.05 0-1.16-.57-2.26-1.71-3.19S7.29 6.75 7 5.3c-.29 1.45-1.14 2.84-2.29 3.76S3 11.1 3 12.25c0 2.22 1.8 4.05 4 4.05z" /> <path d="M12.56 6.6A10.97 10.97 0 0 0 14 3.02c.5 2.5 2 4.9 4 6.5s3 3.5 3 5.5a6.98 6.98 0 0 1-11.91 4.97" /></symbol>' +
    '<symbol id="i-wifi" viewBox="0 0 24 24"><path d="M12 20h.01" /> <path d="M2 8.82a15 15 0 0 1 20 0" /> <path d="M5 12.859a10 10 0 0 1 14 0" /> <path d="M8.5 16.429a5 5 0 0 1 7 0" /></symbol>' +
    '<symbol id="i-bt" viewBox="0 0 24 24"><path d="m7 7 10 10-5 5V2l5 5L7 17" /></symbol>' +
    '<symbol id="i-more" viewBox="0 0 24 24"><rect width="7" height="7" x="3" y="3" rx="1" /> <rect width="7" height="7" x="14" y="3" rx="1" /> <rect width="7" height="7" x="14" y="14" rx="1" /> <rect width="7" height="7" x="3" y="14" rx="1" /></symbol>' +
    '<symbol id="i-logout" viewBox="0 0 24 24"><path d="m16 17 5-5-5-5" /> <path d="M21 12H9" /> <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /></symbol>' +
    '<symbol id="i-spark" viewBox="0 0 24 24"><path d="M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z" /> <path d="M20 2v4" /> <path d="M22 4h-4" /> <circle cx="4" cy="20" r="2" /></symbol>' +
    '<symbol id="i-lock" viewBox="0 0 24 24"><rect width="18" height="11" x="3" y="11" rx="2" ry="2" /> <path d="M7 11V7a5 5 0 0 1 10 0v4" /></symbol>' +
    "</svg>";

  /* ---------- Struktur navigasi ---------- */
  var NAV = [
    { id: "home",         href: "home.html",         icon: "i-home",    label: "Beranda" },
    { id: "monitoring",   href: "monitoring.html",   icon: "i-monitor", label: "Monitoring" },
    { id: "langkah",      href: "langkah.html",      icon: "i-steps",   label: "Langkah Sistem" },
    { id: "ensiklopedia", href: "ensiklopedia.html", icon: "i-book",    label: "Ensiklopedia" },
    { id: "ai",           href: "ai-edukator.html",  icon: "i-bot",     label: "AI Edukator" },
    { id: "penelitian",   href: "penelitian.html",   icon: "i-flask",   label: "Penelitian" }
  ];

  function icon(id, cls) {
    return '<svg class="' + (cls || "ic") + '"><use href="#' + id + '"/></svg>';
  }

  function navItem(item) {
    var active = item.id === PAGE;
    return '<a class="nav-item' + (active ? " is-active" : "") + '" href="' + item.href + '"' +
      (active ? ' aria-current="page"' : "") + ">" + icon(item.icon) + " " + item.label + "</a>";
  }

  var sidebar =
    '<aside class="sidebar glass" aria-label="Navigasi utama">' +
    '<div class="brand">' +
    '<span class="brand-logo">' + icon("i-leaf") + "</span>" +
    '<div><div class="brand-name">ARUNA</div><div class="brand-sub">Smart Biodigester MBG</div></div>' +
    "</div>" +
    NAV.map(navItem).join("") +
    '<div class="nav-sep"></div>' +
    navItem({ id: "perangkat", href: "perangkat.html", icon: "i-cpu", label: "Perangkat" }) +
    '<div class="nav-grow"></div><div class="nav-sep"></div>' +
    navItem({ id: "profil", href: "profil.html", icon: "i-user", label: "Profil" }) +
    '<a class="nav-item" href="index.html" data-logout>' + icon("i-logout") + " Keluar</a>" +
    "</aside>";

  function tab(id, href, ic, label) {
    var active = id === PAGE;
    return '<a class="tab-item' + (active ? " is-active" : "") + '" href="' + href + '"' +
      (active ? ' aria-current="page"' : "") + ">" + icon(ic) + " " + label + "</a>";
  }

  var bottombar =
    '<nav class="bottombar glass" aria-label="Navigasi bawah">' +
    tab("home", "home.html", "i-home", "Beranda") +
    tab("monitoring", "monitoring.html", "i-monitor", "Monitoring") +
    '<a class="tab-item tab-item--fab' + (PAGE === "ai" ? " is-active" : "") + '" href="ai-edukator.html" aria-label="AI Edukator">' +
    '<span class="tab-fab">' + icon("i-bot") + "</span> AI</a>" +
    tab("ensiklopedia", "ensiklopedia.html", "i-book", "Materi") +
    '<button class="tab-item tab-item--btn" type="button" data-sheet-open>' + icon("i-more") + " Lainnya</button>" +
    "</nav>";

  var sheet =
    '<div class="sheet-backdrop" data-sheet-close hidden></div>' +
    '<div class="sheet glass" role="dialog" aria-label="Menu lainnya" hidden>' +
    '<div class="sheet-grip"></div>' +
    '<a class="sheet-item" href="langkah.html"><span class="coin">' + icon("i-steps") + "</span> Langkah Sistem</a>" +
    '<a class="sheet-item" href="penelitian.html"><span class="coin">' + icon("i-flask") + "</span> Penelitian</a>" +
    '<a class="sheet-item" href="perangkat.html"><span class="coin">' + icon("i-cpu") + "</span> Perangkat</a>" +
    '<a class="sheet-item" href="profil.html"><span class="coin">' + icon("i-user") + "</span> Profil</a>" +
    '<a class="sheet-item" href="index.html" data-logout><span class="coin">' + icon("i-logout") + "</span> Keluar</a>" +
    "</div>";

  var bg =
    '<div class="bg-blobs" aria-hidden="true"><span class="blob"></span>' +
    '<div class="bg-bubbles"><span></span><span></span><span></span><span></span>' +
    "<span></span><span></span><span></span><span></span></div></div>";

  /* ---------- Suntik ke dokumen ---------- */
  var frag = document.createElement("div");
  frag.innerHTML = SPRITE + bg;
  while (frag.firstChild) document.body.insertBefore(frag.firstChild, document.body.firstChild);

  var app = document.querySelector(".app") || document.body;
  var shell = document.createElement("div");
  shell.innerHTML = (BARE ? "" : sidebar + bottombar + sheet) +
    '<div class="toast glass" id="toast" role="status"></div>';
  while (shell.firstChild) app.appendChild(shell.firstChild);

  /* ---------- Toast global ---------- */
  var toastTimer;
  window.arunaToast = function (msg) {
    var el = document.getElementById("toast");
    el.textContent = msg;
    el.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.classList.remove("show"); }, 2400);
  };
  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-toast]");
    if (t) { e.preventDefault(); window.arunaToast(t.getAttribute("data-toast")); }
  });

  /* ---------- Sheet "Lainnya" ---------- */
  var sheetEl = document.querySelector(".sheet");
  var backdrop = document.querySelector(".sheet-backdrop");
  if (!sheetEl) return; // halaman publik: selesai di sini
  function openSheet() {
    sheetEl.hidden = false; backdrop.hidden = false;
    requestAnimationFrame(function () { sheetEl.classList.add("open"); backdrop.classList.add("open"); });
  }
  function closeSheet() {
    sheetEl.classList.remove("open"); backdrop.classList.remove("open");
    setTimeout(function () { sheetEl.hidden = true; backdrop.hidden = true; }, 280);
  }
  document.addEventListener("click", function (e) {
    if (e.target.closest("[data-sheet-open]")) openSheet();
    if (e.target.closest("[data-sheet-close]")) closeSheet();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !sheetEl.hidden) closeSheet();
  });

  /* ---------- Entrance berjenjang untuk konten halaman ---------- */
  if (PAGE !== "home" && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var kids = document.querySelectorAll(".app-content > *");
    kids.forEach(function (el, i) {
      el.classList.add("anim-in");
      el.style.animationDelay = (i * 70) + "ms";
    });
  }
})();
