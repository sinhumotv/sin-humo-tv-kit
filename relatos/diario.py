#!/usr/bin/env python3
"""Tanda diaria de un canal, SIN Claude (pensado para GitHub Actions).

Uso: python3 diario.py <canal>   (canal = nombre del archivo en canales/, p. ej. relatos)
Variables: GEMINI_KEY, CF_ACCOUNT, CF_TOKEN, BUFFER_KEY, GITHUB_TOKEN. Opcional: N (nº de vídeos).
Registro de temas usados: rama "datos" del repositorio, archivo <canal>.txt
(fecha|hora|título|tipo de gancho|ids de Buffer).
"""
import datetime as dt, json, os, subprocess, sys, tempfile
from zoneinfo import ZoneInfo

AQUI = os.path.dirname(os.path.abspath(__file__))
CANAL = sys.argv[1]
CFG_P = os.path.join(AQUI, "canales", CANAL + ".json")
C = json.load(open(CFG_P, encoding="utf-8"))
HORAS = C["horas"][: int(os.environ.get("N", len(C["horas"])))]
HOY = dt.datetime.now(ZoneInfo("Europe/Madrid"))
BASE = tempfile.mkdtemp(prefix=CANAL + "-")
TOK = os.environ.get("GITHUB_TOKEN", "")
REPO = f"https://x-access-token:{TOK}@github.com/sinhumotv/sin-humo-tv-kit" if TOK else "https://github.com/sinhumotv/sin-humo-tv-kit"
os.environ["GEMINI_API_KEY"] = os.environ.get("GEMINI_KEY", "")
os.environ["AUTO"] = "1"


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
if not os.path.exists(USADOS):
    open(USADOS, "w").close()

# no repetir horas ya publicadas hoy; en la repesca, solo las horas que aún no han pasado
HECHAS = {l.split("|")[1] for l in open(USADOS, encoding="utf-8") if l.startswith(f"{HOY:%Y-%m-%d}|")}
HORAS = [h for h in HORAS if h not in HECHAS]
if os.environ.get("REPESCA"):
    HORAS = [h for h in HORAS if h >= (HOY + dt.timedelta(minutes=15)).strftime("%H:%M")]
if not HORAS:
    print("Nada pendiente hoy en", CANAL)
    sys.exit(0)

print(sh(f'python3 "{AQUI}/guion.py" "{CFG_P}" "{USADOS}" "{BASE}/guiones" {len(HORAS)}', ok=True))
carpetas = sorted(os.listdir(f"{BASE}/guiones")) if os.path.isdir(f"{BASE}/guiones") else []
resumen = []
for hora, sub in zip(HORAS, carpetas):
    D = f"{BASE}/guiones/{sub}"
    H = json.load(open(f"{D}/historia.json", encoding="utf-8"))
    try:
        for paso in ("voz", "imagenes", "montaje"):
            print(sh(f'python3 "{AQUI}/fabricar.py" "{D}" {paso}').strip()[-600:])
        out = sh(f'python3 "{AQUI}/publicar.py" "{D}" {hora} "{CFG_P}"')
        print(out[-800:])
        res = json.loads(out.strip().splitlines()[-1])["buffer"]
        ids = " ".join(f"{k[:2].upper()} {v}" for k, v in res.items())
        resumen.append(f"{hora} · {H['titulo']} · {ids}")
        with open(USADOS, "a", encoding="utf-8") as f:
            f.write(f"{HOY:%Y-%m-%d}|{hora}|{H['titulo']}|{H.get('gancho_tipo', '')}|{ids}\n")
    except Exception as e:
        resumen.append(f"{hora} · {H.get('titulo')} · FALLO: {str(e)[-300:]}")
        print("FALLO", hora, str(e)[-1500:])

sh(f'git add {CANAL}.txt && git -c user.name="{C["nombre"]}" -c user.email="sinhumotv@users.noreply.github.com" '
   f'commit -qm "{CANAL} {HOY:%Y-%m-%d}" && git push -q {REPO} HEAD:datos', cwd=DAT, ok=True)
print("\nRESUMEN\n" + "\n".join(resumen))
if not resumen or all("FALLO" in r for r in resumen):
    sys.exit(1)
