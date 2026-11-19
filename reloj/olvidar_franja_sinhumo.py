#!/usr/bin/env python3
"""(19-nov-2026) Antes de REINTENTAR un corto de sin humo TV que ha fallado: borra de la memoria (rama estado-canales,
sinhumo.json) las marcas «sh:hecho:<hoy>:…» para que la fábrica vuelva a intentarlo. No duplica nada: la fábrica comprueba
además en Buffer si la franja ya tiene vídeo (±90 min) y entonces no hace nada. Necesita REPO_PUSH."""
import json, os, pathlib, subprocess, tempfile, time
from datetime import datetime
from zoneinfo import ZoneInfo
PUSH = os.environ['REPO_PUSH']
hoy = datetime.now(ZoneInfo('Europe/Madrid')).strftime('%Y%m%d')
def git(*a, cwd=None): return subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True)
for intento in range(5):
    d = pathlib.Path(tempfile.mkdtemp())
    if git('clone', '-q', '--depth=1', '--branch', 'estado-canales', PUSH, str(d)).returncode: print('sin memoria'); break
    f = d / 'sinhumo.json'
    if not f.exists(): break
    m = json.loads(f.read_text()); quitar = [k for k in m if k.startswith(f'sh:hecho:{hoy}:')]
    if not quitar: print('nada que olvidar'); break
    for k in quitar: m.pop(k)
    f.write_text(json.dumps(m, ensure_ascii=False, default=str)); git('add', '-A', cwd=d)
    git('-c', 'user.name=github-actions', '-c', 'user.email=github-actions@users.noreply.github.com', 'commit', '-qm', 'reintento sin humo TV', cwd=d)
    if git('push', '-q', PUSH, 'HEAD:estado-canales', cwd=d).returncode == 0: print('olvidado:', quitar); break
    time.sleep(5 + 5 * intento)
