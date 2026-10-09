#!/usr/bin/env python3
"""Corta la voz en escenas, quita pausas, ajusta ritmo y genera tiempos.json, voz_final.wav y subtitulos.srt.

Uso: python3 audio.py <carpeta_proyecto>
Necesita en la carpeta: proyecto.json y voz.mp3
"""
import json, re, subprocess, sys, os
import numpy as np

D = sys.argv[1]
P = json.load(open(os.path.join(D, "proyecto.json"), encoding="utf-8"))
ESC = P["escenas"]
N = len(ESC)
LARGO = P.get("formato", "LARGO").upper() == "LARGO"
TMAX, TMIN = (60.0, 55.0) if LARGO else (40.0, 33.0)
SR = 48000
RESPIRO = 0.25


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


# --- 1. Cargar audio a mono 48 kHz -------------------------------------------
wav = os.path.join(D, "_voz.wav")
sh(f'ffmpeg -y -v error -i "{os.path.join(D, "voz.mp3")}" -ac 1 -ar {SR} "{wav}"')
rawf = os.path.join(D, "_voz.raw")
sh(f'ffmpeg -y -v error -i "{wav}" -f f32le -ac 1 -ar {SR} "{rawf}"')
raw = np.fromfile(rawf, dtype=np.float32)
DUR = len(raw) / SR

# --- 2. Pausas con silencedetect ----------------------------------------------
out = sh(f'ffmpeg -v info -i "{wav}" -af silencedetect=noise=-32dB:d=0.3 -f null -').stderr
ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
fin = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
pausas = []
for a, b in zip(ini, fin + [DUR] * (len(ini) - len(fin))):
    pausas.append((max(0.0, a), min(DUR, b)))
# tramos de voz entre pausas
tramos, c = [], 0.0
for a, b in pausas:
    if a - c > 0.05:
        tramos.append((c, a))
    c = b
if DUR - c > 0.05:
    tramos.append((c, DUR))
# pausas internas candidatas a corte (entre tramos)
cortes = [(tramos[i][1], tramos[i + 1][0]) for i in range(len(tramos) - 1)]
K = len(cortes)
if K < N - 1:
    sys.exit(f"Solo hay {K} pausas y hacen falta {N-1}: baja el umbral o revisa la voz")

# --- 3. Programación dinámica: N-1 cortes con velocidad uniforme ------------------
chars = [len(re.sub(r"\s+", "", e["hablado"])) for e in ESC]
vtot = sum(b - a for a, b in tramos)
media = sum(chars) / vtot


def voz_entre(i0, i1):  # segundos de voz de los tramos i0..i1 (inclusive)
    return sum(tramos[k][1] - tramos[k][0] for k in range(i0, i1 + 1))


T = len(tramos)
INF = 1e18
# dp[e][j] = coste mínimo con las escenas 0..e terminando en el tramo j
dp = [[INF] * T for _ in range(N)]
bk = [[-1] * T for _ in range(N)]
for j in range(T):
    v = voz_entre(0, j)
    dp[0][j] = (chars[0] / v / media - 1) ** 2
for e in range(1, N):
    for j in range(e, T):
        for i in range(e - 1, j):
            if dp[e - 1][i] >= INF:
                continue
            v = voz_entre(i + 1, j)
            plen = cortes[i][1] - cortes[i][0]
            c = dp[e - 1][i] + (chars[e] / v / media - 1) ** 2 - 0.15 * min(plen, 1.0)
            if c < dp[e][j]:
                dp[e][j], bk[e][j] = c, i
fin_idx = [T - 1]
for e in range(N - 1, 0, -1):
    fin_idx.append(bk[e][fin_idx[-1]])
fin_idx = fin_idx[::-1]
grupos, s = [], 0
for j in fin_idx:
    grupos.append((s, j))
    s = j + 1

# --- 4. Extraer cada escena con pausas recortadas -----------------------------
def trozo(a, b):
    return raw[int(a * SR):int(b * SR)]


def construir(g, max_pausa_int):
    i0, i1 = g
    partes = []
    a0 = max(0.0, tramos[i0][0] - 0.1)
    for k in range(i0, i1 + 1):
        a, b = tramos[k]
        if k == i0:
            a = a0
        partes.append(trozo(a, b))
        if k < i1:
            p = tramos[k + 1][0] - b
            if max_pausa_int is not None and p > 0.32:
                p = max_pausa_int
            partes.append(np.zeros(int(p * SR), np.float32))
    b = min(DUR, tramos[i1][1] + 0.2)
    partes.append(trozo(tramos[i1][1], b))
    return np.concatenate(partes)


palabras = sum(len(e["hablado"].split()) for e in ESC)
vel = palabras / vtot
atempo = 1.0
if vel < 2.9:
    atempo = min(1.15, 3.1 / vel)
max_p = None


def total(atempo, max_p):
    return sum(len(construir(g, max_p)) / SR / atempo + RESPIRO for g in grupos)


while total(atempo, max_p) > TMAX and atempo < 1.15:
    atempo = min(1.15, atempo + 0.01)
if total(atempo, max_p) > TMAX:
    max_p = 0.28
if palabras / (vtot / atempo) > 3.4:
    atempo = max(1.0, palabras / vtot / 3.4)


def aplicar_atempo(x, f):
    if abs(f - 1) < 1e-3:
        return x
    tmp_i, tmp_o = os.path.join(D, "_i.raw"), os.path.join(D, "_o.raw")
    x.astype(np.float32).tofile(tmp_i)
    sh(f'ffmpeg -y -v error -f f32le -ar {SR} -ac 1 -i "{tmp_i}" -af atempo={f:.4f} -f f32le "{tmp_o}"')
    return np.fromfile(tmp_o, dtype=np.float32)


escenas_audio = [aplicar_atempo(construir(g, max_p), atempo) for g in grupos]
# la voz arranca en el fotograma 0: sin silencio inicial en la escena 1
x = escenas_audio[0]
nz = np.argmax(np.abs(x) > 0.02)
escenas_audio[0] = x[max(0, nz - int(0.02 * SR)):]

dur = [len(x) / SR + RESPIRO for x in escenas_audio]
if sum(dur) > TMAX:  # último recurso: recortar respiros
    exceso = sum(dur) - TMAX
    dur = [d - min(RESPIRO, exceso / N) for d in dur]
if sum(dur) < TMIN:
    dur[-1] += TMIN - sum(dur)

# --- 5. Montar voz final y tiempos --------------------------------------------
total_s = sum(dur)
voz = np.zeros(int(total_s * SR) + SR // 10, np.float32)
t, tiempos = 0.0, []
for e, (x, d) in enumerate(zip(escenas_audio, dur)):
    k = int(t * SR)
    voz[k:k + len(x)] += x
    vlen = len(x) / SR
    # líneas del panel repartidas por caracteres
    lineas = ESC[e].get("panel", [])
    pesos = [max(1, len(re.sub(r"[*\s]", "", l))) for l in lineas] or [1]
    acc, li = 0, []
    for p in pesos:
        li.append(round(t + 0.15 + vlen * 0.9 * acc / sum(pesos), 3))
        acc += p
    tiempos.append({"ini": round(t, 3), "fin": round(t + d, 3), "voz_fin": round(t + vlen, 3), "lineas": li})
    t += d
total_s = round(t, 3)
voz = voz[:int(total_s * SR)]
pcm = (np.clip(voz, -1, 1) * 32767).astype(np.int16)
tmp = os.path.join(D, "_vf.raw")
pcm.tofile(tmp)
sh(f'ffmpeg -y -v error -f s16le -ar {SR} -ac 1 -i "{tmp}" "{os.path.join(D, "voz_final.wav")}"')
json.dump({"duracion": total_s, "escenas": tiempos, "atempo": round(atempo, 3)},
          open(os.path.join(D, "tiempos.json"), "w"), indent=1)

# --- 6. Subtítulos .srt ---------------------------------------------------------
def fmt(s):
    h, r = divmod(s, 3600); m, r = divmod(r, 60)
    return f"{int(h):02}:{int(m):02}:{int(r):02},{int(round((r % 1) * 1000)) % 1000:03}"


def bloques(texto):
    pal, out, cur = texto.split(), [], ""
    for w in pal:
        if len(cur) + len(w) + 1 > 42 and cur:
            out.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
        if cur.endswith((".", "?", "!", ":")) and len(cur) > 20:
            out.append(cur); cur = ""
    if cur:
        out.append(cur)
    return out


srt, n = [], 1
for e, tm in enumerate(tiempos):
    txt = (ESC[e].get("subtitulo") or ESC[e]["hablado"].replace("sin humo te uve", "sin humo TV")).replace("*", "")
    bl = bloques(txt)
    L = sum(len(b) for b in bl)
    vt = tm["voz_fin"] - tm["ini"]
    acc = 0
    for b in bl:
        a = tm["ini"] + vt * acc / L
        acc += len(b)
        z = tm["ini"] + vt * acc / L
        srt.append(f"{n}\n{fmt(a)} --> {fmt(z)}\n{b}\n")
        n += 1
open(os.path.join(D, "subtitulos.srt"), "w", encoding="utf-8").write("\n".join(srt))

for f in ("_voz.wav", "_voz.raw", "_i.raw", "_o.raw", "_vf.raw"):
    try:
        os.remove(os.path.join(D, f))
    except OSError:
        pass
print(f"Duración {total_s:.2f}s · atempo {atempo:.3f} · {palabras / (vtot / atempo):.2f} pal/s")
for e, tm in enumerate(tiempos):
    v = chars[e] / (tm["voz_fin"] - tm["ini"])
    print(f"  E{e+1}: {tm['ini']:6.2f}-{tm['fin']:6.2f}  {v:5.1f} car/s  «{ESC[e]['hablado'][:38]}»")
