# Analisis Kebutuhan — ARUNA

**ARUNA: Anaerobic Recycling and Upcycling of Nutrient-rich Food Waste**

Aplikasi web pendamping alat *smart biodigester* (BIOSYNC) untuk memonitor pengolahan
sisa makanan menjadi biogas, pupuk cair, dan kompos padat — sekaligus menjadi media
edukasi di lingkungan sekolah (program MBG).

Tanggal analisis: 10 Juli 2026

---

## 1. Latar Belakang & Tujuan

Alat biodigester menghasilkan data real-time (berat sampah, suhu, gas, level digester,
status) melalui ESP32. Dibutuhkan aplikasi web yang:

1. Menampilkan data monitoring secara real-time.
2. Mengedukasi pengguna (siswa/guru) tentang proses anaerobik.
3. Mengelola perangkat (pairing, konfigurasi, koneksi Bluetooth/WiFi).
4. Menyediakan asisten AI untuk tanya-jawab edukatif.
5. Mendokumentasikan penelitian terkait.

## 2. Pengguna (Aktor)

| Aktor | Deskripsi | Hak Akses |
|---|---|---|
| **Pengunjung** | Belum login | Landing page, daftar/masuk |
| **Pengguna** (siswa/guru) | Sudah login | Semua fitur, kelola perangkat miliknya |
| **Admin** | Pengelola konten | + kelola ensiklopedia, penelitian, semua perangkat |
| **Perangkat (ESP32)** | Alat biodigester | Kirim telemetri ke RTDB, terima perintah |

## 3. Kebutuhan Fungsional

### F1 — Autentikasi (Firebase Auth)
- Daftar & masuk dengan email/password dan Google Sign-In.
- Lupa password (email reset), verifikasi email.
- Profil pengguna (nama, sekolah, foto) disimpan di Firestore.
- Proteksi halaman: selain landing/login, wajib login (redirect guard).

### F2 — Monitoring Alat (fitur inti)
- Data real-time dari Firebase RTDB: **berat sampah (kg)**, **suhu digester (°C)**,
  **gas (ppm/status)**, **level digester (%)**, **status alat** (online/offline, fase fermentasi).
- Grafik riwayat (suhu, gas, berat) harian/mingguan dengan tooltip interaktif.
- Ambang batas & indikator status (Normal / Waspada / Bahaya) — suhu operasional 30–40 °C.
- Ringkasan hasil: estimasi biogas, pupuk cair, kompos padat.
- Riwayat input sampah (dari sensor berat + kamera jenis sampah — jika tersedia).

### F3 — Langkah-Langkah Sistem
- Alur kerja alat langkah demi langkah (input → pencacahan → fermentasi anaerob →
  panen hasil) dengan ilustrasi dan indikator progres fase alat yang sedang berjalan.
- Panduan operasional & keselamatan (SOP), checklist harian.

### F4 — Ensiklopedia / Silabus
- Kumpulan materi terstruktur (bab/sub-bab): biogas, fermentasi anaerob, komposting,
  ekonomi sirkular, dsb. Konten dari Firestore (bisa dikelola admin).
- Pencarian & filter kategori, penanda "sudah dibaca".

### F5 — AI Edukator
- Chat tanya-jawab seputar biodigester & pengolahan sampah.
- Konteks data alat dapat disertakan ("suhu digester saya 35 °C, normal?").
- Implementasi: endpoint AI (mis. Claude API) dipanggil via Cloud Function /
  proxy server agar API key tidak terekspos di klien. Riwayat chat di Firestore.

### F6 — Daftar Penelitian
- Katalog penelitian/jurnal terkait (judul, penulis, tahun, abstrak, tautan/PDF).
- Pencarian, filter tahun/topik. Admin dapat menambah entri.

### F7 — Manajemen Perangkat
- Daftar perangkat milik pengguna (klaim via kode/ID perangkat).
- Detail perangkat: nama, lokasi, firmware, status koneksi, kalibrasi sensor.
- **Bluetooth (Web Bluetooth API)**: pairing langsung ke ESP32 via BLE untuk
  provisioning (mengatur SSID/password WiFi), baca data lokal saat offline.
  ⚠️ Web Bluetooth hanya didukung Chrome/Edge dan wajib HTTPS/localhost.
- Perintah jarak jauh (via RTDB): nyalakan/matikan shredder, mode, dsb.

### F8 — Landing Page
- Publik: hero, deskripsi alat, fitur utama, hasil (biogas/pupuk/kompos),
  spesifikasi teknis, CTA daftar/masuk.

## 4. Kebutuhan Non-Fungsional

| Aspek | Kebutuhan |
|---|---|
| **Teknologi** | HTML, CSS, JS murni (tanpa framework/build tool) |
| **Backend** | Firebase: Auth, Realtime Database (telemetri), Firestore (konten/profil), Hosting |
| **Responsif** | Mobile-first; **navbar bawah di mobile**, **sidebar di desktop** (breakpoint ± 1024px) |
| **Gaya visual** | Glassmorphism (kartu/permukaan) + Neumorphism (kontrol/tombol), mode **terang & gelap** (toggle + ikut preferensi sistem, tersimpan di localStorage) |
| **Aksesibilitas** | Kontras teks memadai di kedua mode, ikon + label (bukan warna saja), target sentuh ≥ 44px |
| **Performa** | Tanpa CDN berat; ikon SVG inline; grafik canvas native |
| **Keamanan** | Firebase Security Rules per-pengguna; API key AI di server-side |

## 5. Arsitektur & Model Data

### 5.1 Alur data
```
ESP32 ──WiFi──▶ Firebase RTDB ──listener──▶ Web App (monitoring real-time)
ESP32 ◀──BLE (Web Bluetooth)──▶ Web App (provisioning / mode offline)
Web App ──▶ Firestore (profil, konten, chat, penelitian)
Web App ──▶ Cloud Function ──▶ AI API (edukator)
```

### 5.2 Realtime Database (telemetri — data cepat)
```
devices/
  {deviceId}/
    info:      { name, owner(uid), model, firmware, claimedAt }
    state:     { online, phase, lastSeen }
    telemetry: { weightToday, temp, gasPpm, gasStatus, level, updatedAt }
    history/
      {yyyy-mm-dd}/{hh}: { temp, gasPpm, weight, level }
    commands:  { shredder, requestedBy, ts }
```

### 5.3 Firestore (data terstruktur)
```
users/{uid}            → nama, sekolah, peran, deviceIds[]
articles/{id}          → ensiklopedia (judul, kategori, bab, konten, urutan)
researches/{id}        → penelitian (judul, penulis, tahun, abstrak, url)
chats/{uid}/messages   → riwayat AI edukator
```

### 5.4 Struktur folder proyek
```
ARUNA/
├── docs/                     ← dokumen analisis & desain
├── firebase.json, .rules     ← konfigurasi deploy (menyusul, bersama config)
└── public/                   ← root Firebase Hosting
    ├── index.html            ← landing page (publik)
    ├── login.html            ← masuk / daftar
    ├── home.html             ← dashboard (halaman ini dibuat pertama) ✅
    ├── monitoring.html       ← monitoring detail + grafik riwayat
    ├── langkah.html          ← langkah-langkah sistem
    ├── ensiklopedia.html     ← silabus/materi
    ├── ai-edukator.html      ← chat AI
    ├── penelitian.html       ← daftar penelitian
    ├── perangkat.html        ← manajemen perangkat + Bluetooth
    ├── profil.html           ← profil & pengaturan
    └── assets/
        ├── css/  (style.css = design system, <page>.css = per halaman)
        ├── js/   (theme.js, layout.js, firebase-init.js*, <page>.js)
        └── img/
```
`*` menunggu config Firebase dari pemilik proyek — sementara halaman berjalan
dengan **data dummy tersimulasi** agar UI bisa direview.

## 6. Peta Navigasi

| Menu | Mobile (navbar bawah) | Desktop (sidebar) |
|---|---|---|
| Beranda | ✅ | ✅ |
| Monitoring | ✅ | ✅ |
| AI Edukator | ✅ (tombol tengah menonjol) | ✅ |
| Ensiklopedia | ✅ | ✅ |
| Lainnya → (Langkah, Penelitian, Perangkat, Profil) | ✅ (sheet) | ✅ (item terpisah) |

## 7. Tahapan Pengerjaan (roadmap)

1. ✅ **Analisis kebutuhan** (dokumen ini)
2. 🔄 **Halaman Home (dashboard)** — design system, layout responsif, tema — *menunggu ACC*
3. Landing page + Login/Daftar
4. Monitoring detail + grafik riwayat
5. Langkah sistem, Ensiklopedia, Penelitian
6. AI Edukator
7. Manajemen Perangkat + Web Bluetooth (ESP32)
8. Integrasi Firebase (Auth, RTDB, Firestore) — setelah config diterima
9. Security Rules + Deploy Hosting
