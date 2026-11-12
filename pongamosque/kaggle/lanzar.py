"""Lanza animar.py en Kaggle (GPU gratis), espera y baja los clips.
Uso: python3 lanzar.py <carpeta_salida> <pedido.json> [modelo]   · pedido.json = [{n, jpg (ruta), prompt, semilla}]
Necesita KAGGLE_API_TOKEN. El cuaderno es privado y se reutiliza (una versión nueva por tanda)."""
import base64, json, os, subprocess, sys, tempfile, time
AQUI = os.path.dirname(os.path.abspath(__file__))
sal, ped = sys.argv[1], json.load(open(sys.argv[2]))
modelo = sys.argv[3] if len(sys.argv) > 3 else 'Lightricks/LTX-Video-0.9.5'   # 2B: cabe en una T4 de 16 GB (el 13B no)
os.makedirs(sal, exist_ok=True)
def k(*a, **kw): return subprocess.run(['kaggle', *a], capture_output=True, text=True, **kw)
from kaggle.api.kaggle_api_extended import KaggleApi
api = KaggleApi(); api.authenticate()
usuario = api.get_config_value('username') or ''
if not usuario:   # con los tokens nuevos (KGAT_) el usuario sale de la propia API
    try: usuario = api.read_config_environment().get('username', '')
    except Exception: pass
print('usuario Kaggle:', usuario or '¿?', flush=True)
lote = [{'n': x['n'], 'jpg_b64': base64.b64encode(open(x['jpg'], 'rb').read()).decode(), 'prompt': x['prompt'],
         'semilla': x.get('semilla', 0), 'fotogramas': x.get('fotogramas', 65)} for x in ped]
cod = open(os.path.join(AQUI, 'animar.py')).read().replace('__PEDIDO__', base64.b64encode(json.dumps(lote).encode()).decode()).replace('__MODELO__', modelo)
d = tempfile.mkdtemp()
open(f'{d}/animar.py', 'w').write(cod)
ref = f'{usuario}/pongamosque-clips'
json.dump({'id': ref, 'title': 'pongamosque-clips', 'code_file': 'animar.py', 'language': 'python', 'kernel_type': 'script',
           'is_private': True, 'enable_gpu': True, 'enable_internet': True, 'machine_shape': 'NvidiaTeslaT4',
           'dataset_sources': [], 'kernel_sources': [], 'competition_sources': []}, open(f'{d}/kernel-metadata.json', 'w'))
r = k('kernels', 'push', '-p', d); print(r.stdout[-500:], r.stderr[-500:], flush=True)
if r.returncode: sys.exit('no se pudo subir el cuaderno a Kaggle')
t0, estado = time.time(), ''
while time.time() - t0 < int(os.environ.get('KAGGLE_ESPERA', '10800')):
    time.sleep(30)
    s = k('kernels', 'status', ref).stdout.strip()
    if s != estado: print(f'{time.time() - t0:.0f} s ·', s, flush=True); estado = s
    if any(x in s.lower() for x in ('complete', 'error', 'cancel')): break
r = k('kernels', 'output', ref, '-p', sal); print(r.stdout[-800:], r.stderr[-300:], flush=True)
try: print(open(f'{sal}/resumen.json').read())
except Exception: print('sin resumen: mira el registro del cuaderno en Kaggle'); sys.exit(1)
