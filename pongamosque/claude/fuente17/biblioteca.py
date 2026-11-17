import json, sys, re, collections
sys.path.insert(0, 'fuente17'); import piezas as P
M = {
 'ascensor': dict(cod='ASCENSOR', v=1, reserva='cilindro', nombre='Hueco de ascensor de un edificio con su cabina',
   descripcion='Corte de un edificio: hueco de hormigón, guías, cables de acero, motor arriba y la cabina con su freno de seguridad (paracaídas).',
   opciones={'vista': {'todo': 'el hueco entero de arriba abajo', 'cabina': 'la cabina por dentro/de cerca', 'cables': 'los cables y el motor', 'freno': 'las mordazas del freno sobre las guías', 'caida': 'la cabina cayendo'},
             'sinCables': 'true = cables rotos', 'frena': 'true = el freno está mordiendo las guías (chispas)', 'altura': 'número 0-12: planta a la que está la cabina'},
   ideas=['Pongamos que te quedas encerrado en un ascensor todo un fin de semana', 'Pongamos que el ascensor no para y sube hasta el tejado', 'Pongamos que se va la luz con el ascensor lleno', 'Pongamos que un edificio de 100 plantas no tuviera ascensor']),
 'nevera': dict(cod='FRIGO', v=2, reserva='bloque', nombre='Frigorífico abierto con comida',
   descripcion='Nevera de cocina con las dos puertas abiertas: estantes con leche, huevos, fruta, carne, queso; congelador arriba; compresor detrás; termómetro.',
   opciones={'vista': {'todo': 'la nevera entera abierta', 'compresor': 'el compresor de detrás', 'termometro': 'el termómetro de cerca', 'comida': 'los estantes con la comida', 'congelador': 'el congelador'},
             'roto': 'true = no enfría (luz apagada, comida estropeándose)', 'dias': 'número de días estropeada (0-7): la comida se pone mohosa'},
   ideas=['Pongamos que no abrieras la nevera en un mes', 'Pongamos que se acabara la electricidad en tu barrio una semana', 'Pongamos que solo pudieras comer lo que hay en tu nevera', 'Pongamos que dejaras la puerta de la nevera abierta toda la noche']),
 'avion': dict(cod='AVION_CORTE', v=3, reserva='avion', nombre='Avión de pasajeros en corte',
   descripcion='Avión de pasajeros volando con un corte que deja ver la cabina con asientos, ventanillas, la puerta con su palanca, máscaras de oxígeno, el ala y un motor.',
   opciones={'vista': {'todo': 'el avión entero volando', 'cabina': 'el pasillo con los asientos', 'puerta': 'la puerta y su palanca de cerca', 'ala': 'el ala y el motor'},
             'abierta': 'true = puerta abierta (solo en tierra)', 'mascaras': 'true = máscaras de oxígeno caídas', 'texto': 'texto corto en la puerta'},
   ideas=['Pongamos que un avión volara sin parar durante un mes', 'Pongamos que el piloto se quedara dormido', 'Pongamos que un pájaro entra en el motor', 'Pongamos que el avión pierde un motor sobre el océano']),
 'coche': dict(cod='COCHE_RAYO', v=4, reserva='coche', nombre='Coche bajo la tormenta',
   descripcion='Coche en una carretera con tormenta: carrocería, ruedas, bajos, pasajeros dentro; puede caer un rayo y verse la corriente recorriendo la carrocería (jaula de Faraday).',
   opciones={'vista': {'todo': 'el coche entero en la carretera', 'rueda': 'una rueda de cerca', 'jaula': 'la carrocería con la corriente por fuera', 'dentro': 'el interior con los pasajeros'},
             'rayo': 'false = sin el rayo cayendo', 'color': 'color de la carrocería en hex (#c0392b…)'},
   ideas=['Pongamos que te quedas atrapado con el coche en una inundación', 'Pongamos que conduces un coche sin frenos cuesta abajo', 'Pongamos que dejas a tu perro en el coche al sol', 'Pongamos que tu coche se quedara sin gasolina en el desierto']),
 'digestivo': dict(cod='DIGESTIVO', v=5, reserva='cuerpo', nombre='Cuerpo humano con el aparato digestivo',
   descripcion='Silueta de cuerpo humano transparente con esófago, estómago con ácido, intestino delgado y grueso; un objeto pequeño (el chicle) que viaja por dentro.',
   opciones={'vista': {'todo': 'el cuerpo entero', 'chicle': 'el objeto tragado de cerca', 'estomago': 'el estómago con el ácido', 'intestino': 'los intestinos'},
             'dia': 'número 0-3: cuánto ha avanzado el objeto por el intestino'},
   ideas=['Pongamos que te tragas una pepita de sandía', 'Pongamos que no comieras nada durante una semana', 'Pongamos que solo bebieras refrescos un mes', 'Pongamos que te tragas una moneda']),
}
def tomas(H):
    out = []
    for i, e in enumerate(H['escenas']):
        d = json.loads(json.dumps(e['escena3d'])); o = d['objetos'][0]; o.pop('codigo', None); o.pop('reserva', None)
        r = d.get('ruta') or {}; a = r.get('mira2') or r.get('mira'); a = a if isinstance(a, str) else (a[0] if isinstance(a, list) and a and isinstance(a[0], str) else None)
        dist = lambda p: sum(x * x for x in p[1]) if isinstance(p, list) and len(p) > 1 and isinstance(p[1], list) else 0
        aleja = bool(r) and dist(r.get('a')) > dist(r.get('de')) * 1.05
        out.append({'id': f't{i+1}', 'aleja': aleja, 'vista': o.get('vista', 'todo'), 'ancla': a, 'se_ve': e['hablado'], 'escena3d': d})
    return out
for k, m in M.items():
    H = json.load(open(f'2026-11-17/v{m["v"]}.json')); tam = collections.defaultdict(list); anc = collections.defaultdict(set); cielos = set()
    for e in H['escenas']:
        d = e['escena3d']; o = d['objetos'][0]; v = o.get('vista', 'todo'); tam[v].append(o['tam']); cielos.add(d.get('cielo'))
        r = d.get('ruta') or {}
        for x in (r.get('de'), r.get('a'), r.get('mira'), r.get('mira2')):
            if isinstance(x, str): anc[v].add(x)
            elif isinstance(x, list) and x and isinstance(x[0], str): anc[v].add(x[0])
    cod = getattr(P, m['cod']); todas = sorted(set(re.findall(r"marca\(\s*'(\w+)'", cod)) | set(re.findall(r"\['(\w+)', -?[\d.]+, -?[\d.]+, -?[\d.]+\]", cod)))
    W = {'id': k, 'nombre': m['nombre'], 'descripcion': m['descripcion'], 'reserva': m['reserva'], 'opciones': m['opciones'],
         'tam': {v: max(set(t), key=t.count) for v, t in tam.items()}, 'anclas': todas, 'anclas_por_vista': {v: sorted(a) for v, a in anc.items()},
         'ideas': m['ideas'], 'creado': '2026-11-17', 'autor': 'claude',
         'usos': [{'fecha': '2026-11-17', 'tema': H['meta']['tema'], 'por': 'claude'}],
         'ejemplo': [{'hablado': e['hablado'], 'visual': e['visual'], 'cielo': e['escena3d'].get('cielo'), 'opciones': {a: b for a, b in e['escena3d']['objetos'][0].items() if a not in ('tipo', 'codigo', 'tam', 'reserva')}} for e in H['escenas']],
         'tomas': tomas(H), 'codigo': cod}
    for v in W['opciones']['vista']: W['tam'].setdefault(v, W['tam'].get('todo'))
    json.dump(W, open(f'mundos/{k}.json', 'w'), ensure_ascii=False, indent=1); print(k, W['tam'], W['anclas'], W['anclas_por_vista'])
