"""Guardar líneas en el registro (rama "datos") sin perder nada cuando varios canales guardan a la vez.

Los tres canales se ejecutan en paralelo y cada uno añade líneas a SU archivo de la rama datos. Antes, si dos
hacían push a la vez, el segundo se rechazaba en silencio y su registro se perdía (por eso la repesca rehacía
vídeos ya publicados y se repetían temas). Ahora: clon nuevo -> añadir las líneas -> commit -> push, y si el
push se rechaza, se repite desde un clon nuevo (hasta 8 veces).
"""
import os, random, shutil, subprocess, tempfile, time


def _sh(c, cwd=None):
    return subprocess.run(c, shell=True, capture_output=True, text=True, cwd=cwd)


def anadir(repo_url, archivo, lineas, autor, mensaje):
    """Añade `lineas` (lista de str sin salto final) al final de <archivo> en la rama datos. Devuelve True si quedó guardado."""
    lineas = [l.rstrip("\n") for l in lineas if l.strip()]
    if not lineas:
        return True
    for intento in range(8):
        tmp = tempfile.mkdtemp(prefix="datos-")
        try:
            r = _sh(f"git clone -q --depth 1 --branch datos {repo_url} {tmp}/d")
            d = f"{tmp}/d"
            if r.returncode:
                os.makedirs(d, exist_ok=True)
                _sh("git init -q && git checkout -q --orphan datos", cwd=d)
            p = os.path.join(d, archivo)
            previas = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
            nuevas = [l for l in lineas if l not in previas.splitlines()]
            if not nuevas:
                return True
            with open(p, "a", encoding="utf-8") as f:
                if previas and not previas.endswith("\n"):
                    f.write("\n")
                f.write("\n".join(nuevas) + "\n")
            _sh(f'git add "{archivo}" && git -c user.name="{autor}" -c user.email="sinhumotv@users.noreply.github.com" '
                f'commit -qm "{mensaje}"', cwd=d)
            if _sh(f"git push -q {repo_url} HEAD:datos", cwd=d).returncode == 0:
                return True
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        time.sleep(3 + random.uniform(0, 6) * (intento + 1))
    print("AVISO: no se pudo guardar el registro", archivo)
    return False
