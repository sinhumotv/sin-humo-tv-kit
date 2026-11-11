#!/usr/bin/env python3
"""Voz GRATIS y SIN LÍMITES con Qwen3-TTS (Alibaba, licencia Apache 2.0), copiando la voz propia del canal.
(12-nov-2026) Sustituye a Gemini como voz principal de sin humo TV: misma voz siempre, acento de España, sin cuotas.

Uso: python3 voz_qwen.py <carpeta> [--voz sinhumo]
Lee <carpeta>/voz.txt (escenas separadas por una línea en blanco) y deja <carpeta>/voz.mp3, listo para audio.py.
La voz de referencia está en voces/<voz>.wav y su transcripción en voces/<voz>.txt.

IMPORTANTE para los guiones: esta voz NO susurra ni actúa emociones por encargo; el tono sale del propio texto
(signos de pregunta y exclamación, puntos suspensivos). Nada de etiquetas ni acotaciones: se quitan.

Control de calidad de cada escena (si falla, se repite con otra semilla, hasta 4 intentos):
  · lo que se oye (faster-whisper) tiene que coincidir con el texto (no se come ni se inventa palabras);
  · el tono medio tiene que parecerse al de la referencia (evita que la voz "cambie" al arrancar);
  · ritmo razonable (ni atropellado ni a cámara lenta).
Sale con código 2 si alguna escena no sale bien: quien lo llama pasa a la voz de reserva (Gemini).
"""
import difflib, os, re, subprocess, sys, time, unicodedata
import numpy as np
import soundfile as sf
import torch

AQUI = os.path.dirname(os.path.abspath(__file__))
ETIQ = re.compile(r"\[[^\]]{1,20}\]\s*")
PAUSA = 0.5          # silencio entre escenas (audio.py luego ajusta las pausas)
INTENTOS = 4


def _letras(m):
    try:
        from num2words import num2words
        return " " + num2words(int(m.group(0).replace(".", "")), lang="es") + " "
    except Exception:
        return " " + m.group(0) + " "


def norm(t):
    t = re.sub(r"\d[\d.]*", _letras, t)   # whisper escribe «90»; el guion dice «noventa»
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ ]", " ", t).split()


def recortar(w, sr, umbral=0.02, margen=0.05):
    win = int(sr * 0.02)
    n = len(w) // win
    if n == 0:
        return w
    e = np.abs(w[: n * win]).reshape(n, win).mean(1)
    on = np.nonzero(e > umbral * e.max())[0]
    if len(on) == 0:
        return w
    return w[max(0, on[0] * win - int(sr * margen)): min(len(w), (on[-1] + 1) * win + int(sr * margen))]


def tono(w, sr):
    import librosa
    y = librosa.resample(w, orig_sr=sr, target_sr=16000) if sr != 16000 else w
    f0 = librosa.yin(y, fmin=60, fmax=400, sr=16000)
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
    k = min(len(f0), len(rms))
    v = f0[:k][rms[:k] > 0.3 * rms.max()]
    return float(np.median(v)) if len(v) else 0.0


class Oido:
    def __init__(self):
        from faster_whisper import WhisperModel
        self.m = WhisperModel(os.environ.get("WHISPER_VOZ", "base"), device="cpu", compute_type="int8")

    def __call__(self, w, sr):
        import librosa
        y = librosa.resample(w, orig_sr=sr, target_sr=16000).astype(np.float32)
        segs, _ = self.m.transcribe(y, language="es", beam_size=1)
        return " ".join(s.text for s in segs)


def generar(escenas, voz="sinhumo", device="cpu", log=print):
    """Devuelve (audio float32, sr, repeticiones). device="cuda" en el servidor con GPU."""
    ref = os.path.join(AQUI, "voces", f"{voz}.wav")
    ref_txt = open(os.path.join(AQUI, "voces", f"{voz}.txt"), encoding="utf-8").read().strip()
    from qwen_tts import Qwen3TTSModel
    if device == "cpu":
        torch.set_num_threads(os.cpu_count() or 4)
    t0 = time.time()
    m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map=device,
                                      dtype=torch.bfloat16 if device != "cpu" else torch.float32)
    prompt = m.create_voice_clone_prompt(ref_audio=ref, ref_text=ref_txt, x_vector_only_mode=False)
    w_ref, sr_ref = sf.read(ref, dtype="float32")
    tono_ref = tono(w_ref if w_ref.ndim == 1 else w_ref.mean(1), sr_ref)
    oido = Oido()
    log(f"Qwen listo en {time.time()-t0:.0f}s · {len(escenas)} escenas · tono de referencia {tono_ref:.0f} Hz")
    partes, sr, repetidas = [], 24000, 0
    for i, esc in enumerate(escenas):
        mejor, nota_mejor = None, -1.0
        for intento in range(INTENTOS):
            torch.manual_seed(1000 + 97 * i + intento)
            wavs, sr = m.generate_voice_clone(text=esc, language="Spanish", voice_clone_prompt=prompt)
            w = recortar(np.asarray(wavs[0], dtype=np.float32), sr)
            dur = len(w) / sr
            oido_txt = oido(w, sr)
            parecido = difflib.SequenceMatcher(None, norm(esc), norm(oido_txt)).ratio()
            t = tono(w, sr)
            desvio = abs(t - tono_ref) / tono_ref if tono_ref and t else 1.0
            cps = len(esc) / max(dur, 0.1)
            ok = parecido >= 0.85 and desvio <= 0.25 and 8 <= cps <= 24
            nota = parecido - desvio
            if nota > nota_mejor:
                mejor, nota_mejor = w, nota
            if ok:
                break
            repetidas += 1
            log(f"escena {i+1}: repito (parecido {parecido:.2f}, tono {t:.0f} Hz, {cps:.0f} car/s) → «{oido_txt[:70]}»")
        else:
            if nota_mejor < 0.6:
                raise RuntimeError(f"la escena {i+1} no sale bien tras {INTENTOS} intentos")
            log(f"escena {i+1}: me quedo con el mejor intento (nota {nota_mejor:.2f})")
        partes += [mejor, np.zeros(int(sr * PAUSA), np.float32)]
    audio = np.concatenate(partes[:-1])
    audio = audio / (float(np.abs(audio).max()) or 1.0) * 0.9
    return audio.astype(np.float32), sr, repetidas


def escenas_de(D):
    texto = ETIQ.sub("", open(os.path.join(D, "voz.txt"), encoding="utf-8").read())
    return [" ".join(e.split()) for e in re.split(r"\n\s*\n", texto) if e.strip()]


def main():
    a = sys.argv[1:]
    D = a[0]
    voz = a[a.index("--voz") + 1] if "--voz" in a else "sinhumo"
    escenas = escenas_de(D)
    if not escenas:
        sys.exit("voz.txt vacío")
    t1 = time.time()
    try:
        if os.environ.get("VOZ_QWEN_REMOTO"):   # en el servidor: la GPU de Modal (función voz_qwen de explicalo-fabrica)
            import io, modal
            f = modal.Function.from_name(os.environ.get("VOZ_QWEN_APP", "explicalo-fabrica"), "voz_qwen")
            audio, sr = sf.read(io.BytesIO(f.remote(escenas, voz)), dtype="float32")
            rep = "?"
        else:
            audio, sr, rep = generar(escenas, voz, log=lambda x: print(x, flush=True))
    except Exception as x:
        print(f"FALLO: {str(x)[:300]}", flush=True)
        sys.exit(2)
    wav = os.path.join(D, "voz_qwen.wav")
    sf.write(wav, audio, sr)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", wav, "-ac", "1", "-ar", "44100", "-b:a", "192k",
                    os.path.join(D, "voz.mp3")], check=True)
    dur = len(audio) / sr
    print(f"VOZ QWEN OK: {dur:.1f}s de audio en {time.time()-t1:.0f}s (x{(time.time()-t1)/dur:.1f}), {rep} repeticiones", flush=True)


if __name__ == "__main__":
    main()
