#!/usr/bin/env python3
"""v26 · Cortes de escena exactos para vídeos largos (gratis, sin créditos).
Cuando audio.py reparte mal las escenas (la tabla muestra escenas por debajo de 9 o por encima de 17 car/s:
la voz de ElevenLabs encadena párrafos sin pausa), transcribe voz.mp3 en local con faster-whisper (modelo
"small", ~3 min para 8 min de voz en 2 núcleos), alinea las palabras con escenas[].hablado y escribe
<carpeta>/inicios.json. Luego basta volver a ejecutar audio.py, que usa esos inicios (parte la voz en el
punto más silencioso junto a la primera palabra de cada escena).
Uso: python3 alinear.py <carpeta>"""
import json, os, sys, re, subprocess, unicodedata, difflib
try:
    from faster_whisper import WhisperModel
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "faster-whisper"], check=False)
    from faster_whisper import WhisperModel
import numpy as np
D = sys.argv[1]
P = json.load(open(D + "/proyecto.json", encoding="utf-8"))
a = np.frombuffer(subprocess.run(["ffmpeg", "-loglevel", "error", "-i", D + "/voz.mp3", "-ar", "16000", "-ac", "1", "-f", "s16le", "-"],
                                 capture_output=True).stdout, np.int16).astype(np.float32) / 32768
segs, _ = WhisperModel(os.environ.get("WHISPER_MODELO", "small"), device="cpu", compute_type="int8").transcribe(a, language="es", word_timestamps=True)
W = [(w.start, w.end, w.word.strip()) for s in segs for w in s.words]
json.dump(W, open(D + "/palabras.json", "w"), ensure_ascii=False)
def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))
ref, sc = [], []
for i, e in enumerate(P["escenas"]):
    for w in e["hablado"].split():
        if norm(w): ref.append(norm(w)); sc.append(i)
hyp = [norm(w[2]) for w in W]
m = {}
for x, y, n in difflib.SequenceMatcher(None, ref, hyp, autojunk=False).get_matching_blocks():
    for k in range(n): m[x + k] = y + k
N = len(P["escenas"]); ini = []
for e in range(N):
    t = None
    for off, r in enumerate([r for r in range(len(ref)) if sc[r] == e]):
        if r in m: t = W[m[r]][0] - 0.33 * off; break
    ini.append(t)
for e in range(N):
    if ini[e] is None:
        a_ = max(j for j in range(e) if ini[j] is not None)
        b_ = min([j for j in range(e + 1, N) if ini[j] is not None] or [None])
        ini[e] = ini[a_] + (ini[b_] - ini[a_]) * (e - a_) / (b_ - a_) if b_ is not None else ini[a_] + 3
ini[0] = 0.0
json.dump([round(x, 2) for x in ini], open(D + "/inicios.json", "w"))
print(f"inicios.json: {N} escenas · palabras reconocidas {sum(1 for r in range(len(ref)) if r in m) / len(ref):.0%}. Ahora: python3 audio.py {D}")
