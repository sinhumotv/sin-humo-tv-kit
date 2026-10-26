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


def generar(texto, voz, tono, k, notas=True, solo=None):
    # notas=False: solo el texto (cuando un modelo ha leído en voz alta las notas de dirección)
    # solo=<modelo>: SOLO ese modelo (vídeos largos: todos los trozos con el mismo modelo, misma voz)
    prompt = ("[Notas de dirección: " + ESTILO[tono] + " Lee solo el texto de TRANSCRIPCIÓN, sin añadir nada.]\nTRANSCRIPCIÓN:\n"
              + texto) if notas else texto
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"languageCode": "es-ES",  # español de España
                                                  "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voz}}}}}
    errores = []
    for m in ([solo] if solo else list(MODELOS)):
        for intento in range(3):
            req = urllib.request.Request(
                f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent",
                data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": k})
            try:
                d = json.load(urllib.request.urlopen(req, context=ctx(), timeout=300))
                parte = d["candidates"][0]["content"]["parts"][0]["inlineData"]
                if m in MODELOS:
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
    def sin_bordes(w, w2):
        subprocess.run(f'ffmpeg -y -v error -i "{w}" -af "silenceremove=start_periods=1:start_threshold=-45dB,'
                       f'areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse" "{w2}"',
                       shell=True, check=True)
        return float(subprocess.run(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{w2}"',
                                    shell=True, capture_output=True, text=True).stdout)

    for i, t in enumerate(trozos(texto)):
        # CONTROL: si el audio dura mucho más de lo que da el texto (menos de 9 caracteres por segundo), el modelo ha
        # leído también las notas de dirección o se ha ido por las ramas: se repite con otro modelo y, si no, sin notas
        r = None
        for intento in range(3):
            r = generar(t, voz, tono, k, notas=intento < 2)
            if r is None:
                break
            wtest = os.path.join(tmp, f"t{i}_{intento}.wav")
            a_wav(r[0], r[1], wtest)
            d_ = sin_bordes(wtest, wtest.replace(".wav", "_c.wav"))
            cps_ = len("".join(t.split())) / max(d_, 0.1)
            if cps_ >= 9.0:
                break
            print(f"trozo {i+1}: audio sospechoso ({cps_:.1f} car/s, {d_:.0f} s): lo repito", flush=True)
            if r[2] in MODELOS:   # el siguiente intento, con otro modelo
                MODELOS.remove(r[2])
                MODELOS.append(r[2])
            r = None if intento == 2 else r
        if r is None and intento == 2:
            sys.exit("FALLO: la voz no sale bien (lee las notas o va demasiado lenta) tras 3 intentos")
        res = "".join(os.environ.get("GEMINI_KEY_RESERVA", "").split())
        if r is None and res and k != res:   # clave del canal sin cuota hoy: misma voz con la clave de reserva
            print("Voz: sigo con la clave de reserva de Gemini")
            k = res
            os.environ["GEMINI_KEY"] = os.environ["GEMINI_API_KEY"] = res
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
        f = min(1.08, max(1.0, OBJ_CPS / cps))   # como mucho un 8 % más rápido: que nunca suene acelerada
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


def rasgos(w):
    """Tono medio (Hz) y brillo (centroide espectral, Hz) de una voz: para comprobar que todos los trozos suenan igual."""
    import numpy as np
    raw = subprocess.run(f'ffmpeg -v error -i "{w}" -ac 1 -ar 16000 -f s16le -', shell=True, capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(float) / 32768
    sr, f0s = 16000, []
    for i in range(0, len(x) - 640, 1600):
        s = x[i:i + 640] - x[i:i + 640].mean()
        if np.sqrt((s ** 2).mean()) < 0.02:
            continue
        c = np.correlate(s, s, "full")[639:]
        k = 53 + int(np.argmax(c[53:228]))
        if c[k] > 0.3 * c[0]:
            f0s.append(sr / k)
    sp = np.abs(np.fft.rfft(x[:sr * 60]))
    fr = np.fft.rfftfreq(len(x[:sr * 60]), 1 / sr)
    return (float(np.median(f0s)) if f0s else 0.0), float((sp * fr).sum() / max(sp.sum(), 1e-9))


def main_largo():
    """VÍDEOS LARGOS: la MISMA voz, el MISMO modelo, la MISMA velocidad y el MISMO volumen de principio a fin.
    - El modelo del primer trozo es el de todo el vídeo (nunca se cambia a otro a mitad: cada modelo suena distinto).
    - Si ese modelo se queda sin cupo, se sigue con la clave de reserva y ESE MISMO modelo; si tampoco, se guarda lo
      hecho y sale con código 3 (la próxima ejecución continúa). Nunca Piper ni «sin notas» a mitad de vídeo.
    - Cada trozo se compara con el primero (tono y timbre); si se aparta, se repite (hasta 3 veces, se queda el más
      parecido).
    - Todos los trozos se dejan exactamente a la misma velocidad (OBJ_CPS) y al mismo volumen (loudnorm)."""
    D = sys.argv[1]
    a = sys.argv[2:]
    tono = a[a.index("--tono") + 1] if "--tono" in a else "relato"
    voz = a[a.index("--voz") + 1] if "--voz" in a else "Algenib"
    texto = open(os.path.join(D, "voz.txt"), encoding="utf-8").read()
    k = clave()
    res = "".join(os.environ.get("GEMINI_KEY_RESERVA", "").split())
    tmp = tempfile.mkdtemp()
    T = os.path.join(D, "voz_trozos")   # trozos ya hechos (se guardan en el proyecto para continuar otro día)
    os.makedirs(T, exist_ok=True)
    meta_p = os.path.join(T, "meta.json")
    meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
    piezas = trozos(texto)
    if meta.get("texto") != texto or meta.get("voz") != voz or meta.get("tono") != tono:
        meta = {"texto": texto, "voz": voz, "tono": tono, "modelo": None, "ref": None, "hechos": {}}
        # MISMA VOZ EN TODOS LOS VÍDEOS DEL CANAL (regla del usuario): modelo, tono, timbre y velocidad de referencia
        # del canal, fijados con el primer largo y guardados en la rama datos (VOZ_REF = ruta del archivo)
        rp = os.environ.get("VOZ_REF", "")
        if rp and os.path.exists(rp):
            lineas = [l for l in open(rp, encoding="utf-8").read().splitlines() if l.strip().startswith("{")]
            if lineas:
                R = json.loads(lineas[-1])
                if R.get("voz") == voz:
                    meta.update(modelo=R["modelo"], ref=[R["f0"], R["cen"]], cps_ref=R["cps"], ref_canal=True)
                    print(f"voz de referencia del canal: {R['modelo']} · tono {R['f0']:.0f} Hz · {R['cps']:.1f} car/s")
    def guardar_meta():
        json.dump(meta, open(meta_p, "w"), ensure_ascii=False)

    def limpio(datos, mime, nombre):
        w = os.path.join(tmp, nombre + ".wav")
        a_wav(datos, mime, w)
        w2 = os.path.join(tmp, nombre + "_c.wav")
        d = sin_bordes_(w, w2)
        return w2, d

    for i, t in enumerate(piezas):
        if str(i) in meta["hechos"] and os.path.exists(os.path.join(T, f"{i:02d}.flac")):
            continue
        n_car = len("".join(t.split()))
        mejor = None   # (distancia, wav)
        for intento in range(3):
            r = None
            for kk in [k] + ([res] if res and res != k else []):
                r = generar(t, voz, tono, kk, solo=meta["modelo"])
                if r:
                    k = kk
                    break
            if r is None:
                guardar_meta()
                print(f"VOZ PENDIENTE: el modelo {meta['modelo']} no responde hoy (trozo {i + 1} de {len(piezas)}); "
                      "se continúa en la próxima ejecución con la misma voz")
                sys.exit(3)
            if meta["modelo"] is None:
                meta["modelo"] = r[2]
            w, d = limpio(r[0], r[1], f"t{i}_{intento}")
            cps = n_car / max(d, 0.1)
            if cps < 9.0:   # ha leído las notas o se ha ido por las ramas: se repite (mismo modelo)
                print(f"trozo {i + 1}: audio sospechoso ({cps:.1f} car/s): lo repito", flush=True)
                time.sleep(8)
                continue
            f0, cen = rasgos(w)
            if meta["ref"] is None:
                meta["ref"] = [f0, cen]
            rf0, rcen = meta["ref"]
            dist = abs(f0 - rf0) / max(rf0, 1) + 0.5 * abs(cen - rcen) / max(rcen, 1)
            print(f"trozo {i + 1}: {meta['modelo']} · {cps:.1f} car/s · tono {f0:.0f} Hz (ref {rf0:.0f}) · "
                  f"timbre {cen:.0f} Hz (ref {rcen:.0f}) · diferencia {dist:.2f}", flush=True)
            if mejor is None or dist < mejor[0]:
                mejor = (dist, w, cps)
            if dist <= 0.08:
                break
            time.sleep(8)
        if mejor is None:
            sys.exit("FALLO: la voz no sale bien tras 3 intentos")
        _, w, cps = mejor
        # misma velocidad en TODOS los trozos (sin cambiar el tono) y mismo volumen: la del primer trozo (si es lento,
        # un poco más ágil), y todos los demás se igualan a ella
        if not meta.get("cps_ref"):
            meta["cps_ref"] = min(max(cps, 11.5), 14.0)
        f = min(1.10, max(0.90, meta["cps_ref"] / cps))
        out = os.path.join(T, f"{i:02d}.flac")
        subprocess.run(f'ffmpeg -y -v error -i "{w}" -af "atempo={f:.4f},loudnorm=I=-17:TP=-2:LRA=7" -ar 44100 -ac 1 '
                       f'"{out}"', shell=True, check=True)
        meta["hechos"][str(i)] = {"atempo": round(f, 3)}
        guardar_meta()
        if i < len(piezas) - 1:
            time.sleep(8)   # límite por minuto del plan gratis
    sil = os.path.join(tmp, "sil.wav")
    subprocess.run(f'ffmpeg -y -v error -f lavfi -i anullsrc=r=44100:cl=mono -t 0.8 -c:a pcm_s16le "{sil}"', shell=True, check=True)
    lista = os.path.join(tmp, "lista.txt")
    with open(lista, "w") as fl:
        for i in range(len(piezas)):
            wv = os.path.join(tmp, f"u{i:02d}.wav")
            subprocess.run(f'ffmpeg -y -v error -i "{os.path.join(T, f"{i:02d}.flac")}" -ac 1 -ar 44100 -c:a pcm_s16le "{wv}"',
                           shell=True, check=True)
            if i:
                fl.write(f"file '{sil}'\n")
            fl.write(f"file '{wv}'\n")
    out = os.path.join(D, "voz.mp3")
    subprocess.run(f'ffmpeg -y -v error -f concat -safe 0 -i "{lista}" -ac 1 -ar 44100 -b:a 192k "{out}"',
                   shell=True, check=True)
    dur = subprocess.run(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{out}"',
                         shell=True, capture_output=True, text=True).stdout.strip()
    if os.environ.get("VOZ_REF") and not meta.get("ref_canal"):
        json.dump({"voz": voz, "modelo": meta["modelo"], "f0": meta["ref"][0], "cen": meta["ref"][1],
                   "cps": meta["cps_ref"]}, open(os.path.join(D, "voz_ref_nueva.json"), "w"))
    print(f"OK voz.mp3 · {float(dur):.1f} s · voz {voz} · UN SOLO modelo: {meta['modelo']} · {len(piezas)} trozos "
          f"igualados en velocidad y volumen · 0 créditos")


def sin_bordes_(w, w2):
    subprocess.run(f'ffmpeg -y -v error -i "{w}" -af "silenceremove=start_periods=1:start_threshold=-45dB,'
                   f'areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse" "{w2}"',
                   shell=True, check=True)
    return float(subprocess.run(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{w2}"',
                                shell=True, capture_output=True, text=True).stdout)


if __name__ == "__main__":
    main_largo() if os.environ.get("VOZ_ESTRICTA") else main()
