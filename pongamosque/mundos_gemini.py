#!/usr/bin/env python3
"""(17-nov-2026) Pongamos Que · vídeos de GEMINI sobre los MUNDOS 3D de la biblioteca hecha por Claude.
Uso: python3 mundos_gemini.py <cuántos> <carpeta_salida>   → <salida>/g1.json, g2.json… (mismo formato que los de Claude)

Claude construye cada día mundos 3D a medida (pongamosque/claude/mundos/<id>.json: el código del mundo, sus vistas, sus
opciones de estado y TOMAS de cámara ya revisadas). Gemini NO toca el 3D: solo escribe un «Pongamos que…» NUEVO que pase
en ese mundo (escalera de tiempo SEGUNDO 0 → AÑO 100) y, para cada frase, elige la toma que la enseña y el estado del
mundo (roto, días, cielo…). Así sale al nivel de los de Claude sin gastar uso de Claude.
Reglas para que no se repita: un mundo no vuelve a salir hasta pasados PQ_MUNDO_DIAS días (7) y nunca con un tema ya
hecho; se eligen primero los que llevan más tiempo sin usarse. Si no hay mundos libres, escribe menos (el resto lo
hace el sistema de siempre). Se apunta el uso en el propio mundo."""
import datetime, glob, json, os, random, re, sys, time, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
MUNDOS = os.path.join(AQUI, 'claude', 'mundos')
HECHOS = os.path.join(AQUI, 'temas_hechos.json')
N, SAL = int(sys.argv[1]), sys.argv[2]
DIAS = int(os.environ.get('PQ_MUNDO_DIAS', '7'))
HOY = datetime.date.today()
ESCALERA = ['SEGUNDO 0', 'MINUTO 1', 'HORA 1', 'DÍA 1', 'SEMANA 1', 'MES 1', 'AÑO 1', 'AÑO 100']
UNIDADES = ['SEGUNDO', 'MINUTO', 'HORA', 'DÍA', 'SEMANA', 'MES', 'AÑO']
CIELOS = ['dia', 'atardecer', 'amanecer', 'noche', 'tormenta']
MODELOS = ['gemini-3.5-flash', 'gemini-3.8-flash'] * 3


def gemini(prompt):
    clave = os.environ['GEMINI_API_KEY'].strip()
    for i, m in enumerate(MODELOS):
        if i: time.sleep(min(120, 20 * i))
        try:
            req = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={clave}',
                                         json.dumps({'contents': [{'parts': [{'text': prompt}]}],
                                                     'generationConfig': {'temperature': 0.9, 'responseMimeType': 'application/json'}}).encode(),
                                         {'Content-Type': 'application/json'})
            t = json.load(urllib.request.urlopen(req, timeout=180))['candidates'][0]['content']['parts'][0]['text']
            return json.loads(re.sub(r'^```(json)?|```$', '', t.strip()))
        except Exception as x:
            print('gemini', m, 'falló:', str(x)[:150], flush=True)
    return None


def ultimo_uso(W):
    fs = [datetime.date.fromisoformat(u['fecha']) for u in W.get('usos', [])]
    return max(fs) if fs else datetime.date(2000, 1, 1)


def prompt(W, hechos, error=''):
    tomas = [{'toma': t['id'], 'vista': t['vista'], 'se_ve': t['se_ve'],
              'estado_en_el_ejemplo': {k: v for k, v in t['escena3d']['objetos'][0].items() if k not in ('tipo', 'tam', 'vista')}} for t in W['tomas']]
    estado = {k: v for k, v in W['opciones'].items() if k != 'vista'}
    return f"""Eres guionista del canal de TikTok/YouTube «Pongamos que…» (español de España, tono cercano, datos reales y sorprendentes).
Cada vídeo es un ESCENARIO HIPOTÉTICO: la primera frase empieza literalmente por «Pongamos que…» y el vídeo avanza por la escalera de tiempo
{' → '.join(ESCALERA)} con consecuencias cada vez mayores (no hace falta usar todos los peldaños y puedes usar intermedios como «HORA 6» o «DÍA 3», pero siempre hacia delante), y termina con una pregunta al espectador.

Este vídeo pasa ENTERO dentro de este mundo 3D (ya construido; no se puede añadir nada que no esté en él):
MUNDO: {W['nombre']}. {W['descripcion']}
ESTADOS que puedes cambiar en cada escena: {json.dumps(estado, ensure_ascii=False)}
TOMAS de cámara disponibles (cada una enseña una parte concreta del mundo; «se_ve» es la frase para la que se diseñó, como pista de lo que enseña):
{json.dumps(tomas, ensure_ascii=False)}

Escribe un «Pongamos que…» NUEVO que ocurra en este mundo. Ideas posibles (o inventa otra mejor): {json.dumps(W.get('ideas', []), ensure_ascii=False)}
PROHIBIDO repetir o parafrasear estos temas ya hechos: {json.dumps([u['tema'] for u in W.get('usos', [])] + hechos[-80:], ensure_ascii=False)}

Reglas:
- 9 a 11 escenas; cada «hablado» es UNA frase corta (6-16 palabras), en total 90-130 palabras. Datos verdaderos; nada de política, religión ni personas reales vivas.
- Cada escena elige la «toma» que enseña JUSTO lo que dice la frase, y el «estado» del mundo en ese momento (solo claves de ESTADOS; {{}} si nada cambia).
  No repitas la misma toma en dos escenas seguidas y usa al menos 5 tomas distintas.
- «visual»: o bien {{"tipo":"dia","texto":"<peldaño de la escalera>","detalle":"2-3 palabras"}} o bien {{"tipo":"cifra","valor":"<número corto>","etiqueta":"3-5 palabras"}}.
  Los peldaños («texto») van de menor a mayor a lo largo del vídeo y la última escena usa el más alto que hayas alcanzado.
- «cielo»: uno de {CIELOS}; que encaje con la historia (y que no sea el mismo en todo el vídeo si el tiempo avanza días).
- «alejar»: true si la cámara debe alejarse (para frases de conclusión o de escala), false si se acerca.
{('ATENCIÓN, el intento anterior estaba mal: ' + error) if error else ''}
Responde SOLO con JSON:
{{"meta":{{"tema":"¿Qué pasaría si …?","titulo":"¿Y si …? <1 emoji> (máx. 60 caracteres)","gancho":"frase para el pie del vídeo","pregunta":"la pregunta final","hashtags":["5 hashtags sin #, el 4º «quepasariasi»"]}},
 "escenas":[{{"hablado":"Pongamos que …","visual":{{…}},"toma":"t1","estado":{{}},"cielo":"noche","alejar":false}}, …]}}"""


def validar(W, G):
    if not isinstance(G, dict) or not isinstance(G.get('escenas'), list) or not isinstance(G.get('meta'), dict): return 'falta meta o escenas'
    E = G['escenas']; ids = {t['id'] for t in W['tomas']}; est = set(W['opciones']) - {'vista'}
    if not 8 <= len(E) <= 12: return f'hay {len(E)} escenas (tienen que ser 9-11)'
    if not str(E[0].get('hablado', '')).strip().startswith('Pongamos que'): return 'la primera frase no empieza por «Pongamos que»'
    if not str(E[-1].get('hablado', '')).strip().endswith('?'): return 'la última frase no es una pregunta'
    pal = sum(len(str(e.get('hablado', '')).split()) for e in E)
    if not 75 <= pal <= 150: return f'el guion tiene {pal} palabras (tienen que ser 90-130)'
    nivel = (-1, 0)
    for i, e in enumerate(E):
        if e.get('toma') not in ids: return f'la escena {i + 1} usa la toma «{e.get("toma")}», que no existe'
        if i and e['toma'] == E[i - 1]['toma']: return f'las escenas {i} y {i + 1} repiten la misma toma'
        if not isinstance(e.get('estado', {}), dict) or set(e.get('estado') or {}) - est: return f'la escena {i + 1} usa estados que no existen'
        v = e.get('visual') or {}
        if v.get('tipo') == 'dia':
            mm = re.fullmatch(r'(SEGUNDO|MINUTO|HORA|DÍA|SEMANA|MES|AÑO)S? (\d+)', str(v.get('texto', '')).strip().upper())
            if not mm: return f'la escena {i + 1} tiene un peldaño que no es de la escalera: {v.get("texto")}'
            k = (UNIDADES.index(mm.group(1)), int(mm.group(2)))
            if k < nivel: return f'la escalera de tiempo va hacia atrás en la escena {i + 1}'
            nivel = k
        elif v.get('tipo') != 'cifra': return f'la escena {i + 1} tiene un visual raro'
    if len({e['toma'] for e in E}) < 5: return 'usa menos de 5 tomas distintas'
    if not G['meta'].get('tema') or not G['meta'].get('titulo'): return 'falta el tema o el título'
    return ''


def construir(W, G):
    tomas = {t['id']: t for t in W['tomas']}; esc = []
    for e in G['escenas']:
        d = json.loads(json.dumps(tomas[e['toma']]['escena3d'])); o0 = d['objetos'][0]
        o = {'tipo': 'nueva', 'codigo': W['codigo'], 'tam': o0['tam'], 'reserva': W.get('reserva', 'bloque'), 'vista': o0.get('vista', 'todo')}
        o.update({k: v for k, v in (e.get('estado') or {}).items() if k in W['opciones'] and k != 'vista'})
        d['objetos'] = [o] + d['objetos'][1:]
        if e.get('cielo') in CIELOS and d.get('cielo') != 'espacio': d['cielo'] = e['cielo']
        r = d.get('ruta')
        if r and bool(e.get('alejar')) != tomas[e['toma']].get('aleja', False):   # se invierte el recorrido de la toma
            inv = lambda q: dict(q, de=q['a'], a=q['de'], mira=q.get('mira2', q.get('mira')), mira2=q.get('mira'))
            d['ruta'] = [inv(q) for q in r] if isinstance(r, list) else inv(r)   # (17-nov-2026) una toma puede tener varios planos
        if not r: d['camara'] = 'alejar' if e.get('alejar') else (d.get('camara') if d.get('camara') not in (None, 'alejar') else 'acercar')
        if d.get('cielo') != 'tormenta': d.pop('efecto', None)
        h = str(e['hablado']).strip()
        esc.append({'hablado': h, 'subtitulo': h, 'visual': e['visual'], 'escena3d': d})
    m = G['meta']; m['hashtags'] = [str(x).lstrip('#') for x in (m.get('hashtags') or [])][:7] or ['pongamosque', 'quepasariasi']
    return {'titulo': m['titulo'], 'meta': m, 'mundo': W['id'], 'autor': 'gemini', 'escenas': esc}


def main():
    os.makedirs(SAL, exist_ok=True)
    hechos = json.load(open(HECHOS)) if os.path.exists(HECHOS) else []
    mundos = []
    for f in glob.glob(os.path.join(MUNDOS, '*.json')):
        W = json.load(open(f)); W['_f'] = f
        if (HOY - ultimo_uso(W)).days >= DIAS and W.get('tomas'): mundos.append(W)   # (18-nov-2026) los mundos del estilo nuevo (sin tomas) los usará el generador nuevo
    random.shuffle(mundos); mundos.sort(key=ultimo_uso)
    print(f'mundos libres: {[W["id"] for W in mundos]} (de {len(glob.glob(os.path.join(MUNDOS, "*.json")))})', flush=True)
    hechos_n = 0
    for W in mundos:
        if hechos_n >= N: break
        err, V = '', None
        for _ in range(3):
            G = gemini(prompt(W, hechos, err))
            if G is None: break
            err = validar(W, G)
            if not err and G['meta']['tema'] in hechos: err = 'ese tema ya está hecho'
            if not err: V = construir(W, G); break
            print(f'[{W["id"]}] guion rechazado: {err}', flush=True)
        if not V: continue
        hechos_n += 1
        json.dump(V, open(os.path.join(SAL, f'g{hechos_n}.json'), 'w'), ensure_ascii=False, indent=1)
        f = W.pop('_f'); W.setdefault('usos', []).append({'fecha': HOY.isoformat(), 'tema': V['meta']['tema'], 'por': 'gemini'})
        json.dump(W, open(f, 'w'), ensure_ascii=False, indent=1)
        hechos.append(V['meta']['tema'])
        print(f'[{W["id"]}] {V["titulo"]} · ' + ' | '.join(e['hablado'] for e in V['escenas']), flush=True)
    print(f'vídeos de Gemini sobre mundos: {hechos_n} de {N}', flush=True)


if __name__ == '__main__':
    main()
