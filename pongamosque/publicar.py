#!/usr/bin/env python3
"""Pongamos Que · publica YA en Instagram (reel), TikTok y YouTube Shorts el siguiente vídeo publicable de videos.json.
Uso: python3 publicar.py <carpeta con videos.json> <url_base_de_los_mp4>   · clave: BUFFER_KEY (cuenta de Buffer del canal)."""
import json, os, sys, urllib.request
D, BASE = sys.argv[1], sys.argv[2].rstrip('/')
videos = json.load(open(f'{D}/videos.json'))
# (13-nov-2026) FRANJAS (hora de Madrid): una sola publicación por franja. Cada franja tiene su disparo y uno de reserva
# 25 min después (GitHub a veces retrasa o se salta las tareas programadas); el de reserva no publica si ya salió.
from datetime import datetime
from zoneinfo import ZoneInfo
ahora = datetime.now(ZoneInfo('Europe/Madrid')); hm = ahora.hour * 60 + ahora.minute
franja = sum(hm >= h * 60 + m for h, m in [(11, 0), (13, 0), (15, 30), (18, 0), (20, 30)])
if franja == 0: print('fuera de horario: no se publica'); sys.exit(0)
if any(x.get('franja') == franja for x in videos): print(f'la franja {franja} ya está publicada'); sys.exit(0)
v = next((x for x in videos if x.get('publicable') and not x.get('publicado')), None)
if not v: print('no queda ningún vídeo por publicar hoy'); sys.exit(0)
def buffer(q, var=None):
    req = urllib.request.Request('https://api.buffer.com', json.dumps({'query': q, 'variables': var or {}}).encode(),
                                 {'Authorization': 'Bearer ' + os.environ['BUFFER_KEY'].strip(), 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
org = buffer('{ account { organizations { id } } }')['data']['account']['organizations'][0]['id']
canales = {c['service']: c['id'] for c in buffer('{ channels(input: {organizationId: "%s"}) { id service isDisconnected } }' % org)['data']['channels']
           if not c.get('isDisconnected')}
url, tit = f'{BASE}/{v["archivo"]}', v['titulo']
tags = ' '.join('#' + str(h).lstrip('#').replace(' ', '') for h in (['pongamosque'] + list(v.get('hashtags') or []))[:8])
txt = f"{v.get('gancho') or v['tema']}\n\n{v.get('pregunta') or '¿Tú qué harías? Te leo en comentarios'} 👇\n\n{tags}"
posts = {
    'instagram': {'text': txt[:2200], 'assets': [{'video': {'url': url, 'metadata': {'thumbnailOffset': 1500}}}],
                  'metadata': {'instagram': {'type': 'reel', 'shouldShareToFeed': True, 'isAiGenerated': True}}},
    'tiktok': {'text': (tit + '\n\n' + txt)[:2200], 'assets': [{'video': {'url': url, 'metadata': {'thumbnailOffset': 1500}}}],
               'metadata': {'tiktok': {'title': tit[:150], 'isAiGenerated': True}}},
    'youtube': {'text': txt[:4900], 'assets': [{'video': {'url': url}}],
                'metadata': {'youtube': {'title': (tit + ' #shorts')[:100], 'categoryId': '28', 'privacy': 'public',
                                         'madeForKids': False, 'notifySubscribers': True, 'isAiGenerated': True}}},
}
Q = """mutation($input: CreatePostInput!) { createPost(input: $input) { ... on PostActionSuccess { post { id status } } ... on MutationError { message } } }"""
for red, post in posts.items():
    if red not in canales: v['publicado'][red] = 'no conectado'; continue
    d = buffer(Q, {'input': {'channelId': canales[red], 'mode': 'shareNow', 'schedulingType': 'automatic', **post}})
    cp = (d.get('data') or {}).get('createPost') or {}
    v['publicado'][red] = cp['post']['id'] if 'post' in cp else 'ERROR ' + (cp.get('message') or json.dumps(d.get('errors'))[:300])
    print(red, ':', v['publicado'][red], flush=True)
v['franja'] = franja
json.dump(videos, open(f'{D}/videos.json', 'w'), ensure_ascii=False, indent=1)
print('publicado:', v['id'], v['tema'])
