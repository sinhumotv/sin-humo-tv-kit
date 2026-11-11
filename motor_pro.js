/* sin humo TV · MOTOR PRO (v68, 11-nov-2026) · cortos (720x1280) y largos (1280x720)
   Pablo: «los vídeos tendrían que ser muchísimo más dinámicos y mejor visualmente, pero una barbaridad. Me da igual que cambie entero
   el estilo, mientras mantengas el tono naranja». Y como referencia de lo que le gusta, un corto de noticias animadas: fondo claro y
   limpio, dibujos planos tipo pegatina, letra negra muy gruesa, la palabra clave con franja naranja, elementos que saltan a pantalla
   cuando la voz los nombra y un plano nuevo cada 2-3 segundos.
   Este motor sigue esa línea con la identidad de sin humo TV (naranja, Lupi, nube):
     · fondo crema liso con trama de puntos; todo a pantalla completa, sin tarjeta;
     · piezas tipo PEGATINA: borde negro grueso y sombra dura; entran con rebote;
     · TEXTO CINÉTICO negro: entra palabra a palabra y la palabra clave lleva una franja naranja que se pinta detrás;
     · PEGATINAS CON LA VOZ: cada palabra clave del subtítulo salta como etiqueta en el momento en que se dice;
     · cifras que cuentan, barras que crecen, listas y líneas de tiempo que avanzan con la escena;
     · las fotos reales van como una gran foto enmarcada (quieta), con su etiqueta «FOTO REAL»;
     · cambio de plano con barrido rápido y desenfoque de movimiento; subtítulos grandes de 2-3 palabras.
   Usa el MISMO proyecto.json y tiempos.json. Se activa con "aspecto": "pro" o ASPECTO_DEFECTO = 'pro' en motor.js. */
(function () {
  const P = window.PROY, T = window.TIEMPOS, SH = window.SH;
  if (!SH || !SH.pro || !SH.pro()) return;
  const HOR = P.formato === 'YOUTUBE', W = HOR ? 1280 : 720, H = HOR ? 720 : 1280;
  const { A, lupi, nube, bloquesKaraoke } = SH, icono = SH.icono || ((n, x, y, s) => A.alerta(x, y, s));
  const BG = '#fbf2dc', INK = '#1b1721', ORA = '#f2681c', ORO = '#ffc61a', VER = '#14a596', ROJ = '#e5372b', AZU = '#2f62e6', MOR = '#6b4fa3', GRI = '#cfc5b0', BLA = '#fffdf7';
  const COL = { rojo: ROJ, azul: AZU, verde: VER, oro: ORO, naranja: ORA, morado: MOR, crema: BLA, tinta: INK, celeste: '#3fa9e0', rosa: '#e0479e', gris: '#8f887c', amarillo: '#f2c80f', granate: '#8e1b2b', negro: INK };
  const col = c => COL[c] || (/^#/.test(c || '') ? c : ORA);
  const cl = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const eo = x => 1 - Math.pow(1 - cl(x), 3), eio = x => { x = cl(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
  const back = x => { x = cl(x); const c = 2.2; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };   // rebote al entrar
  const frac = x => x - Math.floor(x);
  const esc = s => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const E = P.escenas, N = E.length, DUR = T.duracion;
  const CAPS = (P.capitulos || []).filter(c => c && c.desde < N);
  const GRAVE = P.tono === 'grave';
  const SX = HOR ? 0 : 60;   // v55: margen lateral que recortan TikTok/Instagram/YouTube en móviles alargados (zona segura)
  const Z = HOR ? { x: 80, y: 128, w: 1120, h: 392 } : { x: SX + 26, y: 318, w: W - 2 * SX - 52, h: 514 };   // v63: todo baja ~40 px (arriba están los menús de TikTok e Instagram)   // zona del gráfico
  const ZC = { x: Z.x + Z.w / 2, y: Z.y + Z.h / 2 };
  const SOM = HOR ? 7 : 8;                // desplazamiento de la sombra dura
  // ===== v68 (11-nov-2026): Lupi, barra de progreso y logo modernos (pedido de Pablo) =====
  // Lupi moderno: lente de cristal con degradado y brillo, aro degradado naranja-oro, ojos grandes con brillos, mejillas,
  // contornos finos y sombra suave. Misma interfaz que lupi() de motor.js (x, y, s, t, rot, expr, mira, brazos, mini, sinCara, texto, fs).
  const DEF_LUPI = `<defs><radialGradient id="lmL" cx=".38" cy=".32" r=".8"><stop offset="0" stop-color="#ffffff"/><stop offset=".55" stop-color="#e3f3fb"/><stop offset="1" stop-color="#9fd2ea"/></radialGradient>` +
    `<linearGradient id="lmA" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffb347"/><stop offset=".5" stop-color="${ORA}"/><stop offset="1" stop-color="#d9480f"/></linearGradient>` +
    `<linearGradient id="lmM" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff8a3d"/><stop offset="1" stop-color="#c2410c"/></linearGradient>` +
    `<filter id="lmS" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>` +
    `<filter id="somS" x="-20%" y="-20%" width="140%" height="160%"><feGaussianBlur stdDeviation="7"/></filter></defs>`;   // v69: sombra suave de tarjetas
  let defLupiPuesto = -1;
  function caraM(expr, t, mira = [0, 0]) {
    const [mx, my] = mira, parp = ((t + .7) % 3.3) < .12, guino = expr === 'guino';
    const ojo = (ex, cerr) => cerr || parp ? `<path d="M${ex - 12} 0 q12 9 24 0" stroke="${INK}" stroke-width="3" fill="none" stroke-linecap="round"/>`
      : `<ellipse cx="${ex}" cy="0" rx="12" ry="${expr === 'sorprendida' ? 16 : 14}" fill="#fff" stroke="${INK}" stroke-width="3"/><circle cx="${ex + mx * 4}" cy="${2 + my * 4}" r="7.5" fill="${INK}"/><circle cx="${ex + mx * 4 + 2.5}" cy="${-1.5 + my * 4}" r="2.6" fill="#fff"/>`;
    const cej = { sorprendida: [-26, 0], seria: [-20, -6], enfadada: [-17, -14], curiosa: [-22, 5] }[expr] || [-22, 3];
    const ceja = (ex, sg) => `<path d="M${ex - 11} ${cej[0] + sg * cej[1] * .5} Q${ex} ${cej[0] - 4} ${ex + 11} ${cej[0] - sg * cej[1] * .5}" stroke="${INK}" stroke-width="3" fill="none" stroke-linecap="round"/>`;
    const boca = {
      sorprendida: `<ellipse cx="0" cy="27" rx="7" ry="9" fill="${INK}"/>`,
      seria: `<path d="M-9 27 h18" stroke="${INK}" stroke-width="3" stroke-linecap="round"/>`,
      enfadada: `<path d="M-10 30 q10 -8 20 0" stroke="${INK}" stroke-width="3" fill="none" stroke-linecap="round"/>`,
      curiosa: `<path d="M-6 26 q7 5 13 -1" stroke="${INK}" stroke-width="3" fill="none" stroke-linecap="round"/>`,
      habla: `<path d="M-10 23 q10 ${(8 + 9 * Math.abs(Math.sin(t * 17))).toFixed(1)} 20 0 z" fill="${INK}"/><path d="M-5 ${(27 + 4 * Math.abs(Math.sin(t * 17))).toFixed(1)} q5 3 10 0" stroke="#ff6b6b" stroke-width="4" stroke-linecap="round"/>`,
      guino: `<path d="M-11 22 q11 13 22 0 z" fill="${INK}"/>`,
    }[expr] || `<path d="M-11 22 q11 13 22 0 z" fill="${INK}"/>`;
    return `<g>` + `<ellipse cx="-34" cy="16" rx="9" ry="5" fill="#ff7a7a" opacity=".45"/><ellipse cx="34" cy="16" rx="9" ry="5" fill="#ff7a7a" opacity=".45"/>` +
      ceja(-19, 1) + ceja(19, -1) + ojo(-19, false) + ojo(19, guino) + boca + `</g>`;
  }
  function lupiM(o) {
    const R = 60, s = o.s || 1, t = o.t || 0, rot = o.rot || 0, mini = !!o.mini, sw = Math.sin(t * 3) * 4;
    const sombra = mini ? '' : `<ellipse cx="0" cy="${R + 112}" rx="44" ry="9" fill="${INK}" opacity=".18" filter="url(#lmS)"/>`;
    const mango = `<g transform="rotate(${(sw * .4).toFixed(2)} 0 ${R})"><rect x="-14" y="${R + 2}" width="28" height="${mini ? 60 : 96}" rx="14" fill="url(#lmM)" stroke="${INK}" stroke-width="3"/>` +
      `<rect x="-7" y="${R + 10}" width="6" height="${mini ? 40 : 74}" rx="3" fill="#fff" opacity=".35"/></g>`;
    let brazos = '';
    if (!mini) {
      const angD = o.brazos === 'senala' ? -35 : o.brazos === 'saluda' ? -65 + Math.sin(t * 8) * 15 : 35, angI = o.brazos === 'saluda' || o.brazos === 'senala' ? 40 : 35;
      const br = (lado, ang) => { const a = ang * Math.PI / 180, x0 = lado * (R + 6), y0 = 18, x1 = x0 + lado * Math.cos(a) * 62, y1 = y0 + Math.sin(a) * 62;
        return `<path d="M${x0} ${y0} Q${((x0 + x1) / 2).toFixed(1)} ${((y0 + y1) / 2 + 12).toFixed(1)} ${x1.toFixed(1)} ${y1.toFixed(1)}" stroke="${INK}" stroke-width="3" fill="none" stroke-linecap="round"/><circle cx="${x1.toFixed(1)}" cy="${y1.toFixed(1)}" r="11" fill="#fff" stroke="${INK}" stroke-width="3"/>`; };
      brazos = br(1, angD) + br(-1, angI);
    }
    const lente = `<circle r="${R}" fill="url(#lmL)"/><path d="M${-R * .62} ${-R * .18} A${R * .66} ${R * .66} 0 0 1 ${-R * .1} ${-R * .64}" stroke="#fff" stroke-width="10" fill="none" stroke-linecap="round" opacity=".9"/><circle cx="${R * .38}" cy="${-R * .44}" r="6" fill="#fff" opacity=".9"/>`;
    const cara_ = o.sinCara || mini ? '' : caraM(o.expr || 'feliz', t, o.mira || [0, 0]);
    const texto = o.texto !== undefined ? `<g transform="rotate(${-rot})"><text y="${((o.fs || 20) * .36).toFixed(1)}" font-family="Inter" font-weight="900" font-size="${o.fs || 20}" text-anchor="middle" fill="${INK}">${o.texto}</text></g>` : '';
    const aro = `<circle r="${R + 1}" fill="none" stroke="${INK}" stroke-width="15"/><circle r="${R + 1}" fill="none" stroke="url(#lmA)" stroke-width="10"/>`;
    const gorra = mini ? '' : `<g transform="translate(0 ${-R - 6}) rotate(-8)"><path d="M-32 6 Q-30 -28 0 -30 Q30 -28 32 6 Z" fill="${INK}" stroke="${INK}" stroke-width="3"/><path d="M-26 -2 Q-22 -22 0 -24" stroke="#fff" stroke-width="4" fill="none" opacity=".18" stroke-linecap="round"/>` +
      `<path d="M14 4 Q46 0 58 10 Q40 14 14 10 Z" fill="${ORA}" stroke="${INK}" stroke-width="3" stroke-linejoin="round"/><circle cy="-29" r="5" fill="${ORA}"/></g>`;
    return `<g transform="translate(${o.x} ${o.y}) rotate(${rot}) scale(${s})">${sombra}${mango}${brazos}${lente}${cara_}${texto}${aro}${gorra}</g>`;
  }
  // logo moderno: insignia naranja con la nube tachada en blanco + «sin humo» + pastilla «TV»
  function logoM(x, y, esc_ = 1, claro = false) {
    return `<g transform="translate(${x} ${y}) scale(${esc_})"><rect x="-21" y="-21" width="42" height="42" rx="12" fill="url(#lmA)"/><rect x="-21" y="-21" width="42" height="21" rx="12" fill="#fff" opacity=".12"/>` +
      `<path d="M-11 6 a6 6 0 0 1 1.5 -11 a8 8 0 0 1 15 -2 a6 6 0 0 1 4.5 11 Z" fill="#fff"/><path d="M-12 -10 L12 10" stroke="${ORA}" stroke-width="7" stroke-linecap="round"/><path d="M-12 -10 L12 10" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/>` +
      `<text x="32" y="10" font-family="Inter" font-weight="900" font-size="28" letter-spacing="-.8" fill="${claro ? '#fff' : INK}">sin humo</text>` +
      `<rect x="158" y="-14" width="40" height="28" rx="8" fill="${claro ? ORA : INK}"/><text x="178" y="7" font-family="Inter" font-weight="900" font-size="18" text-anchor="middle" fill="#fff">TV</text></g>`;
  }
  window.SH_ARTE = { DEF_LUPI, lupiM, logoM };   // v82: la miniatura de YouTube usa el mismo Lupi y logo modernos

  // ---------- piezas básicas ----------
  const partir0 = (s, max) => { const ls = []; let l = ''; for (const w of String(s || '').split(/\s+/).filter(Boolean)) { if (l && (l + ' ' + w).replace(/[§*]/g, '').length > max) { ls.push(l); l = w; } else l = l ? l + ' ' + w : w; } if (l) ls.push(l); return ls; };
  // v71: líneas equilibradas (sin una palabra huérfana en la última): el ancho más estrecho que da el mismo nº de líneas
  const partir = (s, max) => { const g = partir0(s, max); if (g.length < 2) return g; let m = max; while (m > 6 && partir0(s, m - 1).length === g.length) m--; return partir0(s, m); };
  const tx = (x, y, s, size, fill = INK, anchor = 'middle', peso = 900, extra = '') =>
    `<text x="${x.toFixed(1)}" y="${y.toFixed(1)}" font-family="Inter" font-weight="${peso}" font-size="${size.toFixed(1)}" text-anchor="${anchor}" fill="${fill}" letter-spacing="-.5" ${extra}>${s}</text>`;
  // caja tipo pegatina: sombra dura + relleno + borde negro
  // v69: estilo moderno: sombra suave difuminada (antes, sombra negra dura) y contorno fino
  const caja = (x, y, w, h, rx, fill = BLA, sw = 5, som = SOM) =>
    `<rect x="${(x + 2).toFixed(1)}" y="${(y + som * 1.2).toFixed(1)}" width="${(w - 4).toFixed(1)}" height="${h.toFixed(1)}" rx="${rx}" fill="${INK}" opacity=".2" filter="url(#somS)"/><rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${w.toFixed(1)}" height="${h.toFixed(1)}" rx="${rx}" fill="${fill}" stroke="${INK}" stroke-width="${Math.min(sw, 3)}"/>`;
  // titular cinético: palabra a palabra; las *claves* (o, si no hay, la palabra más larga) llevan franja naranja detrás
  function cinetico(texto, cx, y0, size, L, opt = {}) {
    const max = opt.max || 14, paso = opt.paso || .07, bruto = String(texto || '').replace(/\*/g, '§'), ls = partir(bruto, max), lh = size * 1.14;
    let auto = '';
    if (!/§/.test(bruto) && opt.auto !== false) auto = bruto.split(/\s+/).map(w => w.replace(/[^\wáéíóúñü%€.,-]/gi, '')).filter(w => /\d/.test(w)).sort((a, b) => b.length - a.length)[0] || bruto.split(/\s+/).filter(w => w.length >= 5).sort((a, b) => b.length - a.length)[0] || '';
    let i = 0, clave = false, out = '';
    ls.forEach((ln, j) => {
      const y = y0 + j * lh;
      const ws = ln.split(' ').map(w => { const ini = w.startsWith('§'); if (ini) clave = true; const lim = w.replace(/§/g, ''), o = { w: lim, clave: clave || (auto && lim === auto) }; if (/§[.,;:?!]*$/.test(w) && w.replace(/§/g, '').length) { if (!(ini && w.indexOf('§', 1) < 0)) clave = false; } return o; });
      const sp = ws.map((o, n) => {
        const t0 = (opt.t0 || 0) + (i++) * paso, p = cl((L - t0) / .2);
        if (p <= 0) return `<tspan fill-opacity="0">${esc(o.w)}</tspan>`;
        const fs = size * (1 + .25 * (1 - eo(p)));
        return `<tspan font-size="${fs.toFixed(1)}" fill="${o.clave ? '#fff' : (opt.fill || INK)}" fill-opacity="${eo(p * 2).toFixed(2)}"${o.clave ? ` data-hl="${eo((L - t0) / .28).toFixed(3)}" data-c="${opt.clave || ORA}"` : ''}>${esc(o.w)}</tspan>`;
      }).join(' ');
      out += tx(cx, y, sp, size, opt.fill || INK, opt.anchor || 'middle', 900, 'xml:space="preserve"');
    });
    return out;
  }
  const altoCin = (texto, size, max) => partir(String(texto || '').replace(/\*/g, ''), max).length * size * 1.14;
  // etiqueta/pegatina con texto (su caja se pinta después de medir: ver cajas())
  const peg = (x, y, s, size, fondo = ORA, color = '#fff', anchor = 'middle', op = 1, rot = 0, esc_ = 1) =>
    `<g transform="translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${rot}) scale(${Math.max(.001, esc_).toFixed(3)})" opacity="${op}"><text x="0" y="0" font-family="Inter" font-weight="900" font-size="${size}" text-anchor="${anchor}" fill="${color}" data-peg="${fondo}">${esc(s)}</text></g>`;
  function cajas() {                       // después de pintar: franjas de las palabras clave, cajas de las pegatinas y recuadro de la palabra que suena
    try {
      const NS = 'http://www.w3.org/2000/svg';
      document.querySelectorAll('#lienzo tspan[data-hl]').forEach(el => {
        const b = el.getBBox(), p = parseFloat(el.getAttribute('data-hl')) || 0; if (!b.width || p <= 0) return;
        const r = document.createElementNS(NS, 'rect'), m = b.height * .1;
        r.setAttribute('x', b.x - m); r.setAttribute('y', b.y + b.height * .1); r.setAttribute('width', (b.width + 2 * m) * p); r.setAttribute('height', b.height * .86);
        r.setAttribute('rx', b.height * .12); r.setAttribute('fill', el.getAttribute('data-c') || ORA);
        el.parentNode.parentNode.insertBefore(r, el.parentNode);
      });
      document.querySelectorAll('#lienzo text[data-peg]').forEach(el => {
        const b = el.getBBox(); if (!b.width) return;
        const mx = b.height * .5, my = b.height * .22, mk = (dx, dy, fill, st) => { const r = document.createElementNS(NS, 'rect'); r.setAttribute('x', b.x - mx + dx); r.setAttribute('y', b.y - my + dy); r.setAttribute('width', b.width + 2 * mx); r.setAttribute('height', b.height + 2 * my); r.setAttribute('rx', b.height * .28); r.setAttribute('fill', fill); if (st) { r.setAttribute('stroke', INK); r.setAttribute('stroke-width', Math.max(2, b.height * .07)); } return r; };
        const sm = mk(0, b.height * .2, INK, false); sm.setAttribute('opacity', '.22'); sm.setAttribute('filter', 'url(#somS)');
        el.parentNode.insertBefore(sm, el); el.parentNode.insertBefore(mk(0, 0, el.getAttribute('data-peg'), true), el);
      });
      // v80c: el emoji de la cabecera se coloca midiendo el rótulo de verdad (justo a su derecha)
      document.querySelectorAll('#lienzo g[data-emo]').forEach(g => {
        const peg_ = g.previousElementSibling, txt = peg_ && peg_.querySelector('text[data-peg]'); if (!txt) return;
        const rc = txt.getBoundingClientRect(), M_ = g.parentNode.getScreenCTM(); if (!rc.width || !M_) return;
        const [rot, sc, gap] = g.getAttribute('data-emo').split('|').map(Number), inv = M_.inverse(), pt = document.querySelector('#lienzo svg, svg').createSVGPoint();
        pt.x = rc.right; pt.y = rc.top + rc.height / 2; const q = pt.matrixTransform(inv);
        g.setAttribute('transform', `translate(${(q.x + gap).toFixed(1)} ${(q.y - 2).toFixed(1)}) rotate(${rot}) scale(${sc})`);
      });
      if (SH.resalta) SH.resalta();
    } catch (e) { }
  }

  // ---------- fondo propio de sin humo TV (v47, 11-nov-2026) ----------
  // Pablo: «diferenciarnos del canal de En Plata, parece una copia». Fuera el crema con trama de puntos. Ahora:
  // degradado melocotón cálido, estelas de HUMO naranja que suben despacio (el humo que el canal quita), la nube tachada de la marca
  // enorme y muy suave al fondo y un marco naranja redondeado alrededor de la pantalla.
  const VIAJE = .6;   // v90: segundos que tarda Lupi en volar entre la esquina y el centro
  const BG2 = GRAVE ? ['#f4f1ec', '#e4ded4'] : ['#fff7ee', '#ffe1c4'];
  function humo(i, t) {        // una estela de humo: curva ondulada que sube y se desvanece
    const per = 9 + i * 2.3, f = frac(t / per + i * .37), x0 = W * (.12 + .26 * i) + 30 * Math.sin(i * 2.1), y0 = H * (1.15 - 1.3 * f), a = 60 + 25 * i;
    let d = `M${x0.toFixed(0)} ${(y0 + H * .35).toFixed(0)}`;
    for (let n = 1; n <= 4; n++) { const y = y0 + H * .35 - n * H * .11, x = x0 + a * Math.sin(n * 1.3 + t * .6 + i); d += ` S${(x + a * .6).toFixed(0)} ${(y + H * .05).toFixed(0)} ${x.toFixed(0)} ${y.toFixed(0)}`; }
    const op = Math.sin(Math.PI * f) * (GRAVE ? .05 : .09);
    return `<path d="${d}" fill="none" stroke="${GRAVE ? INK : ORA}" stroke-width="${HOR ? 34 : 42}" stroke-linecap="round" opacity="${op.toFixed(3)}" filter="url(#hb)"/>`;
  }
  function fondo(k, t) {
    const mx = HOR ? W - 210 : W - 120, my = HOR ? H - 150 : H * .58, rot = -8 + 4 * Math.sin(t * .25);
    return `<defs><linearGradient id="gF" x1="0" y1="0" x2=".35" y2="1"><stop offset="0" stop-color="${BG2[0]}"/><stop offset="1" stop-color="${BG2[1]}"/></linearGradient>` +
      `<filter id="hb" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="${HOR ? 14 : 16}"/></filter>` +
      `<radialGradient id="gL"><stop offset="0" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient></defs>` +
      `<rect width="${W}" height="${H}" fill="url(#gF)"/>` + (GRAVE ? '' : `<rect width="${W}" height="${H}" fill="${['#ffffff', '#ffb59a', '#ffd36b'][k % 3]}" opacity="${[0, .12, .14][k % 3]}"/>`) +   // v64: tono distinto por escena
      `<circle cx="${(W * (.3 + .1 * Math.sin(t * .3 + k))).toFixed(1)}" cy="${(H * .3).toFixed(1)}" r="${Math.max(W, H) * .45}" fill="url(#gL)"/>` +
      // v86: manchas de luz de color que flotan despacio por el fondo (aurora cálida), más vivas en cada palabra clave
      (GRAVE ? '' : `<defs>${['#ff7a2f', '#ffc23d', '#ff6f91'].map((c, i) => `<radialGradient id="gA${i}"><stop offset="0" stop-color="${c}" stop-opacity=".55"/><stop offset=".6" stop-color="${c}" stop-opacity=".16"/><stop offset="1" stop-color="${c}" stop-opacity="0"/></radialGradient>`).join('')}</defs>` +
        [0, 1, 2].map(i => { const ph = i * 2.1 + k * .9, x = W * (.5 + .42 * Math.sin(t * (.11 + .03 * i) + ph)), y = H * (.45 + .38 * Math.cos(t * (.09 + .02 * i) + ph * 1.3)), r = Math.max(W, H) * (.38 + .06 * Math.sin(t * .4 + i));
          return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r.toFixed(1)}" fill="url(#gA${i})" opacity="${((i === 2 ? .45 : .7) * (1 + .5 * golpe(k, t))).toFixed(3)}"/>`; }).join('')) +
      [0, 1, 2].map(i => humo(i, t + k * 1.7)).join('') +
      // v60: partículas de humo que suben despacio (vida en el fondo)
      [...Array(HOR ? 14 : 12).keys()].map(i => { const sp = .035 + .02 * frac(i * .37), f = frac(t * sp + i * .618), x = W * frac(i * .414 + .13) + 30 * Math.sin(t * .7 + i), y = H * (1.05 - 1.1 * f), r = 4 + 9 * frac(i * .73);
        return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r.toFixed(1)}" fill="${GRAVE ? INK : (i % 3 ? '#fff' : ORA)}" opacity="${((GRAVE ? .05 : .22) * Math.sin(Math.PI * f)).toFixed(3)}"/>`; }).join('') +
      `<g opacity="${GRAVE ? .04 : .07}" transform="translate(${mx} ${my}) rotate(${rot.toFixed(2)})">${nube(0, 0, HOR ? 7 : 8)}</g>`;
  }
  function marco() {           // marco naranja de la marca (encima de todo, fino y redondeado)
    if (!HOR) return '';   // v67 (11-nov-2026): Pablo prefiere los cortos sin marco ni franjas negras, con el fondo hasta los bordes (como En Plata)
    const g = HOR ? 7 : 9, r = HOR ? 26 : 34;
    // v55 (11-nov-2026): TikTok, Instagram y YouTube amplían el corto para llenar los móviles alargados (19,5:9) y recortan ~9 % por
    // cada lado. El marco redondeado va DENTRO de la zona que siempre se ve (SX) y lo de fuera, en negro: en el iPhone las esquinas
    // redondeadas quedan justo en el borde de la pantalla; en móviles menos alargados se ve una franja negra fina, como un marco de tele.
    const x0 = SX, x1 = W - SX;
    const esq = HOR ? '' : `<path d="M0 0H${W}V${H}H0Z M${x0 + r} 0 H${x1 - r} A${r} ${r} 0 0 1 ${x1} ${r} V${H - r} A${r} ${r} 0 0 1 ${x1 - r} ${H} H${x0 + r} A${r} ${r} 0 0 1 ${x0} ${H - r} V${r} A${r} ${r} 0 0 1 ${x0 + r} 0 Z" fill="#000" fill-rule="evenodd"/>`;
    return esq + `<rect x="${x0 + g / 2}" y="${g / 2}" width="${x1 - x0 - g}" height="${H - g}" rx="${r}" fill="none" stroke="${GRAVE ? '#8a8378' : ORA}" stroke-width="${g}"/>`;
  }
  const rayos = (cx, cy, t, op) => { let d = ''; for (let i = 0; i < 12; i++) { const a0 = (i / 12) * Math.PI * 2 + t * .5, a1 = a0 + Math.PI / 12, R = Math.max(W, H) * 1.2; d += `M${cx} ${cy}L${(cx + R * Math.cos(a0)).toFixed(0)} ${(cy + R * Math.sin(a0)).toFixed(0)}L${(cx + R * Math.cos(a1)).toFixed(0)} ${(cy + R * Math.sin(a1)).toFixed(0)}Z`; } return `<path d="${d}" fill="${ORA}" opacity="${op.toFixed(3)}"/>`; };

  // ---------- foto real de cada escena ----------
  const FOTO = {};
  function fotoDe(k) {
    if (k in FOTO) return FOTO[k];
    const v = E[k].visual || {}; let r = null;
    if (v.tipo === 'foto' && v.foto) r = { ruta: v.foto, credito: v.credito || '', texto: v.texto || '', etiqueta: v.etiqueta || '' };
    else if (window.ESCENAS && typeof window.ESCENAS[k] === 'function') {
      try { const s = String((window.ESCENAS[k](2, A, 0) || {}).svg || ''), m = s.match(/href="file:\/\/([^"]+)"/); if (m) { const c = s.match(/>([^<>]*(?:CC |Commons|Wikimedia|Foto:)[^<>]*)</); r = { ruta: m[1], credito: c ? c[1] : '', texto: E[k].titulo || '', etiqueta: '' }; } } catch (e) { }
    }
    return (FOTO[k] = r);
  }

  // ---------- gráficos ----------
  const num = s => { const m = String(s == null ? '' : s).replace(/\./g, '').replace(',', '.').match(/-?\d+(?:\.\d+)?/); return m ? parseFloat(m[0]) : 0; };
  function contar(valor, p) {
    const m = String(valor).match(/^(\D*)([\d.]+)(?:,(\d+))?(.*)$/); if (!m || /[a-zA-Z]/.test(m[1])) return String(valor);
    const ent = parseInt(m[2].replace(/\./g, ''), 10), dec = m[3] ? m[3].length : 0, tot = ent + (m[3] ? parseInt(m[3], 10) / Math.pow(10, dec) : 0);
    const v = tot * eo(p), e = Math.floor(v + 1e-9), s = e.toString().replace(/\B(?=(\d{3})+(?!\d))/g, /\./.test(m[2]) ? '.' : '');
    return m[1] + s + (dec ? ',' + (v - e).toFixed(dec).slice(2) : '') + m[4];
  }
  // v80: iconos extra dibujados con emoji (Noto Color Emoji): más vocabulario para noticias variadas
  const ICO_EMO = { avion: '✈️', tren: '🚆', hospital: '🏥', escuela: '🏫', movil: '📱', fuego: '🔥', lluvia: '🌧️', nieve: '❄️', sol: '☀️', microfono: '🎤', tele: '📺', futbol: '⚽', urna: '🗳️', candado: '🔒', ordenador: '💻', barco: '🚢', camion: '🚚', medicina: '💊', virus: '🦠', trigo: '🌾', fabrica: '🏭', policia: '🚓', ambulancia: '🚑', bombero: '🚒', agua: '💧', terremoto: '🌋', arbol: '🌳', cohete: '🚀', robot: '🤖', grafica: '📈', bajada: '📉', bombilla: '💡', libro: '📚', maleta: '🧳', comida: '🍽️', gasolina: '⛽', llave: '🔑', regalo: '🎁', trofeo: '🏆', musica: '🎵', cine: '🎬' };
  // ---------- v91: EMOTICONOS PROPIOS de sin humo TV (vectoriales, con contorno, degradados y animados) ----------
  // Pablo: «en vez de emoticonos como los del WhatsApp, emoticonos más sofisticados y mejor hechos, todo animado».
  // Cada uno se dibuja en una caja de 100 x 100 centrada en (0, 0). emojiVec(caracter, tamaño, t) los pinta; los que no
  // están dibujados aquí y existen como icono vectorial del kit salen dentro de una pegatina redonda; el resto no se pinta.
  const EK = `stroke="${INK}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"`;
  const parp = (t, f = 0) => { const x = (t + f) % 2.8; return x < .12 ? .12 : 1; };   // parpadeo cada 2,8 s
  const EDEF = `<defs><radialGradient id="eF" cx=".38" cy=".3" r=".8"><stop offset="0" stop-color="#fff3a6"/><stop offset=".5" stop-color="#ffc93c"/><stop offset="1" stop-color="#ff9420"/></radialGradient>` +
    `<radialGradient id="eR" cx=".38" cy=".3" r=".8"><stop offset="0" stop-color="#ffb08a"/><stop offset=".5" stop-color="#ff5a3c"/><stop offset="1" stop-color="#d42a1e"/></radialGradient>` +
    `<linearGradient id="eL" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#e5372b"/><stop offset=".45" stop-color="#ff8a1f"/><stop offset="1" stop-color="#ffe14d"/></linearGradient>` +
    `<linearGradient id="eV" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7be3a2"/><stop offset="1" stop-color="#1f9d61"/></linearGradient>` +
    `<linearGradient id="eA" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9fd4ff"/><stop offset="1" stop-color="#2f62e6"/></linearGradient>` +
    `<linearGradient id="eO" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff07a"/><stop offset="1" stop-color="#ffb21a"/></linearGradient></defs>`;
  const cara = (fill = 'url(#eF)') => `<circle r="46" fill="${fill}" ${EK}/><ellipse cx="-17" cy="-25" rx="14" ry="7" fill="#fff" opacity=".5" transform="rotate(-30 -17 -25)"/>`;
  const ojo = (x, y, r, mx, my, b = 1) => `<g transform="translate(${x} ${y}) scale(1 ${b})"><ellipse rx="${r}" ry="${r * 1.15}" fill="#fff" ${EK} stroke-width="3"/><circle cx="${(mx * r * .45).toFixed(1)}" cy="${(my * r * .45).toFixed(1)}" r="${(r * .5).toFixed(1)}" fill="${INK}"/><circle cx="${(mx * r * .45 - r * .18).toFixed(1)}" cy="${(my * r * .45 - r * .2).toFixed(1)}" r="${(r * .16).toFixed(1)}" fill="#fff"/></g>`;
  const mejillas = `<ellipse cx="-27" cy="12" rx="8" ry="5" fill="#ff6f91" opacity=".45"/><ellipse cx="27" cy="12" rx="8" ry="5" fill="#ff6f91" opacity=".45"/>`;
  const gota = (x, y, s = 1, c = '#7cc8ff') => `<path transform="translate(${x} ${y}) scale(${s})" d="M0 -12 C6 -3 9 2 9 6 A9 9 0 0 1 -9 6 C-9 2 -6 -3 0 -12 Z" fill="${c}" ${EK} stroke-width="3"/><ellipse cx="${x - 3 * s}" cy="${y + 3 * s}" rx="${2 * s}" ry="${3 * s}" fill="#fff" opacity=".7"/>`;
  const EMV = {
    sorpresa: t => { const m = 12 + 3 * Math.sin(t * 9); return cara() + ojo(-16, -10, 11, 0, .1, parp(t)) + ojo(16, -10, 11, 0, .1, parp(t)) +
      `<path d="M-30 -30 Q-18 -40 -6 -32 M30 -30 Q18 -40 6 -32" fill="none" ${EK}/><ellipse cx="0" cy="22" rx="9" ry="${m.toFixed(1)}" fill="#7a1f2b" ${EK}/>` +
      `<ellipse cx="-38" cy="18" rx="9" ry="14" fill="url(#eF)" ${EK} transform="rotate(20 -38 18)"/><ellipse cx="38" cy="18" rx="9" ry="14" fill="url(#eF)" ${EK} transform="rotate(-20 38 18)"/>` + gota(30, -36 + 6 * ((t * 1.3) % 1), .9); },
    explota: t => { const p = 1 + .15 * Math.sin(t * 10), r = (t * 90) % 360;
      return `<g transform="translate(0 -40) rotate(${r.toFixed(0)}) scale(${p.toFixed(2)})"><path d="${[...Array(16).keys()].map(i => { const a = i * Math.PI / 8, R = i % 2 ? 16 : 34; return (i ? 'L' : 'M') + (Math.cos(a) * R).toFixed(1) + ' ' + (Math.sin(a) * R).toFixed(1); }).join(' ')}Z" fill="url(#eL)" ${EK}/></g>` +
        cara() + `<path d="M-42 -14 Q0 -30 42 -14" fill="none" ${EK}/>` + ojo(-16, 2, 10, Math.sin(t * 6), 0) + ojo(16, 2, 10, -Math.sin(t * 6), 0) + `<ellipse cx="0" cy="28" rx="11" ry="8" fill="#7a1f2b" ${EK}/>`; },
    mueca: t => cara() + ojo(-16, -10, 10, .3, 0, parp(t)) + ojo(16, -10, 10, .3, 0, parp(t)) + `<path d="M-30 -27 L-6 -22 M30 -27 L6 -22" ${EK}/>` +
      `<rect x="-26" y="10" width="52" height="22" rx="10" fill="#fff" ${EK}/><path d="M-26 21 H26 M-13 10 V32 M0 10 V32 M13 10 V32" ${EK} stroke-width="3"/>` + gota(34, -30, .8),
    piensa: t => { const ce = 3 * Math.sin(t * 2); return cara() + ojo(-16, -10, 10, .6, -.7, parp(t)) + ojo(16, -10, 10, .6, -.7, parp(t)) +
      `<path d="M-30 -26 Q-18 -30 -6 -26 M8 ${-32 - ce} Q20 ${-38 - ce} 30 ${-30 - ce}" fill="none" ${EK}/><path d="M-12 24 Q4 18 18 20" fill="none" ${EK}/>` +
      `<g transform="translate(${(18 + 2 * Math.sin(t * 3)).toFixed(1)} 38) rotate(-20)"><rect x="-14" y="-10" width="30" height="20" rx="10" fill="url(#eF)" ${EK}/><rect x="-4" y="-30" width="10" height="24" rx="5" fill="url(#eF)" ${EK}/></g>`; },
    enfado: t => { const v = (t * .9) % 1; return cara('url(#eR)') + `<path d="M-32 -30 L-6 -18 M32 -30 L6 -18" ${EK} stroke-width="5"/>` + ojo(-16, -6, 9, 0, 0) + ojo(16, -6, 9, 0, 0) + `<path d="M-18 30 Q0 16 18 30" fill="none" ${EK}/>` +
      [-1, 1].map(s => `<g opacity="${(1 - v).toFixed(2)}" transform="translate(${s * (40 + 18 * v)} ${-30 - 20 * v}) scale(${(.6 + .6 * v).toFixed(2)})"><circle r="9" fill="#fff" ${EK} stroke-width="3"/><circle cx="${s * 9}" cy="-6" r="7" fill="#fff" ${EK} stroke-width="3"/></g>`).join(''); },
    risa: t => { const b = Math.sin(t * 14); return `<g transform="rotate(${(8 * b).toFixed(1)})">` + cara() + `<path d="M-26 -12 Q-16 -24 -6 -12 M6 -12 Q16 -24 26 -12" fill="none" ${EK}/>` +
      `<path d="M-28 6 Q0 6 28 6 Q24 36 0 36 Q-24 36 -28 6 Z" fill="#7a1f2b" ${EK}/><path d="M-22 7 H22 V13 Q0 16 -22 13 Z" fill="#fff"/>` + gota(-40, -6 + 4 * b, .9) + gota(40, -6 - 4 * b, .9) + mejillas + `</g>`; },
    ojosblanco: t => `<g transform="rotate(${(-6 + 3 * Math.sin(t * 1.5)).toFixed(1)})">` + cara() + ojo(-16, -10, 11, .2 * Math.sin(t * 2), -1) + ojo(16, -10, 11, .2 * Math.sin(t * 2), -1) + `<path d="M-14 24 H14" ${EK}/></g>`,
    triste: t => { const c = (t * .8) % 1; return cara() + `<path d="M-30 -22 Q-20 -32 -8 -30 M30 -22 Q20 -32 8 -30" fill="none" ${EK}/>` + ojo(-16, -8, 10, 0, .4, parp(t)) + ojo(16, -8, 10, 0, .4, parp(t)) +
      `<path d="M-16 30 Q0 18 16 30" fill="none" ${EK}/>` + `<g opacity="${(1 - c * c).toFixed(2)}">${gota(-20, 6 + 34 * c, .9)}</g>`; },
    guino: t => cara() + ojo(-16, -10, 10, .2, 0, parp(t)) + `<path d="M8 -10 Q16 ${-16 + 3 * Math.sin(t * 6)} 26 -10" fill="none" ${EK}/><path d="M-20 16 Q0 34 20 16" fill="none" ${EK}/>` + mejillas,
    ojos: t => { const m = Math.sin(t * 2.2), b = parp(t); return ojo(-22, 0, 22, m, .1, b) + ojo(22, 0, 22, m, .1, b); },
    fuego: t => { const f = (a, s) => 1 + a * Math.sin(t * s); return `<g transform="translate(0 46)"><path transform="scale(${f(.05, 11).toFixed(3)} ${f(.1, 9).toFixed(3)})" d="M0 0 C-34 0 -42 -26 -30 -50 C-26 -38 -18 -36 -16 -42 C-20 -64 -6 -84 6 -96 C6 -78 22 -70 30 -54 C34 -62 34 -70 32 -76 C46 -60 44 -30 34 -14 C28 -4 16 0 0 0 Z" fill="url(#eL)" ${EK}/>` +
      `<path transform="scale(${f(.08, 13).toFixed(3)} ${f(.14, 10).toFixed(3)})" d="M0 -4 C-16 -4 -20 -18 -12 -32 C-8 -24 -2 -24 0 -30 C2 -44 10 -50 14 -54 C14 -42 22 -34 20 -20 C18 -10 10 -4 0 -4 Z" fill="#fff4a3"/></g>`; },
    dinero: t => { const w = 25 * Math.sin(t * 16), y = 4 * Math.sin(t * 4); return `<g transform="translate(0 ${y.toFixed(1)})">` + [-1, 1].map(s => `<g transform="translate(${s * 30} -6) rotate(${(s * (-20 + w)).toFixed(1)})"><path d="M0 0 C${s * 14} -24 ${s * 34} -26 ${s * 44} -18 C${s * 34} -10 ${s * 30} -2 ${s * 22} 2 C${s * 30} 6 ${s * 30} 10 ${s * 22} 12 Z" fill="#fff" ${EK} stroke-width="3"/></g>`).join('') +
      `<g transform="rotate(-8)"><rect x="-36" y="-20" width="72" height="42" rx="8" fill="url(#eV)" ${EK}/><rect x="-28" y="-13" width="56" height="28" rx="5" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="2.5"/><circle r="11" fill="#fff" ${EK} stroke-width="3"/><text y="6" font-family="Inter" font-weight="900" font-size="17" text-anchor="middle" fill="#1f9d61">€</text></g></g>`; },
    explosion: t => { const p = 1 + .1 * Math.sin(t * 12), st = (n, R, r) => [...Array(n * 2).keys()].map(i => { const a = i * Math.PI / n + .2, q = i % 2 ? r : R; return (i ? 'L' : 'M') + (Math.cos(a) * q).toFixed(1) + ' ' + (Math.sin(a) * q).toFixed(1); }).join(' ') + 'Z';
      return `<g transform="rotate(${(t * 20 % 360).toFixed(0)}) scale(${p.toFixed(3)})"><path d="${st(10, 48, 28)}" fill="#e5372b" ${EK}/><path d="${st(8, 32, 18)}" fill="#ffb21a"/><path d="${st(6, 18, 10)}" fill="#fff4a3"/></g>`; },
    alerta: t => { const g = .5 + .5 * Math.sin(t * 7); return `<circle r="${(44 + 6 * g).toFixed(1)}" fill="#ffc61a" opacity="${(.25 * g).toFixed(2)}"/><path d="M0 -40 L44 36 H-44 Z" fill="url(#eO)" ${EK} stroke-width="5"/><rect x="-5" y="-16" width="10" height="30" rx="5" fill="${INK}"/><circle cy="25" r="6" fill="${INK}"/>`; },
    rayo: t => `<circle r="${(36 + 8 * Math.abs(Math.sin(t * 10))).toFixed(1)}" fill="#ffe14d" opacity=".25"/><g transform="rotate(${(4 * Math.sin(t * 9)).toFixed(1)})"><path d="M8 -46 L-26 6 H-2 L-12 46 L26 -8 H2 Z" fill="#ffc61a" ${EK}/><path d="M4 -34 L-14 2" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".7"/></g>`,
    corazon: t => { const p = 1 + .12 * Math.max(0, Math.sin(t * 7)) ** 4; return `<g transform="scale(${p.toFixed(3)})"><path d="M0 40 C-40 12 -46 -6 -42 -20 C-38 -38 -14 -42 0 -22 C14 -42 38 -38 42 -20 C46 -6 40 12 0 40 Z" fill="url(#eR)" ${EK}/><ellipse cx="-20" cy="-20" rx="8" ry="5" fill="#fff" opacity=".55" transform="rotate(-35 -20 -20)"/></g>`; },
    brillo: t => [[0, 0, 40, 0], [-30, -28, 16, 1.3], [30, 26, 14, 2.1]].map(([x, y, r, f]) => { const p = .75 + .25 * Math.sin(t * 6 + f * 3); return `<path transform="translate(${x} ${y}) scale(${p.toFixed(3)}) rotate(${(t * 30 + f * 40) % 360})" d="M0 ${-r} Q${r * .16} ${-r * .16} ${r} 0 Q${r * .16} ${r * .16} 0 ${r} Q${-r * .16} ${r * .16} ${-r} 0 Q${-r * .16} ${-r * .16} 0 ${-r} Z" fill="url(#eO)" ${EK} stroke-width="3"/>`; }).join(''),
    aplauso: t => { const a = Math.abs(Math.sin(t * 9)), mano = sg => `<g transform="translate(${(sg * (4 + 10 * a)).toFixed(1)} 4) rotate(${(sg * (10 + 16 * a)).toFixed(1)})"><path d="M${sg * -2} 34 C${sg * -18} 34 ${sg * -20} 20 ${sg * -20} 6 V-26 A6 6 0 0 1 ${sg * -8} -26 V-6 V-34 A6 6 0 0 1 ${sg * 4} -34 V-6 V-30 A6 6 0 0 1 ${sg * 16} -30 V0 C${sg * 16} 20 ${sg * 12} 34 ${sg * -2} 34 Z" fill="url(#eF)" ${EK} stroke-width="3.5"/><path d="M${sg * 16} 4 C${sg * 26} -6 ${sg * 32} 2 ${sg * 24} 12 L${sg * 14} 22" fill="url(#eF)" ${EK} stroke-width="3.5"/></g>`;
      return mano(-1) + mano(1) + `<path d="M-40 -36 l-8 -8 M0 -50 V-60 M40 -36 l8 -8" ${EK} opacity="${(1 - a).toFixed(2)}"/>`; },
    check: t => `<g transform="scale(${(1 + .05 * Math.sin(t * 5)).toFixed(3)})"><rect x="-40" y="-40" width="80" height="80" rx="20" fill="url(#eV)" ${EK}/><path d="M-20 0 L-5 16 L22 -16" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/></g>`,
    cruz: t => `<g transform="rotate(${(5 * Math.sin(t * 6)).toFixed(1)})"><rect x="-40" y="-40" width="80" height="80" rx="20" fill="url(#eR)" ${EK}/><path d="M-18 -18 L18 18 M18 -18 L-18 18" stroke="#fff" stroke-width="10" stroke-linecap="round"/></g>`,
    pregunta: t => `<g transform="rotate(${(10 * Math.sin(t * 3)).toFixed(1)})"><text y="34" font-family="Inter" font-weight="900" font-size="104" text-anchor="middle" fill="url(#eR)" stroke="${INK}" stroke-width="5" paint-order="stroke" stroke-linejoin="round">?</text></g>`,
    exclama: t => `<g transform="scale(${(1 + .08 * Math.sin(t * 9)).toFixed(3)})"><text y="36" font-family="Inter" font-weight="900" font-size="104" text-anchor="middle" fill="url(#eR)" stroke="${INK}" stroke-width="5" paint-order="stroke" stroke-linejoin="round">!</text></g>`,
    sube: t => { const p = (t * .7) % 1.2, q = Math.min(1, p); return `<rect x="-42" y="-42" width="84" height="84" rx="18" fill="#fff" ${EK}/><path d="M-28 24 L-8 4 L6 14 L28 -16" fill="none" stroke="${VER}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="${(1 - q).toFixed(3)}"/>` + (q > .95 ? `<path d="M14 -18 L30 -18 L30 -2" fill="none" stroke="${VER}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>` : ''); },
    baja: t => { const p = (t * .7) % 1.2, q = Math.min(1, p); return `<rect x="-42" y="-42" width="84" height="84" rx="18" fill="#fff" ${EK}/><path d="M-28 -18 L-8 2 L6 -8 L28 22" fill="none" stroke="${ROJ}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="${(1 - q).toFixed(3)}"/>` + (q > .95 ? `<path d="M14 24 L30 24 L30 8" fill="none" stroke="${ROJ}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>` : ''); },
    megafono: t => { const o = (t * 1.5) % 1; return `<g transform="rotate(-15)"><path d="M-34 -10 H-18 L18 -34 V34 L-18 10 H-34 Z" fill="url(#eR)" ${EK}/><rect x="-28" y="8" width="12" height="22" rx="4" fill="#fff" ${EK} stroke-width="3"/>` +
      [0, 1].map(j => { const f = (o + j * .5) % 1; return `<path d="M${28 + 14 * f} -18 Q${40 + 18 * f} 0 ${28 + 14 * f} 18" fill="none" ${EK} opacity="${(1 - f).toFixed(2)}"/>`; }).join('') + `</g>`; },
    sol: t => `<g transform="rotate(${(t * 25 % 360).toFixed(0)})">${[...Array(10).keys()].map(i => `<path transform="rotate(${i * 36})" d="M0 -46 L7 -32 H-7 Z" fill="url(#eO)" ${EK} stroke-width="3"/>`).join('')}</g><circle r="26" fill="url(#eF)" ${EK}/>` + `<path d="M-10 4 Q0 12 10 4" fill="none" ${EK} stroke-width="3"/><circle cx="-9" cy="-6" r="3" fill="${INK}"/><circle cx="9" cy="-6" r="3" fill="${INK}"/>`,
    lluvia: t => [...Array(5).keys()].map(i => { const f = (t * 1.6 + i * .37) % 1; return `<path d="M${-28 + i * 14} ${10 + 34 * f} l-4 10" stroke="#2f62e6" stroke-width="5" stroke-linecap="round" opacity="${(1 - f).toFixed(2)}"/>`; }).join('') +
      `<path d="M-36 10 A16 16 0 0 1 -26 -18 A22 22 0 0 1 14 -24 A16 16 0 0 1 38 -4 A14 14 0 0 1 30 10 Z" fill="#fff" ${EK}/>`,
    nieve: t => `<g transform="rotate(${(t * 30 % 360).toFixed(0)})">${[0, 60, 120].map(a => `<g transform="rotate(${a})"><path d="M0 -42 V42 M-10 -32 L0 -22 L10 -32 M-10 32 L0 22 L10 32" fill="none" stroke="#2f62e6" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></g>`).join('')}</g><circle r="8" fill="#fff" ${EK} stroke-width="3"/>`,
    gota: t => `<g transform="scale(${(1 + .05 * Math.sin(t * 6)).toFixed(3)} ${(1 - .05 * Math.sin(t * 6)).toFixed(3)})"><path d="M0 -44 C18 -16 30 0 30 14 A30 30 0 0 1 -30 14 C-30 0 -18 -16 0 -44 Z" fill="url(#eA)" ${EK}/><ellipse cx="-12" cy="10" rx="6" ry="10" fill="#fff" opacity=".6"/></g>`,
    avion: t => `<g transform="translate(${(4 * Math.sin(t * 2)).toFixed(1)} ${(4 * Math.sin(t * 3)).toFixed(1)}) rotate(-30)">` + [...Array(3).keys()].map(i => { const f = (t * 1.5 + i / 3) % 1; return `<path d="M${-50 - 20 * f} ${-6 + i * 6} h-14" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity="${(1 - f).toFixed(2)}"/>`; }).join('') +
      `<path d="M-6 -6 L-20 -40 H-8 L14 -6 Z M-6 6 L-20 40 H-8 L14 6 Z M-40 -4 L-48 -18 H-40 L-30 -4 Z" fill="#cfd8e8" ${EK} stroke-width="3"/><path d="M-44 -7 H34 C44 -7 48 0 44 4 C40 8 34 7 34 7 H-44 Z" fill="#fff" ${EK} stroke-width="3.5"/><path d="M28 -4 h8" stroke="#2f62e6" stroke-width="4" stroke-linecap="round"/></g>`,
    tren: t => { const b = 1.5 * Math.sin(t * 18); return `<g transform="translate(0 ${b.toFixed(1)})"><rect x="-30" y="-40" width="60" height="66" rx="16" fill="url(#eR)" ${EK}/><rect x="-22" y="-30" width="44" height="22" rx="6" fill="#bfe3ff" ${EK} stroke-width="3"/><circle cx="-16" cy="10" r="5" fill="#ffe14d" ${EK} stroke-width="2.5"/><circle cx="16" cy="10" r="5" fill="#ffe14d" ${EK} stroke-width="2.5"/></g><path d="M-22 30 L-34 46 M22 30 L34 46 M-30 40 H30" ${EK}/>`; },
    hospital: t => `<rect x="-40" y="-30" width="80" height="70" rx="8" fill="#fff" ${EK}/><rect x="-14" y="16" width="28" height="24" fill="#bfe3ff" ${EK} stroke-width="3"/><g transform="translate(0 -10) scale(${(1 + .1 * Math.max(0, Math.sin(t * 6)) ** 3).toFixed(3)})"><path d="M-6 -18 H6 V-6 H18 V6 H6 V18 H-6 V6 H-18 V-6 H-6 Z" fill="#e5372b" ${EK} stroke-width="3"/></g>`,
    movil: t => `<g transform="rotate(${(8 * Math.sin(t * 20) * (Math.sin(t * 2) > .6 ? 1 : 0)).toFixed(1)})"><rect x="-24" y="-44" width="48" height="88" rx="12" fill="${INK}" ${EK}/><rect x="-18" y="-34" width="36" height="62" rx="4" fill="url(#eA)"/><circle cy="36" r="3.5" fill="#fff"/><rect x="-12" y="-26" width="24" height="10" rx="3" fill="#fff" opacity=".85"/><rect x="-12" y="-12" width="16" height="10" rx="3" fill="#fff" opacity=".6"/></g>`,
    policia: t => { const on = Math.sin(t * 12) > 0; return `<rect x="-14" y="-40" width="28" height="12" rx="6" fill="${on ? '#e5372b' : '#2f62e6'}" ${EK} stroke-width="3"/><circle cx="${on ? -30 : 30}" cy="-34" r="16" fill="${on ? '#e5372b' : '#2f62e6'}" opacity=".3"/><path d="M-44 14 V0 L-32 -22 H32 L44 0 V14 Z" fill="#fff" ${EK}/><path d="M-28 -18 H28 L36 0 H-36 Z" fill="#bfe3ff" ${EK} stroke-width="3"/><rect x="-44" y="2" width="88" height="8" fill="#2f62e6"/><circle cx="-26" cy="16" r="10" fill="${INK}"/><circle cx="26" cy="16" r="10" fill="${INK}"/>`; },
    urna: t => { const f = (t * .7) % 1; return `<g transform="translate(0 ${(-40 + 40 * Math.min(1, f * 1.6)).toFixed(1)})" opacity="${f < .62 ? 1 : 0}"><rect x="-12" y="-14" width="24" height="18" fill="#fff" ${EK} stroke-width="3"/></g><path d="M-38 -8 H38 V40 H-38 Z" fill="url(#eA)" ${EK}/><rect x="-40" y="-16" width="80" height="12" rx="3" fill="#fff" ${EK}/><rect x="-16" y="-12" width="32" height="4" rx="2" fill="${INK}"/>`; },
    candado: t => { const a = Math.max(0, Math.sin(t * 2.5)) * 10; return `<path d="M-20 -6 V-20 A20 20 0 0 1 20 -20 V${(-6 - a).toFixed(1)}" fill="none" ${EK} stroke-width="9" transform="translate(0 ${(-a).toFixed(1)})"/><path d="M-20 -6 V-20 A20 20 0 0 1 20 -20 V${(-6 - a).toFixed(1)}" fill="none" stroke="#cfc5b0" stroke-width="3" transform="translate(0 ${(-a).toFixed(1)})"/><rect x="-32" y="-8" width="64" height="50" rx="10" fill="url(#eO)" ${EK}/><circle cy="12" r="6" fill="${INK}"/><rect x="-2.5" y="14" width="5" height="12" rx="2" fill="${INK}"/>`; },
    trofeo: t => `<g transform="rotate(${(5 * Math.sin(t * 3)).toFixed(1)})"><path d="M-30 -34 C-48 -34 -46 -6 -24 -2 M30 -34 C48 -34 46 -6 24 -2" fill="none" ${EK} stroke-width="5"/><path d="M-30 -40 H30 V-14 C30 6 14 14 0 14 C-14 14 -30 6 -30 -14 Z" fill="url(#eO)" ${EK}/><rect x="-6" y="14" width="12" height="14" fill="#ffb21a" ${EK} stroke-width="3"/><rect x="-22" y="28" width="44" height="12" rx="3" fill="${INK}"/><path d="M-14 -32 V-16" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".6"/></g>`,
    fabrica: t => [0, 1].map(j => { const f = (t * .6 + j * .5) % 1; return `<circle cx="${22 + 8 * f}" cy="${-34 - 26 * f}" r="${(6 + 8 * f).toFixed(1)}" fill="#cfc5b0" opacity="${(1 - f).toFixed(2)}"/>`; }).join('') +
      `<rect x="14" y="-34" width="14" height="30" fill="#cfc5b0" ${EK} stroke-width="3"/><path d="M-42 40 V-4 L-20 -18 V-4 L2 -18 V-4 L24 -18 V-4 H42 V40 Z" fill="url(#eR)" ${EK}/><rect x="-32" y="8" width="12" height="12" fill="#ffe14d" ${EK} stroke-width="2.5"/><rect x="-6" y="8" width="12" height="12" fill="#ffe14d" ${EK} stroke-width="2.5"/><rect x="20" y="8" width="12" height="12" fill="#ffe14d" ${EK} stroke-width="2.5"/>`,
    futbol: t => { const y = -30 * Math.abs(Math.sin(t * 4)), pen = (cx, cy, r, a0) => 'M' + [...Array(5).keys()].map(i => { const a = a0 + i * 2 * Math.PI / 5; return (cx + r * Math.cos(a)).toFixed(1) + ' ' + (cy + r * Math.sin(a)).toFixed(1); }).join(' L') + 'Z';
      return `<ellipse cy="44" rx="${(26 + y * .3).toFixed(1)}" ry="5" fill="${INK}" opacity=".18"/><g transform="translate(0 ${(y + 4).toFixed(1)}) rotate(${(t * 200 % 360).toFixed(0)})"><defs><clipPath id="eB"><circle r="34"/></clipPath></defs><circle r="34" fill="#fff"/>` +
        `<g clip-path="url(#eB)"><path d="${pen(0, 0, 11, -Math.PI / 2)}" fill="${INK}"/>${[...Array(5).keys()].map(i => { const a = -Math.PI / 2 + i * 2 * Math.PI / 5 + Math.PI / 5; return `<path d="${pen(36 * Math.cos(a), 36 * Math.sin(a), 11, a)}" fill="${INK}"/><path d="M${(11 * Math.cos(a - Math.PI / 5)).toFixed(1)} ${(11 * Math.sin(a - Math.PI / 5)).toFixed(1)} L${(26 * Math.cos(a - Math.PI / 5)).toFixed(1)} ${(26 * Math.sin(a - Math.PI / 5)).toFixed(1)}" stroke="${INK}" stroke-width="2.5"/>`; }).join('')}</g><circle r="34" fill="none" ${EK}/></g>`; },
    microfono: t => { const o = (t * 1.4) % 1; return [0, 1].map(j => { const f = (o + j * .5) % 1; return `<path d="M${-34 - 10 * f} -24 Q${-44 - 14 * f} -8 ${-34 - 10 * f} 8 M${34 + 10 * f} -24 Q${44 + 14 * f} -8 ${34 + 10 * f} 8" fill="none" ${EK} stroke-width="3" opacity="${(1 - f).toFixed(2)}"/>`; }).join('') +
      `<rect x="-16" y="-44" width="32" height="50" rx="16" fill="#cfd8e8" ${EK}/><path d="M-16 -30 H16 M-16 -20 H16 M-16 -10 H16" stroke="${INK}" stroke-width="2" opacity=".4"/><path d="M-26 -8 C-26 18 26 18 26 -8 M0 16 V36 M-16 38 H16" fill="none" ${EK}/>`; },
    tele: t => `<rect x="-44" y="-30" width="88" height="62" rx="10" fill="${INK}" ${EK}/><rect x="-36" y="-22" width="72" height="46" rx="5" fill="url(#eA)"/>` + `<rect x="-36" y="${(-22 + 46 * ((t * .8) % 1)).toFixed(1)}" width="72" height="4" fill="#fff" opacity=".35"/><path d="M-14 -44 L0 -30 L14 -44" fill="none" ${EK}/><path d="M-10 0 L8 -10 V10 Z" fill="#fff"/>`,
    medicina: t => `<g transform="rotate(${(-35 + 8 * Math.sin(t * 2.5)).toFixed(1)})"><path d="M-36 -14 H0 V14 H-36 A14 14 0 0 1 -36 -14 Z" fill="#fff" ${EK}/><path d="M0 -14 H36 A14 14 0 0 1 36 14 H0 Z" fill="url(#eR)" ${EK}/><path d="M-30 -6 H-12" stroke="#fff" stroke-width="4" opacity=".0"/><path d="M8 -6 H26" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".6"/></g>`,
    virus: t => `<g transform="rotate(${(t * 25 % 360).toFixed(0)}) scale(${(1 + .05 * Math.sin(t * 5)).toFixed(3)})">${[...Array(8).keys()].map(i => `<g transform="rotate(${i * 45})"><path d="M0 -26 V-40" ${EK} stroke-width="4"/><circle cy="-42" r="6" fill="#ff6f91" ${EK} stroke-width="3"/></g>`).join('')}<circle r="28" fill="url(#eV)" ${EK}/><circle cx="-8" cy="-6" r="5" fill="#1f9d61"/><circle cx="9" cy="8" r="4" fill="#1f9d61"/></g>`,
    ordenador: t => `<rect x="-42" y="-36" width="84" height="56" rx="8" fill="${INK}" ${EK}/><rect x="-34" y="-28" width="68" height="40" rx="3" fill="url(#eA)"/>` + [0, 1, 2].map(i => `<rect x="-28" y="${-22 + i * 11}" width="${(20 + 30 * ((t * .9 + i * .3) % 1)).toFixed(1)}" height="5" rx="2" fill="#fff" opacity=".8"/>`).join('') + `<path d="M-50 30 H50 L42 40 H-42 Z" fill="#cfd8e8" ${EK}/>`,
    escuela: t => `<path d="M-42 40 V-6 L0 -34 L42 -6 V40 Z" fill="url(#eR)" ${EK}/><rect x="-12" y="14" width="24" height="26" fill="#fff" ${EK} stroke-width="3"/><circle cy="-8" r="10" fill="#fff" ${EK} stroke-width="3"/><path d="M0 -8 V-14 M0 -8 L${(5 * Math.cos(t * 2)).toFixed(1)} ${(-8 + 5 * Math.sin(t * 2)).toFixed(1)}" ${EK} stroke-width="2.5"/><path d="M0 -34 V-50 L16 -45 L0 -40" fill="#ffc61a" ${EK} stroke-width="3"/>`,
    llave: t => `<g transform="rotate(${(-40 + 20 * Math.sin(t * 2)).toFixed(1)})"><circle cx="-24" r="18" fill="url(#eO)" ${EK}/><circle cx="-24" r="6" fill="${BLA}" ${EK} stroke-width="3"/><path d="M-6 -6 H40 V6 H32 V16 H24 V6 H16 V14 H8 V6 H-6 Z" fill="url(#eO)" ${EK}/></g>`,
    gasolina: t => `<rect x="-34" y="-36" width="46" height="76" rx="8" fill="url(#eR)" ${EK}/><rect x="-26" y="-28" width="30" height="22" rx="4" fill="#fff" ${EK} stroke-width="3"/><text x="-11" y="-11" font-family="Inter" font-weight="900" font-size="12" text-anchor="middle" fill="${INK}">${(1.4 + .2 * ((t * .5) % 1)).toFixed(2).replace('.', ',')}</text><path d="M12 -20 H24 L34 -8 V22 A6 6 0 0 1 22 22 V8" fill="none" ${EK}/><rect x="-40" y="36" width="58" height="8" rx="3" fill="${INK}"/>`,
    barco: t => { const r = 5 * Math.sin(t * 2.2); return `<g transform="rotate(${r.toFixed(1)})"><path d="M-2 -40 V0 M-2 -40 L26 -8 H-2" fill="#fff" ${EK} stroke-width="3.5"/><path d="M-42 6 H42 L32 26 H-32 Z" fill="url(#eR)" ${EK}/><circle cx="-16" cy="14" r="3" fill="#fff"/><circle cx="0" cy="14" r="3" fill="#fff"/><circle cx="16" cy="14" r="3" fill="#fff"/></g>` +
      `<path d="M-48 ${(34 + 2 * Math.sin(t * 3)).toFixed(1)} q8 -6 16 0 t16 0 t16 0 t16 0 t16 0 t16 0" fill="none" stroke="#2f62e6" stroke-width="5" stroke-linecap="round"/>`; },
    camion: t => { const b = 1.5 * Math.sin(t * 16); return `<g transform="translate(0 ${b.toFixed(1)})"><rect x="-44" y="-26" width="56" height="40" rx="5" fill="url(#eA)" ${EK}/><path d="M12 -12 H30 L42 2 V14 H12 Z" fill="url(#eR)" ${EK}/><rect x="18" y="-6" width="12" height="8" rx="2" fill="#bfe3ff" ${EK} stroke-width="2.5"/></g>` +
      `<circle cx="-26" cy="18" r="9" fill="${INK}"/><circle cx="26" cy="18" r="9" fill="${INK}"/><circle cx="-26" cy="18" r="3" fill="#fff"/><circle cx="26" cy="18" r="3" fill="#fff"/>`; },
    ambulancia: t => { const on = Math.sin(t * 12) > 0; return `<rect x="-14" y="-38" width="16" height="10" rx="4" fill="${on ? '#e5372b' : '#2f62e6'}" ${EK} stroke-width="3"/><circle cx="-6" cy="-34" r="${on ? 16 : 0}" fill="#e5372b" opacity=".25"/><path d="M-44 16 V-28 H16 L42 -2 V16 Z" fill="#fff" ${EK}/><path d="M18 -22 L36 -4 H18 Z" fill="#bfe3ff" ${EK} stroke-width="3"/><path d="M-20 -18 H-10 V-8 H0 V2 H-10 V12 H-20 V2 H-30 V-8 H-20 Z" fill="#e5372b"/><circle cx="-26" cy="18" r="9" fill="${INK}"/><circle cx="26" cy="18" r="9" fill="${INK}"/>`; },
    bombero: t => { const on = Math.sin(t * 12) > 0; return `<rect x="-30" y="-36" width="14" height="9" rx="3" fill="${on ? '#ffc61a' : '#e5372b'}" ${EK} stroke-width="3"/><path d="M-44 16 V-26 H18 L42 -4 V16 Z" fill="url(#eR)" ${EK}/><path d="M-40 -32 L14 -42" stroke="#cfc5b0" stroke-width="6" stroke-linecap="round"/><path d="M-40 -32 L14 -42" stroke="${INK}" stroke-width="2" stroke-dasharray="2 6"/><path d="M20 -20 L36 -4 H20 Z" fill="#bfe3ff" ${EK} stroke-width="3"/><circle cx="-26" cy="18" r="9" fill="${INK}"/><circle cx="26" cy="18" r="9" fill="${INK}"/>`; },
    arbol: t => `<rect x="-7" y="10" width="14" height="32" rx="3" fill="#a0642d" ${EK}/><g transform="rotate(${(4 * Math.sin(t * 2)).toFixed(1)} 0 30)"><circle cx="-18" cy="-4" r="20" fill="url(#eV)" ${EK}/><circle cx="18" cy="-4" r="20" fill="url(#eV)" ${EK}/><circle cy="-26" r="24" fill="url(#eV)" ${EK}/><circle cx="-8" cy="-30" r="5" fill="#fff" opacity=".4"/></g>`,
    cohete: t => { const y = -6 * Math.abs(Math.sin(t * 3)); return `<g transform="translate(0 ${y.toFixed(1)}) rotate(35)"><path d="M-8 30 Q0 ${(54 + 8 * Math.sin(t * 20)).toFixed(1)} 8 30 Z" fill="url(#eL)" ${EK} stroke-width="3"/><path d="M-14 26 L-24 34 V16 L-14 6 Z M14 26 L24 34 V16 L14 6 Z" fill="url(#eR)" ${EK} stroke-width="3"/><path d="M0 -44 C18 -26 16 10 14 28 H-14 C-16 10 -18 -26 0 -44 Z" fill="#fff" ${EK}/><circle cy="-8" r="8" fill="#bfe3ff" ${EK} stroke-width="3"/></g>`; },
    robot: t => `<path d="M0 -36 V-46" ${EK}/><circle cy="-48" r="5" fill="${Math.sin(t * 8) > 0 ? '#e5372b' : '#ffc61a'}" ${EK} stroke-width="3"/><rect x="-32" y="-36" width="64" height="52" rx="14" fill="#cfd8e8" ${EK}/><rect x="-22" y="-24" width="44" height="22" rx="8" fill="${INK}"/><circle cx="-10" cy="-13" r="5" fill="#7be3a2" opacity="${parp(t)}"/><circle cx="10" cy="-13" r="5" fill="#7be3a2" opacity="${parp(t)}"/><path d="M-12 6 H12" stroke="${INK}" stroke-width="3" stroke-dasharray="3 3"/><rect x="-20" y="18" width="40" height="24" rx="6" fill="#cfd8e8" ${EK}/>`,
    libro: t => { const p = Math.sin(t * 3); return `<path d="M0 -26 C-16 -34 -32 -32 -42 -28 V30 C-32 26 -16 26 0 34 Z" fill="url(#eA)" ${EK}/><path d="M0 -26 C16 -34 32 -32 42 -28 V30 C32 26 16 26 0 34 Z" fill="url(#eA)" ${EK}/><path d="M0 -26 C10 -32 ${(20 - 20 * p).toFixed(1)} -32 ${(30 - 34 * p).toFixed(1)} -30 V26 C${(20 - 20 * p).toFixed(1)} 24 10 26 0 32 Z" fill="#fff" ${EK} stroke-width="3"/>`; },
    maleta: t => `<g transform="rotate(${(4 * Math.sin(t * 3)).toFixed(1)})"><path d="M-12 -30 V-38 H12 V-30" fill="none" ${EK}/><rect x="-38" y="-30" width="76" height="60" rx="10" fill="url(#eR)" ${EK}/><path d="M-18 -30 V30 M18 -30 V30" stroke="${INK}" stroke-width="3" opacity=".5"/><circle cx="-24" cy="36" r="5" fill="${INK}"/><circle cx="24" cy="36" r="5" fill="${INK}"/></g>`,
    regalo: t => { const a = Math.max(0, Math.sin(t * 3)) * 8; return `<rect x="-34" y="-8" width="68" height="46" rx="5" fill="url(#eR)" ${EK}/><g transform="translate(0 ${(-a).toFixed(1)})"><rect x="-40" y="-22" width="80" height="16" rx="4" fill="url(#eR)" ${EK}/><path d="M0 -22 C-10 -40 -30 -36 -20 -24 Z M0 -22 C10 -40 30 -36 20 -24 Z" fill="#ffc61a" ${EK} stroke-width="3"/></g><rect x="-6" y="-8" width="12" height="46" fill="#ffc61a"/>`; },
    musica: t => [0, 1].map(j => { const y = 4 * Math.sin(t * 4 + j * 2); return `<g transform="translate(${j ? 16 : -16} ${(y + (j ? -8 : 4)).toFixed(1)})"><ellipse cx="-6" cy="22" rx="12" ry="9" fill="${j ? '#2f62e6' : '#e5372b'}" ${EK} transform="rotate(-20 -6 22)"/><path d="M4 20 V-30 L22 -24" fill="none" ${EK}/></g>`; }).join(''),
    cine: t => `<g transform="translate(0 8)"><rect x="-38" y="-14" width="76" height="44" rx="5" fill="${INK}" ${EK}/><path d="M-30 -2 H30 M-30 10 H30" stroke="#fff" stroke-width="2" opacity=".3"/></g><g transform="translate(-38 -6) rotate(${(-20 * Math.max(0, Math.sin(t * 4))).toFixed(1)})"><rect x="0" y="-12" width="76" height="12" rx="3" fill="#fff" ${EK} stroke-width="3"/><path d="M12 -12 L20 0 M30 -12 L38 0 M48 -12 L56 0" stroke="${INK}" stroke-width="5"/></g>`,
    comida: t => `<ellipse cy="14" rx="44" ry="16" fill="#fff" ${EK}/><path d="M-30 10 C-30 -24 30 -24 30 10 Z" fill="#cfd8e8" ${EK}/><circle cy="-18" r="5" fill="#cfd8e8" ${EK} stroke-width="3"/>` + [0, 1].map(j => { const f = (t * .8 + j * .5) % 1; return `<path d="M${-8 + j * 16} ${-28 - 18 * f} q-4 -5 0 -10" fill="none" stroke="#cfc5b0" stroke-width="3" stroke-linecap="round" opacity="${(1 - f).toFixed(2)}"/>`; }).join(''),
    trigo: t => `<g transform="rotate(${(5 * Math.sin(t * 2)).toFixed(1)} 0 40)">` + [-14, 0, 14].map((x, j) => `<path d="M${x} 40 Q${x} 0 ${x + j * 2 - 2} -20" fill="none" stroke="#a0642d" stroke-width="3"/>` + [0, 1, 2, 3].map(i => `<ellipse cx="${x + j * 2 - 2 + (i % 2 ? 5 : -5)}" cy="${-34 + i * 9}" rx="5" ry="8" fill="url(#eO)" stroke="${INK}" stroke-width="2" transform="rotate(${i % 2 ? 25 : -25} ${x + j * 2 - 2 + (i % 2 ? 5 : -5)} ${-34 + i * 9})"/>`).join('')).join('') + `</g>`,
    volcan: t => [0, 1, 2].map(j => { const f = (t * .9 + j / 3) % 1; return `<circle cx="${(-10 + j * 10 + 10 * f * (j - 1)).toFixed(1)}" cy="${(-26 - 30 * f).toFixed(1)}" r="${(4 + 7 * f).toFixed(1)}" fill="#cfc5b0" opacity="${(1 - f).toFixed(2)}"/>`; }).join('') +
      `<path d="M-46 40 L-16 -22 H16 L46 40 Z" fill="#a0642d" ${EK}/><path d="M-16 -22 H16 L10 -6 L4 4 L-2 -8 L-8 2 Z" fill="url(#eL)" ${EK} stroke-width="3"/>`,
    bombilla: t => { const g = .5 + .5 * Math.sin(t * 5); return `<circle cy="-8" r="${(40 + 6 * g).toFixed(1)}" fill="#ffe14d" opacity="${(.3 * g).toFixed(2)}"/><path d="M-14 22 C-14 10 -30 2 -30 -14 A30 30 0 0 1 30 -14 C30 2 14 10 14 22 Z" fill="url(#eO)" ${EK}/><rect x="-14" y="22" width="28" height="16" rx="4" fill="#cfc5b0" ${EK} stroke-width="3"/><path d="M-6 6 L0 -6 L6 6" fill="none" stroke="#ff8a1f" stroke-width="3"/>`; },
  };
  const EMOJI_VEC = { '😱': 'sorpresa', '😮': 'sorpresa', '😲': 'sorpresa', '😳': 'sorpresa', '🤯': 'explota', '😬': 'mueca', '😅': 'mueca', '🤔': 'piensa', '🧐': 'piensa', '😡': 'enfado', '😠': 'enfado', '😤': 'enfado', '🤬': 'enfado',
    '😂': 'risa', '🤣': 'risa', '😆': 'risa', '😄': 'risa', '🙄': 'ojosblanco', '😒': 'ojosblanco', '😢': 'triste', '😥': 'triste', '😔': 'triste', '😭': 'triste', '😞': 'triste', '😉': 'guino', '😏': 'guino', '👀': 'ojos',
    '🔥': 'fuego', '💸': 'dinero', '💰': 'dinero', '💶': 'dinero', '💵': 'dinero', '🤑': 'dinero', '💥': 'explosion', '⚠': 'alerta', '🚨': 'alerta', '⚡': 'rayo', '❤': 'corazon', '💔': 'corazon', '👏': 'aplauso', '🙌': 'aplauso',
    '✨': 'brillo', '⭐': 'brillo', '🌟': 'brillo', '✅': 'check', '✔': 'check', '❌': 'cruz', '🚫': 'cruz', '❓': 'pregunta', '❔': 'pregunta', '❗': 'exclama', '‼': 'exclama', '📈': 'sube', '📉': 'baja', '📢': 'megafono', '📣': 'megafono',
    '☀': 'sol', '🌞': 'sol', '🌧': 'lluvia', '☔': 'lluvia', '🌦': 'lluvia', '⛈': 'lluvia', '❄': 'nieve', '🌨': 'nieve', '💧': 'gota', '🌊': 'gota', '💡': 'bombilla', '✈': 'avion', '🛫': 'avion', '🚆': 'tren', '🚄': 'tren', '🚇': 'tren', '🏥': 'hospital', '📱': 'movil', '🚓': 'policia', '👮': 'policia', '🗳': 'urna', '🔒': 'candado', '🔐': 'candado', '🏆': 'trofeo', '🏭': 'fabrica', '⚽': 'futbol', '🎤': 'microfono', '🎙': 'microfono', '📺': 'tele', '💊': 'medicina', '🦠': 'virus', '💻': 'ordenador', '🏫': 'escuela', '🔑': 'llave', '⛽': 'gasolina', '🚢': 'barco', '⛴': 'barco', '🚚': 'camion', '🚛': 'camion', '🚑': 'ambulancia', '🚒': 'bombero', '🌳': 'arbol', '🌲': 'arbol', '🚀': 'cohete', '🤖': 'robot', '📚': 'libro', '📖': 'libro', '🧳': 'maleta', '🎁': 'regalo', '🎵': 'musica', '🎶': 'musica', '🎬': 'cine', '🍽': 'comida', '🌾': 'trigo', '🌋': 'volcan' };
  // emojis que ya existen como icono vectorial del kit (motor_v.js): salen en una pegatina redonda
  const EMOJI_ICO = { '🏠': 'casa', '🏡': 'casa', '🏘': 'casa', '⚖': 'balanza', '🚗': 'coche', '🚙': 'coche', '🏢': 'edificio', '🏬': 'edificio', '🏦': 'banco', '🏛': 'banco', '📄': 'documento', '📝': 'documento', '📰': 'documento', '📋': 'documento',
    '📍': 'pin', '🛡': 'escudo', '⏰': 'reloj', '⏱': 'reloj', '🕒': 'reloj', '⌛': 'reloj', '📅': 'calendario', '🗓': 'calendario', '🌡': 'termometro', '🌍': 'globo', '🌎': 'globo', '🌐': 'globo', '👑': 'corona', '🏅': 'medalla', '🥇': 'medalla',
    '🔨': 'mazo', '🕊': 'paloma', '🛒': 'carrito', '🪙': 'moneda', '💳': 'cartera', '👛': 'cartera', '🕯': 'vela', '🛢': 'barril', '👤': 'persona', '🧑': 'persona' };
  const emojiClave = ch => String(ch || '').replace(/[️‍]/g, '').trim();
  const tieneEmoji = ch => { const c = emojiClave(ch); return !!(EMOJI_VEC[c] || EMOJI_ICO[c]); };
  function emojiVec(ch, size, t) {
    const c = emojiClave(ch), n = EMOJI_VEC[c], k = size / 100;
    if (n) return `<g transform="scale(${k.toFixed(3)})">${EDEF}${EMV[n](t)}</g>`;
    const ic = EMOJI_ICO[c]; if (!ic) return '';
    return `<g transform="scale(${k.toFixed(3)})"><circle r="46" fill="${BLA}" ${EK}/><g transform="scale(${['balanza', 'mazo', 'paloma', 'globo'].includes(ic) ? .26 : .32})">${icono(ic, 0, 0, 1.1, t)}</g></g>`;
  }
  const ICO_VEC = { fuego: 'fuego', lluvia: 'lluvia', nieve: 'nieve', sol: 'sol', agua: 'gota', grafica: 'sube', bajada: 'baja', bombilla: 'bombilla', avion: 'avion', tren: 'tren', hospital: 'hospital', movil: 'movil', policia: 'policia', urna: 'urna', candado: 'candado', trofeo: 'trofeo', fabrica: 'fabrica', futbol: 'futbol', microfono: 'microfono', tele: 'tele', medicina: 'medicina', virus: 'virus', ordenador: 'ordenador', escuela: 'escuela', llave: 'llave', gasolina: 'gasolina', barco: 'barco', camion: 'camion', ambulancia: 'ambulancia', bombero: 'bombero', arbol: 'arbol', cohete: 'cohete', robot: 'robot', libro: 'libro', maleta: 'maleta', regalo: 'regalo', musica: 'musica', cine: 'cine', comida: 'comida', trigo: 'trigo', terremoto: 'volcan' };   // v91: estos iconos, con el dibujo propio
  const iconoX = (n, x, y, s, L, c) => ICO_VEC[n] ? `<g transform="translate(${x} ${y}) scale(${(1.9 * s).toFixed(3)})">${EDEF}${EMV[ICO_VEC[n]](L)}</g>` : ICO_EMO[n] ? `<text x="${x}" y="${y + 62 * s}" font-family="Noto Color Emoji" font-size="${(175 * s).toFixed(0)}" text-anchor="middle">${ICO_EMO[n]}</text>` : icono(n, x, y, s, L, c);
  const sticker = (x, y, r, L, t0, nombre, c) => { const e = back((L - t0) / .4); return e <= 0 ? '' : `<g transform="translate(${x} ${y}) rotate(${(-6 + 3 * Math.sin(L * 1.4)).toFixed(2)}) scale(${e.toFixed(3)})"><circle cx="0" cy="${SOM * 1.3}" r="${r}" fill="${INK}" opacity=".2" filter="url(#somS)"/><circle cx="0" cy="0" r="${r}" fill="${BLA}" stroke="${INK}" stroke-width="3"/><g transform="scale(${(r / 150).toFixed(3)})">${iconoX(nombre, 0, 0, 1.25, L, c)}</g></g>`; };
  // ---------- v56: datos del mapa de España (contorno simplificado, lon/lat) ----------
  const ESP = [[-8.9, 43.2], [-8.3, 43.55], [-7.7, 43.75], [-7.0, 43.55], [-5.8, 43.65], [-4.5, 43.42], [-3.8, 43.48], [-3.0, 43.35], [-1.8, 43.38],
    [-1.4, 43.05], [-0.7, 42.85], [0.7, 42.82], [1.5, 42.45], [2.6, 42.35], [3.2, 42.32], [3.15, 41.9], [2.2, 41.4], [1.0, 41.05], [0.85, 40.7],
    [0.0, 40.0], [-0.3, 39.45], [0.2, 38.75], [-0.5, 38.3], [-0.75, 37.62], [-1.6, 37.25], [-2.1, 36.75], [-3.5, 36.72], [-4.45, 36.68],
    [-5.3, 36.18], [-5.62, 36.0], [-6.25, 36.45], [-6.45, 36.85], [-7.4, 37.18], [-7.5, 37.6], [-7.05, 38.2], [-7.3, 38.8], [-7.0, 39.25],
    [-7.5, 39.7], [-6.9, 40.25], [-6.8, 41.0], [-6.2, 41.6], [-6.6, 41.95], [-7.2, 41.88], [-8.1, 41.85], [-8.85, 41.9], [-8.9, 42.4], [-9.3, 42.9], [-9.2, 43.15]];
  const BAL = [[2.95, 39.62, .45, .28], [4.05, 39.97, .2, .1], [1.42, 38.98, .14, .12]];   // Mallorca, Menorca, Ibiza (lon, lat, radio x, radio y en grados)
  const norm = s => String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z ]/g, '').trim();
  const CIUDADES = {
    'madrid': [-3.7, 40.42], 'barcelona': [2.17, 41.39], 'valencia': [-0.38, 39.47], 'sevilla': [-5.98, 37.39], 'zaragoza': [-0.88, 41.65], 'malaga': [-4.42, 36.72],
    'murcia': [-1.13, 37.99], 'cartagena': [-0.98, 37.6], 'bilbao': [-2.93, 43.26], 'oviedo': [-5.85, 43.36], 'gijon': [-5.66, 43.54], 'toledo': [-4.02, 39.86],
    'valladolid': [-4.72, 41.65], 'a coruna': [-8.4, 43.37], 'la coruna': [-8.4, 43.37], 'santiago de compostela': [-8.54, 42.88], 'santiago': [-8.54, 42.88],
    'vigo': [-8.72, 42.24], 'granada': [-3.6, 37.18], 'cordoba': [-4.78, 37.89], 'alicante': [-0.48, 38.35], 'elche': [-0.7, 38.27], 'palma': [2.65, 39.57],
    'palma de mallorca': [2.65, 39.57], 'mallorca': [2.95, 39.62], 'ibiza': [1.42, 38.98], 'menorca': [4.05, 39.97], 'pamplona': [-1.64, 42.81],
    'san sebastian': [-1.98, 43.32], 'donostia': [-1.98, 43.32], 'santander': [-3.8, 43.46], 'salamanca': [-5.66, 40.96], 'cadiz': [-6.29, 36.53],
    'jerez': [-6.14, 36.69], 'huelva': [-6.95, 37.26], 'almeria': [-2.46, 36.84], 'badajoz': [-6.97, 38.88], 'caceres': [-6.37, 39.47], 'merida': [-6.34, 38.92],
    'logrono': [-2.45, 42.47], 'vitoria': [-2.67, 42.85], 'leon': [-5.57, 42.6], 'burgos': [-3.7, 42.34], 'zamora': [-5.75, 41.5], 'avila': [-4.7, 40.66],
    'segovia': [-4.12, 40.95], 'soria': [-2.47, 41.76], 'palencia': [-4.53, 42.01], 'guadalajara': [-3.17, 40.63], 'cuenca': [-2.13, 40.07],
    'ciudad real': [-3.93, 38.98], 'albacete': [-1.86, 38.99], 'jaen': [-3.79, 37.77], 'lugo': [-7.56, 43.01], 'ourense': [-7.86, 42.34],
    'pontevedra': [-8.65, 42.43], 'huesca': [-0.41, 42.14], 'teruel': [-1.11, 40.34], 'lleida': [0.62, 41.62], 'lerida': [0.62, 41.62],
    'girona': [2.82, 41.98], 'gerona': [2.82, 41.98], 'tarragona': [1.25, 41.12], 'castellon': [-0.05, 39.99], 'benidorm': [-0.13, 38.54],
    'lorca': [-1.7, 37.68], 'marbella': [-4.88, 36.51], 'algeciras': [-5.45, 36.13], 'ceuta': [-5.32, 35.89], 'melilla': [-2.94, 35.29],
    'urda': [-3.71, 39.41], 'talavera': [-4.83, 39.96], 'ponferrada': [-6.6, 42.55], 'aviles': [-5.92, 43.56], 'reus': [1.1, 41.15], 'sabadell': [2.11, 41.55],
    'terrassa': [2.01, 41.56], 'mostoles': [-3.86, 40.32], 'alcala de henares': [-3.36, 40.48], 'getafe': [-3.73, 40.31], 'leganes': [-3.76, 40.33],
    'fuenlabrada': [-3.8, 40.28], 'torrejon': [-3.48, 40.46], 'cordoba ': [-4.78, 37.89], 'galicia': [-8.0, 42.8], 'asturias': [-5.9, 43.3],
    'cantabria': [-4.0, 43.2], 'pais vasco': [-2.6, 43.05], 'euskadi': [-2.6, 43.05], 'navarra': [-1.65, 42.7], 'la rioja': [-2.5, 42.3], 'aragon': [-0.7, 41.5],
    'cataluna': [1.5, 41.8], 'catalunya': [1.5, 41.8], 'comunidad valenciana': [-0.6, 39.3], 'region de murcia': [-1.4, 38.0], 'andalucia': [-4.6, 37.4],
    // Canarias: se dibujan en un recuadro (como en los mapas del tiempo); coordenadas reales, el recuadro las traslada
    'canarias': [-15.6, 28.3], 'islas canarias': [-15.6, 28.3], 'tenerife': [-16.55, 28.3], 'santa cruz de tenerife': [-16.25, 28.47], 'gran canaria': [-15.6, 27.95],
    'las palmas': [-15.43, 28.12], 'las palmas de gran canaria': [-15.43, 28.12], 'la palma': [-17.85, 28.68], 'lanzarote': [-13.6, 29.05], 'fuerteventura': [-14.0, 28.4],
    'la gomera': [-17.2, 28.1], 'el hierro': [-18.0, 27.75], 'la graciosa': [-13.5, 29.25], 'arrecife': [-13.55, 28.96],
    'extremadura': [-6.2, 39.2], 'castilla la mancha': [-3.0, 39.5], 'castilla y leon': [-4.6, 41.7], 'comunidad de madrid': [-3.7, 40.45], 'baleares': [2.95, 39.62],
  };
  const G = {
    cifra(v, L, d) {
      const c = col(v.color), s = String(v.valor || ''), size = Math.min(HOR ? 210 : 150, Z.w * .94 / (Math.max(3, s.length) * .6)), p = cl(L / Math.min(1, d * .45));   // v48: en la escena 1 la cifra ya está completa en el fotograma 0
      const yN = ZC.y + (HOR ? 30 : (v.icono ? 70 : 10)), ent = back(L / .4), lab = partir(v.texto || '', HOR ? 36 : 26), wS = size * Math.max(3, s.length) * .58;
      const tB = Math.min(1, d * .45), xb = L - tB, est = xb > 0 && xb < .55 && !GRAVE ? [...Array(12).keys()].map(i => { const a = i / 12 * Math.PI * 2 + .2, r0 = wS * .5 + 10 + 60 * eo(xb / .55), r1 = r0 + 40 * (1 - xb / .55);
        return `<path d="M${(ZC.x + r0 * Math.cos(a)).toFixed(1)} ${(yN - size * .3 + r0 * .45 * Math.sin(a)).toFixed(1)} L${(ZC.x + r1 * Math.cos(a)).toFixed(1)} ${(yN - size * .3 + r1 * .45 * Math.sin(a)).toFixed(1)}" stroke="${INK}" stroke-width="4" stroke-linecap="round" opacity="${(1 - xb / .55).toFixed(2)}"/>`; }).join('') : '';   // v64: estallido al aterrizar
      return est + `<rect x="${(ZC.x - wS / 2 * eo((L - .15) / .4)).toFixed(1)}" y="${(yN - size * .3).toFixed(1)}" width="${(wS * eo((L - .15) / .4)).toFixed(1)}" height="${(size * .36).toFixed(1)}" rx="${size * .06}" fill="${c === INK ? ORO : c}" opacity=".9" transform="rotate(-1.5 ${ZC.x} ${yN})"/>` +
        `<g transform="translate(${ZC.x} ${yN}) scale(${ent.toFixed(3)}) translate(${-ZC.x} ${-yN})">${tx(ZC.x, yN, esc(contar(s, p)), size, INK, 'middle', 900, 'letter-spacing="-4"')}</g>` +
        lab.map((l, i) => tx(ZC.x, yN + (HOR ? 74 : 70) + i * (HOR ? 50 : 44), esc(l), HOR ? 42 : 36, INK, 'middle', 800, `opacity="${eo((L - .45 - i * .1) / .3).toFixed(2)}"`)).join('') +
        (v.icono ? (HOR ? sticker(Z.x + 30, Z.y + 40, 54, L, .25, v.icono, c) : `<g transform="translate(0 ${(4 * Math.sin(L * 2.2)).toFixed(1)})">${sticker(ZC.x, yN - size * .62 - 118, 74, L, 0, v.icono, c)}</g>`) : '');
    },
    comparar(v, L, d) {
      const a = v.a || {}, b = v.b || {}, na = num(a.valor), nb = num(b.valor), mx = Math.max(Math.abs(na), Math.abs(nb), 1e-9), ah = HOR ? 78 : 76, x0 = Z.x + (HOR ? 140 : 14), wM = Z.w - (HOR ? 280 : 28);
      if (!na && !nb) {   // v50: sin cifras («Moderación ok» → «Fallos graves»): dos tarjetas con texto y flecha entre ellas
        const wC = HOR ? Z.w * .4 : Z.w - 20, fs = HOR ? 40 : 34, tarjeta = (o, x, y, c, t0) => {
          const e = back((L - t0) / .4), ls = partir(String(o.valor || ''), HOR ? 18 : 24), hC = 70 + ls.length * fs * 1.15, cx = x + wC / 2, cy = y + hC / 2;
          return L < t0 ? '' : `<g transform="translate(${cx} ${cy}) scale(${e.toFixed(3)}) translate(${-cx} ${-cy})">` + caja(x, y, wC, hC, 22, c, 5) +
            peg(x + 24, y + 2, String(o.etiqueta || '').toUpperCase(), HOR ? 22 : 20, INK, '#fff', 'start', 1, -3) +
            ls.map((l, i) => tx(cx, y + 58 + fs * .8 + i * fs * 1.15, esc(l), fs, c === ORA ? '#fff' : INK, 'middle', 900)).join('') + `</g>`;
        };
        if (HOR) return tarjeta(a, Z.x + 40, ZC.y - 80, BLA, .15) + tx(ZC.x, ZC.y + 20, '→', 90, ORA, 'middle', 900, `opacity="${cl((L - .5) / .2)}"`) + tarjeta(b, Z.x + Z.w - 40 - wC, ZC.y - 80, ORA, .6);
        const x = ZC.x - wC / 2;
        return tarjeta(a, x, Z.y + 40, BLA, .15) + `<g opacity="${cl((L - .45) / .2).toFixed(2)}" transform="translate(${ZC.x} ${Z.y + 250}) rotate(90)">${tx(0, 26, '→', 80, ORA, 'middle', 900)}</g>` + tarjeta(b, x, Z.y + 310, ORA, .6);
      }
      const fila = (o, n, y, c, t0) => {
        const p = eo((L - t0) / .9), w = Math.max(ah * 1.1, wM * (Math.abs(n) / mx) * p), op = cl((L - t0) / .15);
        return `<g opacity="${op}">` + tx(x0, y - 16, esc(o.etiqueta || ''), HOR ? 34 : 32, INK, 'start', 900) + caja(x0, y, w, ah, ah * .28, c) +
          (w > wM * .5 ? tx(x0 + w - 22, y + ah * .7, esc(contar(String(o.valor || ''), p)), ah * .58, c === ORA || c === 'url(#gC1)' ? '#fff' : INK, 'end') : tx(x0 + w + 26, y + ah * .7, esc(contar(String(o.valor || ''), p)), ah * .58, INK, 'start')) + `</g>`;
      };
      let dif = '';   // v45: pastilla con la diferencia (+92 %, ×3…) cuando las dos cifras son comparables
      const tiempo = /\b(1[89]|20)\d\d\b|antes|ahora|hoy|ayer|año|mes|semana|actual|anterior|nuev|viej|pasad/i.test(String(a.etiqueta || '') + ' ' + String(b.etiqueta || ''));   // v53: solo si es un antes/después
      if (tiempo && na > 0 && nb > 0 && na !== nb && !/%/.test(String(a.valor) + String(b.valor))) {
        const r = nb / na, pc = Math.round((r - 1) * 100);
        const et = r >= 2.95 ? '×' + (Math.round(r * 10) / 10).toString().replace('.', ',') : (pc > 0 ? '+' : '') + pc + ' %';
        const t0 = 1.3, e2 = back((L - t0) / .4);
        if (L > t0 && Math.abs(pc) >= 3) dif = peg(HOR ? Z.x + Z.w - 120 : Z.x + Z.w - 92, HOR ? ZC.y + 10 : ZC.y + 8, et, HOR ? 36 : 34, pc > 0 ? ROJ : VER, '#fff', 'middle', 1, -6, e2);
      }
      const gd = `<defs><linearGradient id="gC0" x1="0" x2="1"><stop offset="0" stop-color="#f3c79b"/><stop offset="1" stop-color="#ffe2c2"/></linearGradient><linearGradient id="gC1" x1="0" x2="1"><stop offset="0" stop-color="${ORA}"/><stop offset="1" stop-color="#ff9a3d"/></linearGradient></defs>`;   // v89: barras con degradado
      return gd + fila(a, na, ZC.y - ah - (HOR ? 34 : 70), 'url(#gC0)', .15) + fila(b, nb, ZC.y + (HOR ? 62 : 86), 'url(#gC1)', .6) + dif;
    },
    grafico(v, L, d) {
      const vs = (v.valores || []).slice(0, 7), et = v.etiquetas || [], n = vs.length || 1, mx = Math.max(...vs.map(x => Math.abs(num(x))), 1e-9), base = Z.y + Z.h - (HOR ? 50 : 66), alto = Z.h - (HOR ? 160 : 220);
      const paso = Math.min(HOR ? 190 : 150, Z.w / n), an = paso * .6, x0 = ZC.x - paso * n / 2 + (paso - an) / 2;
      let o = v.titulo ? cinetico(v.titulo, ZC.x, Z.y + (HOR ? 36 : 40), HOR ? 40 : 34, L, { max: HOR ? 46 : 30 }) : '';
      o += [1, 2, 3].map(i => `<path d="M${Z.x} ${base - alto * i / 3} H${Z.x + Z.w}" stroke="${INK}" stroke-opacity=".16" stroke-width="3" stroke-dasharray="4 12"/>`).join('');
      // v89: barras con degradado y brillo (antes, beis plano); la destacada en naranja intenso
      o += `<defs><linearGradient id="gB0" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe2c2"/><stop offset="1" stop-color="#f3c79b"/></linearGradient><linearGradient id="gB1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ff9a3d"/><stop offset="1" stop-color="${ORA}"/></linearGradient></defs>`;
      vs.forEach((x, i) => {
        const t0 = .25 + i * Math.min(.35, d * .5 / n), p = back((L - t0) / .7), h = Math.max(12, alto * Math.abs(num(x)) / mx * p), xx = x0 + i * paso, ult = i === n - 1, op = cl((L - t0) / .12);
        o += `<g opacity="${op}">` + caja(xx, base - h, an, h, Math.min(14, an * .16), ult ? 'url(#gB1)' : 'url(#gB0)') +
          `<rect x="${(xx + an * .14).toFixed(1)}" y="${(base - h + 8).toFixed(1)}" width="${(an * .14).toFixed(1)}" height="${Math.max(0, h - 16).toFixed(1)}" rx="${(an * .07).toFixed(1)}" fill="#fff" opacity=".35"/>` +
          tx(xx + an / 2, base - h - 16, esc(contar(String(x), cl((L - t0) / .7))), Math.min(HOR ? 40 : 32, an * .45), INK) +
          tx(xx + an / 2, base + (HOR ? 42 : 48), esc(et[i] || ''), Math.min(HOR ? 28 : 24, paso * .3), INK, 'middle', 800) + `</g>`;
      });
      // v65: destello en la barra más alta cuando termina de subir
      const im = vs.reduce((b, x, i) => Math.abs(num(x)) > Math.abs(num(vs[b])) ? i : b, 0), tM = .25 + im * Math.min(.35, d * .5 / n) + .7, xs = L - tM;
      if (xs > 0 && xs < .7 && vs.length) { const cxs = x0 + im * paso + an / 2, cys = base - Math.max(12, alto * Math.abs(num(vs[im])) / mx) - 56, r = 18 + 40 * eo(xs / .7);
        o += [...Array(8).keys()].map(i => { const a = i * Math.PI / 4; return `<path d="M${(cxs + r * .5 * Math.cos(a)).toFixed(1)} ${(cys + r * .5 * Math.sin(a)).toFixed(1)} L${(cxs + r * Math.cos(a)).toFixed(1)} ${(cys + r * Math.sin(a)).toFixed(1)}" stroke="${ORO}" stroke-width="6" stroke-linecap="round" opacity="${(1 - xs / .7).toFixed(2)}"/>`; }).join(''); }
      return o + `<path d="M${Z.x} ${base} H${Z.x + Z.w}" stroke="${INK}" stroke-width="4" stroke-linecap="round"/>`;
    },
    lista(v, L, d, k) {
      const it = (v.items || []).slice(0, 4), T0 = entradas(k, it.map(String), d), n = it.length || 1, c = col(v.color), hT = v.titulo ? (HOR ? 74 : 84) : 0, ah = Math.min(HOR ? 80 : 80, (Z.h - hT - 10) / n - 18), y0 = Z.y + hT + (Z.h - hT - n * (ah + 18)) / 2;
      const act = Math.max(0, T0.filter(x => L >= x).length - 1);
      let o = v.titulo ? cinetico(v.titulo, HOR ? Z.x + 20 : ZC.x, Z.y + (HOR ? 46 : 62), HOR ? 46 : 38, L, { max: HOR ? 48 : 28, anchor: HOR ? 'start' : 'middle' }) : '';
      it.forEach((s, i) => {
        const t0 = T0[i], e = back((L - t0) / .4);
        if (L < t0 + .12) o += hueco(Z.x + 8, y0 + i * (ah + 18), Z.w - 24, ah, ah * .26, i + 1, L);
        if (L < t0) return;
        const y = y0 + i * (ah + 18), on = i === act, fs = Math.min(ah * .4, (Z.w - 160) / (Math.max(8, [...String(s)].length) * .56));
        o += `<g transform="translate(${((1 - e) * (i % 2 ? -1 : 1) * 300).toFixed(1)} 0) rotate(${on ? -1 : 0} ${ZC.x} ${y + ah / 2})" opacity="${cl((L - t0) / .12)}">` + caja(Z.x + 8, y, Z.w - 24, ah, ah * .26, on ? c : BLA) +
          `<circle cx="${Z.x + 8 + ah * .5}" cy="${y + ah / 2}" r="${ah * .3}" fill="${on ? '#fff' : c}" stroke="${INK}" stroke-width="2.5"/>` + tx(Z.x + 8 + ah * .5, y + ah / 2 + ah * .13, String(i + 1), ah * .36, on ? c : '#fff') +
          tx(Z.x + 8 + ah * 1.05, y + ah / 2 + fs * .36, esc(s), fs, on && c !== ORO ? '#fff' : INK, 'start', 800) + `</g>`;
      });
      return o;
    },
    frase(v, L, d) {
      const size = HOR ? 48 : 40, max = HOR ? 38 : 24, alto = altoCin(v.texto, size, max), hC = alto + (HOR ? 110 : 150), wC = HOR ? Z.w - 160 : Z.w - 16, x = ZC.x - wC / 2, y = ZC.y - hC / 2, e = back(L / .4);
      return `<g transform="translate(${ZC.x} ${ZC.y}) scale(${e.toFixed(3)}) rotate(-1) translate(${-ZC.x} ${-ZC.y})">` + caja(x, y, wC, hC, 26, BLA, 6, SOM + 3) +
        `<text x="${x + 22}" y="${y + (HOR ? 96 : 112)}" font-family="Georgia, serif" font-weight="900" font-size="${HOR ? 170 : 140}" fill="${ORA}">“</text>` +
        `<text x="${x + wC - 22}" y="${y + (HOR ? 96 : 112)}" font-family="Georgia, serif" font-weight="900" font-size="${HOR ? 170 : 140}" text-anchor="end" fill="${ORA}" opacity="${eo((L - d * .55) / .25).toFixed(2)}" transform="rotate(${(8 * (1 - eo((L - d * .55) / .3))).toFixed(1)} ${x + wC - 60} ${y + 60})">”</text></g>` +   // v65: cierre de comillas al acabar la frase
        cinetico(v.texto, ZC.x, y + (HOR ? 76 : 104) + size * .5, size, L, { max, t0: .3, paso: Math.min(.1, d * .5 / Math.max(6, String(v.texto || '').split(' ').length)) }) +
        (v.fuente ? peg(ZC.x + (HOR ? 300 : 150), y + hC + 4, v.fuente, HOR ? 26 : 30, INK, '#fff', 'middle', eo((L - d * .45) / .3), -3, back((L - d * .45) / .35)) : '');
    },
    linea(v, L, d, k) {
      const hs = (v.hitos || []).slice(0, 5), T0 = entradas(k, hs.map(h => String(h.fecha || '') + ' ' + String(h.texto || '')), d, .2, Math.max(1, d - .8) / Math.max(1, hs.length)), n = hs.length || 1, paso = Math.min(HOR ? 92 : 122, (Z.h - 10) / n), y0 = ZC.y - paso * (n - 1) / 2, x = HOR ? Z.x + 240 : ZC.x - Math.min(200, 40 + Math.max(...hs.map(h => Math.max(String(h.texto || '').length * 17, String(h.fecha || '').length * 15))) / 2);
      const tramo = Math.max(1, d - .8) / n, ia = T0.filter(x => L >= x).length - 1, prog = ia < 0 ? 0 : ia >= n - 1 ? 1 : (ia + eo((L - T0[ia]) / Math.max(.3, T0[ia + 1] - T0[ia]))) / (n - 1), yF = y0 + (n - 1) * paso * prog;
      let o = `<path d="M${x} ${y0} V${y0 + (n - 1) * paso}" stroke="${GRI}" stroke-width="10" stroke-linecap="round"/><path d="M${x} ${y0} V${yF.toFixed(1)}" stroke="${ORA}" stroke-width="10" stroke-linecap="round"/>`;
      hs.forEach((h, i) => {
        const t0 = T0[i], on = L >= t0, e = back((L - t0) / .35), y = y0 + i * paso, ult = on && (i === n - 1 || L < T0[i + 1]);
        o += `<circle cx="${x}" cy="${y}" r="${on ? 18 + (ult ? 4 * Math.sin(L * 6) : 0) : 12}" fill="${on ? ORA : BLA}" stroke="${INK}" stroke-width="3"/>`;
        if (on) o += `<g transform="translate(${((1 - e) * 140).toFixed(1)} 0)" opacity="${cl((L - t0) / .12)}">` + peg(x + 46, y + (HOR ? 10 : -6), String(h.fecha || ''), HOR ? 26 : 24, ult ? ORA : INK, '#fff', 'start', 1, -2) +
          tx(x + 46 + (HOR ? 170 : 0), y + (HOR ? 13 : 44), esc(h.texto || ''), HOR ? 38 : 32, INK, 'start', 800) + `</g>`;
      });
      return o;
    },
    icono(v, L, d) {
      const c = col(v.color), ix = HOR ? Z.x + 190 : ZC.x, iy = HOR ? ZC.y : Z.y + 175, size = HOR ? 58 : 44, max = HOR ? 19 : 22, alto = altoCin(v.texto, size, max);
      const tx0 = HOR ? Z.x + 400 + (Z.w - 400) / 2 : ZC.x, ty = HOR ? ZC.y - alto / 2 + size * .8 : Z.y + 345 + size * .5;
      const R0 = HOR ? 150 : 112, ondas = [0, 1].map(j => { const f = frac(L / 1.8 + j / 2); return `<circle cx="${ix}" cy="${iy}" r="${(R0 + 10 + 70 * f).toFixed(1)}" fill="none" stroke="${c}" stroke-width="${(6 * (1 - f)).toFixed(1)}" opacity="${(.5 * (1 - f) * cl(L / .4)).toFixed(2)}"/>`; }).join('');
      const orbita = atras => [0, 1, 2].map(j => { const a = L * 1.3 + j * 2.094, r = R0 + 26; if ((Math.sin(a) < 0) !== atras) return ''; return `<circle cx="${(ix + r * Math.cos(a)).toFixed(1)}" cy="${(iy + r * .45 * Math.sin(a)).toFixed(1)}" r="${j === 0 ? 11 : 7}" fill="${[ORA, ORO, c][j]}" stroke="${INK}" stroke-width="3" opacity="${cl((L - .3) / .3).toFixed(2)}"/>`; }).join('');   // v61: ondas y órbita (por detrás en la mitad de arriba)
      const halo = `<defs><radialGradient id="gI"><stop offset=".55" stop-color="${c}" stop-opacity=".32"/><stop offset="1" stop-color="${c}" stop-opacity="0"/></radialGradient></defs><circle cx="${ix}" cy="${iy}" r="${(R0 * (1.4 + .05 * Math.sin(L * 2))).toFixed(1)}" fill="url(#gI)" opacity="${eo(L / .5).toFixed(2)}"/>` +   // v89: halo de color detrás del icono
        `<circle cx="${ix}" cy="${iy}" r="${R0 + 34}" fill="none" stroke="${c}" stroke-width="4" stroke-dasharray="3 16" stroke-linecap="round" opacity="${(.6 * eo((L - .2) / .4)).toFixed(2)}" transform="rotate(${(L * 25).toFixed(1)} ${ix} ${iy})"/>`;
      return halo + ondas + orbita(true) + `<g transform="translate(0 ${(5 * Math.sin(L * 2.2)).toFixed(1)})">${sticker(ix, iy, R0, L, 0, v.icono, c)}</g>` + orbita(false) +
        cinetico(v.texto, tx0, ty, size, L, { max, t0: .2 }) +
        (v.etiqueta ? peg(tx0 + (HOR ? 120 : 110), ty + alto + 6, String(v.etiqueta), HOR ? 28 : 24, c === ORA ? AZU : c, '#fff', 'middle', eo((L - .8) / .25), 4, back((L - .8) / .35)) : '');
    },
    pregunta(v, L, d) {
      const size = HOR ? 60 : 48, max = HOR ? 18 : 20, alto = altoCin(v.texto, size, max), qx = HOR ? Z.x + 190 : ZC.x, qy = HOR ? ZC.y + 120 : Z.y + 230, e = back(L / .5), fs = HOR ? 380 : 260;
      const q = (dx, dy, f, st) => `<text x="${dx}" y="${dy}" font-family="Inter" font-weight="900" font-size="${fs}" text-anchor="middle" fill="${f}"${st ? ` stroke="${INK}" stroke-width="10" stroke-linejoin="round"` : ''}>?</text>`;
      const mini = [...Array(6).keys()].map(i => { const f = frac(L * .45 + i / 6), a = i * 1.7, x = qx + Math.cos(a) * (HOR ? 190 : 170) + 14 * Math.sin(L * 2 + i), y = qy - fs * .35 + Math.sin(a) * 90 - 60 * f;   // v64: interrogaciones que flotan
        return `<text x="${x.toFixed(1)}" y="${y.toFixed(1)}" font-family="Inter" font-weight="900" font-size="${32 + 14 * frac(i * .37)}" text-anchor="middle" fill="${[ORA, AZU, ORO][i % 3]}" stroke="${INK}" stroke-width="3" paint-order="stroke" opacity="${(Math.sin(Math.PI * f) * cl((L - .4) / .3)).toFixed(2)}" transform="rotate(${(-20 + 40 * frac(i * .53)).toFixed(0)} ${x.toFixed(1)} ${y.toFixed(1)})">?</text>`; }).join('');
      return mini + `<g transform="translate(${qx} ${qy}) rotate(${(-9 + 7 * Math.sin(L * 1.8)).toFixed(2)}) scale(${e.toFixed(3)})">${q(SOM + 2, SOM + 2, INK, true)}${q(0, 0, ORA, true)}</g>` +
        cinetico(v.texto, HOR ? Z.x + 400 + (Z.w - 400) / 2 : ZC.x, HOR ? ZC.y - alto / 2 + size * .8 : Z.y + 330, size, L, { max, t0: .25 });
    },
    titular(v, L, d) {
      const s = String(v.texto || ''), max = HOR ? 20 : 14, size = Math.min(HOR ? 124 : 84, (Z.w * .98) / (Math.min(max, Math.max(...partir(s.replace(/\*/g, ''), max).map(l => l.length), 4)) * .6));
      const alto = altoCin(s, size, max), ls = partir(s.replace(/\*/g, ''), max), wl = Math.min(Z.w, Math.max(...ls.map(l => l.length)) * size * .56), yU = ZC.y + alto / 2 + 18;
      const q = eio((L - .6 - ls.join(' ').split(' ').length * .11) / .45);   // v64: subrayado «a mano» cuando ha entrado el titular
      let ond = `M${(ZC.x - wl / 2).toFixed(1)} ${yU}`; for (let i = 1; i <= 8; i++) ond += ` Q${(ZC.x - wl / 2 + wl * (i - .5) / 8).toFixed(1)} ${(yU + (i % 2 ? 10 : -6)).toFixed(1)} ${(ZC.x - wl / 2 + wl * i / 8).toFixed(1)} ${(yU + (i % 2 ? 2 : 0)).toFixed(1)}`;
      return cinetico(s, ZC.x, ZC.y - alto / 2 + size * .82, size, L, { max, paso: .11, clave: col(v.color) }) +
        (q > 0 ? `<path d="${ond}" fill="none" stroke="${GRAVE ? INK : ORA}" stroke-width="9" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="${(1 - q).toFixed(3)}"/>` : '');
    },
    // ===== v56 (11-nov-2026): 8 gráficos nuevos para que no se repitan siempre los mismos =====
    // porcentaje: anillo que se llena con la cifra en el centro  {"tipo":"porcentaje","valor":"33,6 %","texto":"…","color":"rojo"}
    porcentaje(v, L, d) {
      const c = col(v.color), pct = cl(num(v.valor) / 100), p = eo(cl((L - .15) / Math.min(1.2, d * .5))), r = HOR ? 130 : 140, sw = HOR ? 38 : 42;
      const cx = HOR ? Z.x + 220 : ZC.x, cy = HOR ? ZC.y : Z.y + 180, C = 2 * Math.PI * r, e = back(L / .4), s = String(v.valor || '');
      const fsN = Math.min(HOR ? 92 : 96, 2 * r * .82 / (Math.max(3, s.length) * .58)), size = HOR ? 50 : 38, max = HOR ? 22 : 24, alto = altoCin(v.texto, size, max), R = r + sw / 2 + 8;
      return `<g transform="translate(${cx} ${cy}) scale(${e.toFixed(3)})"><circle cx="${SOM}" cy="${SOM}" r="${R}" fill="${INK}" opacity=".22" filter="url(#somS)"/><circle r="${R}" fill="${BLA}" stroke="${INK}" stroke-width="3"/>` +
        `<circle r="${r}" fill="none" stroke="${GRI}" stroke-width="${sw}"/>` +
        `<circle r="${r}" fill="none" stroke="${c === INK ? ORA : c}" stroke-width="${sw}" stroke-linecap="round" stroke-dasharray="${(C * pct * p).toFixed(1)} ${C.toFixed(1)}" transform="rotate(-90)"/>` +
        tx(0, fsN * .35, esc(contar(s, p)), fsN, INK, 'middle', 900, 'letter-spacing="-3"') + `</g>` +
        cinetico(v.texto, HOR ? Z.x + 450 + (Z.w - 450) / 2 : ZC.x, HOR ? ZC.y - alto / 2 + size * .8 : cy + R + 64, size, L, { max, t0: .35 });
    },
    // proporcion: «1 de cada 3» con muñequitos  {"tipo":"proporcion","son":1,"de":3,"texto":"…"}
    proporcion(v, L, d) {
      const de = Math.max(2, Math.min(10, Math.round(num(v.de) || 10))), son = Math.max(1, Math.min(de, Math.round(num(v.son) || 1)));
      const por = de <= 5 ? de : Math.ceil(de / 2), filas = Math.ceil(de / por), s = Math.min(HOR ? 105 : 100, (HOR ? Z.w * .5 : Z.w) / por);
      const x0 = HOR ? Z.x + 10 : ZC.x - s * por / 2, y0 = HOR ? ZC.y - s * 1.25 * filas / 2 : Z.y + 30;
      let o = '';
      for (let i = 0; i < de; i++) {
        const t0 = .1 + i * .06, e = back((L - t0) / .35), on = i < son && L > .8 + i * .12, x = x0 + (i % por) * s + s / 2, y = y0 + Math.floor(i / por) * s * 1.25 + s * .6, f = on ? ORA : GRI;
        if (e <= 0) continue;
        o += `<g transform="translate(${x.toFixed(1)} ${y.toFixed(1)}) scale(${(e * (on ? 1 + .05 * Math.sin(L * 5) : 1) * s / 78).toFixed(3)})"><circle cx="0" cy="-24" r="17" fill="${f}" stroke="${INK}" stroke-width="3"/><path d="M-27 36 v-20 a27 24 0 0 1 54 0 v20 z" fill="${f}" stroke="${INK}" stroke-width="3" stroke-linejoin="round"/></g>`;
      }
      const xT = HOR ? Z.x + Z.w * .5 + 30 + (Z.w * .5 - 30) / 2 : ZC.x, yT = HOR ? ZC.y - 30 : y0 + filas * s * 1.25 + 46;
      return o + peg(xT, yT, `${son} DE CADA ${de}`, HOR ? 46 : 40, ORA, '#fff', 'middle', eo((L - .8) / .3), -2, back((L - .8) / .4)) +
        cinetico(v.texto, xT, yT + (HOR ? 84 : 78), HOR ? 40 : 34, L, { max: HOR ? 24 : 26, t0: 1 });
    },
    // versus: cara a cara de dos personas, partidos o posturas  {"tipo":"versus","a":{"nombre":"…","texto":"…"},"b":{…}}
    versus(v, L, d) {
      const lado = (o, i) => {
        o = o || {}; const t0 = .1 + i * .3, e = back((L - t0) / .45); if (e <= 0) return '';
        const w = HOR ? Z.w * .4 : Z.w / 2 - 20, x = i ? Z.x + Z.w - w : Z.x, y = HOR ? Z.y + 20 : Z.y + 30, h = HOR ? Z.h - 40 : Z.h - 90, c = i ? AZU : ORA, cx = x + w / 2;
        const nom = String(o.nombre || ''), ini = nom.split(/\s+/).filter(Boolean).map(s => s[0]).slice(0, 2).join('').toUpperCase() || '?';
        const fsN = Math.min(HOR ? 32 : 26, (w - 24) / (Math.max(4, nom.length) * .58)), ls = partir(String(o.texto || ''), HOR ? 22 : 12), fs = HOR ? 32 : 27, rC = HOR ? 62 : 56, yC = y + 70 + rC + 16;
        return `<g transform="translate(${((1 - e) * (i ? 1 : -1) * 280).toFixed(1)} 0) rotate(${i ? 1.5 : -1.5} ${cx} ${y + h / 2})">` + caja(x, y, w, h, 26, BLA, 5) +
          `<path d="M${x} ${y + 70} V${y + 26} a26 26 0 0 1 26 -26 H${x + w - 26} a26 26 0 0 1 26 26 V${y + 70} Z" fill="${c}" stroke="${INK}" stroke-width="3"/>` +
          tx(cx, y + 47, esc(nom), fsN, '#fff', 'middle', 900) +
          `<circle cx="${cx}" cy="${yC}" r="${rC}" fill="${c}" fill-opacity=".16" stroke="${INK}" stroke-width="3"/>` + tx(cx, yC + rC * .3, esc(ini), rC * .85, c, 'middle', 900) +
          ls.map((l, j) => tx(cx, yC + rC + 50 + j * fs * 1.2, esc(l), fs, INK, 'middle', 800, `opacity="${eo((L - t0 - .3 - j * .08) / .25).toFixed(2)}"`)).join('') + `</g>`;
      };
      const vy = HOR ? ZC.y : Z.y + 30 + (Z.h - 90) / 2, ev = back((L - .6) / .4), pul = 1 + .06 * Math.sin(L * 6);
      const rayo = ev > 0 && !GRAVE ? (() => { const j = Math.floor(L * 12), rr = i => (Math.sin(j * 12.9 + i * 78.2) * 43758.5) % 1, hR = HOR ? Z.h * .7 : Z.h * .75; let dd = `M${ZC.x} ${vy - hR / 2}`;
        for (let i = 1; i <= 6; i++) dd += ` L${(ZC.x + (i % 2 ? 1 : -1) * (8 + 14 * Math.abs(rr(i)))).toFixed(1)} ${(vy - hR / 2 + hR * i / 6).toFixed(1)}`;
        return `<path d="${dd}" fill="none" stroke="${ORO}" stroke-width="10" stroke-linejoin="round" opacity="${(.85 * ev).toFixed(2)}"/><path d="${dd}" fill="none" stroke="#fff" stroke-width="3" stroke-linejoin="round" opacity="${ev.toFixed(2)}"/>`; })() : '';   // v66
      return lado(v.a, 0) + lado(v.b, 1) + rayo + (ev > 0 ? `<g transform="translate(${ZC.x} ${vy}) rotate(-8) scale(${(ev * pul).toFixed(3)})"><circle cx="${SOM}" cy="${SOM}" r="${HOR ? 54 : 46}" fill="${INK}" opacity=".22" filter="url(#somS)"/><circle r="${HOR ? 54 : 46}" fill="${ORO}" stroke="${INK}" stroke-width="4"/>${tx(0, HOR ? 17 : 15, 'VS', HOR ? 48 : 40, INK)}</g>` : '');
    },
    // mapa de España con chinchetas en las ciudades nombradas  {"tipo":"mapa","lugares":["Oviedo","Madrid"],"texto":"…"}
    mapa(v, L, d) {
      const can0 = (v.lugares || []).some(s => (CIUDADES[norm(s)] || [0])[0] < -12), alto = can0 ? 10.1 : 8.2;   // con Canarias, el mapa baja hasta su recuadro
      const lon0 = -9.6, lat0 = 43.95, hTx = !HOR && v.texto ? altoCin(v.texto, 36, 26) + 26 : 56, k = HOR ? Math.min(44, 380 / alto) : Math.min(55, Z.w / 9.96, (Z.h - 34 - hTx) / alto), kx = k * .766, mw = 13.4 * kx, mh = alto * k;
      const ox = HOR ? Z.x + 30 : ZC.x - mw / 2, oy = HOR ? ZC.y - mh / 2 : Z.y + 34, P_ = (lo, la) => [ox + (lo - lon0) * kx, oy + (lat0 - la) * k];
      const dPath = 'M' + ESP.map(([lo, la]) => P_(lo, la).map(n => n.toFixed(1)).join(' ')).join(' L') + ' Z';
      const p = eo(L / .7), f = eo((L - .4) / .4);
      let o = `<path d="${dPath}" transform="translate(${SOM} ${SOM})" fill="${INK}" opacity="${(f * .22).toFixed(3)}" filter="url(#somS)"/>` +
        `<path d="${dPath}" fill="${BLA}" fill-opacity="${f.toFixed(2)}" stroke="${INK}" stroke-width="3" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="${(1 - p).toFixed(3)}"/>` +
        BAL.map(([lo, la, rx, ry]) => { const [x, y] = P_(lo, la); return `<ellipse cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" rx="${rx * kx}" ry="${ry * k}" fill="${BLA}" stroke="${INK}" stroke-width="2.5" opacity="${f.toFixed(2)}"/>`; }).join('');
      const ls = (v.lugares || []).map(s => [s, CIUDADES[norm(s)]]).filter(x => x[1]).slice(0, 3);
      // Canarias en recuadro abajo a la izquierda (solo si se nombra algún lugar canario): se trasladan a (-8.6, 36.9) en el mapa
      const CAN = [[-18.0, 27.75, .13, .1], [-17.85, 28.68, .12, .18], [-17.2, 28.1, .12, .1], [-16.55, 28.3, .35, .22], [-15.6, 27.95, .28, .25], [-14.0, 28.4, .45, .22], [-13.6, 29.05, .3, .18]];
      const canario = ls.some(([, [lo, la]]) => lo < -12), mov = ([lo, la]) => lo < -12 ? [lo + 8.7, la + 6.25] : [lo, la];
      if (canario) {
        const [bx, by] = P_(-9.5, 35.75), [bx2, by2] = P_(-4.55, 33.9);
        o += `<rect x="${bx.toFixed(1)}" y="${by.toFixed(1)}" width="${(bx2 - bx).toFixed(1)}" height="${(by2 - by).toFixed(1)}" rx="10" fill="none" stroke="${INK}" stroke-width="3" stroke-dasharray="8 6" opacity="${f.toFixed(2)}"/>` +
          CAN.map(([lo, la, rx, ry]) => { const [x, y] = P_(...mov([lo, la])); return `<ellipse cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" rx="${rx * kx}" ry="${ry * k}" fill="${BLA}" stroke="${INK}" stroke-width="2.5" opacity="${f.toFixed(2)}"/>`; }).join('');
      }
      if (ls.length > 1 && (v.ruta === true || v.ruta === 'true')) {   // v66: ruta discontinua que une los lugares (v74: solo si hay trayecto real)
        const pts = ls.map(([, ll]) => P_(...mov(ll))), q = eio(cl((L - 1.6) / .8));
        if (q > 0) o += `<path d="M${pts.map(p => p.map(z => z.toFixed(1)).join(' ')).join(' L')}" fill="none" stroke="${ROJ}" stroke-width="5" stroke-dasharray="12 10" stroke-dashoffset="${(-L * 40).toFixed(1)}" opacity="${q.toFixed(2)}"/>`;
      }
      // v71: las etiquetas van encima de todas las chinchetas y, si dos lugares están muy cerca, una va al otro lado y más abajo
      const PT = ls.map(([, ll]) => P_(...mov(ll))); let etq = '';
      ls.forEach(([nom, [lo, la]], i) => {
        const t0 = .8 + i * .35, e = back((L - t0) / .4); if (e <= 0) return;
        const [x, y] = P_(...mov([lo, la])), cae = (1 - eo((L - t0) / .3)) * 90, rip = frac((L - t0) / 1.2);
        const cerca = PT.some((p, j) => j < i && Math.hypot(p[0] - x, p[1] - y) < 110), der0 = x > ox + mw * .6, izq = cerca ? !der0 : der0;
        o += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${(8 + 40 * rip).toFixed(1)}" fill="none" stroke="${ROJ}" stroke-width="4" opacity="${(1 - rip).toFixed(2)}"/>` +
          `<g transform="translate(${x.toFixed(1)} ${(y - cae).toFixed(1)}) scale(${(e * (HOR ? .5 : .55)).toFixed(3)})"><path d="M0 0 C-30 -40 -40 -55 -40 -75 A40 40 0 0 1 40 -75 C40 -55 30 -40 0 0 Z" fill="${ROJ}" stroke="${INK}" stroke-width="4.5"/><circle cy="-75" r="14" fill="${BLA}" stroke="${INK}" stroke-width="3"/></g>` +
          '';
        const arriba = y - 58 < Z.y + 24;   // v77: si el lugar está muy arriba (Asturias, Galicia…), la etiqueta va al lado y no tapa el rótulo
        etq += peg(x + (izq ? -28 : 28), y - (cerca || arriba ? (HOR ? 10 : 6) : (HOR ? 54 : 58)), String(nom).toUpperCase(), 20, INK, '#fff', izq ? 'end' : 'start', eo((L - t0 - .2) / .2), cerca || arriba ? 3 : -3);
      });
      o += etq;
      const size = HOR ? 46 : 36, max = HOR ? 20 : 26;
      return o + (v.texto ? cinetico(v.texto, HOR ? ox + mw + (Z.x + Z.w - ox - mw) / 2 : ZC.x, HOR ? ZC.y - altoCin(v.texto, size, max) / 2 + size * .8 : oy + mh + 40, size, L, { max, t0: .5 }) : '');
    },
    // recorte de periódico con el titular subrayado  {"tipo":"prensa","medio":"El País","texto":"titular tal cual"}
    prensa(v, L, d) {
      const w = HOR ? 820 : Z.w, x = ZC.x - w / 2, fs = HOR ? 46 : 38, ls = partir(String(v.texto || '').replace(/\*/g, ''), HOR ? 26 : 22);
      const h = (HOR ? 140 : 130) + ls.length * fs * 1.14 + (HOR ? 90 : 110), y = ZC.y - h / 2 - (HOR ? 0 : 20), e = back(L / .45), pM = eo((L - .55) / .6), serif = `Georgia, 'DejaVu Serif', serif`;
      let o = `<g transform="translate(${ZC.x} ${ZC.y}) rotate(${(-2.5 + .4 * Math.sin(L * 1.3)).toFixed(2)}) scale(${e.toFixed(3)}) translate(${-ZC.x} ${-ZC.y})">` + caja(x, y, w, h, 4, '#fbf8f0', 4) +
        `<text x="${ZC.x}" y="${y + (HOR ? 62 : 58)}" font-family="${serif}" font-weight="900" font-size="${HOR ? 48 : 40}" text-anchor="middle" fill="${INK}">${esc(v.medio || '')}</text>` +
        `<path d="M${x + 22} ${y + (HOR ? 84 : 78)} H${x + w - 22} M${x + 22} ${y + (HOR ? 91 : 85)} H${x + w - 22}" stroke="${INK}" stroke-width="2.5"/>`;
      const y1 = y + (HOR ? 140 : 128);
      ls.forEach((l, i) => {
        const yy = y1 + i * fs * 1.14, wl = Math.min(w - 40, l.length * fs * .52), pi_ = cl(pM * ls.length - i);
        o += `<rect x="${(ZC.x - wl / 2 - 8).toFixed(1)}" y="${(yy - fs * .78).toFixed(1)}" width="${((wl + 16) * pi_).toFixed(1)}" height="${(fs * .95).toFixed(1)}" fill="${ORO}" opacity=".8"/>` +
          `<text x="${ZC.x}" y="${yy.toFixed(1)}" font-family="${serif}" font-weight="900" font-size="${fs}" text-anchor="middle" fill="${INK}">${esc(l)}</text>`;
      });
      const yg = y1 + ls.length * fs * 1.14;
      for (let i = 0; i < 3; i++) o += `<rect x="${x + 28}" y="${(yg + i * 20).toFixed(1)}" width="${((w - 56) * (i === 2 ? .55 : 1)).toFixed(1)}" height="8" rx="4" fill="${INK}" opacity=".13"/>`;
      return o + `</g>` + peg(x + w - 30, y + h + 6, 'FUENTE', HOR ? 22 : 20, ROJ, '#fff', 'end', eo((L - .4) / .2), 4);
    },
    // diálogo con bocadillos (quién dijo qué)  {"tipo":"dialogo","lineas":[{"quien":"Broncano","texto":"…"},{"quien":"Abascal","texto":"…"}]}
    dialogo(v, L, d) {
      const ls = (v.lineas || []).slice(0, 3), n = ls.length || 1, fs = HOR ? 34 : 31, maxc = HOR ? 32 : 21;
      const bl = ls.map(o => partir(String(o.texto || ''), maxc)), al = bl.map(b => b.length * fs * 1.2 + (HOR ? 54 : 56)), tot = al.reduce((a, b) => a + b, 0) + (n - 1) * 30;
      const quien = [...new Set(ls.map(o => String(o.quien || '')))];
      let y = ZC.y - tot / 2, o = '';
      ls.forEach((ln, i) => {
        const t0 = .15 + i * Math.max(.5, (d - .6) / n), e = back((L - t0) / .4), der = quien.indexOf(String(ln.quien || '')) % 2 === 1, b = bl[i], h = al[i];
        const w = Math.min(HOR ? 760 : Z.w - 30, Math.max(...b.map(l => l.length), String(ln.quien || '').length) * fs * .56 + 64), x = der ? Z.x + Z.w - w - (HOR ? 90 : 0) : Z.x, c = der ? AZU : ORA, yy = y;   // v81: en horizontal deja sitio a Lupi (abajo a la derecha)
        y += h + 30;
        if (e <= 0) return;
        const ax = der ? x + w - 34 : x + 34;
        o += `<g transform="translate(${ax} ${yy + h}) scale(${e.toFixed(3)}) translate(${-ax} ${-(yy + h)})">` +
          `<path d="M${ax - 16} ${yy + h - 6} L${ax + (der ? 22 : -22)} ${yy + h + 26} L${ax + 16} ${yy + h - 6} Z" fill="${der ? '#e7eeff' : '#fff0e3'}" stroke="${INK}" stroke-width="3" stroke-linejoin="round"/>` +
          caja(x, yy, w, h, 26, der ? '#e7eeff' : '#fff0e3', 5) +
          `<path d="M${ax - 14} ${yy + h - 3} H${ax + 14}" stroke="${der ? '#e7eeff' : '#fff0e3'}" stroke-width="8"/>` +
          peg(der ? x + w - 22 : x + 22, yy + 4, String(ln.quien || '').toUpperCase(), HOR ? 22 : 19, c, '#fff', der ? 'end' : 'start', 1, der ? 2 : -2) +
          b.map((l, j) => tx(der ? x + w - 26 : x + 26, yy + (HOR ? 54 : 56) + j * fs * 1.2, esc(l), fs, INK, der ? 'end' : 'start', 800)).join('') + `</g>`;
      });
      return o;
    },
    // ranking con medallas (de mayor a menor)  {"tipo":"ranking","titulo":"…","items":[{"etiqueta":"Madrid","valor":"1.150 €"},…]}
    ranking(v, L, d) {
      const it = (v.items || []).slice(0, 5).map(o => ({ et: String(o.etiqueta || ''), va: String(o.valor || ''), n: Math.abs(num(o.valor)) })).sort((a, b) => b.n - a.n), n = it.length || 1;
      const mx = Math.max(...it.map(o => o.n), 1e-9), hT = v.titulo ? (HOR ? 70 : 80) : 0, ah = Math.min(HOR ? 60 : 74, (Z.h - hT) / n - 16), y0 = Z.y + hT + (Z.h - hT - n * (ah + 16)) / 2;
      const xL = Z.x + ah + 14, wMax = Z.w - ah - 14, med = [ORO, '#c9ccd3', '#d6894a'];
      let o = v.titulo ? cinetico(v.titulo, ZC.x, Z.y + (HOR ? 44 : 54), HOR ? 40 : 34, L, { max: HOR ? 46 : 28 }) : '';
      it.forEach((r, i) => {
        const t0 = .25 + (n - 1 - i) * .22, p = eo((L - t0) / .6); if (L < t0) return;
        const y = y0 + i * (ah + 16), w = Math.max(ah * 2.6, wMax * r.n / mx) * p, top = i === 0, fsE = Math.min(ah * .38, (wMax * .62) / (Math.max(5, r.et.length) * .56));
        o += `<g opacity="${cl((L - t0) / .15)}"><circle cx="${Z.x + ah / 2 + SOM / 2}" cy="${y + ah / 2 + SOM / 2}" r="${ah / 2}" fill="${INK}" opacity=".22" filter="url(#somS)"/><circle cx="${Z.x + ah / 2}" cy="${y + ah / 2}" r="${ah / 2}" fill="${med[i] || BLA}" stroke="${INK}" stroke-width="2.5"/>` +
          tx(Z.x + ah / 2, y + ah / 2 + ah * .16, String(i + 1), ah * .45, INK) + (top ? `<g transform="translate(${Z.x + ah / 2} ${(y - ah * .12 - 4 * Math.abs(Math.sin(L * 3))).toFixed(1)}) rotate(-12) scale(${(ah / 80 * back((L - t0 - .5) / .35)).toFixed(3)})"><path d="M-26 0 L-30 -26 L-14 -12 L0 -32 L14 -12 L30 -26 L26 0 Z" fill="${ORO}" stroke="${INK}" stroke-width="3" stroke-linejoin="round"/></g>` : '') + caja(xL, y, w, ah, ah * .3, top ? ORA : BLA, 4) +
          tx(xL + 18, y + ah / 2 + fsE * .36, esc(r.et), fsE, top ? '#fff' : INK, 'start', 800) +
          tx(xL + w - 16, y + ah / 2 + ah * .15, esc(contar(r.va, p)), ah * .42, top ? '#fff' : INK, 'end', 900) + `</g>`;
      });
      return o;
    },
    // calendario con cuenta atrás  {"tipo":"fecha","fecha":"29 NOV","texto":"elecciones generales"}
    fecha(v, L, d) {
      const MES = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC'], ME = s => MES.indexOf(String(s || '').slice(0, 3).toUpperCase().replace('É', 'E'));
      const m = String(v.fecha || '').toUpperCase().match(/(\d{1,2})\s*(?:DE\s+)?([A-ZÁÉÍÓÚ]{3})/), dia = m ? m[1] : String(v.fecha || '').slice(0, 5), mes = m ? m[2] : '';
      const s = HOR ? 280 : 280, cx = HOR ? Z.x + 220 : ZC.x, cy = HOR ? ZC.y : Z.y + 170, x = cx - s / 2, y = cy - s / 2, fl = eo(L / .45), e = back(L / .4);
      let o = `<g transform="translate(${cx} ${y}) scale(${e.toFixed(3)} ${(e * (.3 + .7 * fl)).toFixed(3)}) translate(${-cx} ${-y})">` + caja(x, y, s, s, 26, BLA, 6) +
        `<path d="M${x} ${y + 84} V${y + 26} a26 26 0 0 1 26 -26 H${x + s - 26} a26 26 0 0 1 26 26 V${y + 84} Z" fill="${ROJ}" stroke="${INK}" stroke-width="4"/>` +
        tx(cx, y + 60, esc(mes), 44, '#fff', 'middle', 900, 'letter-spacing="4"') +
        [-1, 1].map(j => `<rect x="${cx + j * 70 - 9}" y="${y - 22}" width="18" height="44" rx="9" fill="${GRI}" stroke="${INK}" stroke-width="3"/>`).join('') +
        tx(cx, y + 84 + (s - 84) * .5 + 58, esc(dia), 160, INK, 'middle', 900, 'letter-spacing="-6"') + `</g>`;
      // cuenta atrás desde la fecha del vídeo (P.fecha «11 NOV 2026»)
      const hm = String(P.fecha || '').toUpperCase().match(/(\d{1,2})\s+([A-Z]{3})\s+(\d{4})/);
      if (m && hm && ME(mes) >= 0 && ME(hm[2]) >= 0) {
        const a = +hm[3], hoy = Date.UTC(a, ME(hm[2]), +hm[1]); let f = Date.UTC(a, ME(mes), +dia);
        if (f < hoy - 200 * 864e5) f = Date.UTC(a + 1, ME(mes), +dia);
        const dd = Math.round((f - hoy) / 864e5), et = dd === 0 ? 'ES HOY' : dd === 1 ? 'MAÑANA' : dd > 1 && dd < 400 ? `FALTAN ${dd} DÍAS` : dd === -1 ? 'FUE AYER' : '';
        if (et) o += peg(cx + (HOR ? 0 : 0), y + s + (HOR ? 40 : 46), et, HOR ? 30 : 30, ORA, '#fff', 'middle', eo((L - .6) / .2), -3, back((L - .6) / .35));
      }
      const size = HOR ? 48 : 38, max = HOR ? 20 : 24;
      return o + (v.texto ? cinetico(v.texto, HOR ? Z.x + 440 + (Z.w - 440) / 2 : ZC.x, HOR ? ZC.y - altoCin(v.texto, size, max) / 2 + size * .8 : y + s + 120, size, L, { max, t0: .4 }) : '');
    },
    // ===== v58 (11-nov-2026): 9 gráficos animados más =====
    // velocímetro con aguja (riesgo, nivel, nota…)  {"tipo":"medidor","valor":"8,2","max":"10","texto":"…"}
    medidor(v, L, d) {
      const mx = num(v.max) || 100, pr = cl(num(v.valor) / mx), p = back((L - .2) / .9), cx = HOR ? Z.x + 250 : ZC.x, cy = HOR ? ZC.y + 95 : Z.y + 250, r = HOR ? 180 : 200, sw = HOR ? 36 : 40;
      const pt = (a, rr) => [cx + rr * Math.cos(a), cy + rr * Math.sin(a)], arc = (a0, a1, c) => { const [x0, y0] = pt(a0, r), [x1, y1] = pt(a1, r); return `<path d="M${x0.toFixed(1)} ${y0.toFixed(1)} A${r} ${r} 0 0 1 ${x1.toFixed(1)} ${y1.toFixed(1)}" fill="none" stroke="${c}" stroke-width="${sw}"/>`; };
      const e = back(L / .4), R = r + sw / 2 + 16, ang = 180 * pr * cl(p, 0, 1.08) + 2.5 * Math.sin(L * 9) * Math.exp(-Math.max(0, L - 1.1) * 3) * (L > 1.1 ? 1 : 0);
      let o = `<g transform="translate(${cx} ${cy}) scale(${e.toFixed(3)}) translate(${-cx} ${-cy})">` +
        `<path d="M${cx - R + SOM} ${cy + SOM} A${R} ${R} 0 0 1 ${cx + R + SOM} ${cy + SOM} Z" fill="${INK}" opacity=".22" filter="url(#somS)"/><path d="M${cx - R} ${cy} A${R} ${R} 0 0 1 ${cx + R} ${cy} Z" fill="${BLA}" stroke="${INK}" stroke-width="3"/>` +
        arc(Math.PI, Math.PI * 1.5, VER) + arc(Math.PI * 1.5, Math.PI * 1.8, ORO) + arc(Math.PI * 1.8, Math.PI * 2, ROJ);
      for (let i = 0; i <= 10; i++) { const a = Math.PI * (1 + i / 10), [x0, y0] = pt(a, r - sw / 2 - 8), [x1, y1] = pt(a, r - sw / 2 - (i % 5 ? 20 : 34)); o += `<path d="M${x0.toFixed(1)} ${y0.toFixed(1)} L${x1.toFixed(1)} ${y1.toFixed(1)}" stroke="${INK}" stroke-width="${i % 5 ? 3 : 5}"/>`; }
      o += `<g transform="rotate(${ang.toFixed(2)} ${cx} ${cy})"><path d="M${cx} ${cy - 12} L${cx - r + 30} ${cy} L${cx} ${cy + 12} Z" fill="${INK}"/></g><circle cx="${cx}" cy="${cy}" r="22" fill="${ORA}" stroke="${INK}" stroke-width="3"/></g>`;
      const size = HOR ? 48 : 38, max = HOR ? 20 : 24;
      return o + tx(cx, cy + (HOR ? 78 : 86), esc(contar(String(v.valor || ''), eo((L - .2) / .9)) + (v.max ? ` / ${v.max}` : '')), HOR ? 60 : 64, INK, 'middle', 900, `opacity="${eo((L - .3) / .3).toFixed(2)}"`) +
        (v.texto ? cinetico(v.texto, HOR ? Z.x + 520 + (Z.w - 520) / 2 : ZC.x, HOR ? ZC.y - altoCin(v.texto, size, max) / 2 + size * .8 : cy + 160, size, L, { max, t0: .5 }) : '');
    },
    // gráfica de líneas que se dibuja sola  {"tipo":"evolucion","titulo":"…","valores":["1,2","1,9","3,4"],"etiquetas":["2020","2023","2026"]}
    evolucion(v, L, d) {
      const vs = (v.valores || []).slice(0, 8).map(num), et = v.etiquetas || [], n = Math.max(2, vs.length), mn = Math.min(...vs), mxv = Math.max(...vs), rg = (mxv - mn) || 1;
      const hT = v.titulo ? (HOR ? 64 : 76) : 0, x0 = Z.x + (HOR ? 40 : 30), x1 = Z.x + Z.w - (HOR ? 70 : 50), y0 = Z.y + hT + (HOR ? 40 : 60), y1 = Z.y + Z.h - (HOR ? 54 : 80);
      const P_ = i => [x0 + (x1 - x0) * i / (n - 1), y1 - (y1 - y0) * ((vs[i] - mn) / rg * .85 + .1)], pts = vs.map((_, i) => P_(i));
      const p = eio(cl((L - .25) / Math.min(1.6, d * .6))), pos = p * (n - 1), ki = Math.min(n - 2, Math.floor(pos)), fr = pos - ki;
      const cur = pts.length > 1 ? [pts[ki][0] + (pts[ki + 1][0] - pts[ki][0]) * fr, pts[ki][1] + (pts[ki + 1][1] - pts[ki][1]) * fr] : pts[0];
      const linea = 'M' + pts.slice(0, ki + 1).map(q => q.map(z => z.toFixed(1)).join(' ')).join(' L') + ` L${cur[0].toFixed(1)} ${cur[1].toFixed(1)}`;
      let o = v.titulo ? cinetico(v.titulo, ZC.x, Z.y + (HOR ? 40 : 50), HOR ? 40 : 34, L, { max: HOR ? 46 : 28 }) : '';
      o += [0, 1, 2].map(i => `<path d="M${x0} ${(y0 + (y1 - y0) * i / 2).toFixed(1)} H${x1}" stroke="${INK}" stroke-opacity=".14" stroke-width="3" stroke-dasharray="4 12"/>`).join('');
      o += `<path d="${linea} L${cur[0].toFixed(1)} ${y1} L${x0} ${y1} Z" fill="${ORA}" opacity=".16"/>` +
        `<path d="${linea}" transform="translate(${SOM / 2} ${SOM / 2})" fill="none" stroke="${INK}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" opacity=".22" filter="url(#somS)"/>` +
        `<path d="${linea}" fill="none" stroke="${ORA}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>`;
      pts.forEach((q, i) => { if (i > pos + .001) return; o += `<circle cx="${q[0].toFixed(1)}" cy="${q[1].toFixed(1)}" r="9" fill="${BLA}" stroke="${INK}" stroke-width="2.5"/>` + tx(q[0], y1 + (HOR ? 40 : 44), esc(et[i] || ''), HOR ? 24 : 22, INK, 'middle', 800); });
      o += `<circle cx="${cur[0].toFixed(1)}" cy="${cur[1].toFixed(1)}" r="${(16 + 3 * Math.sin(L * 8)).toFixed(1)}" fill="${ORA}" stroke="${INK}" stroke-width="3"/>`;
      const ult = String((v.valores || [])[n - 1] || ''), ep = back((p - .97) / .03 + (L - Math.min(1.6, d * .6) - .25) / .3);
      if (p > .97) o += peg(Math.min(cur[0], x1 - 20), cur[1] - 34, ult, HOR ? 32 : 30, INK, '#fff', 'middle', 1, -3, cl(ep, 0, 1.2));
      return o + `<path d="M${x0} ${y1} H${x1 + 20}" stroke="${INK}" stroke-width="4" stroke-linecap="round"/>`;
    },
    // reparto en tarta (rosco) con leyenda  {"tipo":"reparto","titulo":"…","partes":[{"etiqueta":"Sí","valor":"58"},{"etiqueta":"No","valor":"42"}]}
    reparto(v, L, d) {
      const ps = (v.partes || []).slice(0, 5), tot = ps.reduce((a, b) => a + Math.abs(num(b.valor)), 0) || 1, pal = [ORA, AZU, VER, ORO, MOR];
      const r = HOR ? 140 : 125, sw = HOR ? 70 : 62, cx = HOR ? Z.x + 230 : ZC.x, cy = HOR ? ZC.y : Z.y + (v.titulo ? 215 : 175), C = 2 * Math.PI * r, e = back(L / .4);
      let acc = 0, o = `<g transform="translate(${cx} ${cy}) scale(${e.toFixed(3)})"><circle cx="${SOM}" cy="${SOM}" r="${r + sw / 2 + 6}" fill="${INK}" opacity=".22" filter="url(#somS)"/><circle r="${r + sw / 2 + 6}" fill="${BLA}" stroke="${INK}" stroke-width="3"/>`;
      ps.forEach((q, i) => {
        const fr = Math.abs(num(q.valor)) / tot, t0 = .2 + i * .25, p = eio((L - t0) / .5), c = q.color ? col(q.color) : pal[i];
        o += `<circle r="${r}" fill="none" stroke="${c}" stroke-width="${sw}" stroke-dasharray="${(C * fr * p).toFixed(1)} ${C.toFixed(1)}" transform="rotate(${(-90 + 360 * acc).toFixed(2)})"/>`;
        acc += fr;
      });
      o += `<circle r="${r - sw / 2}" fill="none" stroke="${INK}" stroke-width="2.5"/><circle r="${r + sw / 2}" fill="none" stroke="${INK}" stroke-width="2.5"/></g>`;
      const lx = HOR ? Z.x + 470 : Z.x + 20, ly = HOR ? ZC.y - ps.length * 30 : cy + r + sw / 2 + 50, fs = HOR ? 32 : 28;
      ps.forEach((q, i) => {
        const t0 = .3 + i * .25, ee = back((L - t0) / .35), c = q.color ? col(q.color) : pal[i], y = ly + i * (HOR ? 60 : 50), pc = Math.round(Math.abs(num(q.valor)) / tot * 100);
        if (ee <= 0) return;
        o += `<g transform="translate(${((1 - ee) * -80).toFixed(1)} 0)" opacity="${cl((L - t0) / .15)}"><rect x="${lx}" y="${y - fs * .8}" width="${fs}" height="${fs}" rx="7" fill="${c}" stroke="${INK}" stroke-width="2.5"/>` +
          tx(lx + fs + 16, y, esc(q.etiqueta || ''), fs, INK, 'start', 800) + tx(HOR ? Z.x + Z.w - 20 : Z.x + Z.w - 20, y, esc(/%/.test(String(q.valor)) ? String(q.valor) : (String(q.valor).match(/[a-zA-Z€]/) ? String(q.valor) : pc + ' %')), fs, INK, 'end', 900) + `</g>`;
      });
      return o + (v.titulo ? cinetico(v.titulo, HOR ? lx + (Z.x + Z.w - lx) / 2 : ZC.x, HOR ? Z.y + 30 : Z.y + 22, HOR ? 38 : 32, L, { max: HOR ? 36 : 30 }) : '');
    },
    // flecha de tendencia en zigzag  {"tipo":"tendencia","sentido":"sube","valor":"+12 %","texto":"…","color":"rojo"}
    tendencia(v, L, d) {
      const sube = !/baj|cae|desc|menos/i.test(String(v.sentido || '')), c = v.color ? col(v.color) : (sube ? VER : ROJ), w = HOR ? 500 : Z.w - 110, h = HOR ? 290 : 290;
      const x0 = HOR ? Z.x + 20 : ZC.x - w / 2, y0 = HOR ? ZC.y + h / 2 : Z.y + 30 + h, fy = f => sube ? y0 - h * f : y0 - h + h * f;
      const ks = [[0, .05], [.22, .38], [.36, .22], [.58, .6], [.72, .46], [1, .95]].map(([a, b]) => [x0 + w * a, fy(b)]);
      const p = eio(cl((L - .15) / .9)), pos = p * (ks.length - 1), ki = Math.min(ks.length - 2, Math.floor(pos)), fr = pos - ki, cur = [ks[ki][0] + (ks[ki + 1][0] - ks[ki][0]) * fr, ks[ki][1] + (ks[ki + 1][1] - ks[ki][1]) * fr];
      const lin = 'M' + ks.slice(0, ki + 1).map(q => q.map(z => z.toFixed(1)).join(' ')).join(' L') + ` L${cur[0].toFixed(1)} ${cur[1].toFixed(1)}`;
      const a = Math.atan2(ks[ki + 1][1] - ks[ki][1], ks[ki + 1][0] - ks[ki][0]) * 180 / Math.PI;
      let o = `<path d="${lin}" transform="translate(${SOM} ${SOM})" fill="none" stroke="${INK}" stroke-width="26" stroke-linecap="round" stroke-linejoin="round" opacity=".22" filter="url(#somS)"/><path d="${lin}" fill="none" stroke="${c}" stroke-width="26" stroke-linecap="round" stroke-linejoin="round"/>` +
        `<g transform="translate(${cur[0].toFixed(1)} ${cur[1].toFixed(1)}) rotate(${a.toFixed(1)})"><path d="M-6 -36 L46 0 L-6 36 Z" fill="${c}" stroke="${INK}" stroke-width="4" stroke-linejoin="round"/></g>`;
      for (let i = 0; i < 3; i++) { const fx = frac(L * 1.4 + i / 3); o += `<path d="M${(cur[0] - 70 - 60 * fx).toFixed(1)} ${(cur[1] + (i - 1) * 26 + (sube ? 30 : -30)).toFixed(1)} h${-40 * (1 - fx)}" stroke="${INK}" stroke-width="3" stroke-linecap="round" opacity="${((1 - fx) * p).toFixed(2)}"/>`; }
      const size = HOR ? 46 : 36, max = HOR ? 20 : 24, xT = HOR ? Z.x + 600 + (Z.w - 600) / 2 : ZC.x, yN = HOR ? ZC.y - 20 : y0 + 100;
      return o + `<g transform="translate(${xT} ${yN}) scale(${back((L - .7) / .4).toFixed(3)})">${tx(0, 0, esc(contar(String(v.valor || ''), eo((L - .6) / .6))), HOR ? 110 : 96, c === ORO ? INK : c, 'middle', 900, `letter-spacing="-3" stroke="${INK}" stroke-width="3" paint-order="stroke"`)}</g>` +
        (v.texto ? cinetico(v.texto, xT, yN + (HOR ? 74 : 70), size, L, { max, t0: .8 }) : '');
    },
    // monedas que caen y se apilan + cantidad  {"tipo":"dinero","valor":"1.150 €","texto":"…"}
    dinero(v, L, d) {
      const pilas = HOR ? 4 : 3, por = 6, cw = HOR ? 110 : 120, ch = 22, bx = HOR ? Z.x + 60 : ZC.x - (pilas * cw + (pilas - 1) * 16) / 2, by = HOR ? ZC.y + 150 : Z.y + 300;
      let o = '';
      for (let j = 0; j < pilas; j++) for (let i = 0; i < por - (j % 2); i++) {
        const t0 = .15 + (i * pilas + j) * .045, q = cl((L - t0) / .32); if (q <= 0) continue;
        const caida = (1 - eo(q)) * 260, rebote = q < 1 ? 0 : 0, x = bx + j * (cw + 16) + cw / 2, y = by - i * ch - caida + rebote;
        o += `<g opacity="${cl(q * 3).toFixed(2)}"><ellipse cx="${x}" cy="${(y + 8).toFixed(1)}" rx="${cw / 2}" ry="${ch * .55}" fill="${INK}"/><rect x="${x - cw / 2}" y="${(y - 4).toFixed(1)}" width="${cw}" height="12" fill="#e0a800" stroke="${INK}" stroke-width="2.5"/><ellipse cx="${x}" cy="${(y - 4).toFixed(1)}" rx="${cw / 2}" ry="${ch * .55}" fill="${ORO}" stroke="${INK}" stroke-width="2.5"/><ellipse cx="${x}" cy="${(y - 4).toFixed(1)}" rx="${cw / 2 - 14}" ry="${ch * .32}" fill="none" stroke="#e0a800" stroke-width="3"/></g>`;
      }
      const brillo = frac(L / 1.6); o += `<path d="M${(bx - 40 + (pilas * cw + 80) * brillo).toFixed(1)} ${by - por * ch - 30} l40 0 l-60 ${por * ch + 40} l-40 0 Z" fill="#fff" opacity=".35"/>`;
      const size = HOR ? 46 : 36, max = HOR ? 20 : 24, xT = HOR ? Z.x + 620 + (Z.w - 620) / 2 : ZC.x, yN = HOR ? ZC.y - 10 : by + 120;
      return o + `<g transform="translate(${xT} ${yN}) scale(${back((L - .5) / .4).toFixed(3)})">${tx(0, 0, esc(contar(String(v.valor || ''), eo((L - .4) / .9))), HOR ? 104 : 92, INK, 'middle', 900, 'letter-spacing="-3"')}</g>` +
        (v.texto ? cinetico(v.texto, xT, yN + (HOR ? 72 : 66), size, L, { max, t0: .8 }) : '');
    },
    // reloj con agujas que giran hasta la hora  {"tipo":"reloj","hora":"21:55","texto":"…"}
    reloj(v, L, d) {
      const m = String(v.hora || '').match(/(\d{1,2})[:.h ]?(\d{2})?/), hh = m ? +m[1] % 24 : 12, mm = m && m[2] ? +m[2] : 0, p = eio(cl((L - .15) / 1.1));
      const cx = HOR ? Z.x + 220 : ZC.x, cy = HOR ? ZC.y : Z.y + 190, r = HOR ? 150 : 160, e = back(L / .4);
      const aM = (360 * 2 + mm * 6) * p, aH = ((hh % 12) * 30 + mm * .5) * p, aS = L * 360 / 1.2;
      let o = `<g transform="translate(${cx} ${cy}) scale(${e.toFixed(3)})"><circle cx="${SOM}" cy="${SOM}" r="${r}" fill="${INK}" opacity=".22" filter="url(#somS)"/><circle r="${r}" fill="${BLA}" stroke="${INK}" stroke-width="8"/>`;
      for (let i = 0; i < 12; i++) { const a = i * Math.PI / 6; o += `<path d="M${((r - 18) * Math.sin(a)).toFixed(1)} ${(-(r - 18) * Math.cos(a)).toFixed(1)} L${((r - (i % 3 ? 32 : 44)) * Math.sin(a)).toFixed(1)} ${(-(r - (i % 3 ? 32 : 44)) * Math.cos(a)).toFixed(1)}" stroke="${INK}" stroke-width="${i % 3 ? 4 : 8}" stroke-linecap="round"/>`; }
      o += `<g transform="rotate(${aH.toFixed(1)})"><path d="M-9 14 L0 ${-r * .5} L9 14 Z" fill="${INK}"/></g><g transform="rotate(${aM.toFixed(1)})"><path d="M-6 16 L0 ${-r * .78} L6 16 Z" fill="${INK}"/></g>` +
        `<g transform="rotate(${aS.toFixed(1)})"><path d="M0 22 V${-r * .82}" stroke="${ORA}" stroke-width="4"/></g><circle r="14" fill="${ORA}" stroke="${INK}" stroke-width="2.5"/></g>`;
      const hs = `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}`, size = HOR ? 46 : 36, max = HOR ? 20 : 24;
      return o + peg(cx, cy + r + (HOR ? 46 : 52), hs + (/h/i.test(String(v.hora || '')) || true ? ' H' : ''), HOR ? 40 : 40, INK, ORO, 'middle', eo((L - 1.1) / .2), -2, back((L - 1.1) / .35)) +
        (v.texto ? cinetico(v.texto, HOR ? Z.x + 450 + (Z.w - 450) / 2 : ZC.x, HOR ? ZC.y - altoCin(v.texto, size, max) / 2 + size * .8 : cy + r + 130, size, L, { max, t0: .5 }) : '');
    },
    // lista de comprobación con ✓ y ✗  {"tipo":"checklist","titulo":"…","items":[{"texto":"…","ok":true},{"texto":"…","ok":false}]}
    checklist(v, L, d, k) {
      const it = (v.items || []).slice(0, 4), T0 = entradas(k, it.map(q => String((q || {}).texto || q)), d, .25), n = it.length || 1, hT = v.titulo ? (HOR ? 70 : 80) : 0, ah = Math.min(HOR ? 76 : 84, (Z.h - hT) / n - 18), y0 = Z.y + hT + (Z.h - hT - n * (ah + 18)) / 2;
      let o = v.titulo ? cinetico(v.titulo, ZC.x, Z.y + (HOR ? 44 : 56), HOR ? 40 : 36, L, { max: HOR ? 46 : 28 }) : '';
      it.forEach((q, i) => {
        const t0 = T0[i], e = back((L - t0) / .4);
        if (L < t0 + .12) o += hueco(Z.x + 10, y0 + i * (ah + 18), Z.w - 20, ah, ah * .28, '', L);
        if (e <= 0) return;
        const y = y0 + i * (ah + 18), ok = q.ok !== false && q.ok !== 'false', c = ok ? VER : ROJ, s = String(q.texto || ''), fs = Math.min(ah * .4, (Z.w - ah - 60) / (Math.max(8, s.length) * .56));
        const pm = eo((L - t0 - .25) / .3), bxx = Z.x + 10, cxk = bxx + ah / 2, cyk = y + ah / 2, rr = ah * .3;
        const marca = ok ? `<path d="M${cxk - rr * .6} ${cyk} l${rr * .45} ${rr * .5} l${rr * .85} ${-rr * .95}" fill="none" stroke="#fff" stroke-width="${ah * .12}" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="${(1 - pm).toFixed(3)}"/>`
          : `<path d="M${cxk - rr * .55} ${cyk - rr * .55} l${rr * 1.1} ${rr * 1.1} M${cxk + rr * .55} ${cyk - rr * .55} l${-rr * 1.1} ${rr * 1.1}" fill="none" stroke="#fff" stroke-width="${ah * .12}" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="${(1 - pm).toFixed(3)}"/>`;
        o += `<g transform="translate(${((1 - e) * 240).toFixed(1)} 0)" opacity="${cl((L - t0) / .12)}">` + caja(bxx, y, Z.w - 20, ah, ah * .28, BLA) +
          `<rect x="${cxk - ah * .36}" y="${cyk - ah * .36}" width="${ah * .72}" height="${ah * .72}" rx="${ah * .16}" fill="${pm > 0 ? c : BLA}" stroke="${INK}" stroke-width="4"/>` + marca +
          tx(bxx + ah + 10, cyk + fs * .36, esc(s), fs, INK, 'start', 800) + `</g>`;
      });
      return o;
    },
    // semáforo de alerta (amarillo, naranja, rojo)  {"tipo":"alerta","nivel":"rojo","texto":"…"}
    alerta(v, L, d) {
      const niv = /roj/i.test(v.nivel) ? 2 : /naranj/i.test(v.nivel) ? 1 : 0, cs = [ORO, ORA, ROJ], nm = ['AMARILLO', 'NARANJA', 'ROJO'];
      const cx = HOR ? Z.x + 200 : ZC.x - (HOR ? 0 : 150), cy = HOR ? ZC.y : Z.y + 200, w = 130, h = 360, e = back(L / .4), on = L > .5 + niv * .25;
      let o = '';
      if (on) { const rot = L * 40; let rays = ''; for (let i = 0; i < 10; i++) { const a0 = (i / 10) * Math.PI * 2 + rot * Math.PI / 180, a1 = a0 + Math.PI / 12, Rr = 300; rays += `M0 0L${(Rr * Math.cos(a0)).toFixed(0)} ${(Rr * Math.sin(a0)).toFixed(0)}L${(Rr * Math.cos(a1)).toFixed(0)} ${(Rr * Math.sin(a1)).toFixed(0)}Z`; }
        o += `<g transform="translate(${cx} ${cy - h / 2 + 60 + (2 - niv) * 110})"><path d="${rays}" fill="${cs[niv]}" opacity="${(.18 + .08 * Math.sin(L * 8)).toFixed(3)}"/></g>`; }
      o += `<g transform="translate(${cx} ${cy}) scale(${e.toFixed(3)}) translate(${-cx} ${-cy})">` + caja(cx - w / 2, cy - h / 2, w, h, 34, INK, 5);
      for (let i = 0; i < 3; i++) {
        const lvl = 2 - i, yy = cy - h / 2 + 60 + i * 110, act = lvl === niv && on, lit = act || (lvl < niv && L > .5 + lvl * .25 && L < .5 + niv * .25);   // se van encendiendo hasta su nivel y queda solo esa
        o += `<circle cx="${cx}" cy="${yy}" r="44" fill="${lit ? cs[lvl] : '#3b3640'}" stroke="${BLA}" stroke-width="4" opacity="1"/>` + (act ? `<circle cx="${cx}" cy="${yy}" r="${(48 + 14 * frac(L * 1.5)).toFixed(1)}" fill="none" stroke="${cs[lvl]}" stroke-width="6" opacity="${(1 - frac(L * 1.5)).toFixed(2)}"/>` : '');
      }
      o += `</g>`;
      const size = HOR ? 46 : 34, max = HOR ? 20 : 12, xT = HOR ? Z.x + 420 + (Z.w - 420) / 2 : cx + w / 2 + 25 + (Z.x + Z.w - cx - w / 2 - 25) / 2;
      return o + peg(xT, HOR ? ZC.y - 40 : cy - 60, 'AVISO ' + nm[niv], HOR ? 46 : 32, cs[niv], niv === 0 ? INK : '#fff', 'middle', on ? 1 : 0, -3, back((L - .5 - niv * .25) / .35)) +
        (v.texto ? cinetico(v.texto, xT, HOR ? ZC.y + 40 : cy + 10, size, L, { max, t0: .9 }) : '');
    },
    // hemiciclo de escaños  {"tipo":"escanos","partidos":[{"nombre":"PP","valor":"137","color":"azul"},…],"texto":"…"}
    escanos(v, L, d) {
      const ps = (v.partidos || []).slice(0, 7).map((q, i) => ({ n: String(q.nombre || ''), s: Math.max(0, Math.round(num(q.valor))), c: q.color ? col(q.color) : [AZU, ROJ, VER, MOR, ORO, ORA, INK][i] }));
      const tot = Math.min(400, ps.reduce((a, b) => a + b.s, 0)) || 1, filas = tot > 200 ? 9 : 7, cx = HOR ? Z.x + 310 : ZC.x, cy = HOR ? ZC.y + 150 : Z.y + 330, R1 = HOR ? 250 : 262, R0 = R1 * .42;
      const rad = [...Array(filas).keys()].map(i => R0 + (R1 - R0) * i / (filas - 1)), sumR = rad.reduce((a, b) => a + b, 0);
      let asientos = []; let quedan = tot;
      rad.forEach((rr, i) => { const nfila = i === filas - 1 ? quedan : Math.round(tot * rr / sumR); quedan -= nfila; for (let j = 0; j < nfila; j++) { const a = Math.PI * (1 - (j + .5) / nfila); asientos.push([a, rr]); } });
      asientos.sort((a, b) => b[0] - a[0] || a[1] - b[1]);
      const dr = Math.min(11, (R1 - R0) / filas * .42), p = eio(cl((L - .2) / 1.2)), vis = Math.floor(asientos.length * p);
      let o = '', k = 0;
      ps.forEach(q => { for (let j = 0; j < q.s && k < asientos.length; j++, k++) { const [a, rr] = asientos[k]; if (k >= vis) continue; o += `<circle cx="${(cx + rr * Math.cos(a)).toFixed(1)}" cy="${(cy - rr * Math.sin(a)).toFixed(1)}" r="${dr.toFixed(1)}" fill="${q.c}" stroke="${INK}" stroke-width="1.5"/>`; } });
      const may = Math.floor(tot / 2) + 1;
      if (tot >= 50) o += `<path d="M${cx} ${cy - R1 - 26} V${cy - R0 + 20}" stroke="${INK}" stroke-width="2.5" stroke-dasharray="8 6" opacity="${eo((L - 1.2) / .3).toFixed(2)}"/>` + peg(cx, cy - R1 - 34, `MAYORÍA ${may}`, HOR ? 22 : 22, INK, '#fff', 'middle', eo((L - 1.2) / .3), 0);
      const lx = HOR ? Z.x + 660 : Z.x + 10, ly = HOR ? ZC.y - ps.length * 24 : cy + 50, fs = HOR ? 30 : 26, col2 = !HOR && ps.length > 3;
      ps.forEach((q, i) => {
        const t0 = .4 + i * .15, e = back((L - t0) / .35); if (e <= 0) return;
        const x = col2 ? lx + (i % 2) * (Z.w / 2) : lx, y = ly + (col2 ? Math.floor(i / 2) : i) * (HOR ? 50 : 44);
        o += `<g opacity="${cl((L - t0) / .15)}"><circle cx="${x + 14}" cy="${y - fs * .35}" r="13" fill="${q.c}" stroke="${INK}" stroke-width="3"/>` + tx(x + 38, y, esc(q.n), fs, INK, 'start', 800) +
          tx(x + (col2 ? Z.w / 2 - 30 : (HOR ? Z.x + Z.w - lx - 10 : Z.w - 30)), y, esc(contar(String(q.s), eo((L - t0) / .8))), fs, INK, 'end', 900) + `</g>`;
      });
      const size = HOR ? 40 : 32;
      return o + (v.texto ? cinetico(v.texto, HOR ? cx : ZC.x, HOR ? cy + 70 : ly + Math.ceil(ps.length / (col2 ? 2 : 1)) * 44 + 30, size, L, { max: HOR ? 30 : 28, t0: 1 }) : '');
    },
    // ===== v59 (11-nov-2026): 8 gráficos animados más =====
    // contador de rodillos (tipo tragaperras)  {"tipo":"contador","valor":"4.815.000","texto":"…"}
    contador(v, L, d) {
      const s = String(v.valor || ''), cs = [...s], dig = cs.filter(c => /\d/.test(c)).length || 1, cw = Math.min(HOR ? 86 : 70, (Z.w - 10 - (cs.length - 1) * 6) / (dig + (cs.length - dig) * .5)), ch = cw * 1.45;
      const wT = cs.reduce((a, c) => a + (/\d/.test(c) ? cw : cw * .5), 0) + (cs.length - 1) * 6, x0 = ZC.x - wT / 2, yC = HOR ? ZC.y - 30 : Z.y + 170, e = back(L / .4);
      let x = x0, di = 0, o = `<g transform="translate(${ZC.x} ${yC}) scale(${e.toFixed(3)}) translate(${-ZC.x} ${-yC})">`;
      cs.forEach(c => {
        if (/\d/.test(c)) {
          const t1 = .4 + (dig - 1 - di) * .12 + .5, q = eo(cl((L - .2) / (t1 - .2))), fin = +c, giro = (1 - q) * (8 + di * 3), val = fin + giro, base = Math.floor(val), fr = val - base, id = `cr${di}${Math.round(x)}`;
          o += caja(x, yC - ch / 2, cw, ch, cw * .16, INK, 4, 5) + `<clipPath id="${id}"><rect x="${x}" y="${yC - ch / 2}" width="${cw}" height="${ch}" rx="${cw * .16}"/></clipPath><g clip-path="url(#${id})">` +
            tx(x + cw / 2, yC + cw * .36 + fr * ch, String(base % 10), cw, BLA) + tx(x + cw / 2, yC + cw * .36 + fr * ch - ch, String((base + 1) % 10), cw, BLA) +
            `</g><path d="M${x + 4} ${yC} H${x + cw - 4}" stroke="${BLA}" stroke-opacity=".15" stroke-width="3"/>`;
          x += cw + 6; di++;
        } else { o += tx(x + cw * .25, yC + cw * .36, esc(c), cw, INK); x += cw * .5 + 6; }
      });
      o += `</g>`;
      const size = HOR ? 46 : 38, max = HOR ? 30 : 24;
      return o + (v.texto ? cinetico(v.texto, ZC.x, yC + ch / 2 + (HOR ? 70 : 80), size, L, { max, t0: .9 }) : '');
    },
    // pasos de un proceso unidos por flechas  {"tipo":"pasos","items":["Pides cita","Te llaman","Cobras"]}
    pasos(v, L, d, k) {
      const it = (v.items || []).slice(0, 4), n = it.length || 1, tramo = Math.max(.45, (d - .6) / n), T0 = entradas(k, it.map(q => String((q || {}).texto || q)), d, .2, tramo);
      const hB = HOR ? 150 : 96, wB = HOR ? (Z.w - (n - 1) * 70) / n : Z.w - 40, gap = HOR ? 70 : Math.min(54, (Z.h - n * hB) / Math.max(1, n - 1));
      const tot = HOR ? Z.w : n * hB + (n - 1) * gap, y0 = HOR ? ZC.y - hB / 2 : ZC.y - tot / 2;
      let o = '';
      it.forEach((s, i) => {
        const t0 = T0[i], e = back((L - t0) / .4); if (e <= 0) return;
        const x = HOR ? Z.x + i * (wB + 70) : ZC.x - wB / 2, y = HOR ? y0 : y0 + i * (hB + gap), act = i === n - 1 || L < T0[i + 1], c = [ORA, AZU, VER, MOR][i % 4], cx = x + wB / 2, cy = y + hB / 2;
        const fs = Math.min(HOR ? 34 : 32, (wB - (HOR ? 40 : 110)) / (Math.max(6, String(s).length) * .55));
        o += `<g transform="translate(${cx} ${cy}) scale(${(e * (act ? 1 + .03 * Math.sin(L * 6) : 1)).toFixed(3)}) translate(${-cx} ${-cy})">` + caja(x, y, wB, hB, 24, act ? c : BLA, 5) +
          `<circle cx="${HOR ? cx : x + 50}" cy="${HOR ? y : cy}" r="30" fill="${BLA}" stroke="${INK}" stroke-width="3"/>` + tx(HOR ? cx : x + 50, (HOR ? y : cy) + 12, String(i + 1), 34, c) +
          tx(HOR ? cx : x + 96, HOR ? cy + 26 : cy + fs * .36, esc(s), fs, act && c !== ORO ? '#fff' : INK, HOR ? 'middle' : 'start', 800) + `</g>`;
        if (i < n - 1) {
          const pa = eo((L - T0[i + 1] + .3) / .3); if (pa <= 0) return;
          o += HOR ? `<path d="M${x + wB + 10} ${cy} h${(50 * pa).toFixed(1)}" stroke="${INK}" stroke-width="8" stroke-linecap="round"/>` + (pa > .9 ? `<path d="M${x + wB + 52} ${cy - 14} l16 14 l-16 14" fill="none" stroke="${INK}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>` : '')
            : `<path d="M${cx} ${y + hB + 8} v${((gap - 22) * pa).toFixed(1)}" stroke="${INK}" stroke-width="4.5" stroke-linecap="round"/>` + (pa > .9 ? `<path d="M${cx - 13} ${y + hB + gap - 26} l13 14 l13 -14" fill="none" stroke="${INK}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>` : '');
        }
      });
      return o;
    },
    // termómetro que se llena  {"tipo":"termometro","valor":"38 °C","max":"45","texto":"…"}
    termometro(v, L, d) {
      const mx = num(v.max) || 45, mn = num(v.min) || 0, pr = cl((num(v.valor) - mn) / (mx - mn)), p = eo(cl((L - .2) / 1)), cx = HOR ? Z.x + 200 : ZC.x - 130, top = HOR ? Z.y + 20 : Z.y + 40, hT = HOR ? 280 : 380, w = 56, rb = 58, by = top + hT + rb * .6;
      const c = pr > .66 ? ROJ : pr > .33 ? ORA : AZU, yF = top + hT - (hT - 10) * pr * p, e = back(L / .4);
      let o = `<g transform="translate(${cx} ${by}) scale(${e.toFixed(3)}) translate(${-cx} ${-by})">` +
        `<rect x="${cx - w / 2 + SOM}" y="${top + SOM}" width="${w}" height="${hT}" rx="${w / 2}" fill="${INK}" opacity=".22" filter="url(#somS)"/><circle cx="${cx + SOM}" cy="${by + SOM}" r="${rb}" fill="${INK}" opacity=".22" filter="url(#somS)"/>` +
        `<rect x="${cx - w / 2}" y="${top}" width="${w}" height="${hT}" rx="${w / 2}" fill="${BLA}" stroke="${INK}" stroke-width="4"/>` +
        `<rect x="${cx - w / 2 + 12}" y="${yF.toFixed(1)}" width="${w - 24}" height="${(top + hT - yF + 20).toFixed(1)}" rx="${(w - 24) / 2}" fill="${c}"/>` +
        `<circle cx="${cx}" cy="${by}" r="${rb}" fill="${c}" stroke="${INK}" stroke-width="4"/><path d="M${cx - 20} ${by - 20} a28 28 0 0 1 22 -12" stroke="#fff" stroke-width="7" fill="none" stroke-linecap="round" opacity=".6"/>`;
      for (let i = 1; i < 5; i++) { const y = top + hT * i / 5; o += `<path d="M${cx + w / 2 + 4} ${y} h18" stroke="${INK}" stroke-width="2.5"/>`; }
      o += `</g>`;
      const xT = HOR ? Z.x + 380 + (Z.w - 380) / 2 : ZC.x + 110, size = HOR ? 46 : 34, max = HOR ? 22 : 14;
      return o + `<g transform="translate(${xT} ${HOR ? ZC.y - 20 : Z.y + 220}) scale(${back((L - .5) / .4).toFixed(3)})">${tx(0, 0, esc(contar(String(v.valor || ''), p)), HOR ? 110 : 84, c, 'middle', 900, `stroke="${INK}" stroke-width="3" paint-order="stroke" letter-spacing="-3"`)}</g>` +
        (v.texto ? cinetico(v.texto, xT, (HOR ? ZC.y + 60 : Z.y + 300), size, L, { max, t0: .8 }) : '');
    },
    // batería que se carga o se vacía  {"tipo":"bateria","valor":"23 %","texto":"…"}
    bateria(v, L, d) {
      const pr = cl(num(v.valor) / 100), p = eo(cl((L - .2) / 1.1)), w = HOR ? 380 : 420, h = HOR ? 180 : 190, x = HOR ? Z.x + 30 : ZC.x - w / 2 - 14, y = HOR ? ZC.y - h / 2 : Z.y + 60, e = back(L / .4);
      const c = pr < .25 ? ROJ : pr < .6 ? ORO : VER, segs = 5, fl = pr * p, cx = x + w / 2, cy = y + h / 2;
      let o = `<g transform="translate(${cx} ${cy}) scale(${e.toFixed(3)}) translate(${-cx} ${-cy})">` + caja(x, y, w, h, 30, BLA, 7) + `<rect x="${x + w + 4}" y="${cy - 36}" width="26" height="72" rx="10" fill="${INK}"/>`;
      for (let i = 0; i < segs; i++) {
        const sw = (w - 36 - (segs - 1) * 10) / segs, sx = x + 18 + i * (sw + 10), lleno = cl(fl * segs - i), parp = pr < .25 && i === 0 ? .55 + .45 * Math.sin(L * 9) : 1;
        if (lleno > 0) o += `<rect x="${sx}" y="${y + 18}" width="${(sw * lleno).toFixed(1)}" height="${h - 36}" rx="10" fill="${c}" opacity="${parp.toFixed(2)}"/>`;
      }
      o += `</g>` + `<g transform="translate(${cx} ${cy + 20})">${tx(0, 0, esc(contar(String(v.valor || ''), p)), HOR ? 74 : 76, INK, 'middle', 900, `stroke="${BLA}" stroke-width="10" paint-order="stroke"`)}</g>`;
      const size = HOR ? 46 : 38, max = HOR ? 20 : 24;
      return o + (v.texto ? cinetico(v.texto, HOR ? Z.x + 480 + (Z.w - 480) / 2 : ZC.x, HOR ? ZC.y - altoCin(v.texto, size, max) / 2 + size * .8 : y + h + 90, size, L, { max, t0: .7 }) : '');
    },
    // Lupi con la lupa sobre la letra pequeña  {"tipo":"lupa","titulo":"La letra pequeña","texto":"≤ 50 caracteres: el detalle"}
    lupa(v, L, d) {
      const w = HOR ? 620 : Z.w - 10, h = HOR ? 330 : 340, x = HOR ? Z.x + 20 : ZC.x - w / 2, y = HOR ? ZC.y - h / 2 : Z.y + 10, e = back(L / .45), lineas = 7, fila = 4;
      let o = `<g transform="translate(${x + w / 2} ${y + h / 2}) rotate(-2) scale(${e.toFixed(3)}) translate(${-(x + w / 2)} ${-(y + h / 2)})">` + caja(x, y, w, h, 10, '#fbf8f0', 4) +
        (v.titulo ? tx(x + 30, y + 54, esc(v.titulo), HOR ? 34 : 32, INK, 'start', 900) : '');
      for (let i = 0; i < lineas; i++) { const yy = y + 90 + i * ((h - 120) / lineas); o += i === fila ? `<rect x="${x + 30}" y="${yy - 6}" width="${(w - 60) * eo((L - .9) / .4)}" height="16" rx="4" fill="${ORO}"/><rect x="${x + 30}" y="${yy}" width="${w - 60}" height="5" rx="2" fill="${INK}" opacity=".5"/>` : `<rect x="${x + 30}" y="${yy}" width="${(w - 60) * (i % 3 === 2 ? .7 : 1)}" height="5" rx="2" fill="${INK}" opacity=".16"/>`; }
      o += `</g>`;
      const yF = y + 90 + fila * ((h - 120) / lineas), q = eio(cl((L - .2) / .8)), lx = x + 80 + (w * .55 - 80) * q + 20 * Math.sin(L * 2), ly = yF - 20 + 8 * Math.sin(L * 3);
      o += `<g transform="translate(${lx.toFixed(1)} ${ly.toFixed(1)}) rotate(-25) scale(${HOR ? .95 : 1})">${lupiM({ x: 0, y: 0, s: 1, t: L, expr: 'curiosa', mira: [0, .6] })}</g>`;
      const size = HOR ? 44 : 36, max = HOR ? 18 : 24;
      return o + (v.texto ? cinetico(v.texto, HOR ? x + w + (Z.x + Z.w - x - w) / 2 : ZC.x, HOR ? ZC.y - altoCin(v.texto, size, max) / 2 + size * .8 : y + h + 66, size, L, { max, t0: 1 }) : '');
    },
    // encuesta con barras  {"tipo":"encuesta","pregunta":"¿…?","opciones":[{"texto":"Sí","valor":"58 %"},{"texto":"No","valor":"42 %"}],"fuente":"CIS"}
    encuesta(v, L, d) {
      const op = (v.opciones || []).slice(0, 4), n = op.length || 1, mx = Math.max(...op.map(q => num(q.valor)), 1e-9), hP = v.pregunta ? (HOR ? 90 : 120) : 0;
      const ah = Math.min(HOR ? 66 : 80, (Z.h - hP - 30) / n - 18), y0 = Z.y + hP + 10, gan = op.reduce((b, q, i) => num(q.valor) > num(op[b].valor) ? i : b, 0);
      let o = v.pregunta ? cinetico(v.pregunta, ZC.x, Z.y + (HOR ? 46 : 54), HOR ? 42 : 36, L, { max: HOR ? 40 : 24 }) : '';
      op.forEach((q, i) => {
        const t0 = .3 + i * .15, p = eio(cl((L - t0) / .9)), y = y0 + i * (ah + 18), win = i === gan && p > .99, fs = Math.min(ah * .4, 34);
        o += caja(Z.x + 6, y, Z.w - 20, ah, ah * .3, BLA, 4) + `<rect x="${Z.x + 6}" y="${y}" width="${((Z.w - 20) * num(q.valor) / mx * .98 * p).toFixed(1)}" height="${ah}" rx="${ah * .3}" fill="${win ? ORA : GRI}" opacity="${win ? 1 : .8}"/>` +
          tx(Z.x + 30, y + ah / 2 + fs * .36, esc(q.texto || ''), fs, win ? '#fff' : INK, 'start', 800) + tx(Z.x + Z.w - 34, y + ah / 2 + fs * .36, esc(contar(String(q.valor || ''), p)), fs, INK, 'end', 900) +
          (win ? `<circle cx="${Z.x + Z.w - 14}" cy="${y}" r="${(16 * back((L - t0 - .95) / .3)).toFixed(1)}" fill="${VER}" stroke="${INK}" stroke-width="2.5"/>` : '');
      });
      return o + (v.fuente ? peg(Z.x + Z.w - 16, y0 + n * (ah + 18) + 24, 'FUENTE: ' + String(v.fuente).toUpperCase(), HOR ? 20 : 18, INK, '#fff', 'end', eo((L - .8) / .3), 0) : '');
    },
    // ÚLTIMA HORA: banda roja con destello y cinta de texto  {"tipo":"ultimahora","texto":"≤ 60 caracteres","cinta":"frase que pasa abajo"}
    ultimahora(v, L, d) {
      const e = back(L / .35), fl = Math.sin(L * 10) > 0 ? 1 : .75, yB = HOR ? Z.y + 40 : Z.y + 40, hB = HOR ? 90 : 84, size = HOR ? 56 : 44, max = HOR ? 26 : 18, alto = altoCin(v.texto, size, max);
      let o = `<g transform="translate(${ZC.x} ${yB + hB / 2}) rotate(-3) scale(${e.toFixed(3)}) translate(${-ZC.x} ${-(yB + hB / 2)})">` + caja(Z.x - 6, yB, Z.w + 12, hB, 14, ROJ, 5) +
        `<circle cx="${Z.x + 40}" cy="${yB + hB / 2}" r="14" fill="#fff" opacity="${fl}"/>` + tx(Z.x + 70, yB + hB / 2 + (HOR ? 18 : 16), 'ÚLTIMA HORA', HOR ? 50 : 44, '#fff', 'start', 900, 'letter-spacing="1"') + `</g>`;
      o += cinetico(v.texto, ZC.x, yB + hB + (HOR ? 90 : 110), size, L, { max, t0: .3 });
      const yC = HOR ? Z.y + Z.h - 30 : yB + hB + 110 + alto + 40, cinta = (String(v.cinta || v.texto || '') + '   •   ').toUpperCase(), wc = cinta.length * (HOR ? 15 : 14.5), off = (L * 140) % wc;
      return o + `<clipPath id="ci"><rect x="${Z.x - 6}" y="${yC - 30}" width="${Z.w + 12}" height="48"/></clipPath><rect x="${Z.x - 6}" y="${yC - 30}" width="${Z.w + 12}" height="48" fill="${INK}" opacity="${eo((L - .5) / .3).toFixed(2)}"/>` +
        `<g clip-path="url(#ci)" opacity="${eo((L - .5) / .3).toFixed(2)}">${[0, 1, 2].map(j => tx(Z.x - off + j * wc, yC + 2, esc(cinta), HOR ? 26 : 25, ORO, 'start', 900)).join('')}</g>`;
    },
    // v75: mapa del mundo con zoom desde el planeta hasta los países de la noticia  {"tipo":"mundo","paises":["Ucrania","Rusia"],"texto":"≤ 30"}
    mundo(v, L, d) {
      const M = window.MUNDO; if (!M) return this.icono({ icono: 'globo', texto: v.texto || '' }, L, d);
      if (!M._bb) M._bb = M.p.map(p => p[3].map(r => { let a = 1e9, b = -1e9, c = 1e9, e = -1e9; for (let i = 0; i < r.length; i += 2) { a = Math.min(a, r[i]); b = Math.max(b, r[i]); c = Math.min(c, r[i + 1]); e = Math.max(e, r[i + 1]); } return [a / 10, b / 10, c / 10, e / 10]; }));
      const busca = s => { let n = norm(s); n = M.al[n] || n; return M.p.findIndex(p => p[0].split('|').includes(n) || p[1] === n); };
      const sel = (v.paises || v.lugares || []).map(s => [s, busca(s)]).filter(x => x[1] >= 0).slice(0, 3);
      const bx = HOR ? Z.x + 10 : Z.x, by = HOR ? Z.y + 26 : Z.y + 4, bw = HOR ? 700 : Z.w, bh = HOR ? Z.h - 40 : (v.texto ? Z.h - 120 : Z.h - 40);
      // caja objetivo: la de la parte principal de los países elegidos, con margen
      let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
      sel.forEach(([, i]) => { const b = M.p[i][4]; if (b) { x0 = Math.min(x0, b[0] / 10); x1 = Math.max(x1, b[1] / 10); y0 = Math.min(y0, b[2] / 10); y1 = Math.max(y1, b[3] / 10); } });
      if (!sel.length) { x0 = -10; x1 = 30; y0 = 35; y1 = 60; }
      const cxT = (x0 + x1) / 2, cyT = (y0 + y1) / 2, co = Math.cos(cyT * Math.PI / 180);
      const spanX = Math.max(22, (x1 - x0) * 1.7) * co, spanY = Math.max(16, (y1 - y0) * 1.7), kT = Math.min(bw / spanX, bh / spanY);
      const kW = Math.min(bw / (340 * co), bh / 150), q = eio(cl((L - .15) / 1.3));
      const k = Math.exp(Math.log(kW) + (Math.log(kT) - Math.log(kW)) * q), clon = 10 + (cxT - 10) * q, clat = 25 + (cyT - 25) * q;
      const P = (lo, la) => [bx + bw / 2 + (lo - clon) * co * k, by + bh / 2 - (la - clat) * k];
      const vx0 = clon - bw / 2 / (co * k), vx1 = clon + bw / 2 / (co * k), vy0 = clat - bh / 2 / k, vy1 = clat + bh / 2 / k;
      const elegido = new Set(sel.map(x => x[1])), e = back(L / .45);
      let paths = '', hl = '';
      M.p.forEach((p, i) => p[3].forEach((r, j) => {
        const b = M._bb[i][j]; if (b[1] < vx0 || b[0] > vx1 || b[3] < vy0 || b[2] > vy1) return;
        let dd = ''; for (let n = 0; n < r.length; n += 2) { const [x, y] = P(r[n] / 10, r[n + 1] / 10); dd += (n ? 'L' : 'M') + x.toFixed(1) + ' ' + y.toFixed(1); }
        if (elegido.has(i)) hl += dd + 'Z'; else paths += dd + 'Z';
      }));
      const cid = 'mundoClip' + (HOR ? 'h' : 'v'), fe = eo((L - .9) / .5);
      let o = `<g transform="translate(${bx + bw / 2} ${by + bh / 2}) scale(${e.toFixed(3)}) translate(${-(bx + bw / 2)} ${-(by + bh / 2)})">` +
        `<clipPath id="${cid}"><rect x="${bx}" y="${by}" width="${bw}" height="${bh}" rx="26"/></clipPath>` +
        caja(bx, by, bw, bh, 26, '#d6ebf7', 3) +
        `<g clip-path="url(#${cid})"><path d="${paths}" fill="${BLA}" stroke="${INK}" stroke-width="1.2" stroke-linejoin="round" opacity=".95"/>` +
        `<path d="${hl}" fill="${ORA}" fill-opacity="${(.25 + .75 * fe).toFixed(2)}" stroke="${INK}" stroke-width="2.2" stroke-linejoin="round"/></g>` +
        `<rect x="${bx}" y="${by}" width="${bw}" height="${bh}" rx="26" fill="none" stroke="${INK}" stroke-width="3"/></g>`;
      sel.forEach(([nom, i], n) => {
        const t0 = 1.3 + n * .3, ep = back((L - t0) / .4); if (ep <= 0) return;
        const [x, y] = P(...M.p[i][2]); if (x < bx + 20 || x > bx + bw - 20 || y < by + 30 || y > by + bh - 10) return;
        const cerca = sel.some(([, j], m) => m < n && Math.hypot(P(...M.p[j][2])[0] - x, P(...M.p[j][2])[1] - y) < 110), izq = cerca ? !(x > bx + bw * .62) && x > bx + 150 || x > bx + bw * .62 && !cerca : x > bx + bw * .62;
        o += `<g transform="translate(${x.toFixed(1)} ${y.toFixed(1)}) scale(${(ep * (HOR ? .5 : .5)).toFixed(3)})"><path d="M0 0 C-30 -40 -40 -55 -40 -75 A40 40 0 0 1 40 -75 C40 -55 30 -40 0 0 Z" fill="${ROJ}" stroke="${INK}" stroke-width="4.5"/><circle cy="-75" r="14" fill="${BLA}" stroke="${INK}" stroke-width="3"/></g>` +
          peg(x + (izq ? -24 : 24), y - (cerca ? 2 : 50), String(nom).toUpperCase(), 20, INK, '#fff', izq ? 'end' : 'start', eo((L - t0 - .2) / .2), cerca ? 3 : -3);
      });
      const size = HOR ? 44 : 34, max = HOR ? 18 : 26;
      return o + (v.texto ? cinetico(v.texto, HOR ? bx + bw + (Z.x + Z.w - bx - bw) / 2 : ZC.x, HOR ? ZC.y - altoCin(v.texto, size, max) / 2 + size * .8 : by + bh + 66, size, L, { max, t0: .9 }) : '');
    },
    // v73: balanza que se inclina (dos posturas, sin tomar partido: se inclina solo si lo dicen los datos)
    // {"tipo":"balanza","izq":"≤ 18 caracteres","der":"≤ 18","inclina":"izq|der|igual","texto":"≤ 40, opcional"}
    balanza(v, L, d) {
      const cx = HOR ? Z.x + 330 : ZC.x, y0 = HOR ? Z.y + 70 : Z.y + 80, bw = HOR ? 520 : 430, cuelga = HOR ? 110 : 100, base = HOR ? Z.y + Z.h - 30 : Z.y + 330;
      const sen = /izq/.test(String(v.inclina)) ? -1 : /der/.test(String(v.inclina)) ? 1 : 0, e = back(L / .45);
      const ang = sen * 9 * eio(cl((L - .7) / .9)) + 6 * Math.sin(L * 5.5) * Math.exp(-L * 1.4) * (L > .3 ? 1 : 0), ra = ang * Math.PI / 180;
      let o = `<g transform="translate(${cx} ${base}) scale(${e.toFixed(3)}) translate(${-cx} ${-base})">` +
        `<ellipse cx="${cx}" cy="${base + 8}" rx="${HOR ? 120 : 80}" ry="12" fill="${INK}" opacity=".18" filter="url(#somS)"/>` +
        `<path d="M${cx - (HOR ? 90 : 62)} ${base} L${cx + (HOR ? 90 : 62)} ${base} L${cx + 28} ${base - 26} L${cx - 28} ${base - 26} Z" fill="${INK}"/>` +
        `<rect x="${cx - 6}" y="${y0}" width="12" height="${base - y0 - 22}" rx="6" fill="${INK}"/>` +
        `<circle cx="${cx}" cy="${y0 - 6}" r="${HOR ? 18 : 13}" fill="${ORO}" stroke="${INK}" stroke-width="3"/>`;
      const plato = (lado, txt, col) => {
        const ex = cx + lado * bw / 2 * Math.cos(ra), ey = y0 + lado * bw / 2 * Math.sin(ra), py = ey + cuelga, pw = HOR ? 190 : 196;
        const ls = partir(String(txt || '').replace(/\*/g, ''), HOR ? 14 : 12).slice(0, 2), fs = HOR ? 26 : 24, ch = (HOR ? 26 : 20) + ls.length * fs * 1.15;
        return `<path d="M${ex} ${ey} L${ex - pw / 2 + 12} ${py} M${ex} ${ey} L${ex + pw / 2 - 12} ${py}" stroke="${INK}" stroke-width="3"/>` +
          caja(ex - pw / 2 + 10, py - ch - 4, pw - 20, ch, 12, col, 2.5) +
          ls.map((l, i) => tx(ex, py - ch - 4 + (HOR ? 13 : 10) + fs * .86 + i * fs * 1.15, esc(l), fs, '#fff', 'middle', 900)).join('') +
          `<path d="M${ex - pw / 2} ${py} Q${ex} ${py + (HOR ? 70 : 46)} ${ex + pw / 2} ${py} Z" fill="${col}" stroke="${INK}" stroke-width="3"/>`;
      };
      o += `<path d="M${cx - bw / 2 * Math.cos(ra)} ${y0 - bw / 2 * Math.sin(ra)} L${cx + bw / 2 * Math.cos(ra)} ${y0 + bw / 2 * Math.sin(ra)}" stroke="${INK}" stroke-width="${HOR ? 14 : 9}" stroke-linecap="round"/>` +
        plato(-1, v.izq, AZU) + plato(1, v.der, ORA) + `</g>`;
      const size = HOR ? 44 : 30, max = HOR ? 20 : 26;
      return o + (v.texto ? cinetico(v.texto, HOR ? Z.x + 700 + (Z.w - 700) / 2 : ZC.x, HOR ? ZC.y - altoCin(v.texto, size, max) / 2 + size * .8 : base + 62, size, L, { max, t0: 1.2 }) : '');
    },
    // v73: iceberg: lo que se ve arriba y lo que hay debajo (1-3 datos que aparecen al «bajar»)
    // {"tipo":"iceberg","arriba":"≤ 22 caracteres","abajo":["≤ 26","≤ 26","≤ 26"]}
    iceberg(v, L, d) {
      const cx = ZC.x, yW = HOR ? Z.y + 120 : Z.y + 130, fondo = HOR ? Z.y + Z.h + 10 : Z.y + Z.h - 10, e = eo(L / .5), sube = (1 - e) * 80;
      const ab = (Array.isArray(v.abajo) ? v.abajo : [v.abajo]).filter(Boolean).slice(0, 3), anchoB = HOR ? 760 : 560, pico = HOR ? 1 : .85;
      const ola = x => yW + 5 * Math.sin(x / 38 + L * 3);
      let olas = `M0 ${ola(0)}`; for (let x = 16; x <= W + 16; x += 16) olas += ` L${x} ${ola(x).toFixed(1)}`;
      let o = `<g transform="translate(0 ${sube.toFixed(1)})" opacity="${e.toFixed(2)}">` +
        // parte sumergida (grande) y punta (pequeña)
        `<path d="M${cx - 110 * pico} ${yW} L${cx - anchoB / 2} ${yW + (fondo - yW) * .45} L${cx - anchoB / 2 + 90} ${fondo - 20} L${cx + 60} ${fondo} L${cx + anchoB / 2 - 40} ${fondo - 50} L${cx + anchoB / 2} ${yW + (fondo - yW) * .35} L${cx + 120 * pico} ${yW} Z" fill="#eef8fd" stroke="${INK}" stroke-width="3" stroke-linejoin="round"/>` +
        `<path d="M${cx - 110 * pico} ${yW} L${cx - 30 * pico} ${yW - (HOR ? 100 : 96)} L${cx + 10 * pico} ${yW - (HOR ? 78 : 76)} L${cx + 50 * pico} ${yW - (HOR ? 112 : 108)} L${cx + 120 * pico} ${yW} Z" fill="#fff" stroke="${INK}" stroke-width="3" stroke-linejoin="round"/>` +
        `</g>` +
        `<linearGradient id="agua" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${AZU}" stop-opacity=".26"/><stop offset=".75" stop-color="${AZU}" stop-opacity=".16"/><stop offset="1" stop-color="${AZU}" stop-opacity="0"/></linearGradient>` +
        `<rect x="0" y="${yW}" width="${W}" height="${fondo - yW + 40}" fill="url(#agua)"/>` +
        `<path d="${olas}" fill="none" stroke="${AZU}" stroke-width="5" stroke-linecap="round" opacity=".85"/>`;
      if (v.arriba) o += peg(cx + (HOR ? 150 : 110), yW - (HOR ? 70 : 66), String(v.arriba).replace(/\*/g, ''), HOR ? 26 : 23, INK, '#fff', 'start', eo((L - .4) / .3), -3);
      const fs = HOR ? 28 : 25, paso = (fondo - yW - (HOR ? 40 : 50)) / Math.max(ab.length, 1);
      ab.forEach((it, i) => {
        const t0 = .9 + i * .55, q = eo((L - t0) / .35); if (q <= 0) return;
        const y = yW + (HOR ? 40 : 30) + paso * (i + .5) + (1 - q) * 24;
        o += `<g opacity="${q.toFixed(2)}"><circle cx="${cx - (HOR ? 260 : 206)}" cy="${y - fs * .32}" r="${HOR ? 9 : 8}" fill="${ORA}" stroke="${INK}" stroke-width="2.5"/>` +
          tx(cx - (HOR ? 236 : 188), y, esc(String(it).replace(/\*/g, '').slice(0, 30)), fs, INK, 'start', 800) + `</g>`;
      });
      return o;
    },
    // podio de los tres primeros  {"tipo":"podio","items":[{"etiqueta":"Madrid","valor":"1.650 €"},{"etiqueta":"Barcelona","valor":"1.480 €"},{"etiqueta":"Málaga","valor":"1.200 €"}]}
    podio(v, L, d) {
      const it = (v.items || []).slice(0, 3), orden = [1, 0, 2], alt = [HOR ? 250 : 280, HOR ? 180 : 210, HOR ? 130 : 150], med = [ORO, '#c9ccd3', '#d6894a'];
      const wB = HOR ? 220 : 172, gap = HOR ? 18 : 8, base = HOR ? Z.y + Z.h - 10 : Z.y + Z.h - 60, x0 = ZC.x - (3 * wB + 2 * gap) / 2;
      let o = `<path d="M${x0 - 20} ${base} H${x0 + 3 * wB + 2 * gap + 20}" stroke="${INK}" stroke-width="4.5" stroke-linecap="round"/>`;
      orden.forEach((pos, col_) => {
        const q = it[pos]; if (!q) return;
        const t0 = .2 + (2 - pos) * .35, p = back((L - t0) / .55), h = alt[pos] * cl(p, 0, 1.1), x = x0 + col_ * (wB + gap), y = base - h;
        if (L < t0) return;
        o += caja(x, y, wB, h, 12, pos === 0 ? ORA : BLA, 5) + tx(x + wB / 2, y + Math.min(h - 10, HOR ? 92 : 100), String(pos + 1), HOR ? 84 : 90, pos === 0 ? '#fff' : INK, 'middle', 900, `opacity="${cl(h / 120).toFixed(2)}"`);
        const ep = back((L - t0 - .45) / .35); if (ep <= 0) return;
        const fs = Math.min(HOR ? 32 : 26, (wB - 8) / (Math.max(5, String(q.etiqueta || '').length) * .56));
        o += `<g transform="translate(${x + wB / 2} ${y - 18}) scale(${ep.toFixed(3)})"><circle cx="0" cy="${HOR ? -96 : -104}" r="28" fill="${med[pos]}" stroke="${INK}" stroke-width="3"/>${tx(0, HOR ? -86 : -94, String(pos + 1), 28, INK)}` +
          tx(0, HOR ? -50 : -46, esc(q.etiqueta || ''), fs, INK, 'middle', 900) + peg(0, -6, String(q.valor || ''), HOR ? 26 : 22, INK, '#fff', 'middle', 1, 0) + `</g>`;
        if (pos === 0 && L > t0 + .6) for (let i = 0; i < 14; i++) { const a = i * 2.4, fr = frac((L - t0 - .6) * .7 + i / 14), cx_ = x + wB / 2 + Math.sin(a * 3.1) * 150 * fr, cy_ = y - 150 - 60 * Math.sin(a) + 260 * fr * fr; o += `<rect x="${cx_.toFixed(1)}" y="${cy_.toFixed(1)}" width="12" height="7" fill="${[ORA, AZU, VER, ORO, ROJ][i % 5]}" transform="rotate(${(a * 60 + L * 300).toFixed(0)} ${cx_.toFixed(1)} ${cy_.toFixed(1)})" opacity="${(1 - fr).toFixed(2)}"/>`; }
      });
      return o;
    },
    foto(v, L, d, k) {
      const f = fotoDe(k) || {}, txt = f.texto || v.texto || '', size = HOR ? 50 : 38, max = HOR ? 20 : 26, alto = altoCin(txt, size, max), e = back(L / .45);
      const fw = HOR ? Z.w * .6 : Z.w, fh = HOR ? Z.h - 10 : Z.h - alto - 40, fx = HOR ? Z.x : ZC.x - fw / 2, fy = Z.y + (HOR ? 10 : 6), cx = fx + fw / 2, cy = fy + fh / 2, id = 'fc' + k;
      return `<g transform="translate(${cx} ${cy}) scale(${e.toFixed(3)}) rotate(-1.5) translate(${-cx} ${-cy})"><rect x="${fx + SOM + 3}" y="${fy + SOM + 3}" width="${fw}" height="${fh}" rx="24" fill="${INK}" opacity=".22" filter="url(#somS)"/>` +
        `<clipPath id="${id}"><rect x="${fx}" y="${fy}" width="${fw}" height="${fh}" rx="24"/></clipPath><image href="file://${f.ruta}" x="${fx}" y="${fy}" width="${fw}" height="${fh}" preserveAspectRatio="xMidYMid slice" clip-path="url(#${id})"/>` +
        // v60: la foto queda quieta, pero alrededor hay vida: destello de flash al entrar, un brillo que la cruza y esquinas de visor que enfocan
        `<g clip-path="url(#${id})"><rect x="${fx}" y="${fy}" width="${fw}" height="${fh}" fill="#fff" opacity="${(L < .55 ? .7 * cl(1 - (L - .3) / .25) * cl((L - .25) / .05) : 0).toFixed(3)}"/>` +
        (L > .6 && L < 1.6 ? `<path d="M${(fx - 200 + (fw + 400) * eio((L - .6) / 1)).toFixed(1)} ${fy} l120 0 l-160 ${fh} l-120 0 Z" fill="#fff" opacity=".28"/>` : '') + `</g>` +
        `<rect x="${fx}" y="${fy}" width="${fw}" height="${fh}" rx="24" fill="none" stroke="${INK}" stroke-width="4.5"/>` +
        `<text x="${fx + fw - 16}" y="${fy + fh - 14}" font-family="Inter" font-weight="700" font-size="${HOR ? 14 : 15}" text-anchor="end" fill="#fff" stroke="${INK}" stroke-width="4" paint-order="stroke"${String(f.credito || '').length * (HOR ? 7.6 : 8.2) > fw - 40 ? ` textLength="${fw - 40}" lengthAdjust="spacingAndGlyphs"` : ''}>${esc(f.credito || '')}</text></g>` +
        (() => { const q = eo((L - .2) / .5), m = 26 + 30 * (1 - q) + 4 * Math.sin(L * 3), lc = 34, c_ = GRAVE ? BLA : ORO, op = cl((L - .2) / .2) * (1 - .35 * cl((L - 1.6) / .4));   // esquinas de visor
          return [[fx + m, fy + m, 1, 1], [fx + fw - m, fy + m, -1, 1], [fx + m, fy + fh - m, 1, -1], [fx + fw - m, fy + fh - m, -1, -1]].map(([x, y, sx, sy]) =>
            `<path d="M${x} ${y + sy * lc} V${y} H${x + sx * lc}" fill="none" stroke="${c_}" stroke-width="7" stroke-linecap="round" opacity="${op.toFixed(2)}" transform="rotate(-1.5 ${cx} ${cy})"/>`).join(''); })() +
        peg(fx + 92, fy + 44, 'FOTO REAL', HOR ? 22 : 18, ROJ, '#fff', 'middle', eo((L - .3) / .2), -6, back((L - .3) / .35)) +
        (f.etiqueta ? peg(fx + fw - 86, fy + fh - 40, f.etiqueta, HOR ? 24 : 20, ORO, INK, 'middle', eo((L - .5) / .2), 5, back((L - .5) / .35)) : '') +
        cinetico(txt, HOR ? fx + fw + (Z.w - fw) / 2 + 10 : ZC.x, HOR ? ZC.y - alto / 2 + size * .8 : fy + fh + 22 + size * .7, size, L, { max: HOR ? 14 : max, t0: .35 });
    },
    mencion(v, L, d) {
      const e = L < VIAJE ? 0 : 1 + .1 * Math.exp(-(L - VIAJE) * 9) * Math.sin((L - VIAJE) * 26),   /* v90: Lupi llega volando desde la esquina y rebota al aterrizar */ lx = HOR ? Z.x + 230 : ZC.x, ly = HOR ? ZC.y - 20 : Z.y + 120, tx0 = HOR ? Z.x + 470 + (Z.w - 470) / 2 : ZC.x, hm = HOR ? 0 : altoCin(v.texto || 'Los hechos, sin humo', 44, 22), by = HOR ? ZC.y + 120 : Z.y + 320 + hm + 50, pul = 1 + .05 * Math.sin(L * 5), clic = frac(L / 1.6) > .8 ? .94 : 1;
      return `<g transform="translate(${lx} ${ly}) scale(${((HOR ? 1.45 : 1.05) * e).toFixed(3)}) translate(${-lx} ${-ly})">${lupiM({ x: lx, y: ly, s: 1, t: L, expr: GRAVE ? 'seria' : 'feliz', brazos: GRAVE ? '' : 'saluda', mira: [0, 0] })}</g>` +
        cinetico(v.texto || 'Los hechos, sin humo', tx0, HOR ? ZC.y - 70 : Z.y + 320, HOR ? 58 : 44, L, { max: HOR ? 20 : 22, t0: .2 }) +
        // v78: en noticias graves, sin botón, sin mano ni campana: solo Lupi seria y la frase
        (GRAVE ? '' : `<g transform="translate(${tx0} ${by}) scale(${(pul * clic * back((L - .6) / .4)).toFixed(3)})">${HOR ? caja(-190, -44, 380, 88, 44, ROJ, 6) : caja(-150, -36, 300, 72, 36, ROJ, 5)}<text x="0" y="${HOR ? 15 : 12}" font-family="Inter" font-weight="900" font-size="${HOR ? 40 : 32}" text-anchor="middle" fill="#fff">SUSCRÍBETE</text></g>`) +
        // v61: una mano pulsa el botón y suena la campana
        (() => { if (L < .9 || GRAVE) return ''; const ph = frac((L - .9) / 1.6), pres = ph > .45 && ph < .6, hx = tx0 + (HOR ? 140 : 116) + (1 - eo(cl((L - .9) / .4))) * 90, hy = by + 26 + (pres ? 6 : 0);
          const mano = `<g transform="translate(${hx.toFixed(1)} ${hy.toFixed(1)}) rotate(-20) scale(${HOR ? 1.1 : .95})"><path d="M0 0 v-34 a9 9 0 0 1 18 0 v26 a9 9 0 0 1 16 2 a9 9 0 0 1 16 4 a9 9 0 0 1 15 6 v22 c0 18 -12 30 -30 30 h-14 c-12 0 -20 -6 -26 -16 l-16 -26 a9 9 0 0 1 14 -10 z" fill="${BLA}" stroke="${INK}" stroke-width="3" stroke-linejoin="round"/></g>`;
          const bx = tx0 - (HOR ? 240 : 196), byy = by, sw = ph > .55 ? 18 * Math.sin((L - .9) * 28) * Math.exp(-(ph - .55) * 8) : 0, eb = back((L - 1.0) / .3);
          const campana = eb <= 0 ? '' : `<g transform="translate(${bx} ${byy}) rotate(${sw.toFixed(1)} 0 -26) scale(${(eb * (HOR ? 1.1 : .9)).toFixed(3)})"><path d="M-22 14 c4 -6 4 -14 4 -24 a18 18 0 0 1 36 0 c0 10 0 18 4 24 z" fill="${ORO}" stroke="${INK}" stroke-width="3" stroke-linejoin="round"/><circle cy="20" r="7" fill="${ORO}" stroke="${INK}" stroke-width="2.5"/><circle cy="-30" r="5" fill="${INK}"/></g>`;
          return campana + mano; })();
    },
    cierre(v, L, d) {
      const e = L < VIAJE ? 0 : 1 + .1 * Math.exp(-(L - VIAJE) * 9) * Math.sin((L - VIAJE) * 26), lx = HOR ? Z.x + 230 : ZC.x, ly = HOR ? ZC.y - 20 : Z.y + 120, tx0 = HOR ? Z.x + 470 + (Z.w - 470) / 2 : ZC.x, gr = v.grave || GRAVE, hc = HOR ? 0 : altoCin(v.texto || '¿Tú qué opinas?', 46, 20);
      return `<g transform="translate(${lx} ${ly}) scale(${((HOR ? 1.45 : 1.05) * e).toFixed(3)}) translate(${-lx} ${-ly})">${lupiM({ x: lx, y: ly, s: 1, t: L, expr: gr ? 'seria' : (L > 1.2 ? 'guino' : 'feliz'), brazos: gr ? '' : 'saluda', mira: [0, 0] })}</g>` +
        cinetico(v.texto || '¿Tú qué opinas?', tx0, HOR ? ZC.y - 50 : Z.y + 320, HOR ? 62 : 46, L, { max: HOR ? 20 : 20, t0: .2 }) +
        peg(tx0, HOR ? ZC.y + 130 : Z.y + 320 + hc + 40, 'sin humo TV', HOR ? 34 : 28, ORA, '#fff', 'middle', eo((L - .7) / .2), -3, back((L - .7) / .4)) +
        // v61: bocadillo de comentario con «escribiendo…» (invita a comentar)
        (() => { const e2 = back((L - .9) / .4); if (e2 <= 0) return ''; const bx = HOR ? lx + 120 : lx + 120, by = HOR ? ly - 130 : ly - 70, w = 120, h = 74;
          return `<g transform="translate(${bx} ${by}) rotate(${(6 + 3 * Math.sin(L * 2)).toFixed(2)}) scale(${e2.toFixed(3)})">` + caja(-w / 2, -h / 2, w, h, 26, BLA, 5) +
            `<path d="M-30 ${h / 2 - 3} l-14 22 l30 -22 Z" fill="${BLA}" stroke="${INK}" stroke-width="3" stroke-linejoin="round"/><path d="M-32 ${h / 2 - 2} h18" stroke="${BLA}" stroke-width="8"/>` +
            [-1, 0, 1].map(j => `<circle cx="${j * 28}" cy="${(-4 * Math.max(0, Math.sin(L * 7 - j * .9))).toFixed(1)}" r="9" fill="${ORA}"/>`).join('') + `</g>`; })();
    },
  };
  // pegatinas que saltan cuando la voz dice una palabra clave del subtítulo (máx. 2 por escena)
  function pegatinasVoz(k, t, tipo) {
    if (!HOR) return '';   // v45: en los cortos ensuciaban y se metían encima de textos y fotos
    if (['lista', 'linea', 'grafico', 'comparar', 'mencion', 'cierre', 'titular', 'frase', 'porcentaje', 'proporcion', 'versus', 'mapa', 'prensa', 'dialogo', 'ranking', 'fecha', 'medidor', 'evolucion', 'reparto', 'tendencia', 'dinero', 'reloj', 'checklist', 'alerta', 'escanos', 'contador', 'pasos', 'termometro', 'bateria', 'lupa', 'encuesta', 'ultimahora', 'podio', 'balanza', 'iceberg', 'mundo'].includes(tipo)) return '';
    const bl = bloquesKaraoke(k, HOR ? 34 : 17, HOR ? 34 : 13), cl_ = [];
    bl.forEach(b => b.ls.forEach(ln => ln.forEach(p => { const w = p.w.replace(/[.,;:?!…»«"]/g, ''); if ((p.clave || /\d/.test(w)) && w.length >= 3 && w.length <= 14 && !cl_.some(o => o.w === w)) cl_.push({ w, a: p.a }); })));
    const pos = HOR ? [[Z.x + Z.w - 120, Z.y + 40, 5], [Z.x + Z.w - 150, Z.y + Z.h - 20, -5]] : [[Z.x + Z.w - 130, Z.y + 60, 6], [Z.x + 120, Z.y + Z.h + 8, -5]], cs = [[ORO, INK], [AZU, '#fff']];
    return cl_.slice(0, 2).map((o, i) => t < o.a ? '' : peg(pos[i][0], pos[i][1], o.w.toUpperCase(), HOR ? 28 : 32, cs[i][0], cs[i][1], 'middle', 1, pos[i][2] + 2 * Math.sin(t * 1.7 + i), back((t - o.a) / .35))).join('');
  }

  // ---------- v52 (11-nov-2026): la imagen reacciona a la voz ----------
  // E[k].voz = etiqueta de interpretación de la escena (excited, whispers, indignant…; la elige el guion y la usa la voz de Gemini)
  const EMO = k => String((E[k] || {}).voz || '').toLowerCase();
  const SUSURRO = k => ['whispers', 'conspiratorial'].includes(EMO(k));
  const PALS = {};
  function palabras(k) {        // todas las palabras de la escena con su segundo real y si son clave
    if (!PALS[k]) { PALS[k] = []; try { bloquesKaraoke(k, HOR ? 34 : 30, HOR ? 34 : 18).forEach(b => b.ls.forEach(ln => ln.forEach(p => PALS[k].push(p)))); } catch (e) {} }
    return PALS[k];
  }
  const CLAVES = {};
  function claves(k) {          // segundo en que empieza cada grupo de palabras clave (*así*)
    if (!CLAVES[k]) { const ps = palabras(k); CLAVES[k] = ps.filter((p, i) => p.clave && !(i > 0 && ps[i - 1].clave)).map(p => p.a); }
    return CLAVES[k];
  }
  const hablando = (k, t) => palabras(k).some(p => t >= p.a && t < p.b);
  // v71: cada elemento de una lista aparece cuando la voz lo nombra (si no se nombra, a intervalos iguales como antes)
  const _nrm = w => String(w || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9ñ]/g, '');
  const ENTRAN = {};
  // v85: hueco punteado donde va a aparecer un elemento que la voz aún no ha nombrado (la pantalla nunca se queda vacía)
  const hueco = (x, y, w, h, rx, n, L) => { const op = .55 * eo((L - .15) / .35); return op <= 0 ? '' : `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${w.toFixed(1)}" height="${h.toFixed(1)}" rx="${rx}" fill="#fff" fill-opacity=".35" stroke="${INK}" stroke-opacity=".28" stroke-width="2.5" stroke-dasharray="10 9" opacity="${op.toFixed(2)}"/>` + (n === '' ? `<rect x="${(x + h * .5 - h * .36).toFixed(1)}" y="${(y + h * .14).toFixed(1)}" width="${(h * .72).toFixed(1)}" height="${(h * .72).toFixed(1)}" rx="${(h * .16).toFixed(1)}"` : `<circle cx="${(x + h * .5).toFixed(1)}" cy="${(y + h / 2).toFixed(1)}" r="${(h * .3).toFixed(1)}"`) + ` fill="none" stroke="${INK}" stroke-opacity=".25" stroke-width="2.5" opacity="${op.toFixed(2)}"/>` + tx(x + h * .5, y + h / 2 + h * .13, String(n), h * .36, INK, 'middle', 900, `opacity="${(op * .35).toFixed(2)}"`); };
  function entradas(k, its, d, ini = .3, paso) {
    const key = k + '|' + its.join('§'); if (ENTRAN[key]) return ENTRAN[key];
    const n = its.length || 1, p0 = paso || Math.max(.45, (d - .8) / n), ps = k == null ? [] : palabras(k).map(p => ({ w: _nrm(p.w), a: p.a - T.escenas[k].ini + (k === 0 ? 1 : 0) }));   // al tiempo de la escena (L)
    let desde = 0; const r = its.map((s, i) => {
      const cl4 = String(s || '').split(/\s+/).map(_nrm).filter(w => w.length >= 4 || /\d/.test(w));
      for (let j = desde; j < ps.length && cl4.length; j++) if (cl4.some(c => ps[j].w === c || (c.length > 5 && ps[j].w.startsWith(c.slice(0, 5))))) { desde = j + 1; return Math.max(.15, ps[j].a - .2); }
      return null;
    });
    // los no nombrados: repartidos; y nunca antes que el anterior (+0,3 s)
    let prev = -1; for (let i = 0; i < n; i++) { if (r[i] == null) r[i] = prev < 0 ? ini + i * p0 : Math.max(ini + i * p0, prev + Math.max(.3, Math.min(p0, (d - .5 - prev) / (n - i)))); if (prev >= 0 && r[i] < prev + .3) r[i] = prev + .3; prev = r[i]; }
    return (ENTRAN[key] = r);
  }
  function golpe(k, t) {        // empujón de cámara en cada palabra clave: sube en 0,07 s y vuelve en ~0,5 s
    let g = 0; for (const a of claves(k)) { const x = t - a; if (x >= -.07 && x < .6) g = Math.max(g, x < 0 ? (x + .07) / .07 : Math.exp(-x * 7)); }
    return g;
  }
  function sacudida(k, t) {     // sorpresa: sacudida corta en la primera palabra clave
    if (GRAVE || !['surprised', 'excited', 'emphatic'].includes(EMO(k))) return [0, 0];
    const a = claves(k)[0]; if (a == null) return [0, 0]; const x = t - a; if (x < 0 || x > .35) return [0, 0];
    const amp = 9 * Math.exp(-x * 9); return [amp * Math.sin(x * 70), amp * .6 * Math.cos(x * 55)];
  }
  function asoma(k, t) {        // v60: en sorpresa/emoción, Lupi se asoma por la derecha con un «!» en la primera palabra clave
    if (GRAVE || HOR || k === 0 || !['surprised', 'excited', 'emphatic', 'amused'].includes(EMO(k)) || !['titular', 'pregunta', 'icono', 'frase'].includes((E[k].visual || {}).tipo) || fotoDe(k)) return '';   // solo donde la esquina está libre
    const a = claves(k)[0]; if (a == null) return ''; const x = t - a; if (x < -.05 || x > 1.3) return '';
    const sal = x < .25 ? back((x + .05) / .3) : x > 1 ? 1 - eio((x - 1) / .3) : 1, lx = SX + 30 + 50 * sal, ly = 812;   // por la izquierda (a la derecha están los botones de TikTok)
    return `<g transform="translate(${lx.toFixed(1)} ${ly}) rotate(${(16 - 4 * Math.sin(t * 6)).toFixed(1)})" opacity="${cl(sal * 1.5).toFixed(2)}">${lupiM({ x: 0, y: 0, s: .5, t, expr: 'sorprendida', mira: [1, -.3], brazos: 'senala' })}</g>` +
      peg(lx + 52, ly - 62, '!', 40, ROJ, '#fff', 'middle', cl(sal), 10, back((x - .1) / .25));
  }
  function ambiente(k, t, L) {  // capa de emoción encima del plano (debajo de subtítulos y cabecera)
    const e = EMO(k), ent = eo(L / .45);
    if (SUSURRO(k)) return `<defs><radialGradient id="vg" cx=".5" cy=".45" r=".75"><stop offset=".45" stop-color="${INK}" stop-opacity="0"/><stop offset="1" stop-color="${INK}" stop-opacity="${(.42 * ent).toFixed(3)}"/></radialGradient></defs><rect width="${W}" height="${H}" fill="url(#vg)"/>`;
    if (e === 'indignant' && !GRAVE) return `<rect x="10" y="10" width="${W - 20}" height="${H - 20}" rx="40" fill="none" stroke="${ROJ}" stroke-width="44" opacity="${(ent * (.16 + .1 * Math.sin(t * 6))).toFixed(3)}" filter="url(#hb)"/>`;
    if (['tense', 'sad'].includes(e)) return `<rect width="${W}" height="${H}" fill="#3a4a63" opacity="${(.07 * ent).toFixed(3)}"/>`;
    return '';
  }

  // ---------- una escena completa ----------
  function escena(k, t) {
    const S = T.escenas[k], L = Math.max(0, t - S.ini) + (k === 0 ? 1 : 0), d = Math.max(1, S.fin - S.ini), v = E[k].visual || { tipo: 'icono', icono: 'alerta', texto: E[k].titulo };
    const f = fotoDe(k), tipo = f ? 'foto' : (G[v.tipo] ? v.tipo : 'icono');
    let g = ''; try { g = G[tipo](v, L, d, k) || ''; } catch (e) { g = G.icono({ icono: 'alerta', texto: E[k].titulo || '' }, L, d); }
    const ini = k === 0 ? Math.max(0, .3 - (t - S.ini)) / .3 : 0;   // v52: arranque con golpe de zoom (con el impacto de sonido del segundo 0)
    const z = 1 + .02 * cl(L / d) + .045 * golpe(k, t) + .045 * eo(ini), [sx, sy] = sacudida(k, t);
    return fondo(k, t) + (k === 0 && L < 2.2 ? rayos(ZC.x, ZC.y, t, .1 * (1 - cl((L - 1.4) / .8))) : '') +
      `<g transform="translate(${(ZC.x + sx).toFixed(1)} ${(ZC.y + sy + (tipo === 'foto' ? 0 : 5 * Math.sin(L * 1.6 + k))).toFixed(1)}) rotate(${(tipo === 'foto' ? 0 : .5 * Math.sin(L * .9 + k * 2)).toFixed(3)}) scale(${z.toFixed(4)}) translate(${-ZC.x} ${-ZC.y})">${g}</g>` + (window.LIMPIO ? '' : pegatinasVoz(k, t, tipo)) + (window.LIMPIO ? '' : rotulo(k, L)) + (window.LIMPIO ? '' : reaccion(k, t)) +
      ambiente(k, t, L) + asoma(k, t) + (k === 0 && t - S.ini > 0 && t - S.ini < .3 ? `<rect width="${W}" height="${H}" fill="#fff" opacity="${(.4 * Math.sin(Math.PI * (t - S.ini) / .3)).toFixed(3)}"/>` : '')   // destello (el fotograma 0 queda limpio para la miniatura);
  }
  // rótulo de la escena: banda negra inclinada con el título (entra con rebote en cada plano)
  // v88: emoji de REACCIÓN grande (😱 💸 👀 🔥…) que salta en la palabra clave de la escena, se balancea y se va (como las
  // pegatinas de los editores de TikTok). Lo elige el guion ("reaccion"), nunca en noticias graves ni en mención/cierre.
  function reaccion(k, t) {
    const em = String(E[k].reaccion || '').trim().slice(0, 8), tp = (E[k].visual || {}).tipo; if (!em || !tieneEmoji(em) || GRAVE || ['mencion', 'cierre'].includes(tp)) return '';   // v91: solo emoticonos propios
    const S = T.escenas[k], c = claves(k), t0 = c.length ? c[0] : S.ini + Math.min(1.2, (S.fin - S.ini) * .3), x = t - t0, vida = 1.6;
    if (x < 0 || x > vida) return '';
    // en vertical: abajo a la izquierda (la columna de botones de TikTok/Reels está a la derecha, de media pantalla para abajo);
    // si en esa escena puede asomar Lupi por la izquierda, arriba a la derecha
    const e = back(x / .28), sale = x > vida - .25 ? 1 - eo((x - vida + .25) / .25) : 1, der = ['titular', 'pregunta', 'icono', 'frase'].includes(tp), fs = HOR ? 120 : 100;
    const cx = HOR ? W - 300 : (der ? Z.x + Z.w - 50 : Z.x + 40), cy = HOR ? 250 : (der ? Z.y + 70 : Z.y + Z.h - 60) - 14 * x, rot = (der ? 12 : -12) * Math.sin(x * 7) * (1 - x / vida);
    let o = `<g transform="translate(${cx.toFixed(1)} ${cy.toFixed(1)}) rotate(${rot.toFixed(1)}) scale(${(e * sale).toFixed(3)})">`;
    const an = eo(x / .45); if (an < 1) o += `<circle r="${(fs * (.5 + .55 * an)).toFixed(1)}" fill="none" stroke="${ORA}" stroke-width="${(8 * (1 - an)).toFixed(1)}" opacity="${(1 - an).toFixed(2)}"/>` +
      [...Array(8).keys()].map(i => { const a_ = i * Math.PI / 4 + .3, r1 = fs * (.55 + .35 * an), r2 = r1 + 22 * (1 - an); return `<path d="M${(Math.cos(a_) * r1).toFixed(1)} ${(Math.sin(a_) * r1).toFixed(1)} L${(Math.cos(a_) * r2).toFixed(1)} ${(Math.sin(a_) * r2).toFixed(1)}" stroke="${i % 2 ? ORO : ORA}" stroke-width="6" stroke-linecap="round" opacity="${(1 - an).toFixed(2)}"/>`; }).join('');
    return o + `<ellipse cx="0" cy="${fs * .52}" rx="${fs * .32}" ry="${fs * .07}" fill="${INK}" opacity=".15"/>${emojiVec(em, fs * 1.05, x + 1.3)}</g>`;
  }
  function rotulo(k, L) {
    // v62: en la PRIMERA escena de los cortos, el titular de la noticia grande (mucha gente empieza a ver sin sonido)
    if (k === 0 && !HOR && P.titulo_noticia) {
      let ls = partir(String(P.titulo_noticia), 24), fs = 34; if (ls.length > 2) { ls = partir(String(P.titulo_noticia), 30); fs = 28; } ls = ls.slice(0, 3); const w = Math.min(W - 2 * SX - 40, Math.max(...ls.map(l => l.length)) * fs * .56 + 44), h = ls.length * fs * 1.18 + 26, x = ZC.x - w / 2, y = 208;
      return `<g transform="translate(${ZC.x} ${y + h / 2}) rotate(-1.5) scale(${back(L / .4).toFixed(3)}) translate(${-ZC.x} ${-(y + h / 2)})">` + caja(x, y, w, h, 16, INK, 0, 6) +
        `<rect x="${x + 18}" y="${y + h - 9}" width="${((w - 36) * eo((L - .2) / .5)).toFixed(1)}" height="5" rx="2" fill="${ORA}"/>` +
        ls.map((l, i) => tx(ZC.x, y + 13 + fs * .86 + i * fs * 1.18, esc(l), fs, '#fff', 'middle', 900)).join('') + `</g>`;
    }
    const tit = String(E[k].titulo || ''); if (!tit) return '';
    // v79: emoji de la escena (opcional, nunca en noticias graves) que salta al lado del rótulo y se balancea
    const emo = !GRAVE && E[k].emoji && tieneEmoji(E[k].emoji) && !['mencion', 'cierre'].includes((E[k].visual || {}).tipo) ? String(E[k].emoji).trim().slice(0, 8) : '', fsR = HOR ? 30 : 30, xR = HOR ? Z.x + 6 : ZC.x, yR = HOR ? 104 : 266;   // v87: rótulo de escena más grande en vertical
    let em = '';
    if (emo) { const wR = tit.length * fsR * .6 + fsR, xe = HOR ? xR + wR + 26 : xR + wR / 2 + 30, ee = back((L - .25) / .35);
      if (ee > 0) em = `<g data-emo="${(10 * Math.sin(L * 3.2)).toFixed(2)}|${ee.toFixed(3)}|${(fsR * 1.75).toFixed(1)}" transform="translate(${xe.toFixed(1)} ${yR - fsR * .35}) rotate(${(10 * Math.sin(L * 3.2)).toFixed(2)}) scale(${ee.toFixed(3)})"><g data-emot="1">${emojiVec(emo, fsR * 1.7, L)}</g></g>`; }   /* v91: emoticono propio (no el de WhatsApp) */
    return peg(xR, yR, tit, fsR, INK, BLA, HOR ? 'start' : 'middle', 1, -2, back(L / .4)) + em;
  }

  // ---------- capas fijas ----------
  function cabecera(k, t, L) {
    const ci = CAPS.reduce((a, c, i) => (c.desde <= k ? i : a), -1), tp = (E[k].visual || {}).tipo;
    let o = logoM(HOR ? 100 : SX + 46, HOR ? 46 : 166, HOR ? .82 : .88);   // v68: logo moderno
    if (k === 0 && P.fecha) o += peg(HOR ? 400 : 422, HOR ? 53 : 173, P.fecha, HOR ? 20 : 22, ORO, INK, 'middle', 1, 3);
    if (HOR && ci >= 0) { const sig = CAPS.find(x => x.desde === k + 1), d = Math.max(1, T.escenas[k].fin - T.escenas[k].ini), av = sig && L > d * .4; o += peg(W - 110, 52, av ? 'A CONTINUACIÓN  ▸  ' + String(sig.titulo).toUpperCase() : `${ci + 1}/${CAPS.length} · ${String(CAPS[ci].titulo).toUpperCase()}`, 20, av ? ORO : ORA, av ? INK : '#fff', 'end', 1, 0, av ? back((L - d * .4) / .35) : 1); }
    const lx = HOR ? W - 62 : W - SX - 66, ly = HOR ? H - 196 : 166, s = HOR ? .5 : .46;
    // v90: Lupi nunca cambia de sitio de golpe: vuela de la esquina al centro (mención y cierre) y vuelve después, en arco y girando
    const grande = q => ['mencion', 'cierre'].includes((E[q] || {}).visual ? E[q].visual.tipo : ''), GX = HOR ? Z.x + 230 : ZC.x, GY = HOR ? ZC.y - 20 : Z.y + 120, GS = HOR ? 1.45 : 1.05;
    const viaja = (q, ida) => { const a = ida ? [lx, ly, s] : [GX, GY, GS], b = ida ? [GX, GY, GS] : [lx, ly, s], x = a[0] + (b[0] - a[0]) * q, y = a[1] + (b[1] - a[1]) * q - (HOR ? 160 : 140) * Math.sin(Math.PI * q), sc = a[2] + (b[2] - a[2]) * q;
      return `<g transform="translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${((ida ? -1 : 1) * 360 * eio(q)).toFixed(1)})">${lupiM({ x: 0, y: 0, s: sc, t, expr: 'feliz', brazos: 'saluda', mira: [ida ? -1 : 1, 0] })}</g>`; };
    if (grande(k)) { if (L < VIAJE) o += viaja(eio(L / VIAJE), true); }
    else if (k > 0 && grande(k - 1) && L < VIAJE) o += viaja(eio(L / VIAJE), false);
    else {
      const em = EMO(k), porEmo = { surprised: 'sorprendida', excited: 'sorprendida', emphatic: 'sorprendida', indignant: 'enfadada', whispers: 'curiosa', conspiratorial: 'guino', curious: 'curiosa', serious: 'seria', tense: 'seria', sad: 'seria', amused: 'guino' }[em];
      let ex = GRAVE ? (porEmo === 'curiosa' ? 'curiosa' : 'seria') : porEmo || (tp === 'cifra' ? 'sorprendida' : tp === 'pregunta' ? 'curiosa' : 'feliz');
      if ((ex === 'feliz' || ex === 'seria' && !GRAVE) && hablando(k, t)) ex = 'habla';   // v52: Lupi «habla» con la voz
      const mira = SUSURRO(k) ? [HOR ? -1 : -1, 0] : [HOR ? -1 : -.6, HOR ? -.4 : .8];
      o += lupiM({ x: lx, y: ly + 3 * Math.sin(t * 2.4), s, t, expr: ex, mira, brazos: L < 1 ? 'senala' : '' });
    }
    return o;
  }
  function subtitulos(k, t) {
    // v86: en vertical, bloques más cortos (2 líneas de ~14 letras) y letra MUCHO más grande, que entra de golpe con rebote
    const bl = bloquesKaraoke(k, HOR ? 34 : 24, HOR ? 34 : 14); if (!bl.length) return '';
    let i = bl.findIndex(b => t < b.b); if (i < 0) i = bl.length - 1;
    const B = bl[i], ent = back((t - B.a) / .16) || (i === 0 ? 1 : 0), maxc = Math.max(...B.ls.map(ln => ln.reduce((a, b) => a + b.w.length + 1, -1)));
    const su = SUSURRO(k), fs = Math.round((su ? .9 : 1) * Math.min(HOR ? 52 : 60, Math.floor((HOR ? 1000 : W - 2 * SX - 40) / (Math.max(5, maxc) * .58)))), lh = fs * 1.12, yc = HOR ? 606 : 920, y0 = yc - (B.ls.length - 1) * lh / 2 + fs * .35;
    const pe = HOR ? 0 : cl((t - B.a) / .3), giro = HOR ? 0 : (i % 2 ? 1 : -1) * 2.5 * (1 - eo(pe));
    return `<g transform="translate(${W / 2} ${yc}) rotate(${giro.toFixed(2)}) scale(${(HOR ? .88 + .12 * ent : (i === 0 && k === 0 ? 1 : .7 + .3 * ent)).toFixed(3)}) translate(${-W / 2} ${-yc})">` + B.ls.map((ln, j) => {
      const sp = ln.map(p => {
        const ahora = t >= p.a && t < p.b, dicho = t >= p.b, pp = ahora ? cl((t - p.a) / .1) : 1;
        return `<tspan fill="${ahora || (!HOR && p.clave && dicho) ? ORA : INK}"${ahora ? ` data-a="1"${HOR ? ` font-size="${(fs * (1 + .12 * (1 - pp))).toFixed(1)}"` : (p.clave ? ` font-size="${(fs * (1 + .14 * Math.sin(Math.PI * cl((t - p.a) / .22)))).toFixed(1)}"` : '')}` : ''} fill-opacity="${ahora || dicho ? 1 : (HOR ? .42 : .55)}">${esc(p.w.replace(/⁠/g, ' '))}</tspan>`;
      }).join(' ');
      return `<text x="${W / 2}" y="${(y0 + j * lh).toFixed(1)}" font-family="Inter" font-weight="900" font-size="${fs}"${su ? ' font-style="italic"' : ''} text-anchor="middle" letter-spacing="-.5" stroke="${BG2[0]}" stroke-width="${(fs * .22).toFixed(1)}" paint-order="stroke" stroke-linejoin="round" xml:space="preserve">${sp}</text>`;
    }).join('') + `</g>`;
  }
  function barra(t) {            // v68: barra moderna: fina, degradado con brillo, puntos de cada escena y la lente de Lupi con los segundos
    const y = HOR ? H - 30 : 1040, x0 = HOR ? 80 : 110, w = HOR ? W - 160 : W - 220, p = cl(t / DUR), xk = x0 + w * p, seg = Math.max(0, Math.ceil(DUR - t));
    const ft = t % 1, puls = ft < .2 ? 1 - ft / .2 : 0;
    let o = `<defs><linearGradient id="bgF" x1="0" x2="1"><stop offset="0" stop-color="#ffc34d"/><stop offset="1" stop-color="${ORA}"/></linearGradient><filter id="bgG" x="-10%" y="-300%" width="120%" height="700%"><feGaussianBlur stdDeviation="5"/></filter></defs>` +
      `<rect x="${x0}" y="${y - 4}" width="${w}" height="8" rx="4" fill="${INK}" fill-opacity=".12"/>` +
      `<rect x="${x0}" y="${y - 5}" width="${Math.max(0, xk - x0).toFixed(1)}" height="10" rx="5" fill="${ORA}" opacity=".5" filter="url(#bgG)"/>` +
      `<rect x="${x0}" y="${y - 4}" width="${Math.max(0, xk - x0).toFixed(1)}" height="8" rx="4" fill="url(#bgF)"/>`;
    o += T.escenas.slice(1).map(e => { const xx = x0 + w * e.ini / DUR, pas = xx <= xk; return `<circle cx="${xx.toFixed(1)}" cy="${y}" r="3.2" fill="${pas ? '#fff' : INK}" fill-opacity="${pas ? .95 : .28}"/>`; }).join('');
    if (HOR) o += CAPS.map(c => `<rect x="${(x0 + w * (T.escenas[c.desde] ? T.escenas[c.desde].ini : 0) / DUR - 2).toFixed(1)}" y="${y - 9}" width="4" height="18" rx="2" fill="${INK}"/>`).join('');
    return o + (puls > 0 ? `<circle cx="${xk.toFixed(1)}" cy="${y}" r="${(26 + 10 * (1 - puls)).toFixed(1)}" fill="none" stroke="${ORA}" stroke-width="3" opacity="${(puls * .8).toFixed(2)}"/>` : '') +
      lupiM({ x: xk, y, s: .34, rot: 90, mini: true, sinCara: true, t, texto: seg, fs: 21 / .34 });
  }


  // v44 · pie de los cortos: cinta de titulares que corre + base oscura. Llena la zona que tapan los textos de YouTube/TikTok/Instagram
  // (antes quedaba crema vacío) y hace que el título blanco de la aplicación se lea mejor.
  function pie(t) {
    if (HOR || !window.PIE_CINTA) return '';   // v45: quitado en los cortos (más limpio); window.PIE_CINTA = true lo recupera
    const y = 1088, h = 50, fs = 26, tr = ['SIN HUMO TV', 'LOS HECHOS, SIN HUMO'].concat(P.fecha ? [String(P.fecha).toUpperCase()] : []);
    const an = tr.map(x => Math.round(x.length * fs * .8) + 70), per = an.reduce((a, b) => a + b, 0), off = (t * 70) % per;
    let o = `<rect x="0" y="${y + h}" width="${W}" height="${H - y - h}" fill="${INK}"/><rect x="0" y="${y + h}" width="${W}" height="${H - y - h}" fill="url(#pt2)"/>` +
      `<defs><pattern id="pt2" width="30" height="30" patternUnits="userSpaceOnUse"><circle cx="4" cy="4" r="1.7" fill="#fff" opacity=".08"/></pattern></defs>` +
      `<rect x="-10" y="${y}" width="${W + 20}" height="${h}" fill="${ORA}" stroke="${INK}" stroke-width="3"/>`;
    for (let x = -off; x < W; x += per) { let xx = x; tr.forEach((s_, n) => { o += `<text x="${(xx + an[n] / 2 - 18).toFixed(1)}" y="${y + h / 2 + fs * .36}" font-family="Inter" font-weight="900" font-size="${fs}" text-anchor="middle" fill="#fff" letter-spacing="1">${esc(s_)}</text><circle cx="${(xx + an[n] - 18).toFixed(1)}" cy="${y + h / 2}" r="6" fill="${INK}"/>`; xx += an[n]; }); }
    return o;
  }

  // ---------- fotograma ----------
  const TR = .3, TRC = .42;
  // v56 (11-nov-2026): 9 transiciones (v76: 12). Orden fijo que no repite dos seguidas (mezcla.py usa la MISMA regla para el sonido):
  // la escena de la mención del canal entra con la cortina de la marca; la sorpresa, tensión o indignación, con glitch;
  // en noticias graves solo las sobrias.
  const TR_TODAS = ['barrido', 'iris', 'zoom', 'persiana', 'empuje', 'mancha', 'giro', 'cortina', 'glitch', 'diagonal', 'rebote', 'burbujas'];   // v76: 12
  const TR_GRAVE = ['barrido', 'zoom', 'empuje', 'iris', 'persiana'];
  const DUR_TR = { barrido: .3, zoom: .3, cortina: .42, iris: .38, persiana: .4, empuje: .34, giro: .34, glitch: .26, mancha: .46, diagonal: .44, rebote: .4, burbujas: .46 };
  let TRS = null;
  function TIPO_TR(k) {
    if (!TRS) {
      TRS = [''];
      for (let j = 1; j < N; j++) {
        const base = i => GRAVE ? TR_GRAVE[(i * 2) % 5] : TR_TODAS[(i * 5) % 12], tipo = (E[j].visual || {}).tipo, em = String(E[j].voz || '').toLowerCase();
        let t = !GRAVE && tipo === 'mencion' ? 'cortina' : !GRAVE && ['surprised', 'tense', 'indignant'].includes(em) ? 'glitch' : base(j);
        if (t === 'glitch' && (TRS[j - 1] === 'glitch' || TRS[j - 2] === 'glitch')) t = base(j) === 'glitch' ? base(j + 1) : base(j);   // glitch, como mucho 1 de cada 3
        if (t === TRS[j - 1]) t = base(j + 1) === t ? base(j + 2) : base(j + 1);
        TRS.push(t);
      }
    }
    return TRS[k] || 'barrido';
  }
  window.EMOJIVEC = emojiVec;   // v91: para la galería de emoticonos (pruebas)
  window.render = function (t) {
    t = cl(t, 0, DUR - .001);
    let k = T.escenas.findIndex(s => t < s.fin); if (k < 0) k = N - 1;
    const S = T.escenas[k], L = t - S.ini;
    let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}"><rect width="${W}" height="${H}" fill="${BG2[0]}"/>` + DEF_LUPI;
    const tt = k > 0 ? TIPO_TR(k) : ''; let encima = '';
    if (tt === 'zoom' && L < TR) {         // zoom: el plano anterior se acerca y se funde, el nuevo llega desde un poco más pequeño
      const p = eio(L / TR), ant = escena(k - 1, T.escenas[k - 1].fin - .001), nue = escena(k, t), cx = W / 2, cy = H * .42;
      svg += `<defs><filter id="zb"><feGaussianBlur stdDeviation="${(10 * p).toFixed(1)}"/></filter></defs>` +
        `<g opacity="${(1 - p).toFixed(3)}" filter="url(#zb)" transform="translate(${cx} ${cy}) scale(${(1 + .35 * p).toFixed(3)}) translate(${-cx} ${-cy})">${ant}</g>` +
        `<g opacity="${p.toFixed(3)}" transform="translate(${cx} ${cy}) scale(${(.86 + .14 * p).toFixed(3)}) translate(${-cx} ${-cy})">${nue}</g>`;
    } else if (tt === 'cortina' && L < TRC) {   // cortina naranja de la marca que cruza en diagonal
      const p = eio(L / TRC), sh = HOR ? 260 : 340, x = -W - sh + (2 * W + 2 * sh) * p;
      svg += (p < .5 ? escena(k - 1, T.escenas[k - 1].fin - .001) : escena(k, t));
      encima = `<path d="M${(x + sh).toFixed(1)} 0 H${(x + W + sh).toFixed(1)} L${(x + W).toFixed(1)} ${H} H${x.toFixed(1)} Z" fill="${ORA}"/>` +
        `<path d="M${(x + W + sh).toFixed(1)} 0 l28 0 L${(x + W + 28).toFixed(1)} ${H} l-28 0 Z" fill="${INK}"/>` +
        `<g opacity="${cl(1 - Math.abs(p - .5) * 3).toFixed(2)}" transform="translate(${W / 2} ${H * .42}) scale(${(.9 + .1 * eo(1 - Math.abs(p - .5) * 2)).toFixed(3)})">${nube(HOR ? -215 : -190, 0, HOR ? 2.2 : 2.2)}<text x="${HOR ? 45 : 42}" y="20" font-family="Inter" font-weight="900" font-size="${HOR ? 64 : 58}" text-anchor="middle" fill="#fff">sin humo TV</text></g>`;
    } else if (tt === 'iris' && L < DUR_TR.iris) {      // círculo que se abre desde el centro con aro naranja
      const p = eio(L / DUR_TR.iris), cx = W / 2, cy = H * .42, r = Math.hypot(W, H) * .62 * p;
      svg += escena(k - 1, T.escenas[k - 1].fin - .001) + `<defs><clipPath id="ir"><circle cx="${cx}" cy="${cy}" r="${r.toFixed(1)}"/></clipPath></defs><g clip-path="url(#ir)">${escena(k, t)}</g>` +
        `<circle cx="${cx}" cy="${cy}" r="${r.toFixed(1)}" fill="none" stroke="${GRAVE ? INK : ORA}" stroke-width="${(18 * (1 - p) + 4).toFixed(1)}"/>`;
    } else if (tt === 'persiana' && L < DUR_TR.persiana) {   // persianas: franjas que entran alternando lado
      const p = L / DUR_TR.persiana, nb = HOR ? 6 : 9, bh = H / nb;
      let cp = ''; for (let i = 0; i < nb; i++) { const q = eio(cl((p - i * .045) / .6)), w = W * q; cp += `<rect x="${(i % 2 ? W - w : 0).toFixed(1)}" y="${(i * bh).toFixed(1)}" width="${w.toFixed(1)}" height="${(bh + 1).toFixed(1)}"/>`; }
      svg += escena(k - 1, T.escenas[k - 1].fin - .001) + `<defs><clipPath id="pe">${cp}</clipPath></defs><g clip-path="url(#pe)">${escena(k, t)}</g>`;
    } else if (tt === 'empuje' && L < DUR_TR.empuje) {   // empuje hacia arriba con rebote y costura naranja
      const p = L / DUR_TR.empuje, q = back(p), dy = H * (1 - q), ver = !HOR;
      svg += `<g transform="translate(${ver ? 0 : (-W * eio(p)).toFixed(1)} ${ver ? (-H * eio(p)).toFixed(1) : 0})">${escena(k - 1, T.escenas[k - 1].fin - .001)}</g>` +
        `<g transform="translate(${ver ? 0 : (W * (1 - q)).toFixed(1)} ${ver ? dy.toFixed(1) : 0})">${escena(k, t)}${ver ? `<rect x="0" y="-14" width="${W}" height="14" fill="${GRAVE ? INK : ORA}"/>` : `<rect x="-14" y="0" width="14" height="${H}" fill="${GRAVE ? INK : ORA}"/>`}</g>`;
    } else if (tt === 'giro' && L < DUR_TR.giro) {        // giro de carta: el plano se da la vuelta
      const p = eio(L / DUR_TR.giro), pri = p < .5, sx = Math.max(.002, Math.abs(Math.cos(Math.PI * p))), sk = (pri ? 1 : -1) * 6 * Math.sin(Math.PI * p), cx = W / 2, cy = H / 2;
      svg += `<rect width="${W}" height="${H}" fill="${INK}"/><g transform="translate(${cx} ${cy}) skewY(${sk.toFixed(2)}) scale(${sx.toFixed(3)} ${(1 - .08 * Math.sin(Math.PI * p)).toFixed(3)}) translate(${-cx} ${-cy})">${pri ? escena(k - 1, T.escenas[k - 1].fin - .001) : escena(k, t)}</g>`;
    } else if (tt === 'glitch' && L < DUR_TR.glitch) {    // glitch: separación de colores y franjas desplazadas
      const p = L / DUR_TR.glitch, dx = 22 * Math.sin(Math.PI * p), base = p < .45 ? escena(k - 1, T.escenas[k - 1].fin - .001) : escena(k, t);
      const rnd = i => frac(Math.sin((k + 1) * 91.7 + i * 47.3 + Math.floor(p * 9) * 13.1) * 43758.5);
      let cp = '', tr = ''; for (let i = 0; i < 5; i++) { const y = rnd(i) * H, h = 20 + rnd(i + 9) * 90; cp += `<clipPath id="gs${i}"><rect x="0" y="${y.toFixed(0)}" width="${W}" height="${h.toFixed(0)}"/></clipPath>`; tr += `<g clip-path="url(#gs${i})"><g transform="translate(${((rnd(i + 3) - .5) * 80 * Math.sin(Math.PI * p)).toFixed(1)} 0)">${base}</g></g>`; }
      svg += `<defs><filter id="gl" x="-5%" y="0" width="110%" height="100%"><feOffset in="SourceGraphic" dx="${dx.toFixed(1)}" result="a"/><feColorMatrix in="a" type="matrix" values="1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0" result="r"/><feOffset in="SourceGraphic" dx="${(-dx).toFixed(1)}" result="b"/><feColorMatrix in="b" type="matrix" values="0 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 1 0" result="gb"/><feBlend in="r" in2="gb" mode="screen"/></filter>${cp}</defs>` +
        `<g filter="url(#gl)">${base}</g>${tr}`;
    } else if (tt === 'mancha' && L < DUR_TR.mancha) {    // mancha de tinta naranja: crece desde una esquina y se retira hacia la contraria
      const p = L / DUR_TR.mancha, Rm = Math.hypot(W, H) * 1.08, pri = p < .5, q = pri ? eio(p * 2) : eio((1 - p) * 2), cx = pri ? 0 : W, cy = pri ? H : 0, r = Rm * q;
      let d_ = ''; for (let i = 0; i <= 24; i++) { const a = i / 24 * Math.PI * 2, rr = r * (1 + .06 * Math.sin(a * 5 + p * 9)); d_ += (i ? 'L' : 'M') + (cx + rr * Math.cos(a)).toFixed(1) + ' ' + (cy + rr * Math.sin(a)).toFixed(1); }
      svg += (pri ? escena(k - 1, T.escenas[k - 1].fin - .001) : escena(k, t));
      encima = `<path d="${d_}Z" fill="${ORA}"/>` + (Math.abs(p - .5) < .18 ? `<g transform="translate(${W / 2} ${H * .42}) scale(${(1 - Math.abs(p - .5) * 3).toFixed(3)})">${nube(0, 0, HOR ? 6 : 7)}</g>` : '');
    } else if (tt === 'diagonal' && L < DUR_TR.diagonal) {   // v76: franjas diagonales de la marca (naranja, oro y tinta) que cruzan y destapan el plano nuevo
      // banda ancha en diagonal hecha de franjas pegadas (oro · tinta · naranja · oro): a mitad tapa toda la pantalla y ahí cambia el plano
      const p = eio(L / DUR_TR.diagonal), sh = H * .55, fr = [[ORO, 46], [INK, 26], [ORA, W + 2 * sh], [INK, 18], [ORO, 60]], tot = fr.reduce((a, f) => a + f[1], 0), x0 = W + sh - (W + sh + tot + sh) * p;
      svg += (p < .5 ? escena(k - 1, T.escenas[k - 1].fin - .001) : escena(k, t));
      let xx = x0; fr.forEach(([c, w]) => { encima += `<path d="M${(xx + sh).toFixed(1)} 0 h${w} L${(xx + w).toFixed(1)} ${H} h${-w} Z" fill="${c}"/>`; xx += w; });
    } else if (tt === 'rebote' && L < DUR_TR.rebote) {   // v76: el plano anterior se encoge y el nuevo entra con rebote y un pequeño giro
      const p = L / DUR_TR.rebote, cx = W / 2, cy = H * .45, a = eio(cl(p / .45)), b = back(cl((p - .25) / .75));
      svg += `<rect width="${W}" height="${H}" fill="${ORA}"/>` +
        (a < 1 ? `<g opacity="${(1 - a).toFixed(3)}" transform="translate(${cx} ${cy}) scale(${(1 - .5 * a).toFixed(3)}) rotate(${(-6 * a).toFixed(2)}) translate(${-cx} ${-cy})">${escena(k - 1, T.escenas[k - 1].fin - .001)}</g>` : '') +
        (b > 0 ? `<g transform="translate(${cx} ${cy}) scale(${(.5 + .5 * b).toFixed(3)}) rotate(${(5 * (1 - b)).toFixed(2)}) translate(${-cx} ${-cy})">${escena(k, t)}</g>` : '');
    } else if (tt === 'burbujas' && L < DUR_TR.burbujas) {   // v76: círculos que crecen por toda la pantalla y destapan el plano nuevo
      const p = L / DUR_TR.burbujas, cols = HOR ? 6 : 4, filas = HOR ? 4 : 7, cw = W / cols, ch = H / filas, R0 = Math.hypot(cw, ch) * .62;
      let cp = '', aros = '';
      for (let i = 0; i < cols; i++) for (let j = 0; j < filas; j++) {
        const dd = (Math.hypot(i - cols / 2, j - filas / 2) / Math.hypot(cols / 2, filas / 2)), q = eio(cl((p - dd * .35) / .55)), r = R0 * q, x = (i + .5) * cw, y = (j + .5) * ch;
        if (r > .5) { cp += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r.toFixed(1)}"/>`; if (q < 1) aros += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r.toFixed(1)}" fill="none" stroke="${ORA}" stroke-width="${(8 * (1 - q)).toFixed(1)}"/>`; }
      }
      svg += escena(k - 1, T.escenas[k - 1].fin - .001) + `<defs><clipPath id="bu">${cp}</clipPath></defs><g clip-path="url(#bu)">${escena(k, t)}</g>` + aros;
    } else if (tt === 'barrido' && L < TR) {                 // barrido rápido con desenfoque de movimiento (alterna de lado y de arriba abajo)
      const p = eio(L / TR), ver = k % 2 === 1, bl = 46 * Math.sin(Math.PI * p), ant = escena(k - 1, T.escenas[k - 1].fin - .001), nue = escena(k, t), dir = k % 4 < 2 ? 1 : -1;
      svg += `<defs><filter id="mb" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="${ver ? '0 ' + bl.toFixed(1) : bl.toFixed(1) + ' 0'}"/></filter></defs><g filter="url(#mb)">` +
        `<g transform="translate(${ver ? 0 : (-dir * W * p).toFixed(1)} ${ver ? (-dir * H * p).toFixed(1) : 0})">${ant}</g><g transform="translate(${ver ? 0 : (dir * W * (1 - p)).toFixed(1)} ${ver ? (dir * H * (1 - p)).toFixed(1) : 0})">${nue}</g></g>`;
    } else svg += escena(k, t);
    if (!window.LIMPIO) {
      svg += pie(t) + cabecera(k, t, L) + subtitulos(k, t) + barra(t);
      if (k === N - 1 && P.fuentes) svg += `<text x="${W / 2}" y="${HOR ? H - 8 : 1076}" font-family="Inter" font-weight="700" font-size="${HOR ? 16 : 18}" text-anchor="middle" fill="${INK}" fill-opacity=".75">Fuentes: ${esc(P.fuentes)}</text>`;
    }
    // v62: bucle sin salto (cortos): en los últimos 0,35 s se funde con el primer plano, que es el que se ve al volver a empezar
    if (!HOR && !window.LIMPIO && N > 1 && t > DUR - .35) {
      const q = eio((t - (DUR - .35)) / .35);
      svg += `<g opacity="${q.toFixed(3)}">${escena(0, T.escenas[0].ini)}${cabecera(0, T.escenas[0].ini, 0)}${subtitulos(0, T.escenas[0].ini)}${barra(0)}</g>`;
    }
    svg += encima + (window.LIMPIO ? '' : marco()) + '</svg>';
    document.getElementById('lienzo').innerHTML = svg;
    cajas();
    return true;
  };
})();
