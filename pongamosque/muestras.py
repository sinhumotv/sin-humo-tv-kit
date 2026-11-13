#!/usr/bin/env python3
"""Pongamos Que · un vídeo de muestra por estructura (mismo tema) para comparar. Sin animación IA.
Uso: python3 muestras.py <carpeta_explicalo> <salida> "<tema>" estructura1,estructura2,…   (de 3 en 3 a la vez)"""
import json, os, shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
EXP, SAL, TEMA, ESTS = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), sys.argv[3], sys.argv[4].split(',')
os.makedirs(SAL, exist_ok=True)
def una(est):
    d = os.path.join(SAL, est); os.makedirs(d, exist_ok=True)
    json.dump({'tipo': 'explica', 'tema': TEMA, 'duracion': 38, 'formato': 'vertical', 'tema_visual': est, 'voz': 'Puck', 'estructura_fija': True},
              open(f'{d}/pedido_in.json', 'w'), ensure_ascii=False)
    r = subprocess.run([sys.executable, os.path.join(EXP, 'plataforma/v2/fabricar.py'), f'{d}/pedido_in.json', d], cwd=EXP, capture_output=True, text=True)
    ok = os.path.exists(f'{d}/video_final.mp4')
    if ok: shutil.copy(f'{d}/video_final.mp4', f'{SAL}/{est}.mp4')
    print(est, 'OK' if ok else 'FALLO\n' + (r.stdout + r.stderr)[-1500:], flush=True)
with ThreadPoolExecutor(3) as ex: list(ex.map(una, ESTS))
