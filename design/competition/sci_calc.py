"""
Perhitungan desain ilmiah ARUNA + figur poster A0 (satu sumber angka).

  python design/competition/sci_calc.py
Keluaran: fig/sci_*.png, calc.json

Asumsi (sumber literatur di poster):
- Sisa makanan: TS 25 %, VS/TS 90 % (TS 23–27 %, VS 90–95 % TS).
- BMP terukur literatur ~390 mL CH4/g VS (mesofilik); in-situ diasumsikan 0,38 m3 CH4/kg VS.
- Buswell teoretis 643 mL CH4/g VS (komposisi C48.46 H9.8 O30.48 N2.2).
- CH4 LHV 35,8 MJ/m3; kompor biogas 0,30 m3/jam (rentang 0,2–0,45); LPG LHV 46 MJ/kg, EF 2,98 kg CO2/kg.
- IPCC 2006 FOD (potensi jangka panjang): DOC 0,15; DOCf 0,5; MCF 0,8; F 0,5; OX 0; GWP100 CH4 = 28 (AR5).
"""
import json
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "fig")
os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------------------------ parameter desain
FW = 1.5            # kg sisa makanan / hari (nominal; maks 3)
WATER = 1.5         # L air pengencer / hari
TS, VS_TS = 0.25, 0.90
V_WORK = 100        # L volume kerja digester
Y_CH4 = 0.38        # m3 CH4 / kg VS ditambahkan (in-situ)
CH4_FRAC = 0.60
LHV_CH4 = 35.8      # MJ/m3
STOVE = 0.30        # m3 biogas / jam
LPG_LHV, LPG_EF = 46.0, 2.98
DOC, DOCF, MCF, F_, OX, GWP = 0.15, 0.5, 0.8, 0.5, 0.0, 28

vs_d = FW * TS * VS_TS                         # kg VS/d
q = FW * 0.95 + WATER                          # L/d umpan (densitas sisa makanan ~1,05 kg/L)
hrt = V_WORK / q                               # d
olr = vs_d / (V_WORK / 1000)                   # kg VS/m3.d
ts_feed = FW * TS / (FW + WATER) * 100         # % TS umpan
ch4_d = vs_d * Y_CH4                           # m3 CH4/d
bg_d = ch4_d / CH4_FRAC                        # m3 biogas/d
e_d = ch4_d * LHV_CH4                          # MJ/d
cook_min = bg_d / STOVE * 60                   # menit/hari
lpg_month = e_d * 30 / LPG_LHV                 # kg LPG setara / bulan
fw_year = FW * 365 / 1000                      # t/yr
ch4_landfill = fw_year * DOC * DOCF * MCF * F_ * 16 / 12 * (1 - OX)   # t CH4/yr (potensi)
co2e_landfill = ch4_landfill * GWP
co2_lpg = lpg_month * 12 * LPG_EF / 1000       # t CO2/yr
bmp_th, bmp_lab = 643, 390
biodeg = bmp_lab / bmp_th * 100

calc = dict(FW=FW, WATER=WATER, vs_d=vs_d, q=q, hrt=hrt, olr=olr, ts_feed=ts_feed, ch4_d=ch4_d, bg_d=bg_d, e_d=e_d,
            kwh_d=e_d / 3.6, cook_min=cook_min, lpg_month=lpg_month, fw_year=fw_year, ch4_landfill=ch4_landfill,
            co2e_landfill=co2e_landfill, co2_lpg=co2_lpg, co2e_total=co2e_landfill + co2_lpg, biodeg=biodeg,
            persons=FW / (53 / 365))


def scenario(fw):
    """Nilai harian/tahunan untuk input fw kg/d (pengenceran 1:1, V kerja tetap)."""
    vs = fw * TS * VS_TS
    qq = fw * 0.95 + fw
    ch4 = vs * Y_CH4
    e = ch4 * LHV_CH4
    lpg = e * 30 / LPG_LHV
    ch4l = fw * 365 / 1000 * DOC * DOCF * MCF * F_ * 16 / 12
    return dict(fw=fw, vs=vs, olr=vs / (V_WORK / 1000), hrt=V_WORK / qq, bg=ch4 / CH4_FRAC * 1000, ch4=ch4 * 1000,
                kwh=e / 3.6, cook=ch4 / CH4_FRAC / STOVE * 60, lpg=lpg, co2e=ch4l * GWP + lpg * 12 * LPG_EF / 1000)


calc["hh4"] = scenario(4 * 53 / 365)       # rumah tangga 4 orang (UNEP 2024: 53 kg/kapita/tahun)
calc["nominal"] = scenario(FW)
calc["max"] = scenario(3.0)
json.dump({k: (round(v, 4) if not isinstance(v, dict) else {kk: round(vv, 3) for kk, vv in v.items()}) for k, v in calc.items()}, open(os.path.join(HERE, "calc.json"), "w"), indent=1)
for k, v in calc.items():
    print(k, v if isinstance(v, dict) else round(v, 3))


def F(size, bold=False):
    return ImageFont.truetype("C:/Windows/Fonts/" + ("arialbd.ttf" if bold else "arial.ttf"), size)


GREEN, TEAL, DEEP, INK, INK2 = (21, 138, 82), (14, 122, 106), (15, 107, 64), (16, 32, 26), (74, 91, 82)
AMBER, BLUE, RED = (184, 116, 26), (45, 107, 216), (200, 68, 58)
tint = lambda c, k=.88: tuple(int(x * (1 - k) + 255 * k) for x in c)


def arrow(d, p1, p2, col, w=7, label=None, lpos=None, fs=26):
    d.line([p1, p2], fill=col, width=w)
    a = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    d.polygon([p2, (p2[0] - 28 * math.cos(a - .4), p2[1] - 28 * math.sin(a - .4)),
               (p2[0] - 28 * math.cos(a + .4), p2[1] - 28 * math.sin(a + .4))], fill=col)
    if label:
        x, y = lpos or ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 - 22)
        d.text((x, y), label, font=F(fs, True), fill=col, anchor="mm")


def node(d, x, y, w, h, title, lines, col, r=26):
    d.rounded_rectangle((x, y, x + w, y + h), r, fill=tint(col), outline=col, width=5)
    d.text((x + w / 2, y + 34), title, font=F(32, True), fill=INK, anchor="mm")
    for i, t in enumerate(lines):
        d.text((x + w / 2, y + 76 + i * 34), t, font=F(25), fill=INK2, anchor="mm")


# ------------------------------------------------------------------ diagram alir proses + neraca massa
W, H = 2600, 1150
im = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(im)
node(d, 40, 380, 360, 230, "Food waste", [f"{FW:.1f} kg/d (wet)", f"TS {TS*100:.0f}% · VS/TS {VS_TS*100:.0f}%", f"{vs_d:.3f} kg VS/d"], AMBER)
node(d, 40, 700, 360, 170, "Dilution water", [f"{WATER:.1f} L/d", f"feed TS ≈ {ts_feed:.1f}%"], BLUE)
node(d, 520, 380, 380, 230, "Weigh + shred", ["load cell (HX711)", "twin-shaft, < 10 mm", "camera: waste type"], TEAL)
d.rounded_rectangle((1040, 250, 1640, 900), 40, fill=tint(GREEN, .86), outline=GREEN, width=6)
d.text((1340, 300), "Anaerobic digester", font=F(38, True), fill=INK, anchor="mm")
for i, t in enumerate([f"V_work = {V_WORK} L", f"HRT ≈ {hrt:.0f} d", f"OLR ≈ {olr:.1f} kg VS/m³·d", "T 30–38 °C (mesophilic)",
                       "pH 6.8–7.5 · FOS/TAC < 0.4", "stirring 5 min / 2 h"]):
    d.text((1340, 380 + i * 52), t, font=F(30), fill=INK2, anchor="mm")
d.rectangle((1080, 720, 1600, 860), fill=(205, 190, 150))
d.text((1340, 790), "slurry + biomass", font=F(26, True), fill=INK, anchor="mm")
node(d, 1820, 120, 400, 250, "Biogas", [f"{bg_d*1000:.0f} L/d ({CH4_FRAC*100:.0f}% CH4)", f"{ch4_d*1000:.0f} L CH4/d",
                                        f"{e_d:.1f} MJ/d = {e_d/3.6:.2f} kWh/d"], BLUE)
node(d, 2300, 120, 270, 250, "Stove", [f"{STOVE*1000:.0f} L/h", f"≈ {cook_min:.0f} min/d", f"≈ {lpg_month:.1f} kg LPG/mo"], DEEP)
node(d, 1820, 520, 400, 200, "Liquid digestate", ["tap → fertilizer", "dilute 1 : 10"], GREEN)
node(d, 1820, 800, 400, 200, "Solid digestate", ["drawer → compost", "N, P, K retained"], AMBER)
arrow(d, (400, 495), (520, 495), AMBER)
arrow(d, (400, 785), (1040, 785), BLUE, label="water", lpos=(720, 760))
arrow(d, (900, 495), (1040, 495), TEAL, label=f"{q:.1f} L/d", lpos=(970, 465))
arrow(d, (1640, 330), (1820, 250), BLUE)
arrow(d, (2220, 245), (2300, 245), BLUE)
arrow(d, (1640, 620), (1820, 620), GREEN)
arrow(d, (1640, 860), (1820, 900), AMBER)
d.text((1340, 1062), "Sensors: DS18B20 · pH · NDIR CH4 (0–100 % vol) · ultrasonic level · gas flow · MQ-4 leak alarm",
       font=F(27, True), fill=DEEP, anchor="mm")
d.text((1340, 1112), "Mass basis per day at nominal load; values from design calculation (see equations).",
       font=F(24), fill=INK2, anchor="mm")
im.save(os.path.join(OUT, "sci_pfd.png"))

# ------------------------------------------------------------------ logika kontrol (flowchart)
W, H = 1500, 1500
im = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(im)


def term(x, y, t, col):
    d.rounded_rectangle((x - 230, y - 44, x + 230, y + 44), 44, fill=col)
    d.text((x, y), t, font=F(30, True), fill="white", anchor="mm")


def proc(x, y, t, col=GREEN, w=460):
    d.rounded_rectangle((x - w / 2, y - 48, x + w / 2, y + 48), 14, fill=tint(col), outline=col, width=5)
    d.text((x, y), t, font=F(28, True), fill=INK, anchor="mm")


def dec(x, y, t, col=AMBER):
    d.polygon([(x, y - 80), (x + 250, y), (x, y + 80), (x - 250, y)], fill=tint(col), outline=col)
    d.polygon([(x, y - 80), (x + 250, y), (x, y + 80), (x - 250, y)], outline=col, width=5)
    d.text((x, y), t, font=F(26, True), fill=INK, anchor="mm")


cx = 560
term(cx, 70, "Every 15 min", DEEP)
proc(cx, 200, "Read T, pH, CH4, level, P")
dec(cx, 360, "CH4 leak > 5000 ppm?", RED)
dec(cx, 580, "pH < 6.5 ?")
dec(cx, 800, "T < 30 °C ?")
dec(cx, 1020, "Level > 90 % ?")
proc(cx, 1210, "Stir 5 min if 2 h elapsed")
term(cx, 1360, "Publish to Firebase", DEEP)
for y1, y2 in ((114, 152), (248, 280), (440, 500), (660, 720), (880, 940), (1100, 1162), (1258, 1316)):
    arrow(d, (cx, y1), (cx, y2), INK2, w=5)
acts = [(360, "Close gas valve + alarm", RED), (580, "Pause feeding · alert user", AMBER),
        (800, "Insulation mode · alert", BLUE), (1020, "Prompt: harvest digestate", GREEN)]
for y, t, col in acts:
    arrow(d, (cx + 250, y), (1010, y), col, w=5, label="yes", lpos=(930, y - 26))
    proc(1250, y, t, col, w=440)
    d.text((cx - 40, y + 112), "no", font=F(24, True), fill=INK2, anchor="mm")
im.save(os.path.join(OUT, "sci_control.png"))

# ------------------------------------------------------------------ kinetika Gompertz (parameter literatur, ilustratif)
plt.rcParams.update({"font.family": "Arial", "font.size": 11})
t = np.linspace(0, 30, 300)
P, Rm, lam = 390, 45, 1.5
M = P * np.exp(-np.exp(Rm * math.e / P * (lam - t) + 1))
rate = np.gradient(M, t)
fig, ax = plt.subplots(figsize=(6.4, 3.6), dpi=230)
ax.plot(t, M, color="#158A52", lw=2.6, label="Cumulative CH$_4$ (model)")
ax.axhline(P, color="#158A52", ls=":", lw=1.2)
ax.axhline(bmp_th, color="#B8741A", ls="--", lw=1.4, label=f"Buswell theoretical ({bmp_th})")
ax.set_ylim(0, 700)
ax.set_xlabel("Time (d)")
ax.set_ylabel("mL CH$_4$ / g VS")
ax2 = ax.twinx()
ax2.fill_between(t, rate, color="#2D6BD8", alpha=.15)
ax2.plot(t, rate, color="#2D6BD8", lw=1.6, label="Production rate")
ax2.set_ylabel("mL CH$_4$ / g VS · d")
ax2.set_ylim(0, 60)
ax.annotate(f"λ = {lam} d", xy=(lam, 8), xytext=(4.5, 90), arrowprops=dict(arrowstyle="->", color="#4A5B52"), fontsize=10)
ax.annotate(f"P = {P}", xy=(26, P), xytext=(21, P + 70), fontsize=10, color="#158A52")
ax.annotate(f"R$_m$ = {Rm} mL/g VS·d", xy=(7, 200), xytext=(9.5, 160), fontsize=10, color="#2D6BD8")
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="lower right", frameon=False, fontsize=9)
for a in (ax, ax2):
    a.spines["top"].set_visible(False)
ax.set_title("Modified Gompertz model with literature-range parameters (to be fitted to BMP data)", fontsize=9.5, color="#4A5B52")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "sci_gompertz.png"))
plt.close(fig)

# ------------------------------------------------------------------ sensitivitas: biogas & waktu masak vs input
fig, ax = plt.subplots(figsize=(6.4, 3.4), dpi=230)
x = np.linspace(0.5, 3.0, 50)
bg = x * TS * VS_TS * Y_CH4 / CH4_FRAC * 1000
ax.fill_between(x, x * TS * VS_TS * 0.30 / CH4_FRAC * 1000, x * TS * VS_TS * 0.45 / CH4_FRAC * 1000, color="#D8F0E2",
                label="Y = 0.30–0.45 m³ CH$_4$/kg VS")
ax.plot(x, bg, color="#158A52", lw=2.6, label="Y = 0.38 (design)")
ax.axvline(FW, color="#B8741A", ls="--", lw=1.4)
ax.text(FW + .04, 40, "nominal\n1.5 kg/d", fontsize=9, color="#B8741A")
ax.set_xlabel("Food waste input (kg/d)")
ax.set_ylabel("Biogas (L/d)")
ax3 = ax.twinx()
ax3.set_ylim(np.array(ax.get_ylim()) / (STOVE * 1000) * 60)
ax3.set_ylabel("Cooking time (min/d)")
for a in (ax, ax3):
    a.spines["top"].set_visible(False)
ax.legend(loc="upper left", frameon=False, fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "sci_sensitivity.png"))
plt.close(fig)

# ------------------------------------------------------------------ emisi dihindari per rumah tangga
fig, ax = plt.subplots(figsize=(5.2, 3.2), dpi=230)
labs = ["Landfill CH$_4$\navoided", "LPG\nsubstituted", "Total"]
vals = [co2e_landfill, co2_lpg, co2e_landfill + co2_lpg]
bars = ax.bar(labs, vals, color=["#158A52", "#2D6BD8", "#0F6B40"], width=.55)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width() / 2, v + .02, f"{v:.2f}", ha="center", fontsize=10, fontweight="bold")
ax.set_ylabel("t CO$_2$e / household / year")
ax.set_ylim(0, 0.9)
ax.spines[["top", "right"]].set_visible(False)
ax.set_title("Potential at 1.5 kg/d (IPCC 2006 FOD defaults, GWP$_{100}$ = 28)", fontsize=9, color="#4A5B52")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "sci_ghg.png"))
plt.close(fig)
print("figures ok")
