// Ceuta, dos meses después (8 oct 2026) — ejemplo de tono grave con la biblioteca del kit v2
(function () {
  window.ESCENAS = [
    // 1. Gancho: 72.000 personas en 2 días
    (L, A) => ({
      svg: A.txtC(310, 330, A.cuentaM(L, 0, .8, 72000), 112, A.VER, 'middle', 12) +
        A.gente(L, 70, 420, 11, 3, -.5, A.VER) +
        (L > 2.2 ? A.calendario(520, 230, .7 * A.pop(L, 2.2), 'JULIO', '2 días') : ''),
      lupi: { x: 560, y: 610, s: .8, expr: 'seria', mira: [-.8, -.6], brazos: 'abajo' },
      evitar: [[100, 240, 420, 120]],
    }),
    // 2. Mapa: desde Marruecos, muchos a nado
    (L, A) => {
      const costa = `<path d="M0 520 Q160 500 250 470 Q300 455 330 470 L330 740 L0 740 Z" fill="#e8d6a8" stroke="${A.INK}" stroke-width="6"/>` +
        `<path d="M330 470 Q420 440 520 470 Q600 490 640 480 L640 740 L330 740 Z" fill="#cfe3b6" stroke="${A.INK}" stroke-width="6"/>` +
        `<path d="M330 470 L330 740" stroke="${A.ROJ}" stroke-width="6" stroke-dasharray="12 8"/>`;
      const nado = [0, 1, 2].map(i => A.linea([[230 - i * 50, 560 + i * 40], [200 - i * 40, 430 - i * 10], [380 + i * 30, 380 + i * 15], [450 + i * 20, 455]], A.prog(L, .8 + i * .5, 1.4), A.INK, 5)).join('');
      return {
        svg: A.olas(330, L) + costa + nado +
          A.txt(140, 640, 'MARRUECOS', 34, A.INK, 'middle', 900) + A.txt(500, 600, 'CEUTA', 40, A.INK, 'middle', 900) +
          (L > .2 ? A.calendario(520, 260, .62 * A.pop(L, .2), 'JULIO', '30-31') : '') + A.onda(470, 455, L, 2.6, 70, A.ROJ),
        evitar: [[0, 300, 640, 440]],
      };
    },
    // 3. 1.500 personas cada hora (Lupi amplía la cifra)
    (L, A) => {
      const llega = A.easeIO((L - 2.4) / .6), va = A.easeIO((L - 4.4) / .6);
      return {
        svg: A.reloj(160, 360, A.pop(L, .1), L) +
          (L > .7 ? A.txtC(440, 380, A.cuentaM(L, .7, .9, 1500), 100, A.ORA, 'middle', 12) : '') +
          (L > 1.4 ? A.txt(440, 440, 'cada hora', 40, A.INK, 'middle', 900) : '') +
          A.gente(L, 80, 560, 15, 2, 1.6, A.ORA, 36, .28) + A.destello(440, 350, L, 1.5, 120, A.ORA),
        lupi: { x: 600 - 160 * llega + 160 * va, y: 580 - 210 * llega + 210 * va, s: 1, expr: 'seria', mira: [Math.sin(L * 3) * .8, 0], brazos: 'senala', lupa: L > 2.6 && L < 4.6 ? true : undefined },
        evitar: [[300, 290, 300, 170]],
      };
    },
    // 4. 70.000 volvieron · al menos 57 muertos (sobrio)
    (L, A) => ({
      svg: (L > .1 ? A.txtC(330, 330, A.cuentaM(L, .1, 1, 70000), 96, A.VER, 'middle', 11) : '') +
        A.flecha(470, 400, 200, 400, A.prog(L, 1.0, .6), A.VER, 10) +
        (L > 1.0 ? A.txt(335, 450, 'volvieron', 36, A.INK, 'middle', 900) : '') +
        (L > 2.8 ? A.vela(150, 620, A.fade(L, 2.8, .6), L) : '') +
        (L > 3.2 ? `<g opacity="${A.fade(L, 3.2, .6)}">${A.txtC(340, 645, 'al menos 57', 52, '#4a4458', 'middle', 0)}</g>` : ''),
      lupi: { x: 590, y: 610, s: .7, expr: 'seria', mira: [-.7, .3], brazos: 'abajo' },
      evitar: [[140, 260, 380, 210], [110, 560, 400, 120]],
    }),
    // 5. 11.026 retornos desde agosto · semana récord
    (L, A) => ({
      svg: A.txtC(320, 320, A.cuentaM(L, .1, 1.2, 11026), 104, A.AZU, 'middle', 12) +
        A.txt(320, 380, 'retornos desde agosto', 32, A.INK, 'middle', 900) +
        A.grafico(150, 650, [3, 4, 5, 6, 9], A.prog(L, 1.4, 1.6), .95, A.AZU) +
        (L > 3.2 ? A.etiqueta(500, 470, 'récord', A.pop(L, 3.2), A.ORO, -6) : '') + A.destello(470, 470, L, 3.3, 90),
      evitar: [[130, 250, 400, 150]],
    }),
    // 6. 2.827 menores bajo protección (Lupi amplía la cifra)
    (L, A) => {
      const llega = A.easeIO((L - 2.0) / .6), va = A.easeIO((L - 4.0) / .6);
      return {
        svg: A.escudo(170, 470, A.pop(L, .1), A.VER) +
          A.txtC(430, 460, A.cuentaM(L, .4, 1.2, 2827), 100, A.ROJ, 'middle', 12) +
          (L > 1.0 ? A.txt(430, 520, 'menores', 44, A.INK, 'middle', 900) : '') + A.onda(170, 470, L, .3, 120, A.VER),
        lupi: { x: 610 - 180 * llega + 180 * va, y: 580 - 140 * llega + 140 * va, s: 1, expr: 'seria', mira: [Math.sin(L * 3) * .8, 0], brazos: 'senala', lupa: L > 2.2 && L < 4.2 ? true : undefined },
        evitar: [[290, 380, 300, 160]],
      };
    },
    // 7. Solo 173 trasladados: 6 de cada 100 · varias comunidades se niegan
    (L, A) => {
      const puntos = A.cien(L, 80, 260, 6, .2, 2.6);
      const cierre = L > 5.6 ? [0, 1, 2].map(i => A.tachado(430 + i * 80, 610, A.pop(L, 5.6 + i * .3))).join('') : '';
      return {
        svg: puntos + (L > 1.4 ? A.txtC(510, 330, A.cuentaM(L, 1.4, 1, 173), 96, A.ORA, 'middle', 11) : '') +
          (L > 2.6 ? A.txt(510, 400, '6 de cada 100', 34, A.INK, 'middle', 900) : '') +
          (L > 2.0 ? A.txt(500, 260, 'de 2.827', 30, A.INK, 'middle', 800) : '') + cierre + A.destello(510, 300, L, 1.6, 80, A.ORA),
        lupi: { x: 140, y: 600, s: .75, expr: L > 5.6 ? 'seria' : 'curiosa', mira: [.8, -.4], brazos: 'abajo' },
        evitar: [[60, 240, 580, 320]],
      };
    },
    // 8. Mención: solo hechos · migrantes escondidos (Lupi amplía el sello)
    (L, A) => {
      const paso = A.easeIO((L - .2) / .7), sale = A.easeIO((L - 2.3) / .7);
      return {
        svg: A.sello(330, 360, A.pop(L, 0) * 1.05, -5) +
          [0, 1, 2].map(i => L > 2.8 + i * .4 ? A.casa(160 + i * 170, 600, .9 * A.pop(L, 2.8 + i * .4), A.pop(L, 3.4 + i * .4)) : '').join(''),
        lupi: { x: 600 - 270 * paso + 280 * sale, y: 560 - 200 * paso - 80 * sale, s: L > 2.3 ? 1 - .3 * sale : 1, expr: 'seria', mira: [Math.sin(L * 4) * .9, 0], brazos: L < 2.3 ? 'senala' : 'abajo', lupa: L > .8 && L < 2.4 ? true : undefined },
        evitar: [[100, 290, 460, 140]],
      };
    },
    // 9. Visita de los Reyes · pregunta final (sello pequeño, Lupi seria y luego curiosa)
    (L, A) => ({
      svg: (L > .1 ? A.corona(200, 330, .9 * A.pop(L, .1)) : '') +
        (L > .6 ? A.calendario(440, 330, .75 * A.pop(L, .6), 'MARTES', '13') : '') +
        (L > 2.6 ? A.txtC(300, 600, '?', 170, A.ORO, 'middle', 12) : '') +
        (L > 6.5 ? A.sello(330, 700, .45 * A.pop(L, 6.5), -4) : ''),
      lupi: { x: 560, y: 590, s: .85, expr: L > 2.6 ? 'curiosa' : 'seria', mira: [-.8, -.2], brazos: L > 6.5 ? 'saluda' : 'abajo' },
      evitar: [[100, 240, 480, 180]],
    }),
  ];
})();
