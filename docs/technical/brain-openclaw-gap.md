# OpenClaw vs paper-pipeline — análisis de equivalencias y límites de adopción

Este documento fija **qué mecanismos** del ecosistema OpenClaw (plantillas `AGENTS.md`, `docs.openclaw.ai`, skills de auto-mejora) tienen **paralelo conceptual** en paper-pipeline, qué **no**, y qué **riesgos** hay si el LLM del cerebro (Gemini) alucina capacidades.

**No hay paridad de producto** con un agente OpenClaw completo: paper-pipeline es una app local centrada en **misión → pipeline Perplexity → `outputs/`**, con un submódulo **cerebro** que solo **propone** YAML/JSON validado por el servidor.

---

## 1. Tabla de mapeo conceptual

| Mecanismo OpenClaw (referencia pública) | Rol | Equivalente en paper-pipeline | Vacío / parcial |
|----------------------------------------|-----|----------------------------------|-----------------|
| **SOUL.md** — identidad y principios | Quién es el agente | Tono y rol en el system prompt + sección «Identidad» en [`brain_capabilities.md`](../../paper_pipeline/brain/brain_capabilities.md) | No hay archivo separado SOUL en disco para el operador |
| **USER.md** — a quién ayuda el agente | Perfil del usuario | Implícito en `meta.json` + mensajes del chat; no hay USER.md por misión | Opcional futuro: notas en `outputs/` |
| **AGENTS.md** — constitución: arranque, memoria, límites | Reglas de sesión | **L1** = `brain_capabilities.md` inyectado en prompts; **L0** = código FastAPI + Pydantic | El cerebro no «lee AGENTS al arranque» como proceso; el servidor ensambla el prompt por request |
| **TOOLS.md** — gotchas de herramientas | Notas operativas | Parte del catálogo L1 (Perplexity vs Gemini, flags, UI) | No TOOLS.md editable por misión en v1 |
| **memory/YYYY-MM-DD.md** — bitácora cruda | Log diario | `outputs/brain_chat_history.jsonl` (append por turno) | Formato JSONL, no un .md por día |
| **MEMORY.md** — memoria curada largo plazo | Continuidad semántica | `outputs/brain_brief.md` (brief doctoral) + inyección en el prompt | Curación es responsabilidad humana (Aplicar / editar) |
| **Red lines** — no exfiltrar, no destructivo | Seguridad | Cerebro sin shell, sin acceso a `.env`; claves solo en servidor | Mitigación **no** solo por prompt: rutas API y ausencia de herramientas |
| **External vs internal** — qué requiere permiso | Frontera de acción | Interno: proponer `mission`/`meta`. Externo: run, Notion, Cursor → **otras rutas o CLI** | Usuario debe ejecutar acciones fuera del cerebro |
| **Skills (`SKILL.md`)** | Herramientas versionadas | Capacidades del producto en repo + `section_keys`; no skills editables en runtime por Gemini | — |
| **HEARTBEAT.md** — tareas periódicas | Bucle proactivo | **No soportado** para el cerebro: no hay LLM programado que despierte solo | Scheduler humano / CI / `paper-meta-loop` son otros procesos |
| **Self-improvement** (`.learnings/`, LEARNINGS / ERRORS) | Detectar → integrar con revisión | Ver [brain-learnings-future.md](brain-learnings-future.md) (solo diseño) | **No implementado** en v1 |

---

## 2. Ciclo Detection → Integration (OpenClaw) y qué implica aquí

En descripciones del skill *self-improving*, el ciclo implica **artefactos markdown** y **integración** tras revisión. En paper-pipeline:

- **Detection / Analysis** podrían ser, en el futuro, entradas humanas o logs de fallos del pipeline — **no** el cerebro escribiendo en `main` sin PR.
- **Generation** de «skills» equivaldría a cambios en el **repositorio** (código, docs), gobernados por git.
- **Conclusión:** la «auto-mejora» responsable es **documentación y código versionados** + proceso humano; el cerebro **no** redefine el producto solo.

---

## 3. Amenazas y mitigaciones

| Amenaza | Efecto si el modelo promete capacidad inexistente | Mitigación real (no solo prompt) |
|---------|-----------------------------------------------------|-----------------------------------|
| «Ya ejecuté el pipeline» | Expectativa falsa | No existe tool desde Gemini; `POST .../run` es otra ruta y requiere acción explícita del cliente |
| «Conecté Notion» | Confusión | `enable_notion` + `notion_page_id` son campos; credenciales `NOTION_TOKEN` en servidor |
| «Borré tu misión» | Pánico | API no expone DELETE de misión desde cerebro; solo patch vía `apply` |
| Exfiltración de secretos | Riesgo si el modelo repite texto del usuario | El prompt no incluye API keys; el operador no debe pegar secretos en el chat |

El catálogo L1 **reduce alucinación de marketing**; la **seguridad** sigue en **L0** (código, validación, ausencia de herramientas peligrosas para el LLM).

---

## 4. Roadmap honesto (qué no encaja sin rediseño)

- **Paridad con sesión OpenClaw «completa»** (lectura obligatoria de decenas de archivos por turno, edición de workspace por el agente): **fuera de alcance** del cerebro actual.
- **Heartbeat proactivo** del mismo Gemini hacia el usuario: no hay proceso residente que invoque al modelo sin un HTTP request.
- **RAG / vector DB** «conocimiento total del repo»: proyecto aparte; hoy el contexto es **archivos acotados** + historial truncado.

---

## 5. Referencias

- Plantilla tipo **AGENTS.md** (sesión, memoria, red lines): documentación pública OpenClaw (`docs.openclaw.ai`).
- Implementación **cerebro** en código: [`missions_brain.py`](../../paper_pipeline/server/routers/missions_brain.py), [`prompts.py`](../../paper_pipeline/brain/prompts.py), [`service.py`](../../paper_pipeline/brain/service.py).
