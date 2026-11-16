import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from piezas import *

def N(codigo, tam, reserva='', **k): return dict({'tipo': 'nueva', 'codigo': codigo, 'tam': tam, 'reserva': reserva}, **k)
def D(t, d): return {'tipo': 'dia', 'texto': t, 'detalle': d}
def C(v, e): return {'tipo': 'cifra', 'valor': v, 'etiqueta': e}
def E(texto, visual, pieza, cielo='atardecer', camara='acercar', **k):
    return {'hablado': texto, 'subtitulo': texto, 'visual': visual,
            'escena3d': dict({'cielo': cielo, 'suelo': 'ninguno', 'plano': 'detalle', 'foco': 0, 'camara': camara, 'zoom': 1.35, 'objetos': [pieza]}, **k)}

V = []
A = lambda tam, **k: N(ASCENSOR, tam, 'cilindro', **k)
V.append({'titulo': '¿Y si se rompieran los cables del ascensor? 🛗', 'meta': {
    'tema': '¿Qué pasaría si se rompieran todos los cables de un ascensor contigo dentro?', 'titulo': '¿Y si se rompieran los cables del ascensor? 🛗',
    'gancho': 'Spoiler: hay un freno que casi nadie conoce.', 'pregunta': '¿Te da miedo subir en ascensor?', 'hashtags': ['ascensor', 'ingenieria', 'curiosidades', 'quepasariasi', 'ciencia']}, 'escenas': [
    E('Pongamos que vas en un ascensor por la sexta planta… y se rompen todos los cables.', D('SEGUNDO 0', 'Cables rotos'), A(14, vista='todo', sinCables=True), camara='subir'),
    E('Arriba, el motor sigue girando, pero ya no sujeta nada.', D('SEGUNDO 0', 'Cables rotos'), A(6, vista='cables', sinCables=True), camara='orbita'),
    E('Aunque eso es casi imposible: un ascensor cuelga de seis cables o más.', C('6', 'cables de acero'), A(6, vista='cables'), camara='bajar'),
    E('Y cada uno, por sí solo, aguanta el peso de la cabina llena.', D('MINUTO 1', 'Margen de seguridad'), A(6, vista='cables'), camara='acercar', zoom=1.6, mira=[0.5, 0.75]),
    E('Pero si aun así cayera, la cabina empieza a bajar demasiado rápido…', D('MINUTO 1', 'Margen de seguridad'), A(14, vista='todo', sinCables=True, altura=10.2), camara='bajar'),
    E('…y salta el paracaídas: unas mordazas que se clavan en las guías.', D('MINUTO 1', 'El freno oculto'), A(6, vista='freno', frena=True), camara='orbita', zoom=1.5, mira=[0.85, 0.3]),
    E('Saltan chispas, pero la cabina se frena en pocos metros.', D('MINUTO 1', 'El freno oculto'), A(6, vista='freno', frena=True), camara='acercar', zoom=1.9, mira=[0.15, 0.3]),
    E('Dentro, solo notarías un frenazo seco.', D('HORA 1', 'Un susto'), A(5, vista='cabina'), cielo='atardecer', zoom=1.3),
    E('Este freno lo inventó Elisha Otis en 1853, y por eso los ascensores son tan seguros.', C('1853', 'el freno de Otis'), A(14, vista='todo'), camara='alejar', cielo='atardecer'),
    E('¿Te da miedo subir en ascensor?', D('AÑO 100', 'Más seguro que la escalera'), A(5, vista='cabina'), cielo='atardecer', camara='alejar'),
]})

F = lambda tam, **k: N(FRIGO, tam, 'bloque', **k)
V.append({'titulo': '¿Y si tu nevera se estropeara una semana? 🧊', 'meta': {
    'tema': '¿Qué pasaría si tu frigorífico dejara de enfriar durante una semana?', 'titulo': '¿Y si tu nevera se estropeara una semana? 🧊',
    'gancho': 'Lo primero que se estropea no es lo que crees.', 'pregunta': '¿Qué es lo primero que tirarías?', 'hashtags': ['nevera', 'comida', 'hogar', 'quepasariasi', 'curiosidades']}, 'escenas': [
    E('Pongamos que esta noche tu nevera deja de enfriar.', D('SEGUNDO 0', 'Se apaga'), F(8, vista='todo'), camara='acercar'),
    E('Detrás, el compresor, el corazón de la nevera, se para.', D('SEGUNDO 0', 'Se apaga'), F(6, vista='compresor', roto=True), camara='orbita'),
    E('Si no abres la puerta, el frío aguanta unas cuatro horas.', C('4 h', 'de frío con la puerta cerrada'), F(4, vista='termometro'), camara='acercar'),
    E('A partir de ahí la temperatura sube, y pasa de los cinco grados.', D('HORA 1', 'Sube el calor'), F(4, vista='termometro', roto=True, dias=1), camara='acercar'),
    E('Lo primero en peligro: la carne, el pescado y la leche.', D('DÍA 1', 'Carne y leche'), F(6, vista='comida', roto=True, dias=1), camara='travelin', zoom=1.4, mira=[0.4, 0.75]),
    E('El congelador, si está lleno, aguanta unas cuarenta y ocho horas.', C('48 h', 'congelador lleno'), F(5, vista='congelador'), camara='acercar'),
    E('Después el hielo se derrite y gotea hasta el suelo.', D('DÍA 1', 'Se derrite'), F(8, vista='todo', roto=True, dias=2), camara='bajar'),
    E('A la semana, moho en el queso, la fruta y los huevos.', D('SEMANA 1', 'Moho'), F(6, vista='comida', roto=True, dias=7), camara='orbita', zoom=1.4, mira=[0.5, 0.6]),
    E('Y el olor ya no se va solo: hay que vaciarla y limpiarla entera.', D('SEMANA 1', 'Moho'), F(8, vista='todo', roto=True, dias=7), camara='alejar'),
    E('¿Qué es lo primero que tirarías?', D('AÑO 100', 'A limpiar'), F(4, vista='termometro', roto=True, dias=7), camara='alejar'),
]})

P = lambda tam, **k: N(AVION_CORTE, tam, 'avion', **k)
V.append({'titulo': '¿Y si abrieras la puerta del avión en pleno vuelo? ✈️', 'meta': {
    'tema': '¿Qué pasaría si intentaras abrir la puerta de un avión en pleno vuelo?', 'titulo': '¿Y si abrieras la puerta del avión en pleno vuelo? ✈️',
    'gancho': 'Aunque quisieras, no podrías. Te explico por qué.', 'pregunta': '¿Ventanilla o pasillo?', 'hashtags': ['avion', 'aviacion', 'viajes', 'quepasariasi', 'curiosidades']}, 'escenas': [
    E('Pongamos que vas en un avión a diez mil metros e intentas abrir la puerta.', D('SEGUNDO 0', 'A 10.000 metros'), P(20, vista='todo'), camara='travelin', zoom=0.9),
    E('Tiras de la palanca… y no pasa nada.', D('SEGUNDO 0', 'A 10.000 metros'), P(5, vista='puerta'), camara='acercar', zoom=1.6, mira=[0.5, 0.45]),
    E('Dentro, el aire está presurizado: empuja la puerta hacia fuera con varias toneladas.', C('+5 toneladas', 'empujando la puerta'), P(5, vista='puerta'), camara='orbita', zoom=1.3),
    E('Y la puerta es más grande que el hueco: se abre hacia dentro, contra esa fuerza.', D('MINUTO 1', 'Imposible de abrir'), P(5, vista='puerta'), camara='acercar', zoom=1.6, mira=[0.5, 0.45]),
    E('Ni con todas tus fuerzas lo conseguirías.', D('MINUTO 1', 'Imposible de abrir'), P(20, vista='cabina'), camara='travelin', zoom=1.2),
    E('Solo en tierra, sin presión, la puerta se abre con facilidad.', D('HORA 1', 'En tierra'), P(5, vista='puerta', abierta=True, texto='OPEN'), cielo='atardecer', camara='orbita'),
    E('Si el avión perdiera la presión por otro motivo, caerían las máscaras de oxígeno.', D('HORA 1', 'Máscaras'), P(20, vista='cabina', mascaras=True), camara='acercar', zoom=1.3),
    E('Y el piloto bajaría a tres mil metros, donde ya se respira bien.', C('3.000 m', 'altura segura'), P(9, vista='ala'), cielo='atardecer', camara='bajar'),
    E('Así que, tranquilo: esa puerta no se abre en pleno vuelo.', D('AÑO 100', 'A salvo'), P(20, vista='todo'), cielo='atardecer', camara='alejar', zoom=0.9),
    E('¿Tú eres de ventanilla o de pasillo?', D('AÑO 100', 'A salvo'), P(20, vista='cabina'), cielo='atardecer', camara='alejar'),
]})

K = lambda tam, **k: N(COCHE_RAYO, tam, 'coche', **k)
V.append({'titulo': '¿Y si te cayera un rayo dentro del coche? ⚡', 'meta': {
    'tema': '¿Qué pasaría si un rayo cayera sobre tu coche mientras conduces?', 'titulo': '¿Y si te cayera un rayo dentro del coche? ⚡',
    'gancho': 'No te salvan las ruedas. Te salva otra cosa.', 'pregunta': '¿Sabías que no son las ruedas?', 'hashtags': ['rayo', 'tormenta', 'coche', 'quepasariasi', 'ciencia']}, 'escenas': [
    E('Pongamos que conduces bajo una tormenta y un rayo cae sobre tu coche.', D('SEGUNDO 0', 'El rayo'), K(9, vista='todo'), cielo='tormenta', camara='subir', efecto='lluvia', zoom=0.85, mira=[0.5, 0.2]),
    E('Una descarga de cientos de millones de voltios.', C('300 millones', 'de voltios'), K(9, vista='todo'), cielo='tormenta', camara='acercar', efecto='lluvia', zoom=1.1, mira=[0.5, 0.2]),
    E('Mucha gente cree que te salvan las ruedas de goma.', D('SEGUNDO 0', 'El mito'), K(4, vista='rueda'), cielo='tormenta', camara='orbita'),
    E('Pero no: un rayo que ha atravesado kilómetros de aire no se para por unos centímetros de goma.', D('SEGUNDO 0', 'El mito'), K(4, vista='rueda'), cielo='tormenta', camara='acercar'),
    E('Lo que te salva es la carrocería de metal.', D('MINUTO 1', 'La jaula'), K(9, vista='jaula', rayo=False), cielo='noche', camara='orbita', zoom=1.8, mira=[0.5, 0.45]),
    E('La corriente la recorre por fuera y salta al suelo por debajo del coche.', D('MINUTO 1', 'La jaula'), K(9, vista='jaula', rayo=False), cielo='noche', camara='bajar', zoom=1.8, mira=[0.5, 0.45]),
    E('Se llama jaula de Faraday, y por eso dentro estás a salvo.', D('MINUTO 1', 'La jaula'), K(4, vista='dentro'), cielo='tormenta', camara='acercar', zoom=1.3),
    E('Eso sí: no toques las partes metálicas, y quédate dentro hasta que pase.', D('HORA 1', 'Qué hacer'), K(4, vista='dentro'), cielo='tormenta', camara='orbita'),
    E('Lo peor que puede pasar: se fundan los aparatos electrónicos o se queme una rueda.', D('DÍA 1', 'Daños'), K(4, vista='rueda'), cielo='noche', camara='acercar'),
    E('¿Sabías que no eran las ruedas?', D('AÑO 100', 'A salvo'), K(9, vista='todo'), cielo='tormenta', camara='alejar', efecto='lluvia', zoom=0.85, mira=[0.5, 0.2]),
]})

G = lambda tam, **k: N(DIGESTIVO, tam, 'cuerpo', **k)
V.append({'titulo': '¿Y si te tragaras un chicle? 🍬', 'meta': {
    'tema': '¿Qué pasaría si te tragaras un chicle?', 'titulo': '¿Y si te tragaras un chicle? 🍬',
    'gancho': 'No, no se queda siete años dentro.', 'pregunta': '¿Te habías tragado alguno?', 'hashtags': ['chicle', 'cuerpohumano', 'mitos', 'quepasariasi', 'ciencia']}, 'escenas': [
    E('Pongamos que te tragas un chicle sin querer.', D('SEGUNDO 0', 'Al estómago'), G(6, vista='chicle'), cielo='atardecer', camara='orbita', zoom=0.8),
    E('Baja por el esófago y llega al estómago en unos segundos.', D('SEGUNDO 0', 'Al estómago'), G(12, vista='todo'), camara='bajar'),
    E('Allí, el ácido empieza a deshacer la comida que lo rodea.', D('MINUTO 1', 'El ácido'), G(6, vista='estomago'), camara='acercar', zoom=1.5, mira=[0.5, 0.4]),
    E('Pero la goma del chicle no se digiere: sale casi intacta.', D('HORA 1', 'Indigerible'), G(6, vista='estomago'), camara='orbita', zoom=2.0, mira=[0.47, 0.33]),
    E('El cuerpo la trata como cualquier cosa que no puede usar.', D('HORA 1', 'Indigerible'), G(12, vista='todo'), camara='acercar'),
    E('Y la empuja por el intestino, junto con el resto de la comida.', D('DÍA 1', 'El intestino'), G(7, vista='intestino', dia=1), camara='travelin'),
    E('En uno o dos días, sale por donde ya imaginas.', D('DÍA 1', 'El intestino'), G(7, vista='intestino', dia=2.5), camara='bajar'),
    E('Lo de que se queda siete años dentro es un mito.', C('7 años', 'falso'), G(6, vista='chicle'), cielo='atardecer', camara='acercar', zoom=0.8),
    E('El problema solo llega si alguien, sobre todo un niño, se traga muchos seguidos.', D('SEMANA 1', 'Con cuidado'), G(12, vista='todo'), camara='alejar'),
    E('¿Te habías tragado alguno?', D('AÑO 100', 'Mito desmontado'), G(6, vista='chicle'), cielo='atardecer', camara='alejar', zoom=0.8),
]})

os.makedirs(sys.argv[1], exist_ok=True)
for k, h in enumerate(V, 1): json.dump(h, open(os.path.join(sys.argv[1], f'v{k}.json'), 'w'), ensure_ascii=False, indent=1)
print('ok', [len(h['escenas']) for h in V], [sum(len(e['hablado'].split()) for e in h['escenas']) for h in V])
