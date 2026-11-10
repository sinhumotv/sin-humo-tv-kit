/* sin humo TV · MOTOR PRO (v44, 10-nov-2026) · cortos (720x1280) y largos (1280x720)
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
  const COL = { rojo: ROJ, azul: AZU, verde: VER, oro: ORO, naranja: ORA, morado: MOR, crema: BLA, tinta: INK };
  const col = c => COL[c] || (/^#/.test(c || '') ? c : ORA);
  const cl = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const eo = x => 1 - Math.pow(1 - cl(x), 3), eio = x => { x = cl(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
  const back = x => { x = cl(x); const c = 2.2; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };   // rebote al entrar
  const frac = x => x - Math.floor(x);
  const esc = s => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const E = P.escenas, N = E.length, DUR = T.duracion;
  const CAPS = (P.capitulos || []).filter(c => c && c.desde < N);
  const GRAVE = P.tono === 'grave';
  const Z = HOR ? { x: 80, y: 128, w: 1120, h: 392 } : { x: 44, y: 232, w: 632, h: 560 };   // zona del gráfico
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

  // ---------- fondo: crema liso, trama de puntos y dos manchas de color muy suaves que se mueven ----------
  function fondo(k, t) {
    const a = t * .35, c2 = [ORO, AZU, VER, ROJ][k % 4];
    return `<defs><pattern id="pt" width="30" height="30" patternUnits="userSpaceOnUse"><circle cx="4" cy="4" r="1.7" fill="${INK}" opacity=".1"/></pattern>` +
      `<radialGradient id="mA"><stop offset="0" stop-color="${ORA}" stop-opacity=".2"/><stop offset="1" stop-color="${ORA}" stop-opacity="0"/></radialGradient>` +
      `<radialGradient id="mB"><stop offset="0" stop-color="${c2}" stop-opacity=".16"/><stop offset="1" stop-color="${c2}" stop-opacity="0"/></radialGradient></defs>` +
      `<rect width="${W}" height="${H}" fill="${GRAVE ? '#efece6' : BG}"/>` +
      `<circle cx="${(W * (.1 + .25 * Math.sin(a + k))).toFixed(1)}" cy="${(H * (.92 + .06 * Math.cos(a * 1.3))).toFixed(1)}" r="${Math.max(W, H) * .42}" fill="url(#mA)"/>` +
      `<circle cx="${(W * (.92 + .2 * Math.cos(a * .8 + k))).toFixed(1)}" cy="${(H * (.06 + .1 * Math.sin(a * 1.1))).toFixed(1)}" r="${Math.max(W, H) * .36}" fill="url(#mB)"/>` +
      `<rect width="${W}" height="${H}" fill="url(#pt)"/>`;
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
  const G = {
    cifra(v, L, d) {
      const c = col(v.color), s = String(v.valor || ''), size = Math.min(HOR ? 210 : 200, Z.w * .94 / (Math.max(3, s.length) * .6)), p = cl(L / Math.min(1.3, d * .45));
      const yN = ZC.y + (HOR ? 30 : 10), ent = back(L / .4), lab = partir(v.texto || '', HOR ? 36 : 20), wS = size * Math.max(3, s.length) * .58;
      return `<rect x="${(ZC.x - wS / 2 * eo((L - .15) / .4)).toFixed(1)}" y="${(yN - size * .3).toFixed(1)}" width="${(wS * eo((L - .15) / .4)).toFixed(1)}" height="${(size * .36).toFixed(1)}" rx="${size * .06}" fill="${c === INK ? ORO : c}" opacity=".9" transform="rotate(-1.5 ${ZC.x} ${yN})"/>` +
        `<g transform="translate(${ZC.x} ${yN}) scale(${ent.toFixed(3)}) translate(${-ZC.x} ${-yN})">${tx(ZC.x, yN, esc(contar(s, p)), size, INK, 'middle', 900, 'letter-spacing="-4"')}</g>` +
        lab.map((l, i) => tx(ZC.x, yN + (HOR ? 74 : 86) + i * (HOR ? 50 : 58), esc(l), HOR ? 42 : 48, INK, 'middle', 800, `opacity="${eo((L - .45 - i * .1) / .3).toFixed(2)}"`)).join('') +
        (v.icono ? sticker(HOR ? Z.x + 100 : Z.x + 84, HOR ? Z.y + 70 : Z.y + 46, HOR ? 70 : 70, L, .25, v.icono, c) : '');
    },
    comparar(v, L, d) {
      const a = v.a || {}, b = v.b || {}, na = num(a.valor), nb = num(b.valor), mx = Math.max(Math.abs(na), Math.abs(nb), 1e-9), ah = HOR ? 78 : 96, x0 = Z.x + (HOR ? 140 : 14), wM = Z.w - (HOR ? 280 : 28);
      const fila = (o, n, y, c, t0) => {
        const p = eo((L - t0) / .9), w = Math.max(ah * 1.1, wM * (Math.abs(n) / mx) * p), op = cl((L - t0) / .15);
        return `<g opacity="${op}">` + tx(x0, y - 18, esc(o.etiqueta || ''), HOR ? 34 : 40, INK, 'start', 900) + caja(x0, y, w, ah, ah * .28, c) +
          (w > wM * .5 ? tx(x0 + w - 22, y + ah * .7, esc(contar(String(o.valor || ''), p)), ah * .58, c === ORA ? '#fff' : INK, 'end') : tx(x0 + w + 26, y + ah * .7, esc(contar(String(o.valor || ''), p)), ah * .58, INK, 'start')) + `</g>`;
      };
      return fila(a, na, ZC.y - ah - (HOR ? 34 : 70), GRI, .15) + fila(b, nb, ZC.y + (HOR ? 62 : 86), ORA, .6);
    },
    grafico(v, L, d) {
      const vs = (v.valores || []).slice(0, 7), et = v.etiquetas || [], n = vs.length || 1, mx = Math.max(...vs.map(x => Math.abs(num(x))), 1e-9), base = Z.y + Z.h - (HOR ? 50 : 66), alto = Z.h - (HOR ? 160 : 220);
      const paso = Math.min(HOR ? 190 : 150, Z.w / n), an = paso * .6, x0 = ZC.x - paso * n / 2 + (paso - an) / 2;
      let o = v.titulo ? cinetico(v.titulo, ZC.x, Z.y + (HOR ? 36 : 46), HOR ? 40 : 44, L, { max: HOR ? 46 : 24 }) : '';
      o += [1, 2, 3].map(i => `<path d="M${Z.x} ${base - alto * i / 3} H${Z.x + Z.w}" stroke="${INK}" stroke-opacity=".16" stroke-width="3" stroke-dasharray="4 12"/>`).join('');
      vs.forEach((x, i) => {
        const t0 = .25 + i * Math.min(.35, d * .5 / n), p = back((L - t0) / .7), h = Math.max(12, alto * Math.abs(num(x)) / mx * p), xx = x0 + i * paso, ult = i === n - 1, op = cl((L - t0) / .12);
        o += `<g opacity="${op}">` + caja(xx, base - h, an, h, Math.min(14, an * .16), ult ? ORA : GRI) +
          tx(xx + an / 2, base - h - 16, esc(contar(String(x), cl((L - t0) / .7))), Math.min(HOR ? 40 : 42, an * .5), INK) +
          tx(xx + an / 2, base + (HOR ? 42 : 48), esc(et[i] || ''), Math.min(HOR ? 28 : 30, paso * .3), INK, 'middle', 800) + `</g>`;
      });
      return o + `<path d="M${Z.x} ${base} H${Z.x + Z.w}" stroke="${INK}" stroke-width="6" stroke-linecap="round"/>`;
    },
    lista(v, L, d) {
      const it = (v.items || []).slice(0, 4), n = it.length || 1, c = col(v.color), hT = v.titulo ? (HOR ? 74 : 104) : 0, ah = Math.min(HOR ? 80 : 104, (Z.h - hT - 10) / n - 18), y0 = Z.y + hT + (Z.h - hT - n * (ah + 18)) / 2;
      const act = Math.min(n - 1, Math.floor(cl((L - .3) / Math.max(1, d - .8)) * n));
      let o = v.titulo ? cinetico(v.titulo, HOR ? Z.x + 20 : ZC.x, Z.y + (HOR ? 46 : 62), HOR ? 46 : 52, L, { max: HOR ? 48 : 22, anchor: HOR ? 'start' : 'middle' }) : '';
      it.forEach((s, i) => {
        const t0 = .3 + i * (Math.max(1, d - .8) / n), e = back((L - t0) / .4); if (L < t0) return;
        const y = y0 + i * (ah + 18), on = i === act, fs = Math.min(ah * .44, (Z.w - 160) / (Math.max(8, [...String(s)].length) * .56));
        o += `<g transform="translate(${((1 - e) * (i % 2 ? -1 : 1) * 300).toFixed(1)} 0) rotate(${on ? -1 : 0} ${ZC.x} ${y + ah / 2})" opacity="${cl((L - t0) / .12)}">` + caja(Z.x + 8, y, Z.w - 24, ah, ah * .26, on ? c : BLA) +
          `<circle cx="${Z.x + 8 + ah * .5}" cy="${y + ah / 2}" r="${ah * .3}" fill="${on ? '#fff' : c}" stroke="${INK}" stroke-width="4"/>` + tx(Z.x + 8 + ah * .5, y + ah / 2 + ah * .13, String(i + 1), ah * .36, on ? c : '#fff') +
          tx(Z.x + 8 + ah * 1.05, y + ah / 2 + fs * .36, esc(s), fs, on && c !== ORO ? '#fff' : INK, 'start', 800) + `</g>`;
      });
      return o;
    },
    frase(v, L, d) {
      const size = HOR ? 48 : 52, max = HOR ? 38 : 20, alto = altoCin(v.texto, size, max), hC = alto + (HOR ? 110 : 150), wC = HOR ? Z.w - 160 : Z.w - 16, x = ZC.x - wC / 2, y = ZC.y - hC / 2, e = back(L / .4);
      return `<g transform="translate(${ZC.x} ${ZC.y}) scale(${e.toFixed(3)}) rotate(-1) translate(${-ZC.x} ${-ZC.y})">` + caja(x, y, wC, hC, 26, BLA, 6, SOM + 3) +
        `<text x="${x + 22}" y="${y + (HOR ? 96 : 112)}" font-family="Georgia, serif" font-weight="900" font-size="${HOR ? 170 : 190}" fill="${ORA}">“</text></g>` +
        cinetico(v.texto, ZC.x, y + (HOR ? 76 : 104) + size * .5, size, L, { max, t0: .3, paso: Math.min(.1, d * .5 / Math.max(6, String(v.texto || '').split(' ').length)) }) +
        (v.fuente ? peg(ZC.x + (HOR ? 300 : 150), y + hC + 4, v.fuente, HOR ? 26 : 30, INK, '#fff', 'middle', eo((L - d * .45) / .3), -3, back((L - d * .45) / .35)) : '');
    },
    linea(v, L, d) {
      const hs = (v.hitos || []).slice(0, 5), n = hs.length || 1, paso = Math.min(HOR ? 92 : 122, (Z.h - 10) / n), y0 = ZC.y - paso * (n - 1) / 2, x = Z.x + (HOR ? 240 : 54);
      const tramo = Math.max(1, d - .8) / n, prog = cl((L - .2) / Math.max(1, d - .8)), yF = y0 + (n - 1) * paso * prog;
      let o = `<path d="M${x} ${y0} V${y0 + (n - 1) * paso}" stroke="${GRI}" stroke-width="10" stroke-linecap="round"/><path d="M${x} ${y0} V${yF.toFixed(1)}" stroke="${ORA}" stroke-width="10" stroke-linecap="round"/>`;
      hs.forEach((h, i) => {
        const t0 = .2 + i * tramo, on = L >= t0, e = back((L - t0) / .35), y = y0 + i * paso, ult = on && (i === n - 1 || L < t0 + tramo);
        o += `<circle cx="${x}" cy="${y}" r="${on ? 18 + (ult ? 4 * Math.sin(L * 6) : 0) : 12}" fill="${on ? ORA : BLA}" stroke="${INK}" stroke-width="5"/>`;
        if (on) o += `<g transform="translate(${((1 - e) * 140).toFixed(1)} 0)" opacity="${cl((L - t0) / .12)}">` + peg(x + 46, y + (HOR ? 10 : -6), String(h.fecha || ''), HOR ? 26 : 30, ult ? ORA : INK, '#fff', 'start', 1, -2) +
          tx(x + 46 + (HOR ? 170 : 0), y + (HOR ? 13 : 50), esc(h.texto || ''), HOR ? 38 : 40, INK, 'start', 800) + `</g>`;
      });
      return o;
    },
    icono(v, L, d) {
      const c = col(v.color), ix = HOR ? Z.x + 190 : ZC.x, iy = HOR ? ZC.y : Z.y + 165, size = HOR ? 58 : 62, max = HOR ? 19 : 17, alto = altoCin(v.texto, size, max);
      const tx0 = HOR ? Z.x + 400 + (Z.w - 400) / 2 : ZC.x, ty = HOR ? ZC.y - alto / 2 + size * .8 : Z.y + 372 + size * .5;
      return `<g transform="translate(0 ${(5 * Math.sin(L * 2.2)).toFixed(1)})">${sticker(ix, iy, 150, L, 0, v.icono, c)}</g>` +
        cinetico(v.texto, tx0, ty, size, L, { max, t0: .2 }) +
        (v.etiqueta ? peg(tx0 + (HOR ? 120 : 110), ty + alto + 6, String(v.etiqueta), HOR ? 28 : 30, c === ORA ? AZU : c, '#fff', 'middle', eo((L - .8) / .25), 4, back((L - .8) / .35)) : '');
    },
    pregunta(v, L, d) {
      const size = HOR ? 60 : 68, max = HOR ? 18 : 15, alto = altoCin(v.texto, size, max), qx = HOR ? Z.x + 190 : ZC.x, qy = HOR ? ZC.y + 120 : Z.y + 270, e = back(L / .5), fs = HOR ? 380 : 360;
      const q = (dx, dy, f, st) => `<text x="${dx}" y="${dy}" font-family="Inter" font-weight="900" font-size="${fs}" text-anchor="middle" fill="${f}"${st ? ` stroke="${INK}" stroke-width="10" stroke-linejoin="round"` : ''}>?</text>`;
      return `<g transform="translate(${qx} ${qy}) rotate(${(-9 + 7 * Math.sin(L * 1.8)).toFixed(2)}) scale(${e.toFixed(3)})">${q(SOM + 2, SOM + 2, INK, true)}${q(0, 0, ORA, true)}</g>` +
        cinetico(v.texto, HOR ? Z.x + 400 + (Z.w - 400) / 2 : ZC.x, HOR ? ZC.y - alto / 2 + size * .8 : Z.y + 380, size, L, { max, t0: .25 });
    },
    titular(v, L, d) {
      const s = String(v.texto || ''), max = HOR ? 20 : 11, size = Math.min(HOR ? 124 : 122, (Z.w * .98) / (Math.min(max, Math.max(...partir(s.replace(/\*/g, ''), max).map(l => l.length), 4)) * .6));
      const alto = altoCin(s, size, max);
      return cinetico(s, ZC.x, ZC.y - alto / 2 + size * .82, size, L, { max, paso: .11, clave: col(v.color) });
    },
    foto(v, L, d, k) {
      const f = fotoDe(k) || {}, txt = f.texto || v.texto || '', size = HOR ? 50 : 56, max = HOR ? 20 : 19, alto = altoCin(txt, size, max), e = back(L / .45);
      const fw = HOR ? Z.w * .6 : Z.w - 20, fh = HOR ? Z.h - 10 : Z.h - alto - 56, fx = HOR ? Z.x : ZC.x - fw / 2, fy = Z.y + (HOR ? 10 : 16), cx = fx + fw / 2, cy = fy + fh / 2, id = 'fc' + k;
      return `<g transform="translate(${cx} ${cy}) scale(${e.toFixed(3)}) rotate(-1.5) translate(${-cx} ${-cy})"><rect x="${fx + SOM + 3}" y="${fy + SOM + 3}" width="${fw}" height="${fh}" rx="24" fill="${INK}"/>` +
        `<clipPath id="${id}"><rect x="${fx}" y="${fy}" width="${fw}" height="${fh}" rx="24"/></clipPath><image href="file://${f.ruta}" x="${fx}" y="${fy}" width="${fw}" height="${fh}" preserveAspectRatio="xMidYMid slice" clip-path="url(#${id})"/>` +
        `<rect x="${fx}" y="${fy}" width="${fw}" height="${fh}" rx="24" fill="none" stroke="${INK}" stroke-width="7"/>` +
        `<text x="${fx + fw - 16}" y="${fy + fh - 14}" font-family="Inter" font-weight="700" font-size="${HOR ? 14 : 15}" text-anchor="end" fill="#fff" stroke="${INK}" stroke-width="4" paint-order="stroke">${esc(f.credito || '')}</text></g>` +
        peg(fx + 92, fy + 44, 'FOTO REAL', HOR ? 22 : 24, ROJ, '#fff', 'middle', eo((L - .3) / .2), -6, back((L - .3) / .35)) +
        (f.etiqueta ? peg(fx + fw - 86, fy + fh - 40, f.etiqueta, HOR ? 24 : 26, ORO, INK, 'middle', eo((L - .5) / .2), 5, back((L - .5) / .35)) : '') +
        cinetico(txt, HOR ? fx + fw + (Z.w - fw) / 2 + 10 : ZC.x, HOR ? ZC.y - alto / 2 + size * .8 : fy + fh + 30 + size * .7, size, L, { max: HOR ? 14 : max, t0: .35 });
    },
    mencion(v, L, d) {
      const e = back(L / .5), lx = HOR ? Z.x + 230 : ZC.x, ly = HOR ? ZC.y - 20 : Z.y + 150, tx0 = HOR ? Z.x + 470 + (Z.w - 470) / 2 : ZC.x, by = HOR ? ZC.y + 120 : Z.y + 520, pul = 1 + .05 * Math.sin(L * 5), clic = frac(L / 1.6) > .8 ? .94 : 1;
      return `<g transform="translate(${lx} ${ly}) scale(${(1.45 * e).toFixed(3)}) translate(${-lx} ${-ly})">${lupi({ x: lx, y: ly, s: 1, t: L, expr: GRAVE ? 'seria' : 'feliz', brazos: GRAVE ? '' : 'saluda', mira: [0, 0] })}</g>` +
        cinetico(v.texto || 'Los hechos, sin humo', tx0, HOR ? ZC.y - 70 : Z.y + 400, HOR ? 58 : 56, L, { max: HOR ? 20 : 18, t0: .2 }) +
        `<g transform="translate(${tx0} ${by}) scale(${(pul * clic * back((L - .6) / .4)).toFixed(3)})">${caja(-190, -44, 380, 88, 44, ROJ, 6)}<text x="0" y="15" font-family="Inter" font-weight="900" font-size="40" text-anchor="middle" fill="#fff">SUSCRÍBETE</text></g>`;
    },
    cierre(v, L, d) {
      const e = back(L / .5), lx = HOR ? Z.x + 230 : ZC.x, ly = HOR ? ZC.y - 20 : Z.y + 150, tx0 = HOR ? Z.x + 470 + (Z.w - 470) / 2 : ZC.x, gr = v.grave || GRAVE;
      return `<g transform="translate(${lx} ${ly}) scale(${(1.45 * e).toFixed(3)}) translate(${-lx} ${-ly})">${lupi({ x: lx, y: ly, s: 1, t: L, expr: gr ? 'seria' : (L > 1.2 ? 'guino' : 'feliz'), brazos: gr ? '' : 'saluda', mira: [0, 0] })}</g>` +
        cinetico(v.texto || '¿Tú qué opinas?', tx0, HOR ? ZC.y - 50 : Z.y + 410, HOR ? 62 : 60, L, { max: HOR ? 20 : 16, t0: .2 }) +
        peg(tx0, HOR ? ZC.y + 130 : Z.y + 545, 'sin humo TV', HOR ? 34 : 36, ORA, '#fff', 'middle', eo((L - .7) / .2), -3, back((L - .7) / .4));
    },
  };
  // pegatinas que saltan cuando la voz dice una palabra clave del subtítulo (máx. 2 por escena)
  function pegatinasVoz(k, t, tipo) {
    if (['lista', 'linea', 'grafico', 'comparar', 'mencion', 'cierre', 'titular', 'frase'].includes(tipo)) return '';
    const bl = bloquesKaraoke(k, HOR ? 34 : 17, HOR ? 34 : 13), cl_ = [];
    bl.forEach(b => b.ls.forEach(ln => ln.forEach(p => { const w = p.w.replace(/[.,;:?!…»«"]/g, ''); if ((p.clave || /\d/.test(w)) && w.length >= 3 && w.length <= 14 && !cl_.some(o => o.w === w)) cl_.push({ w, a: p.a }); })));
    const pos = HOR ? [[Z.x + Z.w - 120, Z.y + 40, 5], [Z.x + Z.w - 150, Z.y + Z.h - 20, -5]] : [[Z.x + Z.w - 130, Z.y + 60, 6], [Z.x + 120, Z.y + Z.h + 8, -5]], cs = [[ORO, INK], [AZU, '#fff']];
    return cl_.slice(0, 2).map((o, i) => t < o.a ? '' : peg(pos[i][0], pos[i][1], o.w.toUpperCase(), HOR ? 28 : 32, cs[i][0], cs[i][1], 'middle', 1, pos[i][2] + 2 * Math.sin(t * 1.7 + i), back((t - o.a) / .35))).join('');
  }

  // ---------- una escena completa ----------
  function escena(k, t) {
    const S = T.escenas[k], L = Math.max(0, t - S.ini) + (k === 0 ? 1 : 0), d = Math.max(1, S.fin - S.ini), v = E[k].visual || { tipo: 'icono', icono: 'alerta', texto: E[k].titulo };
    const f = fotoDe(k), tipo = f ? 'foto' : (G[v.tipo] ? v.tipo : 'icono');
    let g = ''; try { g = G[tipo](v, L, d, k) || ''; } catch (e) { g = G.icono({ icono: 'alerta', texto: E[k].titulo || '' }, L, d); }
    const z = (HOR ? 1 : 1.06) + .03 * cl(L / d);   // v44: en vertical el gráfico va un 6 % más grande para llenar la pantalla
    return fondo(k, t) + (k === 0 && L < 2.2 ? rayos(ZC.x, ZC.y, t, .1 * (1 - cl((L - 1.4) / .8))) : '') +
      `<g transform="translate(${ZC.x} ${ZC.y}) scale(${z.toFixed(4)}) translate(${-ZC.x} ${-ZC.y})">${g}</g>` + (window.LIMPIO ? '' : pegatinasVoz(k, t, tipo)) + (window.LIMPIO ? '' : rotulo(k, L));
  }
  // rótulo de la escena: banda negra inclinada con el título (entra con rebote en cada plano)
  function rotulo(k, L) {
    const tit = String(E[k].titulo || ''); if (!tit) return '';
    return peg(HOR ? Z.x + 6 : ZC.x, HOR ? 104 : 190, tit, HOR ? 30 : 38, INK, BLA, HOR ? 'start' : 'middle', 1, -2, back(L / .4));
  }

  // ---------- capas fijas ----------
  function cabecera(k, t, L) {
    const ci = CAPS.reduce((a, c, i) => (c.desde <= k ? i : a), -1), tp = (E[k].visual || {}).tipo;
    let o = `<g>${nube(HOR ? 96 : 78, HOR ? 44 : 84, HOR ? .95 : 1.15)}<text x="${HOR ? 130 : 118}" y="${HOR ? 54 : 96}" font-family="Inter" font-weight="900" font-size="${HOR ? 28 : 34}" fill="${INK}">sin humo TV</text></g>`;
    if (k === 0 && P.fecha) o += peg(HOR ? 400 : 430, HOR ? 53 : 95, P.fecha, HOR ? 20 : 22, ORO, INK, 'middle', 1, 3);
    if (HOR && ci >= 0) { const sig = CAPS.find(x => x.desde === k + 1), d = Math.max(1, T.escenas[k].fin - T.escenas[k].ini), av = sig && L > d * .4; o += peg(W - 110, 52, av ? 'A CONTINUACIÓN  ▸  ' + String(sig.titulo).toUpperCase() : `${ci + 1}/${CAPS.length} · ${String(CAPS[ci].titulo).toUpperCase()}`, 20, av ? ORO : ORA, av ? INK : '#fff', 'end', 1, 0, av ? back((L - d * .4) / .35) : 1); }
    if (tp !== 'mencion' && tp !== 'cierre') {
      const lx = HOR ? W - 62 : W - 82, ly = HOR ? H - 196 : 100, s = HOR ? .5 : .56;
      o += lupi({ x: lx, y: ly + 3 * Math.sin(t * 2.4), s, t, expr: GRAVE ? 'seria' : tp === 'cifra' ? 'sorprendida' : tp === 'pregunta' ? 'curiosa' : 'feliz', mira: [HOR ? -1 : -.6, HOR ? -.4 : .8], brazos: L < 1 ? 'senala' : '' });
    }
    return o;
  }
  function subtitulos(k, t) {
    const bl = bloquesKaraoke(k, HOR ? 34 : 17, HOR ? 34 : 13); if (!bl.length) return '';
    let i = bl.findIndex(b => t < b.b); if (i < 0) i = bl.length - 1;
    const B = bl[i], ent = back((t - B.a) / .16) || (i === 0 ? 1 : 0), maxc = Math.max(...B.ls.map(ln => ln.reduce((a, b) => a + b.w.length + 1, -1)));
    const fs = Math.min(HOR ? 52 : 80, Math.floor((HOR ? 1000 : 640) / (Math.max(5, maxc) * .58))), lh = fs * 1.16, yc = HOR ? 606 : 930, y0 = yc - (B.ls.length - 1) * lh / 2 + fs * .35;
    return `<g transform="translate(${W / 2} ${yc}) scale(${(.88 + .12 * ent).toFixed(3)}) translate(${-W / 2} ${-yc})">` + B.ls.map((ln, j) => {
      const sp = ln.map(p => {
        const ahora = t >= p.a && t < p.b, dicho = t >= p.b, pp = ahora ? cl((t - p.a) / .1) : 1;
        return `<tspan fill="${ahora ? ORA : INK}"${ahora ? ` data-a="1" font-size="${(fs * (1 + .12 * (1 - pp))).toFixed(1)}"` : ''} fill-opacity="${ahora || dicho ? 1 : .42}">${esc(p.w.replace(/⁠/g, ' '))}</tspan>`;
      }).join(' ');
      return `<text x="${W / 2}" y="${(y0 + j * lh).toFixed(1)}" font-family="Inter" font-weight="900" font-size="${fs}" text-anchor="middle" letter-spacing="-.5" stroke="${BG}" stroke-width="${(fs * .22).toFixed(1)}" paint-order="stroke" stroke-linejoin="round" xml:space="preserve">${sp}</text>`;
    }).join('') + `</g>`;
  }
  function barra(t) {
    const y = HOR ? H - 30 : 1040, x0 = HOR ? 80 : 150, w = HOR ? W - 160 : W - 300, p = cl(t / DUR), xk = x0 + w * p;
    let o = `<path d="M${x0} ${y} H${x0 + w}" stroke="${GRI}" stroke-width="7" stroke-linecap="round"/><path d="M${x0} ${y} H${xk.toFixed(1)}" stroke="${ORA}" stroke-width="7" stroke-linecap="round"/>`;
    if (HOR) o += CAPS.map(c => `<rect x="${(x0 + w * (T.escenas[c.desde] ? T.escenas[c.desde].ini : 0) / DUR - 2).toFixed(1)}" y="${y - 9}" width="4" height="18" rx="2" fill="${INK}"/>`).join('');
    return o + `<circle cx="${xk.toFixed(1)}" cy="${y}" r="13" fill="${BLA}" stroke="${INK}" stroke-width="4"/><text x="${xk.toFixed(1)}" y="${y + 4.5}" font-family="Inter" font-weight="900" font-size="12" text-anchor="middle" fill="${INK}">${Math.max(0, Math.ceil(DUR - t))}</text>`;
  }

  // v44 · pie de los cortos: cinta de titulares que corre + base oscura. Llena la zona que tapan los textos de YouTube/TikTok/Instagram
  // (antes quedaba crema vacío) y hace que el título blanco de la aplicación se lea mejor.
  function pie(t) {
    if (HOR) return '';
    const y = 1088, h = 50, fs = 26, tr = ['SIN HUMO TV', 'LOS HECHOS, SIN HUMO'].concat(P.fecha ? [String(P.fecha).toUpperCase()] : []);
    const an = tr.map(x => Math.round(x.length * fs * .8) + 70), per = an.reduce((a, b) => a + b, 0), off = (t * 70) % per;
    let o = `<rect x="0" y="${y + h}" width="${W}" height="${H - y - h}" fill="${INK}"/><rect x="0" y="${y + h}" width="${W}" height="${H - y - h}" fill="url(#pt2)"/>` +
      `<defs><pattern id="pt2" width="30" height="30" patternUnits="userSpaceOnUse"><circle cx="4" cy="4" r="1.7" fill="#fff" opacity=".08"/></pattern></defs>` +
      `<rect x="-10" y="${y}" width="${W + 20}" height="${h}" fill="${ORA}" stroke="${INK}" stroke-width="5"/>`;
    for (let x = -off; x < W; x += per) { let xx = x; tr.forEach((s_, n) => { o += `<text x="${(xx + an[n] / 2 - 18).toFixed(1)}" y="${y + h / 2 + fs * .36}" font-family="Inter" font-weight="900" font-size="${fs}" text-anchor="middle" fill="#fff" letter-spacing="1">${esc(s_)}</text><circle cx="${(xx + an[n] - 18).toFixed(1)}" cy="${y + h / 2}" r="6" fill="${INK}"/>`; xx += an[n]; }); }
    return o;
  }

  // ---------- fotograma ----------
  const TR = .3;
  window.render = function (t) {
    t = cl(t, 0, DUR - .001);
    let k = T.escenas.findIndex(s => t < s.fin); if (k < 0) k = N - 1;
    const S = T.escenas[k], L = t - S.ini;
    let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}"><rect width="${W}" height="${H}" fill="${BG}"/>`;
    if (k > 0 && L < TR) {                 // barrido rápido con desenfoque de movimiento (alterna de lado y de arriba abajo)
      const p = eio(L / TR), ver = k % 2 === 1, bl = 46 * Math.sin(Math.PI * p), ant = escena(k - 1, T.escenas[k - 1].fin - .001), nue = escena(k, t), dir = k % 4 < 2 ? 1 : -1;
      svg += `<defs><filter id="mb" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="${ver ? '0 ' + bl.toFixed(1) : bl.toFixed(1) + ' 0'}"/></filter></defs><g filter="url(#mb)">` +
        `<g transform="translate(${ver ? 0 : (-dir * W * p).toFixed(1)} ${ver ? (-dir * H * p).toFixed(1) : 0})">${ant}</g><g transform="translate(${ver ? 0 : (dir * W * (1 - p)).toFixed(1)} ${ver ? (dir * H * (1 - p)).toFixed(1) : 0})">${nue}</g></g>`;
    } else svg += escena(k, t);
    if (!window.LIMPIO) {
      svg += pie(t) + cabecera(k, t, L) + subtitulos(k, t) + barra(t);
      if (k === N - 1 && P.fuentes) svg += `<text x="${W / 2}" y="${HOR ? H - 8 : 1076}" font-family="Inter" font-weight="700" font-size="${HOR ? 16 : 18}" text-anchor="middle" fill="${INK}" fill-opacity=".75">Fuentes: ${esc(P.fuentes)}</text>`;
    }
    svg += '</svg>';
    document.getElementById('lienzo').innerHTML = svg;
    cajas();
    return true;
  };
})();
