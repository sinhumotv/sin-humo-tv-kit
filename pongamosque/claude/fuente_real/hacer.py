import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from piezas import COCINA
def N(**k): return dict({'tipo': 'nueva', 'codigo': COCINA, 'tam': 12, 'reserva': 'bloque'}, **k)
def D(t, d): return {'tipo': 'dia', 'texto': t, 'detalle': d}
def C(v, e): return {'tipo': 'cifra', 'valor': v, 'etiqueta': e}
def P(a, d0, d1, m2=None, dur=1, de=None):
    return {'de': [de or a, d0], 'a': [a, d1], 'mira': de or a, 'mira2': m2 or a, 'dur': dur}
def E(texto, visual, estado, planos, sonidos=(), sacudidas=None):
    d = {'cielo': 'noche', 'luz': 'nocturna', 'contorno': False, 'suelo': 'ninguno', 'plano': 'detalle', 'foco': 0, 'camara': 'acercar',
         'objetos': [N(**estado)], 'ruta': planos, 'sonidos': [list(x) for x in sonidos]}
    if sacudidas: d['sacudidas'] = sacudidas
    return {'hablado': texto, 'subtitulo': texto, 'visual': visual, 'escena3d': d}
ESC = [
 E('Pongamos que esta noche tu nevera deja de enfriar.', D('SEGUNDO 0', 'Se apaga'), {'puerta': 1, 'apaga': 0.62, 'reloj': [23.0, 23.1], 'persona': True},
   [{'de': ['cocina', [-0.14, 0.0, 0.85]], 'a': ['cocina', [-0.16, -0.01, 0.72]], 'mira': ['cocina', [-0.2, -0.03, 0]], 'mira2': ['cocina', [-0.21, -0.03, 0]], 'dur': 1.1}, P('interior', [0.05, 0.02, 0.22], [0.03, 0.01, 0.17], dur=1.3)],
   [(0.0, 'zumbido'), (0.66, 'chispa')]),
 E('Detrás, el compresor, el corazón de la nevera, se para.', D('SEGUNDO 0', 'Se apaga'), {'puerta': 0, 'sinPared': True, 'parar': 0.5},
   [P('compresor', [0.1, 0.06, -0.26], [0.07, 0.04, -0.2], dur=1), P('compresor', [0.05, 0.02, -0.14], [0.035, 0.01, -0.11], dur=1.2)],
   [(0.0, 'motor'), (0.5, 'golpe')], [[0.5, 0.6]]),
 E('Si no abres la puerta, el frío aguanta unas cuatro horas.', C('4 h', 'de frío con la puerta cerrada'), {'puerta': 0, 'roto': True, 'temp': 4, 'reloj': [23.1, 27.0]},
   [P('nevera', [0.26, 0.05, 0.75], [0.2, 0.04, 0.62], dur=1), P('reloj', [0.02, -0.01, 0.16], [0.0, 0.0, 0.12], dur=1.3)],
   [(0.45, 'tictac')]),
 E('A partir de ahí la temperatura sube, y pasa de los cinco grados.', D('HORA 4', 'Sube el calor'), {'puerta': 0, 'roto': True, 'temp': [4, 8]},
   [P('termo', [0.06, 0.02, 0.32], [0.04, 0.015, 0.26], dur=1.2), P('termo', [-0.02, 0.0, 0.2], [-0.01, 0.0, 0.17], dur=1)],
   [(0.55, 'ding'), (0.85, 'alarma')]),
 E('Lo primero en peligro: la carne, el pescado y la leche.', D('DÍA 1', 'Carne y leche'), {'puerta': [0, 1], 'roto': True, 'dias': 1},
   [P('nevera', [0.18, 0.04, 0.48], [0.12, 0.03, 0.38], 'interior', 0.9), P('carne', [0.02, 0.06, 0.08], [0.01, 0.045, 0.06], dur=1), P('leche', [0.04, 0.02, 0.18], [0.03, 0.015, 0.14], dur=1)],
   [(0.1, 'portazo')]),
 E('El congelador, si está lleno, aguanta unas cuarenta y ocho horas.', C('48 h', 'congelador lleno'), {'puerta': 0, 'congeladorAbierto': 1, 'roto': True, 'dias': 0.6},
   [P('congelador', [0.08, 0.01, 0.36], [0.06, 0.005, 0.3], dur=1.1), P('hielo', [0.03, 0.01, 0.2], [0.02, 0.005, 0.16], dur=1)],
   [(0.05, 'viento'), (0.55, 'crujido')]),
 E('Después el hielo se derrite y gotea hasta el suelo.', D('DÍA 2', 'Se derrite'), {'puerta': 0.15, 'congeladorAbierto': 1, 'roto': True, 'dias': [1, 3.6]},
   [P('hielo', [0.03, 0.01, 0.2], [0.02, 0.005, 0.16], dur=1), P('charco', [0.05, 0.22, 0.32], [0.04, 0.17, 0.26], dur=1.3)],
   [(0.1, 'goteo'), (0.3, 'goteo'), (0.5, 'agua'), (0.7, 'goteo'), (0.9, 'goteo')]),
 E('A la semana, moho en el queso, la fruta y los huevos.', D('SEMANA 1', 'Moho'), {'puerta': 1, 'roto': True, 'dias': [3.5, 7]},
   [P('queso', [0.04, 0.04, 0.15], [0.03, 0.03, 0.12], dur=1), P('tarta', [0.02, 0.02, 0.09], [0.01, 0.015, 0.065], dur=1), P('fruta', [0.0, 0.07, 0.13], [0.0, 0.055, 0.1], dur=1)],
   [(0.05, 'burbujas'), (0.4, 'crujido'), (0.7, 'burbujas')]),
 E('Y el olor ya no se va solo: hay que vaciarla y limpiarla entera.', D('SEMANA 1', 'Moho'), {'puerta': 1, 'roto': True, 'dias': 7},
   [P('olor', [0.16, 0.04, 0.42], [0.11, 0.03, 0.34], 'nevera', 1.1), P('interior', [0.04, 0.02, 0.18], [0.03, 0.01, 0.14], dur=1.2)],
   [(0.0, 'zumbido'), (0.5, 'zumbido')]),
 E('¿Qué es lo primero que tirarías?', D('AÑO 100', 'A limpiar'), {'puerta': 1, 'roto': True, 'dias': 7},
   [{'de': ['cocina', [-0.16, -0.01, 0.7]], 'a': ['cocina', [-0.12, 0.01, 0.92]], 'mira': ['cocina', [-0.21, -0.03, 0]], 'mira2': ['cocina', [-0.18, -0.03, 0]], 'dur': 1}], [(0.2, 'ding')]),
]
meta = {'tema': '¿Qué pasaría si tu frigorífico dejara de enfriar durante una semana?', 'titulo': '¿Y si tu nevera se estropeara una semana? 🧊',
        'gancho': 'Lo primero que se estropea no es lo que crees.', 'pregunta': '¿Qué es lo primero que tirarías?', 'hashtags': ['nevera', 'comida', 'hogar', 'quepasariasi', 'curiosidades']}
H = {'titulo': meta['titulo'], 'meta': meta, 'escenas': ESC}
if __name__ == '__main__':
    json.dump(H, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1); print('ok', len(ESC), sum(len(e['hablado'].split()) for e in ESC))
