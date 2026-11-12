#!/usr/bin/env python3
"""LARGO de sin humo TV hecho SIN Claude (7-nov-2026), igual que la skill «video-largo-sin-humo-tv»: unos 8 minutos en 16:9 con
el kit del canal (motor_h.js: Lupi, capítulos, plantillas), 5 capítulos, hasta 6 fotos reales de Wikimedia Commons en escenas
propias, voz propia del canal con Qwen3-TTS (Gemini Puck de reserva), miniatura con foto real.

Uso: python3 plataforma/sinhumo/largo_sh.py <noticia.json> <carpeta>
  noticia.json = {tema, hechos (texto largo y comprobado), fuentes[], enlaces[], grave, fotos[] (búsquedas en Commons)}
Variables: KIT_SH (kit del canal), GEMINI_API_KEY (y GEMINI_CLAVES de reserva).
Deja en <carpeta>: video_final.mp4, miniatura.jpg, capitulos.txt, creditos.json y largo.json (título, descripción, etiquetas).
"""
import datetime, json, os, re, subprocess, sys, time

AQUI = os.path.dirname(os.path.abspath(__file__))
PLAT = os.path.dirname(AQUI)
KIT = os.environ.get('KIT_SH') or os.path.join(os.path.dirname(PLAT), 'kit_sh')
sys.path.insert(0, os.path.join(PLAT, 'guion'))
import ia   # noqa: E402

N = json.load(open(sys.argv[1], encoding='utf-8'))
D = os.path.abspath(sys.argv[2]); os.makedirs(D, exist_ok=True)
MESES = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']
UA = 'sinhumoTV/1.0 (https://github.com/sinhumotv; sinhumotv@users.noreply.github.com)'
ICONOS = ['billete', 'moneda', 'carrito', 'banco', 'termometro', 'barril', 'rayo', 'globo', 'persona', 'cartera', 'alerta', 'reloj',
          'calendario', 'vela', 'escudo', 'casa', 'corona', 'gente', 'documento', 'edificio', 'coche', 'pin', 'medalla', 'mazo', 'balanza',
          'paloma', 'tachado', 'sello']
TIPOS = {'cifra', 'comparar', 'lista', 'frase', 'linea', 'icono', 'grafico', 'pregunta', 'mencion', 'cierre', 'foto'}
PARTIDOS = r'\b(PSOE|PP|Partido Popular|Podemos|Vox|Sumar|ERC|Junts|Bildu|PNV|Ciudadanos|Compromís|BNG|Más Madrid)\b'
K = ia.clave()
GRAVE = bool(N.get('grave'))


def corre(args, timeout=None):
    r = subprocess.run(args, capture_output=True, text=True, cwd=KIT, timeout=timeout)
    if r.returncode:
        sys.exit(f'FALLO {os.path.basename(args[1] if len(args) > 1 else args[0])}: ' + (r.stdout + r.stderr)[-900:])
    return r.stdout


def gemini(texto, temp):
    """(7-nov-2026) Prueba TODAS las claves de Gemini que tiene el servidor (GEMINI_CLAVES: de pago de Explícalo, la de sin humo TV
    y la de Explícalo) y todos sus modelos de texto antes de rendirse; si todo está saturado, espera y repite."""
    claves = [c for c in dict.fromkeys([K] + os.environ.get('GEMINI_CLAVES', '').split(',')) if c.strip() and c.strip().lower() != 'ninguna']
    ultimo = None
    for intento in range(5):
        for k in claves:
            for m in ia.modelos(k)[:6]:
                try:
                    r = ia.peticion(f'{ia.API}/models/{m}:generateContent?key={k}', {'contents': [{'role': 'user', 'parts': [{'text': texto}]}],
                                    'generationConfig': {'temperature': temp, 'responseMimeType': 'application/json'}}, timeout=300)
                    t = r['candidates'][0]['content']['parts'][0]['text']
                    return json.loads(t[t.index('{'):t.rindex('}') + 1])
                except Exception as e:
                    ultimo = f'{m}: {str(e)[:150]}'
        time.sleep(30 * (intento + 1))
    sys.exit('FALLO Gemini: ' + str(ultimo))


def bajar(url, timeout=60):
    import urllib.error, urllib.request
    for intento in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=timeout).read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or intento == 3: raise
            time.sleep(int(e.headers.get('Retry-After') or 0) or 20 * (intento + 1))


def commons(q):
    import urllib.parse
    url = ('https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrlimit=12&gsrsearch='
           + urllib.parse.quote(q + ' filetype:bitmap') + '&prop=imageinfo&iiprop=url|size|mime|extmetadata&iiurlwidth=1280')
    out = []
    for pg in (json.loads(bajar(url, 40)).get('query') or {}).get('pages', {}).values():
        i = (pg.get('imageinfo') or [{}])[0]; m = i.get('extmetadata') or {}
        lic = str((m.get('LicenseShortName') or {}).get('value') or '')
        autor = re.sub(r'<[^>]+>', '', str((m.get('Artist') or {}).get('value') or '')).strip()[:40] or 'Wikimedia Commons'
        if not re.search(r'^(CC0|CC BY(-SA)? [0-9.]+|Public domain|PD)', lic, re.I) or i.get('mime') not in ('image/jpeg', 'image/png'): continue
        if min(i.get('width') or 0, i.get('height') or 0) < 500: continue
        if re.search(PARTIDOS, pg.get('title', '') + ' ' + autor, re.I): continue
        out.append({'titulo': pg.get('title', '')[5:], 'url': i.get('thumburl') or i.get('url'), 'licencia': lic, 'autor': autor,
                    'desc': re.sub(r'<[^>]+>', '', str((m.get('ImageDescription') or {}).get('value') or ''))[:140]})
    return out


# ---------- 1) FOTOS (hasta 12; 10-nov-2026: antes 6, y el vídeo era casi todo iconos con texto) ----------
MAX_FOTOS = 12
print('· fotos', flush=True)
cand = []
for q in (N.get('fotos') or [])[:8]:
    try:
        for c in commons(q):
            if c['url'] not in [x['url'] for x in cand]: cand.append(c)
    except Exception as x:
        print('fotos:', q, str(x)[:100], flush=True)
    time.sleep(3)
cand = cand[:48]
fotos = []
if cand:
    lista = '\n'.join(f'{i}. {c["titulo"]} · {c["desc"]}' for i, c in enumerate(cand))
    elec = gemini(f'Noticia: «{N["tema"]}». {N["hechos"][:900]}\nFotos libres de Wikimedia Commons:\n{lista}\n'
                  f'Elige hasta {MAX_FOTOS} DISTINTAS (cuantas más válidas, mejor; sin repetir el mismo sitio o persona más de 2 veces) que muestren de verdad a quien o lo que sale en la noticia (personas públicas, lugares, edificios, '
                  'instituciones, objetos). La PRIMERA va en la miniatura y tiene que contar el ASUNTO de un vistazo (11-nov-2026: salió un hotel cualquiera en una '
                  'miniatura sobre la huelga general): la escena típica de la noticia (huelga → manifestación o piquetes; elecciones → urnas; incendio → fuego y '
                  'bomberos; vivienda → bloques de pisos), nunca un edificio genérico de fondo ni un político de partido; sin pancartas con insultos o palabrotas. '
                  'Si eliges políticos, de varias partes, nunca solo de un partido. '
                  'Nunca menores, víctimas, primeros planos de personas que no sean cargos públicos, logos ni carteles '
                  'de partidos. Responde solo JSON: {"elegidas": [números]}', 0.2)
    os.makedirs(os.path.join(D, 'fotos'), exist_ok=True)
    for i in [int(x) for x in (elec.get('elegidas') or []) if str(x).isdigit() and int(x) < len(cand)][:MAX_FOTOS]:
        c = cand[i]; dest = os.path.join(D, 'fotos', f'f{len(fotos)}.jpg')
        try:
            open(dest, 'wb').write(bajar(c['url']))
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', dest, '-vf', 'scale=1280:-2', '-q:v', '3', dest + '.jpg'], check=True)
            os.replace(dest + '.jpg', dest)
        except Exception as x:
            print('foto no bajada:', str(x)[:80], flush=True); continue
        base = re.sub(r'\.(jpe?g|png)$', '', c['titulo'], flags=re.I); base = ' '.join(re.sub(r'[_()\d-]+', ' ', base).split()[:5])
        fotos.append({'ruta': dest, 'que': base[:34], 'titulo': c['titulo'], 'credito': f'{c["autor"]} · Wikimedia Commons · {c["licencia"]}'})
        time.sleep(3)
if not fotos:
    sys.exit('SIN_FOTOS: no hay fotos reales libres de esta noticia')
json.dump(fotos, open(os.path.join(D, 'creditos.json'), 'w'), ensure_ascii=False)
print('fotos:', len(fotos), flush=True)

# ---------- 2) GUION (5 capítulos, ~80 escenas, unos 8 minutos de voz) ----------
print('· guion', flush=True)
fotos_txt = '\n'.join(f'  FOTO{i + 1}: {f["que"]} ({f["titulo"]})' for i, f in enumerate(fotos))
REGLAS = f"""Eres el guionista de «sin humo TV», canal de YouTube de noticias que cuenta los hechos sin humo, en ESPAÑOL DE ESPAÑA.
Vídeo LARGO horizontal de unos 8 minutos que explica a fondo esta noticia. Usa SOLO estos hechos comprobados (fuentes: {', '.join(N.get('fuentes') or [])});
si un dato solo lo da una fuente, dilo como «según <fuente>»; no inventes cifras, fechas ni citas:
\"\"\"{N['hechos']}\"\"\"
Contenido: contexto (qué ha pasado), por qué importa, datos clave, posturas de cada parte (neutral, mismo espacio), qué puede pasar ahora y qué significa
para el espectador. Política: solo hechos y NEUTRALIDAD ESTRICTA: si salen partidos o políticos, el mismo espacio para cada parte (Gobierno y oposición, y cada partido que cites), nunca más de 2 escenas seguidas sobre un mismo partido, y nada de insultos ni descalificaciones literales («mafia», «te come»…): cuéntalo como «críticas duras» sin repetirlas. Antes que declaraciones de partido, prioriza instituciones, datos y cómo afecta a la gente. {'Hay víctimas: tono serio y respetuoso; no identifiques a víctimas ni a menores; nadie es culpable sin condena.' if GRAVE else ''}
Frases cortas (8-15 palabras), tono de narrador curioso y cercano, pausado. Una idea por escena (4-9 segundos).
La voz que lo lee NO interpreta acotaciones ni susurra: el tono tiene que estar en el propio texto (preguntas con ¿?, exclamaciones con ¡!, puntos suspensivos para la intriga). Nunca escribas acotaciones como «(en voz baja)» ni etiquetas entre corchetes.
LENGUAJE DE LA CALLE: palabras sencillas, como se lo contarías a un amigo («votos», no «sufragios»; «elecciones», no «proceso comicial»; «dijo», no «manifestó»;
«pidió», no «formalizó la petición»). Nada de jerga jurídica o administrativa; si una sigla o un término técnico es imprescindible, explícalo en la misma frase la primera vez.
Cada escena aporta algo NUEVO y concreto (un dato, un nombre, una fecha, una consecuencia): nada de frases de relleno ni de repetir lo ya dicho.
Primera frase: gancho de máximo 10 palabras (cifra, pregunta incómoda o hecho sorprendente); prohibido empezar por «Hola», «Hoy», «Bienvenidos» o el canal.
En los primeros 30 s: qué vas a explicar y una promesa concreta que se cumple al final («y al final, lo que casi nadie está contando…»).
Al final de cada capítulo, una frase que abra el siguiente. Hacia la mitad (capítulo 3), UNA escena de mención: «Si te está sirviendo, suscríbete a sin humo TV:
aquí vamos a los hechos.» (variable, máx. 15 palabras) con "visual": {{"tipo":"mencion","texto":"Los hechos, sin humo"}}. Última escena: pregunta abierta y neutral
con "visual": {{"tipo":"cierre","texto":"≤ 30 caracteres","grave":{str(GRAVE).lower()}}}; justo antes, un resumen en 3 frases y la revelación prometida.
Cada escena: {{"capitulo": 1-5, "titulo": "≤ 26 caracteres", "subtitulo": "lo que dice la voz, con cifras y siglas tal cual y 1-3 *palabras clave*", "visual": {{…}}}}
LO QUE SE VE tiene que ser tan concreto como lo que se dice: el texto de cada visual lleva el dato, el nombre o la fecha de esa escena, nunca una etiqueta
genérica («Factor clave», «Reparto geográfico», «Circunscripciones clave» NO valen; «Decide 3 escaños en Ourense» SÍ). Como mucho un tercio de las escenas de tipo
"icono": prefiere foto, cifra, comparar, linea, lista y frase. "grafico" solo con 3 o más cifras reales de la misma cosa (años, meses o lugares en las etiquetas) y
"comparar" solo con dos cifras reales en la misma unidad; si no tienes esas cifras en los hechos, usa otro tipo. "lista": de 2 a 4 puntos, cada uno un hecho concreto.
Tipos de "visual" (no repitas el mismo tipo más de 2 veces seguidas):
  {{"tipo":"cifra","valor":"72.000","texto":"personas en 2 días","icono":"gente","color":"rojo"}}
  {{"tipo":"comparar","a":{{"etiqueta":"2024","valor":"3,1 %"}},"b":{{"etiqueta":"2026","valor":"4,2 %"}}}}   (solo datos reales)
  {{"tipo":"lista","titulo":"(opcional)","items":["…","…","…"],"color":"azul"}}   (hasta 4, ≤ 34 caracteres)
  {{"tipo":"frase","texto":"cita literal de los hechos (≤ 110 caracteres)","fuente":"medio"}}
  {{"tipo":"linea","hitos":[{{"fecha":"Mayo","texto":"≤ 30 caracteres"}}]}}   (hasta 5)
  {{"tipo":"icono","icono":"casa","texto":"≤ 40 caracteres","etiqueta":"(opcional)","color":"…"}}   (con icono calendario, añade "cal":["NOV","29"])
  {{"tipo":"grafico","titulo":"…","valores":["3","5","8"],"etiquetas":["Jul","Ago","Sep"]}}   (solo datos reales)
  {{"tipo":"pregunta","texto":"¿…?"}}
  {{"tipo":"foto","foto":"FOTO1","texto":"rótulo corto de lo que se ve"}}   (fotos reales; úsalas TODAS, cada una una vez, repartidas)
Iconos: {', '.join(ICONOS)}. Colores: rojo, azul, verde, oro, naranja, morado.
FOTOS disponibles:
{fotos_txt}"""
texto = REGLAS + """
Escribe el guion ENTERO: 5 capítulos, 75-85 escenas, entre 7.300 y 7.800 caracteres de texto hablado EN TOTAL (unas 1.250-1.350 palabras).
Responde SOLO con JSON: {"titulo_noticia": "la noticia en 8-12 palabras", "capitulos": ["5 títulos de ≤ 28 caracteres"], "escenas": [ … ]}"""
G = gemini(texto, 0.6)
# (8-nov-2026) REVISIÓN DE NEUTRALIDAD: el primer largo del servidor sobre la huelga del 11-N dio 10 escenas a Podemos y ERC, con insultos
# citados, y casi nada al resto. Otra IA revisa el guion; si no está equilibrado, se reescribe con sus avisos (2 intentos) o no se hace.
for vuelta in range(4):
    texto_g = '\n'.join(f'- {e.get("subtitulo")}' for e in (G.get('escenas') or []) if isinstance(e, dict))
    R = gemini('Eres el editor de neutralidad de un canal de noticias de España. Revisa este guion:\n' + texto_g +
               '\n\n¿Es políticamente neutral? Falla SOLO si: da claramente más espacio o protagonismo a un partido, político o bloque que a los demás '
               'citados; repite insultos o descalificaciones literales; toma partido o califica con adjetivos de opinión a un partido o político '
               '(«ultraderecha» solo vale atribuido: «al que X llama…»); o deja sin la versión de la otra parte una acusación. NO son problemas y '
               'no los cuentes: la mención para suscribirse al canal, el gancho y la promesa del principio («lo que casi nadie está contando»), '
               'la pregunta final, describir un suceso como grave o trágico cuando lo es, ni las cifras. Responde solo JSON: '
               '{"neutral": true|false, "problemas": ["concretos y cortos, solo de los que hacen fallar"]}', 0.1)
    # (8-nov-2026) además, una cuenta objetiva: menciones de cada partido y su líder. Si uno se lleva más del doble que el siguiente
    # de los citados (con al menos 6), el guion no está equilibrado aunque la IA diga que sí (pasó con un largo de sondeos: 37 a 10).
    PARTES = {'PP': r'\bPP\b|Partido Popular|Feij[óo]o', 'PSOE': r'PSOE|socialistas?|S[áa]nchez', 'Vox': r'\bVox\b|Abascal',
              'Sumar': r'\bSumar\b|Yolanda D[íi]az', 'Podemos': r'Podemos|Belarra|Montero', 'Junts': r'Junts|Puigdemont', 'ERC': r'\bERC\b|Rufi[áa]n'}
    cuenta = {k: len(re.findall(v, texto_g)) for k, v in PARTES.items()}
    citados = sorted([c for c in cuenta.values() if c > 0], reverse=True)
    gob, opo = cuenta['PSOE'] + cuenta['Sumar'], cuenta['PP'] + cuenta['Vox']   # Gobierno frente a oposición principal
    if (len(citados) >= 2 and citados[0] >= 6 and citados[0] > 2 * citados[1]) or (max(gob, opo) >= 8 and max(gob, opo) > 2 * max(1, min(gob, opo))):
        R = {'neutral': False, 'problemas': [f'menciones desequilibradas entre partidos: {json.dumps(cuenta)}; da el mismo espacio a cada parte citada']}
    if R.get('neutral') is True: break
    print('neutralidad:', '; '.join(map(str, R.get('problemas') or []))[:400], flush=True)
    if vuelta == 3: sys.exit('FALLO neutralidad: el guion no ha salido equilibrado: ' + '; '.join(map(str, R.get('problemas') or []))[:300])
    G = gemini(texto + '\n\nUN EDITOR HA RECHAZADO LA VERSIÓN ANTERIOR POR FALTA DE NEUTRALIDAD: ' + '; '.join(map(str, R.get('problemas') or [])) +
               '\nCorrígelo: mismo espacio para cada parte, sin insultos citados, más datos e instituciones y menos declaraciones de partido.', 0.5)
esc = [e for e in (G.get('escenas') or []) if isinstance(e, dict) and str(e.get('subtitulo') or '').strip()]
caps = [(str(c) if len(str(c)) <= 28 else str(c)[:29].rsplit(' ', 1)[0]) for c in (G.get('capitulos') or [])][:5]   # sin cortar palabras
largo = lambda es: sum(len(str(e['subtitulo']).replace('*', '')) for e in es)
for vuelta in range(3):   # la IA se queda corta: se le piden escenas nuevas para el capítulo más corto hasta llegar a ~7.300 caracteres
    if largo(esc) >= 7300: break
    porcap = {c: sum(len(str(e['subtitulo'])) for e in esc if int(e.get('capitulo') or 0) == c) for c in range(1, 6)}
    c = min(porcap, key=porcap.get); falta = 7500 - largo(esc)
    dicho = '\n'.join(f'- {e["subtitulo"]}' for e in esc if int(e.get('capitulo') or 0) == c)
    extra = gemini(REGLAS + f'\n\nEl guion se ha quedado corto. Escribe {max(4, falta // 95)} escenas NUEVAS para el final del capítulo {c} '
                   f'(«{caps[c - 1] if c - 1 < len(caps) else c}»), unos {falta} caracteres en total, que profundicen sin repetir nada de esto:\n{dicho}\n'
                   'Nada de menciones al canal ni cierres. Responde solo JSON: {"escenas": [ … ]} con "capitulo": ' + str(c), 0.7)
    nuevas = [dict(x, capitulo=c) for x in (extra.get('escenas') or []) if isinstance(x, dict) and str(x.get('subtitulo') or '').strip()]
    pos = max([i for i, e in enumerate(esc) if int(e.get('capitulo') or 0) == c] or [len(esc) - 2]) + 1
    if c == 5: pos = min(pos, len(esc) - 2)
    esc = esc[:pos] + nuevas + esc[pos:]
print(f'guion: {len(esc)} escenas · {largo(esc)} caracteres', flush=True)

# ---------- 3) PROYECTO, escenas de foto y capítulos ----------
COL = {'rojo': '#d9483b', 'azul': '#2f7fd0', 'verde': '#2e9e6b', 'oro': '#e0a526', 'naranja': '#ef7d2d', 'morado': '#6b4fa3'}
escenas, capitulos, usadas, fotos_esc = [], [], set(), {}
for k, e in enumerate(esc):
    cap = max(1, min(5, int(e.get('capitulo') or 1)))
    if not capitulos or capitulos[-1]['n'] != cap and cap > capitulos[-1]['n']:
        capitulos.append({'n': cap, 'titulo': (caps[cap - 1] if cap - 1 < len(caps) else f'Parte {cap}'), 'desde': len(escenas)})
    v = e.get('visual') if isinstance(e.get('visual'), dict) else {}
    if v.get('tipo') not in TIPOS: v = {'tipo': 'icono', 'icono': 'alerta', 'texto': str(e.get('titulo') or '')[:40]}
    if v.get('tipo') == 'foto':
        m = re.search(r'(\d+)', str(v.get('foto') or '')); i = int(m.group(1)) - 1 if m else -1
        if 0 <= i < len(fotos) and i not in usadas:
            usadas.add(i); fotos_esc[len(escenas)] = (i, str(v.get('texto') or fotos[i]['que'])[:34])
        v = {'tipo': 'icono', 'icono': 'documento', 'texto': str(v.get('texto') or e.get('titulo') or '')[:40]}   # respaldo si no carga
    if v.get('tipo') == 'icono' and v.get('icono') not in ICONOS: v['icono'] = 'alerta'
    sub = ' '.join(str(e['subtitulo']).split())
    escenas.append({'titulo': str(e.get('titulo') or '')[:26], 'hablado': sub.replace('*', ''), 'subtitulo': sub,
                    'color': COL.get(str(v.get('color') or ''), '#2f7fd0'), 'visual': v})
# (7-nov-2026) CIFRAS COHERENTES: en la prueba, la voz decía «6.194 personas» y en pantalla salía «4.698». Toda cifra que se ve
# tiene que estar en lo que se dice en esa escena (o la de al lado); si no, la escena pasa a icono.
_dig = lambda s: re.sub(r'\D', '', str(s))
def _cifras_ok(k, v):
    vals = [v.get('valor')] if v.get('tipo') == 'cifra' else [(v.get('a') or {}).get('valor'), (v.get('b') or {}).get('valor')] if v.get('tipo') == 'comparar' \
        else list(v.get('valores') or []) if v.get('tipo') == 'grafico' else []
    cerca = ' '.join(escenas[j]['subtitulo'] for j in range(max(0, k - 1), min(len(escenas), k + 2)))
    fuente = ' '.join(_dig(x) for x in re.findall(r'\d[\d.,]*', cerca))   # solo lo que se DICE alrededor de la escena
    def dicho(x):   # en cifras («6.194») o en letras («seis mil ciento noventa y cuatro», «tres mil»)
        if _dig(x) in fuente.split(): return True
        try:
            from num2words import num2words
            return num2words(int(_dig(x)), lang='es') in cerca.lower()
        except Exception:
            return False
    return all(not _dig(x) or dicho(x) for x in vals if x not in (None, ''))
def _num_ok(x):
    return bool(re.search(r'\d', str(x or '')))
def _visual_ok(v):
    """(10-nov-2026) Un largo salió con un gráfico de una sola barra y rótulos sin sentido («Hijos», «Septiembre»). Lo que no tenga datos
    de verdad para dibujarse pasa a icono (y de ahí, si queda una foto sin colocar, a foto real)."""
    t = v.get('tipo')
    if t == 'grafico':
        vals, et = list(v.get('valores') or []), list(v.get('etiquetas') or [])
        return len(vals) >= 3 and len(et) == len(vals) and all(_num_ok(x) for x in vals) and all(str(x).strip() for x in et)
    if t == 'comparar':
        a, b = v.get('a') or {}, v.get('b') or {}
        return _num_ok(a.get('valor')) and _num_ok(b.get('valor')) and str(a.get('etiqueta') or '').strip() and str(b.get('etiqueta') or '').strip()
    if t == 'lista': return len([x for x in (v.get('items') or []) if str(x).strip()]) >= 2
    if t == 'linea': return len([h for h in (v.get('hitos') or []) if isinstance(h, dict) and str(h.get('texto') or '').strip()]) >= 2
    if t == 'cifra': return _num_ok(v.get('valor'))
    if t in ('frase', 'pregunta'): return len(str(v.get('texto') or '').strip()) >= 8
    if t == 'icono': return len(str(v.get('texto') or '').strip()) >= 4      # el 10-nov salió una escena con un icono y nada escrito
    return True
for k, e in enumerate(escenas):
    if not _visual_ok(e['visual']):
        print(f'escena {k}: visual sin datos suficientes ({json.dumps(e["visual"], ensure_ascii=False)[:120]}) → icono', flush=True)
        e['visual'] = {'tipo': 'icono', 'icono': 'documento', 'texto': e['titulo'][:40]}
for k, e in enumerate(escenas):
    if e['visual'].get('tipo') in ('cifra', 'comparar', 'grafico') and not _cifras_ok(k, e['visual']):
        print(f'escena {k}: cifra en pantalla que no se dice ({json.dumps(e["visual"], ensure_ascii=False)[:120]}) → icono', flush=True)
        e['visual'] = {'tipo': 'icono', 'icono': 'documento', 'texto': e['titulo'][:40]}
libres = [k for k, e in enumerate(escenas) if e['visual']['tipo'] in ('icono', 'pregunta') and k not in fotos_esc and 0 < k < len(escenas) - 2]
for i, f in enumerate(fotos):   # fotos que la IA no ha colocado: en escenas de icono repartidas
    if i in usadas or not libres: continue
    k = libres.pop(len(libres) * (i + 1) // (len(fotos) + 1) if libres else 0); fotos_esc[k] = (i, f['que'])
men = next((k for k, e in enumerate(escenas) if e['visual']['tipo'] == 'mencion'), None)
if men is None:
    sys.exit('FALLO guion: falta la escena de la mención del canal')
if escenas[-1]['visual'].get('tipo') != 'cierre':
    escenas[-1]['visual'] = {'tipo': 'cierre', 'texto': re.sub(r'\*', '', escenas[-1]['subtitulo'])[:30], 'grave': GRAVE}
capitulos[0]['desde'] = 0
hoy = datetime.date.today()
P = {'formato': 'YOUTUBE', 'fecha': f'{hoy.day} {MESES[hoy.month - 1]} {hoy.year}', 'titulo_noticia': str(G.get('titulo_noticia') or N['tema'])[:90],
     'fuentes': ' · '.join((N.get('fuentes') or [])[:3]), 'tono': 'grave' if GRAVE else 'tensa', 'zum': [], 'mencion': men,
     'capitulos': [{'titulo': c['titulo'], 'desde': c['desde']} for c in capitulos], 'escenas': escenas}
json.dump(P, open(os.path.join(D, 'proyecto.json'), 'w'), ensure_ascii=False, indent=1)
js = ['window.ESCENAS = window.ESCENAS || [];',
      '(function(){ %s.forEach(r=>{const i=new Image(); i.src="file://"+r;}); })();' % json.dumps([f['ruta'] for f in fotos])]
for k, (i, rot) in sorted(fotos_esc.items()):
    f = fotos[i]
    # (10-nov-2026) la foto llena la tarjeta (860x400) y el rótulo va escrito encima, abajo a la izquierda
    js.append(f"window.ESCENAS[{k}] = (L, A) => ({{ svg: A.foto({json.dumps(f['ruta'])}, 540, 325, 860, 400, 0, A.pop(L, 0), {json.dumps(f['credito'])})"
              f" + (L > .5 ? `<text x=\"140\" y=\"474\" font-family=\"Inter\" font-weight=\"900\" font-size=\"40\" fill=\"#fff\" stroke=\"${{A.INK}}\" stroke-width=\"8\" paint-order=\"stroke\" stroke-linejoin=\"round\" opacity=\"${{A.fade(L, .5)}}\">${{A.esc({json.dumps(rot)})}}</text>` : ''), lupi: {{x: 1135, y: 400, s: .85, "
              f"expr: '{'seria' if GRAVE else 'curiosa'}', mira: [-1, 0], brazos: 'senala'}}, evitar: [[100, 120, 880, 420]] }});")
open(os.path.join(D, 'escenas.js'), 'w').write('\n'.join(js) + '\n')
def _hablado():
    """hablado.py pasa cifras, símbolos y siglas a palabras. (8-nov-2026) Si deja algo sin convertir («REVISAR: …»), se arregla aquí
    (cifras → letras, siglas → palabra, símbolos fuera) y se repite, en vez de tirar el vídeo."""
    import ast as _ast
    for vez in range(3):
        r = subprocess.run(['python3', 'hablado.py', D], capture_output=True, text=True, cwd=KIT)
        if r.returncode == 0: return r.stdout.strip().splitlines()[-1][:100]
        m = re.search(r'REVISAR: quedan sin convertir: (.*)', r.stdout)
        if not m or vez == 2: sys.exit('FALLO hablado.py: ' + (r.stdout + r.stderr)[-500:])
        try: restos = _ast.literal_eval(m.group(1).strip())
        except Exception: restos = re.findall(r"'([^']+)'", m.group(1))
        restos = list(restos) if isinstance(restos, (list, tuple, set)) else [str(restos)]
        print('hablado: arreglo', restos[:12], flush=True)
        Pj = json.load(open(os.path.join(D, 'proyecto.json'), encoding='utf-8'))
        def letras(m):
            try:
                from num2words import num2words
                return num2words(int(_dig(m.group(0))), lang='es')
            except Exception: return ' '
        SIM = {'%': ' por ciento', '€': ' euros', '$': ' dólares', '&': ' y ', '+': ' más ', '/': ' ', 'º': '', 'ª': ''}
        for e in Pj['escenas']:
            h = re.sub(r'\d[\d.]*(,\d+)?', letras, e['hablado'])
            for k_, v_ in SIM.items(): h = h.replace(k_, v_)
            h = re.sub(r'\b[A-ZÁÉÍÓÚÑ]{2,}\b', lambda m: m.group(0).capitalize(), h)
            e['hablado'] = ' '.join(h.split())
        json.dump(Pj, open(os.path.join(D, 'proyecto.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('hablado:', _hablado(), flush=True)

# ---------- 4) VOZ: la voz propia del canal con Qwen3-TTS (gratis, sin límites); Gemini solo de reserva ----------
# (12-nov-2026) Pablo eligió la voz de Qwen copiando la voz del canal: misma voz siempre y sin cuotas. No actúa
# susurros ni emociones por encargo: el guion transmite el tono con el texto (preguntas, exclamaciones, puntos suspensivos).
print('· voz', flush=True)
KIT = os.path.dirname(PLAT)
if os.path.exists(os.path.join(D, 'voz.mp3')):
    os.remove(os.path.join(D, 'voz.mp3'))
# (12-nov-2026, 15 h) Pablo vuelve a la voz de GEMINI (Puck) de siempre; Qwen solo de RESERVA si Gemini no puede
r = subprocess.run(['python3', os.path.join(PLAT, 'v2', 'voz.py'), D, '--voz', 'Puck', '--tono', 'noticias_grave' if GRAVE else 'noticias'],
                   capture_output=True, text=True, env=dict(os.environ, VOZ_ESTRICTA='1', VOZ_REINICIA='1', VOZ_CPS='13.5'), timeout=2400)
VOZ_USADA = 'Gemini Puck'
if r.returncode or 'PLAN C' in r.stdout or not os.path.exists(os.path.join(D, 'voz.mp3')):
    print('voz Gemini no disponible, paso a la voz de reserva Qwen: ' + (r.stdout + r.stderr)[-300:], flush=True)
    if os.path.exists(os.path.join(D, 'voz.mp3')):
        os.remove(os.path.join(D, 'voz.mp3'))
    r = subprocess.run(['python3', os.path.join(KIT, 'voz_qwen.py'), D, '--voz', 'sinhumo'],
                       capture_output=True, text=True, timeout=3 * 3600)
    VOZ_USADA = 'Qwen (reserva)'
    if r.returncode or not os.path.exists(os.path.join(D, 'voz.mp3')):
        sys.exit('FALLO voz: ' + (r.stdout + r.stderr)[-400:])
print('\n'.join(r.stdout.strip().splitlines()[-12:]), '·', VOZ_USADA, flush=True)

# ---------- 5) MONTAJE con el kit: alineado, tiempos, render, mezcla, miniatura ----------
print('· montaje', flush=True)
corre(['python3', 'alinear.py', D], timeout=1800)
print(corre(['python3', 'audio.py', D]).strip().splitlines()[-1], flush=True)
corre(['node', 'render.js', D, 'video'], timeout=3 * 3600)
corre(['python3', 'mezcla.py', D], timeout=3600)
if not os.path.exists(os.path.join(D, 'video_final.mp4')):
    sys.exit('FALLO montaje: no hay video_final.mp4')

# ---------- 6) TÍTULO, DESCRIPCIÓN Y MINIATURA ----------
cap_txt = open(os.path.join(D, 'capitulos.txt')).read().strip() if os.path.exists(os.path.join(D, 'capitulos.txt')) else ''
T = gemini(f'Vídeo de YouTube de sin humo TV (unos 8 minutos) sobre: «{P["titulo_noticia"]}». Resumen de los hechos: {N["hechos"][:1500]}\n'
           'Escribe 5 títulos (≤ 70 caracteres) y elige el más fuerte. El título EMPIEZA por las palabras que la gente escribe en el buscador de YouTube '
           '(el asunto y su fecha: «Huelga general 11 de noviembre», «Cambio de hora», «Voto por correo 29-N») y sigue con la duda práctica que resuelve el vídeo '
           '(«¿te descuentan el día?», «¿es el último?», «qué cambia para ti»). Los dos títulos que mejor han funcionado en el canal: «Huelga general 11 de '
           'noviembre: ¿te descuentan el día? Todo explicado» y «Cambio de hora: ¿es el último? Todo lo que debes saber en 8 minutos». Promesa cierta, sin clickbait falso. '
           'Miniatura (NUNCA repite el título, lo complementa con un dato, urgencia o pregunta): l1 y l2, las DOS obligatorias, cada una de 1-2 palabras y como mucho 12 caracteres '
           '(l1 = de qué va, l2 = lo que impacta: «SUPREMO» / «DICE NO»; una cifra solo si se dice en el vídeo) '
           'y sub (franja corta ≤ 45 caracteres). Descripción: 2-3 líneas con las palabras que la gente busca. Etiquetas: 6-8 términos de búsqueda. '
           'Pregunta neutral para comentar. Responde solo JSON: {"titulo":"","l1":"","l2":"","sub":"","descripcion":"","etiquetas":[],"pregunta":""}', 0.7)
titulo = str(T.get('titulo') or P['titulo_noticia'])[:70]
todo_dicho = ' '.join(e['subtitulo'] for e in escenas)
for campo in ('l1', 'l2', 'sub'):   # (8-nov-2026) la miniatura tampoco puede llevar cifras que no diga el vídeo
    for x in re.findall(r'\d[\d.,]*', str(T.get(campo) or '')):
        if _dig(x) not in [_dig(y) for y in re.findall(r'\d[\d.,]*', todo_dicho)]:
            print(f'miniatura: «{T.get(campo)}» lleva una cifra que no se dice → fuera', flush=True); T[campo] = ''
if not (T.get('l1') or T.get('l2')): T['l1'] = ' '.join(P['titulo_noticia'].upper().split()[:2])[:16]
# (10-nov-2026) el titular de la miniatura siempre con DOS líneas (una sola palabra, «VOTO», no decía nada): la que falte se saca del
# título del vídeo (la palabra con mayúscula más larga que no esté ya; si no hay, la más larga)
def _linea_extra(ya):
    pal = [re.sub(r'[^\wáéíóúñüÁÉÍÓÚÑÜ-]', '', w) for w in titulo.split()]
    pal = [w for w in pal if len(w) >= 4 and not re.search(r'\d', w) and w.upper() not in ya.upper().split()]
    prop = [w for w in pal[1:] if w[:1].isupper()] or pal
    return max(prop, key=len).upper()[:14] if prop else ''
T['l1'], T['l2'] = str(T.get('l1') or '').strip(), str(T.get('l2') or '').strip()
if T['l1'] and not T['l2']:
    ws = T['l1'].split()
    if len(ws) >= 2: T['l1'], T['l2'] = ' '.join(ws[:-1]), ws[-1]
    else: T['l2'] = T['l1']; T['l1'] = _linea_extra(T['l2'])
elif T['l2'] and not T['l1']: T['l1'] = _linea_extra(T['l2'])
def _corta(t, n):   # (9-nov-2026) cortar por palabras enteras, nunca a mitad de palabra
    t = ' '.join(str(t or '').split())
    return t if len(t) <= n else t[:n + 1].rsplit(' ', 1)[0].rstrip(' ,;:-')
for n, f in enumerate(fotos[:2]):
    os.makedirs(os.path.join(D, f'v{n + 1}'), exist_ok=True)
    corre(['node', 'miniatura.js', os.path.join(D, f'v{n + 1}'), json.dumps({'l1': str(T.get('l1') or '')[:16], 'l2': str(T.get('l2') or '')[:14],
          'sub': _corta(T.get('sub'), 60), 'color': 'rojo', 'expr': 'seria' if GRAVE else 'sorprendida', 'fondo': 'oscuro',
          'foto': f['ruta'], 'credito': 'Foto: ' + f['credito']}, ensure_ascii=False)])
subprocess.run(['cp', os.path.join(D, 'v1', 'miniatura.jpg'), os.path.join(D, 'miniatura.jpg')], check=True)
enl = '\n'.join(f'{fu}: {u}' for fu, u in zip(N.get('fuentes') or [], N.get('enlaces') or []))
desc = (f"{str(T.get('descripcion') or '').strip()}\n\nCapítulos:\n{cap_txt}\n\nFuentes:\n{enl}\n\n{str(T.get('pregunta') or '').strip()}\n\n"
        f"Fotos: {' | '.join(f['credito'] for f in fotos)}\nVoz: generada con IA (Gemini).\n\n"
        f"Suscríbete a sin humo TV para entender la actualidad, sin humo.\n\n" + ' '.join('#' + re.sub(r'\W', '', str(t)) for t in (T.get('etiquetas') or [])[:4]))
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', os.path.join(D, 'video_final.mp4')],
                           capture_output=True, text=True).stdout or 0)
json.dump({'titulo': titulo, 'descripcion': desc, 'etiquetas': [str(t) for t in (T.get('etiquetas') or [])][:8], 'duracion': round(dur, 1),
           'escenas': len(escenas), 'fotos': len(fotos), 'tema': N['tema']}, open(os.path.join(D, 'largo.json'), 'w'), ensure_ascii=False)
print(f'OK · {dur:.0f} s · {len(escenas)} escenas · {len(fotos)} fotos · «{titulo}»', flush=True)
