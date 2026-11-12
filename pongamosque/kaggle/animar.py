# (12-nov-2026) Pongamos Que · clips IA en la GPU GRATIS de Kaggle. Lo sube y lanza GitHub (pongamosque/kaggle/lanzar.py).
# Entrada: PEDIDO (más abajo, lo rellena lanzar.py) = [{n, jpg_b64, prompt, semilla}] → /kaggle/working/NN_ia.mp4 + resumen.json
import base64, io, json, os, subprocess, sys, time
t0 = time.time()
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'diffusers==0.35.1', 'transformers==4.56.2', 'accelerate', 'sentencepiece', 'imageio', 'imageio-ffmpeg'], check=True)
import torch, numpy as np
from PIL import Image, ImageOps
from diffusers import LTXConditionPipeline
from diffusers.pipelines.ltx.pipeline_ltx_condition import LTXVideoCondition
from diffusers.utils import export_to_video, load_video
PEDIDO = json.loads(base64.b64decode('__PEDIDO__'))
MODELO = os.environ.get('LTX_MODELO', '__MODELO__')
n_gpu = torch.cuda.device_count()
print('GPU:', [torch.cuda.get_device_name(i) for i in range(n_gpu)], flush=True)
dt = torch.float16 if not torch.cuda.is_bf16_supported() else torch.bfloat16
pipe = LTXConditionPipeline.from_pretrained(MODELO, torch_dtype=dt)
if n_gpu > 1:   # T4 x2: el codificador de texto en la segunda GPU, el resto en la primera
    pipe.text_encoder.to('cuda:1'); pipe.transformer.to('cuda:0'); pipe.vae.to('cuda:0')
    _enc = pipe.encode_prompt
    def enc(*a, **k):
        k['device'] = torch.device('cuda:1'); r = _enc(*a, **k)
        return tuple(x.to('cuda:0') if torch.is_tensor(x) else x for x in r)
    pipe.encode_prompt = enc
else:
    pipe.enable_model_cpu_offload()
pipe.vae.enable_tiling()
print(f'modelo {MODELO} cargado en {time.time() - t0:.0f} s · {dt}', flush=True)
NEG = 'worst quality, inconsistent motion, blurry, jittery, distorted, static, frozen, morphing, deformed, text, watermark'
res = []
for it in PEDIDO:
    t1 = time.time()
    try:
        im = Image.open(io.BytesIO(base64.b64decode(it['jpg_b64']))).convert('RGB')
        W, H = (544, 960) if im.height >= im.width else (960, 544)
        im = ImageOps.fit(im, (W, H), Image.LANCZOS)
        f0 = f'/tmp/c{it["n"]}.mp4'; export_to_video([im], f0, fps=24)
        kw = dict(conditions=[LTXVideoCondition(video=load_video(f0), frame_index=0)], prompt=it['prompt'], negative_prompt=NEG,
                  width=W, height=H, num_frames=int(it.get('fotogramas', 97)), frame_rate=24, decode_timestep=0.05, decode_noise_scale=0.025,
                  image_cond_noise_scale=0.0, generator=torch.Generator('cuda:0' if n_gpu else 'cpu').manual_seed(int(it.get('semilla', 0))))
        if 'distilled' in MODELO:
            fr = pipe(timesteps=[1000, 993, 987, 981, 975, 909, 725, 0.03], guidance_scale=1.0, **kw).frames[0]
        else:
            fr = pipe(num_inference_steps=int(os.environ.get('LTX_PASOS', '30')), guidance_scale=3.0, **kw).frames[0]
        mov = float(np.abs(np.asarray(fr[-1].convert('L'), np.float32) - np.asarray(fr[0].convert('L'), np.float32)).mean())
        export_to_video(fr, f'/kaggle/working/{it["n"]:02d}_ia.mp4', fps=24)
        res.append({'n': it['n'], 'ok': True, 's': round(time.time() - t1), 'mov': round(mov, 1)})
    except Exception as x:
        res.append({'n': it['n'], 'ok': False, 'error': str(x)[:300]})
    print(res[-1], flush=True)
json.dump({'clips': res, 'segundos': round(time.time() - t0), 'modelo': MODELO}, open('/kaggle/working/resumen.json', 'w'))
print('FIN', round(time.time() - t0), 's', flush=True)
