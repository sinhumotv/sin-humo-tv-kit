#!/usr/bin/env python3
"""Registro de vídeos de sin humo TV.

DESDE EL 11-OCT-2026 EL REGISTRO VIVE EN GOOGLE DRIVE (las tareas programadas no pueden entrar en el repositorio privado):
archivo "registro-sin-humo-tv.csv" (CSV con ";", sin convertir a Hoja de cálculo) en la carpeta "sin humo TV"
(id 1P341VoGcSUI_frt7xhU7DFrkVUnqLZu7).
  1. Bajarlo: search_files con title = 'registro-sin-humo-tv.csv' (si hay varios, el más reciente) y download_file_content;
     guarda el contenido decodificado en /home/claude/datos/registro.csv
     (p. ej. echo '<base64>' | base64 -d > /home/claude/datos/registro.csv). Luego usa los comandos de abajo.
  2. Subirlo (tras anadir/actualizar): create_file en la carpeta, title "registro-sin-humo-tv.csv", contentMimeType "text/csv",
     disableConversionToGoogleType true, textContent = el archivo entero (cat). Cuando se haya creado bien, trash_file del anterior.
Si /home/claude/datos tiene .git (modo antiguo con add_repo de sinhumotv/sin-humo-tv-datos), sigue funcionando con git.

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
CREDITOS_MES = 30000  # ya no se usa: ver creditos_periodo()


def creditos_periodo(hoy):
    """Plan ElevenLabs Creator: se renueva el día 10. 10-oct→9-nov-2026: 145.000 (incluye 24.000 acumulados); después 121.000."""
    ini = hoy.replace(day=10) if hoy.day >= 10 else (hoy.replace(day=1) - __import__("datetime").timedelta(days=1)).replace(day=10)
    return ini, (145000 if str(ini) == "2026-10-10" else 121000)


def git(*a, cwd=DIR):
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)


def preparar():
    if not os.path.isdir(os.path.join(DIR, ".git")) and (os.environ.get("REGISTRO_DRIVE") or os.path.exists(F)):
        os.makedirs(DIR, exist_ok=True); return  # modo Drive: el CSV ya está bajado en local
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
        ini, total = creditos_periodo(hoy)
        mes = [r for r in filas if r["fecha"] >= str(ini)]
        gastado = sum(num(r["creditos_voz"]) for r in mes)
        print(f"Hoy {hoy} · vídeos hoy: {sum(r['fecha'] == str(hoy) for r in filas)} · créditos de voz gastados desde el {ini}: {gastado:.0f} de {total} · quedan ≈ {total - gastado:.0f}")
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
    elif cmd == "guardar" and not os.path.isdir(os.path.join(DIR, ".git")):
        print("Guardado en local (" + F + "). AHORA súbelo a Drive: create_file 'registro-sin-humo-tv.csv' (text/csv, sin convertir) en la carpeta 1P341VoGcSUI_frt7xhU7DFrkVUnqLZu7 y trash_file del anterior.")
    elif cmd == "guardar":
        git("add", "registro.csv"); git("-c", "user.name=sin humo TV", "-c", "user.email=sinhumotv@users.noreply.github.com", "commit", "-qm", sys.argv[2] if len(sys.argv) > 2 else "registro")
        r = git("push", "-q", "origin", "HEAD")
        print("guardado" if r.returncode == 0 else "ERROR al subir: " + r.stderr[-300:])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
