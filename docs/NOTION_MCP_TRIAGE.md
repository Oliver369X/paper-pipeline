# Notion y triaje (tier 3): mismo token que el MCP

El pipeline **no** habla con el servidor MCP de Cursor desde Python. Usa la **API REST de Notion** con un **token de integración interna**, el mismo que sueles configurar en:

- Variables de entorno del pipeline: `NOTION_TOKEN`
- Cursor: integración **Notion MCP** (misma clave de integración en el panel de Notion)

Así evitas duplicar secretos: una integración Notion, dos usos (IDE vía MCP, pipeline vía HTTPS).

## Qué hace el pipeline

Si el triaje clasifica **tier 3** (breakthrough) y están definidos `NOTION_TOKEN` y `NOTION_TRIAGE_PAGE_ID`, se añade un bloque (título + cuerpo) a una página de Notion que elijas, con topic, métricas y rutas locales. Los errores de red **no** abortan el run (solo log).

## Configuración rápida

1. En [Notion → My integrations](https://www.notion.so/my-integrations), crea o reutiliza una **integración interna** y copia el **Internal Integration Secret** → ese valor es `NOTION_TOKEN` (el mismo que pegas para el MCP en Cursor, si usas integración Notion allí).
2. Crea una página vacía en tu workspace (p. ej. “Paper pipeline — triage breakthroughs”).
3. En la página: **⋯ → Connections → Connect to** → elige tu integración.
4. Copia el ID de la página desde la URL:  
   `https://www.notion.so/workspace/Título-` **`abc123def456...`**  
   (32 caracteres hex, con o sin guiones según cómo lo pegues; la API acepta el formato estándar).
5. Exporta en el entorno donde corre el pipeline:

   ```bash
   set NOTION_TOKEN=secret_...
   set NOTION_TRIAGE_PAGE_ID=...
   ```

   En Linux/macOS: `export NOTION_TOKEN=...` y `export NOTION_TRIAGE_PAGE_ID=...`.

Sin estas variables, el triaje sigue funcionando; simplemente no se escribe nada en Notion.

## Relación con `events.jsonl` y webhooks

- `outputs/triage/events.jsonl` sigue registrando cada triaje localmente.
- Opcionalmente, `PAPER_PIPELINE_TRIAGE_WEBHOOK_URL` dispara un POST en tier 3.
- Notion es **otro canal opcional** para tier 3, pensado para lectura humana en el mismo workspace donde ya trabajas con el MCP.
