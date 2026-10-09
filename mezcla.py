#!/usr/bin/env python3
"""Música por código, efectos, mezcla a -14 LUFS y MP4 final con metadatos.

Uso: python3 mezcla.py <proyecto> [solo_audio]
Necesita: proyecto.json, tiempos.json, voz_final.wav y, salvo solo_audio, _bloques.txt (de render.js video).
proyecto.json puede incluir "tono": "tensa" | "ligera" | "grave" y "zum": [segundos absolutos]."""
import json, os, re, subprocess, sys
import numpy as np

D = sys.argv[1]
SOLO_AUDIO = len(sys.argv) > 2
P = json.load(open(os.path.join(D, "proyecto.json"), encoding="utf-8"))
T = json.load(open(os.path.join(D, "tiempos.json")))
SR, DUR = 48000, T["duracion"]
tono = P.get("tono", "tensa")
rng = np.random.default_rng(11)


def sh(c):
    r = subprocess.run(c, shell=True, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-1500:])
    return r


def guarda(x, nombre):
    x = np.clip(x, -1, 1).astype(np.float32)
    p = os.path.join(D, nombre + ".raw")
    x.tofile(p)
    sh(f'ffmpeg -y -v error -f f32le -ar {SR} -ac 1 -i "{p}" "{os.path.join(D, nombre + ".wav")}"')
    os.remove(p)


# ---------- música ----------
bpm = {"tensa": 104, "ligera": 112, "grave": 84}.get(tono, 104)
beat = 60 / bpm
n = int((DUR + 2) * SR)
t = np.arange(n) / SR
acordes = {  # Hz de las notas de cada acorde (4 compases)
    "tensa": [[110, 130.8, 164.8], [87.3, 110, 130.8], [98, 123.5, 146.8], [82.4, 103.8, 123.5]],
    "ligera": [[130.8, 164.8, 196], [110, 130.8, 164.8], [87.3, 110, 130.8], [98, 123.5, 146.8]],
    "grave": [[73.4, 87.3, 110], [65.4, 77.8, 98], [58.3, 73.4, 87.3], [55, 69.3, 82.4]],
}[tono]
compas = beat * 4
pad = np.zeros(n)
for i in range(int(np.ceil((DUR + 2) / compas))):
    a, b = int(i * compas * SR), min(n, int((i + 1) * compas * SR))
    seg = t[a:b] - t[a]
    env = np.minimum(1, seg / .4) * np.minimum(1, (compas - seg) / .4)
    for f in acordes[i % 4]:
        pad[a:b] += env * (np.sin(2 * np.pi * f * t[a:b]) + .3 * np.sin(2 * np.pi * 2 * f * t[a:b] + .5)) / 3
# pulso: bombo en cada pulso, charles en contratiempo
pulso = np.zeros(n)
kl = int(.25 * SR); kt = np.arange(kl) / SR
bombo = np.sin(2 * np.pi * (55 + 90 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 12)
hl = int(.05 * SR); charles = rng.normal(0, 1, hl) * np.exp(-np.arange(hl) / SR * 90) * .25
k = 0
while k * beat < DUR + 2:
    a = int(k * beat * SR)
    if a + kl < n: pulso[a:a + kl] += bombo * (.9 if tono != "grave" else .6)
    b = int((k + .5) * beat * SR)
    if b + hl < n and tono != "grave": pulso[b:b + hl] += charles
    k += 1
mus = pad * .5 + pulso * .6
# bucle: el final se funde con el principio
L2 = int(2 * SR)
m = mus[:int(DUR * SR)].copy()
fade = np.linspace(0, 1, L2)
m[:L2] = m[:L2] * fade + mus[int(DUR * SR):int(DUR * SR) + L2] * (1 - fade)
m /= np.max(np.abs(m)) + 1e-9
guarda(m * .8, "musica")

# ---------- efectos ----------
sfx = np.zeros(int(DUR * SR) + SR)


def pon(x, ts, g=1):
    a = int(ts * SR)
    if a < 0 or a + len(x) > len(sfx): return
    sfx[a:a + len(x)] += x * g


wl = int(.45 * SR); wt = np.arange(wl) / SR
whoosh = np.convolve(rng.normal(0, 1, wl), np.ones(40) / 40, 'same') * np.sin(np.pi * wt / .45) ** 2
whoosh *= np.sin(2 * np.pi * (300 + 900 * wt / .45) * wt) * .5 + .5
zl = int(.6 * SR); zt = np.arange(zl) / SR
zum = np.sin(2 * np.pi * (200 + 500 * zt) * zt) * np.sin(np.pi * zt / .6) * .5
pl = int(.08 * SR); pt = np.arange(pl) / SR
pop = np.sin(2 * np.pi * 900 * pt * np.exp(-pt * 20)) * np.exp(-pt * 45)
# impacto inicial (grave y corto) sincronizado con el golpe de zoom del fotograma 0
il = int(.5 * SR); it = np.arange(il) / SR
impacto = np.sin(2 * np.pi * (48 + 70 * np.exp(-it * 18)) * it) * np.exp(-it * 7) + rng.normal(0, 1, il) * np.exp(-it * 60) * .25
if P.get("golpe_inicial", True): pon(impacto, 0, .9)
for e in T["escenas"][1:]:
    pon(whoosh, e["ini"] - .3, .9)           # en el respiro entre escenas, no encima de palabras
for z in P.get("zum", []):
    pon(zum, z, .8)
pon(pop, T["escenas"][-1]["voz_fin"] + .05)  # pop final
sfx /= np.max(np.abs(sfx)) + 1e-9
guarda(sfx[:int(DUR * SR)], "efectos")

# ---------- mezcla ----------
def mezcla(extra_db=0, lim2=False):
    post = f",volume={extra_db}dB,alimiter=limit=0.8" if lim2 else ""
    sh(f'ffmpeg -y -v error -i "{D}/voz_final.wav" -i "{D}/musica.wav" -i "{D}/efectos.wav" -filter_complex '
       f'"[0:a]aresample=48000,asplit=2[v][sc];[1:a]volume=0.05[m];[m][sc]sidechaincompress=threshold=0.015:ratio=6:attack=20:release=300[md];'
       f'[2:a]volume=0.12[s];[v][md][s]amix=inputs=3:normalize=0:duration=first,volume=4,alimiter=limit=0.6,'
       f'loudnorm=I=-14:TP=-1.5:LRA=11:linear=true{post}[a]" -map "[a]" -ar 48000 -ac 2 "{D}/mezcla.wav"')
    r = sh(f'ffmpeg -v info -i "{D}/mezcla.wav" -af ebur128=peak=true -f null -')
    i = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])
    pk = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)[-1])
    return i, pk


I, PK = mezcla()
if I < -14.6:
    I, PK = mezcla(min(3, -14 - I), True)
print(f"Sonoridad: {I} LUFS · pico {PK} dBTP")

if SOLO_AUDIO:
    sys.exit()
# ---------- vídeo final ----------
tit = f'{P.get("titulo_noticia", "")} | sin humo TV'.replace('"', "'")
salida = os.path.join(D, "video_final.mp4")
sh(f'cd "{D}" && ffmpeg -y -v error -f concat -safe 0 -i _bloques.txt -i mezcla.wav -map 0:v -map 1:a '
   f'-c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest '
   f'-metadata title="{tit}" -metadata artist="sin humo TV" -metadata copyright="© sin humo TV" '
   f'-metadata comment="Vídeo original de sin humo TV" "{salida}"')
mb = os.path.getsize(salida) / 1e6
if mb > 30:
    sh(f'ffmpeg -y -v error -i "{salida}" -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -c:a copy -movflags +faststart '
       f'-map_metadata 0 "{os.path.join(D, "video_movil.mp4")}"')
print(f"MP4: {mb:.1f} MB")
