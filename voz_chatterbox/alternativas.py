#!/usr/bin/env python3
"""Prueba de motores de voz gratis y de código abierto para sin humo TV (misma voz de referencia, mismas frases).

Uso: python3 voz_chatterbox/alternativas.py <motor> <carpeta_salida>
  motor: qwen_clon | qwen_diseno | zonos
"""
import os, sys, time
import numpy as np
import soundfile as sf
import torch

AQUI = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(AQUI, "referencia.wav")
REF_TXT = ("¡Ojo con esto! Hoy el Gobierno ha aprobado una medida que va a tocar el bolsillo de millones de "
           "españoles. Y escuchad bien, porque casi nadie se ha enterado.")
VOZ = ("Hombre español de unos 28 años, acento de Madrid (castellano de España, con la zeta y la erre bien marcadas), "
       "youtuber de noticias cercano, natural y con chispa")
# (registro, frase, instrucción de estilo, emoción Zonos [felicidad, tristeza, asco, miedo, sorpresa, enfado, otra, neutral])
FRASES = [
    ("erre", "Agarraos, que vienen curvas. El perro corre por la carretera mientras Ramón rompe el récord. ¡Es una barbaridad!",
     "con energía, pronunciando con fuerza las erres", [0.3, 0, 0, 0, 0.3, 0, 0.1, 0.3]),
    ("pregunta", "¿Sabéis cuánto cuesta de verdad un café en España? ¿Un euro? ¿Uno cincuenta? Pues agarraos.",
     "preguntando con curiosidad, subiendo el tono al final de cada pregunta", [0.2, 0, 0, 0, 0.4, 0, 0.1, 0.3]),
    ("susurro", "Acercaos un poco... Esto casi nadie lo sabe. Hay un documento que dice justo lo contrario.",
     "susurrando muy bajito, en tono confidencial, como contando un secreto", [0, 0.1, 0, 0.4, 0.1, 0, 0.2, 0.2]),
    ("exaltacion", "¡Es oficial! ¡España acaba de batir un récord histórico! ¡Noventa millones de turistas! ¡Una auténtica locura!",
     "muy emocionado y eufórico, gritando de alegría", [0.8, 0, 0, 0, 0.6, 0, 0.1, 0.0]),
]


def silencio(sr, s=0.5):
    return np.zeros(int(sr * s), dtype=np.float32)


def qwen(modo, salida):
    from qwen_tts import Qwen3TTSModel
    torch.set_num_threads(os.cpu_count() or 4)
    if modo == "qwen_clon":
        m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map="cpu", dtype=torch.float32)
        prompt = m.create_voice_clone_prompt(ref_audio=REF, ref_text=REF_TXT, x_vector_only_mode=False)
    else:
        m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign", device_map="cpu", dtype=torch.float32)
    partes, sr = [], None
    for reg, txt, estilo, _ in FRASES:
        t = time.time()
        if modo == "qwen_clon":
            wavs, sr = m.generate_voice_clone(text=txt, language="Spanish", voice_clone_prompt=prompt)
        else:
            wavs, sr = m.generate_voice_design(text=txt, language="Spanish", instruct=f"{VOZ}. Habla {estilo}.")
        w = np.asarray(wavs[0], dtype=np.float32)
        sf.write(os.path.join(salida, f"{reg}.wav"), w, sr)
        partes += [w, silencio(sr)]
        print(f"{reg}: {len(w)/sr:.1f}s en {time.time()-t:.0f}s", flush=True)
    sf.write(os.path.join(salida, "todo.wav"), np.concatenate(partes), sr)


def zonos(salida):
    import torchaudio
    from zonos.model import Zonos
    from zonos.conditioning import make_cond_dict
    torch.set_num_threads(os.cpu_count() or 4)
    m = Zonos.from_pretrained("Zyphra/Zonos-v0.1-transformer", device="cpu")
    wav, sr0 = torchaudio.load(REF)
    spk = m.make_speaker_embedding(wav, sr0)
    partes = []
    sr = m.autoencoder.sampling_rate
    for reg, txt, _, emo in FRASES:
        t = time.time()
        torch.manual_seed(7)
        cond = make_cond_dict(text=txt, speaker=spk, language="es", emotion=emo,
                              speaking_rate=15.0 if reg != "exaltacion" else 17.0,
                              pitch_std=30.0 if reg == "susurro" else 90.0)
        codes = m.generate(m.prepare_conditioning(cond))
        w = m.autoencoder.decode(codes).cpu()[0, 0].numpy().astype(np.float32)
        sf.write(os.path.join(salida, f"{reg}.wav"), w, sr)
        partes += [w, silencio(sr)]
        print(f"{reg}: {len(w)/sr:.1f}s en {time.time()-t:.0f}s", flush=True)
    sf.write(os.path.join(salida, "todo.wav"), np.concatenate(partes), sr)


if __name__ == "__main__":
    motor, salida = sys.argv[1], sys.argv[2]
    os.makedirs(salida, exist_ok=True)
    zonos(salida) if motor == "zonos" else qwen(motor, salida)
