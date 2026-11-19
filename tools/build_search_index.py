#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera el índice del buscador de GTA6Encyclopedia leyendo TODAS las páginas del sitio.

Uso:  python3 tools/build_search_index.py [carpeta_del_sitio]

Crea assets/search-es.json y assets/search-en.json con:
  - cada página (título, ruta, descripción y palabras clave de todo su contenido),
  - cada ficha/tarjeta con id dentro de las páginas (vehículos, armas, animales, trofeos, personajes...),
  - cada canción de las estaciones de radio.
Lo ejecuta GitHub Actions en cada push (.github/workflows/search-index.yml), así que
cualquier página nueva o editada aparece sola en el buscador.
"""
import glob, html, json, os, re, sys, time, unicodedata

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), ".."))
TAG = re.compile(r"<[^>]+>")
STOP = set("""de la el los las y o en un una unos unas que con por para del al se su sus es son lo le les como mas más pero si no ya muy
the a an and or of to in on for with by is are be as at from it its this that into your you""".split())

def text(s):
    return re.sub(r"\s+", " ", html.unescape(TAG.sub(" ", s or ""))).strip()

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")

def keywords(main, limit=400):
    chunks = re.findall(r"<(?:h2|h3|b|li|td|th|small|span class=\"t\")[^>]*>(.*?)</", main, re.S)
    words, seen = [], set()
    for c in chunks + [main]:
        for w in re.findall(r"[\w'’\-]{2,}", norm(text(c))):
            if w in STOP or w in seen or w.isdigit() and len(w) < 3:
                continue
            seen.add(w); words.append(w)
            if len(words) >= limit:
                return " ".join(words)
    return " ".join(words)

def build(root=ROOT):
    out = {"es": [], "en": []}
    for path in sorted(glob.glob(os.path.join(root, "**", "index.html"), recursive=True)):
        h = open(path, encoding="utf-8").read()
        if 'http-equiv="refresh"' in h or 'content="noindex' in h:
            continue
        rel = os.path.relpath(os.path.dirname(path), root).replace(os.sep, "/")
        url = "/" if rel == "." else f"/{rel}/"
        if url.startswith("/tools/") or url.startswith("/.github/"):
            continue
        lang = "en" if '<html lang="en"' in h else "es"
        mt = re.search(r"<title>(.*?)</title>", h, re.S)
        title = text(mt.group(1)).replace(" | GTA 6 Encyclopedia", "") if mt else url
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S)
        title = text(h1.group(1)) if h1 else title
        md = re.search(r'<meta (?:content="([^"]*)" name="description"|name="description" content="([^"]*)")', h)
        desc = html.unescape((md.group(1) or md.group(2)) if md else "")
        mc = re.search(r'<p class="crumb">(.*?)</p>', h, re.S)
        crumb = text(mc.group(1)).split(" › ") if mc else []
        ctx = " › ".join(crumb[1:-1]) if len(crumb) > 2 else (crumb[-1] if crumb else "")
        mm = re.search(r'<main id="main">(.*?)</main>', h, re.S)
        main = mm.group(1) if mm else h
        out[lang].append({"t": title, "u": url, "c": ctx, "d": desc[:180], "k": keywords(main)})
        # fichas / tarjetas con id
        for m in re.finditer(r'<div class="item" id="([^"]+)"><div><h3>(.*?)</h3>(.*?)</div>(?:<span class="tag b-(\w+)">(.*?)</span>)?</div>', main, re.S):
            iid, t, rest, g, gl = m.groups()
            t = text(t)
            if not t or iid in ("ficha",):
                continue
            p = re.search(r"<p>(.*?)</p>", rest, re.S)
            e = {"t": t, "u": f"{url}#{iid}", "c": title, "s": text(p.group(1))[:160] if p else "", "i": 1}
            if g:
                e["g"], e["gl"] = g, text(gl)
            out[lang].append(e)
        # canciones de radio
        if "/radio/" in url and 'class="songs"' in main:
            for s in re.finditer(r'<li><span class="t"><b>(.*?)</b><small>(.*?)</small></span></li>', main):
                out[lang].append({"t": f"{text(s.group(1))} — {text(s.group(2))}", "u": f"{url}#canciones", "c": title, "s": "", "i": 1})
    os.makedirs(os.path.join(root, "assets"), exist_ok=True)
    stamp = int(time.time())
    for lang, rows in out.items():
        with open(os.path.join(root, "assets", f"search-{lang}.json"), "w", encoding="utf-8") as f:
            json.dump({"v": stamp, "n": len(rows), "items": rows}, f, ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(root, "assets", "search-version.txt"), "w") as f:
        f.write(str(stamp))
    return {k: len(v) for k, v in out.items()}

if __name__ == "__main__":
    print("Índice de búsqueda:", build())
