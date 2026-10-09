/* Motor de sin humo TV — render(t) determinista.
   Necesita antes: window.PROY (proyecto.json), window.TIEMPOS (tiempos.json), window.ESCENAS (escenas.js).
   Cada escena: function(L, A) -> { svg, lupi?: {x,y,s,rot,expr,mira:[dx,dy], lupa?:{cx,cy}} , evitar?: [[x,y,w,h]] }
   L = segundos desde que empieza la escena. A = API de ayuda (abajo). */
(function () {
  const INK = '#2a2433', ORA = '#f07d2a', AZU = '#2f7fd0', VER = '#2aa6a0', ORO = '#f2b632',
    ROJ = '#d94a3a', CRE = '#fbf3df', GRA = '#7a1f2b', VID = '#dcecf7';
  const W = 720, H = 1280;
  const cl = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const easeOut = p => 1 - Math.pow(1 - cl(p), 3);
  const easeIO = p => { p = cl(p); return p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2; };
  const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  // ---------- API para escenas ----------
  const A = {
    INK, ORA, AZU, VER, ORO, ROJ, CRE, GRA, VID, cl, easeOut, easeIO, esc,
    prog: (L, t0, d = .4) => cl((L - t0) / d),
    // rebote de entrada (0 → 1 con sobrepaso), 0,35 s
    pop: (L, t0, d = .35) => {
      const p = cl((L - t0) / d);
      if (p <= 0) return 0;
      return 1 + Math.sin(p * Math.PI) * 0.18 * (1 - p) + (easeOut(p) - 1);
    },
    fade: (L, t0, d = .3) => easeOut((L - t0) / d),
    cuenta: (L, t0, d, de, a, dec = 0) => (de + (a - de) * easeOut((L - t0) / d)).toFixed(dec).replace('.', ','),
    respira: (L, f = 1.2, amp = 1) => Math.sin(L * Math.PI * 2 / f) * amp,
    // envolver con escala centrada
    esc_: (x, y, s, inner) => `<g transform="translate(${x} ${y}) scale(${Math.max(0.0001, s)}) translate(${-x} ${-y})">${inner}</g>`,
    txt: (x, y, s, size = 40, fill = INK, anchor = 'middle', peso = 900, extra = '') =>
      `<text x="${x}" y="${y}" font-family="Inter" font-weight="${peso}" font-size="${size}" fill="${fill}" text-anchor="${anchor}" ${extra}>${esc(s)}</text>`,
    // texto con contorno de tinta (legible sobre ilustración)
    txtC: (x, y, s, size = 40, fill = '#fff', anchor = 'middle', sw = 8) =>
      `<text x="${x}" y="${y}" font-family="Inter" font-weight="900" font-size="${size}" fill="${fill}" stroke="${INK}" stroke-width="${sw}" stroke-linejoin="round" paint-order="stroke" text-anchor="${anchor}">${esc(s)}</text>`,
    // línea discontinua que se dibuja
    linea: (pts, p, color = INK, w = 5, dash = '14 10') => {
      const d = 'M' + pts.map(q => q.join(' ')).join(' L');
      let len = 0; for (let i = 1; i < pts.length; i++) len += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
      return `<g><mask id="m${Math.round(len)}${pts[0][0]}"><path d="${d}" stroke="#fff" stroke-width="${w + 6}" fill="none" stroke-dasharray="${len}" stroke-dashoffset="${len * (1 - cl(p))}"/></mask>` +
        `<path d="${d}" stroke="${color}" stroke-width="${w}" fill="none" stroke-linecap="round" stroke-dasharray="${dash}" mask="url(#m${Math.round(len)}${pts[0][0]})"/></g>`;
    },
    flecha: (x1, y1, x2, y2, p, color = ROJ, w = 10) => {
      p = easeOut(p); if (p <= 0) return '';
      const x = x1 + (x2 - x1) * p, y = y1 + (y2 - y1) * p, a = Math.atan2(y - y1, x - x1), h = w * 2.6;
      return `<g stroke="${INK}" stroke-width="${w + 7}" stroke-linecap="round" fill="none"><path d="M${x1} ${y1}L${x} ${y}"/></g>` +
        `<path d="M${x1} ${y1}L${x} ${y}" stroke="${color}" stroke-width="${w}" stroke-linecap="round"/>` +
        `<path d="M${x} ${y} L${x - h * Math.cos(a - .5)} ${y - h * Math.sin(a - .5)} L${x - h * Math.cos(a + .5)} ${y - h * Math.sin(a + .5)}Z" fill="${color}" stroke="${INK}" stroke-width="4" stroke-linejoin="round"/>`;
    },
    destello: (x, y, L, t0, r = 40, color = ORO) => {
      const p = cl((L - t0) / .5); if (p <= 0 || p >= 1) return '';
      const rr = r * easeOut(p), o = 1 - p; let s = '';
      for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4; s += `<path d="M${x + Math.cos(a) * rr * .45} ${y + Math.sin(a) * rr * .45}L${x + Math.cos(a) * rr} ${y + Math.sin(a) * rr}"/>`; }
      return `<g stroke="${color}" stroke-width="6" stroke-linecap="round" opacity="${o}">${s}</g>`;
    },
    onda: (x, y, L, t0, r = 80, color = ORA) => {
      const p = cl((L - t0) / .7); if (p <= 0 || p >= 1) return '';
      return `<circle cx="${x}" cy="${y}" r="${r * easeOut(p)}" fill="none" stroke="${color}" stroke-width="${6 * (1 - p) + 1}" opacity="${1 - p}"/>`;
    },
    // ---- Iconos (contorno tinta, colores planos) ----
    billete: (x, y, s = 1, c = VER) => `<g transform="translate(${x} ${y}) scale(${s})"><rect x="-70" y="-38" width="140" height="76" rx="8" fill="${c}" stroke="${INK}" stroke-width="5"/><circle r="22" fill="${CRE}" stroke="${INK}" stroke-width="4"/><text y="10" font-family="Inter" font-weight="900" font-size="28" text-anchor="middle" fill="${INK}">€</text></g>`,
    moneda: (x, y, s = 1) => `<g transform="translate(${x} ${y}) scale(${s})"><circle r="30" fill="${ORO}" stroke="${INK}" stroke-width="5"/><circle r="21" fill="none" stroke="${INK}" stroke-width="3" opacity=".5"/><text y="11" font-family="Inter" font-weight="900" font-size="30" text-anchor="middle" fill="${INK}">€</text></g>`,
    carrito: (x, y, s = 1, c = AZU) => `<g transform="translate(${x} ${y}) scale(${s})" stroke="${INK}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"><path d="M-110 -70 L-80 -70 L-55 40 L80 40" fill="none"/><path d="M-72 -40 L100 -40 L85 20 L-60 20 Z" fill="${c}"/><circle cx="-40" cy="65" r="16" fill="${CRE}"/><circle cx="65" cy="65" r="16" fill="${CRE}"/></g>`,
    banco: (x, y, s = 1, c = CRE) => `<g transform="translate(${x} ${y}) scale(${s})" stroke="${INK}" stroke-width="6" stroke-linejoin="round"><path d="M-130 -60 L0 -130 L130 -60 Z" fill="${ORO}"/><rect x="-130" y="-60" width="260" height="20" fill="${c}"/>${[-95, -32, 32, 95].map(px => `<rect x="${px - 14}" y="-40" width="28" height="120" fill="${c}"/>`).join('')}<rect x="-145" y="80" width="290" height="24" fill="${c}"/></g>`,
    termometro: (x, y, s = 1, nivel = .5, c = ROJ) => `<g transform="translate(${x} ${y}) scale(${s})" stroke="${INK}" stroke-width="6"><rect x="-26" y="-170" width="52" height="200" rx="26" fill="${CRE}"/><rect x="-12" y="${20 - 175 * cl(nivel)}" width="24" height="${175 * cl(nivel) + 10}" fill="${c}" stroke="none"/><circle cy="55" r="45" fill="${c}"/>${[0, 1, 2, 3].map(i => `<path d="M26 ${-130 + i * 40} h18" stroke-width="5"/>`).join('')}</g>`,
    etiqueta: (x, y, txt, s = 1, c = ORO, rot = -8) => { const w = Math.max(150, [...String(txt)].length * 25 + 40), a = -w / 2 - 20, b = w / 2 - 20; return `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${Math.max(0.0001, s)})"><path d="M${a} -42 L${b} -42 L${b + 40} 0 L${b} 42 L${a} 42 Z" fill="${c}" stroke="${INK}" stroke-width="6" stroke-linejoin="round"/><circle cx="${b + 4}" cy="0" r="9" fill="${CRE}" stroke="${INK}" stroke-width="4"/><text x="${(a + b) / 2}" y="13" font-family="Inter" font-weight="900" font-size="38" text-anchor="middle" fill="${INK}">${esc(txt)}</text></g>`; },
    barril: (x, y, s = 1, c = INK) => `<g transform="translate(${x} ${y}) scale(${s})" stroke="${INK}" stroke-width="6"><path d="M-55 -75 Q-70 0 -55 75 L55 75 Q70 0 55 -75 Z" fill="#4a4458"/><path d="M-62 -30 H62 M-62 30 H62" stroke="${ORO}" stroke-width="8"/><path d="M-55 -75 Q-70 0 -55 75 L55 75 Q70 0 55 -75 Z" fill="none"/><path d="M0 -40 q-18 25 0 38 q18 -13 0 -38z" fill="${CRE}" stroke-width="4"/></g>`,
    rayo: (x, y, s = 1, c = ORO) => `<g transform="translate(${x} ${y}) scale(${s})"><path d="M10 -90 L-45 10 L-5 10 L-20 90 L45 -15 L5 -15 Z" fill="${c}" stroke="${INK}" stroke-width="6" stroke-linejoin="round"/></g>`,
    globo: (x, y, s = 1, c = AZU) => `<g transform="translate(${x} ${y}) scale(${s})" stroke="${INK}" stroke-width="6"><circle r="80" fill="${c}"/><path d="M-40 -55 q30 10 20 35 q-25 15 -10 45 q20 10 5 30 M30 -60 q25 30 5 55 q30 15 20 50" fill="none" stroke="${VER}" stroke-width="16" stroke-linecap="round"/><circle r="80" fill="none"/></g>`,
    persona: (x, y, s = 1, c = AZU) => `<g transform="translate(${x} ${y}) scale(${s})" stroke="${INK}" stroke-width="6"><circle cy="-70" r="30" fill="${CRE}"/><path d="M-50 40 Q-50 -30 0 -30 Q50 -30 50 40 Z" fill="${c}"/></g>`,
    cartera: (x, y, s = 1, c = ORA) => `<g transform="translate(${x} ${y}) scale(${s})" stroke="${INK}" stroke-width="6" stroke-linejoin="round"><rect x="-90" y="-60" width="180" height="120" rx="18" fill="${c}"/><rect x="30" y="-25" width="70" height="50" rx="12" fill="${ORO}"/><circle cx="55" r="8" fill="${CRE}"/></g>`,
    grafico: (x, y, valores, p, s = 1, c = VER) => {
      const n = valores.length, bw = 50, gap = 22, max = Math.max(...valores);
      let g = `<path d="M${-20} 0 H${n * (bw + gap)}" stroke="${INK}" stroke-width="6"/>`;
      valores.forEach((v, i) => { const h = 220 * v / max * easeOut(p * n - i); if (h > 0) g += `<rect x="${i * (bw + gap)}" y="${-h}" width="${bw}" height="${h}" fill="${c}" stroke="${INK}" stroke-width="5"/>`; });
      return `<g transform="translate(${x} ${y}) scale(${s})">${g}</g>`;
    },
    alerta: (x, y, s = 1, c = ROJ) => `<g transform="translate(${x} ${y}) scale(${s})"><path d="M0 -70 L70 55 L-70 55 Z" fill="${c}" stroke="${INK}" stroke-width="6" stroke-linejoin="round"/><rect x="-7" y="-25" width="14" height="45" rx="5" fill="${CRE}"/><circle cy="38" r="8" fill="${CRE}"/></g>`,
    nubeHumo: (x, y, s = 1) => nube(x, y, s),
    // ---- Números con puntos de miles ----
    miles: n => String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, '.'),
    cuentaM: (L, t0, d, a, de = 0) => A.miles(de + (a - de) * easeOut((L - t0) / d)),
    // ---- Más iconos (v2) ----
    reloj: (x, y, s, L) => { const a = L * 2.4; return `<g transform="translate(${x} ${y}) scale(${s})" stroke="${INK}" stroke-width="6" stroke-linecap="round"><circle r="70" fill="${CRE}"/><path d="M0 0 L${Math.sin(a) * 50} ${-Math.cos(a) * 50}"/><path d="M0 0 L${Math.sin(a / 12) * 32} ${-Math.cos(a / 12) * 32}" stroke-width="8"/><circle r="6" fill="${INK}"/></g>`; },
    calendario: (x, y, s, arriba, abajo, c = ROJ) => `<g transform="translate(${x} ${y}) scale(${Math.max(0.0001, s)})"><rect x="-75" y="-70" width="150" height="140" rx="14" fill="${CRE}" stroke="${INK}" stroke-width="6"/><rect x="-75" y="-70" width="150" height="42" rx="14" fill="${c}" stroke="${INK}" stroke-width="6"/><text y="-40" font-family="Inter" font-weight="900" font-size="26" text-anchor="middle" fill="${CRE}">${esc(arriba)}</text><text y="40" font-family="Inter" font-weight="900" font-size="${String(abajo).length > 4 ? 40 : 54}" text-anchor="middle" fill="${INK}">${esc(abajo)}</text></g>`,
    vela: (x, y, s, L) => `<g transform="translate(${x} ${y}) scale(${s})" stroke="${INK}" stroke-width="5" stroke-linejoin="round"><rect x="-22" y="-20" width="44" height="90" rx="6" fill="${CRE}"/><path d="M0 -20 v-10" stroke-width="4"/><path d="M0 ${-62 + Math.sin(L * 9) * 2} Q14 -42 0 -32 Q-14 -42 0 ${-62 + Math.sin(L * 9) * 2}Z" fill="${ORO}"/></g>`,
    escudo: (x, y, s, c = VER) => `<g transform="translate(${x} ${y}) scale(${Math.max(0.0001, s)})"><path d="M0 -90 L80 -60 L70 30 Q50 75 0 95 Q-50 75 -70 30 L-80 -60 Z" fill="${c}" stroke="${INK}" stroke-width="7" stroke-linejoin="round"/><path d="M-30 0 L-8 25 L35 -25" stroke="${CRE}" stroke-width="14" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>`,
    casa: (x, y, s, interrogante = 0, c = ROJ) => `<g transform="translate(${x} ${y}) scale(${Math.max(0.0001, s)})" stroke="${INK}" stroke-width="6" stroke-linejoin="round"><path d="M-60 0 L0 -55 L60 0 Z" fill="${c}"/><rect x="-50" y="0" width="100" height="80" fill="${CRE}"/><rect x="-18" y="25" width="36" height="55" fill="#4a4458"/>${interrogante > 0 ? `<text y="-5" font-family="Inter" font-weight="900" font-size="${50 * interrogante}" text-anchor="middle" fill="${ORO}" stroke="${INK}" stroke-width="5" paint-order="stroke">?</text>` : ''}</g>`,
    corona: (x, y, s) => `<g transform="translate(${x} ${y}) scale(${Math.max(0.0001, s)})"><path d="M-80 40 L-90 -40 L-45 0 L0 -60 L45 0 L90 -40 L80 40 Z" fill="${ORO}" stroke="${INK}" stroke-width="7" stroke-linejoin="round"/><circle cx="0" cy="-60" r="10" fill="${ROJ}" stroke="${INK}" stroke-width="4"/><rect x="-80" y="40" width="160" height="22" fill="${ORO}" stroke="${INK}" stroke-width="6"/></g>`,
    olas: (y, L, c = AZU, w = 640) => { let d = `M0 ${y}`; for (let x = 0; x <= w; x += 20) d += ` L${x} ${y + Math.sin(x / 40 + L * 2) * 6}`; return `<path d="${d} L${w} 740 L0 740 Z" fill="${c}" opacity=".35"/><path d="${d}" stroke="${c}" stroke-width="5" fill="none"/>`; },
    // multitud de siluetas genéricas que van apareciendo (sin rasgos: nunca personas reales)
    gente: (L, x0, y0, cols, filas, t0, c = AZU, paso = 34, s = .32) => { let g = ''; for (let f = 0; f < filas; f++) for (let k = 0; k < cols; k++) { const tt = t0 + (f * cols + k) * .03; if (L < tt) continue; const x = x0 + k * paso, y = y0 + f * paso * 1.25; g += A.esc_(x, y, A.pop(L, tt, .25), A.persona(x, y, s, c)); } return g; },
    // cuadrícula de 100 puntos con 'n' destacados ("n de cada 100")
    cien: (L, x0, y0, n, t0, tMarca, c = ORA, paso = 30) => { let g = ''; for (let i = 0; i < 100; i++) { const tt = t0 + i * .012; if (L < tt) continue; const m = i < n && L > tMarca; g += `<circle cx="${x0 + (i % 10) * paso}" cy="${y0 + Math.floor(i / 10) * paso}" r="${m ? 12 : 10}" fill="${m ? c : CRE}" stroke="${INK}" stroke-width="3"/>`; } return g; },
    tachado: (x, y, s = 1) => `<g transform="translate(${x} ${y}) scale(${Math.max(0.0001, s)})"><rect x="-30" y="-40" width="60" height="80" rx="6" fill="${CRE}" stroke="${INK}" stroke-width="5"/><path d="M-18 -18 L18 18 M18 -18 L-18 18" stroke="${ROJ}" stroke-width="8" stroke-linecap="round"/></g>`,
    documento: (x, y, s = 1, c = CRE) => `<g transform="translate(${x} ${y}) scale(${Math.max(0.0001, s)})" stroke="${INK}" stroke-width="6" stroke-linejoin="round"><path d="M-60 -80 L35 -80 L60 -55 L60 80 L-60 80 Z" fill="${c}"/><path d="M35 -80 L35 -55 L60 -55" fill="none"/><path d="M-38 -35 H38 M-38 -5 H38 M-38 25 H20" stroke-width="7" stroke-linecap="round"/></g>`,
    edificio: (x, y, s = 1, c = AZU) => `<g transform="translate(${x} ${y}) scale(${Math.max(0.0001, s)})" stroke="${INK}" stroke-width="6"><rect x="-60" y="-140" width="120" height="220" fill="${c}"/>${[0, 1, 2, 3].map(f => [0, 1].map(k => `<rect x="${-40 + k * 50}" y="${-120 + f * 48}" width="30" height="30" fill="${CRE}" stroke-width="4"/>`).join('')).join('')}</g>`,
    coche: (x, y, s = 1, c = ROJ) => `<g transform="translate(${x} ${y}) scale(${Math.max(0.0001, s)})" stroke="${INK}" stroke-width="6" stroke-linejoin="round"><path d="M-100 20 L-100 -10 L-60 -15 L-35 -50 L40 -50 L70 -15 L100 -10 L100 20 Z" fill="${c}"/><path d="M-25 -42 L-45 -15 L5 -15 L5 -42 Z M15 -42 L15 -15 L55 -15 L35 -42 Z" fill="${CRE}" stroke-width="4"/><circle cx="-55" cy="22" r="20" fill="#4a4458"/><circle cx="55" cy="22" r="20" fill="#4a4458"/></g>`,
    pin: (x, y, s = 1, c = ROJ) => `<g transform="translate(${x} ${y}) scale(${Math.max(0.0001, s)})"><path d="M0 0 C-30 -40 -40 -55 -40 -75 A40 40 0 0 1 40 -75 C40 -55 30 -40 0 0 Z" fill="${c}" stroke="${INK}" stroke-width="6"/><circle cy="-75" r="14" fill="${CRE}" stroke="${INK}" stroke-width="5"/></g>`,
    sello: (x, y, s = 1, rot = -6) => `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})"><rect x="-170" y="-48" width="340" height="96" rx="18" fill="${CRE}" stroke="${INK}" stroke-width="6"/><rect x="-160" y="-38" width="320" height="76" rx="12" fill="none" stroke="${INK}" stroke-width="2" stroke-dasharray="8 6"/>${nube(-118, 0, 1.25)}<text x="22" y="14" font-family="Inter" font-weight="900" font-size="40" text-anchor="middle" fill="${INK}">sin humo TV</text></g>`,
  };

  function nube(x, y, s) { // nube de humo tachada (icono original)
    return `<g transform="translate(${x} ${y}) scale(${s})"><path d="M-12 6 a7 7 0 0 1 2-13 a9 9 0 0 1 17-2 a7 7 0 0 1 5 13 Z" fill="${ORO}" stroke="${INK}" stroke-width="2.2" stroke-linejoin="round"/><path d="M-13 -11 L14 11" stroke="${INK}" stroke-width="4.5" stroke-linecap="round"/><path d="M-13 -11 L14 11" stroke="${ORO}" stroke-width="2" stroke-linecap="round"/></g>`;
  }

  // ---------- Lupi ----------
  function parpadeo(t) { const c = (t + 0.7) % 3.3; return c < 0.12 ? 0.1 : 1; }
  function cara(expr, t, mira = [0, 0], escala = 1, dy = 0) {
    const [mx, my] = mira, b = parpadeo(t);
    const ojo = (ex, guinyo) => guinyo
      ? `<path d="M${ex - 13} ${dy + 2} q13 -12 26 0" stroke="${INK}" stroke-width="5" fill="none" stroke-linecap="round"/>`
      : `<ellipse cx="${ex}" cy="${dy}" rx="13" ry="${17 * b}" fill="#fff" stroke="${INK}" stroke-width="4"/>` +
      (b > .5 ? `<circle cx="${ex + mx * 5}" cy="${dy + 2 + my * 5}" r="6.5" fill="${INK}"/><circle cx="${ex + mx * 5 + 2}" cy="${dy - 1 + my * 5}" r="2" fill="#fff"/>` : '');
    const cej = { curiosa: [-8, 4], sorprendida: [-16, 0], seria: [-6, -8], guino: [-9, 4] }[expr] || [-8, 4];
    const ceja = (ex, s) => `<path d="M${ex - 14} ${dy + cej[0] - 10 + s * cej[1] * .5} L${ex + 14} ${dy + cej[0] - 10 - s * cej[1] * .5}" stroke="${INK}" stroke-width="7" stroke-linecap="round"/>`;
    const boca = {
      curiosa: `<path d="M-8 ${dy + 30} q8 6 16 0" stroke="${INK}" stroke-width="5" fill="none" stroke-linecap="round"/>`,
      sorprendida: `<ellipse cx="0" cy="${dy + 32}" rx="7" ry="9" fill="${INK}"/>`,
      seria: `<path d="M-9 ${dy + 31} h18" stroke="${INK}" stroke-width="5" stroke-linecap="round"/>`,
      guino: `<path d="M-12 ${dy + 27} q12 12 24 0" stroke="${INK}" stroke-width="5" fill="${CRE}" stroke-linecap="round"/>`,
    }[expr] || '';
    return `<g transform="scale(${escala})">${ceja(-20, 1)}${ceja(20, -1)}${ojo(-20, false)}${ojo(20, expr === 'guino')}${boca}</g>`;
  }
  // Lupi completa. o = {x,y,s,rot,expr,mira,t,brazos:'saluda'|'senala'|'abajo', sinCara, texto, lente:svg (contenido ampliado)}
  function lupi(o) {
    const R = 60, s = o.s || 1, t = o.t || 0, rot = o.rot || 0, curva = Math.sin(t * 3) * 6;
    const mango = `<g transform="rotate(${curva * .3} 0 ${R})"><rect x="-13" y="${R + 4}" width="26" height="92" rx="12" fill="${ORA}" stroke="${INK}" stroke-width="5"/>` +
      [0, 1, 2, 3].map(i => `<path d="M-11 ${R + 26 + i * 16} h22" stroke="${CRE}" stroke-width="5"/>`).join('') + `</g>`;
    let brazos = '';
    if (!o.mini) {
      // ángulos en grados (0 = horizontal hacia fuera, negativo = hacia arriba)
      const angD = o.brazos === 'senala' ? -35 : o.brazos === 'saluda' ? -65 + Math.sin(t * 8) * 15 : 35;
      const angI = o.brazos === 'saluda' || o.brazos === 'senala' ? 40 : 35;
      const br = (lado, ang) => {
        const a = ang * Math.PI / 180, x0 = lado * (R + 4), y0 = 16;
        const x1 = x0 + lado * Math.cos(a) * 70, y1 = y0 + Math.sin(a) * 70;
        return `<path d="M${x0} ${y0} Q${(x0 + x1) / 2} ${(y0 + y1) / 2 + 14} ${x1} ${y1}" stroke="${INK}" stroke-width="6" fill="none" stroke-linecap="round"/><circle cx="${x1}" cy="${y1}" r="13" fill="#fff" stroke="${INK}" stroke-width="5"/>`;
      };
      brazos = br(1, angD) + br(-1, angI);
    }
    const lente = o.lente
      ? `<clipPath id="cl${o.id || 'L'}"><circle r="${R}"/></clipPath><g clip-path="url(#cl${o.id || 'L'})"><rect x="-${R}" y="-${R}" width="${2 * R}" height="${2 * R}" fill="#f6ebd0"/>${o.lente}<circle r="${R}" fill="${VID}" opacity=".25"/></g>`
      : `<circle r="${R}" fill="${VID}"/>`;
    const brillo = `<path d="M${-R * .55} ${-R * .2} Q${-R * .5} ${-R * .55} ${-R * .15} ${-R * .62}" stroke="#fff" stroke-width="9" fill="none" stroke-linecap="round" opacity=".85"/>`;
    const caraSvg = o.sinCara ? '' : (o.lente ? cara(o.expr, t, o.mira, .55, -R * .95) : cara(o.expr || 'curiosa', t, o.mira));
    const texto = o.texto !== undefined
      ? `<g transform="rotate(${-rot})"><text y="8" font-family="Inter" font-weight="900" font-size="${o.fs || 20}" text-anchor="middle" fill="${INK}">${o.texto}</text></g>` : '';
    const aro = `<circle r="${R}" fill="none" stroke="${INK}" stroke-width="17"/><circle r="${R}" fill="none" stroke="${ORO}" stroke-width="10"/>`;
    const gorra = o.mini ? '' : `<g transform="translate(0 ${-R - 4}) rotate(-8)"><path d="M-34 4 Q-32 -30 0 -32 Q32 -30 34 4 Z" fill="${GRA}" stroke="${INK}" stroke-width="5"/><path d="M14 2 Q48 -2 60 8 Q40 12 14 8 Z" fill="${GRA}" stroke="${INK}" stroke-width="5" stroke-linejoin="round"/><circle cy="-31" r="5" fill="${INK}"/></g>`;
    return `<g transform="translate(${o.x} ${o.y}) rotate(${rot}) scale(${s})">${mango}${brazos}${lente}${brillo}${caraSvg}${texto}${aro}${gorra}</g>`;
  }
  A.lupi = lupi;

  // ---------- Capas fijas ----------
  const FILTROS = [0, 1, 2, 3].map(i => `<filter id="w${i}" filterUnits="userSpaceOnUse" x="0" y="170" width="720" height="600"><feTurbulence type="fractalNoise" baseFrequency="0.022" numOctaves="1" seed="${i * 7 + 3}" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="4" xChannelSelector="R" yChannelSelector="G"/></filter>`).join('');

  function titulo(txt, L, alpha) {
    const n = [...txt].length, size = n <= 13 ? 62 : n <= 16 ? 56 : 52, w = Math.min(600, n * size * .6);
    const p = cl((L - .05) / .6), x0 = 360 - w / 2;
    let d = `M${x0} 178`; for (let i = 1; i <= 24; i++) d += ` L${x0 + w * i / 24} ${178 + Math.sin(i * Math.PI / 2) * 5}`;
    return `<g opacity="${alpha}">${A.txt(360, 158, txt, size)}<path d="${d}" stroke="${ORA}" stroke-width="7" fill="none" stroke-linecap="round" stroke-dasharray="${w * 1.1}" stroke-dashoffset="${w * 1.1 * (1 - easeOut(p))}"/></g>`;
  }
  function lineaPanel(l, y, a, dy) {
    const partes = l.split('*');
    const ts = partes.map((s, i) => `<tspan fill="${i % 2 ? ORA : CRE}">${esc(s)}</tspan>`).join('');
    return `<text x="56" y="${y + dy}" font-family="Inter" font-weight="800" font-size="42" opacity="${a}">${ts}</text>`;
  }
  function panel(e, t, alpha, dy) {
    const T = window.TIEMPOS.escenas[e], ls = window.PROY.escenas[e].panel || [];
    return ls.map((l, i) => {
      const a = e === 0 && i === 0 ? 1 : easeOut((t - T.lineas[i]) / .25);
      return a > 0 ? lineaPanel(l, 862 + i * 50, a * alpha, dy + (1 - a) * 14) : '';
    }).join('');
  }
  function marcaFija() {
    return `<g>${nube(470, 724, 1)}<text x="630" y="732" font-family="Inter" font-weight="800" font-size="22" fill="${CRE}" fill-opacity=".75" stroke="${INK}" stroke-width="2" paint-order="stroke" text-anchor="end">sin humo TV</text></g>`;
  }
  const POS = [[90, 250], [400, 280], [80, 480], [410, 520], [110, 690], [380, 700]];
  function marcaMovil(t, evitar, oculta) {
    if (oculta) return '';
    let k = Math.floor(t / 4), f = (t % 4);
    const a = f < .5 ? f / .5 : f > 3.5 ? (4 - f) / .5 : 1;
    let i = k % 6;
    for (let n = 0; n < 6; n++) {
      const [x, y] = POS[i];
      const choca = (evitar || []).some(([ex, ey, ew, eh]) => x < ex + ew && x + 210 > ex && y - 30 < ey + eh && y + 10 > ey);
      if (!choca) break; i = (i + 1) % 6;
    }
    const [x, y] = POS[i];
    return `<text x="${x}" y="${y}" transform="rotate(-8 ${x} ${y})" font-family="Inter" font-weight="800" font-size="26" fill="${INK}" fill-opacity="${.14 * a}">sin humo TV</text>`;
  }
  function barra(t, D) {
    const x = 60 + 570 * cl(t / D), seg = Math.min(Math.floor(t) + 1, Math.ceil(D - 1e-6));
    const ft = t % 1, flash = ft < .18 ? (1 - ft / .18) : 0, bote = Math.sin(t * Math.PI * 4) * 2;
    return `<rect x="60" y="767" width="570" height="10" rx="5" fill="${INK}" fill-opacity=".2" stroke="${INK}" stroke-width="2"/>` +
      `<rect x="60" y="767" width="${Math.max(0, x - 60)}" height="10" rx="5" fill="${ORA}"/>` +
      lupi({ x, y: 772 + bote, s: 22 / 60, rot: 90, mini: true, sinCara: true, t, texto: seg, fs: 20 / (22 / 60) * 1 }) +
      (flash > 0 ? `<circle cx="${x}" cy="${772 + bote}" r="${24 + 10 * (1 - flash)}" fill="none" stroke="#fff" stroke-width="3" opacity="${flash}"/>` : '');
  }

  // ---------- render ----------
  let ultimo = '';
  window.render = function (t) {
    const P = window.PROY, T = window.TIEMPOS, E = window.ESCENAS, D = T.duracion;
    let e = T.escenas.findIndex(s => t < s.fin); if (e < 0) e = T.escenas.length - 1;
    const filt = `url(#w${Math.floor(t * 8) % 4})`;
    const capas = [];
    const dibuja = (k, alpha, dy) => {
      const S = T.escenas[k], L = t - S.ini + (k === 0 ? (P.adelanto_inicio ?? 1.5) : 0); // la escena 1 ya empieza avanzada: todo lo que entre antes de L=1,5 se ve en el fotograma 0
      const r = E[k](L, A, t) || {};
      let lup = '';
      if (r.lupi) {
        const o = Object.assign({ t, id: 'L' + k }, r.lupi);
        if (o.lupa === true) o.lupa = { cx: o.x, cy: o.y };
        if (o.lupa) o.lente = `<g transform="rotate(${-(o.rot || 0)}) scale(${1.6 / (o.s || 1)}) translate(${-o.lupa.cx} ${-o.lupa.cy})" filter="${filt}">${r.svg}</g>`;
        lup = lupi(o);
      }
      capas.push({ k, alpha, dy, r, lup, L });
    };
    const S = T.escenas[e], dt = t - S.ini;
    if (e > 0 && dt < .25) { const p = easeOut(dt / .25); dibuja(e - 1, 1 - p, -20 * p); dibuja(e, p, 20 * (1 - p)); }
    else dibuja(e, 1, 0);
    let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}"><defs>${FILTROS}</defs>`;
    svg += `<image href="fondo.jpg" x="0" y="0" width="${W}" height="${H}"/>`;
    for (const c of capas) {
      const tt = P.escenas[c.k].titulo;
      svg += `<g opacity="${c.alpha}" transform="translate(0 ${c.dy})"><g filter="${filt}">${c.r.svg || ''}</g>${c.lup}</g>`;
      svg += `<g transform="translate(0 ${c.dy})">${titulo(tt, c.L, c.alpha)}</g>`;
      if (c.k === 0 && P.fecha) svg += `<g opacity="${c.alpha}" transform="translate(565 214) rotate(5)"><rect x="-74" y="-20" width="148" height="34" rx="8" fill="${ROJ}" stroke="${INK}" stroke-width="3"/><text y="5" font-family="Inter" font-weight="800" font-size="20" text-anchor="middle" fill="${CRE}">${esc(P.fecha)}</text></g>`;
      if (c.k === T.escenas.length - 1 && P.fuentes) svg += `<text x="60" y="748" font-family="Inter" font-weight="800" font-size="18" fill="${INK}" fill-opacity=".7" opacity="${c.alpha}">Fuentes: ${esc(P.fuentes)}</text>`;
    }
    const ev = capas.length ? (capas[capas.length - 1].r.evitar || []) : [];
    svg += marcaMovil(t, ev, e === P.mencion);
    svg += marcaFija();
    svg += barra(t, D);
    svg += `<rect x="32" y="805" width="608" height="230" rx="24" fill="${INK}" fill-opacity=".93"/>`;
    for (const c of capas) svg += panel(c.k, t, c.alpha, 0);
    svg += `</svg>`;
    document.getElementById('lienzo').innerHTML = svg;
    ultimo = svg;
    return true;
  };
})();
