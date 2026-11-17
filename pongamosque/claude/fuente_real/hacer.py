import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from piezas import ILU
# (17-nov-2026) UN SOLO RECORRIDO DE CÁMARA CONTINUO por la cocina (como las referencias): cada frase sigue el movimiento donde lo dejó la anterior
W = [(['cocina', [-0.14, 0.0, 0.85]], ['cocina', [-0.2, -0.03, 0]]),
     (['interior', [0.06, 0.02, 0.32]], 'interior'),
     (['compresor', [0.13, 0.42, -0.03]], 'compresor'),
     (['cocina', [-0.2, 0.06, 0.62]], ['cocina', [-0.22, 0.06, 0]]),
     (['termo', [0.07, 0.0, 0.24]], 'termo'),
     (['carne', [0.03, 0.04, 0.17]], 'carne'),
     (['congelador', [0.06, 0.01, 0.32]], 'congelador'),
     (['charco', [0.05, 0.2, 0.3]], 'charco'),
     (['tarta', [0.02, 0.03, 0.17]], 'queso'),
     (['nevera', [0.15, 0.05, 0.5]], 'nevera'),
     (['cocina', [-0.12, 0.01, 0.95]], ['cocina', [-0.18, -0.03, 0]])]
def N(**k): return dict({'tipo': 'nueva', 'codigo': ILU, 'tam': 12, 'reserva': 'bloque'}, **k)
def D(t, d): return {'tipo': 'dia', 'texto': t, 'detalle': d}
def C(v, e): return {'tipo': 'cifra', 'valor': v, 'etiqueta': e}
ESC = []
VIA = {1: ['nevera', [0.02, 0.44, 0.3]]}
# curva global: puntos de cámara (y de mira) de todo el vídeo, con el punto intermedio de la subida al compresor
CAM, MIR, IDX = [], [], []
for i, (c, m) in enumerate(W):
    if i - 1 in VIA: CAM.append(VIA[i - 1]); MIR.append(['nevera', [0.0, 0.12, 0.0]])
    IDX.append(len(CAM)); CAM.append(c); MIR.append(m)
def E(texto, visual, estado, sonidos=(), sacudidas=None):
    i = len(ESC); (c0, m0), (c1, m1) = W[i], W[i + 1]
    d = {'cielo': 'noche', 'luz': 'nocturna', 'contorno': False, 'suelo': 'ninguno', 'plano': 'detalle', 'foco': 0, 'camara': 'acercar', 'continua': True,
         'objetos': [N(**estado)], 'ruta': {'de': c0, 'a': c1, 'mira': m0, 'mira2': m1, 'continua': True, 'camino': CAM, 'miras': MIR, 't0': IDX[i], 't1': IDX[i + 1], **({'pot': 0.7} if i in VIA else {})}, 'sonidos': [list(x) for x in sonidos]}
    if sacudidas: d['sacudidas'] = sacudidas
    ESC.append({'hablado': texto, 'subtitulo': texto, 'visual': visual, 'escena3d': d})
E('Pongamos que esta noche tu nevera deja de enfriar.', D('SEGUNDO 0', 'Se apaga'), {'puerta': 1, 'apaga': 0.62, 'reloj': [23.0, 23.1], 'persona': True}, [(0.0, 'zumbido'), (0.66, 'chispa')])
E('Detrás, el compresor, el corazón de la nevera, se para.', D('SEGUNDO 0', 'Se apaga'), {'puerta': 1, 'roto': True, 'parar': 0.6, 'reloj': [23.1, 23.2], 'persona': True}, [(0.0, 'motor'), (0.6, 'golpe')], [[0.6, 0.5]])
E('Si no abres la puerta, el frío aguanta unas cuatro horas.', C('4 h', 'de frío con la puerta cerrada'), {'puerta': [1, 0], 'roto': True, 'temp': 4, 'reloj': [23.2, 27.0], 'persona': 'sale'}, [(0.15, 'portazo'), (0.45, 'tictac')])
E('A partir de ahí la temperatura sube, y pasa de los cinco grados.', D('HORA 4', 'Sube el calor'), {'puerta': 0, 'roto': True, 'temp': [4, 8], 'dias': [0.2, 0.5], 'reloj': 27.0}, [(0.55, 'ding'), (0.85, 'alarma')])
E('Lo primero en peligro: la carne, el pescado y la leche.', D('DÍA 1', 'Carne y leche'), {'puerta': [0, 1], 'roto': True, 'temp': 8, 'dias': [0.5, 1]}, [(0.1, 'portazo')])
E('El congelador, si está lleno, aguanta unas cuarenta y ocho horas.', C('48 h', 'congelador lleno'), {'puerta': 1, 'congeladorAbierto': [0, 1], 'roto': True, 'dias': [1, 1.4]}, [(0.1, 'viento'), (0.6, 'crujido')])
E('Después el hielo se derrite y gotea hasta el suelo.', D('DÍA 2', 'Se derrite'), {'puerta': 1, 'congeladorAbierto': 1, 'roto': True, 'dias': [1.4, 3.6]}, [(0.1, 'goteo'), (0.3, 'goteo'), (0.5, 'agua'), (0.7, 'goteo'), (0.9, 'goteo')])
E('A la semana, moho en el queso, la fruta y los huevos.', D('SEMANA 1', 'Moho'), {'puerta': 1, 'congeladorAbierto': [1, 0], 'roto': True, 'dias': [3.6, 7]}, [(0.05, 'burbujas'), (0.4, 'crujido'), (0.7, 'burbujas')])
E('Y el olor ya no se va solo: hay que vaciarla y limpiarla entera.', D('SEMANA 1', 'Moho'), {'puerta': 1, 'congeladorAbierto': 0, 'roto': True, 'dias': 7, 'olor': True}, [(0.0, 'zumbido'), (0.5, 'zumbido')])
E('¿Qué es lo primero que tirarías?', D('AÑO 100', 'A limpiar'), {'puerta': 1, 'congeladorAbierto': 0, 'roto': True, 'dias': 7, 'olor': True}, [(0.2, 'ding')])
meta = {'tema': '¿Qué pasaría si tu frigorífico dejara de enfriar durante una semana?', 'titulo': '¿Y si tu nevera se estropeara una semana? 🧊',
        'gancho': 'Lo primero que se estropea no es lo que crees.', 'pregunta': '¿Qué es lo primero que tirarías?', 'hashtags': ['nevera', 'comida', 'hogar', 'quepasariasi', 'curiosidades']}
H = {'titulo': meta['titulo'], 'meta': meta, 'escenas': ESC}
if __name__ == '__main__':
    json.dump(H, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1); print('ok', len(ESC), sum(len(e['hablado'].split()) for e in ESC))
