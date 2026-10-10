"""
Poster A0 ilmiah ARUNA (841 x 1189 mm) sesuai template lomba (bahasa Inggris).

  python design/competition/sci_calc.py          # angka + figur ilmiah
  python design/competition/build_poster_a0.py
Layout: [Event logo | Flag + Country + Project title | Organizer logo]
        [Introduction | Method] [Data & discussion | Conclusion] [Recommendation] [References]
Keluaran: ARUNA_Poster_A0.pdf + ARUNA_Poster_A0.png
"""
import asyncio
import json
import os
import shutil

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.dirname(HERE)
SHOW = os.path.join(DESIGN, "showcase")
A = os.path.join(HERE, "_poster")
os.makedirs(A, exist_ok=True)
C = json.load(open(os.path.join(HERE, "calc.json")))
CW, CH = 2400, 3394          # kanvas css px, rasio A0


def cp(src, name):
    shutil.copy(src, os.path.join(A, name))
    return "_poster/" + name


FIG = os.path.join(HERE, "fig")
IMG = {k: cp(os.path.join(FIG, f), f) for k, f in {
    "method": "fig_method_4d.png", "xray": "fig_hardware_xray.png", "arch": "fig_architecture.png",
    "pfd": "sci_pfd.png", "control": "sci_control.png", "gompertz": "sci_gompertz.png",
    "sens": "sci_sensitivity.png", "ghg": "sci_ghg.png"}.items()}
IMG["cover"] = cp(os.path.join(SHOW, "deck", "assets", "cover.png"), "cover.png")
IMG["qr"] = cp(os.path.join(SHOW, "deck", "_cache", "qr.png"), "qr.png")
src = open(os.path.join(SHOW, "print", "build_print.py"), encoding="utf-8").read()
ns = {"os": os, "Image": Image, "ASSET": A}
exec(src[src.index("def abstract_bg"):src.index('IMG["bg_poster"]')], ns)
IMG["bg"] = ns["abstract_bg"](CW, CH, 5, "bg_a0", strength=.85, dots=((.02, .36), (.93, .58))).replace("_assets/", "_poster/")

f1 = lambda v: f"{v:,.1f}"
f0 = lambda v: f"{v:,.0f}"
H4, NM, MX = C["hh4"], C["nominal"], C["max"]

STATS = [("53 kg", "household food waste per capita per year in Indonesia", "UNEP, 2024", "#158A52", "#D8F0E2"),
         ("14.7 Mt", "household food waste per year in Indonesia", "UNEP, 2024", "#0E7A6A", "#D3EEEA"),
         ("≈40%", "share of food waste in municipal solid waste", "SIPSN KLHK, 2023", "#B8741A", "#FBE9CC"),
         ("1.7 Gt", "CO₂e from food loss &amp; waste, 2000–2019", "Bappenas, 2021", "#C8443A", "#F9DCD8")]
SENSORS = [("Temperature", "DS18B20 (1-Wire)", "−55–125 °C", "±0.5 °C (−10–85 °C)"),
           ("CH₄ composition", "NDIR, Winsen MH-440D", "0–100 % vol", "T90 &lt; 30 s"),
           ("CH₄ leak (safety)", "MQ-4 (SnO₂)", "300–10,000 ppm", "alarm at 10 % LEL"),
           ("pH", "Industrial pH probe", "0–14", "3-point calibration"),
           ("Slurry level", "Waterproof ultrasonic", "fill ratio", "≈ ±1 cm"),
           ("Input mass", "Load cell + HX711", "0–5 kg", "24-bit ADC"),
           ("Biogas volume", "Diaphragm gas meter", "L/d", "reference")]
EQ = [("Theoretical CH₄ (Buswell &amp; Mueller, 1952)",
       "C<sub>c</sub>H<sub>h</sub>O<sub>o</sub>N<sub>n</sub> + (c − h/4 − o/2 + 3n/4) H<sub>2</sub>O → (c/2 + h/8 − o/4 − 3n/8) CH<sub>4</sub> + (c/2 − h/8 + o/4 + 3n/8) CO<sub>2</sub> + n NH<sub>3</sub>"),
      ("Loading &amp; retention", "OLR = F·TS·(VS/TS) / V<sub>w</sub> &nbsp;&nbsp;·&nbsp;&nbsp; HRT = V<sub>w</sub> / Q"),
      ("Kinetics: modified Gompertz (Zwietering et al., 1990)", "M(t) = P · exp{ −exp[ (R<sub>m</sub>·e / P)(λ − t) + 1 ] }"),
      ("Energy &amp; cooking time", "E = V<sub>CH₄</sub> · LHV<sub>CH₄</sub> (35.8 MJ/m³) &nbsp;·&nbsp; t<sub>cook</sub> = V<sub>biogas</sub> / q<sub>stove</sub>"),
      ("Avoided landfill CH₄ (IPCC 2006 FOD)", "CH<sub>4</sub> = W · DOC · DOC<sub>f</sub> · MCF · F · 16/12 · (1 − OX)"),
      ("Usability (Brooke, 1996)", "SUS = 2.5 · [ Σ(odd − 1) + Σ(5 − even) ]")]
CALC_ROWS = [("Food-waste input (kg/d)", f"{H4['fw']:.2f}", f"{NM['fw']:.1f}", f"{MX['fw']:.1f}"),
             ("OLR (kg VS/m³·d)", f1(H4["olr"]), f1(NM["olr"]), f1(MX["olr"])),
             ("HRT (d)", f0(H4["hrt"]), f0(NM["hrt"]), f0(MX["hrt"])),
             ("Biogas (L/d, 60 % CH₄)", f0(H4["bg"]), f0(NM["bg"]), f0(MX["bg"])),
             ("Energy (kWh/d)", f"{H4['kwh']:.2f}", f"{NM['kwh']:.2f}", f"{MX['kwh']:.2f}"),
             ("Cooking time (min/d)", f0(H4["cook"]), f0(NM["cook"]), f0(MX["cook"])),
             ("LPG equivalent (kg/month)", f1(H4["lpg"]), f1(NM["lpg"]), f1(MX["lpg"])),
             ("Avoided GHG (t CO₂e/yr)", f"{H4['co2e']:.2f}", f"{NM['co2e']:.2f}", f"{MX['co2e']:.2f}")]
REFS = [
    "APHA. (2017). <i>Standard methods for the examination of water and wastewater</i> (23rd ed.), Method 2540. APHA/AWWA/WEF.",
    "Appels, L., Baeyens, J., Degrève, J., &amp; Dewil, R. (2008). Principles and potential of the anaerobic digestion of waste-activated sludge. <i>Prog. Energy Combust. Sci., 34</i>(6), 755–781.",
    "Bappenas. (2021). <i>Food loss and waste in Indonesia</i>. Ministry of National Development Planning.",
    "Brooke, J. (1996). SUS: A “quick and dirty” usability scale. In <i>Usability evaluation in industry</i> (pp. 189–194). Taylor &amp; Francis.",
    "Buswell, A. M., &amp; Mueller, H. F. (1952). Mechanism of methane fermentation. <i>Ind. Eng. Chem., 44</i>(3), 550–552.",
    "Chen, Y., Cheng, J. J., &amp; Creamer, K. S. (2008). Inhibition of anaerobic digestion process: A review. <i>Bioresour. Technol., 99</i>(10), 4044–4064.",
    "IPCC. (2006). <i>2006 IPCC guidelines for national greenhouse gas inventories, Vol. 5: Waste</i>, Ch. 3. IGES.",
    "IPCC. (2014). <i>Climate change 2014: Synthesis report (AR5)</i>. IPCC.",
    "KLHK. (2023). <i>SIPSN: Komposisi sampah</i>. https://sipsn.menlhk.go.id",
    "Mata-Alvarez, J., Macé, S., &amp; Llabrés, P. (2000). Anaerobic digestion of organic solid wastes. <i>Bioresour. Technol., 74</i>(1), 3–16.",
    "Rajendran, K., Aslanzadeh, S., &amp; Taherzadeh, M. J. (2012). Household biogas digesters: A review. <i>Energies, 5</i>(8), 2911–2942.",
    "SSWM / Akvopedia. (2019). <i>Biogas combustion</i>. https://sswm.info",
    "Thiagarajan, S., Semmel, D. S., &amp; Semmel, M. I. (1974). <i>Instructional development for training teachers of exceptional children</i>. Indiana University.",
    "UNEP. (2024). <i>Food waste index report 2024</i>. United Nations Environment Programme.",
    "VDI. (2016). <i>VDI 4630: Fermentation of organic materials</i>. Verein Deutscher Ingenieure.",
    "Weiland, P. (2010). Biogas production: Current state and perspectives. <i>Appl. Microbiol. Biotechnol., 85</i>(4), 849–860.",
    "Winsen. (n.d.). <i>MH-440D NDIR CH₄ sensor</i> and <i>MQ-4 gas sensor</i> datasheets. Zhengzhou Winsen Electronics.",
    "Xu, F., Li, Y., Ge, X., Yang, L., &amp; Li, Y. (2018). Anaerobic digestion of food waste: Challenges and opportunities. <i>Bioresour. Technol., 247</i>, 1047–1058.",
    "Zhang, R., et al. (2007). Characterization of food waste as feedstock for anaerobic digestion. <i>Bioresour. Technol., 98</i>(4), 929–935.",
    "Zwietering, M. H., Jongenburger, I., Rombouts, F. M., &amp; van 't Riet, K. (1990). Modeling of the bacterial growth curve. <i>Appl. Environ. Microbiol., 56</i>(6), 1875–1881.",
]


def table(head, rows, widths, cls=""):
    th = "".join(f'<th style="width:{w}">{h}</th>' for h, w in zip(head, widths))
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table class="t {cls}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'


PH = '<span class="ph">[ ]</span>'
MEAS = [("CH₄ content (%)", "≥ 50", PH, PH), ("Specific yield (m³ CH₄/kg VS)", "≥ 0.30", PH, PH),
        ("FOS/TAC", "&lt; 0.4", PH, "—"), ("VS removal (%)", "≥ 70", PH, "—"), ("SUS score", "≥ 68", PH, "—")]
RECS = ["Run BMP and semi-continuous tests to fit P, R<sub>m</sub>, λ and confirm the OLR limit.",
        "Co-digest with garden waste to raise C/N towards 20–30 and buffer pH.",
        "Add on-device AI to reject bones, oil and plastics before shredding.",
        "Insulate or solar-heat the tank for highland regions below 25 °C.",
        "Pilot in MBG school kitchens with MRV of avoided emissions."]

html = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap" rel="stylesheet">
<style>
@page{{size:841mm 1189mm;margin:0}}
:root{{--ink:#10201A;--ink2:#3C4E45;--muted:#74857C;--green:#158A52;--teal:#0E7A6A;--deep:#0F6B40;--amber:#B8741A;--sans:"Plus Jakarta Sans","Segoe UI",sans-serif;--serif:"Source Serif 4",Georgia,serif}}
*{{box-sizing:border-box;margin:0}}
html{{height:{CH}px;overflow:hidden}}
body{{width:{CW}px;height:{CH}px;overflow:hidden;font-family:var(--sans);color:var(--ink);background:#fff url({IMG["bg"]}) center/cover;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.wrap{{padding:50px 56px;display:grid;gap:24px}}
.box{{border-radius:28px;background:rgba(255,255,255,.94);border:3px solid rgba(15,107,64,.22);box-shadow:0 22px 46px -24px rgba(15,107,64,.45);padding:28px 32px 30px;display:flex;flex-direction:column;gap:14px}}
.box.mint{{background:linear-gradient(160deg,#F1FAF5,#D9F0E2)}}
.box.dark{{background:linear-gradient(150deg,#0F6B40,#0E7A6A 60%,#139067);color:#fff;border-color:#0F6B40}}
.sec{{display:flex;align-items:center;gap:14px}}
.sec h2{{font-size:42px;font-weight:800;letter-spacing:.02em;text-transform:uppercase}}
.sec i{{display:block;width:14px;height:42px;border-radius:8px;background:var(--green)}}
.box.dark .sec i{{background:#A6EBC5}}
h3{{font-size:25px;font-weight:800;color:var(--deep);display:flex;align-items:center;gap:10px}}
h3 span.n{{display:inline-grid;place-items:center;width:34px;height:34px;border-radius:50%;background:var(--green);color:#fff;font-size:19px;flex:none}}
.box.dark h3{{color:#fff}} .box.dark h3 span.n{{background:#fff;color:var(--deep)}}
.box.dark .panel h3{{color:var(--deep)}} .box.dark .panel h3 span.n{{background:var(--green);color:#fff}}
p,li{{font-size:21px;line-height:1.42;color:var(--ink2)}}
.box.dark p,.box.dark li{{color:rgba(255,255,255,.92)}}
.box.dark .panel p,.box.dark .panel li{{color:var(--ink2)}}
ul{{padding-left:24px;display:grid;gap:4px}}
.panel{{background:#fff;border-radius:18px;padding:14px 16px;color:var(--ink)}}
img.fig{{width:100%;display:block;border-radius:14px;background:#fff}}
.cap{{font-size:16.5px;color:var(--muted);text-align:center;margin-top:6px;font-style:italic;font-family:var(--serif)}}
.ph{{background:#FFF2A8;color:#6B5300;font-weight:700;border-radius:6px;padding:0 6px}}
.chip{{display:inline-block;font-size:18px;font-weight:800;color:#fff;border-radius:10px;padding:6px 12px}}
.logo{{border:4px dashed rgba(15,107,64,.45);border-radius:28px;display:grid;place-items:center;text-align:center;font-size:30px;font-weight:800;color:var(--muted);background:rgba(255,255,255,.78)}}
.flag{{width:210px;height:140px;border-radius:10px;overflow:hidden;box-shadow:0 0 0 3px #D9DFDC;margin:0 auto}}
.flag div{{height:50%}}
table.t{{width:100%;border-collapse:separate;border-spacing:0;font-size:18.5px;background:#fff;border-radius:14px;overflow:hidden;color:var(--ink)}}
table.t th{{background:#0F6B40;color:#fff;text-align:left;padding:8px 10px;font-size:17px;font-weight:700}}
table.t td{{padding:7px 10px;border-top:1px solid #E1EAE5}}
table.t tr:nth-child(even) td{{background:#F3FAF6}}
table.t td:not(:first-child),table.t th:not(:first-child){{text-align:center}}
table.t.calc td:nth-child(3){{background:#E3F4EA;font-weight:800;color:var(--deep)}}
.eq{{display:grid;gap:8px}}
.eq div{{background:#fff;border-radius:14px;padding:9px 14px;color:var(--ink)}}
.eq b{{display:block;font-size:16px;color:var(--teal);text-transform:uppercase;letter-spacing:.04em}}
.eq code{{font-family:var(--serif);font-size:23px;font-style:italic;color:var(--ink)}}
.hyp{{border-left:6px solid var(--amber);background:#FFF8EC;border-radius:12px;padding:12px 16px}}
.kpi{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}
.kpi div{{background:#fff;border-radius:16px;padding:12px 14px;border:2px solid rgba(15,107,64,.14)}}
.kpi b{{display:block;font-size:34px;letter-spacing:-.03em;color:var(--green)}}
.kpi span{{font-size:16px;color:var(--ink2);line-height:1.25;display:block}}
ol.refs{{columns:3;column-gap:34px;padding-left:28px}}
ol.refs li{{font-size:15.5px;line-height:1.35;margin-bottom:5px;break-inside:avoid;font-family:var(--serif);color:var(--ink2)}}
/* ===== skin berwarna (layout tidak berubah) ===== */
body{{background:linear-gradient(175deg,#0F6B40 0%,#13906A 14%,#CDEFD9 32%,#FFF2D6 66%,#FFD9C2 100%)!important}}
body::before{{content:"";position:fixed;inset:0;background-image:url('data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2222%22%20height%3D%2222%22%3E%3Ccircle%20cx%3D%225%22%20cy%3D%225%22%20r%3D%222.2%22%20fill%3D%22%23ffffff%22%20fill-opacity%3D%22.22%22%2F%3E%3C%2Fsvg%3E');pointer-events:none}}
.wrap{{position:relative}}
.box{{border-width:0!important;box-shadow:0 26px 54px -26px rgba(15,60,40,.55)!important}}
.box.hdr{{background:linear-gradient(135deg,#0F6B40 0%,#0E7A6A 55%,#1FA567 100%)!important;color:#fff}}
.box.hdr h1{{color:#fff}} .box.hdr h1 span{{color:#FFD166!important}}
.box.hdr div{{color:#E6F7EE!important;border-color:rgba(255,255,255,.35)!important}}
.logo{{background:linear-gradient(160deg,#FFFFFF,#FFF2D6)!important;border-color:#E8912D!important;color:#B8741A!important}}
.box.intro{{background:linear-gradient(165deg,#FFF6EC 0%,#FFE1D0 100%)!important}}
.box.intro .sec i,.box.intro h3 span.n{{background:#E8604C}} .box.intro .sec h2{{color:#B2392A}} .box.intro h3{{color:#B2392A}}
.box.dark{{background-image:url('data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22220%22%20height%3D%22220%22%3E%3Cpath%20d%3D%22M40%2090%20C%205%2055%2030%2010%2090%205%20C%2090%2060%2070%2090%2040%2090%20Z%22%20fill%3D%22%23A6EBC5%22%20fill-opacity%3D%22.10%22%2F%3E%3Cpath%20d%3D%22M150%20200%20C%20115%20165%20140%20120%20200%20115%20C%20200%20170%20180%20200%20150%20200%20Z%22%20fill%3D%22%23FFD166%22%20fill-opacity%3D%22.08%22%2F%3E%3C%2Fsvg%3E'),linear-gradient(150deg,#0F6B40,#0E7A6A 60%,#139067)!important}}
.box.dark .sec h2{{color:#FFD166}}
.box.mint{{background:linear-gradient(165deg,#E3F6FB 0%,#CDEFD9 100%)!important}}
.box.mint .sec i,.box.mint h3 span.n{{background:#2D9CDB}} .box.mint .sec h2,.box.mint h3{{color:#1D6FA5}}
.box.mint table.t th{{background:#1D6FA5}}
.box.concl{{background:linear-gradient(165deg,#FFF6CF 0%,#FFD98A 100%)!important}}
.box.concl .sec i{{background:#B8741A}} .box.concl .sec h2{{color:#8A5418}}
.box.rec{{background:linear-gradient(160deg,#FFB25B 0%,#F08A3C 100%)!important}}
.box.rec .sec h2{{color:#fff}} .box.rec .sec i{{background:#fff!important}}
.box.refs{{background:linear-gradient(165deg,#F2FBF8,#D9F1EA)!important}}
.kpi div:nth-child(1){{background:#158A52}} .kpi div:nth-child(2){{background:#2D9CDB}} .kpi div:nth-child(3){{background:#E8912D}} .kpi div:nth-child(4){{background:#E8604C}}
.kpi div{{border:0!important;box-shadow:0 12px 22px -14px rgba(0,0,0,.45)}} .kpi b,.kpi span{{color:#fff!important}}
</style></head><body><div class="wrap">

<header style="display:grid;grid-template-columns:340px 1fr 340px;gap:26px;min-height:360px">
  <div class="logo">EVENT<br>LOGO</div>
  <div class="box hdr" style="align-items:center;justify-content:center;text-align:center;gap:12px">
    <div class="flag"><div style="background:#FF0000"></div><div style="background:#fff"></div></div>
    <div style="font-size:32px;font-weight:800;letter-spacing:.2em;color:var(--deep);border-bottom:3px solid rgba(15,107,64,.3);padding-bottom:8px">INDONESIA</div>
    <h1 style="font-size:54px;line-height:1.06;letter-spacing:-.02em">ARUNA: Design and Kinetic-Based Sizing of an IoT-Enabled Household Anaerobic Digester<br><span style="color:var(--green)">for Converting Food Waste into Biogas and Biofertilizer</span></h1>
    <div style="font-size:23px;color:var(--ink2)"><span class="ph">[Author 1]</span>, <span class="ph">[Author 2]</span>, <span class="ph">[Author 3]</span> · <span class="ph">[Supervisor]</span> · <span class="ph">[Institution]</span></div>
  </div>
  <div class="logo">ORGANIZER<br>LOGO</div>
</header>

<section style="display:grid;grid-template-columns:.74fr 1.26fr;gap:24px">
  <div class="box intro">
    <div class="sec"><i></i><h2>Introduction</h2></div>
    <h3><span class="n">a</span>Background</h3>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
    {''.join(f'<div style="border-radius:16px;padding:12px 14px;background:linear-gradient(160deg,#fff,{t});border:2px solid {c}33"><div style="font-size:36px;font-weight:800;color:{c};letter-spacing:-.03em">{a}</div><div style="font-size:17px;color:var(--ink);line-height:1.25">{b}</div><div style="font-size:14px;color:var(--ink2);margin-top:3px;font-weight:600">{s}</div></div>' for a,b,s,c,t in STATS)}
    </div>
    <p>Landfilled food waste decays anaerobically and emits CH₄ (GWP<sub>100</sub> = 28; IPCC, 2014). Food waste is an ideal AD feedstock: <b>TS 23–27 %</b>, <b>VS 90–95 % of TS</b> and BMP <b>330–490 mL CH₄/g VS</b> (Zhang et al., 2007; Xu et al., 2018).</p>
    <h3><span class="n">b</span>Research gap</h3>
    <ul><li>Household digesters are manure-oriented, bulky and <b>unmonitored</b> (Rajendran et al., 2012).</li>
        <li>Food waste acidifies quickly: VFA build-up lowers pH and inhibits methanogens (Chen et al., 2008).</li>
        <li>Low-cost MQ-type sensors detect leaks (ppm) but <b>cannot measure biogas CH₄ (%)</b>.</li></ul>
    <h3><span class="n">c</span>Hypotheses</h3>
    <div class="hyp"><p><b>H1</b> A shredded, stirred 100 L digester at OLR ≤ 3.4 kg VS/m³·d (HRT ≈ 34 d) yields CH₄ ≥ 50 % and ≥ 0.30 m³ CH₄/kg VS with FOS/TAC &lt; 0.4.<br><b>H2</b> Sensor-guided feedback yields usability of SUS ≥ 68.</p></div>
    <h3><span class="n">d</span>Objectives</h3>
    <ul><li>Size the digester from kinetics, mass and energy balance.</li><li>Build IoT sensing, safety interlocks and a companion app.</li><li>Validate yield, stability and usability in lab and households.</li></ul>
    <h3><span class="n">e</span>Biochemical pathway</h3>
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px">
    {''.join(f'<div style="border-radius:14px;padding:10px 10px;background:{bg};border:2px solid {c}55;text-align:center"><div style="font-size:19px;font-weight:800;color:{c}">{t}</div><div style="font-size:15px;color:var(--ink2);line-height:1.25;margin-top:3px">{d}</div></div>' for t,d,c,bg in [("Hydrolysis","polymers → sugars, amino acids, LCFA","#0E7A6A","#E3F2EF"),("Acidogenesis","→ VFA, alcohols, H₂, CO₂","#B8741A","#FBF0DF"),("Acetogenesis","VFA → acetate + H₂","#C8443A","#FBE7E5"),("Methanogenesis","acetate / H₂ + CO₂ → CH₄","#158A52","#E3F3EA")])}
    </div>
    <p style="font-size:17px">Rapid hydrolysis of food waste can outpace methanogenesis → VFA accumulation, pH drop, process failure; hence pH and FOS/TAC control (Appels et al., 2008).</p>
    <h3><span class="n">f</span>Proposed system concept</h3>
    <img class="fig" src="{IMG['arch']}" style="padding:6px;border:2px solid rgba(15,107,64,.12);width:82%;align-self:center">
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:auto">
      <span class="chip" style="background:#C89A08">SDG 7.1</span><span class="chip" style="background:#E08010">SDG 11.6</span>
      <span class="chip" style="background:#A07426">SDG 12.3 · 12.5</span><span class="chip" style="background:#3F7E44">SDG 13.2</span></div>
  </div>

  <div class="box dark">
    <div class="sec"><i></i><h2>Method</h2></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <div style="display:grid;gap:10px;align-content:start">
        <h3><span class="n">1</span>R&amp;D design: 4D model</h3>
        <img class="fig" src="{IMG['method']}" style="padding:8px">
        <h3><span class="n">2</span>Process flow &amp; mass balance (nominal load)</h3>
        <img class="fig" src="{IMG['pfd']}" style="padding:6px">
      </div>
      <div style="display:grid;gap:10px;align-content:start">
        <h3><span class="n">3</span>Design equations</h3>
        <div class="eq">{''.join(f'<div><b>{t}</b><code>{e}</code></div>' for t,e in EQ)}</div>
      </div>
    </div>
    <div style="display:grid;grid-template-columns:.9fr .75fr 1.15fr;gap:16px;align-items:start">
      <div><h3><span class="n">4</span>Hardware</h3><img class="fig" src="{IMG['xray']}" style="padding:6px;margin-top:8px"></div>
      <div><h3><span class="n">5</span>Control interlocks</h3><img class="fig" src="{IMG['control']}" style="padding:6px;margin-top:8px"></div>
      <div style="display:grid;gap:10px">
        <h3><span class="n">6</span>Instrumentation</h3>
        {table(["Parameter","Sensor","Range","Accuracy / note"], SENSORS, ["24%","30%","22%","24%"])}
      </div>
    </div>
    <div class="panel" style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:18px">
      <div><h3><span class="n">7</span>Experimental design</h3>
        <ul><li>BMP assay (VDI 4630), ISR ≥ 2, 37 °C, triplicate</li><li>Semi-continuous: OLR 2.0 / 3.4 / 4.5 kg VS/m³·d × 3 replicates, 2 HRT cycles</li><li>Field: <span class="ph">[n]</span> households × 30 d</li></ul></div>
      <div><h3><span class="n">8</span>Measurements</h3>
        <ul><li>TS/VS: APHA 2540 G</li><li>pH, FOS/TAC titration (stable &lt; 0.4)</li><li>CH₄ % (NDIR), biogas L/d, VS removal</li><li>Digestate N, P, K; SUS questionnaire</li></ul></div>
      <div><h3><span class="n">9</span>Data analysis</h3>
        <ul><li>Gompertz fit by non-linear least squares (R², RMSE)</li><li>One-way ANOVA + Tukey, α = 0.05</li><li>Biodegradability = BMP<sub>exp</sub> / BMP<sub>th</sub></li></ul></div>
    </div>
  </div>
</section>

<section style="display:grid;grid-template-columns:1.32fr .68fr;gap:24px">
  <div class="box mint">
    <div class="sec"><i></i><h2>Data and Discussion</h2></div>
    <div class="kpi">
      <div><b>{f0(NM['bg'])} L/d</b><span>biogas at nominal 1.5 kg/d (predicted)</span></div>
      <div><b>≈{f0(NM['cook'])} min</b><span>cooking per day (0.30 m³/h stove)</span></div>
      <div><b>≈{f1(NM['lpg'])} kg</b><span>LPG equivalent per month (one 3-kg cylinder)</span></div>
      <div><b>{NM['co2e']:.2f} t</b><span>CO₂e avoided per year (potential)</span></div>
    </div>
    <div style="display:grid;grid-template-columns:1.05fr 1fr;gap:16px;align-items:start">
      <div><h3><span class="n">A</span>Design calculation for three load scenarios</h3>
        <div style="margin-top:8px">{table(["Parameter","Household of 4","Nominal","Peak"], CALC_ROWS, ["43%","19%","19%","19%"], "calc")}</div>
        <p style="font-size:16px;margin-top:6px">Basis: TS 25 %, VS/TS 90 %, Y = 0.38 m³ CH₄/kg VS, V<sub>w</sub> = 100 L, dilution 1:1, LHV<sub>CH₄</sub> 35.8 MJ/m³, LPG 46 MJ/kg; household of 4 = 4 × 53 kg/yr (UNEP, 2024).</p></div>
      <div><h3><span class="n">B</span>Methane kinetics</h3><img class="fig" src="{IMG['gompertz']}" style="padding:6px;margin-top:8px;width:88%;margin-left:auto;margin-right:auto">
        <div class="cap">Gompertz curve with literature-range parameters; to be fitted to the team's BMP data.</div></div>
    </div>
    <div style="display:grid;grid-template-columns:1fr .82fr 1.1fr;gap:16px;align-items:start">
      <div><h3><span class="n">C</span>Sensitivity to input load</h3><img class="fig" src="{IMG['sens']}" style="padding:6px;margin-top:8px"></div>
      <div><h3><span class="n">D</span>Avoided emissions</h3><img class="fig" src="{IMG['ghg']}" style="padding:6px;margin-top:8px"></div>
      <div><h3><span class="n">E</span>Discussion</h3>
        <ul style="margin-top:6px">
          <li>Expected biodegradability ≈ <b>{C['biodeg']:.0f} %</b> (390 / 643 mL CH₄/g VS), consistent with food-waste degradability in literature.</li>
          <li>Nominal OLR 3.4 kg VS/m³·d lies within reported stable ranges for food waste; <b>peak load (6.8, HRT 17 d) risks VFA build-up</b>, so feeding pauses when pH &lt; 6.5.</li>
          <li>A household of 4 yields ≈ {f0(H4['cook'])} min/d of cooking gas; nominal load suits extended families or small eateries.</li>
          <li>Indonesia's lowland ambient temperature favours mesophilic operation without heating.</li></ul></div>
    </div>
    <div class="panel"><h3><span class="n">F</span>Measured results (lab / field) <span style="color:var(--amber);font-size:17px;margin-left:6px">to be completed</span></h3>
      <div style="margin-top:8px">{table(["Indicator","Target","Measured (mean ± SD)","p-value"], MEAS, ["40%","16%","28%","16%"])}</div></div>
  </div>

  <div class="box concl">
    <div class="sec"><i></i><h2>Conclusion</h2></div>
    <img src="{IMG['cover']}" style="height:460px;width:auto;align-self:center">
    <div class="hyp" style="border-left-color:var(--green);background:#EFF9F3"><p style="font-size:19px"><b>Novelty.</b> (i) shred–stir–digest integrated in a 0.19 m² footprint; (ii) NDIR-based CH₄ quality sensing instead of ppm leak sensors; (iii) rule-based pH/level/leak interlocks translated into plain-language app guidance.</p></div>
    <ul>
      <li>A <b>44 × 44 × 112 cm</b> gravity-fed digester (V<sub>w</sub> 100 L) was sized from mass balance and Gompertz kinetics.</li>
      <li>At 1.5 kg/d the design predicts <b>{f0(NM['bg'])} L biogas/d</b> (≈ {f0(NM['cook'])} min cooking, ≈ {f1(NM['lpg'])} kg LPG/month) and <b>{NM['co2e']:.2f} t CO₂e/yr</b> avoided.</li>
      <li>NDIR CH₄ sensing, pH/level interlocks and app alerts close the monitoring gap of household AD.</li>
      <li><span class="ph">[Confirm or reject H1–H2 with measured data]</span></li></ul>
    <div style="display:flex;align-items:center;gap:18px;margin-top:auto;background:#F1FAF5;border-radius:18px;padding:12px">
      <img src="{IMG['qr']}" style="width:120px"><div><div style="font-size:23px;font-weight:800">Live app &amp; data</div><div style="font-size:23px;font-weight:800;color:var(--green)">aruna-id.web.app</div></div></div>
  </div>
</section>

<section class="box rec">
  <div class="sec"><i style="background:var(--amber)"></i><h2>Recommendation</h2></div>
  <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:14px">
  {''.join(f'<div style="background:#fff;border-radius:18px;padding:14px 16px;border:2px solid rgba(184,116,26,.2)"><div style="font-size:30px;font-weight:800;color:var(--amber)">{i+1}</div><p style="font-size:19px;color:var(--ink)">{t}</p></div>' for i,t in enumerate(RECS))}
  </div>
</section>

<section class="box refs" style="padding-bottom:22px">
  <div class="sec"><i></i><h2>References</h2></div>
  <ol class="refs">{''.join(f'<li>{r}</li>' for r in REFS)}</ol>
  <div style="font-size:14px;color:var(--muted)">Highlighted fields are placeholders for team data and measured results. Design values are calculated predictions, not measurements. 3D character: sthaarpit (Sketchfab, CC-BY 4.0).</div>
</section>
</div></body></html>"""
import re as _re
FONT_SCALE = 1.4   # perbesar semua teks < 40 px (judul besar tetap)
html = _re.sub(r"font-size:\s*([\d.]+)px", lambda m_: f"font-size:{float(m_.group(1)) * (FONT_SCALE if float(m_.group(1)) < 40 else 1.1):.1f}px", html)
open(os.path.join(HERE, "poster_A0.html"), "w", encoding="utf-8").write(html)


async def export():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": CW, "height": CH}, device_scale_factor=2)
        await pg.goto("file:///" + os.path.join(HERE, "poster_A0.html").replace("\\", "/"))
        await pg.wait_for_timeout(2000)
        fit = f"""() => {{ const w = document.querySelector('.wrap'); const lim = {CH - 30};
            const H = z => {{ w.style.zoom = z; w.style.width = ({CW} / z) + 'px'; return w.scrollHeight * z; }};
            let lo = 0.3, hi = 1.0;
            if (H(hi) <= lim) return [Math.round(H(hi)), "1.000"];
            for (let i = 0; i < 22; i++) {{ const mid = (lo + hi) / 2; if (H(mid) <= lim) lo = mid; else hi = mid; }}
            return [Math.round(H(lo)), lo.toFixed(3)]; }}"""
        print("[A0] tinggi konten:", await pg.evaluate(fit), f"/ {CH}")
        await pg.screenshot(path=os.path.join(HERE, "ARUNA_Poster_A0.png"))
        await pg.pdf(path=os.path.join(HERE, "ARUNA_Poster_A0.pdf"), width="841mm", height="1189mm",
                     print_background=True, scale=round(3179 / CW - 0.002, 3))
        await b.close()


asyncio.run(export())
print("[A0] selesai")
