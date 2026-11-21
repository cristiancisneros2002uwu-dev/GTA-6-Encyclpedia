#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reescribe el <title> y la meta descripción de las fichas de vehículos de
GTA6Encyclopedia (español /vehiculos/ e inglés /en/vehicles/) con los datos
de cada ficha: tipo, modelo real en que se inspira y cómo conseguirlo.
También corrige textos en español que se colaron en las páginas en inglés
(por ejemplo «Clase G» o «Carrito de golf»).

Uso:  python3 tools/seo_vehiculos.py [carpeta_del_sitio] [--prueba]

Solo cambia fichas indexables. Se puede volver a correr después de
regenerar el sitio.
"""
import html, os, re, sys

LIMITE, LIMITE_TITULO = 155, 60
ROOT = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("--")),
                            os.path.join(os.path.dirname(__file__), "..")))
PRUEBA = "--prueba" in sys.argv

# Textos en español dentro de las páginas en inglés -> inglés
TRADUCCIONES_EN = {
    "Mercedes-Benz Clase G": "Mercedes-Benz G-Class",
    "Scooter de movilidad Pride Maxima": "Pride Maxima mobility scooter",
    "DHC-2 Beaver (hidroavión)": "DHC-2 Beaver (seaplane)",
    "Carrito de golf": "Golf cart",
    "Caza militar": "Military fighter jet",
}
GEN = re.compile(r"(\d+)ª gen")


def ordinal(m):
    n = int(m.group(1))
    suf = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf} gen"


def a_ingles(s):
    for a, b in TRADUCCIONES_EN.items():
        s = s.replace(a, b)
    return GEN.sub(ordinal, s)


FEMENINOS = ("Motocicleta", "SUV", "Embarcación", "Pickup", "Van", "Bicicleta")
SIGLAS = ("SUV", "BMX")


def texto(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def ficha(h):
    m = re.search(r'<div class="item" id="ficha">(.*?)</ul>', h, re.S)
    if not m:
        return None
    return {texto(a): texto(b) for a, b in re.findall(r"<li><b>(.*?)</b><span>(.*?)</span></li>", m.group(1))}


def minus(s):
    return s if s.split(" ")[0] in SIGLAS else s[0].lower() + s[1:]


def frase(s):
    s = s.strip().rstrip(".")
    return s[0].upper() + s[1:] + "."


def conseguir_es(kv, fem):
    c, n = kv.get("Cómo conseguirlo", ""), kv.get("Notas", "")
    m = re.match(r"Truco(?: [^:]+)?:\s*(.+)", c)
    if m:
        return frase(f"Se consigue con un truco: {m.group(1)}")
    if c:
        return frase(c)
    if n.startswith("Quest "):
        return frase(f"Aparece en la misión {n[6:]}")
    if n.startswith("Misión "):
        return frase(f"Aparece en la misión {n[7:]}")
    if n.startswith("Exclusivo Ultimate Edition"):
        return f"Exclusiv{'a' if fem else 'o'} de la Ultimate Edition."
    if n.startswith("Ultimate Edition"):
        return frase(f"Incluid{'a' if fem else 'o'} en la {n}")
    return ""


def conseguir_en(kv):
    c, n = kv.get("How to get it", ""), kv.get("Notes", "")
    m = re.match(r"(?:[^:]+ )?[Cc]heat:\s*(.+)", c)
    if m:
        return frase(f"Unlocked with a cheat: {m.group(1)}")
    if c:
        return frase(c)
    if n.endswith("quest (Ultimate Edition)"):
        return frase(f"Appears in the {n}")
    if n.startswith("Mission "):
        return frase(f"Appears in the mission {n[8:]}")
    if n.startswith("Ultimate Edition exclusive"):
        return "Ultimate Edition exclusive."
    if n.startswith("Ultimate Edition"):
        return frase(f"Included in the {n}")
    return ""


def corto(nombre, colas):
    for cola in colas:
        t = f"{nombre} {cola}"
        if len(t) <= LIMITE_TITULO:
            return t
    return f"{nombre} {colas[-1]}"


def ajustar(inicio_largo, inicio_corto, cola):
    """Prueba: con modelo real + cola; sin modelo real + cola; con modelo real solo."""
    primera = cola.split(". ")[0].rstrip(".") + "."
    for txt in (f"{inicio_largo}. {cola}", f"{inicio_corto}. {cola}",
                f"{inicio_largo}. {primera}", f"{inicio_corto}. {primera}", f"{inicio_largo}."):
        if len(txt) <= LIMITE:
            return txt
    return f"{inicio_corto}."


def nuevo_es(nombre, kv):
    tipo = kv.get("Tipo", "Vehículo")
    fem = tipo.startswith(FEMENINOS)
    insp = kv.get("Inspirado en")
    marca = kv.get("Marca")
    inicio = f"{nombre} en GTA 6: {minus(tipo)}"
    if marca and marca.lower() not in nombre.lower():
        inicio += f" de {marca}"
    corto_ini = inicio
    if insp:
        genericos = {"Carrito de golf": "un carrito de golf", "Caza militar": "un caza militar"}
        inicio += f" inspirad{'a' if fem else 'o'} en {genericos.get(insp, insp)}"
    get = conseguir_es(kv, fem)
    cola = get or "Ficha con su categoría, marca y modelo real."
    lo = "la" if fem else "lo"
    if get and insp:
        colas = [f"en GTA 6: cómo conseguir{lo} y modelo real", f"en GTA 6: cómo conseguir{lo}"]
    elif get:
        colas = [f"en GTA 6: cómo conseguir{lo}", "en GTA 6"]
    elif insp:
        colas = ["en GTA 6: ficha y modelo real", "en GTA 6: modelo real", "en GTA 6"]
    else:
        colas = ["en GTA 6: ficha del vehículo", "en GTA 6"]
    return corto(nombre, colas), ajustar(inicio, corto_ini, cola)


def nuevo_en(nombre, kv):
    tipo = kv.get("Type", "Vehicle")
    insp = kv.get("Inspired by")
    if insp:
        insp = a_ingles(insp)
    marca = kv.get("Brand")
    inicio = f"{nombre} in GTA 6: {minus(tipo)}"
    if marca and marca.lower() not in nombre.lower():
        inicio += f" by {marca}"
    corto_ini = inicio
    if insp:
        genericos = {"Golf cart": "a golf cart", "Military fighter jet": "a military fighter jet"}
        inicio += f" based on {genericos.get(insp, 'the ' + insp)}"
    get = conseguir_en(kv)
    cola = get or "Profile with its class, brand and real-life model."
    if get and insp:
        colas = ["in GTA 6: How to Get It and Real-Life Model", "in GTA 6: How to Get It"]
    elif get:
        colas = ["in GTA 6: How to Get It", "in GTA 6"]
    elif insp:
        colas = ["in GTA 6: Profile and Real-Life Model", "in GTA 6: Real-Life Model", "in GTA 6"]
    else:
        colas = ["in GTA 6: Vehicle Profile", "in GTA 6"]
    return corto(nombre, colas), ajustar(inicio, corto_ini, cola)


def reemplazar(h, titulo, desc):
    t, d = html.escape(titulo, quote=True), html.escape(desc, quote=True)
    cab, fin = h.split("</head>", 1)
    cab = re.sub(r"<title>.*?</title>", lambda m: f"<title>{t}</title>", cab, count=1, flags=re.S)
    cab = re.sub(r'<meta name="description" content="[^"]*">', lambda m: f'<meta name="description" content="{d}">', cab, count=1)
    cab = re.sub(r'<meta property="og:title" content="[^"]*">', lambda m: f'<meta property="og:title" content="{t}">', cab, count=1)
    cab = re.sub(r'<meta property="og:description" content="[^"]*">', lambda m: f'<meta property="og:description" content="{d}">', cab, count=1)
    return cab + "</head>" + fin


def traducir_en(h):
    return a_ingles(h)


def main():
    cambios, traducidas = [], 0
    # 1) textos en español dentro de /en/
    for d, _, fs in os.walk(os.path.join(ROOT, "en")):
        if "index.html" not in fs:
            continue
        p = os.path.join(d, "index.html")
        h = open(p, encoding="utf-8").read()
        n = traducir_en(h)
        if n != h:
            traducidas += 1
            if not PRUEBA:
                open(p, "w", encoding="utf-8").write(n)
    # 2) títulos y descripciones
    for slug in sorted(os.listdir(os.path.join(ROOT, "vehiculos"))):
        r_es = os.path.join(ROOT, "vehiculos", slug, "index.html")
        r_en = os.path.join(ROOT, "en", "vehicles", slug, "index.html")
        if not (os.path.isfile(r_es) and os.path.isfile(r_en)):
            continue
        for ruta, fn in ((r_es, nuevo_es), (r_en, nuevo_en)):
            h = open(ruta, encoding="utf-8").read()
            kv = ficha(h)
            if not kv or "noindex" in h.split("</head>")[0]:
                continue
            nombre = texto(re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S).group(1))
            titulo, desc = fn(nombre, kv)
            cambios.append((os.path.relpath(ruta, ROOT), titulo, desc))
            if not PRUEBA:
                open(ruta, "w", encoding="utf-8").write(reemplazar(h, titulo, desc))
    for ruta, t, d in cambios:
        print(f"{ruta}\n  T ({len(t)}): {t}\n  D ({len(d)}): {d}")
    print(f"\n{len(cambios)} fichas {'revisadas (prueba)' if PRUEBA else 'actualizadas'}; "
          f"{traducidas} páginas en inglés con textos en español corregidos.")


if __name__ == "__main__":
    main()
