#!/usr/bin/env python3
"""Voz GRATIS de sin humo TV con Qwen3-TTS (Alibaba, Apache 2.0) copiando la voz del canal (referencia.wav).

Uso: python3 voz_chatterbox/voz_qwen.py <carpeta> [<carpeta> ...]
Lee <carpeta>/voz.txt (escenas separadas por una línea en blanco) y deja <carpeta>/voz.wav.
Las etiquetas [susurro] [emocion] [intriga] [normal] se quitan: con este modelo el tono sale del propio texto
(signos, puntos suspensivos, palabras), así que el guion tiene que escribirse con esa intención.
Cada escena se dice de un tirón con la misma referencia, así el tono no salta entre escenas.
"""
import os, re, sys, time
import numpy as np
import soundfile as sf
import torch

AQUI = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(AQUI, "referencia.wav")
REF_TXT = ("¡Ojo con esto! Hoy el Gobierno ha aprobado una medida que va a tocar el bolsillo de millones de "
           "españoles. Y escuchad bien, porque casi nadie se ha enterado.")
ETIQ = re.compile(r"\[(susurro|emoci[oó]n|intriga|normal|claro)\]\s*", re.I)


def recortar(w, sr, umbral=0.02, margen=0.05):
    env = np.abs(w)
    win = int(sr * 0.02)
    n = len(env) // win
    if n == 0:
        return w
    e = env[: n * win].reshape(n, win).mean(1)
    on = np.nonzero(e > umbral * e.max())[0]
    if len(on) == 0:
        return w
    a = max(0, on[0] * win - int(sr * margen))
    b = min(len(w), (on[-1] + 1) * win + int(sr * margen))
    return w[a:b]


def main():
    from qwen_tts import Qwen3TTSModel
    torch.set_num_threads(os.cpu_count() or 4)
    t0 = time.time()
    m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map="cpu", dtype=torch.float32)
    prompt = m.create_voice_clone_prompt(ref_audio=REF, ref_text=REF_TXT, x_vector_only_mode=False)
    print(f"modelo cargado en {time.time()-t0:.0f}s", flush=True)
    for carpeta in sys.argv[1:]:
        texto = ETIQ.sub("", open(os.path.join(carpeta, "voz.txt"), encoding="utf-8").read())
        escenas = [" ".join(e.split()) for e in re.split(r"\n\s*\n", texto) if e.strip()]
        partes, sr, t1 = [], 24000, time.time()
        for esc in escenas:
            wavs, sr = m.generate_voice_clone(text=esc, language="Spanish", voice_clone_prompt=prompt)
            partes += [recortar(np.asarray(wavs[0], dtype=np.float32), sr), np.zeros(int(sr * 0.3), np.float32)]
        audio = np.concatenate(partes[:-1])
        dur = len(audio) / sr
        print(f"{carpeta}: AUDIO {dur:.1f}s en {time.time()-t1:.0f}s (x{(time.time()-t1)/dur:.1f})", flush=True)
        sf.write(os.path.join(carpeta, "voz.wav"), audio, sr)


if __name__ == "__main__":
    main()
