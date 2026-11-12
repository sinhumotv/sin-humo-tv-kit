#!/usr/bin/env python3
"""(8-nov-2026) LARGO DE sin humo TV EN GITHUB, sin Claude y sin gastar el servidor de Explícalo (Modal).
Pablo: «hay que apurar a 20 vídeos al mes en sinhumotv, que es el límite de Metricool».

Cada día (workflow «Largo diario sin humo TV»):
 1. ¿Toca hoy? Se reparten 20 largos al mes: hoy se hace uno si los publicados este mes son menos que 20 × día / días del mes
    (registro en la rama «datos»: largos_sinhumo.txt, «AAAA-MM-DD|hora|tema|título|id de Metricool»).
 2. Noticia de la semana (portadas en RSS + artículos) → guion, fotos reales, voz, montaje, miniatura (sinhumo_largo/sinhumo/largo_sh.py,
    con las comprobaciones de neutralidad, cifras y voz). Si falla, se prueba con otra noticia (hasta 3 veces).
 3. Vídeo y miniatura a la rama pub-largo-gh y programación en YouTube con Metricool para hoy entre las 18:45 y las 19:15.
Variables: GEMINI_CLAVES, REFRESH, GH_SECRETOS, GITHUB_TOKEN. FORZAR=1 lo hace aunque hoy no toque; AHORA=1 publica en cuanto esté;
NO_PUBLICAR=1 solo fabrica.
"""
import calendar, datetime as dt, json, math, os, random, shutil, subprocess, sys
from zoneinfo import ZoneInfo

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AQUI = os.path.join(KIT, 'sinhumo_largo')
MAD = ZoneInfo('Europe/Madrid')
META = 20
REPO = 'https://x-access-token:%s@github.com/sinhumotv/sin-humo-tv-kit' % os.environ.get('GITHUB_TOKEN', '')
ahora = dt.datetime.now(MAD)
hoy = ahora.date()
W = '/tmp/shl'; shutil.rmtree(W, ignore_errors=True); os.makedirs(W)


def sh(c, **k):
    return subprocess.run(c, shell=True, text=True, capture_output=True, **k)


def git_rama(rama, carpeta):
    os.makedirs(carpeta, exist_ok=True)
    r = sh(f'git clone -q --depth 1 --branch {rama} {REPO} {carpeta}')
    if r.returncode:
        sh(f'cd {carpeta} && git init -q && git checkout -q --orphan {rama}')


# ---------- 1) ¿Toca hoy? ----------
DAT = f'{W}/datos'
git_rama('datos', DAT)
REG = f'{DAT}/largos_sinhumo.txt'
lineas = [l.strip() for l in open(REG, encoding='utf-8')] if os.path.exists(REG) else []
del_mes = [l for l in lineas if l[:7] == hoy.isoformat()[:7]]
dias = calendar.monthrange(hoy.year, hoy.month)[1]
cupo = min(META, math.ceil(META * hoy.day / dias))
hecho_hoy = any(l.startswith(hoy.isoformat()) for l in lineas)
print(f'Largos de sin humo TV este mes: {len(del_mes)} de {META} · hasta hoy tocan {cupo} · hoy ya hecho: {hecho_hoy}', flush=True)
if not os.environ.get('FORZAR') and (hecho_hoy or len(del_mes) >= cupo):
    print('HOY NO TOCA'); sys.exit(0)
if len(del_mes) >= META and not os.environ.get('FORZAR'):
    print('CUPO DEL MES COMPLETO'); sys.exit(0)

# ---------- 2) Noticia y fabricación (hasta 3 noticias distintas) ----------
env = dict(os.environ, KIT_SH=KIT, GEMINI_API_KEY=os.environ['GEMINI_CLAVES'].split(',')[0].strip(),
           GEMINI_TTS_KEY=os.environ['GEMINI_CLAVES'].split(',')[0].strip(),
           GEMINI_KEY_RESERVA=(os.environ['GEMINI_CLAVES'].split(',') + [''])[1].strip(), PYTHONUNBUFFERED='1')
previos = f'{W}/previos.txt'
open(previos, 'w', encoding='utf-8').write('\n'.join(lineas[-30:]) + '\n')
hecho = None
for intento in range(3):
    n = sh(f'python3 {AQUI}/noticia.py {W}/noticia.json {previos}', env=env, timeout=1800)
    print(n.stdout[-400:], n.stderr[-800:], flush=True)
    if n.returncode:
        continue
    N = json.load(open(f'{W}/noticia.json', encoding='utf-8'))
    N['fuentes'] = N.get('fuentes_enlaces') or N.get('fuentes')
    json.dump(N, open(f'{W}/noticia.json', 'w', encoding='utf-8'), ensure_ascii=False)
    d = f'{W}/v{intento}'
    r = subprocess.run(['python3', f'{AQUI}/sinhumo/largo_sh.py', f'{W}/noticia.json', d], env=env, text=True, timeout=4 * 3600)
    if r.returncode == 0 and os.path.exists(f'{d}/video_final.mp4'):
        hecho = d; break
    open(previos, 'a', encoding='utf-8').write(f'{hoy}|-|{N["tema"]}|descartado\n')   # que no vuelva a elegir la misma
    print(f'intento {intento + 1} fallido: se prueba con otra noticia', flush=True)
if not hecho:
    sys.exit('FALLO: hoy no ha salido ningún largo de sin humo TV')
L = json.load(open(f'{hecho}/largo.json', encoding='utf-8'))
print(f'LARGO: «{L["titulo"]}» · {L.get("duracion")} s', flush=True)
if os.environ.get('NO_PUBLICAR'):
    # (12-nov-2026) la prueba se guarda para poder verla (artefacto «prueba-largo» del workflow)
    PR = os.path.join(os.environ.get('GITHUB_WORKSPACE', '.'), 'prueba_largo')
    os.makedirs(PR, exist_ok=True)
    for f in ('video_final.mp4', 'miniatura.jpg', 'voz.mp3'):
        if os.path.exists(f'{hecho}/{f}'): shutil.copy(f'{hecho}/{f}', f'{PR}/{f}')
    sys.exit(0)

# ---------- 3) Alojar y programar ----------
PUB = f'{W}/pub'
os.makedirs(PUB)
shutil.copy(f'{hecho}/video_final.mp4', f'{PUB}/video.mp4'); shutil.copy(f'{hecho}/miniatura.jpg', f'{PUB}/miniatura.jpg')
r = sh(f'cd {PUB} && git init -q && git checkout -q --orphan pub-largo-gh && git add . && '
       f'git -c user.name="sin humo TV" -c user.email=sinhumotv@users.noreply.github.com commit -q -m "largo {hoy}" && '
       f'git push -q -f {REPO} HEAD:refs/heads/pub-largo-gh && git rev-parse HEAD')
if r.returncode:
    sys.exit('FALLO al subir el vídeo a GitHub: ' + r.stderr[-300:])
sha = r.stdout.strip().splitlines()[-1]
base = f'https://raw.githubusercontent.com/sinhumotv/sin-humo-tv-kit/{sha}'
for f in ('video.mp4', 'miniatura.jpg'):
    c = sh(f'curl -s -o /dev/null -I -w "%{{http_code}}" {base}/{f}').stdout
    if c != '200':
        sys.exit(f'FALLO: {f} no está en GitHub ({c})')
hora = ahora.replace(hour=18, minute=45, second=0) + dt.timedelta(minutes=random.randint(0, 30))
if hora.minute % 15 == 0: hora += dt.timedelta(minutes=2)
fecha = 'ahora' if os.environ.get('AHORA') or hora < dt.datetime.now(MAD) + dt.timedelta(minutes=20) else hora.strftime('%Y-%m-%dT%H:%M')
pub = {'video': f'{base}/video.mp4', 'miniatura': f'{base}/miniatura.jpg', 'titulo': L['titulo'], 'descripcion': L['descripcion'],
       'etiquetas': L.get('etiquetas') or [], 'categoria': 'NEWS_POLITICS', 'fecha': fecha}
json.dump(pub, open(f'{W}/publicacion.json', 'w', encoding='utf-8'), ensure_ascii=False)
r = subprocess.run(['python3', f'{KIT}/metricool/publicar_largo.py', 'sinhumo', f'{W}/publicacion.json'], text=True, capture_output=True)
print(r.stdout[-600:], r.stderr[-600:], flush=True)
if r.returncode:
    sys.exit('FALLO al programarlo en Metricool')
mid = ''
for l in r.stdout.splitlines():
    if l.startswith('METRICOOL:'):
        try: mid = str(json.loads(l[10:].strip())['data']['id'])
        except Exception: pass

# ---------- 4) Registro ----------
lin = f'{hoy}|{fecha[-5:] if fecha != "ahora" else ahora.strftime("%H:%M")}|{L.get("tema", "")}|{L["titulo"]}|{mid}'
open(REG, 'a', encoding='utf-8').write(lin + '\n')
# (10-nov-2026) el registro del día NO se guardó porque otra tanda escribió a la vez en la rama de datos y el reintento no llevaba
# nombre de autor (sin registro, el largo se podría hacer dos veces el mismo día). Ahora reintenta dos veces con autor.
_GITID = 'git -c user.name="sin humo TV" -c user.email=sinhumotv@users.noreply.github.com'
r = sh(f'cd {DAT} && git add largos_sinhumo.txt && git -c user.name="sin humo TV" -c user.email=sinhumotv@users.noreply.github.com '
       f'commit -q -m "largo sin humo TV {hoy}" && (git push -q {REPO} HEAD:datos || (sleep 5 && {_GITID} pull -q --rebase {REPO} datos && git push -q {REPO} HEAD:datos) '
       f'|| (sleep 20 && {_GITID} pull -q --rebase {REPO} datos && git push -q {REPO} HEAD:datos))')
print('REGISTRO:', lin, '(ok)' if r.returncode == 0 else '(no se ha podido guardar: ' + r.stderr[-200:] + ')')
