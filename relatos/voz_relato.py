#!/usr/bin/env python3
"""Voz GRATIS con Gemini (voz Puck por defecto) para sin humo TV.

Uso: python3 voz_gemini.py <carpeta> [--tono normal|grave] [--voz Puck]
Lee <carpeta>/voz.txt (el texto hablado, escenas separadas por una línea en blanco)
y deja <carpeta>/voz.mp3, listo para audio.py.

La clave va en la variable GEMINI_API_KEY (o en ~/.gemini_key). Nunca la subas al kit.
- Textos largos se parten en trozos de <= 1.800 caracteres por cambios de párrafo
  y se unen con 0,8 s de silencio (pausa clara para el corte por escenas).
- Prueba varios modelos por si uno no responde o agota su cuota gratuita.
- Sale con código 2 y el motivo si ninguno funciona (para pasar al plan B).
"""
import base64, json, os, subprocess, sys, time, urllib.request, urllib.error, ssl, tempfile

MODELOS = ["gemini-3.8-flash-tts", "gemini-3.1-flash-tts-preview",
           "gemini-2.5-flash-preview-tts", "gemini-3.8-flash-lite-tts"]
if os.environ.get("TTS_MODELOS"):  # p. ej. los largos empiezan por otro modelo para no gastar el cupo de los cortos
    MODELOS = os.environ["TTS_MODELOS"].split(",")
MAX = int(os.environ.get("TTS_MAX", 1800))  # menos peticiones: el plan gratis da 10 al día por modelo
OBJ_CPS = 12.5
ESTILO = {
    "normal": ("Presentador joven de noticias para redes sociales, acento castellano de España (la z y la c como en "
               "Madrid), cercano, enérgico y con intriga en las preguntas, ritmo ágil. Pausa corta y clara entre párrafos."),
    "relato": ("Lee en español de España, con acento castellano peninsular de Madrid: la z y la c se pronuncian como en España (cielo, cerveza, nación con el sonido de la z española) y la s es la de España. Nada de acento latinoamericano ni neutro. "
               "Narrador de leyendas y mitología, voz grave, cálida y profunda, acento castellano de España (la z y la c como en Madrid, nada de acento latino), "
               "tono épico e intrigante, como quien cuenta una historia antigua al lado del fuego; ritmo pausado, con emoción contenida y pequeñas pausas dramáticas. Pausa corta y clara entre párrafos."),
    "grave": ("Presentador de noticias, acento castellano de España (la z y la c como en Madrid), tono serio, sobrio y "
              "respetuoso, ritmo pausado sin pausas largas. Pausa corta y clara entre párrafos."),
}


def clave():
    k = os.environ.get("GEMINI_API_KEY", "").strip()
    if not k and os.path.exists(os.path.expanduser("~/.gemini_key")):
        k = open(os.path.expanduser("~/.gemini_key")).read().strip()
    # Drive devuelve el texto del documento con "\\_" en vez de "_" y espacios al final: se limpian
    k = "".join(k.replace("\\", "").split())
    if not k:
        sys.exit("Falta la clave de Gemini (GEMINI_API_KEY)")
    return k


def ctx():
    for ca in ("/root/.ccr/ca-bundle.crt", os.environ.get("SSL_CERT_FILE", "")):
        if ca and os.path.exists(ca):
            return ssl.create_default_context(cafile=ca)
    return ssl.create_default_context()


def trozos(texto):
    pars = [p.strip() for p in texto.strip().split("\n\n") if p.strip()]
    out, cur = [], ""
    for p in pars:
        if cur and len(cur) + 2 + len(p) > MAX:
            out.append(cur)
            cur = p
        else:
            cur = f"{cur}\n\n{p}" if cur else p
    if cur:
        out.append(cur)
    return out


def generar(texto, voz, tono, k):
    body = {"contents": [{"parts": [{"text": "[Notas de dirección: " + ESTILO[tono]
                                             + " Lee solo el texto de TRANSCRIPCIÓN, sin añadir nada.]\nTRANSCRIPCIÓN:\n" + texto}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"languageCode": "es-ES",  # español de España
                                                  "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voz}}}}}
    errores = []
    for m in list(MODELOS):
        for intento in range(3):
            req = urllib.request.Request(
                f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent",
                data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": k})
            try:
                d = json.load(urllib.request.urlopen(req, context=ctx(), timeout=300))
                parte = d["candidates"][0]["content"]["parts"][0]["inlineData"]
                MODELOS.remove(m)
                MODELOS.insert(0, m)  # el resto de trozos, con el mismo modelo (misma voz)
                return base64.b64decode(parte["data"]), parte.get("mimeType", ""), m
            except urllib.error.HTTPError as e:
                msg = e.read()[:1500].decode(errors="ignore")
                errores.append(f"{m}: {e.code} {msg[:120]}")
                if "PerDay" in msg or "per day" in msg.lower():
                    break  # cupo diario de este modelo agotado (10 al día gratis): al siguiente sin esperar
                if e.code in (429, 500, 502, 503, 504) and intento < 2:
                    time.sleep(20 * (intento + 1))
                    continue
                break  # 400/403/404 o cuota agotada: siguiente modelo
            except Exception as e:  # sin audio en la respuesta, red...
                errores.append(f"{m}: {type(e).__name__} {str(e)[:120]}")
                if intento < 1:
                    time.sleep(5)
                    continue
                break
    print("ERROR Gemini:\n  " + "\n  ".join(errores[-6:]), file=sys.stderr)
    return None


def plan_c_piper(texto, tmp):
    """Si Gemini no responde: voz Piper es_ES sharvard (masculina, España, CC BY 3.0; hay que citarla)."""
    base = os.path.expanduser("~/.piper")
    os.makedirs(base, exist_ok=True)
    mod = os.path.join(base, "es_ES-sharvard-medium.onnx")
    url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx"
    subprocess.run("python3 -c 'import piper' 2>/dev/null || pip install -q --break-system-packages piper-tts",
                   shell=True)
    for ext in ("", ".json"):
        if not os.path.exists(mod + ext):
            subprocess.run(f'curl -sSL -o "{mod + ext}" "{url + ext}"', shell=True, check=True)
    partes = []
    for i, p in enumerate(x.strip() for x in texto.strip().split("\n\n") if x.strip()):
        w = os.path.join(tmp, f"c{i}.wav")
        subprocess.run(["python3", "-m", "piper", "-m", mod, "-s", "0", "--length-scale", "0.9", "-f", w],
                       input=p, text=True, check=True, capture_output=True)
        w2 = os.path.join(tmp, f"d{i}.wav")
        subprocess.run(f'ffmpeg -y -v error -i "{w}" -ac 1 -ar 44100 "{w2}"', shell=True, check=True)
        partes.append(w2)
    return partes


def a_wav(datos, mime, destino):
    src = destino + ".bin"
    open(src, "wb").write(datos)
    if datos[:4] == b"RIFF" or "wav" in mime:
        entrada = f'-i "{src}"'
    else:  # PCM 16 bits mono 24 kHz
        entrada = f'-f s16le -ar 24000 -ac 1 -i "{src}"'
    subprocess.run(f'ffmpeg -y -v error {entrada} -ac 1 -ar 44100 "{destino}"', shell=True, check=True)
    os.remove(src)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    D = sys.argv[1]
    a = sys.argv[2:]
    tono = a[a.index("--tono") + 1] if "--tono" in a else "normal"
    voz = a[a.index("--voz") + 1] if "--voz" in a else "Puck"
    texto = open(os.path.join(D, "voz.txt"), encoding="utf-8").read()
    k = clave()
    tmp = tempfile.mkdtemp()
    partes, usados = [], []
    for i, t in enumerate(trozos(texto)):
        r = generar(t, voz, tono, k)
        if r is None:  # plan C para todo el texto (no mezclar voces)
            partes, usados = plan_c_piper(texto, tmp), ["PIPER sharvard (CC BY 3.0: citar en la descripción)"]
            voz = "Piper sharvard"
            print("PLAN C: Gemini no responde; voz Piper es_ES sharvard. Pon en la descripción: "
                  "\"Voz: Piper es_ES sharvard (CC BY 3.0)\"")
            break
        datos, mime, m = r
        w = os.path.join(tmp, f"p{i}.wav")
        a_wav(datos, mime, w)
        # quita silencio inicial y final de cada trozo
        w2 = os.path.join(tmp, f"q{i}.wav")
        subprocess.run(f'ffmpeg -y -v error -i "{w}" -af "silenceremove=start_periods=1:start_threshold=-45dB,'
                       f'areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse" "{w2}"',
                       shell=True, check=True)
        # ritmo parecido al de los vídeos con ElevenLabs: unos 14,5 caracteres por segundo de habla
        # (Gemini a veces se ralentiza en trozos largos); se ajusta cada trozo sin cambiar el tono
        dur = float(subprocess.run(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{w2}"',
                                   shell=True, capture_output=True, text=True).stdout)
        cps = len("".join(t.split())) / dur
        f = min(1.3, max(1.0, OBJ_CPS / cps))
        if f > 1.02:
            w3 = os.path.join(tmp, f"r{i}.wav")
            subprocess.run(f'ffmpeg -y -v error -i "{w2}" -af atempo={f:.3f} "{w3}"', shell=True, check=True)
            w2 = w3
        partes.append(w2)
        usados.append(m)
        print(f"trozo {i+1}: {len(t)} caracteres · {m} · {cps:.1f} car/s · atempo {f:.2f}")
        if i < len(trozos(texto)) - 1:
            time.sleep(8)  # respeta el límite por minuto del plan gratis
    sil = os.path.join(tmp, "sil.wav")
    subprocess.run(f'ffmpeg -y -v error -f lavfi -i anullsrc=r=44100:cl=mono -t 0.8 "{sil}"', shell=True, check=True)
    lista = os.path.join(tmp, "lista.txt")
    with open(lista, "w") as f:
        for i, p in enumerate(partes):
            if i:
                f.write(f"file '{sil}'\n")
            f.write(f"file '{p}'\n")
    out = os.path.join(D, "voz.mp3")
    subprocess.run(f'ffmpeg -y -v error -f concat -safe 0 -i "{lista}" -ac 1 -ar 44100 -b:a 192k "{out}"',
                   shell=True, check=True)
    dur = subprocess.run(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{out}"',
                         shell=True, capture_output=True, text=True).stdout.strip()
    print(f"OK voz.mp3 · {float(dur):.1f} s · voz {voz} · modelos: {', '.join(sorted(set(usados)))} · 0 créditos")


if __name__ == "__main__":
    main()
