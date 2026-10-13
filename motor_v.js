/* PLANTILLAS VERTICALES de sin humo TV (shorts 9:16) — v21
   Se carga DESPUÉS de motor.js. Para cada escena k sin función propia en escenas.js,
   si proyecto.json trae escenas[k].visual = {"tipo": "...", ...}, crea window.ESCENAS[k] con la plantilla.
   Así un short se hace SIN escribir escenas.js (ahorra mucho uso de Claude) y con estilo moderno.

   Tipos (lienzo 720x1280; dibujan en x 60-660, y 195-740):
   - titular  {"texto":"104 *partidos*. Todos en Netflix", "color":"rojo"}  palabras que entran una a una (gancho)
   - cifra    {"valor":"104", "texto":"partidos en Netflix", "icono":"globo", "color":"rojo"}  contador con golpe
   - foto     {"foto":"fotos/f0.jpg", "credito":"Autor · CC BY-SA 4.0", "texto":"(opcional) rótulo", "etiqueta":"(opcional)"}
              foto real a sangre con movimiento lento (Ken Burns), degradado y rótulo
   - comparar {"a":{"etiqueta":"2026","valor":"33"}, "b":{"etiqueta":"2030","valor":"104"}}
   - lista    {"titulo":"(opcional)", "items":["…","…","…"], "color":"verde"}   hasta 4, ≤ 22 caracteres
   - frase    {"texto":"cita literal verificada", "fuente":"BOE"}
   - linea    {"hitos":[{"fecha":"2026","texto":"…"}, …]}   hasta 4
   - icono    {"icono":"casa", "texto":"≤ 36 caracteres", "etiqueta":"(opcional)", "color":"…"}
   - grafico  {"titulo":"…", "valores":["3","5","8"], "etiquetas":["Jul","Ago","Sep"]}  hasta 5
   - pregunta {"texto":"¿…?"}
   - mencion  {"texto":"(opcional)"}  sello + Lupi con lupa (escena de "sin humo TV")
   - cierre   {"texto":"¿Pagarías? Te leo", "grave":false}  guiño de Lupi (grave: serio)
   Iconos y colores: los mismos que en los largos (motor_h.js). Palabras entre *asteriscos* = color de acento. */
(function () {
  if (!window.PROY || String(window.PROY.formato || '').toUpperCase() === 'YOUTUBE') return;
  const { A } = window.SH;
  const { INK, ORA, AZU, VER, ORO, ROJ, CRE, cl, easeOut, easeIO, esc } = A;
  const COLORES = { rojo: ROJ, azul: AZU, verde: VER, oro: ORO, naranja: ORA, crema: CRE, tinta: INK, morado: '#6b4fa3' };
  const col = c => COLORES[c] || c || ORA;

  function partir(txt, n) {
    const ls = []; let l = '';
    for (const w of String(txt).split(/\s+/).filter(Boolean)) {
      if (l && (l + ' ' + w).replace(/\*/g, '').length > n) { ls.push(l); l = w; } else l = l ? l + ' ' + w : w;
    }
    if (l) ls.push(l);
    return ls;
  }
  // texto con *acento*: los trozos entre asteriscos van en color
  function rico(s, acento) {
    let on = false;
    return String(s).split(/(\*)/).map(p => { if (p === '*') { on = !on; return ''; } return p ? `<tspan fill="${on ? acento : 'inherit'}">${esc(p)}</tspan>` : ''; }).join('');
  }
  function bloque(x, y, txt, size, n, fill = INK, anchor = 'middle', alpha = 1, acento = ORA, sw = 0) {
    const st = sw ? ` stroke="${CRE}" stroke-width="${sw}" paint-order="stroke" stroke-linejoin="round"` : '';
    return partir(txt, n).map((l, i) => `<text x="${x}" y="${y + i * size * 1.16}" font-family="Inter" font-weight="900" font-size="${size}" fill="${fill}" text-anchor="${anchor}" opacity="${alpha}"${st}>${rico(l, acento)}</text>`).join('');
  }
  let CAL = [];
  function icono(nombre, x, y, s, L, c) {
    const f = A[nombre];
    if (!f) return A.alerta(x, y, s);
    switch (nombre) {
      case 'reloj': case 'vela': return f(x, y, s, L);
      case 'calendario': return f(x, y, s, (CAL[0] || ''), (CAL[1] || ''), c || ROJ);
      case 'termometro': return f(x, y, s, .7, c || ROJ);
      case 'casa': return f(x, y, s, 0, c || ROJ);
      case 'olas': return f(y, L, c || AZU, 600);
      case 'mazo': return f(x, y, s, 1);
      case 'balanza': return f(x, y, s, Math.sin(L * 1.5) * .3);
      case 'paloma': return f(x, y, s, Math.sin(L * 6));
      case 'medalla': return f(x, y, s, '', c || ORO);
      case 'gente': return f(L, x - 110, y - 50, 7, 3, 0, c || AZU, 34, .32);
      case 'sello': return f(x, y, s, -5);
      default: return c ? f(x, y, s, c) : f(x, y, s);
    }
  }
  function numero(v) {
    const m = String(v).match(/^([^\d-]*)(-?[\d.]*\d(?:,\d+)?)(.*)$/);
    if (!m) return null;
    const dec = (m[2].split(',')[1] || '').length, num = parseFloat(m[2].replace(/\./g, '').replace(',', '.'));
    return isFinite(num) ? { pre: m[1], num, dec, suf: m[3], miles: /\d\.\d{3}/.test(m[2]) } : null;
  }
  function contador(v, L, t0, d) {
    const n = numero(v); if (!n) return String(v);
    const x = n.num * easeOut((L - t0) / d);
    let s = x.toFixed(n.dec).replace('.', ',');
    if (n.miles || Math.abs(n.num) >= 10000) { const [e, f] = s.split(','); s = e.replace(/\B(?=(\d{3})+(?!\d))/g, '.') + (f ? ',' + f : ''); }
    return n.pre + s + n.suf;
  }
  // golpe moderno: al aterrizar, la pieza crece un 18 % y vuelve con un pequeño temblor
  const golpe = (L, t) => { const p = cl((L - t) / .35); return p <= 0 || p >= 1 ? 1 : 1 + .18 * Math.sin(p * Math.PI) * (1 - p * .5); };
  const tiembla = (L, t) => { const p = cl((L - t) / .3); return p <= 0 || p >= 1 ? 0 : Math.sin(p * 40) * 5 * (1 - p); };
  const lupiBase = (L, d, expr = 'curiosa', extra = {}) => Object.assign({ x: 565, y: 610, s: .78, expr, mira: [-.8, -.3], brazos: L < d * .6 ? 'senala' : 'abajo' }, extra);
  const tam = (s, max, ancho) => Math.min(max, Math.floor(ancho / (Math.max(1, [...String(s)].length) * .62)));

  const P_ = {
    titular(L, d, v, k) {
      const c = col(v.color || 'rojo'), ls = partir(v.texto || '', 13), size = ls.length > 3 ? 68 : 80;
      const y0 = 470 - (ls.length - 1) * size * .58;
      const s = ls.map((l, j) => {
        const t0 = .12 * j, p = k === 0 ? 1 : A.pop(L, t0, .3), y = y0 + j * size * 1.12;
        return A.esc_(360, y - size * .35, p, `<text x="360" y="${y}" font-family="Inter" font-weight="900" font-size="${size}" text-anchor="middle" fill="${INK}" stroke="${CRE}" stroke-width="10" paint-order="stroke" stroke-linejoin="round">${rico(l, c)}</text>`);
      }).join('');
      const yb = y0 + (ls.length - 1) * size * 1.12 + 34;
      const sub = `<rect x="${360 - 200 * easeOut((L - .4) / .5)}" y="${yb}" width="${400 * easeOut((L - .4) / .5)}" height="14" rx="7" fill="${c}"/>`;
      return { svg: s + sub, lupi: lupiBase(L, d, 'sorprendida', { y: 650 }), evitar: [[70, y0 - size, 580, ls.length * size * 1.15 + 40]] };
    },
    cifra(L, d, v, k) {
      CAL = v.cal || [];
      const c = col(v.color || 'rojo'), t1 = .25, dur = Math.min(1.4, d * .3), val = String(v.valor);
      const size = tam(val, 150, 560);
      const ic = v.icono ? A.esc_(360, 300, A.pop(L, .05), icono(v.icono, 360, 300, 1.05, L, v.color && col(v.color))) : '';
      const ny = v.icono ? 500 : 450;
      const g = k === 0 ? 1 : golpe(L, t1 + dur), dx = k === 0 ? 0 : tiembla(L, t1 + dur);
      const num = A.esc_(360, ny - size * .35, (k === 0 ? 1 : A.pop(L, t1)) * g, `<g transform="translate(${dx} 0)">${A.txtC(360, ny, k === 0 ? val : contador(val, L, t1, dur), size, c, 'middle', 14)}</g>`);
      const tx = k === 0 || L > .8 ? bloque(360, ny + 75, v.texto || '', 42, 20, INK, 'middle', k === 0 ? 1 : easeOut((L - .8) / .4), c) : '';
      return { svg: ic + num + A.destello(360, ny - size * .35, L, t1 + dur, 150, c) + tx, lupi: lupiBase(L, d, L > t1 + dur ? 'sorprendida' : 'curiosa', L > 1.8 && L < 3.2 ? { x: 360, y: ny - size * .3, lupa: { cx: 360, cy: ny - size * .35 } } : { x: 595, y: 300, s: .6 }), evitar: [[70, ny - size, 580, size + 160]] };
    },
    foto(L, d, v) {
      const x0 = 60, y0 = 200, w = 600, h = 520, id = 'kb' + Math.round(d * 100);
      const ruta = String(v.foto || '');
      const p = cl(L / Math.max(1, d)), z = 1.04 + .12 * easeIO(p), px = (v.pan || 1) * 30 * (easeIO(p) - .5);
      const ent = A.pop(L, 0, .4);
      const img = `<clipPath id="${id}"><rect x="${x0}" y="${y0}" width="${w}" height="${h}" rx="28"/></clipPath>` +
        `<g clip-path="url(#${id})"><g transform="translate(${360 + px} ${y0 + h / 2}) scale(${z.toFixed(4)}) translate(-360 ${-(y0 + h / 2)})"><image href="${ruta.startsWith('/') ? 'file://' + ruta : ruta}" x="${x0}" y="${y0}" width="${w}" height="${h}" preserveAspectRatio="xMidYMid slice"/></g>` +
        `<rect x="${x0}" y="${y0 + h * .5}" width="${w}" height="${h * .5}" fill="url(#gr${id})"/></g>` +
        `<defs><linearGradient id="gr${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1d1828" stop-opacity="0"/><stop offset="1" stop-color="#1d1828" stop-opacity=".85"/></linearGradient></defs>` +
        `<rect x="${x0}" y="${y0}" width="${w}" height="${h}" rx="28" fill="none" stroke="${INK}" stroke-width="6"/>` +
        `<rect x="${x0 + 18}" y="${y0 + 18}" width="132" height="34" rx="17" fill="${ROJ}"/><text x="${x0 + 84}" y="${y0 + 42}" font-family="Inter" font-weight="900" font-size="18" text-anchor="middle" fill="#fff">FOTO REAL</text>` +
        (v.credito ? `<text x="${x0 + w - 16}" y="${y0 + h - 14}" font-family="Inter" font-weight="700" font-size="15" text-anchor="end" fill="#fff" fill-opacity=".85">${esc(v.credito)}</text>` : '');
      const tx = v.texto && L > .5 ? bloque(x0 + 28, y0 + h - 120 + (partir(v.texto, 22).length === 1 ? 46 : 0), v.texto, 44, 22, '#fff', 'start', easeOut((L - .5) / .4), ORO) : '';
      const et = v.etiqueta && L > d * .45 ? A.etiqueta(360, 192, v.etiqueta, .8 * A.pop(L, d * .45), col(v.color || 'oro'), -4) : '';
      return { svg: '<!--FOTO-->' + A.esc_(360, 460, ent, img + tx) + '<!--/FOTO-->' + et, evitar: [[x0, y0, w, h]] };   // sin Lupi: la foto manda
    },
    comparar(L, d, v) {
      const a = v.a || {}, b = v.b || {}, na = numero(a.valor), nb = numero(b.valor);
      const max = Math.max(Math.abs(na ? na.num : 1), Math.abs(nb ? nb.num : 1)) || 1;
      const barra = (o, n, x, t0, c) => {
        const hh = 330 * (n ? Math.max(.04, Math.abs(n.num) / max) : .5) * easeOut((L - t0) / .9);
        const sz = tam(o.valor, 62, 250);
        return `<rect x="${x - 95}" y="${680 - hh}" width="190" height="${hh}" rx="14" fill="${c}" stroke="${INK}" stroke-width="5"/>` +
          (L > t0 + .3 ? A.esc_(x, 650 - hh, golpe(L, t0 + .9), A.txtC(x, 660 - hh, contador(o.valor, L, t0, .9), sz, c, 'middle', 9)) : '') +
          bloque(x, 722, o.etiqueta || '', 30, 13, INK);
      };
      const vs = L > d * .45 ? A.esc_(360, 420, A.pop(L, d * .45), `<circle cx="360" cy="420" r="36" fill="${ORO}" stroke="${INK}" stroke-width="5"/>` + A.txt(360, 432, 'vs', 32)) : '';
      return { svg: `<path d="M110 682 H610" stroke="${INK}" stroke-width="6" stroke-linecap="round"/>` + barra(a, na, 215, .15, col(a.color || 'azul')) + barra(b, nb, 505, d * .38, col(b.color || 'rojo')) + vs, lupi: lupiBase(L, d, L > d * .5 ? 'sorprendida' : 'curiosa', { x: 600, y: 300, s: .62 }), evitar: [[100, 280, 520, 470]] };
    },
    lista(L, d, v) {
      const it = (v.items || []).slice(0, 4), n = it.length || 1, c = col(v.color || 'naranja');
      const tit = v.titulo ? bloque(360, 250, v.titulo, 44, 20, INK, 'middle', easeOut(L / .3), c) : '';
      const y0 = v.titulo ? 340 : 280, paso = Math.min(110, 400 / n);
      const filas = it.map((s, i) => {
        const t0 = .2 + i * (d * .65 / n); if (L < t0) return '';
        const y = y0 + i * paso, e = easeOut((L - t0) / .35);
        return `<g transform="translate(${(1 - e) * -60} 0)" opacity="${e}"><rect x="80" y="${y - 42}" width="560" height="78" rx="20" fill="${CRE}" stroke="${INK}" stroke-width="4"/>` +
          `<circle cx="122" cy="${y - 3}" r="24" fill="${c}" stroke="${INK}" stroke-width="4"/>` + A.txt(122, y + 8, '✓', 28, '#fff') +
          A.txt(162, y + 11, s, tam(s, 36, 460), INK, 'start', 800) + `</g>`;
      }).join('');
      return { svg: tit + filas, lupi: lupiBase(L, d, 'curiosa', { y: 690, s: .6 }), evitar: [[70, 200, 580, 480]] };
    },
    frase(L, d, v) {
      const ls = partir(v.texto || '', 20), hh = 120 + ls.length * 48 + (v.fuente ? 50 : 0), y0 = 450 - hh / 2;
      const card = `<rect x="70" y="${y0}" width="580" height="${hh}" rx="26" fill="${CRE}" stroke="${INK}" stroke-width="6"/><path d="M70 ${y0 + 40} h580" stroke="${col(v.color || 'naranja')}" stroke-width="10"/>` +
        A.txt(110, y0 + 120, '“', 120, col(v.color || 'naranja'), 'start');
      const tx = bloque(360, y0 + 105, v.texto || '', 40, 20, INK, 'middle', easeOut((L - .35) / .5));
      const fu = v.fuente && L > .9 ? `<text x="620" y="${y0 + hh - 28}" font-family="Inter" font-weight="800" font-size="26" text-anchor="end" fill="${INK}" fill-opacity=".7">— ${esc(v.fuente)}</text>` : '';
      return { svg: A.esc_(360, 450, A.pop(L, .05), card) + tx + fu, lupi: lupiBase(L, d, 'seria', { y: 690, s: .6 }), evitar: [[70, y0, 580, hh]] };
    },
    linea(L, d, v) {
      const hs = (v.hitos || []).slice(0, 4), n = hs.length || 1, y0 = 250, y1 = 690;
      const p = easeOut(L / Math.max(1, d * .6));
      let s = `<path d="M140 ${y0} V${y0 + (y1 - y0) * p}" stroke="${INK}" stroke-width="8" stroke-linecap="round"/>`;
      hs.forEach((o, i) => {
        const y = n === 1 ? (y0 + y1) / 2 : y0 + (y1 - y0) * i / (n - 1), t0 = (d * .6) * i / n + .1;
        if (L < t0) return;
        const c = i === n - 1 ? ROJ : ORA, e = easeOut((L - t0) / .3);
        s += A.esc_(140, y, A.pop(L, t0), `<circle cx="140" cy="${y}" r="22" fill="${c}" stroke="${INK}" stroke-width="5"/>`);
        s += `<g opacity="${e}" transform="translate(${(1 - e) * 40} 0)">` + A.txt(190, y - 6, o.fecha || '', 38, c, 'start') + bloque(190, y + 34, o.texto || '', 30, 22, INK, 'start') + `</g>`;
      });
      return { svg: s, lupi: lupiBase(L, d, 'curiosa', { x: 590, y: 300, s: .6 }), evitar: [[110, y0 - 40, 480, y1 - y0 + 80]] };
    },
    icono(L, d, v) {
      CAL = v.cal || [];
      const c = col(v.color || 'naranja');
      const ic = A.esc_(360, 370, A.pop(L, .05) * (1 + .03 * Math.sin(L * 2)), icono(v.icono || 'alerta', 360, 370, v.escala || 1.5, L, v.color && col(v.color)));
      const tx = L > .5 ? bloque(360, 590, v.texto || '', 46, 19, INK, 'middle', easeOut((L - .5) / .4), c, 8) : '';
      const et = v.etiqueta && L > d * .5 ? A.etiqueta(360, 712, v.etiqueta, .8 * A.pop(L, d * .5), col(v.color || 'oro'), -4) : '';
      return { svg: A.onda(360, 370, L, .1, 170, c) + ic + tx + et, lupi: lupiBase(L, d, 'curiosa', { x: 590, y: 300, s: .62 }), evitar: [[80, 540, 560, 200]] };
    },
    grafico(L, d, v) {
      const vals = (v.valores || []).slice(0, 5), et = v.etiquetas || [], n = vals.length || 1;
      const max = Math.max(...vals.map(x => Math.abs(numero(x) ? numero(x).num : 0)), 1);
      const ancho = 500 / n, an = Math.min(110, ancho * .72);
      let s = `<path d="M90 682 H630" stroke="${INK}" stroke-width="6" stroke-linecap="round"/>`;
      if (v.titulo) s += bloque(360, 245, v.titulo, 40, 22, INK);
      vals.forEach((val, i) => {
        const t0 = .2 + i * (d * .45 / n), nn = numero(val), hh = 330 * (nn ? Math.abs(nn.num) / max : 0) * easeOut((L - t0) / .7);
        const x = 110 + i * ancho + (ancho - an) / 2, c = i === n - 1 ? col(v.color || 'rojo') : AZU;
        s += `<rect x="${x}" y="${682 - hh}" width="${an}" height="${hh}" rx="10" fill="${c}" stroke="${INK}" stroke-width="5"/>`;
        if (L > t0 + .3) s += A.txt(x + an / 2, 668 - hh, contador(val, L, t0, .7), tam(val, 34, an + 20), INK);
        s += A.txt(x + an / 2, 720, et[i] || '', tam(et[i] || '', 26, ancho), INK, 'middle', 800);
      });
      return { svg: s, lupi: lupiBase(L, d, L > d * .6 ? 'sorprendida' : 'curiosa', { x: 600, y: 290, s: .58 }), evitar: [[90, 220, 540, 520]] };
    },
    pregunta(L, d, v, k) {
      const c = col(v.color || 'naranja');
      const q = A.esc_(360, 340, k === 0 ? 1 : A.pop(L, .05), A.txtC(360, 420, '?', 240, c, 'middle', 16));
      const tx = k === 0 || L > .3 ? bloque(360, 560, v.texto || '', 50, 17, INK, 'middle', k === 0 ? 1 : easeOut((L - .3) / .4), c, 8) : '';
      return { svg: A.onda(360, 340, L, .2, 150, ORO) + q + tx, lupi: lupiBase(L, d, 'curiosa', { x: 580, y: 330, s: .62, mira: [-1, .3] }), evitar: [[80, 500, 560, 220]] };
    },
    mencion(L, d, v) {
      const paso = easeIO((L - .3) / .6), sale = easeIO((L - Math.min(2.4, d * .65)) / .6);
      const lupa = L > .8 && L < Math.min(2.4, d * .65);
      return {
        svg: A.sello(360, 430, A.pop(L, 0) * 1.6, -5) + A.onda(360, 430, L, .2, 220, ROJ) + (v.texto && L > 1 ? bloque(360, 600, v.texto, 40, 22, INK, 'middle', easeOut((L - 1) / .4)) : ''),
        lupi: { x: 560 - 200 * paso + 200 * sale, y: 620 - 190 * paso + 190 * sale, s: .8, expr: 'guino', mira: [-.5, -.2], brazos: 'senala', lupa: lupa ? { cx: 360, cy: 430 } : undefined },
        evitar: [[150, 330, 420, 200]],
      };
    },
    cierre(L, d, v) {
      const grave = v.grave === true, txt = v.texto || '¿Tú qué opinas? Te leo.';
      const nl = partir(txt, 16).length;
      const tx = bloque(360, 330, txt, 56, 16, INK, 'middle', easeOut((L - .15) / .45), col(v.color || 'naranja'), 8);
      const se = L > d * .45 ? A.sello(300, 330 + nl * 66 + 60, .7 * A.pop(L, d * .45), -4) : '';
      return { svg: tx + se, lupi: { x: 560, y: 600, s: .82, expr: grave ? 'seria' : (L > d * .45 ? 'guino' : 'curiosa'), mira: [-.8, -.3], brazos: !grave && L > d * .45 ? 'saluda' : 'abajo' }, evitar: [[70, 260, 580, nl * 66 + 40]] };
    },
  };
  window.PLANTILLAS_V = P_;

  // Rellena window.ESCENAS con las plantillas (las funciones propias de escenas.js mandan)
  const P = window.PROY, T = window.TIEMPOS;
  window.ESCENAS = window.ESCENAS || [];
  (P.escenas || []).forEach((e, k) => {
    if (typeof window.ESCENAS[k] === 'function' || !e.visual) return;
    const v = e.visual;
    window.ESCENAS[k] = (L, A_, t) => {
      const S = T.escenas[k], d = Math.max(1, S.fin - S.ini);
      return (P_[v.tipo] || P_.icono)(L, d, v, k) || {};
    };
  });
})();
