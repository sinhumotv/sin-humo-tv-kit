#!/usr/bin/env python3
"""Escribe N guiones (historia.json) con Gemini (gratis), sin gastar Claude.

Uso: python3 guion.py <canal.json> <usados.txt> <carpeta_salida> <n>
Crea <carpeta_salida>/01/historia.json, 02/..., con un gancho de tipo distinto en cada vídeo.
Clave: variable GEMINI_KEY (o ~/.gemini_key).
"""
import json, os, random, re, sys, time, urllib.request, urllib.error

C = json.load(open(sys.argv[1], encoding="utf-8"))
USADOS = [l.split("|") for l in open(sys.argv[2], encoding="utf-8").read().splitlines() if l.count("|") >= 2] \
    if os.path.exists(sys.argv[2]) else []
OUT = sys.argv[3]
N = int(sys.argv[4])
KEY = os.environ.get("GEMINI_KEY") or open(os.path.expanduser("~/.gemini_key")).read().strip()
MODELOS = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.5-flash", "gemini-2.5-flash", "gemini-flash-latest"]

GANCHOS = {
    "sabias": "Empieza con «¿Sabías que…?» y un dato sorprendente del relato, y promete que lo más fuerte llega al final (p. ej. «…y el final es aún peor»).",
    "consecuencia": "Empieza por la consecuencia más impactante, como un adelanto del final, sin explicar aún por qué (p. ej. «Un solo vistazo le costó el amor de su vida»).",
    "nadie": "Empieza con «Hay algo que casi nadie te ha contado de…» o una variante, y revela ese algo al final.",
    "pregunta": "Empieza con una pregunta directa al espectador que le ponga en la piel del protagonista (p. ej. «¿Qué harías si un dios te concediera un deseo?»).",
    "final": "Empieza pidiendo que se quede hasta el final con un motivo concreto (p. ej. «Quédate hasta el final, porque el último giro lo cambia todo») y di de qué va en pocas palabras.",
    "increible": "Empieza con una frase que parezca increíble pero sea verdad dentro del relato (p. ej. «Este rey murió de hambre rodeado de oro»).",
    "error": "Empieza con el error o la decisión que lo desencadenó todo (p. ej. «Este error le costó la vida a su hijo»).",
    "cuenta": "Empieza con una cifra o una cuenta atrás impactante del relato (p. ej. «Tenía tres días para hacer lo imposible»).",
}


def gemini(prompt, temp=0.95):
    cuerpo = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
              "generationConfig": {"temperature": temp, "responseMimeType": "application/json", "maxOutputTokens": 16000}}
    ultimo = None
    for ronda in range(3):  # si Gemini está saturado, espera y vuelve a probar todos los modelos
        if ronda:
            print(f"Gemini saturado ({ultimo}); reintento en {120 * ronda} s", flush=True)
            time.sleep(120 * ronda)
        r = _ronda(cuerpo)
        if r[0] is not None:
            return r
        ultimo = r[1]
    raise SystemExit("Gemini no responde: " + str(ultimo))


def _ronda(cuerpo):
    ultimo = None
    for m in MODELOS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={KEY}"
        for intento in range(2):
            try:
                req = urllib.request.Request(url, json.dumps(cuerpo).encode(), {"Content-Type": "application/json"})
                j = json.load(urllib.request.urlopen(req, timeout=180))
                txt = "".join(p.get("text", "") for p in j["candidates"][0]["content"]["parts"])
                return json.loads(txt), m
            except urllib.error.HTTPError as e:
                ultimo = f"{m}: HTTP {e.code} {e.read()[:200]!r}"
                if e.code in (429, 503):
                    time.sleep(8)
                    continue
                break
            except Exception as e:
                ultimo = f"{m}: {e}"
                time.sleep(3)
    return None, ultimo


def leer_noticias():
    """Noticias reales y recientes de los feeds RSS del canal (gratis, sin buscador de pago)."""
    cfg = C.get("noticias") or {}
    if not cfg.get("por_dia"):
        return []
    import email.utils, datetime as dt, html, xml.etree.ElementTree as ET
    limite = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=cfg.get("horas", 72))
    filtro = re.compile(cfg.get("filtro", "."), re.I)
    vistos_t = {u[2].lower() for u in USADOS}
    salida, titulares = [], set()
    for f in cfg.get("feeds", []):
        try:
            req = urllib.request.Request(f["url"], headers={"User-Agent": "Mozilla/5.0"})
            raiz = ET.fromstring(urllib.request.urlopen(req, timeout=30).read())
        except Exception as e:
            print(f"noticias: {f['medio']} no responde ({str(e)[:60]})")
            continue
        for it in raiz.iter("item"):
            tit = html.unescape(it.findtext("title") or "").strip()
            txt = html.unescape(re.sub(r"<[^>]+>", " ", it.findtext("description") or ""))
            txt = re.sub(r"\s+", " ", txt).strip()
            try:
                fecha = email.utils.parsedate_to_datetime(it.findtext("pubDate"))
            except Exception:
                continue
            if fecha < limite or not tit or tit.lower() in titulares:
                continue
            if f.get("filtrar") and not filtro.search(tit + " " + txt[:600]):
                continue
            titulares.add(tit.lower())
            salida.append({"fecha": fecha.strftime("%d/%m/%Y"), "medio": f["medio"], "titular": tit, "texto": txt[:1500]})
    salida = [x for x in salida if x["titular"].lower() not in vistos_t][: cfg.get("max", 14)]
    print(f"noticias reales leídas: {len(salida)}")
    return salida


NOTICIAS = leer_noticias()
K_NOT = min(int((C.get("noticias") or {}).get("por_dia", 0)), len(NOTICIAS))


def bloque_noticias(k):
    if not k:
        return ""
    lista = "\n".join(f"[{i + 1}] {x['fecha']} · {x['medio']} · {x['titular']}\n    {x['texto']}" for i, x in enumerate(NOTICIAS))
    return f"""
NOTICIAS REALES DE LOS ÚLTIMOS DÍAS (leídas hoy de medios; son la ÚNICA fuente válida para los vídeos de noticias):
{lista}

Los vídeos 1 a {k} son VÍDEOS DE NOTICIA: cada uno cuenta UNA noticia distinta de esa lista (elige las de más impacto y
más interesantes para el público general, y nunca una ya publicada). Cuenta SOLO lo que dice su texto: no añadas cifras,
nombres, fechas ni detalles que no aparezcan. Puedes explicar en una frase qué significa para la gente, sin inventar.
No exageres: nada de absolutos («exacto», «siempre», «nunca», «para siempre») que el texto no diga.
En esos vídeos, "titulo" es el tema de la noticia y la primera línea de "descripcion" dice el medio (p. ej. «Según Xataka, …»).
Si una noticia es solo publicidad, rumores o no trata de verdad de IA o tecnología, descártala.
El resto de vídeos son de los temas generales del canal, no de esta lista.
"""


def palabras(t):
    return len(re.findall(r"\w+", t))


def valida(h):
    errs = []
    esc = h.get("escenas") or []
    if not 6 <= len(esc) <= 9:
        errs.append(f"{len(esc)} escenas (deben ser 7 u 8)")
    total = sum(palabras(e.get("hablado", "")) for e in esc)
    if not 78 <= total <= 112:
        errs.append(f"{total} palabras (deben ser 85-100)")
    if esc and palabras(esc[0].get("hablado", "")) > 16:
        errs.append("la primera escena es demasiado larga (máximo 14 palabras)")
    for i, e in enumerate(esc):
        if not e.get("prompt") or len(e["prompt"]) < 40:
            errs.append(f"escena {i + 1} sin prompt de imagen")
        if re.search(r"\d", e.get("hablado", "")):
            errs.append(f"escena {i + 1} tiene cifras: escríbelas en letra")
    for k in ("titulo", "titulo_youtube", "descripcion", "pregunta", "titulo_tiktok"):
        if not h.get(k):
            errs.append(f"falta {k}")
    return errs


def instrucciones(n, tipos, k=0):
    vistos = "; ".join(u[2] for u in USADOS[-150:]) or "(ninguno)"
    lista = "\n".join(f"- Vídeo {i + 1}: gancho «{t}»: {GANCHOS[t]}" for i, t in enumerate(tipos))
    return f"""Eres guionista de vídeos cortos verticales (Shorts, Reels, TikTok) del canal "{C['nombre']}".
Tema del canal: {C['tema']}.
Ideas posibles (no obligatorias): {C['ideas']}.
YA PUBLICADOS (prohibido repetirlos, ni el mismo episodio con otro título): {vistos}.
{bloque_noticias(k)}
Escribe {n} guiones, cada uno sobre un tema DISTINTO y variados entre sí (no todos del mismo tipo).
Reglas de cada guion (español de España, natural, frases cortas, tono de narrador intrigante):
- 7 u 8 escenas; entre 85 y 100 palabras en total (unos 32-38 segundos de voz). Una idea y una imagen por escena.
- La escena 1 es el GANCHO (máximo 14 palabras) y abre una promesa que SOLO se cumple al final. Tipos de gancho asignados:
{lista}
- Prohibido empezar por "Hoy", "Hola", "En la mitología griega", "Había una vez" o el nombre del canal.
- Hacia la mitad (escena 4 o 5), un pequeño reenganche ("Pero entonces…", "Y aquí viene lo peor…").
- La última escena cumple la promesa del gancho con el giro final y termina con una pregunta corta al espectador.
- "hablado" es el texto exacto que leerá la voz: números en letra, sin siglas, sin emojis, sin comillas, nombres como se pronuncian en español.
- Hechos fieles a la versión más conocida. No inventes. Si hay varias versiones, cuenta la más conocida.
- {C.get('reglas_extra', '')}
- "prompt" (EN INGLÉS, 40-90 palabras): imagen vertical fotorrealista de esa escena. Describe a cada personaje SIEMPRE con la misma frase en todas sus escenas (edad, pelo, barba, ropa) para que se parezca. Nada de texto en la imagen. Nada de sangre, gore ni desnudos: lo duro se sugiere (sombras, reacciones). Si un nombre de dios puede bloquearse, descríbelo por su aspecto.
- "efecto": "brasas" (fuego, batallas, inframundo), "polvo" (día, interiores), "niebla" (mar, cuevas, fantasmas) o "nada". "fuego": true si se ven antorchas o fuego.
Campos de publicación de cada guion:
- "titulo": nombre corto del tema. "gancho_tipo": el tipo asignado.
- "titulo_youtube": máximo 60 caracteres, con intriga, sin prometer lo que no hay.
- "descripcion": 2 líneas; la primera repite el gancho con otras palabras; la segunda termina en "{C['firma']}".
- "pregunta": pregunta para comentarios que se conteste con una palabra o eligiendo entre dos opciones.
- "hashtags": 1 o 2 hashtags del tema, sin #. "titulo_tiktok": el gancho en forma de pregunta.
Devuelve SOLO JSON: {{"guiones": [{{"titulo": "...", "gancho_tipo": "...", "escenas": [{{"hablado": "...", "prompt": "...", "efecto": "polvo", "fuego": false}}], "titulo_youtube": "...", "descripcion": "...", "pregunta": "...", "hashtags": ["..."], "titulo_tiktok": "..."}}]}}"""


# tipos de gancho: distintos entre sí y distintos de los del último día
ult = {u[3] for u in USADOS[-N:] if len(u) > 3}
tipos = [t for t in GANCHOS if t not in ult]
random.shuffle(tipos)
tipos = (tipos + [t for t in GANCHOS if t in ult])[:N]

datos, modelo = gemini(instrucciones(N, tipos, K_NOT))
guiones = datos.get("guiones", []) if isinstance(datos, dict) else datos
buenos = []
for i in range(N):
    h = guiones[i] if i < len(guiones) else None
    errs = valida(h) if h else ["no generado"]
    for intento in range(2):
        if not errs:
            break
        print(f"guion {i + 1}: {errs} -> lo pido de nuevo")
        extra = (f"\nCorrige este guion (errores: {errs}). Mantén el tema si es válido y el gancho «{tipos[i]}».\n"
                 f"{json.dumps(h, ensure_ascii=False) if h else ''}")
        d2, _ = gemini(instrucciones(1, [tipos[i]], 1 if i < K_NOT else 0) + extra, temp=0.7)
        g2 = d2.get("guiones", [d2]) if isinstance(d2, dict) else d2
        h = g2[0] if g2 else None
        errs = valida(h) if h else ["no generado"]
    if errs:
        print(f"guion {i + 1} descartado: {errs}")
        continue
    usados_tit = {u[2].lower() for u in USADOS} | {b["titulo"].lower() for b in buenos}
    if h["titulo"].lower() in usados_tit:
        print(f"guion {i + 1} repetido ({h['titulo']}), descartado")
        continue
    for e in h["escenas"]:
        e["subtitulo"] = e["hablado"]
    tags = C["hashtags_base"] + [x.lstrip("#").replace(" ", "").lower() for x in h.get("hashtags", [])][:2]
    h["hashtags"] = list(dict.fromkeys(tags))
    h["seguir"] = random.choice(C["seguir"])
    h["voz"] = C.get("voz", "Algenib")
    h["gancho_tipo"] = h.get("gancho_tipo") or tipos[i]
    h["portada_s"] = 0.8
    h["estilo_imagen"] = C.get("estilo_imagen", "")
    if C.get("color_subtitulo"):
        h["color"] = C["color_subtitulo"]
    buenos.append(h)

for k, h in enumerate(buenos, 1):
    d = os.path.join(OUT, f"{k:02d}")
    os.makedirs(d, exist_ok=True)
    json.dump(h, open(os.path.join(d, "historia.json"), "w"), ensure_ascii=False, indent=1)
    print(f"{k:02d} · {h['titulo']} · gancho {h['gancho_tipo']} · «{h['escenas'][0]['hablado']}»")
print(f"{len(buenos)}/{N} guiones con {modelo}")
