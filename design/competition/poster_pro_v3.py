# Poster A0 "Living Ledger" — di-exec oleh build_poster_a0.py (memakai IMG, NM, MX, C, CALC_ROWS, REFS, MEAS, RECS, cp, FIG, A, SHOW, CW, CH).
from PIL import Image as _I

VA = os.path.join(SHOW, "deck", "assets")


def crop_save(src, name, box, maxw=1500):
    im = _I.open(src)
    W_, H_ = im.size
    im = im.crop((int(box[0] * W_), int(box[1] * H_), int(box[2] * W_), int(box[3] * H_)))
    im.thumbnail((maxw, maxw * 2))
    im.save(os.path.join(A, name))
    return "_poster/" + name


XCROP = (0.2, 0.1, 0.8, 0.95)
IMG["xray_big"] = crop_save(os.path.join(VA, "hw_xray.png"), "xray_big.png", XCROP)
for fr, box in ((40, (0, .10, 1, .70)), (96, (0, .12, 1, .62)), (165, (0, .12, 1, .62)), (250, (0, .14, 1, .64)),
                (330, (0, .14, 1, .64)), (430, (0, .14, 1, .64))):
    IMG[f"f{fr}"] = crop_save(os.path.join(SHOW, "video", "frames", f"f_{fr:04d}.png"), f"pf{fr}.png", box, 800)
for k in ("pro_gompertz", "pro_sens", "pro_ghg"):
    IMG[k] = cp(os.path.join(FIG, k + ".png"), k + ".png")
PTS_ = json.load(open(os.path.join(VA, "hw_points.json")))


def ppt(k):
    u, v = PTS_[k]
    return (u - XCROP[0]) / (XCROP[2] - XCROP[0]) * 100, (v - XCROP[1]) / (XCROP[3] - XCROP[1]) * 100


PARTS = [("pencacah", "Twin-shaft shredder", "L"), ("loadcell", "Load cell · HX711", "L"), ("layar", "Panel · ESP32-S3", "L"),
         ("suhu", "Temperature · DS18B20", "L"), ("keran", "Liquid digestate tap", "L"), ("kompos", "Compost drawer", "L"),
         ("level", "Ultrasonic level", "R"), ("gas", "CH₄ · NDIR MH-440D", "R"), ("pengaduk", "Stirrer · 5 min / 2 h", "R"),
         ("ph", "pH probe", "R"), ("gauge", "Gas gauge + valve", "R")]


def xray_html(width_pct):
    sv, hs = [], []
    for side in ("L", "R"):
        items = sorted([q for q in PARTS if q[2] == side], key=lambda q: PTS_[q[0]][1])
        for i, (k, lab, _) in enumerate(items):
            x, y = ppt(k)
            ly = 4 + i * (92 / max(1, len(items) - 1))
            lx = -4 if side == "L" else 104
            sv.append(f'<polyline points="{x},{y} {lx + (2 if side == "L" else -2)},{ly} {lx},{ly}" fill="none" stroke="#E89B2D" style="stroke-width:1.6px" vector-effect="non-scaling-stroke"/>')
            hs.append(f'<span class="xd" style="left:{x}%;top:{y}%"></span>')
            anc = "right:105%;text-align:right" if side == "L" else "left:105%"
            hs.append(f'<div class="xl" style="{anc};top:{ly}%">{lab}</div>')
    return (f'<div class="xray" style="width:{width_pct}px"><img src="{IMG["xray_big"]}">'
            f'<svg viewBox="0 0 100 100" preserveAspectRatio="none">' + "".join(sv) + "</svg>" + "".join(hs) + "</div>")


SDG = [("7", "#C89A08"), ("11", "#E08010"), ("12", "#A07426"), ("13", "#3F7E44")]
FONT = "_poster/fonts/"
IMG["logo_isif"] = cp(os.path.join(FIG, "logo_isif.png"), "logo_isif.png")
IMG["logo_iysa"] = cp(os.path.join(FIG, "logo_iysa.png"), "logo_iysa.png")

CSS = """
@page{size:841mm 1189mm;margin:0}
@font-face{font-family:"ISerif";src:url(FONTInstrumentSerif-Regular.ttf)}
@font-face{font-family:"ISerif";font-style:italic;src:url(FONTInstrumentSerif-Italic.ttf)}
@font-face{font-family:"ISans";src:url(FONTInstrumentSans-Regular.ttf)}
@font-face{font-family:"ISans";font-weight:700;src:url(FONTInstrumentSans-Bold.ttf)}
@font-face{font-family:"GMono";src:url(FONTGeistMono-Regular.ttf)}
@font-face{font-family:"GMono";font-weight:700;src:url(FONTGeistMono-Bold.ttf)}
:root{--forest:#0C3B2E;--forest2:#124A3A;--paper:#F6F2E9;--ink:#16241E;--ink2:#34413A;--mute:#5F6C64;--rule:#CFC8B6;
--saff:#E89B2D;--sage:#8FB9A0;--serif:"ISerif",Georgia,serif;--sans:"ISans","Segoe UI",sans-serif;--mono:"GMono",Consolas,monospace}
*{box-sizing:border-box;margin:0;padding:0}
html{height:CHpx;overflow:hidden}
body{width:CWpx;height:CHpx;overflow:hidden;background:var(--paper);color:var(--ink);font-family:var(--sans);-webkit-print-color-adjust:exact;print-color-adjust:exact}
.wrap{display:flex;flex-direction:column}
.idx{font-family:var(--mono);font-size:30px;letter-spacing:.12em;color:var(--saff);font-weight:700}
.lab{font-family:var(--mono);font-size:22px;letter-spacing:.1em;text-transform:uppercase;color:var(--mute)}
.sh{display:flex;align-items:baseline;gap:24px;padding-bottom:18px;border-bottom:3px solid var(--ink);margin-bottom:34px}
.sh h2{font-family:var(--serif);font-weight:400;font-size:104px;line-height:1;letter-spacing:-.01em}
.dark .sh{border-color:rgba(246,242,233,.55)} .dark .sh h2{color:var(--paper)}
p{font-size:33px;line-height:1.38;color:var(--ink2)}
.ph{background:#F4E2B8;color:#6A4A10;padding:0 8px;border-radius:4px;font-weight:700}
/* header */
.band{background:var(--forest);color:var(--paper);padding:64px 96px 70px;display:grid;grid-template-columns:560px 1fr 560px;gap:56px;align-items:center;position:relative}
.band::after{content:"";position:absolute;left:96px;right:96px;bottom:0;height:12px;background:linear-gradient(90deg,var(--saff) 0 22%,var(--sage) 22% 100%)}
.logo{height:300px;background:#fff;border-radius:22px;display:grid;place-items:center;padding:26px 30px;box-shadow:0 20px 40px -20px rgba(0,0,0,.6)}
.logo img{max-width:100%;max-height:100%;object-fit:contain}
.ttl{text-align:center}
.ttl .country{display:inline-flex;align-items:center;gap:18px;font-family:var(--mono);font-size:30px;letter-spacing:.3em;color:rgba(246,242,233,.9)}
.flag{width:78px;height:52px;display:inline-block;background:linear-gradient(#E8281F 50%,#fff 50%)}
.ttl h1{font-family:var(--serif);font-weight:400;font-size:132px;line-height:.96;letter-spacing:-.015em;margin:24px 0 18px}
.ttl h1 em{color:var(--saff)}
.ttl .sub{font-size:36px;color:rgba(246,242,233,.88);line-height:1.3}
.ttl .auth{margin-top:20px;font-family:var(--mono);font-size:24px;letter-spacing:.06em}
/* rows */
.row{display:grid;gap:84px;padding:84px 96px 0;position:relative}
.big{display:flex;align-items:flex-end;gap:28px}
.big b{font-family:var(--serif);font-weight:400;font-size:300px;line-height:.78;color:var(--forest);letter-spacing:-.03em}
.big b sup{font-size:90px;vertical-align:top;color:var(--saff)}
.big > span{font-size:44px;line-height:1.22;color:var(--ink);padding-bottom:20px}
.stats3{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);margin:30px 0 34px}
.stats3 div{padding:22px 22px 24px 0}
.stats3 div+div{padding-left:24px;border-left:1px solid var(--rule)}
.stats3 b{display:block;font-family:var(--serif);font-weight:400;font-size:110px;line-height:1;color:var(--forest)}
.stats3 span{display:block;font-size:31px;line-height:1.28;color:var(--ink2);margin-top:10px}
.stats3 i{display:block;font-style:normal;margin-top:10px}
ol.num{list-style:none;counter-reset:g;display:grid;gap:18px;margin-top:16px}
ol.num li{counter-increment:g;font-size:38px;line-height:1.32;color:var(--ink2);padding-left:70px;position:relative}
ol.num li::before{content:counter(g,decimal-leading-zero);position:absolute;left:0;top:4px;font-family:var(--mono);font-size:26px;color:var(--saff);font-weight:700}
ol.num b{color:var(--forest)}
.path{display:grid;grid-template-columns:repeat(4,1fr);margin:40px 0 0;position:relative}
.path::before{content:"";position:absolute;left:30px;right:30px;top:29px;height:3px;background:var(--forest)}
.path div{position:relative;padding-right:12px}
.path i{display:block;width:60px;height:60px;border-radius:50%;background:var(--paper);border:3px solid var(--forest);margin-bottom:16px;position:relative}
.path div:last-child i{background:var(--forest)}
.path div:last-child i::after{content:"";position:absolute;inset:15px;border-radius:50%;background:var(--saff)}
.path b{font-size:35px;display:block} .path span{font-family:var(--mono);font-size:24px;color:var(--mute)}
.hyp{margin-top:40px;padding-top:26px;border-top:1px solid var(--rule)}
.hyp p{font-family:var(--serif);font-size:58px;line-height:1.16;color:var(--forest);margin-top:10px}
.hyp p em{color:var(--saff);font-style:normal}
.sdg{display:flex;gap:12px;margin-top:34px;align-items:center}
.sdg span.sq{width:84px;height:84px;display:grid;place-items:center;color:#fff;font-family:var(--mono);font-weight:700;font-size:32px}
/* method */
.dark{background:var(--forest);color:var(--paper);padding:56px 60px 64px;position:relative}
.dark p{color:rgba(246,242,233,.85)}
.rail{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid rgba(246,242,233,.3)}
.rail div{padding:24px 20px 6px 0}
.rail div+div{padding-left:22px;border-left:1px solid rgba(246,242,233,.18)}
.rail .lab{color:var(--saff)} .rail b{display:block;font-family:var(--serif);font-weight:400;font-size:62px;margin:6px 0 8px}
.rail span{font-size:26px;line-height:1.3;color:rgba(246,242,233,.82);display:block}
.mgrid{display:grid;grid-template-columns:1.25fr .75fr;gap:40px;margin-top:40px;align-items:start}
.xray{position:relative;margin:30px auto 0}
.xray img{width:100%;display:block;filter:drop-shadow(0 30px 40px rgba(0,0,0,.45))}
.xray svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
.xd{position:absolute;width:20px;height:20px;margin:-10px 0 0 -10px;border-radius:50%;background:var(--saff);box-shadow:0 0 0 8px rgba(232,155,45,.28)}
.xl{position:absolute;transform:translateY(-50%);white-space:nowrap;font-family:var(--mono);font-size:25px;color:var(--paper)}
.dark .lab{color:rgba(246,242,233,.65)}
.flow div{padding:18px 0 18px 40px;border-left:3px solid rgba(246,242,233,.35);position:relative}
.flow div::before{content:"";position:absolute;left:-11px;top:28px;width:19px;height:19px;border-radius:50%;background:var(--paper)}
.flow div.out::before{background:var(--saff)}
.flow b{display:block;font-size:35px} .flow span{font-family:var(--mono);font-size:22px;color:rgba(246,242,233,.75)}
.eqs{display:grid;grid-template-columns:1fr 1fr;margin-top:44px;border-top:1px solid rgba(246,242,233,.3)}
.eqs div{padding:24px 24px 4px 0} .eqs div+div{padding-left:26px;border-left:1px solid rgba(246,242,233,.18)}
.eqs code{display:block;font-family:var(--serif);font-style:italic;font-size:46px;line-height:1.22;margin-top:8px}
.exp{display:grid;grid-template-columns:repeat(3,1fr);margin-top:38px;background:var(--forest2)}
.exp div{padding:26px 26px 30px} .exp div+div{border-left:1px solid rgba(246,242,233,.12)}
.exp .lab{color:var(--saff)}
.exp ul{list-style:none;margin-top:12px;display:grid;gap:8px}
.exp li{font-size:28px;line-height:1.3;color:rgba(246,242,233,.9)}
/* data */
.kpis{display:grid;grid-template-columns:repeat(4,1fr);border-bottom:1px solid var(--rule);margin-bottom:40px}
.kpis div{padding:0 20px 28px 0} .kpis div+div{padding-left:24px;border-left:1px solid var(--rule)}
.kpis b{display:block;font-family:var(--serif);font-weight:400;font-size:150px;line-height:.92;color:var(--forest)}
.kpis b small{font-size:52px} .kpis div:first-child b{color:var(--saff)}
.kpis span{display:block;font-size:32px;color:var(--ink2);margin-top:12px}
.charts{display:grid;grid-template-columns:1fr 1fr;gap:44px}
figure{margin:0}
figure > img{width:100%;height:620px;object-fit:contain;display:block}
figcaption{display:flex;gap:16px;align-items:baseline;border-top:2px solid var(--ink);padding-top:14px;margin-bottom:10px}
figcaption b{font-size:38px}
.disc{display:grid;grid-template-columns:1fr 1fr;gap:44px;margin-top:40px}
.disc p{font-size:37px}
.disc p b{color:var(--forest)}
table.t{width:100%;border-collapse:collapse;font-size:31px}
table.t th{font-family:var(--mono);font-size:20px;letter-spacing:.08em;text-transform:uppercase;color:var(--mute);font-weight:400;text-align:left;padding:0 10px 12px;border-bottom:3px solid var(--ink)}
table.t td{padding:11px 10px;border-bottom:1px solid var(--rule);color:var(--ink2)}
table.t td:not(:first-child),table.t th:not(:first-child){text-align:right;font-family:var(--mono);font-size:28px}
/* conclusion with breakout hero */
.concl{position:relative}
.hero{position:absolute;right:-150px;top:-380px;width:1150px;height:1560px;pointer-events:none;z-index:2}
.hero::before{content:"";position:absolute;left:120px;top:330px;width:980px;height:980px;border-radius:50%;background:radial-gradient(circle at 50% 45%,#E2EDE2 0%,#D7E5D8 55%,rgba(215,229,216,0) 71%)}
.hero img{position:absolute;right:0;bottom:0;height:1560px;width:auto;filter:drop-shadow(0 40px 50px rgba(12,59,46,.35))}
.concl .content{position:relative;z-index:3;padding-top:1160px}
.novelty{font-family:var(--serif);font-size:54px;line-height:1.12;color:var(--forest);border-left:8px solid var(--saff);padding-left:30px;margin:0 0 34px}
.qr{display:flex;gap:28px;align-items:center;margin-top:40px;padding-top:30px;border-top:1px solid var(--rule)}
.qr img{width:190px}
.qr b{font-family:var(--serif);font-weight:400;font-size:60px;color:var(--forest);display:block}
/* strip */
.strip{display:grid;grid-template-columns:repeat(5,1fr);gap:24px}
.strip img{width:100%;height:360px;object-fit:cover;display:block}
.strip figcaption{border:0;padding:14px 0 0}
.strip figcaption b{font-size:36px}
.recs{display:grid;grid-template-columns:repeat(5,1fr);gap:24px;margin-top:24px}
.recs div{border-top:5px solid var(--forest);padding-top:16px} .recs div:first-child{border-color:var(--saff)}
.recs p{font-size:33px;line-height:1.3}
.refs{columns:4;column-gap:46px;list-style:none;counter-reset:r}
.refs li{counter-increment:r;font-size:21px;line-height:1.36;color:var(--ink2);break-inside:avoid;margin-bottom:6px;padding-left:38px;position:relative;font-family:var(--serif)}
.refs li::before{content:counter(r);position:absolute;left:0;font-family:var(--mono);font-size:17px;color:var(--mute)}
.foot{display:flex;justify-content:space-between;padding:26px 96px 52px;font-family:var(--mono);font-size:18px;letter-spacing:.06em;color:var(--mute);text-transform:uppercase}
""".replace("CHpx", f"{CH}px").replace("CWpx", f"{CW}px").replace("FONT", FONT)

stats3 = "".join(f'<div><b>{a}</b><span>{b}</span><i class="lab">{s}</i></div>' for a, b, s in
                 [("14.7 Mt", "household food waste per year in Indonesia", "UNEP 2024"),
                  ("≈ 40 %", "of municipal solid waste is food", "SIPSN 2023"),
                  ("1.7 Gt", "CO₂e from food loss &amp; waste, 2000–19", "Bappenas 2021")])
path = "".join(f'<div><i></i><b>{t_}</b><span>{d_}</span></div>' for t_, d_ in
               [("Hydrolysis", "→ monomers"), ("Acidogenesis", "→ VFA, H₂"), ("Acetogenesis", "→ acetate"), ("Methanogenesis", "→ CH₄ + CO₂")])
rail = "".join(f'<div><span class="lab">{n}</span><b>{t_}</b><span>{d_}</span></div>' for n, t_, d_ in
               [("Stage 1", "Define", "waste audit · user needs"), ("Stage 2", "Design", "CAD · sizing · IoT"),
                ("Stage 3", "Develop", "prototype · lab tests"), ("Stage 4", "Disseminate", "field test · SUS")])
flow = "".join(f'<div class="{c}"><b>{t_}</b><span>{d_}</span></div>' for t_, d_, c in
               [("Food waste", f"{NM['fw']:.1f} kg/d · TS 25 %", ""), ("Weigh + shred", "particles < 10 mm", ""),
                ("Digest 100 L", f"OLR {NM['olr']:.1f} · HRT {NM['hrt']:.0f} d", ""),
                ("Biogas", f"{NM['bg']:.0f} L/d", "out"), ("Liquid digestate", "fertilizer 1 : 10", "out"), ("Solid digestate", "compost", "out")])
eqs = "".join(f'<div><span class="lab">{t_}</span><code>{e_}</code></div>' for t_, e_ in
              [("Loading &amp; retention", "OLR = F·TS·(VS/TS) / V<sub>w</sub> · HRT = V<sub>w</sub>/Q"),
               ("Kinetics · modified Gompertz", "M(t) = P·exp{−exp[(R<sub>m</sub>e/P)(λ−t)+1]}")])
exp = "".join(f'<div><span class="lab">{t_}</span><ul>{"".join(f"<li>{x}</li>" for x in xs)}</ul></div>' for t_, xs in
              [("Experiments", ["BMP · VDI 4630 · 37 °C", "OLR 2.0 / 3.4 / 4.5 × 3", 'Field · <span class="ph">[n]</span> homes × 30 d']),
               ("Measurements", ["TS / VS · APHA 2540", "pH · FOS/TAC < 0.4", "CH₄ % (NDIR) · L/d"]),
               ("Analysis", ["Gompertz fit · R²", "ANOVA + Tukey", "SUS (Brooke 1996)"])])
kpis = "".join(f'<div><b>{a}<small>{u}</small></b><span>{b}</span></div>' for a, u, b in
               [(f"{NM['bg']:.0f}", " L", "biogas / day"), (f"{NM['cook']:.0f}", " min", "cooking / day"),
                (f"{NM['lpg']:.1f}", " kg", "LPG saved / month"), (f"{NM['co2e']:.2f}", " t", "CO₂e avoided / year")])
MEAS2 = [(a, b, c) for a, b, c, _ in MEAS]
strip = "".join(f'<figure><img src="{IMG[f"f{fr}"]}"><figcaption><span class="idx">{i + 1:02d}</span><b>{lab}</b></figcaption></figure>'
                for i, (fr, lab) in enumerate([(96, "Feed"), (165, "Digest"), (250, "Monitor"), (330, "Fertilize"), (430, "Cook")]))
RECS2 = ["Fit P, R<sub>m</sub>, λ from BMP and confirm the OLR limit.", "Co-digest garden waste to reach C/N 20–30.",
         "On-device AI to reject bones, oil and plastic.", "Insulate or solar-heat for highlands < 25 °C.", "Pilot in MBG school kitchens with MRV."]
recs = "".join(f'<div><span class="idx">R{i + 1}</span><p>{t_}</p></div>' for i, t_ in enumerate(RECS2))
refs = "".join(f"<li>{r}</li>" for r in REFS)
sdg = "".join(f'<span class="sq" style="background:{c}">{n}</span>' for n, c in SDG)

html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="wrap">
<header class="band">
  <div class="logo"><img src="{IMG['logo_isif']}" alt="ISIF"></div>
  <div class="ttl">
    <div class="country"><span class="flag"></span>INDONESIA</div>
    <h1>ARUNA: a kinetically sized, <em>sensor-guided</em> home digester</h1>
    <div class="sub">IoT-enabled household anaerobic digester converting food waste into biogas and biofertilizer</div>
    <div class="auth"><span class="ph">[Author 1]</span> · <span class="ph">[Author 2]</span> · <span class="ph">[Author 3]</span> — <span class="ph">[Supervisor]</span> · <span class="ph">[Institution]</span></div>
  </div>
  <div class="logo"><img src="{IMG['logo_iysa']}" alt="IYSA"></div>
</header>

<section class="row" style="grid-template-columns:.9fr 1.1fr">
  <div style="padding-top:56px">
    <div class="sh"><span class="idx">01</span><h2>Introduction</h2></div>
    <div class="big"><b>53<sup>kg</sup></b><span>of food wasted per person, per year, in Indonesian homes<br><span class="lab">UNEP Food Waste Index 2024</span></span></div>
    <div class="stats3">{stats3}</div>
    <span class="lab">Research gap</span>
    <ol class="num">
      <li>Home digesters are bulky, manure-fed and <b>unmonitored</b>.</li>
      <li>Food waste acidifies fast: VFA build-up halts methane.</li>
      <li>Cheap MQ sensors read ppm leaks, <b>not biogas CH₄ %</b>.</li></ol>
    <div class="path">{path}</div>
    <div class="hyp"><span class="lab">Hypothesis</span>
      <p>A shredded, stirred 100 L digester at OLR ≤ <em>{NM['olr']:.1f}</em> reaches <em>≥ 50 % CH₄</em>, and sensor guidance keeps usability at SUS ≥ 68.</p></div>
    <div class="sdg"><span class="lab" style="margin-right:10px">SDG</span>{sdg}</div>
  </div>

  <div class="dark">
    <div class="sh"><span class="idx">02</span><h2>Method</h2><span class="lab" style="margin-left:auto">R&amp;D · 4D model</span></div>
    <div class="rail">{rail}</div>
    <div class="mgrid">
      <div><span class="lab">X-ray of the digital twin</span>{xray_html(560)}</div>
      <div><span class="lab">Daily mass balance</span><div class="flow" style="margin-top:24px">{flow}</div></div>
    </div>
    <div class="eqs">{eqs}</div>
    <div class="exp">{exp}</div>
  </div>
</section>

<section class="row" style="grid-template-columns:1.18fr .82fr">
  <div>
    <div class="sh"><span class="idx">03</span><h2>Data &amp; Discussion</h2><span class="lab" style="margin-left:auto">design predictions</span></div>
    <div class="kpis">{kpis}</div>
    <div class="charts">
      <figure><figcaption><span class="idx">A</span><b>Methane kinetics</b></figcaption><img src="{IMG['pro_gompertz']}"></figure>
      <figure><figcaption><span class="idx">B</span><b>Load sensitivity</b></figcaption><img src="{IMG['pro_sens']}"></figure>
    </div>
    <div class="disc">
      <p><b>Biodegradability ≈ {C['biodeg']:.0f} %:</b> BMP 390 vs Buswell 643 mL CH₄/g VS, within the food-waste range.</p>
      <p><b>Stability limit:</b> peak OLR {MX['olr']:.1f} (HRT {MX['hrt']:.0f} d) risks VFA build-up; pH interlock pauses feeding.</p>
    </div>
    <figure style="margin-top:40px"><figcaption><span class="idx">C</span><b>Measured results</b><span class="lab" style="margin-left:auto">after testing</span></figcaption>{table(["Indicator", "Target", "Measured"], MEAS2, ["50%", "22%", "28%"])}</figure>
  </div>

  <div class="concl">
    <div class="hero"><img src="{IMG['cover']}" alt="ARUNA digester with user"></div>
    <div class="content">
      <div class="sh"><span class="idx">04</span><h2>Conclusion</h2></div>
      <div class="novelty">Shred, stir, digest and measure in a 0.19 m² footprint.</div>
      <ol class="num">
        <li><b>{NM['bg']:.0f} L biogas/day</b> from 1.5 kg food waste.</li>
        <li><b>{NM['cook']:.0f} min</b> cooking/day · <b>{NM['co2e']:.2f} t CO₂e</b>/year avoided.</li>
        <li><span class="ph">[Confirm H1–H2 with data]</span></li></ol>
      <div class="qr"><img src="{IMG['qr']}"><div><span class="lab">Live app</span><b>aruna-id.web.app</b></div></div>
    </div>
  </div>
</section>

<section class="row" style="grid-template-columns:1fr">
  <div>
    <div class="sh"><span class="idx">05</span><h2>Recommendation</h2></div>
    <div class="strip">{strip}</div>
    <div class="recs">{recs}</div>
  </div>
</section>

<section class="row" style="grid-template-columns:1fr;padding-top:70px">
  <div><div class="sh" style="margin-bottom:22px"><span class="idx">06</span><h2 style="font-size:64px">References</h2></div><ol class="refs">{refs}</ol></div>
</section>
<div class="foot"><span>Highlighted fields are placeholders · values are design predictions</span><span>3D character: sthaarpit · Sketchfab · CC-BY 4.0</span></div>
</div></body></html>"""
