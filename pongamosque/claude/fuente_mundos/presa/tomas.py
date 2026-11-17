R = lambda a, d, m2=None, de=None: {'de': [de or a, d[0]], 'a': [a, d[1]], 'mira': de or a, 'mira2': m2 or a}
TOMAS = [
 ('el valle entero: el pueblo río abajo y la presa al fondo', 'atardecer', {}, R('pueblo', ([0.0, 0.22, 0.2], [0.0, 0.15, 0.12]), m2='muro')),
 ('las compuertas de arriba de la presa soltando agua', 'dia', {'abiertas': True}, R('compuertas', ([0.2, 0.05, 0.45], [0.08, 0.02, 0.3]), m2='muro')),
 ('la central eléctrica al pie de la presa con sus turbinas', 'noche', {}, R('turbina', ([0.0, 0.05, 0.24], [0.0, 0.035, 0.17]))),
 ('el embalse lleno visto desde lo alto de la presa', 'dia', {}, {'de': ['corona', [0.05, 0.06, 0.12]], 'a': ['corona', [0.0, 0.05, 0.04]], 'mira': 'embalse', 'mira2': 'embalse'}),
 ('el paseo de la coronación de la presa con farolas', 'noche', {}, R('corona', ([0.12, 0.03, 0.12], [0.05, 0.02, 0.06]), m2='compuertas')),
 ('el embalse vacío: asoman las ruinas y el campanario del pueblo sumergido', 'dia', {'nivel': 0.0}, R('pueblo_sumergido', ([-0.3, 0.1, -0.15], [-0.2, 0.06, -0.08]), m2='campanario')),
 ('una grieta en el muro de la presa con agua filtrándose', 'atardecer', {'grieta': True}, R('grieta', ([0.06, 0.0, 0.18], [0.02, 0.0, 0.12]))),
 ('la presa rota: el agua sale en tromba hacia el pueblo', 'tormenta', {'roto': True}, R('pueblo', ([0.05, 0.2, 0.2], [0.02, 0.13, 0.12]), m2='muro')),
 ('el río y el puente del pueblo, con la central detrás', 'dia', {}, R('puente', ([0.0, 0.05, 0.16], [0.0, 0.035, 0.11]), m2='pueblo')),
 ('la orilla del embalse medio vacío, con la tierra seca al descubierto', 'atardecer', {'nivel': 0.35}, {'de': ['corona', [-0.1, 0.1, 0.1]], 'a': ['corona', [-0.08, 0.08, 0.03]], 'mira': 'orilla', 'mira2': 'orilla'}),
]
