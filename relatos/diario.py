#!/usr/bin/env python3
"""Tanda diaria de un canal, SIN Claude (pensado para GitHub Actions).

Uso: python3 diario.py <canal>   (canal = nombre del archivo en canales/, p. ej. relatos)
Variables: GEMINI_KEY, CF_ACCOUNT, CF_TOKEN, BUFFER_KEY, GITHUB_TOKEN. Opcional: N (nº de vídeos).
Registro de temas usados: rama "datos" del repositorio, archivo <canal>.txt
(fecha|hora|título|tipo de gancho|ids de Buffer).
"""
import datetime as dt, json, os, subprocess, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import datos
from zoneinfo import ZoneInfo

AQUI = os.path.dirname(os.path.abspath(__file__))
CANAL = sys.argv[1]
CFG_P = os.path.join(AQUI, "canales", CANAL + ".json")
C = json.load(open(CFG_P, encoding="utf-8"))
TODAS = C["horas"]
HORAS = TODAS[: int(os.environ.get("N", len(TODAS)))]
HOY = dt.datetime.now(ZoneInfo("Europe/Madrid"))
BASE = tempfile.mkdtemp(prefix=CANAL + "-")
TOK = os.environ.get("GITHUB_TOKEN", "")
REPO = f"https://x-access-token:{TOK}@github.com/sinhumotv/sin-humo-tv-kit" if TOK else "https://github.com/sinhumotv/sin-humo-tv-kit"
os.environ["GEMINI_API_KEY"] = os.environ.get("GEMINI_KEY", "")
os.environ["AUTO"] = "1"


def variar(hora, canal, dia, minutos=40):
    """Hora con una variación de hasta ±minutos, distinta cada día y canal (y siempre la misma para ese día)."""
    import hashlib
    h, m = map(int, hora.split(":"))
    v = int(hashlib.sha256(f"{canal}|{dia}|{hora}".encode()).hexdigest(), 16) % (2 * minutos + 1) - minutos
    t = max(6 * 60 + 30, min(23 * 60 + 15, h * 60 + m + v))
    return f"{t // 60:02d}:{t % 60:02d}"


def sh(c, cwd=None, ok=False):
    r = subprocess.run(c, shell=True, capture_output=True, text=True, cwd=cwd)
    salida = (r.stdout + r.stderr).replace(TOK or "~~", "***")
    if r.returncode and not ok:
        raise RuntimeError(salida[-1500:])
    return salida


# registro (rama datos)
DAT = os.path.join(BASE, "datos")
sh(f"git clone -q --depth 1 --branch datos {REPO} {DAT} || (mkdir -p {DAT} && cd {DAT} && git init -q && git checkout -q --orphan datos)", ok=True)
USADOS = os.path.join(DAT, CANAL + ".txt")
CLIPS_USADOS = os.path.join(DAT, f"clips_{CANAL}.txt")   # clips de Pixabay ya usados (no se repiten entre vídeos)
open(CLIPS_USADOS, "a").close()
if not os.path.exists(USADOS):
    open(USADOS, "w").close()

# no repetir horas ya publicadas hoy; en la repesca, solo las horas que aún no han pasado
HECHAS = set() if os.environ.get("PROBAR") else {l.split("|")[1] for l in open(USADOS, encoding="utf-8") if l.startswith(f"{HOY:%Y-%m-%d}|")}
HORAS = [h for h in HORAS if h not in HECHAS]
if os.environ.get("REPESCA"):
    HORAS = [h for h in HORAS if h >= (HOY + dt.timedelta(minutes=15)).strftime("%H:%M")]
if not HORAS:
    print("Nada pendiente hoy en", CANAL)
    sys.exit(0)

# PRUEBA A/B: cada día, unos cuantos cortos (2 de 5 por defecto) se hacen SOLO con vídeo real de internet
# (Pixabay) en vez de imágenes de IA de Cloudflare, para comparar visitas. Las horas elegidas rotan cada día.
N_REAL = int(C.get("prueba_real", 2))
_o = HOY.toordinal()
REALES = {TODAS[(_o + k * 2) % len(TODAS)] for k in range(N_REAL)} if TODAS else set()


PROBAR = os.environ.get("PROBAR")   # 1 = solo fabricar (con vídeo real), sin publicar ni registrar


def modo_de(hora):
    if PROBAR:
        return os.environ.get("MODO_PRUEBA", "real")
    return "real" if hora in REALES else "ia"


print(sh(f'python3 "{AQUI}/guion.py" "{CFG_P}" "{USADOS}" "{BASE}/guiones" {len(HORAS)}', ok=True))
carpetas = sorted(os.listdir(f"{BASE}/guiones")) if os.path.isdir(f"{BASE}/guiones") else []
resumen = []
for hora, sub in zip(HORAS, carpetas):
    D = f"{BASE}/guiones/{sub}"
    H = json.load(open(f"{D}/historia.json", encoding="utf-8"))
    try:
        for paso in ("voz", "imagenes", "montaje"):
            print(sh(f'MODO_IMG={modo_de(hora)} CANAL_JSON="{CFG_P}" CLIPS_USADOS="{CLIPS_USADOS}" python3 "{AQUI}/fabricar.py" "{D}" {paso}').strip()[-600:])
        modo = open(f"{D}/modo_imagenes.txt").read().strip() if os.path.exists(f"{D}/modo_imagenes.txt") else "ia"
        ids_clips = [str(v["clip_id"]) for v in json.load(open(f"{D}/historia.json", encoding="utf-8")).get("clips_info", {}).values()]
        with open(CLIPS_USADOS, "a") as f:
            f.write("".join(x + "\n" for x in ids_clips))
        if PROBAR:
            os.makedirs("prueba", exist_ok=True)
            import shutil
            shutil.copy(f"{D}/video_final.mp4", f"prueba/{CANAL}-{sub}.mp4")
            shutil.copy(f"{D}/hoja.jpg", f"prueba/{CANAL}-{sub}-hoja.jpg")
            resumen.append(f"{hora} · {H['titulo']} · [{modo}] · PRUEBA (sin publicar)")
            continue
        hora_real = variar(hora, CANAL, f"{HOY:%Y-%m-%d}")
        out = sh(f'RAMA_HORA={hora} python3 "{AQUI}/publicar.py" "{D}" {hora_real} "{CFG_P}"')
        print(out[-800:])
        res = json.loads(out.strip().splitlines()[-1])["buffer"]
        ids = " ".join(f"{k[:2].upper()} {v}" for k, v in res.items())
        resumen.append(f"{hora} · {H['titulo']} · [{modo}] · {ids}")
        linea = f"{HOY:%Y-%m-%d}|{hora}|{H['titulo']}|{H.get('gancho_tipo', '')}|{ids}|img={modo}|{hora_real}"
        with open(USADOS, "a", encoding="utf-8") as f:
            f.write(linea + "\n")
        # se guarda en cuanto se publica (con reintentos), para que la repesca y los temas nunca lo pierdan
        datos.anadir(REPO, f"{CANAL}.txt", [linea], C["nombre"], f"{CANAL} {HOY:%Y-%m-%d} {hora}")
        if ids_clips:
            datos.anadir(REPO, f"clips_{CANAL}.txt", ids_clips, C["nombre"], f"clips {CANAL} {HOY:%Y-%m-%d} {hora}")
    except Exception as e:
        resumen.append(f"{hora} · {H.get('titulo')} · FALLO: {str(e)[-300:]}")
        print("FALLO", hora, str(e)[-1500:])

print("\nRESUMEN\n" + "\n".join(resumen))
if not resumen or all("FALLO" in r for r in resumen):
    sys.exit(1)
