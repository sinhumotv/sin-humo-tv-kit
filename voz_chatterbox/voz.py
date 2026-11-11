#!/usr/bin/env python3
"""Voz GRATIS de sin humo TV con Chatterbox (modelo español de España) y la voz propia del canal.

Uso: python3 voz_chatterbox/voz.py <carpeta> [--expresividad 0.7]
Lee <carpeta>/voz.txt (escenas separadas por una línea en blanco) y deja <carpeta>/voz.wav y voz.mp3.
Cada frase se genera por separado con la MISMA referencia y la misma semilla, para que el tono no salte,
y se unen con pausas cortas (0,35 s entre frases, 0,8 s entre escenas).
Necesita el código del Space oficial (ResembleAI/Chatterbox-Multilingual-TTS-es-es) en PYTHONPATH.
"""
import os, re, sys, time, subprocess
import torch, torchaudio as ta

AQUI = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(AQUI, "referencia.wav")


def frases(parrafo):
    partes = re.split(r"(?<=[.!?…])\s+", parrafo.strip())
    out = []
    for p in partes:
        if out and len(out[-1]) < 40:  # frases muy cortas se juntan con la anterior (suenan más naturales)
            out[-1] += " " + p
        else:
            out.append(p)
    return [p for p in out if p]


def main():
    carpeta = sys.argv[1]
    ex = float(sys.argv[sys.argv.index("--expresividad") + 1]) if "--expresividad" in sys.argv else 0.7
    torch.set_num_threads(os.cpu_count() or 2)
    from chatterbox.tts import ChatterboxTTS
    t0 = time.time()
    m = ChatterboxTTS.from_pretrained("cpu")
    print(f"modelo cargado en {time.time()-t0:.0f}s", flush=True)
    texto = open(os.path.join(carpeta, "voz.txt"), encoding="utf-8").read()
    escenas = [e for e in re.split(r"\n\s*\n", texto) if e.strip()]
    sr = m.sr
    trozos = []
    t1 = time.time()
    for i, esc in enumerate(escenas):
        for j, f in enumerate(frases(esc)):
            torch.manual_seed(1234)
            w = m.generate(f, language_id="es", audio_prompt_path=REF, exaggeration=ex, cfg_weight=0.4, temperature=0.75)
            trozos.append(w)
            trozos.append(torch.zeros(1, int(sr * 0.35)))
        trozos[-1] = torch.zeros(1, int(sr * 0.8))
    audio = torch.cat(trozos[:-1], dim=1)
    dur = audio.shape[1] / sr
    print(f"AUDIO {dur:.1f}s generado en {time.time()-t1:.0f}s (x{(time.time()-t1)/dur:.1f} del tiempo real)", flush=True)
    wav = os.path.join(carpeta, "voz.wav")
    ta.save(wav, audio, sr)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", wav, "-af", "loudnorm=I=-16", "-b:a", "160k",
                    os.path.join(carpeta, "voz.mp3")], check=True)


if __name__ == "__main__":
    main()
