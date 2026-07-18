/* ARUNA — Halaman Home (dashboard).
   Mode hibrida: mulai dengan simulasi lokal, lalu otomatis beralih ke
   data asli begitu telemetri Firebase RTDB tiba (via live.js yang
   menyebarkan event "aruna:telemetry"). */
(function () {
  "use strict";

  /* ================= Data dummy ================= */

  var state = {
    weightToday: 2.35,   // kg
    temp: 35.6,          // °C
    gasPpm: 452,         // ppm (MQ-4)
    level: 75,           // %
    fermentDay: 5,       // hari ke-n
    fermentTotal: 14,
    lastUpdate: Date.now(),
    yields: { biogas: 0.42, pupuk: 1.8, kompos: 0.9 }
  };

  // Riwayat suhu 24 jam terakhir (per jam)
  var history = (function () {
    var out = [], now = new Date();
    for (var i = 23; i >= 0; i--) {
      var t = new Date(now.getTime() - i * 3600e3);
      var base = 34.5 + 1.6 * Math.sin((t.getHours() - 14) / 24 * 2 * Math.PI);
      out.push({ time: t, temp: +(base + (Math.random() - 0.5) * 0.9).toFixed(1) });
    }
    out[out.length - 1].temp = state.temp;
    return out;
  })();

  /* ================= Util DOM ================= */

  var $ = function (sel) { return document.querySelector(sel); };

  function fmtID(n, digits) {
    return n.toLocaleString("id-ID", { minimumFractionDigits: digits, maximumFractionDigits: digits });
  }

  function gasStatus(ppm) {
    if (ppm < 800)  return { label: "Normal",  cls: "chip--good" };
    if (ppm < 1500) return { label: "Waspada", cls: "chip--warn" };
    return { label: "Bahaya", cls: "chip--danger" };
  }

  /* ================= Animasi nilai (tween) ================= */

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function tween(from, to, dur, cb) {
    if (reduceMotion || dur <= 0 || from === to) { cb(to); return; }
    var t0 = performance.now();
    requestAnimationFrame(function step(t) {
      var p = Math.min(1, (t - t0) / dur);
      p = 1 - Math.pow(1 - p, 3); // ease-out kubik
      cb(from + (to - from) * p);
      if (p < 1) requestAnimationFrame(step);
    });
  }

  // Nilai yang sedang tampil di layar (sumber animasi count-up)
  var shown = { weight: 0, temp: 0, gas: 0, level: 0 };

  function updateNumbers(dur) {
    tween(shown.weight, state.weightToday, dur, function (v) {
      shown.weight = v;
      $("#statWeight").firstChild.nodeValue = fmtID(v, 2);
    });
    tween(shown.temp, state.temp, dur, function (v) {
      shown.temp = v;
      $("#statTemp").firstChild.nodeValue = fmtID(v, 1);
    });
    tween(shown.gas, state.gasPpm, dur, function (v) {
      shown.gas = v;
      $("#statGasPpm").textContent = fmtID(Math.round(v), 0) + " ppm";
    });
    tween(shown.level, state.level, dur, function (v) {
      shown.level = v;
      $("#ringLabel").textContent = Math.round(v) + "%";
    });
  }

  /* ================= Render angka ================= */

  function renderStats() {
    var g = gasStatus(state.gasPpm);
    var chip = $("#statGasChip");
    chip.className = "chip " + g.cls;
    chip.querySelector("b").textContent = g.label;

    // Cincin level (bar-nya dianimasikan transisi CSS)
    var C = 2 * Math.PI * 30; // r=30
    $("#ringBar").style.strokeDashoffset = String(C * (1 - state.level / 100));

    // Suhu di luar rentang operasional?
    var note = $("#tempNote");
    if (state.temp >= 30 && state.temp <= 40) {
      note.textContent = "Rentang optimal (30–40 °C)";
      note.style.color = "";
    } else {
      note.textContent = "Di luar rentang 30–40 °C!";
      note.style.color = "var(--critical)";
    }

    // Fase fermentasi
    var pct = Math.min(100, state.fermentDay / state.fermentTotal * 100);
    $("#phaseFill").style.width = pct + "%";
    $("#phaseDay").textContent = "Hari ke-" + state.fermentDay;
  }

  // Hasil produksi: menghitung naik saat halaman dibuka
  function renderYields(dur) {
    tween(0, state.yields.biogas, dur, function (v) { $("#yieldBiogas").textContent = fmtID(v, 2) + " m³"; });
    tween(0, state.yields.pupuk,  dur, function (v) { $("#yieldPupuk").textContent  = fmtID(v, 1) + " L"; });
    tween(0, state.yields.kompos, dur, function (v) { $("#yieldKompos").textContent = fmtID(v, 1) + " kg"; });
  }

  function renderClock() {
    var s = Math.max(0, Math.round((Date.now() - state.lastUpdate) / 1000));
    $("#lastUpdate").textContent = "Diperbarui " + (s < 3 ? "baru saja" : s + " dtk lalu");
  }

  /* ================= Grafik suhu (canvas) ================= */

  var canvas = $("#tempChart");
  var tip = $("#chartTip");
  var ctx = canvas.getContext("2d");
  var plot = { l: 34, r: 10, t: 12, b: 24 }; // padding plot
  var hoverIdx = -1;
  var introP = reduceMotion ? 1 : 0; // progres animasi "grafik menggambar diri"

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function chartGeom() {
    var rect = canvas.getBoundingClientRect();
    return { w: rect.width, h: rect.height };
  }

  function yRange() {
    var min = Infinity, max = -Infinity;
    history.forEach(function (d) { min = Math.min(min, d.temp); max = Math.max(max, d.temp); });
    min = Math.floor(Math.min(min, 30) - 1);
    max = Math.ceil(Math.max(max, 40) + 1);
    return { min: min, max: max };
  }

  function drawChart() {
    var g = chartGeom();
    var dpr = window.devicePixelRatio || 1;
    canvas.width = g.w * dpr;
    canvas.height = g.h * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, g.w, g.h);

    var r = yRange();
    var iw = g.w - plot.l - plot.r, ih = g.h - plot.t - plot.b;
    var x = function (i) { return plot.l + i / (history.length - 1) * iw; };
    var y = function (v) { return plot.t + (1 - (v - r.min) / (r.max - r.min)) * ih; };

    var ink3 = cssVar("--ink-3"), grid = cssVar("--grid"), axis = cssVar("--axis");
    var line = cssVar("--chart-line"), band = cssVar("--accent-soft");
    var surface = cssVar("--card-solid");

    // Pita rentang operasional 30–40 °C
    ctx.fillStyle = band;
    ctx.fillRect(plot.l, y(40), iw, y(30) - y(40));

    // Grid horizontal + label sumbu Y
    ctx.strokeStyle = grid;
    ctx.lineWidth = 1;
    ctx.fillStyle = ink3;
    ctx.font = "10px system-ui, sans-serif";
    ctx.textAlign = "right";
    ctx.textBaseline = "middle";
    var step = Math.ceil((r.max - r.min) / 4);
    for (var v = r.min; v <= r.max; v += step) {
      var yy = y(v);
      ctx.beginPath(); ctx.moveTo(plot.l, yy); ctx.lineTo(g.w - plot.r, yy); ctx.stroke();
      ctx.fillText(String(v), plot.l - 6, yy);
    }

    // Garis dasar
    ctx.strokeStyle = axis;
    ctx.beginPath(); ctx.moveTo(plot.l, plot.t + ih); ctx.lineTo(g.w - plot.r, plot.t + ih); ctx.stroke();

    // Label jam tiap 6 titik
    ctx.textAlign = "center"; ctx.textBaseline = "top";
    for (var i = 0; i < history.length; i += 6) {
      var hh = String(history[i].time.getHours()).padStart(2, "0") + ":00";
      ctx.fillText(hh, x(i), plot.t + ih + 6);
    }

    // Garis seri (2px) — saat intro, garis "menggambar diri" dari kiri
    ctx.save();
    if (introP < 1) {
      ctx.beginPath();
      ctx.rect(0, 0, plot.l + iw * introP, g.h);
      ctx.clip();
    }
    ctx.strokeStyle = line;
    ctx.lineWidth = 2;
    ctx.lineJoin = "round";
    ctx.beginPath();
    history.forEach(function (d, i) {
      i === 0 ? ctx.moveTo(x(i), y(d.temp)) : ctx.lineTo(x(i), y(d.temp));
    });
    ctx.stroke();
    ctx.restore();

    // Hover: crosshair + penanda titik (ring 2px warna permukaan)
    if (hoverIdx >= 0) {
      var hx = x(hoverIdx), hy = y(history[hoverIdx].temp);
      ctx.strokeStyle = axis;
      ctx.setLineDash([3, 3]);
      ctx.beginPath(); ctx.moveTo(hx, plot.t); ctx.lineTo(hx, plot.t + ih); ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = line;
      ctx.beginPath(); ctx.arc(hx, hy, 5, 0, 2 * Math.PI); ctx.fill();
      ctx.strokeStyle = surface;
      ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(hx, hy, 5, 0, 2 * Math.PI); ctx.stroke();
    }
  }

  function moveTip(clientX, clientY) {
    var rect = canvas.getBoundingClientRect();
    var g = chartGeom();
    var iw = g.w - plot.l - plot.r;
    var rel = (clientX - rect.left - plot.l) / iw;
    var idx = Math.round(rel * (history.length - 1));
    idx = Math.max(0, Math.min(history.length - 1, idx));
    if (idx !== hoverIdx) { hoverIdx = idx; drawChart(); }

    var d = history[idx];
    var r = yRange();
    var xPix = plot.l + idx / (history.length - 1) * iw;
    var yPix = plot.t + (1 - (d.temp - r.min) / (r.max - r.min)) * (g.h - plot.t - plot.b);
    tip.innerHTML = '<span class="t-val">' + fmtID(d.temp, 1) + " °C</span><br>" +
      String(d.time.getHours()).padStart(2, "0") + ":00";
    tip.style.left = xPix + "px";
    tip.style.top = Math.max(0, yPix - 54) + "px";
    tip.classList.add("show");
  }

  function hideTip() {
    tip.classList.remove("show");
    if (hoverIdx !== -1) { hoverIdx = -1; drawChart(); }
  }

  canvas.addEventListener("pointermove", function (e) { moveTip(e.clientX, e.clientY); });
  canvas.addEventListener("pointerdown", function (e) { moveTip(e.clientX, e.clientY); });
  canvas.addEventListener("pointerleave", hideTip);

  if ("ResizeObserver" in window) {
    new ResizeObserver(function () { drawChart(); }).observe(canvas.parentElement);
  } else {
    window.addEventListener("resize", drawChart);
  }
  document.addEventListener("aruna:themechange", drawChart);

  /* ================= Telemetri asli dari Firebase RTDB ================= */

  var liveMode = false; // begitu data RTDB tiba, simulasi berhenti

  document.addEventListener("aruna:telemetry", function (e) {
    var t = e.detail;
    liveMode = true;
    if (typeof t.temp === "number") state.temp = t.temp;
    if (typeof t.weightToday === "number") state.weightToday = t.weightToday;
    if (typeof t.gasPpm === "number") state.gasPpm = t.gasPpm;
    if (typeof t.level === "number") state.level = t.level;
    state.lastUpdate = typeof t.updatedAt === "number" ? t.updatedAt : Date.now();
    history[history.length - 1].temp = state.temp;
    renderStats();
    updateNumbers(700);
    renderClock();
    if (hoverIdx === -1) drawChart();
  });

  document.addEventListener("aruna:devstate", function (e) {
    if (typeof e.detail.fermentDay === "number") {
      state.fermentDay = e.detail.fermentDay;
      renderStats();
    }
  });

  /* ================= Simulasi data (fallback tanpa perangkat) ================= */

  setInterval(function () {
    if (liveMode) return; // data asli sudah mengalir
    state.temp = +(Math.min(39.5, Math.max(31, state.temp + (Math.random() - 0.5) * 0.4))).toFixed(1);
    state.gasPpm = Math.round(Math.min(900, Math.max(300, state.gasPpm + (Math.random() - 0.5) * 40)));
    if (Math.random() < 0.25) state.weightToday = +(state.weightToday + Math.random() * 0.05).toFixed(2);
    state.level = Math.min(100, state.level + (Math.random() < 0.2 ? 0.5 : 0));
    state.lastUpdate = Date.now();
    history[history.length - 1].temp = state.temp;
    renderStats();
    updateNumbers(700);
    if (hoverIdx === -1) drawChart();
  }, 4000);

  setInterval(renderClock, 1000);

  /* ================= Sapaan & tanggal ================= */

  var userName = "Sobat ARUNA";
  function renderGreet() {
    var h = new Date().getHours();
    var greet = h < 11 ? "Selamat pagi" : h < 15 ? "Selamat siang" : h < 18 ? "Selamat sore" : "Selamat malam";
    $("#greeting").textContent = greet + ", " + userName + "! 👋";
  }
  document.addEventListener("aruna:user", function (e) {
    userName = e.detail.nama || userName;
    renderGreet();
  });
  renderGreet();
  $("#today").textContent = new Date().toLocaleDateString("id-ID", {
    weekday: "long", day: "numeric", month: "long", year: "numeric"
  });

  /* ================= Init ================= */
  renderStats();
  renderClock();
  updateNumbers(1100);   // angka menghitung naik saat halaman dibuka
  renderYields(1100);
  drawChart();
  tween(0, 1, 950, function (p) { introP = p; drawChart(); });
})();
