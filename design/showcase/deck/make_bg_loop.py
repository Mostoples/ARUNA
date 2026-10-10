"""
Video latar looping mulus untuk deck (1920x1080, 10 s, 30 fps).
Gradien mint + aura hijau yang berputar + gelembung biogas naik. Semua gerak periodik
terhadap T sehingga frame terakhir menyambung ke frame pertama.

  python design/showcase/deck/make_bg_loop.py
Keluaran: design/showcase/deck/assets/bg_loop.mp4 (+ bg_poster.png)
"""
import glob
import math
import os
import subprocess

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets")
TMP = os.path.join(HERE, "_bgframes")
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)
FF = glob.glob(os.path.join(os.environ["LOCALAPPDATA"], "Microsoft/WinGet/Packages/Gyan.FFmpeg*/ffmpeg-*/bin/ffmpeg.exe"))[0]

W, H = 960, 540            # dirender setengah, di-upscale (konten lembut)
FPS, SEC = 30, 10
N = FPS * SEC
rng = np.random.default_rng(7)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

top = np.array([0.975, 0.99, 0.98])        # #F9FCFA
bot = np.array([0.89, 0.95, 0.915])        # #E3F2E9
base = top[None, None, :] * (1 - yy[..., None] / H) + bot[None, None, :] * (yy[..., None] / H)

BLOBS = [  # (cx, cy, rx, ry, radius, warna, alpha, fase)
    (0.82, 0.18, 0.08, 0.06, 0.42, (0.13, 0.66, 0.40), 0.20, 0.0),
    (0.12, 0.85, 0.07, 0.05, 0.38, (0.05, 0.48, 0.42), 0.16, 1.7),
    (0.55, 0.62, 0.10, 0.07, 0.30, (0.55, 0.85, 0.66), 0.18, 3.1),
    (0.30, 0.20, 0.06, 0.08, 0.26, (0.70, 0.90, 0.78), 0.20, 4.4),
]
NB = 26
bub = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(4, 13), int(rng.integers(1, 3)), rng.uniform(0, 6.28),
        rng.uniform(8, 22)) for _ in range(NB)]

for f in range(N):
    path = os.path.join(TMP, f"b_{f:04d}.png")
    if os.path.exists(path):
        continue
    t = f / N                                  # 0..1, periodik
    img = base.copy()
    for cx, cy, rx, ry, rad, col, a, ph in BLOBS:
        x = (cx + rx * math.cos(2 * math.pi * t + ph)) * W
        y = (cy + ry * math.sin(2 * math.pi * t + ph)) * H
        r = rad * W
        g = np.exp(-(((xx - x) ** 2 + (yy - y) ** 2) / (2 * (r * 0.5) ** 2)))
        img = img * (1 - a * g[..., None]) + np.array(col) * (a * g[..., None])
    for x0, y0, r, k, ph, sway in bub:
        y = (y0 - t * k * H) % (H + 40) - 20      # naik k kali layar per loop -> mulus
        x = x0 + sway * math.sin(2 * math.pi * (t * k) + ph)
        d = np.sqrt((xx - x) ** 2 + (yy - y) ** 2)
        ring = np.clip(1 - np.abs(d - r) / 1.6, 0, 1) * 0.55 + np.clip(1 - d / r, 0, 1) * 0.10
        hl = np.clip(1 - np.sqrt((xx - x + r * 0.35) ** 2 + (yy - y + r * 0.35) ** 2) / (r * 0.35), 0, 1) * 0.6
        m = np.clip(ring + hl, 0, 1)[..., None]
        img = img * (1 - m * 0.5) + np.array([1.0, 1.0, 1.0]) * (m * 0.5)
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(path)
    if f % 60 == 0:
        print("bg", f, "/", N)

subprocess.run([FF, "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(TMP, "b_%04d.png"),
                "-vf", "scale=1920:1080:flags=lanczos,format=yuv420p", "-c:v", "libx264", "-crf", "24",
                "-preset", "slow", "-movflags", "+faststart", "-an", os.path.join(OUT, "bg_loop.mp4")], check=True)
Image.open(os.path.join(TMP, "b_0000.png")).resize((1920, 1080), Image.LANCZOS).save(os.path.join(OUT, "bg_poster.png"))
a = np.asarray(Image.open(os.path.join(TMP, "b_0000.png")), dtype=np.float32)
b = np.asarray(Image.open(os.path.join(TMP, f"b_{N - 1:04d}.png")), dtype=np.float32)
print("selisih frame akhir->awal (rata-rata /255):", round(float(np.abs(a - b).mean()), 3))
print("ok", os.path.getsize(os.path.join(OUT, "bg_loop.mp4")) // 1024, "KB")
