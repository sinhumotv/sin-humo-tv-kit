"""Llamadas a Gemini (gratis) con reintentos y varios modelos. Clave: GEMINI_KEY o GEMINI_API_KEY."""
import base64, json, os, time, urllib.error, urllib.request

MODELOS = ["gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.8-flash", "gemini-2.5-flash", "gemini-flash-lite-latest"]


def clave():
    k = os.environ.get("GEMINI_KEY") or os.environ.get("GEMINI_API_KEY") or ""
    if not k and os.path.exists(os.path.expanduser("~/.gemini_key")):
        k = open(os.path.expanduser("~/.gemini_key")).read()
    return "".join(k.replace("\\", "").split())


def _ronda(cuerpo):
    ultimo = None
    for m in MODELOS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"
        for intento in range(2):
            try:
                req = urllib.request.Request(url, json.dumps(cuerpo).encode(),
                                             {"Content-Type": "application/json", "x-goog-api-key": clave()})
                j = json.load(urllib.request.urlopen(req, timeout=240))
                txt = "".join(p.get("text", "") for p in j["candidates"][0]["content"]["parts"])
                return txt, m
            except urllib.error.HTTPError as e:
                ultimo = f"{m}: HTTP {e.code} {e.read()[:200]!r}"
                if e.code in (429, 500, 503):
                    time.sleep(10)
                    continue
                break
            except Exception as e:  # sin respuesta (saturado): al siguiente modelo sin repetir
                ultimo = f"{m}: {e}"
                break
    return None, ultimo


def pedir(prompt, temp=0.9, json_out=True, imagenes=None, max_tokens=32000):
    """Devuelve (respuesta, modelo). imagenes: lista de bytes JPEG que acompañan al texto."""
    partes = [{"text": prompt}]
    for b in imagenes or []:
        partes.append({"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(b).decode()}})
    cfg = {"temperature": temp, "maxOutputTokens": max_tokens}
    if json_out:
        cfg["responseMimeType"] = "application/json"
    cuerpo = {"contents": [{"role": "user", "parts": partes}], "generationConfig": cfg}
    ultimo = None
    for ronda in range(3):  # si Gemini está saturado, espera y vuelve a probar todos los modelos
        if ronda:
            print(f"Gemini saturado ({str(ultimo)[:120]}); reintento en {120 * ronda} s", flush=True)
            time.sleep(120 * ronda)
        txt, info = _ronda(cuerpo)
        if txt is not None:
            if not json_out:
                return txt, info
            try:
                return json.loads(txt), info
            except Exception:
                t = txt[txt.find("{"): txt.rfind("}") + 1]
                try:
                    return json.loads(t), info
                except Exception:
                    ultimo = f"{info}: JSON no válido"
                    continue
        ultimo = info
    raise SystemExit("Gemini no responde: " + str(ultimo))
