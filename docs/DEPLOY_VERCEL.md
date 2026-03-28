# Desplegar el Cockpit en Vercel (solo frontend)

El SPA vive en `web/` (Vite + React). El **backend FastAPI** debe correr en otro host (misma máquina con reverse proxy, Docker, Railway, Fly, etc.); este repo no incluye un serverless Python listo para Vercel.

## Pasos en Vercel

1. **Importar el repo** y fijar **Root Directory** = `web`.
2. **Variables de entorno** (entorno Production y Preview si querés previews funcionales):
   - `VITE_API_BASE_URL` — URL pública del API **sin** barra final, p. ej. `https://api.tu-dominio.com`.
3. En el **servidor** FastAPI, añadí el origen del frontend a CORS:
   - `PAPER_PIPELINE_CORS_ORIGINS=https://tu-proyecto.vercel.app,https://tu-dominio.com`
   - Incluí también el dominio de **preview** de Vercel si probás PRs desde el mismo API.

Detalle de build: `web/vercel.json` usa el preset Vite (`outputDirectory: dist`). Tras el build, las peticiones van a `VITE_API_BASE_URL + /api/...`.

## Mismo origen (sin Vercel)

Si servís `web/dist` desde `paper-web` (FastAPI monta estáticos), **no** hace falta `VITE_API_BASE_URL`: el navegador llama al mismo host. Ver [web/README.md](../web/README.md).

## Checklist CLI (opcional)

1. `vercel` instalado (`npm i -g vercel`).
2. Desde `web/`: `vercel link` si aún no existe `.vercel/project.json` en esa carpeta.
3. `npm run build` local antes de `vercel` o `vercel --prod` para detectar fallos de TypeScript o Vite.
4. **No subas al repo** `.env.local` ni secretos del API: `VITE_API_BASE_URL` es solo la URL pública del backend; las keys van en el entorno del servidor FastAPI o en el dashboard de Vercel solo si fueran prefijo `VITE_` de build (nunca commitees tokens en el front).
5. **Preview**: `vercel` (sin `--prod`) genera una URL `*.vercel.app`; definí `VITE_API_BASE_URL` también para el entorno Preview si querés probar contra un API de staging.
6. **Producción**: `vercel --prod` solo cuando confirmes dominio y CORS.

## Referencia

- Variables: [VARIABLES_Y_FLAGS.md](VARIABLES_Y_FLAGS.md) (`VITE_API_BASE_URL`, `PAPER_PIPELINE_CORS_ORIGINS`).
- README del front: [web/README.md](../web/README.md).
