#!/usr/bin/env python3
"""GUION CON IA (Explícalo) — escribe el CONTENIDO de un vídeo (formato de guion/guion.js) sobre el tema del cliente con Gemini
(capa gratuita de Google AI Studio). La clave va en la variable GEMINI_API_KEY (secreto de Modal «explicalo-gemini»), nunca en el código.

  python3 plataforma/guion/ia.py <pedido.json> <contenido.json>

- Pide el plan (escenas y palabras) a desde_pedido.js, elige plantilla y escribe en español de España.
- Comprueba el resultado con generarProyecto() y, si hay avisos graves (faltan partes, muy largo o muy corto), lo corrige una vez.
- Prueba varios modelos «flash» (los que la cuenta tenga disponibles) por si uno agota su cuota gratuita.
Sale con 2 si no hay clave o ningún modelo responde (la fábrica usa entonces un guion de muestra y lo avisa)."""
import json, os, re, subprocess, sys, tempfile, urllib.request, urllib.error

AQUI = os.path.dirname(os.path.abspath(__file__))
PLAT = os.path.dirname(AQUI)
API = 'https://generativelanguage.googleapis.com/v1beta'
PREFERIDOS = ['gemini-3.5-flash', 'gemini-3.1-flash', 'gemini-3-flash', 'gemini-3.8-flash', 'gemini-3.8-flash-lite']   # (8-nov-2026) gemini-3.8-flash se queda colgado (>100 s): al final   # (7-nov-2026) Google retiró gemini-2.5-flash: daba 404
ICONOS = ['moneda', 'carrito', 'banco', 'termometro', 'barril', 'rayo', 'globo', 'persona', 'cartera', 'alerta', 'reloj', 'calendario', 'vela',
          'escudo', 'casa', 'corona', 'olas', 'gente', 'documento', 'edificio', 'coche', 'medalla', 'mazo', 'balanza', 'paloma', 'pin']

FORMATO = """Devuelve SOLO un objeto JSON con este formato (contenido de un vídeo explicativo corto):
{ "plantilla": "pasos" | "mito_realidad" | "top3" | "antes_despues" | "explicacion",
  "titulo": "título del vídeo (máx. 60 caracteres)",
  "gancho": PARTE,            // primera frase: engancha en 3 segundos (pregunta «¿Y si…?», dato sorprendente o problema)
  …partes de la plantilla…,
  "cierre": PARTE }           // última frase: pregunta para comentar («Te leo en comentarios») o idea final
Partes según la plantilla:
  pasos:         "pasos": [PARTE × 2-5], "resumen": PARTE opcional
  mito_realidad: "mito": PARTE, "realidad": PARTE, "explicacion": [PARTE × 0-3]
  top3:          "items": [PARTE × 3]  (del número 3 al número 1)
  antes_despues: "antes": PARTE, "despues": PARTE, "diferencia": PARTE opcional
  explicacion:   "claves": [PARTE × 2-4]
PARTE = { "voz": "lo que se dice (1-2 frases naturales, para escuchar)",
          "titulo": "cabecera de la escena, MÁX. 22 caracteres, concreta e intrigante (nunca «Clave 1», «Paso 2» ni «Explicación»)",
          "texto": "rótulo corto en pantalla (máx. 34 caracteres)",
          "valor": "cifra grande opcional, máx. 8 caracteres (p. ej. «70 %», «8 h», «x600», «1969») — SOLO si es un dato real y seguro",
          "dibujo": una ilustración de DIBUJOS que represente esa parte (ponla SIEMPRE, la más concreta posible),
          "esquema": "flecha" (causa → efecto, A → B → C) | "grupo" (varias cosas alrededor de la idea) | "proceso" (pasos 1-2-3) |
                     "versus" (A frente a B) | "lista" (filas con ✓),
          "elementos": [ 2-4 × { "dibujo": clave de DIBUJOS, "texto": rótulo de 1-2 palabras (máx. 16), "palabra": UNA palabra que
                         aparece LITERALMENTE en "voz" en el momento en que debe aparecer ese dibujo } ]
                     → la escena se monta en pantalla mientras se habla: usa elementos en casi todas las partes (no en la que lleve "valor"),
          "color": "rojo|azul|verde|oro|naranja|morado" (opcional) }
En "texto" puedes marcar UNA palabra clave entre *asteriscos*."""


def dibujos():
    out = subprocess.run(['node', '-e', f'console.log(JSON.stringify(require({json.dumps(os.path.join(PLAT, "dibujos", "dibujos.js"))}).CLAVES))'],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def clave():
    k = os.environ.get('GEMINI_API_KEY', '').strip()
    if not k or k.lower() == 'ninguna': sys.exit(2)
    return k


def peticion(url, cuerpo=None, timeout=90):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(url, data=datos, headers={'content-type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def modelos(k):
    try:
        lista = [m['name'].split('/')[-1] for m in peticion(f'{API}/models?key={k}&pageSize=200').get('models', [])
                 if 'generateContent' in m.get('supportedGenerationMethods', [])]
    except Exception:
        return PREFERIDOS
    ok = [m for m in lista if 'flash' in m and not re.search(r'tts|image|live|audio|embed|thinking|vision', m) and not m.startswith('gemini-2.5')]
    orden = [m for m in PREFERIDOS if m in ok] + sorted([m for m in ok if m not in PREFERIDOS], reverse=True)
    return orden[:6] or PREFERIDOS


def _una(k, m, texto, temperatura, timeout):
    r = peticion(f'{API}/models/{m}:generateContent?key={k}', {
        'contents': [{'role': 'user', 'parts': [{'text': texto}]}],
        'generationConfig': {'temperature': temperatura, 'responseMimeType': 'application/json'}}, timeout=timeout)
    t = r['candidates'][0]['content']['parts'][0]['text']
    return json.loads(t[t.index('{'):t.rindex('}') + 1]), m


def preguntar(k, texto, temperatura=0.8, timeout=90, relevo=None):
    """relevo (segundos): si el modelo no contesta en ese tiempo, se lanza ya el siguiente sin cortar el primero y vale
    la primera respuesta buena (8-nov-2026: a veces un modelo se queda colgado más de 100 s y el cliente esperaba)."""
    if relevo:
        import queue, threading
        cola, ms, vivos, ultimo = queue.Queue(), list(modelos(k)), 0, None
        def lanzar():
            m = ms.pop(0)
            def h():
                try: cola.put(('ok', _una(k, m, texto, temperatura, timeout)))
                except Exception as e: cola.put(('mal', f'{m}: {e}'))
            threading.Thread(target=h, daemon=True).start()
        lanzar(); vivos = 1
        while vivos:
            try: est, v = cola.get(timeout=relevo)
            except queue.Empty:
                if ms: lanzar(); vivos += 1
                continue
            vivos -= 1
            if est == 'ok': return v
            ultimo = v
            if ms: lanzar(); vivos += 1
        print('ningún modelo responde:', ultimo, file=sys.stderr); sys.exit(2)
    ultimo = None
    for m in modelos(k):
        try:
            r = peticion(f'{API}/models/{m}:generateContent?key={k}', {
                'contents': [{'role': 'user', 'parts': [{'text': texto}]}],
                'generationConfig': {'temperature': temperatura, 'responseMimeType': 'application/json'}}, timeout=timeout)
            t = r['candidates'][0]['content']['parts'][0]['text']
            return json.loads(t[t.index('{'):t.rindex('}') + 1]), m
        except (urllib.error.HTTPError, urllib.error.URLError, KeyError, IndexError, ValueError, TimeoutError) as e:
            ultimo = f'{m}: {e}'
    print('ningún modelo responde:', ultimo, file=sys.stderr); sys.exit(2)


def node(*args):
    r = subprocess.run(['node', os.path.join(PLAT, 'produccion', 'desde_pedido.js'), *args], capture_output=True, text=True)
    return r.returncode, (r.stdout or r.stderr).strip().split('\n')[-1]


def planteamiento(pe):
    out = subprocess.run(['node', '-e', f'console.log(JSON.stringify(require({json.dumps(os.path.join(AQUI, "planteamientos.js"))}).PLANTEAMIENTOS))'],
                         capture_output=True, text=True, check=True).stdout
    todos = json.loads(out)
    return todos.get(pe.get('planteamiento') or 'auto') or todos['auto']


def instrucciones(pe, plan):
    p, pl = plan['peticion'], plan['plan']
    pt = planteamiento(pe)
    obligado = (f'\nPLANTEAMIENTO OBLIGATORIO: «{pt["nombre"]}». {pt["guia"]}' + (f' Usa la plantilla "{pt["plantilla"]}".' if pt.get('plantilla') else '')) if pt.get('plantilla') else '\n' + pt['guia']
    return f"""Eres guionista de vídeos cortos explicativos para redes sociales (TikTok, Reels, Shorts), en ESPAÑOL DE ESPAÑA
(vocabulario y expresiones de España: «ordenador», «móvil», «coche», «vale»; nada de «ustedes» para la 2.ª persona del plural).
Tema que pide el cliente: «{p['tema']}»
Tono: {p['tono']}. Duración: {p['duracion']} s → unas {pl['palabras']} palabras habladas EN TOTAL, repartidas en {pl['escenas'][0]}-{pl['escenas'][1]} partes
(contando gancho y cierre). Frases cortas, claras y con ritmo; tutea al espectador; nada de relleno ni de «en este vídeo».
Reglas: contenido veraz y prudente (si un dato no es seguro, no pongas cifra); nada de política partidista, insultos, contenido
sexual, violencia ni consejos médicos o financieros peligrosos; no menciones marcas reales salvo que el tema lo pida; nunca
nombres a «sin humo TV».{obligado}
DIBUJOS disponibles (usa exactamente estas claves): {', '.join(dibujos())}.
{FORMATO}"""


def main(f_pedido, f_salida):
    k = clave()
    pe = json.load(open(f_pedido))
    cod, sal = node('plan', f_pedido)
    plan = json.loads(sal)
    if plan['filtro']['estado'] == 'bloqueada': print('tema bloqueado por el filtro', file=sys.stderr); sys.exit(3)
    texto = instrucciones(pe, plan)
    contenido, modelo = preguntar(k, texto)
    # comprobación con el generador real; una corrección si hay avisos graves
    for intento in range(2):
        tmp = tempfile.mkdtemp(prefix='guion_')
        fc = os.path.join(tmp, 'contenido.json'); json.dump(contenido, open(fc, 'w'), ensure_ascii=False)
        cod, sal = node('proyecto', f_pedido, fc, tmp)
        avisos = json.loads(sal).get('avisos', []) if sal.startswith('{') else [sal]
        graves = [a for a in avisos if re.search(r'falta|hacen falta|no existe, uso "explicacion"|guion largo|guion corto|no pasa|bloquead', a)]
        if cod == 0 and not graves: break
        if intento == 1: break
        contenido, modelo = preguntar(k, texto + '\n\nTu respuesta anterior:\n' + json.dumps(contenido, ensure_ascii=False) +
                                      '\nTiene estos problemas, corrígelos y devuelve el JSON completo:\n- ' + '\n- '.join(graves or avisos), 0.5)
    contenido['_modelo'] = modelo
    json.dump(contenido, open(f_salida, 'w'), ensure_ascii=False, indent=1)
    print(json.dumps({'modelo': modelo, 'plantilla': contenido.get('plantilla'), 'titulo': contenido.get('titulo'), 'avisos': avisos}, ensure_ascii=False))


if __name__ == '__main__':
    if len(sys.argv) != 3: sys.exit('uso: ia.py <pedido.json> <contenido.json>')
    main(sys.argv[1], sys.argv[2])
