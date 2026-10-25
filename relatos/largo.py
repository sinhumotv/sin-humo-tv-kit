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
sys.path.insert(0, AQUI)
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
    open(f"{P}/.gitignore", "w").write("*.wav\n_*\nvideo_final.mp4\n*.raw\nclips/\n")
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
    AHORA = dt.datetime.now(MAD)   # la hora real del momento de programar (la ejecución puede llevar horas)
    """Primera fecha libre del calendario (cada 2 días desde 'inicio', a la hora del canal) con margen de 30 min."""
    hh, mm = map(int, L["hora"].split(":"))
    d = dt.datetime.fromisoformat(L["inicio"]).replace(hour=hh, minute=mm, tzinfo=MAD)
    paso = dt.timedelta(days=int(L.get("cada_dias", 2)))
    import hashlib
    def variado(d):  # la hora cambia cada vez (hasta ±45 min), para que no se publique siempre a la misma
        v = int(hashlib.sha256(f"{CANAL}|{d:%Y-%m-%d}".encode()).hexdigest(), 16) % 91 - 45
        return d + dt.timedelta(minutes=v)
    por_mes = int(L.get("por_mes", 0))
    if por_mes:
        # X largos al mes (cupo gratis de Metricool: 20 publicaciones al mes por cuenta), repartidos por igual en el mes
        import calendar
        def toca(d):
            n = calendar.monthrange(d.year, d.month)[1]
            return int(d.day * por_mes / n) != int((d.day - 1) * por_mes / n)
        def lleno(d):
            return sum(1 for r in REGISTRO if r[0][:7] == d.strftime("%Y-%m")) >= por_mes
        d = max(d, AHORA.replace(hour=hh, minute=mm, second=0, microsecond=0))
        paso = dt.timedelta(days=1)
        while (not toca(d) or lleno(d) or variado(d) < AHORA + dt.timedelta(minutes=30)
               or d.strftime("%Y-%m-%d") in huecos_ocupados()):
            d += paso
    else:
        while variado(d) < AHORA + dt.timedelta(minutes=30) or d.strftime("%Y-%m-%d") in huecos_ocupados():
            d += paso
    d = variado(d)
    if os.environ.get("AHORA") and not any(r[0] >= AHORA.strftime("%Y-%m-%d") for r in REGISTRO):
        d = AHORA + dt.timedelta(minutes=20)  # primera vez: publicar en cuanto esté
    return d


# ---------- proyecto en curso ----------
rc, _ = sh(f"git clone -q --depth 1 --branch {RAMA} {REPO_URL} {P}", ok=True)
# REHACER=<id del post de Metricool>: rehace con el sistema nuevo un largo ya programado (mismo tema y guion, voz e
# imagen nuevas) y SUSTITUYE ese post en Metricool, a la misma fecha y hora.
REH = os.environ.get("REHACER", "").strip()
if REH and not rc and estado().get("fase") == "hecho" and not estado().get("rehacer"):
    print("REHACER: se rehace el largo programado", REH)
    Hh = json.load(open(f"{P}/historia.json", encoding="utf-8"))
    for e in Hh["escenas"]:
        im = e["imagen"]
        for k in ("clip", "clip_id", "clip_ini", "extra"):
            im.pop(k, None)
        im["tipo"] = "video"
        im.setdefault("busqueda", im.get("descripcion", "")[:60] or "technology future")
    json.dump(Hh, open(f"{P}/historia.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for d in ("imgs", "clips", "voz_trozos"):
        shutil.rmtree(f"{P}/{d}", ignore_errors=True)
    for f in ("voz.mp3", "miniatura_base.jpg", "creditos.json", "tiempos.json", "subtitulos.srt"):
        if os.path.exists(f"{P}/{f}"):
            os.remove(f"{P}/{f}")
    E0 = estado()
    json.dump({"empezado": AHORA.isoformat(), "fase": "voz", "rehacer": REH, "publicado_antes": E0.get("publicado")},
              open(f"{P}/estado.json", "w"), ensure_ascii=False, indent=1)
    guardar_proyecto()
if os.environ.get("REINICIAR") and not rc and estado().get("fase") != "hecho":
    print("REINICIAR: se descarta el proyecto en curso y se empieza uno nuevo")
    rc = 1
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
    json.dump({"formato": "YOUTUBE", "duracion_max": 1500, "duracion_min": 0, "fecha": "", "fuentes": "",
               "titulo_noticia": H["titulo"], "tono": "grave", "mencion": 0, "zum": [],
               "efectos": ["nada" if e["imagen"]["tipo"] == "video" else e.get("efecto", "polvo") for e in ESC],
               "fuego": [],
               "clips": {str(k): (f"{P}/clips/{k + 1:02d}_full.mp4" if os.path.exists(f"{P}/clips/{k + 1:02d}_full.mp4")
                                else f"{P}/clips/{k + 1:02d}.mp4") for k, e in enumerate(ESC) if e["imagen"].get("clip")},
               "capitulos": caps,
               "color": C.get("color_subtitulo"),
               "escenas": [{"titulo": "", "hablado": e["hablado"], "subtitulo": e["subtitulo"]} for e in ESC]},
              open(f"{P}/proyecto.json", "w"), ensure_ascii=False, indent=1)


if E["fase"] == "voz":
    proyecto_json()
    open(f"{P}/voz.txt", "w").write("\n\n".join(e["hablado"] for e in ESC))
    # VOZ_ESTRICTA: un solo modelo para todo el vídeo, misma velocidad, mismo volumen y control de que todos los
    # trozos suenan igual (regla del usuario: la voz no puede cambiar a mitad del vídeo). Nunca el modelo «lite».
    env = ("VOZ_ESTRICTA=1 TTS_MAX=3000 "
           "TTS_MODELOS=gemini-3.1-flash-tts-preview,gemini-2.5-flash-preview-tts,gemini-3.8-flash-tts")
    rc, out = sh(f'{env} python3 "{AQUI}/voz_relato.py" "{P}" --tono relato --voz {H.get("voz", "Algenib")}', ok=True)
    print(out.strip()[-1500:])
    if rc == 3:
        guardar_proyecto()
        print("Voz pendiente: sigue en la próxima ejecución con el mismo modelo")
        sys.exit(0)
    if rc:
        raise SystemExit("fallo en la voz")
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
    # los clips de vídeo no se guardan entre días: se vuelven a bajar si faltan
    import urllib.request, time as _t
    import stock
    os.makedirs(f"{P}/clips", exist_ok=True)

    def bajar_url(url, dst):
        for intento in range(4):
            try:
                open(dst, "wb").write(urllib.request.urlopen(urllib.request.Request(
                    url, headers={"User-Agent": "SinHumoTV-largos/1.0"}), timeout=180).read())
                if os.path.getsize(dst) > 50000:
                    return True
            except Exception as ex:
                print(f"  descarga fallida ({str(ex)[:60]}), reintento {intento + 1}")
            _t.sleep(10 * (intento + 1))
        return False

    sin_clip = []
    for k, e in enumerate(ESC):
        im, n = e["imagen"], k + 1
        piezas = [(im.get("clip"), im.get("clip_ini"), f"{P}/clips/{n:02d}.mp4")]
        piezas += [(x.get("clip"), x.get("clip_ini"), f"{P}/clips/{n:02d}_{j + 1}.mp4")
                   for j, x in enumerate(im.get("extra", []))]
        for c, ini, dst in piezas:
            if not c or os.path.exists(dst):
                continue
            ok_ = (stock.bajar_segmento({"url": c, "inicio": ini}, dst, segundos=20) if ini is not None
                   else bajar_url(c, dst))
            if not ok_ and dst.endswith(f"{n:02d}.mp4"):
                sin_clip.append(n)
    if sin_clip:
        # NUNCA se monta con el fotograma quieto: esas escenas vuelven a buscar vídeo (y se sigue en esta ejecución
        # o en la próxima)
        for n in sin_clip:
            for f in (f"{P}/imgs/{n:02d}.jpg",):
                if os.path.exists(f):
                    os.remove(f)
            ESC[n - 1]["imagen"].pop("clip", None)
            ESC[n - 1]["imagen"].pop("extra", None)
        json.dump(H, open(f"{P}/historia.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        estado("imagenes")
        guardar_proyecto()
        print(f"clips que no se han podido bajar {sin_clip}: se buscan otros")
        if int(os.environ.get("REPETIR_LARGO", "0")) < 2:
            os.environ["REPETIR_LARGO"] = str(int(os.environ.get("REPETIR_LARGO", "0")) + 1)
            os.execv(sys.executable, [sys.executable] + sys.argv)   # vuelve a empezar desde la fase de imágenes
        sys.exit(0)   # se sigue en la próxima ejecución
    proyecto_json()
    print(sh(f'python3 "{KIT}/audio.py" "{P}"')[1].strip().splitlines()[0])
    # RITMO (para que la gente se quede): un plano nuevo cada 5-6 s. Si la escena tiene varios clips, cada uno ocupa
    # su parte de la escena (recortado a esa duración) y se unen con un fundido corto; todo a 1920x1080 y 30 fps.
    TE = json.load(open(f"{P}/tiempos.json"))["escenas"]
    for k, e in enumerate(ESC):
        n, im = k + 1, e["imagen"]
        partes = [f"{P}/clips/{n:02d}.mp4"] + [f"{P}/clips/{n:02d}_{j + 1}.mp4" for j in range(len(im.get("extra", [])))]
        partes = [d for d in partes if os.path.exists(d)]
        full = f"{P}/clips/{n:02d}_full.mp4"
        if len(partes) < 2 or os.path.exists(full) or k >= len(TE):
            continue
        largo_esc = TE[k]["fin"] - TE[k]["ini"] + 1.5
        seg = largo_esc / len(partes) + 0.5
        norm = []
        for j, d in enumerate(partes):
            o = f"{P}/clips/_n{n:02d}_{j}.mp4"
            ini = 0.5 if j else 0   # (el primero empieza desde el principio, para el fundido de entrada)
            sh(f'ffmpeg -y -v error -ss {ini} -i "{d}" -t {seg:.2f} -an -vf "scale=1920:1080:force_original_aspect_ratio=increase,'
               f'crop=1920:1080,fps=30,format=yuv420p" -c:v libx264 -preset veryfast -crf 20 "{o}"')
            norm.append(o)
        cur = norm[0]
        for j, o in enumerate(norm[1:], 1):
            d0 = float(sh(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{cur}"')[1].strip())
            nxt = f"{P}/clips/_x{n:02d}_{j}.mp4"
            sh(f'ffmpeg -y -v error -i "{cur}" -i "{o}" -filter_complex "[0][1]xfade=transition=fade:duration=0.5:'
               f'offset={max(0.1, d0 - 0.5):.2f},format=yuv420p" -c:v libx264 -preset veryfast -crf 20 "{nxt}"')
            cur = nxt
        shutil.move(cur, full)
    proyecto_json()
    print(sh(f'python3 "{AQUI}/montaje.py" "{P}"')[1].strip()[-300:])
    # CONTROL (regla del usuario: todo vídeo en movimiento): si algún tramo se queda quieto, esa escena se rehace
    rc_q, out_q = sh(f'python3 "{AQUI}/control_movimiento.py" "{P}/video_final.mp4" "{P}/tiempos.json"', ok=True)
    print(out_q.strip()[-600:])
    if rc_q == 4:
        quietas = json.loads(out_q.strip().splitlines()[-1].split(" ", 1)[1] or "[]")
        if int(os.environ.get("REPETIR_LARGO", "0")) >= 2 or not quietas:
            print("NO SE PUBLICA: sigue habiendo tramos quietos tras rehacer las escenas")
            guardar_proyecto()
            sys.exit(1)
        veto = set(H.get("vetados", []))
        for n in quietas:
            im = ESC[n - 1]["imagen"]
            veto |= {str(im.get("clip_id"))} | {str(x.get("clip_id")) for x in im.get("extra", [])}
            im.pop("clip", None); im.pop("extra", None); im["tipo"] = "video"
            for f in [f"{P}/imgs/{n:02d}.jpg"] + [f"{P}/clips/{n:02d}{x}.mp4" for x in ("", "_1", "_2", "_3", "_full")]:
                if os.path.exists(f):
                    os.remove(f)
        H["vetados"] = sorted(veto)
        json.dump(H, open(f"{P}/historia.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        estado("imagenes")
        guardar_proyecto()
        print(f"Escenas con imagen quieta {quietas}: se buscan otros clips y se vuelve a montar")
        os.environ["REPETIR_LARGO"] = str(int(os.environ.get("REPETIR_LARGO", "0")) + 1)
        os.execv(sys.executable, [sys.executable] + sys.argv)
    print(sh(f'python3 "{AQUI}/largo_miniatura.py" "{P}"')[1].strip()[-200:])
    T = json.load(open(f"{P}/tiempos.json"))
    # descripción: gancho + capítulos + créditos
    caps = open(f"{P}/capitulos.txt", encoding="utf-8").read().strip() if os.path.exists(f"{P}/capitulos.txt") else ""
    cred = json.load(open(f"{P}/creditos.json", encoding="utf-8")) if os.path.exists(f"{P}/creditos.json") else {}
    tags = " ".join("#" + t.replace(" ", "").lower() for t in (C.get("hashtags_base") or [])[:3])
    desc = f"{H['descripcion'].strip()}\n\nCAPÍTULOS\n{caps}\n\n"
    n_ia = sum(1 for e in ESC if e["imagen"]["tipo"] == "ia")
    desc += "Narración generada con inteligencia artificial. Imágenes: material real de archivo (Pixabay y Wikimedia Commons)"
    desc += (" y algunas escenas generadas con IA." if n_ia else ".")
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
    REH = E.get("rehacer")
    cuando = (dt.datetime.fromisoformat(E["publicado_antes"]).astimezone(MAD) if REH and E.get("publicado_antes")
              else siguiente_hueco())
    if REH and cuando < dt.datetime.now(MAD) + dt.timedelta(minutes=20):
        cuando = dt.datetime.now(MAD) + dt.timedelta(minutes=30)
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
    uuid_viejo = None
    if REH:
        lst = s.llamar("getScheduledPosts", {"brandId": str(marca["id"]), "timezone": "Europe/Madrid",
                                             "fromDate": (cuando - dt.timedelta(days=3)).strftime("%Y-%m-%dT00:00:00+01:00"),
                                             "toDate": (cuando + dt.timedelta(days=3)).strftime("%Y-%m-%dT23:59:59+01:00")})
        txt_l = json.dumps(lst)
        import re as _re
        posts = lst.get("data", lst) if isinstance(lst, dict) else lst
        for po in (posts if isinstance(posts, list) else []):
            if str(po.get("id")) == str(REH):
                uuid_viejo = po.get("uuid")
        print("post a sustituir:", REH, "uuid:", uuid_viejo, "" if uuid_viejo else txt_l[:600])
    try:
        if uuid_viejo:
            res = s.llamar("updateScheduledPost", {"id": str(REH), "uuid": uuid_viejo, "blogId": str(marca["id"]),
                                                   "info": args["info"]})
        else:
            res = s.llamar("createScheduledPost", args)
    except RuntimeError as e:
        if "THUMBNAIL" not in str(e).upper():
            raise
        print("Metricool no acepta la miniatura (¿canal sin verificar por teléfono?): se publica sin ella")
        info.pop("videoThumbnailUrl")
        args["info"] = json.dumps(info, ensure_ascii=False)
        res = (s.llamar("updateScheduledPost", {"id": str(REH), "uuid": uuid_viejo, "blogId": str(marca["id"]),
                                                "info": args["info"]}) if uuid_viejo
               else s.llamar("createScheduledPost", args))
    print("METRICOOL:", json.dumps(res, ensure_ascii=False)[:400])
    pid = ""
    if isinstance(res, dict):
        x = res.get("data", res)
        pid = str(x.get("id", "")) if isinstance(x, dict) else ""
    import datos
    if REH and uuid_viejo:   # el registro ya tiene esa fecha y ese título: no se duplica
        estado("hecho", publicado=cuando.isoformat(), rehecho=pid)
        guardar_proyecto()
        print(f"REHECHO Y SUSTITUIDO · {C['nombre']} · {cuando:%d/%m %H:%M} · «{H['titulo_youtube']}»")
        sys.exit(0)
    datos.anadir(REPO_URL, f"largos_{CANAL}.txt",
                 [f"{cuando:%Y-%m-%d %H:%M}|{H['titulo']}|{H['titulo_youtube']}|{pid}|{E['tag']}"],
                 C["nombre"], f"largo {CANAL} {cuando:%Y-%m-%d}")
    estado("hecho", publicado=cuando.isoformat())
    guardar_proyecto()
    print(f"PROGRAMADO · {C['nombre']} · {cuando:%d/%m %H:%M} · «{H['titulo_youtube']}»")
