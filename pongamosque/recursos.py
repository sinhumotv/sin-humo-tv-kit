#!/usr/bin/env python3
"""(17-nov-2026) Pongamos Que · descarga RECURSOS LIBRES (CC0, gratis) para el motor 3D: modelos, texturas y cielos HDR de
Poly Haven y packs de sonidos de Kenney. Se guardan en la rama «pq-recursos» (el entorno de Claude no llega a esas webs;
GitHub sí). Uso: python3 recursos.py <carpeta> "<pedido>"
pedido = palabras separadas por espacios: catalogo · m:<id> (modelo glTF 1k) · h:<id> (cielo HDR 1k) · t:<id> (textura 1k)
         · k:<pack> (pack de Kenney, p. ej. k:impact-sounds)"""
import io, json, os, re, sys, urllib.request, zipfile
D, PED = sys.argv[1], sys.argv[2].split()
UA = {'User-Agent': 'pq-recursos/1.0'}
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read()
def js(u): return json.loads(get(u))
def guarda(ruta, datos):
    os.makedirs(os.path.dirname(ruta), exist_ok=True); open(ruta, 'wb').write(datos)
for p in PED:
    try:
        if p == 'catalogo':
            for t in ('models', 'hdris', 'textures'):
                a = js(f'https://api.polyhaven.com/assets?t={t}')
                c = {k: {'nombre': v.get('name'), 'cat': v.get('categories'), 'tags': v.get('tags'), 'pol': v.get('polycount'), 'dim': v.get('dimensions')} for k, v in a.items()}
                guarda(f'{D}/catalogo_{t}.json', json.dumps(c, ensure_ascii=False, indent=0).encode()); print(t, len(c))
            continue
        tipo, i = p.split(':', 1)
        if tipo == 'm':
            f = js(f'https://api.polyhaven.com/files/{i}')['gltf']; q = f.get('1k') or f.get('2k'); g = q['gltf']
            guarda(f'{D}/modelos/{i}/{os.path.basename(g["url"])}', get(g['url']))
            for rel, inc in (g.get('include') or {}).items(): guarda(f'{D}/modelos/{i}/{rel}', get(inc['url']))
        elif tipo == 'h':
            f = js(f'https://api.polyhaven.com/files/{i}')['hdri']; q = f.get('1k')
            guarda(f'{D}/hdri/{i}.hdr', get(q['hdr']['url']))
        elif tipo == 't':
            f = js(f'https://api.polyhaven.com/files/{i}')
            for mapa in ('Diffuse', 'nor_gl', 'Rough', 'AO', 'Displacement'):
                if mapa in f and '1k' in f[mapa]: guarda(f'{D}/texturas/{i}/{mapa}.jpg', get(f[mapa]['1k'].get('jpg', f[mapa]['1k'].get('png'))['url']))
        elif tipo == 'k':
            html = get(f'https://kenney.nl/assets/{i}').decode('utf-8', 'ignore')
            z = re.findall(r'href="([^"]+\.zip)"', html)
            if not z: print('sin zip', i); continue
            u = z[0] if z[0].startswith('http') else 'https://kenney.nl' + z[0]
            zipfile.ZipFile(io.BytesIO(get(u))).extractall(f'{D}/kenney/{i}')
        print('ok', p, flush=True)
    except Exception as x:
        print('FALLO', p, str(x)[:200], flush=True)
# índice de lo que hay (el motor solo precarga los nombres que estén aquí)
ind = {'modelos': sorted(os.listdir(f'{D}/modelos')) if os.path.isdir(f'{D}/modelos') else [],
       'texturas': sorted(os.listdir(f'{D}/texturas')) if os.path.isdir(f'{D}/texturas') else [],
       'hdri': sorted(f[:-4] for f in os.listdir(f'{D}/hdri')) if os.path.isdir(f'{D}/hdri') else []}
json.dump(ind, open(f'{D}/indice.json', 'w'), indent=0); print('índice:', {k: len(v) for k, v in ind.items()})
