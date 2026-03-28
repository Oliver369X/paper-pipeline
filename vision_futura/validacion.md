

# Paper-Pipeline 2.0: Sistema Completo de Calidad y Anti-Degradación

## El Problema Central que Describes (Bien Identificado)

Tienes toda la razón en el diagnóstico más importante: **un LLM evaluando su propio output en un loop se convence a sí mismo de que está mejorando mientras la calidad real cae** . Esto se llama *reward hacking* y está documentado empíricamente — los scores del evaluador **suben** mientras la calidad humana percibida **baja**. El `paper-loop` actual tiene exactamente esta vulnerabilidad porque Perplexity genera Y Perplexity revisa .

***

## Las 5 Capas de Defensa

### Capa 1 — Anclaje Externo Inmutable

La regla de oro: **el sistema nunca puede ser su único árbitro**. Antes de que empiece el loop, se fija un `ExternalAnchor` con el embedding del topic original, un corpus de 50 papers del venue objetivo, y — lo más crítico — **poison pills**: afirmaciones deliberadamente falsas sobre el dominio (ej. "Transformers fueron inventados por LeCun en 1995"). Si el fact-checker valida una poison pill como correcta → el sistema está en reward hacking → loop se para inmediatamente .

### Capa 2 — Evaluador Heterogéneo (Cross-Model)

**Si el generador es Perplexity/Claude, el evaluador DEBE ser GPT-4o o Gemini.** Nunca el mismo vendor. El documento incluye el mapa completo de qué modelos evalúan a cuáles, y el **trajectory tracking**: si el score nativo sube mientras el score externo baja → `REWARD_HACKING_DETECTED` → halt inmediato .

### Capa 3 — Verificación Matemática Formal

Para claims matemáticos, el único verificador confiable es un proof assistant . El documento implementa tres niveles:

- **SymPy**: verificación simbólica de fórmulas algebraicas (¿F1 = harmonic mean de P y R? Chequeable automáticamente)
- **Lean4**: verificación formal de teoremas
- **Empírico**: si el paper dice "corre en O(n log n)", benchmark con n =  y ajusta la curva

Incluye también verificaciones matemáticas de coherencia interna: probabilidades deben sumar a 1, métricas en rango válido, reproducibilidad con mismo seed.

### Capa 4 — Verificación de Código con Ejecución Real

Ningún claim sobre código puede ser verdadero si el código no corre. El `CodeVerifier` implementa: tests unitarios, **property-based testing** (verificar que f(x) ≤ f(y) para todo x < y si el paper dice "la función es monótona"), fuzzing con Atheris, análisis estático, y comparación contra ciclo anterior — si las métricas bajan > 5%, revierte automáticamente via git.

### Capa 5 — Monitor de Degradación en Tiempo Real

El `DegradationMonitor` captura en cada ciclo: densidad de información, auto-repetición (n-gram overlap con historia), drift de tema (coseno similarity con anchor), y % de citas verificadas. Si detecta tendencias negativas en 2+ métricas críticas → `HALT` + rollback al mejor ciclo identificado .

***

## El Rol del Humano: Cognitive Forcing Functions

El problema que describes sobre revisión humana es real: **poner al humano "en el loop" sin diseño correcto es teatro**. Un estudio de Microsoft 2025 confirma que mayor confianza en GenAI se asocia con **menos pensamiento crítico**. La solución son las **Cognitive Forcing Functions (CFFs)**: fricción estructurada que obliga a razonar, no solo aprobar.

El documento define 5 checkpoints con preguntas abiertas obligatorias:

| Checkpoint | Cuándo | Qué hace el humano |
|-----------|--------|--------------------|
| CP-0 | Antes del loop | Escribe `mission.md` con poison pills propias |
| CP-1 | Post-secciones | Verifica 3 citas al azar en la fuente original |
| CP-2 | Post-experimentos | Corre el código en su máquina local |
| CP-3 | Degradation Alert | Decide: continuar / revertir / cambiar misión |
| CP-5 | Pre-publicación | Firma checklist con respuestas de al menos 10 palabras |

Las respuestas de 1-2 palabras no son aceptadas — el sistema pide más detalle. Esto fuerza pensamiento genuino, no rubber-stamping .

***

## Taxonomía Completa de Fallos

El documento mapea **14 tipos de fallos** con causa raíz, síntoma, detección y solución: desde loop stall (ya implementado) hasta reward hacking semántico, drift de tema, p-hacking, colapso de diversidad de revisores, código no reproducible, y repo contaminado por `--force` sin backup .

***

## Próximos Pasos por Prioridad

**Prioridad 1 (máximo impacto, mínima fricción):**
- `DegradationMonitor` básico (info density + topic similarity)
- Git auto-commit después de cada ciclo
- Evaluador heterogéneo: 1 llamada extra a GPT-4o después de Perplexity
- 3 poison pills automáticas por misión

**Prioridad 2:**
- FactChecker con HTTP verification de URLs
- `StatisticalRigorChecker` (p-hacking, error bars)
- CFFs con preguntas abiertas en checkpoints humanos

**Prioridad 3:**
- `FormalMathVerifier` con SymPy
- Property-based testing + fuzzing
- `ReplicationTester` en Docker limpio
