#!/usr/bin/env python3
"""Registro de vídeos de sin humo TV en el repositorio PRIVADO sinhumotv/sin-humo-tv-datos (barato: el archivo no pasa por la conversación).
Antes de usarlo: add_repo (owner "sinhumotv", repo "sin-humo-tv-datos", access "push").

Uso:
  python3 registro.py resumen                 → últimos 6 vídeos, créditos del mes, vídeos de hoy y filas sin métricas
  python3 registro.py anadir '<json>'          → añade una fila (claves = columnas; las que falten quedan vacías)
  python3 registro.py actualizar <fila> '<json>' → cambia campos de la fila n.º <fila> (la que muestra 'resumen'); "notas" se AÑADE
  python3 registro.py guardar "<mensaje>"      → commit y push (hace falta add_repo con access push)
La carpeta local es /home/claude/datos (se clona sola la primera vez)."""
import csv, io, json, os, subprocess, sys
from datetime import datetime
from zoneinfo import ZoneInfo

REPO = os.environ.get("REGISTRO_REPO", "https://github.com/sinhumotv/sin-humo-tv-datos")
DIR = os.environ.get("REGISTRO_DIR", "/home/claude/datos")
F = os.path.join(DIR, "registro.csv")
COLS = ["fecha", "hora_publicacion", "tema", "categoria", "tipo_gancho", "gancho", "titulo", "color_protagonista",
        "duracion_s", "creditos_voz", "youtube", "instagram", "tiktok", "visitas_24h", "notas"]
CREDITOS_MES = 30000


def git(*a, cwd=DIR):
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)


def preparar():
    if not os.path.isdir(os.path.join(DIR, ".git")):
        r = git("clone", "-q", "--depth", "1", REPO, DIR, cwd="/home/claude")
        if r.returncode: sys.exit("No se pudo clonar el registro (¿falta add_repo?): " + r.stderr[-300:])
    else:
        git("pull", "-q", "--rebase")


def leer():
    with open(F, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))


def escribir(filas):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLS, delimiter=";", lineterminator="\n", extrasaction="ignore")
    w.writeheader()
    for r in filas:
        w.writerow({c: str(r.get(c, "") or "").replace(";", ",").replace("\n", " ") for c in COLS})
    open(F, "w", encoding="utf-8").write(buf.getvalue())


def num(x):
    try: return float(str(x).replace(",", "."))
    except ValueError: return 0.0


def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    preparar()
    if not os.path.exists(F): escribir([])
    cmd, filas = sys.argv[1], leer()
    hoy = datetime.now(ZoneInfo("Europe/Madrid")).date()
    if cmd == "resumen":
        mes = [r for r in filas if r["fecha"].startswith(hoy.strftime("%Y-%m"))]
        gastado = sum(num(r["creditos_voz"]) for r in mes)
        print(f"Hoy {hoy} · vídeos hoy: {sum(r['fecha'] == str(hoy) for r in filas)} · créditos de voz gastados este mes: {gastado:.0f} · quedan ≈ {CREDITOS_MES - gastado:.0f}")
        print("Últimos 6 (n.º | fecha hora | categoría | tipo de gancho | color | título | visitas):")
        for i, r in list(enumerate(filas))[-6:]:
            print(f"  {i} | {r['fecha']} {r['hora_publicacion']} | {r['categoria']} | {r['tipo_gancho']} | {r['color_protagonista']} | {r['titulo'][:60]} | {r['visitas_24h'][:80]}")
        sin = [i for i, r in enumerate(filas) if not r["visitas_24h"] and r["hora_publicacion"] and r["fecha"] < str(hoy)]
        print("Filas publicadas sin métricas:", sin or "ninguna")
    elif cmd == "anadir":
        filas.append(json.loads(sys.argv[2])); escribir(filas); print("añadida fila", len(filas) - 1)
    elif cmd == "actualizar":
        i, cambios = int(sys.argv[2]), json.loads(sys.argv[3])
        for k, v in cambios.items():
            filas[i][k] = (filas[i].get(k, "") + " · " + v).strip(" ·") if k == "notas" else v
        escribir(filas); print("actualizada fila", i)
    elif cmd == "guardar":
        git("add", "registro.csv"); git("-c", "user.name=sin humo TV", "-c", "user.email=sinhumotv@users.noreply.github.com", "commit", "-qm", sys.argv[2] if len(sys.argv) > 2 else "registro")
        r = git("push", "-q", "origin", "HEAD")
        print("guardado" if r.returncode == 0 else "ERROR al subir: " + r.stderr[-300:])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
