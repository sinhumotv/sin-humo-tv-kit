#!/usr/bin/env python3
"""Sube el vídeo a GitHub (rama rel-HHMM) y lo programa en Buffer (cuenta de Relatos en Español).

Uso: python3 publicar.py <carpeta> <HH:MM>
Necesita ~/.buffer_relatos (clave de la API de Buffer de Relatos) y permiso de escritura en
sinhumotv/sin-humo-tv-kit. Lee de historia.json: titulo_youtube, descripcion, pregunta, hashtags, titulo_tiktok.
Imprime los ids de Buffer o el error de cada red.
"""
import datetime as dt, json, os, subprocess, sys, tempfile, urllib.request
from zoneinfo import ZoneInfo

D = os.path.abspath(sys.argv[1])
HORA = sys.argv[2]
H = json.load(open(f"{D}/historia.json", encoding="utf-8"))
CFG = json.load(open(sys.argv[3], encoding="utf-8")) if len(sys.argv) > 3 else \
    json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "canales", "relatos.json"), encoding="utf-8"))
CANALES = CFG["buffer_canales"]
KEY = os.environ.get("BUFFER_KEY") or open(os.path.expanduser("~/.buffer_relatos")).read().strip()
TOK = os.environ.get("GITHUB_TOKEN")
REPO = (f"https://x-access-token:{TOK}@github.com/sinhumotv/sin-humo-tv-kit" if TOK
        else "https://github.com/sinhumotv/sin-humo-tv-kit")
RAMA = ("rel" if CFG["id"] == "relatos" else CFG["id"]) + "-" + HORA.replace(":", "")


def sh(c, cwd=None):
    return subprocess.run(c, shell=True, capture_output=True, text=True, cwd=cwd)


# ---------- 1. alojar el vídeo en GitHub ----------
video = f"{D}/video_final.mp4"
tam = os.path.getsize(video)
tmp = tempfile.mkdtemp()
sh(f'git init -q && git checkout -q --orphan {RAMA} && cp "{video}" video.mp4 && git add video.mp4 && '
   f'git -c user.name="{CFG['nombre']}" -c user.email="sinhumotv@users.noreply.github.com" commit -qm "{RAMA}"', tmp)
r = sh(f"git push -q --force {REPO} {RAMA}", tmp)
url = f"https://raw.githubusercontent.com/sinhumotv/sin-humo-tv-kit/{RAMA}/video.mp4"
chk = sh(f'curl -sI "{url}"').stdout
if " 200" not in chk.splitlines()[0] or f"content-length: {tam}" not in chk.lower():
    print("FALLO al subir el vídeo a GitHub:", r.stderr[-400:].replace(TOK or "~", "***"), chk[:200])
    sys.exit(1)
print("vídeo alojado:", url)


# ---------- 2. Buffer ----------
def gql(query, variables):
    req = urllib.request.Request("https://api.buffer.com", json.dumps({"query": query, "variables": variables}).encode(),
                                 {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=60))


ahora = dt.datetime.now(ZoneInfo("Europe/Madrid"))
hh, mm = map(int, HORA.split(":"))
cuando = ahora.replace(hour=hh, minute=mm, second=0, microsecond=0)
modo = "customScheduled" if cuando - ahora > dt.timedelta(minutes=5) else "shareNow"

tags = " ".join("#" + h.lstrip("#") for h in H["hashtags"])
desc = H["descripcion"].strip()
pregunta = H["pregunta"].strip()
seguir = H.get("seguir") or CFG["seguir"][0]
cuerpo = f"{desc}\n\n{pregunta}\n\n{seguir}\n\n{tags}"
offset = int(H.get("portada_s", 0.8) * 1000)

posts = {
    "youtube": {"text": cuerpo, "assets": [{"video": {"url": url}}],
                "metadata": {"youtube": {"title": H["titulo_youtube"][:100], "categoryId": CFG.get("youtube_categoria", "24"), "privacy": "public",
                                         "madeForKids": False, "notifySubscribers": True, "isAiGenerated": True}}},
    "instagram": {"text": cuerpo, "assets": [{"video": {"url": url, "metadata": {"thumbnailOffset": offset}}}],
                  "metadata": {"instagram": {"type": "reel", "shouldShareToFeed": True, "isAiGenerated": True}}},
    "tiktok": {"text": f"{H['titulo_tiktok']}\n\n{desc}\n\n{tags}"[:2200],
               "assets": [{"video": {"url": url, "metadata": {"thumbnailOffset": offset}}}],
               "metadata": {"tiktok": {"title": H["titulo_tiktok"][:150], "isAiGenerated": True}}},
}
Q = """mutation($input: CreatePostInput!) { createPost(input: $input) {
  ... on PostActionSuccess { post { id dueAt status } }
  ... on MutationError { message } } }"""
res = {}
for red, p in posts.items():
    inp = {"channelId": CANALES[red], "mode": modo, "schedulingType": "automatic", **p}
    if modo == "customScheduled":
        inp["dueAt"] = cuando.isoformat()
    for intento in range(2):
        try:
            d = gql(Q, {"input": inp})
            cp = (d.get("data") or {}).get("createPost") or {}
            if "post" in cp:
                res[red] = cp["post"]["id"]
                break
            res[red] = "ERROR: " + (cp.get("message") or json.dumps(d.get("errors"))[:300])
            break  # error de validación: no reintentar
        except Exception as e:
            res[red] = f"ERROR: {e}"
print(json.dumps({"hora": HORA, "modo": modo, "buffer": res}, ensure_ascii=False))
