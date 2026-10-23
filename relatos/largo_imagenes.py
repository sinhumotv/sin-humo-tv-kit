#!/usr/bin/env python3
"""Imágenes de un vídeo largo (1920x1080): material REAL de Wikimedia Commons (revisado por Gemini) + imágenes de IA
de Cloudflare hasta agotar la cuota gratis del día. Se puede ejecutar varios días seguidos: solo hace lo que falta.

Uso: python3 largo_imagenes.py <carpeta> <canal.json>
Sale con 0 si están todas, 3 si la cuota de Cloudflare se ha agotado y faltan imágenes (se sigue otro día).
"""
import base64, io, json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gem import pedir
from PIL import Image, ImageFilter

D = os.path.abspath(sys.argv[1])
C = json.load(open(sys.argv[2], encoding="utf-8"))
L = C.get("largo", {})
H = json.load(open(f"{D}/historia.json", encoding="utf-8"))
ESC = H["escenas"]
W, HH = 1920, 1080
UA = {"User-Agent": "SinHumoTV-largos/1.0 (https://github.com/sinhumotv/sin-humo-tv-kit; sinhumotv@users.noreply.github.com)"}
os.makedirs(f"{D}/imgs", exist_ok=True)
CRED_P = f"{D}/creditos.json"
CRED = json.load(open(CRED_P, encoding="utf-8")) if os.path.exists(CRED_P) else {}
ESTILO = H.get("estilo_imagen", "")
SEGURO = " Tasteful, no blood, no gore, no nudity."


def guardar():
    json.dump(H, open(f"{D}/historia.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(CRED, open(CRED_P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def componer(im):
    """Siempre a pantalla completa 1920x1080 (recorte centrado, sin bandas ni fondo difuminado)."""
    im = im.convert("RGB")
    s_ = max(W / im.width, HH / im.height)
    im = im.resize((round(im.width * s_), round(im.height * s_)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - HH) // 2
    return im.crop((x, y, x + W, y + HH))


def licencia_ok(lic):
    l = lic.lower()
    if re.search(r"\bnc\b|\bnd\b|non-?commercial|no ?deriv", l):
        return False
    return bool(re.search(r"public domain|^pd|cc0|cc[ -]by", l))


def limpia(t):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t or "")).strip()


def commons(busqueda, n=6):
    q = urllib.parse.urlencode({"action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
                                "gsrsearch": busqueda + " filetype:bitmap", "gsrlimit": 12, "prop": "imageinfo",
                                "iiprop": "url|size|mime|extmetadata", "iiurlwidth": 1920})
    d = {}
    for intento in range(4):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(
                "https://commons.wikimedia.org/w/api.php?" + q, headers=UA), timeout=40))
            break
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(int(e.headers.get("Retry-After") or 10) + 5 * intento)
                continue
            print("commons:", e.code)
            return []
        except Exception as e:
            print("commons:", str(e)[:80])
            return []
    time.sleep(1)
    out = []
    for p in sorted((d.get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 99)):
        ii = (p.get("imageinfo") or [{}])[0]
        md = ii.get("extmetadata", {})
        lic = (md.get("LicenseShortName") or {}).get("value", "")
        if ii.get("mime") not in ("image/jpeg", "image/png") or ii.get("width", 0) < 1600 or not 1.45 <= ii.get("width", 1) / max(1, ii.get("height", 1)) <= 2.1 or not licencia_ok(lic):
            continue
        out.append({"url": ii.get("thumburl") or ii["url"], "pagina": ii.get("descriptionurl", ""),
                    "titulo": p["title"].replace("File:", "").rsplit(".", 1)[0],
                    "autor": limpia((md.get("Artist") or {}).get("value", ""))[:80] or "Wikimedia Commons",
                    "licencia": lic})
        if len(out) >= n:
            break
    return out


def bajar(url):
    for intento in range(4):
        try:
            b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
            time.sleep(0.5)
            return b
        except urllib.error.HTTPError as e:
            time.sleep((int(e.headers.get("Retry-After") or 8) if e.code == 429 else 3) + 5 * intento)
        except Exception:
            time.sleep(3 + 5 * intento)
    return None


def real(i, e):
    im = e["imagen"]
    cands = []
    usadas = {v.split(" · ")[-1] for v in CRED.values()}
    res, vistas = [], set(usadas)
    for q in [im["busqueda"]] + list(im.get("otras") or []) + [" ".join(im["busqueda"].split()[:2])]:
        for c in commons(q):
            if c["pagina"] not in vistas:
                vistas.add(c["pagina"])
                res.append(c)
        if len(res) >= 6:
            break
    for c in res:
        b = bajar(c["url"])
        if not b:
            continue
        try:
            pil = Image.open(io.BytesIO(b))
            pil.load()
        except Exception:
            continue
        c["pil"] = pil
        cands.append(c)
        if len(cands) == 6:
            break
    if not cands:
        return None
    mini = []
    for c in cands:
        t = c["pil"].convert("RGB")
        t.thumbnail((512, 512))
        buf = io.BytesIO()
        t.save(buf, "JPEG", quality=80)
        mini.append(buf.getvalue())
    q = f"""Vídeo de YouTube: "{H['titulo']}". Escena: «{e['hablado']}».
Se busca una imagen real que muestre: {im.get('descripcion', im['busqueda'])}.
Te paso {len(cands)} imágenes candidatas (en orden, desde 0). Títulos: {json.dumps([c['titulo'] for c in cands], ensure_ascii=False)}.
Elige la que mejor acompañe a la escena y quede bien en un vídeo. No hace falta que sea exactamente esa escena: vale una
obra de arte, foto o lugar real del mismo personaje, objeto, lugar o época (es un vídeo documental, el espectador lo
entiende). Descártalas solo si no tienen relación, tienen mala calidad, texto ilegible o son esquemas raros.
{L.get('reglas_reales', '')} Si ninguna encaja de verdad, elige -1 y escribe "prompt_ia": un prompt EN INGLÉS de 40-80
palabras para generar una imagen horizontal fotorrealista de la escena (sin texto, sin sangre, sin caras de personas reales).
Devuelve SOLO JSON: {{"elegida": <número o -1>, "prompt_ia": "..."}}"""
    try:
        j, _ = pedir(q, temp=0.2, imagenes=mini, max_tokens=2000)
    except SystemExit:
        return None
    k = j.get("elegida", -1) if isinstance(j, dict) else -1
    if isinstance(k, int) and 0 <= k < len(cands):
        c = cands[k]
        componer(c["pil"]).save(f"{D}/imgs/{i:02d}.jpg", quality=90)
        CRED[f"{i:02d}"] = f"{c['titulo']} · {c['autor']} · {c['licencia']} · {c['pagina']}"
        return True
    return j.get("prompt_ia") if isinstance(j, dict) else None


def cloudflare(prompt, out, ancho=1536, alto=864):
    A, T = os.environ["CF_ACCOUNT"].strip(), os.environ["CF_TOKEN"].strip()
    for intento, (extra, (ww, hh)) in enumerate([("", (ancho, alto)), (SEGURO, (ancho, alto)), (SEGURO, (1344, 768))]):
        r = subprocess.run(["curl", "-sS", "-m", "150", "-H", f"Authorization: Bearer {T}",
                            f"https://api.cloudflare.com/client/v4/accounts/{A}/ai/run/@cf/black-forest-labs/flux-2-klein-4b",
                            "-F", "prompt=" + ESTILO + prompt + extra, "-F", f"width={ww}", "-F", f"height={hh}"],
                           capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
        except Exception:
            d = {"errors": [r.stdout[:200] or r.stderr[:200]]}
        if d.get("success"):
            componer(Image.open(io.BytesIO(base64.b64decode(d["result"]["image"])))).save(out, quality=92)
            return "ok"
        err = json.dumps(d.get("errors"))
        if re.search(r"4006|allocation|neurons|quota|rate limit|429", err, re.I):
            return "cuota"
        print(f"  imagen IA intento {intento + 1}: {err[:160]}")
        time.sleep(2)
    return "fallo"


# ---------- clips de vídeo real (Pixabay, gratis, sin atribución obligatoria) ----------
PIXA = os.environ.get("PIXABAY_KEY", "").strip()
os.makedirs(f"{D}/clips", exist_ok=True)


def pixabay(q):
    if not PIXA:
        return []
    url = "https://pixabay.com/api/videos/?" + urllib.parse.urlencode(
        {"key": PIXA, "q": q[:100], "per_page": 20, "safesearch": "true", "video_type": "film"})
    for intento in range(3):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40))
            break
        except Exception as e:
            print("pixabay:", str(e)[:80])
            time.sleep(5)
    else:
        return []
    out = []
    for h in d.get("hits", []):
        tags = h.get("tags", "").lower()
        if h.get("duration", 0) < 5 or re.search(r"\bai\b|generated|3d|render|cgi|animation|abstract|digital art|"
                                                     r"hologram|futuristic|sci-fi|motion graphic|loop|background|particles", tags):
            continue
        v = h["videos"]
        # el tamaño más pequeño que llegue a 1920 de ancho (o el mayor disponible)
        opciones = sorted([x for x in v.values() if x.get("url")], key=lambda x: x.get("width", 0))
        buena = next((x for x in opciones if x.get("width", 0) >= 1900), opciones[-1] if opciones else None)
        if not buena or buena.get("width", 0) < 1200:
            continue
        thumb = (v.get("medium") or {}).get("thumbnail") or (v.get("small") or {}).get("thumbnail") \
            or (v.get("tiny") or {}).get("thumbnail")
        out.append({"id": h["id"], "url": buena["url"], "thumb": thumb, "tiny": (v.get("tiny") or {}).get("url"),
                    "tags": h.get("tags", ""), "pagina": h.get("pageURL", "")})
    return out


def miniatura_clip(c):
    if c.get("thumb"):
        b = bajar(c["thumb"])
        if b:
            return b
    if c.get("tiny"):  # sin miniatura: un fotograma del clip pequeño
        tmp = f"{D}/_tiny.mp4"
        b = bajar(c["tiny"])
        if b:
            open(tmp, "wb").write(b)
            r = subprocess.run(f'ffmpeg -v error -ss 1 -i "{tmp}" -frames:v 1 -f image2pipe -vcodec mjpeg -', shell=True,
                               capture_output=True)
            os.remove(tmp)
            return r.stdout or None
    return None


def bajar_clip(url, destino):
    b = bajar(url)
    if not b:
        return False
    open(destino, "wb").write(b)
    # fotograma fijo de la escena (para fundidos, miniaturas y por si el clip falla)
    r = subprocess.run(f'ffmpeg -v error -y -i "{destino}" -frames:v 1 -f image2pipe -vcodec mjpeg -', shell=True,
                       capture_output=True)
    if not r.stdout:
        return False
    componer(Image.open(io.BytesIO(r.stdout))).save(destino.replace("/clips/", "/imgs/").replace(".mp4", ".jpg"), quality=92)
    return True


def movimiento(ruta):
    """Diferencia media entre dos fotogramas separados 1,5 s (clip casi quieto = número bajo)."""
    fr = []
    for t in (0.5, 2.0):
        r = subprocess.run(f'ffmpeg -v error -ss {t} -i "{ruta}" -frames:v 1 -vf scale=160:90,format=gray -f rawvideo -',
                           shell=True, capture_output=True)
        fr.append(r.stdout)
    if len(fr[0]) != 14400 or len(fr[1]) != 14400:
        return 0
    import numpy as np
    return float(np.abs(np.frombuffer(fr[0], np.uint8).astype(float) - np.frombuffer(fr[1], np.uint8).astype(float)).mean())


def video(i, e):
    im = e["imagen"]
    usados = {x.get("imagen", {}).get("clip_id") for x in ESC}
    cands, vistos = [], set(usados)
    genericas = list(L.get("video_generico") or [])
    for q in [im["busqueda"]] + list(im.get("otras") or []) + genericas[(i * 3) % max(1, len(genericas)):][:3]:
        for c in pixabay(q):
            if c["id"] not in vistos:
                vistos.add(c["id"])
                cands.append(c)
        if len(cands) >= 12:
            break
    ok = []
    for c in cands[:8]:
        b = miniatura_clip(c)
        if b:
            try:
                t = Image.open(io.BytesIO(b)).convert("RGB")
                t.thumbnail((480, 480))
                buf = io.BytesIO()
                t.save(buf, "JPEG", quality=80)
                c["mini"] = buf.getvalue()
                ok.append(c)
            except Exception:
                pass
        if len(ok) == 6:
            break
    if not ok:
        return False
    q = f"""Vídeo documental de YouTube: "{H['titulo']}". Escena: «{e['hablado']}».
Se busca un clip de vídeo real que acompañe: {im.get('descripcion', im['busqueda'])}.
Te paso {len(ok)} fotogramas de clips candidatos (en orden, desde 0). Etiquetas: {json.dumps([c['tags'] for c in ok], ensure_ascii=False)}.
Elige el que mejor acompañe a la escena (vale algo relacionado con el lugar, el ambiente o la época, como en cualquier
documental). Descarta los que no peguen nada, los que se vean de otra época que desentone o con texto en pantalla.
Prefiere vídeo REAL y natural, como grabado con una cámara normal o un móvil: gente de verdad, calles, casas, trabajos,
lugares y objetos reales, con movimiento visible. DESCARTA todo lo que parezca hecho por ordenador o con IA (renders 3D,
animaciones, hologramas, efectos, ciudades o robots de ciencia ficción, fondos abstractos) y los planos casi quietos.
{L.get('reglas_reales', '')} Devuelve SOLO JSON con TODOS los que valen, del mejor al peor (lista vacía si ninguno):
{{"validos": [<números>]}}"""
    try:
        j, _ = pedir(q, temp=0.2, imagenes=[c["mini"] for c in ok], max_tokens=500)
        orden = [k for k in (j.get("validos") or []) if isinstance(k, int) and 0 <= k < len(ok)] if isinstance(j, dict) else []
    except SystemExit:
        orden = list(range(len(ok)))  # Gemini no responde: en el orden de Pixabay
    destino = f"{D}/clips/{i:02d}.mp4"
    for k in orden:
        c = ok[k]
        if not bajar_clip(c["url"], destino):
            continue
        mov = movimiento(destino)
        if mov < 3.0:   # casi quieto: parece una foto, se busca otro
            print(f"  escena {i}: clip {c['id']} casi sin movimiento ({mov:.1f}), descartado")
            continue
        im["clip"], im["clip_id"] = c["url"], c["id"]
        CRED[f"{i:02d}"] = f"Vídeo de Pixabay · {c['pagina']}"
        return True
    # ningún clip aprobado: vídeo real de ambiente del canal (nunca una foto)
    for q in genericas[i % max(1, len(genericas)):] + genericas:
        for c in pixabay(q):
            if c["id"] in usados or not bajar_clip(c["url"], destino):
                continue
            if movimiento(destino) >= 3.0:
                im["clip"], im["clip_id"] = c["url"], c["id"]
                CRED[f"{i:02d}"] = f"Vídeo de Pixabay · {c['pagina']}"
                print(f"  escena {i}: vídeo de ambiente ({q})")
                return True
    for f in (destino, destino.replace("/clips/", "/imgs/").replace(".mp4", ".jpg")):
        if os.path.exists(f):
            os.remove(f)
    return False


for i, e in enumerate(ESC, 1):
    if e["imagen"]["tipo"] != "video" or os.path.exists(f"{D}/imgs/{i:02d}.jpg"):
        continue
    if video(i, e):
        print(f"escena {i}: vídeo · {e['imagen']['clip_id']}")
    else:
        e["imagen"]["tipo"] = "real"   # sin clip: se intenta con una foto real
        print(f"escena {i}: sin clip de vídeo -> foto real")
    guardar()

# 1) material real (no gasta cuota de Cloudflare)
for i, e in enumerate(ESC, 1):
    if e["imagen"]["tipo"] != "real" or os.path.exists(f"{D}/imgs/{i:02d}.jpg"):
        continue
    r = real(i, e)
    if r is True:
        print(f"escena {i}: real · {CRED[f'{i:02d}'][:90]}")
    else:
        e["imagen"] = {"tipo": "ia", "prompt": r if isinstance(r, str) and len(r) > 30 else
                       f"Documentary photograph illustrating: {e['imagen'].get('descripcion', e['imagen']['busqueda'])}"}
        print(f"escena {i}: sin imagen real válida -> IA")
    guardar()

# 2) imagen base de la miniatura (prioridad) y escenas de IA, hasta agotar la cuota del día
pend = []
if not os.path.exists(f"{D}/miniatura_base.jpg"):
    pend.append(("miniatura", H["miniatura"]["prompt"], f"{D}/miniatura_base.jpg"))
pend += [(i, e["imagen"]["prompt"], f"{D}/imgs/{i:02d}.jpg") for i, e in enumerate(ESC, 1)
         if e["imagen"]["tipo"] == "ia" and not os.path.exists(f"{D}/imgs/{i:02d}.jpg")]
hechas = 0
for k, (i, prompt, out) in enumerate(pend):
    r = cloudflare(prompt, out)
    if r == "cuota":
        print(f"CUOTA de Cloudflare agotada: {hechas} imágenes hoy, faltan {len(pend) - k}")
        guardar()
        faltan_ia = [x for x in pend[k:] if isinstance(x[0], int)]
        if not os.environ.get("FORZAR") or len(faltan_ia) > 3:
            sys.exit(3)   # se sigue otro día con la cuota nueva (nunca rellenar un vídeo con imágenes repetidas)
        # FORZAR: completa con imágenes ya hechas (otro encuadre y en espejo) para no esperar al día siguiente
        hay = [j for j in range(1, len(ESC) + 1) if os.path.exists(f"{D}/imgs/{j:02d}.jpg")]
        if not hay:
            sys.exit(3)
        for (i2, _, out2) in pend[k:]:
            if not isinstance(i2, int):
                continue
            j = min(hay, key=lambda j: abs(j - i2))
            im = Image.open(f"{D}/imgs/{j:02d}.jpg").transpose(Image.FLIP_LEFT_RIGHT)
            im = im.crop((160, 90, W - 160, HH - 90)).resize((W, HH), Image.LANCZOS)
            im.save(out2, quality=92)
            print(f"escena {i2}: sin cuota, reutilizo la {j} con otro encuadre")
        break
    if r == "fallo":
        e = ESC[i - 1] if isinstance(i, int) else None
        if e is not None:  # se queda con la imagen de la escena vecina para no perder el vídeo
            vec = [j for j in range(1, len(ESC) + 1) if os.path.exists(f"{D}/imgs/{j:02d}.jpg")]
            if vec:
                j = min(vec, key=lambda j: abs(j - i))
                Image.open(f"{D}/imgs/{j:02d}.jpg").save(out, quality=92)
                print(f"escena {i}: bloqueada, reutilizo la {j}")
    hechas += 1
guardar()
faltan = [i for i in range(1, len(ESC) + 1) if not os.path.exists(f"{D}/imgs/{i:02d}.jpg")]
if faltan:
    print("faltan imágenes:", faltan)
    sys.exit(3)
n_vid = sum(1 for e in ESC if e["imagen"]["tipo"] == "video")
n_real = sum(1 for e in ESC if e["imagen"]["tipo"] == "real")
print(f"IMÁGENES OK · {len(ESC)} escenas ({n_vid} vídeo, {n_real} fotos reales, {len(ESC) - n_vid - n_real} IA) · hoy {hechas} de IA")
