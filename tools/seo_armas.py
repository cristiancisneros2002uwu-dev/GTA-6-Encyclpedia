#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reescribe el <title> y la meta descripción de las fichas de armas de
GTA6Encyclopedia (español /armas/ e inglés /en/weapons/) usando los datos
que ya muestra cada ficha: tipo, daño, cargador, alcance y precio.

Uso:  python3 tools/seo_armas.py [carpeta_del_sitio]
      python3 tools/seo_armas.py [carpeta_del_sitio] --prueba   (solo muestra, no guarda)

Solo toca fichas indexables que tienen estadísticas. Las fichas con
noindex o sin estadísticas se dejan igual. Se puede volver a correr
cada vez que se regenere el sitio.
"""
import html, os, re, sys

LIMITE = 155
LIMITE_TITULO = 60
ROOT = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("--")),
                            os.path.join(os.path.dirname(__file__), "..")))
PRUEBA = "--prueba" in sys.argv


def texto(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def ficha(h):
    m = re.search(r'<div class="item" id="ficha">(.*?)</ul>', h, re.S)
    if not m:
        return None
    return {texto(a): texto(b) for a, b in re.findall(r"<li><b>(.*?)</b><span>(.*?)</span></li>", m.group(1))}


def subtitulo(h):
    m = re.search(r'<p class="sub">(.*?)</p>', h, re.S)
    return texto(m.group(1)) if m else ""


def tipo_es(kv, sub_en):
    t, modo, s = kv.get("Tipo", ""), kv.get("Modo de disparo", ""), sub_en.lower()
    if t.startswith("Pistolas"):
        if "revolver" in s:
            return "revólver"
        if "machine pistol" in s or modo in ("Automática", "Ráfaga de 3"):
            return "pistola ametralladora"
        return "pistola"
    if t.startswith("Subfusiles"):
        return "subfusil"
    if t.startswith("Escopetas"):
        return "escopeta"
    if t.startswith("Rifles de asalto"):
        return "rifle de asalto"
    if t.startswith("Rifles tácticos"):
        return "rifle de francotirador" if modo == "Cerrojo" else "rifle táctico"
    if t.startswith("Ametralladoras"):
        return "ametralladora ligera"
    if t.startswith("Lanzagranadas"):
        return "lanzagranadas" if "grenade" in s else "lanzacohetes"
    return "arma"


def tipo_en(kv, sub_en):
    t, modo, s = kv.get("Type", ""), kv.get("Fire mode", ""), sub_en.lower()
    if t.startswith("Handguns"):
        if "revolver" in s:
            return "revolver"
        if "machine pistol" in s or modo in ("Full-auto", "3-round burst"):
            return "machine pistol"
        return "pistol"
    if t.startswith("Submachine"):
        return "SMG"
    if t.startswith("Shotguns"):
        return "shotgun"
    if t.startswith("Assault"):
        return "assault rifle"
    if t.startswith("Tactical"):
        return "sniper rifle" if modo == "Bolt action" else "tactical rifle"
    if t.startswith("Light machine"):
        return "light machine gun"
    if t.startswith("Grenade"):
        return "grenade launcher" if "grenade" in s else "rocket launcher"
    return "weapon"


def precio(kv, clave):
    m = re.search(r"\$[\d,]+", kv.get(clave, ""))
    return m.group(0) if m else None


def armar(nombre, tipo, stats, cierre):
    inicio = f"{nombre} en GTA 6: {tipo}." if cierre.startswith("y ") else f"{nombre} in GTA 6: {tipo}."
    partes = list(stats)
    while True:
        cuerpo = ", ".join(partes)
        txt = f"{inicio} {cuerpo[0].upper() + cuerpo[1:]} {cierre}" if partes else f"{inicio} {cierre[0].upper() + cierre[1:]}"
        if len(txt) <= LIMITE or not partes:
            return txt
        # quita primero el alcance, luego el cargador
        for quitar in ("alcance", "range", "cargador", "-round"):
            idx = next((i for i, p in enumerate(partes) if quitar in p), None)
            if idx is not None:
                partes.pop(idx)
                break
        else:
            partes.pop()


def corto(nombre, colas):
    """Prueba títulos de más largo a más corto hasta que quepa en LIMITE_TITULO.
    Si el nombre trae un alias entre paréntesis, lo quita del título."""
    nombres = [nombre]
    sin_alias = re.sub(r"\s*\(.*?\)", "", nombre).strip()
    if sin_alias != nombre:
        nombres.append(sin_alias)
    for n in nombres:
        for cola in colas:
            t = f"{n} {cola}"
            if len(t) <= LIMITE_TITULO:
                return t
    return f"{nombres[-1]} {colas[-1]}"


def nuevo_es(nombre, kv, sub_en):
    p = precio(kv, "Precio / cómo conseguirla")
    stats = [f"daño {kv['Daño']}", f"cargador de {kv['Cargador']}", f"alcance {kv['Alcance']}"]
    if p:
        stats.append(f"cuesta {p}")
    titulo = corto(nombre, [f"en GTA 6: {'precio' if p else 'daño'}, stats y dónde conseguirla",
                            "en GTA 6: stats y dónde conseguirla", "en GTA 6: stats y ubicación"])
    return titulo, armar(nombre, tipo_es(kv, sub_en), stats, "y dónde conseguirla.")


def nuevo_en(nombre, kv, sub_en):
    p = precio(kv, "Price / how to get it")
    stats = [f"damage {kv['Damage']}", f"{kv['Magazine']}-round mag", f"range {kv['Range']}"]
    if p:
        stats.append(f"costs {p}")
    titulo = corto(nombre, [f"in GTA 6: {'Price' if p else 'Damage'}, Stats and Where to Get It",
                            "in GTA 6: Stats and Where to Get It", "in GTA 6: Stats and Location"])
    return titulo, armar(nombre, tipo_en(kv, sub_en), stats, "and where to get it.")


def reemplazar(h, titulo, desc):
    t, d = html.escape(titulo, quote=True), html.escape(desc, quote=True)
    cab, fin = h.split("</head>", 1)
    cab = re.sub(r"<title>.*?</title>", lambda m: f"<title>{t}</title>", cab, count=1, flags=re.S)
    cab = re.sub(r'<meta name="description" content="[^"]*">', lambda m: f'<meta name="description" content="{d}">', cab, count=1)
    cab = re.sub(r'<meta property="og:title" content="[^"]*">', lambda m: f'<meta property="og:title" content="{t}">', cab, count=1)
    cab = re.sub(r'<meta property="og:description" content="[^"]*">', lambda m: f'<meta property="og:description" content="{d}">', cab, count=1)
    return cab + "</head>" + fin


def main():
    cambios, saltadas = [], []
    for slug in sorted(os.listdir(os.path.join(ROOT, "armas"))):
        ruta_es = os.path.join(ROOT, "armas", slug, "index.html")
        ruta_en = os.path.join(ROOT, "en", "weapons", slug, "index.html")
        if not (os.path.isfile(ruta_es) and os.path.isfile(ruta_en)):
            continue
        h_es = open(ruta_es, encoding="utf-8").read()
        h_en = open(ruta_en, encoding="utf-8").read()
        kv_es, kv_en = ficha(h_es), ficha(h_en)
        if not kv_es or not kv_en:
            continue  # página de categoría, no ficha
        if "noindex" in h_es.split("</head>")[0] or "Daño" not in kv_es or "Damage" not in kv_en:
            saltadas.append(slug)
            continue
        sub_en = subtitulo(h_en)
        n_es = texto(re.search(r"<h1[^>]*>(.*?)</h1>", h_es, re.S).group(1))
        n_en = texto(re.search(r"<h1[^>]*>(.*?)</h1>", h_en, re.S).group(1))
        for ruta, h, (titulo, desc) in ((ruta_es, h_es, nuevo_es(n_es, kv_es, sub_en)),
                                         (ruta_en, h_en, nuevo_en(n_en, kv_en, sub_en))):
            nuevo = reemplazar(h, titulo, desc)
            cambios.append((os.path.relpath(ruta, ROOT), titulo, desc))
            if not PRUEBA and nuevo != h:
                open(ruta, "w", encoding="utf-8").write(nuevo)
    for ruta, t, d in cambios:
        print(f"{ruta}\n  T ({len(t)}): {t}\n  D ({len(d)}): {d}")
    print(f"\n{len(cambios)} páginas {'revisadas (prueba)' if PRUEBA else 'actualizadas'}; "
          f"{len(saltadas)} fichas sin cambios (noindex o sin estadísticas).")


if __name__ == "__main__":
    main()
