#!/usr/bin/env python3
"""Voz GRATIS de sin humo TV con Chatterbox (modelo español de España) y la voz propia del canal.

Uso: python3 voz_chatterbox/voz.py <carpeta>
Lee <carpeta>/voz.txt (escenas separadas por una línea en blanco) y deja <carpeta>/voz.wav y voz.mp3.

REGISTROS: en el guion se puede poner una etiqueta delante de una frase para cambiar cómo se dice:
  [susurro]  en voz baja, confidencial      [emocion]  sorpresa, entusiasmo, subidón
  [intriga]  misterio, suspense              [normal]   vuelve al tono de siempre
La etiqueta vale para esa frase y las siguientes de la misma escena, hasta otra etiqueta.
Cada registro usa una muestra de la MISMA voz del canal (referencia_*.wav), así el timbre no cambia.
"""
import os, re, sys, time, subprocess
import torch, torchaudio as ta

AQUI = os.path.dirname(os.path.abspath(__file__))
# registro: (muestra de referencia, expresividad, cfg, temperatura)
REGISTROS = {
    # Susurro: solo más bajo de intensidad (sin filtros: sonaban a enlatado).
    # (11-nov-2026) TODOS con la muestra original de la voz 6: las muestras emocionales sacadas con ElevenLabs v4
    # perdían el acento de España y Chatterbox lo copiaba. El registro se consigue con los ajustes y, en el susurro,
    # con un tratamiento de audio (más bajo, sin graves, más íntimo).
    "normal":  ("referencia.wav", 0.80, 0.35, 0.75),
    "emocion": ("referencia.wav", 1.60, 0.25, 0.90),
    "intriga": ("referencia.wav", 0.70, 0.40, 0.80),
    "susurro": ("referencia.wav", 0.35, 0.50, 0.70),
}
ETIQ = re.compile(r"\[(susurro|emoci[oó]n|intriga|normal)\]", re.I)


def piezas(escena):
    """Devuelve [(registro, frase)] de una escena, respetando las etiquetas."""
    reg, out = "normal", []
    for i, trozo in enumerate(ETIQ.split(escena)):
        if i % 2 == 1:
            reg = trozo.lower().replace("ó", "o")
            continue
        partes = [p for p in re.split(r"(?<=[.!?…])\s+", trozo.strip()) if p]
        for p in partes:
            # las preguntas van solas: así el modelo sube el tono al final, como una pregunta de verdad
            if out and out[-1][0] == reg and len(out[-1][1]) + len(p) < 280 and not out[-1][1].endswith("?") and not p.endswith("?"):
                out[-1] = (reg, out[-1][1] + " " + p)   # se dice de un tirón todo lo que se pueda: suena más natural y sin cortes
            else:
                out.append((reg, p))
    return out


def recortar(w, sr, umbral=0.02, margen=0.06):
    """Quita el silencio que Chatterbox deja al principio y al final de cada trozo (las pausas largas)."""
    env = w.abs().squeeze(0)
    win = int(sr * 0.02)
    e = torch.nn.functional.avg_pool1d(env[None, None], win, win).squeeze()
    on = (e > umbral * e.max()).nonzero()
    if len(on) == 0:
        return w
    a = max(0, int(on[0]) * win - int(sr * margen))
    b = min(w.shape[1], (int(on[-1]) + 1) * win + int(sr * margen))
    w = w[:, a:b]
    f = int(sr * 0.01)
    w[:, :f] *= torch.linspace(0, 1, f); w[:, -f:] *= torch.linspace(1, 0, f)
    return w


def main():
    carpeta = sys.argv[1]
    torch.set_num_threads(os.cpu_count() or 2)
    from chatterbox.tts import ChatterboxTTS
    t0 = time.time()
    m = ChatterboxTTS.from_pretrained("cpu")
    print(f"modelo cargado en {time.time()-t0:.0f}s", flush=True)
    texto = open(os.path.join(carpeta, "voz.txt"), encoding="utf-8").read()
    escenas = [e for e in re.split(r"\n\s*\n", texto) if e.strip()]
    sr, trozos, n, t1 = m.sr, [], 0, time.time()
    for esc in escenas:
        for reg, f in piezas(esc):
            ref, ex, cfg, temp = REGISTROS[reg]
            torch.manual_seed(1000 + n); n += 1   # semilla distinta por frase: entonación menos repetitiva
            w = m.generate(f, language_id="es", audio_prompt_path=os.path.join(AQUI, ref),
                           exaggeration=ex, cfg_weight=cfg, temperature=temp)
            trozos.append(recortar(w, sr))
            trozos.append(torch.zeros(1, int(sr * 0.12)))
        trozos[-1] = torch.zeros(1, int(sr * 0.35))
    audio = torch.cat(trozos[:-1], dim=1)
    dur = audio.shape[1] / sr
    print(f"AUDIO {dur:.1f}s generado en {time.time()-t1:.0f}s (x{(time.time()-t1)/dur:.1f} del tiempo real)", flush=True)
    wav = os.path.join(carpeta, "voz.wav")
    ta.save(wav, audio, sr)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", wav, "-af", "loudnorm=I=-16", "-b:a", "160k",
                    os.path.join(carpeta, "voz.mp3")], check=True)


if __name__ == "__main__":
    main()
