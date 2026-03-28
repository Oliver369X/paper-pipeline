# Desarrollo del proyecto: código, tests y convenciones

Guía para quien toca **Python**, **tests** o el **frontend** (`web/`). Complementa [GUIA_PRUEBAS_Y_DEBUG.md](GUIA_PRUEBAS_Y_DEBUG.md) (cómo probar cada pieza) y el [README principal](../README.md) (instalación y uso). Inventario de **todos** los comandos `paper-*` y variables sueltas: [technical/07-inventario-cli-y-entorno.md](technical/07-inventario-cli-y-entorno.md).

---

## 1. Entorno de desarrollo

| Requisito | Uso |
|-----------|-----|
| Python **3.10+** | Mismo rango que `requires-python` en `pyproject.toml`. |
| `perplexity-webui-scraper` | Dependencia editable **antes** que `paper-pipeline` (ver README). |
| `pip install -e ".[dev]"` | Incluye **pytest**, **ruff**, **pytest-cov**, **httpx** (TestClient para la API). |
| Extra opcional `e2e` | `pip install -e ".[e2e]"` + `playwright install chromium` para tests marcados `e2e`. |

**Recomendación:** siempre trabajar dentro de un **venv** (`.venv/` en la raíz del repo, ignorado por git).

```bash
cd paper-pipeline
python -m venv .venv
# Windows: .\.venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -e ../perplexity-webui-scraper
pip install -e ".[dev]"
```

**Node** (solo para `web/`): Node 18+; `cd web && npm install`.

---

## 2. Estructura del repositorio (resumen)

```
paper-pipeline/
├── paper_pipeline/          # Paquete Python principal
│   ├── pipeline/runner.py   # Orquestador `run_pipeline` (fases ledger)
│   ├── orchestrator.py      # Re-exporta `run_pipeline` y helpers (compat)
│   ├── integrated_loop.py  # Bucle @PERPLEXITY / @NOTION / @CURSOR
│   ├── templates.py        # Plantillas por sección (SECTION_PROMPTS)
│   ├── mission.py          # Modelo Mission + load/save mission.md
│   ├── logger.py           # PipelineLogger → run.log JSONL
│   ├── server/             # FastAPI (CRUD misiones, SSE, web)
│   └── ...
├── tests/                  # pytest
├── web/                    # Vite + React + TypeScript (SPA)
├── docs/                   # Documentación en Markdown
└── pyproject.toml          # Dependencias, scripts, pytest, cobertura
```

- **CLI:** entradas en `paper_pipeline/*_main.py` y `__main__.py`; registrados en `[project.scripts]` del `pyproject.toml`.
- **Secciones del paper:** claves válidas = claves de `SECTION_PROMPTS` en `templates.py`. El servidor expone `GET /api/section-keys` y normaliza en `server/section_keys.py`.

---

## 3. Convenciones de código (Python)

1. **Seguir el estilo ya presente** en el archivo que edites (imports, tipos, nombres de funciones).
2. **Tipado** con anotaciones (`list[str]`, `Path | None`, etc.) donde el resto del módulo lo use.
3. **Cambios acotados:** no mezclar refactors grandes con un arreglo puntual; facilita revisión y `git blame`.
4. **Secretos:** nunca tokens en código; usar `.env` (ver `.env.example`) y variables de entorno.
5. **Compatibilidad:** no romper el CLI ni la web sin actualizar tests o documentación.

**Linter (opcional en local):**

```bash
ruff check paper_pipeline tests
ruff format paper_pipeline tests
```

`ruff` está en el extra `dev`; no hay obligación de CI local salvo que el proyecto añada workflow.

En el repo hay un workflow opcional **`.github/workflows/pytest-focused.yml`**: ejecuta solo tests de triage/publicación/ledger (útil en CI sin correr toda la suite). Si el repositorio git está en un monorepo padre, puede hacer falta ajustar `working-directory` o rutas `paths:`.

---

## 4. Tests

### 4.1 Comandos habituales

```bash
# Toda la suite salvo integración real con Perplexity (rápida, sin cuota)
pytest tests/ -q --ignore=tests/test_perplexity_integration.py

# Solo un archivo
pytest tests/test_loop_directives.py -v

# API web
pytest tests/test_server.py -q
```

### 4.2 Marcadores

Definidos en `pyproject.toml` → `[tool.pytest.ini_options]`:

| Marcador | Significado |
|----------|-------------|
| `integration` | `test_perplexity_integration.py` — llama a Perplexity de verdad; requiere `PERPLEXITY_SESSION_TOKEN`; consume cuota. |
| `e2e` | Playwright / visual-flow; requiere extra `e2e` y navegador instalado. |

Por defecto conviene **excluir** `integration` en CI o en el día a día.

### 4.3 Cobertura (opcional)

```bash
pytest tests/ --cov=paper_pipeline --cov-report=term-missing --ignore=tests/test_perplexity_integration.py
```

Umbral mínimo configurado en `pyproject.toml` (`fail_under` para cobertura); puede fallar si añadís código sin tests.

### 4.4 Buenas prácticas al escribir tests

- **Mocks** para Perplexity, subprocess y red (`unittest.mock.patch`, fixtures en `conftest.py`).
- **Fixtures** compartidos: `tmp_output_dir`, `minimal_mission` en `tests/conftest.py`.
- **Servidor:** `TestClient` con `PAPER_PIPELINE_DATA_DIR` apuntando a un `tmp_path` (ver `tests/test_server.py`).
- **Sin dependencia de orden** entre tests; cada test debe ser independiente.

### 4.5 Catálogo L1 del cerebro (`brain_capabilities.md`)

Si editás [`paper_pipeline/brain/brain_capabilities.md`](../paper_pipeline/brain/brain_capabilities.md), actualizá el hash fijado en `tests/test_brain_capabilities.py` (`_BRAIN_CAPABILITIES_SHA256`) para que el test `test_brain_capabilities_sha256_matches_pinned` siga pasando.

```bash
python -c "import hashlib; from pathlib import Path; p=Path('paper_pipeline/brain/brain_capabilities.md'); print(hashlib.sha256(p.read_bytes()).hexdigest())"
```

La función `brain_capabilities_sha256_hex()` en [`paper_pipeline/brain/prompts.py`](../paper_pipeline/brain/prompts.py) expone el mismo digest para scripts o CI.

---

## 5. Frontend (`web/`)

| Tema | Detalle |
|------|---------|
| **Stack** | Vite, React, TypeScript, TanStack Query, Tailwind. |
| **Build** | `cd web && npm run build` (tsc + vite). |
| **Lint** | `npm run lint` (ESLint). |
| **Proxy** | En desarrollo, `/api` → `http://127.0.0.1:8000` (`vite.config.ts`). |

Convenciones razonables: componentes en `src/components/`, páginas en `src/pages/`, hooks compartidos en `src/`. Mantener tipos alineados con la API JSON del backend.

---

## 6. Añadir una nueva “sección” de paper (Perplexity)

1. Añadir entrada en `paper_pipeline/templates.py` → `SECTION_PROMPTS` (clave única, texto del prompt).
2. No hace falta tocar `server/section_keys.py` si solo importa `SECTION_PROMPTS` (ya está cableado).
3. **Frontend:** el desplegable de secciones usa `GET /api/section-keys`; la nueva clave aparecerá sola.
4. Opcional: actualizar `mission.example.md` y documentación de usuario.

---

## 7. Commits y revisiones

- Mensajes de commit en **frases completas** y orientados al cambio real (“qué” y “por qué” breve).
- Si el cambio es solo documentación, indicarlo en el mensaje.
- Antes de abrir PR o compartir rama: `pytest` (sin `integration`) y, si tocaste `web/`, `npm run build`.

---

## 8. Documentos relacionados

- [GUIA_PRUEBAS_Y_DEBUG.md](GUIA_PRUEBAS_Y_DEBUG.md) — flujos de prueba y depuración.
- [OUTPUTS_REFERENCE.md](OUTPUTS_REFERENCE.md) — qué archivo genera qué.
- [GUIA_FLUJO_COMPLETO.md](GUIA_FLUJO_COMPLETO.md) — flujo de comandos y bucles.

---

*Última actualización: orientada a contribución en código y tests; no sustituye el README de instalación.*
