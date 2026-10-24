#!/usr/bin/env python3
"""Programa en YouTube, con la cuenta de Metricool de un canal, un vídeo largo descrito en un JSON.

Uso: python3 publicar_largo.py <canal> <publicacion.json>
publicacion.json: {"video": url mp4, "miniatura": url jpg, "titulo": "...", "descripcion": "...",
                   "etiquetas": [...], "categoria": "NEWS_POLITICS", "fecha": "AAAA-MM-DDTHH:MM" (hora de Madrid)
                   o "ahora" (en 10 minutos)}
Variables: REFRESH (secreto METRICOOL_<CANAL>_REFRESH), GH_SECRETOS.
"""
import datetime as dt, json, os, sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mc

canal, P = sys.argv[1], json.load(open(sys.argv[2], encoding="utf-8"))
MAD = ZoneInfo("Europe/Madrid")
ahora = dt.datetime.now(MAD)
if P.get("fecha", "ahora") == "ahora":
    cuando = ahora + dt.timedelta(minutes=10)
else:
    cuando = dt.datetime.fromisoformat(P["fecha"]).replace(tzinfo=MAD)
    if cuando < ahora + dt.timedelta(minutes=5):
        cuando = ahora + dt.timedelta(minutes=10)
s = mc.Sesion(mc.acceso(canal))
marca = mc.marca(s)
info = {"autoPublish": True, "draft": False, "descendants": [], "firstCommentText": "", "hasNotReadNotes": False,
        "media": [P["video"]], "mediaAltText": [], "providers": [{"network": "youtube"}],
        "publicationDate": {"dateTime": cuando.strftime("%Y-%m-%dT%H:%M:00"), "timezone": "Europe/Madrid"},
        "shortener": False, "smartLinkData": {"ids": []}, "text": P["descripcion"][:4900],
        "youtubeData": {"title": P["titulo"][:100], "type": "video", "privacy": "public",
                        "tags": (P.get("etiquetas") or [])[:15], "category": P.get("categoria", "NEWS_POLITICS"),
                        "madeForKids": False, "isAiGeneratedContent": True}}
if P.get("miniatura"):
    info["videoThumbnailUrl"] = P["miniatura"]
args = {"date": cuando.isoformat(timespec="seconds"), "blogId": str(marca["id"]), "info": json.dumps(info, ensure_ascii=False)}
try:
    res = s.llamar("createScheduledPost", args)
except RuntimeError as e:
    if "THUMBNAIL" not in str(e).upper():
        raise
    print("Metricool no acepta la miniatura: se publica sin ella")
    info.pop("videoThumbnailUrl", None)
    args["info"] = json.dumps(info, ensure_ascii=False)
    res = s.llamar("createScheduledPost", args)
print("METRICOOL:", json.dumps(res, ensure_ascii=False)[:300])
print(f"PROGRAMADO · {canal} · {cuando:%d/%m %H:%M} · «{P['titulo']}»")
