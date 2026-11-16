# Piezas del 17-nov: UN objeto por vídeo, con «vistas» (o.vista) para acercarse a cada parte

ASCENSOR = r"""
const marca = (nom, obj, x, y, z) => { const m = new THREE.Object3D(); m.name = 'p_' + nom; m.position.set(x, y, z); obj.add(m); };
const g = new THREE.Group(), v = o.vista || 'todo', sin = !!o.sinCables, frena = !!o.frena;
const hormigon = h.M('#6b6f78', { roughness: 0.9 }), acero = h.M('#aeb5bf', { metalness: 0.7, roughness: 0.3 }), oscuro = h.M('#2a2d33', { roughness: 0.6 });
const naranja = new THREE.MeshStandardMaterial({ color: '#ff8a1a', emissive: '#ff6a00', emissiveIntensity: 0.6 });
const HP = 3.4, pisos = 6, W = 3.2, alto = pisos * HP;
g.add((() => { const l = new THREE.PointLight('#ffe2b8', 12, 14, 1.5); l.position.set(0, 3, 5); return l; })());
const cabY = o.altura !== undefined ? o.altura : 3.2 * HP;
// hueco del ascensor en corte: paredes, forjados de cada planta con su puerta, guías y cables
const hueco = () => { const q = new THREE.Group();
  h.caja(q, W + 2.6, alto + 4, 0.4, hormigon, 0, alto / 2, -1.9);
  [-1, 1].forEach(s => h.caja(q, 0.4, alto + 4, 4, hormigon, s * (W / 2 + 1.1), alto / 2, 0));
  for (let p = 0; p <= pisos; p++) { const y = p * HP; [-1, 1].forEach(s => h.caja(q, 1.6, 0.35, 4, hormigon, s * (W / 2 + 2.0), y, 0));
    const cv = document.createElement('canvas'); cv.width = 64; cv.height = 64; const x = cv.getContext('2d'); x.fillStyle = '#1c1f24'; x.fillRect(0, 0, 64, 64); x.fillStyle = '#ffcf5a'; x.font = '900 44px Mont, Inter, sans-serif'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText(String(p), 32, 34);
    const tx = new THREE.CanvasTexture(cv); tx.colorSpace = THREE.SRGBColorSpace; h.caja(q, 0.5, 0.5, 0.05, new THREE.MeshStandardMaterial({ map: tx, emissive: '#ffffff', emissiveMap: tx, emissiveIntensity: 0.6 }), -W / 2 - 0.4, y + 2.5, -1.66); }
  [-1, 1].forEach(s => { h.caja(q, 0.18, alto + 3, 0.18, acero, s * (W / 2 + 0.25), alto / 2, 0); for (let p = 0; p < pisos * 2; p++) h.caja(q, 0.5, 0.08, 0.4, oscuro, s * (W / 2 + 0.5), p * HP / 2 + 0.6, 0); });
  // contrapeso por detrás
  const cp = new THREE.Group(); for (let k = 0; k < 10; k++) h.caja(cp, 1.4, 0.22, 0.5, h.M(k % 2 ? '#5a5f68' : '#4a4f58', { metalness: 0.4, roughness: 0.5 }), 0, k * 0.24, 0); h.caja(cp, 1.6, 2.6, 0.12, acero, 0, 1.1, 0.3); cp.position.set(0.9, alto - cabY - 1, -1.3); q.add(cp);
  // pisos del edificio a ambos lados (en corte): habitaciones iluminadas con muebles
  const pared = ['#e9d8b8', '#cfe0d4', '#e8c8c0', '#d8d4ea'];
  for (let p = 0; p < pisos; p++) [-1, 1].forEach(s => { const x0 = s * (W / 2 + 1.3 + 3.2), y = p * HP;
    h.caja(q, 6.4, HP - 0.35, 0.2, h.M(pared[(p + (s > 0 ? 1 : 0)) % 4], { roughness: 0.8 }), x0, y + HP / 2 + 0.17, -1.8);
    h.caja(q, 6.4, 0.08, 3.6, h.M('#a8805a', { roughness: 0.7 }), x0, y + 0.2, 0);
    const lam = h.malla(new THREE.ConeGeometry(0.35, 0.3, 16, 1, true), new THREE.MeshStandardMaterial({ color: '#fff2d0', emissive: '#ffcf7a', emissiveIntensity: 1.2, side: THREE.DoubleSide }), x0, y + HP - 0.6, -0.3); q.add(lam); q.add(h.en(h.brillo('#ffcf7a', 2.4, 0.45), x0, y + HP - 0.8, -0.3));
    const mueble = Math.floor(r() * 3); if (mueble === 0) { h.caja(q, 2.2, 0.8, 1, h.M('#5a7aa8'), x0 - s * 0.8, y + 0.6, -1.0); h.caja(q, 2.2, 0.8, 0.3, h.M('#4a6a98'), x0 - s * 0.8, y + 1.1, -1.4); }
    else if (mueble === 1) { h.caja(q, 1.4, 0.08, 0.9, h.M('#8a5a3a'), x0, y + 1.0, -0.6); [-0.6, 0.6].forEach(dx => h.caja(q, 0.08, 0.8, 0.08, h.M('#6a4a2a'), x0 + dx, y + 0.6, -0.6)); }
    else { h.caja(q, 1.0, 2.0, 0.5, h.M('#c9a26a'), x0 + s * 1.5, y + 1.2, -1.5); }
    if (r() < 0.5) { const pr = new THREE.Group(); pr.add(h.malla(new THREE.CapsuleGeometry(0.18, 0.5, 4, 8), h.M(['#2fb38a', '#f2c94c', '#8a5ad8'][p % 3]), 0, 0.85, 0)); pr.add(h.malla(new THREE.SphereGeometry(0.16, 12, 8), h.M('#e8b896'), 0, 1.4, 0)); pr.position.set(x0 + s * 0.8, y + 0.2, 0.3); q.add(pr); } });
  marca('hueco', q, 0, alto / 2, 0);
  const lz = new THREE.PointLight('#ffd9a0', 30, 30, 1.6); lz.position.set(0, alto * 0.6, 6); q.add(lz);
  return q; };
const cabina = () => { const c2 = new THREE.Group(), madera = h.M('#9a6a44', { roughness: 0.6 }), espejo = h.M('#cfe0ee', { metalness: 0.6, roughness: 0.05 });
  h.caja(c2, W, 0.2, 2.6, acero, 0, 0, 0); h.caja(c2, W, 0.2, 2.6, acero, 0, 2.6, 0); h.caja(c2, W, 2.6, 0.08, espejo, 0, 1.3, -1.25);
  [-1, 1].forEach(s => h.caja(c2, 0.08, 2.6, 2.6, madera, s * W / 2, 1.3, 0)); h.caja(c2, W - 0.2, 0.06, 0.06, acero, 0, 1.0, -1.15);
  c2.add(h.en(h.brillo('#fff2c4', 2.5, 0.6), 0, 2.4, 0)); h.caja(c2, 1.4, 0.05, 1.0, new THREE.MeshStandardMaterial({ color: '#fff6dc', emissive: '#fff2c4', emissiveIntensity: 1.2 }), 0, 2.48, 0);
  // panel de botones
  const pan = new THREE.Group(); h.caja(pan, 0.4, 1.2, 0.05, acero, 0, 0, 0); for (let k = 0; k < 7; k++) pan.add(h.malla(new THREE.CylinderGeometry(0.06, 0.06, 0.04, 12), k === 3 ? naranja : h.M('#e8e8ea'), 0, -0.45 + k * 0.15, 0.04)).children; pan.children.forEach(m => { if (m.geometry.type === 'CylinderGeometry') m.rotation.x = Math.PI / 2; });
  pan.position.set(W / 2 - 0.1, 1.4, 0.4); pan.rotation.y = -Math.PI / 2; c2.add(pan);
  // dos personas dentro (figuras con ropa, brazos, manos, pelo y cara)
  const persona = (ropa, piel, pelo, pant, x, giro) => { const p = new THREE.Group(), mR = h.M(ropa, { roughness: 0.7 }), mP = h.M(piel, { roughness: 0.6 });
    const tor = h.malla(new THREE.CylinderGeometry(0.2, 0.25, 0.75, 16), mR, 0, 1.25, 0); p.add(tor); p.add(h.malla(new THREE.SphereGeometry(0.2, 16, 10, 0, 6.3, 0, 1.6), mR, 0, 1.6, 0));
    [-0.11, 0.11].forEach(px => { p.add(h.malla(new THREE.CylinderGeometry(0.09, 0.08, 0.85, 10), h.M(pant), px, 0.45, 0)); const z = h.malla(new THREE.BoxGeometry(0.14, 0.08, 0.26), h.M('#2b2b30'), px, 0.04, 0.05); p.add(z); });
    [-1, 1].forEach(sd => { const br = h.malla(new THREE.CylinderGeometry(0.065, 0.055, 0.7, 10), mR, sd * 0.28, 1.2, 0); br.rotation.z = sd * 0.12; p.add(br); p.add(h.malla(new THREE.SphereGeometry(0.06, 10, 8), mP, sd * 0.32, 0.83, 0.02)); });
    p.add(h.malla(new THREE.CylinderGeometry(0.07, 0.07, 0.12, 10), mP, 0, 1.73, 0));
    const cab = h.malla(new THREE.SphereGeometry(0.18, 20, 14), mP, 0, 1.92, 0); cab.scale.set(0.95, 1.1, 1); p.add(cab);
    const pe = h.malla(new THREE.SphereGeometry(0.19, 20, 14, 0, 6.3, 0, 1.3), h.M(pelo, { roughness: 0.8 }), 0, 1.97, -0.02); pe.scale.set(1, 1.05, 1.05); p.add(pe);
    [-0.06, 0.06].forEach(ex => p.add(h.malla(new THREE.SphereGeometry(0.022, 8, 6), h.M('#1a1410'), ex, 1.94, 0.165)));
    p.add(h.malla(new THREE.BoxGeometry(0.07, 0.015, 0.01), h.M('#8a4a3a'), 0, 1.84, 0.172));
    p.position.set(x, 0.1, 0.1); p.rotation.y = giro; return p; };
  c2.add(persona('#2f6fd8', '#e8b896', '#3a2a1a', '#2b3a5a', -0.6, 0.25)); c2.add(persona('#d8323a', '#c98a5a', '#141414', '#3a3a40', 0.6, -0.25));
  // bastidor y paracaídas (freno de emergencia) en los laterales, abrazando las guías
  [-1, 1].forEach(s => { h.caja(c2, 0.2, 3.4, 0.3, h.M('#c9a226', { metalness: 0.5, roughness: 0.35 }), s * (W / 2 + 0.05), 1.3, 0);
    const pc = new THREE.Group(), rojo = h.M('#c8282c', { metalness: 0.35, roughness: 0.4 }), cromo = h.M('#e8ecf0', { metalness: 0.9, roughness: 0.15 }), torn = h.M('#9aa0a8', { metalness: 0.8, roughness: 0.3 });
    [-1, 1].forEach(t => { h.caja(pc, 0.12, 0.7, 0.5, rojo, t * 0.18, 0, 0); for (let b = 0; b < 3; b++) h.caja(pc, 0.03, 0.62, 0.04, h.M('#a81e22'), t * 0.25, 0, -0.18 + b * 0.18);
      for (let b = 0; b < 4; b++) { const tt = h.malla(new THREE.CylinderGeometry(0.035, 0.035, 0.04, 6), torn, t * 0.25, -0.25 + (b % 2) * 0.5, -0.15 + Math.floor(b / 2) * 0.3); tt.rotation.z = Math.PI / 2; pc.add(tt); } });
    h.caja(pc, 0.48, 0.12, 0.5, rojo, 0, 0.38, 0); h.caja(pc, 0.48, 0.1, 0.5, rojo, 0, -0.38, 0);
    [-1, 1].forEach(t => { const cu = new THREE.Group(); h.caja(cu, 0.06, 0.42, 0.34, cromo, 0, 0, 0); for (let d = 0; d < 7; d++) h.caja(cu, 0.03, 0.03, 0.34, h.M('#5a5f68'), -t * 0.04, -0.18 + d * 0.06, 0);
      cu.position.set(t * (frena ? 0.065 : 0.1), frena ? 0.08 : 0, 0); cu.rotation.z = t * (frena ? 0.0 : 0.08); pc.add(cu); });
    pc.add(h.malla(new THREE.CylinderGeometry(0.025, 0.025, 0.8, 8), torn, 0, 0.8, 0.2)); for (let k = 0; k < 8; k++) { const mu = h.malla(new THREE.TorusGeometry(0.06, 0.012, 6, 14), cromo, 0, 0.5 + k * 0.05, 0.2); mu.rotation.x = Math.PI / 2; pc.add(mu); }
    const cvf = document.createElement('canvas'); cvf.width = 128; cvf.height = 48; const xf = cvf.getContext('2d'); xf.fillStyle = '#f2c94c'; xf.fillRect(0, 0, 128, 48); xf.fillStyle = '#111'; xf.font = '900 20px Mont, Inter, sans-serif'; xf.textAlign = 'center'; xf.textBaseline = 'middle'; xf.fillText('PARACAÍDAS', 64, 25);
    const txf = new THREE.CanvasTexture(cvf); txf.colorSpace = THREE.SRGBColorSpace; h.caja(pc, 0.3, 0.11, 0.01, new THREE.MeshStandardMaterial({ map: txf }), 0.18 * s, 0.1, 0.26);
    if (frena) { for (let k = 0; k < 16; k++) { const ch = h.malla(new THREE.BoxGeometry(0.012, 0.08 + r() * 0.12, 0.012), new THREE.MeshStandardMaterial({ color: '#ffd27a', emissive: '#ffa020', emissiveIntensity: 3 }), (r() - 0.5) * 0.25, -0.45 - r() * 0.6, (r() - 0.5) * 0.4); ch.rotation.z = (r() - 0.5) * 1.2; pc.add(ch); }
      pc.add(h.en(h.brillo('#ffb347', 1.0, 0.9), 0, -0.4, 0)); pc.add(h.en(h.brillo('#ff7a1a', 1.8, 0.5), 0, -0.6, 0)); }
    pc.position.set(s * (W / 2 + 0.25), -0.2, 0); c2.add(pc); });
  marca('cabina', c2, 0, 1.3, 0); marca('freno', c2, W / 2 + 0.25, -0.2, 0); marca('frenoI', c2, -(W / 2 + 0.25), -0.2, 0);
  return c2; };
const cables = (largo) => { const q = new THREE.Group(); for (let k = 0; k < 6; k++) { if (sin) { const ps = []; for (let j = 0; j <= 8; j++) ps.push(new THREE.Vector3(-0.5 + k * 0.2 + Math.sin(j * 1.3 + k) * 0.5, largo * 0.4 - j * 0.35, Math.cos(j + k) * 0.2)); q.add(h.malla(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(ps), 30, 0.045, 6), h.M('#3a3a3a', { metalness: 0.6, roughness: 0.4 }))); }
  else q.add(h.malla(new THREE.CylinderGeometry(0.045, 0.045, largo, 8), h.M('#4a4a4a', { metalness: 0.7, roughness: 0.35 }), -0.5 + k * 0.2, largo / 2, 0)); } marca('cables', q, 0, sin ? 0 : largo / 2, 0); return q; };
const maquina = () => { const q = new THREE.Group(), azulM = h.M('#2a5fb8', { metalness: 0.45, roughness: 0.35 }), cromo = h.M('#dfe4ea', { metalness: 0.85, roughness: 0.2 }), negroM = h.M('#22252b', { metalness: 0.5, roughness: 0.4 });
  h.caja(q, W + 2.6, 0.4, 4, hormigon, 0, 0, 0); h.caja(q, 4.2, 0.3, 2.2, h.M('#e2c23a', { metalness: 0.3 }), 0.4, 0.35, 0);
  const pol = new THREE.Group(); const disco = h.malla(new THREE.CylinderGeometry(1.0, 1.0, 1.4, 48), cromo); disco.rotation.x = Math.PI / 2; pol.add(disco);
  for (let k = 0; k < 6; k++) pol.add(h.malla(new THREE.TorusGeometry(0.98, 0.07, 8, 48), h.M('#3a3a3a', { metalness: 0.6, roughness: 0.35 }), 0, 0, -0.55 + k * 0.22));
  [-1, 1].forEach(t => { const tapa = h.malla(new THREE.CylinderGeometry(1.08, 1.08, 0.08, 48), negroM, 0, 0, t * 0.74); tapa.rotation.x = Math.PI / 2; pol.add(tapa); for (let k = 0; k < 8; k++) { const b = h.malla(new THREE.CylinderGeometry(0.05, 0.05, 0.06, 8), cromo, Math.cos(k * 0.785) * 0.7, Math.sin(k * 0.785) * 0.7, t * 0.8); b.rotation.x = Math.PI / 2; pol.add(b); } });
  pol.position.set(0, 1.5, 0); q.add(pol);
  const mot = new THREE.Group(); const cu = h.malla(new THREE.CylinderGeometry(0.75, 0.75, 1.8, 32), azulM); cu.rotation.z = Math.PI / 2; mot.add(cu);
  for (let k = 0; k < 16; k++) { const al = h.malla(new THREE.BoxGeometry(1.6, 0.06, 0.16), h.M('#1f4fb8', { metalness: 0.45 }), 0, Math.cos(k / 16 * 6.28) * 0.78, Math.sin(k / 16 * 6.28) * 0.78); al.rotation.x = k / 16 * 6.28; mot.add(al); }
  const tam2 = h.malla(new THREE.CylinderGeometry(0.6, 0.6, 0.4, 32), cromo, -1.15, 0, 0); tam2.rotation.z = Math.PI / 2; mot.add(tam2);
  [-1, 1].forEach(t => mot.add(h.malla(new THREE.BoxGeometry(0.3, 0.2, 0.9), h.M('#c8282c'), -1.15, t * 0.68, 0)));
  const cvm = document.createElement('canvas'); cvm.width = 128; cvm.height = 64; const xm = cvm.getContext('2d'); xm.fillStyle = '#d9dde3'; xm.fillRect(0, 0, 128, 64); xm.fillStyle = '#111'; xm.font = '700 13px Inter, sans-serif'; ['MOTOR TRACCIÓN', '11 kW · 400 V', 'Nº 2026-PQ'].forEach((l, k) => xm.fillText(l, 8, 18 + k * 18));
  const txm = new THREE.CanvasTexture(cvm); txm.colorSpace = THREE.SRGBColorSpace; h.caja(mot, 0.5, 0.25, 0.01, new THREE.MeshStandardMaterial({ map: txm }), 0.3, 0.2, 0.79);
  mot.position.set(1.9, 1.5, 0); q.add(mot);
  h.caja(q, 1.0, 1.8, 0.8, h.M('#5a5f68', { metalness: 0.3 }), -2.0, 1.1, -0.6); for (let k = 0; k < 4; k++) q.add(h.malla(new THREE.SphereGeometry(0.05, 8, 6), new THREE.MeshStandardMaterial({ color: ['#2fe08a', '#ffb347', '#2fe08a', '#ff3a2a'][k], emissive: ['#2fe08a', '#ffb347', '#2fe08a', '#ff3a2a'][k], emissiveIntensity: 2 }), -2.3 + k * 0.2, 1.7, -0.19));
  q.add(h.en(h.brillo('#fff2c4', 3, 0.4), 0, 3.2, 0.5));
  marca('motor', q, 0, 1.4, 0); return q; };
if (v === 'todo' || v === 'caida') { g.add(hueco()); const cb = cabina(); cb.position.y = cabY; g.add(cb);
  const cb2 = cables(sin ? 3 : alto - cabY + 0.8); cb2.position.y = sin ? cabY + 3 : cabY + 2.7; g.add(cb2); const mq = maquina(); mq.position.y = alto + 1.2; mq.scale.setScalar(0.8); g.add(mq); }
else if (v === 'cables') { const mq = maquina(); g.add(mq); h.caja(g, W + 3, 0.2, 5, hormigon, 0, 4.5, 0); h.caja(g, W + 3, 5, 0.3, hormigon, 0, 2.2, -2.2); g.add(h.en(h.brillo('#fff2c4', 3, 0.5), 0, 4.2, 0)); const cb2 = cables(sin ? 3 : 6); cb2.position.set(0, sin ? -2.5 : -6, 0.8); g.add(cb2); }
else if (v === 'freno') { const cb = cabina(); g.add(cb); [-1, 1].forEach(s => h.caja(g, 0.18, 9, 0.18, acero, s * (W / 2 + 0.25), 0.5, 0)); h.caja(g, W + 2.6, 9, 0.4, hormigon, 0, 0.5, -1.9); [-1, 1].forEach(s => h.caja(g, 0.4, 9, 4, hormigon, s * (W / 2 + 1.1), 0.5, 0)); }
else if (v === 'cabina') { const cb = cabina(); g.add(cb); }
return h.sombra(g);
"""

FRIGO = r"""
const marca = (nom, obj, x, y, z) => { const m = new THREE.Object3D(); m.name = 'p_' + nom; m.position.set(x, y, z); obj.add(m); };
const g = new THREE.Group(), v = o.vista || 'todo', roto = !!o.roto, dias = o.dias || 0;
const blanco = h.M('#eef1f4', { roughness: 0.35 }), plast = new THREE.MeshStandardMaterial({ color: '#dff1ff', roughness: 0.05, transparent: true, opacity: 0.35 }), interior = h.M('#f7f9fb', { roughness: 0.4 });
const W = 3.4, H = 7, F = 2.6;
const pod = (col) => roto ? new THREE.Color(col).lerp(new THREE.Color('#6a7a3a'), Math.min(0.75, dias * 0.12)).getStyle() : col;
const cuerpo = () => { const q = new THREE.Group();
  h.caja(q, W, H, 0.1, blanco, 0, H / 2, -F / 2); [-1, 1].forEach(s => h.caja(q, 0.12, H, F, blanco, s * W / 2, H / 2, 0)); h.caja(q, W, 0.12, F, blanco, 0, H, 0); h.caja(q, W, 0.3, F, blanco, 0, 0.15, 0);
  h.caja(q, W - 0.24, H - 0.4, 0.05, interior, 0, H / 2, -F / 2 + 0.08);
  // congelador arriba
  h.caja(q, W - 0.2, 0.12, F - 0.1, blanco, 0, H - 2.0, 0);
  for (let k = 0; k < 4; k++) { const s = h.malla(new THREE.BoxGeometry(W - 0.3, 0.05, F - 0.3), plast, 0, 1.0 + k * 1.15, 0.05); q.add(s); }
  // luz interior
  const luzOn = !roto; h.caja(q, 0.8, 0.08, 0.3, new THREE.MeshStandardMaterial({ color: '#ffffff', emissive: '#e8f4ff', emissiveIntensity: luzOn ? 1.4 : 0 }), 0, H - 2.15, -0.6); if (luzOn) q.add(h.en(h.brillo('#e8f4ff', 5, 0.35), 0, H - 2.5, 0));
  // puertas abiertas (giradas)
  [[H - 2.0, 2.0], [0.3, H - 2.3]].forEach(([y0, hh], j) => { const pu = new THREE.Group(); h.caja(pu, W, hh, 0.2, blanco, W / 2, hh / 2, 0); h.caja(pu, W - 0.3, hh - 0.3, 0.05, interior, W / 2, hh / 2, -0.12);
    h.caja(pu, 0.12, hh * 0.5, 0.15, h.M('#b8bec6', { metalness: 0.7, roughness: 0.25 }), W - 0.3, hh / 2, 0.18);
    if (j === 1) for (let k = 0; k < 3; k++) { h.caja(pu, W - 0.5, 0.06, 0.45, plast, W / 2, 0.8 + k * 1.4, -0.35); for (let b = 0; b < 3; b++) { const bt = h.malla(new THREE.CylinderGeometry(0.16, 0.16, 0.8, 14), h.M(pod(['#f2f2f2', '#f2a81e', '#2fb38a'][b]), { roughness: 0.3 }), 0.6 + b * 1.0, 1.25 + k * 1.4, -0.35); pu.add(bt); } }
    pu.position.set(W / 2, y0, F / 2); pu.rotation.y = -1.9; q.add(pu); });
  return q; };
const comida = () => { const q = new THREE.Group();
  // leche, huevos, fruta, verdura, carne, queso
  const leche = new THREE.Group(); h.caja(leche, 0.6, 1.0, 0.6, h.M(pod('#ffffff')), 0, 0.5, 0); const t = h.malla(new THREE.ConeGeometry(0.43, 0.3, 4), h.M(pod('#2f6fd8')), 0, 1.15, 0); t.rotation.y = Math.PI / 4; leche.add(t); leche.position.set(-1.0, 1.05, 0); q.add(leche);
  for (let k = 0; k < 6; k++) { const hu = h.malla(new THREE.SphereGeometry(0.13, 12, 10), h.M(pod('#f2e2c4')), 0.2 + (k % 3) * 0.3, 2.3, -0.3 + Math.floor(k / 3) * 0.3); hu.scale.y = 1.25; q.add(hu); }
  h.caja(q, 1.0, 0.1, 0.7, h.M('#c9a26a'), 0.5, 2.2, -0.15);
  for (let k = 0; k < 7; k++) q.add(h.malla(new THREE.SphereGeometry(0.2, 14, 10), h.M(pod(['#d8283c', '#f2a81e', '#7ac74f'][k % 3]), { roughness: 0.4 }), -1.1 + k * 0.35, 3.45, (k % 2) * 0.3 - 0.2));
  const carne = h.malla(new THREE.BoxGeometry(1.0, 0.25, 0.7), h.M(pod('#c8484a'), { roughness: 0.5 }), -0.6, 4.6, 0); q.add(carne); h.caja(q, 1.1, 0.06, 0.8, plast, -0.6, 4.75, 0);
  const queso = h.malla(new THREE.CylinderGeometry(0.4, 0.4, 0.4, 24, 1, false, 0, 4.8), h.M(pod('#f2c94c'), { roughness: 0.6 }), 0.8, 4.6, 0); q.add(queso);
  if (roto && dias > 2) for (let k = 0; k < 14; k++) { const m = h.malla(new THREE.SphereGeometry(0.05 + r() * 0.08, 8, 6), h.M('#7a9a4a', { roughness: 1 }), -1.2 + r() * 2.4, 1.2 + r() * 3.6, (r() - 0.5) * 0.8); q.add(m); }
  // congelador: hielo o charco
  if (!roto || dias < 1) { for (let k = 0; k < 5; k++) { const hi = h.malla(new THREE.BoxGeometry(0.5, 0.4, 0.5), new THREE.MeshStandardMaterial({ color: '#cfeaff', roughness: 0.1, transparent: true, opacity: 0.8 }), -1.0 + k * 0.5, H - 1.7, 0); hi.rotation.y = r(); q.add(hi); } }
  else { const ch = h.malla(new THREE.CylinderGeometry(1.3, 1.3, 0.03, 30), new THREE.MeshStandardMaterial({ color: '#9fd3ff', roughness: 0.02, metalness: 0.3, transparent: true, opacity: 0.7 }), 0.3, 0.32, 1.6); ch.scale.z = 0.6; q.add(ch); for (let k = 0; k < 6; k++) q.add(h.malla(new THREE.SphereGeometry(0.06, 8, 6), new THREE.MeshStandardMaterial({ color: '#9fd3ff', transparent: true, opacity: 0.8 }), -1 + k * 0.4, H - 1.95, 1.2)); }
  return q; };
const compresor = () => { const q = new THREE.Group(), cobre = h.M('#c87a3a', { metalness: 0.8, roughness: 0.3 });
  h.caja(q, W, 2.6, 0.1, h.M('#3a3d44'), 0, 1.3, 0); for (let k = 0; k < 14; k++) { const tb = h.malla(new THREE.TorusGeometry(1.3, 0.04, 6, 30, Math.PI), h.M('#2b2b30', { metalness: 0.6 }), 0, 3.2 + k * 0.18, 0.15); tb.rotation.z = Math.PI / 2; tb.scale.y = 0.95; q.add(tb); }
  for (let k = 0; k < 16; k++) h.caja(q, 0.04, 2.6, 0.04, h.M('#4a4d55'), -1.5 + k * 0.2, 4.4, 0.2);
  const cm = h.malla(new THREE.CapsuleGeometry(0.55, 0.5, 8, 20), h.M('#1c1c20', { metalness: 0.4, roughness: 0.4 }), 0.6, 0.9, 0.6); q.add(cm);
  const ps = [new THREE.Vector3(0.6, 1.5, 0.6), new THREE.Vector3(0.6, 2.2, 0.4), new THREE.Vector3(-0.8, 2.6, 0.3), new THREE.Vector3(-1.2, 3.2, 0.2)]; q.add(h.malla(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(ps), 30, 0.06, 8), cobre));
  if (roto) { for (let k = 0; k < 8; k++) q.add(h.en(h.brillo(k % 2 ? '#ffb347' : '#ff5a1a', 0.4 + k * 0.05, 0.8), 0.6 + (r() - 0.5) * 0.6, 1.3 + r() * 0.5, 1.0)); const hm = h.humo(6, 3, '#8a8a8a', r); hm.position.set(0.6, 1.5, 0.7); q.add(hm); }
  else { const led = h.malla(new THREE.SphereGeometry(0.08, 10, 8), new THREE.MeshStandardMaterial({ color: '#2fe08a', emissive: '#2fe08a', emissiveIntensity: 2 }), 1.2, 1.5, 0.6); q.add(led); }
  return q; };
const termo = () => { const q = new THREE.Group(), gr = roto ? Math.min(22, 4 + dias * 3) : 4; const cv = document.createElement('canvas'); cv.width = 256; cv.height = 128; const x = cv.getContext('2d'); x.fillStyle = '#10161f'; x.fillRect(0, 0, 256, 128); x.fillStyle = gr > 8 ? '#ff5a3a' : '#5ad1ff'; x.font = '900 80px Mont, Inter, sans-serif'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText(gr + '°C', 128, 66);
  const tx = new THREE.CanvasTexture(cv); tx.colorSpace = THREE.SRGBColorSpace; h.caja(q, 1.4, 0.7, 0.08, new THREE.MeshStandardMaterial({ map: tx, emissive: '#ffffff', emissiveMap: tx, emissiveIntensity: 0.9 }), 0, 0, 0); return q; };
const cocina = () => { const q = new THREE.Group(); const az = h.lienzoTex('azulejoCocina', 128, 128, (x, w) => { x.fillStyle = '#e8e2d4'; x.fillRect(0, 0, w, w); x.fillStyle = '#cfc6b2'; for (let f = 0; f < 8; f++) { x.fillRect(0, f * 16, w, 2); for (let k = 0; k < 4; k++) x.fillRect(k * 32 + (f % 2) * 16, f * 16, 2, 16); } }, true);
  h.caja(q, 16, 10, 0.2, h.M('#ffffff', { map: az, roughness: 0.4 }), 0, 5, -F / 2 - 0.2); h.caja(q, 16, 0.2, 8, h.M('#b8956a', { roughness: 0.6 }), 0, -0.1, 1);
  [-1, 1].forEach(sd => { h.caja(q, 4.5, 3.2, F, h.M('#5a6a7a', { roughness: 0.5 }), sd * (W / 2 + 2.3), 1.6, 0); h.caja(q, 4.6, 0.2, F + 0.2, h.M('#f2efe9', { roughness: 0.3 }), sd * (W / 2 + 2.3), 3.3, 0); h.caja(q, 4.5, 2.4, 1.4, h.M('#5a6a7a', { roughness: 0.5 }), sd * (W / 2 + 2.3), 7.2, -0.6); });
  h.caja(q, 1.4, 0.5, 0.8, h.M('#c9ccd2', { metalness: 0.6, roughness: 0.3 }), -(W / 2 + 2.3), 3.65, -0.2); q.add(h.malla(new THREE.CylinderGeometry(0.35, 0.3, 0.7, 20), h.M('#d8323a'), W / 2 + 2.0, 3.75, 0));
  q.add((() => { const l = new THREE.PointLight('#ffe2b8', 25, 18, 1.5); l.position.set(0, 8, 5); return l; })()); return q; };
if (v === 'todo') { g.add(cocina()); g.add(cuerpo()); g.add(comida()); const t = termo(); t.position.set(0, H - 1.0, -F / 2 + 0.15); g.add(t); }
else if (v === 'comida') { g.add((() => { const l = new THREE.PointLight(roto ? '#c8d8a0' : '#e8f4ff', 10, 10, 1.5); l.position.set(0, 4, 3); return l; })()); g.add(comida()); h.caja(g, W - 0.3, 0.05, F - 0.3, plast, 0, 1.0, 0); h.caja(g, W - 0.3, 0.05, F - 0.3, plast, 0, 2.15, 0); h.caja(g, W - 0.3, 0.05, F - 0.3, plast, 0, 3.3, 0); h.caja(g, W - 0.3, 0.05, F - 0.3, plast, 0, 4.45, 0); h.caja(g, W, 5.4, 0.1, interior, 0, 2.8, -F / 2); }
else if (v === 'congelador') { const q = comida(); q.position.y = -(H - 2.5); g.add(q); h.caja(g, W, 0.12, F, blanco, 0, -0.05, 0); h.caja(g, W, 2.0, 0.1, interior, 0, 0.9, -F / 2); }
else if (v === 'compresor') { g.add(compresor()); g.add((() => { const l = new THREE.PointLight('#ffb070', 8, 10, 1.5); l.position.set(1, 2, 3); return l; })()); }
else if (v === 'termometro') { const t = termo(); t.position.y = 1; g.add(t); h.caja(g, 2.0, 1.2, 0.1, blanco, 0, 1, -0.1); }
[['nevera', 0, 3.5, 0], ['leche', -1.0, 1.55, 0], ['huevos', 0.5, 2.3, 0], ['fruta', 0, 3.45, 0], ['carne', -0.6, 4.6, 0], ['queso', 0.8, 4.6, 0], ['congelador', 0, 5.3, 0], ['termo', 0, 6.0, -1.15], ['charco', 0.3, 0.3, 1.6], ['compresor', 0.6, 1.2, 0.6], ['serpentin', 0, 4.2, 0.2]].forEach(([n2, x, y, z]) => marca(n2, g, x, y, z));
return h.sombra(g);
"""

AVION_CORTE = r"""
const marca = (nom, obj, x, y, z) => { const m = new THREE.Object3D(); m.name = 'p_' + nom; m.position.set(x, y, z); obj.add(m); };
const g = new THREE.Group(), v = o.vista || 'todo', abierta = !!o.abierta, mascaras = !!o.mascaras;
const piel = h.M('#eef1f5', { roughness: 0.35, metalness: 0.2 }), azul = h.M('#1f3a6a', { roughness: 0.5 }), gris = h.M('#8a929c', { metalness: 0.5, roughness: 0.35 });
const L = v === 'cabina' ? 9.5 : 22, R = 2.6;
// fuselaje cortado a lo largo: media piel detrás, suelo de cabina, filas de asientos con pasajeros, portaequipajes, ventanillas
const fus = () => { const q = new THREE.Group();
  const cas = h.malla(new THREE.CylinderGeometry(R, R, L, 48, 1, true, Math.PI / 2, Math.PI), new THREE.MeshStandardMaterial({ color: '#e9edf2', roughness: 0.4, side: THREE.DoubleSide }), 0, 0, 0); cas.rotation.z = Math.PI / 2; q.add(cas);
  for (let k = 0; k < Math.floor(L / 0.8) - 1; k++) { const vt = h.malla(new THREE.CapsuleGeometry(0.16, 0.18, 4, 10), new THREE.MeshStandardMaterial({ color: '#9fd3ff', emissive: '#bfe6ff', emissiveIntensity: 0.5 }), -L / 2 + 1.2 + k * 0.8, 0.5, -R + 0.08); q.add(vt); }
  h.caja(q, L, 0.15, 2 * R - 0.4, h.M('#3a3d55', { roughness: 0.8 }), 0, -1.1, 0);
  h.caja(q, L, 0.08, 0.5, h.M('#c9a26a'), 0, -1.0, 0.5);
  for (let k = 0; k < Math.floor((L - 2) / 1.55); k++) { const x = -L / 2 + 1.5 + k * 1.55;
    [-1.5, -0.9].forEach((z, j) => { const as = new THREE.Group(); h.caja(as, 0.55, 0.2, 0.5, azul, 0, 0, 0); h.caja(as, 0.15, 0.8, 0.5, azul, -0.25, 0.45, 0); h.caja(as, 0.12, 0.2, 0.52, h.M('#d9dde3'), -0.28, 0.9, 0);
      if ((k + j) % 3 !== 2) { const p = new THREE.Group(), ropa = h.M(['#d8323a', '#2fb38a', '#f2c94c', '#8a5ad8', '#2f6fd8'][(k + j) % 5]); p.add(h.malla(new THREE.CapsuleGeometry(0.17, 0.4, 4, 8), ropa, 0, 0.45, 0)); p.add(h.malla(new THREE.SphereGeometry(0.15, 12, 10), h.M(['#f1c7a0', '#c98a5a', '#8a5a3a'][k % 3]), 0.02, 0.92, 0)); p.add(h.malla(new THREE.SphereGeometry(0.155, 12, 8, 0, 6.3, 0, 1.4), h.M(['#2b2117', '#5a3a22', '#d9b25a'][(k + j) % 3]), 0, 0.97, 0)); as.add(p); }
      as.position.set(x, -0.95, z); q.add(as); }); }
  // portaequipajes
  h.caja(q, L - 1, 0.6, 0.9, h.M('#f2f4f6'), 0, 1.4, -1.85);
  // máscaras de oxígeno colgando
  if (mascaras) for (let k = 0; k < Math.floor((L - 2) / 1.55); k++) { const x = -L / 2 + 1.5 + k * 1.55; [-1.5, -0.9].forEach(z => { q.add(h.malla(new THREE.CylinderGeometry(0.01, 0.01, 1.0, 4), h.M('#ffffff'), x + 0.1, 0.6, z)); const m = h.malla(new THREE.ConeGeometry(0.12, 0.18, 14, 1, true), h.M('#f2c94c', { side: THREE.DoubleSide }), x + 0.1, 0.05, z); q.add(m); }); }
  // luces de techo
  for (let k = 0; k < Math.ceil(L / 3.6); k++) q.add(h.en(h.brillo('#fff2c4', 2.2, 0.35), -L / 2 + 2 + k * 3.6, 2.0, -0.8));
  q.add((() => { const l = new THREE.PointLight('#ffe2b8', 18, 16, 1.5); l.position.set(0, 1.5, 3); return l; })());
  return q; };
const puerta = () => { const q = new THREE.Group(), marco = gris;
  h.caja(q, 3.4, 4.6, 0.25, piel, 0, 0, 0);
  const pu = new THREE.Group(); h.caja(pu, 1.6, 2.6, 0.3, h.M('#dfe4ea', { roughness: 0.4 }), 0, 0, 0); pu.add(h.malla(new THREE.CapsuleGeometry(0.2, 0.2, 4, 12), new THREE.MeshStandardMaterial({ color: '#9fd3ff', emissive: '#bfe6ff', emissiveIntensity: 0.4 }), 0, 0.6, 0.16));
  const pal = h.malla(new THREE.BoxGeometry(0.9, 0.12, 0.12), h.M('#d8323a', { metalness: 0.4 }), 0.1, -0.3, 0.25); pal.rotation.z = abierta ? -1.2 : 0; pu.add(pal); h.caja(pu, 0.15, 0.15, 0.2, marco, -0.35, -0.3, 0.2);
  const cv = document.createElement('canvas'); cv.width = 256; cv.height = 64; const x = cv.getContext('2d'); x.fillStyle = '#d8323a'; x.fillRect(0, 0, 256, 64); x.fillStyle = '#fff'; x.font = '900 34px Mont, Inter, sans-serif'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText(o.texto || 'EMERGENCY', 128, 34);
  const tx = new THREE.CanvasTexture(cv); tx.colorSpace = THREE.SRGBColorSpace; h.caja(pu, 0.9, 0.22, 0.02, new THREE.MeshStandardMaterial({ map: tx }), 0, -0.85, 0.17);
  pu.position.set(abierta ? 1.0 : 0, 0, 0.2); pu.rotation.y = abierta ? -0.5 : 0; q.add(pu);
  // manómetro de presión de cabina
  const mn = new THREE.Group(); mn.add(h.malla(new THREE.CylinderGeometry(0.35, 0.35, 0.1, 30), h.M('#1c1f24'), 0, 0, 0)); mn.children[0].rotation.x = Math.PI / 2; const ag = h.malla(new THREE.BoxGeometry(0.04, 0.28, 0.02), h.M('#ff5a3a'), 0, 0.1, 0.06); ag.rotation.z = abierta ? -1.2 : 0.4; mn.add(ag);
  mn.position.set(1.3, 1.6, 0.2); q.add(mn);
  if (abierta) for (let k = 0; k < 20; k++) { const s = h.brillo('#ffffff', 0.4 + r() * 0.8, 0.5); s.position.set(1.4 + r() * 2, (r() - 0.5) * 2.4, 0.5 + r() * 2); q.add(s); }
  return q; };
const ala = () => { const q = new THREE.Group(); const sh = new THREE.Shape(); sh.moveTo(0, 0); sh.lineTo(-3, 9); sh.lineTo(-4.5, 9); sh.lineTo(-4, 0); sh.lineTo(0, 0);
  const geo = new THREE.ExtrudeGeometry(sh, { depth: 0.3, bevelEnabled: true, bevelSize: 0.08, bevelThickness: 0.08 }); geo.rotateX(Math.PI / 2); q.add(h.malla(geo, piel));
  const mo = h.malla(new THREE.CylinderGeometry(0.9, 0.75, 3.2, 30), gris, -1.2, -0.9, 3.0); mo.rotation.z = Math.PI / 2; q.add(mo); const bo = h.malla(new THREE.CircleGeometry(0.85, 30), h.M('#1c1c20'), 0.42, -0.9, 3.0); bo.rotation.y = Math.PI / 2; q.add(bo);
  const fan = new THREE.Group(); for (let k = 0; k < 14; k++) { const b = h.malla(new THREE.BoxGeometry(0.05, 0.75, 0.15), h.M('#aeb5bf', { metalness: 0.7 }), 0, 0.38, 0); b.rotation.x = 0.3; const gg = new THREE.Group(); gg.add(b); gg.rotation.x = k / 14 * 6.28; fan.add(gg); } fan.position.set(0.38, -0.9, 3.0); fan.userData.giraY = 10; fan.rotation.y = Math.PI / 2; q.add(fan);
  q.add(h.en(h.brillo('#ff3a2a', 1.2, 0.9), -3.8, 0.1, 9)); return q; };
const nubes = () => { const q = new THREE.Group(); for (let k = 0; k < 40; k++) { const n = h.malla(new THREE.SphereGeometry(1.5 + r() * 2.5, 16, 12), h.M('#f4f6fa', { roughness: 1 }), (r() - 0.5) * 26, -6 - r() * 2, (r() - 0.5) * 12); n.scale.y = 0.5; q.add(n); } return q; };
const extremos = () => { const q = new THREE.Group(); const mo = h.malla(new THREE.SphereGeometry(R, 40, 24, 0, Math.PI * 2, 0, Math.PI / 2), piel, L / 2, 0, 0); mo.rotation.z = -Math.PI / 2; mo.scale.set(1, 1.7, 1); q.add(mo);
  q.add(h.malla(new THREE.BoxGeometry(1.2, 0.5, 2.2), h.M('#1a2230', { roughness: 0.1, metalness: 0.5 }), L / 2 + 2.6, 1.0, 0)); const co = h.malla(new THREE.ConeGeometry(R, 5, 40, 1, true), new THREE.MeshStandardMaterial({ color: '#e9edf2', roughness: 0.4, side: THREE.DoubleSide }), -L / 2 - 2.5, 0.4, 0); co.rotation.z = Math.PI / 2; q.add(co);
  const de = new THREE.Shape(); de.moveTo(0, 0); de.lineTo(-3, 5); de.lineTo(-4.5, 5); de.lineTo(-4, 0); const dg = new THREE.ExtrudeGeometry(de, { depth: 0.3, bevelEnabled: false }); dg.translate(0, 0, -0.15); q.add(h.malla(dg, azul, -L / 2 - 0.5, 1.8, 0)); return q; };
if (v === 'todo') { g.add(fus()); g.add(extremos()); g.add(nubes()); const a = ala(); a.position.set(2, -1.3, 2.6); a.scale.setScalar(0.7); g.add(a); }
else if (v === 'cabina') { const f = fus(); g.add(f); }
else if (v === 'puerta') { g.add(puerta()); h.caja(g, 8, 6, 0.2, piel, 0, 0, -0.3); for (let k = 0; k < 3; k++) g.add(h.malla(new THREE.CapsuleGeometry(0.2, 0.25, 4, 10), new THREE.MeshStandardMaterial({ color: '#9fd3ff', emissive: '#bfe6ff', emissiveIntensity: 0.5 }), -3 + k * 0.9, 0.9, -0.15)); g.add((() => { const l = new THREE.PointLight('#ffe2b8', 10, 10, 1.5); l.position.set(0, 2, 3); return l; })()); }
else if (v === 'ala') { g.add(ala()); const nb = nubes(); nb.position.y = 4; g.add(nb); }
if (v === 'puerta') { marca('palanca', g, 0.1, -0.3, 0.45); marca('manometro', g, 1.3, 1.6, 0.2); marca('puerta', g, 0, 0, 0.3); }
else if (v === 'ala') { marca('motor', g, -1.2, -0.9, 3.0); marca('ala', g, -2, 0, 4.5); }
else { marca('cabina', g, 0, 0, 0); marca('asientos', g, 0, -0.6, -1.2); marca('mascaras', g, 0, 0.1, -1.2); marca('ventanillas', g, 0, 0.5, -2.5); }
return h.sombra(g);
"""

COCHE_RAYO = r"""
const marca = (nom, obj, x, y, z) => { const m = new THREE.Object3D(); m.name = 'p_' + nom; m.position.set(x, y, z); obj.add(m); };
const g = new THREE.Group(), v = o.vista || 'todo', rayo = o.rayo !== false;
const coche = h.P.coche({ cantidad: 1, color: o.color || '#d8323a' }, r, c); coche.children.forEach(a => { a.position.set(0, 0, 0); a.rotation.y = 0; a.userData.fase = undefined; a.userData.carril = undefined; }); coche.userData.coches = false;
const cuerpo = new THREE.Group(); cuerpo.add(coche); cuerpo.scale.setScalar(1.6);
const brilla = new THREE.MeshStandardMaterial({ color: '#cfe8ff', emissive: '#9fd8ff', emissiveIntensity: 2.2, transparent: true, opacity: 0.9 });
const zig = (desde, hasta, n, grosor) => { const ps = [desde.clone()]; for (let k = 1; k < n; k++) { const t = k / n; ps.push(new THREE.Vector3().lerpVectors(desde, hasta, t).add(new THREE.Vector3((r() - 0.5) * 1.6, 0, (r() - 0.5) * 1.6))); } ps.push(hasta.clone()); return h.malla(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(ps, false, 'catmullrom', 0), n * 4, grosor, 6), brilla); };
// jaula de Faraday: la corriente recorre la carrocería por fuera (líneas brillantes sobre la chapa)
const jaula = () => { const q = new THREE.Group(); const pts = [[-3, 0.6], [-2.9, 1.5], [-1.4, 1.6], [-0.7, 2.5], [1.1, 2.5], [1.8, 1.6], [3.1, 1.5], [3.2, 0.6]];
  [-1.35, 1.35].forEach(z => { const ps = pts.map(([x, y]) => new THREE.Vector3(x, y, z)); q.add(h.malla(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(ps), 60, 0.06, 6), brilla)); });
  for (let k = 0; k < pts.length; k++) q.add(h.malla(new THREE.CylinderGeometry(0.05, 0.05, 2.7, 6), brilla, pts[k][0], pts[k][1], 0)).children; q.children.forEach(m => { if (m.geometry.type === 'CylinderGeometry') m.rotation.x = Math.PI / 2; });
  [[-2.0, 1.35], [2.0, 1.35], [-2.0, -1.35], [2.0, -1.35]].forEach(([x, z]) => q.add(zig(new THREE.Vector3(x, 0.8, z), new THREE.Vector3(x + (r() - 0.5), 0.0, z * 1.4), 4, 0.05)));
  return q; };
const carretera = () => { const q = new THREE.Group(); h.caja(q, 16, 0.1, 9, h.M('#2a2d33', { roughness: 0.15, metalness: 0.5 }), 0, -0.05, 0); for (let k = -2; k <= 2; k++) h.caja(q, 1.6, 0.02, 0.2, h.M('#f2f2f2'), k * 3.2, 0.01, 2.2);
  [-1, 1].forEach(s2 => h.caja(q, 16, 0.3, 1.5, h.M('#6a6f78'), 0, 0.1, s2 * 5)); for (let k = 0; k < 3; k++) { const x = -6 + k * 6; h.caja(q, 0.15, 5, 0.15, h.M('#3a3d44', { metalness: 0.5 }), x, 2.5, -5); q.add(h.en(h.brillo('#ffcf7a', 2.5, 0.8), x, 5, -4.5)); }
  for (let k = 0; k < 6; k++) h.caja(q, 1.2 + r() * 1.5, 3 + r() * 5, 2, h.M('#2a3048'), -7 + k * 2.8, 3, -7); return q; };
if (v === 'todo' || v === 'jaula') { g.add(carretera()); g.add(cuerpo); if (v === 'jaula' || rayo) g.add(jaula());
  if (rayo) { g.add(zig(new THREE.Vector3(1.5, 30, -2), new THREE.Vector3(0.3, 2.6, 0), 14, 0.18)); g.add(zig(new THREE.Vector3(6, 26, -4), new THREE.Vector3(1.5, 16, -2), 6, 0.08)); g.add(h.en(h.brillo('#dff1ff', 9, 0.9), 0.3, 2.8, 0)); for (let k = 0; k < 6; k++) g.add(h.en(h.brillo('#cfe8ff', 3, 0.5), 0.3, 6 + k * 4, -0.5)); }
  // charcos de lluvia
  for (let k = 0; k < 5; k++) { const ch = h.malla(new THREE.CylinderGeometry(0.6 + r(), 0.6 + r(), 0.02, 20), h.M('#3a4a5a', { roughness: 0.02, metalness: 0.6 }), (r() - 0.5) * 9, 0.01, 2 + r() * 2); g.add(ch); } }
else if (v === 'dentro') { // pasajeros a salvo dentro: asientos, volante y personas, la descarga por fuera de los cristales
  const asi = h.M('#2b2b30', { roughness: 0.7 }); [-0.7, 0.7].forEach(z => { h.caja(g, 1.2, 0.3, 1.0, asi, 0, 0.5, z); h.caja(g, 0.25, 1.4, 1.0, asi, -0.55, 1.2, z); });
  const vol = h.malla(new THREE.TorusGeometry(0.45, 0.06, 8, 30), h.M('#1c1c20'), 1.0, 1.4, -0.7); vol.rotation.y = Math.PI / 2; vol.rotation.x = 0.3; g.add(vol);
  h.caja(g, 0.8, 0.8, 3, h.M('#3a3d44'), 1.5, 0.9, 0);
  [-0.7, 0.7].forEach((z, k) => { const p = new THREE.Group(); p.add(h.malla(new THREE.CapsuleGeometry(0.25, 0.6, 4, 10), h.M(['#2f6fd8', '#f2c94c'][k]), 0, 1.25, 0)); p.add(h.malla(new THREE.SphereGeometry(0.22, 14, 10), h.M(['#e8b896', '#c98a5a'][k]), 0.05, 1.95, 0)); p.position.set(-0.1, 0, z); g.add(p); });
  const cr = new THREE.MeshStandardMaterial({ color: '#9fc7e8', transparent: true, opacity: 0.25, roughness: 0.05 }); h.caja(g, 0.05, 1.2, 3, cr, 1.9, 2.0, 0); h.caja(g, 2.4, 1.0, 0.05, cr, 0.2, 2.0, 1.5);
  const arco = new THREE.CatmullRomCurve3([new THREE.Vector3(2.0, 2.8, -1.6), new THREE.Vector3(0.5, 3.2, -1.6), new THREE.Vector3(-1.2, 2.9, -1.6), new THREE.Vector3(-1.6, 0.3, -1.6)]); g.add(h.malla(new THREE.TubeGeometry(arco, 40, 0.06, 6), brilla));
  g.add(h.en(h.brillo('#cfe8ff', 4, 0.6), 0.5, 3.2, -1.6)); }
else if (v === 'rueda') { const rr2 = new THREE.Group(); const ne = h.malla(new THREE.TorusGeometry(1.0, 0.45, 20, 40), h.M('#1c1c20', { roughness: 0.8 })); rr2.add(ne); const ll = h.malla(new THREE.CylinderGeometry(0.7, 0.7, 0.5, 30), h.M('#c9ccd2', { metalness: 0.8, roughness: 0.25 })); ll.rotation.x = Math.PI / 2; rr2.add(ll);
  for (let k = 0; k < 5; k++) { const ra = h.malla(new THREE.BoxGeometry(0.15, 0.6, 0.1), h.M('#9aa0a8', { metalness: 0.8 }), Math.cos(k * 1.26) * 0.35, Math.sin(k * 1.26) * 0.35, 0.27); ra.rotation.z = k * 1.26; rr2.add(ra); }
  for (let k = 0; k < 6; k++) { const q = h.malla(new THREE.SphereGeometry(0.15 + r() * 0.1, 8, 6), h.M('#1a1410', { roughness: 1 }), Math.cos(k) * 1.2, Math.sin(k) * 1.2, 0.35); q.scale.z = 0.2; rr2.add(q); }
  rr2.position.y = 1.45; g.add(rr2); g.add(zig(new THREE.Vector3(0.9, 1.8, 0.4), new THREE.Vector3(1.2, 0, 1.2), 5, 0.05)); g.add(h.en(h.brillo('#cfe8ff', 2, 0.7), 1.1, 0.3, 1.0)); }
if (v === 'todo' || v === 'jaula') { marca('coche', g, 0, 1.4, 0); marca('techo', g, 0.3, 3.4, 0); marca('bajos', g, -2.0, 0.3, 1.8); marca('cielo', g, 1.0, 14, -1); }
else if (v === 'dentro') { marca('pasajeros', g, -0.1, 1.6, 0); marca('arco', g, 0.5, 2.8, -1.6); }
else if (v === 'rueda') { marca('rueda', g, 0, 1.45, 0); marca('quemado', g, 1.0, 0.6, 1.0); }
return h.sombra(g);
"""

DIGESTIVO = r"""
const marca = (nom, obj, x, y, z) => { const m = new THREE.Object3D(); m.name = 'p_' + nom; m.position.set(x, y, z); obj.add(m); };
const g = new THREE.Group(), v = o.vista || 'todo', dia = o.dia || 0;
const carne = h.M('#e88a8a', { roughness: 0.55 }), rosa = h.M('#f2a6a0', { roughness: 0.5 }), acido = new THREE.MeshStandardMaterial({ color: '#d8e84a', emissive: '#a8c81a', emissiveIntensity: 0.5, transparent: true, opacity: 0.8, roughness: 0.1 });
const chicle = new THREE.MeshStandardMaterial({ color: '#ff6ac1', roughness: 0.35, emissive: '#ff2a9a', emissiveIntensity: 0.25 });
const piel = new THREE.MeshPhysicalMaterial({ color: '#9fd3ff', roughness: 0.2, transparent: true, opacity: 0.18, depthWrite: false, clearcoat: 1 });
const estomago = () => { const q = new THREE.Group(), pared = new THREE.MeshStandardMaterial({ color: '#d8706a', roughness: 0.5, side: THREE.DoubleSide }), dentro = new THREE.MeshStandardMaterial({ color: '#f29a8a', roughness: 0.45, side: THREE.BackSide });
  // bolsa cortada por la mitad para ver el interior
  const b = new THREE.Mesh(new THREE.SphereGeometry(1.8, 48, 32, Math.PI, Math.PI), pared); b.scale.set(1.35, 1, 0.85); b.rotation.z = -0.35; q.add(b);
  const b2 = new THREE.Mesh(new THREE.SphereGeometry(1.74, 48, 32, Math.PI, Math.PI), dentro); b2.scale.set(1.35, 1, 0.85); b2.rotation.z = -0.35; q.add(b2);
  const borde = h.malla(new THREE.TorusGeometry(1.77, 0.07, 8, 60), h.M('#c85a54')); borde.scale.set(1.35, 1, 1); borde.rotation.z = -0.35; q.add(borde);
  // esófago y salida al intestino
  const es = new THREE.CatmullRomCurve3([new THREE.Vector3(-1.4, 4.5, -0.3), new THREE.Vector3(-1.5, 2.6, -0.3), new THREE.Vector3(-1.1, 1.4, -0.3)]); q.add(h.malla(new THREE.TubeGeometry(es, 30, 0.3, 16), pared));
  const du = new THREE.CatmullRomCurve3([new THREE.Vector3(2.0, -0.8, -0.3), new THREE.Vector3(2.8, -0.6, -0.3), new THREE.Vector3(3.2, -1.6, -0.3), new THREE.Vector3(2.6, -2.4, -0.3)]); q.add(h.malla(new THREE.TubeGeometry(du, 30, 0.28, 16), pared));
  // pliegues de la pared
  for (let k = 0; k < 10; k++) { const pl = h.malla(new THREE.TorusGeometry(1.2 + (k % 3) * 0.2, 0.05, 6, 30, Math.PI * 0.7), h.M('#e07a72'), -0.6 + k * 0.15, 0.2 - k * 0.12, -0.9); pl.rotation.z = -0.4 + k * 0.05; q.add(pl); }
  // ácido verde con burbujas y el chicle rosa entero
  const ac = h.malla(new THREE.SphereGeometry(1.5, 40, 20, 0, Math.PI * 2, Math.PI * 0.55, Math.PI * 0.45), acido, 0.1, 0.0, -0.4); ac.scale.set(1.25, 1, 0.6); ac.rotation.z = -0.35; q.add(ac);
  for (let k = 0; k < 18; k++) { const bb = h.malla(new THREE.SphereGeometry(0.05 + r() * 0.07, 8, 6), new THREE.MeshStandardMaterial({ color: '#f2ff9a', transparent: true, opacity: 0.8 }), (r() - 0.5) * 2.6, -0.9 + r() * 0.6, -0.2 + r() * 0.3); q.add(bb); }
  const ch = h.malla(new THREE.SphereGeometry(0.42, 24, 16), chicle, 0.1, -0.55, -0.1); ch.scale.set(1.25, 0.8, 1); q.add(ch); q.add(h.en(h.brillo('#ff6ac1', 1.4, 0.4), 0.1, -0.5, 0.2));
  for (let k = 0; k < 8; k++) q.add(h.malla(new THREE.DodecahedronGeometry(0.12 + r() * 0.1, 0), h.M(['#c98a45', '#7ac74f', '#f2c94c'][k % 3], { transparent: true, opacity: 0.7 }), (r() - 0.5) * 2.2, -0.8 + r() * 0.5, -0.1));
  q.add((() => { const l = new THREE.PointLight('#ffd0c0', 10, 10, 1.5); l.position.set(0, 1, 3); return l; })());
  return q; };
const intestino = () => { const q = new THREE.Group(), tubo = new THREE.MeshStandardMaterial({ color: '#f0a090', roughness: 0.4 });
  // intestino delgado: un tubo largo plegado sobre sí mismo (paseo aleatorio suave dentro de una caja)
  const ps = []; let p = new THREE.Vector3(-1.5, 2.2, 0), d = new THREE.Vector3(1, 0, 0);
  for (let k = 0; k < 140; k++) { ps.push(p.clone()); d.add(new THREE.Vector3((r() - 0.5) * 0.9, (r() - 0.55) * 0.5, (r() - 0.5) * 0.5)).normalize(); p = p.clone().add(d.clone().multiplyScalar(0.32));
    if (Math.abs(p.x) > 2) d.x *= -1; if (p.y > 2.4 || p.y < -2.4) d.y *= -1; if (Math.abs(p.z) > 0.8) d.z *= -1; p.clamp(new THREE.Vector3(-2.2, -2.6, -0.9), new THREE.Vector3(2.2, 2.6, 0.9)); }
  const curva = new THREE.CatmullRomCurve3(ps); q.add(h.malla(new THREE.TubeGeometry(curva, 600, 0.22, 12), tubo));
  // intestino grueso enmarcando (forma de U invertida)
  const gr = new THREE.CatmullRomCurve3([new THREE.Vector3(-2.8, -2.8, -0.6), new THREE.Vector3(-2.9, 2.9, -0.6), new THREE.Vector3(2.9, 2.9, -0.6), new THREE.Vector3(2.8, -2.9, -0.6)]); q.add(h.malla(new THREE.TubeGeometry(gr, 80, 0.42, 16), h.M('#d88a7a', { roughness: 0.5 })));
  const pp = curva.getPoint(Math.min(0.95, 0.2 + dia * 0.28)); const ch = h.malla(new THREE.SphereGeometry(0.3, 20, 14), chicle, pp.x, pp.y, pp.z + 0.25); ch.scale.set(1.3, 0.8, 1); q.add(ch); q.add(h.en(h.brillo('#ff6ac1', 1.8, 0.55), pp.x, pp.y, pp.z + 0.5));
  q.add((() => { const l = new THREE.PointLight('#ffd0c0', 10, 10, 1.5); l.position.set(0, 1, 4); return l; })());
  return q; };
const torso = () => { const q = new THREE.Group(); const t = h.malla(new THREE.CapsuleGeometry(2.3, 4.5, 10, 30), piel, 0, 4.6, 0); t.scale.z = 0.55; t.renderOrder = 3; q.add(t); const cab = h.malla(new THREE.SphereGeometry(1.3, 30, 20), piel, 0, 9.4, 0); cab.renderOrder = 3; q.add(cab);
  q.add(h.malla(new THREE.CylinderGeometry(0.18, 0.18, 3.6, 14), rosa, 0, 7.4, 0)); const es = estomago(); es.position.set(0.3, 5.0, 0); es.scale.setScalar(0.55); q.add(es); const it = intestino(); it.position.set(0, 2.2, 0); it.scale.setScalar(0.5); q.add(it);
  q.add(h.malla(new THREE.SphereGeometry(0.7, 20, 14), h.M('#a65a3a', { roughness: 0.5 }), -1.1, 5.9, 0.2)); return q; };
if (v === 'todo') g.add(torso());
else if (v === 'estomago') g.add(estomago());
else if (v === 'intestino') g.add(intestino());
else if (v === 'chicle') { const ch = h.malla(new THREE.SphereGeometry(1.2, 30, 20), chicle, 0, 1.3, 0); ch.scale.set(1.3, 0.8, 1); g.add(ch); for (let k = 0; k < 30; k++) { const m = h.malla(new THREE.SphereGeometry(0.05, 6, 4), h.M('#ffd0ec'), (r() - 0.5) * 2.6, 1.3 + (r() - 0.5) * 1.5, (r() - 0.5) * 2); g.add(m); } const ai = new THREE.Group(); [['GOMA BASE', '#ffffff']].forEach(() => {}); g.add(ai); }
if (v === 'todo') { marca('estomago', g, 0.3, 5.0, 0); marca('intestino', g, 0, 2.2, 0); marca('esofago', g, 0, 7.4, 0); marca('cuerpo', g, 0, 4.8, 0); }
else if (v === 'estomago') { marca('acido', g, 0.1, -0.5, -0.1); marca('estomago', g, 0, 0.3, 0); marca('esofago', g, -1.3, 2.5, -0.3); }
else if (v === 'intestino') { marca('intestino', g, 0, 0, 0); }
else { marca('chicle', g, 0, 1.3, 0); }
return h.sombra(g);
"""
