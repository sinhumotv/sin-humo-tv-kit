/* sin humo TV · MOTOR PRO (v56, 11-nov-2026) · cortos (720x1280) y largos (1280x720)
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
  const Z = HOR ? { x: 80, y: 128, w: 1120, h: 392 } : { x: SX + 26, y: 262, w: W - 2 * SX - 52, h: 560 };   // zona del gráfico
  const ZC = { x: Z.x + Z.w / 2, y: Z.y + Z.h / 2 };
  const SOM = HOR ? 7 : 8;                // desplazamiento de la sombra dura

  // ---------- piezas básicas ----------
  const partir = (s, max) => { const ls = []; let l = ''; for (const w of String(s || '').split(/\s+/).filter(Boolean)) { if (l && (l + ' ' + w).replace(/[§*]/g, '').length > max) { ls.push(l); l = w; } else l = l ? l + ' ' + w : w; } if (l) ls.push(l); return ls; };
  const tx = (x, y, s, size, fill = INK, anchor = 'middle', peso = 900, extra = '') =>
    `<text x="${x.toFixed(1)}" y="${y.toFixed(1)}" font-family="Inter" font-weight="${peso}" font-size="${size.toFixed(1)}" text-anchor="${anchor}" fill="${fill}" letter-spacing="-.5" ${extra}>${s}</text>`;
  // caja tipo pegatina: sombra dura + relleno + borde negro
  const caja = (x, y, w, h, rx, fill = BLA, sw = 5, som = SOM) =>
    `<rect x="${(x + som).toFixed(1)}" y="${(y + som).toFixed(1)}" width="${w.toFixed(1)}" height="${h.toFixed(1)}" rx="${rx}" fill="${INK}"/><rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${w.toFixed(1)}" height="${h.toFixed(1)}" rx="${rx}" fill="${fill}" stroke="${INK}" stroke-width="${sw}"/>`;
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
        const mx = b.height * .5, my = b.height * .22, mk = (dx, dy, fill, st) => { const r = document.createElementNS(NS, 'rect'); r.setAttribute('x', b.x - mx + dx); r.setAttribute('y', b.y - my + dy); r.setAttribute('width', b.width + 2 * mx); r.setAttribute('height', b.height + 2 * my); r.setAttribute('rx', b.height * .28); r.setAttribute('fill', fill); if (st) { r.setAttribute('stroke', INK); r.setAttribute('stroke-width', Math.max(3, b.height * .12)); } return r; };
        el.parentNode.insertBefore(mk(b.height * .16, b.height * .16, INK, false), el); el.parentNode.insertBefore(mk(0, 0, el.getAttribute('data-peg'), true), el);
      });
      if (SH.resalta) SH.resalta();
    } catch (e) { }
  }

  // ---------- fondo propio de sin humo TV (v47, 11-nov-2026) ----------
  // Pablo: «diferenciarnos del canal de En Plata, parece una copia». Fuera el crema con trama de puntos. Ahora:
  // degradado melocotón cálido, estelas de HUMO naranja que suben despacio (el humo que el canal quita), la nube tachada de la marca
  // enorme y muy suave al fondo y un marco naranja redondeado alrededor de la pantalla.
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
      `<rect width="${W}" height="${H}" fill="url(#gF)"/>` +
      `<circle cx="${(W * (.3 + .1 * Math.sin(t * .3 + k))).toFixed(1)}" cy="${(H * .3).toFixed(1)}" r="${Math.max(W, H) * .45}" fill="url(#gL)"/>` +
      [0, 1, 2].map(i => humo(i, t + k * 1.7)).join('') +
      // v60: partículas de humo que suben despacio (vida en el fondo)
      [...Array(HOR ? 14 : 12).keys()].map(i => { const sp = .035 + .02 * frac(i * .37), f = frac(t * sp + i * .618), x = W * frac(i * .414 + .13) + 30 * Math.sin(t * .7 + i), y = H * (1.05 - 1.1 * f), r = 4 + 9 * frac(i * .73);
        return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r.toFixed(1)}" fill="${GRAVE ? INK : (i % 3 ? '#fff' : ORA)}" opacity="${((GRAVE ? .05 : .22) * Math.sin(Math.PI * f)).toFixed(3)}"/>`; }).join('') +
      `<g opacity="${GRAVE ? .04 : .07}" transform="translate(${mx} ${my}) rotate(${rot.toFixed(2)})">${nube(0, 0, HOR ? 7 : 8)}</g>`;
  }
  function marco() {           // marco naranja de la marca (encima de todo, fino y redondeado)
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
  const sticker = (x, y, r, L, t0, nombre, c) => { const e = back((L - t0) / .4); return e <= 0 ? '' : `<g transform="translate(${x} ${y}) rotate(${(-6 + 3 * Math.sin(L * 1.4)).toFixed(2)}) scale(${e.toFixed(3)})"><circle cx="${SOM}" cy="${SOM}" r="${r}" fill="${INK}"/><circle cx="0" cy="0" r="${r}" fill="${BLA}" stroke="${INK}" stroke-width="5"/><g transform="scale(${(r / 150).toFixed(3)})">${icono(nombre, 0, 0, 1.25, L, c)}</g></g>`; };
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
      return `<rect x="${(ZC.x - wS / 2 * eo((L - .15) / .4)).toFixed(1)}" y="${(yN - size * .3).toFixed(1)}" width="${(wS * eo((L - .15) / .4)).toFixed(1)}" height="${(size * .36).toFixed(1)}" rx="${size * .06}" fill="${c === INK ? ORO : c}" opacity=".9" transform="rotate(-1.5 ${ZC.x} ${yN})"/>` +
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
          (w > wM * .5 ? tx(x0 + w - 22, y + ah * .7, esc(contar(String(o.valor || ''), p)), ah * .58, c === ORA ? '#fff' : INK, 'end') : tx(x0 + w + 26, y + ah * .7, esc(contar(String(o.valor || ''), p)), ah * .58, INK, 'start')) + `</g>`;
      };
      let dif = '';   // v45: pastilla con la diferencia (+92 %, ×3…) cuando las dos cifras son comparables
      const tiempo = /\b(1[89]|20)\d\d\b|antes|ahora|hoy|ayer|año|mes|semana|actual|anterior|nuev|viej|pasad/i.test(String(a.etiqueta || '') + ' ' + String(b.etiqueta || ''));   // v53: solo si es un antes/después
      if (tiempo && na > 0 && nb > 0 && na !== nb && !/%/.test(String(a.valor) + String(b.valor))) {
        const r = nb / na, pc = Math.round((r - 1) * 100);
        const et = r >= 2.95 ? '×' + (Math.round(r * 10) / 10).toString().replace('.', ',') : (pc > 0 ? '+' : '') + pc + ' %';
        const t0 = 1.3, e2 = back((L - t0) / .4);
        if (L > t0 && Math.abs(pc) >= 3) dif = peg(HOR ? Z.x + Z.w - 120 : Z.x + Z.w - 70, HOR ? ZC.y + 10 : ZC.y + 8, et, HOR ? 36 : 34, pc > 0 ? ROJ : VER, '#fff', 'middle', 1, -6, e2);
      }
      return fila(a, na, ZC.y - ah - (HOR ? 34 : 70), GRI, .15) + fila(b, nb, ZC.y + (HOR ? 62 : 86), ORA, .6) + dif;
    },
    grafico(v, L, d) {
      const vs = (v.valores || []).slice(0, 7), et = v.etiquetas || [], n = vs.length || 1, mx = Math.max(...vs.map(x => Math.abs(num(x))), 1e-9), base = Z.y + Z.h - (HOR ? 50 : 66), alto = Z.h - (HOR ? 160 : 220);
      const paso = Math.min(HOR ? 190 : 150, Z.w / n), an = paso * .6, x0 = ZC.x - paso * n / 2 + (paso - an) / 2;
      let o = v.titulo ? cinetico(v.titulo, ZC.x, Z.y + (HOR ? 36 : 40), HOR ? 40 : 34, L, { max: HOR ? 46 : 30 }) : '';
      o += [1, 2, 3].map(i => `<path d="M${Z.x} ${base - alto * i / 3} H${Z.x + Z.w}" stroke="${INK}" stroke-opacity=".16" stroke-width="3" stroke-dasharray="4 12"/>`).join('');
      vs.forEach((x, i) => {
        const t0 = .25 + i * Math.min(.35, d * .5 / n), p = back((L - t0) / .7), h = Math.max(12, alto * Math.abs(num(x)) / mx * p), xx = x0 + i * paso, ult = i === n - 1, op = cl((L - t0) / .12);
        o += `<g opacity="${op}">` + caja(xx, base - h, an, h, Math.min(14, an * .16), ult ? ORA : GRI) +
          tx(xx + an / 2, base - h - 16, esc(contar(String(x), cl((L - t0) / .7))), Math.min(HOR ? 40 : 32, an * .45), INK) +
          tx(xx + an / 2, base + (HOR ? 42 : 48), esc(et[i] || ''), Math.min(HOR ? 28 : 24, paso * .3), INK, 'middle', 800) + `</g>`;
      });
      return o + `<path d="M${Z.x} ${base} H${Z.x + Z.w}" stroke="${INK}" stroke-width="6" stroke-linecap="round"/>`;
    },
    lista(v, L, d) {
      const it = (v.items || []).slice(0, 4), n = it.length || 1, c = col(v.color), hT = v.titulo ? (HOR ? 74 : 84) : 0, ah = Math.min(HOR ? 80 : 80, (Z.h - hT - 10) / n - 18), y0 = Z.y + hT + (Z.h - hT - n * (ah + 18)) / 2;
      const act = Math.min(n - 1, Math.floor(cl((L - .3) / Math.max(1, d - .8)) * n));
      let o = v.titulo ? cinetico(v.titulo, HOR ? Z.x + 20 : ZC.x, Z.y + (HOR ? 46 : 62), HOR ? 46 : 38, L, { max: HOR ? 48 : 28, anchor: HOR ? 'start' : 'middle' }) : '';
      it.forEach((s, i) => {
        const t0 = .3 + i * (Math.max(1, d - .8) / n), e = back((L - t0) / .4); if (L < t0) return;
        const y = y0 + i * (ah + 18), on = i === act, fs = Math.min(ah * .4, (Z.w - 160) / (Math.max(8, [...String(s)].length) * .56));
        o += `<g transform="translate(${((1 - e) * (i % 2 ? -1 : 1) * 300).toFixed(1)} 0) rotate(${on ? -1 : 0} ${ZC.x} ${y + ah / 2})" opacity="${cl((L - t0) / .12)}">` + caja(Z.x + 8, y, Z.w - 24, ah, ah * .26, on ? c : BLA) +
          `<circle cx="${Z.x + 8 + ah * .5}" cy="${y + ah / 2}" r="${ah * .3}" fill="${on ? '#fff' : c}" stroke="${INK}" stroke-width="4"/>` + tx(Z.x + 8 + ah * .5, y + ah / 2 + ah * .13, String(i + 1), ah * .36, on ? c : '#fff') +
          tx(Z.x + 8 + ah * 1.05, y + ah / 2 + fs * .36, esc(s), fs, on && c !== ORO ? '#fff' : INK, 'start', 800) + `</g>`;
      });
      return o;
    },
    frase(v, L, d) {
      const size = HOR ? 48 : 40, max = HOR ? 38 : 24, alto = altoCin(v.texto, size, max), hC = alto + (HOR ? 110 : 150), wC = HOR ? Z.w - 160 : Z.w - 16, x = ZC.x - wC / 2, y = ZC.y - hC / 2, e = back(L / .4);
      return `<g transform="translate(${ZC.x} ${ZC.y}) scale(${e.toFixed(3)}) rotate(-1) translate(${-ZC.x} ${-ZC.y})">` + caja(x, y, wC, hC, 26, BLA, 6, SOM + 3) +
        `<text x="${x + 22}" y="${y + (HOR ? 96 : 112)}" font-family="Georgia, serif" font-weight="900" font-size="${HOR ? 170 : 140}" fill="${ORA}">“</text></g>` +
        cinetico(v.texto, ZC.x, y + (HOR ? 76 : 104) + size * .5, size, L, { max, t0: .3, paso: Math.min(.1, d * .5 / Math.max(6, String(v.texto || '').split(' ').length)) }) +
        (v.fuente ? peg(ZC.x + (HOR ? 300 : 150), y + hC + 4, v.fuente, HOR ? 26 : 30, INK, '#fff', 'middle', eo((L - d * .45) / .3), -3, back((L - d * .45) / .35)) : '');
    },
    linea(v, L, d) {
      const hs = (v.hitos || []).slice(0, 5), n = hs.length || 1, paso = Math.min(HOR ? 92 : 122, (Z.h - 10) / n), y0 = ZC.y - paso * (n - 1) / 2, x = HOR ? Z.x + 240 : ZC.x - Math.min(200, 40 + Math.max(...hs.map(h => Math.max(String(h.texto || '').length * 17, String(h.fecha || '').length * 15))) / 2);
      const tramo = Math.max(1, d - .8) / n, prog = cl((L - .2) / Math.max(1, d - .8)), yF = y0 + (n - 1) * paso * prog;
      let o = `<path d="M${x} ${y0} V${y0 + (n - 1) * paso}" stroke="${GRI}" stroke-width="10" stroke-linecap="round"/><path d="M${x} ${y0} V${yF.toFixed(1)}" stroke="${ORA}" stroke-width="10" stroke-linecap="round"/>`;
      hs.forEach((h, i) => {
        const t0 = .2 + i * tramo, on = L >= t0, e = back((L - t0) / .35), y = y0 + i * paso, ult = on && (i === n - 1 || L < t0 + tramo);
        o += `<circle cx="${x}" cy="${y}" r="${on ? 18 + (ult ? 4 * Math.sin(L * 6) : 0) : 12}" fill="${on ? ORA : BLA}" stroke="${INK}" stroke-width="5"/>`;
        if (on) o += `<g transform="translate(${((1 - e) * 140).toFixed(1)} 0)" opacity="${cl((L - t0) / .12)}">` + peg(x + 46, y + (HOR ? 10 : -6), String(h.fecha || ''), HOR ? 26 : 24, ult ? ORA : INK, '#fff', 'start', 1, -2) +
          tx(x + 46 + (HOR ? 170 : 0), y + (HOR ? 13 : 44), esc(h.texto || ''), HOR ? 38 : 32, INK, 'start', 800) + `</g>`;
      });
      return o;
    },
    icono(v, L, d) {
      const c = col(v.color), ix = HOR ? Z.x + 190 : ZC.x, iy = HOR ? ZC.y : Z.y + 140, size = HOR ? 58 : 44, max = HOR ? 19 : 22, alto = altoCin(v.texto, size, max);
      const tx0 = HOR ? Z.x + 400 + (Z.w - 400) / 2 : ZC.x, ty = HOR ? ZC.y - alto / 2 + size * .8 : Z.y + 300 + size * .5;
      const R0 = HOR ? 150 : 112, ondas = [0, 1].map(j => { const f = frac(L / 1.8 + j / 2); return `<circle cx="${ix}" cy="${iy}" r="${(R0 + 10 + 70 * f).toFixed(1)}" fill="none" stroke="${c}" stroke-width="${(6 * (1 - f)).toFixed(1)}" opacity="${(.5 * (1 - f) * cl(L / .4)).toFixed(2)}"/>`; }).join('');
      const orbita = atras => [0, 1, 2].map(j => { const a = L * 1.3 + j * 2.094, r = R0 + 26; if ((Math.sin(a) < 0) !== atras) return ''; return `<circle cx="${(ix + r * Math.cos(a)).toFixed(1)}" cy="${(iy + r * .45 * Math.sin(a)).toFixed(1)}" r="${j === 0 ? 11 : 7}" fill="${[ORA, ORO, c][j]}" stroke="${INK}" stroke-width="3" opacity="${cl((L - .3) / .3).toFixed(2)}"/>`; }).join('');   // v61: ondas y órbita (por detrás en la mitad de arriba)
      return ondas + orbita(true) + `<g transform="translate(0 ${(5 * Math.sin(L * 2.2)).toFixed(1)})">${sticker(ix, iy, R0, L, 0, v.icono, c)}</g>` + orbita(false) +
        cinetico(v.texto, tx0, ty, size, L, { max, t0: .2 }) +
        (v.etiqueta ? peg(tx0 + (HOR ? 120 : 110), ty + alto + 6, String(v.etiqueta), HOR ? 28 : 24, c === ORA ? AZU : c, '#fff', 'middle', eo((L - .8) / .25), 4, back((L - .8) / .35)) : '');
    },
    pregunta(v, L, d) {
      const size = HOR ? 60 : 48, max = HOR ? 18 : 20, alto = altoCin(v.texto, size, max), qx = HOR ? Z.x + 190 : ZC.x, qy = HOR ? ZC.y + 120 : Z.y + 230, e = back(L / .5), fs = HOR ? 380 : 260;
      const q = (dx, dy, f, st) => `<text x="${dx}" y="${dy}" font-family="Inter" font-weight="900" font-size="${fs}" text-anchor="middle" fill="${f}"${st ? ` stroke="${INK}" stroke-width="10" stroke-linejoin="round"` : ''}>?</text>`;
      return `<g transform="translate(${qx} ${qy}) rotate(${(-9 + 7 * Math.sin(L * 1.8)).toFixed(2)}) scale(${e.toFixed(3)})">${q(SOM + 2, SOM + 2, INK, true)}${q(0, 0, ORA, true)}</g>` +
        cinetico(v.texto, HOR ? Z.x + 400 + (Z.w - 400) / 2 : ZC.x, HOR ? ZC.y - alto / 2 + size * .8 : Z.y + 330, size, L, { max, t0: .25 });
    },
    titular(v, L, d) {
      const s = String(v.texto || ''), max = HOR ? 20 : 14, size = Math.min(HOR ? 124 : 84, (Z.w * .98) / (Math.min(max, Math.max(...partir(s.replace(/\*/g, ''), max).map(l => l.length), 4)) * .6));
      const alto = altoCin(s, size, max);
      return cinetico(s, ZC.x, ZC.y - alto / 2 + size * .82, size, L, { max, paso: .11, clave: col(v.color) });
    },
    // ===== v56 (11-nov-2026): 8 gráficos nuevos para que no se repitan siempre los mismos =====
    // porcentaje: anillo que se llena con la cifra en el centro  {"tipo":"porcentaje","valor":"33,6 %","texto":"…","color":"rojo"}
    porcentaje(v, L, d) {
      const c = col(v.color), pct = cl(num(v.valor) / 100), p = eo(cl((L - .15) / Math.min(1.2, d * .5))), r = HOR ? 130 : 140, sw = HOR ? 38 : 42;
      const cx = HOR ? Z.x + 220 : ZC.x, cy = HOR ? ZC.y : Z.y + 180, C = 2 * Math.PI * r, e = back(L / .4), s = String(v.valor || '');
      const fsN = Math.min(HOR ? 92 : 96, 2 * r * .82 / (Math.max(3, s.length) * .58)), size = HOR ? 50 : 38, max = HOR ? 22 : 24, alto = altoCin(v.texto, size, max), R = r + sw / 2 + 8;
      return `<g transform="translate(${cx} ${cy}) scale(${e.toFixed(3)})"><circle cx="${SOM}" cy="${SOM}" r="${R}" fill="${INK}"/><circle r="${R}" fill="${BLA}" stroke="${INK}" stroke-width="5"/>` +
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
        o += `<g transform="translate(${x.toFixed(1)} ${y.toFixed(1)}) scale(${(e * (on ? 1 + .05 * Math.sin(L * 5) : 1) * s / 78).toFixed(3)})"><circle cx="0" cy="-24" r="17" fill="${f}" stroke="${INK}" stroke-width="5"/><path d="M-27 36 v-20 a27 24 0 0 1 54 0 v20 z" fill="${f}" stroke="${INK}" stroke-width="5" stroke-linejoin="round"/></g>`;
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
          `<path d="M${x} ${y + 70} V${y + 26} a26 26 0 0 1 26 -26 H${x + w - 26} a26 26 0 0 1 26 26 V${y + 70} Z" fill="${c}" stroke="${INK}" stroke-width="5"/>` +
          tx(cx, y + 47, esc(nom), fsN, '#fff', 'middle', 900) +
          `<circle cx="${cx}" cy="${yC}" r="${rC}" fill="${c}" fill-opacity=".16" stroke="${INK}" stroke-width="5"/>` + tx(cx, yC + rC * .3, esc(ini), rC * .85, c, 'middle', 900) +
          ls.map((l, j) => tx(cx, yC + rC + 50 + j * fs * 1.2, esc(l), fs, INK, 'middle', 800, `opacity="${eo((L - t0 - .3 - j * .08) / .25).toFixed(2)}"`)).join('') + `</g>`;
      };
      const vy = HOR ? ZC.y : Z.y + 30 + (Z.h - 90) / 2, ev = back((L - .6) / .4), pul = 1 + .06 * Math.sin(L * 6);
      return lado(v.a, 0) + lado(v.b, 1) + (ev > 0 ? `<g transform="translate(${ZC.x} ${vy}) rotate(-8) scale(${(ev * pul).toFixed(3)})"><circle cx="${SOM}" cy="${SOM}" r="${HOR ? 54 : 46}" fill="${INK}"/><circle r="${HOR ? 54 : 46}" fill="${ORO}" stroke="${INK}" stroke-width="6"/>${tx(0, HOR ? 17 : 15, 'VS', HOR ? 48 : 40, INK)}</g>` : '');
    },
    // mapa de España con chinchetas en las ciudades nombradas  {"tipo":"mapa","lugares":["Oviedo","Madrid"],"texto":"…"}
    mapa(v, L, d) {
      const can0 = (v.lugares || []).some(s => (CIUDADES[norm(s)] || [0])[0] < -12), alto = can0 ? 10.1 : 8.2;   // con Canarias, el mapa baja hasta su recuadro
      const lon0 = -9.6, lat0 = 43.95, k = HOR ? Math.min(44, 380 / alto) : Math.min(55, Z.w / 9.96, (Z.h - 90) / alto), kx = k * .766, mw = 13.4 * kx, mh = alto * k;
      const ox = HOR ? Z.x + 30 : ZC.x - mw / 2, oy = HOR ? ZC.y - mh / 2 : Z.y + 10, P_ = (lo, la) => [ox + (lo - lon0) * kx, oy + (lat0 - la) * k];
      const dPath = 'M' + ESP.map(([lo, la]) => P_(lo, la).map(n => n.toFixed(1)).join(' ')).join(' L') + ' Z';
      const p = eo(L / .7), f = eo((L - .4) / .4);
      let o = `<path d="${dPath}" transform="translate(${SOM} ${SOM})" fill="${INK}" opacity="${f.toFixed(2)}"/>` +
        `<path d="${dPath}" fill="${BLA}" fill-opacity="${f.toFixed(2)}" stroke="${INK}" stroke-width="5" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="${(1 - p).toFixed(3)}"/>` +
        BAL.map(([lo, la, rx, ry]) => { const [x, y] = P_(lo, la); return `<ellipse cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" rx="${rx * kx}" ry="${ry * k}" fill="${BLA}" stroke="${INK}" stroke-width="4" opacity="${f.toFixed(2)}"/>`; }).join('');
      const ls = (v.lugares || []).map(s => [s, CIUDADES[norm(s)]]).filter(x => x[1]).slice(0, 3);
      // Canarias en recuadro abajo a la izquierda (solo si se nombra algún lugar canario): se trasladan a (-8.6, 36.9) en el mapa
      const CAN = [[-18.0, 27.75, .13, .1], [-17.85, 28.68, .12, .18], [-17.2, 28.1, .12, .1], [-16.55, 28.3, .35, .22], [-15.6, 27.95, .28, .25], [-14.0, 28.4, .45, .22], [-13.6, 29.05, .3, .18]];
      const canario = ls.some(([, [lo, la]]) => lo < -12), mov = ([lo, la]) => lo < -12 ? [lo + 8.7, la + 6.25] : [lo, la];
      if (canario) {
        const [bx, by] = P_(-9.5, 35.75), [bx2, by2] = P_(-4.55, 33.9);
        o += `<rect x="${bx.toFixed(1)}" y="${by.toFixed(1)}" width="${(bx2 - bx).toFixed(1)}" height="${(by2 - by).toFixed(1)}" rx="10" fill="none" stroke="${INK}" stroke-width="3" stroke-dasharray="8 6" opacity="${f.toFixed(2)}"/>` +
          CAN.map(([lo, la, rx, ry]) => { const [x, y] = P_(...mov([lo, la])); return `<ellipse cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" rx="${rx * kx}" ry="${ry * k}" fill="${BLA}" stroke="${INK}" stroke-width="4" opacity="${f.toFixed(2)}"/>`; }).join('');
      }
      ls.forEach(([nom, [lo, la]], i) => {
        const t0 = .8 + i * .35, e = back((L - t0) / .4); if (e <= 0) return;
        const [x, y] = P_(...mov([lo, la])), cae = (1 - eo((L - t0) / .3)) * 90, rip = frac((L - t0) / 1.2);
        o += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${(8 + 40 * rip).toFixed(1)}" fill="none" stroke="${ROJ}" stroke-width="4" opacity="${(1 - rip).toFixed(2)}"/>` +
          `<g transform="translate(${x.toFixed(1)} ${(y - cae).toFixed(1)}) scale(${(e * (HOR ? .5 : .55)).toFixed(3)})"><path d="M0 0 C-30 -40 -40 -55 -40 -75 A40 40 0 0 1 40 -75 C40 -55 30 -40 0 0 Z" fill="${ROJ}" stroke="${INK}" stroke-width="7"/><circle cy="-75" r="14" fill="${BLA}" stroke="${INK}" stroke-width="5"/></g>` +
          peg(x + (x > ox + mw * .6 ? -20 : 20), y - (HOR ? 54 : 58), String(nom).toUpperCase(), HOR ? 20 : 20, INK, '#fff', x > ox + mw * .6 ? 'end' : 'start', eo((L - t0 - .2) / .2), -3);
      });
      const size = HOR ? 46 : 36, max = HOR ? 20 : 26;
      return o + (v.texto ? cinetico(v.texto, HOR ? ox + mw + (Z.x + Z.w - ox - mw) / 2 : ZC.x, HOR ? ZC.y - altoCin(v.texto, size, max) / 2 + size * .8 : oy + mh + 46, size, L, { max, t0: .5 }) : '');
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
        const w = Math.min(HOR ? 760 : Z.w - 30, Math.max(...b.map(l => l.length), String(ln.quien || '').length) * fs * .56 + 64), x = der ? Z.x + Z.w - w : Z.x, c = der ? AZU : ORA, yy = y;
        y += h + 30;
        if (e <= 0) return;
        const ax = der ? x + w - 34 : x + 34;
        o += `<g transform="translate(${ax} ${yy + h}) scale(${e.toFixed(3)}) translate(${-ax} ${-(yy + h)})">` +
          `<path d="M${ax - 16} ${yy + h - 6} L${ax + (der ? 22 : -22)} ${yy + h + 26} L${ax + 16} ${yy + h - 6} Z" fill="${der ? '#e7eeff' : '#fff0e3'}" stroke="${INK}" stroke-width="5" stroke-linejoin="round"/>` +
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
        o += `<g opacity="${cl((L - t0) / .15)}"><circle cx="${Z.x + ah / 2 + SOM / 2}" cy="${y + ah / 2 + SOM / 2}" r="${ah / 2}" fill="${INK}"/><circle cx="${Z.x + ah / 2}" cy="${y + ah / 2}" r="${ah / 2}" fill="${med[i] || BLA}" stroke="${INK}" stroke-width="4"/>` +
          tx(Z.x + ah / 2, y + ah / 2 + ah * .16, String(i + 1), ah * .45, INK) + caja(xL, y, w, ah, ah * .3, top ? ORA : BLA, 4) +
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
        `<path d="M${x} ${y + 84} V${y + 26} a26 26 0 0 1 26 -26 H${x + s - 26} a26 26 0 0 1 26 26 V${y + 84} Z" fill="${ROJ}" stroke="${INK}" stroke-width="6"/>` +
        tx(cx, y + 60, esc(mes), 44, '#fff', 'middle', 900, 'letter-spacing="4"') +
        [-1, 1].map(j => `<rect x="${cx + j * 70 - 9}" y="${y - 22}" width="18" height="44" rx="9" fill="${GRI}" stroke="${INK}" stroke-width="5"/>`).join('') +
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
        `<path d="M${cx - R + SOM} ${cy + SOM} A${R} ${R} 0 0 1 ${cx + R + SOM} ${cy + SOM} Z" fill="${INK}"/><path d="M${cx - R} ${cy} A${R} ${R} 0 0 1 ${cx + R} ${cy} Z" fill="${BLA}" stroke="${INK}" stroke-width="5"/>` +
        arc(Math.PI, Math.PI * 1.5, VER) + arc(Math.PI * 1.5, Math.PI * 1.8, ORO) + arc(Math.PI * 1.8, Math.PI * 2, ROJ);
      for (let i = 0; i <= 10; i++) { const a = Math.PI * (1 + i / 10), [x0, y0] = pt(a, r - sw / 2 - 8), [x1, y1] = pt(a, r - sw / 2 - (i % 5 ? 20 : 34)); o += `<path d="M${x0.toFixed(1)} ${y0.toFixed(1)} L${x1.toFixed(1)} ${y1.toFixed(1)}" stroke="${INK}" stroke-width="${i % 5 ? 3 : 5}"/>`; }
      o += `<g transform="rotate(${ang.toFixed(2)} ${cx} ${cy})"><path d="M${cx} ${cy - 12} L${cx - r + 30} ${cy} L${cx} ${cy + 12} Z" fill="${INK}"/></g><circle cx="${cx}" cy="${cy}" r="22" fill="${ORA}" stroke="${INK}" stroke-width="5"/></g>`;
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
        `<path d="${linea}" transform="translate(${SOM / 2} ${SOM / 2})" fill="none" stroke="${INK}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>` +
        `<path d="${linea}" fill="none" stroke="${ORA}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>`;
      pts.forEach((q, i) => { if (i > pos + .001) return; o += `<circle cx="${q[0].toFixed(1)}" cy="${q[1].toFixed(1)}" r="9" fill="${BLA}" stroke="${INK}" stroke-width="4"/>` + tx(q[0], y1 + (HOR ? 40 : 44), esc(et[i] || ''), HOR ? 24 : 22, INK, 'middle', 800); });
      o += `<circle cx="${cur[0].toFixed(1)}" cy="${cur[1].toFixed(1)}" r="${(16 + 3 * Math.sin(L * 8)).toFixed(1)}" fill="${ORA}" stroke="${INK}" stroke-width="5"/>`;
      const ult = String((v.valores || [])[n - 1] || ''), ep = back((p - .97) / .03 + (L - Math.min(1.6, d * .6) - .25) / .3);
      if (p > .97) o += peg(Math.min(cur[0], x1 - 20), cur[1] - 34, ult, HOR ? 32 : 30, INK, '#fff', 'middle', 1, -3, cl(ep, 0, 1.2));
      return o + `<path d="M${x0} ${y1} H${x1 + 20}" stroke="${INK}" stroke-width="6" stroke-linecap="round"/>`;
    },
    // reparto en tarta (rosco) con leyenda  {"tipo":"reparto","titulo":"…","partes":[{"etiqueta":"Sí","valor":"58"},{"etiqueta":"No","valor":"42"}]}
    reparto(v, L, d) {
      const ps = (v.partes || []).slice(0, 5), tot = ps.reduce((a, b) => a + Math.abs(num(b.valor)), 0) || 1, pal = [ORA, AZU, VER, ORO, MOR];
      const r = HOR ? 140 : 125, sw = HOR ? 70 : 62, cx = HOR ? Z.x + 230 : ZC.x, cy = HOR ? ZC.y : Z.y + (v.titulo ? 215 : 175), C = 2 * Math.PI * r, e = back(L / .4);
      let acc = 0, o = `<g transform="translate(${cx} ${cy}) scale(${e.toFixed(3)})"><circle cx="${SOM}" cy="${SOM}" r="${r + sw / 2 + 6}" fill="${INK}"/><circle r="${r + sw / 2 + 6}" fill="${BLA}" stroke="${INK}" stroke-width="5"/>`;
      ps.forEach((q, i) => {
        const fr = Math.abs(num(q.valor)) / tot, t0 = .2 + i * .25, p = eio((L - t0) / .5), c = q.color ? col(q.color) : pal[i];
        o += `<circle r="${r}" fill="none" stroke="${c}" stroke-width="${sw}" stroke-dasharray="${(C * fr * p).toFixed(1)} ${C.toFixed(1)}" transform="rotate(${(-90 + 360 * acc).toFixed(2)})"/>`;
        acc += fr;
      });
      o += `<circle r="${r - sw / 2}" fill="none" stroke="${INK}" stroke-width="4"/><circle r="${r + sw / 2}" fill="none" stroke="${INK}" stroke-width="4"/></g>`;
      const lx = HOR ? Z.x + 470 : Z.x + 20, ly = HOR ? ZC.y - ps.length * 30 : cy + r + sw / 2 + 50, fs = HOR ? 32 : 28;
      ps.forEach((q, i) => {
        const t0 = .3 + i * .25, ee = back((L - t0) / .35), c = q.color ? col(q.color) : pal[i], y = ly + i * (HOR ? 60 : 50), pc = Math.round(Math.abs(num(q.valor)) / tot * 100);
        if (ee <= 0) return;
        o += `<g transform="translate(${((1 - ee) * -80).toFixed(1)} 0)" opacity="${cl((L - t0) / .15)}"><rect x="${lx}" y="${y - fs * .8}" width="${fs}" height="${fs}" rx="7" fill="${c}" stroke="${INK}" stroke-width="4"/>` +
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
      let o = `<path d="${lin}" transform="translate(${SOM} ${SOM})" fill="none" stroke="${INK}" stroke-width="26" stroke-linecap="round" stroke-linejoin="round"/><path d="${lin}" fill="none" stroke="${c}" stroke-width="26" stroke-linecap="round" stroke-linejoin="round"/>` +
        `<g transform="translate(${cur[0].toFixed(1)} ${cur[1].toFixed(1)}) rotate(${a.toFixed(1)})"><path d="M-6 -36 L46 0 L-6 36 Z" fill="${c}" stroke="${INK}" stroke-width="6" stroke-linejoin="round"/></g>`;
      for (let i = 0; i < 3; i++) { const fx = frac(L * 1.4 + i / 3); o += `<path d="M${(cur[0] - 70 - 60 * fx).toFixed(1)} ${(cur[1] + (i - 1) * 26 + (sube ? 30 : -30)).toFixed(1)} h${-40 * (1 - fx)}" stroke="${INK}" stroke-width="5" stroke-linecap="round" opacity="${((1 - fx) * p).toFixed(2)}"/>`; }
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
        o += `<g opacity="${cl(q * 3).toFixed(2)}"><ellipse cx="${x}" cy="${(y + 8).toFixed(1)}" rx="${cw / 2}" ry="${ch * .55}" fill="${INK}"/><rect x="${x - cw / 2}" y="${(y - 4).toFixed(1)}" width="${cw}" height="12" fill="#e0a800" stroke="${INK}" stroke-width="4"/><ellipse cx="${x}" cy="${(y - 4).toFixed(1)}" rx="${cw / 2}" ry="${ch * .55}" fill="${ORO}" stroke="${INK}" stroke-width="4"/><ellipse cx="${x}" cy="${(y - 4).toFixed(1)}" rx="${cw / 2 - 14}" ry="${ch * .32}" fill="none" stroke="#e0a800" stroke-width="3"/></g>`;
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
      let o = `<g transform="translate(${cx} ${cy}) scale(${e.toFixed(3)})"><circle cx="${SOM}" cy="${SOM}" r="${r}" fill="${INK}"/><circle r="${r}" fill="${BLA}" stroke="${INK}" stroke-width="8"/>`;
      for (let i = 0; i < 12; i++) { const a = i * Math.PI / 6; o += `<path d="M${((r - 18) * Math.sin(a)).toFixed(1)} ${(-(r - 18) * Math.cos(a)).toFixed(1)} L${((r - (i % 3 ? 32 : 44)) * Math.sin(a)).toFixed(1)} ${(-(r - (i % 3 ? 32 : 44)) * Math.cos(a)).toFixed(1)}" stroke="${INK}" stroke-width="${i % 3 ? 4 : 8}" stroke-linecap="round"/>`; }
      o += `<g transform="rotate(${aH.toFixed(1)})"><path d="M-9 14 L0 ${-r * .5} L9 14 Z" fill="${INK}"/></g><g transform="rotate(${aM.toFixed(1)})"><path d="M-6 16 L0 ${-r * .78} L6 16 Z" fill="${INK}"/></g>` +
        `<g transform="rotate(${aS.toFixed(1)})"><path d="M0 22 V${-r * .82}" stroke="${ORA}" stroke-width="4"/></g><circle r="14" fill="${ORA}" stroke="${INK}" stroke-width="4"/></g>`;
      const hs = `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}`, size = HOR ? 46 : 36, max = HOR ? 20 : 24;
      return o + peg(cx, cy + r + (HOR ? 46 : 52), hs + (/h/i.test(String(v.hora || '')) || true ? ' H' : ''), HOR ? 40 : 40, INK, ORO, 'middle', eo((L - 1.1) / .2), -2, back((L - 1.1) / .35)) +
        (v.texto ? cinetico(v.texto, HOR ? Z.x + 450 + (Z.w - 450) / 2 : ZC.x, HOR ? ZC.y - altoCin(v.texto, size, max) / 2 + size * .8 : cy + r + 130, size, L, { max, t0: .5 }) : '');
    },
    // lista de comprobación con ✓ y ✗  {"tipo":"checklist","titulo":"…","items":[{"texto":"…","ok":true},{"texto":"…","ok":false}]}
    checklist(v, L, d) {
      const it = (v.items || []).slice(0, 4), n = it.length || 1, hT = v.titulo ? (HOR ? 70 : 80) : 0, ah = Math.min(HOR ? 76 : 84, (Z.h - hT) / n - 18), y0 = Z.y + hT + (Z.h - hT - n * (ah + 18)) / 2;
      let o = v.titulo ? cinetico(v.titulo, ZC.x, Z.y + (HOR ? 44 : 56), HOR ? 40 : 36, L, { max: HOR ? 46 : 28 }) : '';
      it.forEach((q, i) => {
        const t0 = .25 + i * Math.max(.45, (d - .8) / n), e = back((L - t0) / .4); if (e <= 0) return;
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
      if (tot >= 50) o += `<path d="M${cx} ${cy - R1 - 26} V${cy - R0 + 20}" stroke="${INK}" stroke-width="4" stroke-dasharray="8 6" opacity="${eo((L - 1.2) / .3).toFixed(2)}"/>` + peg(cx, cy - R1 - 34, `MAYORÍA ${may}`, HOR ? 22 : 22, INK, '#fff', 'middle', eo((L - 1.2) / .3), 0);
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
    pasos(v, L, d) {
      const it = (v.items || []).slice(0, 4), n = it.length || 1, tramo = Math.max(.45, (d - .6) / n);
      const hB = HOR ? 150 : 96, wB = HOR ? (Z.w - (n - 1) * 70) / n : Z.w - 40, gap = HOR ? 70 : Math.min(54, (Z.h - n * hB) / Math.max(1, n - 1));
      const tot = HOR ? Z.w : n * hB + (n - 1) * gap, y0 = HOR ? ZC.y - hB / 2 : ZC.y - tot / 2;
      let o = '';
      it.forEach((s, i) => {
        const t0 = .2 + i * tramo, e = back((L - t0) / .4); if (e <= 0) return;
        const x = HOR ? Z.x + i * (wB + 70) : ZC.x - wB / 2, y = HOR ? y0 : y0 + i * (hB + gap), act = L < t0 + tramo || i === n - 1, c = [ORA, AZU, VER, MOR][i % 4], cx = x + wB / 2, cy = y + hB / 2;
        const fs = Math.min(HOR ? 34 : 32, (wB - (HOR ? 40 : 110)) / (Math.max(6, String(s).length) * .55));
        o += `<g transform="translate(${cx} ${cy}) scale(${(e * (act ? 1 + .03 * Math.sin(L * 6) : 1)).toFixed(3)}) translate(${-cx} ${-cy})">` + caja(x, y, wB, hB, 24, act ? c : BLA, 5) +
          `<circle cx="${HOR ? cx : x + 50}" cy="${HOR ? y : cy}" r="30" fill="${BLA}" stroke="${INK}" stroke-width="5"/>` + tx(HOR ? cx : x + 50, (HOR ? y : cy) + 12, String(i + 1), 34, c) +
          tx(HOR ? cx : x + 96, HOR ? cy + 26 : cy + fs * .36, esc(s), fs, act && c !== ORO ? '#fff' : INK, HOR ? 'middle' : 'start', 800) + `</g>`;
        if (i < n - 1) {
          const pa = eo((L - t0 - tramo + .25) / .3); if (pa <= 0) return;
          o += HOR ? `<path d="M${x + wB + 10} ${cy} h${(50 * pa).toFixed(1)}" stroke="${INK}" stroke-width="8" stroke-linecap="round"/>` + (pa > .9 ? `<path d="M${x + wB + 52} ${cy - 14} l16 14 l-16 14" fill="none" stroke="${INK}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>` : '')
            : `<path d="M${cx} ${y + hB + 8} v${((gap - 22) * pa).toFixed(1)}" stroke="${INK}" stroke-width="7" stroke-linecap="round"/>` + (pa > .9 ? `<path d="M${cx - 13} ${y + hB + gap - 26} l13 14 l13 -14" fill="none" stroke="${INK}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>` : '');
        }
      });
      return o;
    },
    // termómetro que se llena  {"tipo":"termometro","valor":"38 °C","max":"45","texto":"…"}
    termometro(v, L, d) {
      const mx = num(v.max) || 45, mn = num(v.min) || 0, pr = cl((num(v.valor) - mn) / (mx - mn)), p = eo(cl((L - .2) / 1)), cx = HOR ? Z.x + 200 : ZC.x - 130, top = HOR ? Z.y + 20 : Z.y + 40, hT = HOR ? 280 : 380, w = 56, rb = 58, by = top + hT + rb * .6;
      const c = pr > .66 ? ROJ : pr > .33 ? ORA : AZU, yF = top + hT - (hT - 10) * pr * p, e = back(L / .4);
      let o = `<g transform="translate(${cx} ${by}) scale(${e.toFixed(3)}) translate(${-cx} ${-by})">` +
        `<rect x="${cx - w / 2 + SOM}" y="${top + SOM}" width="${w}" height="${hT}" rx="${w / 2}" fill="${INK}"/><circle cx="${cx + SOM}" cy="${by + SOM}" r="${rb}" fill="${INK}"/>` +
        `<rect x="${cx - w / 2}" y="${top}" width="${w}" height="${hT}" rx="${w / 2}" fill="${BLA}" stroke="${INK}" stroke-width="6"/>` +
        `<rect x="${cx - w / 2 + 12}" y="${yF.toFixed(1)}" width="${w - 24}" height="${(top + hT - yF + 20).toFixed(1)}" rx="${(w - 24) / 2}" fill="${c}"/>` +
        `<circle cx="${cx}" cy="${by}" r="${rb}" fill="${c}" stroke="${INK}" stroke-width="6"/><path d="M${cx - 20} ${by - 20} a28 28 0 0 1 22 -12" stroke="#fff" stroke-width="7" fill="none" stroke-linecap="round" opacity=".6"/>`;
      for (let i = 1; i < 5; i++) { const y = top + hT * i / 5; o += `<path d="M${cx + w / 2 + 4} ${y} h18" stroke="${INK}" stroke-width="4"/>`; }
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
      const w = HOR ? 620 : Z.w - 10, h = HOR ? 330 : 380, x = HOR ? Z.x + 20 : ZC.x - w / 2, y = HOR ? ZC.y - h / 2 : Z.y + 20, e = back(L / .45), lineas = 7, fila = 4;
      let o = `<g transform="translate(${x + w / 2} ${y + h / 2}) rotate(-2) scale(${e.toFixed(3)}) translate(${-(x + w / 2)} ${-(y + h / 2)})">` + caja(x, y, w, h, 10, '#fbf8f0', 4) +
        (v.titulo ? tx(x + 30, y + 54, esc(v.titulo), HOR ? 34 : 32, INK, 'start', 900) : '');
      for (let i = 0; i < lineas; i++) { const yy = y + 90 + i * ((h - 120) / lineas); o += i === fila ? `<rect x="${x + 30}" y="${yy - 6}" width="${(w - 60) * eo((L - .9) / .4)}" height="16" rx="4" fill="${ORO}"/><rect x="${x + 30}" y="${yy}" width="${w - 60}" height="5" rx="2" fill="${INK}" opacity=".5"/>` : `<rect x="${x + 30}" y="${yy}" width="${(w - 60) * (i % 3 === 2 ? .7 : 1)}" height="5" rx="2" fill="${INK}" opacity=".16"/>`; }
      o += `</g>`;
      const yF = y + 90 + fila * ((h - 120) / lineas), q = eio(cl((L - .2) / .8)), lx = x + 80 + (w * .55 - 80) * q + 20 * Math.sin(L * 2), ly = yF - 20 + 8 * Math.sin(L * 3);
      o += `<g transform="translate(${lx.toFixed(1)} ${ly.toFixed(1)}) rotate(-25) scale(${HOR ? .95 : 1})">${lupi({ x: 0, y: 0, s: 1, t: L, expr: 'curiosa', mira: [0, .6] })}</g>`;
      const size = HOR ? 44 : 36, max = HOR ? 18 : 24;
      return o + (v.texto ? cinetico(v.texto, HOR ? x + w + (Z.x + Z.w - x - w) / 2 : ZC.x, HOR ? ZC.y - altoCin(v.texto, size, max) / 2 + size * .8 : y + h + 80, size, L, { max, t0: 1 }) : '');
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
          (win ? `<circle cx="${Z.x + Z.w - 14}" cy="${y}" r="${(16 * back((L - t0 - .95) / .3)).toFixed(1)}" fill="${VER}" stroke="${INK}" stroke-width="4"/>` : '');
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
    // podio de los tres primeros  {"tipo":"podio","items":[{"etiqueta":"Madrid","valor":"1.650 €"},{"etiqueta":"Barcelona","valor":"1.480 €"},{"etiqueta":"Málaga","valor":"1.200 €"}]}
    podio(v, L, d) {
      const it = (v.items || []).slice(0, 3), orden = [1, 0, 2], alt = [HOR ? 250 : 280, HOR ? 180 : 210, HOR ? 130 : 150], med = [ORO, '#c9ccd3', '#d6894a'];
      const wB = HOR ? 220 : 172, gap = HOR ? 18 : 8, base = HOR ? Z.y + Z.h - 10 : Z.y + Z.h - 60, x0 = ZC.x - (3 * wB + 2 * gap) / 2;
      let o = `<path d="M${x0 - 20} ${base} H${x0 + 3 * wB + 2 * gap + 20}" stroke="${INK}" stroke-width="7" stroke-linecap="round"/>`;
      orden.forEach((pos, col_) => {
        const q = it[pos]; if (!q) return;
        const t0 = .2 + (2 - pos) * .35, p = back((L - t0) / .55), h = alt[pos] * cl(p, 0, 1.1), x = x0 + col_ * (wB + gap), y = base - h;
        if (L < t0) return;
        o += caja(x, y, wB, h, 12, pos === 0 ? ORA : BLA, 5) + tx(x + wB / 2, y + Math.min(h - 10, HOR ? 92 : 100), String(pos + 1), HOR ? 84 : 90, pos === 0 ? '#fff' : INK, 'middle', 900, `opacity="${cl(h / 120).toFixed(2)}"`);
        const ep = back((L - t0 - .45) / .35); if (ep <= 0) return;
        const fs = Math.min(HOR ? 32 : 26, (wB - 8) / (Math.max(5, String(q.etiqueta || '').length) * .56));
        o += `<g transform="translate(${x + wB / 2} ${y - 18}) scale(${ep.toFixed(3)})"><circle cx="0" cy="${HOR ? -96 : -104}" r="28" fill="${med[pos]}" stroke="${INK}" stroke-width="5"/>${tx(0, HOR ? -86 : -94, String(pos + 1), 28, INK)}` +
          tx(0, HOR ? -50 : -46, esc(q.etiqueta || ''), fs, INK, 'middle', 900) + peg(0, -6, String(q.valor || ''), HOR ? 26 : 22, INK, '#fff', 'middle', 1, 0) + `</g>`;
        if (pos === 0 && L > t0 + .6) for (let i = 0; i < 14; i++) { const a = i * 2.4, fr = frac((L - t0 - .6) * .7 + i / 14), cx_ = x + wB / 2 + Math.sin(a * 3.1) * 150 * fr, cy_ = y - 150 - 60 * Math.sin(a) + 260 * fr * fr; o += `<rect x="${cx_.toFixed(1)}" y="${cy_.toFixed(1)}" width="12" height="7" fill="${[ORA, AZU, VER, ORO, ROJ][i % 5]}" transform="rotate(${(a * 60 + L * 300).toFixed(0)} ${cx_.toFixed(1)} ${cy_.toFixed(1)})" opacity="${(1 - fr).toFixed(2)}"/>`; }
      });
      return o;
    },
    foto(v, L, d, k) {
      const f = fotoDe(k) || {}, txt = f.texto || v.texto || '', size = HOR ? 50 : 38, max = HOR ? 20 : 26, alto = altoCin(txt, size, max), e = back(L / .45);
      const fw = HOR ? Z.w * .6 : Z.w + 20, fh = HOR ? Z.h - 10 : Z.h - alto - 40, fx = HOR ? Z.x : ZC.x - fw / 2, fy = Z.y + (HOR ? 10 : 6), cx = fx + fw / 2, cy = fy + fh / 2, id = 'fc' + k;
      return `<g transform="translate(${cx} ${cy}) scale(${e.toFixed(3)}) rotate(-1.5) translate(${-cx} ${-cy})"><rect x="${fx + SOM + 3}" y="${fy + SOM + 3}" width="${fw}" height="${fh}" rx="24" fill="${INK}"/>` +
        `<clipPath id="${id}"><rect x="${fx}" y="${fy}" width="${fw}" height="${fh}" rx="24"/></clipPath><image href="file://${f.ruta}" x="${fx}" y="${fy}" width="${fw}" height="${fh}" preserveAspectRatio="xMidYMid slice" clip-path="url(#${id})"/>` +
        // v60: la foto queda quieta, pero alrededor hay vida: destello de flash al entrar, un brillo que la cruza y esquinas de visor que enfocan
        `<g clip-path="url(#${id})"><rect x="${fx}" y="${fy}" width="${fw}" height="${fh}" fill="#fff" opacity="${(L < .55 ? .7 * cl(1 - (L - .3) / .25) * cl((L - .25) / .05) : 0).toFixed(3)}"/>` +
        (L > .6 && L < 1.6 ? `<path d="M${(fx - 200 + (fw + 400) * eio((L - .6) / 1)).toFixed(1)} ${fy} l120 0 l-160 ${fh} l-120 0 Z" fill="#fff" opacity=".28"/>` : '') + `</g>` +
        `<rect x="${fx}" y="${fy}" width="${fw}" height="${fh}" rx="24" fill="none" stroke="${INK}" stroke-width="7"/>` +
        `<text x="${fx + fw - 16}" y="${fy + fh - 14}" font-family="Inter" font-weight="700" font-size="${HOR ? 14 : 15}" text-anchor="end" fill="#fff" stroke="${INK}" stroke-width="4" paint-order="stroke">${esc(f.credito || '')}</text></g>` +
        (() => { const q = eo((L - .2) / .5), m = 26 + 30 * (1 - q) + 4 * Math.sin(L * 3), lc = 34, c_ = GRAVE ? BLA : ORO, op = cl((L - .2) / .2) * (1 - .35 * cl((L - 1.6) / .4));   // esquinas de visor
          return [[fx + m, fy + m, 1, 1], [fx + fw - m, fy + m, -1, 1], [fx + m, fy + fh - m, 1, -1], [fx + fw - m, fy + fh - m, -1, -1]].map(([x, y, sx, sy]) =>
            `<path d="M${x} ${y + sy * lc} V${y} H${x + sx * lc}" fill="none" stroke="${c_}" stroke-width="7" stroke-linecap="round" opacity="${op.toFixed(2)}" transform="rotate(-1.5 ${cx} ${cy})"/>`).join(''); })() +
        peg(fx + 92, fy + 44, 'FOTO REAL', HOR ? 22 : 18, ROJ, '#fff', 'middle', eo((L - .3) / .2), -6, back((L - .3) / .35)) +
        (f.etiqueta ? peg(fx + fw - 86, fy + fh - 40, f.etiqueta, HOR ? 24 : 20, ORO, INK, 'middle', eo((L - .5) / .2), 5, back((L - .5) / .35)) : '') +
        cinetico(txt, HOR ? fx + fw + (Z.w - fw) / 2 + 10 : ZC.x, HOR ? ZC.y - alto / 2 + size * .8 : fy + fh + 22 + size * .7, size, L, { max: HOR ? 14 : max, t0: .35 });
    },
    mencion(v, L, d) {
      const e = back(L / .5), lx = HOR ? Z.x + 230 : ZC.x, ly = HOR ? ZC.y - 20 : Z.y + 120, tx0 = HOR ? Z.x + 470 + (Z.w - 470) / 2 : ZC.x, hm = HOR ? 0 : altoCin(v.texto || 'Los hechos, sin humo', 44, 22), by = HOR ? ZC.y + 120 : Z.y + 320 + hm + 50, pul = 1 + .05 * Math.sin(L * 5), clic = frac(L / 1.6) > .8 ? .94 : 1;
      return `<g transform="translate(${lx} ${ly}) scale(${((HOR ? 1.45 : 1.05) * e).toFixed(3)}) translate(${-lx} ${-ly})">${lupi({ x: lx, y: ly, s: 1, t: L, expr: GRAVE ? 'seria' : 'feliz', brazos: GRAVE ? '' : 'saluda', mira: [0, 0] })}</g>` +
        cinetico(v.texto || 'Los hechos, sin humo', tx0, HOR ? ZC.y - 70 : Z.y + 320, HOR ? 58 : 44, L, { max: HOR ? 20 : 22, t0: .2 }) +
        `<g transform="translate(${tx0} ${by}) scale(${(pul * clic * back((L - .6) / .4)).toFixed(3)})">${HOR ? caja(-190, -44, 380, 88, 44, ROJ, 6) : caja(-150, -36, 300, 72, 36, ROJ, 5)}<text x="0" y="${HOR ? 15 : 12}" font-family="Inter" font-weight="900" font-size="${HOR ? 40 : 32}" text-anchor="middle" fill="#fff">SUSCRÍBETE</text></g>` +
        // v61: una mano pulsa el botón y suena la campana
        (() => { if (L < .9) return ''; const ph = frac((L - .9) / 1.6), pres = ph > .45 && ph < .6, hx = tx0 + (HOR ? 140 : 116) + (1 - eo(cl((L - .9) / .4))) * 90, hy = by + 26 + (pres ? 6 : 0);
          const mano = `<g transform="translate(${hx.toFixed(1)} ${hy.toFixed(1)}) rotate(-20) scale(${HOR ? 1.1 : .95})"><path d="M0 0 v-34 a9 9 0 0 1 18 0 v26 a9 9 0 0 1 16 2 a9 9 0 0 1 16 4 a9 9 0 0 1 15 6 v22 c0 18 -12 30 -30 30 h-14 c-12 0 -20 -6 -26 -16 l-16 -26 a9 9 0 0 1 14 -10 z" fill="${BLA}" stroke="${INK}" stroke-width="5" stroke-linejoin="round"/></g>`;
          const bx = tx0 - (HOR ? 240 : 196), byy = by, sw = ph > .55 ? 18 * Math.sin((L - .9) * 28) * Math.exp(-(ph - .55) * 8) : 0, eb = back((L - 1.0) / .3);
          const campana = eb <= 0 ? '' : `<g transform="translate(${bx} ${byy}) rotate(${sw.toFixed(1)} 0 -26) scale(${(eb * (HOR ? 1.1 : .9)).toFixed(3)})"><path d="M-22 14 c4 -6 4 -14 4 -24 a18 18 0 0 1 36 0 c0 10 0 18 4 24 z" fill="${ORO}" stroke="${INK}" stroke-width="5" stroke-linejoin="round"/><circle cy="20" r="7" fill="${ORO}" stroke="${INK}" stroke-width="4"/><circle cy="-30" r="5" fill="${INK}"/></g>`;
          return campana + mano; })();
    },
    cierre(v, L, d) {
      const e = back(L / .5), lx = HOR ? Z.x + 230 : ZC.x, ly = HOR ? ZC.y - 20 : Z.y + 120, tx0 = HOR ? Z.x + 470 + (Z.w - 470) / 2 : ZC.x, gr = v.grave || GRAVE, hc = HOR ? 0 : altoCin(v.texto || '¿Tú qué opinas?', 46, 20);
      return `<g transform="translate(${lx} ${ly}) scale(${((HOR ? 1.45 : 1.05) * e).toFixed(3)}) translate(${-lx} ${-ly})">${lupi({ x: lx, y: ly, s: 1, t: L, expr: gr ? 'seria' : (L > 1.2 ? 'guino' : 'feliz'), brazos: gr ? '' : 'saluda', mira: [0, 0] })}</g>` +
        cinetico(v.texto || '¿Tú qué opinas?', tx0, HOR ? ZC.y - 50 : Z.y + 320, HOR ? 62 : 46, L, { max: HOR ? 20 : 20, t0: .2 }) +
        peg(tx0, HOR ? ZC.y + 130 : Z.y + 320 + hc + 40, 'sin humo TV', HOR ? 34 : 28, ORA, '#fff', 'middle', eo((L - .7) / .2), -3, back((L - .7) / .4)) +
        // v61: bocadillo de comentario con «escribiendo…» (invita a comentar)
        (() => { const e2 = back((L - .9) / .4); if (e2 <= 0) return ''; const bx = HOR ? lx + 120 : lx + 120, by = HOR ? ly - 130 : ly - 70, w = 120, h = 74;
          return `<g transform="translate(${bx} ${by}) rotate(${(6 + 3 * Math.sin(L * 2)).toFixed(2)}) scale(${e2.toFixed(3)})">` + caja(-w / 2, -h / 2, w, h, 26, BLA, 5) +
            `<path d="M-30 ${h / 2 - 3} l-14 22 l30 -22 Z" fill="${BLA}" stroke="${INK}" stroke-width="5" stroke-linejoin="round"/><path d="M-32 ${h / 2 - 2} h18" stroke="${BLA}" stroke-width="8"/>` +
            [-1, 0, 1].map(j => `<circle cx="${j * 28}" cy="${(-4 * Math.max(0, Math.sin(L * 7 - j * .9))).toFixed(1)}" r="9" fill="${ORA}"/>`).join('') + `</g>`; })();
    },
  };
  // pegatinas que saltan cuando la voz dice una palabra clave del subtítulo (máx. 2 por escena)
  function pegatinasVoz(k, t, tipo) {
    if (!HOR) return '';   // v45: en los cortos ensuciaban y se metían encima de textos y fotos
    if (['lista', 'linea', 'grafico', 'comparar', 'mencion', 'cierre', 'titular', 'frase', 'porcentaje', 'proporcion', 'versus', 'mapa', 'prensa', 'dialogo', 'ranking', 'fecha', 'medidor', 'evolucion', 'reparto', 'tendencia', 'dinero', 'reloj', 'checklist', 'alerta', 'escanos', 'contador', 'pasos', 'termometro', 'bateria', 'lupa', 'encuesta', 'ultimahora', 'podio'].includes(tipo)) return '';
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
    if (GRAVE || HOR || !['surprised', 'excited', 'emphatic', 'amused'].includes(EMO(k))) return '';
    const a = claves(k)[0]; if (a == null) return ''; const x = t - a; if (x < -.05 || x > 1.3) return '';
    const sal = x < .25 ? back((x + .05) / .3) : x > 1 ? 1 - eio((x - 1) / .3) : 1, lx = SX + 30 + 50 * sal, ly = 790;   // por la izquierda (a la derecha están los botones de TikTok)
    return `<g transform="translate(${lx.toFixed(1)} ${ly}) rotate(${(16 - 4 * Math.sin(t * 6)).toFixed(1)})" opacity="${cl(sal * 1.5).toFixed(2)}">${lupi({ x: 0, y: 0, s: .5, t, expr: 'sorprendida', mira: [1, -.3], brazos: 'senala' })}</g>` +
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
      `<g transform="translate(${(ZC.x + sx).toFixed(1)} ${(ZC.y + sy + (tipo === 'foto' ? 0 : 5 * Math.sin(L * 1.6 + k))).toFixed(1)}) rotate(${(tipo === 'foto' ? 0 : .5 * Math.sin(L * .9 + k * 2)).toFixed(3)}) scale(${z.toFixed(4)}) translate(${-ZC.x} ${-ZC.y})">${g}</g>` + (window.LIMPIO ? '' : pegatinasVoz(k, t, tipo)) + (window.LIMPIO ? '' : rotulo(k, L)) +
      ambiente(k, t, L) + asoma(k, t) + (k === 0 && t - S.ini > 0 && t - S.ini < .3 ? `<rect width="${W}" height="${H}" fill="#fff" opacity="${(.4 * Math.sin(Math.PI * (t - S.ini) / .3)).toFixed(3)}"/>` : '')   // destello (el fotograma 0 queda limpio para la miniatura);
  }
  // rótulo de la escena: banda negra inclinada con el título (entra con rebote en cada plano)
  function rotulo(k, L) {
    const tit = String(E[k].titulo || ''); if (!tit) return '';
    return peg(HOR ? Z.x + 6 : ZC.x, HOR ? 104 : 196, tit, HOR ? 30 : 26, INK, BLA, HOR ? 'start' : 'middle', 1, -2, back(L / .4));
  }

  // ---------- capas fijas ----------
  function cabecera(k, t, L) {
    const ci = CAPS.reduce((a, c, i) => (c.desde <= k ? i : a), -1), tp = (E[k].visual || {}).tipo;
    let o = `<g>${nube(HOR ? 96 : SX + 42, HOR ? 44 : 84, HOR ? .95 : 1.15)}<text x="${HOR ? 130 : SX + 80}" y="${HOR ? 54 : 96}" font-family="Inter" font-weight="900" font-size="${HOR ? 28 : 30}" fill="${INK}">sin humo TV</text></g>`;
    if (k === 0 && P.fecha) o += peg(HOR ? 400 : 430, HOR ? 53 : 95, P.fecha, HOR ? 20 : 22, ORO, INK, 'middle', 1, 3);
    if (HOR && ci >= 0) { const sig = CAPS.find(x => x.desde === k + 1), d = Math.max(1, T.escenas[k].fin - T.escenas[k].ini), av = sig && L > d * .4; o += peg(W - 110, 52, av ? 'A CONTINUACIÓN  ▸  ' + String(sig.titulo).toUpperCase() : `${ci + 1}/${CAPS.length} · ${String(CAPS[ci].titulo).toUpperCase()}`, 20, av ? ORO : ORA, av ? INK : '#fff', 'end', 1, 0, av ? back((L - d * .4) / .35) : 1); }
    if (tp !== 'mencion' && tp !== 'cierre') {
      const lx = HOR ? W - 62 : W - SX - 48, ly = HOR ? H - 196 : 96, s = HOR ? .5 : .46;
      const em = EMO(k), porEmo = { surprised: 'sorprendida', excited: 'sorprendida', emphatic: 'sorprendida', indignant: 'enfadada', whispers: 'curiosa', conspiratorial: 'guino', curious: 'curiosa', serious: 'seria', tense: 'seria', sad: 'seria', amused: 'guino' }[em];
      let ex = GRAVE ? (porEmo === 'curiosa' ? 'curiosa' : 'seria') : porEmo || (tp === 'cifra' ? 'sorprendida' : tp === 'pregunta' ? 'curiosa' : 'feliz');
      if ((ex === 'feliz' || ex === 'seria' && !GRAVE) && hablando(k, t)) ex = 'habla';   // v52: Lupi «habla» con la voz
      const mira = SUSURRO(k) ? [HOR ? -1 : -1, 0] : [HOR ? -1 : -.6, HOR ? -.4 : .8];
      o += lupi({ x: lx, y: ly + 3 * Math.sin(t * 2.4), s, t, expr: ex, mira, brazos: L < 1 ? 'senala' : '' });
    }
    return o;
  }
  function subtitulos(k, t) {
    const bl = bloquesKaraoke(k, HOR ? 34 : 30, HOR ? 34 : 18); if (!bl.length) return '';
    let i = bl.findIndex(b => t < b.b); if (i < 0) i = bl.length - 1;
    const B = bl[i], ent = back((t - B.a) / .16) || (i === 0 ? 1 : 0), maxc = Math.max(...B.ls.map(ln => ln.reduce((a, b) => a + b.w.length + 1, -1)));
    const su = SUSURRO(k), fs = Math.round((su ? .9 : 1) * Math.min(HOR ? 52 : 46, Math.floor((HOR ? 1000 : W - 2 * SX - 60) / (Math.max(5, maxc) * .58)))), lh = fs * 1.18, yc = HOR ? 606 : 900, y0 = yc - (B.ls.length - 1) * lh / 2 + fs * .35;
    return `<g transform="translate(${W / 2} ${yc}) scale(${(HOR ? .88 + .12 * ent : .96 + .04 * ent).toFixed(3)}) translate(${-W / 2} ${-yc})">` + B.ls.map((ln, j) => {
      const sp = ln.map(p => {
        const ahora = t >= p.a && t < p.b, dicho = t >= p.b, pp = ahora ? cl((t - p.a) / .1) : 1;
        return `<tspan fill="${ahora ? ORA : INK}"${ahora ? ` data-a="1"${HOR ? ` font-size="${(fs * (1 + .12 * (1 - pp))).toFixed(1)}"` : ''}` : ''} fill-opacity="${ahora || dicho ? 1 : (HOR ? .42 : .55)}">${esc(p.w.replace(/⁠/g, ' '))}</tspan>`;
      }).join(' ');
      return `<text x="${W / 2}" y="${(y0 + j * lh).toFixed(1)}" font-family="Inter" font-weight="900" font-size="${fs}"${su ? ' font-style="italic"' : ''} text-anchor="middle" letter-spacing="-.5" stroke="${BG2[0]}" stroke-width="${(fs * .22).toFixed(1)}" paint-order="stroke" stroke-linejoin="round" xml:space="preserve">${sp}</text>`;
    }).join('') + `</g>`;
  }
  function barra(t) {            // v47: vuelve Lupi a la barra (tumbada, con los segundos en la lente, bote y destello cada segundo)
    const y = HOR ? H - 30 : 1040, x0 = HOR ? 80 : 110, w = HOR ? W - 160 : W - 220, p = cl(t / DUR), xk = x0 + w * p;
    const seg = Math.max(0, Math.ceil(DUR - t)), ft = t % 1, flash = ft < .18 ? (1 - ft / .18) : 0, bote = Math.sin(t * Math.PI * 4) * 2;
    let o = `<rect x="${x0}" y="${y - 5}" width="${w}" height="10" rx="5" fill="${INK}" fill-opacity=".14"/><rect x="${x0}" y="${y - 5}" width="${Math.max(0, xk - x0).toFixed(1)}" height="10" rx="5" fill="${ORA}"/>`;
    if (HOR) o += CAPS.map(c => `<rect x="${(x0 + w * (T.escenas[c.desde] ? T.escenas[c.desde].ini : 0) / DUR - 2).toFixed(1)}" y="${y - 9}" width="4" height="18" rx="2" fill="${INK}"/>`).join('');
    return o + lupi({ x: xk, y: y + bote, s: 22 / 60, rot: 90, mini: true, sinCara: true, t, texto: seg, fs: 20 / (22 / 60) }) +
      (flash > 0 ? `<circle cx="${xk.toFixed(1)}" cy="${(y + bote).toFixed(1)}" r="${(24 + 10 * (1 - flash)).toFixed(1)}" fill="none" stroke="${ORA}" stroke-width="3" opacity="${flash.toFixed(2)}"/>` : '');
  }

  // v44 · pie de los cortos: cinta de titulares que corre + base oscura. Llena la zona que tapan los textos de YouTube/TikTok/Instagram
  // (antes quedaba crema vacío) y hace que el título blanco de la aplicación se lea mejor.
  function pie(t) {
    if (HOR || !window.PIE_CINTA) return '';   // v45: quitado en los cortos (más limpio); window.PIE_CINTA = true lo recupera
    const y = 1088, h = 50, fs = 26, tr = ['SIN HUMO TV', 'LOS HECHOS, SIN HUMO'].concat(P.fecha ? [String(P.fecha).toUpperCase()] : []);
    const an = tr.map(x => Math.round(x.length * fs * .8) + 70), per = an.reduce((a, b) => a + b, 0), off = (t * 70) % per;
    let o = `<rect x="0" y="${y + h}" width="${W}" height="${H - y - h}" fill="${INK}"/><rect x="0" y="${y + h}" width="${W}" height="${H - y - h}" fill="url(#pt2)"/>` +
      `<defs><pattern id="pt2" width="30" height="30" patternUnits="userSpaceOnUse"><circle cx="4" cy="4" r="1.7" fill="#fff" opacity=".08"/></pattern></defs>` +
      `<rect x="-10" y="${y}" width="${W + 20}" height="${h}" fill="${ORA}" stroke="${INK}" stroke-width="5"/>`;
    for (let x = -off; x < W; x += per) { let xx = x; tr.forEach((s_, n) => { o += `<text x="${(xx + an[n] / 2 - 18).toFixed(1)}" y="${y + h / 2 + fs * .36}" font-family="Inter" font-weight="900" font-size="${fs}" text-anchor="middle" fill="#fff" letter-spacing="1">${esc(s_)}</text><circle cx="${(xx + an[n] - 18).toFixed(1)}" cy="${y + h / 2}" r="6" fill="${INK}"/>`; xx += an[n]; }); }
    return o;
  }

  // ---------- fotograma ----------
  const TR = .3, TRC = .42;
  // v56 (11-nov-2026): 9 transiciones. Orden fijo que no repite dos seguidas (mezcla.py usa la MISMA regla para el sonido):
  // la escena de la mención del canal entra con la cortina de la marca; la sorpresa, tensión o indignación, con glitch;
  // en noticias graves solo las sobrias.
  const TR_TODAS = ['barrido', 'iris', 'zoom', 'persiana', 'empuje', 'mancha', 'giro', 'cortina', 'glitch'];
  const TR_GRAVE = ['barrido', 'zoom', 'empuje', 'iris', 'persiana'];
  const DUR_TR = { barrido: .3, zoom: .3, cortina: .42, iris: .38, persiana: .4, empuje: .34, giro: .34, glitch: .26, mancha: .46 };
  let TRS = null;
  function TIPO_TR(k) {
    if (!TRS) {
      TRS = [''];
      for (let j = 1; j < N; j++) {
        const base = i => GRAVE ? TR_GRAVE[(i * 2) % 5] : TR_TODAS[(i * 5) % 9], tipo = (E[j].visual || {}).tipo, em = String(E[j].voz || '').toLowerCase();
        let t = !GRAVE && tipo === 'mencion' ? 'cortina' : !GRAVE && ['surprised', 'tense', 'indignant'].includes(em) ? 'glitch' : base(j);
        if (t === 'glitch' && (TRS[j - 1] === 'glitch' || TRS[j - 2] === 'glitch')) t = base(j) === 'glitch' ? base(j + 1) : base(j);   // glitch, como mucho 1 de cada 3
        if (t === TRS[j - 1]) t = base(j + 1) === t ? base(j + 2) : base(j + 1);
        TRS.push(t);
      }
    }
    return TRS[k] || 'barrido';
  }
  window.render = function (t) {
    t = cl(t, 0, DUR - .001);
    let k = T.escenas.findIndex(s => t < s.fin); if (k < 0) k = N - 1;
    const S = T.escenas[k], L = t - S.ini;
    let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}"><rect width="${W}" height="${H}" fill="${BG2[0]}"/>`;
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
    } else if (tt === 'barrido' && L < TR) {                 // barrido rápido con desenfoque de movimiento (alterna de lado y de arriba abajo)
      const p = eio(L / TR), ver = k % 2 === 1, bl = 46 * Math.sin(Math.PI * p), ant = escena(k - 1, T.escenas[k - 1].fin - .001), nue = escena(k, t), dir = k % 4 < 2 ? 1 : -1;
      svg += `<defs><filter id="mb" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="${ver ? '0 ' + bl.toFixed(1) : bl.toFixed(1) + ' 0'}"/></filter></defs><g filter="url(#mb)">` +
        `<g transform="translate(${ver ? 0 : (-dir * W * p).toFixed(1)} ${ver ? (-dir * H * p).toFixed(1) : 0})">${ant}</g><g transform="translate(${ver ? 0 : (dir * W * (1 - p)).toFixed(1)} ${ver ? (dir * H * (1 - p)).toFixed(1) : 0})">${nue}</g></g>`;
    } else svg += escena(k, t);
    if (!window.LIMPIO) {
      svg += pie(t) + cabecera(k, t, L) + subtitulos(k, t) + barra(t);
      if (k === N - 1 && P.fuentes) svg += `<text x="${W / 2}" y="${HOR ? H - 8 : 1076}" font-family="Inter" font-weight="700" font-size="${HOR ? 16 : 18}" text-anchor="middle" fill="${INK}" fill-opacity=".75">Fuentes: ${esc(P.fuentes)}</text>`;
    }
    svg += encima + (window.LIMPIO ? '' : marco()) + '</svg>';
    document.getElementById('lienzo').innerHTML = svg;
    cajas();
    return true;
  };
})();
