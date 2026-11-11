/* sin humo TV · MOTOR PRO (v52, 11-nov-2026) · cortos (720x1280) y largos (1280x720)
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
  const Z = HOR ? { x: 80, y: 128, w: 1120, h: 392 } : { x: 60, y: 262, w: 600, h: 560 };   // zona del gráfico
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
      `<g opacity="${GRAVE ? .04 : .07}" transform="translate(${mx} ${my}) rotate(${rot.toFixed(2)})">${nube(0, 0, HOR ? 7 : 8)}</g>`;
  }
  function marco() {           // marco naranja de la marca (encima de todo, fino y redondeado)
    const g = HOR ? 7 : 9, r = HOR ? 26 : 34;
    return `<rect x="${g / 2}" y="${g / 2}" width="${W - g}" height="${H - g}" rx="${r}" fill="none" stroke="${GRAVE ? '#8a8378' : ORA}" stroke-width="${g}"/>`;
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
      if (na > 0 && nb > 0 && na !== nb && !/%/.test(String(a.valor) + String(b.valor))) {
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
      return `<g transform="translate(0 ${(5 * Math.sin(L * 2.2)).toFixed(1)})">${sticker(ix, iy, HOR ? 150 : 112, L, 0, v.icono, c)}</g>` +
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
    foto(v, L, d, k) {
      const f = fotoDe(k) || {}, txt = f.texto || v.texto || '', size = HOR ? 50 : 38, max = HOR ? 20 : 26, alto = altoCin(txt, size, max), e = back(L / .45);
      const fw = HOR ? Z.w * .6 : W - 44, fh = HOR ? Z.h - 10 : Z.h - alto - 40, fx = HOR ? Z.x : ZC.x - fw / 2, fy = Z.y + (HOR ? 10 : 6), cx = fx + fw / 2, cy = fy + fh / 2, id = 'fc' + k;
      return `<g transform="translate(${cx} ${cy}) scale(${e.toFixed(3)}) rotate(-1.5) translate(${-cx} ${-cy})"><rect x="${fx + SOM + 3}" y="${fy + SOM + 3}" width="${fw}" height="${fh}" rx="24" fill="${INK}"/>` +
        `<clipPath id="${id}"><rect x="${fx}" y="${fy}" width="${fw}" height="${fh}" rx="24"/></clipPath><image href="file://${f.ruta}" x="${fx}" y="${fy}" width="${fw}" height="${fh}" preserveAspectRatio="xMidYMid slice" clip-path="url(#${id})"/>` +
        `<rect x="${fx}" y="${fy}" width="${fw}" height="${fh}" rx="24" fill="none" stroke="${INK}" stroke-width="7"/>` +
        `<text x="${fx + fw - 16}" y="${fy + fh - 14}" font-family="Inter" font-weight="700" font-size="${HOR ? 14 : 15}" text-anchor="end" fill="#fff" stroke="${INK}" stroke-width="4" paint-order="stroke">${esc(f.credito || '')}</text></g>` +
        peg(fx + 92, fy + 44, 'FOTO REAL', HOR ? 22 : 18, ROJ, '#fff', 'middle', eo((L - .3) / .2), -6, back((L - .3) / .35)) +
        (f.etiqueta ? peg(fx + fw - 86, fy + fh - 40, f.etiqueta, HOR ? 24 : 20, ORO, INK, 'middle', eo((L - .5) / .2), 5, back((L - .5) / .35)) : '') +
        cinetico(txt, HOR ? fx + fw + (Z.w - fw) / 2 + 10 : ZC.x, HOR ? ZC.y - alto / 2 + size * .8 : fy + fh + 22 + size * .7, size, L, { max: HOR ? 14 : max, t0: .35 });
    },
    mencion(v, L, d) {
      const e = back(L / .5), lx = HOR ? Z.x + 230 : ZC.x, ly = HOR ? ZC.y - 20 : Z.y + 120, tx0 = HOR ? Z.x + 470 + (Z.w - 470) / 2 : ZC.x, hm = HOR ? 0 : altoCin(v.texto || 'Los hechos, sin humo', 44, 22), by = HOR ? ZC.y + 120 : Z.y + 320 + hm + 50, pul = 1 + .05 * Math.sin(L * 5), clic = frac(L / 1.6) > .8 ? .94 : 1;
      return `<g transform="translate(${lx} ${ly}) scale(${((HOR ? 1.45 : 1.05) * e).toFixed(3)}) translate(${-lx} ${-ly})">${lupi({ x: lx, y: ly, s: 1, t: L, expr: GRAVE ? 'seria' : 'feliz', brazos: GRAVE ? '' : 'saluda', mira: [0, 0] })}</g>` +
        cinetico(v.texto || 'Los hechos, sin humo', tx0, HOR ? ZC.y - 70 : Z.y + 320, HOR ? 58 : 44, L, { max: HOR ? 20 : 22, t0: .2 }) +
        `<g transform="translate(${tx0} ${by}) scale(${(pul * clic * back((L - .6) / .4)).toFixed(3)})">${HOR ? caja(-190, -44, 380, 88, 44, ROJ, 6) : caja(-150, -36, 300, 72, 36, ROJ, 5)}<text x="0" y="${HOR ? 15 : 12}" font-family="Inter" font-weight="900" font-size="${HOR ? 40 : 32}" text-anchor="middle" fill="#fff">SUSCRÍBETE</text></g>`;
    },
    cierre(v, L, d) {
      const e = back(L / .5), lx = HOR ? Z.x + 230 : ZC.x, ly = HOR ? ZC.y - 20 : Z.y + 120, tx0 = HOR ? Z.x + 470 + (Z.w - 470) / 2 : ZC.x, gr = v.grave || GRAVE, hc = HOR ? 0 : altoCin(v.texto || '¿Tú qué opinas?', 46, 20);
      return `<g transform="translate(${lx} ${ly}) scale(${((HOR ? 1.45 : 1.05) * e).toFixed(3)}) translate(${-lx} ${-ly})">${lupi({ x: lx, y: ly, s: 1, t: L, expr: gr ? 'seria' : (L > 1.2 ? 'guino' : 'feliz'), brazos: gr ? '' : 'saluda', mira: [0, 0] })}</g>` +
        cinetico(v.texto || '¿Tú qué opinas?', tx0, HOR ? ZC.y - 50 : Z.y + 320, HOR ? 62 : 46, L, { max: HOR ? 20 : 20, t0: .2 }) +
        peg(tx0, HOR ? ZC.y + 130 : Z.y + 320 + hc + 40, 'sin humo TV', HOR ? 34 : 28, ORA, '#fff', 'middle', eo((L - .7) / .2), -3, back((L - .7) / .4));
    },
  };
  // pegatinas que saltan cuando la voz dice una palabra clave del subtítulo (máx. 2 por escena)
  function pegatinasVoz(k, t, tipo) {
    if (!HOR) return '';   // v45: en los cortos ensuciaban y se metían encima de textos y fotos
    if (['lista', 'linea', 'grafico', 'comparar', 'mencion', 'cierre', 'titular', 'frase'].includes(tipo)) return '';
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
      `<g transform="translate(${(ZC.x + sx).toFixed(1)} ${(ZC.y + sy).toFixed(1)}) scale(${z.toFixed(4)}) translate(${-ZC.x} ${-ZC.y})">${g}</g>` + (window.LIMPIO ? '' : pegatinasVoz(k, t, tipo)) + (window.LIMPIO ? '' : rotulo(k, L)) +
      ambiente(k, t, L) + (k === 0 && t - S.ini > 0 && t - S.ini < .3 ? `<rect width="${W}" height="${H}" fill="#fff" opacity="${(.4 * Math.sin(Math.PI * (t - S.ini) / .3)).toFixed(3)}"/>` : '')   // destello (el fotograma 0 queda limpio para la miniatura);
  }
  // rótulo de la escena: banda negra inclinada con el título (entra con rebote en cada plano)
  function rotulo(k, L) {
    const tit = String(E[k].titulo || ''); if (!tit) return '';
    return peg(HOR ? Z.x + 6 : ZC.x, HOR ? 104 : 196, tit, HOR ? 30 : 26, INK, BLA, HOR ? 'start' : 'middle', 1, -2, back(L / .4));
  }

  // ---------- capas fijas ----------
  function cabecera(k, t, L) {
    const ci = CAPS.reduce((a, c, i) => (c.desde <= k ? i : a), -1), tp = (E[k].visual || {}).tipo;
    let o = `<g>${nube(HOR ? 96 : 78, HOR ? 44 : 84, HOR ? .95 : 1.15)}<text x="${HOR ? 130 : 118}" y="${HOR ? 54 : 96}" font-family="Inter" font-weight="900" font-size="${HOR ? 28 : 30}" fill="${INK}">sin humo TV</text></g>`;
    if (k === 0 && P.fecha) o += peg(HOR ? 400 : 430, HOR ? 53 : 95, P.fecha, HOR ? 20 : 22, ORO, INK, 'middle', 1, 3);
    if (HOR && ci >= 0) { const sig = CAPS.find(x => x.desde === k + 1), d = Math.max(1, T.escenas[k].fin - T.escenas[k].ini), av = sig && L > d * .4; o += peg(W - 110, 52, av ? 'A CONTINUACIÓN  ▸  ' + String(sig.titulo).toUpperCase() : `${ci + 1}/${CAPS.length} · ${String(CAPS[ci].titulo).toUpperCase()}`, 20, av ? ORO : ORA, av ? INK : '#fff', 'end', 1, 0, av ? back((L - d * .4) / .35) : 1); }
    if (tp !== 'mencion' && tp !== 'cierre') {
      const lx = HOR ? W - 62 : W - 78, ly = HOR ? H - 196 : 96, s = HOR ? .5 : .46;
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
    const su = SUSURRO(k), fs = Math.round((su ? .9 : 1) * Math.min(HOR ? 52 : 46, Math.floor((HOR ? 1000 : 620) / (Math.max(5, maxc) * .58)))), lh = fs * 1.18, yc = HOR ? 606 : 900, y0 = yc - (B.ls.length - 1) * lh / 2 + fs * .35;
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
  const TR = .3, TRC = .42;   // v45: tres transiciones que se alternan: barrido con desenfoque, zoom y cortina naranja
  const TIPO_TR = k => ['barrido', 'zoom', 'barrido', 'cortina'][k % 4];
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
