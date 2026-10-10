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

exec(open(os.path.join(HERE, "poster_pro.py"), encoding="utf-8").read())
import re as _re
FONT_SCALE = 1.0   # perbesar semua teks < 40 px (judul besar tetap)
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
