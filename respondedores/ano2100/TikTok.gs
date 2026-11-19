/**
 * (18-nov-2026) TIKTOK · respuestas a comentarios con la app aprobada «Explícalo Community Replies» (TikTok Business API,
 * permiso «TikTok Accounts»). Este archivo se añade TAL CUAL al proyecto de Apps Script de cada canal, junto a Codigo.gs.
 *
 * Propiedades del script (Configuración del proyecto → Propiedades del script; solo las ves tú):
 *   TIKTOK_APP_ID   → el App ID de la app (7709560388471373845)
 *   TIKTOK_SECRET   → el «Secret» de la app (portal de TikTok → My Apps → la app)
 *   TIKTOK_CODIGO   → el auth_code que da TikTok al autorizar la cuenta del canal (solo para conectar; caduca en minutos)
 *   TIKTOK_REDIRECT → (opcional) la dirección de redirección de la app; por defecto https://explicalo.es/
 * Conectar: 1) abre el enlace de autorización de la app (portal → My Apps → la app → «TikTok account holder authorization»),
 * entra con la cuenta de TikTok de ESTE canal y acepta; 2) te lleva a explicalo.es/?auth_code=…: copia el valor de auth_code
 * en TIKTOK_CODIGO; 3) ejecuta conectarTikTok. 4) ejecuta probarTikTok para ver que lee los vídeos y comentarios (no responde).
 * Las claves se renuevan solas (la de acceso dura 24 h; la de renovación, un año).
 */
const TT_API = 'https://business-api.tiktok.com/open_api/v1.3';

function ttLlamar_(metodo, ruta, datos, token) {
  const op = { method: metodo, muteHttpExceptions: true, headers: { 'Content-Type': 'application/json' } };
  if (token) op.headers['Access-Token'] = token;
  let url = TT_API + ruta;
  if (metodo === 'get') url += '?' + Object.keys(datos || {}).map(k => k + '=' + encodeURIComponent(typeof datos[k] === 'string' ? datos[k] : JSON.stringify(datos[k]))).join('&');
  else op.payload = JSON.stringify(datos || {});
  const r = UrlFetchApp.fetch(url, op), txt = r.getContentText();
  let j = {}; try { j = JSON.parse(txt || '{}'); } catch (e) { throw new Error('TikTok ' + ruta + ' respuesta rara: ' + txt.slice(0, 200)); }
  if (j.code !== 0) throw new Error('TikTok ' + ruta + ' → ' + j.code + ' ' + (j.message || '') + ' ' + txt.slice(0, 200));
  return j.data || {};
}

function ttGuardar_(d) {
  const p = PropertiesService.getScriptProperties(), viejo = JSON.parse(p.getProperty('TIKTOK_TOKENS') || '{}');
  const t = { access: d.access_token, refresh: d.refresh_token || viejo.refresh, open_id: d.open_id || viejo.open_id,
              caduca: Date.now() + ((d.expires_in || 86400) - 600) * 1000 };
  p.setProperty('TIKTOK_TOKENS', JSON.stringify(t)); return t;
}

/** Ejecútala una vez por canal, con TIKTOK_CODIGO recién copiado. */
function conectarTikTok() {
  const p = PropertiesService.getScriptProperties();
  const d = ttLlamar_('post', '/tt_user/oauth2/token/', {
    client_id: (p.getProperty('TIKTOK_APP_ID') || '').trim(), client_secret: (p.getProperty('TIKTOK_SECRET') || '').trim(),
    grant_type: 'authorization_code', auth_code: decodeURIComponent((p.getProperty('TIKTOK_CODIGO') || '').trim()),
    redirect_uri: (p.getProperty('TIKTOK_REDIRECT') || 'https://explicalo.es/').trim() });
  const t = ttGuardar_(d); p.deleteProperty('TIKTOK_CODIGO');
  console.log('TikTok conectado. open_id: ' + t.open_id + '. Ahora ejecuta probarTikTok.');
}

function ttToken_() {
  const p = PropertiesService.getScriptProperties();
  let t = JSON.parse(p.getProperty('TIKTOK_TOKENS') || 'null');
  if (!t) return null;
  if (Date.now() > t.caduca) {
    t = ttGuardar_(ttLlamar_('post', '/tt_user/oauth2/refresh_token/', {
      client_id: (p.getProperty('TIKTOK_APP_ID') || '').trim(), client_secret: (p.getProperty('TIKTOK_SECRET') || '').trim(),
      grant_type: 'refresh_token', refresh_token: t.refresh }));
  }
  return t;
}

function ttVideos_(t) {
  const d = ttLlamar_('get', '/business/video/list/', { business_id: t.open_id, fields: ['item_id', 'create_time', 'caption'], max_count: 10 }, t.access);
  return d.videos || d.list || [];
}
function ttComentarios_(t, videoId) {
  const d = ttLlamar_('get', '/business/comment/list/', { business_id: t.open_id, video_id: videoId, max_count: 30, status: 'PUBLIC', sort_field: 'create_time', sort_order: 'desc' }, t.access);
  return d.comments || d.list || [];
}

/** (18-nov-2026) Hora en minutos desde que se escribió (TikTok la da en segundos o en milisegundos, como número o texto). */
function ttEdadMin_(ct) { let n = Number(ct); if (!n) return 999; if (n > 1e12) n = n / 1000; return (Date.now() / 1000 - n) / 60; }
/** Por qué un comentario no se responde: 'propio' (lo escribió el canal), 'respuesta' (contesta a otro comentario) u '' (se responde). */
function ttMotivo_(c, t, vid) {
  if (c.owner === true || c.owner === 'true' || (c.user_id && c.user_id === t.open_id)) return 'propio';
  const p = String(c.parent_comment_id || ''), cid = String(c.comment_id || c.id || '');
  if (p && p !== '0' && p !== cid && p !== String(vid)) return 'respuesta';
  return '';
}

/** La llama revisarComentarios() cada 5 minutos. */
function revisarTikTok_(estado, cupo) {
  if (cupo <= 0) return 0;
  const t = ttToken_(); if (!t) return 0;
  let hechas = 0;
  for (const v of ttVideos_(t)) {
    if (hechas >= cupo || !quedaCupoDiario_(estado)) break;
    const vid = v.item_id || v.video_id;
    if (v.create_time && (Date.now() / 1000 - v.create_time) > (AJUSTES.diasAtras + 7) * 86400) continue;
    for (const c of ttComentarios_(t, vid)) {
      if (hechas >= cupo || !quedaCupoDiario_(estado)) break;
      const id = 'tt:' + (c.comment_id || c.id);
      if (estado.hechos.indexOf(id) >= 0) continue;
      const mot = ttMotivo_(c, t, vid);
      if (mot === 'propio' || mot === 'respuesta') { marcar_(estado, id); continue; }
      const edadMin = ttEdadMin_(c.create_time);
      if (edadMin < AJUSTES.esperaMinutos) continue;
      if (edadMin > AJUSTES.diasAtras * 1440) { marcar_(estado, id); continue; }
      const respuesta = crearRespuesta_(c.text || '', v.caption || '');
      if (respuesta === undefined) continue;
      marcar_(estado, id); guardarEstado_(estado);   // (19-nov-2026) se guarda YA: si la ronda se corta, no se responde dos veces
      if (!respuesta) { registrar_('TikTok', c.username || c.display_name || '', c.text, '(ignorado)'); continue; }
      ttLlamar_('post', '/business/comment/reply/create/', { business_id: t.open_id, video_id: vid, comment_id: c.comment_id || c.id, text: respuesta }, t.access);
      contarDia_(estado);
      registrar_('TikTok', c.username || c.display_name || '', c.text, respuesta);
      hechas++;
      Utilities.sleep(1500);
    }
  }
  return hechas;
}

/** Comprueba la conexión: muestra los últimos vídeos y comentarios SIN responder nada. */
function probarTikTok() {
  const t = ttToken_(); if (!t) { console.log('Falta conectar: ejecuta conectarTikTok con TIKTOK_CODIGO.'); return; }
  const vs = ttVideos_(t); console.log('Vídeos leídos: ' + vs.length);
  vs.slice(0, 3).forEach(v => { const cs = ttComentarios_(t, v.item_id || v.video_id); console.log('· ' + (v.caption || '').slice(0, 60) + ' → ' + cs.length + ' comentarios'); cs.slice(0, 3).forEach(c => console.log('   - ' + (c.text || '').slice(0, 80))); });
}

/** (18-nov-2026) Muestra, para los comentarios recientes, los datos que da TikTok y si se van a responder (no responde nada). */
function diagnosticarTikTok() {
  const t = ttToken_(), e = leerEstado_();
  ttVideos_(t).slice(0, 3).forEach(v => { const vid = v.item_id || v.video_id;
    ttComentarios_(t, vid).slice(0, 5).forEach(c => { const id = 'tt:' + (c.comment_id || c.id);
      console.log((c.text || '').slice(0, 40) + ' | ya visto: ' + (e.hechos.indexOf(id) >= 0) + ' | motivo: ' + (ttMotivo_(c, t, vid) || 'se responde') + ' | minutos: ' + Math.round(ttEdadMin_(c.create_time)) + ' | datos: ' + JSON.stringify(c).slice(0, 300)); }); });
}
/** Vuelve a mirar los comentarios de TikTok que se dieron por vistos (por si se saltaron por error). */
function reintentarTikTok() { const e = leerEstado_(); e.hechos = e.hechos.filter(x => x.indexOf('tt:') !== 0); guardarEstado_(e); console.log('Listo: en la próxima ronda se revisan otra vez los comentarios de TikTok.'); }
