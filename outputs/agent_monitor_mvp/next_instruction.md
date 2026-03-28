<!-- meta_loop round=1 2026-03-24T23:58:17.186171+00:00 -->

@CURSOR

Agrega al monitor Leaflet un **panel lateral de detalle de evento**: al hacer clic en un marcador del mapa, muestra en un `<div id="event-detail">` fijo a la derecha los campos `title`, `date`, `description` y `type` del evento seleccionado (leer desde `data/events.json`). Sin backend, todo client-side.

**Archivos a tocar:**
- `code/monitor/index.html` — añadir el `<div id="event-detail">` con estilos inline o clase CSS básica (posición fija derecha, ancho ~280px, fondo blanco, sombra).
- `code/monitor/app.js` (o el JS principal) — en el `onEachFeature` / `bindPopup` del layer GeoJSON, agregar listener `.on('click', ...)` que populace el panel con los datos del feature.

**Verificar:**
- El panel aparece vacío al cargar y muestra datos reales al clicar un marcador.
- El export JSON filtrado existente no se rompe.
- No se introduce ninguna dependencia externa nueva.
