#!/usr/bin/env python3
"""Pongamos Que · elige N temas nuevos («¿Qué pasaría si…?») que enganchen y no se hayan hecho nunca.
Uso: python3 temas.py N salida.json   (lee y amplía pongamosque/temas_hechos.json). Clave: GEMINI_API_KEY."""
import json, os, random, re, sys, urllib.request
AQUI = os.path.dirname(os.path.abspath(__file__))
N, SAL = int(sys.argv[1]), sys.argv[2]
HECHOS = os.path.join(AQUI, os.environ.get('TEMAS_HECHOS', 'temas_hechos.json'))   # (14-nov-2026) los largos llevan su propia lista
hechos = json.load(open(HECHOS)) if os.path.exists(HECHOS) else []
CAMPOS = ['el planeta Tierra', 'el espacio y el Sol', 'el cuerpo humano', 'los animales', 'la tecnología y la energía', 'la historia',
          'la física imposible', 'el clima', 'los océanos', 'la sociedad y el dinero', 'la Luna', 'el tiempo y la gravedad']
random.shuffle(CAMPOS)
FORMATO = os.environ.get('TEMAS_FORMATO', 'vídeos cortos')
P = f"""Eres el guionista del canal de {FORMATO} «Pongamos Que…» (escenarios hipotéticos espectaculares contados del SEGUNDO 0 al AÑO 100).
Propón {N} temas NUEVOS, muy virales y visuales, en español de España, de campos variados (por ejemplo: {', '.join(CAMPOS[:N + 2])}).
Cada tema es un «¿Qué pasaría si…?» concreto y sorprendente que dé ganas de verlo hasta el final (nada de política, religión ni personas reales).
NO repitas ni parafrasees ninguno de estos ya hechos: {json.dumps(hechos[-150:], ensure_ascii=False)}
Responde SOLO con JSON: [{{"tema": "¿Qué pasaría si …?", "titulo": "título corto con gancho (máx. 60 caracteres, 1 emoji al final)",
"gancho": "una frase para el pie del vídeo que enganche", "pregunta": "pregunta para que comenten", "hashtags": ["5-7 hashtags sin #"]}}]"""
clave = os.environ['GEMINI_API_KEY'].strip()
import time
MODELOS = ['gemini-3.5-flash', 'gemini-3.8-flash'] * 4   # si hay cola (429/503) o no responde se espera y se repite (~25 min en total)   # si hay cola (429/503) se espera y se repite
for intento, m in enumerate(MODELOS):
    if intento: time.sleep(min(240, 30 * intento))
    try:
        req = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={clave}',
                                     json.dumps({'contents': [{'parts': [{'text': P}]}], 'generationConfig': {'temperature': 1.0, 'responseMimeType': 'application/json'}}).encode(),
                                     {'Content-Type': 'application/json'})
        t = json.load(urllib.request.urlopen(req, timeout=180))['candidates'][0]['content']['parts'][0]['text']
        temas = json.loads(re.sub(r'^```(json)?|```$', '', t.strip()))
        temas = [x for x in temas if x.get('tema') and x['tema'] not in hechos][:N]
        if temas: break
    except Exception as x:
        print('tema con', m, 'falló:', str(x)[:150], flush=True)
else:
    # (14-nov-2026) Gemini caído un buen rato: nunca se queda el día sin vídeo. Se tiran temas de la reserva (escritos a mano).
    RESERVA = json.load(open(os.path.join(AQUI, 'temas_reserva.json')))
    temas = [x for x in RESERVA if x['tema'] not in hechos]
    random.shuffle(temas)
    temas = temas[:N]
    if not temas: sys.exit('no se pudieron elegir temas')
    print('Gemini no responde: temas de la reserva', flush=True)
json.dump(temas, open(SAL, 'w'), ensure_ascii=False, indent=1)
json.dump(hechos + [x['tema'] for x in temas], open(HECHOS, 'w'), ensure_ascii=False, indent=1)
for x in temas: print('tema:', x['tema'])
