// Escenas del vídeo: España crece más, pero la inflación empeora (9 oct 2026)
window.ESCENAS = [
  // 1. Gancho: la economía sube… y tu cartera baja
  (L, A) => {
    const g = A.grafico(80, 640, [3, 4, 5, 7], A.prog(L, 0, 1.2), 1.15, A.VER);
    const fl = A.flecha(100, 560, 390, 300, A.prog(L, .6, .7), A.VER, 12);
    const cart = A.esc_(500, 420, A.pop(L, 2.0) * (1 - 0.25 * A.easeOut((L - 3.2) / 1.2)), A.cartera(500, 420, 1));
    const baja = A.flecha(640, 300, 640, 470, A.prog(L, 3.0, .5), A.ROJ, 10);
    return {
      svg: g + fl + A.destello(390, 300, L, 1.3) + cart + baja + A.onda(500, 420, L, 3.0),
      lupi: { x: 560, y: 605, s: .8, expr: L > 3 ? 'sorprendida' : 'curiosa', mira: L > 3 ? [-0.6, -0.5] : [-1, -0.4], brazos: 'senala' },
      evitar: [[60, 260, 360, 400]],
    };
  },
  // 2. Banco de España: +2,6 %
  (L, A) => {
    const banco = A.esc_(330, 590, A.pop(L, .1), A.banco(330, 590, 1.05));
    const num = L > 1.0 ? A.esc_(360, 330, A.pop(L, 1.0), A.txtC(360, 360, '+' + A.cuenta(L, 1.0, 1.4, 2.3, 2.6, 1) + ' %', 120, A.VER, 'middle', 12)) : '';
    const junio = L > 3.4 ? A.etiqueta(560, 470, '2,3 %', .8 * A.pop(L, 3.4), A.CRE, 8) + (L > 3.6 ? A.txt(560, 425, 'junio', 26, A.INK, 'middle', 800) : '') : '';
    const tacha = L > 4.4 ? `<path d="M490 470 L${490 + 140 * A.prog(L, 4.4, .3)} 470" stroke="${A.ROJ}" stroke-width="8" stroke-linecap="round"/>` : '';
    return {
      svg: banco + num + A.destello(360, 300, L, 2.4, 90) + junio + tacha + A.onda(330, 590, L, .2, 160, A.VER),
      evitar: [[200, 230, 330, 160]],
    };
  },
  // 3. La trampa: inflación 3,6 → 3,9 (Lupi la amplía)
  (L, A) => {
    const nivel = .55 + .17 * A.easeOut((L - 2.0) / 1.5);
    const term = A.esc_(180, 520, A.pop(L, .1), A.termometro(180, 520, 1.1, nivel));
    const a = L > .6 ? A.esc_(470, 310, A.pop(L, .6), A.txtC(470, 330, '3,6 %', 78, A.CRE, 'middle', 10)) : '';
    const fl = A.flecha(470, 360, 470, 450, A.prog(L, 1.6, .5), A.ROJ, 10);
    const b = L > 2.1 ? A.esc_(470, 520, A.pop(L, 2.1), A.txtC(470, 545, '3,9 %', 96, A.ROJ, 'middle', 12)) : '';
    const llega = A.easeIO((L - 3.2) / .7);
    const va = A.easeIO((L - 5.2) / .6);
    const lx = 620 - 150 * llega + 140 * va, ly = 580 - 55 * llega + 50 * va;
    return {
      svg: term + a + fl + b + A.destello(470, 520, L, 2.3, 110, A.ROJ),
      lupi: { x: lx, y: ly, s: 1, expr: L > 3.8 ? 'sorprendida' : 'curiosa', mira: [Math.sin(L * 3) * .8, -.2], brazos: 'senala', lupa: L > 3.4 && L < 5.4 ? true : undefined },
      evitar: [[330, 260, 300, 330]],
    };
  },
  // 4. Qué significa: 1.500 € → 58 € más
  (L, A) => {
    const carro = A.esc_(330, 560, A.pop(L, .1), A.carrito(330, 560, 1.4, A.AZU));
    const et1 = L > .9 ? A.etiqueta(300, 380, '1.500 €', A.pop(L, .9), A.CRE, -6) : '';
    const et2 = L > 2.6 ? A.etiqueta(500, 270, '+58 €', A.pop(L, 2.6), A.ROJ, 8) : '';
    let monedas = '';
    for (let i = 0; i < 4; i++) {
      const t0 = 3.4 + i * .45; if (L < t0) continue;
      const y = 250 + 300 * A.easeOut((L - t0) / .6);
      monedas += A.moneda(150 + i * 110, Math.min(y, 520 - i * 8), .9);
    }
    return {
      svg: carro + et1 + et2 + A.destello(500, 270, L, 2.8, 100, A.ROJ) + monedas,
      evitar: [[180, 220, 460, 220]],
    };
  },
  // 5. Mención al canal + causas (Lupi amplía el sello)
  (L, A) => {
    const sello = A.sello(330, 400, A.pop(L, 0) * 1.05, -5);
    const paso = A.easeIO((L - .3) / .8), sale = A.easeIO((L - 2.6) / .8);
    const lx = 600 - 300 * paso + 260 * sale, ly = 560 - 170 * paso - 230 * sale;
    const rayo = L > 3.1 ? A.rayo(150, 610, A.pop(L, 3.1) * .9) : '';
    const barril = L > 3.6 ? A.barril(330, 620, A.pop(L, 3.6) * .9) : '';
    const globo = L > 4.2 ? A.globo(500, 615, A.pop(L, 4.2) * .75, A.AZU) : '';
    return {
      svg: sello + rayo + barril + globo + A.destello(150, 610, L, 3.2) + A.onda(500, 615, L, 4.3, 90, A.ROJ),
      lupi: { x: lx, y: ly, s: L > 2.6 ? 1 - .3 * sale : 1, expr: L > 3 ? 'seria' : 'curiosa', mira: [Math.sin(L * 4) * .9, 0], brazos: L < 2.6 ? 'senala' : 'abajo', lupa: L > .9 && L < 2.7 ? true : undefined },
      evitar: [[100, 330, 460, 140]],
    };
  },
  // 6. Peor escenario + pregunta + guiño final
  (L, A) => {
    const al = A.esc_(170, 420, A.pop(L, .1), A.alerta(170, 420, 1.1));
    const n = L > 1.0 ? A.esc_(430, 380, A.pop(L, 1.0), A.txtC(430, 400, '+1 punto', 76, A.ROJ, 'middle', 10)) : '';
    const casi = L > 1.6 ? A.txt(430, 300, 'casi', 44, A.INK, 'middle', 900) : '';
    const carro = L > 4.2 ? A.esc_(260, 600, A.pop(L, 4.2), A.carrito(260, 600, .85, A.ORA) + A.txtC(280, 520, '?', 90, A.ORO, 'middle', 9)) : '';
    const sello = L > 6.0 ? A.sello(300, 690, .5 * A.pop(L, 6.0), -4) : '';
    return {
      svg: al + n + casi + A.destello(430, 380, L, 1.2, 110, A.ROJ) + carro + A.onda(170, 420, L, .3, 110, A.ROJ) + sello,
      lupi: { x: 570, y: 590, s: .85, expr: L > 6.2 ? 'guino' : L > 4 ? 'curiosa' : 'seria', mira: L > 4 ? [-.8, .2] : [-.6, -.4], brazos: L > 6.2 ? 'saluda' : 'abajo' },
      evitar: [[300, 300, 280, 140]],
    };
  },
];
