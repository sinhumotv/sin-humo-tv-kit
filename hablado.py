#!/usr/bin/env python3
"""Texto hablado a prueba de voz (v23): convierte cifras, símbolos y siglas en palabras ANTES de mandar el texto
a ElevenLabs o a Gemini, para que la voz no lea "UGT" ni "1.917" a su manera.

Uso:
  python3 hablado.py <carpeta>          normaliza escenas[].hablado de <carpeta>/proyecto.json (guarda copia
                                        proyecto.antes_hablado.json), escribe <carpeta>/voz.txt (escenas separadas
                                        por una línea en blanco) y lo imprime. El texto para la voz es EXACTAMENTE voz.txt.
  python3 hablado.py <archivo.txt>      normaliza el archivo en su sitio.
  python3 hablado.py --texto "…"        imprime el texto normalizado.
Sale con código 1 (y "REVISAR: …") si queda algún dígito, símbolo o sigla en mayúsculas sin convertir.
Las siglas que no conoce las deletrea ("CNMC" → "ce ene eme ce") y las lista en "AVISO" para revisarlas.
"""
import json, os, re, subprocess, sys

try:
    from num2words import num2words
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "num2words"], check=False)
    from num2words import num2words

SIGLAS = {
    "UGT": "u ge te", "CCOO": "comisiones obreras", "PP": "pepé", "PSOE": "pesoe", "IPC": "i pe ce", "IVA": "iva",
    "OTAN": "otan", "UE": "unión europea", "EEUU": "estados unidos", "EE.UU.": "estados unidos", "EE. UU.": "estados unidos",
    "USA": "estados unidos", "UK": "reino unido", "DGT": "de ge te", "DNI": "de ene i", "NIE": "nie", "ONU": "onu",
    "IRPF": "i erre pe efe", "SMI": "ese eme i", "INE": "ine", "BOE": "boe", "CGPJ": "ce ge pe jota",
    "BCE": "be ce e", "FMI": "efe eme i", "OMS": "o eme ese", "PIB": "pe i be", "ERE": "ere", "ERTE": "erte",
    "IA": "i a", "ERC": "e erre ce", "PNV": "pe ene uve", "IU": "izquierda unida", "BNG": "be ene ge", "CUP": "cup",
    "UPN": "u pe ene", "RTVE": "erre te uve e", "TVE": "te uve e", "CIS": "cis", "AEMET": "aemet", "SEPE": "sepe",
    "OCU": "ocu", "FIFA": "fifa", "UEFA": "uefa", "NBA": "ene be a", "VTC": "uve te ce", "ITV": "i te uve",
    "DANA": "dana", "COVID": "covid", "ADN": "a de ene", "UCI": "uci", "MIR": "mir", "ESO": "eso", "EBAU": "ebau",
    "PAU": "pau", "IBEX": "ibex", "CEOE": "ce o e e", "CEPYME": "cepyme", "CNMC": "ce ene eme ce",
    "CNMV": "ce ene eme uve", "BBVA": "be be uve a", "OCDE": "o ce de e", "NASA": "nasa", "ETA": "eta",
    "TV": "te uve", "UME": "ume", "OPA": "opa", "SIDA": "sida", "VIH": "uve i hache", "ONG": "o ene ge",
    "ONGS": "o ene ges", "AVE": "ave", "RENFE": "renfe", "ADIF": "adif", "AENA": "aena", "TSJ": "te ese jota",
    "TC": "te ce", "TS": "te ese", "UCO": "uco", "CNI": "ce ene i", "PYME": "pyme", "PYMES": "pymes",
    "IBI": "ibi", "SUV": "suv", "WIFI": "wifi", "APP": "app", "EH": "e hache", "VOX": "vox", "UPV": "u pe uve",
    "UNED": "uned", "OK": "okey", "CEO": "ceo", "PDF": "pe de efe", "SMS": "ese eme ese", "LGTBI": "elegetebeí",
    "MUFACE": "muface", "SOS": "ese o ese", "FBI": "efe be i", "CIA": "cia", "G7": "ge siete", "G20": "ge veinte",
    "F1": "fórmula uno", "5G": "cinco ge", "4G": "cuatro ge", "COP": "cop", "UNICEF": "unicef", "OIT": "o i te",
}
LETRAS = dict(zip("ABCDEFGHIJKLMNÑOPQRSTUVWXYZ", ["a", "be", "ce", "de", "e", "efe", "ge", "hache", "i", "jota", "ka",
         "ele", "eme", "ene", "eñe", "o", "pe", "cu", "erre", "ese", "te", "u", "uve", "uve doble", "equis", "i griega", "zeta"]))
ORDINALES = ["", "primero", "segundo", "tercero", "cuarto", "quinto", "sexto", "séptimo", "octavo", "noveno", "décimo"]
ORD_F = ["", "primera", "segunda", "tercera", "cuarta", "quinta", "sexta", "séptima", "octava", "novena", "décima"]
MASC_EN_A = {"días", "problemas", "mapas", "programas", "sistemas", "temas", "idiomas", "planetas", "dramas", "poemas",
             "climas", "pijamas", "sofás", "papás", "tranvías", "dilemas", "esquemas", "fantasmas", "lemas", "cometas"}
FEM_OTRAS = {"personas", "veces", "horas", "mujeres", "noches", "calles", "leyes", "naves", "redes", "sedes", "llaves",
             "clases", "fuentes", "muertes", "mil", "unidades", "ciudades", "comunidades", "universidades", "sociedades"}
FEM_OTRAS.discard("mil")
AVISOS = []


def es_fem(sig):
    w = (sig or "").lower().strip(".,;:¡!¿?()\"'«»")
    if w in MASC_EN_A:
        return False
    return w.endswith(("a", "as")) or w in FEM_OTRAS or w.endswith(("ión", "iones", "dad", "dades", "tud", "tudes"))


def cardinal(n, fem=False, delante=True):
    t = num2words(n, lang="es")
    if delante:
        t = re.sub(r"\buno\b", "una" if fem else "un", t)
        t = re.sub(r"veintiuno\b", "veintiuna" if fem else "veintiún", t)
    if fem:
        ws = t.split()
        corte = max([i for i, w in enumerate(ws) if w.startswith("mill")], default=-1)
        ws = [w if i <= corte else w.replace("ientos", "ientas").replace("quinientos", "quinientas") for i, w in enumerate(ws)]
        t = " ".join(ws)
    # "un mil" no existe
    t = re.sub(r"^un mil\b", "mil", t)
    return t


def numero(txt, fem=False, delante=True):
    """txt en formato español: 1.917 · 2,5 · 1.200.000 · 0,75"""
    entero, _, dec = txt.partition(",")
    e = int(entero.replace(".", "")) if entero else 0
    if dec:
        d = dec.lstrip("0")
        ceros = " ".join(["cero"] * (len(dec) - len(d)))
        return f"{cardinal(e, fem, False)} coma {(ceros + ' ') if ceros else ''}{cardinal(int(d), False, False) if d else ''}".strip()
    return cardinal(e, fem, delante)


ROMANOS = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}


def romano(s):
    if not re.fullmatch(r"[IVXLC]+", s):
        return None
    v, prev = 0, 0
    for ch in reversed(s):
        n = ROMANOS[ch]
        v = v - n if n < prev else v + n
        prev = max(prev, n)
    return v


NUM = r"\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?"


def normaliza(t):
    t = t.replace(" ", " ").replace(" ", " ")
    t = re.sub(r"sin humo TV", "sin humo te uve", t, flags=re.I)
    # siglas con puntos
    for k in ("EE. UU.", "EE.UU."):
        t = t.replace(k, SIGLAS[k])
    # siglo XXI, Felipe VI, Juan XXIII...
    def rom(m):
        pre, r = m.group(1), m.group(2)
        v = romano(r)
        if v is None:
            return m.group(0)
        if pre.lower() in ("siglo", "siglos") or v > 10:
            return f"{pre} {cardinal(v, False, False)}"
        return f"{pre} {ORDINALES[v]}"
    t = re.sub(r"\b(siglo|siglos|[A-ZÁÉÍÓÚ][a-záéíóúñ]+)\s+([IVXLC]{1,6})\b", rom, t)
    # 24/7, horas 14:30
    t = re.sub(r"\b24\s*/\s*7\b", "veinticuatro horas, siete días", t)
    def hora(m):
        h, mi = int(m.group(1)), int(m.group(2))
        return cardinal(h, True, False) + ("" if mi == 0 else " y media" if mi == 30 else " y cuarto" if mi == 15 else " y " + cardinal(mi, False, False))
    t = re.sub(r"\b([01]?\d|2[0-3]):([0-5]\d)(\s*h\b)?", hora, t)
    # ordinales 3.º 2.ª 1º
    t = re.sub(r"\b(10|[1-9])\.?\s?º", lambda m: ORDINALES[int(m.group(1))], t)
    t = re.sub(r"\b(10|[1-9])\.?\s?ª", lambda m: ORD_F[int(m.group(1))], t)
    t = re.sub(r"\b(primero|tercero)\s+(?=[a-záéíóúñ])(?!de\b|y\b|en\b|que\b|con\b)", lambda m: m.group(1)[:-1] + " ", t)
    # cifra + % / € / $ / millones
    t = re.sub(rf"({NUM})\s*%", lambda m: numero(m.group(1), False, False) + " por ciento", t)
    def moneda(m):
        n, mult, sim = m.group(1), m.group(2), m.group(3)
        nombre = "euros" if sim == "€" else "dólares"
        if mult:
            return f"{numero(n, False, True)} {mult} de {nombre}"
        return f"{numero(n, False, True)} {nombre}" if n != "1" else f"un {nombre[:-1]}"
    t = re.sub(rf"({NUM})\s*(millones|millón|mil millones)?\s*(€|\$)", moneda, t)
    t = re.sub(rf"(€|\$)\s*({NUM})", lambda m: numero(m.group(2)) + (" euros" if m.group(1) == "€" else " dólares"), t)
    # resto de cifras, con el género de la palabra siguiente
    def cifra(m):
        sig = t_post(m)
        return numero(m.group(1), es_fem(sig), True)
    def t_post(m):
        resto = m.string[m.end():]
        w = re.match(r"\s*(de\s+)?(\w+)", resto)
        if not w:
            return ""
        return "" if (w.group(1) and w.group(2).lower().startswith("mill")) else w.group(2)
    t = re.sub(rf"(?<![\w.,])({NUM})(?![\w])", cifra, t)
    t = t.replace("%", " por ciento").replace("€", " euros").replace("&", " y ").replace("+", " más ")
    t = re.sub(r"\s*/\s*", " entre ", t)
    # siglas
    def sigla(m):
        s = m.group(0)
        if s in SIGLAS:
            return SIGLAS[s]
        if s.endswith("S") and s[:-1] in SIGLAS and len(s) > 2:
            return SIGLAS[s[:-1]] + ("s" if SIGLAS[s[:-1]][-1] in "aeiouáéíóú" else "es")
        v = romano(s)
        if v is not None and v <= 10:
            return s  # se queda para revisar (puede ser romano suelto)
        letras = " ".join(LETRAS.get(c, c.lower()) for c in s)
        AVISOS.append(f"{s} → \"{letras}\"")
        return letras
    t = re.sub(r"\b[A-ZÁÉÍÓÚÑ0-9]*[A-ZÁÉÍÓÚÑ]{2,}[A-ZÁÉÍÓÚÑ0-9]*\b", sigla, t)
    t = re.sub(r"[ \t]{2,}", " ", t)
    t = re.sub(r" +([,.;:?!])", r"\1", t)
    return t


def restos(t):
    return re.findall(r"[0-9%€$º/ª&+]|\b[A-ZÁÉÍÓÚÑ]{2,}\b", t)


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    if sys.argv[1] == "--texto":
        out = normaliza(" ".join(sys.argv[2:]))
        print(out)
    else:
        ruta = sys.argv[1]
        if os.path.isdir(ruta):
            pj = os.path.join(ruta, "proyecto.json")
            P = json.load(open(pj, encoding="utf-8"))
            copia = os.path.join(ruta, "proyecto.antes_hablado.json")
            if not os.path.exists(copia):
                json.dump(P, open(copia, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            for e in P["escenas"]:
                h = normaliza(e["hablado"]).strip()
                e["hablado"] = h[:1].upper() + h[1:]
            json.dump(P, open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            out = "\n\n".join(e["hablado"] for e in P["escenas"])
            open(os.path.join(ruta, "voz.txt"), "w", encoding="utf-8").write(out)
        else:
            out = normaliza(open(ruta, encoding="utf-8").read())
            open(ruta, "w", encoding="utf-8").write(out)
        print(out)
        print(f"\n[{len(out)} caracteres]")
    for a in AVISOS:
        print("AVISO sigla deletreada:", a)
    r = restos(out)
    if r:
        print("REVISAR: quedan sin convertir:", r)
        sys.exit(1)
    print("OK: sin cifras, símbolos ni siglas")


if __name__ == "__main__":
    main()
