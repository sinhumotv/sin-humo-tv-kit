#!/usr/bin/env python3
"""(8-nov-2026) Noticia de la semana para el LARGO de sin humo TV, en GitHub (copiado del servidor de Explícalo).
Uso: python3 sinhumo_largo/noticia.py <salida.json> <archivo de temas anteriores>   Variables: GEMINI_CLAVES (separadas por comas)."""
import json, os, sys, time, datetime
from zoneinfo import ZoneInfo
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, 'guion'))
import ia  # noqa: E402

def ZoneInfoMadrid():
    return ZoneInfo('Europe/Madrid')

def _sh_claves():
    return [c.strip() for c in os.environ.get('GEMINI_CLAVES', '').split(',') if c.strip()]

def _sh_clave():
    c = _sh_claves()
    return c[0] if c else ''

def _sh_web(url, timeout=30):
    import urllib.request
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; sinhumoTV/1.0; +https://github.com/sinhumotv)'})
    return urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8', 'ignore')

def _sh_ganadores():
    """(10-nov-2026) Temas que están funcionando AHORA en el canal: títulos de los vídeos de los últimos 5 días con muchas más visitas
    que el resto (al menos 300 y el triple de la mediana), leídos del feed público de YouTube (no necesita claves). → lista (máx. 3)."""
    import datetime as _d, html as _h, re as _r
    try:
        x = _sh_web('https://www.youtube.com/feeds/videos.xml?channel_id=UCCz-7FqKL1uEjz3IB2m1xuw', 20)
        ahora, vids = _d.datetime.now(_d.timezone.utc), []
        for e in _r.findall(r'<entry>(.*?)</entry>', x, _r.S):
            t, p, v = _r.search(r'<title>(.*?)</title>', e, _r.S), _r.search(r'<published>(.*?)</published>', e), _r.search(r'<media:statistics views="(\d+)"', e)
            if t and p and v:
                vids.append(((ahora - _d.datetime.fromisoformat(p.group(1))).total_seconds() / 3600, int(v.group(1)), _h.unescape(t.group(1)).strip()))
        if len(vids) < 5: return []
        mediana = sorted(v for _, v, _ in vids)[len(vids) // 2]
        gan = sorted([(v, t) for h, v, t in vids if h <= 120 and v >= max(300, 3 * mediana)], reverse=True)
        return [f'«{t}» ({v} visitas)' for v, t in gan[:3]]
    except Exception as x:
        print('ganadores:', str(x)[:100]); return []


def _sh_gemini(k, texto, temperatura=0.3):
    import urllib.error
    errores = []
    for intento in range(4):
        for k2 in list(dict.fromkeys([k] + _sh_claves())):
            for m in ia.modelos(k2)[:6]:
                try:
                    r = ia.peticion(f'{ia.API}/models/{m}:generateContent?key={k2}', {'contents': [{'role': 'user', 'parts': [{'text': texto}]}],
                                    'generationConfig': {'temperature': temperatura, 'responseMimeType': 'application/json'}}, timeout=180)
                    t = r['candidates'][0]['content']['parts'][0]['text']
                    return json.loads(t[t.index('{'):t.rindex('}') + 1]), m
                except urllib.error.HTTPError as e:
                    errores.append(f'{m}: {e.code}')
                except Exception as e:
                    errores.append(f'{m}: {str(e)[:120]}')
        time.sleep(20 * (intento + 1))
    raise RuntimeError('Gemini no responde: ' + (errores[-1] if errores else '?'))

SH_FEEDS = {   # portadas en RSS de medios españoles (si alguna falla, se sigue con las demás)
    'Europa Press': 'https://www.europapress.es/rss/rss.aspx',
    'RTVE': 'https://api2.rtve.es/rss/temas_noticias.xml',
    '20minutos': 'https://www.20minutos.es/rss/',
    'El País': 'https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada',
    'elDiario.es': 'https://www.eldiario.es/rss/',
    'La Vanguardia': 'https://www.lavanguardia.com/rss/home.xml',
    'El Mundo': 'https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml',
    'ABC': 'https://www.abc.es/rss/2.0/portada/',
}


def _sh_noticia_larga(previos):
    """Noticia de la semana para el largo: titulares de las portadas (RSS), Gemini elige la que más merece explicarse a fondo
    (al menos 2 medios), se leen hasta 4 artículos y Gemini escribe 450-700 palabras SOLO con lo que dicen. → dict."""
    import datetime, email.utils, html, re as _re
    k = _sh_clave()
    if not k: raise RuntimeError('falta la clave de Gemini de sin humo TV')
    ahora = datetime.datetime.now(datetime.timezone.utc)
    items = []
    for medio, url in SH_FEEDS.items():
        try: x = _sh_web(url)
        except Exception as e: print('rss', medio, str(e)[:80]); continue
        for it in _re.findall(r'<item\b.*?</item>', x, _re.S)[:30]:
            g = lambda tag: html.unescape(_re.sub(r'<!\[CDATA\[|\]\]>|<[^>]+>', ' ', (_re.search(rf'<{tag}\b[^>]*>(.*?)</{tag}>', it, _re.S) or [None, ''])[1])).strip()
            try: fecha = email.utils.parsedate_to_datetime(g('pubDate'))
            except Exception: fecha = None
            if fecha and (ahora - fecha).total_seconds() > 48 * 3600: continue
            if g('title') and g('link'):
                items.append({'medio': medio, 'titulo': ' '.join(g('title').split())[:160], 'resumen': ' '.join(g('description').split())[:240], 'url': g('link').split()[0]})
    if len({i['medio'] for i in items}) < 2: raise RuntimeError(f'no se han podido leer las portadas ({len(items)} titulares)')
    lista = '\n'.join(f'{i}. [{x["medio"]}] {x["titulo"]} — {x["resumen"][:160]}' for i, x in enumerate(items[:200]))
    hoy = datetime.datetime.now(ZoneInfoMadrid()).strftime('%d/%m/%Y')
    _gan = _sh_ganadores()
    if _gan: print('temas que están funcionando:', '; '.join(_gan))
    el, _ = _sh_gemini(k, (
        f'Hoy es {hoy}. Eres el editor de «sin humo TV», canal de YouTube de noticias para España que explica la actualidad sin humo. '
        'Titulares de las portadas de hoy y ayer:\n' + lista + '\n\nElige UNA noticia de esta semana que merezca un vídeo de 8 minutos que la explique '
        'a fondo: la que más se está buscando o comentando en España, la que más afecta a la vida de la gente o la que más dudas genera («qué es», '
        '«cómo me afecta», «qué pasa ahora»). Que la publiquen AL MENOS DOS medios distintos. Nada de deportes, cotilleos ni sucesos morbosos. '
        # (10-nov-2026) datos del canal: 4 de cada 10 visitas llegan por la BÚSQUEDA de YouTube. Los largos que más han funcionado son los de
        # servicio («Huelga general 11 de noviembre: ¿te descuentan el día?», 2.400 visitas; «Cambio de hora: ¿es el último?», 590) y los que
        # menos, los de política de partidos y sondeos (10-100 visitas).
        'PRIORIDAD (lo que de verdad funciona en el canal): 1.º, noticias de SERVICIO que la gente va a buscar estos días porque le tocan el bolsillo, '
        'el trabajo, la casa o un trámite, sobre todo si hay una FECHA cercana (una huelga, un plazo, una subida, una ayuda, una norma que entra en '
        'vigor, cómo votar, un cambio que afecta a todos); 2.º, un suceso grande del que la gente quiere entender qué pasó y qué viene ahora '
        '(accidente, temporal, apagón, investigación). Deja para cuando no haya nada mejor la política de partidos, los sondeos y las '
        'declaraciones: interesan poco y cuesta ser neutral. '
        + (f'TEMAS QUE ESTÁN FUNCIONANDO AHORA en el canal (vídeos de estos días con muchas más visitas que el resto): {"; ".join(_gan)}. Si en los titulares hay NOVEDADES de alguno de esos temas, elige esa noticia y cuéntala desde un ángulo NUEVO (qué ha cambiado, qué viene ahora), aunque el tema ya haya salido en el canal; nunca repitas lo ya contado. ' if _gan else '') +
        f'No repitas tema ni categoría de los últimos largos: {"; ".join(previos[-8:]) or "ninguno"}. '
        'Responde solo JSON: {"numeros": [3 o 4 titulares de medios DISTINTOS sobre esa noticia], "tema": "la noticia en una frase"}'), 0.4)
    nums = [int(n) for n in (el.get('numeros') or []) if str(n).isdigit() and int(n) < len(items)]
    elegidos = [items[n] for n in nums][:4]
    if len({x['medio'] for x in elegidos}) < 2: raise RuntimeError('Gemini no ha encontrado una noticia de dos medios distintos')
    textos = []
    for x in elegidos:
        try:
            pag = _sh_web(x['url'])
            parr = [' '.join(html.unescape(_re.sub(r'<[^>]+>', ' ', p)).split()) for p in _re.findall(r'<p\b[^>]*>(.*?)</p>', pag, _re.S)]
            cuerpo = ' '.join(p for p in parr if len(p) > 60 and not _re.search(r'cookie|suscri|consentimiento|newsletter|\\u00', p, _re.I))[:7000]
        except Exception:
            cuerpo = ''
        textos.append(f'[{x["medio"]}] {x["titulo"]}\n{x["resumen"]}\n{cuerpo or "(no se ha podido leer el artículo; solo titular y entradilla)"}')
    n, modelo = _sh_gemini(k, (
        f'Hoy es {hoy}. Noticia para un vídeo LARGO de «sin humo TV»: {el.get("tema")}.\nTextos de {len(textos)} medios:\n\n' + '\n\n---\n\n'.join(textos) +
        '\n\nEscribe la noticia SOLO con datos de estos textos (las cifras y afirmaciones clave, solo si las dan al menos dos medios; si solo una, '
        '«según <medio>»). No inventes nada. En política, neutral y con el mismo espacio para cada parte. Si hay víctimas, no las identifiques ni a '
        'menores, y nadie es culpable sin condena.\nResponde SOLO JSON: {"tema": "la noticia en una frase de menos de 90 caracteres", '
        '"hechos": "450-700 palabras en español de España, ordenadas así: qué ha pasado (con fechas), contexto y antecedentes, datos clave con cifras, '
        'qué dice cada parte, qué puede pasar ahora y cómo afecta a la gente", "fuentes": ["los medios usados"], "grave": true si hay víctimas o tragedia, '
        '"fotos": ["8 búsquedas DISTINTAS para FOTOS REALES en Wikimedia Commons (cuantas más fotos reales lleve el vídeo, mejor): nombres propios de personas públicas, lugares, edificios, instituciones u '
        'objetos de la noticia; nunca víctimas ni particulares"]}'), 0.3)
    if len(str(n.get('hechos') or '').split()) < 300: raise RuntimeError('la noticia elegida no tiene datos suficientes para un largo')
    n['fuentes'] = [f for f in (n.get('fuentes') or []) if f] or sorted({x['medio'] for x in elegidos})
    n['enlaces'] = [x['url'] for x in elegidos]; n['fuentes_enlaces'] = [x['medio'] for x in elegidos]; n['modelo'] = modelo
    return n


if __name__ == '__main__':
    previos = [l.split('|')[2].strip() for l in open(sys.argv[2], encoding='utf-8') if l.count('|') >= 2] if os.path.exists(sys.argv[2]) else []
    n = _sh_noticia_larga(previos)
    json.dump(n, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False)
    print('NOTICIA:', n['tema'])
