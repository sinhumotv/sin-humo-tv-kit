#!/usr/bin/env python3
"""Tres miniaturas de YouTube (1280x720) pensadas para el clic. La A es la que se publica.

Rediseño (14-nov-2026, petición del usuario: «mejorar notablemente las miniaturas fijándote en vídeos similares con
muchas visitas»). Lo que tienen en común las miniaturas que más funcionan en mitología, misterio y futuro (outliers de
vidIQ: «Hércules y el toro de Creta» x235, «2030 LO OCULTAN» x411, «33 misterios sin explicar», «RESUELTO»...):
  - la imagen ocupa TODA la miniatura, luminosa, épica y con colores saturados (nada de media miniatura en negro);
  - texto ENORME de 1-3 palabras abajo o en un lateral, con un color de marca por temática (oro metálico en mitología,
    amarillo con caja blanca en futuro, rojo encendido en misterio), contorno grueso y sombra;
  - solo se oscurece la franja donde va el texto.
Además, si la imagen base sale oscura se ilumina, y si sale casi negra o vacía se cambia por otra (nunca más una
miniatura en negro con solo letras).

Uso: CANAL=<relatos|ano2100|cajanegra|...> python3 largo_miniatura.py <carpeta>
     -> miniatura_A.jpg, miniatura_B.jpg, miniatura_C.jpg
"""
import io, json, os, shutil, sys
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageStat

D = os.path.abspath(sys.argv[1])
H = json.load(open(f"{D}/historia.json", encoding="utf-8"))
AQUI = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(AQUI)
FUENTES = os.path.join(KIT, "fonts")
W, HH = 1280, 720
CANAL = os.environ.get("CANAL", "")
if not CANAL:   # se deduce de la carpeta (largo-relatos-xxxx) si no viene en el entorno
    for c in ("relatos", "ano2100", "cajanegra", "pongamosque", "explicalo"):
        if c in D:
            CANAL = c

LIMPIA = lambda p: p.strip(".,¿?¡!:;\"'«»")
TXT = [p for p in H["miniatura"]["texto"].upper().split() if LIMPIA(p)][:5]
CLAVE = LIMPIA(H["miniatura"].get("clave", "").upper())
if CLAVE not in [LIMPIA(p) for p in TXT]:   # la clave tiene que estar en el texto; si no, la palabra más larga
    CLAVE = LIMPIA(max(TXT, key=lambda p: len(LIMPIA(p)))) if TXT else ""

ESTILOS = {
    # mitología / historias: letras romanas en oro metálico (como las de los vídeos de mitología con más visitas)
    "relatos": dict(fuente=("Cinzel-VF.ttf", b"Black"), relleno="oro", clave="rojo", mayor=1.0, ajuste=0.0),
    # futuro: palabra clave gigante en amarillo y el resto en caja blanca con letras negras
    "ano2100": dict(fuente=("Anton-Regular.ttf", None), relleno="blanco", clave="amarillo", mayor=1.12, ajuste=0.02),
    # misterio / crímenes: rojo encendido con brillo, resto en blanco
    "cajanegra": dict(fuente=("Anton-Regular.ttf", None), relleno="blanco", clave="rojo_neon", mayor=1.12, ajuste=0.02),
}
EST = ESTILOS.get(CANAL, dict(fuente=("Inter-Black.otf", None), relleno="blanco", clave="amarillo", mayor=1.0, ajuste=0.0))


def fuente(size):
    nombre, var = EST["fuente"]
    f = ImageFont.truetype(os.path.join(FUENTES, nombre), size)
    if var:
        try:
            f.set_variation_by_name(var)
        except Exception:
            pass
    return f


# ---------------------------------------------------------------- imagen base
def luz(im):
    s = ImageStat.Stat(im.convert("L"))
    return s.mean[0], s.stddev[0]


def valida(p):
    """Descarta imágenes casi negras, vacías o planas (lo que dio la miniatura negra de «HUMILLÓ A ZEUS»)."""
    try:
        m, sd = luz(Image.open(p).convert("RGB").resize((160, 90)))
        return m > 38 and sd > 22
    except Exception:
        return False


def base(p, espejo=False):
    im = Image.open(p).convert("RGB")
    s = max(W / im.width, HH / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - HH) // 2
    im = im.crop((x, y, x + W, y + HH))
    if espejo:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    # si está oscura, se levantan las sombras (curva gamma) hasta una luminosidad media de miniatura que se ve bien
    m, _ = luz(im)
    if m < 105:
        g = max(0.5, min(1.0, (m / 105) ** 0.9))
        im = im.point(lambda v: int(255 * (v / 255) ** g))
    im = ImageEnhance.Contrast(im).enhance(1.18)
    im = ImageEnhance.Color(im).enhance(1.35)
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=120, threshold=2))
    # viñeta muy suave (solo esquinas): el centro se queda luminoso
    v = Image.new("L", (W, HH), 0)
    ImageDraw.Draw(v).ellipse((-W * 0.25, -HH * 0.35, W * 1.25, HH * 1.35), fill=255)
    v = v.filter(ImageFilter.GaussianBlur(140))
    return Image.composite(im, Image.new("RGB", (W, HH)), v.point(lambda x: 150 + x * 105 // 255))


def sombra_abajo(im, desde=0.5, fuerza=0.82):
    g = Image.new("L", (1, HH))
    for y in range(HH):
        g.putpixel((0, y), int(255 * fuerza * max(0, (y / HH - desde) / (1 - desde)) ** 1.25))
    return Image.composite(Image.new("RGB", (W, HH)), im, g.resize((W, HH)))


def sombra_lado(im, lado="izq", ancho=0.55, fuerza=0.7):
    g = Image.new("L", (W, 1))
    for x in range(W):
        u = x / W if lado == "izq" else 1 - x / W
        g.putpixel((x, 0), int(255 * fuerza * max(0, 1 - u / ancho) ** 1.5))
    return Image.composite(Image.new("RGB", (W, HH)), im, g.resize((W, HH)))


# ---------------------------------------------------------------- texto
def rellenos(nombre, caja):
    """Imagen RGB del tamaño de la caja con el relleno de las letras."""
    w, h = caja
    if nombre == "oro":   # oro metálico: claro arriba, brillo en el centro, más oscuro abajo
        g = Image.new("RGB", (1, h))
        paradas = [(0, (255, 246, 196)), (.35, (255, 214, 92)), (.55, (232, 168, 36)), (.62, (255, 226, 120)), (1, (170, 104, 14))]
        for y in range(h):
            t = y / max(1, h - 1)
            for (a, ca), (b, cb) in zip(paradas, paradas[1:]):
                if a <= t <= b:
                    k = (t - a) / (b - a)
                    g.putpixel((0, y), tuple(int(ca[i] + (cb[i] - ca[i]) * k) for i in range(3)))
                    break
        return g.resize((w, h))
    col = {"blanco": (255, 255, 255), "amarillo": (255, 216, 0), "rojo": (232, 30, 30), "rojo_neon": (255, 36, 36),
           "negro": (16, 16, 16)}[nombre]
    return Image.new("RGB", (w, h), col)


def poner(im, palabras, f, x, y, nombre, brillo=None, contorno=True):
    """Dibuja una línea de texto con relleno (degradado o color), contorno negro grueso, sombra y brillo opcional."""
    texto_ = " ".join(palabras)
    d = ImageDraw.Draw(im)
    l, t, r, b = d.textbbox((x, y), texto_, font=f)
    sw = max(6, f.size // 13) if contorno else 0
    mascara = Image.new("L", (W, HH), 0)
    ImageDraw.Draw(mascara).text((x, y), texto_, font=f, fill=255)
    borde = Image.new("L", (W, HH), 0)
    ImageDraw.Draw(borde).text((x, y), texto_, font=f, fill=255, stroke_width=sw, stroke_fill=255)
    # sombra paralela + halo
    sombra = borde.filter(ImageFilter.GaussianBlur(10))
    sombra = ImageChops.offset(sombra, 7, 9)
    im = Image.composite(Image.new("RGB", (W, HH)), im, sombra.point(lambda v: v * 210 // 255))
    if brillo:
        halo = borde.filter(ImageFilter.GaussianBlur(26)).point(lambda v: min(255, v * 2))
        im = Image.composite(Image.new("RGB", (W, HH), brillo), im, halo.point(lambda v: v * 170 // 255))
    if sw:
        im = Image.composite(Image.new("RGB", (W, HH)), im, borde)
    capa = Image.new("RGB", (W, HH))
    caja = (max(0, int(l)), max(0, int(t)), min(W, int(r) + 1), min(HH, int(b) + 1))
    if caja[2] > caja[0] and caja[3] > caja[1]:
        capa.paste(rellenos(nombre, (caja[2] - caja[0], caja[3] - caja[1])), caja[:2])
    return Image.composite(capa, im, mascara)


def ajustar(lineas_, ancho, alto_max, tam0=230):
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    size = tam0
    while size > 40:
        fs = [fuente(int(size * e)) for e, _ in lineas_]
        if all(d.textlength(" ".join(l), font=f) <= ancho for f, (_, l) in zip(fs, lineas_)) and \
                sum(f.size * 1.0 for f in fs) <= alto_max:
            return fs
        size -= 4
    return [fuente(int(40 * e)) for e, _ in lineas_]


def repartir():
    """Líneas del texto: la palabra clave en su propia línea y más grande (es lo primero que se lee)."""
    limp = [LIMPIA(p) for p in TXT]
    if CLAVE in limp and len(TXT) > 1:
        i = limp.index(CLAVE)
        antes, despues = TXT[:i], TXT[i + 1:]
        ls = []
        if antes:
            ls.append((SEC, antes, False))
        ls.append((EST["mayor"], [TXT[i]], True))
        if despues:
            ls.append((SEC, despues, False))
        return ls
    if len(TXT) <= 2:
        return [(1.0, TXT, True)]
    c = (len(TXT) + 1) // 2
    return [(0.7, TXT[:c], False), (1.0, TXT[c:], True)]


SEC = 0.62 if EST["fuente"][0].startswith("Cinzel") else 0.74


def color_de(es_clave):
    return EST["clave"] if es_clave else EST["relleno"]


def brillo_de(nombre):
    return {"rojo_neon": (255, 0, 0), "oro": (255, 170, 40), "amarillo": (255, 190, 0)}.get(nombre)


def texto_abajo(im):
    """Variante «Hércules»: texto centrado abajo, a todo lo ancho, sobre una franja oscurecida."""
    ls = repartir()
    fs = ajustar([(e, l) for e, l, _ in ls], W * 0.92, HH * 0.46)
    alto = sum(int(f.size * 1.0) for f in fs)
    y = HH - alto - 34
    d = ImageDraw.Draw(im)
    for f, (e, l, k) in zip(fs, ls):
        tw = d.textlength(" ".join(l), font=f)
        top = d.textbbox((0, 0), " ".join(l), font=f)[1]
        im = poner(im, l, f, (W - tw) / 2, y - top, color_de(k), brillo_de(color_de(k)))
        y += int(f.size * 1.0)
    return im


def texto_lado(im, lado="izq"):
    """Variante «2030 LO OCULTAN»: palabra clave gigante y el resto en caja de color debajo, en un lateral."""
    ls = repartir()
    ancho = W * 0.5
    fs = ajustar([(e, l) for e, l, _ in ls], ancho, HH * 0.8, 260)
    d = ImageDraw.Draw(im)
    alto = sum(int(f.size * 1.08) for f in fs)
    y = (HH - alto) // 2
    x0 = 56 if lado == "izq" else W - 56 - ancho
    for f, (e, l, k) in zip(fs, ls):
        s = " ".join(l)
        tw = d.textlength(s, font=f)
        l_, t_, r_, b_ = d.textbbox((0, 0), s, font=f)
        x = x0 + (ancho - tw) / 2
        if k:
            im = poner(im, l, f, x, y - t_, color_de(True), brillo_de(color_de(True)))
        else:   # caja: blanca con letras negras (oro: caja negra con letras doradas)
            caja_col, letra = ((10, 10, 10), "oro") if EST["relleno"] == "oro" else ((255, 255, 255), "negro")
            pad = f.size * 0.16
            dd = ImageDraw.Draw(im)
            dd.rectangle((x - pad, y - pad * 0.55, x + tw + pad, y + (b_ - t_) + pad * 0.55), fill=caja_col)
            im = poner(im, l, f, x, y - t_, letra, contorno=False)
        y += int(f.size * 1.08)
    return im


# ---------------------------------------------------------------- imágenes
escenas = sorted(f for f in os.listdir(f"{D}/imgs") if f.endswith(".jpg")) if os.path.isdir(f"{D}/imgs") else []
candidatas = [f"{D}/miniatura_base.jpg"] + [f"{D}/miniatura_ia_{k}.jpg" for k in (1, 2, 3)] + [f"{D}/imgs/{e}" for e in escenas]
candidatas = [p for p in dict.fromkeys(candidatas) if os.path.exists(p)]
buenas = [p for p in candidatas if valida(p)]
if not buenas:
    buenas = candidatas[:1]
if not buenas:
    sys.exit("sin imágenes para la miniatura")
principal = buenas[0]
otras_ia = [p for p in buenas[1:] if "miniatura_ia_" in p]
reales = [f"{D}/imgs/{i + 1:02d}.jpg" for i, e in enumerate(H.get("escenas", [])) if e.get("imagen", {}).get("tipo") == "real"]
segunda = next((p for p in otras_ia + [p for p in reales if p in buenas] + buenas[1:]), principal)
if principal != candidatas[0]:
    print("miniatura: la base estaba oscura o vacía; se usa", os.path.basename(principal))

a = texto_abajo(sombra_abajo(base(principal), 0.45, 0.85))
a.save(f"{D}/miniatura_A.jpg", quality=92)
b = texto_lado(sombra_lado(base(principal), "izq"), "izq")
b.save(f"{D}/miniatura_B.jpg", quality=92)
c = texto_abajo(sombra_abajo(base(segunda), 0.45, 0.85))
c.save(f"{D}/miniatura_C.jpg", quality=92)

# la que se publica (A) es la que Gemini cree que daría más clics de las tres (petición del usuario: máximo CTR)
if os.environ.get("SIN_JUEZ") != "1":
    try:
        sys.path.insert(0, AQUI)
        from gem import pedir
        minis = []
        for k in "ABC":
            t = Image.open(f"{D}/miniatura_{k}.jpg"); t.thumbnail((640, 360))
            buf = io.BytesIO(); t.save(buf, "JPEG", quality=85); minis.append(buf.getvalue())
        j, _ = pedir(f"""Eres experto en CTR de YouTube. Título del vídeo: "{H.get('titulo_youtube', '')}". Te paso 3 miniaturas (0, 1 y 2).
¿Cuál conseguiría MÁS clics vista pequeña en el móvil (se lee el texto, se entiende la imagen, despierta curiosidad o
emoción)? Devuelve SOLO JSON: {{"mejor": <0, 1 o 2>, "motivo": "..."}}""", temp=0.2, imagenes=minis, max_tokens=4000)
        k = j.get("mejor") if isinstance(j, dict) else 0
        if k in (1, 2):
            g = "ABC"[k]
            shutil.copy(f"{D}/miniatura_A.jpg", f"{D}/_a.jpg")
            shutil.copy(f"{D}/miniatura_{g}.jpg", f"{D}/miniatura_A.jpg")
            shutil.move(f"{D}/_a.jpg", f"{D}/miniatura_{g}.jpg")
        print("miniatura elegida:", "ABC"[k if k in (0, 1, 2) else 0], "·", str(j.get("motivo", ""))[:120] if isinstance(j, dict) else "")
    except BaseException as x:
        print("sin juez de miniaturas:", str(x)[:80])
print("MINIATURAS OK · A (se publica), B y C ·", " ".join(TXT), "·", CANAL or "genérico")
