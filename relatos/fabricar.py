#!/usr/bin/env python3
"""Fabrica un relato de mitología completo a partir de <carpeta>/historia.json.

Uso: python3 fabricar.py <carpeta> [voz|imagenes|montaje]   (sin paso: hace los tres)

historia.json:
{
 "titulo": "Orfeo y Eurídice",
 "escenas": [
   {"hablado": "texto exacto que lee la voz",
    "subtitulo": "mismas palabras, con 1-2 *claves* entre asteriscos",
    "prompt": "descripción EN INGLÉS de la imagen (personajes descritos siempre igual)",
    "efecto": "brasas|polvo|niebla|nada",
    "fuego": false}
 ], ...campos de publicación (ver publicar.py)
}
Claves (fuera del repositorio): ~/.gemini_key, ~/.cf_account, ~/.cf_token.
"""
import base64, json, os, subprocess, sys, time

AQUI = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(AQUI)
D = os.path.abspath(sys.argv[1])
PASO = sys.argv[2] if len(sys.argv) > 2 else "todo"
H = json.load(open(f"{D}/historia.json", encoding="utf-8"))
ESC = H["escenas"]
ESTILO = H.get("estilo_imagen") or ("Cinematic photorealistic film still, ancient Greece, dramatic lighting, shallow depth of field, "
          "ultra detailed, 35mm film grain. ")
SEGURO = " Tasteful, no blood, no gore, no nudity."
VOZ = H.get("voz", "Algenib")


def sh(c):
    r = subprocess.run(c, shell=True, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-1500:], r.stderr[-1500:])
        sys.exit(f"FALLO: {c}")
    return r.stdout


def voz():
    P = {"formato": "CORTO", "duracion_max": 45, "duracion_min": 26, "fecha": "", "fuentes": "",
         "titulo_noticia": H["titulo"], "tono": "grave", "mencion": 0, "zum": [],
         "efectos": [e.get("efecto", "polvo") for e in ESC],
         "fuego": [i for i, e in enumerate(ESC) if e.get("fuego")],
         "escenas": [{"titulo": "", "hablado": e["hablado"], "subtitulo": e["subtitulo"]} for e in ESC]}
    if H.get("color"):
        P["color"] = H["color"]
    json.dump(P, open(f"{D}/proyecto.json", "w"), ensure_ascii=False, indent=1)
    open(f"{D}/voz.txt", "w").write("\n\n".join(e["hablado"] for e in ESC))
    print(sh(f'python3 "{AQUI}/voz_relato.py" "{D}" --tono relato --voz {VOZ}').strip().splitlines()[-1])
    print(sh(f'python3 "{KIT}/audio.py" "{D}"').splitlines()[0])


def reales(indices):
    """Pone vídeo REAL de internet (Pixabay) en las escenas indicadas (1..n). Devuelve las que no se consiguieron."""
    sys.path.insert(0, AQUI)
    import stock
    cfg = {}
    if os.environ.get("CANAL_JSON") and os.path.exists(os.environ["CANAL_JSON"]):
        cfg = json.load(open(os.environ["CANAL_JSON"], encoding="utf-8"))
    fuentes = cfg.get("fuentes") or ["pixabay"]
    if not stock.hay_fuentes(fuentes):
        print("sin fuentes de vídeo real disponibles")
        return list(indices)
    os.makedirs(f"{D}/clips", exist_ok=True)
    gen = (cfg.get("largo") or {}).get("video_generico") or []
    if "busquedas" not in H:
        H["busquedas"] = stock.busquedas(H["titulo"], ESC, cfg.get("tema", ""), cfg.get("visual", ""))
    P = json.load(open(f"{D}/proyecto.json", encoding="utf-8"))
    clips = P.get("clips") or {}
    cred = H.setdefault("creditos_video", {})
    usados = {c.get("clip_id") for c in H.get("clips_info", {}).values()}
    if os.environ.get("CLIPS_USADOS") and os.path.exists(os.environ["CLIPS_USADOS"]):
        usados |= {x.strip() for x in open(os.environ["CLIPS_USADOS"], encoding="utf-8").read().splitlines() if x.strip()}
    info = H.setdefault("clips_info", {})
    sin = []
    vistos = {str(x) for x in usados}
    # 1) candidatos de todas las escenas, 2) UNA consulta a Gemini para elegir, 3) descargas
    lote = []
    for i in indices:
        c = stock.preparar(i, H["busquedas"][i - 1], gen, vistos, fuentes)
        vistos |= {x["id"] for x in c}
        lote.append((i, ESC[i - 1]["hablado"], c))
    orden = stock.elegir_lote(H["titulo"], lote, (cfg.get("largo") or {}).get("reglas_reales", ""), cfg.get("visual", ""))
    sin_aprobar = [i for i, _, c in lote if not orden.get(i)]
    if sin_aprobar and gen:
        lote2 = []
        for n, i in enumerate(sin_aprobar):
            b2 = {"busqueda": gen[(i * 2) % len(gen)], "otras": [gen[(i * 2 + 1) % len(gen)], gen[(i * 2 + 5) % len(gen)]]}
            c2 = stock.preparar(i, b2, [], vistos, fuentes)
            vistos |= {x["id"] for x in c2}
            lote2.append((i, ESC[i - 1]["hablado"], c2))
        orden2 = stock.elegir_lote(H["titulo"], lote2, (cfg.get("largo") or {}).get("reglas_reales", ""), cfg.get("visual", ""))
        lote = [x for x in lote if x[0] not in sin_aprobar] + [x for x in lote2]
        orden.update(orden2)
        lote.sort(key=lambda x: x[0])
    bajados = {str(x) for x in usados}
    for i, _, c in lote:
        r = stock.descargar(i, [x for x in c], orden.get(i, []), [], bajados, f"{D}/clips", f"{D}/imgs", fuentes)
        if r:
            bajados.add(r["clip_id"])
        if not r:
            sin.append(i)
            continue
        usados.add(r["clip_id"])
        info[str(i)] = {"clip_id": r["clip_id"]}
        cred[str(i)] = r["credito"]
        if r.get("atribucion"):
            H.setdefault("creditos_atribucion", {})[str(i)] = r["credito"].rsplit(" · ", 1)[0]
        clips[str(i - 1)] = r["clip"]
        P["efectos"][i - 1] = "nada"
        print(f"escena {i}: vídeo real · {r['clip_id']}")
    P["clips"] = clips
    json.dump(P, open(f"{D}/proyecto.json", "w"), ensure_ascii=False, indent=1)
    json.dump(H, open(f"{D}/historia.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return sin


def imagenes():
    os.makedirs(f"{D}/imgs", exist_ok=True)
    modo = os.environ.get("MODO_IMG", "ia")
    pendientes = [i for i in range(1, len(ESC) + 1) if not os.path.exists(f"{D}/imgs/{i:02d}.jpg")]
    con_video = []
    if modo == "real" and pendientes:
        # PRUEBA A/B: este corto se hace solo con vídeo real; lo que no se encuentre, con IA
        sin = reales(pendientes)
        con_video = [i for i in pendientes if i not in sin]
        if len(con_video) < len(pendientes) / 2:
            print("vídeo real insuficiente: este corto se hace con IA")
            modo = "ia"
    A = os.environ.get("CF_ACCOUNT") or open(os.path.expanduser("~/.cf_account")).read().strip()
    T = os.environ.get("CF_TOKEN") or open(os.path.expanduser("~/.cf_token")).read().strip()
    fallos = []
    sin_cuota = False
    for i, e in enumerate(ESC, 1):
        out = f"{D}/imgs/{i:02d}.jpg"
        if os.path.exists(out):
            continue
        if sin_cuota:   # sin cuota: no se sigue llamando a Cloudflare
            fallos.append(i)
            continue
        ok = False
        for intento, (extra, (ww, hh)) in enumerate([("", (1024, 1792)), (SEGURO, (1024, 1792)), (SEGURO, (768, 1344))]):
            r = subprocess.run(["curl", "-sS", "-m", "150", "-H", f"Authorization: Bearer {T}",
                                f"https://api.cloudflare.com/client/v4/accounts/{A}/ai/run/@cf/black-forest-labs/flux-2-klein-4b",
                                "-F", "prompt=" + ESTILO + e["prompt"] + extra, "-F", f"width={ww}", "-F", f"height={hh}"],
                               capture_output=True, text=True)
            try:
                d = json.loads(r.stdout)
            except Exception:
                d = {"errors": [r.stdout[:200] or r.stderr[:200]]}
            if d.get("success"):
                open(out, "wb").write(base64.b64decode(d["result"]["image"]))
                ok = True
                break
            print(f"escena {i} intento {intento + 1}: {str(d.get('errors'))[:160]}")
            if "4006" in str(d.get("errors")) or "neurons" in str(d.get("errors")):
                sin_cuota = True
                break
            time.sleep(2)
        if not ok:
            fallos.append(i)
    if fallos:
        # PLAN B: Cloudflare sin cuota o imagen rechazada -> vídeo real de internet para esas escenas
        print("Cloudflare no ha podido con las escenas", fallos, "-> vídeo real")
        sin = reales(fallos)
        con_video += [i for i in fallos if i not in sin]
        fallos = sin
    n_vid = len([i for i in range(1, len(ESC) + 1) if os.path.exists(f"{D}/clips/{i:02d}.mp4")])
    open(f"{D}/modo_imagenes.txt", "w").write("real" if n_vid == len(ESC) else "mixto" if n_vid else "ia")
    if fallos and os.environ.get("AUTO"):
        # modo automático: reutiliza la imagen de la escena vecina para no perder el vídeo
        for i in fallos:
            vec = [k for k in range(1, len(ESC) + 1) if k not in fallos]
            if not vec:
                sys.exit("ninguna imagen generada")
            k = min(vec, key=lambda k: abs(k - i))
            import shutil
            shutil.copy(f"{D}/imgs/{k:02d}.jpg", f"{D}/imgs/{i:02d}.jpg")
            print(f"escena {i}: sin imagen, reutilizo la {k}")
        fallos = []
    if fallos:
        print("SIN IMAGEN en escenas:", fallos, "-> reescribe su 'prompt' (más suave) y repite: fabricar.py <carpeta> imagenes")
        sys.exit(2)
    # hoja de contacto para revisar
    from PIL import Image
    n = len(ESC)
    ims = [Image.open(f"{D}/imgs/{i:02d}.jpg").resize((192, 336)) for i in range(1, n + 1)]
    g = Image.new("RGB", (192 * min(n, 5), 336 * ((n + 4) // 5)))
    for k, im in enumerate(ims):
        g.paste(im, ((k % 5) * 192, (k // 5) * 336))
    g.save(f"{D}/hoja.jpg", quality=80)
    print("imágenes OK ·", n, "· hoja:", f"{D}/hoja.jpg")


def montaje():
    out = sh(f'python3 "{AQUI}/montaje.py" "{D}"')
    print(out.strip().splitlines()[-1])
    # CONTROL: los subtítulos tienen que ir pegados a la voz. Si el reconocimiento de voz no casa con el guion
    # (la voz ha dicho otra cosa o sobra audio), el vídeo NO se publica (la repesca lo rehace).
    import re as _re
    m = _re.search(r"karaoke: (\d+)/(\d+)", out)
    oidas = _re.search(r"\((\d+) oídas\)", out)
    if oidas and m and int(oidas.group(1)) > 1.25 * int(m.group(2)):
        sys.exit(f"FALLO: la voz dice bastante más que el guion ({oidas.group(1)} palabras oídas, {m.group(2)} en el guion)")
    if not m or int(m.group(1)) < 0.75 * int(m.group(2)):
        sys.exit("FALLO: los subtítulos no casan con la voz (" + (m.group(0) if m else "sin reconocimiento") + ")")
    portada = f"{D}/portada.jpg"
    sh(f'ffmpeg -v error -y -ss 0.8 -i "{D}/video_final.mp4" -frames:v 1 -q:v 3 "{portada}"')


if PASO in ("todo", "voz"):
    voz()
if PASO in ("todo", "imagenes"):
    imagenes()
if PASO in ("todo", "montaje"):
    montaje()
