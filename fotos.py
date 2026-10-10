"""Fotos reales para los vídeos de sin humo TV.

El entorno de trabajo no puede descargar de Wikimedia Commons ni de webs oficiales (la red lo bloquea).
Hay dos caminos; el A es el normal y funciona también en las tareas programadas:

A) GITHUB (v14, automático, sin navegador). Requiere add_repo de sinhumotv/sin-humo-tv-datos (ya se hace para el
   registro). El workflow "Descargar fotos" de ese repositorio busca y descarga desde GitHub; cada llamada tarda ~30 s.
   1. python3 fotos.py buscar <carpeta> "<búsqueda>"
        -> busca en Wikimedia Commons, imprime los resultados numerados (título, licencia, tamaño, autor, fecha,
           descripción) y crea <carpeta>/fotos/busqueda/previas.jpg: hoja con las miniaturas numeradas. Mírala con Read.
           Busca en inglés o español con nombres propios y lugar ("Congreso de los Diputados hemiciclo",
           "Pedro Sánchez 2025"); si sale poco, prueba otra búsqueda (máximo 3).
   2. python3 fotos.py traer <carpeta> 3 7 [https://...]
        -> trae los números elegidos de la última búsqueda y/o URLs directas (Commons, lamoncloa.gob.es,
           congreso.es, pexels...), y los deja como <carpeta>/fotos/f0.jpg, f1.jpg... + creditos.json.
           Imprime la línea de crédito de cada foto para A.foto y para la descripción.
   Si falla (sin permiso en el repositorio, workflow caído), di en una línea del mensaje final que el vídeo va
   sin fotos y sigue con dibujos: no es motivo para parar.

B) NAVEGADOR de la app (solo con el PC del usuario conectado; método v10):
   1. python3 fotos.py js  -> código JavaScript para javascript_tool en https://commons.wikimedia.org
   2. await buscar("…") y await get("File:Nombre.jpg", k) en el navegador
   3. python3 fotos.py extraer <carpeta>/fotos

Qué fotos elegir: licencia libre (CC0, CC BY, CC BY-SA, dominio público) o de webs oficiales de prensa (La Moncloa,
Congreso: citar la fuente); recientes si son de la noticia; sin menores ni víctimas; sin caras en primer plano de
particulares; sin logos protagonistas ni pancartas de un partido (neutralidad). Pexels solo para recursos genéricos
(una calle, un supermercado), nunca como si fuera la noticia.
Uso: A.precarga([ruta...]) y A.foto(ruta, cx, cy, w, h, rot, escala, 'Autor · Wikimedia Commons · CC BY-SA 4.0').
Pon el crédito también en la descripción de cada red. Miniatura del largo: "foto" y "credito" en miniatura.js.
"""
import sys, os, json, glob, base64, re, time, shutil, subprocess, tempfile, urllib.request, urllib.error, urllib.parse

JS = r'''
window.buscar = async (q, n = 10) => {
  const r = await fetch(`https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrlimit=${n}&gsrsearch=${encodeURIComponent(q)}&prop=imageinfo&iiprop=url|size|extmetadata`).then(r => r.json());
  return JSON.stringify(Object.values(r.query?.pages || {}).map(p => { const i = p.imageinfo[0], m = i.extmetadata || {};
    return [p.title, i.width + 'x' + i.height, m.LicenseShortName?.value, (m.Artist?.value || '').replace(/<[^>]+>/g, '').trim().slice(0, 40), String(m.DateTimeOriginal?.value || '').slice(0, 10), (m.ImageDescription?.value || '').replace(/<[^>]+>/g, '').slice(0, 90)]; }));
};
window.get = async (t, k) => {
  const r = await fetch(`https://commons.wikimedia.org/w/api.php?action=query&format=json&titles=${encodeURIComponent(t)}&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=1280`).then(r => r.json());
  const i = Object.values(r.query.pages)[0].imageinfo[0];
  const b = await fetch(i.thumburl).then(r => r.blob()); const bm = await createImageBitmap(b);
  const c = document.createElement('canvas'); c.width = bm.width; c.height = bm.height; c.getContext('2d').drawImage(bm, 0, 0);
  return 'FOTO' + JSON.stringify({ k, t, page: i.descriptionurl, lic: i.extmetadata.LicenseShortName?.value, artist: (i.extmetadata.Artist?.value || '').replace(/<[^>]+>/g, '').trim(), d: c.toDataURL('image/jpeg', 0.82) });
};
'buscar() y get() listos'
'''


def extraer(dest):
    os.makedirs(dest, exist_ok=True)
    cred_p = os.path.join(dest, 'creditos.json')
    cred = json.load(open(cred_p)) if os.path.exists(cred_p) else {}
    fs = sorted(glob.glob('/root/.claude/projects/**/tool-results/*.txt', recursive=True), key=os.path.getmtime)
    n = 0
    for f in fs:
        try:
            t = json.load(open(f))[0]['text']
        except Exception:
            continue
        i = t.find('"FOTO')
        if i < 0:
            continue
        try:
            inner = json.loads(t[i:t.rfind('}"') + 2])
            o = json.loads(inner[4:])
        except Exception as e:
            print('no se pudo leer', f, e)
            continue
        open(os.path.join(dest, f"f{o['k']}.jpg"), 'wb').write(base64.b64decode(o['d'].split(',')[1]))
        cred[str(o['k'])] = {k: o.get(k) for k in ('t', 'page', 'lic', 'artist')}
        n += 1
    json.dump(cred, open(cred_p, 'w'), ensure_ascii=False, indent=1)
    for k, v in sorted(cred.items()):
        print(f"f{k}.jpg · {v['artist']} · {v['lic']} · {v['t']}")
    print('fotos guardadas:', n)


# ---------- Camino A: GitHub Actions (v14) ----------
REPO = 'sinhumotv/sin-humo-tv-datos'
WORKFLOW = 'descargar-fotos.yml'
API = f'https://api.github.com/repos/{REPO}'


def _api(method, path, data=None):
    req = urllib.request.Request(API + path, method=method,
                                 data=json.dumps(data).encode() if data is not None else None,
                                 headers={'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json',
                                          'User-Agent': 'sin-humo-tv-kit'})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read()
    return json.loads(body) if body else {}


def _lanzar(carpeta_remota, urls='', buscar=''):
    """Lanza el workflow, espera a que termine y devuelve la carpeta local con lo descargado."""
    titulo = f'Fotos → {carpeta_remota}'
    inicio = time.time()
    try:
        _api('POST', f'/actions/workflows/{WORKFLOW}/dispatches',
             {'ref': 'main', 'inputs': {'carpeta': carpeta_remota, 'urls': urls, 'buscar': buscar}})
    except urllib.error.HTTPError as e:
        sys.exit(f'No se pudo lanzar el workflow ({e.code}). ¿Falta add_repo de {REPO}? Sigue sin fotos.')
    run = None
    while time.time() - inicio < 240:
        time.sleep(6)
        runs = _api('GET', f'/actions/workflows/{WORKFLOW}/runs?event=workflow_dispatch&per_page=15').get('workflow_runs', [])
        run = next((r for r in runs if r.get('display_title') == titulo), None)
        if run and run.get('status') == 'completed':
            break
    if not run or run.get('status') != 'completed':
        sys.exit('El workflow no ha terminado en 4 minutos. Sigue sin fotos.')
    if run.get('conclusion') != 'success':
        print(f"Aviso: el workflow terminó con «{run.get('conclusion')}»: {run.get('html_url')}")
    dest = tempfile.mkdtemp(prefix='fotos-')
    sh = lambda c: subprocess.run(c, shell=True, check=True, capture_output=True, text=True)
    try:
        sh(f'git -C {dest} init -q && git -C {dest} fetch -q --depth 1 https://github.com/{REPO} fotos')
        sh(f'git -C {dest} archive FETCH_HEAD fotos/{carpeta_remota} | tar -x -C {dest}')
    except subprocess.CalledProcessError as e:
        sys.exit(f'No se pudieron traer las fotos de GitHub: {e.stderr.strip()[:200]}. Sigue sin fotos.')
    return os.path.join(dest, 'fotos', carpeta_remota)


def _nombre(carpeta, sufijo):
    base = re.sub(r'[^A-Za-z0-9._-]+', '-', os.path.basename(os.path.abspath(carpeta))).strip('-') or 'video'
    return f'{base}-{sufijo}{time.strftime("%H%M%S")}'


def gh_buscar(carpeta, consulta):
    remoto = _lanzar(_nombre(carpeta, 'b'), buscar=consulta)
    out = os.path.join(carpeta, 'fotos', 'busqueda')
    shutil.rmtree(out, ignore_errors=True)
    shutil.copytree(remoto, out)
    res = json.load(open(os.path.join(out, 'busqueda.json')))['resultados']
    if not res:
        print(f'Sin resultados para «{consulta}». Prueba otra búsqueda (más general, en inglés o con el lugar).')
        return
    for r in res:
        print(f"{r['n']:2d}. {r['titulo'][5:]}  [{r['licencia'] or '¿licencia?'}]  {r['tamano']}  {r['autor'][:30]}  {r['fecha']}")
        if r.get('descripcion'):
            print(f"      {r['descripcion'][:120]}")
    try:  # hoja de contacto numerada para mirarla con Read
        from PIL import Image, ImageDraw
        ims = []
        for r in res:
            if r.get('previa'):
                im = Image.open(os.path.join(out, r['previa'])).convert('RGB')
                im.thumbnail((300, 220))
                ims.append((r['n'], im))
        cols = 4
        filas = (len(ims) + cols - 1) // cols
        hoja = Image.new('RGB', (cols * 310, filas * 240), '#1d1824')
        d = ImageDraw.Draw(hoja)
        for i, (n, im) in enumerate(ims):
            x, y = (i % cols) * 310 + 5, (i // cols) * 240 + 5
            hoja.paste(im, (x + (300 - im.width) // 2, y + (220 - im.height) // 2))
            d.rectangle([x, y, x + 34, y + 30], fill='#ff7a1a')
            d.text((x + 8, y + 7), str(n), fill='white')
        hoja.save(os.path.join(out, 'previas.jpg'), quality=85)
        print('Miniaturas numeradas:', os.path.join(out, 'previas.jpg'))
    except Exception as e:  # noqa: BLE001
        print('No se pudo hacer la hoja de miniaturas:', e)


def gh_traer(carpeta, refs):
    dest = os.path.join(carpeta, 'fotos')
    os.makedirs(dest, exist_ok=True)
    bj = os.path.join(dest, 'busqueda', 'busqueda.json')
    res = {str(r['n']): r for r in json.load(open(bj))['resultados']} if os.path.exists(bj) else {}
    urls = []
    for r in refs:
        if r.startswith('http'):
            urls.append(r)
        elif r in res:
            urls.append(res[r]['ficha'])
        else:
            print(f'«{r}» no es una URL ni un número de la última búsqueda: lo salto')
    if not urls:
        sys.exit('No hay nada que traer.')
    remoto = _lanzar(_nombre(carpeta, 't'), urls=' '.join(urls))
    man = json.load(open(os.path.join(remoto, 'manifiesto.json')))
    cred_p = os.path.join(dest, 'creditos.json')
    cred = json.load(open(cred_p)) if os.path.exists(cred_p) else {}
    k = max([int(x) for x in cred] + [-1]) + 1
    from PIL import Image
    for m in man:
        if not m.get('ok'):
            print(f"ERROR {m['url_pedida']}: {m.get('error')}")
            continue
        im = Image.open(os.path.join(remoto, m['archivo']))
        if im.mode in ('RGBA', 'LA', 'P'):
            fondo = Image.new('RGB', im.size, 'white')
            im = im.convert('RGBA')
            fondo.paste(im, mask=im.split()[-1])
            im = fondo
        im.thumbnail((1920, 1920))  # de sobra para 1080p y no pesa en el render
        im.convert('RGB').save(os.path.join(dest, f'f{k}.jpg'), quality=90)
        host = re.sub(r'^www\.', '', urllib.parse.urlparse(m['url_pedida']).netloc)
        if m.get('titulo'):  # Commons
            cred[str(k)] = {'t': m['titulo'], 'page': m.get('ficha'), 'lic': m.get('licencia'),
                            'artist': m.get('autor') or 'Autor desconocido', 'fuente': 'Wikimedia Commons'}
        else:
            cred[str(k)] = {'t': os.path.basename(m['url_descargada']), 'page': m['url_pedida'], 'lic': '',
                            'artist': '', 'fuente': {'lamoncloa.gob.es': 'La Moncloa', 'congreso.es': 'Congreso',
                                                     'images.pexels.com': 'Pexels'}.get(host, host)}
        k += 1
    json.dump(cred, open(cred_p, 'w'), ensure_ascii=False, indent=1)
    for kk, v in sorted(cred.items(), key=lambda x: int(x[0])):
        print(f"{dest}/f{kk}.jpg  ->  crédito: '{credito(v)}'")


def credito(v):
    """Texto del crédito para A.foto y la descripción."""
    if v.get('fuente', 'Wikimedia Commons') == 'Wikimedia Commons' or v.get('lic'):
        partes = [(v.get('artist') or '')[:40], 'Wikimedia Commons', v.get('lic') or '']
    else:
        partes = ['Foto: ' + v['fuente']]
    return ' · '.join(p for p in partes if p).replace("'", '’')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'js':
        print(JS)
    elif len(sys.argv) > 2 and sys.argv[1] == 'extraer':
        extraer(sys.argv[2])
    elif len(sys.argv) > 3 and sys.argv[1] == 'buscar':
        gh_buscar(sys.argv[2], ' '.join(sys.argv[3:]))
    elif len(sys.argv) > 3 and sys.argv[1] == 'traer':
        gh_traer(sys.argv[2], sys.argv[3:])
    else:
        print(__doc__)
