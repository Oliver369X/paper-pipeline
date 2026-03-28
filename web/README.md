# Cockpit web (Vite + React)

## Desarrollo local

```bash
npm install
npm run dev
```

La API debe estar en `http://127.0.0.1:8000` (proxy en `vite.config.ts` → `/api`).

Todo en uno (desde la raíz del repo `paper-pipeline`):

```bash
cd web && npm run dev:all
```

## Despliegue en Vercel (solo frontend)

1. En Vercel, **Root Directory** del proyecto: `web` (esta carpeta).
2. Variables de entorno de **build** (Production y Preview):
   - `VITE_API_BASE_URL` — URL pública del backend FastAPI (sin `/` final), p. ej. `https://tu-servidor.railway.app`. El API debe permitir CORS desde el dominio del frontend (ver `PAPER_PIPELINE_CORS_ORIGINS` en el servidor).
3. El backend **no** corre en Vercel con este repo tal cual: desplegalo aparte (misma máquina, Docker, Railway, Fly, etc.).
4. No commitees `.env.local` ni secretos: la URL del API es pública; tokens viven solo en el servidor del pipeline.

### CLI rápido

```bash
npm run build
vercel        # preview
# vercel --prod   # producción (confirmar antes)
```

Desde `web/`, `vercel link` la primera vez si no tenés `.vercel/project.json`. Guía larga: [docs/DEPLOY_VERCEL.md](../docs/DEPLOY_VERCEL.md).

## Producción embebida (FastAPI sirve `dist/`)

Si construís el SPA y el servidor monta `web/dist` (ver `paper_pipeline/server/main.py`), no hace falta `VITE_API_BASE_URL`: las peticiones van al mismo origen.

```bash
npm run build
```
