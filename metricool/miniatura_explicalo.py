#!/usr/bin/env python3
"""(10-nov-2026) Miniatura pensada para el clic de los largos de Explícalo, con el mismo sistema que los otros canales
(relatos/largo_miniatura.py: texto enorme de 2-4 palabras con la clave en amarillo, contraste, viñeta y 3 versiones que
juzga Gemini). Los fotogramas salen del propio vídeo; Gemini elige los dos mejores y escribe el texto.

Uso: python3 miniatura_explicalo.py <publicacion.json> <carpeta>   -> <carpeta>/miniatura_A.jpg
Variable: GEMINI_KEY.
"""
import io, json, os, subprocess, sys, urllib.request
from PIL import Image

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(KIT, "relatos"))
P = json.load(open(sys.argv[1], encoding="utf-8"))
D = os.path.abspath(sys.argv[2])
os.makedirs(f"{D}/imgs", exist_ok=True)
mp4 = f"{D}/video.mp4"
with urllib.request.urlopen(urllib.request.Request(P["video"], headers={"User-Agent": "Explicalo"}), timeout=600) as r, \
        open(mp4, "wb") as f:
    f.write(r.read())
dur = float(subprocess.run(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{mp4}"', shell=True,
                           capture_output=True, text=True).stdout.strip() or 0)
# 12 fotogramas repartidos (sin el gancho inicial ni el cierre promocional); se recorta la franja de abajo (subtítulos)
fot = []
for k in range(12):
    t = 8 + (dur - 35) * k / 11
    r = subprocess.run(f'ffmpeg -v error -ss {t:.1f} -i "{mp4}" -frames:v 1 -f image2pipe -vcodec mjpeg -', shell=True,
                       capture_output=True)
    if not r.stdout:
        continue
    im = Image.open(io.BytesIO(r.stdout)).convert("RGB")
    im = im.crop((0, 0, im.width, int(im.height * 0.76)))
    fot.append(im)
if not fot:
    sys.exit("no se han podido sacar fotogramas del vídeo")
eleg, texto, clave = [0, min(len(fot) - 1, len(fot) // 2)], " ".join(P["titulo"].split()[:3]), ""
try:
    from gem import pedir
    minis = []
    for im in fot:
        t = im.copy(); t.thumbnail((480, 270))
        b = io.BytesIO(); t.save(b, "JPEG", quality=80); minis.append(b.getvalue())
    j, _ = pedir(f"""Eres experto en miniaturas de YouTube con CTR altísimo. Vídeo: "{P['titulo']}" (tema: {P.get('tema', '')}).
Te paso {len(minis)} fotogramas del vídeo (0 a {len(minis) - 1}). Elige los DOS que mejor funcionarían de fondo de miniatura:
imagen clara, llamativa, que se entienda en pequeño en el móvil y relacionada con el tema (evita los que son casi solo texto).
Escribe además el TEXTO de la miniatura: 2 a 4 palabras en español, MAYÚSCULAS, que despierten curiosidad y NO repitan el
título (p. ej. «NO GASTA DATOS», «EL TRUCO OCULTO», «¿CÓMO LO SABE?»), y la palabra CLAVE de ese texto (irá en amarillo).
Devuelve SOLO JSON: {{"fotogramas": [<mejor>, <segundo>], "texto": "...", "clave": "..."}}""",
                 temp=0.5, imagenes=minis, max_tokens=400)
    if isinstance(j, dict):
        f2 = [k for k in (j.get("fotogramas") or []) if isinstance(k, int) and 0 <= k < len(fot)]
        if f2:
            eleg = (f2 + [k for k in eleg if k not in f2])[:2]
        texto = str(j.get("texto") or texto)
        clave = str(j.get("clave") or "")
except BaseException as x:
    print("sin Gemini para la miniatura:", str(x)[:120])
fot[eleg[0]].save(f"{D}/imgs/01.jpg", quality=95)
fot[eleg[-1]].save(f"{D}/imgs/02.jpg", quality=95)
fot[eleg[0]].save(f"{D}/miniatura_base.jpg", quality=95)
json.dump({"titulo_youtube": P["titulo"], "miniatura": {"texto": texto, "clave": clave},
           "escenas": [{"imagen": {"tipo": "ia"}}, {"imagen": {"tipo": "real"}}]},
          open(f"{D}/historia.json", "w", encoding="utf-8"), ensure_ascii=False)
os.remove(mp4)
r = subprocess.run([sys.executable, os.path.join(KIT, "relatos", "largo_miniatura.py"), D], capture_output=True, text=True)
print(r.stdout[-600:], r.stderr[-600:])
if not os.path.exists(f"{D}/miniatura_A.jpg"):
    sys.exit("no se ha hecho la miniatura")
print("MINIATURA LISTA ·", texto)
