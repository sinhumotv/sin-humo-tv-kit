# (13-nov-2026) Pongamos Que · clips IA en la GPU GRATIS de Kaggle (2 x T4 de 15 GB). Lo sube y lanza lanzar.py.
# 1) los textos se codifican primero (T5) y se libera su memoria; 2) cada GPU lleva su copia del modelo y anima la mitad
# de los clips a la vez; 3) se prueba primero un modelo DESTILADO (8 pasos) y, si no existe, el normal con menos pasos.
import base64, io, json, os, subprocess, sys, threading, time
t0 = time.time()
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'diffusers==0.35.1', 'transformers==4.56.2', 'accelerate', 'sentencepiece', 'imageio', 'imageio-ffmpeg'], check=True)
import torch, numpy as np
from PIL import Image, ImageOps
from diffusers import LTXConditionPipeline
from diffusers.pipelines.ltx.pipeline_ltx_condition import LTXVideoCondition
from diffusers.utils import export_to_video, load_video
PEDIDO = json.loads(base64.b64decode('__PEDIDO__'))
CANDIDATOS = [m for m in '__MODELO__'.split(',') if m]
NEG = 'worst quality, inconsistent motion, blurry, jittery, distorted, static, frozen, morphing, deformed, text, watermark'
n_gpu = torch.cuda.device_count(); dt = torch.float16
print('GPU:', [torch.cuda.get_device_name(i) for i in range(n_gpu)], flush=True)
pipe, modelo = None, ''
for m in CANDIDATOS:
    try:
        pipe = LTXConditionPipeline.from_pretrained(m, torch_dtype=dt); modelo = m; break
    except Exception as x:
        print('modelo no disponible:', m, str(x)[:160], flush=True)
destilado = 'distill' in modelo
print(f'modelo {modelo} cargado en {time.time() - t0:.0f} s', flush=True)
# 1) textos: todos de una vez en la GPU 0, y fuera el codificador (9,5 GB)
pipe.text_encoder.to('cuda:0')
emb = {}
with torch.no_grad():
    for it in PEDIDO:
        pe, pm, ne, nm = pipe.encode_prompt(it['prompt'], NEG, do_classifier_free_guidance=not destilado, device=torch.device('cuda:0'))
        emb[it['n']] = [x.cpu() if x is not None else None for x in (pe, pm, ne, nm)]
pipe.text_encoder.to('cpu'); del pipe.text_encoder; pipe.text_encoder = None; torch.cuda.empty_cache()
# 2) una copia del modelo por GPU
import copy
pipes = [pipe] + [copy.deepcopy(pipe) for _ in range(max(0, n_gpu - 1))]
for g, p in enumerate(pipes):
    p.transformer.to(f'cuda:{g}'); p.vae.to(f'cuda:{g}'); p.vae.enable_tiling()
    type(p)._execution_device = property(lambda self: next(self.transformer.parameters()).device)
print(f'listo en {time.time() - t0:.0f} s · {len(pipes)} GPU · {"destilado, 8 pasos" if destilado else "normal"}', flush=True)
res, cerrojo = [], threading.Lock()
def trabajar(g, lote):
    p, dev = pipes[g], torch.device(f'cuda:{g}')
    for it in lote:
        t1 = time.time()
        try:
            if it.get('url'):
                import urllib.request
                datos = urllib.request.urlopen(urllib.request.Request(it['url'], headers={'User-Agent': 'pongamosque'}), timeout=60).read()
            else:
                datos = base64.b64decode(it['jpg_b64'])
            im = Image.open(io.BytesIO(datos)).convert('RGB')
            W, H = (448, 800) if im.height >= im.width else (800, 448)
            im = ImageOps.fit(im, (W, H), Image.LANCZOS)
            f0 = f'/tmp/c{it["n"]}.mp4'; export_to_video([im], f0, fps=24)
            pe, pm, ne, nm = [x.to(dev) if x is not None else None for x in emb[it['n']]]
            kw = dict(conditions=[LTXVideoCondition(video=load_video(f0), frame_index=0)], prompt_embeds=pe, prompt_attention_mask=pm,
                      width=W, height=H, num_frames=int(it.get('fotogramas', 65)), frame_rate=24, decode_timestep=0.05, decode_noise_scale=0.025,
                      image_cond_noise_scale=0.0, generator=torch.Generator(dev).manual_seed(int(it.get('semilla', 0))))
            if destilado:
                fr = p(timesteps=[1000, 993, 987, 981, 975, 909, 725, 0.03], guidance_scale=1.0, **kw).frames[0]
            else:
                fr = p(negative_prompt_embeds=ne, negative_prompt_attention_mask=nm, num_inference_steps=int(os.environ.get('LTX_PASOS', '20')),
                       guidance_scale=3.0, **kw).frames[0]
            mov = float(np.abs(np.asarray(fr[-1].convert('L'), np.float32) - np.asarray(fr[0].convert('L'), np.float32)).mean())
            export_to_video(fr, f'/kaggle/working/{it["n"]:02d}_ia.mp4', fps=24)
            r = {'n': it['n'], 'ok': True, 's': round(time.time() - t1), 'mov': round(mov, 1), 'gpu': g}
        except Exception as x:
            r = {'n': it['n'], 'ok': False, 'error': str(x)[:300], 'gpu': g}
        torch.cuda.empty_cache()
        with cerrojo: res.append(r)
        print(r, flush=True)
hilos = [threading.Thread(target=trabajar, args=(g, PEDIDO[g::len(pipes)])) for g in range(len(pipes))]
[h.start() for h in hilos]; [h.join() for h in hilos]
json.dump({'clips': sorted(res, key=lambda r: r['n']), 'segundos': round(time.time() - t0), 'modelo': modelo}, open('/kaggle/working/resumen.json', 'w'))
print('FIN', round(time.time() - t0), 's', flush=True)
