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
- **Zona segura de TikTok/Instagram** (17-nov): lo importante (objetos protagonistas y textos) en el centro; nada importante en el 11 % de arriba, el 22 % de abajo ni en el borde derecho (botones). El motor ya coloca así subtítulos, etapa y cifras; el encuadre de la cámara también debe dejar el protagonista centrado.
- **(18-nov) QUE SE VEA DE VERDAD LO QUE SE DICE** (el usuario: «he visto el vídeo y no he visto nada en concreto»): la cámara se QUEDA en lo que nombra cada frase (`ruta.mantener: 2.4`, y cada frase centrada en su punto: `t0 = i - 0.5`, `t1 = i + 0.5`), bien iluminado y a distancia de primer/medio plano; y en cada frase PASA algo visible delante de la cámara (se apaga, cae, se enciende, se corta, crece…). Pocos sitios distintos (6-8), no un tour por todo.
