import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from piezas import EDIFICIO
# un solo recorrido de cámara en curva por todo el edificio
W = [(['edificio', [0.0, 0.0, 1.6]], 'edificio'),
     (['salon1', [0.06, 0.03, 0.42]], 'tv1'),
     (['ascensor', [0.03, 0.0, 0.28]], 'ascensor'),
     (['salon2', [0.05, 0.02, 0.45]], 'salon2'),
     (['bomba', [0.06, 0.05, 0.22]], ['bomba', [-0.04, 0.0, 0]]),
     (['grifo3', [0.03, 0.03, 0.25]], 'grifo3'),
     (['nevera3', [-0.04, 0.02, 0.3]], 'nevera3'),
     (['movil1', [0.006, 0.004, 0.045]], 'movil1'),
     (['calle', [0.2, -0.05, 0.28]], 'semaforo'),
     (['portal', [0.05, 0.03, 0.4]], 'portal'),
     (['portal', [0.02, 0.08, 0.75]], 'portal'),
     (['edificio', [0.02, 0.0, 1.75]], 'edificio')]
CAM = [c for c, m in W]; MIR = [m for c, m in W]
def N(**k): return dict({'tipo': 'nueva', 'codigo': EDIFICIO, 'tam': 18, 'reserva': 'bloque'}, **k)
def D(t, d): return {'tipo': 'dia', 'texto': t, 'detalle': d}
def C(v, e): return {'tipo': 'cifra', 'valor': v, 'etiqueta': e}
ESC = []
def E(texto, visual, estado, sonidos=(), sacudidas=None):
    i = len(ESC)
    d = {'cielo': 'noche', 'luz': 'nocturna', 'contorno': False, 'suelo': 'ninguno', 'plano': 'detalle', 'foco': 0, 'camara': 'acercar', 'continua': True,
         'objetos': [N(**estado)], 'ruta': {'de': CAM[i], 'a': CAM[min(i + 1, len(CAM) - 1)], 'mira': MIR[i], 'mira2': MIR[min(i + 1, len(MIR) - 1)], 'continua': True, 'mantener': 2.4, 'camino': CAM, 'miras': MIR, 't0': max(0, i - 0.5), 't1': i + 0.5 if i < 10 else len(CAM) - 1},
         'sonidos': [list(x) for x in sonidos]}
    if sacudidas: d['sacudidas'] = sacudidas
    ESC.append({'hablado': texto, 'subtitulo': texto, 'visual': visual, 'escena3d': d})
E('Pongamos que esta noche se va la luz en todo tu edificio.', D('SEGUNDO 0', 'Apagón'), {'luz': [1, 0], 'queda': 1}, [(0.0, 'zumbido'), (0.2, 'chispa'), (0.45, 'chispa')])
E('La tele, la nevera y la calefacción se apagan a la vez.', D('SEGUNDO 0', 'Apagón'), {'luz': 0, 'ultimo': 1}, [(0.42, 'chispa'), (0.45, 'golpe')])
E('Si alguien iba en el ascensor, se queda parado entre dos plantas.', D('MINUTO 1', 'Atrapados'), {'luz': 0, 'cae': 0.35}, [(0.35, 'impacto'), (0.6, 'alarma')], [[0.35, 0.6]])
E('Enseguida, los vecinos encienden la linterna del móvil.', D('MINUTO 5', 'Linternas'), {'luz': 0, 'linternas': [0, 1], 'caido': True}, [(0.22, 'pop'), (0.32, 'pop'), (0.42, 'pop'), (0.52, 'pop')])
E('En el tejado, la bomba que sube el agua se para.', D('HORA 1', 'Sin agua'), {'luz': 0, 'linternas': 1, 'caido': True}, [(0.2, 'motor'), (0.6, 'golpe')])
E('Y en los pisos de arriba deja de salir agua del grifo.', D('HORA 2', 'Sin agua'), {'luz': 0, 'linternas': 1, 'caido': True, 'grifo': 3, 'corta': 0.45}, [(0.0, 'agua'), (0.55, 'goteo'), (0.7, 'goteo')])
E('Al día siguiente, el congelador se derrite y gotea hasta el suelo.', D('DÍA 1', 'La nevera'), {'luz': 0, 'linternas': 1, 'caido': True, 'velas': [0, 1], 'charco': [0, 1]}, [(0.3, 'goteo'), (0.5, 'goteo'), (0.7, 'goteo')])
E('Los móviles se quedan sin batería, y solo quedan las velas.', D('DÍA 2', 'Velas'), {'luz': 0, 'linternas': [1, 0], 'bateria': [1, 0], 'velas': 1, 'caido': True, 'charco': 1}, [(0.6, 'ding')])
E('En la calle, sin farolas ni semáforos, la noche es oscura de verdad.', D('DÍA 3', 'Oscuridad'), {'luz': 0, 'velas': 1, 'bateria': 0, 'portal': True, 'caido': True, 'charco': 1}, [(0.1, 'viento')])
E('A la semana, los vecinos se juntan en el portal a la luz de las velas.', D('SEMANA 1', 'Juntos'), {'luz': 0, 'velas': 1, 'bateria': 0, 'portal': True, 'caido': True, 'charco': 1}, [(0.3, 'fuego')])
E('¿Tú qué echarías más de menos?', D('SEMANA 1', 'Juntos'), {'luz': 0, 'velas': 1, 'bateria': 0, 'portal': True, 'caido': True, 'charco': 1}, [(0.2, 'ding')])
meta = {'tema': '¿Qué pasaría si se fuera la luz en todo tu edificio durante una semana?', 'titulo': '¿Y si se fuera la luz en tu edificio una semana? 🕯️',
        'gancho': 'Lo primero que falla no es la luz, es el agua.', 'pregunta': '¿Tú qué echarías más de menos?', 'hashtags': ['apagon', 'edificio', 'vecinos', 'quepasariasi', 'curiosidades']}
H = {'titulo': meta['titulo'], 'meta': meta, 'escenas': ESC}
if __name__ == '__main__':
    json.dump(H, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1); print('ok', len(ESC), sum(len(e['hablado'].split()) for e in ESC))
