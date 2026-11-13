#!/usr/bin/env python3
"""Pongamos Que · fabrica la tanda del día en GitHub (gratis) con TODAS las escenas animadas con IA en Kaggle.
Uso: python3 diario.py <temas.json> <carpeta_explicalo> <salida>
1) lanza a la vez un fabricar.py del motor de Explícalo por tema (guion, voz, imágenes, profundidad);
2) cuando todos han pedido sus clips («@ANIMAR»), los anima TODOS en una sola sesión de Kaggle (lanzar.py);
3) entrega los clips a cada vídeo de uno en uno (así los renders no se pisan) → <salida>/videos.json + NN.mp4
Si no se puede animar (Kaggle falla o no hay cupo), el vídeo sale igual con las imágenes de IA y el efecto 3D, y se publica."""
import json, os, shutil, subprocess, sys, threading, time
AQUI = os.path.dirname(os.path.abspath(__file__))
temas, EXP, SAL = json.load(open(sys.argv[1])), os.path.abspath(sys.argv[2]), os.path.abspath(sys.argv[3])
os.makedirs(SAL, exist_ok=True)
FAB = os.path.join(EXP, 'plataforma/v2/fabricar.py')
env = dict(os.environ, ANIMAR_IA='1', ANIMAR_ESPERA='10800', WHISPER_MODELO='small')
trab = []
for i, t in enumerate(temas, 1):
    d = os.path.join(SAL, f'v{i}'); os.makedirs(d, exist_ok=True)
    json.dump({'tipo': 'explica', 'tema': t['tema'], 'duracion': 38, 'formato': 'vertical', 'tema_visual': 'pongamosque', 'voz': 'Puck',
               'estructura_fija': True}, open(f'{d}/pedido_in.json', 'w'), ensure_ascii=False)
    pr = subprocess.Popen([sys.executable, FAB, f'{d}/pedido_in.json', d], cwd=EXP, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    trab.append({'i': i, 'd': d, 'tema': t, 'pr': pr, 'pide': False, 'log': []})
def leer(w):
    for l in w['pr'].stdout:
        w['log'].append(l.rstrip())
        if l.startswith('@ANIMAR'): w['pide'] = True
        if l.startswith(('·', '⏱', '@', 'animación', 'FALLO', 'render')): print(f'[v{w["i"]}]', l.rstrip(), flush=True)
for w in trab: w['hilo'] = threading.Thread(target=leer, args=(w,), daemon=True); w['hilo'].start()
t0 = time.time()
while time.time() - t0 < 3600 and not all(w['pide'] or w['pr'].poll() is not None for w in trab): time.sleep(5)
listos = [w for w in trab if w['pide'] and w['pr'].poll() is None]
print(f'piden clips {len(listos)} de {len(trab)} vídeos en {time.time() - t0:.0f} s', flush=True)
# 2) una sola sesión de Kaggle para todos los clips del día (n = vídeo*100 + escena)
lote = []
for w in listos:
    for e in json.load(open(f'{w["d"]}/animar.json'))['escenas']:
        lote.append({'n': w['i'] * 100 + e['n'], 'jpg': e['img'], 'prompt': e['prompt'], 'semilla': e.get('semilla', 0)})
json.dump(lote, open(f'{SAL}/lote.json', 'w'))
clips = os.path.join(SAL, 'clips'); motivo = ''
if lote:
    r = subprocess.run([sys.executable, os.path.join(AQUI, 'kaggle', 'lanzar.py'), clips, f'{SAL}/lote.json'], capture_output=True, text=True)
    print(r.stdout[-3000:], r.stderr[-1500:], flush=True)
    try: motivo = 'Kaggle: ' + json.dumps(json.load(open(f'{clips}/resumen.json'))['segundos']) + ' s'
    except Exception: motivo = 'Kaggle no devolvió resumen'
# 3) a cada vídeo sus clips, de uno en uno
videos = []
for w in trab:
    hechos = []
    if w in listos:
        for e in json.load(open(f'{w["d"]}/animar.json'))['escenas']:
            f = f'{clips}/{w["i"] * 100 + e["n"]}_ia.mp4'
            if os.path.exists(f): shutil.copy(f, f'{w["d"]}/imgs/{e["n"]:02d}_ia.mp4'); hechos.append(e['n'])
        json.dump({'clips': hechos, 'fps': 24, 'motivo': motivo}, open(f'{w["d"]}/animar_fin.json', 'w'))
    w['pr'].wait(); w['hilo'].join(5)
    total = len(json.load(open(f'{w["d"]}/historia.json'))['escenas']) if os.path.exists(f'{w["d"]}/historia.json') else 0
    ok = w['pr'].returncode == 0 and os.path.exists(f'{w["d"]}/video_final.mp4')
    animadas = len(hechos) / max(1, total)
    v = {'id': f'v{w["i"]}', 'tema': w['tema']['tema'], 'titulo': w['tema'].get('titulo') or w['tema']['tema'], 'gancho': w['tema'].get('gancho', ''),
         'pregunta': w['tema'].get('pregunta', ''), 'hashtags': w['tema'].get('hashtags', []), 'escenas': total, 'animadas': len(hechos),
         'publicable': ok, 'publicado': {}}
    if ok: shutil.copy(f'{w["d"]}/video_final.mp4', f'{SAL}/{v["id"]}.mp4'); v['archivo'] = f'{v["id"]}.mp4'
    else: v['error'] = '\n'.join(w['log'][-12:])[-800:]
    print(f'{v["id"]}: {"OK" if ok else "FALLO"} · {len(hechos)}/{total} escenas animadas · {"animado con IA" if animadas >= 0.8 else "con imágenes y efecto 3D"} · {v["tema"]}', flush=True)
    videos.append(v)
json.dump(videos, open(f'{SAL}/videos.json', 'w'), ensure_ascii=False, indent=1)
