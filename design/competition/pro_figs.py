"""Grafik poster 'Living Ledger': palet hutan/saffron/sage, font Instrument Sans + Geist Mono."""
import json, math, os
import matplotlib; matplotlib.use("Agg")
from matplotlib import font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "fig")
for f in os.listdir(os.path.join(HERE, "_poster", "fonts")):
    fm.fontManager.addfont(os.path.join(HERE, "_poster", "fonts", f))
C = json.load(open(os.path.join(HERE, "calc.json"))); NM, H4, MX = C["nominal"], C["hh4"], C["max"]
FOREST, SAFF, SAGE, TEAL, INK, MUTE, PAPER = "#0C3B2E", "#E89B2D", "#8FB9A0", "#1F7A6C", "#16241E", "#6E7B73", "#F6F2E9"
plt.rcParams.update({"font.family": "Instrument Sans", "font.size": 17, "text.color": INK, "axes.labelcolor": INK,
                     "axes.edgecolor": MUTE, "xtick.color": MUTE, "ytick.color": MUTE, "axes.linewidth": 1.0,
                     "xtick.major.width": 1, "ytick.major.width": 1, "axes.facecolor": "none", "figure.facecolor": "none"})
MONO = {"family": "Geist Mono", "size": 13, "color": MUTE}

def tidy(ax):
    ax.spines[["top", "right"]].set_visible(False); ax.grid(axis="y", color="#D9D3C4", lw=.8); ax.set_axisbelow(True)
    for t in ax.get_xticklabels() + ax.get_yticklabels(): t.set_fontfamily("Geist Mono"); t.set_fontsize(13)

# 1 kinetika
t = np.linspace(0, 30, 300); P, Rm, lam = 390, 45, 1.5
M = P * np.exp(-np.exp(Rm * math.e / P * (lam - t) + 1)); r = np.gradient(M, t)
fig, ax = plt.subplots(figsize=(7.6, 4.6), dpi=220)
ax.axhline(643, color=MUTE, ls=(0, (4, 4)), lw=1.2); ax.text(30, 655, "theoretical (Buswell) 643", ha="right", **MONO)
ax.fill_between(t, M, color=SAGE, alpha=.35, lw=0); ax.plot(t, M, color=FOREST, lw=3.2)
ax.plot(t, r * 8, color=SAFF, lw=2.4); ax.text(5.6, 45 * 8 + 12, "rate × 8", color=SAFF, fontfamily="Geist Mono", fontsize=13)
ax.text(29.5, P + 14, f"P = {P} mL/g VS", ha="right", fontweight="bold", color=FOREST)
ax.annotate(f"λ = {lam} d", xy=(lam, 6), xytext=(4.8, 70), arrowprops=dict(arrowstyle="-", color=MUTE, lw=1), **MONO)
ax.set_xlim(0, 30); ax.set_ylim(0, 720); ax.set_xlabel("Digestion time (d)"); ax.set_ylabel("Cumulative CH$_4$ (mL/g VS)")
tidy(ax); fig.tight_layout(); fig.savefig(os.path.join(OUT, "pro_gompertz.png")); plt.close(fig)

# 2 sensitivitas
x = np.linspace(.5, 3, 60); k = .25 * .90 / .60 * 1000
fig, ax = plt.subplots(figsize=(7.6, 4.6), dpi=220)
ax.axvspan(2.5, 3.0, color=SAFF, alpha=.12, lw=0); ax.text(2.55, 470, "VFA risk\nHRT < 20 d", color=SAFF, fontfamily="Geist Mono", fontsize=13, va="top")
ax.fill_between(x, x * k * .30, x * k * .45, color=SAGE, alpha=.35, lw=0); ax.plot(x, x * k * .38, color=FOREST, lw=3.2)
ax.plot([1.5], [1.5 * k * .38], "o", ms=12, color=SAFF, mec=PAPER, mew=3, zorder=5)
ax.annotate(f"{NM['bg']:.0f} L/d  ·  {NM['cook']:.0f} min", xy=(1.5, 1.5 * k * .38), xytext=(.55, 330),
            fontweight="bold", color=FOREST, arrowprops=dict(arrowstyle="-", color=FOREST, lw=1))
ax.text(3.0, 40, "band: Y = 0.30–0.45 m³ CH₄/kg VS", ha="right", **MONO)
ax.set_xlim(.5, 3); ax.set_ylim(0, 500); ax.set_xlabel("Food-waste input (kg/d)"); ax.set_ylabel("Biogas (L/d)")
tidy(ax); fig.tight_layout(); fig.savefig(os.path.join(OUT, "pro_sens.png")); plt.close(fig)

# 3 emisi
fig, ax = plt.subplots(figsize=(5.6, 4.6), dpi=220)
lab = ["Home of 4", "Nominal", "Peak"]; v = [H4["co2e"], NM["co2e"], MX["co2e"]]
b = ax.bar(lab, v, color=[SAGE, FOREST, SAFF], width=.56)
for bb, val in zip(b, v): ax.text(bb.get_x() + bb.get_width() / 2, val + .04, f"{val:.2f}", ha="center", fontweight="bold", fontsize=19)
ax.set_ylim(0, 1.7); ax.set_ylabel("t CO$_2$e avoided per year"); tidy(ax)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "pro_ghg.png")); plt.close(fig)
print("ok")
