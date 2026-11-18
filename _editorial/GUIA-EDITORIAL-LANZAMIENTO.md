# GTA 6 Encyclopedia — guía editorial de lanzamiento

## Objetivo
Convertir la web en una enciclopedia útil basada en pruebas del juego, no en una colección de predicciones. Esta guía es interna: los archivos JSON de esta carpeta son plantillas de captura, no datos publicados.

## Estados de verificación
- `official`: dato publicado directamente por Rockstar Games o Take-Two. Guardar URL y fecha de consulta.
- `visual`: elemento identificable directamente en material oficial. No inferir nombre, función o disponibilidad si no aparecen.
- `demo`: observado por una fuente que probó una demo; indicar quién lo observó y cuándo. No equivale a confirmación de la versión final.
- `community`: identificación o conclusión de jugadores; atribuirla y no llamarla oficial.
- `pending`: falta una prueba reproducible. No presentar como hecho ni usar para completar listas.
- `verified_in_game`: comprobado directamente en una copia del juego. Registrar plataforma, versión, fecha y pasos de reproducción.

## Protocolo de captura dentro del juego
1. Registrar plataforma (PS5/Xbox Series X|S), región de cuenta si afecta al contenido, versión/actualización y modo de juego.
2. Capturar el nombre exacto mostrado por el juego y los pasos para reproducir el hallazgo.
3. Para misiones: punto de inicio, requisitos, objetivos principales y opcionales, recompensas, fallos y condiciones perdibles.
4. Para vehículos/armas: nombre exacto, categoría, forma de obtención, ubicación, modificaciones y pruebas comparables. No inventar estadísticas numéricas.
5. Para mapa/coleccionables: referencia cartográfica reproducible, requisito previo, ruta, cantidad total solo cuando se haya completado un barrido verificable y recompensa.
6. Para trucos: probar cada secuencia desde un estado limpio, anotar el efecto, restricciones y si bloquea trofeos/logros. No reutilizar códigos de GTA anteriores.
7. Para logros: verificar texto exacto, plataforma, requisitos, condiciones perdibles y método de desbloqueo.
8. Para easter eggs: registrar ubicación, pasos, evidencia y explicaciones alternativas; no presentar interpretaciones como hechos.
9. Redactar primero la ficha en español y después adaptar al inglés; no traducir nombres propios que el juego no traduzca.
10. Una segunda persona debe revisar la prueba y la redacción antes de publicar.

## Plantilla mínima visible en cada ficha publicada
- Nombre exacto del juego.
- Estado de verificación y qué significa.
- Plataforma y versión comprobadas.
- Fecha de última prueba.
- Pasos o método de obtención reproducible.
- Recompensas/efectos solo si se verificaron.
- Fuentes primarias y evidencia editorial propia.
- Nota de cambios si una actualización modifica el dato.

## Publicación e indexación
- Mantener `noindex` y fuera del sitemap cualquier página vacía, duplicada o que solo contenga un aviso de “sin datos”.
- Retirar `noindex` solo cuando la página tenga información original suficiente para resolver una intención de búsqueda concreta, no solo una plantilla o una lista de enlaces.
- Añadir al sitemap únicamente URLs canónicas, con contenido accesible en HTML sin depender de JavaScript para mostrar el texto principal.
- Actualizar `lastmod` solo cuando cambie sustancialmente el contenido de esa URL.
- Mantener hreflang recíproco solo entre traducciones reales equivalentes.
- No crear reseñas falsas, autores ficticios, valoraciones, estadísticas o FAQ schema que no estén visibles en la página.

## Monetización y propiedad intelectual — bloqueo previo
- Este sitio es independiente y no debe insinuar afiliación con Rockstar Games o Take-Two Interactive.
- El uso de un disclaimer no concede licencia para usar marcas, capturas, vídeos, mapas, música, logotipos, tipografías o recursos del juego.
- Antes de explotar comercialmente contenido que pueda implicar derechos de terceros, solicitar revisión legal y, cuando corresponda, autorización escrita del titular. El dominio con “GTA” también merece revisión de marca; un aviso de independencia no elimina por sí solo ese riesgo.
- No activar AdSense, afiliación ni otros anuncios hasta revisar privacidad, cookies/consentimiento, disclosures, condiciones del proveedor y derechos de propiedad intelectual aplicables.
- Identificar al responsable real del sitio en la documentación legal; no inventar domicilio, razón social ni datos del titular.

## Archivos JSON
Cada archivo `*.json` define campos para un tipo de ficha. Los valores `null`, listas vacías y cadenas vacías significan “pendiente de investigar”; nunca deben convertirse en afirmaciones publicadas.
