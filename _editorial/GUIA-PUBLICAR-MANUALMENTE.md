# Publicar una ficha nueva en GTA6Encyclopedia

Esta web es estática: una ficha nueva se incorpora como una página HTML dentro de la categoría correspondiente. Los JSON de `_editorial/` sirven para capturar y comprobar datos; por sí solos no publican contenido.

## Flujo recomendado

1. Identifica la categoría en `MAPA-SECCIONES-Y-CATEGORIAS.md`.
2. Copia una página existente de esa misma categoría y usa su estructura visual como base. No empieces desde un HTML vacío.
3. Rellena la plantilla Markdown adecuada y el JSON del mismo tipo.
4. Verifica nombre exacto, plataforma, versión del juego, fecha de prueba, evidencia y fuentes.
5. Crea la página española y su equivalente inglesa cuando exista traducción real. No traduzcas nombres propios que el juego mantenga iguales.
6. Actualiza el título, meta description, H1, canonical, Open Graph, breadcrumbs, selector de idioma y enlaces relacionados.
7. Añade la URL al sitemap solo cuando la página tenga contenido original suficiente, sea indexable y tenga canonical correcto.
8. Añade la ficha al índice de búsqueda `assets/search-index.json` siguiendo el formato de sus entradas existentes.
9. Comprueba los enlaces y que la página cargue bien en móvil y escritorio.

## Dónde insertar el contenido

- Para una ficha dentro de una categoría, añade un nuevo bloque `.item` dentro del contenedor `.list` de esa categoría.
- Para una guía completa, usa los encabezados y listas de la plantilla correspondiente, conservando las clases del sitio.
- Para noticias, utiliza fecha visible, fuente primaria y resumen original.
- Mantén la etiqueta de verificación que corresponda. No conviertas `pending` en un hecho publicado.

## Bloque de ficha para listados

Copia y adapta este bloque en el contenedor `.list`. Conserva los nombres de clase para respetar el diseño actual.

```html
<div class="item" id="slug-unico">
  <div>
    <h3><a href="/ruta-de-la-ficha/">Nombre exacto</a></h3>
    <p>Resumen breve, original y basado en datos comprobados.</p>
  </div>
  <span class="tag b-VI">Visual</span>
</div>
```

Clases de estado ya utilizadas:
- `b-OF`: Oficial
- `b-VI`: Visual
- `b-DE`: En demostraciones
- `b-CO`: Comunidad
- `b-NC`: Sin confirmar

Usa `verified_in_game` en los registros internos cuando se haya probado directamente en el juego. Si el diseño público no tiene todavía una etiqueta específica para ese estado, descríbelo en el texto y no reutilices una etiqueta incorrecta.

## Comprobación antes de publicar

- [ ] El nombre y los datos coinciden con el juego o la fuente citada.
- [ ] Se indica plataforma y versión cuando pueden afectar al resultado.
- [ ] Se documenta la fecha de última comprobación.
- [ ] Los pasos se pueden repetir.
- [ ] La página tiene un H1 único, title y meta description específicos.
- [ ] Canonical apunta a la URL definitiva.
- [ ] Hreflang solo enlaza una traducción equivalente real.
- [ ] El enlace desde la categoría funciona.
- [ ] El buscador incluye la ficha si debe aparecer en búsquedas internas.
- [ ] Sitemap actualizado solo si la página ya es indexable.
- [ ] No se han copiado textos, imágenes, mapas, vídeos ni recursos protegidos sin autorización.

## Importante
No cambies el diseño global, `assets/site.css`, el buscador, la cuenta regresiva ni los avisos legales al añadir una ficha normal. Si una nueva sección requiere una categoría nueva, crea primero sus equivalentes ES/EN y revisa navegación, enlaces, canonical, hreflang, buscador y sitemap.
