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
# v34 (10-nov-2026) · MÚSICA NUEVA hecha por código (sin licencias): bajo, acordes con cuerpo, arpegio y batería suave, con una
# progresión de 8 compases y cambios cada pocos compases (entrada sin batería, cortes, tramos más tranquilos) para que no sea
# un bucle idéntico durante todo el vídeo. Tres ambientes según "tono": tensa (La menor), ligera (Do mayor) y grave
# (Re menor, lenta y sin batería). "musica": "clasica" en proyecto.json vuelve a la anterior.
# v72 (11-nov-2026): cada vídeo con su propia variante (progresión, tonalidad y tempo elegidos con el título como semilla),
# para que los cortos seguidos no suenen todos igual; el mismo vídeo siempre suena igual si se rehace.
import zlib
_rv = np.random.default_rng(zlib.crc32(str(P.get("titulo_noticia") or P.get("titulo") or "").encode()))
_TR = int(_rv.choice([-3, -2, -1, 0, 1, 2]))
_ALT = {"tensa": [None,
                  [[57, 60, 64], [52, 55, 59], [53, 57, 60], [55, 59, 62], [57, 60, 64], [52, 55, 59], [50, 53, 57], [52, 56, 59]],
                  [[57, 60, 64], [55, 59, 62], [53, 57, 60], [52, 56, 59]] * 2,
                  [[57, 60, 64], [48, 52, 55], [55, 59, 62], [50, 54, 57], [57, 60, 64], [48, 52, 55], [53, 57, 60], [52, 56, 59]]],
        "ligera": [None,
                   [[53, 57, 60], [48, 52, 55], [55, 59, 62], [57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62], [55, 59, 62]]],
        "grave": [None, [[50, 53, 57], [46, 50, 53], [43, 46, 50], [45, 49, 52]] * 2]}
_PV = _rv.integers(0, 99)
_DBPM = int(_rv.integers(-6, 7))

def musica_nueva():
    bpm = {"tensa": 104, "ligera": 112, "grave": 84}.get(tono, 104) + _DBPM
    beat = 60 / bpm; compas = 4 * beat
    n = int((DUR + 2) * SR)
    hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)
    # acordes (notas MIDI de la tríada, fundamental primero), 8 compases
    PROG = {"tensa": [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62], [57, 60, 64], [53, 57, 60], [50, 53, 57], [52, 56, 59]],
            "ligera": [[48, 52, 55], [55, 59, 62], [57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62], [53, 57, 60], [55, 59, 62]],
            "grave": [[50, 53, 57], [46, 50, 53], [53, 57, 60], [48, 52, 55], [50, 53, 57], [46, 50, 53], [55, 58, 62], [57, 61, 64]]}[tono if tono in ("tensa", "ligera", "grave") else "tensa"]
    _alts = _ALT.get(tono if tono in _ALT else "tensa"); _p = _alts[_PV % len(_alts)]
    if _p: PROG = _p
    PROG = [[m + _TR for m in ac] for ac in PROG]
    print(f"música: tono {tono}, variante {_PV % len(_alts)}, transporte {_TR:+d}, {bpm} bpm")
    grave = tono == "grave"
    pad, bajo, arp, bat = np.zeros(n), np.zeros(n), np.zeros(n), np.zeros(n)

    def pon_(dest, x, ts, g=1.0):
        a = int(ts * SR)
        if a >= n or a < 0: return
        x = x[:n - a]; dest[a:a + len(x)] += x * g

    def nota(f, dur, arm, caida, ataque=.004):   # timbre = armónicos; envolvente = ataque corto + caída exponencial
        t = np.arange(int(dur * SR)) / SR
        x = sum(am * np.sin(2 * np.pi * f * (k + 1) * t) for k, am in enumerate(arm))
        return x * np.minimum(1, t / ataque) * np.exp(-t * caida) * np.minimum(1, (dur - t) / .02)

    # batería
    kt = np.arange(int(.28 * SR)) / SR
    bombo = np.sin(2 * np.pi * (48 * kt + 62 / 28 * (1 - np.exp(-kt * 28)))) * np.exp(-kt * 11)
    ct = np.arange(int(.16 * SR)) / SR
    ruido = rng.normal(0, 1, len(ct)); ruido = ruido - np.convolve(ruido, np.ones(24) / 24, "same")     # sin graves
    palma = ruido * (np.exp(-ct * 34) + .6 * np.exp(-np.maximum(0, ct - .012) * 34) * (ct > .012)) * .5
    ht = np.arange(int(.045 * SR)) / SR
    hr = rng.normal(0, 1, len(ht)); hr = hr - np.convolve(hr, np.ones(6) / 6, "same")                   # solo agudos
    charles = hr * np.exp(-ht * 110) * .22

    ncomp = int(np.ceil((DUR + 2) / compas))
    PAT = [[0, 1, 2, 1, 0, 2, 1, 2], [0, 2, 1, 2, 0, 1, 2, 1], [2, 1, 0, 1, 2, 0, 1, 0]]
    for c in range(ncomp):
        t0 = c * compas; ac = PROG[c % 8]
        tranquilo = (c // 8) % 4 == 3 and c % 8 < 4          # cada 32 compases, 4 más tranquilos (sin batería)
        corte = c % 8 == 7                                    # último compás de cada vuelta: sin bombo ni palma
        # acordes con cuerpo: 3 notas, dos voces un poco desafinadas, entrada y salida suaves
        tt = np.arange(int((compas + .5) * SR)) / SR
        env = np.minimum(1, tt / .45) * np.minimum(1, (compas + .5 - tt) / .5)
        for m in ac:
            f = hz(m)
            x = sum(am * (np.sin(2 * np.pi * f * 1.0015 * (k + 1) * tt) + np.sin(2 * np.pi * f * .9985 * (k + 1) * tt + .7)) for k, am in enumerate([1, .32, .14, .06]))
            pon_(pad, x * env, t0, .16)
        if c < 2: pass                                        # entrada: solo acordes y arpegio (la voz arranca limpia)
        # bajo
        f0 = hz(ac[0] - 24)
        if c >= 2:
            if grave: pon_(bajo, nota(f0, compas, [1, .25], .5, .03), t0, .8)
            else:
                for bt in ([0, 1.5, 2, 3.5] if not tranquilo else [0, 2]):
                    pon_(bajo, nota(f0, beat * .9, [1, .3, .08], 4.2), t0 + bt * beat, .85)
        # arpegio (notas del acorde una octava arriba)
        pat = PAT[(c // 8) % 3]
        if grave:
            for i in range(4): pon_(arp, nota(hz(ac[pat[i]] + 12), beat * 1.6, [1, .35, .12, .04], 2.6, .006), t0 + i * beat, .30)
        else:
            oct_ = 24 if (c // 16) % 2 else 12
            for i in range(8):
                acento = 1.0 if i % 2 == 0 else .72
                pon_(arp, nota(hz(ac[pat[i]] + oct_), beat * .48, [1, .4, .18], 9.0), t0 + i * beat / 2, .30 * acento)
        # batería (nunca en tono grave)
        if not grave and c >= 2:
            for i in range(8):
                if i % 2 == 1 or c >= 4: pon_(bat, charles, t0 + i * beat / 2, 1.0 if i % 2 else .6)
            if c >= 4 and not tranquilo and not corte:
                for bt in (0, 2, 2.5 if c % 2 else 99): 
                    if bt < 4: pon_(bat, bombo, t0 + bt * beat, .9)
                for bt in (1, 3): pon_(bat, palma, t0 + bt * beat, .55)
    mus = pad * .55 + bajo * .55 + arp * .5 + bat * .6
    m = np.tanh(mus[:int(DUR * SR)] * 1.2)
    fin = min(len(m), int(1.5 * SR)); m[-fin:] *= np.linspace(1, 0, fin)      # se apaga al final
    return m / (np.max(np.abs(m)) + 1e-9)


def musica_clasica():
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
    return m


m = musica_clasica() if P.get("musica") == "clasica" else musica_nueva()
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
PRO = (P.get("aspecto") or "pro") == "pro"
# v56 (11-nov-2026): MISMA regla que TIPO_TR de motor_pro.js (v76: 12 transiciones), cada una con su sonido
GRAVE_ = P.get("tono") == "grave"
TR_TODAS = ["barrido", "iris", "zoom", "persiana", "empuje", "mancha", "giro", "cortina", "glitch", "diagonal", "rebote", "burbujas"]   # v76: 12
TR_GRAVE = ["barrido", "zoom", "empuje", "iris", "persiana"]
def _base(i): return TR_GRAVE[(i * 2) % 5] if GRAVE_ else TR_TODAS[(i * 5) % 12]
TRS = [""]
for j_ in range(1, len(P["escenas"])):
    e_ = P["escenas"][j_]; tipo_ = (e_.get("visual") or {}).get("tipo"); em_ = str(e_.get("voz") or "").lower()
    t_ = "cortina" if (not GRAVE_ and tipo_ == "mencion") else "glitch" if (not GRAVE_ and em_ in ("surprised", "tense", "indignant")) else _base(j_)
    if t_ == "glitch" and "glitch" in TRS[max(0, j_ - 2):j_]: t_ = _base(j_ + 1) if _base(j_) == "glitch" else _base(j_)
    if t_ == TRS[j_ - 1]: t_ = _base(j_ + 2) if _base(j_ + 1) == t_ else _base(j_ + 1)
    TRS.append(t_)
gl_ = int(.26 * SR); gt_ = np.arange(gl_) / SR
glitch_s = (rng.normal(0, 1, gl_) * (np.sign(np.sin(2 * np.pi * 37 * gt_)) * .5 + .5) + np.sign(np.sin(2 * np.pi * 220 * gt_)) * .3) * np.exp(-gt_ * 6) * .5
for k, e in enumerate(T["escenas"][1:], 1):
    if not PRO:
        pon(whoosh, e["ini"] - .3, .9)           # en el respiro entre escenas, no encima de palabras
        continue
    tr = TRS[k] if k < len(TRS) else "barrido"
    if tr in ("barrido", "empuje"):
        pon(whoosh, e["ini"] - .2, .9)
    elif tr == "zoom":
        pon(whoosh[::-1] * .8, e["ini"] - .3, .9); pon(pop, e["ini"] + .02, .5)
    elif tr == "cortina":
        pon(whoosh, e["ini"] - .14, 1.0); pon(impacto, e["ini"] + .2, .35)
    elif tr == "iris":
        pon(zum, e["ini"] - .12, .55)
    elif tr == "persiana":
        pon(whoosh[: len(whoosh) // 2], e["ini"] - .05, .8)
        for q in (0, .1, .2): pon(pop, e["ini"] + q, .25)
    elif tr == "giro":
        pon(whoosh * .6, e["ini"] - .1, .8); pon(pop, e["ini"] + .17, .45)
    elif tr == "glitch":
        pon(glitch_s, e["ini"], .9 if not GRAVE_ else .4)
    elif tr == "diagonal":
        pon(whoosh, e["ini"] - .16, 1.0)
    elif tr == "rebote":
        pon(whoosh[::-1] * .6, e["ini"] - .1, .7); pon(pop, e["ini"] + .12, .6)
    elif tr == "burbujas":
        for q in (0, .08, .16, .24): pon(pop, e["ini"] - .05 + q, .3)
    elif tr == "mancha":
        pon(whoosh, e["ini"] - .1, .9); pon(impacto, e["ini"] + .22, .25)
for z in P.get("zum", []):
    pon(zum, z, .8)
pon(pop, T["escenas"][-1]["voz_fin"] + .05)  # pop final
# v52 (11-nov-2026): «tic» muy suave en cada palabra clave (*así*), a la vez que el empujón de cámara del motor pro
if PRO and P.get("tono") != "grave":
    tl_ = int(.05 * SR); tt_ = np.arange(tl_) / SR
    tic = np.sin(2 * np.pi * 1700 * tt_) * np.exp(-tt_ * 90) + np.sin(2 * np.pi * 120 * tt_) * np.exp(-tt_ * 40) * .6
    for e, s_ in zip(P["escenas"], T["escenas"]):
        ws, pal = str(e.get("subtitulo") or "").split(), s_.get("palabras") or []
        if len(ws) != len(pal): continue
        for i, w in enumerate(ws):
            if w.startswith("*"):   # empieza un grupo de palabras clave
                pon(tic, pal[i][0] - .01, .22)
sfx /= np.max(np.abs(sfx)) + 1e-9
# ---------- v60 (11-nov-2026): sonido propio de cada gráfico del motor pro, a tiempo con su animación ----------
def _t(d): return np.arange(int(d * SR)) / SR
def tono(f0, f1, d, dec=6, onda="sin"):
    t = _t(d); f = f0 + (f1 - f0) * t / d; fase = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(fase) if onda == "sin" else np.sign(np.sin(fase)) * .5
    return x * np.exp(-t * dec) * np.minimum(1, t / .004)
def suma(*xs):
    n = max(len(x) for x in xs); o = np.zeros(n)
    for x in xs: o[:len(x)] += x
    return o
def clic(f=2400, d=.03): return tono(f, f * .7, d, 120)
def tintineo(): return suma(tono(2900, 2900, .25, 14), .6 * tono(4350, 4350, .2, 18), .3 * tono(6100, 6100, .12, 25)) * .45
def ding(f=1320): return suma(tono(f, f, .6, 5), .4 * tono(f * 2, f * 2, .4, 8)) * .5
def zumbido(): return tono(150, 140, .28, 6, "cuad") * .6
def subida(d=.9, f0=300, f1=1100): t = _t(d); return tono(f0, f1, d, 0) * np.sin(np.pi * t / d) * .35
def golpe_seco(): t = _t(.18); return (np.sin(2 * np.pi * (90 + 120 * np.exp(-t * 30)) * t) * np.exp(-t * 18) + rng.normal(0, 1, len(t)) * np.exp(-t * 80) * .3) * .8
def roce(d=.3): t = _t(d); return np.convolve(rng.normal(0, 1, len(t)), np.ones(25) / 25, "same") * np.sin(np.pi * t / d) * .5
def aplauso(d=1.2):
    x = np.zeros(int(d * SR))
    for _ in range(int(d * 40)):
        i = int(rng.uniform(0, len(x) - 2000)); b = rng.normal(0, 1, 1200) * np.exp(-np.arange(1200) / 150); x[i:i + 1200] += b * rng.uniform(.3, 1)
    return x * np.sin(np.pi * np.arange(len(x)) / len(x)) * .25
def sintonia(): return np.concatenate([ding(988)[:int(.14 * SR)], ding(1318)[:int(.14 * SR)], ding(1760)]) * .8
def alarma(d=.8): t = _t(d); f = np.where((t * 4).astype(int) % 2 == 0, 880, 660); return np.sin(2 * np.pi * np.cumsum(f) / SR) * .25 * np.minimum(1, (d - t) / .05)
GSFX = PRO and str(P.get("sonido_graficos", "si")) != "no"
# v83: mismo cálculo que entradas() de motor_pro.js: cada elemento de una lista entra cuando la voz lo nombra
import unicodedata
def _nrm(w): return re.sub(r"[^a-z0-9ñ]", "", "".join(c for c in unicodedata.normalize("NFD", str(w).lower()) if unicodedata.category(c) != "Mn"))
def entradas(k, its, d, ini=.3, paso=None):
    e, s_ = P["escenas"][k], T["escenas"][k]; n = max(1, len(its)); p0 = paso or max(.45, (d - .8) / n)
    ws = str(e.get("subtitulo") or e.get("hablado") or "").replace("*", "").split(); pal = s_.get("palabras") or []
    if len(ws) == len(pal): ps = [(_nrm(w), a - s_["ini"] + (1 if k == 0 else 0)) for w, (a, *_r) in zip(ws, pal)]
    else: ps = []
    r, desde = [], 0
    for it in its:
        cl4 = [c for c in map(_nrm, str(it or "").split()) if len(c) >= 4 or re.search(r"\d", c)]; hit = None
        for j in range(desde, len(ps)):
            if cl4 and any(ps[j][0] == c or (len(c) > 5 and ps[j][0].startswith(c[:5])) for c in cl4): desde = j + 1; hit = max(.15, ps[j][1] - .2); break
        r.append(hit)
    prev = -1
    for i in range(len(r)):
        if r[i] is None: r[i] = ini + i * p0 if prev < 0 else max(ini + i * p0, prev + max(.3, min(p0, (d - .5 - prev) / (len(r) - i))))
        if prev >= 0 and r[i] < prev + .3: r[i] = prev + .3
        prev = r[i]
    return r
if GSFX:
    for k, (e, s_) in enumerate(zip(P["escenas"], T["escenas"])):
        v = e.get("visual") or {}; tp = v.get("tipo"); d = max(1.0, s_["fin"] - s_["ini"])
        b = s_["ini"] - (1 if k == 0 else 0)          # en la escena 1 la animación ya está hecha en el fotograma 0
        g = .5 if GRAVE_ else 1.0
        def at(x, dt, gain=1.0):
            if b + dt >= s_["ini"] - .02: pon(x, b + dt, gain * g)
        if e.get("emoji") and not GRAVE_ and tp not in ("mencion", "cierre"): at(pop, .27, .25)   # v79: el emoji de la cabecera salta
        if tp == "mencion" and not GRAVE_:
            # v97: mismo guion que el motor: el botón aparece, la mano lo pulsa (clic), campana, y salen me gusta / comenta / comparte
            f_ = min(1, max(.55, (d - .4) / 2.6)); tP = 1.35 * f_
            at(pop, .55 * f_, .35); at(clic(900, .04), tP, .7); at(suma(ding(1046), .7 * ding(1318)) * .8, tP + .12, .55)
            for i in range(3): at(pop, tP + .25 + i * .18, .3)
            at(ding(1568) * .5, tP + .25 + .35, .35)
        elif tp == "cierre":
            at(pop, .9, .6)
        elif tp == "cifra" and any(c.isdigit() for c in str(v.get("valor") or "")):
            fin = min(1.0, d * .45)
            for q in np.arange(.03, fin, .06): at(clic(1600 + 1400 * q / fin, .02), q, .35)
            at(golpe_seco() * .6, fin, .6)
        elif tp == "contador":
            cs = [c for c in str(v.get("valor") or "") if c.isdigit()]; n = max(1, len(cs)); fin = .9 + .12 * (n - 1)
            for q in np.arange(.2, fin, .055): at(clic(1800 + rng.uniform(-200, 200)), q, .5)
            for i in range(n): at(golpe_seco() * .5, .9 + .12 * i, .5)
        elif tp == "dinero":
            for i in range(17): at(tintineo(), .15 + i * .045 + .3, .35)
        elif tp == "alerta":
            niv = 2 if "roj" in str(v.get("nivel")) else 1 if "naranj" in str(v.get("nivel")) else 0
            for l in range(niv + 1): at(tono(600 + 200 * l, 600 + 200 * l, .12, 10), .5 + l * .25, .5)
            at(alarma(), .5 + niv * .25 + .1, .7)
        elif tp == "reloj":
            at(subida(1.1, 500, 1400) * .6, .15); at(ding(1568), 1.25, .8)
            for q in np.arange(1.6, d - .2, .5): at(clic(3000 if int(q * 2) % 2 else 2200, .02), q, .4)
        elif tp == "checklist":
            it = (v.get("items") or [])[:4]; n = max(1, len(it))
            for i, q in enumerate(it):
                ok = q.get("ok") not in (False, "false") if isinstance(q, dict) else True
                at(ding(1480) if ok else zumbido(), entradas(k, [str(x.get("texto") if isinstance(x, dict) else x) for x in it], d, .25)[i] + .25, .7)
        elif tp == "ultimahora":
            at(sintonia(), 0, .8)
        elif tp == "podio":
            for pos in (2, 1, 0): at(subida(.5, 200, 600), .2 + (2 - pos) * .35, .6)
            at(aplauso(), .2 + 2 * .35 + .55, .9); at(ding(1760), .2 + 2 * .35 + .45, .5)
        elif tp == "escanos":
            for q in np.arange(.2, 1.4, .06): at(clic(1200 + 900 * (q - .2), .02), q, .25)
        elif tp in ("tendencia", "evolucion", "porcentaje", "termometro", "medidor"):
            baja = tp == "tendencia" and any(w in str(v.get("sentido", "")).lower() for w in ("baj", "cae", "desc", "menos"))
            at(subida(1.0, 900, 300) if baja else subida(1.0), .15, .8); at(ding(1320 if not baja else 880), 1.15, .5)
        elif tp == "bateria":
            for i in range(5): at(tono(700 + 120 * i, 700 + 120 * i, .08, 20), .2 + i * .2, .45)
        elif tp == "proporcion":
            de = min(10, max(2, int(float(str(v.get("de") or 10).replace(",", ".") or 10))))
            son = min(de, max(1, int(float(str(v.get("son") or 1).replace(",", ".") or 1))))
            for i in range(de): at(clic(1500, .025), .1 + i * .06, .4)
            for i in range(son): at(ding(1175 + 150 * i), .8 + i * .12, .4)
        elif tp == "mapa":
            for i, _ in enumerate((v.get("lugares") or [])[:3]): at(golpe_seco(), .8 + i * .35 + .28, .6)
        elif tp == "mundo":   # v75: zoom (silbido que baja) y golpe por cada chincheta
            at(subida(1.2, 1200, 380) * .7, .15, .7)
            for i, _ in enumerate((v.get("paises") or [])[:3]): at(golpe_seco(), 1.3 + i * .3 + .28, .6)
        elif tp == "balanza":   # v73: crujido al balancearse y golpe suave al asentarse
            at(roce(.25), .35, .4); at(roce(.2), .9, .35); at(golpe_seco() * .5, 1.6, .5)
        elif tp == "iceberg":   # v73: inmersión y un «ding» grave por cada dato de abajo
            at(subida(.8, 700, 220) * .6, .1, .6)
            for i, _ in enumerate((v.get("abajo") or [])[:3]): at(ding(880 - 110 * i), .9 + i * .55, .45)
        elif tp == "versus":
            at(roce(), .1, .5); at(roce(), .4, .5); at(impacto, .6, .5)
        elif tp == "fecha":
            at(roce(.25), 0, .6); at(golpe_seco(), .6, .5)
        elif tp == "lupa":
            at(subida(.6, 1200, 2400) * .5, .9)
        elif tp == "encuesta":
            at(roce(.9), .3, .4); at(ding(1568), 1.3, .5)
        elif tp == "prensa":
            at(roce(.3), 0, .7); at(roce(.5) * .6, .55, .5)
        elif tp == "dialogo":
            n = max(1, len((v.get("lineas") or [])[:3]))
            for i in range(n): at(pop, .15 + i * max(.5, (d - .6) / n), .8)
        elif tp in ("ranking", "lista", "pasos"):
            it = (v.get("items") or [])[:5 if tp == "ranking" else 4]; n = max(1, len(it))
            for i in range(n):
                q = (.25 + (n - 1 - i) * .22) if tp == "ranking" else entradas(k, [str(x.get("texto") if isinstance(x, dict) else x) for x in it[:4]], d, .3 if tp == "lista" else .2, None if tp == "lista" else max(.45, (d - .6) / n))[min(i, 3)]
                at(pop, q, .6)
# v88: «boing» corto cuando salta el emoji de reacción (en la primera palabra clave de la escena)
if PRO and P.get("tono") != "grave":
    for e, s_ in zip(P["escenas"], T["escenas"]):
        if not str(e.get("reaccion") or "").strip() or (e.get("visual") or {}).get("tipo") in ("mencion", "cierre"): continue
        ws, pal = str(e.get("subtitulo") or "").split(), s_.get("palabras") or []
        t0 = next((pal[i][0] for i, w in enumerate(ws) if w.startswith("*")), None) if len(ws) == len(pal) else None
        if t0 is None: t0 = s_["ini"] + min(1.2, (s_["fin"] - s_["ini"]) * .3)
        tb = np.arange(int(.22 * SR)) / SR
        boing = np.sin(2 * np.pi * np.cumsum(300 + 700 * (tb / .22) ** .5) / SR) * np.exp(-tb * 14) * np.minimum(1, tb / .005)
        pon(boing * .5 + pop[:len(boing)] * .4 if len(pop) >= len(boing) else boing * .6, t0, .7)
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
YOUTUBE = str(P.get("formato", "")).upper() == "YOUTUBE"
# Vídeo largo: calidad alta pero tamaño razonable para subirlo (10 min ≈ 150-300 MB)
CALIDAD = "-preset medium -crf 18 -maxrate 6M -bufsize 12M" if YOUTUBE else "-preset slow -crf 14"
META = (f'-metadata title="{tit}" -metadata artist="sin humo TV" -metadata copyright="© sin humo TV" '
        f'-metadata comment="Vídeo original de sin humo TV"')
if YOUTUBE:
    # Vídeo largo: dos pasadas con bitrate fijo para que pese ~88 MB (cabe en GitHub, límite 100 MB) sea cual sea la duración
    kbps = int(min(6000, max(600, 88e6 * 8 / DUR / 1000 - 160)))
    base = f'cd "{D}" && ffmpeg -y -v error -f concat -safe 0 -i _bloques.txt'
    sh(f'{base} -c:v libx264 -preset medium -tune animation -b:v {kbps}k -pass 1 -passlogfile _x264 -pix_fmt yuv420p -r 30 -an -f mp4 /dev/null')
    sh(f'{base} -i mezcla.wav -map 0:v -map 1:a -c:v libx264 -preset medium -tune animation -b:v {kbps}k -pass 2 -passlogfile _x264 '
       f'-pix_fmt yuv420p -r 30 -c:a aac -b:a 128k -ar 48000 -movflags +faststart -shortest {META} "{salida}"')
    sh(f'cd "{D}" && rm -f _x264*')
else:
    sh(f'cd "{D}" && ffmpeg -y -v error -f concat -safe 0 -i _bloques.txt -i mezcla.wav -map 0:v -map 1:a '
       f'-c:v libx264 {CALIDAD} -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest '
       f'{META} "{salida}"')
mb = os.path.getsize(salida) / 1e6
if mb > 30 and not YOUTUBE:
    sh(f'ffmpeg -y -v error -i "{salida}" -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -c:a copy -movflags +faststart '
       f'-map_metadata 0 "{os.path.join(D, "video_movil.mp4")}"')
print(f"MP4: {mb:.1f} MB")
