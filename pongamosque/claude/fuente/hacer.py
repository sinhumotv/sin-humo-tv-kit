import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from piezas import *

def N(codigo, tam, reserva='', anim='', **k):
    return dict({'tipo': 'nueva', 'codigo': codigo, 'tam': tam, 'reserva': reserva, **({'anim': anim} if anim else {})}, **k)

def D(t, d): return {'tipo': 'dia', 'texto': t, 'detalle': d}
def C(v, e): return {'tipo': 'cifra', 'valor': v, 'etiqueta': e}

def E(texto, visual, e3):
    return {'hablado': texto, 'subtitulo': texto, 'visual': visual, 'escena3d': e3}

V = []
# 1 · ABEJAS
V.append({'titulo': '¿Y si desaparecieran todas las abejas? 🐝', 'meta': {
    'tema': '¿Qué pasaría si desaparecieran todas las abejas del planeta?', 'titulo': '¿Y si desaparecieran todas las abejas? 🐝',
    'gancho': 'Sin abejas no se acaba el mundo… pero tu nevera cambiaría muchísimo.', 'pregunta': '¿Qué fruta echarías más de menos?',
    'hashtags': ['abejas', 'naturaleza', 'ciencia', 'quepasariasi', 'curiosidades']}, 'escenas': [
    E('Pongamos que mañana desaparecen todas las abejas del planeta.', D('SEGUNDO 0', 'Adiós abejas'),
      {'cielo': 'atardecer', 'suelo': 'hierba', 'plano': 'detalle', 'foco': 0, 'camara': 'orbita', 'objetos': [N(ABEJA, 5, 'emoji', 'flotar', emoji='🐝'), N(FLORES, 9, 'arbusto')]}),
    E('Las colmenas se quedan en silencio: millones de panales, vacíos.', D('MINUTO 1', 'Colmenas vacías'),
      {'cielo': 'atardecer', 'suelo': 'hierba', 'plano': 'detalle', 'foco': 0, 'camara': 'acercar', 'objetos': [N(PANAL, 7, 'bloque', vacio=True)]}),
    E('En el campo, nadie lleva el polen de flor en flor.', D('HORA 1', 'Sin polinizar'),
      {'cielo': 'dia', 'suelo': 'hierba', 'plano': 'aerea', 'camara': 'travelin', 'objetos': [N(FLORES, 14, 'arbusto', cantidad=70), {'tipo': 'arboles', 'cantidad': 8, 'z': -8}]}),
    E('Y muchas flores se marchitan sin dar fruto.', D('DÍA 1', 'Flores sin fruto'),
      {'cielo': 'atardecer', 'suelo': 'hierba', 'plano': 'detalle', 'foco': 0, 'camara': 'acercar', 'objetos': [N(FLORES_MUSTIAS, 7, 'arbusto', cantidad=9)]}),
    E('Tres de cada cuatro cultivos dependen en parte de los polinizadores.', C('3 de 4', 'cultivos los necesitan'),
      {'cielo': 'dia', 'suelo': 'hierba', 'plano': 'aerea', 'camara': 'orbita', 'objetos': [{'tipo': 'arboles', 'cantidad': 14}, {'tipo': 'casa', 'cantidad': 2, 'x': 8, 'z': -5}]}),
    E('En el súper, fresas, manzanas y almendras empiezan a escasear.', D('SEMANA 1', 'Fruta agotada'),
      {'cielo': 'dia', 'suelo': 'ciudad', 'plano': 'detalle', 'foco': 0, 'camara': 'travelin', 'objetos': [N(ESTANTERIA, 9, 'monedas', vacia=True)]}),
    E('Y lo poco que queda, sube de precio.', D('MES 1', 'Precios por las nubes'),
      {'cielo': 'atardecer', 'suelo': 'ciudad', 'plano': 'detalle', 'foco': 0, 'camara': 'subir', 'objetos': [{'tipo': 'billetes', 'cantidad': 6, 'anim': 'crecer'}]}),
    E('Habría que polinizar a mano, flor a flor, como ya pasa en zonas de China.', D('AÑO 1', 'Polinizar a mano'),
      {'cielo': 'dia', 'suelo': 'hierba', 'plano': 'fachada', 'foco': 0, 'camara': 'orbita', 'objetos': [N(POLINIZAR, 8, 'arboles')]}),
    E('El trigo y el arroz no necesitan abejas: no pasaríamos hambre…', D('AÑO 100', 'Un mundo distinto'),
      {'cielo': 'amanecer', 'suelo': 'hierba', 'plano': 'aerea', 'camara': 'alejar', 'objetos': [{'tipo': 'casa', 'cantidad': 4}, {'tipo': 'arboles', 'cantidad': 10}]}),
    E('…pero comeríamos mucho peor. ¿Qué fruta echarías más de menos?', D('AÑO 100', 'Un mundo distinto'),
      {'cielo': 'atardecer', 'suelo': 'hierba', 'plano': 'detalle', 'foco': 0, 'camara': 'orbita', 'objetos': [N(PANAL, 7, 'bloque'), N(ABEJA, 3, 'emoji', 'flotar', emoji='🐝')]}),
]})

# 2 · INTERNET
V.append({'titulo': '¿Y si se apagara internet en todo el mundo? 📵', 'meta': {
    'tema': '¿Qué pasaría si internet se apagara en todo el mundo a la vez?', 'titulo': '¿Y si se apagara internet en todo el mundo? 📵',
    'gancho': 'No es solo quedarte sin redes: es quedarte sin pagar, sin volar y sin mapas.', 'pregunta': '¿Aguantarías una semana sin internet?',
    'hashtags': ['internet', 'tecnologia', 'apagon', 'quepasariasi', 'curiosidades']}, 'escenas': [
    E('Pongamos que ahora mismo se apaga internet en todo el mundo.', D('SEGUNDO 0', 'Apagón digital'),
      {'cielo': 'noche', 'suelo': 'ciudad', 'plano': 'detalle', 'foco': 0, 'camara': 'acercar', 'objetos': [N(MOVIL_SIN, 6, 'movil')]}),
    E('En millones de casas, la misma pantalla: sin conexión.', D('MINUTO 1', 'Sin conexión'),
      {'cielo': 'noche', 'suelo': 'hierba', 'plano': 'interior', 'camara': 'acercar', 'objetos': [{'tipo': 'personas', 'cantidad': 2}, N(MOVIL_SIN, 1.2, 'movil'), {'tipo': 'ordenador', 'texto': 'SIN RED'}]}),
    E('Los pagos con tarjeta dejan de funcionar.', D('HORA 1', 'Tarjetas inútiles'),
      {'cielo': 'atardecer', 'suelo': 'ciudad', 'plano': 'detalle', 'foco': 0, 'camara': 'orbita', 'objetos': [N(CAJERO, 6, 'cartel', texto='SIN CONEXIÓN')]}),
    E('Y en los cajeros, colas que no avanzan.', D('HORA 1', 'Tarjetas inútiles'),
      {'cielo': 'atardecer', 'suelo': 'ciudad', 'plano': 'fachada', 'camara': 'travelin', 'objetos': [N(CAJERO, 5, 'cartel', texto='FUERA DE SERVICIO'), {'tipo': 'personas', 'cantidad': 7, 'x': 0, 'z': 1}, {'tipo': 'edificios', 'cantidad': 3, 'z': -6}]}),
    E('Los aviones se quedan en tierra: sin datos no se puede gestionar un vuelo.', D('DÍA 1', 'Aviones parados'),
      {'cielo': 'dia', 'suelo': 'ciudad', 'plano': 'aerea', 'foco': 0, 'camara': 'orbita', 'objetos': [N(AEROPUERTO, 34, 'avion', texto='CANCELADO')]}),
    E('Las tiendas solo aceptan efectivo, y el dinero en mano se acaba.', D('SEMANA 1', 'Solo efectivo'),
      {'cielo': 'atardecer', 'suelo': 'ciudad', 'plano': 'detalle', 'foco': 0, 'camara': 'subir', 'objetos': [{'tipo': 'billetes', 'cantidad': 4}]}),
    E('Los centros de datos siguen en pie, esperando a que vuelva la red.', D('MES 1', 'Servidores en espera'),
      {'cielo': 'noche', 'suelo': 'ciudad', 'plano': 'detalle', 'foco': 0, 'camara': 'travelin', 'objetos': [{'tipo': 'servidores'}]}),
    E('Volveríamos a las cartas, al teléfono fijo y a los mapas de papel.', D('AÑO 1', 'Vuelta al papel'),
      {'cielo': 'dia', 'suelo': 'hierba', 'plano': 'mapa', 'objetos': [{'tipo': 'marcador', 'nombre': 'Madrid'}, {'tipo': 'marcador', 'nombre': 'Barcelona'}, {'tipo': 'marcador', 'nombre': 'Sevilla'}, {'tipo': 'ruta', 'desde': 'Madrid', 'hasta': 'Barcelona'}, {'tipo': 'ruta', 'desde': 'Madrid', 'hasta': 'Sevilla'}]}),
    E('Y tú, ¿aguantarías una semana sin internet?', D('AÑO 100', 'Desconectados'),
      {'cielo': 'noche', 'suelo': 'ciudad', 'plano': 'detalle', 'foco': 0, 'camara': 'alejar', 'objetos': [N(MOVIL_SIN, 6, 'movil', texto='¿Y ahora qué?')]}),
]})

# 3 · SIN LLUVIA
V.append({'titulo': '¿Y si no lloviera en España en un año? ☀️', 'meta': {
    'tema': '¿Qué pasaría si en España no lloviera ni una gota durante un año entero?', 'titulo': '¿Y si no lloviera en España en un año? ☀️',
    'gancho': 'Los pueblos que se tragaron los embalses volverían a salir a la luz.', 'pregunta': '¿Cómo ahorras tú agua en casa?',
    'hashtags': ['sequia', 'agua', 'españa', 'quepasariasi', 'embalses']}, 'escenas': [
    E('Pongamos que en España no cae ni una gota de lluvia durante un año.', D('SEGUNDO 0', 'Cielo sin nubes'),
      {'cielo': 'atardecer', 'suelo': 'arena', 'plano': 'detalle', 'foco': 0, 'camara': 'orbita', 'objetos': [N(CAMPO_SECO, 14, 'cactus')]}),
    E('Al principio nadie lo nota: los grifos siguen echando agua.', D('MINUTO 1', 'Todo normal'),
      {'cielo': 'dia', 'suelo': 'hierba', 'plano': 'interior', 'camara': 'acercar', 'objetos': [{'tipo': 'personas', 'cantidad': 2}]}),
    E('Pero los campos de secano empiezan a cuartearse.', D('HORA 1', 'Tierra cuarteada'),
      {'cielo': 'atardecer', 'suelo': 'arena', 'plano': 'aerea', 'camara': 'travelin', 'objetos': [N(CAMPO_SECO, 18, 'cactus')]}),
    E('Los embalses bajan cada semana un poco más.', D('DÍA 1', 'Embalses bajo mínimos'),
      {'cielo': 'dia', 'suelo': 'arena', 'plano': 'aerea', 'foco': 0, 'camara': 'orbita', 'objetos': [N(EMBALSE, 30, 'crater')]}),
    E('Hasta que asoman los pueblos que quedaron bajo el agua.', D('SEMANA 1', 'Pueblos fantasma'),
      {'cielo': 'atardecer', 'suelo': 'arena', 'plano': 'aerea', 'foco': 0, 'camara': 'acercar', 'objetos': [N(EMBALSE, 30, 'crater', vacio=True)]}),
    E('En muchos pueblos, el agua llega en camiones cisterna.', D('MES 1', 'Agua en camiones'),
      {'cielo': 'dia', 'suelo': 'ciudad', 'plano': 'fachada', 'camara': 'travelin', 'objetos': [N(CISTERNA, 8, 'autobus'), {'tipo': 'personas', 'cantidad': 6, 'z': 3}, {'tipo': 'casa', 'cantidad': 3, 'z': -6}]}),
    E('Los incendios se multiplican en los montes secos.', D('AÑO 1', 'Montes en llamas'),
      {'cielo': 'rojo', 'suelo': 'roca', 'plano': 'aerea', 'efecto': 'ceniza', 'camara': 'orbita', 'objetos': [{'tipo': 'fuego'}, {'tipo': 'arboles', 'cantidad': 14}, {'tipo': 'helicoptero'}]}),
    E('Y el aceite y la fruta se disparan de precio.', D('AÑO 1', 'Montes en llamas'),
      {'cielo': 'dia', 'suelo': 'ciudad', 'plano': 'detalle', 'foco': 0, 'camara': 'travelin', 'objetos': [N(ESTANTERIA, 9, 'monedas', vacia=True)]}),
    E('España ya ha vivido sequías largas, y siempre volvió a llover.', D('AÑO 100', 'Vuelve la lluvia'),
      {'cielo': 'tormenta', 'suelo': 'hierba', 'plano': 'aerea', 'foco': 0, 'efecto': 'lluvia', 'camara': 'alejar', 'objetos': [N(EMBALSE, 30, 'crater', lleno=True)]}),
    E('¿Y tú, cómo ahorras agua en casa?', D('AÑO 100', 'Vuelve la lluvia'),
      {'cielo': 'tormenta', 'suelo': 'hierba', 'plano': 'interior', 'efecto': 'lluvia', 'camara': 'acercar', 'objetos': [{'tipo': 'personas', 'cantidad': 2}]}),
]})

# 4 · ASTEROIDE
V.append({'titulo': '¿Y si un asteroide cayera en el Mediterráneo? ☄️', 'meta': {
    'tema': '¿Qué pasaría si un asteroide de un kilómetro cayera en el mar Mediterráneo?', 'titulo': '¿Y si un asteroide cayera en el Mediterráneo? ☄️',
    'gancho': 'Un kilómetro de roca a 60.000 km/h contra nuestro mar.', 'pregunta': '¿Crees que sabríamos desviarlo a tiempo?',
    'hashtags': ['asteroide', 'mediterraneo', 'espacio', 'quepasariasi', 'ciencia']}, 'escenas': [
    E('Pongamos que un asteroide de un kilómetro se dirige al Mediterráneo.', D('SEGUNDO 0', 'Rumbo a la Tierra'),
      {'cielo': 'espacio', 'suelo': 'ninguno', 'plano': 'detalle', 'camara': 'acercar', 'objetos': [N(ASTEROIDE, 9, 'meteorito'), {'tipo': 'tierra', 'x': 9}]}),
    E('Entra en la atmósfera a más de sesenta mil kilómetros por hora.', C('60.000 km/h', 'velocidad de entrada'),
      {'cielo': 'espacio', 'suelo': 'ninguno', 'plano': 'detalle', 'foco': 0, 'camara': 'orbita', 'objetos': [N(ASTEROIDE, 9, 'meteorito')]}),
    E('El impacto levanta una columna de agua y vapor de varios kilómetros.', D('MINUTO 1', 'El impacto'),
      {'cielo': 'tormenta', 'suelo': 'agua', 'plano': 'fachada', 'efecto': 'ceniza', 'camara': 'subir', 'objetos': [{'tipo': 'ola', 'escala': 1.6}, {'tipo': 'humo'}]}),
    E('En menos de una hora, olas gigantes alcanzan Baleares y la costa de Valencia.', D('HORA 1', 'Olas gigantes'),
      {'cielo': 'tormenta', 'suelo': 'hierba', 'plano': 'mapa', 'objetos': [{'tipo': 'marcador', 'nombre': 'Palma'}, {'tipo': 'marcador', 'nombre': 'Valencia'}, {'tipo': 'marcador', 'nombre': 'Barcelona'}, {'tipo': 'ruta', 'desde': 'Palma', 'hasta': 'Valencia'}]}),
    E('El agua entra en las ciudades de la costa.', D('HORA 1', 'Olas gigantes'),
      {'cielo': 'tormenta', 'suelo': 'agua', 'plano': 'fachada', 'camara': 'travelin', 'objetos': [{'tipo': 'ola'}, {'tipo': 'edificios', 'cantidad': 5}]}),
    E('Puertos y paseos marítimos quedan destrozados.', D('DÍA 1', 'Costa destrozada'),
      {'cielo': 'atardecer', 'suelo': 'agua', 'plano': 'detalle', 'foco': 0, 'camara': 'orbita', 'objetos': [{'tipo': 'barco', 'cantidad': 2, 'anim': 'hundirse'}, {'tipo': 'muelle'}]}),
    E('El vapor lanzado al cielo enfría el clima durante meses.', D('SEMANA 1', 'Cielo gris'),
      {'cielo': 'tormenta', 'suelo': 'nieve', 'plano': 'aerea', 'efecto': 'nieve', 'camara': 'orbita', 'objetos': [{'tipo': 'casa', 'cantidad': 5}, {'tipo': 'pino_nieve', 'cantidad': 8}]}),
    E('Y las cosechas se resienten en media Europa.', D('MES 1', 'Cosechas perdidas'),
      {'cielo': 'tormenta', 'suelo': 'arena', 'plano': 'detalle', 'foco': 0, 'camara': 'travelin', 'objetos': [N(CAMPO_SECO, 14, 'cactus')]}),
    E('La buena noticia: la NASA vigila los asteroides grandes y ya ha probado a desviar uno.', D('AÑO 1', 'Defensa planetaria'),
      {'cielo': 'espacio', 'suelo': 'ninguno', 'plano': 'detalle', 'camara': 'orbita', 'objetos': [{'tipo': 'satelite', 'x': -5}, N(ASTEROIDE, 7, 'meteorito')]}),
    E('¿Crees que sabríamos desviarlo a tiempo?', D('AÑO 100', '¿A salvo?'),
      {'cielo': 'espacio', 'suelo': 'ninguno', 'plano': 'detalle', 'foco': 0, 'camara': 'alejar', 'objetos': [{'tipo': 'tierra', 'anim': 'girar'}]}),
]})

# 5 · LUNA
V.append({'titulo': '¿Y si la Luna desapareciera esta noche? 🌙', 'meta': {
    'tema': '¿Qué pasaría si la Luna desapareciera de repente esta noche?', 'titulo': '¿Y si la Luna desapareciera esta noche? 🌙',
    'gancho': 'Las noches serían más oscuras… pero lo más grave pasaría en el mar.', 'pregunta': '¿Echarías de menos la Luna?',
    'hashtags': ['luna', 'espacio', 'mareas', 'quepasariasi', 'ciencia']}, 'escenas': [
    E('Pongamos que esta noche la Luna desaparece del cielo.', D('SEGUNDO 0', 'Sin Luna'),
      {'cielo': 'noche', 'suelo': 'ciudad', 'plano': 'fachada', 'camara': 'subir', 'objetos': [{'tipo': 'luna'}, {'tipo': 'edificios', 'cantidad': 4}]}),
    E('Las noches se vuelven mucho más oscuras.', D('MINUTO 1', 'Noches negras'),
      {'cielo': 'noche', 'suelo': 'hierba', 'plano': 'aerea', 'camara': 'travelin', 'objetos': [{'tipo': 'casa', 'cantidad': 4}, {'tipo': 'arboles', 'cantidad': 10}]}),
    E('Pero lo que más cambia está en el mar: las mareas se quedan en un tercio.', C('1/3', 'de la marea de hoy'),
      {'cielo': 'atardecer', 'suelo': 'agua', 'plano': 'fachada', 'camara': 'acercar', 'objetos': [{'tipo': 'barco'}, {'tipo': 'muelle'}, {'tipo': 'boyas'}]}),
    E('Playas y charcas que vivían con la marea cambian para siempre.', D('DÍA 1', 'Mareas mínimas'),
      {'cielo': 'dia', 'suelo': 'arena', 'plano': 'fachada', 'foco': 0, 'camara': 'travelin', 'objetos': [N(LUNA_MAREA, 22, 'barco')]}),
    E('Corales y peces que se reproducen siguiendo a la Luna se desorientan.', D('SEMANA 1', 'Mar desorientado'),
      {'cielo': 'noche', 'suelo': 'ninguno', 'plano': 'detalle', 'foco': 0, 'camara': 'orbita', 'objetos': [N(ARRECIFE, 16, 'peces')]}),
    E('Muchos animales nocturnos que cazan con su luz lo tienen más difícil.', D('MES 1', 'Cazar a oscuras'),
      {'cielo': 'noche', 'suelo': 'hierba', 'plano': 'detalle', 'foco': 0, 'camara': 'acercar', 'objetos': [N(BUHO, 7, 'pajaros')]}),
    E('Los días siguen durando 24 horas: la Tierra no frena de golpe.', D('AÑO 1', 'Días normales'),
      {'cielo': 'espacio', 'suelo': 'ninguno', 'plano': 'detalle', 'foco': 0, 'camara': 'orbita', 'objetos': [{'tipo': 'tierra', 'anim': 'girar'}]}),
    E('Pero, con los siglos, el eje de la Tierra se tambalearía y el clima sería más extremo.', D('AÑO 100', 'Clima extremo'),
      {'cielo': 'espacio', 'suelo': 'ninguno', 'plano': 'detalle', 'camara': 'alejar', 'objetos': [{'tipo': 'tierra', 'anim': 'temblar'}, {'tipo': 'sol', 'x': -10}]}),
    E('¿Echarías de menos la Luna?', D('AÑO 100', 'Clima extremo'),
      {'cielo': 'noche', 'suelo': 'hierba', 'plano': 'aerea', 'camara': 'alejar', 'objetos': [{'tipo': 'luna'}, {'tipo': 'casa', 'cantidad': 3}]}),
]})

os.makedirs(sys.argv[1], exist_ok=True)
for k, h in enumerate(V, 1):
    json.dump(h, open(os.path.join(sys.argv[1], f'v{k}.json'), 'w'), ensure_ascii=False, indent=1)
print('ok', [len(h['escenas']) for h in V], [sum(len(e['hablado'].split()) for e in h['escenas']) for h in V])
