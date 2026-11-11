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
    # (11-nov-2026) TODOS con la muestra original de la voz 6: las muestras emocionales sacadas con ElevenLabs v4
    # perdían el acento de España y Chatterbox lo copiaba. El registro se consigue con los ajustes y, en el susurro,
    # con un tratamiento de audio (más bajo, sin graves, más íntimo).
    "normal":  ("referencia.wav", 0.80, 0.35, 0.75),
    "emocion": ("referencia.wav", 1.05, 0.30, 0.80),
    "intriga": ("referencia.wav", 0.60, 0.45, 0.75),
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
            if out and out[-1][0] == reg and len(out[-1][1]) < 40:
                out[-1] = (reg, out[-1][1] + " " + p)   # frases muy cortas se juntan (suenan más naturales)
            else:
                out.append((reg, p))
    return out


def susurro(w, sr):
    """Voz baja e íntima: quita graves, suaviza y baja el volumen (sin que suene a efecto)."""
    import torchaudio.functional as F
    w = F.highpass_biquad(w, sr, 260)
    w = F.lowpass_biquad(w, sr, 7000)
    return w * 0.55


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
            if reg == "susurro":
                w = susurro(w, sr)
            trozos.append(w)
            pausa = 0.45 if f.endswith("...") or f.endswith("…") else 0.25
            trozos.append(torch.zeros(1, int(sr * pausa)))
        trozos[-1] = torch.zeros(1, int(sr * 0.7))
    audio = torch.cat(trozos[:-1], dim=1)
    dur = audio.shape[1] / sr
    print(f"AUDIO {dur:.1f}s generado en {time.time()-t1:.0f}s (x{(time.time()-t1)/dur:.1f} del tiempo real)", flush=True)
    wav = os.path.join(carpeta, "voz.wav")
    ta.save(wav, audio, sr)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", wav, "-af", "loudnorm=I=-16", "-b:a", "160k",
                    os.path.join(carpeta, "voz.mp3")], check=True)


if __name__ == "__main__":
    main()
