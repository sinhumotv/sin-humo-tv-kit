import json, sys
sys.path.insert(0, '.')
import piezas as P
COD = {2: P.FRIGO, 3: P.AVION_CORTE, 4: P.COCHE_RAYO, 5: P.DIGESTIVO}
K = float(__import__('os').environ.get('K', '2.5'))
def R(anc, d0, d1, dy0=0.06, dy1=0.03, lado=0.18, mira2=None, de_anc=None):
    d0, d1, dy0, dy1, lado = d0 * K, d1 * K, dy0 * K, dy1 * K, lado * K
    return {'de': [de_anc or anc, [lado, dy0, d0]], 'a': [anc, [lado * 0.3, dy1, d1]], 'mira': de_anc or anc, 'mira2': mira2 or anc}
RUTAS = {
 2: [R('nevera', 0.9, 0.6), R('compresor', 0.7, 0.45), None, None, R('carne', 0.5, 0.3, mira2='leche'), None, R('charco', 0.55, 0.32, dy0=0.2, dy1=0.12), R('queso', 0.45, 0.28, mira2='fruta'), R('nevera', 0.6, 1.0, lado=0.1), None],
 3: [R('cabina', 0.6, 0.4, lado=0.3), R('palanca', 0.5, 0.3), R('manometro', 0.45, 0.3), R('puerta', 0.6, 0.45), R('asientos', 0.35, 0.22, lado=0.25), R('puerta', 0.6, 0.4, lado=0.3), R('mascaras', 0.3, 0.2, dy0=0.06, dy1=0.02), R('motor', 0.6, 0.4, lado=-0.3), R('cabina', 0.5, 0.9, lado=0.25), R('ventanillas', 0.3, 0.4, lado=0.3)],
 4: [R('coche', 0.9, 0.6, dy0=0.35, dy1=0.1, de_anc=None, mira2='coche'), R('techo', 0.5, 0.35), R('rueda', 1.3, 0.95), R('quemado', 1.1, 0.8), R('coche', 0.7, 0.5, lado=0.4), R('bajos', 0.5, 0.3, lado=0.3), R('pasajeros', 0.7, 0.5), R('pasajeros', 0.75, 0.55, lado=-0.15), R('rueda', 1.2, 0.85, lado=-0.2), R('coche', 0.6, 1.0, dy0=0.1, dy1=0.3)],
 5: [R('chicle', 2.2, 1.6), {'de': ['cuerpo', [0, 0.15 * K, 0.7 * K]], 'a': ['estomago', [0, 0.02 * K, 0.35 * K]], 'mira': 'esofago', 'mira2': 'estomago'}, R('acido', 0.55, 0.35), R('acido', 0.4, 0.28, lado=-0.2), R('estomago', 0.4, 0.6), R('intestino', 0.7, 0.5), R('intestino', 0.5, 0.35, dy0=-0.05, dy1=-0.1), R('chicle', 2.0, 1.5), R('cuerpo', 0.7, 0.9), R('chicle', 1.6, 2.4)],
}
for n, rs in RUTAS.items():
    f = f'v/v{n}.json'; H = json.load(open(f))
    for e, r in zip(H['escenas'], rs):
        d = e['escena3d']; d['objetos'][0]['codigo'] = COD[n]
        if r: d['ruta'] = r
        else: d.pop('ruta', None)
    json.dump(H, open(f, 'w'), ensure_ascii=False, indent=1)
print('ok')
