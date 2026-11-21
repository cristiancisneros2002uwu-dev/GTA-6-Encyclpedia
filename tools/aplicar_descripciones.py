#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aplica las descripciones ampliadas (meta description y og:description) a las
páginas de la lista D. Uso: python3 aplicar_descripciones.py carpeta_del_sitio"""
import html, os, re, sys, importlib.util
root = sys.argv[1]
spec = importlib.util.spec_from_file_location("d", os.path.join(os.path.dirname(os.path.abspath(__file__)), "descripciones_nuevas.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
ok = 0
for url, desc in m.D.items():
    p = os.path.join(root, url.strip("/"), "index.html")
    h = open(p, encoding="utf-8").read()
    cab, fin = h.split("</head>", 1)
    e = html.escape(desc, quote=True)
    n = 0
    for pat, tpl in ((r'<meta name="description" content="[^"]*">', '<meta name="description" content="{}">'),
                     (r'<meta content="[^"]*" name="description"/>', '<meta content="{}" name="description"/>'),
                     (r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="{}">'),
                     (r'<meta content="[^"]*" property="og:description"/>', '<meta content="{}" property="og:description"/>')):
        cab, k = re.subn(pat, lambda _m: tpl.format(e), cab, count=1); n += k
    assert n >= 1, url
    open(p, "w", encoding="utf-8").write(cab + "</head>" + fin); ok += 1
print(ok, "páginas actualizadas")
