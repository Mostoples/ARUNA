"""
Brosur trifold A4 lanskap ARUNA — gaya "Living Ledger" (sama dengan poster A0 lomba).

  python design/showcase/print/build_print.py id      # menyiapkan _assets (sekali)
  python design/showcase/print/build_brosur_pro.py [id|en]
Keluaran: ARUNA_brosur_A4_<lang>.pdf (hal. 1 luar, hal. 2 dalam) + ARUNA_brosur_luar/dalam_<lang>.png
"""
import asyncio
import json
import os
import sys

LANG = (sys.argv[1] if len(sys.argv) > 1 else "id").lower()
HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.dirname(os.path.dirname(HERE))
NM = json.load(open(os.path.join(DESIGN, "competition", "calc.json")))["nominal"]
PTS = json.load(open(os.path.join(DESIGN, "showcase", "deck", "assets", "hw_points.json")))
CROP = (0.2, 0.1, 0.8, 0.95)
BW, BH = 1123, 794
A = "_assets/"


def T(id_, en):
    return id_ if LANG == "id" else en


def n(v, d=0):
    s = f"{v:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".") if LANG == "id" else s


PARTS = [("pencacah", T("Pencacah", "Shredder"), "L"), ("loadcell", T("Timbangan", "Load cell"), "L"),
         ("layar", "ESP32-S3", "L"), ("suhu", T("Suhu", "Temp."), "L"), ("keran", T("Keran pupuk", "Tap"), "L"),
         ("kompos", T("Laci kompos", "Drawer"), "L"), ("level", T("Level", "Level"), "R"), ("gas", "CH₄ NDIR", "R"),
         ("pengaduk", T("Pengaduk", "Stirrer"), "R"), ("ph", "pH", "R"), ("gauge", T("Katup gas", "Gas valve"), "R")]


def xray(width):
    sv, hs = [], []
    for side in ("L", "R"):
        items = sorted([q for q in PARTS if q[2] == side], key=lambda q: PTS[q[0]][1])
        for i, (k, lab, _) in enumerate(items):
            u, v = PTS[k]
            x = (u - CROP[0]) / (CROP[2] - CROP[0]) * 100
            y = (v - CROP[1]) / (CROP[3] - CROP[1]) * 100
            ly = 4 + i * (92 / max(1, len(items) - 1))
            lx = -6 if side == "L" else 106
            sv.append(f'<polyline points="{x},{y} {lx + (3 if side == "L" else -3)},{ly} {lx},{ly}" fill="none" stroke="#E89B2D" style="stroke-width:1.2px" vector-effect="non-scaling-stroke"/>')
            hs.append(f'<span class="xd" style="left:{x}%;top:{y}%"></span>')
            anc = "right:107%;text-align:right" if side == "L" else "left:107%"
            hs.append(f'<div class="xl" style="{anc};top:{ly}%">{lab}</div>')
    return (f'<div class="xray" style="width:{width}px"><img src="{A}xray.png"><svg viewBox="0 0 100 100" preserveAspectRatio="none">'
            + "".join(sv) + "</svg>" + "".join(hs) + "</div>")


F = A + "fonts/"
CSS = f"""
@page{{size:297mm 210mm;margin:0}}
@font-face{{font-family:ISerif;src:url({F}InstrumentSerif-Regular.ttf)}}
@font-face{{font-family:ISerif;font-style:italic;src:url({F}InstrumentSerif-Italic.ttf)}}
@font-face{{font-family:ISans;src:url({F}InstrumentSans-Regular.ttf)}}
@font-face{{font-family:ISans;font-weight:700;src:url({F}InstrumentSans-Bold.ttf)}}
@font-face{{font-family:GMono;src:url({F}GeistMono-Regular.ttf)}}
@font-face{{font-family:GMono;font-weight:700;src:url({F}GeistMono-Bold.ttf)}}
:root{{--forest:#0C3B2E;--forest2:#124A3A;--paper:#F6F2E9;--ink:#16241E;--ink2:#34413A;--mute:#5F6C64;--rule:#CFC8B6;--saff:#E89B2D;--sage:#8FB9A0;
--serif:ISerif,Georgia,serif;--sans:ISans,"Segoe UI",sans-serif;--mono:GMono,Consolas,monospace}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:{BW}px;font-family:var(--sans);color:var(--ink);-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.sheet{{width:{BW}px;height:{BH}px;display:grid;grid-template-columns:repeat(3,1fr);page-break-after:always;overflow:hidden;background:var(--paper)}}
.pn{{position:relative;overflow:hidden;padding:30px 26px 26px;display:flex;flex-direction:column}}
.pn+.pn{{border-left:1px dashed rgba(22,36,30,.18)}}
.dark{{background:var(--forest);color:var(--paper)}}
.idx{{font-family:var(--mono);font-size:11px;letter-spacing:.14em;color:var(--saff);font-weight:700}}
.lab{{font-family:var(--mono);font-size:9.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--mute)}}
.dark .lab{{color:rgba(246,242,233,.6)}}
.sh{{display:flex;align-items:baseline;gap:10px;padding-bottom:8px;border-bottom:1.5px solid var(--ink);margin-bottom:14px}}
.dark .sh{{border-color:rgba(246,242,233,.5)}}
h2{{font-family:var(--serif);font-weight:400;font-size:38px;line-height:1;letter-spacing:-.01em}}
p{{font-size:12.5px;line-height:1.45;color:var(--ink2)}}
.dark p{{color:rgba(246,242,233,.85)}}
em{{font-style:normal;color:var(--saff)}}
ol.num{{list-style:none;counter-reset:c;display:grid;gap:9px}}
ol.num li{{counter-increment:c;font-size:13px;line-height:1.38;padding-left:30px;position:relative;color:var(--ink2)}}
ol.num li::before{{content:counter(c,decimal-leading-zero);position:absolute;left:0;top:1px;font-family:var(--mono);font-size:11px;font-weight:700;color:var(--saff)}}
.dark ol.num li{{color:rgba(246,242,233,.88)}}
ol.num b{{color:var(--forest)}} .dark ol.num b{{color:var(--paper)}}
/* sampul */
.cover h1{{font-family:var(--serif);font-weight:400;font-size:74px;line-height:.9;letter-spacing:-.02em;margin-top:18px}}
.cover h1 em{{font-style:italic}}
.cover .hero{{position:absolute;left:-30px;right:-60px;bottom:58px;height:430px;display:grid;place-items:end center}}
.cover .hero::before{{content:"";position:absolute;width:380px;height:380px;border-radius:50%;bottom:10px;left:40px;background:radial-gradient(circle,#1E5A47 0%,rgba(30,90,71,0) 70%)}}
.cover .hero img{{position:relative;height:430px;filter:drop-shadow(0 22px 26px rgba(0,0,0,.45))}}
.cover .bar{{position:absolute;left:0;right:0;bottom:0;height:58px;background:var(--saff);color:var(--forest);display:flex;align-items:center;gap:14px;padding:0 26px;font-family:var(--mono);font-size:11px;letter-spacing:.12em;font-weight:700;text-transform:uppercase}}
.brand{{display:flex;align-items:center;gap:9px;font-family:var(--mono);font-size:12px;letter-spacing:.2em;font-weight:700}}
.brand i{{width:22px;height:22px;border-radius:6px;background:var(--saff);display:grid;place-items:center}}
.brand i::after{{content:"";width:8px;height:8px;border-radius:50%;background:var(--forest)}}
/* x-ray */
.xray{{position:relative;margin:26px auto 0}}
.xray img{{width:100%;display:block;filter:drop-shadow(0 16px 20px rgba(0,0,0,.45))}}
.xray svg{{position:absolute;inset:0;width:100%;height:100%;overflow:visible}}
.xd{{position:absolute;width:9px;height:9px;margin:-4.5px 0 0 -4.5px;border-radius:50%;background:var(--saff);box-shadow:0 0 0 3px rgba(232,155,45,.3)}}
.xl{{position:absolute;transform:translateY(-50%);white-space:nowrap;font-family:var(--mono);font-size:10.5px;color:var(--paper)}}
/* angka */
.big{{font-family:var(--serif);font-weight:400;font-size:150px;line-height:.78;color:var(--forest);letter-spacing:-.03em}}
.big sup{{font-size:46px;vertical-align:top;color:var(--saff)}}
.stats{{display:grid;grid-template-columns:1fr 1fr;border-top:1px solid var(--rule);margin-top:16px}}
.stats div{{padding:12px 10px 12px 0;border-bottom:1px solid var(--rule)}}
.stats div:nth-child(even){{padding-left:12px;border-left:1px solid var(--rule)}}
.stats b{{display:block;font-family:var(--serif);font-weight:400;font-size:40px;line-height:1;color:var(--forest)}}
.stats span{{display:block;font-size:11px;line-height:1.3;margin-top:5px;color:var(--ink2)}}
.kpi{{display:grid;grid-template-columns:1fr 1fr;gap:0;margin:14px 0}}
.kpi div{{padding:10px 10px 12px 0;border-top:1px solid rgba(246,242,233,.25)}}
.kpi div:nth-child(even){{padding-left:12px;border-left:1px solid rgba(246,242,233,.18)}}
.kpi b{{display:block;font-family:var(--serif);font-weight:400;font-size:52px;line-height:.95;color:var(--paper)}}
.kpi b small{{font-size:22px}} .kpi div:first-child b{{color:var(--saff)}}
.kpi span{{font-size:11px;color:rgba(246,242,233,.78)}}
.out{{display:grid;gap:0;margin-top:auto}}
.out div{{display:flex;align-items:baseline;gap:10px;padding:10px 0;border-top:1px solid rgba(246,242,233,.25)}}
.out div b{{font-family:var(--serif);font-weight:400;font-size:26px}}
.out div span{{margin-left:auto;font-family:var(--mono);font-size:10.5px;color:rgba(246,242,233,.75)}}
/* langkah */
.steps{{display:grid;gap:12px}}
.step{{display:grid;grid-template-columns:128px 1fr;gap:12px;align-items:center}}
.step img{{width:128px;height:92px;object-fit:cover;display:block}}
.step b{{font-size:15px;display:block}} .step span{{font-size:11.5px;color:var(--ink2);line-height:1.35}}
/* belakang */
.spec{{display:grid;gap:0;margin-top:6px}}
.spec div{{display:flex;justify-content:space-between;gap:10px;padding:7px 0;border-bottom:1px solid var(--rule);font-size:12px}}
.spec div span:last-child{{font-family:var(--mono);font-size:11px;text-align:right}}
.sdg{{display:flex;gap:6px;margin-top:12px}}
.sdg span{{width:34px;height:34px;display:grid;place-items:center;color:#fff;font-family:var(--mono);font-weight:700;font-size:13px}}
.logos{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:auto;padding-top:12px;border-top:1px solid var(--rule)}}
.logos div{{height:62px;display:grid;place-items:center;background:#fff;border:1px solid var(--rule)}}
.logos img{{max-width:86%;max-height:46px}}
.qr{{display:flex;gap:12px;align-items:center;margin-top:12px}}
.qr img{{width:74px}}
.qr b{{font-family:var(--serif);font-weight:400;font-size:24px;color:var(--forest);display:block}}
.foot{{font-family:var(--mono);font-size:7.5px;letter-spacing:.05em;color:var(--mute);margin-top:8px;line-height:1.4}}
"""

SDG = "".join(f'<span style="background:{c}">{x}</span>' for x, c in (("7", "#C89A08"), ("11", "#E08010"), ("12", "#A07426"), ("13", "#3F7E44")))
STEPS = [(96, T("Masukkan", "Feed"), T("Buka tutup, tuang sisa makanan.", "Open the lid, add leftovers.")),
         (165, T("Cerna", "Digest"), T("Dicacah & diaduk otomatis, ±34 hari.", "Shredded & stirred, ±34 days.")),
         (250, T("Pantau", "Monitor"), T("Status & notifikasi di HP.", "Status & alerts on your phone.")),
         (330, T("Pupuk", "Fertilize"), T("Encerkan 1 : 10, siram tanaman.", "Dilute 1 : 10, water plants.")),
         (430, T("Masak", "Cook"), T(f"Api biru, ±{n(NM['cook'])} menit/hari*.", f"Blue flame, ±{n(NM['cook'])} min/day*."))]
steps = "".join(f'<div class="step"><img src="{A}f{fr}.png"><div><span class="idx">{i + 1:02d}</span><b>{a}</b><span>{b}</span></div></div>'
                for i, (fr, a, b) in enumerate(STEPS))

outside = f"""
<div class="sheet">
  <div class="pn dark">
    <div class="sh"><span class="idx">03</span><h2>{T("Di dalam", "Inside")} <em>ARUNA</em></h2></div>
    <p>{T("Sisa makanan dicacah, lalu dicerna bakteri tanpa oksigen pada 30–38 °C. Sensor menjaga prosesnya tetap stabil.",
          "Food waste is shredded, then digested by bacteria without oxygen at 30–38 °C. Sensors keep the process stable.")}</p>
    {xray(196)}
    <ol class="num" style="margin-top:auto">
      <li>{T("pH turun di bawah 6,5? Umpan otomatis dihentikan.", "pH below 6.5? Feeding pauses automatically.")}</li>
      <li>{T("Bocor gas > 5.000 ppm? Katup menutup.", "Gas leak > 5,000 ppm? Valve closes.")}</li></ol>
  </div>

  <div class="pn">
    <div class="sh"><span class="idx">06</span><h2>{T("Spesifikasi", "Specifications")}</h2></div>
    <div class="spec">
      <div><span>{T("Ukuran", "Size")}</span><span>44 × 44 × 112 cm</span></div>
      <div><span>{T("Kapasitas", "Capacity")}</span><span>{T("1,5 kg/hari (puncak 3)", "1.5 kg/day (peak 3)")}</span></div>
      <div><span>{T("Volume kerja", "Working volume")}</span><span>100 L</span></div>
      <div><span>{T("Waktu cerna", "Retention time")}</span><span>{T("±34 hari", "±34 days")}</span></div>
      <div><span>{T("Sensor", "Sensors")}</span><span>T · pH · CH₄ · level · {T("berat", "mass")}</span></div>
      <div><span>{T("Kontrol", "Controller")}</span><span>ESP32-S3 · Wi-Fi · BLE</span></div>
    </div>
    <div class="lab" style="margin-top:14px">{T("Mendukung SDG", "Supports SDGs")} 7.1 · 11.6 · 12.3 · 13.2</div>
    <div class="sdg">{SDG}</div>
    <div class="qr"><img src="{A}qr.jpg"><div><span class="lab">{T("Coba aplikasinya", "Try the app")}</span><b>aruna-id.web.app</b></div></div>
    <img src="{A}kipas.png" style="width:100%;margin-top:14px;border:1px solid var(--rule)">
    <div class="logos"><div><img src="{A}logo_isif.png"></div><div><img src="{A}logo_iysa.png"></div></div>
    <div class="foot">{T("*Prediksi perhitungan desain pada 1,5 kg/hari. Karakter 3D: sthaarpit, Sketchfab, CC-BY 4.0.",
                        "*Design prediction at 1.5 kg/day. 3D character: sthaarpit, Sketchfab, CC-BY 4.0.")}</div>
  </div>

  <div class="pn dark cover">
    <div class="brand"><i></i>ARUNA</div>
    <h1>{T("Sisa makanan,", "Leftovers,")}<br><em>{T("jadi energi.", "made energy.")}</em></h1>
    <p style="margin-top:12px;font-size:13.5px">{T("Biodigester rumahan pintar: biogas untuk memasak, pupuk cair, dan kompos dari dapurmu sendiri.",
                                                   "A smart home biodigester: cooking gas, liquid fertilizer and compost from your own kitchen.")}</p>
    <div class="hero"><img src="{A}cover.png"></div>
    <div class="bar"><span>Biogas</span>·<span>{T("Pupuk cair", "Fertilizer")}</span>·<span>{T("Kompos", "Compost")}</span></div>
  </div>
</div>"""

inside = f"""
<div class="sheet">
  <div class="pn">
    <div class="sh"><span class="idx">01</span><h2>{T("Masalah", "The problem")}</h2></div>
    <div class="big">53<sup>kg</sup></div>
    <p style="margin-top:10px;font-size:14px;color:var(--ink)">{T("sisa makanan dibuang per orang setiap tahun di rumah tangga Indonesia.",
                                                                 "of food is thrown away per person each year in Indonesian homes.")}</p>
    <span class="lab" style="margin-top:4px">UNEP Food Waste Index 2024</span>
    <div class="stats">
      <div><b>{n(14.7, 1)} Mt</b><span>{T("sisa makanan rumah tangga / tahun", "household food waste / year")}</span></div>
      <div><b>≈ 40 %</b><span>{T("sampah kota berupa sisa makanan", "of municipal waste is food")}</span></div>
      <div><b>{n(1.7, 1)} Gt</b><span>{T("CO₂e dari susut & sisa pangan", "CO₂e from food loss & waste")}</span></div>
      <div><b>CH<sub style="font-size:.5em">4</sub></b><span>{T("dilepas saat membusuk di TPA", "released as it rots in landfill")}</span></div>
    </div>
    <p style="margin-top:auto;font-family:var(--serif);font-size:21px;line-height:1.2;color:var(--forest)">{T("Di ARUNA, metana itu ditangkap dan menjadi <em>api untuk memasak</em>.",
                                                                                                          "In ARUNA, that methane is captured as <em>a cooking flame</em>.")}</p>
  </div>

  <div class="pn dark">
    <div class="sh"><span class="idx">02</span><h2>{T("Satu mesin,", "One machine,")} <em>{T("tiga hasil", "three outputs")}</em></h2></div>
    <p>{T("Dari 1,5 kg sisa makanan per hari, perhitungan desain memperkirakan:", "From 1.5 kg of food waste a day, the design calculation predicts:")}</p>
    <div class="kpi">
      <div><b>{n(NM['bg'])}<small> L</small></b><span>{T("biogas per hari", "biogas per day")}</span></div>
      <div><b>{n(NM['cook'])}<small> {T("mnt", "min")}</small></b><span>{T("memasak per hari", "cooking per day")}</span></div>
      <div><b>{n(NM['lpg'], 1)}<small> kg</small></b><span>{T("LPG dihemat / bulan", "LPG saved / month")}</span></div>
      <div><b>{n(NM['co2e'], 2)}<small> t</small></b><span>{T("CO₂e terhindar / tahun", "CO₂e avoided / year")}</span></div>
    </div>
    <img src="{A}mesin.png" style="height:250px;align-self:center;filter:drop-shadow(0 18px 22px rgba(0,0,0,.45))">
    <div class="out">
      <div><b>Biogas</b><span>{T("kompor dapur", "kitchen stove")}</span></div>
      <div><b>{T("Pupuk cair", "Liquid fertilizer")}</b><span>{T("encer 1 : 10", "dilute 1 : 10")}</span></div>
      <div><b>{T("Kompos", "Compost")}</b><span>{T("laci bawah", "bottom drawer")}</span></div>
    </div>
  </div>

  <div class="pn">
    <div class="sh"><span class="idx">04</span><h2>{T("Cara pakai", "How to use")}</h2></div>
    <div class="steps">{steps}</div>
    <p style="margin-top:auto;padding-top:12px;border-top:1px solid var(--rule)">{T("Cukup 2 menit sehari. Aplikasi ARUNA memberi tahu kapan pupuk dan kompos siap diambil.",
                                                                                  "Two minutes a day. The ARUNA app tells you when fertilizer and compost are ready.")}</p>
  </div>
</div>"""

src = os.path.join(HERE, f"brosur_{LANG}.html")
open(src, "w", encoding="utf-8").write(f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{outside}{inside}</body></html>')


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
