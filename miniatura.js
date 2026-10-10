// Miniatura de YouTube (1280x720, JPG < 2 MB) pensada para el CTR:
// titular enorme de 2 líneas, Lupi grande con expresión, un dato o icono protagonista y la marca.
// Uso: node miniatura.js <carpeta> '<json>'
//   json: {"l1":"ELECCIONES","l2":"29-N","sub":"Cómo votar por correo","dato":"29","dato_sub":"NOV",
//          "icono":"calendario","color":"rojo","expr":"sorprendida","fondo":"oscuro|claro"}
// Crea <carpeta>/miniatura.jpg y miniatura.png
const fs = require('fs'), path = require('path');
let pw; try { pw = require('playwright'); } catch { pw = require('/opt/npm-tools/node_modules/playwright'); }
const KIT = __dirname, DIR = path.resolve(process.argv[2]), O = JSON.parse(process.argv[3] || '{}');
if (!fs.existsSync(path.join(KIT, 'fondo_h.jpg'))) require('child_process').execSync(`python3 "${path.join(KIT, 'fondo.py')}" h`);

const f = p => 'file://' + path.join(KIT, 'fonts', p);
const html = `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:Inter;font-weight:800;src:url('${f('Inter-ExtraBold.otf')}')}
@font-face{font-family:Inter;font-weight:900;src:url('${f('Inter-Black.otf')}')}
html,body{margin:0;background:#2a2433}#c{width:1280px;height:720px}</style></head><body><div id="c"></div>
<script>window.PROY={escenas:[]};window.TIEMPOS={escenas:[],duracion:1};window.ESCENAS=[];</script>
<script src="${path.join(KIT, 'motor.js')}"></script>
<script>
const O=${JSON.stringify(O)}, {A,lupi}=window.SH, esc=A.esc;
const COL={rojo:A.ROJ,azul:A.AZU,verde:A.VER,oro:A.ORO,naranja:A.ORA,morado:'#6b4fa3'};
const c=COL[O.color]||O.color||A.ROJ, oscuro=O.fondo!=='claro';
const tinta=oscuro?A.CRE:A.INK;
// tamaño del titular: lo más grande que quepa en 760 px
const fit=(t,max,w,min=60)=>{let s=max;while(s>min&&t.length*s*.66>w)s-=2;return s;};
const s1=fit(O.l1||'',150,760), s2=fit(O.l2||'',190,760);
let svg='<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">';
svg+=oscuro?'<rect width="1280" height="720" fill="#2a2433"/><circle cx="1010" cy="380" r="330" fill="'+c+'" opacity=".25"/>'
           :'<image href="${path.join(KIT, 'fondo_h.jpg')}" width="1280" height="720" preserveAspectRatio="xMidYMid slice"/><circle cx="1010" cy="380" r="330" fill="'+c+'" opacity=".18"/>';
// rayos detrás de Lupi (llaman la atención)
for(let i=0;i<14;i++){const a=i*Math.PI/7;svg+='<path d="M1010 380 L'+(1010+600*Math.cos(a))+' '+(380+600*Math.sin(a))+' L'+(1010+600*Math.cos(a+.12))+' '+(380+600*Math.sin(a+.12))+'Z" fill="'+(oscuro?'#fff':A.INK)+'" opacity=".05"/>';}
// titular
svg+='<text x="60" y="'+(70+s1*.82)+'" font-family="Inter" font-weight="900" font-size="'+s1+'" fill="'+tinta+'" stroke="'+A.INK+'" stroke-width="'+(oscuro?0:10)+'" paint-order="stroke">'+esc(O.l1||'')+'</text>';
const y2=70+s1*.95+s2*.86;
svg+='<text x="54" y="'+y2+'" font-family="Inter" font-weight="900" font-size="'+s2+'" fill="'+c+'" stroke="'+A.INK+'" stroke-width="14" paint-order="stroke">'+esc(O.l2||'')+'</text>';
if(O.sub){const ss=fit(O.sub,56,680,34);svg+='<rect id="subr" x="50" y="'+(y2+30)+'" width="700" height="'+(ss+34)+'" rx="16" fill="'+A.ORO+'" stroke="'+A.INK+'" stroke-width="6"/><text id="subt" x="75" y="'+(y2+30+ss+6)+'" font-family="Inter" font-weight="900" font-size="'+ss+'" fill="'+A.INK+'">'+esc(O.sub)+'</text>';}
// dato o icono protagonista junto a Lupi
if(O.icono&&A[O.icono]){svg+=O.icono==='calendario'?A.calendario(820,600,1.25,O.dato_sub||'',O.dato||'',c):A.esc_(820,600,1.4,A[O.icono](820,600,1));}
else if(O.dato){svg+=A.txtC(870,600,O.dato,150,c,'middle',14);}
// Lupi grande
svg+=lupi({x:1060,y:300,s:2.3,expr:O.expr||'sorprendida',mira:[-.7,.2],brazos:'abajo',t:.3});
// marca
svg+='<g transform="translate(60 670)"><rect x="-14" y="-38" width="250" height="52" rx="14" fill="'+A.INK+'" stroke="'+A.CRE+'" stroke-width="3"/><text x="111" y="-2" font-family="Inter" font-weight="900" font-size="30" fill="'+A.CRE+'" text-anchor="middle">sin humo TV</text></g>';
svg+='</svg>';
document.getElementById('c').innerHTML=svg;
window.ajustar=()=>{const st=document.getElementById('subt');if(st){const w=st.getBBox().width;document.getElementById('subr').setAttribute('width',w+50);}};
</script></body></html>`;
const tmp = path.join(DIR, '_miniatura.html');
fs.writeFileSync(tmp, html);
(async () => {
  const b = await pw.chromium.launch({ args: ['--disable-gpu', '--force-color-profile=srgb'] });
  const pg = await b.newPage({ viewport: { width: 1280, height: 720 } });
  await pg.goto('file://' + tmp); await pg.evaluate(() => document.fonts.ready);
  await pg.evaluate(() => window.ajustar());   // medir el texto con la fuente ya cargada
  await pg.waitForTimeout(300);
  await pg.screenshot({ path: path.join(DIR, 'miniatura.png') });
  await pg.screenshot({ path: path.join(DIR, 'miniatura.jpg'), type: 'jpeg', quality: 92 });
  await b.close(); fs.unlinkSync(tmp);
  console.log('miniatura ok', (fs.statSync(path.join(DIR, 'miniatura.jpg')).size / 1e6).toFixed(2), 'MB');
})();
