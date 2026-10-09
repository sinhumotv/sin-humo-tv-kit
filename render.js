// Render de sin humo TV con Playwright.
// node render.js <proyecto> pruebas 0.1,5,12.5   -> PNG en <proyecto>/pruebas/
// node render.js <proyecto> foto <t> <salida.png> -> un fotograma PNG
// node render.js <proyecto> video                 -> bloques _bloqueN.mp4 (intermedios casi sin pérdida)
const fs = require('fs'), path = require('path'), os = require('os');
const { spawn } = require('child_process');
let pw;
try { pw = require('playwright'); } catch { pw = require('/opt/npm-tools/node_modules/playwright'); }
const KIT = __dirname, DIR = path.resolve(process.argv[2]), MODO = process.argv[3];
const FPS = 30;

function preparar() {
  if (!fs.existsSync(path.join(KIT, 'fondo.jpg'))) require('child_process').execSync(`python3 "${path.join(KIT, 'fondo.py')}"`);
  if (!fs.existsSync(path.join(KIT, 'fonts', 'Inter-Black.otf'))) {
    fs.mkdirSync(path.join(KIT, 'fonts'), { recursive: true });
    for (const f of ['Inter-ExtraBold.otf', 'Inter-Black.otf']) {
      const src = ['/usr/share/fonts/opentype/inter/' + f, '/usr/share/fonts/truetype/inter/' + f.replace('.otf', '.ttf')].find(p => fs.existsSync(p));
      if (src) fs.copyFileSync(src, path.join(KIT, 'fonts', f));
    }
  }
}
function html() {
  preparar();
  const P = fs.readFileSync(path.join(DIR, 'proyecto.json'), 'utf8');
  const T = fs.readFileSync(path.join(DIR, 'tiempos.json'), 'utf8');
  fs.copyFileSync(path.join(KIT, 'fondo.jpg'), path.join(DIR, 'fondo.jpg'));
  const f = p => 'file://' + path.join(KIT, 'fonts', p);
  const h = `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:Inter;font-weight:800;src:url('${f('Inter-ExtraBold.otf')}')}
@font-face{font-family:Inter;font-weight:900;src:url('${f('Inter-Black.otf')}')}
html,body{margin:0;padding:0;background:#f6ebd0;overflow:hidden}#lienzo{width:720px;height:1280px}</style></head>
<body><div id="lienzo"></div><span style="font:900 1px Inter;position:absolute;opacity:0">a</span><span style="font:800 1px Inter;position:absolute;opacity:0">a</span>
<script>window.PROY=${P};window.TIEMPOS=${T};</script>
<script src="${path.join(DIR, 'escenas.js')}"></script><script src="${path.join(KIT, 'motor.js')}"></script></body></html>`;
  const out = path.join(DIR, '_motor.html');
  fs.writeFileSync(out, h);
  return 'file://' + out;
}

async function pagina(browser, url) {
  const pg = await browser.newPage({ viewport: { width: 720, height: 1280 }, deviceScaleFactor: 1.5 });
  const errores = [];
  pg.on('pageerror', e => errores.push(e.message));
  await pg.goto(url);
  await pg.evaluate(() => document.fonts.ready);
  await pg.evaluate(() => window.render(0));
  await pg.evaluate(() => document.fonts.ready);
  const ok = await pg.evaluate(() => document.fonts.check('900 40px Inter') && document.fonts.check('800 40px Inter'));
  if (!ok) console.error('AVISO: Inter no se ha cargado');
  if (errores.length) throw new Error('Error en escenas/motor: ' + errores.join(' | '));
  return pg;
}

async function foto(pg, t, salida) {
  await pg.evaluate(t => window.render(t), t);
  await pg.screenshot({ path: salida, type: 'png' });
}

(async () => {
  const url = html();
  const browser = await pw.chromium.launch({ args: ['--disable-gpu', '--force-color-profile=srgb'] });
  if (MODO === 'pruebas') {
    fs.mkdirSync(path.join(DIR, 'pruebas'), { recursive: true });
    const pg = await pagina(browser, url);
    const ts = process.argv[4].split(',').map(Number);
    for (let i = 0; i < ts.length; i++) await foto(pg, ts[i], path.join(DIR, 'pruebas', `p${String(i).padStart(2, '0')}.png`));
    console.log('pruebas:', ts.length);
  } else if (MODO === 'foto') {
    const pg = await pagina(browser, url);
    await foto(pg, Number(process.argv[4]), process.argv[5]);
  } else if (MODO === 'video') {
    const T = JSON.parse(fs.readFileSync(path.join(DIR, 'tiempos.json')));
    const total = Math.round(T.duracion * FPS);
    const nw = Math.max(1, Math.min(8, os.cpus().length));
    const tam = Math.ceil(total / nw);
    const t0 = Date.now();
    await Promise.all([...Array(nw).keys()].map(async w => {
      const a = w * tam, b = Math.min(total, a + tam);
      if (a >= b) return;
      const pg = await pagina(browser, url);
      const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '10', '-pix_fmt', 'yuv420p', path.join(DIR, `_bloque${w}.mp4`)]);
      for (let f = a; f < b; f++) {
        await pg.evaluate(t => window.render(t), f / FPS);
        const buf = await pg.screenshot({ type: 'jpeg', quality: 92 });
        if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
        if (w === 0 && (f - a) % 150 === 0) console.log(`bloque 0: ${f - a}/${b - a} (${((Date.now() - t0) / 1000).toFixed(0)} s)`);
      }
      ff.stdin.end();
      await new Promise(r => ff.on('close', r));
    }));
    fs.writeFileSync(path.join(DIR, '_bloques.txt'), [...Array(nw).keys()].filter(w => w * tam < total).map(w => `file '_bloque${w}.mp4'`).join('\n'));
    console.log(`render ${total} fotogramas en ${((Date.now() - t0) / 1000).toFixed(0)} s`);
  }
  await browser.close();
})().catch(e => { console.error(e.message || e); process.exit(1); });
