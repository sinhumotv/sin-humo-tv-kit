#!/usr/bin/env python3
"""Crea voces PROPIAS con Qwen3-TTS VoiceDesign (Apache 2.0), solo a partir de una descripción (sin audio de terceros).
La elegida se guarda en voces/<canal>.wav (+ .txt con lo que dice) y Qwen Base la copia siempre igual en los vídeos.

Uso: python3 voz_chatterbox/disenar_voz.py <grupo> <carpeta_salida>     (grupos en voz_chatterbox/voces_disenos.json)
Las descripciones van en inglés: el modelo las sigue mucho mejor (en español salían voces agudas o femeninas).
"""
import json, os, sys, time
import numpy as np
import soundfile as sf
import torch

AQUI = os.path.dirname(os.path.abspath(__file__))


def main():
    from qwen_tts import Qwen3TTSModel
    grupo, salida = sys.argv[1], sys.argv[2]
    os.makedirs(salida, exist_ok=True)
    G = json.load(open(os.path.join(AQUI, "voces_disenos.json"), encoding="utf-8"))[grupo]
    torch.set_num_threads(os.cpu_count() or 4)
    m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign", device_map="cpu", dtype=torch.float32)
    n = G.get("candidatas", 1)
    for v in G["voces"]:
        texto = v.get("texto") or G["texto"]
        for k in range(n):
            torch.manual_seed(100 + 31 * k)
            t = time.time()
            wavs, sr = m.generate_voice_design(text=texto, language="Spanish", instruct=v["descripcion"])
            w = np.asarray(wavs[0], dtype=np.float32)
            nombre = f"{v['id']}_{k + 1}" if n > 1 else v["id"]
            sf.write(os.path.join(salida, f"{nombre}.wav"), w, sr)
            open(os.path.join(salida, f"{nombre}.txt"), "w", encoding="utf-8").write(texto)
            print(f"{nombre}: {len(w)/sr:.1f}s en {time.time()-t:.0f}s", flush=True)


if __name__ == "__main__":
    main()
