#!/usr/bin/env python3
"""(14-nov-2026) RELOJ DE LOS CANALES. GitHub llega a lanzar las tareas programadas con 7-8 horas de retraso, así que la hora la
lleva este proceso: se queda despierto ~5 h 40 min, mira la hora de Madrid cada minuto y lanza cada trabajo de reloj/agenda.json
a su hora (si el reloj estuvo parado, lo lanza con retraso mientras esté dentro del «margen»). Lo ya lanzado se apunta en la
rama «reloj-estado» (lanzados-AAAA-MM-DD.json) para no lanzarlo dos veces. Antes de acabar se relanza a sí mismo; la alarma de
GitHub cada 20 min solo sirve para rearrancarlo si la cadena se corta. Necesita GH_TOKEN (actions: write) y GITHUB_REPOSITORY."""
import json, os, subprocess, tempfile, time, urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
AQUI = os.path.dirname(os.path.abspath(__file__))
REPO, TOK = os.environ['GITHUB_REPOSITORY'], os.environ['GH_TOKEN']
PUSH = f'https://x-access-token:{TOK}@github.com/{REPO}'
FIN = time.time() + float(os.environ.get('RELOJ_SEGUNDOS', 5 * 3600 + 40 * 60))
MAD = ZoneInfo('Europe/Madrid')
def api(ruta, metodo='GET', datos=None):
    req = urllib.request.Request(f'https://api.github.com/repos/{REPO}/{ruta}', json.dumps(datos).encode() if datos else None,
                                 {'Authorization': f'Bearer {TOK}', 'Accept': 'application/vnd.github+json'}, method=metodo)
    with urllib.request.urlopen(req, timeout=60) as r:
        t = r.read(); return json.loads(t) if t else {}
def git(*a, cwd=None): return subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True)
def lanzados(dia):
    """Lo ya lanzado ese día (de la rama reloj-estado)."""
    d = tempfile.mkdtemp()
    if git('clone', '-q', '--depth=1', '--branch', 'reloj-estado', PUSH, d).returncode: return set(), d
    f = os.path.join(d, f'lanzados-{dia}.json')
    return (set(json.load(open(f))) if os.path.exists(f) else set()), d
def apuntar(dia, clave):
    for intento in range(5):
        hechos, d = lanzados(dia)
        if not os.path.exists(os.path.join(d, '.git')): git('init', '-q', '-b', 'reloj-estado', cwd=d)
        hechos.add(clave)
        for f in os.listdir(d):   # solo se guardan los últimos 7 días
            if f.startswith('lanzados-') and f < f'lanzados-{(datetime.now(MAD) - timedelta(days=7)):%Y-%m-%d}': os.remove(os.path.join(d, f))
        json.dump(sorted(hechos), open(os.path.join(d, f'lanzados-{dia}.json'), 'w'), indent=1)
        git('add', '-A', cwd=d)
        git('-c', 'user.name=github-actions', '-c', 'user.email=github-actions@users.noreply.github.com', 'commit', '-qm', clave, cwd=d)
        if git('push', '-q', PUSH, 'HEAD:reloj-estado', cwd=d).returncode == 0: return True
        time.sleep(3 + 3 * intento)
    return False
ult = 0
while time.time() < FIN:
    if time.time() - ult >= 55:
        ult = time.time()
        ahora = datetime.now(MAD)
        try:
            agenda = json.load(open(os.path.join(AQUI, 'agenda.json')))['eventos']
            pendientes = []
            for ev in agenda:
                if 'dias' in ev and ahora.weekday() not in ev['dias']: continue   # 0 = lunes
                for h in ev['horas']:
                    hh, mm = map(int, h.split(':'))
                    t = ahora.replace(hour=hh, minute=mm, second=0, microsecond=0)
                    if t <= ahora <= t + timedelta(minutes=ev.get('margen', 45)):
                        pendientes.append((ev, f'{ev["id"]}@{h}'))
            if pendientes:
                dia = ahora.strftime('%Y-%m-%d'); hechos, _ = lanzados(dia)
                for ev, clave in pendientes:
                    if clave in hechos: continue
                    try:
                        api(f'actions/workflows/{ev["workflow"]}/dispatches', 'POST', {'ref': 'main', 'inputs': ev.get('inputs') or {}})
                        apuntar(dia, clave)
                        print(ahora.strftime('%H:%M'), 'lanzado', clave, flush=True)
                    except Exception as x:
                        print(ahora.strftime('%H:%M'), 'no se pudo lanzar', clave, str(x)[:200], flush=True)
        except Exception as x:
            print(ahora.strftime('%H:%M'), 'error (sigue):', str(x)[:300], flush=True)
    time.sleep(5)
try: api('actions/workflows/reloj-canales.yml/dispatches', 'POST', {'ref': 'main'}); print('relevo lanzado')
except Exception as x: print('no se pudo lanzar el relevo (lo hará la alarma):', x)
