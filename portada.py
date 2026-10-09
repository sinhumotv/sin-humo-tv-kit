#!/usr/bin/env python3
"""Portada 1080x1920: fotograma + titular grande (máx. 4 palabras) + marca.
Uso: python3 portada.py <proyecto> <segundo> "<titular>" """
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

D, T, TIT = sys.argv[1], float(sys.argv[2]), sys.argv[3]
KIT = os.path.dirname(os.path.abspath(__file__))
foto = os.path.join(D, "_portada_base.png")
subprocess.run(["node", os.path.join(KIT, "render.js"), D, "foto", str(T), foto], check=True)
im = Image.open(foto).convert("RGB")
d = ImageDraw.Draw(im)
INK, ORA, CRE = (0x2a, 0x24, 0x33), (0xf0, 0x7d, 0x2a), (0xfb, 0xf3, 0xdf)
negra = os.path.join(KIT, "fonts", "Inter-Black.otf")
# titular en hasta 2 líneas, lo más grande que quepa en 960 px
pal = TIT.split()
lineas = [" ".join(pal[:(len(pal) + 1) // 2]), " ".join(pal[(len(pal) + 1) // 2:])] if len(pal) > 2 else [TIT]
size = 190
while size > 60:
    f = ImageFont.truetype(negra, size)
    if max(d.textlength(l, font=f) for l in lineas) <= 960: break
    size -= 6
f = ImageFont.truetype(negra, size)
alto = len(lineas) * size * 1.08 + 80
y0 = 1380 - alto / 2
d.rounded_rectangle([40, y0, 1040, y0 + alto], radius=40, fill=INK)
for i, l in enumerate(lineas):
    w = d.textlength(l, font=f)
    d.text(((1080 - w) / 2, y0 + 40 + i * size * 1.08), l, font=f, fill=ORA if i == len(lineas) - 1 else CRE)
fm = ImageFont.truetype(negra, 64)
w = d.textlength("sin humo TV", font=fm)
d.text(((1080 - w) / 2, y0 + alto + 40), "sin humo TV", font=fm, fill=CRE, stroke_width=8, stroke_fill=INK)
im.save(os.path.join(D, "portada.png"))
os.remove(foto)
print("portada ok", size)
