"""
Rakit video use case portrait ARUNA (1080x1920, 30 fps, ±28 s) dari frame Blender + layer PIL + musik synth.

  python design/showcase/video/edit.py
Masukan : frames/f_####.png (scene.py), ../../app/screens/*.png, ../../app/img/mesin.png
Keluaran: ARUNA_usecase_portrait.mp4
"""
import glob
import math
import os
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.abspath(os.path.join(HERE, "..", ".."))
FR = os.path.join(HERE, "frames")
OUTF = os.path.join(HERE, "_edit")
os.makedirs(OUTF, exist_ok=True)
FF = glob.glob(os.path.join(os.environ["LOCALAPPDATA"], "Microsoft/WinGet/Packages/Gyan.FFmpeg*/ffmpeg-*/bin/ffmpeg.exe"))[0]
W, H, FPS = 1080, 1920, 30

INK, INK2, MUTED = (16, 32, 26), (74, 91, 82), (134, 149, 141)
GREEN, SOFT, WHITE = (21, 138, 82), (227, 243, 234), (255, 255, 255)
BG_T, BG_B = (250, 253, 251), (221, 237, 228)


def font(size, weight="b"):
    f = {"b": "segoeuib.ttf", "r": "segoeui.ttf", "sb": "seguisb.ttf", "k": "seguibl.ttf"}[weight]
    for cand in (f, "segoeuib.ttf"):
        p = os.path.join("C:/Windows/Fonts", cand)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


ease = lambda t: 1 - (1 - min(max(t, 0), 1)) ** 3


def bg():
    g = np.linspace(0, 1, H)[:, None, None]
    a = np.array(BG_T)[None, None, :] * (1 - g) + np.array(BG_B)[None, None, :] * g
    return Image.fromarray(np.repeat(a, W, axis=1).astype(np.uint8)).convert("RGBA")


BG = bg()


def card(w, h, r=46, alpha=242):
    pad = 60
    im = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle((pad + 6, pad + 24, pad + w, pad + h + 24), r, fill=90)
    im.putalpha(0)
    shadow = Image.new("RGBA", im.size, (20, 90, 60, 0))
    shadow.putalpha(sh.filter(ImageFilter.GaussianBlur(28)))
    im.alpha_composite(shadow)
    ImageDraw.Draw(im).rounded_rectangle((pad, pad, pad + w, pad + h), r, fill=(255, 255, 255, alpha),
                                         outline=(255, 255, 255, 255), width=2)
    return im, pad


def logo(size=64):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, size - 1, size - 1), int(size * 0.3), fill=GREEN)
    c = size // 2
    r = int(size * 0.17)
    d.ellipse((c - r, c - r, c + r, c + r), fill=WHITE)
    return im


def caption_layer(step, chip, l1, l2, sub, t_in):
    """Kartu caption di bawah, masuk dari bawah + fade (t_in detik sejak mulai shot)."""
    k = ease(t_in / 0.55)
    if k <= 0:
        return None, 0
    cw, chh = 940, 330
    c, pad = card(cw, chh)
    d = ImageDraw.Draw(c)
    x0, y0 = pad + 52, pad + 44
    if step:
        d.ellipse((x0, y0, x0 + 58, y0 + 58), fill=GREEN)
        d.text((x0 + 29, y0 + 29), step, font=font(32), fill=WHITE, anchor="mm")
        cx = x0 + 76
    else:
        cx = x0
    d.rounded_rectangle((cx, y0 + 6, cx + 26 + d.textlength(chip, font=font(25, "b")), y0 + 52), 23, fill=SOFT)
    d.text((cx + 13, y0 + 29), chip, font=font(25, "b"), fill=GREEN, anchor="lm")
    d.text((x0, y0 + 84), l1, font=font(62, "b"), fill=INK)
    d.text((x0, y0 + 154), l2, font=font(62, "b"), fill=GREEN)
    d.text((x0, y0 + 236), sub, font=font(32, "r"), fill=INK2)
    a = c.getchannel("A").point(lambda v: int(v * k))
    c.putalpha(a)
    return c, int((1 - k) * 80)


SHOTS = [  # (mulai, akhir, nomor, chip, baris1, baris2, sub)
    (1, 57, "", "SISA MAKAN MALAM", "Jangan dibuang,", "masukkan ke ARUNA.", "Mesin biodigester rumahan setinggi pinggang."),
    (58, 120, "1", "MASUKKAN", "Buka tutup,", "tuang sisa makanan.", "Timbangan & kamera mencatat otomatis."),
    (121, 200, "2", "CERNA OTOMATIS", "Dicacah, diaduk,", "dicerna ±34 hari.", "Sensor suhu, pH, dan metana menjaga prosesnya."),
    (201, 290, "3", "PANTAU", "Semua kabar", "langsung di HP.", "Notifikasi saat pupuk & gas siap."),
    (291, 380, "4", "PUPUK CAIR", "Tanaman subur,", "tanpa beli pupuk.", "Encerkan 1:10, siram seperti biasa."),
    (381, 470, "5", "BIOGAS", "Api biru", "untuk memasak.", "Target ±45 menit memasak per hari."),
    (471, 560, "", "ARUNA", "Sisa makanan", "jadi energi.", "Smart biodigester untuk setiap dapur."),
]


def shot_of(f):
    for s in SHOTS:
        if s[0] <= f <= s[1]:
            return s
    return SHOTS[-1]


LOGO = logo(72)
FLOGO = font(34, "b")
COUNT = [0]


class _Out:
    def append(self, im):
        im.convert("RGB").save(os.path.join(OUTF, f"e_{COUNT[0]:04d}.jpg"), quality=94)
        COUNT[0] += 1


frames = _Out()

# ------------------------------------------------------------------ 1) intro 2,5 s
mesin = Image.open(os.path.join(DESIGN, "app", "img", "mesin.png")).convert("RGBA")
mesin = mesin.resize((int(mesin.width * 0.95), int(mesin.height * 0.95)), Image.LANCZOS)
N_INTRO = 75
for i in range(N_INTRO):
    t = i / FPS
    im = BG.copy()
    k1, k2, k3 = ease(t / 0.7), ease((t - 0.35) / 0.7), ease((t - 0.7) / 0.8)
    m = mesin.copy()
    m.putalpha(m.getchannel("A").point(lambda v: int(v * k3)))
    im.alpha_composite(m, ((W - m.width) // 2, int(700 + (1 - k3) * 120)))
    lg = logo(120)
    lg.putalpha(lg.getchannel("A").point(lambda v: int(v * k1)))
    im.alpha_composite(lg, ((W - 120) // 2, int(260 + (1 - k1) * 40)))
    d = ImageDraw.Draw(im)
    f1 = font(150, "b")
    txt = "ARUNA"
    d.text((W // 2, 470 + (1 - k2) * 40), txt, font=f1, fill=INK + (int(255 * k2),), anchor="mm")
    d.text((W // 2, 590 + (1 - k2) * 40), "sisa makanan → energi", font=font(44, "sb"), fill=GREEN + (int(255 * k2),), anchor="mm")
    frames.append(im)

# ------------------------------------------------------------------ 2) 3D + caption
src = sorted(glob.glob(os.path.join(FR, "f_*.png")))
assert len(src) >= 560, f"frame 3D baru {len(src)}"
for path in src[:560]:
    f = int(os.path.basename(path)[2:6])
    im = Image.open(path).convert("RGBA")
    if im.size != (W, H):
        im = im.resize((W, H), Image.LANCZOS)
    s = shot_of(f)
    # vignette tipis bawah supaya caption terbaca
    lay, dy = caption_layer(s[2], s[3], s[4], s[5], s[6], (f - s[0]) / FPS)
    if lay is not None:
        im.alpha_composite(lay, ((W - lay.width) // 2, H - lay.height - 70 + dy))
    im.alpha_composite(LOGO, (W - 72 - 56, 70))
    ImageDraw.Draw(im).text((W - 56 - 72 - 18, 106), "ARUNA", font=FLOGO, fill=INK, anchor="rm")
    frames.append(im)

# ------------------------------------------------------------------ 3) segmen aplikasi 4 s
scr = []
for k in ("home", "monitor", "chat"):
    s_ = Image.open(os.path.join(DESIGN, "app", "screens", f"{k}.png")).convert("RGBA").resize((450, 974), Image.LANCZOS)
    mask = Image.new("L", s_.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, s_.width - 1, s_.height - 1), 56, fill=255)
    fr_ = Image.new("RGBA", (s_.width + 24, s_.height + 24), (0, 0, 0, 0))
    ImageDraw.Draw(fr_).rounded_rectangle((0, 0, fr_.width - 1, fr_.height - 1), 66, fill=(245, 248, 246, 255),
                                          outline=(210, 220, 214, 255), width=3)
    fr_.paste(s_, (12, 12), mask)
    scr.append(fr_)
N_APP = 120
for i in range(N_APP):
    t = i / FPS
    im = BG.copy()
    d = ImageDraw.Draw(im)
    k = ease(t / 0.6)
    d.text((W // 2, 250), "Aplikasi ARUNA", font=font(76, "b"), fill=INK + (int(255 * k),), anchor="mm")
    d.text((W // 2, 335), "status · notifikasi panen · tanya AI", font=font(38, "r"), fill=INK2 + (int(255 * k),), anchor="mm")
    for j, p in enumerate(scr):
        kj = ease((t - 0.25 - j * 0.22) / 0.7)
        if kj <= 0:
            continue
        x = W // 2 - p.width // 2 + (j - 1) * 330
        y = 470 + (0 if j == 1 else 90) + int((1 - kj) * 260) - int(10 * math.sin(t * 2 + j))
        q = p.copy()
        sc_ = 1.0 if j == 1 else 0.86
        if sc_ != 1:
            q = q.resize((int(q.width * sc_), int(q.height * sc_)), Image.LANCZOS)
            x += int(p.width * (1 - sc_) / 2)
        q.putalpha(q.getchannel("A").point(lambda v: int(v * kj)))
        if j != 1:
            im.alpha_composite(q, (x, y))
    for j, p in enumerate(scr):
        if j == 1:
            kj = ease((t - 0.25 - j * 0.22) / 0.7)
            if kj > 0:
                q = p.copy()
                q.putalpha(q.getchannel("A").point(lambda v: int(v * kj)))
                im.alpha_composite(q, (W // 2 - p.width // 2, 470 + int((1 - kj) * 260) - int(10 * math.sin(t * 2 + 1))))
    frames.append(im)

# ------------------------------------------------------------------ 4) outro 3 s
N_OUT = 90
small = mesin.resize((int(mesin.width * 0.72), int(mesin.height * 0.72)), Image.LANCZOS)  # ~0,68x asli
for i in range(N_OUT):
    t = i / FPS
    im = BG.copy()
    k = ease(t / 0.7)
    m = small.copy()
    m.putalpha(m.getchannel("A").point(lambda v: int(v * k)))
    im.alpha_composite(m, ((W - m.width) // 2, 680 + int((1 - k) * 80)))
    lg = logo(110)
    im.alpha_composite(lg, ((W - 110) // 2, 230))
    d = ImageDraw.Draw(im)
    d.text((W // 2, 450), "ARUNA", font=font(130, "b"), fill=INK, anchor="mm")
    d.text((W // 2, 560), "Mulai dari piring malam ini.", font=font(48, "sb"), fill=GREEN, anchor="mm")
    kb = ease((t - 0.6) / 0.6)
    c, pad = card(620, 110, r=55)
    c.putalpha(c.getchannel("A").point(lambda v: int(v * kb)))
    im.alpha_composite(c, ((W - c.width) // 2, 1640 - pad))
    d.text((W // 2, 1640 + 55), "aruna-id.web.app", font=font(46, "b"), fill=GREEN + (int(255 * kb),), anchor="mm")
    d.text((W // 2, 1850), "Karakter 3D: sthaarpit (Sketchfab, CC-BY 4.0) · rig Rigify", font=font(24, "r"),
           fill=MUTED + (int(255 * kb),), anchor="mm")
    frames.append(im)

# ------------------------------------------------------------------ tulis frame
N = COUNT[0]
dur = N / FPS
print("[EDIT] frame:", N, "durasi", round(dur, 2), "s")

# ------------------------------------------------------------------ musik synth (pad + pluck), bebas lisensi
SR = 44100
tt = np.arange(int(SR * dur)) / SR
CH = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 52, 55, 60], [55, 59, 62, 67]]  # Am F C G
hz = lambda n: 440 * 2 ** ((n - 69) / 12)
bar = 2.0
music = np.zeros_like(tt)
for b in range(int(dur / bar) + 1):
    t0 = b * bar
    seg = (tt >= t0) & (tt < t0 + bar + 0.6)
    ts = tt[seg] - t0
    env = np.minimum(ts / 0.4, 1) * np.exp(-np.maximum(ts - bar, 0) * 4)
    for n in CH[b % 4]:
        music[seg] += 0.05 * env * (np.sin(2 * np.pi * hz(n) * ts) + 0.3 * np.sin(2 * np.pi * hz(n) * 2.005 * ts))
    for j in range(8):
        tp = ts - j * 0.25
        pk = (tp >= 0)
        note = CH[b % 4][(j * 3) % 4] + 12
        music[seg] += pk * 0.07 * np.exp(-np.maximum(tp, 0) * 9) * np.sin(2 * np.pi * hz(note) * np.maximum(tp, 0))
kick = np.zeros_like(tt)
for b in np.arange(0, dur, 0.5):
    tp = tt - b
    m = (tp >= 0) & (tp < 0.3)
    kick[m] += 0.25 * np.exp(-tp[m] * 18) * np.sin(2 * np.pi * (55 + 90 * np.exp(-tp[m] * 30)) * tp[m])
mix = music + kick * (tt > 2.5)
fade = np.minimum(1, tt / 0.8) * np.minimum(1, (dur - tt) / 1.2)
mix = np.clip(mix * fade / (np.abs(mix).max() + 1e-9) * 0.9, -1, 1)
wav = os.path.join(HERE, "_music.wav")
with wave.open(wav, "w") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())

out = os.path.join(HERE, "ARUNA_usecase_portrait.mp4")
subprocess.run([FF, "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(OUTF, "e_%04d.jpg"), "-i", wav,
                "-af", "loudnorm=I=-17:TP=-1.5", "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
print("[EDIT]", out, os.path.getsize(out) // 1024, "KB")
