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
    json.dump(P, open(f"{D}/proyecto.json", "w"), ensure_ascii=False, indent=1)
    open(f"{D}/voz.txt", "w").write("\n\n".join(e["hablado"] for e in ESC))
    print(sh(f'python3 "{AQUI}/voz_relato.py" "{D}" --tono relato --voz {VOZ}').strip().splitlines()[-1])
    print(sh(f'python3 "{KIT}/audio.py" "{D}"').splitlines()[0])


def imagenes():
    A = os.environ.get("CF_ACCOUNT") or open(os.path.expanduser("~/.cf_account")).read().strip()
    T = os.environ.get("CF_TOKEN") or open(os.path.expanduser("~/.cf_token")).read().strip()
    os.makedirs(f"{D}/imgs", exist_ok=True)
    fallos = []
    for i, e in enumerate(ESC, 1):
        out = f"{D}/imgs/{i:02d}.jpg"
        if os.path.exists(out):
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
            print(f"escena {i} intento {intento + 1}: {d.get('errors')}")
            time.sleep(2)
        if not ok:
            fallos.append(i)
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
    print(sh(f'python3 "{AQUI}/montaje.py" "{D}"').strip().splitlines()[-1])
    portada = f"{D}/portada.jpg"
    sh(f'ffmpeg -v error -y -ss 0.8 -i "{D}/video_final.mp4" -frames:v 1 -q:v 3 "{portada}"')


if PASO in ("todo", "voz"):
    voz()
if PASO in ("todo", "imagenes"):
    imagenes()
if PASO in ("todo", "montaje"):
    montaje()
