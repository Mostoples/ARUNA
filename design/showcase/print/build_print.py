"""
Poster A2 + brosur trifold A4 ARUNA (HTML -> Playwright -> PDF & PNG).

  python design/showcase/print/build_print.py [id|en]
Keluaran: design/showcase/print/ARUNA_poster_A2_<lang>.pdf/.png, ARUNA_brosur_A4_<lang>.pdf + PNG per sisi
"""
import asyncio
import json
import os
import sys

from PIL import Image

LANG = (sys.argv[1] if len(sys.argv) > 1 else "id").lower()
HERE = os.path.dirname(os.path.abspath(__file__))
SHOW = os.path.dirname(HERE)
DESIGN = os.path.dirname(SHOW)
ASSET = os.path.join(HERE, "_assets")
os.makedirs(ASSET, exist_ok=True)


def T(id_, en):
    return id_ if LANG == "id" else en


def prep(src, name, crop=None, max_w=1600):
    im = Image.open(src)
    if crop:
        w, h = im.size
        im = im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
    im.thumbnail((max_w, max_w * 2))
    ext = ".png" if im.mode == "RGBA" else ".jpg"
    out = os.path.join(ASSET, name + ext)
    (im.save(out) if ext == ".png" else im.convert("RGB").save(out, quality=90))
    return "_assets/" + name + ext


DA = os.path.join(SHOW, "deck", "assets")
IMG = {
    "cover": prep(os.path.join(DA, "cover.png"), "cover", max_w=1800),
    "xray": prep(os.path.join(DA, "hw_xray.png"), "xray", crop=(0.2, 0.1, 0.8, 0.95), max_w=1100),
    "kipas": prep(os.path.join(DESIGN, "app", "renders", "mockup_kipas.png"), "kipas", crop=(0.06, 0.18, 0.94, 0.82)),
    "mesin": prep(os.path.join(DESIGN, "app", "img", "mesin.png"), "mesin", max_w=900),
    "qr": prep(os.path.join(SHOW, "deck", "_cache", "qr.png"), "qr", max_w=400),
}
for fr in (96, 165, 250, 330, 430):
    IMG[f"f{fr}"] = prep(os.path.join(SHOW, "video", "frames", f"f_{fr:04d}.png"), f"f{fr}", crop=(0, 0.08, 1, 0.78), max_w=700)
def abstract_bg(w, h, seed, name, strength=1.0, dots=((.06, .70), (.82, .08))):
    """Latar putih abstrak: gumpalan warna lembut + garis kontur mengalir + pola titik."""
    import math
    import numpy as np
    from PIL import ImageDraw
    rng = np.random.default_rng(seed)
    S = 0.25  # gumpalan dihitung di resolusi rendah lalu di-upscale (lembut)
    sw, sh = int(w * S), int(h * S)
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    img = np.ones((sh, sw, 3), np.float32)
    BLOBS = [((21, 138, 82), .30), ((14, 122, 106), .26), ((140, 215, 170), .55), ((246, 196, 84), .30),
             ((21, 138, 82), .22), ((178, 228, 200), .55), ((45, 107, 216), .10)]
    for col, a in BLOBS:
        cx, cy = rng.uniform(-.1, 1.1) * sw, rng.uniform(-.05, 1.05) * sh
        r = rng.uniform(.18, .38) * max(sw, sh)
        g = np.exp(-(((xx - cx) / (r * rng.uniform(.7, 1.3))) ** 2 + ((yy - cy) / r) ** 2) * 1.6)
        a *= strength
        img = img * (1 - a * g[..., None]) + (np.array(col) / 255) * (a * g[..., None])
    base = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    unit = w / 1000
    for k in range(14):  # garis kontur mengalir
        amp, fr, ph = rng.uniform(25, 70) * unit, rng.uniform(1.2, 2.6), rng.uniform(0, 6.3)
        y0 = h * (0.08 + k * 0.065)
        pts = [(x, y0 + amp * math.sin(x / w * fr * 6.283 + ph) + amp * .35 * math.sin(x / w * 11 + ph * 2))
               for x in range(0, w + 8, 8)]
        d.line(pts, fill=(21, 138, 82, int(38 * strength)), width=max(1, int(1.6 * unit)))
    for ox, oy in dots:  # pola titik (posisi dipilih di area kosong)
        for i in range(9):
            for j in range(9):
                cx, cy, r = (ox + i * .012) * w, oy * h + j * .012 * w, 2.2 * unit
                d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(21, 138, 82, int(70 * strength)))
    base = base.convert("RGBA")
    base.alpha_composite(lay)
    out = os.path.join(ASSET, name + ".jpg")
    base.convert("RGB").save(out, quality=90)
    return "_assets/" + name + ".jpg"


IMG["bg_poster"] = abstract_bg(2100, 2970, 3, "bg_poster", dots=((.04, .70), (.37, .13)))
IMG["bg_out"] = abstract_bg(2246, 1588, 11, "bg_bro_out", dots=((.06, .72), (.37, .57)))
IMG["bg_in"] = abstract_bg(2246, 1588, 21, "bg_bro_in", strength=.8, dots=((.07, .90),))
PTS = json.load(open(os.path.join(DA, "hw_points.json")))
CROP = (0.2, 0.1, 0.8, 0.95)


def pt(k):
    u, v = PTS[k]
    return (u - CROP[0]) / (CROP[2] - CROP[0]) * 100, (v - CROP[1]) / (CROP[3] - CROP[1]) * 100


CSS = """
:root{--bg:#EEF5F1;--paper:#fff;--ink:#10201A;--ink2:#4A5B52;--muted:#86958D;--line:#DCE7E1;--green:#158A52;--teal:#0E7A6A;
--deep:#0F6B40;--soft:#E3F3EA;--amber:#B8741A;--blue:#2D6BD8;--red:#C8443A;--sans:"Plus Jakarta Sans","Segoe UI",sans-serif}
*{box-sizing:border-box;margin:0}
body{font-family:var(--sans);color:var(--ink);background:var(--bg);-webkit-print-color-adjust:exact;print-color-adjust:exact}
.card{background:rgba(255,255,255,.93);border-radius:var(--r,28px);box-shadow:0 2px 4px rgba(16,32,26,.05),0 26px 54px -26px rgba(15,107,64,.45);border:2px solid rgba(21,138,82,.12)}
.card.mint{background:linear-gradient(160deg,#EDF9F2,#D2EEDC);border-color:#BFE3CD}
.card.sky{background:linear-gradient(160deg,#EDF6FA,#D6ECEA);border-color:#C3E0DC}
.card.dark{background:linear-gradient(150deg,#0F6B40 0%,#0E7A6A 55%,#139067 100%);border-color:#0F6B40;color:#fff}
.card.dark .g,.pn.dark .g{color:#A6EBC5}
.card.dark p{color:rgba(255,255,255,.85)}
.card.dark .chip,.pn.dark .chip{background:#fff;color:var(--deep)}
.card.dark .callout,.pn.dark .callout{color:#fff}
.card.dark .dot,.pn.dark .dot{background:#A6EBC5;box-shadow:0 0 0 calc(var(--d)*.45) rgba(166,235,197,.28)}
.row{background:rgba(255,255,255,.9);border-radius:18px;border:1.5px solid rgba(21,138,82,.12)}
.chip{align-self:flex-start;display:inline-flex;align-items:center;gap:.5em;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:#fff;background:var(--green);border-radius:99px;padding:.45em 1em;box-shadow:0 6px 14px -6px rgba(21,138,82,.6)}
.num{display:inline-grid;place-items:center;border-radius:50%;background:var(--green);color:#fff;font-weight:800}
h1,h2,h3{letter-spacing:-.035em;line-height:1.02}
.g{color:var(--green)}
.mark{display:inline-grid;place-items:center;border-radius:28%;background:var(--green)}
.mark::after{content:"";width:34%;height:34%;border-radius:50%;background:#fff}
.tag{display:inline-block;font-weight:700;color:var(--amber);background:#FBF0DF;border-radius:99px;padding:.35em .9em}
.sdg{color:#fff;border-radius:18px;padding:.6em .8em;font-weight:800}
.callout{position:absolute;display:flex;align-items:center;gap:.5em;white-space:nowrap}
.dot{position:absolute;width:var(--d);height:var(--d);margin:calc(var(--d)/-2) 0 0 calc(var(--d)/-2);border-radius:50%;background:var(--green);box-shadow:0 0 0 calc(var(--d)*.45) rgba(21,138,82,.18)}
"""
SDGS = [("7", T("Energi bersih", "Clean energy"), "#C89A08"), ("11", T("Kota berkelanjutan", "Sustainable cities"), "#E08010"),
        ("12", T("Konsumsi bertanggung jawab", "Responsible consumption"), "#A07426"), ("13", T("Aksi iklim", "Climate action"), "#3F7E44")]
STATS = [("±40%", T("sampah nasional berupa sisa makanan", "of national waste is food"), "SIPSN KLHK"),
         ("115–184 kg", T("makanan terbuang / orang / tahun", "food wasted / person / year"), "Bappenas, 2021"),
         ("Rp213–551 T", T("kerugian ekonomi per tahun", "economic loss per year"), "Bappenas, 2021"),
         ("1,7 Gt CO₂e", T("emisi susut & sisa pangan 2000–2019", "emissions from food loss & waste 2000–2019"), "Bappenas, 2021")]
STEPS = [(96, T("Masukkan", "Put in"), T("Buka tutup, tuang sisa makanan.", "Open the lid, tip the leftovers.")),
         (165, T("Cerna", "Digest"), T("Dicacah & diaduk otomatis, ±34 hari.", "Shredded & stirred automatically, ±34 days.")),
         (250, T("Pantau", "Monitor"), T("Status & notifikasi di HP.", "Status & alerts on your phone.")),
         (330, T("Pupuk cair", "Fertilize"), T("Encerkan 1:10, siram tanaman.", "Dilute 1:10, water the plants.")),
         (430, T("Masak", "Cook"), T("Api biru biogas, ±45 menit/hari*.", "Blue biogas flame, ±45 min/day*."))]
PARTS = [("pencacah", T("Pencacah dua poros", "Twin-shaft shredder"), "L"), ("loadcell", T("Load cell (berat)", "Load cell (weight)"), "L"),
         ("layar", T("Panel 7″ + ESP32-S3", "7″ panel + ESP32-S3"), "L"), ("suhu", T("Sensor suhu", "Temperature sensor"), "L"),
         ("keran", T("Keran pupuk cair", "Fertilizer tap"), "L"), ("kompos", T("Laci kompos", "Compost drawer"), "L"),
         ("level", T("Sensor level", "Level sensor"), "R"), ("gas", T("Sensor metana NDIR", "NDIR methane sensor"), "R"),
         ("pengaduk", T("Pengaduk otomatis", "Auto stirrer"), "R"), ("ph", T("Probe pH", "pH probe"), "R"),
         ("gauge", T("Gauge + katup gas", "Gas gauge + valve"), "R")]
CREDIT = T("Karakter 3D: “Casual Male 3D Character – T-Pose” oleh sthaarpit (Sketchfab, CC-BY 4.0), di-rig ulang dengan Rigify. "
           "*Angka hasil adalah target desain prototipe.",
           "3D character: “Casual Male 3D Character – T-Pose” by sthaarpit (Sketchfab, CC-BY 4.0), re-rigged with Rigify. "
           "*Output figures are prototype design targets.")


def xray_block(width_pct, lab_size, line="#158A52"):
    """Gambar x-ray dengan titik + label kiri/kanan (posisi % dari bounding box gambar)."""
    left = sorted([p for p in PARTS if p[2] == "L"], key=lambda p: PTS[p[0]][1])
    right = sorted([p for p in PARTS if p[2] == "R"], key=lambda p: PTS[p[0]][1])
    svg, html = [], []
    for side, items in (("L", left), ("R", right)):
        for i, (k, lab, _) in enumerate(items):
            x, y = pt(k)
            ly = 6 + i * (88 / max(1, len(items) - 1))
            lx = -2 if side == "L" else 102
            svg.append(f'<line x1="{x}" y1="{y}" x2="{lx}" y2="{ly}" stroke="{line}" stroke-width=".25" vector-effect="non-scaling-stroke" style="stroke-width:2px"/>')
            html.append(f'<span class="dot" style="left:{x}%;top:{y}%;--d:{lab_size*0.75}px"></span>')
            anchor = "right:102%" if side == "L" else "left:102%"
            html.append(f'<div class="callout" style="{anchor};top:calc({ly}% - {lab_size*0.75}px);font-size:{lab_size}px;font-weight:700">'
                        f'{lab}</div>')
    return (f'<div style="position:relative;width:{width_pct}%;margin:0 auto"><img src="{IMG["xray"]}" style="width:100%;display:block">'
            f'<svg viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute;inset:0;width:100%;height:100%;overflow:visible">'
            + "".join(svg) + '</svg>' + "".join(html) + '</div>')


# ================================================================== POSTER A2 (2100 x 2970 px)
poster = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>{CSS}
body{{width:2100px;height:2970px;overflow:hidden;background:#fff url({IMG["bg_poster"]}) center/cover no-repeat}}
.wrap{{padding:80px 100px;display:grid;gap:40px}}
.sec h2{{font-size:60px;margin:14px 0 20px}}
.chip{{font-size:24px}}
p{{font-size:30px;line-height:1.45;color:var(--ink2)}}
</style></head><body><div class="wrap">
<header style="display:flex;justify-content:space-between;align-items:center">
  <div style="display:flex;align-items:center;gap:24px"><span class="mark" style="width:84px;height:84px"></span>
  <span style="font-size:46px;font-weight:800;letter-spacing:.12em">ARUNA</span></div>
  <div style="text-align:right;font-size:26px;color:var(--ink2)"><b class="tag" style="font-size:24px">[Nama Tim]</b><br>[Institusi] · 2026</div>
</header>

<section style="display:grid;grid-template-columns:1.3fr .85fr;align-items:center;gap:30px;margin-top:-20px">
  <div><span class="chip">{T("Biodigester rumahan pintar","Smart home biodigester")}</span>
  <h1 style="font-size:128px;margin:22px 0 20px">{T("Sisa makanan","Leftovers")}<br><span class="g">{T("jadi energi.","become energy.")}</span></h1>
  <p style="font-size:36px;max-width:820px">{T("ARUNA mencerna sisa makanan rumah tangga secara anaerob menjadi <b>biogas</b> untuk memasak, <b>pupuk cair</b>, dan <b>kompos</b>, dipantau sensor dan aplikasi.",
  "ARUNA anaerobically digests household leftovers into <b>biogas</b> for cooking, <b>liquid fertilizer</b> and <b>compost</b>, monitored by sensors and an app.")}</p>
  <div style="display:flex;gap:14px;margin-top:34px">{''.join(f'<span class="sdg" style="background:{c};font-size:26px">SDG {n}</span>' for n,_,c in SDGS)}</div></div>
  <img src="{IMG['cover']}" style="width:100%;max-height:900px;object-fit:contain">
</section>

<section class="sec"><span class="chip">01 · {T("Masalah","Problem")}</span>
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:28px;margin-top:26px">
  {''.join(f'<div class="card" style="padding:34px;background:linear-gradient(160deg,#fff 0%,{t} 100%);border-color:{c}33"><div style="font-size:58px;font-weight:800;letter-spacing:-.04em;color:{c}">{a}</div><p style="font-size:26px;margin-top:8px;color:var(--ink)">{b}</p><div style="font-size:19px;color:var(--ink2);margin-top:10px;font-weight:600">{s}</div></div>' for (a,b,s),c,t in zip(STATS,["#158A52","#0E7A6A","#B8741A","#C8443A"],["#D8F0E2","#D3EEEA","#FBE9CC","#F9DCD8"]))}
  </div></section>

<section style="display:grid;grid-template-columns:1.1fr 1fr;gap:44px">
  <div class="card dark sec" style="padding:46px 40px 50px"><span class="chip">02 · {T("Cara kerja","How it works")}</span>
    <h2>{T("Gravitasi bekerja,","Gravity works,")} <span class="g">{T("sensor mengawasi.","sensors watch.")}</span></h2>
    {xray_block(46, 25, "#A6EBC5")}
  </div>
  <div style="display:grid;gap:44px;align-content:start">
    <div class="card mint sec" style="padding:46px 44px"><span class="chip">03 · {T("Cara pakai","How to use")}</span>
      <h2>{T("5 langkah,","5 steps,")} <span class="g">{T("2 menit sehari.","2 minutes a day.")}</span></h2>
      <div style="display:grid;gap:14px">
      {''.join(f'<div class="row" style="display:grid;grid-template-columns:170px 1fr;gap:24px;align-items:center;padding:10px"><img src="{IMG[f"f{fr}"]}" style="width:170px;height:118px;object-fit:cover;border-radius:20px"><div><div style="display:flex;align-items:center;gap:16px"><span class="num" style="width:50px;height:50px;font-size:26px">{i+1}</span><b style="font-size:34px">{a}</b></div><p style="font-size:25px;margin-top:4px">{b}</p></div></div>' for i,(fr,a,b) in enumerate(STEPS))}
      </div></div>
  </div>
</section>

<section style="display:grid;grid-template-columns:1.25fr 1fr;gap:44px;align-items:stretch">
  <div class="card sky sec" style="padding:46px"><span class="chip">04 · {T("Aplikasi","App")}</span>
    <h2>{T("Semua terlihat","Everything visible")} <span class="g">{T("dari HP.","on your phone.")}</span></h2>
    <img src="{IMG['kipas']}" style="width:100%;border-radius:24px"></div>
  <div class="card sec" style="padding:46px;display:flex;flex-direction:column"><span class="chip">05 · {T("Dampak","Impact")}</span>
    <h2>{T("Satu dapur,","One kitchen,")} <span class="g">{T("tiga hasil.","three outputs.")}</span></h2>
    {''.join(f'<div style="display:flex;justify-content:space-between;align-items:center;background:{c}18;border:2px solid {c}30;border-radius:22px;padding:18px 26px;margin-bottom:14px"><span style="font-size:32px;font-weight:700">{a}</span><span style="font-size:50px;font-weight:800;color:{c}">{b}</span></div>' for a,b,c in [(T("Biogas memasak","Cooking gas"),"±45 mnt*","#2D6BD8"),(T("Pupuk cair / siklus","Liquid fertilizer / cycle"),"±1,4 L*","#158A52"),(T("Sisa makanan dialihkan","Waste diverted"),"1,5 kg/hari*","#B8741A")])}
    <div style="margin-top:auto;display:flex;align-items:center;gap:28px;padding-top:20px"><img src="{IMG['qr']}" style="width:190px;border-radius:16px;border:1px solid var(--line)">
    <div><b style="font-size:36px">{T("Coba aplikasinya","Try the app")}</b><br><span style="font-size:32px;font-weight:800;color:var(--green)">aruna-id.web.app</span></div></div>
  </div>
</section>
<footer style="font-size:19px;color:var(--muted)">{CREDIT}</footer>
</div></body></html>"""

# ================================================================== BROSUR TRIFOLD A4 lanskap (3508 x 2480 px @300dpi -> 1123x794 css px x3)
BW, BH = 1123, 794
PANEL = BW / 3
bro_css = CSS + f"""
@page{{size:297mm 210mm;margin:0}}
body{{width:{BW}px;background:#fff}}
.sheet.out{{background:#fff url({IMG["bg_out"]}) center/cover}}
.sheet.in{{background:#fff url({IMG["bg_in"]}) center/cover}}
.sheet{{width:{BW}px;height:{BH}px;display:grid;grid-template-columns:repeat(3,1fr);page-break-after:always;overflow:hidden;position:relative}}
.pn{{padding:34px 30px;position:relative;display:flex;flex-direction:column;gap:14px}}
.pn+.pn{{border-left:1.5px solid rgba(21,138,82,.18)}}
.pn.dark{{background:linear-gradient(160deg,#0F6B40,#0E7A6A 60%,#139067);color:#fff}}
.pn.mint{{background:linear-gradient(170deg,rgba(237,249,242,.9),rgba(210,238,220,.9))}}
.chip{{font-size:9.5px}}
h2{{font-size:27px}}
p,li{{font-size:11.5px;line-height:1.5;color:var(--ink2)}}
.card{{--r:16px}}
"""
outside = f"""
<div class="sheet out">
  <div class="pn mint">
    <span class="chip">{T("Spesifikasi","Specifications")}</span>
    <h2>{T("Kecil di dapur,","Small in the kitchen,")} <span class="g">{T("besar dampaknya.","big in impact.")}</span></h2>
    <img src="{IMG['mesin']}" style="height:270px;align-self:center">
    <div class="card" style="padding:14px 16px"><ul style="padding-left:16px;display:grid;gap:4px">
      <li>{T("Dimensi 44 × 44 × 112 cm, beroda","Size 44 × 44 × 112 cm, on wheels")}</li>
      <li>{T("Kapasitas 1,5 kg sisa makanan/hari (puncak 3 kg)","Capacity 1.5 kg of leftovers/day (peak 3 kg)")}</li>
      <li>{T("ESP32-S3, Wi-Fi + Bluetooth","ESP32-S3, Wi-Fi + Bluetooth")}</li>
      <li>{T("Sensor suhu, pH, metana, level, berat","Temperature, pH, methane, level, weight sensors")}</li>
      <li>{T("Daya ±38 W","Power ±38 W")}</li></ul></div>
  </div>
  <div class="pn">
    <span class="chip">SDGs</span>
    <h2>{T("Mendukung","Supporting")} <span class="g">{T("4 tujuan global.","4 global goals.")}</span></h2>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
    {''.join(f'<div class="sdg" style="background:{c};height:96px;font-size:11px;display:flex;flex-direction:column;gap:2px"><span style="font-size:30px;line-height:1">{n}</span>{lab}</div>' for n,lab,c in SDGS)}
    </div>
    <p>{T("Sisa makanan tidak lagi berakhir di TPA sebagai metana, tetapi menjadi energi memasak dan pupuk untuk kebun rumah.",
          "Leftovers no longer end in landfill as methane; they become cooking energy and fertilizer for the home garden.")}</p>
    <div style="margin-top:auto;display:flex;gap:14px;align-items:center"><img src="{IMG['qr']}" style="width:86px;border-radius:10px;border:1px solid var(--line)">
      <div><b style="font-size:15px">{T("Coba aplikasinya","Try the app")}</b><br><span style="font-size:14px;font-weight:800;color:var(--green)">aruna-id.web.app</span></div></div>
    <p style="font-size:8px;color:var(--muted)">{CREDIT}</p>
  </div>
  <div class="pn" style="padding-top:40px">
    <div style="display:flex;align-items:center;gap:10px"><span class="mark" style="width:30px;height:30px"></span><b style="letter-spacing:.12em;font-size:15px">ARUNA</b></div>
    <h1 style="font-size:46px;margin-top:10px">{T("Sisa makanan","Leftovers")}<br><span class="g">{T("jadi energi.","become energy.")}</span></h1>
    <p style="font-size:12.5px">{T("Biodigester rumahan pintar: biogas, pupuk cair, dan kompos dari dapurmu sendiri.","Smart home biodigester: biogas, liquid fertilizer and compost from your own kitchen.")}</p>
    <img src="{IMG['cover']}" style="width:118%;margin:auto -14% -20px -4%">
  </div>
</div>"""
inside = f"""
<div class="sheet in">
  <div class="pn">
    <span class="chip">01 · {T("Masalah","Problem")}</span>
    <h2>{T("Sisa makanan,","Food waste,")} <span class="g">{T("sampah terbesar.","the biggest trash.")}</span></h2>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
    {''.join(f'<div class="card" style="padding:12px;background:linear-gradient(160deg,#fff,{t});border-color:{c}33"><div style="font-size:19px;font-weight:800;color:{c}">{a}</div><p style="font-size:10px;color:var(--ink)">{b}</p><div style="font-size:8px;color:var(--ink2)">{s}</div></div>' for (a,b,s),c,t in zip(STATS,["#158A52","#0E7A6A","#B8741A","#C8443A"],["#D8F0E2","#D3EEEA","#FBE9CC","#F9DCD8"]))}
    </div>
    <span class="chip" style="margin-top:6px">02 · {T("Solusi","Solution")}</span>
    <h2 style="font-size:23px">{T("Satu mesin,","One machine,")} <span class="g">{T("tiga hasil.","three outputs.")}</span></h2>
    {''.join(f'<div class="card" style="padding:10px 14px;display:flex;justify-content:space-between;align-items:center;background:{c}18;border-color:{c}35"><b style="font-size:13px">{a}</b><b style="font-size:17px;color:{c}">{b}</b></div>' for a,b,c in [(T("Biogas memasak","Cooking gas"),"±45 mnt*","#2D6BD8"),(T("Pupuk cair","Liquid fertilizer"),"±1,4 L*","#158A52"),(T("Kompos","Compost"),T("laci","drawer"),"#B8741A")])}
  </div>
  <div class="pn dark">
    <span class="chip">03 · {T("Cara kerja","How it works")}</span>
    <h2>{T("Di dalam","Inside")} <span class="g">ARUNA.</span></h2>
    <div style="padding:10px 0 6px">{xray_block(44, 9.5, "#A6EBC5")}</div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:auto">
    {''.join(f'<div class="card" style="padding:10px;text-align:center"><b style="font-size:20px;color:var(--green)">{a}</b><p style="font-size:9.5px">{b}</p></div>' for a,b in [("5",T("sensor","sensors")),("±34",T("hari cerna","days to digest")),("1,5 kg",T("per hari","per day"))])}
    </div>
  </div>
  <div class="pn mint">
    <span class="chip">04 · {T("Cara pakai","How to use")}</span>
    <h2>{T("5 langkah","5 steps")} <span class="g">{T("sehari-hari.","every day.")}</span></h2>
    {''.join(f'<div class="row" style="display:grid;grid-template-columns:78px 1fr;gap:12px;align-items:center;padding:6px;border-radius:12px"><img src="{IMG[f"f{fr}"]}" style="width:78px;height:58px;object-fit:cover;border-radius:10px"><div><b style="font-size:13px"><span class="num" style="width:20px;height:20px;font-size:11px;margin-right:6px">{i+1}</span>{a}</b><p style="font-size:10.5px">{b}</p></div></div>' for i,(fr,a,b) in enumerate(STEPS))}
    <img src="{IMG['kipas']}" style="width:100%;border-radius:12px;margin-top:auto">
  </div>
</div>"""
brochure = (f'<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">'
            f'<style>{bro_css}</style></head><body>{outside}{inside}</body></html>')

open(os.path.join(HERE, f"poster_{LANG}.html"), "w", encoding="utf-8").write(poster)
open(os.path.join(HERE, f"brosur_{LANG}.html"), "w", encoding="utf-8").write(brochure)


async def export():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 2100, "height": 2970})
        await pg.goto("file:///" + os.path.join(HERE, f"poster_{LANG}.html").replace("\\", "/"))
        await pg.wait_for_timeout(1500)
        fit = """() => { const w = document.querySelector('.wrap'); let z = 1;
            for (let i = 0; i < 4; i++) { const h = w.scrollHeight * z; if (h <= 2950) break;
              z = z * 2950 / h; w.style.zoom = z; w.style.width = (2100 / z) + 'px'; }
            return [w.scrollHeight * z, z]; }"""
        hgt = await pg.evaluate(fit)
        print("[PRINT] tinggi konten poster:", hgt, "/ 2970")
        await pg.screenshot(path=os.path.join(HERE, f"ARUNA_poster_A2_{LANG}.png"))
        await pg.pdf(path=os.path.join(HERE, f"ARUNA_poster_A2_{LANG}.pdf"), width="420mm", height="594mm",
                     print_background=True, scale=0.756)   # 2100 px -> 420 mm
        pg2 = await b.new_page(viewport={"width": BW, "height": BH * 2}, device_scale_factor=3)
        await pg2.goto("file:///" + os.path.join(HERE, f"brosur_{LANG}.html").replace("\\", "/"))
        await pg2.wait_for_timeout(1500)
        for i, side in enumerate(("luar", "dalam")):
            await pg2.screenshot(path=os.path.join(HERE, f"ARUNA_brosur_{side}_{LANG}.png"),
                                 clip={"x": 0, "y": i * BH, "width": BW, "height": BH})
        await pg2.pdf(path=os.path.join(HERE, f"ARUNA_brosur_A4_{LANG}.pdf"), width="297mm", height="210mm", print_background=True)
        await b.close()


asyncio.run(export())
print("[PRINT] selesai", LANG)
