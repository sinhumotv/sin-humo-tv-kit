#!/usr/bin/env python3
"""Revisión final en un paso: formato, duración, audio, metadatos, fotogramas negros y hoja de revisión.
Uso: python3 comprobar.py <proyecto>   → imprime OK/AVISO y crea <proyecto>/revision.png (fotograma 0 + uno por escena + último)."""
import json, os, subprocess, sys

D = sys.argv[1]
V = os.path.join(D, "video_final.mp4")
P = json.load(open(os.path.join(D, "proyecto.json"), encoding="utf-8"))
T = json.load(open(os.path.join(D, "tiempos.json")))
LARGO = P.get("formato", "LARGO").upper() == "LARGO"


def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True)


r = json.loads(sh(f'ffprobe -v error -show_entries format=duration,size:format_tags=title,artist:stream=codec_type,width,height,r_frame_rate,sample_rate -of json "{V}"').stdout)
fmt, st = r["format"], r["streams"]
vid = next(s for s in st if s["codec_type"] == "video")
aud = [s for s in st if s["codec_type"] == "audio"]
dur = float(fmt["duration"])
avisos = []
if (vid["width"], vid["height"]) != (1080, 1920): avisos.append(f"resolución {vid['width']}x{vid['height']}")
if vid["r_frame_rate"] != "30/1": avisos.append(f"fps {vid['r_frame_rate']}")
if not aud: avisos.append("sin audio")
lo, hi = (55, 60.05) if LARGO else (33, 40.05)
if not lo <= dur <= hi: avisos.append(f"duración {dur:.1f}s fuera de {lo}-{hi:.0f}s")
if fmt.get("tags", {}).get("artist") != "sin humo TV": avisos.append("faltan metadatos del canal")
mb = int(fmt["size"]) / 1e6
negros = sh(f'ffmpeg -v info -i "{V}" -vf blackdetect=d=0.1 -an -f null - 2>&1 | grep black_start').stdout.strip()
if negros: avisos.append("fotogramas negros: " + negros[:120])

ts = [0.0] + [round((e["ini"] + e["voz_fin"]) / 2, 2) for e in T["escenas"]] + [round(dur - 0.1, 2)]
tmp = os.path.join(D, "_rev")
os.makedirs(tmp, exist_ok=True)
for i, t in enumerate(ts):
    sh(f'ffmpeg -y -v error -ss {t} -i "{V}" -frames:v 1 -vf scale=240:-1 "{tmp}/r{i:02d}.png"')
cols = 6 if len(ts) > 10 else 4
filas = -(-len(ts) // cols)
sh(f'ffmpeg -y -v error -i "{tmp}/r%02d.png" -vf "tile={cols}x{filas}" -frames:v 1 "{os.path.join(D, "revision.png")}"')
sh(f'rm -rf "{tmp}"')
print(f"{'OK' if not avisos else 'AVISO'} · {dur:.1f}s · {mb:.1f} MB · {vid['width']}x{vid['height']} · audio {'sí' if aud else 'no'}")
for a in avisos:
    print("  -", a)
print(f"Hoja de revisión: {os.path.join(D, 'revision.png')} (fotograma 0, una por escena y el último). Mírala con Read.")
