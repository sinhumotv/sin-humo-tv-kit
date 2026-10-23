#!/usr/bin/env python3
"""Tres miniaturas de YouTube (1280x720) pensadas para el clic: imagen potente con más contraste, texto enorme de
2-4 palabras con la palabra clave en amarillo, contorno grueso y sombra. La A es la que se publica.

Uso: python3 largo_miniatura.py <carpeta>   -> miniatura_A.jpg, miniatura_B.jpg, miniatura_C.jpg
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

D = os.path.abspath(sys.argv[1])
H = json.load(open(f"{D}/historia.json", encoding="utf-8"))
KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEGRA = os.path.join(KIT, "fonts", "Inter-Black.otf")
W, HH = 1280, 720
AMARILLO, BLANCO = (255, 214, 0), (255, 255, 255)
TXT = H["miniatura"]["texto"].upper().split()[:5]
CLAVE = H["miniatura"].get("clave", "").upper().strip(".,¿?¡!")


def base(p, espejo=False):
    im = Image.open(p).convert("RGB")
    s = max(W / im.width, HH / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - HH) // 2
    im = im.crop((x, y, x + W, y + HH))
    if espejo:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im = ImageEnhance.Contrast(im).enhance(1.18)
    im = ImageEnhance.Color(im).enhance(1.22)
    return im.filter(ImageFilter.UnsharpMask(radius=2, percent=80, threshold=2))


def degradado(im, lado="izq", fuerza=0.85):
    g = Image.new("L", (W, HH))
    px = g.load()
    for x in range(W):
        u = x / W if lado == "izq" else 1 - x / W
        v = int(255 * fuerza * max(0, 1 - u / 0.62) ** 1.4)
        for y in range(HH):
            px[x, y] = v
    negro = Image.new("RGB", (W, HH), (0, 0, 0))
    return Image.composite(negro, im, g)


def lineas(pal):
    if len(pal) <= 2:
        return [pal]
    corte = (len(pal) + 1) // 2
    return [pal[:corte], pal[corte:]]


def texto(im, x0, ancho, caja_clave=False, centrado=False):
    d = ImageDraw.Draw(im)
    ls = lineas(TXT)
    size = 190
    while size > 50:
        f = ImageFont.truetype(NEGRA, size)
        if all(d.textlength(" ".join(l), font=f) <= ancho for l in ls) and size * 1.02 * len(ls) <= HH * 0.78:
            break
        size -= 4
    alto = int(size * 1.02) * len(ls)
    y = (HH - alto) // 2 if not centrado else HH - alto - 40
    sombra = Image.new("RGBA", (W, HH), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sombra)
    capa = Image.new("RGBA", (W, HH), (0, 0, 0, 0))
    dc = ImageDraw.Draw(capa)
    esp = d.textlength(" ", font=f)
    for l in ls:
        tw = sum(d.textlength(p, font=f) for p in l) + esp * (len(l) - 1)
        x = (W - tw) / 2 if centrado else x0
        for p in l:
            clave = p.strip(".,¿?¡!") == CLAVE
            pw = d.textlength(p, font=f)
            if clave and caja_clave:
                dc.rounded_rectangle((x - 14, y + size * 0.06, x + pw + 14, y + size * 1.02), 14, fill=AMARILLO + (255,))
            ds.text((x + 8, y + 10), p, font=f, fill=(0, 0, 0, 230))
            col = (20, 16, 10) if (clave and caja_clave) else (AMARILLO if clave else BLANCO)
            dc.text((x, y), p, font=f, fill=col + (255,), stroke_width=0 if (clave and caja_clave) else max(6, size // 18),
                    stroke_fill=(0, 0, 0, 255))
            x += pw + esp
        y += int(size * 1.02)
    sombra = sombra.filter(ImageFilter.GaussianBlur(9))
    out = Image.alpha_composite(im.convert("RGBA"), sombra)
    return Image.alpha_composite(out, capa).convert("RGB")


principal = f"{D}/miniatura_base.jpg"
escenas = sorted(os.listdir(f"{D}/imgs"))
if not os.path.exists(principal):
    principal = f"{D}/imgs/{escenas[0]}"
# segunda imagen: la primera escena real (o la del gancho)
reales = [f"{i + 1:02d}.jpg" for i, e in enumerate(H["escenas"]) if e["imagen"]["tipo"] == "real"]
segunda = f"{D}/imgs/{(reales or escenas)[0]}"

a = texto(degradado(base(principal)), 60, W * 0.56)
a.save(f"{D}/miniatura_A.jpg", quality=92)
b = texto(degradado(base(segunda), fuerza=0.8), 60, W * 0.56, caja_clave=True)
b.save(f"{D}/miniatura_B.jpg", quality=92)
c = base(principal, espejo=True)
g = Image.new("L", (W, HH))
for y in range(HH):
    g.paste(int(230 * max(0, (y / HH - 0.35) / 0.65) ** 1.3), (0, y, W, y + 1))
c = Image.composite(Image.new("RGB", (W, HH)), c, g)
texto(c, 0, W * 0.9, caja_clave=True, centrado=True).save(f"{D}/miniatura_C.jpg", quality=92)
print("MINIATURAS OK · A (se publica), B y C ·", " ".join(TXT))
