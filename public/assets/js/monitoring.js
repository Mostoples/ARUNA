/* ARUNA — Monitoring detail. Data DUMMY tersimulasi; nanti diganti
   listener Firebase RTDB devices/{id}/history saat tahap integrasi. */
(function () {
  "use strict";

  var $ = function (s) { return document.querySelector(s); };
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function fmtID(n, d) {
    return n.toLocaleString("id-ID", { minimumFractionDigits: d, maximumFractionDigits: d });
  }
  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  /* ================= Pembangkit data dummy ================= */

  var range = "24h"; // "24h" | "7d"

  function genSeries(base, amp, noise, clampLo, clampHi) {
    var n = range === "24h" ? 24 : 28;              // 7d = titik per 6 jam
    var stepMs = range === "24h" ? 3600e3 : 6 * 3600e3;
    var out = [], now = Date.now();
    for (var i = n - 1; i >= 0; i--) {
      var t = new Date(now - i * stepMs);
      var v = base + amp * Math.sin((t.getHours() - 14) / 24 * 2 * Math.PI) + (Math.random() - 0.5) * noise;
      v = Math.min(clampHi, Math.max(clampLo, v));
      out.push({ t: t, v: v });
    }
    return out;
  }

  function labelTime(t) {
    if (range === "24h") return String(t.getHours()).padStart(2, "0") + ":00";
    return t.toLocaleDateString("id-ID", { weekday: "short" }) + " " + String(t.getHours()).padStart(2, "0") + ":00";
  }

  /* ================= Grafik garis generik ================= */

  function lineChart(cfg) {
    var canvas = $(cfg.canvas), tip = $(cfg.tip);
    var ctx = canvas.getContext("2d");
    var plot = { l: 38, r: 10, t: 12, b: 22 };
    var hover = -1, intro = reduceMotion ? 1 : 0;
    var data = [];

    function yRange() {
      var lo = Infinity, hi = -Infinity;
      data.forEach(function (d) { lo = Math.min(lo, d.v); hi = Math.max(hi, d.v); });
      if (cfg.band) { lo = Math.min(lo, cfg.band[0]); hi = Math.max(hi, cfg.band[1]); }
      if (cfg.ref) hi = Math.max(hi, cfg.ref);
      var pad = (hi - lo) * 0.12 || 1;
      return { lo: Math.floor(lo - pad), hi: Math.ceil(hi + pad) };
    }

    function draw() {
      var rect = canvas.getBoundingClientRect();
      var w = rect.width, h = rect.height;
      var dpr = window.devicePixelRatio || 1;
      canvas.width = w * dpr; canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);
      if (!data.length) return;

      var r = yRange();
      var iw = w - plot.l - plot.r, ih = h - plot.t - plot.b;
      var x = function (i) { return plot.l + i / (data.length - 1) * iw; };
      var y = function (v) { return plot.t + (1 - (v - r.lo) / (r.hi - r.lo)) * ih; };

      var ink3 = cssVar("--ink-3"), grid = cssVar("--grid"), axis = cssVar("--axis");
      var line = cssVar("--chart-line"), surface = cssVar("--card-solid");

      if (cfg.band) {
        ctx.fillStyle = cssVar("--accent-soft");
        ctx.fillRect(plot.l, y(cfg.band[1]), iw, y(cfg.band[0]) - y(cfg.band[1]));
      }

      ctx.strokeStyle = grid; ctx.lineWidth = 1;
      ctx.fillStyle = ink3; ctx.font = "10px system-ui, sans-serif";
      ctx.textAlign = "right"; ctx.textBaseline = "middle";
      var step = Math.max(1, Math.ceil((r.hi - r.lo) / 4));
      for (var v = r.lo; v <= r.hi; v += step) {
        var yy = y(v);
        ctx.beginPath(); ctx.moveTo(plot.l, yy); ctx.lineTo(w - plot.r, yy); ctx.stroke();
        ctx.fillText(String(v), plot.l - 6, yy);
      }

      if (cfg.ref) { // garis ambang (putus-putus, warna waspada)
        ctx.strokeStyle = cssVar("--warning");
        ctx.setLineDash([5, 4]);
        ctx.beginPath(); ctx.moveTo(plot.l, y(cfg.ref)); ctx.lineTo(w - plot.r, y(cfg.ref)); ctx.stroke();
        ctx.setLineDash([]);
      }

      ctx.strokeStyle = axis;
      ctx.beginPath(); ctx.moveTo(plot.l, plot.t + ih); ctx.lineTo(w - plot.r, plot.t + ih); ctx.stroke();

      ctx.textAlign = "center"; ctx.textBaseline = "top"; ctx.fillStyle = ink3;
      var lblStep = Math.ceil(data.length / 4);
      for (var i = 0; i < data.length; i += lblStep) {
        ctx.fillText(labelTime(data[i].t), x(i), plot.t + ih + 5);
      }

      ctx.save();
      if (intro < 1) { ctx.beginPath(); ctx.rect(0, 0, plot.l + iw * intro, h); ctx.clip(); }
      ctx.strokeStyle = line; ctx.lineWidth = 2; ctx.lineJoin = "round";
      ctx.beginPath();
      data.forEach(function (d, i) { i === 0 ? ctx.moveTo(x(i), y(d.v)) : ctx.lineTo(x(i), y(d.v)); });
      ctx.stroke();
      ctx.restore();

      if (hover >= 0) {
        var hx = x(hover), hy = y(data[hover].v);
        ctx.strokeStyle = axis; ctx.setLineDash([3, 3]);
        ctx.beginPath(); ctx.moveTo(hx, plot.t); ctx.lineTo(hx, plot.t + ih); ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = line;
        ctx.beginPath(); ctx.arc(hx, hy, 5, 0, 2 * Math.PI); ctx.fill();
        ctx.strokeStyle = surface; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(hx, hy, 5, 0, 2 * Math.PI); ctx.stroke();
      }
    }

    function onMove(e) {
      var rect = canvas.getBoundingClientRect();
      var iw = rect.width - plot.l - plot.r;
      var idx = Math.round((e.clientX - rect.left - plot.l) / iw * (data.length - 1));
      idx = Math.max(0, Math.min(data.length - 1, idx));
      if (idx !== hover) { hover = idx; draw(); }
      var d = data[idx];
      var r = yRange();
      var xPix = plot.l + idx / (data.length - 1) * iw;
      var yPix = plot.t + (1 - (d.v - r.lo) / (r.hi - r.lo)) * (rect.height - plot.t - plot.b);
      tip.innerHTML = '<span class="t-val">' + fmtID(d.v, cfg.digits) + " " + cfg.unit + "</span><br>" + labelTime(d.t);
      tip.style.left = xPix + "px";
      tip.style.top = Math.max(0, yPix - 52) + "px";
      tip.classList.add("show");
    }
    function onLeave() {
      tip.classList.remove("show");
      if (hover !== -1) { hover = -1; draw(); }
    }
    canvas.addEventListener("pointermove", onMove);
    canvas.addEventListener("pointerdown", onMove);
    canvas.addEventListener("pointerleave", onLeave);

    if ("ResizeObserver" in window) new ResizeObserver(draw).observe(canvas.parentElement);

    return {
      setData: function (d) {
        data = d; hover = -1;
        if (!reduceMotion) {
          intro = 0;
          var t0 = performance.now();
          requestAnimationFrame(function step(t) {
            intro = Math.min(1, (t - t0) / 850);
            intro = 1 - Math.pow(1 - intro, 3);
            draw();
            if (intro < 1) requestAnimationFrame(step);
          });
        } else draw();
      },
      draw: draw
    };
  }

  /* ================= Grafik batang (berat 7 hari) ================= */

  function barChart(cfg) {
    var canvas = $(cfg.canvas), tip = $(cfg.tip);
    var ctx = canvas.getContext("2d");
    var plot = { l: 34, r: 10, t: 12, b: 22 };
    var hover = -1, intro = reduceMotion ? 1 : 0;
    var data = cfg.data;

    function geom() {
      var rect = canvas.getBoundingClientRect();
      var iw = rect.width - plot.l - plot.r, ih = rect.height - plot.t - plot.b;
      var hi = Math.ceil(Math.max.apply(null, data.map(function (d) { return d.v; })) + 1);
      var bw = Math.min(46, iw / data.length * 0.55);
      return { rect: rect, iw: iw, ih: ih, hi: hi, bw: bw };
    }

    function draw() {
      var g = geom();
      var dpr = window.devicePixelRatio || 1;
      canvas.width = g.rect.width * dpr; canvas.height = g.rect.height * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, g.rect.width, g.rect.height);

      var ink3 = cssVar("--ink-3"), grid = cssVar("--grid"), axis = cssVar("--axis");
      var barCol = cssVar("--chart-line");

      ctx.strokeStyle = grid; ctx.lineWidth = 1;
      ctx.fillStyle = ink3; ctx.font = "10px system-ui, sans-serif";
      ctx.textAlign = "right"; ctx.textBaseline = "middle";
      for (var v = 0; v <= g.hi; v++) {
        var yy = plot.t + (1 - v / g.hi) * g.ih;
        ctx.beginPath(); ctx.moveTo(plot.l, yy); ctx.lineTo(g.rect.width - plot.r, yy); ctx.stroke();
        ctx.fillText(String(v), plot.l - 6, yy);
      }
      ctx.strokeStyle = axis;
      ctx.beginPath(); ctx.moveTo(plot.l, plot.t + g.ih); ctx.lineTo(g.rect.width - plot.r, plot.t + g.ih); ctx.stroke();

      ctx.textAlign = "center"; ctx.textBaseline = "top";
      data.forEach(function (d, i) {
        var cx = plot.l + (i + 0.5) / data.length * g.iw;
        ctx.fillStyle = ink3;
        ctx.fillText(d.label, cx, plot.t + g.ih + 5);

        var bh = (d.v / g.hi) * g.ih * intro;
        var bx = cx - g.bw / 2, by = plot.t + g.ih - bh;
        ctx.fillStyle = barCol;
        ctx.globalAlpha = hover === -1 || hover === i ? 1 : 0.45;
        ctx.beginPath();
        // ujung data membulat 4px, pangkal menempel garis dasar
        if (ctx.roundRect) ctx.roundRect(bx, by, g.bw, bh, [4, 4, 0, 0]);
        else ctx.rect(bx, by, g.bw, bh);
        ctx.fill();
        ctx.globalAlpha = 1;
      });
    }

    function idxAt(e) {
      var rect = canvas.getBoundingClientRect();
      var iw = rect.width - plot.l - plot.r;
      var i = Math.floor((e.clientX - rect.left - plot.l) / iw * data.length);
      return Math.max(0, Math.min(data.length - 1, i));
    }
    canvas.addEventListener("pointermove", function (e) {
      var i = idxAt(e);
      if (i !== hover) { hover = i; draw(); }
      var g = geom();
      var cx = plot.l + (i + 0.5) / data.length * g.iw;
      var by = plot.t + (1 - data[i].v / g.hi) * g.ih;
      tip.innerHTML = '<span class="t-val">' + fmtID(data[i].v, 2) + " kg</span><br>" + data[i].full;
      tip.style.left = cx + "px";
      tip.style.top = Math.max(0, by - 52) + "px";
      tip.classList.add("show");
    });
    canvas.addEventListener("pointerleave", function () {
      tip.classList.remove("show");
      hover = -1; draw();
    });

    if ("ResizeObserver" in window) new ResizeObserver(draw).observe(canvas.parentElement);

    if (!reduceMotion) {
      var t0 = performance.now();
      requestAnimationFrame(function step(t) {
        intro = Math.min(1, (t - t0) / 800);
        intro = 1 - Math.pow(1 - intro, 3);
        draw();
        if (intro < 1) requestAnimationFrame(step);
      });
    } else draw();

    return { draw: draw };
  }

  /* ================= Inisialisasi ================= */

  var suhu  = lineChart({ canvas: "#chartSuhu",  tip: "#tipSuhu",  unit: "°C",  digits: 1, band: [30, 40] });
  var gas   = lineChart({ canvas: "#chartGas",   tip: "#tipGas",   unit: "ppm", digits: 0, ref: 800 });
  var level = lineChart({ canvas: "#chartLevel", tip: "#tipLevel", unit: "%",   digits: 0 });

  function loadRange() {
    suhu.setData(genSeries(34.5, 1.6, 0.9, 30.5, 39.5));
    gas.setData(genSeries(480, 130, 90, 300, 780));
    level.setData(genSeries(73, 2, 1.2, 68, 78));
    document.querySelectorAll("[data-range-label]").forEach(function (el) {
      el.textContent = range === "24h" ? "24 jam terakhir" : "7 hari terakhir";
    });
  }

  document.querySelectorAll("[data-range]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      range = btn.getAttribute("data-range");
      document.querySelectorAll("[data-range]").forEach(function (b) {
        b.classList.toggle("is-active", b === btn);
      });
      loadRange();
    });
  });

  // Berat per hari (7 hari)
  var hariIni = new Date();
  var beratData = [3.1, 4.2, 2.8, 3.6, 4.5, 2.9, 2.35].map(function (v, i) {
    var d = new Date(hariIni.getTime() - (6 - i) * 864e5);
    return {
      v: v,
      label: d.toLocaleDateString("id-ID", { weekday: "short" }),
      full: d.toLocaleDateString("id-ID", { weekday: "long", day: "numeric", month: "short" })
    };
  });
  var berat = barChart({ canvas: "#chartBerat", tip: "#tipBerat", data: beratData });

  // Tabel riwayat
  (function () {
    var body = $("#historyBody");
    var rows = "";
    for (var i = 0; i < 10; i++) {
      var t = new Date(Date.now() - i * 3600e3);
      var s = 34.5 + Math.sin((t.getHours() - 14) / 24 * 2 * Math.PI) * 1.6 + (Math.random() - 0.5) * 0.8;
      var g = Math.round(480 + Math.sin(t.getHours() / 24 * 2 * Math.PI) * 120 + (Math.random() - 0.5) * 80);
      var l = Math.round(75 - i * 0.2);
      var ok = g < 800 && s >= 30 && s <= 40;
      rows += "<tr><td>" +
        t.toLocaleDateString("id-ID", { day: "numeric", month: "short" }) + " " + labelTimeShort(t) +
        "</td><td>" + fmtID(s, 1) + "</td><td>" + fmtID(g, 0) + "</td><td>" + l + "</td><td>" +
        (ok ? '<span class="chip chip--good"><span class="dot"></span> Normal</span>'
            : '<span class="chip chip--warn"><span class="dot"></span> Waspada</span>') +
        "</td></tr>";
    }
    body.innerHTML = rows;
    function labelTimeShort(t) { return String(t.getHours()).padStart(2, "0") + ":00"; }
  })();

  // Jam "diperbarui x dtk lalu"
  var last = Date.now();
  setInterval(function () {
    var s = Math.round((Date.now() - last) / 1000);
    if (s > 30) { last = Date.now(); s = 0; }
    $("#lastUpdate").textContent = "Diperbarui " + (s < 3 ? "baru saja" : s + " dtk lalu");
  }, 1000);

  document.addEventListener("aruna:themechange", function () {
    suhu.draw(); gas.draw(); level.draw(); berat.draw();
  });

  loadRange();
})();
