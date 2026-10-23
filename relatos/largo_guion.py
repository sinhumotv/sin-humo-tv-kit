#!/usr/bin/env python3
"""Guion de un vídeo LARGO horizontal (8-10 min) con Gemini (gratis), sin Claude.

Uso: python3 largo_guion.py <canal.json> <usados_largos.txt> <carpeta_salida>
Deja <carpeta_salida>/historia.json con escenas (texto + imagen IA o real), capítulos, título y miniatura.
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gem import pedir

C = json.load(open(sys.argv[1], encoding="utf-8"))
L = C.get("largo", {})
USADOS = [l.split("|") for l in open(sys.argv[2], encoding="utf-8").read().splitlines() if l.count("|") >= 2] \
    if os.path.exists(sys.argv[2]) else []
OUT = sys.argv[3]
os.makedirs(OUT, exist_ok=True)


def palabras(t):
    return len(re.findall(r"\w+", t))


MINUTOS = L.get("minutos")   # [mín, máx] -> guion por capítulos
OBJETIVO = int(sum(MINUTOS) / 2 * 60 * 2.65) if MINUTOS else 1450


def valida(h):
    errs = []
    esc = h.get("escenas") or []
    tot = sum(palabras(e.get("hablado", "")) for e in esc)
    if MINUTOS:
        if tot < OBJETIVO * 0.82:
            errs.append(f"solo {tot} palabras de {OBJETIVO}")
    elif tot < 1250:
        errs.append(f"el texto hablado suma solo {tot} palabras y debe llegar a 1400-1600: FALTAN {1450 - tot} PALABRAS. "
                    f"Añade unas {max(6, (1450 - tot) // 30)} escenas NUEVAS en los capítulos centrales con más detalles, contexto, "
                    f"datos curiosos y tensión (no alargues las frases: añade escenas), y devuelve el guion COMPLETO")
    elif tot > 1800:
        errs.append(f"el texto hablado suma {tot} palabras: recórtalo a unas 1600")
    if not 36 <= len(esc) <= (140 if MINUTOS else 64):
        errs.append(f"{len(esc)} escenas (deben ser entre 40 y 52)")
    for i, e in enumerate(esc, 1):
        if re.search(r"\d", e.get("hablado", "")):
            errs.append(f"escena {i} tiene cifras: escríbelas en letra")
        im = e.get("imagen") or {}
        if im.get("tipo") not in ("ia", "real", "video"):
            errs.append(f"escena {i} sin imagen válida")
        elif im["tipo"] == "ia" and len(im.get("prompt", "")) < 40:
            errs.append(f"escena {i} sin prompt de imagen")
        elif im["tipo"] in ("real", "video") and not im.get("busqueda"):
            errs.append(f"escena {i} real sin búsqueda")
    n_ia = sum(1 for e in esc if (e.get("imagen") or {}).get("tipo") == "ia")
    if n_ia > int(L.get("max_ia", 3)) + 2:
        errs.append(f"{n_ia} escenas con imagen IA: como mucho {L.get('max_ia', 3)}; usa vídeo o foto real")
    caps = h.get("capitulos") or []
    if len(caps) < 4 or caps[0].get("escena") != 0:
        errs.append("faltan capítulos (mínimo 4, el primero en la escena 0)")
    if len(h.get("titulos") or []) < 6:
        errs.append("faltan títulos candidatos (10)")
    return errs[:12]


vistos = "; ".join(u[1] for u in USADOS[-200:]) or "(ninguno)"
PROMPT = f"""Eres guionista jefe de un canal de YouTube en español de España de vídeos largos narrados: "{C['nombre']}".
Tema del canal: {L.get('tema', C['tema'])}.
Ideas posibles (no obligatorias): {L.get('ideas', C['ideas'])}.
YA PUBLICADOS EN VÍDEO LARGO (prohibido repetirlos, ni el mismo caso con otro título): {vistos}.

Elige UN tema con mucho interés de búsqueda y potencial de clics (casos o historias conocidas que la gente busca, con un
misterio, un giro o un dato increíble), y escribe el guion completo de un vídeo HORIZONTAL de 9 a 10 minutos.

ESTRUCTURA PARA RETENER AL ESPECTADOR:
- Escenas 1-3 (unos 25 segundos): el GANCHO. Empieza con lo más impactante o con la pregunta clave, promete algo concreto
  que solo se revela al final y di en una frase qué va a descubrir quien se quede. Nada de saludos ni de "en este vídeo".
- Después, de 5 a 7 capítulos con nombre propio (corto y con intriga). Cada capítulo cierra con un pequeño gancho hacia el
  siguiente ("pero lo peor aún no había llegado…"). Cada minuto y medio, un reenganche o una revelación.
- Final: se cumple la promesa del gancho con el giro más fuerte, una reflexión breve y una pregunta para comentarios.
- Tono: {L.get('tono', 'narrador de documental, intrigante y cercano')}. Frases cortas y claras, como se habla.
- {C.get('reglas_extra', '')}
- Hechos reales y fieles a la versión más conocida. No inventes datos; si algo es dudoso, dilo como teoría.

ESCENAS: entre 40 y 52 escenas, 1350-1650 palabras en total. Cada escena = una idea y una imagen, de 20 a 45 palabras.
- "hablado": texto exacto que leerá la voz. Números SIEMPRE en letra, sin siglas, sin emojis, sin comillas.
- "imagen": una de estas tres:
  · {{"tipo": "video", "busqueda": "<2-4 palabras en inglés para buscar un clip de vídeo de stock real>",
      "otras": ["<otra búsqueda más general>", "<otra aún más general>"], "descripcion": "<qué debe verse>"}}
    Clip de vídeo REAL de archivo de stock (Pixabay): {L.get('video', 'lugares, objetos, ambientes y acciones reales')}.
    Es la opción PRINCIPAL: úsala en la mayoría de escenas. Busca cosas genéricas que existan en vídeo (no personas
    concretas ni hechos concretos): p. ej. "ancient temple ruins", "night city rain", "robot arm factory".
  · {{"tipo": "real", "busqueda": "<búsqueda en inglés para Wikimedia Commons, 2-5 palabras concretas>",
      "otras": ["<otra más general>", "<otra más general aún>"], "descripcion": "<qué debe verse>"}}
    Foto o documento real CONCRETO de Wikimedia Commons: {L.get('real', 'fotografías o documentos reales de lo que se cuenta')}.
    Úsala cuando la escena hable de una persona, objeto, lugar u obra concreta que exista en foto o cuadro.
  · {{"tipo": "ia", "prompt": "<EN INGLÉS, 40-80 palabras>"}}: imagen generada, SOLO cuando no hay forma real de
    mostrarlo; como mucho {L.get('max_ia', 3)} escenas en todo el vídeo. Fotorrealista, sin texto, sin sangre, gore ni desnudos,
    sin caras reconocibles de personas reales.
- "efecto": "polvo", "niebla", "brasas" o "nada".

CAPÍTULOS: "capitulos": [{{"escena": <índice desde 0 de la escena donde empieza>, "titulo": "..."}}], el primero en la
escena 0 con el título "Introducción" o similar.

TÍTULO Y MINIATURA (lo MÁS importante: de ellos depende que hagan clic):
- "titulos": 10 títulos distintos de máximo 60 caracteres: palabras que la gente busca + curiosidad o emoción fuerte
  + promesa concreta y CIERTA. Variados: pregunta, dato increíble, "la verdad sobre…", consecuencia, número… Sin
  mayúsculas enteras salvo una palabra, sin emojis, sin mentir.
- "miniatura": {{"texto": "<2 a 4 palabras en MAYÚSCULAS que complementen al título, sin repetirlo>",
  "clave": "<la palabra del texto que irá en amarillo>",
  "prompt": "<EN INGLÉS, 50-90 palabras: imagen horizontal muy llamativa para la miniatura: UN solo protagonista o objeto
  grande en la mitad derecha, emoción intensa o tensión, alto contraste, colores saturados, fondo simple y oscuro en la
  mitad izquierda para el texto; sin texto, sin sangre>"}}
- "descripcion": 2 párrafos para YouTube (el primero repite el gancho con otras palabras e incluye las palabras clave de
  búsqueda; el segundo resume de qué trata sin destripar el final). "etiquetas": 12 etiquetas de búsqueda.
- "titulo": nombre corto del tema (para el registro).

Devuelve SOLO JSON: {{"titulo": "...", "titulos": ["..."], "miniatura": {{...}}, "descripcion": "...", "etiquetas": ["..."],
"capitulos": [...], "escenas": [{{"hablado": "...", "imagen": {{...}}, "efecto": "polvo"}}]}}"""

def por_capitulos():
    """Vídeos de 11-16 min: primero el esquema (título, miniatura, capítulos) y luego cada capítulo por separado."""
    cab = PROMPT[:PROMPT.index("ESCENAS:")]
    reglas = PROMPT[PROMPT.index("ESCENAS:"):PROMPT.index("CAPÍTULOS:")]
    reglas = re.sub(r"ESCENAS: entre 40 y 52 escenas, 1350-1650 palabras en total\.", "ESCENAS:", reglas)
    tit = PROMPT[PROMPT.index("TÍTULO Y MINIATURA"):PROMPT.index("Devuelve SOLO JSON")]
    esq_p = cab + f"""
PASO 1, SOLO EL ESQUEMA de un vídeo de {MINUTOS[0]} a {MINUTOS[1]} minutos (unas {OBJETIVO} palabras habladas en total):
"capitulos": de 8 a 10 capítulos: [{{"titulo": "<corto y con intriga>", "resumen": "<qué se cuenta: 4-6 frases con los
hechos, nombres, fechas y datos clave, en orden>", "palabras": <número>}}]. El primero es el GANCHO más la introducción
(unas 200 palabras); el último, el desenlace con el giro final, una reflexión y la pregunta para comentarios. Reparte
bien la historia: cada capítulo aporta algo nuevo (nada de repetir). Las "palabras" deben sumar unas {OBJETIVO}.
{tit}
Devuelve SOLO JSON: {{"titulo": "...", "titulos": ["..."], "miniatura": {{...}}, "descripcion": "...", "etiquetas": ["..."], "capitulos": [...]}}"""
    E, m = pedir(esq_p, temp=0.9)
    caps = E.get("capitulos") or []
    if len(caps) < 6:
        sys.exit("esquema sin capítulos suficientes")
    resumen = json.dumps([{"titulo": c["titulo"], "resumen": c["resumen"]} for c in caps], ensure_ascii=False)
    escenas, indices, ultimo = [], [], ""
    for k, c in enumerate(caps):
        obj = int(c.get("palabras") or OBJETIVO / len(caps))
        pos = ("Es el COMIENZO del vídeo: aplica las reglas del GANCHO." if k == 0 else
               f"Continúa justo donde terminó el capítulo anterior (su última frase: «{ultimo}»). No repitas nada ya contado.")
        if k == len(caps) - 1:
            pos += " Es el FINAL: cumple la promesa del gancho con el giro final, una reflexión breve y una pregunta para comentarios."
        cp = cab + f"""
ESQUEMA COMPLETO DEL VÍDEO «{E['titulo']}»: {resumen}

PASO 2: escribe AHORA SOLO el capítulo {k + 1} de {len(caps)}: «{c['titulo']}» ({c['resumen']}).
Unas {obj} palabras habladas (MÍNIMO {int(obj * 0.85)}), repartidas en escenas de 20 a 45 palabras. {pos}
{reglas}
Devuelve SOLO JSON: {{"escenas": [{{"hablado": "...", "imagen": {{...}}, "efecto": "polvo"}}]}}"""
        esc = []
        for intento in range(3):
            j, m = pedir(cp, temp=0.85)
            esc = j.get("escenas", []) if isinstance(j, dict) else []
            n = sum(palabras(e.get("hablado", "")) for e in esc)
            malas = [e for e in esc if re.search(r"\d", e.get("hablado", "")) or (e.get("imagen") or {}).get("tipo") not in ("ia", "real", "video")]
            if n >= obj * 0.8 and not malas:
                break
            cp += f"\n\nTu respuesta anterior tenía {n} palabras{' y escenas con cifras o sin imagen válida' if malas else ''}: corrígelo (mínimo {int(obj * 0.85)} palabras, números en letra)."
        indices.append(len(escenas))
        escenas += esc
        ultimo = esc[-1]["hablado"] if esc else ultimo
        print(f"capítulo {k + 1}/{len(caps)} «{c['titulo']}»: {len(esc)} escenas, {sum(palabras(e['hablado']) for e in esc)} palabras")
    E["escenas"] = escenas
    E["capitulos"] = [{"escena": i, "titulo": c["titulo"]} for i, c in zip(indices, caps)]
    E["capitulos"][0]["escena"] = 0
    return E, m


if MINUTOS:
    h, modelo = por_capitulos()
else:
    h, modelo = pedir(PROMPT, temp=0.9)
errs = valida(h)
for intento in range(0 if MINUTOS else 3):
    if not errs:
        break
    print(f"guion largo: {errs} -> corrijo")
    h2, modelo = pedir(PROMPT + f"\n\nCorrige este guion (errores: {errs}). Mantén el tema.\n" + json.dumps(h, ensure_ascii=False), temp=0.6)
    if isinstance(h2, dict):
        h = h2
    errs = valida(h)
if errs:
    sys.exit(f"guion largo no válido: {errs}")
if h["titulo"].lower() in {u[1].lower() for u in USADOS}:
    sys.exit(f"tema repetido: {h['titulo']}")

# ---- elegir el título y el texto de la miniatura con más probabilidad de clic ----
JUEZ = f"""Eres experto en CTR de YouTube en español. Canal: "{C['nombre']}". Vídeo: {h['titulo']}.
Resumen: {h['descripcion'][:600]}
Títulos candidatos: {json.dumps(h['titulos'], ensure_ascii=False)}
Texto de miniatura propuesto: {h['miniatura'].get('texto')}

Elige el título con MÁS probabilidad de clic sin ser engañoso (curiosidad, emoción, palabras que se buscan al principio,
máximo 60 caracteres, fácil de leer en el móvil). Puedes mejorarlo un poco. Luego propone el texto de la miniatura
(2-4 palabras en MAYÚSCULAS) que COMPLEMENTE al título sin repetir sus palabras, y la palabra clave que irá en amarillo.
Devuelve SOLO JSON: {{"titulo_youtube": "...", "texto_miniatura": "...", "clave": "...", "motivo": "..."}}"""
try:
    j, _ = pedir(JUEZ, temp=0.4)
    h["titulo_youtube"] = j["titulo_youtube"][:100]
    h["miniatura"]["texto"] = j.get("texto_miniatura") or h["miniatura"]["texto"]
    h["miniatura"]["clave"] = j.get("clave") or h["miniatura"].get("clave", "")
    print("título elegido:", h["titulo_youtube"], "·", j.get("motivo", "")[:160])
except SystemExit:
    h["titulo_youtube"] = h["titulos"][0]
for e in h["escenas"]:
    e["subtitulo"] = e["hablado"]
h["voz"] = C.get("voz", "Algenib")
h["estilo_imagen"] = L.get("estilo_imagen", C.get("estilo_imagen", ""))
json.dump(h, open(os.path.join(OUT, "historia.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
tot = sum(palabras(e["hablado"]) for e in h["escenas"])
reales = sum(1 for e in h["escenas"] if e["imagen"]["tipo"] != "ia")
print(f"GUION LARGO · {h['titulo']} · «{h['titulo_youtube']}» · {len(h['escenas'])} escenas ({reales} reales) · "
      f"{tot} palabras · {len(h['capitulos'])} capítulos · {modelo}")
