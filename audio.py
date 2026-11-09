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
FORMATO = P.get("formato", "LARGO").upper()
LARGO = FORMATO == "LARGO"
YOUTUBE = FORMATO == "YOUTUBE"   # vídeo largo horizontal
TMAX, TMIN = (900.0, 0.0) if YOUTUBE else (60.0, 55.0) if LARGO else (40.0, 33.0)
# Duración libre (desde v22): "duracion_max" y "duracion_min" en proyecto.json mandan sobre el formato
if "duracion_max" in P:
    TMAX, TMIN = float(P["duracion_max"]), float(P.get("duracion_min", 0))
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
# En los vídeos largos la voz a veces encadena párrafos con pausas cortas: se detectan también pausas de 0,15 s
out = sh(f'ffmpeg -v info -i "{wav}" -af silencedetect=noise=-32dB:d={0.15 if YOUTUBE else 0.3} -f null -').stderr
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


_acum = [0.0]
for _a, _b in tramos:
    _acum.append(_acum[-1] + _b - _a)


def voz_entre(i0, i1):  # segundos de voz de los tramos i0..i1 (inclusive), con sumas acumuladas
    return _acum[i1 + 1] - _acum[i0]


T = len(tramos)
INF = 1e18
VENTANA = T if N <= 12 else 60   # en los shorts, búsqueda completa (igual que antes)
# dp[e][j] = coste mínimo con las escenas 0..e terminando en el tramo j
dp = [[INF] * T for _ in range(N)]
bk = [[-1] * T for _ in range(N)]
for j in range(T):
    v = voz_entre(0, j)
    dp[0][j] = (chars[0] / v / media - 1) ** 2
for e in range(1, N):
    for j in range(e, T):
        for i in range(max(e - 1, j - VENTANA), j):   # una escena no abarca más de VENTANA tramos
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
# v26: cortes forzados. Si existe <carpeta>/inicios.json (lista con el segundo de voz.mp3 en que empieza cada
# escena, p. ej. sacado de una transcripción con marcas de tiempo), cada escena empieza en el tramo de voz más cercano.
_fz = os.path.join(D, "inicios.json")
# (9-nov-2026) si los cortes forzados no encajan (p. ej. menos pausas que escenas en un corto), se usa el reparto normal en vez de fallar
_tramos0, _grupos0 = list(tramos), list(grupos)
try:
    if os.path.exists(_fz):
        _ini = json.load(open(_fz))
        if len(_ini) == N:
            # si un inicio cae dentro de un tramo de voz continuo, se parte el tramo en el punto más silencioso cercano
            def _hueco(t):
                fr = int(0.02 * SR); best, bt = 1e9, t
                for x in np.arange(t - 0.3, t + 0.06, 0.01):
                    i = int(x * SR)
                    if i < fr or i + fr > len(raw): continue
                    r = float(np.sqrt(np.mean(raw[i - fr // 2:i + fr // 2] ** 2)))
                    if r < best: best, bt = r, x
                return bt
            for e in range(1, N):
                t = _hueco(_ini[e])
                for k, (a, b) in enumerate(tramos):
                    if a + 0.35 < t < b - 0.15:
                        tramos[k:k + 1] = [(a, t - 0.2), (t + 0.1, b)]
                        break
                else:
                    continue
                _ini[e] = t + 0.1
            T = len(tramos)
            _st = [0]
            for e in range(1, N):
                cand = [k for k in range(_st[-1] + 1, T - (N - 1 - e))]
                _st.append(min(cand, key=lambda k: abs(tramos[k][0] - _ini[e])))
            grupos = [(_st[e], (_st[e + 1] - 1) if e + 1 < N else T - 1) for e in range(N)]
            print("Cortes forzados con inicios.json")
        else:
            print(f"AVISO: inicios.json tiene {len(_ini)} valores y hay {N} escenas: se ignora")
except Exception as _x:
    tramos, grupos = _tramos0, _grupos0
    print("AVISO: cortes forzados con inicios.json no aplicables, se usa el reparto normal:", _x)

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
if vel < (2.6 if YOUTUBE else 2.9):   # en los largos, ritmo algo más pausado (se escucha 10 minutos)
    atempo = min(1.08, (2.8 if YOUTUBE else 3.1) / vel)
max_p = None


def total(atempo, max_p):
    return sum(len(construir(g, max_p)) / SR / atempo + RESPIRO for g in grupos)


while total(atempo, max_p) > TMAX and atempo < 1.08:
    atempo = min(1.08, atempo + 0.01)
if total(atempo, max_p) > TMAX:
    max_p = 0.28
if palabras / (vtot / atempo) > 3.4:   # demasiado rápido: no acelerar más (antes esta línea aceleraba)
    atempo = max(1.0, min(atempo, 3.4 * vtot / palabras))


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
RECORTE0 = max(0, nz - int(0.02 * SR)) / SR   # segundos (ya con atempo) quitados al principio de la escena 1
escenas_audio[0] = x[int(RECORTE0 * SR):]

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


# --- 5b. (v28) Tiempo REAL de cada palabra del subtítulo --------------------------
# Si existe palabras.json (lo deja alinear.py: palabras de voz.mp3 con su segundo exacto), cada palabra del subtítulo
# recibe el instante en que la voz la dice de verdad, ya trasladado al vídeo (pausas recortadas, atempo y respiros).
# motor.js lo usa para el karaoke y el .srt para sus bloques. Sin palabras.json todo sigue como antes (reparto por longitud).
def _norm(w):
    import unicodedata
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))


def fichas_sub(e):
    """Las palabras del subtítulo de la escena tal y como las parte motor.js (el nombre del canal es una sola)."""
    txt = ESC[e].get("subtitulo") or ESC[e]["hablado"]
    txt = re.sub(r"sin humo te uve", "sin humo TV", txt, flags=re.I).replace("sin humo TV", "sin\u2060humo\u2060TV")
    return [w for w in re.split(r"[ \t\n]+", txt) if w]


def mapa_escena(g):
    """Tramos (inicio_original, fin_original, inicio_en_la_escena) de construir(g, max_p), antes del atempo."""
    i0, i1 = g
    m, o = [], 0.0
    a0 = max(0.0, tramos[i0][0] - 0.1)
    for k in range(i0, i1 + 1):
        a, b = tramos[k]
        if k == i0:
            a = a0
        m.append((a, b, o, 1.0)); o += b - a
        if k < i1:
            p = tramos[k + 1][0] - b
            q = max_p if (max_p is not None and p > 0.32) else p
            m.append((b, tramos[k + 1][0], o, q / p if p > 0 else 1.0)); o += q
    b = min(DUR, tramos[i1][1] + 0.2)
    m.append((tramos[i1][1], b, o, 1.0))
    return m


def a_video(e, s):
    """Segundo de voz.mp3 → segundo del vídeo final, dentro de la escena e."""
    m = mapa_escena(grupos[e])
    if s <= m[0][0]:
        o = 0.0
    elif s >= m[-1][1]:
        o = m[-1][2] + (m[-1][1] - m[-1][0])
    else:
        a, b, o0, f = next(x for x in m if x[0] <= s <= x[1])
        o = o0 + (s - a) * f
    o = o / atempo - (RECORTE0 if e == 0 else 0.0)
    T_ = tiempos[e]
    return min(max(T_["ini"] + o, T_["ini"]), T_["voz_fin"])


_pj = os.path.join(D, "palabras.json")
if os.path.exists(_pj):
    try:
        W = json.load(open(_pj))
        hyp = [_norm(w[2]) for w in W]
        ref, de = [], []
        for e in range(N):
            for i, w in enumerate(fichas_sub(e)):
                ref.append(_norm(w.replace("\u2060", " ")).replace(" ", "")); de.append((e, i))
        import difflib
        par = {}
        for x, y, n in difflib.SequenceMatcher(None, ref, hyp, autojunk=False).get_matching_blocks():
            for k in range(n):
                if ref[x + k]:
                    par[x + k] = y + k
        acertadas = 0
        for e in range(N):
            idx = [r for r in range(len(ref)) if de[r][0] == e]
            T_ = tiempos[e]
            ini = [None] * len(idx)
            for j, r in enumerate(idx):
                if r in par:
                    t_ = a_video(e, W[par[r]][0])
                    if T_["ini"] - 0.01 <= t_ <= T_["voz_fin"]:   # la palabra está en el trozo de voz de su escena
                        ini[j] = t_; acertadas += 1
            # huecos (cifras que la voz dice en letra, palabras mal oídas): se reparten por longitud entre las vecinas
            fichas = fichas_sub(e)
            peso = [len(_norm(w)) + 2 for w in fichas]
            anclas = [(-1, T_["ini"] + 0.02)] + [(j, ini[j]) for j in range(len(ini)) if ini[j] is not None] + [(len(ini), T_["voz_fin"] - 0.05)]
            for (ja, ta), (jb, tb) in zip(anclas, anclas[1:]):
                if jb - ja <= 1:
                    continue
                s0 = max(ja, 0); tot = max(1, sum(peso[s0:jb]))
                for j in range(ja + 1, jb):
                    ini[j] = ta + (tb - ta) * sum(peso[s0:j]) / tot
            for j in range(1, len(ini)):   # nunca hacia atrás
                ini[j] = max(ini[j], ini[j - 1] + 0.04)
            fin = [min(ini[j + 1], ini[j] + 1.2) if j + 1 < len(ini) else max(ini[j] + 0.2, T_["voz_fin"] - 0.05) for j in range(len(ini))]
            T_["palabras"] = [[round(a, 3), round(b, 3)] for a, b in zip(ini, fin)]
        print(f"Subtítulos al ritmo real de la voz: {acertadas}/{len(ref)} palabras con su segundo exacto")
    except Exception as x:
        print("AVISO: no se pudo usar palabras.json (subtítulos repartidos por longitud):", x)
pcm = (np.clip(voz, -1, 1) * 32767).astype(np.int16)
tmp = os.path.join(D, "_vf.raw")
pcm.tofile(tmp)
sh(f'ffmpeg -y -v error -f s16le -ar {SR} -ac 1 -i "{tmp}" "{os.path.join(D, "voz_final.wav")}"')
json.dump({"duracion": total_s, "escenas": tiempos, "atempo": round(atempo, 3)},
          open(os.path.join(D, "tiempos.json"), "w"), indent=1)
# Capítulos para la descripción de YouTube (0:00 Título…): necesita "capitulos" en proyecto.json
if YOUTUBE and P.get("capitulos"):
    caps = sorted(P["capitulos"], key=lambda c: c["desde"])
    lin = []
    for c in caps:
        s0 = 0 if c["desde"] == 0 else tiempos[c["desde"]]["ini"]
        lin.append(f"{int(s0 // 60)}:{int(s0 % 60):02d} {c['titulo']}")
    open(os.path.join(D, "capitulos.txt"), "w", encoding="utf-8").write("\n".join(lin) + "\n")

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
    PW = tm.get("palabras")
    if PW and len(PW) != len(txt.split()):
        PW = None   # el nombre del canal cuenta como una palabra en motor.js: se usa el reparto clásico
    wi = 0
    for b in bl:
        a = tm["ini"] + vt * acc / L
        acc += len(b)
        z = tm["ini"] + vt * acc / L
        if PW:   # v28: con los tiempos reales de cada palabra
            nw = len(b.split()); a, z = PW[wi][0], PW[wi + nw - 1][1]; wi += nw
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
