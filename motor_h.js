/* Motor HORIZONTAL de sin humo TV (vídeos largos de YouTube, 16:9).
   Se carga DESPUÉS de motor.js y sustituye window.render cuando proyecto.json tiene "formato": "YOUTUBE".
   Lienzo lógico 1280x720 (se graba a 1920x1080).

   Cada escena puede ser:
   - una función propia en escenas.js (igual que en los shorts, pero con coordenadas 1280x720), o
   - una PLANTILLA declarada en proyecto.json: escenas[k].visual = {"tipo": "...", ...}  (sin escribir código)
   Si window.ESCENAS[k] existe, manda la función; si no, se usa la plantilla.

   Zona de dibujo: x 60-1040, y 120-560 (a la derecha, x 1050-1220, suele estar Lupi).
   Capítulos: proyecto.json "capitulos": [{"titulo": "...", "desde": <índice de escena>}, ...] (el primero desde 0). */
(function () {
  if (!window.PROY || String(window.PROY.formato || '').toUpperCase() !== 'YOUTUBE') return;
  const { A, lupi, nube, bloquesKaraoke } = window.SH;
  const { INK, ORA, AZU, VER, ORO, ROJ, CRE, cl, easeOut, easeIO, esc } = A;
  const W = 1280, H = 720;
  const ZONA = { x0: 60, x1: 1040, y0: 120, y1: 560 };
  const COLORES = { rojo: ROJ, azul: AZU, verde: VER, oro: ORO, naranja: ORA, crema: CRE, tinta: INK, morado: '#6b4fa3' };
  const col = c => COLORES[c] || c || ORA;

  // ---------- utilidades ----------
  // Parte un texto en líneas de como mucho n caracteres
  function partir(txt, n) {
    const ls = []; let l = '';
    for (const w of String(txt).split(/\s+/).filter(Boolean)) {
      if (l && (l + ' ' + w).length > n) { ls.push(l); l = w; } else l = l ? l + ' ' + w : w;
    }
    if (l) ls.push(l);
    return ls;
  }
  function textoMultilinea(x, y, txt, size, n, fill = INK, anchor = 'middle', alpha = 1) {
    return partir(txt, n).map((l, i) => `<text x="${x}" y="${y + i * size * 1.18}" font-family="Inter" font-weight="900" font-size="${size}" fill="${fill}" text-anchor="${anchor}" opacity="${alpha}">${esc(l)}</text>`).join('');
  }
  // Dibuja cualquier icono del kit por su nombre (calendario: textos de la hoja en visual.cal = ["NOV", "29"])
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
  // Interpreta "72.000", "2,5 %", "+58 €": devuelve {pre, num, dec, suf} para animar el contador
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

  // ---------- PLANTILLAS ----------
  // Todas reciben (L, d, v, k): L segundos desde que empieza, d duración, v = visual, k = índice.
  // Devuelven { svg, lupi?, evitar? }. Lo nuevo entra repartido a lo largo de la escena.
  const lupiDcha = (L, d, expr = 'curiosa', extra = {}) => Object.assign({ x: 1135, y: 400, s: .85, expr, mira: [-.8, -.3], brazos: L < d * .6 ? 'senala' : 'abajo' }, extra);
  const P_ = {
    // Gran cifra con contador, texto debajo e icono a la izquierda
    cifra(L, d, v, k) {
      CAL = v.cal || [];
      const c = col(v.color || 'rojo');
      const ic = v.icono ? A.esc_(260, 340, A.pop(L, .1), icono(v.icono, 260, 340, 1.5, L, v.color && col(v.color))) : '';
      const x = v.icono ? 690 : 550;
      // en la primera escena la cifra ya se ve entera en el fotograma 0 (es el gancho)
      const num = A.esc_(x, 300, k === 0 ? 1 : A.pop(L, .3), A.txtC(x, 340, k === 0 ? String(v.valor) : contador(v.valor, L, .3, Math.min(1.6, d * .3)), 140, c, 'middle', 14));
      const tx = k === 0 || L > .9 ? textoMultilinea(x, 430, v.texto || '', 46, 26, INK, 'middle', k === 0 ? 1 : easeOut((L - .9) / .4)) : '';
      return { svg: ic + num + A.destello(x, 300, L, .5 + Math.min(1.6, d * .3), 120, c) + tx, lupi: lupiDcha(L, d, 'sorprendida', L > 1.2 && L < 3 ? { x: x + 10, y: 330, lupa: { cx: x, cy: 300 } } : {}), evitar: [[x - 300, 220, 600, 260]] };
    },
    // Dos barras que crecen: a vs b
    comparar(L, d, v) {
      const a = v.a || {}, b = v.b || {}, na = numero(a.valor), nb = numero(b.valor);
      const max = Math.max(Math.abs(na ? na.num : 1), Math.abs(nb ? nb.num : 1)) || 1;
      const barra = (o, n, x, t0, c) => {
        const h = 300 * (n ? Math.abs(n.num) / max : .5) * easeOut((L - t0) / 1);
        return `<rect x="${x - 90}" y="${520 - h}" width="180" height="${h}" rx="10" fill="${c}" stroke="${INK}" stroke-width="5"/>` +
          (L > t0 + .3 ? A.txtC(x, 505 - h, contador(o.valor, L, t0, 1), 64, c, 'middle', 9) : '') +
          `<text x="${x}" y="555" font-family="Inter" font-weight="900" font-size="34" text-anchor="middle" fill="${INK}">${esc(o.etiqueta || '')}</text>`;
      };
      const vs = L > d * .45 ? A.esc_(550, 380, A.pop(L, d * .45), `<circle cx="550" cy="380" r="40" fill="${ORO}" stroke="${INK}" stroke-width="5"/>` + A.txt(550, 393, 'vs', 36)) : '';
      return { svg: `<path d="M260 522 H840" stroke="${INK}" stroke-width="6" stroke-linecap="round"/>` + barra(a, na, 380, .2, col(a.color || 'azul')) + barra(b, nb, 720, d * .4, col(b.color || 'rojo')) + vs, lupi: lupiDcha(L, d, L > d * .5 ? 'sorprendida' : 'curiosa'), evitar: [[270, 150, 580, 400]] };
    },
    // Lista de hasta 4 puntos que van apareciendo
    lista(L, d, v) {
      const it = (v.items || []).slice(0, 4), n = it.length || 1, c = col(v.color || 'naranja');
      const tit = v.titulo ? A.txt(80, 165, v.titulo, 44, INK, 'start') : '';
      const y0 = v.titulo ? 235 : 190, paso = Math.min(100, 330 / n);
      const filas = it.map((s, i) => {
        const t0 = .2 + i * (d * .7 / n); if (L < t0) return '';
        const p = A.pop(L, t0), y = y0 + i * paso;
        return A.esc_(110, y, p, `<circle cx="110" cy="${y}" r="26" fill="${c}" stroke="${INK}" stroke-width="5"/>` + A.txt(110, y + 12, String(i + 1), 32, CRE)) +
          `<g opacity="${easeOut((L - t0) / .3)}">${A.txt(160, y + 14, s, 40, INK, 'start', 800)}</g>`;
      }).join('');
      return { svg: tit + filas, lupi: lupiDcha(L, d, 'curiosa'), evitar: [[60, 140, 900, 400]] };
    },
    // Frase importante en una tarjeta (lo que dice un documento, una ley, una fuente)
    frase(L, d, v) {
      const doc = A.esc_(170, 340, A.pop(L, .05), A.documento(170, 340, 1.4));
      const tarjeta = `<rect x="290" y="175" width="700" height="${v.fuente ? 330 : 300}" rx="22" fill="${CRE}" stroke="${INK}" stroke-width="6"/>` +
        `<path d="M290 215 h700" stroke="${col(v.color || 'naranja')}" stroke-width="10"/>`;
      const tx = textoMultilinea(640, 290, v.texto || '', 44, 28, INK, 'middle', easeOut((L - .4) / .5));
      const fu = v.fuente && L > 1 ? `<text x="960" y="485" font-family="Inter" font-weight="800" font-size="28" text-anchor="end" fill="${INK}" fill-opacity=".7">— ${esc(v.fuente)}</text>` : '';
      return { svg: doc + A.esc_(640, 340, A.pop(L, .2), tarjeta) + tx + fu, lupi: lupiDcha(L, d, 'seria'), evitar: [[290, 175, 700, 330]] };
    },
    // Línea de tiempo con hasta 5 hitos
    linea(L, d, v) {
      const h = (v.hitos || []).slice(0, 5), n = h.length || 1, x0 = 130, x1 = 930;
      const p = easeOut(L / Math.max(1, d * .6));
      let s = `<path d="M${x0} 380 H${x0 + (x1 - x0) * p}" stroke="${INK}" stroke-width="8" stroke-linecap="round"/>`;
      h.forEach((o, i) => {
        const x = n === 1 ? (x0 + x1) / 2 : x0 + (x1 - x0) * i / (n - 1), t0 = (d * .6) * i / n + .1;
        if (L < t0) return;
        const arriba = i % 2 === 0, c = i === n - 1 ? ROJ : ORA;
        s += A.esc_(x, 380, A.pop(L, t0), `<circle cx="${x}" cy="380" r="20" fill="${c}" stroke="${INK}" stroke-width="5"/>`);
        s += `<g opacity="${easeOut((L - t0) / .3)}">` + A.txt(x, arriba ? 330 : 450, o.fecha || '', 36, c) + textoMultilinea(x, arriba ? 230 : 500, o.texto || '', 28, 16, INK) + `</g>`;
      });
      return { svg: s, lupi: lupiDcha(L, d, 'curiosa', { y: 420 }), evitar: [[x0 - 40, 200, x1 - x0 + 80, 340]] };
    },
    // Un icono grande y un texto (o una etiqueta)
    icono(L, d, v) {
      CAL = v.cal || [];
      const ic = A.esc_(290, 350, A.pop(L, .05) * (1 + .03 * Math.sin(L * 2)), icono(v.icono || 'alerta', 290, 350, v.escala || 1.3, L, v.color && col(v.color)));
      const ls = partir(v.texto || '', 16), y0 = 330 - (ls.length - 1) * 32;
      const tx = L > .6 ? textoMultilinea(780, y0, v.texto || '', 54, 16, INK, 'middle', easeOut((L - .6) / .4)) : '';
      const et = v.etiqueta && L > d * .5 ? A.etiqueta(780, 480, v.etiqueta, A.pop(L, d * .5), col(v.color || 'oro'), -5) : '';
      return { svg: ic + A.onda(290, 350, L, .1, 170, col(v.color || 'naranja')) + tx + et, lupi: lupiDcha(L, d, 'curiosa'), evitar: [[560, 220, 420, 300]] };
    },
    // Gráfico de barras con etiquetas
    grafico(L, d, v) {
      const vals = v.valores || [], et = v.etiquetas || [], n = vals.length || 1, max = Math.max(...vals.map(x => Math.abs(numero(x) ? numero(x).num : 0)), 1);
      const anch = Math.min(150, 780 / n), x0 = 140;
      let s = `<path d="M110 520 H980" stroke="${INK}" stroke-width="6" stroke-linecap="round"/>`;
      if (v.titulo) s += A.txt(80, 165, v.titulo, 42, INK, 'start');
      vals.forEach((val, i) => {
        const t0 = .2 + i * (d * .5 / n), nn = numero(val), h = 300 * (nn ? Math.abs(nn.num) / max : 0) * easeOut((L - t0) / .7);
        const x = x0 + i * (780 / n) + (780 / n - anch) / 2, c = i === n - 1 ? col(v.color || 'rojo') : AZU;
        s += `<rect x="${x}" y="${520 - h}" width="${anch}" height="${h}" rx="8" fill="${c}" stroke="${INK}" stroke-width="5"/>`;
        if (L > t0 + .3) s += A.txt(x + anch / 2, 505 - h, contador(val, L, t0, .7), 34, INK);
        s += A.txt(x + anch / 2, 556, et[i] || '', 28, INK, 'middle', 800);
      });
      return { svg: s, lupi: lupiDcha(L, d, L > d * .6 ? 'sorprendida' : 'curiosa'), evitar: [[110, 150, 880, 410]] };
    },
    // Pregunta grande
    pregunta(L, d, v) {
      const q = A.esc_(220, 340, A.pop(L, .05), A.txtC(220, 430, '?', 260, col(v.color || 'naranja'), 'middle', 16));
      const ls = partir(v.texto || '', 20), y0 = 345 - (ls.length - 1) * 33;
      const tx = textoMultilinea(400, y0, v.texto || '', 56, 20, INK, 'start', easeOut((L - .3) / .5));
      return { svg: q + tx + A.onda(220, 340, L, .2, 150, ORO), lupi: lupiDcha(L, d, 'curiosa', { mira: [-1, -.5] }), evitar: [[390, 220, 620, 260]] };
    },
    // Escena de mención del canal: sello grande y Lupi lo amplía
    mencion(L, d, v) {
      const paso = easeIO((L - .3) / .7), sale = easeIO((L - Math.min(2.6, d * .6)) / .7);
      return {
        svg: A.sello(560, 330, A.pop(L, 0) * 1.6, -4) + (v.texto && L > 1 ? textoMultilinea(560, 470, v.texto, 40, 34, INK, 'middle', easeOut((L - 1) / .4)) : ''),
        lupi: { x: 1130 - 450 * paso + 420 * sale, y: 420 - 80 * paso, s: .9, expr: 'curiosa', mira: [-.5, 0], brazos: 'senala', lupa: L > .9 && L < Math.min(2.6, d * .6) ? { cx: 560, cy: 330 } : undefined },
        evitar: [[290, 260, 540, 140]],
      };
    },
    // Cierre: pregunta para comentar, sello pequeño y guiño
    cierre(L, d, v) {
      const tx = textoMultilinea(560, 260, v.texto || '¿Tú qué opinas? Te leo.', 58, 19, INK, 'middle', easeOut((L - .2) / .5));
      const se = L > d * .5 ? A.sello(560, 480, .8 * A.pop(L, d * .5), -4) : '';
      const grave = v.grave === true;
      return { svg: tx + se, lupi: { x: 1120, y: 400, s: .95, expr: grave ? 'seria' : (L > d * .5 ? 'guino' : 'curiosa'), mira: [-.8, -.2], brazos: !grave && L > d * .5 ? 'saluda' : 'abajo' }, evitar: [[300, 200, 520, 200]] };
    },
  };

  function escena(k, L, t) {
    const f = window.ESCENAS && window.ESCENAS[k];
    if (typeof f === 'function') return f(L, A, t) || {};
    const v = window.PROY.escenas[k].visual || { tipo: 'pregunta', texto: window.PROY.escenas[k].titulo || '' };
    const S = window.TIEMPOS.escenas[k], d = Math.max(1, S.fin - S.ini);
    return (P_[v.tipo] || P_.icono)(L, d, v, k) || {};
  }
  window.PLANTILLAS = P_;

  // ---------- capas fijas ----------
  const FILTROS = [0, 1, 2, 3].map(i => `<filter id="w${i}" filterUnits="userSpaceOnUse" x="0" y="100" width="1280" height="480"><feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="1" seed="${i * 7 + 3}" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="4" xChannelSelector="R" yChannelSelector="G"/></filter>`).join('');
  const CAPS = () => (window.PROY.capitulos || []).slice().sort((a, b) => a.desde - b.desde);
  function capituloDe(k) { const c = CAPS(); let i = -1; c.forEach((x, j) => { if (k >= x.desde) i = j; }); return i; }

  function cabecera(k, L, alpha) {
    const tt = window.PROY.escenas[k].titulo || '', ci = capituloDe(k), cap = CAPS()[ci];
    const n = [...tt].length, size = n <= 22 ? 50 : 44, w = Math.min(760, n * size * .58);
    const p = cl((L - .05) / .6);
    let dd = `M60 101`; for (let i = 1; i <= 30; i++) dd += ` L${60 + w * i / 30} ${101 + Math.sin(i * Math.PI / 2) * 4}`;
    return `<g opacity="${alpha}">` +
      (cap ? `<text x="60" y="34" font-family="Inter" font-weight="800" font-size="22" fill="${ORA}">CAPÍTULO ${ci + 1} · ${esc(cap.titulo.toUpperCase())}</text>` : '') +
      A.txt(60, 86, tt, size, INK, 'start') +
      `<path d="${dd}" stroke="${ORA}" stroke-width="6" fill="none" stroke-linecap="round" stroke-dasharray="${w * 1.1}" stroke-dashoffset="${w * 1.1 * (1 - easeOut(p))}"/></g>`;
  }
  // Cartela de capítulo: los primeros 1,6 s de la escena con la que empieza cada capítulo (salvo el primero)
  function cartela(k, L) {
    const ci = capituloDe(k), cap = CAPS()[ci];
    if (!cap || cap.desde !== k || ci === 0 || L > 1.8) return '';
    const a = L < .25 ? easeOut(L / .25) : L > 1.45 ? 1 - easeOut((L - 1.45) / .35) : 1;
    return `<g opacity="${a}"><rect x="0" y="0" width="${W}" height="${H}" fill="${INK}" fill-opacity=".92"/>` +
      A.txtC(640, 300, String(ci + 1), 170, ORA, 'middle', 12) +
      textoMultilinea(640, 400, cap.titulo, 60, 30, CRE) + `</g>`;
  }
  function marcaFija() {
    return `<g>${nube(1048, 34, 1)}<text x="1222" y="42" font-family="Inter" font-weight="800" font-size="24" fill="${INK}" fill-opacity=".8" text-anchor="end">sin humo TV</text></g>`;
  }
  const POS = [[120, 170], [700, 190], [140, 520], [720, 520], [420, 300], [880, 350]];
  function marcaMovil(t, evitar, oculta) {
    if (oculta) return '';
    const f = t % 5, a = f < .5 ? f / .5 : f > 4.5 ? (5 - f) / .5 : 1;
    let i = Math.floor(t / 5) % POS.length;
    for (let n = 0; n < POS.length; n++) {
      const [x, y] = POS[i];
      if (!(evitar || []).some(([ex, ey, ew, eh]) => x < ex + ew && x + 220 > ex && y - 30 < ey + eh && y + 10 > ey)) break;
      i = (i + 1) % POS.length;
    }
    const [x, y] = POS[i];
    return `<text x="${x}" y="${y}" transform="rotate(-8 ${x} ${y})" font-family="Inter" font-weight="800" font-size="28" fill="${INK}" fill-opacity="${.12 * a}">sin humo TV</text>`;
  }
  const mmss = s => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
  function barra(t, D) {
    const x0 = 60, x1 = 1110, x = x0 + (x1 - x0) * cl(t / D), T = window.TIEMPOS.escenas;
    const marcas = CAPS().slice(1).map(c => { const xx = x0 + (x1 - x0) * (T[c.desde] ? T[c.desde].ini : 0) / D; return `<rect x="${xx - 2}" y="684" width="4" height="22" fill="${INK}"/>`; }).join('');
    const bote = Math.sin(t * Math.PI * 2) * 1.5;
    return `<rect x="${x0}" y="690" width="${x1 - x0}" height="10" rx="5" fill="${INK}" fill-opacity=".2" stroke="${INK}" stroke-width="2"/>` +
      `<rect x="${x0}" y="690" width="${Math.max(0, x - x0)}" height="10" rx="5" fill="${ORA}"/>` + marcas +
      lupi({ x, y: 695 + bote, s: 20 / 60, rot: 90, mini: true, sinCara: true, t }) +
      `<text x="1222" y="703" font-family="Inter" font-weight="800" font-size="22" fill="${INK}" text-anchor="end">${mmss(t)}</text>`;
  }
  function karaoke(k, t) {
    const bl = bloquesKaraoke(k, 62, 34); if (!bl.length) return '';
    let i = bl.findIndex(b => t < b.b); if (i < 0) i = bl.length - 1;
    const B = bl[i], ent = cl((t - B.a) / .12) || (i === 0 ? 1 : 0);
    const maxc = Math.max(...B.ls.map(ln => ln.reduce((a, b) => a + b.w.length + 1, -1))), fs = Math.min(42, Math.floor(1000 / (maxc * .56)));
    const y0 = B.ls.length === 1 ? 638 : 618;
    return `<rect x="110" y="580" width="1060" height="${B.ls.length === 1 ? 84 : 92}" rx="22" fill="${INK}" fill-opacity=".9"/>` + B.ls.map((ln, j) => {
      const tsp = ln.map(p => {
        const ahora = t >= p.a && t < p.b, dicho = t >= p.b;
        return `<tspan fill="${ahora ? ORA : p.clave ? '#7fd8d2' : CRE}" fill-opacity="${ahora || dicho || p.clave ? 1 : .72}">${esc(p.w.replace(/⁠/g, ' '))}</tspan>`;
      }).join(' ');
      return `<text x="640" y="${y0 + j * 46 + (1 - easeOut(ent)) * 8}" font-family="Inter" font-weight="900" font-size="${fs}" text-anchor="middle" opacity="${.35 + .65 * easeOut(ent)}">${tsp}</text>`;
    }).join('');
  }

  // ---------- encuadre automático (igual que en los shorts, en la zona horizontal) ----------
  const FIT = {};
  function encuadre(k) {
    if (FIT[k]) return FIT[k];
    const P = window.PROY, S = window.TIEMPOS.escenas[k];
    let f = { s: 1, tx: 0, ty: 0 };
    if (P.encuadre !== false) {
      try {
        const r = escena(k, (S.fin - S.ini) - .15, S.fin - .15);
        const ns = 'http://www.w3.org/2000/svg', sv = document.createElementNS(ns, 'svg');
        sv.setAttribute('width', W); sv.setAttribute('height', H); sv.style.cssText = 'position:absolute;left:-9999px;top:0';
        sv.innerHTML = `<g>${r.svg || ''}</g>`; document.body.appendChild(sv);
        const b = sv.firstChild.getBBox(); sv.remove();
        if (b.width > 40 && b.height > 40) {
          const zw = ZONA.x1 - ZONA.x0, zh = ZONA.y1 - ZONA.y0;
          let sc = Math.min(zw / b.width, zh / b.height, P.encuadre_max || 1.3);
          if (sc < 1.06 && sc > .97) sc = 1;
          sc = Math.max(.8, sc);
          const cx = b.x + b.width / 2, cy = b.y + b.height / 2;
          f = { s: sc, tx: (ZONA.x0 + zw / 2) - cx * sc, ty: (ZONA.y0 + zh / 2) - cy * sc };
        }
      } catch (e) { }
    }
    return (FIT[k] = f);
  }

  window.render = function (t) {
    const P = window.PROY, T = window.TIEMPOS, D = T.duracion;
    let e = T.escenas.findIndex(s => t < s.fin); if (e < 0) e = T.escenas.length - 1;
    const filt = `url(#w${Math.floor(t * 4) % 4})`;   // temblor de dibujo más tranquilo que en los shorts (y el vídeo pesa menos)
    const capas = [];
    const dibuja = (k, alpha, dx) => {
      const S = T.escenas[k], L = t - S.ini + (k === 0 ? (P.adelanto_inicio ?? 1) : 0);
      const r = escena(k, L, t);
      const dur = Math.max(1, S.fin - S.ini), z = P.camara === false ? 1 : 1 + .03 * easeIO(cl((t - S.ini) / dur));
      const F = encuadre(k), fx = x => F.tx + F.s * x, fy = y => F.ty + F.s * y;
      const kb = `translate(${F.tx.toFixed(2)} ${F.ty.toFixed(2)}) scale(${F.s.toFixed(4)}) translate(550 340) scale(${z.toFixed(4)}) translate(-550 -340)`;
      let lup = '';
      if (r.lupi) {
        const o = Object.assign({ t, id: 'L' + k }, r.lupi), s = o.s || 1;
        if (o.lupa === true) o.lupa = { cx: o.x, cy: o.y };
        // Lupi se mueve con el encuadre si está dentro del dibujo; si está a la derecha, se queda en su sitio
        if (o.x < ZONA.x1) { o.x = fx(o.x); o.y = fy(o.y); }
        o.x = Math.max(90, Math.min(1190, o.x)); o.y = Math.max(120 + 100 * s, Math.min(o.y, 565 - 156 * s));
        if (o.lupa) { const cx = fx(o.lupa.cx), cy = fy(o.lupa.cy); o.lente = `<g transform="rotate(${-(o.rot || 0)}) scale(${1.6 / s}) translate(${-cx} ${-cy})" filter="${filt}"><g transform="${kb}">${r.svg}</g></g>`; }
        lup = lupi(o);
      }
      if (r.evitar) r.evitar = r.evitar.map(([x, y, w, h]) => [fx(x), fy(y), w * F.s, h * F.s]);
      const kf = `translate(${F.tx.toFixed(2)} ${F.ty.toFixed(2)}) scale(${F.s.toFixed(4)})`;
      capas.push({ k, alpha, dx, r, lup, L, kb, kf });
    };
    const S = T.escenas[e], dt = t - S.ini;
    if (e > 0 && dt < .25) { const p = easeOut(dt / .25); dibuja(e - 1, 1 - p, -30 * p); dibuja(e, p, 30 * (1 - p)); }
    else dibuja(e, 1, 0);
    let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}"><defs>${FILTROS}</defs>`;
    svg += `<image href="fondo_h.jpg" x="0" y="0" width="${W}" height="${H}" preserveAspectRatio="xMidYMid slice"/>`;
    for (const c of capas) {
      const SF = A.separaFotos(c.r.svg);
      svg += `<g opacity="${c.alpha}" transform="translate(${c.dx} 0)"><g transform="${c.kf}">${SF.fotos}</g><g transform="${c.kb}"><g filter="${filt}">${SF.resto}</g></g>${c.lup}</g>`;
      if (!window.LIMPIO) svg += cabecera(c.k, c.L, c.alpha);
      if (c.k === 0 && P.fecha && !window.LIMPIO) svg += `<g opacity="${c.alpha}" transform="translate(1100 112) rotate(4)"><rect x="-80" y="-20" width="160" height="34" rx="8" fill="${ROJ}" stroke="${INK}" stroke-width="3"/><text y="5" font-family="Inter" font-weight="800" font-size="20" text-anchor="middle" fill="${CRE}">${esc(P.fecha)}</text></g>`;
      if (c.k === T.escenas.length - 1 && P.fuentes) svg += `<text x="60" y="574" font-family="Inter" font-weight="800" font-size="18" fill="${INK}" fill-opacity=".7" opacity="${c.alpha}">Fuentes: ${esc(P.fuentes)}</text>`;
    }
    const ev = capas.length ? (capas[capas.length - 1].r.evitar || []) : [];
    const ultimo = capas[capas.length - 1];
    if (!window.LIMPIO) svg += marcaMovil(t, ev, P.escenas[e].visual && P.escenas[e].visual.tipo === 'mencion' || e === P.mencion);
    svg += marcaFija();
    if (!window.LIMPIO) { svg += barra(t, D); svg += karaoke(ultimo.k, t); }
    svg += cartela(ultimo.k, ultimo.L);
    svg += `</svg>`;
    const g = P.golpe_inicial === false ? 0 : 1 - easeOut(t / .45);
    if (g > 0) svg = svg.replace('<image href="fondo_h.jpg"', `<g transform="translate(640 360) scale(${(1 + .05 * g).toFixed(4)}) translate(-640 -360)"><image href="fondo_h.jpg"`).replace(/<\/svg>$/, '</g></svg>');
    document.getElementById('lienzo').innerHTML = svg;
    return true;
  };
})();
