"""Fotos reales para los vídeos de sin humo TV (v10).

El entorno de trabajo no puede descargar de Wikimedia Commons ni de webs oficiales (la red lo bloquea),
así que las fotos se traen con el navegador integrado de la app de Claude en el PC del usuario:

1. python3 fotos.py js        -> imprime el código JavaScript que hay que ejecutar UNA vez con la herramienta
                                 javascript_tool del navegador (pestaña abierta en https://commons.wikimedia.org).
                                 Define buscar(q) y get(titulo, k).
2. En el navegador:  await buscar("manifestación vivienda Madrid")  -> lista de [título, tamaño, licencia, autor, fecha]
   Elige 1-3 fotos (shorts) o hasta 6 (largos): licencia libre (CC0, CC BY, CC BY-SA, dominio público), recientes
   si son de la noticia, sin menores ni víctimas, sin caras en primer plano de particulares, sin logos protagonistas
   ni pancartas de un partido concreto (neutralidad).
3. Para cada foto, UNA llamada:  await get("File:Nombre.jpg", 0)  (k = 0, 1, 2...). La respuesta es demasiado grande
   para la conversación y se guarda sola en un archivo de tool-results: es lo que se busca, no es un error.
4. python3 fotos.py extraer <carpeta>/fotos  -> guarda f0.jpg, f1.jpg... y creditos.json (autor, licencia, página)
   leyendo esos archivos de tool-results de la sesión.
5. En escenas.js:  A.precarga([ruta...])  y  A.foto(ruta, cx, cy, w, h, rot, escala, 'Autor · Wikimedia Commons · CC BY-SA 4.0').
   Pon el crédito también en la descripción de cada red.
"""
import sys, os, json, glob, base64

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


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'js':
        print(JS)
    elif len(sys.argv) > 2 and sys.argv[1] == 'extraer':
        extraer(sys.argv[2])
    else:
        print(__doc__)
