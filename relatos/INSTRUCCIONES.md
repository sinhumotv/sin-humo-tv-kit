# Relatos en Español: 5 relatos diarios de mitología griega

Tarea diaria: crear 5 vídeos verticales (≈30-40 s) que cuentan cada uno un mito griego distinto con imágenes
realistas (Cloudflare FLUX.2, gratis), zoom lento, partículas, subtítulos serif con la clave en amarillo, música y voz
Gemini "Algenib" (gratis), y programarlos en Buffer (cuenta de Relatos, NO la de sin humo TV) a las
08:00, 12:00, 15:00, 18:00 y 21:00 (hora de Madrid). Hazlo todo sin preguntar: decide tú y sigue.
GASTO MÍNIMO de uso de Claude: no narres, no leas archivos grandes, una sola revisión visual por vídeo.

## 0) Preparación (una vez por ejecución)
- add_repo owner "sinhumotv" repo "sin-humo-tv-kit" access "push" y repo "sin-humo-tv-datos" access "push".
- Kit: `[ -d /home/claude/kit/.git ] && git -C /home/claude/kit pull -q || git clone -q --depth 1 https://github.com/sinhumotv/sin-humo-tv-kit /home/claude/kit`
- Datos: `git clone -q --depth 1 https://github.com/sinhumotv/sin-humo-tv-datos /home/claude/datos` (contiene relatos.txt).
- Claves (privadas: nunca en el repositorio, en mensajes ni en textos publicados): en Google Drive, carpeta
  "sin humo TV" (id 1P341VoGcSUI_frt7xhU7DFrkVUnqLZu7), lee con read_file_content el Doc "clave-gemini" (la clave
  tal cual, quitando las barras invertidas de escape) y el Doc "claves-relatos" (líneas CF_ACCOUNT=, CF_TOKEN=,
  BUFFER_RELATOS=). Guárdalas con permisos 600 en ~/.gemini_key, ~/.cf_account, ~/.cf_token y ~/.buffer_relatos
  (sin espacios ni saltos de línea). Si falta alguna, avisa con SendUserMessage y termina.
- Comprueba: ffmpeg, python3 con numpy y PIL.

## 1) Elegir 5 mitos
- Lee las últimas 80 líneas de /home/claude/datos/relatos.txt (fecha|hora|título|ids). No repitas ningún mito de ahí.
- Elige 5 mitos griegos CONCRETOS y variados entre sí (no 5 de dioses, ni 5 tragedias): mezcla héroes (Perseo,
  Teseo, Heracles, Jasón, Odiseo, Aquiles…), dioses y castigos (Prometeo, Sísifo, Tántalo, Aracne, Midas, Narciso…),
  monstruos (Medusa, Minotauro, Escila, Cerbero, Tifón…), amores y tragedias (Eco, Pigmalión, Faetón, Ícaro,
  Psique, Hero y Leandro…), episodios poco conocidos y curiosos. Cuando se agoten los grandes, usa episodios
  concretos (un trabajo de Heracles, una aventura de Odiseo…).
- Cuenta la versión clásica más conocida (Ovidio, Homero, Apolodoro…). No inventes hechos; si hay varias versiones,
  usa la más conocida sin decir que es la única.

## 2) Guion (español de España) → /home/claude/relatos/AAAA-MM-DD-HHMM/historia.json
- 7 u 8 escenas, 85-100 palabras en total (≈ 30-38 s). Frases cortas. Una idea y una imagen por escena.
- Escena 1 (0-2 s): gancho que obligue a seguir: la consecuencia más impactante o una pregunta ("Un solo vistazo le
  costó el amor de su vida."). Prohibido empezar por "Hoy", "Hola", "En la mitología griega" o el nombre del canal.
- Mantén la intriga y deja el giro para el final. Última escena: desenlace + pregunta corta al espectador
  ("¿Tú habrías mirado?").
- "hablado": lo que lee la voz (nombres como se pronuncian en español; sin cifras, en letra). "subtitulo": mismas
  palabras y en el mismo orden, con 1-2 *palabras clave* por escena entre asteriscos.
- "prompt" (EN INGLÉS): imagen vertical realista de esa escena. Describe a cada personaje SIEMPRE con la misma frase
  (pelo, barba, ropa) para que se parezca en todas las escenas. Nada de desnudos, sangre, gore ni violencia explícita:
  lo duro se sugiere (sombras, la espada levantada, la reacción). Llama a los dioses por su aspecto si un nombre da
  problemas ("a majestic bearded king with an iron crown" en vez de "Hades").
- "efecto": brasas (fuego, batallas, Inframundo), polvo (escenas de día o interiores), niebla (mar, cuevas,
  fantasmas), nada. "fuego": true si hay antorchas o fuego visibles.
- Campos de publicación: "titulo" (nombre del mito), "titulo_youtube" (≤60 caracteres, gancho con intriga, sin
  prometer lo que no hay, p. ej. "Bajó al Inframundo por amor… y lo perdió todo"), "descripcion" (2 líneas: la
  primera repite el gancho con otras palabras; la segunda termina en "Relatos en Español"), "pregunta" (pregunta
  para comentar, se contesta con una palabra o eligiendo entre dos opciones), "hashtags" (4-5: #mitologiagriega
  #mitologia #historias y 1-2 del mito), "titulo_tiktok" (gancho en forma de pregunta), "portada_s": 0.8.
- Varía entre vídeos: tipo de gancho (pregunta, consecuencia, frase increíble), número de escenas y tono.

## 3) Fabricar y publicar (uno detrás de otro, en orden de hora)
Para cada vídeo:
1. `python3 /home/claude/kit/relatos/fabricar.py <carpeta> voz` y luego `... imagenes`.
   - Si una imagen falla (filtro de Cloudflare), el script ya reintenta solo; si aun así sale "SIN IMAGEN",
     suaviza ese "prompt" en historia.json y repite `... imagenes` (solo genera las que faltan).
   - Mira UNA vez la hoja (hoja.jpg) con Read. Si una imagen está claramente mal (personaje deforme, texto raro,
     no encaja con la escena), bórrala de imgs/, ajusta su prompt y repite `... imagenes`. Máximo una ronda.
2. `python3 /home/claude/kit/relatos/fabricar.py <carpeta> montaje` (≈3-4 min).
3. `python3 /home/claude/kit/relatos/publicar.py <carpeta> <HH:MM>` → aloja el vídeo en GitHub (rama rel-HHMM) y lo
   programa en YouTube, Instagram y TikTok de Relatos (etiqueta "hecho con IA" siempre activada). Si un canal da
   error, no repitas en bucle: apúntalo.
4. Añade la línea a /home/claude/datos/relatos.txt: `AAAA-MM-DD|HH:MM|<titulo>|YT <id> IG <id> TT <id>`.
Si un vídeo falla del todo, sigue con el siguiente y avísalo al final.

## 4) Cierre
- `cd /home/claude/datos && git add relatos.txt && git -c user.name="Relatos en Español" -c user.email="sinhumotv@users.noreply.github.com" commit -qm "relatos AAAA-MM-DD" && git push -q`
- Mensaje final con SendUserMessage (breve): los 5 mitos con su hora y título de YouTube, y qué canal falló si alguno.
  No envíes los vídeos salvo que algo haya fallado (para publicar a mano).
