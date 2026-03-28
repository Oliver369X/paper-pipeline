# Pruebas en 5 niveles + paralelo (10) y Notion (3 páginas)

Guía para validar el producto como lo usaría un operador real, sin depender solo de tests unitarios.

## Tres páginas recomendadas en Notion

Comparte las tres con la **misma integración interna** (mismo `NOTION_TOKEN` que el MCP de Cursor).

| Orden sugerido | Nombre de página (puedes renombrar) | Variable / uso |
|----------------|-------------------------------------|----------------|
| 1 | **Paper pipeline — borrador paper** | `notion_page_id` en `mission.md` + `enable_notion: true` — secciones del paper sincronizadas aquí. |
| 2 | **Paper pipeline — triaje breakthrough** | `NOTION_TRIAGE_PAGE_ID` en `.env` — solo entradas tier 3 del hipervisor. |
| 3 | **Paper pipeline — registro / export** | Opcional: pegar manualmente el TSV de `GET /api/missions/export.tsv` o resúmenes; puede ser tu “tablero” tipo autoresearch `results.tsv`. |

Renombrá las páginas cuando quieras; lo importante es el **ID** en la URL y que la integración tenga acceso.

---

## Nivel 1 — Entorno y API (sin Perplexity)

1. `cd paper-pipeline && pip install -e ".[dev]"` (o tu venv habitual).
2. `python -m pytest -m "not integration and not notion_real" -q` → debe pasar.
3. `PAPER_PIPELINE_DATA_DIR` apuntando a `data/missions` (o default).
4. `paper-web` o `uvicorn paper_pipeline.server.main:app` → `GET http://127.0.0.1:8000/api/health` → `{"status":"ok"}`.
5. Desde `web/`: `npm run build` sin errores.

**Criterio:** API viva y frontend compilable.

**Contrato métricas + triaje + publicación (un vistazo):** dejá un `outputs/metrics.json` que pase `MetricsBundle` (véase `examples/metrics.valid.json`), ejecutá el pipeline con hipervisor activo y comprobá `triage/triage_report.json`, `publication/publish_decision.json` y, si aplica, `run_ledger.json` → `decision` alineada con tier y bloqueos — sin contradicciones entre quality y tier 3.

---

## Nivel 2 — Flujo web (como el usuario)

1. `npm run dev:all` en `web/` (API + Vite) o dos terminales.
2. Abrir la UI, **Nueva misión**, Editor: pestañas General / Pipeline 2.0 / Avanzado (`quality_gates`, hipóteses).
3. **Guardar**, recargar: flags y bloques persisten.
4. **Exportar TSV** en Inicio → archivo `paper-pipeline-missions.tsv` con cabecera correcta.

**Criterio:** CRUD y export sin tocar YAML a mano.

---

## Nivel 3 — Pipeline con Perplexity (real)

1. `.env` con `PERPLEXITY_SESSION_TOKEN` (no commitear).
2. Ejecutar pipeline desde UI **Pipeline** o CLI `paper-pipeline` sobre una misión de prueba.
3. Revisar `outputs/run.log` (JSONL) y eventos en la UI.

**Criterio:** al menos un run completo o error entendible (rate limit, auth).

---

## Nivel 4 — Notion (paper + triaje)

1. `NOTION_TOKEN` + página (1) con `notion_page_id` en la misión; `enable_notion: true`.
2. Tras un run, comprobar bloques en esa página.
3. Opcional triaje: `NOTION_TRIAGE_PAGE_ID` + misión con `enable_hypervisor_triage: true` y `outputs/metrics.json` que dispare tier 3 → línea en página (2).

**Smoke automático opcional:** con `NOTION_TOKEN` y `NOTION_SMOKE_PAGE_ID` definidos, `pytest tests/test_notion_smoke_optional.py -m notion_real`.

**Criterio:** al menos una escritura visible en Notion (paper o triaje).

---

## Nivel 5 — Paralelo extremo (10 worktrees)

Objetivo: demostrar que **`paper-parallel batch`** corre **10 experimentos** con concurrencia alta (p. ej. `--max-concurrent 10`).

1. Repo git con al menos un commit (el propio `paper-pipeline` o un clon mínimo).
2. Usar el ejemplo [`scripts/examples/specs10_parallel.json`](../scripts/examples/specs10_parallel.json).
3. Comando (ajustá rutas):

   ```bash
   paper-parallel batch --repo . --specs scripts/examples/specs10_parallel.json --max-concurrent 10 --timeout 120
   ```

4. Salida JSON con 10 `exp_id` y sin `error` (o revisar `error_log` si algún SO falla en el comando).

**Test automático:** `pytest tests/test_parallel_worktree.py::TestRunBatch::test_batch_ten_parallel_echo` (no requiere Notion ni Perplexity).

**Criterio:** 10 agentes completados; concurrencia limitada por `--max-concurrent`.

---

## Doble de 5 → 10 en paralelo

Los **5 niveles** cubren: entorno, web, Perplexity, Notion, paralelo.  
La **carga 10×** es explícitamente el **Nivel 5** con `--max-concurrent 10` y 10 filas en `specs.json` (no hace falta duplicar niveles: el “doble de 5” es **10 jobs en paralelo**).

---

## MCP opcionales

| MCP | Cuándo |
|-----|--------|
| **Notion** | Edición de páginas desde el IDE; mismo token que el pipeline. |
| **Colab / GPU** | Si el experimento pesado no corre en local; fuera de este repo (notebook o job); el pipeline solo consume `outputs/metrics.json` que generes allí. |
| **Perplexity (MCP)** | Alternativa al scraper por cookie; no sustituye `PERPLEXITY_SESSION_TOKEN` en el servidor salvo que integres otro camino. |

---

## Checklist rápido sin errores

- [ ] `pytest -m "not integration and not notion_real"` verde.
- [ ] `npm run build` en `web/`.
- [ ] Nivel 5 (paralelo 10) vía pytest o CLI.
- [ ] Notion Nivel 4 manual o `notion_real` con env.

Si algo falla, corregir en código o documentar el prerequisito (Git en PATH, permisos worktree en Windows, etc.).

---

## Flujo real + SOTA + figuras para el paper

Guía ampliada (Perplexity/Notion sin mocks, expectativas de SOTA, inglés académico, `paper-report-figures`): [**FLUJO_REAL_SOTA_FIGURES.md**](FLUJO_REAL_SOTA_FIGURES.md).
