/* ARUNA app — SPA mobile (UI putih-modern).
   Auth: Firebase Auth (Google, email/sandi, tamu). Data: RTDB devices/{DEVICE_ID}/{telemetry,state,history}.
   Jika data alat belum tersedia, tampil nilai contoh berlabel "simulasi". */
import {
  auth, rtdb, db, googleProvider, signInWithPopup, signInAnonymously, signInWithEmailAndPassword,
  createUserWithEmailAndPassword, sendPasswordResetEmail, onAuthStateChanged, signOut,
  ref, onValue, doc, setDoc, getDoc, serverTimestamp,
} from "/assets/js/firebase-init.js";

const DEVICE_ID = "ARN-2201";
const CYCLE_DAYS = 34;            // HRT desain (lihat design/competition/sci_calc.py)
const MIN_PER_KG = 43 / 1.5;      // menit masak per kg sisa makanan (prediksi desain)
const $root = document.getElementById("root");
const $tabs = document.getElementById("tabs");
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const fmt = (v, d = 0) => (v == null || isNaN(v)) ? "—" : Number(v).toLocaleString("id-ID", { minimumFractionDigits: d, maximumFractionDigits: d });
const ic = (id) => `<svg class="i"><use href="#${id}"/></svg>`;

/* ------------------------------------------------------------------ state */
const SIM = { temp: 36.4, level: 62, ch4: 58, ph: 7.1, gasPpm: 420, weightToday: 1.9, online: true, day: 12 };
const S = { user: null, nama: "", data: { ...SIM }, live: false, devState: null, history: null, updatedAt: null, range: "24h" };

function toast(msg) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.classList.add("on");
  clearTimeout(t._h);
  t._h = setTimeout(() => t.classList.remove("on"), 2600);
}

function subscribe() {
  const base = "devices/" + DEVICE_ID;
  onValue(ref(rtdb, base + "/telemetry"), (snap) => {
    const t = snap.val();
    if (!t) return;
    S.data = S.live ? { ...S.data, ...t } : { ...t };   // data live menggantikan seluruh nilai simulasi
    S.live = true;
    S.updatedAt = t.updatedAt || Date.now();
    render(false);
  }, (e) => console.warn("telemetry:", e.message));
  onValue(ref(rtdb, base + "/state"), (snap) => { S.devState = snap.val(); render(false); }, (e) => console.warn("state:", e.message));
  onValue(ref(rtdb, base + "/history"), (snap) => { S.history = snap.val(); if (route() === "monitor") render(false); },
    (e) => console.warn("history:", e.message));
}

/* ------------------------------------------------------------------ helpers data */
const lastTs = () => Number(S.devState?.lastSeen || S.updatedAt || 0);
// online hanya jika alat melapor dalam 1 jam terakhir
const online = () => (S.live || S.devState) ? (S.devState?.online !== false && lastTs() > 0 && Date.now() - lastTs() < 3600e3) : true;
const PHASES = ["Penguraian", "Pengasaman", "Pembentukan gas", "Stabil"];
const phaseLabel = () => { const p = S.devState?.phase; if (p == null) return "Mencerna"; return typeof p === "number" ? (PHASES[p - 1] || "Fase " + p) : String(p); };
const dayInCycle = () => S.devState?.day ?? (S.live ? S.data.day ?? null : SIM.day);
const gasLabel = () => (S.data.ch4 != null && S.live ? "ch4" : S.live ? "ppm" : "ch4");
function ago(ts) {
  if (!ts) return "";
  const s = Math.max(0, (Date.now() - Number(ts)) / 1000);
  if (s < 60) return "baru saja";
  if (s < 3600) return Math.round(s / 60) + " mnt lalu";
  if (s < 86400) return Math.round(s / 3600) + " jam lalu";
  return Math.round(s / 86400) + " hari lalu";
}
function series(key, range) {
  // dari RTDB history/{yyyy-mm-dd}/{hh}: {temp, gasPpm, weight, level}
  if (S.history) {
    const days = Object.keys(S.history).sort();
    const pts = [];
    if (range === "24h") {
      const d = days[days.length - 1];
      Object.keys(S.history[d] || {}).sort().forEach((h) => { const v = S.history[d][h]?.[key]; if (v != null) pts.push([h, +v]); });
    } else {
      days.slice(-7).forEach((d) => {
        const vals = Object.values(S.history[d] || {}).map((o) => o?.[key]).filter((v) => v != null);
        if (vals.length) pts.push([d.slice(5), vals.reduce((a, b) => +a + +b, 0) / vals.length]);
      });
    }
    if (pts.length > 1) return { pts, sim: false };
  }
  // contoh berlabel simulasi
  const n = range === "24h" ? 24 : 7;
  const base = { temp: 35.8, level: 60, gasPpm: 400, weight: 1.6 }[key] ?? 1;
  const amp = { temp: 0.8, level: 4, gasPpm: 60, weight: 0.5 }[key] ?? 0.1;
  const pts = Array.from({ length: n }, (_, i) => [range === "24h" ? String(i).padStart(2, "0") : "H-" + (n - 1 - i),
    base + amp * Math.sin(i / 3) + amp * 0.3 * Math.cos(i * 1.7) + (key === "level" ? i * 0.2 : 0)]);
  return { pts, sim: true };
}
function lineChart(pts, { band, unit = "", digits = 1, color = "#158A52" } = {}) {
  const W = 330, H = 140, L = 30, T = 16, B = 118;
  const ys = pts.map((p) => p[1]);
  let lo = Math.min(...ys, band ? band[0] : Infinity), hi = Math.max(...ys, band ? band[1] : -Infinity);
  const pad = (hi - lo) * 0.15 || 1;
  lo -= pad; hi += pad;
  const X = (i) => L + (i / Math.max(1, pts.length - 1)) * (W - L - 10);
  const Y = (v) => B - ((v - lo) / (hi - lo)) * (B - T);
  const path = pts.map((p, i) => (i ? "L" : "M") + X(i).toFixed(1) + " " + Y(p[1]).toFixed(1)).join(" ");
  const last = pts[pts.length - 1];
  const step = Math.ceil(pts.length / 5);
  const ticks = pts.map((p, i) => (i % step === 0 || i === pts.length - 1) ? `<text x="${X(i)}" y="${H - 4}" text-anchor="middle">${esc(p[0])}</text>` : "").join("");
  const grid = [hi - pad, (hi + lo) / 2, lo + pad].map((v) => `<line x1="${L}" x2="${W}" y1="${Y(v)}" y2="${Y(v)}" stroke="#E4EBE7"/><text x="0" y="${Y(v) + 3}">${fmt(v, digits)}</text>`).join("");
  const bandEl = band ? `<rect x="${L}" y="${Y(band[1])}" width="${W - L}" height="${Y(band[0]) - Y(band[1])}" fill="#E6F4EC" opacity=".6"/>` : "";
  return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Grafik">${bandEl}${grid}
    <path d="${path} L${X(pts.length - 1)} ${B} L${L} ${B}Z" fill="${color}" opacity=".08"/>
    <path d="${path}" fill="none" stroke="${color}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>
    <circle cx="${X(pts.length - 1)}" cy="${Y(last[1])}" r="5" fill="#fff" stroke="${color}" stroke-width="3"/>${ticks}</svg>`;
}

/* ------------------------------------------------------------------ views */
const V = {};

V.login = () => `
<section class="login">
  <div class="brand"><span class="mark"></span>ARUNA</div>
  <div class="hero-m">
    <img src="img/mesin.png" alt="Mesin biodigester ARUNA">
    <div class="float" style="left:20px;top:120px"><span class="ico b sm">${ic("i-flame")}</span><div><b class="num">±43 mnt</b>gas masak / hari*</div></div>
    <div class="float" style="right:18px;top:210px;animation-delay:1.2s"><span class="ico g sm">${ic("i-drop")}</span><div><b>Pupuk cair</b>+ kompos</div></div>
  </div>
  <h1>Sisa makanan jadi <span>gas &amp; pupuk</span> untuk rumahmu</h1>
  <p style="margin:0 0 16px;color:var(--ink-2)">Pantau mesin ARUNA dari HP. Kami kabari saat pupuk siap atau laci kompos penuh.</p>
  <form id="fLogin" style="display:grid;gap:10px" novalidate>
    <div class="field"><label for="em">Email</label><input id="em" type="email" autocomplete="email" placeholder="nama@email.com" required></div>
    <div class="field"><label for="pw">Kata sandi</label><input id="pw" type="password" autocomplete="current-password" placeholder="minimal 6 karakter" required></div>
    <div class="field" id="nmWrap" hidden><label for="nm">Nama</label><input id="nm" autocomplete="name" placeholder="Nama panggilan"></div>
    <div class="err" id="err" role="alert"></div>
    <button class="btn pri" type="submit" id="bSubmit">Masuk ${ic("i-arrow")}</button>
    <button class="btn sec2" type="button" id="bGoogle"><span class="gmark"></span>Masuk dengan Google</button>
    <button class="btn sec2" type="button" id="bGuest">${ic("i-user")}Coba sebagai tamu</button>
  </form>
  <p style="text-align:center;font-size:14px;color:var(--ink-2);margin:14px 0 4px"><span id="swText">Belum punya akun?</span> <button class="link" id="bSwitch" type="button">Daftar</button> · <button class="link" id="bReset" type="button">Lupa sandi</button></p>
  <p class="note" style="text-align:center">*prediksi desain pada 1,5 kg sisa makanan/hari</p>
</section>`;

function statusChip() {
  if (!S.live) return `<span class="chip amber"><i></i>Simulasi</span>`;
  return online() ? `<span class="chip"><i></i>Online</span>` : `<span class="chip grey"><i></i>Offline</span>`;
}
function simBanner() {
  return S.live ? "" : `<div class="banner">${ic("i-bell")}Belum ada data dari alat. Angka di bawah adalah contoh (simulasi).</div>`;
}

V.home = () => {
  const d = S.data, day = dayInCycle();
  const cook = d.weightToday != null ? Math.round(d.weightToday * MIN_PER_KG) : null;
  const gas = gasLabel() === "ch4"
    ? `<div class="v num">${fmt(d.ch4)}<small>% CH₄</small></div><div class="bar"><i style="width:${Math.min(100, d.ch4 || 0)}%;background:var(--blue)"></i></div>`
    : `<div class="v num">${fmt(d.gasPpm)}<small>ppm</small></div><span class="lbl" style="font-weight:500">${esc(d.gasStatus || "sensor gas sekitar")}</span>`;
  const jam = new Date().getHours();
  const salam = jam < 11 ? "Selamat pagi," : jam < 15 ? "Selamat siang," : jam < 18 ? "Selamat sore," : "Selamat malam,";
  return `
<section class="view">
  <div class="hello">
    <img class="hello-3d" src="/assets/3d/flame-anim.webp" alt="">
    <div class="avatar">${esc((S.nama[0] || "A").toUpperCase())}</div>
    <div><small>${salam}</small><b>${esc(S.nama)}</b></div><span class="sp"></span>
    <a class="ibtn" href="#alat" aria-label="Alat & akun">${ic("i-bell")}</a>
  </div>
  ${simBanner()}
  <div class="card dev">
    <div class="pic"><img src="img/mesin.png" alt=""></div>
    <div class="info">
      <div>${statusChip()}<h4>ARUNA Dapur</h4><span class="id">${DEVICE_ID}${S.updatedAt ? " · " + ago(S.updatedAt) : ""}</span></div>
      <div class="prog">
        <div><span>${esc(phaseLabel())}</span><span>${day != null ? `<b>hari ${day}</b> dari ${CYCLE_DAYS}` : ""}</span></div>
        <div class="bar"><i style="width:${day != null ? Math.min(100, (day / CYCLE_DAYS) * 100) : 0}%"></i></div>
      </div>
    </div>
  </div>
  <div class="sec sec-k"><h3>Kondisi sekarang</h3><a href="#monitor">Detail</a></div>
  <div class="stats">
    <div class="card st"><div class="top"><span class="lbl">Suhu</span><img class="i3d" src="/assets/3d/therm.webp" alt="" style="width:34px;height:34px"></div>
      <div class="v num">${fmt(d.temp, 1)}<small>°C</small></div><span class="lbl" style="font-weight:500">ideal 30–38 °C</span></div>
    <div class="card st"><div class="top"><span class="lbl">Isi digester</span><img class="i3d" src="/assets/3d/bowl.webp" alt="" style="width:34px;height:34px"></div>
      <div class="v num">${fmt(d.level)}<small>%</small></div><div class="bar"><i style="width:${Math.min(100, d.level || 0)}%;background:var(--green-2)"></i></div></div>
    <div class="card st"><div class="top"><span class="lbl">Gas</span><img class="i3d" src="/assets/3d/ch4.webp" alt="" style="width:34px;height:34px"></div>${gas}</div>
    <div class="card st"><div class="top"><span class="lbl">Sampah hari ini</span><img class="i3d" src="/assets/3d/compost.webp" alt="" style="width:34px;height:34px"></div>
      <div class="v num">${fmt(d.weightToday, 1)}<small>kg</small></div><div class="bar"><i style="width:${Math.min(100, ((d.weightToday || 0) / 3) * 100)}%;background:var(--amber)"></i></div></div>
  </div>
  <div class="sec"><h3>Perkiraan hasil</h3></div>
  <div class="harv">
    <div class="card hv c-blue"><img class="i3d" src="/assets/3d/flame.webp" alt="" style="width:40px;height:40px"><b class="num">${cook != null ? "±" + cook + " mnt" : "—"}</b><span>Biogas*</span></div>
    <div class="card hv c-green"><img class="i3d" src="/assets/3d/drop.webp" alt="" style="width:40px;height:40px"><b>1 : 10</b><span>Pupuk cair</span></div>
    <div class="card hv c-amber"><img class="i3d" src="/assets/3d/compost.webp" alt="" style="width:40px;height:40px"><b class="num">${fmt(d.level)}%</b><span>Isi tangki</span></div>
  </div>
  <div class="tip"><img class="i3d" src="/assets/3d/leaf.webp" alt="" style="width:40px;height:40px"><div><b>Tips:</b> ${tipText()}</div></div>
  <p class="note">*estimasi dari berat sampah hari ini (±29 menit masak per kg), bukan hasil ukur.</p>
</section>`;
};
function tipText() {
  const d = S.data;
  if (d.temp != null && d.temp < 30) return "suhu di bawah 30 °C, bakteri melambat. Pindahkan mesin ke tempat lebih hangat atau tutup dengan insulasi.";
  if (d.ph != null && d.ph < 6.5) return "pH turun (asam). Berhenti memasukkan sisa makanan 2–3 hari sampai pH kembali ≥ 6,8.";
  if (d.level != null && d.level > 90) return "digester hampir penuh. Ambil pupuk cair dan kosongkan laci kompos dulu.";
  return "potong sisa makanan besar dan hindari tulang, minyak, serta plastik supaya pencernaan stabil.";
}

V.monitor = () => {
  const r = S.range;
  const t = series("temp", r), l = series("level", r), g = series("gasPpm", r);
  const sim = t.sim || l.sim || g.sim;
  const d = S.data;
  return `
<section class="view">
  <div class="ttl"><h2>Monitoring</h2><p>${statusChip()} ARUNA Dapur${S.updatedAt ? " · " + ago(S.updatedAt) : ""}</p></div>
  <div class="seg" role="group" aria-label="Rentang">
    <button data-range="24h" aria-pressed="${r === "24h"}">24 Jam</button>
    <button data-range="7d" aria-pressed="${r === "7d"}">7 Hari</button>
    <button disabled aria-pressed="false" title="Segera">30 Hari</button>
  </div>
  ${sim ? `<div class="banner">${ic("i-bell")}Riwayat alat belum tersedia; grafik memakai data contoh.</div>` : ""}
  <div class="card chart"><div class="hd"><div><span class="eyebrow">Suhu digester</span><div class="big num">${fmt(d.temp, 1)}<small>°C</small></div></div><span class="chip">Ideal 30–38</span></div>
    ${lineChart(t.pts, { band: [30, 38], digits: 1 })}<div class="note">Area hijau = rentang mesofilik ideal.</div></div>
  <div class="card chart"><div class="hd"><div><span class="eyebrow">Isi digester</span><div class="big num">${fmt(d.level)}<small>%</small></div></div><span class="chip blue">Panen di 90 %</span></div>
    ${lineChart(l.pts, { digits: 0, color: "#0E7A6A" })}</div>
  <div class="card chart"><div class="hd"><div><span class="eyebrow">Gas sekitar alat</span><div class="big num">${fmt(d.gasPpm)}<small>ppm</small></div></div><span class="chip ${d.gasPpm > 5000 ? "red" : "grey"}">${d.gasPpm > 5000 ? "Waspada" : "Aman"}</span></div>
    ${lineChart(g.pts, { digits: 0, color: "#2D6BD8" })}<div class="note">Alarm kebocoran di atas 5.000 ppm (10 % LEL metana).</div></div>
  <div class="card list">
    <div class="li"><span class="ico t">${ic("i-flask")}</span><div><b>Keasaman</b><span class="s">ideal 6,8 – 7,5</span></div><span class="sp"></span><div class="val num">${d.ph != null ? "pH " + fmt(d.ph, 1) : "—"}</div></div>
    <div class="li"><span class="ico b">${ic("i-flame")}</span><div><b>Metana di biogas</b><span class="s">sensor NDIR · target ≥ 50 %</span></div><span class="sp"></span><div class="val num">${d.ch4 != null ? fmt(d.ch4) + " %" : "—"}</div></div>
  </div>
</section>`;
};

const KB = [
  { k: ["kulit telur", "cangkang"], a: "Boleh, asal <b>dihancurkan halus</b> dan sedikit saja (segenggam per hari). Cangkang utuh lama terurai." },
  { k: ["api", "kecil", "gas kecil", "tekanan"], a: () => `Cek dua hal: <b>kadar metana</b> (target ≥ 50 %) dan <b>isi tabung gas</b>. ${S.data.ch4 != null ? `Saat ini metana ${fmt(S.data.ch4)} %. ` : ""}Jika metana bagus tapi api kecil, stok gas belum penuh. Tunggu beberapa jam sebelum memasak.` },
  { k: ["suhu", "panas", "dingin"], a: () => `Bakteri pengurai bekerja paling baik pada <b>30–38 °C</b> (mesofilik). Suhu alat sekarang ${fmt(S.data.temp, 1)} °C.` },
  { k: ["pupuk", "cair", "siram", "tanaman"], a: "Ambil dari keran tengah, lalu <b>encerkan 1 : 10</b> dengan air. Siram ke tanah, bukan ke daun, 1–2 kali seminggu." },
  { k: ["kompos", "laci", "padat"], a: "Kosongkan laci kompos saat aplikasi memberi tahu (isi tangki ≥ 90 %). Kompos matang berwarna cokelat gelap dan beraroma tanah; campur dengan tanah 1 : 3." },
  { k: ["lama", "berapa hari", "kapan", "waktu"], a: `Satu siklus desain sekitar <b>${CYCLE_DAYS} hari</b> waktu tinggal di tangki. Gas mulai stabil setelah fase asam (sekitar hari 5–15) lewat.` },
  { k: ["bau", "busuk"], a: "Bau biasanya karena tutup kurang rapat, terlalu banyak daging/ikan, atau pH terlalu asam. Kurangi protein, tutup rapat, dan cek pH di Monitor." },
  { k: ["boleh", "jenis", "apa saja", "masuk"], a: "Boleh: nasi, sayur, buah, kulit buah, ampas kopi/teh. Hindari: <b>plastik, tulang besar, minyak jelantah</b>." },
  { k: ["ph", "asam"], a: () => `pH ideal 6,8–7,5. ${S.data.ph != null ? "Sekarang pH " + fmt(S.data.ph, 1) + ". " : ""}Jika di bawah 6,5, berhenti mengisi 2–3 hari.` },
  { k: ["berapa", "banyak", "kapasitas", "kg"], a: "Kapasitas nominal <b>1,5 kg sisa makanan per hari</b> (maksimal 3 kg sesekali). Sekitar 1,5 kg menghasilkan ±214 L biogas atau ±43 menit memasak (prediksi desain)." },
];
V.tanya = () => `
<section class="view" style="gap:12px">
  <div class="chat-hd"><span class="bot">${ic("i-spark")}</span><div><b>Tanya ARUNA</b><span class="s">● Asisten biodigester (mode demo)</span></div></div>
  <div class="log" id="log">${(S.chat || [{ me: false, t: `Halo ${esc(S.nama)}! Tanyakan apa saja tentang mesin ARUNA: sampah yang boleh masuk, pupuk cair, api biogas, atau suhu.` }])
    .map((m) => `<div class="msg ${m.me ? "me" : "ai"}">${m.t}</div>`).join("")}</div>
  <form class="composer" id="fChat">
    <div class="sugg">${["Kulit telur boleh?", "Api biogas kecil", "Cara pakai pupuk cair", "Kapan kosongkan kompos?", "Bau tidak sedap"].map((s) => `<button type="button" data-q="${s}">${s}</button>`).join("")}</div>
    <div class="inp"><input id="q" placeholder="Tulis pertanyaanmu…" autocomplete="off" aria-label="Pertanyaan"><button class="send" aria-label="Kirim">${ic("i-send")}</button></div>
  </form>
</section>`;
function answer(q) {
  const s = q.toLowerCase();
  let best = null, score = 0;
  KB.forEach((it) => { const n = it.k.filter((k) => s.includes(k)).length; if (n > score) { score = n; best = it; } });
  if (!best) return "Aku belum tahu jawabannya di mode demo. Coba tanya soal <b>jenis sampah</b>, <b>pupuk cair</b>, <b>kompos</b>, <b>api biogas</b>, <b>suhu</b>, atau <b>pH</b>.";
  return typeof best.a === "function" ? best.a() : best.a;
}

const LEARN = [
  ["i-flask", "Apa itu pencernaan anaerob?", "4 tahap kerja bakteri",
    "<p>Tanpa oksigen, bakteri mengurai sisa makanan dalam 4 tahap: <b>hidrolisis</b> (memecah), <b>asidogenesis</b> (menjadi asam), <b>asetogenesis</b> (asetat), lalu <b>metanogenesis</b> (menjadi metana).</p><p>Biogas berisi sekitar 50–70 % metana, sisanya CO₂.</p>"],
  ["i-therm", "Kenapa suhu & pH penting?", "zona nyaman bakteri",
    "<p>Bakteri metana paling aktif di <b>30–38 °C</b> dan <b>pH 6,8–7,5</b>. Sisa makanan cepat menjadi asam; jika pH turun di bawah 6,5, produksi gas berhenti. Karena itu ARUNA menghentikan umpan otomatis saat pH rendah.</p>"],
  ["i-drop", "Cara memakai pupuk cair", "encer 1 : 10",
    "<p>Pupuk cair (digestat) kaya nitrogen. Campur 1 bagian pupuk dengan 10 bagian air, siram ke tanah 1–2 kali seminggu. Jangan dipakai tanpa diencerkan.</p>"],
  ["i-weight", "Sampah apa yang boleh?", "daftar boleh & jangan",
    "<p><b>Boleh:</b> nasi, lauk, sayur, buah, kulit buah, ampas kopi/teh, kulit telur yang dihancurkan.</p><p><b>Jangan:</b> plastik, karet, tulang besar, cangkang keras, minyak jelantah, bahan kimia.</p>"],
  ["i-gauge", "Keamanan biogas", "cara aman memakai gas",
    "<p>Metana mudah terbakar pada 5–15 % di udara. ARUNA memasang sensor kebocoran: di atas 5.000 ppm katup gas menutup dan alarm berbunyi. Cek sambungan selang dengan air sabun secara berkala.</p>"],
];
const FLOW = [
  ["i-weight", "Masukkan & timbang", "Sisa makanan masuk lewat tutup atas; load cell mencatat berat dan kamera mengenali jenisnya."],
  ["i-rot", "Cacah & aduk", "Pencacah dua poros memperkecil ukuran (< 10 mm); pengaduk berjalan 5 menit tiap 2 jam."],
  ["i-flask", "Cerna anaerob", "Bakteri mengurai tanpa oksigen pada 30–38 °C selama ±34 hari (OLR ±3,4 kg VS/m³·hari)."],
  ["i-gauge", "Pantau & lindungi", "Sensor suhu, pH, metana NDIR, level, dan bocor gas dikirim tiap 15 menit; interlock bekerja otomatis."],
  ["i-flame", "Panen biogas", "±214 L biogas/hari pada 1,5 kg/hari, cukup untuk ±43 menit memasak (prediksi desain)."],
  ["i-drop", "Panen pupuk & kompos", "Digestat cair lewat keran (encer 1 : 10); digestat padat terkumpul di laci kompos."],
];
const PAPERS = [
  ["Xu et al. (2018)", "Anaerobic digestion of food waste – challenges and opportunities", "Bioresource Technology 247", "10.1016/j.biortech.2017.09.020"],
  ["Zhang et al. (2007)", "Characterization of food waste as feedstock for anaerobic digestion", "Bioresource Technology 98", "10.1016/j.biortech.2006.02.039"],
  ["Chen et al. (2008)", "Inhibition of anaerobic digestion process: a review", "Bioresource Technology 99", "10.1016/j.biortech.2007.01.057"],
  ["Rajendran et al. (2012)", "Household biogas digesters — a review", "Energies 5", "10.3390/en5082911"],
  ["Weiland (2010)", "Biogas production: current state and perspectives", "Appl. Microbiol. Biotechnol. 85", "10.1007/s00253-009-2246-7"],
  ["Prasetyono et al. (2026)", "IoT-based monitoring system for biodigester production and purification", "J. Mechatronics, Electrical Power & Vehicular Tech. 17", "10.55981/j.mev.2026.1352"],
  ["UNEP (2024)", "Food Waste Index Report 2024", "United Nations Environment Programme", null],
];
V.belajar = () => {
  const t = S.learnTab || "materi";
  const seg = `<div class="seg" role="group" aria-label="Bagian belajar">${[["materi", "Materi"], ["alur", "Alur sistem"], ["riset", "Penelitian"]]
    .map(([k, l]) => `<button data-learn="${k}" aria-pressed="${t === k}">${l}</button>`).join("")}</div>`;
  let body;
  if (t === "alur") {
    body = `<div class="card list">${FLOW.map(([icn, h, d], i) => `<div class="li" style="align-items:flex-start"><span class="ico ${["a", "t", "g", "b", "b", "g"][i]}">${ic(icn)}</span><div><span class="s" style="font-weight:700;color:var(--green)">Langkah ${i + 1}</span><b>${h}</b><span class="s" style="font-size:13px;color:var(--ink-2)">${d}</span></div></div>`).join("")}</div>
      <img src="/assets/img/xray.png" alt="Bagian dalam mesin ARUNA" class="card" style="width:100%;padding:14px;background:#0C3B2E">`;
  } else if (t === "riset") {
    body = `<div class="card list">${PAPERS.map(([a, ti, j, doi]) => `<div class="li" style="align-items:flex-start"><span class="ico t">${ic("i-book")}</span><div><b style="font-size:14px">${ti}</b><span class="s">${a} · ${j}</span>${doi ? `<a class="link" style="display:block;margin-top:2px" href="https://doi.org/${doi}" target="_blank" rel="noopener">doi:${doi}</a>` : ""}</div></div>`).join("")}</div>
      <p class="note">Daftar acuan ilmiah yang dipakai untuk merancang ARUNA.</p>`;
  } else {
    body = `<a class="feature" href="/cerita/"><img class="i3d" src="/assets/3d/leaf-anim.webp" alt="" style="width:64px;height:64px"><div><b>Cerita 3D ARUNA</b><span>Scroll dan lihat mesin bekerja dari dapur ke kompor</span></div></a>
      ${LEARN.map(([icn, ti, sub, bd], i) => `<details class="card"${i === 0 ? " open" : ""}><summary><span class="ico ${["g", "a", "g", "t", "b"][i]}">${ic(icn)}</span><div><b>${ti}</b><span class="s">${sub}</span></div><span class="sp"></span><svg class="i chev"><use href="#i-chev"/></svg></summary><div class="body">${bd}</div></details>`).join("")}`;
  }
  return `<section class="view"><div class="ttl"><h2>Belajar</h2><p>Materi, alur kerja, dan riset di balik ARUNA</p></div>${seg}${body}</section>`;
};

function pref(k, def) { try { const v = localStorage.getItem("aruna:" + k); return v == null ? def : v === "1"; } catch { return def; } }
V.alat = () => `
<section class="view">
  <div class="ttl"><h2>Alat saya</h2><p>1 alat terhubung</p></div>
  <div class="devhero"><img src="img/mesin.png" alt="Mesin ARUNA">
    <div class="txt">${statusChip()}<h4>ARUNA Dapur</h4><span class="id">${DEVICE_ID}</span>
      <div class="kv"><span>Kapasitas <b>1,5 kg/hari</b></span><span>Volume kerja <b>100 L</b></span><span>Terakhir aktif <b>${S.devState?.lastSeen ? ago(S.devState.lastSeen) : S.updatedAt ? ago(S.updatedAt) : "—"}</b></span></div></div></div>
  <div class="sec"><h3>Hubungkan Wi-Fi alat</h3></div>
  <div class="card bt">
    <div class="row"><span class="ico b">${ic("i-bt")}</span><div><b>Lewat Bluetooth</b><div class="note" id="btStatus">Belum terhubung</div></div><span class="sp"></span><button class="chip blue" id="bScan">Pindai</button></div>
    <div class="field"><label for="ssid">Nama Wi-Fi (SSID)</label><input id="ssid" disabled placeholder="Wi-Fi rumah"></div>
    <div class="field"><label for="wpass">Kata sandi Wi-Fi</label><input id="wpass" type="password" disabled></div>
    <button class="btn pri" id="bSend" disabled>${ic("i-wifi")}Kirim ke alat</button>
  </div>
  <div class="sec"><h3>Pengaturan</h3></div>
  <div class="card set">
    ${[["stir", "i-rot", "g", "Pengaduk otomatis", "5 menit tiap 2 jam", true], ["quiet", "i-moon", "t", "Mode malam senyap", "22.00 – 05.00", false], ["notif", "i-bell", "a", "Kabari saat siap panen", "pupuk, kompos, gas", true]]
      .map(([k, icn, c, t, s, def]) => `<div class="li"><span class="ico ${c}">${ic(icn)}</span><div><b>${t}</b><span class="s">${s}</span></div><span class="sp"></span><button class="sw" role="switch" data-pref="${k}" aria-checked="${pref(k, def)}" aria-label="${t}"></button></div>`).join("")}
  </div>
  <p class="note">Pengaturan disimpan di HP ini. Pengiriman perintah ke alat aktif setelah firmware mendukung.</p>
  <div class="sec"><h3>Profil</h3></div>
  <div class="card bt">
    <div class="row"><span class="avatar" style="width:42px;height:42px;font-size:15px">${esc((S.nama[0] || "A").toUpperCase())}</span><div><b>${esc(S.nama)}</b><div class="note">${esc(S.user?.email || (S.user?.isAnonymous ? "Mode tamu — data tidak disimpan permanen" : ""))}</div></div></div>
    <div class="field"><label for="pNama">Nama tampilan</label><input id="pNama" value="${esc(S.nama)}" maxlength="40"></div>
    <button class="btn sec2" id="bSaveNama">${ic("i-check")}Simpan nama</button>
  </div>
  <button class="btn sec2" id="bOut" style="color:var(--red)">${ic("i-power")}Keluar</button>
</section>`;

/* ------------------------------------------------------------------ router & bind */
const ROUTES = ["home", "monitor", "tanya", "belajar", "alat"];
const route = () => { const h = location.hash.slice(1); return ROUTES.includes(h) ? h : "home"; };
let lastRoute = null;
function render(scrollTop = true) {
  if (!S.user) { $tabs.hidden = true; $root.innerHTML = V.login(); bindLogin(); return; }
  const r = route();
  if (r === "tanya" && lastRoute === "tanya" && !scrollTop) return; // jangan ganggu ketikan chat
  const y = window.scrollY;
  $tabs.hidden = false;
  $root.innerHTML = V[r]();
  document.querySelectorAll(".tab").forEach((a) => a.setAttribute("aria-current", a.getAttribute("href") === "#" + r ? "page" : "false"));
  if (scrollTop && r !== lastRoute) window.scrollTo(0, 0); else window.scrollTo(0, y);
  lastRoute = r;
  ({ monitor: bindMonitor, tanya: bindChat, alat: bindAlat, belajar: bindBelajar }[r] || (() => {}))();
}
window.addEventListener("hashchange", () => render(true));

function bindBelajar() {
  document.querySelectorAll("[data-learn]").forEach((b) => b.addEventListener("click", () => { S.learnTab = b.dataset.learn; render(false); }));
}
function bindMonitor() {
  document.querySelectorAll("[data-range]").forEach((b) => b.addEventListener("click", () => { S.range = b.dataset.range; render(false); }));
}
function bindChat() {
  const log = document.getElementById("log"), f = document.getElementById("fChat"), q = document.getElementById("q");
  S.chat = S.chat || [{ me: false, t: log.firstElementChild.innerHTML }];
  const ask = (txt) => {
    if (!txt.trim()) return;
    S.chat.push({ me: true, t: esc(txt) });
    log.insertAdjacentHTML("beforeend", `<div class="msg me">${esc(txt)}</div><div class="typing"><i></i><i></i><i></i></div>`);
    window.scrollTo(0, document.body.scrollHeight);
    setTimeout(() => {
      log.querySelector(".typing")?.remove();
      const a = answer(txt);
      S.chat.push({ me: false, t: a });
      log.insertAdjacentHTML("beforeend", `<div class="msg ai">${a}</div>`);
      window.scrollTo(0, document.body.scrollHeight);
    }, 650);
  };
  f.addEventListener("submit", (e) => { e.preventDefault(); ask(q.value); q.value = ""; });
  f.querySelectorAll("[data-q]").forEach((b) => b.addEventListener("click", () => ask(b.dataset.q)));
}
function bindAlat() {
  document.querySelectorAll("[data-pref]").forEach((b) => b.addEventListener("click", () => {
    const on = b.getAttribute("aria-checked") !== "true";
    b.setAttribute("aria-checked", on);
    try { localStorage.setItem("aruna:" + b.dataset.pref, on ? "1" : "0"); } catch { /* abaikan */ }
    toast("Pengaturan disimpan");
  }));
  document.getElementById("bOut").addEventListener("click", () => signOut(auth).then(() => { location.hash = ""; }));
  document.getElementById("bSaveNama").addEventListener("click", async () => {
    const v = document.getElementById("pNama").value.trim();
    if (!v) { toast("Nama tidak boleh kosong"); return; }
    S.nama = v;
    try { await setDoc(doc(db, "users", S.user.uid), { nama: v, updatedAt: serverTimestamp() }, { merge: true }); toast("Nama disimpan"); }
    catch { toast("Tersimpan di perangkat ini saja (izin database belum aktif)"); }
    render(false);
  });
  // Web Bluetooth provisioning (Nordic UART Service, samakan dengan firmware)
  const SVC = "6e400001-b5a3-f393-e0a9-e50e24dcca9e", RX = "6e400002-b5a3-f393-e0a9-e50e24dcca9e";
  const st = document.getElementById("btStatus"), ssid = document.getElementById("ssid"), pw = document.getElementById("wpass"), send = document.getElementById("bSend");
  let server = null;
  document.getElementById("bScan").addEventListener("click", async () => {
    if (!("bluetooth" in navigator)) { toast("Browser ini belum mendukung Bluetooth web. Pakai Chrome di Android/PC."); return; }
    try {
      st.textContent = "Memindai…";
      const dev = await navigator.bluetooth.requestDevice({ filters: [{ namePrefix: "ARUNA" }, { namePrefix: "BIOSYNC" }], optionalServices: [SVC] });
      server = await dev.gatt.connect();
      st.textContent = "Terhubung: " + (dev.name || "ESP32");
      [ssid, pw, send].forEach((el) => (el.disabled = false));
    } catch (e) { st.textContent = "Belum terhubung"; if (e.name !== "NotFoundError") toast("Gagal terhubung: " + e.message); }
  });
  send.addEventListener("click", async () => {
    if (!server || !ssid.value) { toast("Isi nama Wi-Fi dulu"); return; }
    try {
      const ch = await (await server.getPrimaryService(SVC)).getCharacteristic(RX);
      await ch.writeValue(new TextEncoder().encode(JSON.stringify({ ssid: ssid.value, pass: pw.value })));
      toast("Data Wi-Fi terkirim ke alat");
    } catch (e) { toast("Gagal mengirim: " + e.message); }
  });
}

let mode = "login";
function bindLogin() {
  const f = document.getElementById("fLogin"), err = document.getElementById("err");
  const em = document.getElementById("em"), pw = document.getElementById("pw"), nm = document.getElementById("nm");
  const busy = (on) => f.querySelectorAll("button").forEach((b) => (b.disabled = on));
  const fail = (e) => {
    busy(false);
    const map = { "auth/invalid-credential": "Email atau kata sandi salah.", "auth/invalid-email": "Format email tidak valid.",
      "auth/email-already-in-use": "Email sudah terdaftar. Silakan masuk.", "auth/weak-password": "Kata sandi minimal 6 karakter.",
      "auth/popup-closed-by-user": "Jendela Google ditutup sebelum selesai.", "auth/network-request-failed": "Tidak ada koneksi internet." };
    err.textContent = map[e.code] || "Gagal: " + (e.message || e.code);
  };
  const setMode = (m) => {
    mode = m;
    document.getElementById("nmWrap").hidden = m !== "daftar";
    document.getElementById("bSubmit").innerHTML = (m === "daftar" ? "Buat akun " : "Masuk ") + ic("i-arrow");
    document.getElementById("swText").textContent = m === "daftar" ? "Sudah punya akun?" : "Belum punya akun?";
    document.getElementById("bSwitch").textContent = m === "daftar" ? "Masuk" : "Daftar";
    pw.autocomplete = m === "daftar" ? "new-password" : "current-password";
    err.textContent = "";
  };
  setMode(location.hash === "#daftar" ? "daftar" : mode);
  document.getElementById("bSwitch").addEventListener("click", () => setMode(mode === "daftar" ? "login" : "daftar"));
  f.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!em.value || pw.value.length < 6) { err.textContent = "Isi email dan kata sandi (minimal 6 karakter)."; return; }
    busy(true); err.textContent = "";
    try {
      if (mode === "daftar") {
        const c = await createUserWithEmailAndPassword(auth, em.value.trim(), pw.value);
        await setDoc(doc(db, "users", c.user.uid), { nama: nm.value.trim() || em.value.split("@")[0], email: c.user.email, createdAt: serverTimestamp() }, { merge: true }).catch(() => {});
      } else {
        await signInWithEmailAndPassword(auth, em.value.trim(), pw.value);
      }
    } catch (x) { fail(x); }
  });
  document.getElementById("bGoogle").addEventListener("click", () => { busy(true); signInWithPopup(auth, googleProvider).catch(fail); });
  document.getElementById("bGuest").addEventListener("click", () => { busy(true); signInAnonymously(auth).catch(fail); });
  document.getElementById("bReset").addEventListener("click", () => {
    if (!em.value) { err.textContent = "Isi email dulu, lalu tekan Lupa sandi."; return; }
    sendPasswordResetEmail(auth, em.value.trim()).then(() => toast("Tautan reset dikirim ke email")).catch(fail);
  });
}

/* ------------------------------------------------------------------ start */
let subscribed = false;
onAuthStateChanged(auth, async (user) => {
  S.user = user;
  if (user) {
    S.nama = user.displayName || (user.isAnonymous ? "Tamu" : (user.email || "Pengguna").split("@")[0]);
    try { const snap = await getDoc(doc(db, "users", user.uid)); if (snap.exists() && snap.data().nama) S.nama = snap.data().nama; } catch { /* offline */ }
    if (!subscribed) { subscribed = true; subscribe(); }
    if (!ROUTES.includes(location.hash.slice(1))) history.replaceState(null, "", "#home");
  }
  render(true);
});
if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});
