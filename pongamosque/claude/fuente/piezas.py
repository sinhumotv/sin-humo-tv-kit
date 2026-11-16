# Piezas a medida para los vídeos del 16-nov (cuerpo de función: (o, r, c, h, THREE) -> THREE.Group)

ABEJA = r"""
const g = new THREE.Group();
const negro = h.M('#1b1712', { roughness: 0.6 }), amar = h.M('#f2b51e', { roughness: 0.55 }), pelo = h.M('#e8a33a', { roughness: 0.9 });
// abdomen a rayas
const ab = new THREE.Group();
for (let k = 0; k < 6; k++) { const rr = 1.0 - Math.abs(k - 2.3) * 0.16; const s = h.malla(new THREE.CylinderGeometry(rr, rr * 0.96, 0.42, 28), k % 2 ? negro : amar, 0, 0, 0); s.rotation.z = Math.PI / 2; s.position.x = -0.9 - k * 0.4; ab.add(s); }
ab.add(h.malla(new THREE.SphereGeometry(0.62, 24, 16), amar, -0.75, 0, 0)); ab.add(h.malla(new THREE.ConeGeometry(0.42, 0.7, 20), negro, -3.35, 0, 0)).children;
ab.children[ab.children.length - 1].rotation.z = Math.PI / 2; ab.rotation.z = 0.18; g.add(ab);
// tórax peludo
const tor = h.malla(new THREE.SphereGeometry(0.95, 32, 24), pelo, 0.25, 0.15, 0); g.add(tor);
for (let k = 0; k < 90; k++) { const a = r() * 6.28, b = r() * 3.14; const p = h.malla(new THREE.ConeGeometry(0.05, 0.22, 4), pelo, 0.25 + Math.sin(b) * Math.cos(a) * 0.95, 0.15 + Math.cos(b) * 0.95, Math.sin(b) * Math.sin(a) * 0.95); p.lookAt(0.25 + Math.sin(b) * Math.cos(a) * 3, 0.15 + Math.cos(b) * 3, Math.sin(b) * Math.sin(a) * 3); p.rotateX(Math.PI / 2); g.add(p); }
// cabeza con ojos compuestos y antenas
const cab = h.malla(new THREE.SphereGeometry(0.72, 28, 20), negro, 1.45, 0.25, 0); cab.scale.set(0.9, 1, 1.05); g.add(cab);
[-1, 1].forEach(s => { const o = h.malla(new THREE.SphereGeometry(0.4, 24, 16), h.M('#2a2018', { roughness: 0.15, metalness: 0.4 }), 1.65, 0.42, s * 0.48); o.scale.set(0.7, 1.15, 0.6); g.add(o);
  const ant = new THREE.CatmullRomCurve3([new THREE.Vector3(1.9, 0.75, s * 0.2), new THREE.Vector3(2.3, 1.5, s * 0.35), new THREE.Vector3(2.75, 1.7, s * 0.55)]);
  g.add(h.malla(new THREE.TubeGeometry(ant, 16, 0.045, 6), negro)); g.add(h.malla(new THREE.SphereGeometry(0.08, 10, 8), negro, 2.75, 1.7, s * 0.55)); });
// alas transparentes con nervios
const ala = h.M('#dff1ff', { transparent: true, opacity: 0.38, roughness: 0.05, metalness: 0.3, side: THREE.DoubleSide, depthWrite: false });
[-1, 1].forEach(s => { [0, 1].forEach(j => { const w = new THREE.Shape(); w.moveTo(0, 0); w.quadraticCurveTo(-0.6 - j * 0.2, 2.2 - j * 0.6, -1.9 + j * 0.5, 2.0 - j * 0.6); w.quadraticCurveTo(-1.2, 0.6, 0, 0);
  const m = new THREE.Mesh(new THREE.ShapeGeometry(w, 16), ala); m.position.set(0.1 - j * 0.35, 0.9, s * 0.25); m.rotation.x = s * (1.25 + j * 0.15); m.userData.alaS = s; g.add(m); }); });
// patas
for (let k = 0; k < 3; k++) [-1, 1].forEach(s => { const p = new THREE.CatmullRomCurve3([new THREE.Vector3(0.6 - k * 0.45, -0.5, s * 0.4), new THREE.Vector3(0.7 - k * 0.6, -1.1, s * 0.9), new THREE.Vector3(0.5 - k * 0.7, -1.7, s * 1.0)]); g.add(h.malla(new THREE.TubeGeometry(p, 12, 0.06, 6), negro)); });
g.userData.flotaE = 0.3;
return h.sombra(g);
"""

PANAL = r"""
const g = new THREE.Group();
const marco = h.M('#9a6a3c', { roughness: 0.7 }), cera = h.M('#e9b545', { roughness: 0.5 }), miel = h.M('#f2a114', { roughness: 0.15, emissive: '#c26a00', emissiveIntensity: o.vacio ? 0.0 : 0.35 });
const R = 0.42, filas = 12, cols = 10, hex = new THREE.CylinderGeometry(R, R, 0.5, 6, 1, true), tapa = new THREE.CylinderGeometry(R * 0.86, R * 0.86, 0.06, 6);
const W = cols * R * 1.75, H = filas * R * 1.52;
for (let f = 0; f < filas; f++) for (let k = 0; k < cols; k++) {
  const x = -W / 2 + k * R * 1.75 + (f % 2) * R * 0.87, y = 0.6 + f * R * 1.52; const celda = h.malla(hex, cera, x, y, 0); celda.rotation.x = Math.PI / 2; celda.rotation.y = Math.PI / 6; g.add(celda);
  const llena = o.vacio ? r() < 0.08 : r() < 0.72; if (llena) { const t = h.malla(tapa, miel, x, y, 0.2); t.rotation.x = Math.PI / 2; t.rotation.y = Math.PI / 6; g.add(t); }
}
h.caja(g, W + 1.0, 0.35, 0.7, marco, 0, 0.3, 0); h.caja(g, W + 1.0, 0.35, 0.7, marco, 0, H + 0.95, 0); h.caja(g, 0.35, H + 1.0, 0.7, marco, -W / 2 - 0.45, H / 2 + 0.6, 0); h.caja(g, 0.35, H + 1.0, 0.7, marco, W / 2 + 0.45, H / 2 + 0.6, 0);
for (let k = 0; k < 5; k++) { const gota = h.malla(new THREE.SphereGeometry(0.12, 12, 10), miel, -W / 2 + r() * W, 0.2, 0.3); gota.scale.y = 1.6; g.add(gota); }
return h.sombra(g);
"""

FLORES = r"""
const g = new THREE.Group(), n = o.cantidad || 40, mustia = !!o.mustias;
const cols = mustia ? ['#8a7a5a', '#7a6a4a', '#9a8a6a'] : ['#e2443a', '#f2c94c', '#ffffff', '#c86bd8', '#f39c12', '#ff7aa8'];
for (let k = 0; k < n; k++) { const f = new THREE.Group(), al = 0.8 + r() * 0.8, tallo = h.M(mustia ? '#7a7040' : '#4f9a44');
  const curva = new THREE.CatmullRomCurve3([new THREE.Vector3(0, 0, 0), new THREE.Vector3((r() - 0.5) * 0.2, al * 0.5, 0), new THREE.Vector3(mustia ? 0.35 : 0, al * (mustia ? 0.8 : 1), mustia ? 0.1 : 0)]);
  f.add(h.malla(new THREE.TubeGeometry(curva, 8, 0.03, 5), tallo));
  const top = curva.getPoint(1), pc = h.M(cols[k % cols.length], { roughness: 0.6, side: THREE.DoubleSide });
  for (let p = 0; p < 6; p++) { const pt = h.malla(new THREE.SphereGeometry(0.14, 10, 8), pc, top.x + Math.cos(p) * 0.15, top.y, top.z + Math.sin(p) * 0.15); pt.scale.set(1.3, mustia ? 0.25 : 0.35, 0.8); pt.rotation.y = -p; if (mustia) pt.position.y -= 0.12; f.add(pt); }
  f.add(h.malla(new THREE.SphereGeometry(0.09, 10, 8), h.M(mustia ? '#5a4a2a' : '#f2b51e'), top.x, top.y + 0.04, top.z));
  [-1, 1].forEach(s => { const hj = h.malla(new THREE.SphereGeometry(0.1, 8, 6), tallo, s * 0.08, al * 0.35, 0); hj.scale.set(1.8, 0.3, 0.7); f.add(hj); });
  f.position.set((r() - 0.5) * 9, 0, (r() - 0.5) * 6); f.rotation.y = r() * 6; g.add(f); }
return h.sombra(g);
"""

ESTANTERIA = r"""
const g = new THREE.Group(), metal = h.M('#c9ccd2', { metalness: 0.6, roughness: 0.35 }), vacia = !!o.vacia;
const W = 8, baldas = 4;
h.caja(g, 0.2, 5.2, 1.6, metal, -W / 2, 2.6, 0); h.caja(g, 0.2, 5.2, 1.6, metal, W / 2, 2.6, 0); h.caja(g, W, 5.2, 0.12, h.M('#e9ecef'), 0, 2.6, -0.75);
const frutas = [['#d8283c', 0.3], ['#f2a81e', 0.32], ['#7ac74f', 0.28], ['#f2c94c', 0.3], ['#a8326a', 0.22]];
for (let b = 0; b < baldas; b++) { const y = 0.5 + b * 1.3; h.caja(g, W, 0.1, 1.5, metal, 0, y, 0);
  const cv = document.createElement('canvas'); cv.width = 256; cv.height = 48; const x = cv.getContext('2d'); x.fillStyle = vacia ? '#d8323a' : '#ffffff'; x.fillRect(0, 0, 256, 48); x.fillStyle = vacia ? '#ffffff' : '#2b2b30'; x.font = '900 30px Mont, Inter, sans-serif'; x.textAlign = 'center'; x.textBaseline = 'middle';
  x.fillText(vacia ? 'AGOTADO' : ['MANZANAS', 'NARANJAS', 'PERAS', 'LIMONES'][b] + '  1,99 €', 128, 26); const tx = new THREE.CanvasTexture(cv); tx.colorSpace = THREE.SRGBColorSpace;
  h.caja(g, 1.6, 0.3, 0.05, new THREE.MeshStandardMaterial({ map: tx }), -W / 2 + 1.2 + (b % 2) * 3, y - 0.1, 0.78);
  const nf = vacia ? Math.floor(r() * 2) : 26; const [col, rad] = frutas[b % frutas.length];
  for (let k = 0; k < nf; k++) g.add(h.malla(new THREE.SphereGeometry(rad, 14, 10), h.M(col, { roughness: 0.4 }), -W / 2 + 0.5 + (k % 13) * 0.55 + r() * 0.1, y + rad + 0.05 + Math.floor(k / 13) * rad * 1.5, -0.3 + Math.floor(k / 13) * 0.45));
}
return h.sombra(g);
"""

CAJERO = r"""
const g = new THREE.Group(), cuerpo = h.M('#3a4a5a', { metalness: 0.4, roughness: 0.4 }), gris = h.M('#c9ccd2', { metalness: 0.6, roughness: 0.3 });
h.caja(g, 3.2, 5.0, 1.6, cuerpo, 0, 2.5, 0); h.caja(g, 3.4, 0.5, 1.8, h.M('#d8323a'), 0, 5.2, 0);
const cv = document.createElement('canvas'); cv.width = 512; cv.height = 384; const x = cv.getContext('2d'); x.fillStyle = '#0a2a5a'; x.fillRect(0, 0, 512, 384);
x.strokeStyle = '#ffffff'; x.lineWidth = 10; [60, 100, 140].forEach((rr, j) => { x.beginPath(); x.arc(256, 210, rr, Math.PI * 1.2, Math.PI * 1.8); x.stroke(); }); x.beginPath(); x.arc(256, 210, 12, 0, 6.3); x.fillStyle = '#ffffff'; x.fill();
x.strokeStyle = '#ff3b3b'; x.lineWidth = 16; x.beginPath(); x.moveTo(150, 80); x.lineTo(362, 280); x.stroke();
x.fillStyle = '#ffffff'; x.font = '900 40px Mont, Inter, sans-serif'; x.textAlign = 'center'; x.fillText(o.texto || 'SIN CONEXIÓN', 256, 345);
const tx = new THREE.CanvasTexture(cv); tx.colorSpace = THREE.SRGBColorSpace;
const pan = h.malla(new THREE.PlaneGeometry(2.2, 1.65), new THREE.MeshStandardMaterial({ map: tx, emissive: '#ffffff', emissiveMap: tx, emissiveIntensity: 0.8 }), 0, 3.6, 0.81); g.add(pan);
h.caja(g, 2.4, 0.15, 0.5, gris, 0, 2.55, 1.0); for (let k = 0; k < 12; k++) h.caja(g, 0.35, 0.08, 0.3, h.M('#2b2b30'), -0.6 + (k % 3) * 0.6, 2.66, 0.8 + Math.floor(k / 3) * -0.0 + (Math.floor(k / 3) - 1.5) * 0.12);
h.caja(g, 1.2, 0.1, 0.1, h.M('#111'), 0, 1.6, 0.81); h.caja(g, 0.8, 0.08, 0.1, h.M('#2fe08a', { emissive: '#2fe08a', emissiveIntensity: 0.4 }), 0, 1.25, 0.81);
g.add(h.en(h.brillo('#5aa0ff', 3.5, 0.5), 0, 3.6, 1.0));
return h.sombra(g);
"""

MOVIL_SIN = r"""
const g = new THREE.Group();
const cuerpo = h.malla(new THREE.BoxGeometry(3.2, 6.4, 0.35), h.M('#1c1c22', { metalness: 0.5, roughness: 0.25 }), 0, 3.4, 0); g.add(cuerpo);
const cv = document.createElement('canvas'); cv.width = 320; cv.height = 640; const x = cv.getContext('2d'); const gr = x.createLinearGradient(0, 0, 0, 640); gr.addColorStop(0, '#1f2a44'); gr.addColorStop(1, '#0a0f1c'); x.fillStyle = gr; x.fillRect(0, 0, 320, 640);
x.fillStyle = '#ffffff'; x.font = '600 26px Mont, Inter, sans-serif'; x.fillText('09:41', 24, 40); x.textAlign = 'right'; x.fillText('Sin servicio', 300, 40); x.textAlign = 'center';
x.strokeStyle = '#8fa3c8'; x.lineWidth = 14; [50, 85, 120].forEach(rr => { x.beginPath(); x.arc(160, 330, rr, Math.PI * 1.22, Math.PI * 1.78); x.stroke(); });
x.beginPath(); x.arc(160, 330, 12, 0, 6.3); x.fillStyle = '#8fa3c8'; x.fill(); x.strokeStyle = '#ff4a4a'; x.lineWidth = 14; x.beginPath(); x.moveTo(70, 200); x.lineTo(250, 380); x.stroke();
x.fillStyle = '#ffffff'; x.font = '900 34px Mont, Inter, sans-serif'; x.fillText(o.texto || 'Sin conexión', 160, 460); x.font = '500 22px Mont, Inter, sans-serif'; x.fillStyle = '#b8c4dc'; x.fillText('Comprueba tu red', 160, 500);
const tx = new THREE.CanvasTexture(cv); tx.colorSpace = THREE.SRGBColorSpace;
g.add(h.malla(new THREE.PlaneGeometry(2.95, 6.1), new THREE.MeshStandardMaterial({ map: tx, emissive: '#ffffff', emissiveMap: tx, emissiveIntensity: 0.85 }), 0, 3.4, 0.18));
g.add(h.malla(new THREE.CylinderGeometry(0.12, 0.12, 0.05, 16), h.M('#000'), 0, 6.3, 0.18)).children; g.children[g.children.length - 1].rotation.x = Math.PI / 2;
g.add(h.en(h.brillo('#6a8aff', 5, 0.35), 0, 3.4, 0.6));
return h.sombra(g);
"""

EMBALSE = r"""
const g = new THREE.Group(), noche = c && c.noche;
// vaso del embalse: tierra cuarteada en terrazas, un charco al fondo y el campanario del pueblo sumergido asomando
const tierra = h.M('#b89466', { roughness: 0.95 }), grieta = h.M('#5a4632', { roughness: 1 });
for (let k = 0; k < 5; k++) { const rr = 14 - k * 2.4; const m = h.malla(new THREE.CylinderGeometry(rr, rr + 0.8, 0.5, 48), h.M(['#c7a676', '#bb9a6a', '#b08e60', '#a58456', '#9a7a4e'][k], { roughness: 0.95 }), 0, 0.25 - k * 0.5, 0); m.scale.z = 0.6; g.add(m); }
const charco = o.vacio ? 2.2 : 5; g.add(h.malla(new THREE.CylinderGeometry(charco, charco, 0.08, 40), h.M('#4a6a5a', { roughness: 0.1, metalness: 0.3 }), 1.5, -2.0, 0.4)).children; g.children[g.children.length - 1].scale.z = 0.55;
for (let k = 0; k < 70; k++) { const a = r() * 6.28, d = 3 + r() * 9, l = 0.6 + r() * 1.6; const gr = h.malla(new THREE.BoxGeometry(l, 0.03, 0.06), grieta, Math.cos(a) * d, 0.52 - Math.min(4, Math.floor((14 - d) / 2.4)) * 0.5, Math.sin(a) * d * 0.6); gr.rotation.y = r() * 3; g.add(gr); }
// marcas del nivel antiguo en la presa
const presa = new THREE.Group(), hm = h.M('#cfcac0', { roughness: 0.8 });
const forma = new THREE.Shape(); forma.moveTo(-1.6, 0); forma.lineTo(1.6, 0); forma.lineTo(0.7, 9); forma.lineTo(-0.7, 9); forma.lineTo(-1.6, 0);
const pg = new THREE.ExtrudeGeometry(forma, { depth: 26, bevelEnabled: false }); pg.translate(0, -3, -13); const pm = new THREE.Mesh(pg, hm); pm.rotation.y = Math.PI / 2; presa.add(pm);
for (let k = 0; k < 6; k++) { const b = h.malla(new THREE.BoxGeometry(26, 0.12, 0.05), h.M(k < 4 ? '#8a8270' : '#d8d2c6'), 0, -2.5 + k * 1.3, -1.2); presa.add(b); }
presa.position.set(0, 0, -9); g.add(presa);
// campanario del pueblo sumergido
const ig = new THREE.Group(), pi = h.piedra ? h.piedra('#cdbb9c', 1, 3) : h.M('#cdbb9c'); ig.add(h.malla(new THREE.BoxGeometry(1.6, 6, 1.6), pi, 0, 1, 0));
ig.add(h.malla(new THREE.ConeGeometry(1.25, 2.4, 4), h.M('#8a5a3a'), 0, 5.2, 0)).children; ig.children[1].rotation.y = Math.PI / 4;
[-1, 1].forEach(s => { const v = h.malla(new THREE.BoxGeometry(0.4, 0.9, 0.1), h.M('#1c1714'), s * 0.0, 3.0, 0.81); ig.add(v); });
ig.add(h.malla(new THREE.BoxGeometry(0.5, 0.9, 0.1), h.M('#1c1714'), 0, 3, 0.81)); ig.position.set(-3, -2, 1.5); ig.rotation.z = 0.06; g.add(ig);
return h.sombra(g);
"""

CAMPO_SECO = r"""
const g = new THREE.Group();
// tierra cuarteada en placas y árboles secos
const losa = h.M('#c8a46e', { roughness: 0.95 });
for (let x = -6; x <= 6; x++) for (let z = -4; z <= 4; z++) { const p = h.malla(new THREE.CylinderGeometry(0.62 + r() * 0.1, 0.65, 0.18, 5 + Math.floor(r() * 3)), losa, x * 1.25 + (r() - 0.5) * 0.3, 0.09, z * 1.25 + (r() - 0.5) * 0.3); p.rotation.y = r() * 3; g.add(p); }
const tronco = h.M('#5a4232', { roughness: 0.9 });
for (let t = 0; t < 3; t++) { const a = new THREE.Group(); const al = 3 + r() * 2;
  a.add(h.malla(new THREE.CylinderGeometry(0.12, 0.25, al, 7), tronco, 0, al / 2, 0));
  for (let k = 0; k < 6; k++) { const ps = [new THREE.Vector3(0, al * (0.55 + r() * 0.4), 0)]; const dir = r() * 6.28; ps.push(new THREE.Vector3(Math.cos(dir) * 0.8, ps[0].y + 0.6, Math.sin(dir) * 0.8)); ps.push(new THREE.Vector3(Math.cos(dir) * 1.5, ps[0].y + 1.0 + r(), Math.sin(dir) * 1.5));
    a.add(h.malla(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(ps), 8, 0.06, 5), tronco)); }
  a.position.set((t - 1) * 4.5, 0, -1.5 + r() * 1.5); g.add(a); }
// espigas secas
for (let k = 0; k < 50; k++) { const e = h.malla(new THREE.CylinderGeometry(0.015, 0.02, 0.6 + r() * 0.4, 4), h.M('#b8994e'), (r() - 0.5) * 14, 0.3, (r() - 0.5) * 9); e.rotation.z = (r() - 0.5) * 0.6; g.add(e); }
return h.sombra(g);
"""

CISTERNA = r"""
const g = new THREE.Group(), blanco = h.M('#f4f4f2', { roughness: 0.4 }), azul = h.M('#1f5fb8', { roughness: 0.4 }), neg = h.M('#1c1c20');
h.caja(g, 2.4, 2.2, 2.4, azul, 3.6, 1.6, 0); h.caja(g, 2.3, 0.8, 2.42, h.M('#9ec7e8', { roughness: 0.05, metalness: 0.4 }), 3.75, 2.2, 0);
const tq = h.malla(new THREE.CylinderGeometry(1.25, 1.25, 6, 32), h.M('#d9dde3', { metalness: 0.7, roughness: 0.25 }), -0.6, 1.95, 0); tq.rotation.z = Math.PI / 2; g.add(tq);
const cv = document.createElement('canvas'); cv.width = 512; cv.height = 96; const x = cv.getContext('2d'); x.fillStyle = '#1f5fb8'; x.fillRect(0, 0, 512, 96); x.fillStyle = '#fff'; x.font = '900 60px Mont, Inter, sans-serif'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText(o.texto || 'AGUA POTABLE', 256, 50);
const tx = new THREE.CanvasTexture(cv); tx.colorSpace = THREE.SRGBColorSpace; const et = h.malla(new THREE.PlaneGeometry(4.6, 0.85), new THREE.MeshStandardMaterial({ map: tx }), -0.6, 1.95, 1.27); g.add(et);
h.caja(g, 7.6, 0.3, 2.0, neg, 0.3, 0.6, 0);
[[-2.6, 1], [-2.6, -1], [-1.2, 1], [-1.2, -1], [3.6, 1], [3.6, -1]].forEach(([px, pz]) => { const w = h.malla(new THREE.CylinderGeometry(0.48, 0.48, 0.35, 18), neg, px, 0.48, pz * 1.05); w.rotation.x = Math.PI / 2; g.add(w); });
g.add(h.en(h.brillo('#ffb347', 1.2, 0.8), 4.82, 1.2, 0.8)); g.add(h.en(h.brillo('#ffb347', 1.2, 0.8), 4.82, 1.2, -0.8));
return h.sombra(g);
"""

ASTEROIDE = r"""
const g = new THREE.Group();
const geo = new THREE.IcosahedronGeometry(3, 4), pos = geo.attributes.position;
for (let i = 0; i < pos.count; i++) { const v = new THREE.Vector3().fromBufferAttribute(pos, i); const n = 1 + 0.18 * Math.sin(v.x * 1.7 + v.y) * Math.cos(v.z * 1.3) + 0.08 * Math.sin(v.y * 4.1 + v.x * 2.3); v.multiplyScalar(n); pos.setXYZ(i, v.x, v.y, v.z); }
geo.computeVertexNormals(); const roca = h.malla(geo, h.M('#4a4248', { roughness: 0.95, flatShading: true })); g.add(roca);
for (let k = 0; k < 14; k++) { const a = r() * 6.28, b = r() * 3.14; const cr = h.malla(new THREE.SphereGeometry(0.3 + r() * 0.5, 12, 8), h.M('#2e282c', { roughness: 1 }), Math.sin(b) * Math.cos(a) * 3.05, Math.cos(b) * 3.05, Math.sin(b) * Math.sin(a) * 3.05); cr.scale.y = 0.3; cr.lookAt(0, 0, 0); g.add(cr); }
// cara incandescente por la entrada en la atmósfera y estela de fuego
const fuego = new THREE.MeshStandardMaterial({ color: '#ff7a1a', emissive: '#ff4a0a', emissiveIntensity: 2.2, transparent: true, opacity: 0.75, depthWrite: false });
const cap = h.malla(new THREE.SphereGeometry(3.25, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2.4), fuego, 0, 0, 0); cap.rotation.x = -0.9; g.add(cap);
for (let k = 0; k < 9; k++) { const s = h.brillo(k % 2 ? '#ffb347' : '#ff5a1a', 4 + k * 1.6, 0.75 - k * 0.06); s.position.set(-k * 1.1, k * 1.5, -k * 0.6); g.add(s); }
roca.userData.giraEje = 0.4;
return g;
"""

LUNA_MAREA = r"""
const g = new THREE.Group();
// playa con la marea muy baja: barcas varadas sobre la arena mojada, algas y charcas
g.add(h.malla(new THREE.BoxGeometry(22, 0.3, 14), h.M('#cbb28a', { roughness: 0.9 }), 0, -0.15, 0));
for (let k = 0; k < 9; k++) { const ch = h.malla(new THREE.CylinderGeometry(0.6 + r() * 1.2, 0.6 + r() * 1.2, 0.04, 20), h.M('#6a9aa8', { roughness: 0.05, metalness: 0.3 }), (r() - 0.5) * 18, 0.02, (r() - 0.5) * 10); ch.scale.z = 0.5; g.add(ch); }
for (let b = 0; b < 3; b++) { const bc = new THREE.Group(), col = ['#d8323a', '#2f6fd8', '#f2c94c'][b];
  const sh = new THREE.Shape(); sh.moveTo(-1.6, 0.6); sh.lineTo(1.8, 0.6); sh.quadraticCurveTo(1.6, 0, 1.0, -0.2); sh.lineTo(-1.3, -0.2); sh.lineTo(-1.6, 0.6);
  const cg = new THREE.ExtrudeGeometry(sh, { depth: 1.2, bevelEnabled: true, bevelSize: 0.06, bevelThickness: 0.06 }); cg.translate(0, 0, -0.6);
  bc.add(h.malla(cg, h.M(col, { roughness: 0.5 }))); bc.add(h.malla(new THREE.BoxGeometry(3.2, 0.06, 1.1), h.M('#8a6a48'), 0.1, 0.6, 0));
  bc.position.set(-6 + b * 6, 0.25, (r() - 0.5) * 4); bc.rotation.set(0, r() * 2, b % 2 ? 0.35 : -0.3); g.add(bc); }
for (let k = 0; k < 30; k++) { const a = h.malla(new THREE.SphereGeometry(0.12, 6, 4), h.M('#3a5a2a'), (r() - 0.5) * 18, 0.04, (r() - 0.5) * 10); a.scale.set(3, 0.2, 1); g.add(a); }
// marca del agua donde debería estar
const mar = h.malla(new THREE.BoxGeometry(22, 0.05, 3), h.M('#2f8fc0', { roughness: 0.1, metalness: 0.2 }), 0, 0, -8.5); g.add(mar);
return h.sombra(g);
"""

PANAL = r"""
const g = new THREE.Group();
const marco = h.M('#9a6a3c', { roughness: 0.7 }), cera = h.M('#e2ac3e', { roughness: 0.55 }), fondo = h.M('#7a4a12', { roughness: 0.8 });
const miel = new THREE.MeshStandardMaterial({ color: '#f2a114', roughness: 0.12, metalness: 0.1, emissive: '#b85a00', emissiveIntensity: 0.35 });
const R = 0.42, filas = 12, cols = 10, W = cols * R * 1.75, H = filas * R * 1.52;
h.caja(g, W + 0.4, H + 0.4, 0.2, fondo, 0, H / 2 + 0.6, -0.15);
// cada celda: anillo hexagonal (pared de cera) + fondo oscuro; las llenas, con su opérculo de miel brillante
const pared = new THREE.TorusGeometry(R * 0.82, 0.07, 4, 6);
for (let f = 0; f < filas; f++) for (let k = 0; k < cols; k++) {
  const x = -W / 2 + R + k * R * 1.75 + (f % 2) * R * 0.87, y = 0.6 + R + f * R * 1.52;
  const a = h.malla(pared, cera, x, y, 0.05); a.rotation.z = Math.PI / 6; a.scale.z = 3; g.add(a);
  const llena = o.vacio ? r() < 0.06 : r() < 0.75;
  if (llena) { const t = h.malla(new THREE.CircleGeometry(R * 0.78, 6), miel, x, y, 0.12); t.rotation.z = Math.PI / 6; g.add(t); }
}
h.caja(g, W + 1.0, 0.35, 0.7, marco, 0, 0.3, 0); h.caja(g, W + 1.0, 0.35, 0.7, marco, 0, H + 1.1, 0); h.caja(g, 0.35, H + 1.1, 0.7, marco, -W / 2 - 0.45, H / 2 + 0.7, 0); h.caja(g, 0.35, H + 1.1, 0.7, marco, W / 2 + 0.45, H / 2 + 0.7, 0);
if (!o.vacio) for (let k = 0; k < 6; k++) { const gota = h.malla(new THREE.SphereGeometry(0.13, 12, 10), miel, -W / 2 + r() * W, 0.35, 0.3); gota.scale.y = 1.7; g.add(gota); }
return h.sombra(g);
"""

FLORES = r"""
const g = new THREE.Group(), n = o.cantidad || 40, mustia = !!o.mustias, ext = 2.2 * Math.sqrt(n);
const cols = mustia ? ['#8a6a4a', '#7a5a3a', '#9a7a5a'] : ['#e2443a', '#f2c94c', '#ffffff', '#c86bd8', '#f39c12', '#ff7aa8'];
for (let k = 0; k < n; k++) { const f = new THREE.Group(), al = 0.8 + r() * 0.8, tallo = h.M(mustia ? '#7a7040' : '#4f9a44');
  const curva = new THREE.CatmullRomCurve3([new THREE.Vector3(0, 0, 0), new THREE.Vector3((r() - 0.5) * 0.2, al * 0.5, 0), new THREE.Vector3(mustia ? 0.4 : 0, al * (mustia ? 0.75 : 1), mustia ? 0.1 : 0)]);
  f.add(h.malla(new THREE.TubeGeometry(curva, 8, 0.035, 5), tallo));
  const top = curva.getPoint(1), pc = h.M(cols[k % cols.length], { roughness: 0.6, side: THREE.DoubleSide });
  for (let p = 0; p < 6; p++) { const pt = h.malla(new THREE.SphereGeometry(0.15, 10, 8), pc, top.x + Math.cos(p) * 0.16, top.y - (mustia ? 0.16 : 0), top.z + Math.sin(p) * 0.16); pt.scale.set(1.3, mustia ? 0.2 : 0.35, 0.8); pt.rotation.y = -p; if (mustia) pt.rotation.z = 0.9; f.add(pt); }
  f.add(h.malla(new THREE.SphereGeometry(0.1, 10, 8), h.M(mustia ? '#4a3a22' : '#f2b51e'), top.x, top.y + 0.04, top.z));
  [-1, 1].forEach(s => { const hj = h.malla(new THREE.SphereGeometry(0.11, 8, 6), tallo, s * 0.09, al * 0.35, 0); hj.scale.set(1.8, 0.3, 0.7); f.add(hj); });
  if (mustia) for (let p = 0; p < 2; p++) { const caida = h.malla(new THREE.SphereGeometry(0.12, 8, 6), pc, (r() - 0.5) * 0.8, 0.02, (r() - 0.5) * 0.8); caida.scale.set(1.3, 0.15, 0.8); f.add(caida); }
  f.position.set((r() - 0.5) * ext, 0, (r() - 0.5) * ext * 0.6); f.rotation.y = r() * 6; g.add(f); }
return h.sombra(g);
"""

ESTANTERIA = r"""
const g = new THREE.Group(), metal = h.M('#8a929c', { metalness: 0.6, roughness: 0.4 }), vacia = !!o.vacia;
const W = 8, baldas = 4;
h.caja(g, 0.25, 5.4, 1.7, metal, -W / 2, 2.7, 0); h.caja(g, 0.25, 5.4, 1.7, metal, W / 2, 2.7, 0); h.caja(g, W, 5.4, 0.12, h.M('#2e6a8a', { roughness: 0.7 }), 0, 2.7, -0.8);
const cv0 = document.createElement('canvas'); cv0.width = 512; cv0.height = 96; const x0 = cv0.getContext('2d'); x0.fillStyle = '#2fa84a'; x0.fillRect(0, 0, 512, 96); x0.fillStyle = '#fff'; x0.font = '900 60px Mont, Inter, sans-serif'; x0.textAlign = 'center'; x0.textBaseline = 'middle'; x0.fillText('FRUTERÍA', 256, 50);
const t0 = new THREE.CanvasTexture(cv0); t0.colorSpace = THREE.SRGBColorSpace; h.caja(g, W, 0.9, 0.15, new THREE.MeshStandardMaterial({ map: t0, emissive: '#ffffff', emissiveMap: t0, emissiveIntensity: 0.3 }), 0, 5.7, 0.2);
const frutas = [['#d8283c', 0.3], ['#f2a81e', 0.32], ['#7ac74f', 0.28], ['#f2d84c', 0.3]];
for (let b = 0; b < baldas; b++) { const y = 0.5 + b * 1.3; h.caja(g, W, 0.12, 1.6, metal, 0, y, 0);
  const cv = document.createElement('canvas'); cv.width = 256; cv.height = 48; const x = cv.getContext('2d'); x.fillStyle = vacia ? '#d8323a' : '#ffffff'; x.fillRect(0, 0, 256, 48); x.fillStyle = vacia ? '#ffffff' : '#2b2b30'; x.font = '900 30px Mont, Inter, sans-serif'; x.textAlign = 'center'; x.textBaseline = 'middle';
  x.fillText(vacia ? 'AGOTADO' : ['FRESAS', 'NARANJAS', 'PERAS', 'LIMONES'][b] + ' 1,99 €', 128, 26); const tx = new THREE.CanvasTexture(cv); tx.colorSpace = THREE.SRGBColorSpace;
  h.caja(g, 1.8, 0.34, 0.05, new THREE.MeshStandardMaterial({ map: tx }), -W / 2 + 1.4 + (b % 2) * 4, y - 0.12, 0.83);
  const [col, rad] = frutas[b % frutas.length], nf = vacia ? (b === 1 ? 2 : 0) : 26;
  for (let k = 0; k < nf; k++) g.add(h.malla(new THREE.SphereGeometry(rad, 14, 10), h.M(col, { roughness: 0.4 }), -W / 2 + 0.6 + (k % 13) * 0.55 + r() * 0.1 + (vacia ? 3 : 0), y + rad + 0.06 + Math.floor(k / 13) * rad * 1.5, -0.3 + Math.floor(k / 13) * 0.45));
  if (vacia) for (let k = 0; k < 2; k++) h.caja(g, 0.9, 0.5, 0.6, h.M('#c9a26a', { roughness: 0.9 }), -2.5 + k * 3.2 + r(), y + 0.31, 0);
}
return h.sombra(g);
"""

AEROPUERTO = r"""
const g = new THREE.Group();
// pista con marcas y tres aviones parados en fila, con escaleras y la terminal detrás
g.add(h.malla(new THREE.BoxGeometry(34, 0.1, 10), h.M('#3a3d44', { roughness: 0.9 }), 0, 0.05, 0));
for (let k = -7; k <= 7; k++) g.add(h.malla(new THREE.BoxGeometry(1.4, 0.02, 0.25), h.M('#f2f2f2'), k * 2.2, 0.11, 0));
[-4.6, 4.6].forEach(z => g.add(h.malla(new THREE.BoxGeometry(34, 0.02, 0.18), h.M('#f2c14e'), 0, 0.11, z)));
for (let k = 0; k < 3; k++) { const a = h.P.avion({ color: ['#f4f6fa', '#e8ecf2', '#f4f6fa'][k], color2: ['#1f4fb8', '#d8323a', '#2fb38a'][k] }, r, c); a.position.set(-10 + k * 10, 1.9, (k - 1) * 1.2); a.rotation.y = 0.3; g.add(a);
  [-1, 1].forEach(s => g.add(h.malla(new THREE.CylinderGeometry(0.25, 0.25, 0.3, 12), h.M('#1c1c20'), -10 + k * 10 + s * 1.2, 0.3, (k - 1) * 1.2 + s * 0.9)));
  const esc = h.malla(new THREE.BoxGeometry(2.2, 0.15, 0.9), h.M('#d9dde3', { metalness: 0.5 }), -10 + k * 10 + 3, 1.0, (k - 1) * 1.2 + 1.6); esc.rotation.z = 0.5; g.add(esc); }
const ter = h.caja(g, 34, 5, 4, h.M('#8fb6d6', { roughness: 0.1, metalness: 0.5 }), 0, 2.5, -9); h.caja(g, 34.4, 0.5, 4.4, h.M('#e8ecf0'), 0, 5.2, -9);
const cv = document.createElement('canvas'); cv.width = 512; cv.height = 96; const x = cv.getContext('2d'); x.fillStyle = '#d8323a'; x.fillRect(0, 0, 512, 96); x.fillStyle = '#fff'; x.font = '900 56px Mont, Inter, sans-serif'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText(o.texto || 'CANCELADO', 256, 50);
const tx = new THREE.CanvasTexture(cv); tx.colorSpace = THREE.SRGBColorSpace; h.caja(g, 8, 1.5, 0.1, new THREE.MeshStandardMaterial({ map: tx, emissive: '#ffffff', emissiveMap: tx, emissiveIntensity: 0.6 }), 0, 6.4, -6.8);
return h.sombra(g);
"""

EMBALSE = r"""
const g = new THREE.Group(), nivel = o.lleno ? 0.85 : (o.vacio ? 0.05 : 0.3);
// vaso del embalse: laderas en terrazas (las marcas del agua que ya no está), presa de hormigón en arco y lámina de agua
const R = 13, prof = 5, tierra = ['#c9a878', '#bf9e6e', '#b39264', '#a8875a', '#9c7c50', '#8f714a'];
for (let k = 0; k < 6; k++) { const rr = R - k * 2.0, y = -k * (prof / 6); const m = h.malla(new THREE.CylinderGeometry(rr, rr, prof / 6, 56, 1), h.M(tierra[k], { roughness: 0.95 }), 0, y, 0); m.scale.z = 0.62; g.add(m); }
const agua = new THREE.MeshStandardMaterial({ color: '#2f7fa8', roughness: 0.08, metalness: 0.2, transparent: true, opacity: 0.88 });
const ra = 1.5 + nivel * (R - 3), wa = h.malla(new THREE.CylinderGeometry(ra, ra, 0.1, 56), agua, 0, -prof + 0.6 + nivel * (prof - 0.6), 0); wa.scale.z = 0.62; g.add(wa);
// grietas en el fondo seco
for (let k = 0; k < 80; k++) { const a = r() * 6.28, d = ra + r() * (R - ra - 1), l = 0.5 + r() * 1.2, nv = Math.min(5, Math.floor((R - d) / 2)); const gr = h.malla(new THREE.BoxGeometry(l, 0.03, 0.07), h.M('#5a4632'), Math.cos(a) * d, -nv * (prof / 6) + prof / 12 + 0.02, Math.sin(a) * d * 0.62); gr.rotation.y = r() * 3; g.add(gr); }
// presa en arco (hormigón) con las marcas del nivel antiguo
const presa = new THREE.Group(), hor = h.M('#d6d2c8', { roughness: 0.75 });
const arco = h.malla(new THREE.CylinderGeometry(9, 9, 7.5, 40, 1, true, -0.55, 1.1), new THREE.MeshStandardMaterial({ color: '#d6d2c8', roughness: 0.75, side: THREE.DoubleSide }), 0, -1.2, 0); presa.add(arco);
for (let k = 0; k < 5; k++) { const b = h.malla(new THREE.CylinderGeometry(9.02, 9.02, 0.12, 40, 1, true, -0.55, 1.1), new THREE.MeshStandardMaterial({ color: k < 3 ? '#8a8270' : '#b8b2a4', side: THREE.DoubleSide }), 0, -4.2 + k * 1.3, 0); presa.add(b); }
presa.add(h.malla(new THREE.CylinderGeometry(9.3, 9.3, 0.5, 40, 1, false, -0.6, 1.2), hor, 0, 2.6, 0));
presa.position.set(0, 0, -R * 0.62 - 7.5); g.add(presa);
// pueblo sumergido que asoma: campanario y muros de casas
const pueblo = new THREE.Group(), pi = h.piedra('#cdbb9c', 1, 3), yb = -prof + 0.4;
pueblo.add(h.malla(new THREE.BoxGeometry(1.8, 7, 1.8), pi, 0, yb + 3.5, 0)); const tj = h.malla(new THREE.ConeGeometry(1.4, 2.4, 4), h.M('#8a5a3a'), 0, yb + 8.2, 0); tj.rotation.y = Math.PI / 4; pueblo.add(tj);
[[0, 5.4, 0.92], [0, 5.4, -0.92]].forEach(([x, y, z]) => pueblo.add(h.malla(new THREE.BoxGeometry(0.5, 1.0, 0.1), h.M('#1c1714'), x, yb + y, z)));
for (let k = 0; k < 6; k++) { const w = h.malla(new THREE.BoxGeometry(2 + r() * 1.5, 1 + r() * 1.6, 0.35), h.piedra('#c4b294', 1, 1), 2.5 + (k % 3) * 2.4, yb + 0.8, -1 + Math.floor(k / 3) * 2.2); w.rotation.y = r() * 1.5; pueblo.add(w); }
pueblo.position.set(-2.5, 0, 0.5); g.add(pueblo);
return h.sombra(g);
"""

ARRECIFE = r"""
const g = new THREE.Group();
g.add(h.malla(new THREE.CylinderGeometry(9, 10, 0.6, 40), h.M('#d8c79a', { roughness: 0.95 }), 0, -0.3, 0));
const cols = ['#ff7a8a', '#ffb347', '#c86bd8', '#4fd1c5', '#f2c94c', '#ff5a5a'];
for (let k = 0; k < 16; k++) { const c0 = cols[k % cols.length], m = h.M(c0, { roughness: 0.5, emissive: c0, emissiveIntensity: 0.25 }), x0 = (r() - 0.5) * 14, z0 = (r() - 0.5) * 8, tipo = k % 3;
  if (tipo === 0) { for (let b = 0; b < 7; b++) { const ps = [new THREE.Vector3(x0, 0, z0)]; let p = ps[0].clone(); for (let j = 0; j < 3; j++) { p = p.clone().add(new THREE.Vector3((r() - 0.5) * 0.8, 0.6 + r() * 0.5, (r() - 0.5) * 0.8)); ps.push(p); } g.add(h.malla(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(ps), 10, 0.12, 6), m)); } }
  else if (tipo === 1) { const s = h.malla(new THREE.SphereGeometry(0.9 + r() * 0.6, 20, 14), m, x0, 0.4, z0); s.scale.y = 0.7; g.add(s); for (let j = 0; j < 12; j++) { const a = j / 12 * 6.28; g.add(h.malla(new THREE.TorusGeometry(0.5, 0.04, 4, 12), h.M('#ffffff', { transparent: true, opacity: 0.5 }), x0 + Math.cos(a) * 0.3, 0.9, z0 + Math.sin(a) * 0.3)); } }
  else { for (let j = 0; j < 5; j++) { const f = h.malla(new THREE.CylinderGeometry(0.5 - j * 0.08, 0.15, 1.6 + j * 0.3, 10, 1, true), new THREE.MeshStandardMaterial({ color: c0, roughness: 0.6, side: THREE.DoubleSide }), x0 + (r() - 0.5) * 0.9, 0.8, z0 + (r() - 0.5) * 0.9); g.add(f); } } }
// peces de colores (algunos dando vueltas desorientados)
for (let k = 0; k < 18; k++) { const p = new THREE.Group(), col = ['#ff8a1a', '#2f9ad8', '#f2c94c', '#ffffff'][k % 4];
  const cu = h.malla(new THREE.SphereGeometry(0.35, 14, 10), h.M(col, { roughness: 0.4 })); cu.scale.set(1.6, 0.9, 0.5); p.add(cu);
  const co = h.malla(new THREE.ConeGeometry(0.3, 0.5, 3), h.M(col), -0.65, 0, 0); co.rotation.z = Math.PI / 2; p.add(co);
  if (col === '#ff8a1a') [-0.15, 0.2].forEach(x => { const f = h.malla(new THREE.TorusGeometry(0.3, 0.05, 4, 12), h.M('#ffffff'), x, 0, 0); f.rotation.y = Math.PI / 2; f.scale.set(1, 1, 0.8); p.add(f); });
  p.add(h.malla(new THREE.SphereGeometry(0.06, 8, 6), h.M('#111'), 0.38, 0.1, 0.16));
  p.position.set((r() - 0.5) * 12, 2 + r() * 4, (r() - 0.5) * 6); p.rotation.y = r() * 6; p.userData.flotaE = r() * 6; g.add(p); }
for (let k = 0; k < 40; k++) g.add(h.en(h.brillo('#cfe8ff', 0.25, 0.6), (r() - 0.5) * 14, r() * 8, (r() - 0.5) * 8));
return h.sombra(g);
"""

BUHO = r"""
const g = new THREE.Group();
const pluma = h.M('#7a5a3a', { roughness: 0.9 }), claro = h.M('#c9a77a', { roughness: 0.9 }), rama = h.M('#4a3424', { roughness: 0.9 });
const rm = h.malla(new THREE.CylinderGeometry(0.35, 0.45, 12, 10), rama, 0, 0.3, 0); rm.rotation.z = Math.PI / 2; g.add(rm);
for (let k = 0; k < 4; k++) { const hj = h.malla(new THREE.SphereGeometry(0.5, 8, 6), h.M('#2f5a2a'), -5 + k * 3, 0.9, 0.2); hj.scale.set(1.6, 0.6, 1); g.add(hj); }
const cu = h.malla(new THREE.SphereGeometry(1.6, 28, 20), pluma, 0, 2.4, 0); cu.scale.set(1, 1.3, 0.95); g.add(cu);
const pecho = h.malla(new THREE.SphereGeometry(1.25, 24, 16), claro, 0, 2.2, 0.6); pecho.scale.set(0.95, 1.2, 0.6); g.add(pecho);
for (let k = 0; k < 18; k++) { const m = h.malla(new THREE.SphereGeometry(0.1, 6, 4), pluma, (r() - 0.5) * 1.6, 1.5 + r() * 1.6, 1.32); m.scale.set(1.4, 0.5, 0.3); g.add(m); }
const cab = h.malla(new THREE.SphereGeometry(1.3, 28, 20), pluma, 0, 4.6, 0); cab.scale.set(1.15, 0.95, 1); g.add(cab);
[-1, 1].forEach(s => { const disco = h.malla(new THREE.CircleGeometry(0.62, 24), claro, s * 0.6, 4.6, 1.2); g.add(disco);
  const ojo = h.malla(new THREE.SphereGeometry(0.42, 20, 14), new THREE.MeshStandardMaterial({ color: '#ffb000', emissive: '#ff9a00', emissiveIntensity: 0.9, roughness: 0.2 }), s * 0.6, 4.65, 1.18); g.add(ojo);
  g.add(h.malla(new THREE.SphereGeometry(0.22, 14, 10), h.M('#050505', { roughness: 0.1 }), s * 0.6, 4.65, 1.5));
  const or = h.malla(new THREE.ConeGeometry(0.28, 0.9, 6), pluma, s * 0.85, 5.6, 0.2); or.rotation.z = -s * 0.3; g.add(or);
  const ala = h.malla(new THREE.SphereGeometry(0.9, 16, 12), h.M('#5a4028', { roughness: 0.9 }), s * 1.35, 2.3, -0.1); ala.scale.set(0.45, 1.3, 0.9); g.add(ala); });
const pico = h.malla(new THREE.ConeGeometry(0.16, 0.45, 8), h.M('#d9a33a'), 0, 4.25, 1.35); pico.rotation.x = Math.PI; g.add(pico);
[-0.4, 0.4].forEach(x => { for (let k = 0; k < 3; k++) g.add(h.malla(new THREE.CylinderGeometry(0.05, 0.03, 0.4, 6), h.M('#d9a33a'), x + (k - 1) * 0.12, 0.7, 0.3)); });
g.add(h.en(h.brillo('#ffb000', 1.4, 0.6), -0.6, 4.65, 1.6)); g.add(h.en(h.brillo('#ffb000', 1.4, 0.6), 0.6, 4.65, 1.6));
return h.sombra(g);
"""

EMBALSE = r"""
const g = new THREE.Group(), nivel = o.lleno ? 0.9 : (o.vacio ? 0.08 : 0.35);
// VALLE ENTRE MONTAÑAS cerrado por una presa de hormigón: detrás de la presa, el agua (o lo que queda) y las bandas claras de los niveles antiguos
const L = 30, A = 16;
const ladera = (s) => { const m = new THREE.Group(); for (let k = 0; k < 7; k++) { const h0 = 10 - k * 0.6; const b = h.malla(new THREE.BoxGeometry(5.5 + k * 0.4, h0, 4.2), h.M(['#8a7458', '#93805f', '#7e6a50'][k % 3], { roughness: 0.95, flatShading: true }), 0, h0 / 2 - 2, -k * 4.2 + 2); b.rotation.y = s * 0.05; m.add(b); } m.position.x = s * (A / 2 + 2.2); return m; };
g.add(ladera(-1)); g.add(ladera(1));
const fondo = h.malla(new THREE.BoxGeometry(A, 0.4, L), h.M('#7a5a3a', { roughness: 1 }), 0, -2.2, -L / 2 + 2); g.add(fondo);
// bandas de nivel en las laderas (tierra lavada, más clara)
for (let k = 0; k < 6; k++) { const y = -2 + k * 1.2; if (y < -2 + nivel * 7.5) continue; [-1, 1].forEach(s => g.add(h.malla(new THREE.BoxGeometry(0.15, 0.9, L), h.M('#d8c7a4', { roughness: 0.95 }), s * (A / 2 - 0.1), y, -L / 2 + 2))); }
// grietas y barro en el fondo al descubierto
for (let k = 0; k < 90; k++) { const gr = h.malla(new THREE.BoxGeometry(0.5 + r() * 1.4, 0.03, 0.07), h.M('#4a3624'), (r() - 0.5) * (A - 1), -1.98, -r() * (L - 4)); gr.rotation.y = r() * 3; g.add(gr); }
const agua = new THREE.MeshStandardMaterial({ color: '#2f7fa8', roughness: 0.06, metalness: 0.25, transparent: true, opacity: 0.9 });
const ya = -2 + nivel * 7.5, la = 2.5 + nivel * (L - 6); g.add(h.malla(new THREE.BoxGeometry(A - 0.2, 0.15, la), agua, 0, ya, 1.6 - la / 2));
// presa
const presa = new THREE.Group(), hor = h.M('#d6d2c8', { roughness: 0.7 });
presa.add(h.malla(new THREE.BoxGeometry(A + 4, 10, 2.4), hor, 0, 3, 0)); presa.add(h.malla(new THREE.BoxGeometry(A + 4.6, 0.6, 3.2), h.M('#bdb8ac'), 0, 8.3, 0));
for (let k = 0; k < 9; k++) presa.add(h.malla(new THREE.BoxGeometry(0.12, 9.6, 0.1), h.M('#bdb8ac'), -A / 2 - 1.5 + k * (A + 3) / 8, 3, 1.25));
for (let k = 0; k < 10; k++) presa.add(h.malla(new THREE.BoxGeometry(0.15, 0.5, 0.15), h.M('#8a929c', { metalness: 0.5 }), -A / 2 + k * A / 9, 8.85, 1.4));
presa.add(h.malla(new THREE.BoxGeometry(A + 4, 0.25, 0.1), h.M('#8a8270'), 0, ya + 0.6, -1.25));
presa.position.z = 3; g.add(presa);
g.rotation.y = Math.PI;
// pueblo sumergido que asoma: campanario y muros de piedra
const pueblo = new THREE.Group(), pi = h.piedra('#cdbb9c', 1, 3);
pueblo.add(h.malla(new THREE.BoxGeometry(1.8, 8, 1.8), pi, 0, 2, 0)); const tj = h.malla(new THREE.ConeGeometry(1.4, 2.6, 4), h.M('#8a5a3a'), 0, 7.3, 0); tj.rotation.y = Math.PI / 4; pueblo.add(tj);
[[0.92], [-0.92]].forEach(([z]) => pueblo.add(h.malla(new THREE.BoxGeometry(0.55, 1.1, 0.1), h.M('#1c1714'), 0, 4.6, z)));
for (let k = 0; k < 7; k++) { const w = h.malla(new THREE.BoxGeometry(2 + r() * 1.6, 1.2 + r() * 2, 0.4), h.piedra('#c4b294', 1, 1), -4 + (k % 4) * 2.6, -1.0, -3 - Math.floor(k / 4) * 3); w.rotation.y = r() * 1.5; pueblo.add(w); }
pueblo.position.set(1, 0, -12); g.add(pueblo);
return h.sombra(g);
"""

FLORES_MUSTIAS = r"""
const g = new THREE.Group(), n = o.cantidad || 12;
// flores grandes vistas de cerca, con los pétalos secos cayendo y el tallo doblado
for (let k = 0; k < n; k++) { const f = new THREE.Group(), al = 1.6 + r() * 1.0, tallo = h.M('#8a8a3a', { roughness: 0.8 });
  const dob = 0.5 + r() * 0.5; const curva = new THREE.CatmullRomCurve3([new THREE.Vector3(0, 0, 0), new THREE.Vector3(0.05, al * 0.6, 0), new THREE.Vector3(dob * 0.6, al * 0.95, 0), new THREE.Vector3(dob, al * 0.7, 0)]);
  f.add(h.malla(new THREE.TubeGeometry(curva, 16, 0.06, 6), tallo));
  const top = curva.getPoint(1), colP = ['#c96a3a', '#b8864a', '#d08a6a', '#a8603a'][k % 4];
  f.add(h.malla(new THREE.SphereGeometry(0.2, 12, 10), h.M('#5a3a1a'), top.x, top.y, top.z));
  for (let p = 0; p < 4; p++) { const pt = h.malla(new THREE.SphereGeometry(0.26, 10, 8), h.M(colP, { roughness: 0.9 }), top.x + Math.cos(p * 1.6) * 0.2, top.y - 0.25, top.z + Math.sin(p * 1.6) * 0.2); pt.scale.set(0.6, 1.4, 0.25); pt.rotation.z = Math.cos(p) * 0.6; f.add(pt); }
  for (let p = 0; p < 4; p++) { const caida = h.malla(new THREE.SphereGeometry(0.24, 8, 6), h.M(colP, { roughness: 0.9 }), (r() - 0.5) * 1.6, 0.04, (r() - 0.5) * 1.6); caida.scale.set(1.3, 0.12, 0.7); caida.rotation.y = r() * 3; f.add(caida); }
  [-1, 1].forEach(s => { const hj = h.malla(new THREE.SphereGeometry(0.22, 8, 6), h.M('#9a8a3a'), s * 0.18, al * 0.3, 0); hj.scale.set(1.8, 0.25, 0.7); hj.rotation.z = s * -0.7; f.add(hj); });
  f.position.set((r() - 0.5) * 7, 0, (r() - 0.5) * 3.5); f.rotation.y = r() * 6; g.add(f); }
return h.sombra(g);
"""

POLINIZAR = r"""
const g = new THREE.Group();
// árbol frutal en flor con una persona en una escalera polinizando a mano con un plumero
const tronco = h.M('#6a4a32', { roughness: 0.9 });
g.add(h.malla(new THREE.CylinderGeometry(0.35, 0.5, 4, 10), tronco, 0, 2, 0));
for (let k = 0; k < 6; k++) { const a = k / 6 * 6.28, ps = [new THREE.Vector3(0, 3.2, 0), new THREE.Vector3(Math.cos(a) * 1.4, 4.2, Math.sin(a) * 1.4), new THREE.Vector3(Math.cos(a) * 2.6, 5.0 + r() * 0.6, Math.sin(a) * 2.6)]; g.add(h.malla(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(ps), 10, 0.13, 6), tronco)); }
const copa = h.M('#f4c6d4', { roughness: 0.7 }), blanco = h.M('#ffffff', { roughness: 0.6 });
for (let k = 0; k < 26; k++) { const a = r() * 6.28, d = r() * 2.8; const b = h.malla(new THREE.SphereGeometry(0.6 + r() * 0.4, 12, 10), k % 3 ? copa : blanco, Math.cos(a) * d, 4.6 + r() * 1.6, Math.sin(a) * d); g.add(b); }
for (let k = 0; k < 40; k++) g.add(h.malla(new THREE.SphereGeometry(0.1, 6, 4), h.M('#f2c94c', { emissive: '#f2c94c', emissiveIntensity: 0.3 }), (r() - 0.5) * 5.4, 4.4 + r() * 2, (r() - 0.5) * 5.4 + 0.6));
// escalera
const esc = new THREE.Group(), madera = h.M('#c9a26a', { roughness: 0.8 });
[-0.4, 0.4].forEach(x => { const l = h.malla(new THREE.BoxGeometry(0.1, 4.2, 0.1), madera, x, 2.1, 0); esc.add(l); }); for (let k = 0; k < 8; k++) esc.add(h.malla(new THREE.BoxGeometry(0.8, 0.07, 0.08), madera, 0, 0.3 + k * 0.5, 0));
esc.position.set(2.0, 0, 1.6); esc.rotation.x = -0.25; g.add(esc);
// persona arriba con gorro y plumero
const p = new THREE.Group(), ropa = h.M('#2f6fd8'), piel = h.M('#e8b896');
p.add(h.malla(new THREE.CapsuleGeometry(0.3, 0.7, 4, 10), ropa, 0, 1.0, 0)); p.add(h.malla(new THREE.SphereGeometry(0.26, 14, 10), piel, 0, 1.75, 0));
p.add(h.malla(new THREE.CylinderGeometry(0.42, 0.42, 0.06, 16), h.M('#f2c94c'), 0, 1.95, 0)); p.add(h.malla(new THREE.CylinderGeometry(0.2, 0.24, 0.24, 14), h.M('#f2c94c'), 0, 2.07, 0));
[-0.15, 0.15].forEach(x => p.add(h.malla(new THREE.CapsuleGeometry(0.11, 0.6, 3, 6), h.M('#3a3a40'), x, 0.35, 0)));
const brazo = h.malla(new THREE.CapsuleGeometry(0.09, 0.7, 3, 6), ropa, -0.35, 1.45, 0.1); brazo.rotation.z = 2.3; p.add(brazo);
const palo = h.malla(new THREE.CylinderGeometry(0.03, 0.03, 1.2, 6), madera, -0.95, 2.0, 0.1); palo.rotation.z = 0.8; p.add(palo);
const plumero = h.malla(new THREE.SphereGeometry(0.18, 10, 8), h.M('#f2e6c8', { roughness: 1 }), -1.4, 2.45, 0.1); plumero.scale.set(1, 1.6, 1); p.add(plumero);
p.position.set(2.0, 2.4, 1.0); p.rotation.y = -0.9; g.add(p);
// cesta con flores recogidas
g.add(h.malla(new THREE.CylinderGeometry(0.5, 0.4, 0.5, 14), h.M('#a87a4a'), 3.6, 0.25, 2.6));
return h.sombra(g);
"""
