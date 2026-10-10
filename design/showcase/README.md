# ARUNA Showcase

Paket presentasi ARUNA: video use case portrait, web scroll interaktif, deck PPTX, poster A2, dan brosur trifold.
Semua visual dihasilkan skrip, jadi revisi cukup dengan mengubah konstanta lalu menjalankan ulang.

## Struktur

| Folder | Isi |
|---|---|
| `char/` | Karakter Sketchfab (`source.glb`), `rig.py` (Rigify + 7 aksi FK), `export_glb.py` (GLB web) |
| `video/` | `scene.py` (scene Blender 560 frame), `edit.py` (intro, caption, segmen app, outro, musik) → `ARUNA_usecase_portrait.mp4` |
| `web/` | `index.html` (three.js, karakter bergerak mengikuti scroll), `assets/*.glb`, `shoot.py` (QA Playwright) |
| `deck/` | `make_bg_loop.py` (video latar looping), `hw_xray.py`, `cover_render.py`, `deck.py` → `ARUNA_deck_en.pptx`, `ARUNA_deck_id.pptx` |
| `print/` | `build_print.py` → poster A2 + brosur A4 (PDF & PNG), `id` dan `en` |

## Urutan build ulang (dari root repo)

```bash
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
"$B" -b -P design/showcase/char/rig.py                                   # rig Rigify + aksi
"$B" -b design/showcase/char/char_rigged.blend -P design/showcase/char/export_glb.py
"$B" -b design/blender/aruna_mesin.blend -P design/showcase/video/scene.py   # (--test = 540x960)
"$B" -b design/showcase/video/usecase.blend -a                           # render frame (bisa dilanjutkan)
python design/showcase/video/edit.py
python design/showcase/deck/make_bg_loop.py
"$B" -b design/blender/aruna_mesin.blend -P design/showcase/deck/hw_xray.py
"$B" -b design/showcase/video/usecase.blend -P design/showcase/deck/cover_render.py
python design/showcase/deck/deck.py en && python design/showcase/deck/deck.py id
python design/showcase/print/build_print.py id && python design/showcase/print/build_print.py en   # poster showcase (+ aset)
python design/showcase/print/build_brosur_pro.py id && python design/showcase/print/build_brosur_pro.py en   # brosur (gaya poster; jalankan SETELAH build_print)
```

Web lokal: `cd design/showcase/web && python -m http.server` lalu buka `http://localhost:8000` (GLB tidak bisa dimuat lewat `file://`).

## Keputusan

- Karakter: “Casual Male 3D Character – T-Pose” oleh sthaarpit (Sketchfab, CC-BY 4.0). Kredit wajib dicantumkan dan sudah ada di web, video, deck, poster, dan brosur. Karakter sebelumnya diganti atas permintaan (pakaian kurang sopan).
- Rigging: addon Rigify (metarig human). Bone heat dijalankan pada proxy voxel-remesh, lalu bobotnya ditransfer ke mesh asli. Animasi memakai kontrol FK.
- Bahasa: video berbahasa Indonesia. Deck, poster, dan brosur tersedia dalam ID dan EN.
- Video latar PPTX diputar otomatis, tanpa suara, dan berulang terus (`repeatCount="indefinite"`) di setiap slide.

## Belum final / asumsi

- **Slide 10–11 dan angka hasil** (CH₄ per hari, 2,4 kg/hari, SUS 78) adalah **data ilustrasi** dan diberi label. Ganti dengan hasil uji lapangan.
- `[Team name]`, `[Institution]`, dan `[n]` rumah tangga adalah placeholder.
- Angka ±45 menit gas dan ±1,4 L pupuk adalah target desain, bukan hasil ukur.
- Statistik latar belakang berasal dari SIPSN KLHK (komposisi sampah) dan Bappenas 2021 (Food Loss & Waste di Indonesia).
