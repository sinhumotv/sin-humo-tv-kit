# Plantilla del estilo de Pongamos Que (aprobada por el usuario el 17-nov-2026)

Modelo a seguir para TODOS los vídeos nuevos: `piezas.py` (el mundo) + `hacer.py` (guion y cámara).

- **Estilo de las referencias**: ilustración 3D de cine, noche azul (`cielo: 'noche'`, `luz: 'nocturna'`) o atardecer, luces cálidas de interior/ventanas,
  vista en corte, escenario completo (nunca el objeto flotando), personas pequeñas, objetos estilizados y limpios (nada fotorrealista).
- **Cámara**: UNA sola curva suave para todo el vídeo. Lista global de puntos `CAM` y de miradas `MIR`; cada frase lleva
  `ruta = {de, a, mira, mira2, continua: True, camino: CAM, miras: MIR, t0, t1}` (t0/t1 = índices de sus puntos) y `escena3d.continua = True`
  (sin whoosh entre frases). Puntos intermedios para rodear objetos (VIA). Nada de cortes ni de acercamientos que se paran.
- **Estado continuo**: lo que acaba una frase es lo que empieza la siguiente (puerta [1, 0] → 0 → [0, 1]…, días que avanzan).
- **Vida constante**: animaciones con el tiempo global `tick(x, u, L, t)` (respirar, balanceos, polvo, moscas, goteo…) y sucesos dentro del plano con `x`.
- **Sonido**: `escena3d.sonidos = [[x, nombre]]` (efectos de sfx.py) y `sacudidas` en impactos.
- **Rótulos en español**; números de pantallas con segmentos (no texto en canvas: en GitHub a veces sale en negro).
- Revisar con el workflow «Pongamos Que · fotogramas de prueba» antes de dejarlo.
