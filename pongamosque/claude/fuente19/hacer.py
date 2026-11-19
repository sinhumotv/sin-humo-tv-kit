import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from piezas import NIEVE
W = [(['calle', [0.0, 0.06, 0.95]], 'calle'),
     (['tejados', [0.06, 0.14, 0.85]], 'tejados'),
     (['coche', [0.06, 0.06, 0.32]], 'coche'),
     (['semaforo', [0.07, 0.0, 0.3]], 'semaforo'),
     (['portal', [0.03, 0.02, 0.32]], 'portal'),
     (['palas', [0.06, 0.05, 0.45]], 'palas'),
     (['arbol', [0.04, 0.02, 0.4]], 'arbol'),
     (['carretera', [0.0, 0.1, 0.55]], 'carretera'),
     (['muneco', [-0.04, 0.03, 0.35]], 'muneco'),
     (['calle', [0.0, 0.08, 1.05]], 'calle')]
CAM = [c for c, m in W] + [['calle', [0.0, 0.12, 1.25]]]; MIR = [m for c, m in W] + ['calle']
def N(**k): return dict({'tipo': 'nueva', 'codigo': NIEVE, 'tam': 20, 'reserva': 'bloque'}, **k)
def D(t, d): return {'tipo': 'dia', 'texto': t, 'detalle': d}
def C(v, e): return {'tipo': 'cifra', 'valor': v, 'etiqueta': e}
ESC = []
def E(texto, visual, estado, sonidos=(), noche=True, nevando=True):
    i = len(ESC)
    d = {'cielo': 'noche' if noche else 'amanecer', 'contorno': False, 'suelo': 'ninguno', 'plano': 'detalle', 'foco': 0, 'camara': 'acercar', 'continua': True,
         'objetos': [N(**estado)], 'ruta': {'de': CAM[i], 'a': CAM[i + 1], 'mira': MIR[i], 'mira2': MIR[i + 1], 'continua': True, 'mantener': 2.4,
                                            'camino': CAM, 'miras': MIR, 't0': max(0, i - 0.5), 't1': i + 0.5 if i < 9 else len(CAM) - 1},
         'sonidos': [list(x) for x in sonidos]}
    if noche: d['luz'] = 'nocturna'
    if nevando: d['efecto'] = 'nieve'
    ESC.append({'hablado': texto, 'subtitulo': texto, 'visual': visual, 'escena3d': d})
E('Pongamos que esta noche empieza a nevar en tu ciudad, y no para.', D('SEGUNDO 0', 'Nieve'), {'nieve': [0, 0.12]}, [(0.1, 'viento')])
E('En una hora, los tejados ya están blancos.', D('HORA 1', 'Todo blanco'), {'nieve': [0.12, 0.35]}, [(0.2, 'viento')])
E('Los coches desaparecen poco a poco bajo la nieve.', D('HORA 6', 'Coches'), {'nieve': [0.35, 0.6]}, [(0.4, 'crujido')])
E('Los semáforos siguen cambiando, pero ya no pasa nadie.', D('HORA 8', 'Calles vacías'), {'nieve': [0.6, 0.7]}, [(0.3, 'tictac')])
E('Al amanecer, medio metro de nieve bloquea los portales.', C('50 cm', 'de nieve en la calle'), {'nieve': [0.7, 0.85], 'empuja': True, 'dia': True}, [(0.35, 'golpe'), (0.55, 'golpe')], noche=False)
E('Los vecinos salen con palas para abrir un camino.', D('DÍA 1', 'Palas'), {'nieve': 0.85, 'vecinos': True, 'palas': [0, 1], 'dia': True}, [(0.2, 'crujido'), (0.5, 'crujido'), (0.8, 'crujido')], noche=False, nevando=False)
E('Las ramas se doblan por el peso, y alguna se rompe.', D('DÍA 2', 'Peso'), {'nieve': 0.85, 'vecinos': True, 'palas': 1, 'rama': [0, 1], 'dia': True}, [(0.6, 'crujido'), (0.65, 'impacto')], noche=False, nevando=False)
E('Por fin llega la quitanieves y abre la calle.', D('DÍA 3', 'Quitanieves'), {'nieve': 0.85, 'vecinos': True, 'palas': 1, 'rama': 1, 'quita': [0, 1], 'dia': True}, [(0.1, 'motor'), (0.5, 'motor')], noche=False, nevando=False)
E('Y los niños levantan el muñeco de nieve más grande del barrio.', D('SEMANA 1', 'Muñeco'), {'nieve': 0.85, 'vecinos': True, 'palas': 1, 'rama': 1, 'quita': True, 'muneco': [0, 1], 'dia': True}, [(0.3, 'pop'), (0.6, 'pop'), (0.85, 'ding')], noche=False, nevando=False)
E('¿Tú qué harías con un día así?', D('SEMANA 1', 'Muñeco'), {'nieve': 0.85, 'vecinos': True, 'palas': 1, 'rama': 1, 'quita': True, 'muneco': 1, 'dia': True}, [(0.2, 'ding')], noche=False, nevando=False)
meta = {'tema': '¿Qué pasaría si empezara a nevar en tu ciudad y no parara en toda la noche?', 'titulo': '¿Y si nevara toda la noche en tu ciudad? ❄️',
        'gancho': 'Lo más difícil no es la nieve. Es salir del portal.', 'pregunta': '¿Tú qué harías con un día así?', 'hashtags': ['nieve', 'nevada', 'invierno', 'quepasariasi', 'curiosidades']}
H = {'titulo': meta['titulo'], 'meta': meta, 'escenas': ESC}
if __name__ == '__main__':
    json.dump(H, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1); print('ok', len(ESC), sum(len(e['hablado'].split()) for e in ESC))
