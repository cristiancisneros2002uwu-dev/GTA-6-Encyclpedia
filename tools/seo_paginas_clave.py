#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aplica título, meta descripción y primer párrafo (p.sub) a las páginas con
más impresiones en Search Console, en inglés y español, usando
tools/seo_paginas_clave.json (llave = ruta en inglés; la ruta en español se
toma del hreflang="es" de la página en inglés).

Uso:  python3 tools/seo_paginas_clave.py [carpeta_del_sitio]
      python3 tools/seo_paginas_clave.py [carpeta_del_sitio] --prueba   (solo muestra, no guarda)
"""
import html, json, os, re, sys

ROOT = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("--")),
                            os.path.join(os.path.dirname(__file__), "..")))
PRUEBA = "--prueba" in sys.argv
DATOS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "seo_paginas_clave.json"), encoding="utf-8"))


def archivo(ruta):
    return os.path.join(ROOT, ruta.strip("/"), "index.html")


def aplicar(ruta, d):
    p = archivo(ruta)
    h = open(p, encoding="utf-8").read()
    cab, cuerpo = h.split("</head>", 1)
    t = html.escape(d["title"], quote=True)
    e = html.escape(d["description"], quote=True)
    n = 0
    for pat, rep in ((r"<title>.*?</title>", f"<title>{t}</title>"),
                     (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{t}">'),
                     (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{e}">'),
                     (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{e}">'),
                     (r'<meta content="[^"]*" property="og:title"/>', f'<meta content="{t}" property="og:title"/>'),
                     (r'<meta content="[^"]*" name="description"/>', f'<meta content="{e}" name="description"/>'),
                     (r'<meta content="[^"]*" property="og:description"/>', f'<meta content="{e}" property="og:description"/>')):
        cab, k = re.subn(pat, lambda _m: rep, cab, count=1, flags=re.S); n += k
    i = html.escape(d["intro"], quote=False)
    cuerpo, k = re.subn(r'(</h1>\s*<p class="sub">).*?(</p>)', lambda m: m.group(1) + i + m.group(2), cuerpo, count=1, flags=re.S)
    n += k
    assert n == 5, f"{ruta}: solo {n} de 5 reemplazos"
    if not PRUEBA:
        open(p, "w", encoding="utf-8").write(cab + "</head>" + cuerpo)
    print(("[prueba] " if PRUEBA else "") + ruta, "->", d["title"])


ok = 0
for ruta_en, v in DATOS.items():
    if ruta_en.startswith("_"):
        continue
    h = open(archivo(ruta_en), encoding="utf-8").read()
    m = re.search(r'<link rel="alternate" hreflang="es" href="https://gta6encyclopedia\.com(/[^"]*)">', h)
    ruta_es = v.get("ruta_es") or (m and m.group(1))
    assert ruta_es, f"{ruta_en}: sin ruta en español"
    aplicar(ruta_en, v["en"]); aplicar(ruta_es, v["es"]); ok += 2
print(ok, "páginas actualizadas")
