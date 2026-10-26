#!/usr/bin/env python3
"""CONTROL antes de publicar un largo: busca tramos en los que la imagen se queda QUIETA (foto o fotograma congelado)
y planos REPETIDOS (el mismo plano que ya salió antes en el vídeo).
Uso: python3 control_movimiento.py <video.mp4> [tiempos.json]
Imprime los tramos y, si hay tiempos.json, las escenas afectadas. Sale con 4 si hay algún tramo quieto de 2,4 s o más."""
import json, subprocess, sys
import numpy as np

v = sys.argv[1]
raw = subprocess.run(f'ffmpeg -v error -i "{v}" -vf fps=5,scale=192:108,format=gray -f rawvideo -', shell=True,
                     capture_output=True).stdout
f = np.frombuffer(raw, np.uint8).reshape(-1, 108, 192).astype(np.float32)[:, :60]   # mitad de arriba: sin subtítulos
d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
dur = len(f) / 5
tramos, s = [], None
for i, q in enumerate(list(d < 0.25) + [False]):
    if q and s is None:
        s = i
    if not q and s is not None:
        if i - s >= 12 and s / 5 < dur - 2.5:   # (el fundido final no cuenta)
            tramos.append((s / 5, (i - s) / 5))
        s = None
# PLANOS REPETIDOS: el mismo plano que ya salió antes en el vídeo (regla del usuario: nunca repetir escena)
g = f[::2]   # 2,5 por segundo
peq = g.reshape(len(g), 6, 10, 192)[:, :, :, :].mean(axis=2)   # 6 x 192
peq = peq.reshape(len(g), 6, 24, 8).mean(axis=3)              # 6 x 24
bits = (peq[:, :, 1:] > peq[:, :, :-1]).reshape(len(g), -1)
plano = g.std(axis=(1, 2)) > 12                                 # sin fotogramas casi lisos (negro, fundidos)
rep, s, ult = [], None, -99
for i in range(len(g)):
    hit = False
    if plano[i]:
        lim = max(0, i - 38)   # más de 15 s antes (dentro del mismo plano es normal que se parezca)
        if lim:
            dist = (bits[:lim] != bits[i]).sum(axis=1)
            hit = bool(((dist <= 6) & plano[:lim]).any())
    if hit and s is None:
        s = i
    if not hit and s is not None:
        if i - s >= 5:   # 2 s o más
            rep.append((s / 2.5, (i - s) / 2.5))
        s = None
for a, b in tramos:
    print(f"QUIETO {int(a // 60)}:{a % 60:04.1f} durante {b:.1f} s")
for a, b in rep:
    print(f"REPETIDO {int(a // 60)}:{a % 60:04.1f} durante {b:.1f} s")
tramos += rep
esc = set()
if len(sys.argv) > 2:
    T = json.load(open(sys.argv[2]))["escenas"]
    for a, b in tramos:
        for k, e in enumerate(T, 1):
            if e["ini"] < a + b and e["fin"] > a:
                esc.add(k)
print("ESCENAS_QUIETAS", json.dumps(sorted(esc)))
sys.exit(4 if tramos else 0)
