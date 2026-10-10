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

CSS = """
@page{size:841mm 1189mm;margin:0}
@font-face{font-family:"ISerif";src:url(FONTInstrumentSerif-Regular.ttf)}
@font-face{font-family:"ISerif";font-style:italic;src:url(FONTInstrumentSerif-Italic.ttf)}
@font-face{font-family:"ISans";src:url(FONTInstrumentSans-Regular.ttf)}
@font-face{font-family:"ISans";font-weight:700;src:url(FONTInstrumentSans-Bold.ttf)}
@font-face{font-family:"ISans";font-style:italic;src:url(FONTInstrumentSans-Italic.ttf)}
@font-face{font-family:"GMono";src:url(FONTGeistMono-Regular.ttf)}
@font-face{font-family:"GMono";font-weight:700;src:url(FONTGeistMono-Bold.ttf)}
:root{--forest:#0C3B2E;--forest2:#124A3A;--paper:#F6F2E9;--paper2:#EEE8DA;--ink:#16241E;--ink2:#3E4B44;--mute:#6E7B73;--rule:#CFC8B6;
--saff:#E89B2D;--sage:#8FB9A0;--teal:#1F7A6C;--serif:"ISerif",Georgia,serif;--sans:"ISans","Segoe UI",sans-serif;--mono:"GMono",Consolas,monospace}
*{box-sizing:border-box;margin:0;padding:0}
html{height:CHpx;overflow:hidden}
body{width:CWpx;height:CHpx;overflow:hidden;background:var(--paper);color:var(--ink);font-family:var(--sans);-webkit-print-color-adjust:exact;print-color-adjust:exact}
.wrap{display:flex;flex-direction:column}
.pad{padding:0 96px}
.mono{font-family:var(--mono);letter-spacing:.08em;text-transform:uppercase}
.idx{font-family:var(--mono);font-size:22px;letter-spacing:.14em;color:var(--saff);font-weight:700}
.sh{display:flex;align-items:baseline;gap:22px;padding-bottom:16px;border-bottom:2px solid var(--ink);margin-bottom:30px}
.sh h2{font-family:var(--serif);font-weight:400;font-size:76px;line-height:1;letter-spacing:-.01em}
.sh .note{margin-left:auto;font-family:var(--mono);font-size:18px;color:var(--mute);letter-spacing:.1em;text-transform:uppercase}
.dark .sh{border-color:rgba(246,242,233,.55)} .dark .sh h2{color:var(--paper)} .dark .sh .note{color:rgba(246,242,233,.6)}
p{font-size:27px;line-height:1.42;color:var(--ink2)}
.lab{font-family:var(--mono);font-size:17px;letter-spacing:.12em;text-transform:uppercase;color:var(--mute)}
.ph{background:#F4E2B8;color:#6A4A10;padding:0 6px;border-radius:3px;font-weight:700}
/* header */
.band{background:var(--forest);color:var(--paper);padding:70px 96px 64px;display:grid;grid-template-columns:300px 1fr 300px;gap:60px;align-items:center;position:relative}
.band::after{content:"";position:absolute;left:96px;right:96px;bottom:0;height:10px;background:linear-gradient(90deg,var(--saff) 0 22%,var(--sage) 22% 100%)}
.logo{height:300px;border:2px solid rgba(246,242,233,.4);display:grid;place-items:center;text-align:center;font-family:var(--mono);font-size:20px;letter-spacing:.16em;color:rgba(246,242,233,.65)}
.ttl{text-align:center}
.ttl .country{display:inline-flex;align-items:center;gap:16px;font-family:var(--mono);font-size:24px;letter-spacing:.3em;color:rgba(246,242,233,.85)}
.flag{width:66px;height:44px;display:inline-block;background:linear-gradient(#E8281F 50%,#fff 50%);box-shadow:0 0 0 1px rgba(255,255,255,.5)}
.ttl h1{font-family:var(--serif);font-weight:400;font-size:112px;line-height:.98;letter-spacing:-.015em;margin:26px 0 18px}
.ttl h1 em{color:var(--saff)}
.ttl .sub{font-size:31px;color:rgba(246,242,233,.85);max-width:1250px;margin:0 auto;line-height:1.35}
.ttl .auth{margin-top:22px;font-family:var(--mono);font-size:19px;letter-spacing:.08em;color:rgba(246,242,233,.75)}
/* rows */
.row{display:grid;gap:80px;padding:84px 96px 0}
.intro .big{display:flex;align-items:flex-end;gap:26px;margin-bottom:6px}
.intro .big b{font-family:var(--serif);font-weight:400;font-size:230px;line-height:.8;color:var(--forest);letter-spacing:-.03em}
.intro .big b sup{font-size:70px;vertical-align:top;color:var(--saff)}
.intro .big > span{font-size:30px;line-height:1.25;color:var(--ink);padding-bottom:16px;max-width:430px}
.stats3{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);margin:26px 0 30px}
.stats3 div{padding:20px 22px 22px 0}
.stats3 div+div{padding-left:22px;border-left:1px solid var(--rule)}
.stats3 b{display:block;font-family:var(--serif);font-weight:400;font-size:74px;line-height:1;color:var(--forest)}
.stats3 span{display:block;font-size:20px;line-height:1.3;color:var(--ink2);margin-top:8px}
.stats3 i{display:block;font-style:normal;margin-top:8px}
.photo{width:100%;display:block;object-fit:cover}
.gap{display:grid;grid-template-columns:1fr 1fr;gap:34px;margin-top:30px;align-items:start}
.gap ol{list-style:none;counter-reset:g;display:grid;gap:16px}
.gap li{counter-increment:g;font-size:25px;line-height:1.38;color:var(--ink2);padding-left:56px;position:relative}
.gap li::before{content:counter(g,decimal-leading-zero);position:absolute;left:0;top:2px;font-family:var(--mono);font-size:20px;color:var(--saff);font-weight:700}
.path{display:grid;grid-template-columns:repeat(4,1fr);margin:34px 0 0;position:relative}
.path::before{content:"";position:absolute;left:24px;right:24px;top:23px;height:2px;background:var(--forest)}
.path div{position:relative;padding-right:14px}
.path i{display:block;width:48px;height:48px;border-radius:50%;background:var(--paper);border:2px solid var(--forest);margin-bottom:14px;position:relative}
.path div:last-child i{background:var(--forest)}
.path div:last-child i::after{content:"";position:absolute;inset:12px;border-radius:50%;background:var(--saff)}
.path b{font-size:24px;display:block;color:var(--ink)} .path span{font-family:var(--mono);font-size:16px;color:var(--mute)}
.hyp{margin-top:38px;padding:26px 0 0;border-top:1px solid var(--rule)}
.hyp p{font-family:var(--serif);font-size:38px;line-height:1.22;color:var(--forest)}
.hyp p em{color:var(--saff);font-style:normal}
.sdg{display:flex;gap:10px;margin-top:26px;align-items:center}
.sdg span{width:64px;height:64px;display:grid;place-items:center;color:#fff;font-family:var(--mono);font-weight:700;font-size:24px}
/* method */
.dark{background:var(--forest);color:var(--paper);padding:56px 60px 60px;margin-top:-6px}
.dark p{color:rgba(246,242,233,.82)}
.rail{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid rgba(246,242,233,.3)}
.rail div{padding:22px 22px 6px 0}
.rail div+div{padding-left:22px;border-left:1px solid rgba(246,242,233,.18)}
.rail .lab{color:var(--saff)} .rail b{display:block;font-family:var(--serif);font-weight:400;font-size:46px;margin:6px 0 8px;color:var(--paper)}
.rail span{font-size:20px;line-height:1.35;color:rgba(246,242,233,.78);display:block}
.mgrid{display:grid;grid-template-columns:1.32fr .68fr;gap:56px;margin-top:44px;align-items:start}
.xray{position:relative;margin:34px auto 10px}
.xray img{width:100%;display:block}
.xray svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
.xd{position:absolute;width:14px;height:14px;margin:-7px 0 0 -7px;border-radius:50%;background:var(--saff);box-shadow:0 0 0 6px rgba(232,155,45,.25)}
.xl{position:absolute;transform:translateY(-50%);white-space:nowrap;font-family:var(--mono);font-size:19px;letter-spacing:.04em;color:var(--paper)}
.flow{display:grid;gap:0;margin-top:30px}
.flow div{padding:16px 0 16px 34px;border-left:2px solid rgba(246,242,233,.35);position:relative}
.flow div::before{content:"";position:absolute;left:-8px;top:24px;width:14px;height:14px;border-radius:50%;background:var(--paper)}
.flow div.out::before{background:var(--saff)}
.flow b{display:block;font-size:27px;color:var(--paper)} .flow span{font-family:var(--mono);font-size:17px;color:rgba(246,242,233,.7);letter-spacing:.03em}
.eqs{display:grid;grid-template-columns:repeat(3,1fr);gap:0;margin-top:46px;border-top:1px solid rgba(246,242,233,.3)}
.eqs div{padding:22px 24px 4px 0}
.eqs div+div{padding-left:24px;border-left:1px solid rgba(246,242,233,.18)}
.eqs .lab{color:rgba(246,242,233,.6)}
.eqs code{display:block;font-family:var(--serif);font-style:italic;font-size:33px;line-height:1.25;margin-top:8px;color:var(--paper)}
.exp{display:grid;grid-template-columns:repeat(3,1fr);margin-top:40px;background:var(--forest2)}
.exp div{padding:24px 26px}
.exp div+div{border-left:1px solid rgba(246,242,233,.12)}
.exp .lab{color:var(--saff)}
.exp ul{list-style:none;margin-top:10px;display:grid;gap:6px}
.exp li{font-size:21px;line-height:1.35;color:rgba(246,242,233,.86)}
/* data */
.kpis{display:grid;grid-template-columns:repeat(4,1fr);border-bottom:1px solid var(--rule);margin-bottom:34px}
.kpis div{padding:0 22px 26px 0}
.kpis div+div{padding-left:24px;border-left:1px solid var(--rule)}
.kpis b{display:block;font-family:var(--serif);font-weight:400;font-size:96px;line-height:.95;color:var(--forest)}
.kpis b small{font-size:40px}
.kpis div:first-child b{color:var(--saff)}
.kpis span{display:block;font-size:20px;color:var(--ink2);margin-top:10px}
.charts{display:grid;grid-template-columns:1fr 1fr;gap:44px}
figure{margin:0}
figure img{width:100%;height:520px;object-fit:contain;display:block}
figcaption{display:flex;gap:14px;align-items:baseline;border-top:1px solid var(--ink);padding-top:12px;margin-bottom:10px}
figcaption b{font-size:25px} figcaption .lab{margin-left:auto}
.dgrid{display:grid;grid-template-columns:1.25fr .75fr;gap:44px;margin-top:40px;align-items:start}
table.t{width:100%;border-collapse:collapse;font-size:21px}
table.t th{font-family:var(--mono);font-size:15px;letter-spacing:.1em;text-transform:uppercase;color:var(--mute);font-weight:400;text-align:left;padding:0 10px 10px;border-bottom:2px solid var(--ink)}
table.t td{padding:9px 10px;border-bottom:1px solid var(--rule);color:var(--ink2)}
table.t td:not(:first-child),table.t th:not(:first-child){text-align:right;font-family:var(--mono);font-size:19px}
table.t.calc td:nth-child(3){color:var(--forest);font-weight:700;background:rgba(143,185,160,.22)}
.disc{display:grid;grid-template-columns:1fr 1fr;gap:44px;margin-top:40px}
.disc p b{color:var(--forest)}
/* conclusion */
.concl{display:flex;flex-direction:column}
.hero{position:relative;height:1010px;display:grid;place-items:center;margin-bottom:10px}
.hero::before{content:"";position:absolute;width:800px;height:800px;border-radius:50%;background:radial-gradient(circle at 50% 45%,#E3EDE3 0%,#DCE7DC 55%,rgba(220,231,220,0) 70%)}
.hero img{position:relative;height:1010px;width:auto}
.novelty{font-family:var(--serif);font-size:42px;line-height:1.18;color:var(--forest);border-left:6px solid var(--saff);padding-left:26px;margin:16px 0 30px}
.cl{list-style:none;display:grid;gap:18px;counter-reset:c}
.cl li{counter-increment:c;font-size:25px;line-height:1.38;color:var(--ink2);padding-left:58px;position:relative}
.cl li::before{content:counter(c,decimal-leading-zero);position:absolute;left:0;top:2px;font-family:var(--mono);font-size:20px;font-weight:700;color:var(--saff)}
.cl b{color:var(--forest)}
.qr{display:flex;gap:24px;align-items:center;margin-top:auto;padding-top:28px;border-top:1px solid var(--rule)}
.qr img{width:150px}
.qr b{font-family:var(--serif);font-weight:400;font-size:44px;color:var(--forest);display:block}
/* strip */
.strip{display:grid;grid-template-columns:repeat(5,1fr);gap:22px}
.strip figure img{width:100%;height:300px;object-fit:cover}
.strip figcaption{border:0;padding:12px 0 0}
.strip figcaption b{font-size:22px}
.recs{display:grid;grid-template-columns:repeat(5,1fr);gap:22px;margin-top:26px}
.recs div{border-top:4px solid var(--forest);padding-top:14px}
.recs div:first-child{border-color:var(--saff)}
.recs p{font-size:22px;line-height:1.36}
.refs{columns:4;column-gap:44px;list-style:none;counter-reset:r}
.refs li{counter-increment:r;font-size:15.5px;line-height:1.38;color:var(--ink2);break-inside:avoid;margin-bottom:6px;padding-left:34px;position:relative;font-family:var(--serif)}
.refs li::before{content:counter(r);position:absolute;left:0;font-family:var(--mono);font-size:14px;color:var(--mute)}
.foot{display:flex;justify-content:space-between;padding:26px 96px 56px;font-family:var(--mono);font-size:15px;letter-spacing:.08em;color:var(--mute);text-transform:uppercase}
""".replace("CHpx", f"{CH}px").replace("CWpx", f"{CW}px").replace("FONT", FONT)

stats3 = "".join(f'<div><b>{a}</b><span>{b}</span><i class="lab">{s}</i></div>' for a, b, s in
                 [("14.7 Mt", "household food waste per year, Indonesia", "UNEP 2024"),
                  ("≈ 40 %", "of municipal solid waste is food", "SIPSN KLHK 2023"),
                  ("1.7 Gt", "CO₂e from food loss &amp; waste, 2000–19", "Bappenas 2021")])
path = "".join(f'<div><i></i><b>{t_}</b><span>{d_}</span></div>' for t_, d_ in
               [("Hydrolysis", "polymers → monomers"), ("Acidogenesis", "→ VFA · H₂ · CO₂"), ("Acetogenesis", "→ acetate"), ("Methanogenesis", "→ CH₄ + CO₂")])
rail = "".join(f'<div><span class="lab">{n}</span><b>{t_}</b><span>{d_}</span></div>' for n, t_, d_ in
               [("Stage 1", "Define", "food-waste audit · user needs · requirements"), ("Stage 2", "Design", "3D CAD · sizing · IoT &amp; app architecture"),
                ("Stage 3", "Develop", "prototype · lab digestion · expert validation"), ("Stage 4", "Disseminate", "household field test · SUS · revision")])
flow = "".join(f'<div class="{c}"><b>{t_}</b><span>{d_}</span></div>' for t_, d_, c in
               [("Food waste in", f"{NM['fw']:.1f} kg/d · TS 25 % · VS/TS 90 %", ""), ("Weigh + shred", "load cell · particles < 10 mm", ""),
                ("Anaerobic digestion", f"100 L · OLR {NM['olr']:.1f} kg VS/m³·d · HRT {NM['hrt']:.0f} d", ""),
                ("Biogas", f"{NM['bg']:.0f} L/d · ≈{NM['cook']:.0f} min cooking", "out"), ("Liquid digestate", "fertilizer · dilute 1 : 10", "out"),
                ("Solid digestate", "compost drawer", "out")])
eqs = "".join(f'<div><span class="lab">{t_}</span><code>{e_}</code></div>' for t_, e_ in
              [("Loading &amp; retention", "OLR = F·TS·(VS/TS) / V<sub>w</sub><br>HRT = V<sub>w</sub> / Q"),
               ("Kinetics · Gompertz", "M(t) = P·exp{−exp[(R<sub>m</sub>e/P)(λ−t)+1]}"),
               ("Energy &amp; cooking", "E = V<sub>CH₄</sub>·35.8 MJ/m³<br>t<sub>cook</sub> = V<sub>biogas</sub> / q<sub>stove</sub>")])
exp = "".join(f'<div><span class="lab">{t_}</span><ul>{"".join(f"<li>{x}</li>" for x in xs)}</ul></div>' for t_, xs in
              [("Experiments", ["BMP · VDI 4630 · 37 °C · triplicate", "OLR 2.0 / 3.4 / 4.5 × 3 replicates", 'Field · <span class="ph">[n]</span> homes × 30 d']),
               ("Measurements", ["TS / VS · APHA 2540 G", "pH · FOS/TAC &lt; 0.4", "CH₄ % (NDIR) · biogas L/d"]),
               ("Analysis", ["Gompertz fit · R², RMSE", "ANOVA + Tukey · α = 0.05", "Usability · SUS (Brooke 1996)"])])
kpis = "".join(f'<div><b>{a}<small>{u}</small></b><span>{b}</span></div>' for a, u, b in
               [(f"{NM['bg']:.0f}", " L", "biogas per day"), (f"{NM['cook']:.0f}", " min", "cooking per day"),
                (f"{NM['lpg']:.1f}", " kg", "LPG-equivalent per month"), (f"{NM['co2e']:.2f}", " t", "CO₂e avoided per year")])
strip = "".join(f'<figure><img src="{IMG[f"f{fr}"]}"><figcaption><span class="idx">{i + 1:02d}</span><b>{lab}</b></figcaption></figure>'
                for i, (fr, lab) in enumerate([(96, "Feed"), (165, "Digest"), (250, "Monitor"), (330, "Fertilize"), (430, "Cook")]))
recs = "".join(f'<div><span class="idx">R{i + 1}</span><p>{t_}</p></div>' for i, t_ in enumerate(RECS))
refs = "".join(f"<li>{r}</li>" for r in REFS)
sdg = "".join(f'<span style="background:{c}">{n}</span>' for n, c in SDG)

html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="wrap">

<header class="band">
  <div class="logo">EVENT<br>LOGO</div>
  <div class="ttl">
    <div class="country"><span class="flag"></span>INDONESIA</div>
    <h1>ARUNA: a kinetically sized, <em>sensor-guided</em> home digester</h1>
    <div class="sub">Design of an IoT-enabled household anaerobic digester converting food waste into biogas and biofertilizer</div>
    <div class="auth"><span class="ph">[Author 1]</span> · <span class="ph">[Author 2]</span> · <span class="ph">[Author 3]</span> — <span class="ph">[Supervisor]</span> · <span class="ph">[Institution]</span></div>
  </div>
  <div class="logo">ORGANIZER<br>LOGO</div>
</header>

<section class="row" style="grid-template-columns:.86fr 1.14fr">
  <div class="intro" style="padding-top:56px">
    <div class="sh"><span class="idx">01</span><h2>Introduction</h2><span class="note">Problem · gap · hypothesis</span></div>
    <div class="big"><b>53<sup>kg</sup></b><span>of food is thrown away per person, per year, by Indonesian households.<br><span class="lab">UNEP Food Waste Index 2024</span></span></div>
    <div class="stats3">{stats3}</div>
    <div class="gap">
      <img class="photo" src="{IMG['f40']}" style="height:540px">
      <div><span class="lab">Research gap</span><ol style="margin-top:14px">
        <li>Home digesters are bulky, manure-oriented and <b>unmonitored</b>.</li>
        <li>Food waste acidifies fast; VFA build-up halts methane.</li>
        <li>Low-cost MQ sensors read ppm leaks, <b>not biogas CH₄ %</b>.</li></ol></div>
    </div>
    <div class="path">{path}</div>
    <div class="hyp"><span class="lab">Hypothesis</span>
      <p style="margin-top:10px">A shredded, stirred 100-litre digester at OLR ≤ <em>{NM['olr']:.1f}</em> kg VS/m³·d reaches <em>≥ 50 % CH₄</em> and ≥ 0.30 m³ CH₄/kg VS, while sensor guidance keeps usability at SUS ≥ 68.</p></div>
    <div class="sdg"><span class="lab" style="margin-right:12px">SDG</span>{sdg}<span class="lab" style="margin-left:18px;white-space:nowrap">targets 7.1 · 11.6 · 12.3 · 13.2</span></div>
  </div>

  <div class="dark">
    <div class="sh"><span class="idx">02</span><h2>Method</h2><span class="note">R&amp;D · 4D model · Thiagarajan 1974</span></div>
    <div class="rail">{rail}</div>
    <div class="mgrid">
      <div><span class="lab" style="color:rgba(246,242,233,.6)">Hardware &amp; instrumentation · x-ray of the digital twin</span>{xray_html(470)}</div>
      <div><span class="lab" style="color:rgba(246,242,233,.6)">Process &amp; daily mass balance</span><div class="flow">{flow}</div></div>
    </div>
    <div class="eqs">{eqs}</div>
    <div class="exp">{exp}</div>
  </div>
</section>

<section class="row" style="grid-template-columns:1.22fr .78fr">
  <div>
    <div class="sh"><span class="idx">03</span><h2>Data and Discussion</h2><span class="note">Design predictions · measured data pending</span></div>
    <div class="kpis">{kpis}</div>
    <div class="charts">
      <figure><figcaption><span class="idx">A</span><b>Methane kinetics</b><span class="lab">modified Gompertz</span></figcaption><img src="{IMG['pro_gompertz']}"></figure>
      <figure><figcaption><span class="idx">B</span><b>Sensitivity to daily input</b><span class="lab">nominal 1.5 kg/d</span></figcaption><img src="{IMG['pro_sens']}"></figure>
    </div>
    <div class="dgrid">
      <figure><figcaption><span class="idx">C</span><b>Three load scenarios</b></figcaption>{table(["Parameter", "Home of 4", "Nominal", "Peak"], CALC_ROWS, ["46%", "18%", "18%", "18%"], "calc")}</figure>
      <figure><figcaption><span class="idx">D</span><b>Avoided emissions</b></figcaption><img src="{IMG['pro_ghg']}"></figure>
    </div>
    <div class="disc">
      <p><b>Biodegradability ≈ {C['biodeg']:.0f} %.</b> The expected BMP of 390 mL CH₄/g VS against the Buswell maximum of 643 lies within the reported food-waste range (Zhang et al., 2007).</p>
      <p><b>Stability limit.</b> At peak load (OLR {MX['olr']:.1f}, HRT {MX['hrt']:.0f} d) VFA accumulates; the pH interlock pauses feeding below 6.5 (Chen et al., 2008).</p>
    </div>
    <figure style="margin-top:36px"><figcaption><span class="idx">E</span><b>Measured results</b><span class="lab">to be completed after testing</span></figcaption>{table(["Indicator", "Target", "Measured (mean ± SD)", "p"], MEAS, ["40%", "18%", "28%", "14%"])}</figure>
  </div>

  <div class="concl" style="padding-top:0">
    <div class="sh"><span class="idx">04</span><h2>Conclusion</h2></div>
    <div class="hero"><img src="{IMG['cover']}"></div>
    <div class="novelty">Shred, stir, digest and measure in a 0.19 m² footprint — with NDIR methane sensing and safety interlocks a non-expert can trust.</div>
    <ol class="cl">
      <li>Sized from mass balance and kinetics: <b>{NM['bg']:.0f} L biogas/day</b> at 1.5 kg food waste.</li>
      <li>≈ <b>{NM['cook']:.0f} minutes</b> of cooking per day and <b>{NM['co2e']:.2f} t CO₂e</b> avoided per year.</li>
      <li><span class="ph">[Confirm or reject H1–H2 with measured data]</span></li></ol>
    <div class="qr"><img src="{IMG['qr']}"><div><span class="lab">Live prototype app</span><b>aruna-id.web.app</b></div></div>
  </div>
</section>

<section class="row" style="grid-template-columns:1fr">
  <div>
    <div class="sh"><span class="idx">05</span><h2>Recommendation</h2><span class="note">Use case · next steps</span></div>
    <div class="strip">{strip}</div>
    <div class="recs">{recs}</div>
  </div>
</section>

<section class="row" style="grid-template-columns:1fr;padding-top:70px">
  <div>
    <div class="sh" style="margin-bottom:22px"><span class="idx">06</span><h2 style="font-size:54px">References</h2></div>
    <ol class="refs">{refs}</ol>
  </div>
</section>
<div class="foot"><span>Highlighted fields are placeholders · values are design predictions, not measurements</span><span>Rendered in Blender · 3D character: sthaarpit, Sketchfab, CC-BY 4.0</span></div>
</div></body></html>"""
