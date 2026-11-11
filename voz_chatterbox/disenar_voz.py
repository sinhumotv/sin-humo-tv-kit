#!/usr/bin/env python3
"""Crea la voz PROPIA de sin humo TV con Qwen3-TTS VoiceDesign (Apache 2.0), solo a partir de una descripción
(sin usar ningún audio de terceros). Genera varias candidatas; la elegida se guarda como referencia_qwen.wav
y Qwen Base la copia siempre igual en todos los vídeos.

Uso: python3 voz_chatterbox/disenar_voz.py <carpeta_salida>
"""
import os, sys, time
import numpy as np
import soundfile as sf
import torch

TEXTO = ("¡Ojo con esto! Hoy el Gobierno ha aprobado una medida que va a tocar el bolsillo de millones de "
         "españoles. Y escuchad bien, porque casi nadie se ha enterado. ¿Y sabéis lo mejor? Que esto acaba de empezar.")
BASE = ("Hombre español de unos 28 años, de Madrid, con acento castellano de España muy natural (la zeta y la erre "
        "doble bien marcadas). Voz de tono medio-grave, cálida y con cuerpo, nada aguda. Youtuber de noticias con mucha "
        "chispa y personalidad: habla rápido y con energía, sonríe al hablar, sube y baja el tono constantemente, "
        "cercano como un amigo que te cuenta algo increíble, espontáneo y nada de locutor.")
VARIANTES = [
    BASE,
    BASE + " Un punto más grave y con un toque pícaro.",
    BASE + " Un punto más joven y enérgico, muy expresivo.",
    BASE + " Algo más pausado en las pausas dramáticas, con intriga.",
]


def main():
    from qwen_tts import Qwen3TTSModel
    salida = sys.argv[1]
    os.makedirs(salida, exist_ok=True)
    torch.set_num_threads(os.cpu_count() or 4)
    m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign", device_map="cpu", dtype=torch.float32)
    for i, desc in enumerate(VARIANTES, 1):
        torch.manual_seed(100 + i)
        t = time.time()
        wavs, sr = m.generate_voice_design(text=TEXTO, language="Spanish", instruct=desc)
        w = np.asarray(wavs[0], dtype=np.float32)
        sf.write(os.path.join(salida, f"candidata_{i}.wav"), w, sr)
        print(f"candidata {i}: {len(w)/sr:.1f}s en {time.time()-t:.0f}s", flush=True)
    open(os.path.join(salida, "descripciones.txt"), "w").write("\n\n".join(VARIANTES) + "\n\nTEXTO: " + TEXTO)


if __name__ == "__main__":
    main()
