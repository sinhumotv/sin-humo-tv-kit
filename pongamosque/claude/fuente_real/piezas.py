ILU = r"""
const marca = (nom, obj, x, y, z) => { const m = new THREE.Object3D(); m.name = 'p_' + nom; m.position.set(x, y, z); obj.add(m); return m; };
const L2 = (v, x) => Array.isArray(v) ? v[0] + (v[1] - v[0]) * x : (v || 0);
const cl = x => Math.max(0, Math.min(1, x)), sm = x => { x = cl(x); return x * x * (3 - 2 * x); };
const g = new THREE.Group(), dias = o.dias === undefined ? 0 : o.dias, roto = !!o.roto, apaga = !!o.apaga, sinPared = !!o.sinPared;
const D0 = Array.isArray(dias) ? dias[0] : dias, D1 = Array.isArray(dias) ? dias[1] : dias, Dm = (D0 + D1) / 2;
const R = k => { const s = Math.sin(k * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
const tick = (obj, f) => { obj.userData.tick = f; return obj; };
const lisa = (col, ex) => { const m = new THREE.MeshStandardMaterial(Object.assign({ color: col, roughness: 0.5 }, ex || {})); m.defines = { PQ_LISO: 1 }; return m; };
const caja = (p, w, hh, d, m, x, y, z) => h.caja(p, w, hh, d, m, x, y, z);

const lisa2 = (col, ex) => { const m = new THREE.MeshStandardMaterial(Object.assign({ color: col, roughness: 0.55 }, ex || {})); m.defines = { PQ_LISO: 1 }; return m; };
const torno = (perfil, col, ex, seg) => new THREE.Mesh(new THREE.LatheGeometry(perfil.map(([a, b]) => new THREE.Vector2(a, b)), seg || 32), lisa2(col, ex));
const ESTIL = {
  manzana: (col) => { const q = new THREE.Group(); const m = h.malla(new THREE.SphereGeometry(0.5, 24, 18), lisa2(col || '#c8262c', { roughness: 0.35 }), 0, 0.5, 0); m.scale.set(1, 0.9, 1); q.add(m); q.add(h.malla(new THREE.CylinderGeometry(0.03, 0.04, 0.25, 6), lisa2('#5a3a1e'), 0.02, 1.0, 0)); const hj = h.malla(new THREE.SphereGeometry(0.12, 8, 6), lisa2('#4a9a3a'), 0.12, 1.02, 0); hj.scale.set(1.4, 0.3, 0.7); q.add(hj); return q; },
  lemon: () => { const q = new THREE.Group(); const m = h.malla(new THREE.SphereGeometry(0.5, 20, 14), lisa2('#f2cf2a', { roughness: 0.45 }), 0, 0.42, 0); m.scale.set(1.25, 0.85, 0.85); q.add(m); return q; },
  food_lime_01: () => { const q = new THREE.Group(); q.add(h.malla(new THREE.SphereGeometry(0.5, 20, 14), lisa2('#6db33a', { roughness: 0.45 }), 0, 0.5, 0)); return q; },
  food_kiwi_01: () => { const q = new THREE.Group(); const m = h.malla(new THREE.SphereGeometry(0.5, 16, 12), lisa2('#7a5a32', { roughness: 0.9 }), 0, 0.42, 0); m.scale.set(1.25, 0.85, 0.85); q.add(m); return q; },
  food_avocado_01: () => { const q = new THREE.Group(); q.add(torno([[0, 0], [0.3, 0.05], [0.42, 0.3], [0.32, 0.7], [0.18, 0.95], [0, 1]], '#2f4a22', { roughness: 0.8 })); return q; },
  food_pomegranate_01: () => { const q = new THREE.Group(); q.add(h.malla(new THREE.SphereGeometry(0.5, 20, 16), lisa2('#a3202c', { roughness: 0.4 }), 0, 0.48, 0)); q.add(h.malla(new THREE.CylinderGeometry(0.12, 0.08, 0.16, 6), lisa2('#7a1820'), 0, 0.98, 0)); return q; },
  sweet_potato: () => { const q = new THREE.Group(); const m = h.malla(new THREE.CapsuleGeometry(0.25, 0.6, 6, 12), lisa2('#8a4a2a', { roughness: 0.9 }), 0, 0.25, 0); m.rotation.z = Math.PI / 2; q.add(m); return q; },
  yellow_onion: () => { const q = new THREE.Group(); q.add(torno([[0, 0], [0.35, 0.1], [0.5, 0.4], [0.35, 0.75], [0.06, 0.95], [0.02, 1.1], [0, 1.1]], '#c98a3a', { roughness: 0.6 })); return q; },
  carrot_cake: () => { const q = new THREE.Group(); q.add(h.malla(new THREE.CylinderGeometry(0.5, 0.5, 0.75, 40), lisa2('#a8682e', { roughness: 0.8 }), 0, 0.375, 0)); q.add(h.malla(new THREE.CylinderGeometry(0.505, 0.505, 0.06, 40), lisa2('#f4e6d0'), 0, 0.42, 0)); q.add(h.malla(new THREE.CylinderGeometry(0.52, 0.5, 0.12, 40), lisa2('#f7eedf', { roughness: 0.3 }), 0, 0.8, 0));
    for (let k = 0; k < 8; k++) { const a = k / 8 * 6.283; q.add(h.malla(new THREE.SphereGeometry(0.06, 10, 8), lisa2('#b5121b', { roughness: 0.2 }), Math.cos(a) * 0.36, 0.9, Math.sin(a) * 0.36)); } return q; },
  jug_01: () => { const q = new THREE.Group(); q.add(torno([[0, 0], [0.32, 0], [0.36, 0.08], [0.38, 0.55], [0.3, 0.85], [0.33, 1], [0.3, 1], [0, 0.98]], '#f3f1ea', { roughness: 0.3 })); const as = h.malla(new THREE.TorusGeometry(0.2, 0.05, 8, 16, Math.PI), lisa2('#f3f1ea', { roughness: 0.3 }), -0.38, 0.55, 0); as.rotation.z = Math.PI / 2; q.add(as);
    q.add(h.malla(new THREE.CylinderGeometry(0.381, 0.381, 0.12, 32, 1, true), lisa2('#2f6fd0', { side: THREE.DoubleSide }), 0, 0.45, 0)); return q; },
  electric_stove: () => { const q = new THREE.Group(); h.caja(q, 0.76, 0.86, 0.6, lisa2('#e9e5dc', { roughness: 0.35 }), 0, 0.43, 0); h.caja(q, 0.6, 0.42, 0.02, lisa2('#1c1f24', { roughness: 0.15 }), 0, 0.42, 0.305); h.caja(q, 0.7, 0.02, 0.56, lisa2('#16181c', { roughness: 0.1 }), 0, 0.87, 0);
    [[-0.18, -0.13], [0.18, -0.13], [-0.18, 0.13], [0.18, 0.13]].forEach(([x, z]) => { const r2 = h.malla(new THREE.TorusGeometry(0.09, 0.008, 6, 24), lisa2('#555'), x, 0.885, z); r2.rotation.x = Math.PI / 2; q.add(r2); }); for (let k = 0; k < 4; k++) q.add(h.malla(new THREE.CylinderGeometry(0.025, 0.025, 0.03, 12), lisa2('#333'), -0.24 + k * 0.16, 0.76, 0.31)).rotation.x = Math.PI / 2; return q; },
  vintage_microwave: () => { const q = new THREE.Group(); h.caja(q, 0.5, 0.29, 0.36, lisa2('#2b2f36', { roughness: 0.4 }), 0, 0.145, 0); h.caja(q, 0.32, 0.2, 0.01, new THREE.MeshStandardMaterial({ color: '#0d1014', emissive: '#203040', emissiveIntensity: 0.4, roughness: 0.1 }), -0.06, 0.15, 0.18);
    const rel = h.malla(new THREE.PlaneGeometry(0.08, 0.03), new THREE.MeshBasicMaterial({ color: '#3cff8a' }), 0.17, 0.22, 0.182); q.add(rel); return q; },
  vintage_electric_kettle: () => { const q = new THREE.Group(); q.add(torno([[0, 0], [0.4, 0], [0.42, 0.1], [0.4, 0.7], [0.25, 0.95], [0, 0.97]], '#c9ced6', { metalness: 0.7, roughness: 0.25 })); const as = h.malla(new THREE.TorusGeometry(0.28, 0.05, 8, 16, Math.PI), lisa2('#222'), -0.38, 0.55, 0); as.rotation.z = Math.PI / 2; q.add(as); return q; },
  wooden_cutting_board: () => { const q = new THREE.Group(); h.caja(q, 1, 0.06, 0.6, lisa2('#b07a45', { roughness: 0.7 }), 0, 0.03, 0); return q; },
  wooden_bowl_01: () => { const q = new THREE.Group(); q.add(torno([[0, 0], [0.3, 0], [0.48, 0.15], [0.5, 0.4], [0.46, 0.4], [0.44, 0.17], [0.28, 0.05], [0, 0.05]], '#9a6a3c', { roughness: 0.6 })); return q; },
  pot_enamel_01: () => { const q = new THREE.Group(); q.add(h.malla(new THREE.CylinderGeometry(0.5, 0.48, 0.6, 32), lisa2('#c43a2c', { roughness: 0.3 }), 0, 0.3, 0)); q.add(h.malla(new THREE.CylinderGeometry(0.52, 0.52, 0.06, 32), lisa2('#a32f24', { roughness: 0.3 }), 0, 0.62, 0)); q.add(h.malla(new THREE.SphereGeometry(0.08, 10, 8), lisa2('#222'), 0, 0.68, 0)); return q; },
  painted_wooden_chair_01: () => { const q = new THREE.Group(); const m = lisa2('#8a5a34', { roughness: 0.6 }); h.caja(q, 0.45, 0.05, 0.45, m, 0, 0.47, 0); [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([a, b]) => h.caja(q, 0.04, 0.47, 0.04, m, a * 0.2, 0.235, b * 0.2)); h.caja(q, 0.45, 0.45, 0.04, m, 0, 0.75, -0.2); return q; },
};
const pon = (id, op, x, y, z, ry, p) => { op = op || {}; const f = ESTIL[id] || (id === 'food_apple_01' ? ESTIL.manzana : null); const w = new THREE.Group(); let m = f ? f() : new THREE.Group();
  const b = new THREE.Box3().setFromObject(m), sz = b.getSize(new THREE.Vector3()); const k = op.alto ? op.alto / Math.max(1e-3, sz.y) : op.ancho ? op.ancho / Math.max(1e-3, sz.x) : op.largo ? op.largo / Math.max(1e-3, Math.max(sz.x, sz.z)) : 1;
  m.scale.setScalar(k); m.position.y = -b.min.y * k; w.add(m); w.position.set(x, y, z); w.rotation.y = ry || 0; (p || g).add(w); return w; };

const W = 4.6, F = 3.2, AL = 2.7;
const lienzo = (w, hh, f, rx, ry) => { const cv = document.createElement('canvas'); cv.width = w; cv.height = hh; f(cv.getContext('2d'), w, hh); const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rx || 1, ry || 1); return t; };
const sueloM = new THREE.MeshStandardMaterial({ map: lienzo(256, 256, (c2, w, hh) => { for (let k = 0; k < 8; k++) { c2.fillStyle = ['#7a4a2a', '#835233', '#6f4325', '#8a5838'][k % 4]; c2.fillRect(0, k * 32, w, 32); c2.fillStyle = 'rgba(0,0,0,0.25)'; c2.fillRect(0, k * 32, w, 2); c2.fillRect((k * 97) % w, k * 32, 2, 32); } }, 3, 4), roughness: 0.45 }); sueloM.defines = { PQ_LISO: 1 };
const suelo = new THREE.Mesh(new THREE.PlaneGeometry(W, F), sueloM); suelo.rotation.x = -Math.PI / 2; suelo.receiveShadow = true; g.add(suelo);
const azul = new THREE.MeshStandardMaterial({ map: lienzo(256, 256, (c2, w, hh) => { c2.fillStyle = '#3c4f58'; c2.fillRect(0, 0, w, hh); c2.strokeStyle = 'rgba(255,255,255,0.10)'; c2.lineWidth = 3; for (let k = 0; k <= 8; k++) { c2.beginPath(); c2.moveTo(0, k * 32); c2.lineTo(w, k * 32); c2.stroke(); c2.beginPath(); c2.moveTo(k * 64 + (k % 2) * 0, 0); c2.lineTo(k * 64, hh); c2.stroke(); } }, 5, 3), roughness: 0.35 }); azul.defines = { PQ_LISO: 1 };
if (!sinPared) { caja(g, W, AL, 0.08, azul, 0, AL / 2, -F / 2); }
else { caja(g, W, 0.12, 0.08, azul, 0, 0.06, -F / 2); }
caja(g, 0.08, AL, F, lisa('#33424c', { roughness: 0.8 }), -W / 2, AL / 2, 0);
caja(g, W, 0.1, 0.03, lisa('#e8e2d8'), 0, 0.05, -F / 2 + 0.06);
const vent = new THREE.Group(); caja(vent, 0.06, 1.1, 1.0, lisa('#f2f2ee'), 0, 0, 0);
{ const noche = lienzo(256, 288, (c2, w, hh) => { const gr = c2.createLinearGradient(0, 0, 0, hh); gr.addColorStop(0, '#0a1530'); gr.addColorStop(1, '#2a3f6e'); c2.fillStyle = gr; c2.fillRect(0, 0, w, hh); c2.fillStyle = '#fff6d8'; c2.beginPath(); c2.arc(190, 60, 22, 0, 7); c2.fill();
  for (let k = 0; k < 9; k++) { const bx = k * 30 - 6, bh = 70 + R(k + 40) * 120; c2.fillStyle = '#0e1626'; c2.fillRect(bx, hh - bh, 28, bh); for (let y = hh - bh + 8; y < hh - 6; y += 14) for (let x = bx + 4; x < bx + 24; x += 8) if (R(x * 7 + y) > 0.55) { c2.fillStyle = '#ffcf6a'; c2.fillRect(x, y, 4, 6); } } });
  caja(vent, 0.02, 0.98, 0.88, new THREE.MeshStandardMaterial({ map: noche, emissive: '#ffffff', emissiveMap: noche, emissiveIntensity: 0.9 }), 0.03, 0, 0).rotation.y = 0; }
for (let k = 0; k < 9; k++) caja(vent, 0.03, 0.03, 0.9, lisa('#f7f7f4'), 0.06, -0.44 + k * 0.11, 0);
vent.position.set(-W / 2 + 0.05, 1.55, 0.55); g.add(vent);
const mueble = lisa('#d8c7a8', { roughness: 0.5 }), tirador = lisa('#c9ced6', { metalness: 0.8, roughness: 0.25 }), marmol = lisa('#3b4048', { roughness: 0.2 });
for (let x = -0.55; x < 1.3; x += 0.6) { caja(g, 0.58, 0.82, 0.6, mueble, x + 0.3, 0.45, -F / 2 + 0.35); caja(g, 0.3, 0.02, 0.02, tirador, x + 0.3, 0.78, -F / 2 + 0.66); }
caja(g, 0.06, 0.08, 0.55, lisa('#2a2a2a'), 0.32, 0.04, -F / 2 + 0.33);
caja(g, 1.9, 0.04, 0.64, marmol, 0.38, 0.88, -F / 2 + 0.34);
for (let x = -0.55; x < 1.3; x += 0.6) { caja(g, 0.58, 0.7, 0.35, mueble, x + 0.3, 1.95, -F / 2 + 0.2); caja(g, 0.02, 0.22, 0.02, tirador, x + 0.52, 1.75, -F / 2 + 0.38); }
pon('electric_stove', { alto: 0.92 }, 1.82, 0, -F / 2 + 0.36, 0);
pon('vintage_microwave', { ancho: 0.5 }, 0.0, 0.9, -F / 2 + 0.3, 0);
pon('vintage_electric_kettle', { alto: 0.26 }, 0.62, 0.9, -F / 2 + 0.3, -0.5);
pon('wooden_cutting_board', { largo: 0.42 }, 1.0, 0.9, -F / 2 + 0.38, 0.2);
pon('yellow_onion', { alto: 0.08 }, 1.05, 0.92, -F / 2 + 0.4, 0);
pon('wooden_bowl_01', { ancho: 0.3 }, 0.45, 0.9, -F / 2 + 0.52, 0);
[[0.4, 0.06], [0.5, 0.05], [0.45, 0.1]].forEach(([x, dz], k) => pon(k === 1 ? 'lemon' : 'food_apple_01', { alto: 0.075 }, x, 0.95, -F / 2 + 0.47 + dz, k));
pon('pot_enamel_01', { ancho: 0.28 }, 1.75, 0.92, -F / 2 + 0.3, 0);
pon('painted_wooden_chair_01', { alto: 0.95 }, 1.2, 0, 0.6, -2.4);
const reloj = new THREE.Group(); reloj.position.set(0.7, 2.42, -F / 2 + 0.05); g.add(reloj);
const esfera = h.malla(new THREE.CylinderGeometry(0.17, 0.17, 0.04, 40), lisa('#fbfaf6', { roughness: 0.3 }), 0, 0, 0.02); esfera.rotation.x = Math.PI / 2; reloj.add(esfera);
const aro = h.malla(new THREE.TorusGeometry(0.17, 0.018, 10, 40), lisa('#2b2b2b', { metalness: 0.5, roughness: 0.4 }), 0, 0, 0.04); reloj.add(aro);
for (let k = 0; k < 12; k++) { const a = k / 12 * Math.PI * 2; caja(reloj, 0.012, k % 3 ? 0.025 : 0.045, 0.005, lisa('#222'), Math.sin(a) * 0.14, Math.cos(a) * 0.14, 0.045).rotation.z = -a; }
const ag = (l, w) => { const q = new THREE.Group(); caja(q, w, l, 0.006, lisa('#1a1a1a'), 0, l / 2 - 0.015, 0); q.position.z = 0.05; reloj.add(q); return q; };
const hh2 = ag(0.09, 0.014), mm2 = ag(0.13, 0.009); const RH = o.reloj || [8, 8];
tick(reloj, x => { const hora = L2(RH, sm(x)); mm2.rotation.z = -(hora % 1) * Math.PI * 2; hh2.rotation.z = -(hora % 12) / 12 * Math.PI * 2; }); reloj.userData.tick(0);
marca('reloj', reloj, 0, 0, 0.1);
const cal = document.createElement('canvas'); cal.width = 256; cal.height = 320; { const c2 = cal.getContext('2d'); c2.fillStyle = '#ffffff'; c2.fillRect(0, 0, 256, 320); c2.fillStyle = '#d6322f'; c2.fillRect(0, 0, 256, 80); c2.fillStyle = '#fff'; c2.font = '900 46px Archivo Black, Inter, sans-serif'; c2.textAlign = 'center'; c2.fillText('NOVIEMBRE', 128, 58); c2.fillStyle = '#222'; c2.font = '900 170px Archivo Black, Inter, sans-serif'; c2.fillText(String(Math.round(17 + Dm)), 128, 270); }
const ct = new THREE.CanvasTexture(cal); ct.colorSpace = THREE.SRGBColorSpace; caja(g, 0.32, 0.4, 0.01, new THREE.MeshStandardMaterial({ map: ct, roughness: 0.7 }), -W / 2 + 0.05, 1.5, -0.55).rotation.y = Math.PI / 2;
marca('calendario', g, -W / 2 + 0.1, 1.5, -0.55);
const NX = -1.55, NW = 0.76, NH = 1.86, ND = 0.68, NZ = -F / 2 + 0.06 + ND / 2 + (sinPared ? 0.25 : 0);
const nev = new THREE.Group(); nev.position.set(NX, 0, NZ); g.add(nev);
const esmalte = new THREE.MeshPhysicalMaterial({ color: '#efe8da', roughness: 0.3, metalness: 0.0, clearcoat: 0.6, clearcoatRoughness: 0.2 }); esmalte.defines = { PQ_LISO: 1 };
const forro = lisa('#f7f9fa', { roughness: 0.6 }), cristal = new THREE.MeshPhysicalMaterial({ color: '#e8f6ff', roughness: 0.4, transmission: 0, transparent: true, opacity: 0.28, depthWrite: false }); cristal.defines = { PQ_LISO: 1 };
const e = 0.04; caja(nev, e, NH, ND, esmalte, -NW / 2 + e / 2, NH / 2, 0); caja(nev, e, NH, ND, esmalte, NW / 2 - e / 2, NH / 2, 0); caja(nev, NW, e, ND, esmalte, 0, NH - e / 2, 0); caja(nev, NW, 0.1, ND, esmalte, 0, 0.05, 0); caja(nev, NW, NH, e, esmalte, 0, NH / 2, -ND / 2 + e / 2);
caja(nev, NW - 2 * e, NH - 0.16, 0.01, forro, 0, NH / 2 + 0.03, -ND / 2 + e + 0.005);
const FY = 1.38; caja(nev, NW - 2 * e, 0.05, ND - e, esmalte, 0, FY, 0.0);
caja(nev, NW - 0.02, 0.06, 0.02, lisa('#2a2a2a'), 0, 0.05, ND / 2 + 0.005);
for (let k = 0; k < 6; k++) caja(nev, 0.02, 0.03, 0.01, lisa('#555'), -0.25 + k * 0.1, 0.05, ND / 2 + 0.012);
const pisos = [0.42, 0.74, 1.06]; pisos.forEach(y => { caja(nev, NW - 2 * e - 0.01, 0.012, ND - e - 0.06, cristal, 0, y, 0.0); caja(nev, NW - 2 * e - 0.01, 0.02, 0.015, lisa('#d8dde2'), 0, y, ND / 2 - 0.04); });
const cajon = new THREE.Group(); caja(cajon, NW - 0.1, 0.22, ND - 0.1, new THREE.MeshPhysicalMaterial({ color: '#f0f8ff', roughness: 0.1, transparent: true, opacity: 0.35, depthWrite: false }), 0, 0.11, 0); cajon.position.set(0, 0.13, 0.0); nev.add(cajon);
const luzAct = { v: 1 }; const lmat = new THREE.MeshStandardMaterial({ color: '#ffffff', emissive: '#eaf6ff', emissiveIntensity: 2.2 });
caja(nev, 0.22, 0.02, 0.08, lmat, 0, FY - 0.04, -0.1);
const lin = new THREE.PointLight('#eef7ff', 2.5, 6, 1.3); lin.position.set(0, 1.2, 0.05); nev.add(lin);
const encendida = !roto || apaga;
const A0 = typeof o.apaga === 'number' ? o.apaga : 0.4; const fl = x => apaga ? (x < A0 ? 1 : x < A0 + 0.12 ? ((Math.sin(x * 160) > 0.2) ? 1 : 0.1) : 0) : (roto ? 0 : 1);
tick(lin, x => { const v = fl(x); lin.intensity = 5.5 * v; lmat.emissiveIntensity = 2.2 * v; }); lin.userData.tick(0);
const termoCv = document.createElement('canvas'); termoCv.width = 256; termoCv.height = 128; const termoTx = new THREE.CanvasTexture(termoCv); termoTx.colorSpace = THREE.SRGBColorSpace;
const TT = o.temp === undefined ? (roto ? 5 + Dm * 2.5 : 4) : o.temp; let tPrev = null;
const pintaT = v => { const r2 = Math.round(v); tPrev = r2; const c2 = termoCv.getContext('2d'); c2.fillStyle = '#0d1418'; c2.fillRect(0, 0, 256, 128); c2.font = '900 92px Archivo Black, Inter, sans-serif'; c2.textAlign = 'center'; c2.fillStyle = r2 > 7 ? '#ff5a3c' : r2 > 4 ? '#ffb53c' : '#5fe0ff'; c2.fillText(r2 + '°', 128, 100); termoTx.needsUpdate = true; };
const pantalla = new THREE.Mesh(new THREE.PlaneGeometry(0.16, 0.08), new THREE.MeshStandardMaterial({ map: termoTx, emissive: '#ffffff', emissiveMap: termoTx, emissiveIntensity: 1.1, roughness: 0.2 }));
tick(pantalla, x => pintaT(L2(TT, sm(x)))); pantalla.userData.tick(0);
const AB = o.puerta === undefined ? 1 : o.puerta;
const puerta = new THREE.Group(); puerta.position.set(-NW / 2, 0, ND / 2); nev.add(puerta);
const pa = new THREE.Group(); pa.position.x = NW / 2; puerta.add(pa);
caja(pa, NW, FY - 0.12, 0.06, esmalte, 0, 0.1 + (FY - 0.12) / 2, 0.03); caja(pa, NW - 0.08, FY - 0.2, 0.02, forro, 0, 0.1 + (FY - 0.12) / 2, -0.01);
caja(pa, 0.03, 0.5, 0.04, tirador, NW / 2 - 0.08, 0.95, 0.08);
const bal = (y) => { caja(pa, NW - 0.12, 0.012, 0.11, new THREE.MeshPhysicalMaterial({ color: '#eaf6ff', roughness: 0.1, transparent: true, opacity: 0.45, depthWrite: false }), 0, y, -0.08); caja(pa, NW - 0.12, 0.08, 0.008, new THREE.MeshPhysicalMaterial({ color: '#eaf6ff', roughness: 0.1, transparent: true, opacity: 0.4, depthWrite: false }), 0, y + 0.04, -0.135); };
bal(0.3); bal(0.65); bal(0.98);
const botella = (x, y, col, hb) => { const b = new THREE.Group(); b.add(h.malla(new THREE.CylinderGeometry(0.032, 0.032, hb, 18), new THREE.MeshPhysicalMaterial({ color: col, roughness: 0.08, transparent: true, opacity: 0.75 }), 0, hb / 2, 0)); b.add(h.malla(new THREE.CylinderGeometry(0.013, 0.03, 0.05, 14), new THREE.MeshPhysicalMaterial({ color: col, roughness: 0.08, transparent: true, opacity: 0.75 }), 0, hb + 0.025, 0)); b.add(h.malla(new THREE.CylinderGeometry(0.015, 0.015, 0.02, 12), lisa('#d33'), 0, hb + 0.06, 0)); b.position.set(x, y, -0.08); pa.add(b); };
botella(-0.22, 0.31, '#3d8a3a', 0.22); botella(-0.14, 0.31, '#a8d8f0', 0.24); botella(0.12, 0.66, '#e8a23a', 0.16);
const carton = (txt, col, x, y, z, p, al) => { const cv = document.createElement('canvas'); cv.width = 128; cv.height = 256; const c2 = cv.getContext('2d'); c2.fillStyle = '#ffffff'; c2.fillRect(0, 0, 128, 256); c2.fillStyle = col; c2.fillRect(0, 150, 128, 106); c2.beginPath(); c2.arc(64, 95, 34, 0, 7); c2.fill(); c2.fillStyle = '#ffffff'; c2.font = '900 30px Archivo Black, Inter, sans-serif'; c2.textAlign = 'center'; c2.fillText(txt, 64, 212);
  const tx = new THREE.CanvasTexture(cv); tx.colorSpace = THREE.SRGBColorSpace; const m = new THREE.MeshStandardMaterial({ map: tx, roughness: 0.5 }); m.defines = { PQ_LISO: 1 }; const q = new THREE.Group(); caja(q, 0.07, al || 0.2, 0.07, m, 0, (al || 0.2) / 2, 0); const t = h.malla(new THREE.CylinderGeometry(0.0, 0.05, 0.03, 4), lisa('#f4f4f4'), 0, (al || 0.2) + 0.015, 0); t.rotation.y = Math.PI / 4; q.add(t); q.position.set(x, y, z); p.add(q); return q; };
carton('LECHE', '#2f6fd0', 0.08, 0.31, -0.08, pa); carton('ZUMO', '#f08a1c', 0.18, 0.31, -0.08, pa, 0.17);
pon('jug_01', { alto: 0.16 }, -0.12, 0.99, -0.08, 0, pa);
const termoP = new THREE.Group(); termoP.position.set(0.0, FY + 0.18, 0.065); pa.add(termoP);
const pc = new THREE.Group(); pc.position.set(0, 0, 0); puerta.add(pc);
const pcI = new THREE.Group(); pcI.position.x = NW / 2; pc.add(pcI);
caja(pcI, NW, NH - FY - 0.04, 0.06, esmalte, 0, FY + 0.02 + (NH - FY - 0.04) / 2, 0.03); caja(pcI, 0.03, 0.25, 0.04, tirador, NW / 2 - 0.08, FY + 0.15, 0.08);
pantalla.position.set(-0.12, FY + 0.28, 0.062); pcI.add(pantalla); caja(pcI, 0.19, 0.11, 0.008, lisa('#cfd4d8', { metalness: 0.6, roughness: 0.3 }), -0.12, FY + 0.28, 0.058);
marca('termo', pcI, -0.12, FY + 0.28, 0.07);
const AB2 = o.congeladorAbierto === undefined ? AB : o.congeladorAbierto;
tick(puerta, x => { puerta.rotation.y = -L2(AB, sm(x)) * 1.95; pc.rotation.y = -L2(AB2, sm(x)) * 1.85; }); puerta.userData.tick(0);
const moho = (p, x, y, z, s, k0) => { const q = new THREE.Group(); q.position.set(x, y, z); p.add(q); const n = 34; const ms = [];
  const mm = ['#9db070', '#d9e2c4', '#6f8a4a', '#eef2e4', '#b8c79a'].map(cc => lisa(cc, { roughness: 1 }));
  for (let k = 0; k < n; k++) { const a = R(k0 + k * 3) * 6.283, rr = Math.sqrt(R(k0 + k * 7)) * s; const sp = h.malla(new THREE.SphereGeometry(s * (0.06 + R(k0 + k) * 0.1), 8, 6), mm[k % 5], Math.cos(a) * rr, R(k0 + k * 5) * s * 0.08, Math.sin(a) * rr); q.add(sp); ms.push(sp); }
  tick(q, x => { const d = L2(dias, sm(x)); const m0 = cl((d - 2) / 4.5); q.visible = m0 > 0.01; ms.forEach((sp, k) => { const v = Math.max(0.001, cl(m0 * 1.6 - (k / n) * 0.8)); sp.scale.set(v, v * 0.6, v); }); }); q.userData.tick(0); return q; };
const pudre = (m, col, k) => { const t = cl((Dm - 1.5) / 5) * (k || 0.7); if (t <= 0) return m; m.traverse(c => { if (c.isMesh) { c.material = c.material.clone(); c.material.color.lerp(new THREE.Color(col || '#6a6a3a'), t); } }); return m; };
const y1 = pisos[0] + 0.007, y2 = pisos[1] + 0.007, y3 = pisos[2] + 0.007, zf = 0.04;
const plato = (x, y, z, r2) => { const p = h.malla(new THREE.CylinderGeometry(r2, r2 * 0.85, 0.015, 32), lisa('#ffffff', { roughness: 0.2 }), x, y + 0.008, z); nev.add(p); };
plato(0.12, y3, zf, 0.13); pudre(pon('carrot_cake', { alto: 0.11 }, 0.12, y3 + 0.015, zf, 0.4, nev), '#5a5a30', 0.6); moho(nev, 0.12, y3 + 0.118, zf, 0.06, 11);
marca('tarta', nev, 0.12, y3 + 0.07, zf);
const queso = new THREE.Group(); { const qg = new THREE.CylinderGeometry(0.085, 0.085, 0.07, 32, 1, false, 0.5, Math.PI * 1.65); const qm = lisa('#ffcc3a', { roughness: 0.45, emissive: '#3a2a00', emissiveIntensity: 0.3 }); queso.add(h.malla(qg, qm, 0, 0.035, 0)); for (let k = 0; k < 6; k++) { const a = R(k + 500) * Math.PI * 0.5, rr = 0.03 + R(k + 501) * 0.05; const ag2 = h.malla(new THREE.CircleGeometry(0.008 + R(k + 502) * 0.008, 12), lisa('#c99a1e'), Math.sin(a) * rr, 0.0715, Math.cos(a) * rr); ag2.rotation.x = -Math.PI / 2; queso.add(ag2); } queso.position.set(-0.14, y3, zf + 0.02); queso.rotation.y = 0.9; [0, 1].forEach(k2 => { const cara = h.malla(new THREE.PlaneGeometry(0.085, 0.07), lisa('#ffd85a', { side: THREE.DoubleSide, roughness: 0.5 }), 0, 0.035, 0); cara.position.set(Math.sin(0.5 + k2 * Math.PI * 1.65) * 0.0425, 0.035, Math.cos(0.5 + k2 * Math.PI * 1.65) * 0.0425); cara.rotation.y = 0.5 + k2 * Math.PI * 1.65 - Math.PI / 2; queso.add(cara); }); nev.add(queso); pudre(queso, '#8a8a4a', 0.6); }
moho(nev, -0.14, y3 + 0.072, zf + 0.02, 0.05, 31); marca('queso', nev, -0.14, y3 + 0.05, zf + 0.02);
pon('jug_01', { alto: 0.17 }, -0.2, y2, -0.08, 0.5, nev); marca('leche', nev, -0.2, y2 + 0.09, -0.08);
const vetaTx = (() => { const cv = document.createElement('canvas'); cv.width = cv.height = 256; const c2 = cv.getContext('2d'); c2.fillStyle = '#8c1a22'; c2.fillRect(0, 0, 256, 256);
  for (let k = 0; k < 900; k++) { c2.fillStyle = `rgba(${150 + R(k) * 60 | 0},${20 + R(k + 1) * 30 | 0},${30 + R(k + 2) * 20 | 0},0.5)`; c2.fillRect(R(k + 3) * 256, R(k + 4) * 256, 3, 3); }
  c2.strokeStyle = 'rgba(245,225,215,0.85)'; for (let k = 0; k < 22; k++) { c2.lineWidth = 1 + R(k + 9) * 3; c2.beginPath(); let x = R(k + 5) * 256, y = R(k + 6) * 256; c2.moveTo(x, y); for (let j = 0; j < 6; j++) { x += (R(k * 7 + j) - 0.5) * 60; y += (R(k * 3 + j) - 0.5) * 60; c2.lineTo(x, y); } c2.stroke(); }
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; return t; })();
const carneM = new THREE.MeshStandardMaterial({ map: vetaTx, roughness: 0.5 }); carneM.defines = { PQ_LISO: 1 };
const carne = new THREE.Group(); caja(carne, 0.22, 0.02, 0.15, lisa('#1d1d1d', { roughness: 0.5 }), 0, 0.01, 0);
for (let k = 0; k < 2; k++) { const fm = h.malla(new THREE.SphereGeometry(0.05, 24, 14), carneM, -0.05 + k * 0.1, 0.03, 0); fm.scale.set(1.0, 0.22, 0.75); fm.rotation.y = k * 0.5; carne.add(fm);
  const gr = h.malla(new THREE.TorusGeometry(0.048, 0.006, 6, 20, 2.0), lisa('#f1e2d2', { roughness: 0.6 }), -0.05 + k * 0.1, 0.03, 0); gr.rotation.x = -Math.PI / 2; gr.scale.set(1.0, 0.75, 1); gr.rotation.z = 2.2 + k; carne.add(gr); }
caja(carne, 0.225, 0.045, 0.155, new THREE.MeshPhysicalMaterial({ color: '#ffffff', roughness: 0.05, transparent: true, opacity: 0.15, depthWrite: false }), 0, 0.03, 0);
{ const cv = document.createElement('canvas'); cv.width = 256; cv.height = 96; const c2 = cv.getContext('2d'); c2.fillStyle = '#fff'; c2.fillRect(0, 0, 256, 96); c2.fillStyle = '#c62828'; c2.font = '900 40px Archivo Black, Inter, sans-serif'; c2.textAlign = 'center'; c2.fillText('TERNERA', 128, 60); const tx = new THREE.CanvasTexture(cv); tx.colorSpace = THREE.SRGBColorSpace; const et = h.malla(new THREE.PlaneGeometry(0.09, 0.034), new THREE.MeshStandardMaterial({ map: tx, roughness: 0.6 }), 0.05, 0.054, 0.04); et.rotation.x = -Math.PI / 2; carne.add(et); }
carne.position.set(0.15, y2, zf + 0.05); nev.add(carne); pudre(carne, '#6a5a3a', 0.8); marca('carne', nev, 0.15, y2 + 0.04, zf + 0.05);
const huevos = new THREE.Group(); caja(huevos, 0.24, 0.035, 0.11, lisa('#c9b89a', { roughness: 1 }), 0, 0.017, 0); for (let k = 0; k < 6; k++) { const hv = h.malla(new THREE.SphereGeometry(0.022, 14, 10), lisa('#f3e6d2', { roughness: 0.6 }), -0.08 + (k % 3) * 0.08, 0.05, (k < 3 ? -0.025 : 0.025)); hv.scale.y = 1.3; huevos.add(hv); }
huevos.position.set(0.15, y1, -0.05); nev.add(huevos); marca('huevos', nev, 0.15, y1 + 0.05, -0.05);
carton('YOGUR', '#d6322f', -0.22, y1, -0.05, nev, 0.09); carton('NATA', '#3aa05a', -0.13, y1, -0.08, nev, 0.12);
pudre(pon('food_avocado_01', { alto: 0.08 }, -0.18, 0.15, 0.02, 0, nev), '#3a3a20', 0.8); pudre(pon('food_kiwi_01', { alto: 0.06 }, -0.05, 0.15, 0.05, 1, nev), '#4a4a2a'); pudre(pon('food_lime_01', { alto: 0.06 }, 0.07, 0.15, 0.0, 2, nev), '#6a6a2a');
pudre(pon('sweet_potato', { largo: 0.15 }, 0.18, 0.15, 0.06, 0.5, nev), '#4a3a2a'); pudre(pon('food_pomegranate_01', { alto: 0.08 }, 0.05, y2, -0.1, 0, nev), '#5a3a2a');
moho(nev, -0.18, 0.15 + 0.08, 0.02, 0.035, 51); moho(nev, 0.07, 0.15 + 0.06, 0.0, 0.03, 53); moho(nev, -0.05, 0.15 + 0.055, 0.05, 0.03, 55); moho(nev, 0.05, y2 + 0.08, -0.1, 0.03, 61);
marca('fruta', nev, 0.0, 0.2, 0.04); marca('verduras', nev, 0.0, 0.2, 0.04);
marca('interior', nev, 0, 0.75, 0.05); marca('nevera', nev, 0, 0.95, ND / 2);
const con = new THREE.Group(); con.position.y = FY + 0.03; nev.add(con);
const hielo = new THREE.MeshPhysicalMaterial({ color: '#cfeeff', roughness: 0.1, transparent: true, opacity: 0.75, emissive: '#8fd0ff', emissiveIntensity: 0.35, clearcoat: 1 }); hielo.defines = { PQ_LISO: 1 };
const escarcha = lisa('#f4fbff', { roughness: 0.9, emissive: '#dff0ff', emissiveIntensity: 0.35 });
const fundido = cl((Dm - 0.6) / 1.6) * (roto ? 1 : 0);
const bloques = []; for (let k = 0; k < 10; k++) { const b = caja(con, 0.035, 0.035, 0.035, hielo, -0.26 + (k % 5) * 0.045, 0.02, 0.12 + Math.floor(k / 5) * 0.045); b.rotation.y = R(k) * 0.6; bloques.push(b); }
const bolsa = (txt, col, x, z, w, hb) => { const cv = document.createElement('canvas'); cv.width = 256; cv.height = 160; const c2 = cv.getContext('2d'); c2.fillStyle = col; c2.fillRect(0, 0, 256, 160); c2.fillStyle = '#fff'; c2.font = '900 34px Archivo Black, Inter, sans-serif'; c2.textAlign = 'center'; c2.fillText(txt, 128, 92); const tx = new THREE.CanvasTexture(cv); tx.colorSpace = THREE.SRGBColorSpace; const m = new THREE.MeshStandardMaterial({ map: tx, roughness: 0.35 }); m.defines = { PQ_LISO: 1 }; const b = caja(con, w, hb, 0.1, m, x, hb / 2, z); return b; };
const bg1 = bolsa('GUISANTES', '#2e8b3e', 0.12, -0.05, 0.24, 0.12); const bg2 = bolsa('HELADO', '#7a3fc0', -0.16, -0.1, 0.2, 0.1); bg2.position.y = 0.05;
const pizza = bolsa('PIZZA', '#d9472b', 0.05, -0.18, 0.4, 0.03); pizza.position.y = 0.135;
const capa = caja(con, NW - 0.1, 0.03, ND - 0.12, escarcha, 0, 0.43, -0.02);
const escM = lisa('#f2f9ff', { roughness: 1, transparent: true, opacity: 0.85, emissive: '#cfe6ff', emissiveIntensity: 0.5 }); const esc2 = []; for (let k = 0; k < 0; k++) { const sp = h.malla(new THREE.SphereGeometry(0.012 + R(k + 300) * 0.02, 8, 6), escM, (R(k + 200) - 0.5) * (NW - 0.14), 0.41, (R(k + 250) - 0.5) * (ND - 0.16)); sp.scale.y = 0.4; con.add(sp); esc2.push(sp); }
const aguaC = h.malla(new THREE.PlaneGeometry(NW - 0.1, ND - 0.12), new THREE.MeshPhysicalMaterial({ color: '#a8d4ea', roughness: 0.02, metalness: 0.3, transparent: true, opacity: 0.7, clearcoat: 1 }), 0, 0.004, -0.02); aguaC.rotation.x = -Math.PI / 2; con.add(aguaC);
const gC = []; for (let k = 0; k < 4; k++) { const gd = h.malla(new THREE.SphereGeometry(0.008, 8, 6), aguaC.material, -0.25 + k * 0.15, -0.02, ND / 2 - 0.08); gd.scale.y = 1.7; con.add(gd); gC.push(gd); }
tick(con, x => { const d = L2(dias, sm(x)); const f = roto ? cl((d - 0.6) / 1.6) : 0; bloques.forEach((b, k) => { const s2 = Math.max(0.05, 1 - f * (0.8 + R(k) * 0.3)); b.scale.set(s2, s2 * 0.8, s2); b.position.y = 0.0175 * s2; }); capa.scale.y = Math.max(0.05, 1 - f); capa.visible = f < 0.95; esc2.forEach((sp, k) => { const v = Math.max(0.001, 1 - f * (1 + R(k))); sp.scale.set(v, v * 0.4, v); });
  aguaC.visible = f > 0.05; aguaC.material.opacity = 0.25 + f * 0.5; gC.forEach((gd, k) => { gd.visible = f > 0.2 && f < 1.2; const ph = (x * 2.5 + R(k + 9)) % 1; gd.position.y = -0.01 - ph * 0.25; }); }); con.userData.tick(0);
marca('congelador', nev, 0, FY + 0.2, 0.05); marca('hielo', nev, -0.1, FY + 0.06, 0);
const charcoN = cl((Dm - 1.2) / 2.5) * (roto ? 1 : 0);
const agua = new THREE.MeshPhysicalMaterial({ color: '#8cc4ea', roughness: 0.02, metalness: 0.3, transparent: true, opacity: 0.8, clearcoat: 1, emissive: '#3a7ab0', emissiveIntensity: 0.35 }); agua.defines = { PQ_LISO: 1 };
const charco = h.malla(new THREE.CircleGeometry(0.5, 40), agua, NX + 0.25, 0.004, NZ + ND / 2 + 0.35); charco.rotation.x = -Math.PI / 2; g.add(charco);
tick(charco, x => { const d = L2(dias, sm(x)); const c2 = roto ? cl((d - 1.2) / 2.5) : 0; charco.visible = c2 > 0.01; charco.scale.set(0.3 + c2 * 1.4, 0.2 + c2 * 1.0, 1); }); charco.userData.tick(0);
marca('charco', g, NX + 0.25, 0.05, NZ + ND / 2 + 0.35);
const gotas = []; for (let k = 0; k < 5; k++) { const gd = h.malla(new THREE.SphereGeometry(0.012, 10, 8), agua, NX - 0.15 + k * 0.08, 0.1, NZ + ND / 2 + 0.02); gd.scale.y = 1.6; g.add(gd); gotas.push(gd); }
tick(gotas[0], x => { const d = L2(dias, sm(x)); const on = roto && d > 0.8 && d < 6; gotas.forEach((gd, k) => { gd.visible = on; const ph = ((x * 3 + R(k) ) % 1); gd.position.y = 0.12 - ph * 0.12; }); }); gotas[0].userData.tick(0);
const olor = new THREE.Group(); g.add(olor); const cintas = [];
for (let k = 0; k < 5; k++) { const pts = []; for (let j = 0; j < 12; j++) pts.push(new THREE.Vector3(Math.sin(j * 0.9 + k) * 0.06, j * 0.07, 0)); const cu = new THREE.CatmullRomCurve3(pts);
  const cm = new THREE.MeshBasicMaterial({ color: '#a8c45a', transparent: true, opacity: 0.0, depthWrite: false }); const ci = new THREE.Mesh(new THREE.TubeGeometry(cu, 40, 0.012, 6), cm); ci.position.set(NX - 0.25 + k * 0.12, 0.9 + R(k) * 0.3, NZ + ND / 2 + 0.25); olor.add(ci); cintas.push(ci); }
tick(olor, x => { const d = L2(dias, sm(x)); const v = roto ? cl((d - 4.5) / 2) : 0; cintas.forEach((ci, k) => { const ph = (x * 0.8 + k * 0.2) % 1; ci.position.y = 0.85 + ph * 0.6; ci.material.opacity = v * 0.6 * Math.sin(ph * Math.PI); ci.visible = ci.material.opacity > 0.01; ci.rotation.y = x * 2 + k; }); }); olor.userData.tick(0);
marca('olor', g, NX, 1.2, NZ + ND / 2 + 0.3);
const moscas = new THREE.Group(); g.add(moscas); const ms2 = [];
for (let k = 0; k < 4; k++) { const mo = new THREE.Group(); mo.add(h.malla(new THREE.SphereGeometry(0.008, 8, 6), lisa('#111'), 0, 0, 0)); [-1, 1].forEach(s => { const al = h.malla(new THREE.CircleGeometry(0.01, 10), new THREE.MeshBasicMaterial({ color: '#cfd8e0', transparent: true, opacity: 0.6, side: THREE.DoubleSide }), s * 0.008, 0.005, 0); al.rotation.x = -1.2; mo.add(al); }); moscas.add(mo); ms2.push(mo); }
tick(moscas, x => { const d = L2(dias, sm(x)); moscas.visible = roto && d >= 5.5; ms2.forEach((mo, k) => { const a = x * 9 + k * 1.6; mo.position.set(NX + Math.sin(a) * 0.25, 1.0 + Math.sin(a * 1.7) * 0.15 + k * 0.06, NZ + ND / 2 + 0.2 + Math.cos(a) * 0.2); }); }); moscas.userData.tick(0);

const ledM = new THREE.MeshStandardMaterial({ color: '#fff1d0', emissive: '#ffc874', emissiveIntensity: 3.5 }); caja(g, 1.85, 0.015, 0.03, ledM, 0.38, 1.59, -F / 2 + 0.33);
g.add((() => { const l = new THREE.PointLight('#ffc874', 7, 7, 1.4); l.position.set(0.4, 1.5, -F / 2 + 0.5); return l; })());
const lamp = new THREE.Group(); lamp.position.set(0.9, AL, 0.2); g.add(lamp); lamp.add(h.malla(new THREE.CylinderGeometry(0.004, 0.004, 0.7, 4), lisa('#111'), 0, -0.35, 0));
lamp.add(h.malla(new THREE.ConeGeometry(0.22, 0.2, 24, 1, true), lisa('#1d2a33', { side: THREE.DoubleSide }), 0, -0.78, 0)); lamp.add(h.malla(new THREE.SphereGeometry(0.06, 12, 10), new THREE.MeshStandardMaterial({ color: '#fff', emissive: '#ffd28a', emissiveIntensity: 3 }), 0, -0.86, 0));
lamp.add((() => { const l = new THREE.PointLight('#ffd28a', 14, 12, 1.3); l.position.set(0, -0.9, 0); return l; })());
const conoM = new THREE.MeshBasicMaterial({ color: '#cfe8ff', transparent: true, opacity: 0.16, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide });
const cono = h.malla(new THREE.CylinderGeometry(0.35, 0.75, 1.5, 24, 1, true), conoM, NX, 0.75, NZ + ND / 2 + 0.45); cono.rotation.x = 0.45; g.add(cono);
const charcoLuz = h.malla(new THREE.CircleGeometry(0.6, 32), new THREE.MeshBasicMaterial({ color: '#bfe2ff', transparent: true, opacity: 0.18, depthWrite: false, blending: THREE.AdditiveBlending }), NX, 0.006, NZ + ND / 2 + 0.6); charcoLuz.rotation.x = -Math.PI / 2; charcoLuz.scale.set(1.1, 0.8, 1); g.add(charcoLuz);
tick(cono, x => { const v = fl(x) * L2(AB, sm(x)); conoM.opacity = 0.16 * v; charcoLuz.material.opacity = 0.18 * v; cono.visible = v > 0.02; charcoLuz.visible = v > 0.02; }); cono.userData.tick(0);
if (o.persona) { const pp = new THREE.Group(); const piel = lisa('#e0b48c'), pij = lisa('#4a6fa8', { roughness: 0.8 }), pij2 = lisa('#3a5a8c', { roughness: 0.8 }), pelo = lisa('#2a1c14', { roughness: 0.8 });
  [-1, 1].forEach(s2 => { pp.add(h.malla(new THREE.CapsuleGeometry(0.065, 0.62, 4, 10), pij2, s2 * 0.09, 0.42, 0)); pp.add(h.malla(new THREE.CapsuleGeometry(0.045, 0.5, 4, 10), pij, s2 * 0.25, 1.15, 0.02)); pp.add(h.malla(new THREE.SphereGeometry(0.05, 10, 8), piel, s2 * 0.25, 0.86, 0.04)); pp.add(h.malla(new THREE.BoxGeometry(0.1, 0.05, 0.22), lisa('#e8e2d6'), s2 * 0.09, 0.03, 0.04)); });
  const tor = h.malla(new THREE.CapsuleGeometry(0.19, 0.48, 6, 14), pij, 0, 1.14, 0); tor.scale.z = 0.65; pp.add(tor); pp.add(h.malla(new THREE.CylinderGeometry(0.05, 0.06, 0.1, 10), piel, 0, 1.55, 0));
  pp.add(h.malla(new THREE.SphereGeometry(0.12, 18, 14), piel, 0, 1.7, 0)); const pl = h.malla(new THREE.SphereGeometry(0.125, 18, 14, 0, 6.283, 0, 1.7), pelo, 0, 1.72, -0.01); pp.add(pl);
  pp.position.set(NX + 0.45, 0, NZ + ND / 2 + 0.55); pp.rotation.y = -Math.PI * 0.72; g.add(pp); marca('persona', g, NX + 0.25, 1.4, NZ + ND / 2 + 0.75); }
const comp = new THREE.Group(); comp.position.set(0, 0, -ND / 2 - 0.02); nev.add(comp); comp.add((() => { const l = new THREE.PointLight('#ffb070', 6, 5, 1.4); l.position.set(0.3, 0.6, -0.5); return l; })());
const negro = lisa('#1d1f22', { metalness: 0.4, roughness: 0.4 }), cobre = lisa('#c27a45', { metalness: 0.9, roughness: 0.3 });
const domo = h.malla(new THREE.SphereGeometry(0.11, 24, 16), negro, 0.15, 0.17, -0.1); domo.scale.y = 0.8; comp.add(domo); comp.add(h.malla(new THREE.CylinderGeometry(0.11, 0.11, 0.08, 24), negro, 0.15, 0.11, -0.1));
caja(comp, 0.05, 0.04, 0.04, lisa('#333'), 0.27, 0.15, -0.1);
const led = h.malla(new THREE.SphereGeometry(0.012, 10, 8), new THREE.MeshStandardMaterial({ color: '#3cff6a', emissive: '#3cff6a', emissiveIntensity: 3 }), 0.27, 0.19, -0.075); comp.add(led);
for (let k = 0; k < 9; k++) { const y = 0.35 + k * 0.14; const tb = h.malla(new THREE.CylinderGeometry(0.006, 0.006, NW - 0.12, 8), negro, 0, y, -0.04); tb.rotation.z = Math.PI / 2; comp.add(tb); if (k < 8) { const cv = h.malla(new THREE.TorusGeometry(0.07, 0.006, 6, 12, Math.PI), negro, (k % 2 ? -1 : 1) * (NW / 2 - 0.06), y + 0.07, -0.04); cv.rotation.z = (k % 2 ? 1 : -1) * Math.PI / 2; comp.add(cv); } }
for (let k = 0; k < 14; k++) caja(comp, 0.004, 1.2, 0.004, negro, -NW / 2 + 0.08 + k * 0.045, 0.95, -0.04);
const tubo = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([new THREE.Vector3(0.15, 0.25, -0.1), new THREE.Vector3(0.05, 0.32, -0.08), new THREE.Vector3(-0.2, 0.3, -0.05), new THREE.Vector3(-0.3, 0.35, -0.04)]), 30, 0.008, 8), cobre); comp.add(tubo);
const vent2 = new THREE.Group(); vent2.position.set(-0.15, 0.15, -0.1); comp.add(vent2); for (let k = 0; k < 5; k++) { const as = caja(vent2, 0.02, 0.1, 0.005, lisa('#444'), 0, 0.05, 0); as.rotation.z = k / 5 * Math.PI * 2; as.position.set(Math.sin(k / 5 * Math.PI * 2) * 0.05, Math.cos(k / 5 * Math.PI * 2) * 0.05, 0); }
const para = !!o.parar, P0 = typeof o.parar === 'number' ? o.parar : 0.45;
tick(comp, x => { const on = para ? x < P0 : !roto; const giro = para ? (x < P0 ? x * 40 : P0 * 40 + (1 - Math.exp(-(x - P0) * 6)) * 6) : (on ? x * 40 : 0); vent2.rotation.z = giro; domo.position.x = 0.15 + (on ? Math.sin(x * 400) * 0.0015 : 0); led.material.emissiveIntensity = on ? 3 : 0; led.material.color.set(on ? '#3cff6a' : '#3a1010'); }); comp.userData.tick(0);
marca('compresor', nev, 0.05, 0.2, -ND / 2 - 0.1);
marca('cocina', g, 0, 1.2, 0);
return g;
"""

COCINA = ILU
