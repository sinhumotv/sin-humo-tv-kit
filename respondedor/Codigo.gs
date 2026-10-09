/**
 * RESPONDEDOR DE COMENTARIOS DE SIN HUMO TV
 * Cada 5 minutos mira los comentarios nuevos de YouTube e Instagram y los responde.
 *
 * Tus claves NO están en este código: se guardan en
 * "Configuración del proyecto" → "Propiedades del script" (solo las ves tú):
 *   INSTAGRAM_TOKEN  → token de Instagram (opcional: sin él, solo YouTube)
 *   GEMINI_KEY       → clave gratuita de Google AI Studio (opcional: sin ella, respuestas tipo)
 *   PAUSADO          → pon 1 para parar las respuestas sin borrar nada
 *
 * Primer uso: ejecuta la función "configurar" una vez y acepta los permisos.
 */

const AJUSTES = {
  esperaMinutos: 2,          // solo responde comentarios con al menos 2 min de antigüedad
  diasAtras: 3,              // ignora comentarios de hace más de 3 días
  maxPorRonda: 12,           // respuestas máximas cada 5 minutos
  maxPorDia: 150,            // tope diario (evita que las redes lo vean como spam)
  igPublicaciones: 12,       // últimas publicaciones de Instagram que revisa
  ytHilos: 40,               // últimos comentarios de YouTube que revisa
  modeloGemini: 'gemini-2.5-flash',
  canal: 'sin humo TV',
};

// Comentarios que NO se responden (insultos, odio, spam). Se ignoran en silencio.
const PALABRAS_IGNORAR = [
  'gilipollas', 'subnormal', 'imbecil', 'imbécil', 'idiota', 'puta', 'puto', 'mierda', 'cabron', 'cabrón',
  'hijo de', 'retrasado', 'maricon', 'maricón', 'zorra', 'basura', 'asco de', 'muerete', 'muérete',
  'follow back', 'sígueme', 'sigueme', 'check my', 'mi perfil', 'gana dinero', 'crypto', 'bitcoin', 'onlyfans', 'promo',
];

const RESPUESTAS_TIPO = {
  gracias: [
    '¡Gracias por comentar! 🙌 Aquí seguimos contando los hechos, sin humo.',
    '¡Gracias! Nos alegra que te sirva. Mañana, más noticias sin humo 💨',
    '¡Gracias por estar ahí! ¿Qué noticia quieres que expliquemos la próxima vez?',
  ],
  pregunta: [
    'Buena pregunta 👀 En la descripción tienes las fuentes para ampliarlo. ¿Tú qué opinas?',
    'Gracias por preguntar. Nos ceñimos a lo que dicen las fuentes oficiales; si hay novedades, las contaremos.',
  ],
  opinion: [
    'Gracias por compartir tu opinión 🙌 Aquí contamos los hechos y cada uno saca sus conclusiones.',
    'Interesante punto de vista. ¿Alguien lo ve de otra forma? Os leemos 👇',
    'Gracias por comentar. Aquí damos los datos, sin humo; el debate es vuestro 👇',
  ],
  emoji: ['🙌🙌', '¡Gracias! 💨', '👀🙌'],
};

const INSTRUCCIONES_IA = `Eres el community manager del canal de noticias "sin humo TV" (vídeos cortos que explican noticias del día con datos, de forma neutral).
Escribe UNA respuesta a un comentario de un seguidor, en español de España.
Reglas:
- Máximo 2 frases y 220 caracteres. Tono cercano, amable y con energía. Como mucho un emoji.
- Neutralidad total: nunca des tu opinión política ni tomes partido, no ataques a nadie, no califiques a partidos, personas ni colectivos.
- No inventes datos. Solo puedes usar lo que aparece en el título o la descripción del vídeo. Si preguntan algo que no sabes, invita a mirar las fuentes de la descripción.
- No prometas nada (fechas, vídeos concretos) ni des consejos legales, médicos o financieros.
- Si el comentario es una opinión, agradécela y devuelve una pregunta abierta y neutral.
- Si es un elogio, da las gracias.
- No uses comillas ni firmes. No menciones que eres una IA salvo que te lo pregunten directamente; si lo preguntan, di que las respuestas son automáticas.
- Si el comentario es ofensivo, de odio, sexual, spam o sobre un menor o una víctima, responde solo con: NO_RESPONDER`;

/* ================== PUNTO DE ENTRADA (cada 5 minutos) ================== */

function revisarComentarios() {
  const props = PropertiesService.getScriptProperties();
  if (props.getProperty('PAUSADO') === '1') return;
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(5000)) return;
  try {
    const estado = leerEstado_();
    let hechas = 0;
    try { hechas += revisarYouTube_(estado, AJUSTES.maxPorRonda - hechas); } catch (e) { anotarError_('YouTube', e); }
    try { hechas += revisarInstagram_(estado, AJUSTES.maxPorRonda - hechas); } catch (e) { anotarError_('Instagram', e); }
    guardarEstado_(estado);
  } finally {
    lock.releaseLock();
  }
}

/* ================== YOUTUBE ================== */

function revisarYouTube_(estado, cupo) {
  if (cupo <= 0) return 0;
  const props = PropertiesService.getScriptProperties();
  let miCanal = props.getProperty('YT_CANAL');
  if (!miCanal) {
    const r = YouTube.Channels.list('id', { mine: true });
    if (!r.items || !r.items.length) throw new Error('La cuenta autorizada no tiene canal de YouTube');
    miCanal = r.items[0].id;
    props.setProperty('YT_CANAL', miCanal);
  }
  const res = YouTube.CommentThreads.list('snippet,replies', {
    allThreadsRelatedToChannelId: miCanal, order: 'time', maxResults: AJUSTES.ytHilos, textFormat: 'plainText',
  });
  const titulos = {};
  let hechas = 0;
  for (const hilo of (res.items || [])) {
    if (hechas >= cupo || !quedaCupoDiario_(estado)) break;
    const c = hilo.snippet.topLevelComment;
    const s = c.snippet;
    const id = 'yt:' + c.id;
    if (estado.hechos.indexOf(id) >= 0) continue;
    if (s.authorChannelId && s.authorChannelId.value === miCanal) { marcar_(estado, id); continue; }
    const yaRespondido = ((hilo.replies && hilo.replies.comments) || []).some(
      r => r.snippet.authorChannelId && r.snippet.authorChannelId.value === miCanal);
    if (yaRespondido) { marcar_(estado, id); continue; }
    const edad = minutosDesde_(s.publishedAt);
    if (edad < AJUSTES.esperaMinutos) continue;
    if (edad > AJUSTES.diasAtras * 1440) { marcar_(estado, id); continue; }
    const vid = s.videoId;
    if (vid && !(vid in titulos)) {
      try {
        const v = YouTube.Videos.list('snippet', { id: vid });
        titulos[vid] = v.items && v.items[0] ? v.items[0].snippet.title + '\n' + (v.items[0].snippet.description || '').slice(0, 600) : '';
      } catch (e) { titulos[vid] = ''; }
    }
    const texto = s.textOriginal || s.textDisplay || '';
    const respuesta = crearRespuesta_(texto, titulos[vid] || '');
    marcar_(estado, id);
    if (!respuesta) { registrar_('YouTube', s.authorDisplayName, texto, '(ignorado)'); continue; }
    YouTube.Comments.insert({ snippet: { parentId: c.id, textOriginal: respuesta } }, 'snippet');
    contarDia_(estado);
    registrar_('YouTube', s.authorDisplayName, texto, respuesta);
    hechas++;
  }
  return hechas;
}

/* ================== INSTAGRAM ================== */

const IG = 'https://graph.instagram.com/v21.0';

function igGet_(ruta, params) {
  const token = PropertiesService.getScriptProperties().getProperty('INSTAGRAM_TOKEN');
  const q = Object.keys(params || {}).map(k => k + '=' + encodeURIComponent(params[k])).join('&');
  const url = IG + ruta + '?' + (q ? q + '&' : '') + 'access_token=' + encodeURIComponent(token);
  const r = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
  const j = JSON.parse(r.getContentText() || '{}');
  if (r.getResponseCode() >= 300 || j.error) throw new Error('Instagram ' + r.getResponseCode() + ': ' + (j.error ? j.error.message : r.getContentText()).slice(0, 200));
  return j;
}

function igPost_(ruta, params) {
  const token = PropertiesService.getScriptProperties().getProperty('INSTAGRAM_TOKEN');
  const r = UrlFetchApp.fetch(IG + ruta, {
    method: 'post', muteHttpExceptions: true,
    payload: Object.assign({}, params, { access_token: token }),
  });
  const j = JSON.parse(r.getContentText() || '{}');
  if (r.getResponseCode() >= 300 || j.error) throw new Error('Instagram ' + r.getResponseCode() + ': ' + (j.error ? j.error.message : r.getContentText()).slice(0, 200));
  return j;
}

function revisarInstagram_(estado, cupo) {
  if (cupo <= 0) return 0;
  const props = PropertiesService.getScriptProperties();
  if (!props.getProperty('INSTAGRAM_TOKEN')) return 0;
  let yo = props.getProperty('IG_USUARIO');
  if (!yo) {
    const me = igGet_('/me', { fields: 'user_id,username' });
    yo = me.username;
    props.setProperty('IG_USUARIO', yo);
  }
  const medios = igGet_('/me/media', { fields: 'id,caption,timestamp', limit: AJUSTES.igPublicaciones }).data || [];
  let hechas = 0;
  for (const m of medios) {
    if (hechas >= cupo || !quedaCupoDiario_(estado)) break;
    if (minutosDesde_(m.timestamp) > (AJUSTES.diasAtras + 7) * 1440) continue;
    const coms = igGet_('/' + m.id + '/comments', { fields: 'id,text,username,timestamp,replies{username}', limit: 50 }).data || [];
    for (const c of coms) {
      if (hechas >= cupo || !quedaCupoDiario_(estado)) break;
      const id = 'ig:' + c.id;
      if (estado.hechos.indexOf(id) >= 0) continue;
      if (c.username === yo) { marcar_(estado, id); continue; }
      const yaRespondido = ((c.replies && c.replies.data) || []).some(r => r.username === yo);
      if (yaRespondido) { marcar_(estado, id); continue; }
      const edad = minutosDesde_(c.timestamp);
      if (edad < AJUSTES.esperaMinutos) continue;
      if (edad > AJUSTES.diasAtras * 1440) { marcar_(estado, id); continue; }
      const respuesta = crearRespuesta_(c.text || '', m.caption || '');
      marcar_(estado, id);
      if (!respuesta) { registrar_('Instagram', c.username, c.text, '(ignorado)'); continue; }
      igPost_('/' + c.id + '/replies', { message: respuesta });
      contarDia_(estado);
      registrar_('Instagram', c.username, c.text, respuesta);
      hechas++;
    }
  }
  return hechas;
}

/** Renueva el token de Instagram (caduca a los 60 días). Se ejecuta sola cada semana. */
function renovarTokenInstagram() {
  const props = PropertiesService.getScriptProperties();
  const token = props.getProperty('INSTAGRAM_TOKEN');
  if (!token) return;
  const r = UrlFetchApp.fetch('https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=' + encodeURIComponent(token), { muteHttpExceptions: true });
  const j = JSON.parse(r.getContentText() || '{}');
  if (j.access_token) props.setProperty('INSTAGRAM_TOKEN', j.access_token);
  else anotarError_('Renovar token Instagram', new Error(r.getContentText().slice(0, 200)));
}

/* ================== CREAR LA RESPUESTA ================== */

function crearRespuesta_(comentario, contexto) {
  const t = (comentario || '').trim();
  if (!t) return null;
  const min = t.toLowerCase();
  if (/https?:\/\/|www\.|\.com\b|\.es\b|@\w{3,}.*@\w{3,}/.test(min)) return null;   // enlaces o spam de menciones
  const palabras = ' ' + min.split(/[^\p{L}\p{N}]+/u).join(' ') + ' ';   // compara palabras completas ("imputado" no es un insulto)
  if (PALABRAS_IGNORAR.some(p => palabras.indexOf(' ' + p + ' ') >= 0)) return null;
  const sinLetras = t.replace(/[\s\p{Emoji_Presentation}\p{Extended_Pictographic}‍️!?¡¿.,]/gu, '');
  if (!sinLetras) return elegir_(RESPUESTAS_TIPO.emoji);

  const clave = PropertiesService.getScriptProperties().getProperty('GEMINI_KEY');
  if (clave) {
    try {
      const ia = preguntarGemini_(clave, t, contexto);
      if (ia === 'NO_RESPONDER') return null;
      if (ia) return ia;
    } catch (e) { console.error('Gemini: ' + e); }   // si falla, usa una respuesta tipo
  }
  return respuestaTipo_(min);
}

function preguntarGemini_(clave, comentario, contexto) {
  const url = 'https://generativelanguage.googleapis.com/v1beta/models/' + AJUSTES.modeloGemini + ':generateContent?key=' + encodeURIComponent(clave);
  const cuerpo = {
    systemInstruction: { parts: [{ text: INSTRUCCIONES_IA }] },
    contents: [{ role: 'user', parts: [{ text: 'VÍDEO (título y descripción):\n' + (contexto || '(sin datos)').slice(0, 1200) + '\n\nCOMENTARIO DEL SEGUIDOR:\n' + comentario.slice(0, 1500) }] }],
    generationConfig: { temperature: 0.7, maxOutputTokens: 150, thinkingConfig: { thinkingBudget: 0 } },
  };
  const r = UrlFetchApp.fetch(url, { method: 'post', contentType: 'application/json', payload: JSON.stringify(cuerpo), muteHttpExceptions: true });
  if (r.getResponseCode() >= 300) throw new Error('Gemini ' + r.getResponseCode() + ': ' + r.getContentText().slice(0, 200));
  const j = JSON.parse(r.getContentText());
  const partes = j.candidates && j.candidates[0] && j.candidates[0].content && j.candidates[0].content.parts;
  if (!partes) return null;                       // bloqueado por seguridad → respuesta tipo
  let txt = partes.map(p => p.text || '').join('').trim().replace(/^["“«]|["”»]$/g, '');
  if (txt.indexOf('NO_RESPONDER') >= 0) return 'NO_RESPONDER';
  if (!txt) return null;
  if (txt.length > 280) txt = txt.slice(0, 277).replace(/\s+\S*$/, '') + '…';
  return txt;
}

function respuestaTipo_(min) {
  if (/[¿?]/.test(min)) return elegir_(RESPUESTAS_TIPO.pregunta);
  if (/(gracias|genial|buen[oa]|crack|top|me encanta|bravo|excelente|bien explicado|sigue así|sigan así)/.test(min)) return elegir_(RESPUESTAS_TIPO.gracias);
  return elegir_(RESPUESTAS_TIPO.opinion);
}

function elegir_(lista) { return lista[Math.floor(Math.random() * lista.length)]; }

/* ================== ESTADO, LÍMITES Y REGISTRO ================== */

function leerEstado_() {
  const p = PropertiesService.getScriptProperties();
  let e;
  try { e = JSON.parse(p.getProperty('ESTADO') || '{}'); } catch (x) { e = {}; }
  e.hechos = e.hechos || [];
  const hoy = Utilities.formatDate(new Date(), 'Europe/Madrid', 'yyyy-MM-dd');
  if (e.dia !== hoy) { e.dia = hoy; e.hoy = 0; }
  return e;
}

function guardarEstado_(e) {
  e.hechos = e.hechos.slice(-400);              // recuerda los últimos 400 comentarios revisados
  PropertiesService.getScriptProperties().setProperty('ESTADO', JSON.stringify(e));
}

function marcar_(e, id) { if (e.hechos.indexOf(id) < 0) e.hechos.push(id); }
function quedaCupoDiario_(e) { return e.hoy < AJUSTES.maxPorDia; }
function contarDia_(e) { e.hoy++; }
function minutosDesde_(fecha) { return (Date.now() - new Date(fecha).getTime()) / 60000; }

/** Hoja "sin humo TV - respuestas" en tu Drive: puedes ver desde el móvil todo lo que se ha respondido. */
function hoja_() {
  const p = PropertiesService.getScriptProperties();
  let id = p.getProperty('HOJA_ID');
  let ss = null;
  if (id) { try { ss = SpreadsheetApp.openById(id); } catch (e) { ss = null; } }
  if (!ss) {
    ss = SpreadsheetApp.create('sin humo TV - respuestas a comentarios');
    ss.getSheets()[0].appendRow(['Fecha', 'Red', 'Usuario', 'Comentario', 'Respuesta']);
    ss.getSheets()[0].setFrozenRows(1);
    p.setProperty('HOJA_ID', ss.getId());
  }
  return ss.getSheets()[0];
}

function registrar_(red, usuario, comentario, respuesta) {
  try {
    hoja_().appendRow([Utilities.formatDate(new Date(), 'Europe/Madrid', 'dd/MM/yyyy HH:mm'), red, usuario || '', (comentario || '').slice(0, 500), respuesta]);
  } catch (e) { console.log('No se pudo registrar: ' + e); }
}

function anotarError_(donde, e) {
  console.error(donde + ': ' + e);
  try { hoja_().appendRow([Utilities.formatDate(new Date(), 'Europe/Madrid', 'dd/MM/yyyy HH:mm'), donde, 'ERROR', String(e).slice(0, 300), '']); } catch (x) {}
}

/* ================== INSTALACIÓN ================== */

/** Ejecútala UNA vez: pide permisos, crea la hoja de registro y activa la revisión cada 5 minutos. */
function configurar() {
  ScriptApp.getProjectTriggers().forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('revisarComentarios').timeBased().everyMinutes(5).create();
  ScriptApp.newTrigger('renovarTokenInstagram').timeBased().everyWeeks(1).onWeekDay(ScriptApp.WeekDay.MONDAY).atHour(4).create();
  const canal = YouTube.Channels.list('snippet', { mine: true });
  const nombre = canal.items && canal.items[0] ? canal.items[0].snippet.title : '(sin canal en esta cuenta)';
  hoja_();
  // Al empezar no responde a los comentarios antiguos: solo a los que lleguen desde ahora.
  const estado = leerEstado_();
  guardarEstado_(estado);
  marcarExistentes_();
  console.log('Listo. Canal de YouTube: ' + nombre + '. Instagram: ' + (PropertiesService.getScriptProperties().getProperty('INSTAGRAM_TOKEN') ? 'conectado' : 'sin token (solo YouTube)') + '. Gemini: ' + (PropertiesService.getScriptProperties().getProperty('GEMINI_KEY') ? 'sí' : 'no (respuestas tipo)'));
}

/** Marca como ya vistos los comentarios que existían antes de activarlo. */
function marcarExistentes_() {
  const estado = leerEstado_();
  const p = PropertiesService.getScriptProperties();
  try {
    const r = YouTube.Channels.list('id', { mine: true });
    if (r.items && r.items.length) {
      p.setProperty('YT_CANAL', r.items[0].id);
      const res = YouTube.CommentThreads.list('snippet', { allThreadsRelatedToChannelId: r.items[0].id, order: 'time', maxResults: AJUSTES.ytHilos });
      (res.items || []).forEach(h => marcar_(estado, 'yt:' + h.snippet.topLevelComment.id));
    }
  } catch (e) { anotarError_('YouTube (inicio)', e); }
  try {
    if (p.getProperty('INSTAGRAM_TOKEN')) {
      const medios = igGet_('/me/media', { fields: 'id', limit: AJUSTES.igPublicaciones }).data || [];
      medios.forEach(m => (igGet_('/' + m.id + '/comments', { fields: 'id', limit: 50 }).data || []).forEach(c => marcar_(estado, 'ig:' + c.id)));
    }
  } catch (e) { anotarError_('Instagram (inicio)', e); }
  guardarEstado_(estado);
}

/** Para pararlo del todo: ejecuta esta función (o pon PAUSADO = 1 en las propiedades). */
function desactivar() {
  ScriptApp.getProjectTriggers().forEach(t => ScriptApp.deleteTrigger(t));
  console.log('Respondedor desactivado.');
}

/** Prueba sin publicar nada: muestra qué respondería a un comentario de ejemplo. */
function probarRespuesta() {
  console.log(crearRespuesta_('¿Y entonces el PSOE no está imputado?', '¿Puede un partido entero acabar imputado? 5 delitos y un juez'));
  console.log(crearRespuesta_('Muy bien explicado, gracias', ''));
  console.log(crearRespuesta_('🔥🔥', ''));
}
