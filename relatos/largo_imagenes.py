#!/usr/bin/env python3
"""Imágenes de un vídeo largo (1920x1080): material REAL de Wikimedia Commons (revisado por Gemini) + imágenes de IA
de Cloudflare hasta agotar la cuota gratis del día. Se puede ejecutar varios días seguidos: solo hace lo que falta.

Uso: python3 largo_imagenes.py <carpeta> <canal.json>
Sale con 0 si están todas, 3 si la cuota de Cloudflare se ha agotado y faltan imágenes (se sigue otro día).
"""
import base64, io, json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gem import pedir
import stock
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


def pixabay(q, pagina=1):
    if not PIXA:
        return []
    url = "https://pixabay.com/api/videos/?" + urllib.parse.urlencode(
        {"key": PIXA, "q": q[:100], "per_page": 30, "page": pagina, "safesearch": "true", "video_type": "film"})
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


def bajar_extra(c, destino):
    """Trozo de vídeo de Commons/NASA/Internet Archive + su fotograma a pantalla completa."""
    if not stock.bajar_segmento(c, destino, segundos=20):
        return False
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


def candidatos(q):
    """Pixabay (horizontal, Full HD) + las demás fuentes del canal (Wikimedia Commons, NASA, Internet Archive)."""
    out = pixabay(q)[:6]
    for f in [f for f in (C.get("fuentes") or []) if f != "pixabay"]:
        try:
            out += {"commons": stock.commons, "nasa": stock.nasa, "archive": stock.archive,
                    "mixkit": stock.mixkit}[f](q)[:4 if f == "mixkit" else 3]
        except Exception as ex:
            print("  fuente", f, str(ex)[:60])
    return out


def video(i, e):
    im = e["imagen"]
    usados = {x.get("imagen", {}).get("clip_id") for x in ESC}
    cands, vistos = [], set(usados)
    genericas = list(L.get("video_generico") or [])
    for q in [im["busqueda"]] + list(im.get("otras") or []) + genericas[(i * 3) % max(1, len(genericas)):][:3]:
        for c in candidatos(q):
            if c["id"] not in vistos:
                vistos.add(c["id"])
                cands.append(c)
        if len(cands) >= 12:
            break
    ok = []
    for c in cands[:12]:
        try:
            b = stock.miniatura(c) if c.get("fuente") else miniatura_clip(c)
        except Exception:
            b = None
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
        if len(ok) == 8:
            break
    if not ok:
        return False
    q = f"""Vídeo documental de YouTube: "{H['titulo']}". Escena: «{e['hablado']}».
Se busca un clip de vídeo real que acompañe: {im.get('descripcion', im['busqueda'])}.
Te paso {len(ok)} fotogramas de clips candidatos (en orden, desde 0). Etiquetas o títulos: {json.dumps([c['tags'][:80] for c in ok], ensure_ascii=False)}.
Pueden venir de un banco de vídeo, de Wikimedia Commons, de la NASA o de archivo histórico (estos con calidad de época:
valen si encajan con la época de lo que se cuenta). Descarta los muy borrosos o pixelados.
Elige el que mejor acompañe a la escena (vale algo relacionado con el lugar, el ambiente o la época, como en cualquier
documental). Descarta los que no peguen nada, los que se vean de otra época que desentone o con texto en pantalla.
Prefiere vídeo REAL y natural, como grabado con una cámara normal o un móvil: gente de verdad, calles, casas, trabajos,
lugares y objetos reales, con movimiento visible. DESCARTA todo lo que parezca hecho por ordenador o con IA (renders 3D,
animaciones, hologramas, efectos, ciudades o robots de ciencia ficción, fondos abstractos) y los planos casi quietos.
Que se reconozca el tema del vídeo: {C.get('visual', '')} Un paisaje genérico solo si no hay nada más concreto.
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
        if not (bajar_extra(c, destino) if c.get("fuente") else bajar_clip(c["url"], destino)):
            continue
        mov = movimiento(destino)
        if mov < 3.0:   # casi quieto: parece una foto, se busca otro
            print(f"  escena {i}: clip {c['id']} casi sin movimiento ({mov:.1f}), descartado")
            continue
        im["clip"], im["clip_id"] = c["url"], c["id"]
        if c.get("fuente"):
            im["clip_ini"] = c.get("inicio", 1)
        CRED[f"{i:02d}"] = c.get("credito") or f"Vídeo de Pixabay · {c['pagina']}"
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


def ambiente(i, e):
    """Vídeo real de ambiente del canal (cuando ningún clip concreto vale)."""
    im, destino = e["imagen"], f"{D}/clips/{i:02d}.mp4"
    usados = {str(x.get("imagen", {}).get("clip_id")) for x in ESC} | {str(x) for x in H.get("vetados", [])}
    genericas = list(L.get("video_generico") or [])
    for q in genericas[i % max(1, len(genericas)):] + genericas:
        for c in pixabay(q):
            if str(c["id"]) in usados or not bajar_clip(c["url"], destino):
                continue
            if movimiento(destino) >= 3.0:
                im["clip"], im["clip_id"] = c["url"], c["id"]
                CRED[f"{i:02d}"] = f"Vídeo de Pixabay · {c['pagina']}"
                print(f"  escena {i}: vídeo de ambiente ({q})")
                return True
    return False


def lote(indices):
    """Clips para varias escenas con UNA sola consulta a Gemini (antes era una por escena)."""
    vistos = {str(x.get("imagen", {}).get("clip_id")) for x in ESC if x.get("imagen", {}).get("clip_id")}
    vistos |= {str(x) for x in H.get("vetados", [])}
    gen = list(L.get("video_generico") or [])
    items = []
    for i in indices:
        im = ESC[i - 1]["imagen"]
        b = {"busqueda": im.get("busqueda", ""), "otras": list(im.get("otras") or [])}
        c = stock.preparar(i, b, gen, vistos, maximo=6, buscador=candidatos)
        vistos |= {str(x["id"]) for x in c}
        items.append((i, ESC[i - 1]["hablado"], c))
    orden = stock.elegir_lote(H["titulo"], items, L.get("reglas_reales", ""), C.get("visual", ""), "horizontal")
    hechos = set()
    for i, _, c in items:
        im, destino = ESC[i - 1]["imagen"], f"{D}/clips/{i:02d}.mp4"
        for k in orden.get(i, []):
            cc = c[k]
            if not (bajar_extra(cc, destino) if cc.get("fuente") else bajar_clip(cc["url"], destino)):
                continue
            if movimiento(destino) < 3.0:
                continue
            im["clip"], im["clip_id"] = cc["url"], cc["id"]
            if cc.get("fuente"):
                im["clip_ini"] = cc.get("inicio", 1)
            CRED[f"{i:02d}"] = cc.get("credito") or f"Vídeo de Pixabay · {cc['pagina']}"
            hechos.add(i)
            break
        if i not in hechos and ambiente(i, ESC[i - 1]):
            hechos.add(i)
        if i not in hechos:
            for f in (destino, destino.replace("/clips/", "/imgs/").replace(".mp4", ".jpg")):
                if os.path.exists(f):
                    os.remove(f)
    return hechos


# ---------- REGLA DEL USUARIO: en los largos TODO es vídeo en movimiento, nunca fotos ni imágenes fijas ----------
def usados_ids():
    ids = {str(x) for x in H.get("vetados", [])}   # clips que dieron imagen quieta: no se vuelven a usar
    for x in ESC:
        im_ = x.get("imagen", {})
        ids.add(str(im_.get("clip_id")))
        ids |= {str(y.get("clip_id")) for y in im_.get("extra", [])}
    return ids


def clip_pixabay(qs, destino, paginas=(1, 2)):
    """Primer clip de Pixabay con movimiento de verdad para esas búsquedas, que no se haya usado ya en el vídeo."""
    usados = usados_ids()
    for pag in paginas:
        for q in qs:
            for c in pixabay(q, pag):
                if str(c["id"]) in usados or not bajar_clip(c["url"], destino):
                    continue
                if movimiento(destino) >= 3.0:
                    return c
    return None


def rescate(i):
    """Escena sin clip concreto ni de ambiente: búsquedas más amplias (2 páginas) y, como último recurso, otro trozo de
    un clip ya usado (con movimiento). NUNCA una foto."""
    im, destino = ESC[i - 1]["imagen"], f"{D}/clips/{i:02d}.mp4"
    pal = [w for w in re.findall(r"[A-Za-z]+", im.get("busqueda", "")) if len(w) > 3]
    qs = pal[:2] + list(L.get("video_generico") or []) + list(L.get("video_rescate") or [])
    c = clip_pixabay(qs, destino)
    if c:
        im.update(tipo="video", clip=c["url"], clip_id=c["id"])
        im.pop("clip_ini", None)
        CRED[f"{i:02d}"] = f"Vídeo de Pixabay · {c['pagina']}"
        return True
    return False


def extras():
    """Si el clip es más corto que lo que dura la escena, se le añaden más clips (hasta 3) en vez de ralentizarlo o
    dejarlo congelado. La duración de la escena se calcula con el texto hablado (misma velocidad que la voz)."""
    for i, e in enumerate(ESC, 1):
        im = e["imagen"]
        base = f"{D}/clips/{i:02d}.mp4"
        if im.get("tipo") != "video" or not os.path.exists(base):
            continue
        necesita = len("".join(e["hablado"].split())) / 12.5 + 2.0
        total = dur(base)
        im.setdefault("extra", [])
        total += sum(dur(f"{D}/clips/{i:02d}_{n + 1}.mp4") for n in range(len(im["extra"]))
                     if os.path.exists(f"{D}/clips/{i:02d}_{n + 1}.mp4"))
        # RITMO: un plano distinto cada ~5,5 s (y siempre clips suficientes para cubrir la escena sin congelar)
        planos = min(4, max(1, int(-(-necesita // 5.5))))
        while (total < necesita * 1.1 or 1 + len(im["extra"]) < planos) and len(im["extra"]) < 3:
            n = len(im["extra"]) + 1
            dst = f"{D}/clips/{i:02d}_{n}.mp4"
            qs = [im.get("busqueda", "")] + list(im.get("otras") or []) + list(L.get("video_generico") or [])
            c = clip_pixabay([q for q in qs if q], dst, paginas=(1,))
            if not c:
                break
            im["extra"].append({"clip": c["url"], "clip_id": c["id"]})
            CRED[f"{i:02d}_{n}"] = f"Vídeo de Pixabay · {c['pagina']}"
            total += dur(dst)
            print(f"escena {i}: clip extra {n} ({c['id']}) para cubrir {necesita:.0f} s")
        guardar()


def dur(ruta):
    r = subprocess.run(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{ruta}"', shell=True,
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


pend = [i for i, e in enumerate(ESC, 1) if e["imagen"]["tipo"] == "video" and not os.path.exists(f"{D}/imgs/{i:02d}.jpg")]
for k in range(0, len(pend), 12):
    hechos = lote(pend[k:k + 12])
    for i in pend[k:k + 12]:
        if i in hechos:
            print(f"escena {i}: vídeo · {ESC[i - 1]['imagen']['clip_id']}")
        elif rescate(i):
            print(f"escena {i}: vídeo de rescate · {ESC[i - 1]['imagen']['clip_id']}")
        else:
            print(f"escena {i}: SIN VÍDEO (nunca se pone una foto): se reintenta en la próxima ejecución")
    guardar()

# 1) (DESACTIVADO por orden del usuario: nada de fotos en los largos) las escenas que el guion pedía como foto
#    real se buscan como vídeo, igual que las de IA (paso 2)
for i, e in enumerate(ESC, 1):
    if e["imagen"]["tipo"] == "real" and not os.path.exists(f"{D}/imgs/{i:02d}.jpg"):
        e["imagen"]["tipo"] = "ia"
        e["imagen"].setdefault("prompt", e["imagen"].get("descripcion", e["imagen"].get("busqueda", "")))
for i, e in enumerate(ESC, 1):
    if True:
        continue
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

# 2) regla del usuario: en los largos TODO es vídeo real de internet. Las escenas que el guion pedía con IA o que
#    se han quedado sin foto real se buscan también en vídeo (y si no hay nada concreto, vídeo de ambiente del canal).
for i, e in enumerate(ESC, 1):
    if e["imagen"]["tipo"] != "ia" or os.path.exists(f"{D}/imgs/{i:02d}.jpg"):
        continue
    im = e["imagen"]
    pal = [w for w in re.findall(r"[A-Za-z]+", im.get("prompt", "")) if w.lower() not in
           {"a", "an", "the", "of", "in", "on", "with", "and", "photo", "photograph", "documentary", "illustrating",
            "cinematic", "realistic", "image", "shot", "style", "showing", "at", "by", "for", "from", "to"}]
    im.setdefault("busqueda", " ".join(pal[:4]) or "dramatic sky clouds")
    im.setdefault("descripcion", im.get("prompt", ""))
pend = [i for i, e in enumerate(ESC, 1) if e["imagen"]["tipo"] == "ia" and not os.path.exists(f"{D}/imgs/{i:02d}.jpg")]
for k in range(0, len(pend), 12):
    hechos = lote(pend[k:k + 12])
    for i in pend[k:k + 12]:
        if i in hechos or rescate(i):
            ESC[i - 1]["imagen"]["tipo"] = "video"
            print(f"escena {i}: vídeo real · {ESC[i - 1]['imagen']['clip_id']}")
    guardar()
extras()

# 3) imagen base de la miniatura: un fotograma REAL del propio vídeo (lo elige Gemini). La IA solo si no hay nada.
if not os.path.exists(f"{D}/miniatura_base.jpg"):
    cand = [i for i in range(1, len(ESC) + 1) if os.path.exists(f"{D}/imgs/{i:02d}.jpg")]
    if cand:
        paso_ = max(1, len(cand) // 10)
        cand = cand[::paso_][:10]
        minis = []
        for i in cand:
            t = Image.open(f"{D}/imgs/{i:02d}.jpg").convert("RGB")
            t.thumbnail((480, 480))
            buf = io.BytesIO()
            t.save(buf, "JPEG", quality=80)
            minis.append(buf.getvalue())
        elegido = cand[0]
        try:
            j, _ = pedir(f"""Miniatura de YouTube para el vídeo "{H['titulo_youtube']}". Idea de la miniatura:
{H['miniatura'].get('prompt', '')}. Te paso {len(cand)} fotogramas reales del vídeo (desde 0). Elige el que mejor
funcionaría de fondo de miniatura: impactante, claro en pequeño, con un sujeto o lugar fuerte, buen contraste y sin
texto. Devuelve SOLO JSON: {{"mejor": <número>}}""", temp=0.2, imagenes=minis, max_tokens=300)
            k = j.get("mejor") if isinstance(j, dict) else None
            if isinstance(k, int) and 0 <= k < len(cand):
                elegido = cand[k]
        except SystemExit:
            pass
        Image.open(f"{D}/imgs/{elegido:02d}.jpg").save(f"{D}/miniatura_base.jpg", quality=92)
        print(f"miniatura: fondo real de la escena {elegido}")

# 4) IA de Cloudflare solo para lo que no haya podido ser real (casi nunca), hasta agotar la cuota del día
pend = []
if not os.path.exists(f"{D}/miniatura_base.jpg"):
    pend.append(("miniatura", H["miniatura"]["prompt"], f"{D}/miniatura_base.jpg"))
# (escenas con IA: desactivado, en los largos todo es vídeo real)
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
faltan = [i for i, e in enumerate(ESC, 1) if e["imagen"]["tipo"] != "video" or not e["imagen"].get("clip")]
if faltan:
    print("escenas SIN VÍDEO (no se monta con fotos; se sigue en la próxima ejecución):", faltan)
    sys.exit(3)
n_vid = sum(1 for e in ESC if e["imagen"]["tipo"] == "video")
n_real = sum(1 for e in ESC if e["imagen"]["tipo"] == "real")
print(f"IMÁGENES OK · {len(ESC)} escenas ({n_vid} vídeo, {n_real} fotos reales, {len(ESC) - n_vid - n_real} IA) · hoy {hechas} de IA")
