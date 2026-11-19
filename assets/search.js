/* Buscador de GTA6Encyclopedia
   - Busca en TODO el sitio: páginas, fichas (vehículos, armas, animales, trofeos, personajes...) y canciones.
   - El índice (/assets/search-es.json y search-en.json) se regenera solo en cada push con GitHub Actions,
     y el navegador siempre comprueba si hay una versión nueva (cache: no-cache).
   - Tolera faltas de ortografía (1–2 letras) y acentos.
   - Aprende de cada visitante: recuerda sus búsquedas recientes y sube en los resultados lo que más abre. */
(function () {
  var form = document.getElementById("site-search");
  if (!form) return;
  var input = form.querySelector("input");
  var box = form.querySelector(".results");
  var lang = (document.documentElement.lang || "es").slice(0, 2) === "en" ? "en" : "es";
  var L = lang === "en"
    ? { none: "No results for", found: "Results", recent: "Recent searches", fuzzy: "Did you mean…", clear: "Clear" }
    : { none: "Sin resultados para", found: "Resultados", recent: "Búsquedas recientes", fuzzy: "Quizá buscabas…", clear: "Borrar" };
  var index = null, loading = null, cur = [], sel = -1;
  var KEY_R = "g6e-recent-" + lang, KEY_C = "g6e-clicks";

  function store(k, v) { try { if (v === undefined) return JSON.parse(localStorage.getItem(k) || "null"); localStorage.setItem(k, JSON.stringify(v)); } catch (e) { return null; } }
  function norm(s) { return (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  function load() {
    if (index) return Promise.resolve(index);
    if (loading) return loading;
    loading = fetch("/assets/search-" + lang + ".json", { cache: "no-cache" })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        index = (d.items || d).map(function (e) {
          e._t = norm(e.t);
          e._h = norm([e.t, e.c, e.d, e.s].join(" "));
          e._k = norm(e.k || "");
          e._w = null;
          return e;
        });
        return index;
      })
      .catch(function () { index = []; return index; });
    return loading;
  }

  function lev(a, b, max) {
    if (Math.abs(a.length - b.length) > max) return max + 1;
    var prev = [], i, j;
    for (j = 0; j <= b.length; j++) prev[j] = j;
    for (i = 1; i <= a.length; i++) {
      var row = [i], best = i;
      for (j = 1; j <= b.length; j++) {
        row[j] = Math.min(prev[j] + 1, row[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
        if (row[j] < best) best = row[j];
      }
      if (best > max) return max + 1;
      prev = row;
    }
    return prev[b.length];
  }
  function words(e) {
    if (!e._w) e._w = (e._h + " " + e._k).split(/[^a-z0-9ñ'’-]+/).filter(function (w) { return w.length > 2; });
    return e._w;
  }
  function near(t, ws, max) {
    for (var i = 0; i < ws.length; i++) {
      var w = ws[i];
      if (lev(t, w.length > t.length ? w.slice(0, t.length) : w, max) <= max) return true;
    }
    return false;
  }
  /* 0 = no se parece; 4 = parecida a una palabra del título; 2 = del texto; 0.5 = del contenido */
  function fuzzyHit(e, t) {
    var max = t.length >= 7 ? 2 : 1;
    if (!e._tw) e._tw = e._t.split(/[^a-z0-9ñ'’-]+/).filter(function (w) { return w.length > 2; });
    if (near(t, e._tw, max)) return 4;
    if (!e._hw) e._hw = e._h.split(/[^a-z0-9ñ'’-]+/).filter(function (w) { return w.length > 2; });
    if (near(t, e._hw, max)) return 2;
    if (near(t, words(e), max)) return 0.5;
    return 0;
  }

  function search(q) {
    var terms = norm(q).split(/\s+/).filter(Boolean);
    if (!terms.length) return { terms: [], list: [], fuzzy: false };
    var clicks = store(KEY_C) || {};
    function run(fuzzy) {
      var res = [];
      index.forEach(function (e) {
        var score = 0;
        for (var i = 0; i < terms.length; i++) {
          var t = terms[i];
          if (e._t === t) score += 14;
          else if (e._t.indexOf(t) === 0) score += 9;
          else if (e._t.indexOf(t) !== -1) score += 6;
          else if (e._h.indexOf(t) !== -1) score += 3;
          else if (e._k.indexOf(t) !== -1) score += 1.5;
          else if (fuzzy && t.length >= 4) { var f = fuzzyHit(e, t); if (!f) return; score += f; }
          else return;
        }
        if (!e.i && !fuzzy) score += 1.5;
        if (clicks[e.u]) score += Math.min(6, Math.log(1 + clicks[e.u]) * 2);
        res.push({ e: e, s: score });
      });
      res.sort(function (a, b) { return b.s - a.s || a.e.t.length - b.e.t.length; });
      return res;
    }
    var res = run(false), fuzzy = false;
    if (res.length < 3) { var f = run(true); if (f.length > res.length) { res = f; fuzzy = true; } }
    var seen = {}, list = [];
    for (var i = 0; i < res.length && list.length < 12; i++) {
      var e = res[i].e, key = e._t + "|" + norm(e.s || e.d || "").slice(0, 60);
      if (seen[key]) continue;
      seen[key] = 1; list.push(e);
    }
    return { terms: terms, list: list, fuzzy: fuzzy };
  }

  function hl(text, terms) {
    var n = norm(text), ranges = [];
    terms.forEach(function (t) {
      var i = 0, p;
      while (t && (p = n.indexOf(t, i)) !== -1) { ranges.push([p, p + t.length]); i = p + t.length; }
    });
    if (!ranges.length) return esc(text);
    ranges.sort(function (a, b) { return a[0] - b[0]; });
    var merged = [ranges[0]];
    for (var k = 1; k < ranges.length; k++) {
      var last = merged[merged.length - 1];
      if (ranges[k][0] <= last[1]) last[1] = Math.max(last[1], ranges[k][1]); else merged.push(ranges[k]);
    }
    var out = "", pos = 0;
    merged.forEach(function (r) { out += esc(text.slice(pos, r[0])) + "<mark>" + esc(text.slice(r[0], r[1])) + "</mark>"; pos = r[1]; });
    return out + esc(text.slice(pos));
  }

  function remember(q) {
    q = (q || "").trim(); if (q.length < 2) return;
    var r = (store(KEY_R) || []).filter(function (x) { return norm(x) !== norm(q); });
    r.unshift(q); store(KEY_R, r.slice(0, 6));
  }
  function count(u) { var c = store(KEY_C) || {}; c[u] = (c[u] || 0) + 1; store(KEY_C, c); }

  function showRecent() {
    var r = store(KEY_R) || [];
    if (!r.length) { box.hidden = true; return; }
    cur = []; sel = -1;
    box.innerHTML = '<div class="hint">' + L.recent + ' <button type="button" class="clr">' + L.clear + "</button></div>" +
      r.map(function (q) { return '<a class="res recent" href="#" data-q="' + esc(q) + '"><span class="r1"><b>' + esc(q) + "</b></span></a>"; }).join("");
    box.hidden = false;
  }

  function render(q) {
    if (!q.trim()) { showRecent(); input.setAttribute("aria-expanded", "false"); return; }
    var r = search(q);
    cur = r.list; sel = -1;
    if (!cur.length) {
      box.innerHTML = '<div class="none">' + L.none + " «" + esc(q.trim()) + "»</div>";
    } else {
      box.innerHTML = '<div class="hint">' + (r.fuzzy ? L.fuzzy : L.found) + "</div>" + cur.map(function (e, i) {
        var tag = e.g ? '<span class="tag b-' + e.g + '">' + esc(e.gl || "") + "</span>" : "";
        var sn = e.s || e.d || "";
        return '<a class="res" role="option" id="res-' + i + '" href="' + e.u + '">' +
          '<span class="r1"><b>' + hl(e.t, r.terms) + "</b>" + tag + "</span>" +
          '<span class="rc">' + esc(e.c || "") + "</span>" +
          (sn ? '<span class="rs">' + hl(sn, r.terms) + "</span>" : "") + "</a>";
      }).join("");
    }
    box.hidden = false;
    input.setAttribute("aria-expanded", "true");
  }
  function mark(i) {
    var els = box.querySelectorAll(".res");
    els.forEach(function (el, k) { el.setAttribute("aria-selected", k === i ? "true" : "false"); });
    if (els[i]) { els[i].scrollIntoView({ block: "nearest" }); input.setAttribute("aria-activedescendant", els[i].id); }
  }

  input.setAttribute("role", "combobox");
  input.setAttribute("aria-expanded", "false");
  input.setAttribute("aria-controls", "search-results");
  input.addEventListener("focus", function () { load(); if (!input.value.trim()) showRecent(); });
  var timer = null;
  input.addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(function () { load().then(function () { render(input.value); }); }, 90); });
  input.addEventListener("keydown", function (ev) {
    if (ev.key === "ArrowDown") { ev.preventDefault(); if (cur.length) { sel = (sel + 1) % cur.length; mark(sel); } }
    else if (ev.key === "ArrowUp") { ev.preventDefault(); if (cur.length) { sel = (sel - 1 + cur.length) % cur.length; mark(sel); } }
    else if (ev.key === "Escape") { box.hidden = true; input.setAttribute("aria-expanded", "false"); }
  });
  box.addEventListener("click", function (ev) {
    var clr = ev.target.closest(".clr");
    if (clr) { ev.preventDefault(); store(KEY_R, []); box.hidden = true; return; }
    var a = ev.target.closest("a.res");
    if (!a) return;
    if (a.classList.contains("recent")) { ev.preventDefault(); input.value = a.getAttribute("data-q"); load().then(function () { render(input.value); }); return; }
    remember(input.value); count(a.getAttribute("href"));
  });
  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var t = cur[sel >= 0 ? sel : 0];
    if (t) { remember(input.value); count(t.u); location.href = t.u; }
  });
  document.addEventListener("click", function (ev) { if (!form.contains(ev.target)) box.hidden = true; });
  document.addEventListener("keydown", function (ev) {
    var tg = (ev.target.tagName || "").toLowerCase();
    if (ev.key === "/" && tg !== "input" && tg !== "textarea") { ev.preventDefault(); input.focus(); }
  });
})();
