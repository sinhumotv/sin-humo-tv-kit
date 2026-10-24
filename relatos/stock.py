"""Clips de vídeo REAL de internet para los CORTOS verticales (y fuentes extra para los LARGOS).

Fuentes (todas gratis; las que usa cada canal van en "fuentes" de canales/<canal>.json):
  - pixabay: banco de vídeo (clave PIXABAY_KEY), sin atribución obligatoria.
  - commons: vídeos de Wikimedia Commons con licencia libre (CC0, CC BY, CC BY-SA, dominio público): se cita al autor.
  - nasa:    vídeos de la NASA (dominio público), en alta calidad.
  - archive: películas y noticiarios antiguos de dominio público de Internet Archive (baja resolución, aire de época).
De commons, nasa y archive se baja solo un trozo de unos 14 s, ya recodificado a MP4.

Se usa en dos casos (ver fabricar.py):
  - prueba A/B: algunos cortos del día se hacen solo con vídeo real (MODO_IMG=real);
  - plan B: si Cloudflare no puede hacer una imagen (sin cuota o la rechaza), esa escena va con vídeo real.
Gemini elige, mirando fotogramas, el clip que mejor acompaña a cada escena; nunca se usan renders/IA/animaciones.
"""
import io, json, os, re, subprocess, time, urllib.error, urllib.parse, urllib.request

from PIL import Image

UA = {"User-Agent": "SinHumoTV-cortos/1.0 (https://github.com/sinhumotv/sin-humo-tv-kit; sinhumotv@users.noreply.github.com)"}
NO_REAL = re.compile(r"\bai\b|generated|3d|render|cgi|animation|animated|abstract|digital art|hologram|futuristic|"
                     r"sci-fi|motion graphic|loop|background|particles|cartoon|illustration", re.I)


def clave():
    return "".join(os.environ.get("PIXABAY_KEY", "").split())


def hay_fuentes(fuentes):
    return bool(clave()) or any(f != "pixabay" for f in fuentes)


def bajar(url, timeout=120):
    for intento in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        except Exception as e:
            print("  descarga:", str(e)[:80])
            time.sleep(3)
    return None


def buscar(q):
    k = clave()
    if not k:
        return []
    url = "https://pixabay.com/api/videos/?" + urllib.parse.urlencode(
        {"key": k, "q": q[:100], "per_page": 30, "safesearch": "true", "video_type": "film"})
    d = None
    for intento in range(3):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40))
            break
        except Exception as e:
            print("  pixabay:", str(e)[:80])
            time.sleep(5)
    out = []
    for h in (d or {}).get("hits", []):
        if h.get("duration", 0) < 4 or NO_REAL.search(h.get("tags", "")):
            continue
        v = h["videos"]
        ops = [x for x in v.values() if x.get("url")]
        if not ops:
            continue
        # vertical: se recorta el centro, así que interesa la mayor altura (sin pasar de 4K)
        buena = max(ops, key=lambda x: (min(x.get("height", 0), 2160), -x.get("size", 0)))
        if buena.get("height", 0) < 1080:
            continue
        vertical = buena.get("height", 0) > buena.get("width", 1)
        thumb = (v.get("medium") or {}).get("thumbnail") or (v.get("small") or {}).get("thumbnail")
        out.append({"id": str(h["id"]), "url": buena["url"], "thumb": thumb, "tags": h.get("tags", ""),
                    "pagina": h.get("pageURL", ""), "vertical": vertical, "fuente": "pixabay",
                    "credito": f"Vídeo de Pixabay · {h.get('pageURL', '')}"})
    out.sort(key=lambda c: not c["vertical"])  # primero los grabados en vertical
    return out


def _json(url, timeout=40):
    for intento in range(3):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(20)
                continue
            print("  fuente:", url[:60], e.code)
            return None
        except Exception as e:
            print("  fuente:", url[:60], str(e)[:60])
            time.sleep(3)
    return None


def _limpia(t):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t or "")).strip()


def _licencia_ok(lic):
    l = lic.lower()
    if re.search(r"\bnc\b|\bnd\b|non-?commercial|no ?deriv", l):
        return False
    return bool(re.search(r"public domain|^pd|cc0|cc[ -]by", l))


def commons(q, minimo=720):
    d = _json("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
         "gsrsearch": q + " filetype:video", "gsrlimit": 15, "prop": "imageinfo",
         "iiprop": "url|size|mime|extmetadata", "iiurlwidth": 480}))
    out = []
    for pg in ((d or {}).get("query") or {}).get("pages", {}).values():
        ii = (pg.get("imageinfo") or [{}])[0]
        md = ii.get("extmetadata") or {}
        lic = _limpia((md.get("LicenseShortName") or {}).get("value", ""))
        if not _licencia_ok(lic) or min(ii.get("width", 0), ii.get("height", 0)) < minimo:
            continue
        if NO_REAL.search(pg.get("title", "") + " " + _limpia((md.get("Categories") or {}).get("value", ""))):
            continue
        autor = _limpia((md.get("Artist") or {}).get("value", ""))[:80] or "autor desconocido"
        out.append({"id": "wc:" + pg["title"], "url": ii["url"], "thumb": ii.get("thumburl"), "inicio": 1,
                    "tags": pg["title"].replace("File:", ""), "pagina": ii.get("descriptionurl", ""),
                    "vertical": ii.get("height", 0) > ii.get("width", 1), "fuente": "commons", "atribucion": True,
                    "credito": f"{autor} ({lic}), Wikimedia Commons · {ii.get('descriptionurl', '')}"})
    return out


def nasa(q):
    d = _json("https://images-api.nasa.gov/search?" + urllib.parse.urlencode({"q": q, "media_type": "video"}))
    out = []
    for it in ((d or {}).get("collection") or {}).get("items", [])[:12]:
        dt_ = (it.get("data") or [{}])[0]
        tit = dt_.get("title", "")
        if re.search(r"animation|simulation|render|graphic", dt_.get("nasa_id", ""), re.I) or re.search(r"briefing|conference|interview|ceremony|webinar|town hall|podcast|live|remarks|speech|animation|"
                     r"simulation|visualization|graphic", tit + " " + " ".join(dt_.get("keywords") or []), re.I):
            continue
        thumb = next((l["href"] for l in it.get("links", []) if l.get("render") == "image"), None)
        out.append({"id": "nasa:" + dt_.get("nasa_id", ""), "coleccion": it.get("href"), "thumb": thumb, "inicio": 6,
                    "tags": tit, "pagina": f"https://images.nasa.gov/details/{dt_.get('nasa_id', '')}",
                    "vertical": False, "fuente": "nasa",
                    "credito": f"Vídeo de la NASA · https://images.nasa.gov/details/{dt_.get('nasa_id', '')}"})
    return out


def archive(q):
    d = _json("https://archive.org/advancedsearch.php?" + urllib.parse.urlencode(
        {"q": f"({q}) AND mediatype:movies AND (collection:prelinger OR collection:universal_newsreels)",
         "fl[]": "identifier,title", "rows": 8, "output": "json"}))
    out = []
    for doc in ((d or {}).get("response") or {}).get("docs", []):
        ide = doc["identifier"]
        out.append({"id": "ia:" + ide, "ia": ide, "thumb": None, "tags": doc.get("title", ""),
                    "pagina": f"https://archive.org/details/{ide}", "vertical": False, "fuente": "archive",
                    "credito": f"Internet Archive (dominio público) · https://archive.org/details/{ide}"})
    return out


def _resolver(c):
    """URL directa del vídeo (NASA e Internet Archive la dan aparte) y punto de inicio del trozo."""
    if c.get("url"):
        return c["url"]
    if c["fuente"] == "nasa" and c.get("coleccion"):
        fs = _json(c["coleccion"]) or []
        for suf in ("~large.mp4", "~orig.mp4", "~medium.mp4"):
            u = next((f for f in fs if f.endswith(suf)), None)
            if u:
                c["url"] = u.replace("http://", "https://").replace(" ", "%20")
                return c["url"]
    if c["fuente"] == "archive":
        m = _json(f"https://archive.org/metadata/{c['ia']}") or {}
        fs = [f for f in m.get("files", []) if f.get("name", "").lower().endswith(".mp4")]
        fs.sort(key=lambda f: -int(f.get("height") or 0) or -int(f.get("size") or 0))
        if fs:
            dur = float(fs[0].get("length") or 0) if str(fs[0].get("length", "")).replace(".", "").isdigit() else 0
            import zlib
            c["inicio"] = 30 + zlib.crc32(c["ia"].encode()) % max(1, int(dur - 60)) if dur > 120 else 5
            c["url"] = f"https://archive.org/download/{c['ia']}/{urllib.parse.quote(fs[0]['name'])}"
            return c["url"]
    return None


def miniatura(c):
    """Fotograma pequeño del candidato (de su miniatura o del propio vídeo en el punto de inicio)."""
    if c.get("thumb"):
        b = bajar(c["thumb"], 40)
        if b:
            return b
    u = _resolver(c)
    if not u:
        return None
    r = subprocess.run(f'ffmpeg -v error -ss {c.get("inicio", 1) + 2} -i "{u}" -frames:v 1 -vf scale=400:-2 '
                       f'-f image2pipe -vcodec mjpeg -', shell=True, capture_output=True, timeout=90)
    return r.stdout or None


def bajar_segmento(c, mp4, segundos=14):
    """Baja un trozo del vídeo (fuentes distintas de Pixabay), recodificado a MP4 sin agrandarlo."""
    u = _resolver(c)
    if not u:
        return False
    r = subprocess.run(f'ffmpeg -v error -y -ss {c.get("inicio", 1)} -i "{u}" -t {segundos} -an '
                       f'-vf "scale=\'min(1920,iw)\':-2,fps=30" -c:v libx264 -preset veryfast -crf 19 -pix_fmt yuv420p "{mp4}"',
                       shell=True, capture_output=True, timeout=600)
    return r.returncode == 0 and os.path.exists(mp4) and os.path.getsize(mp4) > 50000


def buscar_todo(q, fuentes=("pixabay",)):
    """Candidatos de todas las fuentes del canal, intercalados para que Gemini elija entre todas."""
    listas = []
    for f in fuentes:
        try:
            listas.append({"pixabay": buscar, "commons": commons, "nasa": nasa, "archive": archive}[f](q))
        except Exception as e:
            print("  fuente", f, str(e)[:80])
    cupo = {"pixabay": 5, "commons": 3, "nasa": 3, "archive": 2}
    out = []
    for k in range(max([len(l) for l in listas] or [0])):
        for l in listas:
            if k < len(l) and k < cupo.get(l[0]["fuente"], 3):
                out.append(l[k])
    return out


def movimiento(ruta):
    fr = []
    for t in (0.5, 2.0):
        r = subprocess.run(f'ffmpeg -v error -ss {t} -i "{ruta}" -frames:v 1 -vf scale=160:90,format=gray -f rawvideo -',
                           shell=True, capture_output=True)
        fr.append(r.stdout)
    if len(fr[0]) != 14400 or len(fr[1]) != 14400:
        return 0
    import numpy as np
    return float(np.abs(np.frombuffer(fr[0], np.uint8).astype(float) - np.frombuffer(fr[1], np.uint8).astype(float)).mean())


def _fotograma_vertical(mp4, jpg, W=1080, H=1920):
    r = subprocess.run(f'ffmpeg -v error -y -ss 0.3 -i "{mp4}" -frames:v 1 -vf "scale={W}:{H}:force_original_aspect_ratio=increase,'
                       f'crop={W}:{H}" -q:v 2 "{jpg}"', shell=True, capture_output=True)
    return r.returncode == 0 and os.path.exists(jpg)


def _bajar_clip(c, mp4, jpg):
    if c.get("fuente", "pixabay") == "pixabay":
        b = bajar(c["url"])
        if not b:
            return False
        open(mp4, "wb").write(b)
    elif not bajar_segmento(c, mp4):
        return False
    if movimiento(mp4) < 3.0:  # casi quieto: parece una foto
        print(f"  clip {c['id']} casi sin movimiento, descartado")
        return False
    return _fotograma_vertical(mp4, jpg)


def busquedas(titulo, escenas, tema="", visual=""):
    """Una búsqueda en inglés (y 2 alternativas) por escena, pensadas para un banco de vídeo real. Usa Gemini."""
    from gem import pedir
    lista = "\n".join(f"{k}. {e['hablado']}" for k, e in enumerate(escenas))
    q = f"""Vídeo corto vertical de redes: "{titulo}" ({tema}). Escenas (lo que dice la voz):
{lista}
Para cada escena, escribe una búsqueda corta EN INGLÉS (2-4 palabras) para encontrar en Pixabay un clip de VÍDEO REAL
(grabado con cámara, no animación) que muestre LO CONCRETO que se cuenta en esa escena, de forma que quien lo vea sin
sonido reconozca el tema del vídeo. LO QUE TIENE QUE VERSE EN ESTE CANAL: {visual}
Piensa como un montador de documentales: si la escena es imposible de grabar (un dios, un monstruo, el futuro), busca
algo real y reconocible del tema que la represente (p. ej. la estatua o el templo de ese dios, el lugar del caso, la
tecnología real de la que se habla), no un paisaje cualquiera. Varía: que no salgan dos escenas con lo mismo.
Añade 2 alternativas un poco más generales pero del mismo tema. Nada de sangre, armas apuntando ni violencia explícita.
Devuelve SOLO JSON: {{"escenas": [{{"busqueda": "...", "otras": ["...", "..."]}}, ...]}} (una por escena, en orden)."""
    try:
        j, _ = pedir(q, temp=0.4, max_tokens=4000)
        es = j.get("escenas") if isinstance(j, dict) else None
        if isinstance(es, list) and len(es) >= len(escenas):
            return es[:len(escenas)]
    except SystemExit:
        pass
    return [{"busqueda": " ".join(re.findall(r"[A-Za-z]+", e.get("prompt", ""))[:4]) or "dramatic sky", "otras": []}
            for e in escenas]


def clip_para(i, escena, b, genericas, usados, dir_clips, dir_imgs, titulo, reglas="", visual="", fuentes=("pixabay",)):
    """Busca, elige y baja un clip para la escena i (1..n). Devuelve dict con clip/creditos o None."""
    from gem import pedir
    mp4, jpg = f"{dir_clips}/{i:02d}.mp4", f"{dir_imgs}/{i:02d}.jpg"
    cands, vistos = [], {str(x) for x in usados}
    gen = list(genericas or [])
    for q in [b.get("busqueda", "")] + list(b.get("otras") or []) + gen[(i * 3) % max(1, len(gen)):][:2]:
        if not q:
            continue
        for c in buscar_todo(q, fuentes):
            if c["id"] not in vistos:
                vistos.add(c["id"])
                cands.append(c)
        if len(cands) >= 12:
            break
    ok = []
    for c in cands[:12]:
        try:
            t = miniatura(c)
        except Exception:
            t = None
        if not t:
            continue
        try:
            im = Image.open(io.BytesIO(t)).convert("RGB")
            im.thumbnail((400, 400))
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=80)
            c["mini"] = buf.getvalue()
            ok.append(c)
        except Exception:
            pass
        if len(ok) == 8:
            break
    orden = []
    if ok:
        q = f"""Vídeo corto vertical: "{titulo}". Escena: «{escena['hablado']}».
Te paso {len(ok)} fotogramas de clips de vídeo candidatos (desde 0). Etiquetas o títulos: {json.dumps([c['tags'][:80] for c in ok], ensure_ascii=False)}.
Pueden venir de un banco de vídeo moderno, de Wikimedia Commons, de la NASA o de archivo histórico (estos últimos con
calidad de época: valen si encajan con la época del relato o del caso). Descarta los que se vean muy borrosos o pixelados.
Se recortarán en VERTICAL por el centro. Elige los que muestren de forma RECONOCIBLE lo que cuenta la escena y el tema
del vídeo. Lo que tiene que verse en este canal: {visual}
Un paisaje o un cielo genérico solo vale si de verdad no hay nada más concreto entre los candidatos. Descarta lo que no pegue nada, lo que tenga texto o logotipos, lo que
parezca hecho por ordenador y los que pierdan lo importante al recortar el centro.
MUY IMPORTANTE: si la historia es antigua o de otra época, descarta gente con ropa, peinados, coches, móviles u objetos
actuales (mejor paisajes, ruinas, fuego, agua, cielo, manos, objetos antiguos). Descarta mascotas y animales graciosos,
caras sonrientes a cámara, deporte, fiestas y cualquier cosa alegre o turística que rompa el tono del relato.
{reglas}
Sé exigente: es mejor no elegir ninguno que poner uno que desentone.
Devuelve SOLO JSON con los válidos, del mejor al peor: {{"validos": [<números>]}}"""
        try:
            j, _ = pedir(q, temp=0.2, imagenes=[c["mini"] for c in ok], max_tokens=500)
            v = [k for k in (j.get("validos") or []) if isinstance(k, int) and 0 <= k < len(ok)] if isinstance(j, dict) else []
            orden = v   # solo los aprobados; si ninguno convence, vídeo de ambiente del canal
        except SystemExit:
            pass
    for k in orden:
        if _bajar_clip(ok[k], mp4, jpg):
            return {"clip": mp4, "clip_id": ok[k]["id"], "credito": ok[k]["credito"], "atribucion": ok[k].get("atribucion", False)}
    # último recurso: vídeo de ambiente del canal
    for q in gen[i % max(1, len(gen)):] + gen:
        for c in buscar(q)[:4]:
            if c["id"] not in vistos and _bajar_clip(c, mp4, jpg):
                print(f"  escena {i}: vídeo de ambiente ({q})")
                return {"clip": mp4, "clip_id": c["id"], "credito": c["credito"]}
    for f in (mp4, jpg):
        if os.path.exists(f):
            os.remove(f)
    return None
