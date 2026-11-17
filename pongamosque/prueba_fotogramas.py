#!/usr/bin/env python3
"""(17-nov-2026) Pongamos Que · fotogramas de prueba de un vídeo de Claude (un fotograma por plano) sin voz ni montaje.
Uso: python3 prueba_fotogramas.py <vN.json> <carpeta_explicalo> <salida>"""
import copy, json, os, subprocess, sys
H = json.load(open(sys.argv[1])); EXP = os.path.abspath(sys.argv[2]); SAL = os.path.abspath(sys.argv[3])
V2 = os.path.join(EXP, 'plataforma', 'v2'); sys.path.insert(0, V2)
import banco
es = []
for e in H['escenas']:
    rs = e['escena3d'].get('ruta'); rs = rs if isinstance(rs, list) else [rs]
    for r in rs:
        d = copy.deepcopy(e['escena3d']); d['ruta'] = r; d.pop('sacudidas', None); es.append(d)
HH = {'titulo': 'prueba', 'escenas': [{'hablado': 'uno dos tres cuatro cinco seis', 'subtitulo': 'uno', 'visual': {'tipo': 'nada'}, 'escena3d': d} for d in es]}
os.makedirs(SAL, exist_ok=True); json.dump(HH, open(SAL + '/h.json', 'w'), ensure_ascii=False)
esc, _ = banco.preparar(SAL + '/h.json', 'pq3d', SAL + '/d')
h2 = json.load(open(SAL + '/d/historia.json'))
for a, b in zip(h2['escenas'], HH['escenas']): a['escena3d'] = b['escena3d']
json.dump(h2, open(SAL + '/d/historia.json', 'w'), ensure_ascii=False)
p = json.load(open(SAL + '/d/proyecto.json')); p['limpio'] = True; json.dump(p, open(SAL + '/d/proyecto.json', 'w'))
tt = [x['ini'] + 0.6 * (x['fin'] - x['ini']) for x in esc]
r = subprocess.run(['node', os.path.join(V2, 'render2.js'), SAL + '/d', 'pruebas', ','.join(f'{x:.2f}' for x in tt)], capture_output=True, text=True, env=dict(os.environ, PQ_DEBUG='1'))
print(r.stdout[-6000:], r.stderr[-3000:])
