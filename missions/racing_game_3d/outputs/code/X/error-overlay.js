/**
 * Mensaje de error a pantalla completa (p. ej. WebGL no disponible).
 * @param {string} message
 */
export function showGameError(message) {
  const el = document.createElement("div");
  el.setAttribute("role", "alert");
  el.style.cssText =
    "position:fixed;inset:0;display:flex;align-items:center;justify-content:center;padding:2rem;background:#0b0c10;color:#f5f8fc;font-family:system-ui,sans-serif;font-size:1rem;text-align:center;z-index:9999;";
  el.textContent = message;
  document.body.appendChild(el);
}
