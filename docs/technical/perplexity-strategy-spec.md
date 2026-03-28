# Perplexity Strategy Layer — especificación V1

Trata a Perplexity como **sensor multi-régimen**: no todas las secciones merecen el mismo costo, modelo o uso de web. Esta capa es **opt-in** (`PAPER_PIPELINE_PERPLEXITY_STRATEGY`) y no cambia el comportamiento del cliente cuando está desactivada.

## Modos (`QueryMode`)

| Modo | Uso | Web típico |
|------|-----|------------|
| `discovery` | Mapeo de literatura, gaps, taxonomías | Sí |
| `verification` | Contrastar hipótesis, chequeos empíricos | Sí |
| `synthesis` | Reescritura y ensamblado con evidencia ya local | Preferir no |
| `review` | Crítica de borrador, limitaciones, discusión | Según perfil |
| `monitor` | Reservado: vigilancia temporal / novedades (futuro) | Sí |

V1 infiere el modo principalmente desde el **nombre de sección** (`related_work` → discovery, `methodology` → verification, etc.); versiones futuras pueden usar `goal_selection.json`.

## Perfiles

- `deep_discovery`: `cost_class=high`, `web=true`.
- `fast_check`: `cost_class=medium`, `web=true` (verificación).
- `synthesis_profile`: `cost_class=low`, `web=false` (redacción interna).
- `review_mode`: `cost_class=medium`, `web=true`.

El modelo efectivo se toma de `mission.model` (p. ej. `best`).

## Dedup / logging

- `query_fingerprint(prompt, scope)`: SHA-256 truncada de `scope` + prompt normalizado (espacios colapsados). Sirve para deduplicación futura y auditoría.

## Registro append-only

Archivo: `outputs/perplexity_call_record.jsonl` (una línea JSON por llamada planificada **antes** de `conversation.ask`).

Campos mínimos:

- `ts` (ISO UTC)
- `query_hash`
- `profile_id`
- `mode`
- `model`
- `cost_class`
- `section_or_goal`
- `mission_id` (opcional; V1 suele ser `null`)
- `web`

## Degradación

- Sesión Perplexity ausente o fallos de red: **no** los maneja esta capa (sigue el pipeline existente).
- Si `PAPER_PIPELINE_PERPLEXITY_STRATEGY` está apagado, **no** se registra ni se crea el archivo por esta vía.

## Doble pasada (futuro)

Claims fuertes pueden requerir segunda pasada “refutadora”; no implementado en V1.

## Ver también

- [agent-eval-spec.md](agent-eval-spec.md) — métricas de proceso sin Perplexity en CI.
- [../OUTPUTS_REFERENCE.md](../OUTPUTS_REFERENCE.md) — ubicación del JSONL.
