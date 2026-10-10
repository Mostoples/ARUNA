"""
Brosur trifold A4 lanskap ARUNA — versi berwarna & bercorak (HTML -> Playwright -> PDF + PNG).

  python design/showcase/print/build_print.py id      # menyiapkan _assets (sekali)
  python design/showcase/print/build_brosur.py [id|en]
Keluaran: ARUNA_brosur_A4_<lang>.pdf (2 halaman: luar, dalam) + ARUNA_brosur_luar/dalam_<lang>.png
"""
import asyncio
import json
import os
import sys
from urllib.parse import quote

LANG = (sys.argv[1] if len(sys.argv) > 1 else "id").lower()
HERE = os.path.dirname(os.path.abspath(__file__))
SHOW = os.path.dirname(HERE)
DESIGN = os.path.dirname(SHOW)
CALC = json.load(open(os.path.join(DESIGN, "competition", "calc.json")))
NM = CALC["nominal"]
PTS = json.load(open(os.path.join(SHOW, "deck", "assets", "hw_points.json")))
CROP = (0.2, 0.1, 0.8, 0.95)
BW, BH = 1123, 794


def T(id_, en):
    return id_ if LANG == "id" else en


def num(v, d=0):
    s_ = f"{v:,.{d}f}"
    return s_.replace(",", "X").replace(".", ",").replace("X", ".") if LANG == "id" else s_


def svg(markup, w, h):
    return "url('data:image/svg+xml," + quote(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">{markup}</svg>', safe="") + "')"


# ---------------------------------------------------------------- corak
P_DOTS = svg('<circle cx="6" cy="6" r="2" fill="#ffffff" fill-opacity=".22"/>', 18, 18)
P_DOTS_G = svg('<circle cx="6" cy="6" r="2" fill="#158A52" fill-opacity=".18"/>', 18, 18)
P_WAVE = svg(''.join(f'<path d="M0 {y} Q 47 {y-14} 94 {y} T 188 {y} T 282 {y} T 376 {y}" fill="none" stroke="#ffffff" stroke-opacity=".28" stroke-width="2"/>'
                     for y in range(20, 820, 34)), 376, 800)
P_WAVE_G = svg(''.join(f'<path d="M0 {y} Q 47 {y-14} 94 {y} T 188 {y} T 282 {y} T 376 {y}" fill="none" stroke="#0E7A6A" stroke-opacity=".16" stroke-width="2"/>'
                       for y in range(20, 820, 38)), 376, 800)
LEAF = ('<path d="M30 70 C 0 40 20 5 70 0 C 70 45 55 70 30 70 Z" fill="#A6EBC5" fill-opacity=".14"/>'
        '<path d="M30 70 L 62 10" stroke="#A6EBC5" stroke-opacity=".2" stroke-width="2"/>')
P_LEAF = svg(f'<g transform="translate(10 10)">{LEAF}</g><g transform="translate(110 90) rotate(40 35 35)">{LEAF}</g>', 190, 190)
P_STRIPE = svg('<path d="M0 40 L40 0" stroke="#ffffff" stroke-opacity=".09" stroke-width="10"/>', 40, 40)


def blob(color, opacity=1.0):
    return svg(f'<path fill="{color}" fill-opacity="{opacity}" d="M150 20 C 230 10 290 80 280 160 C 270 240 200 290 130 280 '
               f'C 50 270 5 210 15 140 C 25 70 80 28 150 20 Z"/>', 300, 300)


A = "_assets/"


def pt(k):
    u, v = PTS[k]
    return (u - CROP[0]) / (CROP[2] - CROP[0]) * 100, (v - CROP[1]) / (CROP[3] - CROP[1]) * 100


PARTS = [("pencacah", T("Pencacah dua poros", "Twin-shaft shredder"), "L"), ("loadcell", T("Load cell (berat)", "Load cell"), "L"),
         ("layar", T("Panel 7″ + ESP32-S3", "7″ panel + ESP32-S3"), "L"), ("suhu", T("Sensor suhu", "Temperature"), "L"),
         ("keran", T("Keran pupuk cair", "Fertilizer tap"), "L"), ("kompos", T("Laci kompos", "Compost drawer"), "L"),
         ("level", T("Sensor level", "Level sensor"), "R"), ("gas", T("Sensor metana NDIR", "NDIR methane"), "R"),
         ("pengaduk", T("Pengaduk otomatis", "Auto stirrer"), "R"), ("ph", T("Probe pH", "pH probe"), "R"),
         ("gauge", T("Gauge + katup gas", "Gas gauge + valve"), "R")]


def xray(width_pct=46, fs=9.5):
    svgl, html = [], []
    for side in ("L", "R"):
        items = sorted([p for p in PARTS if p[2] == side], key=lambda p: PTS[p[0]][1])
        for i, (k, lab, _) in enumerate(items):
            x, y = pt(k)
            ly = 6 + i * (88 / max(1, len(items) - 1))
            lx = -2 if side == "L" else 102
            svgl.append(f'<line x1="{x}" y1="{y}" x2="{lx}" y2="{ly}" stroke="#FFD166" style="stroke-width:1.6px" vector-effect="non-scaling-stroke"/>')
            html.append(f'<span class="xd" style="left:{x}%;top:{y}%"></span>')
            anchor = "right:102%;text-align:right" if side == "L" else "left:102%"
            html.append(f'<div class="xl" style="{anchor};top:calc({ly}% - 7px);font-size:{fs}px">{lab}</div>')
    return (f'<div style="position:relative;width:{width_pct}%;margin:0 auto"><img src="{A}xray.png" style="width:100%;display:block">'
            f'<svg viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute;inset:0;width:100%;height:100%;overflow:visible">'
            + "".join(svgl) + "</svg>" + "".join(html) + "</div>")


STATS = [("53 kg", T("sisa makanan rumah tangga per orang per tahun", "household food waste per person per year"), "UNEP 2024", "#158A52"),
         (num(14.7, 1) + " Mt", T("sisa makanan rumah tangga per tahun di Indonesia", "household food waste per year in Indonesia"), "UNEP 2024", "#0E7A6A"),
         ("≈40%", T("sampah kota berupa sisa makanan", "of municipal waste is food"), "SIPSN KLHK 2023", "#E8912D"),
         (num(1.7, 1) + " Gt", T("CO₂e dari susut & sisa pangan 2000–2019", "CO₂e from food loss & waste 2000–2019"), "Bappenas 2021", "#E8604C")]
STEPS = [(96, T("Masukkan", "Put in"), T("Buka tutup, tuang sisa makanan.", "Open the lid, tip the leftovers."), "#158A52"),
         (165, T("Cerna", "Digest"), T("Dicacah & diaduk otomatis, ±34 hari.", "Shredded & stirred, ±34 days."), "#0E7A6A"),
         (250, T("Pantau", "Monitor"), T("Status & notifikasi di HP.", "Status & alerts on your phone."), "#2D9CDB"),
         (330, T("Pupuk cair", "Fertilize"), T("Encerkan 1:10, siram tanaman.", "Dilute 1:10, water plants."), "#E8912D"),
         (430, T("Masak", "Cook"), T(f"Api biru biogas, ±{num(NM['cook'])} menit/hari*.", f"Blue biogas flame, ±{num(NM['cook'])} min/day*."), "#E8604C")]
SDGS = [("7", T("Energi bersih & terjangkau", "Affordable & clean energy"), "#C89A08"),
        ("11", T("Kota berkelanjutan", "Sustainable cities"), "#E08010"),
        ("12", T("Konsumsi bertanggung jawab", "Responsible consumption"), "#A07426"),
        ("13", T("Penanganan iklim", "Climate action"), "#3F7E44")]
CREDIT = T("*Prediksi perhitungan desain pada 1,5 kg/hari. Karakter 3D: sthaarpit (Sketchfab, CC-BY 4.0), rig Rigify.",
           "*Design-calculation prediction at 1.5 kg/day. 3D character: sthaarpit (Sketchfab, CC-BY 4.0), Rigify rig.")

CSS = f"""
@page{{size:297mm 210mm;margin:0}}
:root{{--ink:#10201A;--ink2:#3C4E45;--deep:#0F6B40;--green:#158A52;--teal:#0E7A6A;--mint:#CDEFD9;--sun:#FFD166;--orange:#E8912D;
--coral:#E8604C;--sky:#2D9CDB;--cream:#FFF6E5;--sans:"Plus Jakarta Sans","Segoe UI",sans-serif}}
*{{box-sizing:border-box;margin:0}}
body{{width:{BW}px;font-family:var(--sans);color:var(--ink);-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.sheet{{width:{BW}px;height:{BH}px;display:grid;grid-template-columns:repeat(3,1fr);page-break-after:always;overflow:hidden}}
.pn{{position:relative;overflow:hidden;padding:30px 26px;display:flex;flex-direction:column;gap:12px}}
.pn > *{{position:relative;z-index:1}}
.deco{{position:absolute!important;z-index:0!important;pointer-events:none;background-repeat:no-repeat;background-size:contain}}
.chip{{align-self:flex-start;font-size:9.5px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;padding:6px 12px;border-radius:99px;background:#fff;color:var(--deep);box-shadow:0 4px 10px -4px rgba(0,0,0,.25)}}
h1,h2{{letter-spacing:-.035em;line-height:1.02;font-weight:800}}
h2{{font-size:27px}}
p,li{{font-size:11.5px;line-height:1.5}}
.card{{background:#fff;border-radius:16px;box-shadow:0 10px 24px -14px rgba(0,0,0,.35)}}
.n{{display:inline-grid;place-items:center;border-radius:50%;color:#fff;font-weight:800;flex:none}}
.xd{{position:absolute;width:9px;height:9px;margin:-4.5px 0 0 -4.5px;border-radius:50%;background:var(--sun);box-shadow:0 0 0 4px rgba(255,209,102,.3)}}
.xl{{position:absolute;white-space:nowrap;font-weight:700;color:#fff}}
"""


def deco(bg, style):
    return f'<div class="deco" style="background-image:{bg};{style}"></div>'


outside = f"""
<div class="sheet">
  <!-- 1. flap dalam: spesifikasi (kuning matahari) -->
  <div class="pn" style="background:linear-gradient(165deg,#FFE29A 0%,#FFC85C 55%,#F6A623 100%)">
    {deco(P_WAVE, "inset:0;background-size:cover;opacity:.9")}
    {deco(blob('#ffffff', .55), "width:330px;height:330px;left:20px;top:150px")}
    {deco(blob('#E8604C', .25), "width:120px;height:120px;right:-30px;top:-20px")}
    <span class="chip">{T("Spesifikasi", "Specifications")}</span>
    <h2>{T("Kecil di dapur,", "Small in the kitchen,")}<br><span style="color:var(--deep)">{T("besar dampaknya.", "big in impact.")}</span></h2>
    <img src="{A}mesin.png" style="height:330px;align-self:center;filter:drop-shadow(0 16px 18px rgba(0,0,0,.25))">
    <div style="display:grid;gap:6px;margin-top:auto">
    {''.join(f'<div class="card" style="display:flex;align-items:center;gap:9px;padding:7px 10px;border-radius:12px"><span class="n" style="width:22px;height:22px;font-size:10px;background:{c}">{i}</span><span style="font-size:11px;font-weight:600">{t}</span></div>'
             for i, (t, c) in enumerate([(T("44 × 44 × 112 cm, beroda", "44 × 44 × 112 cm, on wheels"), "#158A52"),
                                         (T("1,5 kg sisa makanan/hari (puncak 3 kg)", "1.5 kg food waste/day (peak 3 kg)"), "#0E7A6A"),
                                         (T("Volume kerja 100 L · ±34 hari cerna", "100 L working volume · ±34 days"), "#2D9CDB"),
                                         (T("Sensor suhu, pH, metana NDIR, level, berat", "Temp, pH, NDIR methane, level, weight"), "#E8912D"),
                                         ("ESP32-S3 · Wi-Fi + Bluetooth", "#E8604C")], 1))}
    </div>
  </div>

  <!-- 2. panel belakang: SDG + kontak (hijau tua) -->
  <div class="pn" style="background:linear-gradient(170deg,#0F6B40 0%,#0E7A6A 70%,#13906A 100%);color:#fff">
    {deco(P_DOTS, "inset:0;background-repeat:repeat;background-size:18px 18px")}
    {deco(blob('#A6EBC5', .16), "width:300px;height:300px;right:-120px;bottom:120px")}
    {deco(P_STRIPE, "left:0;right:0;top:0;height:140px;background-repeat:repeat;background-size:40px 40px")}
    <span class="chip">SDGs</span>
    <h2>{T("Mendukung", "Supporting")} <span style="color:var(--sun)">{T("4 tujuan global.", "4 global goals.")}</span></h2>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:9px">
    {''.join(f'<div style="background:{c};border-radius:14px;padding:10px;height:92px;box-shadow:0 8px 16px -8px rgba(0,0,0,.4);display:flex;flex-direction:column;gap:3px"><span style="font-size:30px;font-weight:800;line-height:1">{n}</span><span style="font-size:10.5px;font-weight:700;line-height:1.2">{lab}</span></div>' for n, lab, c in SDGS)}
    </div>
    <div style="background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);border-radius:14px;padding:10px 12px">
      <p style="color:#E6F7EE">{T(f"Satu unit pada 1,5 kg/hari menghindari ±{num(NM['co2e'], 2)} t CO₂e per tahun* dan menggantikan ±{num(NM['lpg'], 1)} kg LPG per bulan*.",
                                   f"One unit at 1.5 kg/day avoids ±{num(NM['co2e'], 2)} t CO₂e per year* and replaces ±{num(NM['lpg'], 1)} kg of LPG per month*.")}</p></div>
    <div style="display:grid;gap:7px">
    {''.join(f'<div style="display:flex;gap:10px;align-items:center"><span class="n" style="width:30px;height:30px;font-size:15px;background:{c}">{ic}</span><div><b style="font-size:12.5px">{a}</b><div style="font-size:10px;color:#CFEFDD">{b}</div></div></div>'
             for ic, a, b, c in [("✓", T("Tanpa bau", "Odour-free"), T("proses tertutup rapat (anaerob)", "fully sealed anaerobic process"), "#FFD166"),
                                 ("✓", T("Hemat LPG", "Saves LPG"), T("gas masak dari sisa dapur", "cooking gas from kitchen scraps"), "#2D9CDB"),
                                 ("✓", T("Dipantau dari HP", "Monitored by phone"), T("notifikasi saat siap panen", "alerts when ready to harvest"), "#E8912D")])}
    </div>
    <div class="card" style="margin-top:auto;display:flex;gap:12px;align-items:center;padding:10px;color:var(--ink)">
      <img src="{A}qr.jpg" style="width:78px;border-radius:8px">
      <div><b style="font-size:14px">{T("Coba aplikasinya", "Try the app")}</b><br><span style="font-size:13px;font-weight:800;color:var(--green)">aruna-id.web.app</span>
      <div style="font-size:10px;color:var(--ink2);margin-top:2px">{T("Cerita 3D: /cerita", "3D story: /cerita")}</div></div></div>
    <p style="font-size:7.5px;color:rgba(255,255,255,.7)">{CREDIT}</p>
  </div>

  <!-- 3. sampul (teal -> emerald) -->
  <div class="pn" style="background:linear-gradient(160deg,#0E7A6A 0%,#158A52 55%,#1FA567 100%);color:#fff;padding-top:34px">
    {deco(blob('#CDEFD9', .9), "width:430px;height:430px;left:-20px;top:300px")}
    {deco(blob('#FFD166', 1), "width:120px;height:120px;right:-24px;top:70px")}
    {deco(P_LEAF, "inset:0;background-repeat:repeat;background-size:190px 190px")}
    <div style="display:flex;align-items:center;gap:9px"><span style="width:30px;height:30px;border-radius:9px;background:#fff;display:grid;place-items:center"><span style="width:11px;height:11px;border-radius:50%;background:var(--green)"></span></span>
      <b style="letter-spacing:.14em;font-size:15px">ARUNA</b></div>
    <h1 style="font-size:46px;margin-top:6px">{T("Sisa makanan", "Leftovers")}<br><span style="background:var(--sun);color:var(--deep);padding:0 8px;border-radius:10px;box-decoration-break:clone">{T("jadi energi.", "become energy.")}</span></h1>
    <p style="font-size:12.5px;color:#E6F7EE;max-width:290px">{T("Biodigester rumahan pintar: biogas untuk memasak, pupuk cair, dan kompos dari dapurmu sendiri.", "Smart home biodigester: cooking biogas, liquid fertilizer and compost from your own kitchen.")}</p>
    <img src="{A}cover.png" style="width:104%;margin:auto -6% 0 -2%;filter:drop-shadow(0 18px 20px rgba(0,0,0,.25))">
    <div style="display:flex;gap:6px;justify-content:center;margin-top:-6px">
      {''.join(f'<span style="background:{c};color:#fff;border-radius:99px;padding:6px 11px;font-size:10.5px;font-weight:800;box-shadow:0 6px 12px -6px rgba(0,0,0,.4)">{t}</span>' for t, c in [(T("Biogas", "Biogas"), "#2D9CDB"), (T("Pupuk cair", "Fertilizer"), "#E8912D"), (T("Kompos", "Compost"), "#E8604C")])}
    </div>
  </div>
</div>"""

inside = f"""
<div class="sheet">
  <!-- 1. masalah + solusi (krem-koral) -->
  <div class="pn" style="background:linear-gradient(170deg,#FFF6E5 0%,#FFE4D6 100%)">
    {deco(blob('#E8604C', .18), "width:280px;height:280px;right:-110px;top:-80px")}
    {deco(blob('#FFD166', .35), "width:220px;height:220px;left:-90px;bottom:-60px")}
    {deco(P_DOTS_G, "left:200px;top:300px;width:160px;height:120px;background-repeat:repeat;background-size:18px 18px")}
    <span class="chip" style="background:var(--coral);color:#fff">01 · {T("Masalah", "Problem")}</span>
    <h2>{T("Sisa makanan,", "Food waste,")} <span style="color:var(--coral)">{T("sampah terbesar.", "the biggest trash.")}</span></h2>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
    {''.join(f'<div style="background:{c};color:#fff;border-radius:14px;padding:13px 12px;box-shadow:0 10px 18px -10px {c}"><div style="font-size:23px;font-weight:800;letter-spacing:-.03em">{a}</div><div style="font-size:10.5px;line-height:1.3;margin-top:3px">{b}</div><div style="font-size:8px;opacity:.8;margin-top:4px;font-weight:700">{s}</div></div>' for a, b, s, c in STATS)}
    </div>
    <span class="chip" style="background:var(--green);color:#fff;margin-top:4px">02 · {T("Solusi", "Solution")}</span>
    <h2 style="font-size:23px">{T("Satu mesin,", "One machine,")} <span style="color:var(--green)">{T("tiga hasil.", "three outputs.")}</span></h2>
    {''.join(f'<div style="display:flex;align-items:center;gap:10px;background:#fff;border-left:7px solid {c};border-radius:12px;padding:13px 12px;box-shadow:0 8px 16px -12px rgba(0,0,0,.4)"><span style="font-size:13px;font-weight:800;flex:1">{a}</span><span style="font-size:15px;font-weight:800;color:{c}">{b}</span></div>'
             for a, b, c in [(T("Biogas memasak", "Cooking biogas"), f"±{num(NM['cook'])} {T('mnt', 'min')}*", "#2D9CDB"),
                             (T("Pupuk cair", "Liquid fertilizer"), T("encer 1:10", "dilute 1:10"), "#E8912D"),
                             (T("Kompos padat", "Solid compost"), T("laci bawah", "drawer"), "#E8604C")])}
    <div style="margin-top:auto;background:linear-gradient(135deg,#158A52,#0E7A6A);color:#fff;border-radius:14px;padding:12px 14px;box-shadow:0 10px 18px -10px #0F6B40">
      <b style="font-size:12.5px">{T("Kenapa dicerna, bukan dibuang?", "Why digest, not dump?")}</b>
      <p style="font-size:10.5px;color:#E6F7EE;margin-top:3px">{T("Di TPA, sisa makanan membusuk dan melepas metana ke udara. Di ARUNA, metana itu ditangkap menjadi api untuk memasak.", "In landfill, food waste rots and releases methane into the air. In ARUNA, that methane is captured as a cooking flame.")}</p></div>
  </div>

  <!-- 2. cara kerja (hijau tua, corak daun) -->
  <div class="pn" style="background:linear-gradient(165deg,#0F6B40 0%,#0E7A6A 60%,#13906A 100%);color:#fff">
    {deco(P_LEAF, "inset:0;background-repeat:repeat;background-size:190px 190px")}
    {deco(blob('#FFD166', .16), "width:300px;height:300px;left:40px;top:230px")}
    <span class="chip">03 · {T("Cara kerja", "How it works")}</span>
    <h2>{T("Di dalam", "Inside")} <span style="color:var(--sun)">ARUNA.</span></h2>
    <div style="padding:14px 0 6px">{xray(50, 9.5)}</div>
    <div style="background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);border-radius:14px;padding:10px 12px"><p style="color:#E6F7EE">{T("Sisa makanan dicacah lalu dicerna bakteri tanpa oksigen pada 30–38 °C. Sensor menjaga pH 6,8–7,5; jika pH turun, mesin berhenti menerima umpan dan memberi peringatan.", "Food waste is shredded and digested by bacteria without oxygen at 30–38 °C. Sensors keep pH at 6.8–7.5; if pH drops, feeding pauses and the app alerts you.")}</p></div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:auto">
    {''.join(f'<div style="background:{c};border-radius:14px;padding:9px;text-align:center;color:{tc};box-shadow:0 8px 16px -8px rgba(0,0,0,.4)"><b style="font-size:21px">{a}</b><div style="font-size:9.5px;font-weight:700">{b}</div></div>'
             for a, b, c, tc in [("5", T("sensor", "sensors"), "#FFD166", "#0F6B40"), ("±34", T("hari cerna", "days"), "#ffffff", "#0F6B40"),
                                 (f"{num(NM['bg'])} L", T("biogas/hari*", "biogas/day*"), "#E8912D", "#ffffff")])}
    </div>
  </div>

  <!-- 3. cara pakai (mint-biru, gelombang) -->
  <div class="pn" style="background:linear-gradient(170deg,#E3F6FB 0%,#CDEFD9 100%)">
    {deco(P_WAVE_G, "inset:0;background-size:cover")}
    {deco(blob('#2D9CDB', .16), "width:240px;height:240px;right:-90px;top:-60px")}
    <span class="chip" style="background:var(--sky);color:#fff">04 · {T("Cara pakai", "How to use")}</span>
    <h2>{T("5 langkah", "5 steps")} <span style="color:var(--sky)">{T("sehari-hari.", "every day.")}</span></h2>
    {''.join(f'<div class="card" style="display:grid;grid-template-columns:92px 1fr;gap:10px;align-items:center;padding:6px;border-radius:13px;border-left:6px solid {c}"><img src="{A}f{fr}.png" style="width:92px;height:68px;object-fit:cover;border-radius:9px"><div><b style="font-size:12.5px;display:flex;align-items:center;gap:6px"><span class="n" style="width:19px;height:19px;font-size:10px;background:{c}">{i+1}</span>{a}</b><p style="font-size:10px;color:var(--ink2);line-height:1.35">{b}</p></div></div>'
             for i, (fr, a, b, c) in enumerate(STEPS))}
    <img src="{A}kipas.png" style="width:100%;border-radius:12px;margin-top:auto;box-shadow:0 10px 20px -12px rgba(0,0,0,.4)">
  </div>
</div>"""

html = (f'<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">'
        f'<style>{CSS}</style></head><body>{outside}{inside}</body></html>')
src = os.path.join(HERE, f"brosur_{LANG}.html")
open(src, "w", encoding="utf-8").write(html)


async def export():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": BW, "height": BH * 2}, device_scale_factor=3)
        await pg.goto("file:///" + src.replace("\\", "/"))
        await pg.wait_for_timeout(1800)
        for i, side in enumerate(("luar", "dalam")):
            await pg.screenshot(path=os.path.join(HERE, f"ARUNA_brosur_{side}_{LANG}.png"), clip={"x": 0, "y": i * BH, "width": BW, "height": BH})
        await pg.pdf(path=os.path.join(HERE, f"ARUNA_brosur_A4_{LANG}.pdf"), width="297mm", height="210mm", print_background=True)
        await b.close()


asyncio.run(export())
print("[BROSUR] selesai", LANG)
