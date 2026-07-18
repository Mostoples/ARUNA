# 🌱 ARUNA

**Anaerobic Recycling and Upcycling of Nutrient-rich Food Waste**

Aplikasi web pendamping *smart biodigester* (BIOSYNC) untuk sekolah program MBG —
mengubah sisa makanan menjadi biogas, pupuk cair, dan kompos padat, sekaligus
menjadi media belajar ekonomi sirkular.

🔗 **Live**: https://aruna-id.web.app

## Fitur

- **Monitoring IoT real-time** — berat sampah, suhu, gas metana (MQ-4), dan level
  digester dari ESP32 via Firebase Realtime Database
- **Langkah Sistem** — SOP interaktif, fase proses, checklist harian
- **Ensiklopedia / Silabus** — materi biogas, fermentasi anaerob, kompos
- **AI Edukator** — chat tanya-jawab seputar biodigester
- **Daftar Penelitian** — referensi riset untuk karya ilmiah siswa
- **Manajemen Perangkat** — klaim unit + provisioning WiFi via **Web Bluetooth** ke ESP32
- Autentikasi email / Google / mode tamu, mode terang-gelap, responsif
  (sidebar desktop, navbar bawah mobile), gaya *neu-glass* (glassmorphism × neumorphism)

## Teknologi

HTML, CSS, dan JavaScript murni (tanpa framework/build tool) + Firebase:
**Auth**, **Realtime Database** (telemetri alat), **Firestore** (profil & konten),
**Hosting**. SDK dimuat sebagai ES Module dari CDN gstatic.

## Struktur

```
├── docs/analisis-kebutuhan.md   # analisis kebutuhan & roadmap
├── firebase.json                # konfigurasi hosting + rules
├── database.rules.json          # security rules RTDB
├── firestore.rules              # security rules Firestore
├── deploy.ps1                   # deploy otomatis (service account)
└── public/                      # root Firebase Hosting
    ├── index.html               # landing page
    ├── login.html               # masuk / daftar
    ├── home.html …              # halaman aplikasi (dijaga auth)
    └── assets/
        ├── css/                 # style.css (design system), pages.css, …
        └── js/                  # layout.js, firebase-init.js, auth.js, live.js, …
```

## Menjalankan & Deploy

Pratinjau lokal cukup buka `public/index.html` di browser (fitur Firebase butuh
domain ter-otorisasi; gunakan `firebase serve` bila perlu).

Deploy (butuh `secrets/service-account.json` — tidak ada di repo):

```powershell
.\deploy.ps1
```

> ⚠️ Folder `secrets/` berisi kredensial dan **tidak boleh** di-commit — sudah
> tercantum di `.gitignore`.

## Skema Data (RTDB)

```
devices/{deviceId}/
  info      { name, model, firmware, school }
  state     { online, phase, fermentDay, lastSeen }
  telemetry { weightToday, temp, gasPpm, gasStatus, level, updatedAt }
```

ESP32 menulis ke `telemetry`; aplikasi berlangganan lewat `assets/js/live.js`.

---

© 2026 Tim ARUNA · Dibangun untuk sekolah program MBG 💚
