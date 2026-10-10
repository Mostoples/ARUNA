"""
Figur untuk full paper & poster A0 (bahasa Inggris).

  python design/competition/make_figures.py
Keluaran: design/competition/fig/*.png
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.dirname(HERE)
SHOW = os.path.join(DESIGN, "showcase")
OUT = os.path.join(HERE, "fig")
os.makedirs(OUT, exist_ok=True)

GREEN, TEAL, DEEP, INK, INK2 = (21, 138, 82), (14, 122, 106), (15, 107, 64), (16, 32, 26), (74, 91, 82)
AMBER, BLUE = (184, 116, 26), (45, 107, 216)


def F(size, bold=False):
    return ImageFont.truetype("C:/Windows/Fonts/" + ("arialbd.ttf" if bold else "arial.ttf"), size)


# ------------------------------------------------------------------ Fig: produk (render luar + x-ray berdampingan)
def flatten(im, bg=(255, 255, 255)):
    b = Image.new("RGBA", im.size, bg + (255,))
    b.alpha_composite(im.convert("RGBA"))
    return b.convert("RGB")


outer = Image.open(os.path.join(SHOW, "deck", "assets", "hw_outer.png")).crop((300, 160, 1200, 1700))
xray = Image.open(os.path.join(SHOW, "deck", "assets", "hw_xray.png"))
PTS = json.load(open(os.path.join(SHOW, "deck", "assets", "hw_points.json")))

# x-ray beranotasi (callout kiri/kanan, garis tidak bersilang)
CROP = (0.2, 0.1, 0.8, 0.95)
W0, H0 = xray.size
xc = xray.crop((int(CROP[0] * W0), int(CROP[1] * H0), int(CROP[2] * W0), int(CROP[3] * H0)))
scale = 1100 / xc.height
xc = xc.resize((int(xc.width * scale), 1100), Image.LANCZOS)
PAD = 560
can = Image.new("RGBA", (xc.width + 2 * PAD, 1180), (255, 255, 255, 255))
can.alpha_composite(xc, (PAD, 40))
d = ImageDraw.Draw(can)
LAB = {"pencacah": "Twin-shaft shredder", "loadcell": "Load cell (HX711)", "layar": "7\" panel + ESP32-S3",
       "suhu": "Temperature (DS18B20)", "keran": "Liquid fertilizer tap", "kompos": "Compost drawer",
       "level": "Ultrasonic level", "gas": "CH4 NDIR (MH-440D)", "pengaduk": "Auto stirrer",
       "ph": "pH probe", "gauge": "Gas gauge + valve"}
SIDE = {"pencacah": "L", "loadcell": "L", "layar": "L", "suhu": "L", "keran": "L", "kompos": "L",
        "level": "R", "gas": "R", "pengaduk": "R", "ph": "R", "gauge": "R"}


def px(k):
    u, v = PTS[k]
    return (PAD + (u - CROP[0]) / (CROP[2] - CROP[0]) * xc.width, 40 + (v - CROP[1]) / (CROP[3] - CROP[1]) * xc.height)


for side in ("L", "R"):
    ks = sorted([k for k in LAB if SIDE[k] == side], key=lambda k: PTS[k][1])
    for i, k in enumerate(ks):
        x, y = px(k)
        ly = 120 + i * (940 / max(1, len(ks) - 1))
        lx = PAD - 30 if side == "L" else PAD + xc.width + 30
        d.line([(x, y), (lx, ly)], fill=GREEN, width=4)
        d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=GREEN, outline="white", width=3)
        f = F(34, True)
        tw = d.textlength(LAB[k], font=f)
        tx = lx - tw - 10 if side == "L" else lx + 10
        d.text((tx, ly - 20), LAB[k], font=f, fill=INK)
fig_xray = can.convert("RGB")
fig_xray.save(os.path.join(OUT, "fig_hardware_xray.png"))

o = flatten(outer)
o = o.resize((int(o.width * 1100 / o.height), 1100), Image.LANCZOS)
prod = Image.new("RGB", (o.width + 80, 1180), "white")
prod.paste(o, (40, 40))
prod.save(os.path.join(OUT, "fig_product.png"))

# ------------------------------------------------------------------ Fig: arsitektur sistem
W, H = 2400, 1000
im = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(im)


def box(x, y, w, h, title, sub, col):
    d.rounded_rectangle((x, y, x + w, y + h), 36, fill=tuple(int(c * .12 + 255 * .88) for c in col), outline=col, width=6)
    d.text((x + w / 2, y + h / 2 - 28), title, font=F(46, True), fill=INK, anchor="mm")
    d.text((x + w / 2, y + h / 2 + 34), sub, font=F(32), fill=INK2, anchor="mm")


def arrow(x1, y1, x2, y2, label="", col=GREEN):
    d.line([(x1, y1), (x2, y2)], fill=col, width=8)
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    for s in (2.6, -2.6):
        d.line([(x2, y2), (x2 - 34 * math.cos(a + s / 6), y2 - 34 * math.sin(a + s / 6))], fill=col, width=8)
    if label:
        d.text(((x1 + x2) / 2, (y1 + y2) / 2 - 34), label, font=F(30, True), fill=col, anchor="mm")


box(60, 120, 470, 300, "Sensors", "temp · pH · CH4 · level · weight", TEAL)
box(60, 600, 470, 300, "Actuators", "shredder · stirrer · valve", AMBER)
box(760, 330, 470, 340, "ESP32-S3", "controller + camera", GREEN)
box(1460, 330, 470, 340, "Firebase", "RTDB · Firestore · Auth", (190, 120, 20))
box(2000, 120, 360, 300, "Web app", "PWA · alerts", BLUE)
box(2000, 600, 360, 300, "AI educator", "Q&A from data", DEEP)
arrow(530, 270, 760, 430)
d.text((690, 300), "readings", font=F(30, True), fill=GREEN, anchor="mm")
arrow(760, 570, 530, 750, "", AMBER)
d.text((690, 720), "commands", font=F(30, True), fill=AMBER, anchor="mm")
arrow(1230, 500, 1460, 500, "Wi-Fi / MQTT")
arrow(1930, 430, 2000, 300)
arrow(1930, 570, 2000, 730)
d.text((995, 760), "BLE provisioning (offline setup)", font=F(30, True), fill=BLUE, anchor="mm")
d.line([(995, 670), (995, 735)], fill=BLUE, width=6)
im.save(os.path.join(OUT, "fig_architecture.png"))

# ------------------------------------------------------------------ Fig: alur metode 4D
W, H = 2400, 760
im = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(im)
ST = [("1  Define", ["food-waste audit", "user needs survey", "requirement list"], TEAL),
      ("2  Design", ["3D CAD & sizing", "sensor/IoT architecture", "app UX prototype"], GREEN),
      ("3  Develop", ["prototype build", "lab digestion test", "expert validation"], DEEP),
      ("4  Disseminate", ["household field test", "SUS questionnaire", "evaluation & revision"], AMBER)]
bw = 520
for i, (t, items, col) in enumerate(ST):
    x = 40 + i * (bw + 80)
    d.rounded_rectangle((x, 60, x + bw, 700), 40, fill=tuple(int(c * .10 + 255 * .90) for c in col), outline=col, width=6)
    d.rounded_rectangle((x, 60, x + bw, 190), 40, fill=col)
    d.rectangle((x, 150, x + bw, 190), fill=col)
    d.text((x + bw / 2, 125), t, font=F(52, True), fill="white", anchor="mm")
    for j, it in enumerate(items):
        d.ellipse((x + 40, 268 + j * 130, x + 64, 292 + j * 130), fill=col)
        d.text((x + 86, 280 + j * 130), it, font=F(38), fill=INK, anchor="lm")
    if i < 3:
        ax = x + bw + 12
        d.polygon([(ax, 350), (ax + 56, 380), (ax, 410)], fill=col)
im.save(os.path.join(OUT, "fig_method_4d.png"))

# ------------------------------------------------------------------ Fig: layar aplikasi
scr = [Image.open(os.path.join(DESIGN, "app", "screens", f"{k}.png")).convert("RGB").resize((585, 1266), Image.LANCZOS)
       for k in ("home", "monitor", "chat", "device")]
W = 585 * 4 + 60 * 5
im = Image.new("RGB", (W, 1266 + 180), "white")
d = ImageDraw.Draw(im)
for i, (s, lab) in enumerate(zip(scr, ("Home", "Monitoring", "AI educator", "Device"))):
    x = 60 + i * (585 + 60)
    mask = Image.new("L", s.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, s.width - 1, s.height - 1), 70, fill=255)
    d.rounded_rectangle((x - 8, 32, x + 585 + 8, 32 + 1266 + 16), 78, fill=(220, 228, 224))
    im.paste(s, (x, 40), mask)
    d.text((x + 292, 1266 + 110), lab, font=F(50, True), fill=INK, anchor="mm")
im.save(os.path.join(OUT, "fig_app.png"))

# ------------------------------------------------------------------ Fig: grafik (ILUSTRASI - diberi watermark)
plt.rcParams.update({"font.family": "Arial", "font.size": 11})
days = list(range(1, 15))
ch4 = [8, 15, 22, 29, 35, 41, 46, 50, 53, 55, 57, 58, 58, 59]
temp = [33.1, 34.0, 34.8, 35.2, 35.6, 35.9, 36.1, 36.2, 36.4, 36.3, 36.5, 36.4, 36.4, 36.5]
fig, ax = plt.subplots(figsize=(7.2, 3.4), dpi=220)
ax.axhspan(50, 70, color="#D8F0E2", label="Target CH$_4$ ≥ 50%")
ax.plot(days, ch4, "-o", color="#158A52", lw=2.4, ms=5, label="CH$_4$ content (%)")
ax.set_xlabel("Digestion day")
ax.set_ylabel("CH$_4$ (%)")
ax.set_ylim(0, 70)
ax2 = ax.twinx()
ax2.plot(days, temp, "--", color="#B8741A", lw=2, label="Temperature (°C)")
ax2.set_ylabel("Temperature (°C)")
ax2.set_ylim(30, 40)
for a in (ax, ax2):
    a.spines["top"].set_visible(False)
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="lower right", frameon=False, fontsize=9)
ax.text(0.01, 0.97, "ILLUSTRATIVE TARGET CURVE – replace with measured data", transform=ax.transAxes,
        fontsize=8.5, color="#B8741A", fontweight="bold", va="top")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig_results_ch4.png"))
print("figures:", sorted(os.listdir(OUT)))
