#!/usr/bin/env python3
"""Montaje estilo 'relato': imágenes con zoom lento (Ken Burns), fundidos cortos,
subtítulos de 2-3 palabras en serif blanca con la palabra clave en amarillo, música y voz.
Uso: python3 montaje.py <carpeta>   (necesita proyecto.json, tiempos.json, voz_final.wav, imgs/01.jpg...)
"""
import json, os, re, subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = sys.argv[1]
P = json.load(open(f"{D}/proyecto.json", encoding="utf-8"))
YT = str(P.get("formato", "")).upper() == "YOUTUBE"   # vídeo largo horizontal
W, H, FPS = (1920, 1080, 25) if YT else (1080, 1920, 30)
T = json.load(open(f"{D}/tiempos.json"))
DUR = T["duracion"] + 0.4
NF = int(DUR * FPS)
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "pf.ttf")
fnt = ImageFont.truetype(FONT, 66 if YT else 80)
try:
    fnt.set_variation_by_name("Bold")
except Exception:
    pass
AMARILLO = tuple(P.get("color") or (242, 190, 70))  # color de la palabra que suena (por canal)
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
    im = im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=70, threshold=2))
    imgs.append(im)
# patrón de movimientos que varía: acercar, alejar, desplazar
MOV = ["in", "out", "in_up", "out", "in", "pan", "in_up", "out"]
# clips de vídeo real (largos): {índice de escena: ruta del .mp4}
CLIPS = {int(k): v for k, v in (P.get("clips") or {}).items() if os.path.exists(v)}
LECT = {}


def frame_clip(i):
    """Siguiente fotograma del clip de la escena i, ya a W x H (en bucle si el clip es más corto que la escena)."""
    if i not in LECT:
        for k in list(LECT):
            LECT.pop(k).kill()
        LECT[i] = subprocess.Popen(
            f'ffmpeg -v error -stream_loop -1 -i "{CLIPS[i]}" -an -vf "scale={W}:{H}:force_original_aspect_ratio=increase,'
            f'crop={W}:{H},fps={FPS},format=rgb24" -f rawvideo -pix_fmt rgb24 -', shell=True, stdout=subprocess.PIPE)
    b = LECT[i].stdout.read(W * H * 3)
    if len(b) < W * H * 3:
        return None
    return Image.frombytes("RGB", (W, H), b)


def cuadro(i, u):
    """Imagen i en el instante relativo u (0..1) con su movimiento."""
    im = imgs[i]
    e = u * u * (3 - 2 * u) * 0.6 + u * 0.4  # suave pero sin pararse
    m = "in" if i in CLIPS else MOV[i % len(MOV)]
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
    return im.transform((W, H), Image.AFFINE, (a, 0, x0, 0, b, y0), resample=Image.BICUBIC)


# ---------- subtítulos karaoke: cada palabra se ilumina cuando se dice ----------
def norm(w):
    import unicodedata
    w = unicodedata.normalize("NFD", w.lower())
    return "".join(c for c in w if c.isalnum() and not unicodedata.combining(c))


pals = []   # (palabra, escena)
for k, e in enumerate(P["escenas"]):
    for w in e["subtitulo"].split():
        pals.append([w.replace("*", ""), k])
# 1) tiempos aproximados (proporcionales dentro de cada escena)
ini_p = [0.0] * len(pals)
for k, (e, t) in enumerate(zip(P["escenas"], escenas)):
    idx = [j for j, p in enumerate(pals) if p[1] == k]
    t0 = t["lineas"][0] if t.get("lineas") else t["ini"]
    t1 = t["voz_fin"]
    pes = np.array([len(norm(pals[j][0])) + 2 for j in idx], float)
    acu = t0 + np.concatenate([[0], np.cumsum(pes)])[:-1] / pes.sum() * (t1 - t0)
    for j, v in zip(idx, acu):
        ini_p[j] = float(v)
# 2) tiempos reales con reconocimiento de voz (si está disponible)
try:
    from faster_whisper import WhisperModel
    import difflib
    mod = WhisperModel(os.environ.get("WHISPER_MODELO", "base"), device="cpu", compute_type="int8")
    pcm = subprocess.run(f'ffmpeg -v error -i "{D}/voz_final.wav" -ac 1 -ar 16000 -f f32le -', shell=True,
                         capture_output=True).stdout
    audio16 = np.frombuffer(pcm, np.float32)
    segs, _ = mod.transcribe(audio16, language="es", word_timestamps=True,
                             initial_prompt=" ".join(p[0] for p in pals))
    rec = [(norm(w.word), w.start) for s_ in segs for w in s_.words]
    sm = difflib.SequenceMatcher(None, [norm(p[0]) for p in pals], [r[0] for r in rec], autojunk=False)
    real = {}
    for blk in sm.get_matching_blocks():
        for q in range(blk.size):
            real[blk.a + q] = rec[blk.b + q][1]
    if len(real) > 0.6 * len(pals):
        # palabras sin casar: interpolar entre vecinas casadas
        cas = sorted(real)
        for j in range(len(pals)):
            if j in real:
                ini_p[j] = real[j]
            else:
                prev = max([c for c in cas if c < j], default=None)
                nxt = min([c for c in cas if c > j], default=None)
                if prev is not None and nxt is not None:
                    ini_p[j] = real[prev] + (real[nxt] - real[prev]) * (j - prev) / (nxt - prev)
        for j in range(1, len(pals)):
            ini_p[j] = max(ini_p[j], ini_p[j - 1] + 0.05)
        print(f"karaoke: {len(real)}/{len(pals)} palabras con tiempo real")
    else:
        print("karaoke: reconocimiento poco fiable, tiempos aproximados")
except Exception as ex:
    print("karaoke: sin reconocimiento de voz (" + str(ex)[:80] + "), tiempos aproximados")

# 3) bloques de 2-3 palabras, cortando tras puntuación o cambio de escena
trozos = []  # [t0, t1, [índices de palabra]]
grupo = []
for j, (w, k) in enumerate(pals):
    grupo.append(j)
    fin = (bool(re.search(r"[.,?!:;…]$", w)) or len(grupo) == 3 or (len(grupo) == 2 and len(w) > 8)
           or j == len(pals) - 1 or pals[j + 1][1] != k)
    if fin:
        trozos.append([ini_p[grupo[0]], None, grupo])
        grupo = []
for q in range(len(trozos)):
    sig = trozos[q + 1][0] if q + 1 < len(trozos) else T["duracion"] + 0.3
    ult = trozos[q][2][-1]
    fin_voz = ini_p[ult] + 0.25 + 0.06 * len(pals[ult][0])
    trozos[q][1] = sig if sig - fin_voz < 0.7 else fin_voz + 0.3
fin_pal = {j: (ini_p[j + 1] if j + 1 < len(pals) else 1e9) for j in range(len(pals))}

Y_SUB = int(H * (0.885 if YT else 0.69))   # más abajo, pero por encima de los textos de las redes
LH = 84 if YT else 100
cache = {}


def capa_texto(q, activa):
    """Bloque q con la palabra 'activa' (índice global) iluminada en amarillo."""
    key = (q, activa)
    if key in cache:
        return cache[key]
    idxs = trozos[q][2]
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sombra)
    esp = d.textlength(" ", font=fnt)
    anchos = {j: d.textlength(pals[j][0], font=fnt) for j in idxs}
    total = sum(anchos.values()) + esp * (len(idxs) - 1)
    lineas = [idxs] if (total <= W * 0.86 or len(idxs) == 1) else [idxs[:-1], idxs[-1:]]
    y = Y_SUB - (len(lineas) - 1) * LH // 2
    for ln in lineas:
        tw = sum(anchos[j] for j in ln) + esp * (len(ln) - 1)
        x = (W - tw) / 2
        for j in ln:
            w = pals[j][0]
            on = j == activa
            ds.text((x + 3, y + 6), w, font=fnt, fill=(0, 0, 0, 210), anchor="ls")
            if on:  # resplandor detrás de la palabra que suena
                ds.text((x, y), w, font=fnt, fill=AMARILLO + (150,), anchor="ls", stroke_width=10, stroke_fill=AMARILLO + (110,))
            d.text((x, y), w, font=fnt, fill=AMARILLO if on else (255, 255, 255),
                   stroke_width=4, stroke_fill=(15, 10, 5), anchor="ls")
            x += anchos[j] + esp
        y += LH
    sombra = sombra.filter(ImageFilter.GaussianBlur(7))
    out = Image.alpha_composite(sombra, capa)
    cache[key] = out
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

# ---------- rótulo de capítulo (vídeo largo) ----------
CAPS = []
if YT:
    negra = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts", "Inter-Black.otf")
    f1, f2 = ImageFont.truetype(negra, 30), ImageFont.truetype(negra, 58)
    for n, c in enumerate(P.get("capitulos", [])):
        if n == 0 or c["escena"] >= len(escenas):
            continue
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        tit = c["titulo"].upper()
        tw = max(d.textlength(tit, font=f2), d.textlength(f"CAPÍTULO {n}", font=f1))
        d.rounded_rectangle((70, 70, 70 + tw + 70, 70 + 150), 18, fill=(10, 8, 6, 175))
        d.rectangle((70, 70, 80, 220), fill=AMARILLO + (255,))
        d.text((110, 92), f"CAPÍTULO {n}", font=f1, fill=AMARILLO + (255,))
        d.text((110, 132), tit, font=f2, fill=(255, 255, 255, 255))
        CAPS.append((escenas[c["escena"]]["ini"] + 0.3, capa))


def rotulo(fr, t):
    for t0, capa in CAPS:
        if t0 <= t < t0 + 4.0:
            a = min(1, (t - t0) / 0.4, (t0 + 4.0 - t) / 0.4)
            if a < 1:
                capa = capa.copy(); capa.putalpha(capa.getchannel("A").point(lambda v: int(v * a)))
            return Image.alpha_composite(fr, capa)
    return fr

ff = subprocess.Popen(
    f'ffmpeg -y -v error -f rawvideo -pix_fmt rgb24 -s {W}x{H} -r {FPS} -i - '
    f'-c:v libx264 -preset faster -crf {20 if YT else 16} -tune film -pix_fmt yuv420p "{D}/_video.mp4"', shell=True, stdin=subprocess.PIPE)
for f in range(NF):
    t = f / FPS
    i = max(k for k, e in enumerate(escenas) if e["ini"] <= t + 1e-6) if t < escenas[-1]["fin"] else len(escenas) - 1
    e = escenas[i]
    ini, fin = e["ini"], (e["fin"] if i < len(escenas) - 1 else DUR)
    span = fin - ini + XF
    fr = frame_clip(i) if i in CLIPS else None
    if fr is None:
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
    fr = rotulo(fr, t)
    for q, (a, b, idxs) in enumerate(trozos):
        if a - 0.04 <= t < b:
            act = next((j for j in idxs if ini_p[j] - 0.04 <= t < fin_pal[j]), None)
            if act is None and t >= ini_p[idxs[-1]]:
                act = idxs[-1] if t < fin_pal[idxs[-1]] else None
            fr = Image.alpha_composite(fr, capa_texto(q, act))
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
