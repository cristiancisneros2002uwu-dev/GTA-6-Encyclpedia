/* Buscador de la enciclopedia: índice estático /assets/search-index.json */
(function () {
  var form = document.getElementById("site-search");
  if (!form) return;
  var input = form.querySelector("input");
  var box = form.querySelector(".results");
  var lang = (document.documentElement.lang || "es").slice(0, 2);
  var L = lang === "en"
    ? { none: "No results for", pages: "Pages", found: "Results", sec: "Section" }
    : { none: "Sin resultados para", pages: "Páginas", found: "Resultados", sec: "Sección" };
  var index = null, loading = null, cur = [], sel = -1;

  function norm(s) {
    return (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  }
  function esc(s) {
    return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  }
  function load() {
    if (index) return Promise.resolve(index);
    if (loading) return loading;
    loading = fetch("/assets/search-index.json?v=3")
      .then(function (r) { return r.json(); })
      .then(function (d) {
        index = d.filter(function (e) { return e.l === lang; }).map(function (e) {
          e._t = norm(e.t); e._h = norm([e.t, e.c, e.d, e.s].join(" "));
          return e;
        });
        return index;
      })
      .catch(function () { index = []; return index; });
    return loading;
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
    merged.forEach(function (r) {
      out += esc(text.slice(pos, r[0])) + "<mark>" + esc(text.slice(r[0], r[1])) + "</mark>";
      pos = r[1];
    });
    return out + esc(text.slice(pos));
  }
  function search(q) {
    var terms = norm(q).split(/\s+/).filter(Boolean);
    if (!terms.length) return [];
    var res = [];
    index.forEach(function (e) {
      for (var i = 0; i < terms.length; i++) if (e._h.indexOf(terms[i]) === -1) return;
      var score = 0;
      terms.forEach(function (t) {
        if (e._t === t) score += 12;
        else if (e._t.indexOf(t) === 0) score += 8;
        else if (e._t.indexOf(t) !== -1) score += 5;
        else if (norm(e.c).indexOf(t) !== -1) score += 2;
        else score += 1;
      });
      if (!e.i) score += 1.5; /* las páginas pesan un poco más que sus fichas */
      res.push({ e: e, s: score });
    });
    res.sort(function (a, b) { return b.s - a.s || a.e.t.length - b.e.t.length; });
    return { terms: terms, list: res.slice(0, 9).map(function (r) { return r.e; }) };
  }
  function render(q) {
    var r = search(q);
    cur = r.list || [];
    sel = -1;
    if (!q.trim()) { box.hidden = true; box.innerHTML = ""; input.setAttribute("aria-expanded", "false"); return; }
    if (!cur.length) {
      box.innerHTML = '<div class="none">' + L.none + " «" + esc(q.trim()) + "»</div>";
    } else {
      box.innerHTML = '<div class="hint">' + L.found + "</div>" + cur.map(function (e, i) {
        var tag = e.g ? '<span class="tag b-' + e.g + '">' + esc(e.gl) + "</span>" : "";
        return '<a class="res" role="option" id="res-' + i + '" href="' + e.u + '">' +
          '<span class="r1"><b>' + hl(e.t, r.terms) + "</b>" + tag + "</span>" +
          '<span class="rc">' + esc(e.c) + "</span>" +
          (e.s ? '<span class="rs">' + hl(e.s, r.terms) + "</span>" : (e.d ? '<span class="rs">' + hl(e.d, r.terms) + "</span>" : "")) +
          "</a>";
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
  input.addEventListener("focus", load);
  input.addEventListener("input", function () { load().then(function () { render(input.value); }); });
  input.addEventListener("keydown", function (ev) {
    if (ev.key === "ArrowDown") { ev.preventDefault(); if (cur.length) { sel = (sel + 1) % cur.length; mark(sel); } }
    else if (ev.key === "ArrowUp") { ev.preventDefault(); if (cur.length) { sel = (sel - 1 + cur.length) % cur.length; mark(sel); } }
    else if (ev.key === "Escape") { box.hidden = true; input.setAttribute("aria-expanded", "false"); }
  });
  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var t = cur[sel >= 0 ? sel : 0];
    if (t) location.href = t.u;
  });
  document.addEventListener("click", function (ev) { if (!form.contains(ev.target)) box.hidden = true; });
  document.addEventListener("keydown", function (ev) {
    var tg = (ev.target.tagName || "").toLowerCase();
    if (ev.key === "/" && tg !== "input" && tg !== "textarea") { ev.preventDefault(); input.focus(); }
  });
})();
