"""
Ekspor deck ke PDF + PNG per slide via PowerPoint COM (Windows), lalu buat contact sheet untuk QA.

  python design/showcase/deck/export_qa.py en
"""
import glob
import os
import subprocess
import sys

from PIL import Image

LANG = sys.argv[1] if len(sys.argv) > 1 else "en"
HERE = os.path.dirname(os.path.abspath(__file__))
pptx = os.path.join(HERE, f"ARUNA_deck_{LANG}.pptx")
pdf = os.path.join(HERE, f"ARUNA_deck_{LANG}.pdf")
pngdir = os.path.join(HERE, f"_png_{LANG}")
os.makedirs(pngdir, exist_ok=True)
for f in set(glob.glob(os.path.join(pngdir, "*.png"))):
    os.remove(f)
ps = f"""
$app = New-Object -ComObject PowerPoint.Application
$p = $app.Presentations.Open('{pptx}', $true, $false, $false)
$p.SaveAs('{pdf}', 32)
$i = 1
foreach ($s in $p.Slides) {{ $s.Export('{pngdir}\\s' + $i.ToString('00') + '.png', 'PNG', 1600, 900); $i++ }}
$p.Close(); $app.Quit()
"""
for attempt in range(3):  # COM PowerPoint kadang gagal saat baru start
    subprocess.run(["powershell", "-NoProfile", "-Command", ps])
    if os.path.exists(os.path.join(pngdir, "s01.png")):
        break
fs = sorted(glob.glob(os.path.join(pngdir, "s*.png")))
cols = 4
tw, th = 640, 360
sheet = Image.new("RGB", (tw * cols, th * ((len(fs) + cols - 1) // cols)), "white")
for i, f in enumerate(fs):
    sheet.paste(Image.open(f).convert("RGB").resize((tw, th)), ((i % cols) * tw, (i // cols) * th))
sheet.save(os.path.join(HERE, f"_contact_{LANG}.png"))
print("[QA]", len(fs), "slide ->", pdf)
