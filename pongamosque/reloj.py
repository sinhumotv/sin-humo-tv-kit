#!/usr/bin/env python3
"""(14-nov-2026) PONGAMOS QUE · RELOJ. GitHub retrasa las tareas programadas hasta 7-8 horas, así que no se usa su hora:
este proceso se queda despierto (~5 h 40 min), mira la hora de Madrid cada minuto y
  · desde las 9:37, si aún no hay tanda de hoy y no se está fabricando, lanza «Pongamos Que · fabricar tanda»;
  · cada 2 minutos intenta publicar (publicar.py solo publica cuando empieza una franja nueva: 11:43, 13:17, 15:47, 18:13, 20:41);
y antes de acabar se vuelve a lanzar a sí mismo. Una alarma de GitHub cada 20 min lo rearranca si la cadena se corta.
Necesita GH_TOKEN (permiso actions: write), BUFFER_KEY y GITHUB_REPOSITORY."""
import json, os, subprocess, sys, time, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo
AQUI = os.path.dirname(os.path.abspath(__file__))
REPO, TOK = os.environ['GITHUB_REPOSITORY'], os.environ['GH_TOKEN']
FIN = time.time() + float(os.environ.get('RELOJ_SEGUNDOS', 5 * 3600 + 40 * 60))
def api(ruta, metodo='GET', datos=None):
    req = urllib.request.Request(f'https://api.github.com/repos/{REPO}/{ruta}', json.dumps(datos).encode() if datos else None,
                                 {'Authorization': f'Bearer {TOK}', 'Accept': 'application/vnd.github+json'}, method=metodo)
    with urllib.request.urlopen(req, timeout=60) as r:
        t = r.read(); return json.loads(t) if t else {}
def sh(*a, **k): return subprocess.run(a, capture_output=True, text=True, **k)
def rama():
    """Copia fresca de la rama pongamosque-videos en /tmp/pv (o None si no existe)."""
    sh('rm', '-rf', '/tmp/pv')
    r = sh('git', 'clone', '-q', '--depth=1', '--branch', 'pongamosque-videos', f'https://x-access-token:{TOK}@github.com/{REPO}', '/tmp/pv')
    return '/tmp/pv' if r.returncode == 0 else None
def fabricando():
    runs = api('actions/workflows/pongamosque-diario.yml/runs?per_page=5').get('workflow_runs', [])
    return any(r['status'] in ('queued', 'in_progress', 'pending', 'waiting', 'requested') for r in runs)
ult_pub = 0
while time.time() < FIN:
    ahora = datetime.now(ZoneInfo('Europe/Madrid')); hm = ahora.hour * 60 + ahora.minute
    try:
        if time.time() - ult_pub > 120:
            ult_pub = time.time(); d = rama()
            hoy = ahora.date().isoformat()
            hay_tanda = bool(d) and open(f'{d}/fecha.txt').read().strip() == hoy if d and os.path.exists(f'{d}/fecha.txt') else False
            # 1) fabricación del día
            if hm >= 9 * 60 + 37 and not hay_tanda and not fabricando():
                api('actions/workflows/pongamosque-diario.yml/dispatches', 'POST', {'ref': 'main', 'inputs': {'cuantos': '5'}})
                print(ahora.strftime('%H:%M'), 'lanzada la tanda de hoy', flush=True)
            # 2) publicación (publicar.py decide si toca)
            if d:
                r = sh(sys.executable, os.path.join(AQUI, 'publicar.py'), d, f'https://raw.githubusercontent.com/{REPO}/pongamosque-videos')
                if 'publicado:' in r.stdout:
                    print(ahora.strftime('%H:%M'), r.stdout.strip()[-400:], flush=True)
                    sh('git', '-C', d, 'add', 'videos.json')
                    sh('git', '-C', d, '-c', 'user.name=github-actions', '-c', 'user.email=github-actions@users.noreply.github.com', 'commit', '-qm', f'Publicado {ahora:%H:%M}')
                    p = sh('git', '-C', d, 'push', '-q', 'origin', 'HEAD:pongamosque-videos')
                    if p.returncode: print('no se pudo guardar videos.json:', p.stderr[-300:], flush=True)
                elif r.returncode: print(ahora.strftime('%H:%M'), 'publicar falló:', (r.stdout + r.stderr)[-500:], flush=True)
    except Exception as x:
        print(ahora.strftime('%H:%M'), 'error (sigue):', str(x)[:300], flush=True)
    time.sleep(60)
# relevo: otro reloj igual (si ya hay uno esperando, GitHub lo deja en cola y no se duplica)
try: api('actions/workflows/pongamosque-reloj.yml/dispatches', 'POST', {'ref': 'main'}); print('relevo lanzado')
except Exception as x: print('no se pudo lanzar el relevo (lo hará la alarma):', x)
