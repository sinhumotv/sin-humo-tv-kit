#!/usr/bin/env python3
"""Vídeo LARGO de un canal, de principio a fin y SIN Claude (GitHub Actions). Se puede repartir en varios días:
el proyecto en curso se guarda en la rama largo-<canal> y cada ejecución sigue donde se quedó.

Fases: guion -> voz -> imagenes (real + IA con la cuota que sobre) -> montaje + miniaturas -> publicar (Metricool).
Uso: python3 largo.py <canal>
Variables: GEMINI_KEY, CF_ACCOUNT, CF_TOKEN, GITHUB_TOKEN, REFRESH (Metricool), GH_SECRETOS.
Opcionales: FORZAR=1 (no esperar a otro día por la cuota), AHORA=1 (publicar en cuanto esté), NO_PUBLICAR=1.
"""
import datetime as dt, json, os, shutil, subprocess, sys, tempfile
from zoneinfo import ZoneInfo

AQUI = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(AQUI)
sys.path.insert(0, os.path.join(KIT, "metricool"))
CANAL = sys.argv[1]
CFG_P = os.path.join(AQUI, "canales", CANAL + ".json")
C = json.load(open(CFG_P, encoding="utf-8"))
L = C["largo"]
MAD = ZoneInfo("Europe/Madrid")
AHORA = dt.datetime.now(MAD)
TOK = os.environ.get("GITHUB_TOKEN", "")
REPO_URL = f"https://x-access-token:{TOK}@github.com/sinhumotv/sin-humo-tv-kit" if TOK else "https://github.com/sinhumotv/sin-humo-tv-kit"
RAMA = f"largo-{CANAL}"
BASE = tempfile.mkdtemp(prefix=f"largo-{CANAL}-")
P = os.path.join(BASE, "proyecto")
os.environ["AUTO"] = "1"
os.environ.setdefault("GEMINI_API_KEY", os.environ.get("GEMINI_KEY", ""))


def sh(c, cwd=None, ok=False):
    r = subprocess.run(c, shell=True, capture_output=True, text=True, cwd=cwd)
    out = (r.stdout + r.stderr).replace(TOK or "~~", "***")
    if r.returncode and not ok:
        raise RuntimeError(f"{c[:80]} -> {out[-1500:]}")
    return r.returncode, out


def guardar_proyecto():
    """Guarda el proyecto (sin archivos pesados regenerables) en la rama largo-<canal>, en un único commit."""
    shutil.rmtree(f"{P}/.git", ignore_errors=True)
    sh(f"git init -q && git checkout -q --orphan {RAMA}", cwd=P)
    open(f"{P}/.gitignore", "w").write("*.wav\n_*\nvideo_final.mp4\n*.raw\n")
    sh(f'git add -A && git -c user.name="{C["nombre"]}" -c user.email="sinhumotv@users.noreply.github.com" '
       f'commit -qm "{RAMA} {AHORA:%Y-%m-%d %H:%M}" && git push -q --force {REPO_URL} {RAMA}', cwd=P)


def estado(fase=None, **kw):
    E = json.load(open(f"{P}/estado.json")) if os.path.exists(f"{P}/estado.json") else {}
    if fase:
        E.update(kw, fase=fase)
        json.dump(E, open(f"{P}/estado.json", "w"), ensure_ascii=False, indent=1)
    return E


# ---------- registro de largos publicados (rama datos) ----------
DAT = os.path.join(BASE, "datos")
sh(f"git clone -q --depth 1 --branch datos {REPO_URL} {DAT}", ok=True)
REG = os.path.join(DAT, f"largos_{CANAL}.txt")
open(REG, "a").close()
REGISTRO = [l.split("|") for l in open(REG, encoding="utf-8").read().splitlines() if l.count("|") >= 2]


def huecos_ocupados():
    return {r[0][:10] for r in REGISTRO}   # un largo por día como mucho


def siguiente_hueco():
    """Primera fecha libre del calendario (cada 2 días desde 'inicio', a la hora del canal) con margen de 30 min."""
    hh, mm = map(int, L["hora"].split(":"))
    d = dt.datetime.fromisoformat(L["inicio"]).replace(hour=hh, minute=mm, tzinfo=MAD)
    paso = dt.timedelta(days=int(L.get("cada_dias", 2)))
    import hashlib
    def variado(d):  # la hora cambia cada vez (hasta ±45 min), para que no se publique siempre a la misma
        v = int(hashlib.sha256(f"{CANAL}|{d:%Y-%m-%d}".encode()).hexdigest(), 16) % 91 - 45
        return d + dt.timedelta(minutes=v)
    while variado(d) < AHORA + dt.timedelta(minutes=30) or d.strftime("%Y-%m-%d") in huecos_ocupados():
        d += paso
    d = variado(d)
    if os.environ.get("AHORA") and not any(r[0] >= AHORA.strftime("%Y-%m-%d") for r in REGISTRO):
        d = AHORA + dt.timedelta(minutes=20)  # primera vez: publicar en cuanto esté
    return d


# ---------- proyecto en curso ----------
rc, _ = sh(f"git clone -q --depth 1 --branch {RAMA} {REPO_URL} {P}", ok=True)
if rc or not os.path.exists(f"{P}/estado.json") or estado().get("fase") == "hecho":
    shutil.rmtree(P, ignore_errors=True)
    os.makedirs(P)
    futuros = [r for r in REGISTRO if r[0] > AHORA.strftime("%Y-%m-%d %H:%M")]
    if len(futuros) >= 2:
        print(f"Ya hay {len(futuros)} largos programados: no hace falta empezar otro")
        sys.exit(0)
    estado("guion", empezado=AHORA.isoformat())
E = estado()
print("fase:", E["fase"])

if E["fase"] == "guion":
    print(sh(f'python3 "{AQUI}/largo_guion.py" "{CFG_P}" "{REG}" "{P}"')[1].strip()[-700:])
    E = estado("voz")
    guardar_proyecto()

H = json.load(open(f"{P}/historia.json", encoding="utf-8"))
ESC = H["escenas"]


def proyecto_json():
    caps = [{"desde": c["escena"], "escena": c["escena"], "titulo": c["titulo"]} for c in H["capitulos"]
            if 0 <= c["escena"] < len(ESC)]
    json.dump({"formato": "YOUTUBE", "duracion_max": 900, "duracion_min": 0, "fecha": "", "fuentes": "",
               "titulo_noticia": H["titulo"], "tono": "grave", "mencion": 0, "zum": [],
               "efectos": [e.get("efecto", "polvo") for e in ESC], "fuego": [],
               "capitulos": caps,
               "color": C.get("color_subtitulo"),
               "escenas": [{"titulo": "", "hablado": e["hablado"], "subtitulo": e["subtitulo"]} for e in ESC]},
              open(f"{P}/proyecto.json", "w"), ensure_ascii=False, indent=1)


if E["fase"] == "voz":
    proyecto_json()
    open(f"{P}/voz.txt", "w").write("\n\n".join(e["hablado"] for e in ESC))
    env = "TTS_MODELOS=gemini-3.1-flash-tts-preview,gemini-2.5-flash-preview-tts,gemini-3.8-flash-tts,gemini-3.8-flash-lite-tts"
    print(sh(f'{env} python3 "{AQUI}/voz_relato.py" "{P}" --tono relato --voz {H.get("voz", "Algenib")}')[1].strip()[-400:])
    E = estado("imagenes")
    guardar_proyecto()

if E["fase"] == "imagenes":
    rc, out = sh(f'python3 "{AQUI}/largo_imagenes.py" "{P}" "{CFG_P}"', ok=True)
    print(out.strip()[-2500:])
    guardar_proyecto()
    if rc == 3:
        print("Imágenes pendientes: sigue en la próxima ejecución")
        sys.exit(0)
    if rc:
        raise SystemExit("fallo en imágenes")
    E = estado("montaje")
    guardar_proyecto()

if E["fase"] == "montaje":
    proyecto_json()
    print(sh(f'python3 "{KIT}/audio.py" "{P}"')[1].strip().splitlines()[0])
    print(sh(f'python3 "{AQUI}/montaje.py" "{P}"')[1].strip()[-300:])
    print(sh(f'python3 "{AQUI}/largo_miniatura.py" "{P}"')[1].strip()[-200:])
    T = json.load(open(f"{P}/tiempos.json"))
    # descripción: gancho + capítulos + créditos
    caps = open(f"{P}/capitulos.txt", encoding="utf-8").read().strip() if os.path.exists(f"{P}/capitulos.txt") else ""
    cred = json.load(open(f"{P}/creditos.json", encoding="utf-8")) if os.path.exists(f"{P}/creditos.json") else {}
    tags = " ".join("#" + t.replace(" ", "").lower() for t in (C.get("hashtags_base") or [])[:3])
    desc = f"{H['descripcion'].strip()}\n\nCAPÍTULOS\n{caps}\n\n"
    desc += "Narración e imágenes de las escenas generadas con inteligencia artificial"
    desc += (" y material de archivo de Wikimedia Commons." if cred else ".")
    desc += f"\n\nSuscríbete a {C['nombre']} para no perderte el próximo.\n\n{tags}"
    if cred:
        desc += "\n\nCRÉDITOS DE IMÁGENES\n" + "\n".join(sorted(set(v.rsplit(' · ', 1)[0] for v in cred.values())))
    desc = desc[:4900]
    open(f"{P}/descripcion.txt", "w", encoding="utf-8").write(desc)
    print(f"MONTADO · {T['duracion'] / 60:.1f} min · «{H['titulo_youtube']}»")

    # alojar en una release de GitHub (admite archivos grandes)
    tag = f"largo-{CANAL}-{AHORA:%Y%m%d-%H%M}"
    env = {**os.environ, "GH_TOKEN": TOK}
    shutil.copy(f"{P}/video_final.mp4", f"{BASE}/video.mp4")
    r = subprocess.run(["gh", "release", "create", tag, f"{BASE}/video.mp4", f"{P}/miniatura_A.jpg", f"{P}/miniatura_B.jpg",
                        f"{P}/miniatura_C.jpg", "-R", "sinhumotv/sin-humo-tv-kit", "--title",
                        f"{C['nombre']} · {H['titulo_youtube']}", "--notes", f"{T['duracion'] / 60:.1f} min"],
                       env=env, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit("no se pudo crear la release: " + r.stderr[-400:])
    url = f"https://github.com/sinhumotv/sin-humo-tv-kit/releases/download/{tag}"
    E = estado("publicar", tag=tag, video=f"{url}/video.mp4", miniatura=f"{url}/miniatura_A.jpg",
               duracion=T["duracion"])
    guardar_proyecto()
    print("ALOJADO:", url)

if E["fase"] == "publicar":
    if os.environ.get("NO_PUBLICAR"):
        print("NO_PUBLICAR: listo para programar ·", E["video"])
        sys.exit(0)
    desc = open(f"{P}/descripcion.txt", encoding="utf-8").read()
    cuando = siguiente_hueco()
    import mc
    s = mc.Sesion(mc.acceso(CANAL))
    marca = mc.marca(s)
    info = {"autoPublish": True, "draft": False, "descendants": [], "firstCommentText": "", "hasNotReadNotes": False,
            "media": [E["video"]], "videoThumbnailUrl": E["miniatura"], "mediaAltText": [],
            "providers": [{"network": "youtube"}],
            "publicationDate": {"dateTime": cuando.strftime("%Y-%m-%dT%H:%M:00"), "timezone": "Europe/Madrid"},
            "shortener": False, "smartLinkData": {"ids": []}, "text": desc,
            "youtubeData": {"title": H["titulo_youtube"][:100], "type": "video", "privacy": "public",
                            "tags": H.get("etiquetas", [])[:15], "category": L.get("categoria", "ENTERTAINMENT"),
                            "madeForKids": False, "isAiGeneratedContent": True}}
    args = {"date": cuando.isoformat(timespec="seconds"), "blogId": str(marca["id"]), "info": json.dumps(info, ensure_ascii=False)}
    try:
        res = s.llamar("createScheduledPost", args)
    except RuntimeError as e:
        if "THUMBNAIL" not in str(e).upper():
            raise
        print("Metricool no acepta la miniatura (¿canal sin verificar por teléfono?): se publica sin ella")
        info.pop("videoThumbnailUrl")
        args["info"] = json.dumps(info, ensure_ascii=False)
        res = s.llamar("createScheduledPost", args)
    print("METRICOOL:", json.dumps(res, ensure_ascii=False)[:400])
    pid = ""
    if isinstance(res, dict):
        x = res.get("data", res)
        pid = str(x.get("id", "")) if isinstance(x, dict) else ""
    with open(REG, "a", encoding="utf-8") as f:
        f.write(f"{cuando:%Y-%m-%d %H:%M}|{H['titulo']}|{H['titulo_youtube']}|{pid}|{E['tag']}\n")
    sh(f'git add largos_{CANAL}.txt && git -c user.name="{C["nombre"]}" -c user.email="sinhumotv@users.noreply.github.com" '
       f'commit -qm "largo {CANAL} {cuando:%Y-%m-%d}" && git push -q {REPO_URL} HEAD:datos', cwd=DAT, ok=True)
    estado("hecho", publicado=cuando.isoformat())
    guardar_proyecto()
    print(f"PROGRAMADO · {C['nombre']} · {cuando:%d/%m %H:%M} · «{H['titulo_youtube']}»")
