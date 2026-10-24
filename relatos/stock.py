"""Clips de vídeo REAL de internet (Pixabay, gratis) para los CORTOS verticales.

Se usa en dos casos (ver fabricar.py):
  - prueba A/B: algunos cortos del día se hacen solo con vídeo real (MODO_IMG=real);
  - plan B: si Cloudflare no puede hacer una imagen (sin cuota o la rechaza), esa escena va con vídeo real.
Gemini elige, mirando fotogramas, el clip que mejor acompaña a cada escena; nunca se usan renders/IA/animaciones.
"""
import io, json, os, re, subprocess, time, urllib.parse, urllib.request

from PIL import Image

UA = {"User-Agent": "SinHumoTV-cortos/1.0 (https://github.com/sinhumotv/sin-humo-tv-kit; sinhumotv@users.noreply.github.com)"}
NO_REAL = re.compile(r"\bai\b|generated|3d|render|cgi|animation|animated|abstract|digital art|hologram|futuristic|"
                     r"sci-fi|motion graphic|loop|background|particles|cartoon|illustration", re.I)


def clave():
    return "".join(os.environ.get("PIXABAY_KEY", "").split())


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
        out.append({"id": h["id"], "url": buena["url"], "thumb": thumb, "tags": h.get("tags", ""),
                    "pagina": h.get("pageURL", ""), "vertical": vertical})
    out.sort(key=lambda c: not c["vertical"])  # primero los grabados en vertical
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
    b = bajar(c["url"])
    if not b:
        return False
    open(mp4, "wb").write(b)
    if movimiento(mp4) < 3.0:  # casi quieto: parece una foto
        print(f"  clip {c['id']} casi sin movimiento, descartado")
        return False
    return _fotograma_vertical(mp4, jpg)


def busquedas(titulo, escenas, tema=""):
    """Una búsqueda en inglés (y 2 alternativas) por escena, pensadas para un banco de vídeo real. Usa Gemini."""
    from gem import pedir
    lista = "\n".join(f"{k}. {e['hablado']}" for k, e in enumerate(escenas))
    q = f"""Vídeo corto vertical de redes: "{titulo}" ({tema}). Escenas (lo que dice la voz):
{lista}
Para cada escena, escribe una búsqueda corta EN INGLÉS (2-4 palabras) para encontrar en Pixabay un clip de VÍDEO REAL
(grabado con cámara, no animación) que acompañe a lo que se cuenta: un lugar, un ambiente, un objeto, una acción o gente
real de espaldas o lejos. Piensa como un montador de documentales: si la escena es imposible de grabar (un dios, un
monstruo, el futuro), busca algo real que la evoque (ruinas, tormenta, mar, fuego, laboratorio, ciudad de noche...).
Añade 2 alternativas más generales. Nada de sangre, armas apuntando ni violencia explícita.
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


def clip_para(i, escena, b, genericas, usados, dir_clips, dir_imgs, titulo, reglas=""):
    """Busca, elige y baja un clip para la escena i (1..n). Devuelve dict con clip/creditos o None."""
    from gem import pedir
    mp4, jpg = f"{dir_clips}/{i:02d}.mp4", f"{dir_imgs}/{i:02d}.jpg"
    cands, vistos = [], set(usados)
    gen = list(genericas or [])
    for q in [b.get("busqueda", "")] + list(b.get("otras") or []) + gen[(i * 3) % max(1, len(gen)):][:2]:
        if not q:
            continue
        for c in buscar(q):
            if c["id"] not in vistos:
                vistos.add(c["id"])
                cands.append(c)
        if len(cands) >= 10:
            break
    ok = []
    for c in cands[:8]:
        t = bajar(c["thumb"], 40) if c.get("thumb") else None
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
        if len(ok) == 6:
            break
    orden = []
    if ok:
        q = f"""Vídeo corto vertical: "{titulo}". Escena: «{escena['hablado']}».
Te paso {len(ok)} fotogramas de clips de vídeo candidatos (desde 0). Etiquetas: {json.dumps([c['tags'] for c in ok], ensure_ascii=False)}.
Se recortarán en VERTICAL por el centro. Elige los que mejor acompañen a la escena (vale algo que evoque el lugar, el
ambiente o la época, como en un documental). Descarta lo que no pegue nada, lo que tenga texto o logotipos, lo que
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
            return {"clip": mp4, "clip_id": ok[k]["id"], "credito": f"Vídeo de Pixabay · {ok[k]['pagina']}"}
    # último recurso: vídeo de ambiente del canal
    for q in gen[i % max(1, len(gen)):] + gen:
        for c in buscar(q)[:4]:
            if c["id"] not in usados and _bajar_clip(c, mp4, jpg):
                print(f"  escena {i}: vídeo de ambiente ({q})")
                return {"clip": mp4, "clip_id": c["id"], "credito": f"Vídeo de Pixabay · {c['pagina']}"}
    for f in (mp4, jpg):
        if os.path.exists(f):
            os.remove(f)
    return None
