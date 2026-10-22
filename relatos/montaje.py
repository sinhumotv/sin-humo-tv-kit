#!/usr/bin/env python3
"""Montaje estilo 'relato': imágenes con zoom lento (Ken Burns), fundidos cortos,
subtítulos de 2-3 palabras en serif blanca con la palabra clave en amarillo, música y voz.
Uso: python3 montaje.py <carpeta>   (necesita proyecto.json, tiempos.json, voz_final.wav, imgs/01.jpg...)
"""
import json, os, re, subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = sys.argv[1]
W, H, FPS = 1080, 1920, 30
P = json.load(open(f"{D}/proyecto.json", encoding="utf-8"))
T = json.load(open(f"{D}/tiempos.json"))
DUR = T["duracion"] + 0.4
NF = int(DUR * FPS)
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "pf.ttf")
fnt = ImageFont.truetype(FONT, 74)
try:
    fnt.set_variation_by_name("Bold")
except Exception:
    pass
AMARILLO = (242, 190, 70)
XF = 0.35  # fundido entre imágenes (s)

# ---------- imágenes y movimiento ----------
escenas = T["escenas"]
imgs = []
for i in range(len(escenas)):
    p = f"{D}/imgs/{i + 1:02d}.jpg"
    im = Image.open(p).convert("RGB")
    # rellenar 9:16 a 1.25x para tener margen de zoom sin perder nitidez
    s = max(W * 1.25 / im.width, H * 1.25 / im.height)
    im = im.resize((math.ceil(im.width * s), math.ceil(im.height * s)), Image.LANCZOS)
    imgs.append(im)
# patrón de movimientos que varía: acercar, alejar, desplazar
MOV = ["in", "out", "in_up", "out", "in", "pan", "in_up", "out"]


def cuadro(i, u):
    """Imagen i en el instante relativo u (0..1) con su movimiento."""
    im = imgs[i]
    e = u * u * (3 - 2 * u) * 0.6 + u * 0.4  # suave pero sin pararse
    m = MOV[i % len(MOV)]
    z0, z1 = (1.0, 1.14) if m.startswith("in") else (1.14, 1.0) if m == "out" else (1.08, 1.08)
    z = z0 + (z1 - z0) * e
    cw, ch = im.width / 1.25 / z, im.height / 1.25 / z
    cx, cy = im.width / 2, im.height / 2
    if m == "in_up":
        cy -= (im.height - ch) * 0.12 * e
    if m == "pan":
        cx += (im.width - cw) * (e - 0.5) * 0.5
    x0, y0 = cx - cw / 2, cy - ch / 2
    a, b = cw / W, ch / H
    return im.transform((W, H), Image.AFFINE, (a, 0, x0, 0, b, y0), resample=Image.BILINEAR)


# ---------- subtítulos: palabras con tiempos proporcionales ----------
trozos = []  # (t0, t1, [(palabra, clave)])
for k, (e, t) in enumerate(zip(P["escenas"], escenas)):
    t0 = t["lineas"][0] if t.get("lineas") else t["ini"]
    t1 = t["voz_fin"]
    pals = []
    for w in e["subtitulo"].split():
        clave = "*" in w
        pals.append((w.replace("*", ""), clave))
    pesos = np.array([len(re.sub(r"\W", "", w)) + 2 + (4 if re.search(r"[.,?!]$", w) else 0) for w, _ in pals], float)
    bordes = t0 + np.concatenate([[0], np.cumsum(pesos)]) / pesos.sum() * (t1 - t0)
    # agrupar en bloques de 2-3 palabras, cortando tras puntuación
    grupo = []
    for j, (w, c) in enumerate(pals):
        grupo.append(j)
        fin_frase = bool(re.search(r"[.,?!]$", w))
        if len(grupo) == 3 or fin_frase or (len(grupo) == 2 and len(w) > 7) or j == len(pals) - 1:
            trozos.append([bordes[grupo[0]], bordes[grupo[-1] + 1], [pals[g] for g in grupo]])
            grupo = []
for a, b in zip(trozos, trozos[1:]):  # sin huecos: cada bloque dura hasta el siguiente
    if b[0] - a[1] < 0.6:
        a[1] = b[0]

cache = {}


def capa_texto(idx):
    if idx in cache:
        return cache[idx]
    pals = trozos[idx][2]
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    esp = d.textlength(" ", font=fnt)
    anchos = [d.textlength(w, font=fnt) for w, _ in pals]
    total = sum(anchos) + esp * (len(pals) - 1)
    # si no cabe en una línea, se parte en dos
    lineas = [list(range(len(pals)))]
    if total > W * 0.84 and len(pals) > 1:
        lineas = [list(range(len(pals) - 1)), [len(pals) - 1]]
    y = int(H * 0.60) - (len(lineas) - 1) * 50
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sombra)
    for ln in lineas:
        tw = sum(anchos[j] for j in ln) + esp * (len(ln) - 1)
        x = (W - tw) / 2
        for j in ln:
            w, c = pals[j]
            ds.text((x + 3, y + 5), w, font=fnt, fill=(0, 0, 0, 200), anchor="ls")
            d.text((x, y), w, font=fnt, fill=AMARILLO if c else (255, 255, 255),
                   stroke_width=3, stroke_fill=(20, 14, 8), anchor="ls")
            x += anchos[j] + esp
        y += 100
    sombra = sombra.filter(ImageFilter.GaussianBlur(6))
    out = Image.alpha_composite(sombra, capa)
    cache[idx] = out
    return out


# viñeta suave para que el texto se lea
yy, xx = np.mgrid[0:H, 0:W]
r = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2)
vig = np.clip(1 - (r - 0.55) * 0.9, 0.62, 1.0)[..., None].astype(np.float32)

# ---------- efectos gratis: partículas y luz de fuego ----------
EFE = P.get("efectos", ["brasas"] * len(escenas))
rngp = np.random.default_rng(7)
def sprite(r, col):
    yy2, xx2 = np.mgrid[-r:r + 1, -r:r + 1]
    a = np.clip(1 - np.sqrt(xx2 ** 2 + yy2 ** 2) / r, 0, 1) ** 2
    im = np.zeros((2 * r + 1, 2 * r + 1, 4), np.uint8); im[..., :3] = col; im[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(im, "RGBA")
SPR = {"brasas": [sprite(r, (255, 150, 50)) for r in (4, 6, 9)],
       "polvo": [sprite(r, (255, 235, 190)) for r in (3, 5, 7)],
       "niebla": [sprite(r, (220, 235, 255)) for r in (5, 8, 12)]}
NIV = {}
for tp, lst in SPR.items():
    for si, sp in enumerate(lst):
        NIV[(tp, si)] = []
        for lv in range(5):
            c = sp.copy(); c.putalpha(sp.getchannel("A").point(lambda v, f=(lv + .5) / 5: int(v * f))); NIV[(tp, si)].append(c)
NP = 60
part = {"x": rngp.uniform(0, W, NP), "y": rngp.uniform(0, H, NP), "v": rngp.uniform(25, 90, NP),
        "f": rngp.uniform(0, 6.28, NP), "s": rngp.integers(0, 3, NP), "a": rngp.uniform(.3, .9, NP)}
def particulas(fr, tipo, t):
    if tipo not in SPR: return fr
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sube = 1 if tipo in ("brasas", "niebla") else 0.25
    for k in range(NP if tipo != "polvo" else 45):
        x = (part["x"][k] + 40 * np.sin(t * .7 + part["f"][k])) % W
        y = (part["y"][k] - part["v"][k] * t * sube) % H
        sp = SPR[tipo][part["s"][k]]
        a = part["a"][k] * (0.6 + 0.4 * np.sin(t * 3 + part["f"][k]))
        if tipo == "niebla": a *= .5
        capa.alpha_composite(NIV[(tipo, part["s"][k])][min(4, int(a * 5))], (int(x), int(y)))
    return Image.alpha_composite(fr, capa)
FUEGO = set(P.get("fuego", []))

ff = subprocess.Popen(
    f'ffmpeg -y -v error -f rawvideo -pix_fmt rgb24 -s {W}x{H} -r {FPS} -i - '
    f'-c:v libx264 -preset veryfast -crf 17 -pix_fmt yuv420p "{D}/_video.mp4"', shell=True, stdin=subprocess.PIPE)
for f in range(NF):
    t = f / FPS
    i = max(k for k, e in enumerate(escenas) if e["ini"] <= t + 1e-6) if t < escenas[-1]["fin"] else len(escenas) - 1
    e = escenas[i]
    ini, fin = e["ini"], (e["fin"] if i < len(escenas) - 1 else DUR)
    span = fin - ini + XF
    fr = cuadro(i, min(1, (t - ini) / span))
    if i + 1 < len(escenas) and t > fin - XF:  # fundido con la siguiente
        nxt = cuadro(i + 1, 0)
        fr = Image.blend(fr, nxt, (t - (fin - XF)) / XF * 0.999)
    luz = 1.0
    if i in FUEGO:
        luz = 0.93 + 0.05 * np.sin(t * 11) + 0.03 * np.sin(t * 23 + 1) + 0.02 * np.sin(t * 37)
    arr = (np.asarray(fr, np.float32) * vig * luz).clip(0, 255).astype(np.uint8)
    fr = Image.fromarray(arr).convert("RGBA")
    fr = particulas(fr, EFE[i], t)
    for k, (a, b, _) in enumerate(trozos):
        if a <= t < b + 0.05:
            fr = Image.alpha_composite(fr, capa_texto(k))
            break
    ff.stdin.write(fr.convert("RGB").tobytes())
ff.stdin.close()
ff.wait()

# ---------- música: ambiente épico y melancólico (sintetizado, sin derechos) ----------
SR = 48000
n = int(DUR * SR)
tt = np.arange(n) / SR
import zlib
rng = np.random.default_rng(zlib.crc32(P.get("titulo_noticia", "x").encode()))
PROG = [  # progresiones menores épicas/melancólicas (Hz base en Re)
    [[73.42, 110.0, 146.83, 174.61], [58.27, 87.31, 116.54, 146.83], [49.0, 98.0, 116.54, 146.83], [55.0, 82.41, 110.0, 138.59]],
    [[73.42, 110.0, 146.83, 174.61], [65.41, 98.0, 130.81, 164.81], [58.27, 87.31, 116.54, 146.83], [55.0, 82.41, 110.0, 138.59]],
    [[73.42, 110.0, 146.83, 174.61], [49.0, 98.0, 116.54, 146.83], [58.27, 87.31, 116.54, 146.83], [65.41, 98.0, 130.81, 164.81]],
    [[73.42, 110.0, 146.83, 174.61], [87.31, 130.81, 174.61, 220.0], [65.41, 98.0, 130.81, 164.81], [58.27, 87.31, 116.54, 146.83]],
]
tr = 2 ** (rng.integers(-3, 3) / 12)  # transposición para que no suene siempre igual
acordes = [[f * tr for f in ac] for ac in PROG[rng.integers(0, len(PROG))]]
comp = float(rng.uniform(3.4, 4.8))
pad = np.zeros(n)
for c in range(int(np.ceil(DUR / comp)) + 1):
    a, b = int(c * comp * SR), min(n, int((c + 1) * comp * SR + 0.8 * SR))
    if a >= n:
        break
    s = tt[a:b] - tt[a]
    env = np.minimum(1, s / 1.2) * np.clip((comp + 0.8 - s) / 1.0, 0, 1)
    for fq in acordes[c % 4]:
        for det in (-0.6, 0.6):
            pad[a:b] += env * np.sin(2 * np.pi * (fq + det) * tt[a:b] + rng.uniform(0, 6)) / 8
    # golpe grave de timbal al cambiar de acorde
    kl = min(b - a, int(1.2 * SR)); kt = np.arange(kl) / SR
    pad[a:a + kl] += 0.5 * np.sin(2 * np.pi * (48 + 30 * np.exp(-kt * 8)) * kt) * np.exp(-kt * 3.5)
drone = 0.25 * np.sin(2 * np.pi * 36.71 * tr * tt) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.1 * tt))
mus = pad + drone
mus *= np.minimum(1, tt / 1.0) * np.clip((DUR - tt) / 1.5, 0, 1)
mus /= np.abs(mus).max() + 1e-9
mus.astype(np.float32).tofile(f"{D}/_mus.raw")
subprocess.run(f'ffmpeg -y -v error -f f32le -ar {SR} -ac 1 -i "{D}/_mus.raw" -af "lowpass=f=2500,aecho=0.8:0.7:60:0.25" "{D}/musica.wav"', shell=True)
os.remove(f"{D}/_mus.raw")

subprocess.run(
    f'ffmpeg -y -v error -i "{D}/_video.mp4" -i "{D}/voz_final.wav" -i "{D}/musica.wav" -filter_complex '
    f'"[1:a]aresample=48000,apad[v];[2:a]volume=0.22[m];[v][m]amix=inputs=2:duration=shortest:normalize=0,'
    f'loudnorm=I=-14:TP=-1.5:LRA=11[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest '
    f'-movflags +faststart "{D}/video_final.mp4"', shell=True, check=True)
print("OK", f"{D}/video_final.mp4", f"{DUR:.1f}s", len(trozos), "bloques de subtítulos")
