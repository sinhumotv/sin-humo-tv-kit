#!/usr/bin/env python3
"""(14-nov-2026) PONGAMOS QUE · LARGO DE YOUTUBE (horizontal, ~5 min, con el efecto 3D; sin animación IA).
Uso: python3 largo.py <carpeta_explicalo> <salida>
Tema nuevo con Gemini (lista propia: temas_largos.json) → motor de Explícalo (estructura «pongamosque», horizontal) →
<salida>/video.mp4 + publicacion.json (para metricool/publicar_largo.py; la miniatura la hace metricool/miniatura_explicalo.py)."""
import json, os, subprocess, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
EXP, SAL = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.makedirs(SAL, exist_ok=True)
env = dict(os.environ, TEMAS_HECHOS='temas_largos.json', TEMAS_FORMATO='vídeos largos de YouTube (5 minutos)')
r = subprocess.run([sys.executable, os.path.join(AQUI, 'temas.py'), '1', f'{SAL}/tema.json'], env=env)
if r.returncode: sys.exit('no hay tema')
t = json.load(open(f'{SAL}/tema.json'))[0]
d = os.path.join(SAL, 'v')
os.makedirs(d, exist_ok=True)
json.dump({'tipo': 'explica', 'tema': t['tema'], 'duracion': 300, 'formato': 'horizontal', 'tema_visual': 'pongamosque', 'voz': 'Puck',
           'estructura_fija': True}, open(f'{d}/pedido_in.json', 'w'), ensure_ascii=False)
r = subprocess.run([sys.executable, os.path.join(EXP, 'plataforma/v2/fabricar.py'), f'{d}/pedido_in.json', d], cwd=EXP,
                   env=dict(os.environ, PQ_IMG_NORMAL='1', WHISPER_MODELO='small'))
if r.returncode or not os.path.exists(f'{d}/video_final.mp4'): sys.exit('el largo no ha salido')
os.replace(f'{d}/video_final.mp4', f'{SAL}/video.mp4')
tags = [str(h).lstrip('#') for h in (t.get('hashtags') or [])]
desc = (f"{t.get('gancho') or t['tema']}\n\nDel segundo 0 al año 100: qué pasaría, paso a paso, según lo que creen los científicos "
        f"(es ciencia especulativa).\n\n{t.get('pregunta') or '¿Tú qué harías?'} Te leo en comentarios 👇\n\n"
        + ' '.join('#' + x for x in (['pongamosque'] + tags)[:6]))
json.dump({'titulo': t.get('titulo') or t['tema'], 'tema': t['tema'], 'descripcion': desc[:4900], 'etiquetas': (['pongamos que', 'que pasaria si'] + tags)[:15],
           'categoria': 'SCIENCE_TECHNOLOGY', 'fecha': os.environ.get('PQ_FECHA', 'ahora')}, open(f'{SAL}/publicacion.json', 'w'), ensure_ascii=False, indent=1)
print('largo listo:', t['tema'])
