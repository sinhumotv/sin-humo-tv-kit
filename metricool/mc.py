#!/usr/bin/env python3
"""Conexión propia con el MCP oficial de Metricool (OAuth), una cuenta por canal, sin Claude.

Los accesos se guardan SOLO como secretos de GitHub (METRICOOL_<CANAL>_REFRESH) y se renuevan en cada uso
(Metricool cambia el refresh token cada vez): el nuevo se vuelve a guardar con el token GH_SECRETOS.

Uso:
  python3 mc.py enlaces relatos cajanegra ano2100   -> crea los PKCE (secretos) e imprime los enlaces de autorización
  python3 mc.py canjear <canal> <code o url>        -> canjea el código y guarda el acceso (variables: PKCE)
  python3 mc.py probar <canal>                      -> comprueba el acceso (variable: REFRESH)
"""
import base64, hashlib, json, os, re, secrets, subprocess, sys, urllib.parse, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
CLIENTE = json.load(open(os.path.join(AQUI, "cliente.json")))["client_id"]
REDIR = "http://localhost:8765/callback"
TOKEN_URL = "https://app.metricool.com/oauth/token"
MCP = "https://ai.metricool.com/mcp"
REPO = "sinhumotv/sin-humo-tv-kit"


def guardar_secreto(nombre, valor):
    r = subprocess.run(["gh", "secret", "set", nombre, "-R", REPO], input=valor, text=True, capture_output=True,
                       env={**os.environ, "GH_TOKEN": os.environ["GH_SECRETOS"]})
    if r.returncode:
        raise SystemExit(f"No se pudo guardar el secreto {nombre}: {r.stderr[-300:]}")


def _token(datos):
    req = urllib.request.Request(TOKEN_URL, urllib.parse.urlencode(datos).encode(),
                                 {"Content-Type": "application/x-www-form-urlencoded"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Metricool rechaza el acceso ({e.code}): {e.read()[:200]!r}")


def acceso(canal):
    """Devuelve un access token válido y guarda el refresh token nuevo."""
    t = _token({"grant_type": "refresh_token", "refresh_token": os.environ["REFRESH"].strip(), "client_id": CLIENTE})
    guardar_secreto(f"METRICOOL_{canal.upper()}_REFRESH", t["refresh_token"])
    return t["access_token"]


class Sesion:
    def __init__(self, access):
        self.h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
                  "Authorization": "Bearer " + access}
        self.i = 0
        _, sid = self._post({"jsonrpc": "2.0", "id": 0, "method": "initialize",
                             "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                                        "clientInfo": {"name": "publicador-largos", "version": "1"}}})
        if sid:
            self.h["Mcp-Session-Id"] = sid
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def _post(self, cuerpo):
        r = urllib.request.urlopen(urllib.request.Request(MCP, json.dumps(cuerpo).encode(), self.h), timeout=180)
        return r.read().decode(), r.headers.get("Mcp-Session-Id")

    def llamar(self, herramienta, args):
        self.i += 1
        txt, _ = self._post({"jsonrpc": "2.0", "id": self.i, "method": "tools/call",
                             "params": {"name": herramienta, "arguments": args}})
        if "data:" in txt:
            txt = [l[5:] for l in txt.splitlines() if l.startswith("data:")][-1]
        res = json.loads(txt)
        if "error" in res:
            raise RuntimeError(json.dumps(res["error"])[:500])
        cont = res["result"].get("content", [{}])[0].get("text", "")
        if res["result"].get("isError"):
            raise RuntimeError(cont[:500])
        try:
            return json.loads(cont)
        except Exception:
            return cont


def marca(s):
    d = s.llamar("getBrandSettings", {})
    d = d.get("data", d) if isinstance(d, dict) else d
    return d[0] if isinstance(d, list) else d


if __name__ == "__main__":
    paso = sys.argv[1]
    if paso == "enlaces":
        for canal in sys.argv[2:]:
            v = secrets.token_urlsafe(48)
            guardar_secreto(f"METRICOOL_{canal.upper()}_PKCE", v)
            ch = base64.urlsafe_b64encode(hashlib.sha256(v.encode()).digest()).rstrip(b"=").decode()
            q = urllib.parse.urlencode({"response_type": "code", "client_id": CLIENTE, "redirect_uri": REDIR,
                                        "scope": "mcp:read mcp:write", "state": canal, "code_challenge": ch,
                                        "code_challenge_method": "S256", "resource": MCP})
            print(f"ENLACE {canal} https://app.metricool.com/oauth/authorize?{q}")
    elif paso == "canjear":
        canal, code = sys.argv[2], sys.argv[3]
        m = re.search(r"code=([^&\s]+)", code)
        code = urllib.parse.unquote(m.group(1)) if m else code.strip()
        t = _token({"grant_type": "authorization_code", "code": code, "redirect_uri": REDIR, "client_id": CLIENTE,
                    "code_verifier": os.environ["PKCE"].strip(), "resource": MCP})
        guardar_secreto(f"METRICOOL_{canal.upper()}_REFRESH", t["refresh_token"])
        b = marca(Sesion(t["access_token"]))
        print(f"CONECTADO {canal}: cuenta {b.get('ownerUsername')} · marca {b.get('id')} · YouTube {b.get('networksData', {}).get('youtubeData')}")
    elif paso == "probar":
        canal = sys.argv[2]
        b = marca(Sesion(acceso(canal)))
        print(f"OK {canal}: marca {b.get('id')} · YouTube {b.get('networksData', {}).get('youtubeData')}")
