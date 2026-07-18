/* ARUNA — AI Edukator (mode demo).
   Jawaban dari basis pengetahuan lokal berbasis kata kunci.
   Tahap integrasi: panggilan ke model AI lewat Cloud Function
   + konteks data alat dari RTDB, riwayat disimpan di Firestore. */
(function () {
  "use strict";

  var log = document.getElementById("chatLog");
  var form = document.getElementById("chatForm");
  var text = document.getElementById("chatText");

  /* ---------- Basis pengetahuan demo ---------- */
  var KB = [
    { kunci: ["suhu", "panas", "dingin", "derajat", "30", "40"],
      jawab: "Suhu <b>30–40 °C</b> adalah zona nyaman bakteri <b>mesofilik</b> yang menguraikan sampah. " +
        "Di bawah 30 °C kerja bakteri melambat sehingga biogas sedikit; di atas 40 °C bakteri bisa mati. " +
        "Alat menjaga suhu ini otomatis, dan kamu bisa memantaunya di halaman Monitoring. Suhu digester saat ini sekitar <b>35,6 °C</b> — optimal! ✅" },
    { kunci: ["biogas", "gas apa", "metana", "ch4", "energi"],
      jawab: "<b>Biogas</b> adalah gas hasil penguraian bahan organik tanpa oksigen (anaerob). Komposisinya sekitar " +
        "<b>50–70% metana (CH₄)</b> dan sisanya CO₂. Metana inilah yang bisa dibakar untuk kompor kantin sekolah. " +
        "1 kg sisa makanan bisa menghasilkan kira-kira 0,05–0,1 m³ biogas 🔥" },
    { kunci: ["gas tinggi", "ppm", "bahaya", "bocor", "waspada", "800"],
      jawab: "Kalau pembacaan gas melebihi <b>800 ppm</b> di area sekitar alat, itu tanda perlu waspada: " +
        "1) pastikan ventilasi ruangan baik, 2) periksa sambungan selang gas dengan air sabun (muncul gelembung = bocor), " +
        "3) jauhkan api terbuka. Jika angka terus naik, tutup katup gas dan laporkan ke guru pembina ⚠️" },
    { kunci: ["pupuk", "cair", "tanaman", "siram", "poc"],
      jawab: "<b>Pupuk organik cair (POC)</b> dari digester kaya nitrogen. Cara pakainya: <b>encerkan 1 bagian pupuk " +
        "dengan 10–20 bagian air</b>, lalu siramkan ke media tanam (bukan langsung ke daun) 1–2× seminggu. " +
        "Jangan gunakan tanpa diencerkan karena terlalu pekat untuk tanaman 🌿" },
    { kunci: ["lama", "berapa hari", "waktu", "fermentasi", "selesai", "panen"],
      jawab: "Fermentasi anaerob di alat ini butuh <b>7–14 hari</b> tergantung jenis sampah dan suhu. " +
        "Sampah lunak (nasi, sayur) lebih cepat; yang berserat lebih lama. Digester-mu sekarang di <b>hari ke-5</b> — " +
        "biasanya gas mulai stabil di hari 5–7, jadi sebentar lagi! ⏳" },
    { kunci: ["kompos", "padat", "media tanam"],
      jawab: "<b>Kompos padat</b> adalah ampas fermentasi yang sudah stabil. Ciri kompos matang: warna cokelat kehitaman, " +
        "tidak berbau busuk (beraroma tanah), dan remah. Bisa langsung dicampur tanah 1:3 untuk media tanam, " +
        "atau dikemas sebagai produk kewirausahaan sekolah 🪴" },
    { kunci: ["bau", "busuk", "amis"],
      jawab: "Bau menyengat biasanya karena: 1) tutup hopper kurang rapat, 2) terlalu banyak sampah berprotein " +
        "(daging/ikan), atau 3) pH digester terlalu asam. Coba kurangi porsi protein, tambahkan sampah karbon " +
        "(daun kering sedikit), dan pastikan semua seal tertutup. Fermentasi sehat harusnya nyaris tidak berbau 👃" },
    { kunci: ["sampah apa", "boleh", "masuk", "jenis", "input"],
      jawab: "Yang <b>boleh</b>: nasi, sayur, buah, kulit buah, sisa lauk. Yang <b>dihindari</b>: tulang besar, " +
        "plastik/kemasan, minyak dalam jumlah banyak, dan kulit telur berlebihan. Potongan kecil lebih baik — " +
        "tapi tenang, shredder alat akan mencacahnya otomatis 😄" }
  ];

  var FALLBACK =
    "Pertanyaan bagus! Di mode demo, aku baru bisa menjawab topik dasar: <b>suhu digester</b>, <b>biogas</b>, " +
    "<b>gas tinggi</b>, <b>pupuk cair</b>, <b>kompos</b>, <b>lama fermentasi</b>, <b>bau</b>, dan <b>jenis sampah</b>. " +
    "Setelah tersambung ke model AI pada tahap integrasi, aku bisa menjawab apa saja plus membaca data alatmu langsung 🤖✨";

  function jawab(q) {
    q = q.toLowerCase();
    var skorTerbaik = 0, hasil = null;
    KB.forEach(function (item) {
      var skor = 0;
      item.kunci.forEach(function (k) { if (q.indexOf(k) !== -1) skor++; });
      if (skor > skorTerbaik) { skorTerbaik = skor; hasil = item.jawab; }
    });
    return hasil || FALLBACK;
  }

  /* ---------- Render pesan ---------- */
  function tambah(cls, html) {
    var el = document.createElement("div");
    el.className = "msg " + cls;
    el.innerHTML = html;
    log.appendChild(el);
    log.scrollTop = log.scrollHeight;
    return el;
  }

  function balas(q) {
    var typing = tambah("msg--bot", '<span class="typing"><i></i><i></i><i></i></span>');
    var tunggu = 700 + Math.random() * 900;
    setTimeout(function () {
      typing.remove();
      tambah("msg--bot", jawab(q));
    }, tunggu);
  }

  function kirim(q) {
    q = q.trim();
    if (!q) return;
    tambah("msg--user", q.replace(/</g, "&lt;"));
    text.value = "";
    text.style.height = "";
    balas(q);
  }

  form.addEventListener("submit", function (e) { e.preventDefault(); kirim(text.value); });
  text.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); kirim(text.value); }
  });
  text.addEventListener("input", function () {
    text.style.height = "auto";
    text.style.height = Math.min(120, text.scrollHeight) + "px";
  });
  document.querySelectorAll(".suggest").forEach(function (btn) {
    btn.addEventListener("click", function () { kirim(btn.textContent); });
  });

  /* ---------- Sapaan pembuka ---------- */
  setTimeout(function () {
    tambah("msg--bot",
      "Halo! Aku <b>ARUNA</b>, edukator biodigester-mu 🌱<br>" +
      "Tanyakan apa saja soal biogas, fermentasi, pupuk, atau data alatmu. " +
      "Coba mulai dari pertanyaan cepat di bawah ini 👇");
  }, 350);
})();
