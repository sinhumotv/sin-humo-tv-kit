#!/usr/bin/env python3
"""ÚLTIMO RECURSO de los largos (14-nov-2026): cuando a una escena no le quedan clips reales sin repetir, o su clip se queda
quieto o repite un plano anterior, en vez de tirar el largo entero se hace una imagen de IA (Cloudflare) de esa escena y se
anima con movimiento de cámara (acercamiento + desplazamiento, nunca quieta). Así el vídeo sale y sigue todo en movimiento.

Uso: python3 rescate_ia.py <carpeta> <escena (desde 1)> <segundos>
Deja <carpeta>/clips/NN_full.mp4 (y NN.mp4) y marca la escena en historia.json. Sale con 3 si no hay cuota de imágenes."""
import base64, io, json, os, subprocess, sys

from PIL import Image, ImageEnhance

P, N, SEG = os.path.abspath(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
H = json.load(open(f"{P}/historia.json", encoding="utf-8"))
E = H["escenas"][N - 1]
im = E["imagen"]
W, HH, FPS = 1920, 1080, 30


def cloudflare(prompt, out):
    A, T = os.environ.get("CF_ACCOUNT", "").strip(), os.environ.get("CF_TOKEN", "").strip()
    if not A or not T:
        return "fallo"
    for extra, (ww, hh) in (("", (1536, 864)), (" Tasteful, no blood, no gore, no nudity.", (1344, 768))):
        r = subprocess.run(["curl", "-sS", "-m", "150", "-H", f"Authorization: Bearer {T}",
                            f"https://api.cloudflare.com/client/v4/accounts/{A}/ai/run/@cf/black-forest-labs/flux-2-klein-4b",
                            "-F", "prompt=" + prompt + extra, "-F", f"width={ww}", "-F", f"height={hh}"],
                           capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
        except Exception:
            d = {"errors": [r.stdout[:200] or r.stderr[:200]]}
        if d.get("success"):
            Image.open(io.BytesIO(base64.b64decode(d["result"]["image"]))).convert("RGB").save(out, quality=94)
            return "ok"
        if any(x in json.dumps(d.get("errors")).lower() for x in ("4006", "allocation", "neurons", "quota", "429")):
            return "cuota"
    return "fallo"


desc = im.get("prompt") or im.get("descripcion") or im.get("busqueda") or ""
if not desc or not any(c.isascii() and c.isalpha() for c in desc[:20]):
    desc = f"Cinematic scene illustrating: {E.get('hablado', '')[:300]}"
prompt = (H.get("estilo_imagen", "") + " " + desc.rstrip(". ") +
          ". Cinematic, photorealistic, rich detail, well lit, vivid colors, wide 16:9 composition. No text, no letters.").strip()
os.makedirs(f"{P}/clips", exist_ok=True)
os.makedirs(f"{P}/imgs", exist_ok=True)
foto = f"{P}/imgs/{N:02d}_ia.jpg"   # (imgs/ se guarda en la rama del proyecto; clips/ no)
if not os.path.exists(foto):
    r = cloudflare(prompt, foto)
    if r != "ok":
        print(f"escena {N}: sin imagen de IA ({r})")
        sys.exit(3 if r == "cuota" else 1)
# imagen grande para que el movimiento sea suave; un poco más de contraste y color
f = Image.open(foto).convert("RGB")
s = max(W * 1.35 / f.width, HH * 1.35 / f.height)
f = f.resize((round(f.width * s), round(f.height * s)), Image.LANCZOS)
f = ImageEnhance.Color(ImageEnhance.Contrast(f).enhance(1.08)).enhance(1.12)
big = f"{P}/clips/{N:02d}_ia_big.jpg"
f.save(big, quality=94)
# movimiento claro (nunca «quieto» para control_movimiento.py): acercamiento del 1,0 al 1,3 con desplazamiento lateral,
# en sentido distinto según la escena
fr = max(2, int(round(SEG * FPS)))
z = f"1+0.30*on/{fr}"
dx = ["(iw-iw/zoom)*on/{fr}", "(iw-iw/zoom)*(1-on/{fr})", "(iw-iw/zoom)/2", "(iw-iw/zoom)*on/{fr}"][N % 4].format(fr=fr)
dy = ["(ih-ih/zoom)/2", "(ih-ih/zoom)/3", "(ih-ih/zoom)*on/{fr}", "(ih-ih/zoom)*(1-on/{fr})"][N % 4].format(fr=fr)
out = f"{P}/clips/{N:02d}_full.mp4"
cmd = (f'ffmpeg -y -v error -loop 1 -i "{big}" -vf "zoompan=z=\'{z}\':x=\'{dx}\':y=\'{dy}\':d={fr}:s={W}x{HH}:fps={FPS},'
       f'format=yuv420p" -frames:v {fr} -c:v libx264 -preset veryfast -crf 19 -movflags +faststart "{out}"')
rc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
if rc.returncode or not os.path.exists(out):
    print(f"escena {N}: no se pudo animar la imagen: {rc.stderr[-300:]}")
    sys.exit(1)
subprocess.run(["cp", out, f"{P}/clips/{N:02d}.mp4"])
open(f"{P}/clips/{N:02d}.mp4.ok", "w").close()
Image.open(foto).convert("RGB").resize((W, HH)).save(f"{P}/imgs/{N:02d}.jpg", quality=90)
im.pop("extra", None)
im.update({"tipo": "video", "clip": "ia", "clip_id": f"ia-{N}", "fuente": "", "rescate_ia": True, "rescate_seg": round(SEG, 2)})
json.dump(H, open(f"{P}/historia.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"escena {N}: imagen de IA con movimiento de cámara ({SEG:.1f} s) en lugar de un clip real")
