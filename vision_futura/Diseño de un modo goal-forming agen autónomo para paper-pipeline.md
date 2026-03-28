# Diseño de un modo "goal-forming agent" autónomo para paper-pipeline

## 1. Objetivo del documento

Este documento propone una arquitectura concreta para añadir un **modo de agente autónomo con formación de metas (goal-forming agent)** encima del sistema actual `paper-pipeline`, manteniendo su filosofía de trazabilidad, control explícito y foco en producción de papers reales.

El foco es:
- Pasar de un orquestador reactivo guiado por `mission.md` + directivas humanas a un **sistema que también pueda generar, priorizar y sostener metas internas** dentro de cotas claras de costo y seguridad.
- Apoyarse explícitamente en la literatura de **autotelic agents**, **SelfGoal**, **LLM-based autonomous agents** y **auto-research** para no reinventar la rueda.[1][2][3][4][5]
- Explotar al máximo Perplexity como motor de conocimiento: distintos modelos, navegación web, verificación profunda y contraste con mundo real.

La intención no es afirmar que el sistema “tiene deseos” en sentido fuerte, sino dotarlo de **objetivos internos persistentes y parcialmente autogenerados**, con memoria y criterio de utilidad más allá del siguiente prompt.

## 2. Estado actual del sistema

### 2.1 Componentes existentes

Según la documentación actual:
- `paper-pipeline` implementa un **flujo lineal** de secciones: validación de misión, preflight, llamadas a Perplexity por sección, ensamblado de `draft_paper.md`, quality-check opcional, sync a Notion y llamada opcional a Cursor CLI.[6][7]
- `paper-loop` implementa el bucle reactivo sobre `cursorturn.md` y `nextinstruction.md`, ejecutando bloques `PERPLEXITY`, `NOTION`, `CURSOR` y disparando luego un meta-loop revisor que decide `CONTINUE` o `STOP`.[8][6]
- El **meta-loop** (`paper-meta-loop` y `paper-meta-watch`) actúa como un revisor que observa los artefactos y escribe nuevas instrucciones resumidas.[8][6]
- El **hipervisor de triaje** clasifica resultados experimentales en tiers 0–3 usando `outputs_metrics.json` y genera `triage_report.json`, webhooks y entradas opcionales en Notion en caso de breakthrough.[9][10]
- El servidor API (`paperpipeline.server.main`) expone una **cockpit API** con acceso a ledger, evidencia, triaje, publicación, métricas y estado del loop.[11]
- Hay soporte para **worktrees en paralelo** (`paper-parallel`) que ejecutan múltiples misiones en batch con triaje y control de concurrencia.[12][9]

En conjunto, esto configura ya un **sistema de orquestación complejo, auditable y orientado a papers**, no un simple script de prompts.[13][14]

### 2.2 Limitaciones clave para autonomía

Las principales limitaciones respecto a un agente formador de metas son:
- Las metas **entran desde fuera**: `topic`, `paper_target`, `sections_needed`, `quality_gates`, bloques `PERPLEXITY/NOTION/CURSOR` y decisiones humanas sobre cuándo relanzar el pipeline.[6][8]
- La memoria es sobre todo **operacional por run** (`run_state`, `manifest`, `ledger`, `triage_report`, `publish_decision`), sin una **capa explícita de memoria estratégica** que consolide aprendizajes entre misiones.[15][7][11]
- El hipervisor funciona como **triaje post-hoc**, no como controlador online que module exploración, explotación o parada temprana según señales parciales.[10][9]
- No existe un **scheduler autónomo**: los runs se disparan por CLI o desde la UI, no por el propio sistema al detectar gaps interesantes, anomalías o nuevas oportunidades.[13][12]

## 3. Lecciones de la literatura relevante

### 3.1 Autotelic agents y LMA3

La línea de **autotelic agents** define agentes que generan, seleccionan y resuelven sus propias metas, sin depender de un set de objetivos predefinidos.[2]
En particular, LMA3 (Language Model Augmented Autotelic Agent) usa un LM para tres funciones:
1. **Relabeler**: describir las metas efectivamente logradas en trayectorias pasadas.
2. **Goal generator**: proponer nuevas metas de alto nivel y descomponerlas en submetas ya dominadas.
3. **Reward functions**: definir funciones de recompensa asociadas a las metas generadas.[16][17][1]

Estos tres roles son directamente mapeables a tu contexto: relabel de experimentos y runs, generación de nuevas líneas de trabajo y definición de señales de éxito (calidad del paper, mejora sobre baseline, claridad de contribución, etc.).[1][16]

### 3.2 SelfGoal y descomposición adaptativa

SelfGoal muestra que un agente basado en LLM puede **descomponer una meta de alto nivel en un árbol de submetas** más accionables, actualizando esa estructura a medida que interactúa con el entorno y obtiene feedback, sin requerir instrucciones humanas hiper detalladas.[18][19][20][5]

La idea central es una estructura de **goal tree** que se refina dinámicamente mientras el agente actúa y observa resultados: exactamente lo que falta hoy entre tu `mission.md` y los bucles `paper-pipeline` / `paper-loop`.[5]

### 3.3 LLM-based autonomous agents y auto-research

Los surveys de agentes autónomos basados en LLM describen una arquitectura relativamente convergente: **LLM central + memoria + planificación + herramientas + feedback ambiental + evaluación**.[21][4]

Trabajos como **Agent Laboratory** y la visión de **Agent-Based Auto Research** proponen pipelines multi-agente que cubren el ciclo completo de investigación: revisión de literatura, experimentación, análisis de resultados y redacción de papers, con roles tipo “PhD agent”, “Postdoc agent”, “Professor agent” y herramientas específicas para cada fase.[3][22][23]

En estos sistemas, la revisión de literatura no solo resume papers, sino que **identifica huecos, compara métodos y sugiere direcciones prometedoras**, que luego alimentan la fase de experimentación y finalmente la redacción.[23][3]

Estas ideas encajan muy bien con tu diseño actual, que ya separa claramente literatura (Perplexity por sección), experimentos (métricas y triaje) y escritura (draft + Notion + figuras).[10][13]

## 4. Definición del nuevo modo: "Autonomy / Goal-Forming Mode"

### 4.1 Qué significa autonomía aquí

Para este proyecto, un **modo de autonomía razonable** puede definirse como:

> Un modo en el que el sistema, dado un espacio de investigación acotado y presupuestos claros, **genera, prioriza, ejecuta y refina metas de investigación** (preguntas, hipótesis, experimentos, ajustes de paper) sin requerir que el humano supervise cada paso local, manteniendo trazabilidad, cotas de costo y puntos de intervención humana.

No implica consciencia ni deseos humanos, pero sí:
- Persistencia de objetivos entre runs.
- Capacidad de inventar nuevas submetas dentro de un marco dado.
- Reutilización de memoria histórica para evitar repetir errores y explotar hallazgos.

### 4.2 Principios de diseño

1. **Compatibilidad hacia atrás**: el modo autónomo es opt-in; el modo actual sigue funcionando con `mission.md` clásico.[13]
2. **Estado explícito**: todas las metas, decisiones y cambios se escriben en artefactos (`goals.json`, `research_memory.jsonl`, etc.) y en el ledger.[7][11]
3. **Bucles cerrados pero acotados**: loops autónomos siempre limitados por `max_cycles`, `max_cost`, `max_parallel`, etc.[8][6]
4. **Perplexity como sensor epistemológico**: el agente usa Perplexity para **leer y validar contra el mundo real**: literatura, datos, fact checking, contraejemplos.[3][23]
5. **Multi-model y multi-modo**: selección dinámica de modelo rápido/lento, con o sin web, para balancear costo vs profundidad.[23][3]

## 5. Arquitectura propuesta de alto nivel

### 5.1 Componentes nuevos

Se propone añadir cinco componentes principales:

1. **Goal Manager (`paperpipeline.agent.goals`)**
   - Mantiene una **cola priorizada de metas de investigación** (goals) y submetas.
   - Cada goal tiene campos como: `id`, `parent_id`, `description`, `type` (literature, experiment, writing, refactor), `status`, `priority`, `budget_tokens`, `expected_impact`, `evidence_links`.
   - Expone operaciones: `propose_goals`, `refine_goal_tree`, `select_next_goal`, `update_goal_status`.

2. **Research Memory (`paperpipeline.agent.memory`)**
   - Consolida información de runs pasados: resúmenes de literatura, decisiones de diseño, resultados de experimentos, fracasos y breakthroughs.
   - Se almacena en un `research_memory.jsonl` y opcionalmente en Notion (p.ej. una “Research Log” page).[9][12][10]
   - Incluye índices tipo: por tema, por dataset, por método, por métrica.

3. **Controller / Utility (`paperpipeline.agent.controller`)**
   - Define una **función de utilidad** combinando: calidad del paper, mejora sobre baseline, coste en tokens, cobertura de hipótesis, riesgo de overclaiming, etc.[9][10]
   - Utiliza señales parciales (p.ej. borrador estancado, poca mejora de métrica, repetición de experimentos) para decidir **continuar, cambiar de plan, explorar nueva meta o parar**.[8][9]

4. **Scheduler y Event Loop (`paperpipeline.agent.scheduler`)**
   - Orquesta ejecución de goals: dispara `paper-pipeline`, `paper-loop`, batch en paralelo o llamadas directas a Perplexity según el tipo de goal.[6][9]
   - Se alimenta de eventos: nuevos papers relevantes detectados, anomalías métricas, feedback humano, etc.[3][9]

5. **Perplexity Strategy Layer (`paperpipeline.agent.perplexity_strategies`)**
   - Capa de alto nivel que decide **qué modelo de Perplexity usar, con qué profundidad de búsqueda, con o sin browsing y con qué prompts** según el tipo de goal: exploración amplia, verificación concreta, revisión crítica, etc.[23][3]

### 5.2 Integración con componentes actuales

- El **Goal Manager** se sitúa por encima de `mission.md`: el modo autónomo podría empezar a partir de una `mission.md` semilla, pero a partir de ahí genera nuevas misiones y submisiones.[13][6]
- El **Controller** usa artefactos actuales: `run_ledger.json`, `metrics.json`, `triage_report.json`, `publish_decision.json`, `loop_stop_decision.json`.[7][11][9]
- El **Scheduler** llama a las CLIs existentes (`paper-pipeline`, `paper-loop`, `paper-parallel`) y procesa sus outputs para alimentar memoria y metas.[9][6][8]
- La **Research Memory** referencia directamente artefactos existentes (`outputs/*.md`, `metrics`, `triage`, `Notion`), creando un grafo de evidencia reutilizable.[12][10][9]

## 6. Extensiones al contrato de misión

### 6.1 Nuevo modo en `mission.md`

Se puede extender el frontmatter de `mission.md` con un bloque opcional:

```yaml
---
mode: standard  # o "autonomy"
autonomy:
  enable_goal_manager: true
  max_global_tokens: 2_000_000
  max_parallel_experiments: 10
  max_depth_goal_tree: 3
  allowed_tools:
    - perplexity_web
    - perplexity_no_web
    - notion
    - cursor_cli
  safety:
    require_human_approval_for:
      - sota_claims
      - new_dataset_use
      - code_execution_outside_sandbox
  perplexity_profiles:
    exploration_model: "sonar-deep-research"  # ejemplo
    fast_model: "sonar-small"                # ejemplo
    writing_model: "sonar-pro"
---
```

Esto mantiene compatibilidad: si `mode` no es `autonomy`, el pipeline se comporta como ahora.[6][8]

### 6.2 Artefactos nuevos

Propuesta de nuevos artefactos bajo `outputs/` por misión:

- `goals.json`: árbol de metas con estados (`pending`, `in_progress`, `done`, `abandoned`).
- `research_memory.jsonl`: eventos de memoria de alto nivel (nuevo paper leído, hipótesis añadida, experimento fallido, breakthrough, etc.).
- `agent_decisions.log.jsonl`: decisiones del controller con justificación breve.
- `auto_missions/`: subcarpeta con `mission_auto_*.md` generadas por el Goal Manager.

Estos archivos se exponen en la cockpit API para inspección humana.[11]

## 7. Flujo de investigación completo en modo autonomía

### 7.1 Fase 0: Semilla humana mínima

1. El operador crea una `mission.md` semilla con un **espacio de problema**, no una pregunta hiper específica (por ejemplo, “métodos de calibración de modelos de incendios forestales en LatAm” en lugar de “comparar método X vs Y en dataset Z”).[10]
2. Activa `mode: autonomy` y configura límites de costo, herramientas permitidas y políticas de aprobación humana.[8][6]

### 7.2 Fase 1: Generación inicial de metas

1. El Goal Manager llama a Perplexity en modo exploración (modelo profundo + web) para:
   - Mapear el **espacio de literatura**: técnicas, datasets, benchmarks, brechas conocidas.[3][23]
   - Identificar **preguntas de investigación** candidatas y posibles contribuciones razonables para un venue dado.[22][3]
2. A partir de esas respuestas, el Goal Manager construye un **árbol de metas** semejante a SelfGoal: nodos padre (líneas de trabajo) y nodos hijo (experimentos concretos, revisiones de secciones, figuras, etc.).[18][5]
3. Se escribe `goals.json` con ese árbol, etiquetando cada meta con impacto estimado, coste y tipo.[7]

### 7.3 Fase 2: Bucle de investigación iterativo

Para cada iteración del scheduler:

1. El Controller selecciona el siguiente goal en función de utilidad esperada (impacto × probabilidad de éxito ÷ coste) y estado actual del paper y las métricas.[24][2]
2. Según el tipo de goal, el Scheduler:
   - **Literature goal**: lanza un bloque Perplexity con modelo de exploración o verificación profunda, consolidando resúmenes y referencias en `outputs/*.md` y `research_memory.jsonl`.[23][3]
   - **Experiment goal**: genera o actualiza una misión hija `mission_auto_X.md` con parámetros concretos, dispara `paper-pipeline` o `paper-parallel` (quizá solo la parte experimental) y espera `metrics.json` + `triage`.[10][9]
   - **Writing goal**: usa Perplexity en modo escritura sin web para reestructurar secciones específicas del borrador apoyándose en los outputs previos.[3][6]
3. Tras cada acción, el Controller:
   - Actualiza la memoria con un evento: qué se intentó, qué resultado hubo, cómo cambia la creencia sobre la viabilidad de metas relacionadas.[9][10]
   - Recalcula utilidades y puede **cerrar, refinar o dividir metas** al estilo LMA3 / SelfGoal.[5][1]
4. Periódicamente, el sistema lanza **goals de verificación externa**, p.ej. pedir a Perplexity que busque contraejemplos, papers discrepantes o críticas conocidas a la aproximación elegida.[23][3]

### 7.4 Fase 3: Consolidación hacia un paper candidato

Cuando varias metas de experimentos y escritura están completadas y el triaje reporta uno o más tiers 2–3:

1. El Controller crea un goal de tipo **“paper consolidation”**, que dispara `paper-pipeline` completo con las mejores decisiones hasta el momento, generando un draft coherente.[13][10]
2. A partir de ese draft, el agente puede lanzar metas de **“gap-filling”** (identificar huecos de related work, detalles de metodología poco claros, limitaciones insuficientemente discutidas, etc.).[22][3]
3. Se prepara un claim de SOTA prudente usando el módulo de figuras y párrafos de resultados ya existente, pero ahora guiado por la utilidad y por validaciones adicionales con Perplexity (por ejemplo, buscando papers con métricas similares o superiores).[10][3]

### 7.5 Fase 4: Transición a revisión humana

En lugar de publicar automáticamente, el modo autonomía debería, por defecto:

1. Generar un **paquete de revisión** (tu `researchpack.zip`) con borrador, métricas, triaje, log de decisiones del agente y un resumen ejecutivo de por qué considera que el trabajo es prometedor.[6][10]
2. Abrir un goal de tipo “esperar feedback humano” y detener la ejecución autónoma hasta recibir señal explícita (por API o desde la UI) de aprobar, pedir cambios específicos o archivar.[11]

## 8. Aprovechando al máximo Perplexity

### 8.1 Perfiles de uso por tipo de goal

Se recomienda definir **perfiles de uso de Perplexity**:

- **Exploración amplia (literature discovery)**
  - Modelo: grande / profundo con navegación web.
  - Prompts: mapeo de espacios, taxonomías de métodos, identificación de gaps, preguntas abiertas, datasets clave.
  - Uso: solo para metas de tipo literature-exploration.

- **Verificación puntual (fact-checking, contraejemplos)**
  - Modelo: intermedio con web.
  - Prompts: búsqueda de resultados contradictorios, críticas, fallos reportados, amenazas a la validez.
  - Uso: metas de verification-goal y al final de fases críticas.

- **Síntesis y redacción**
  - Modelo: de escritura sin web (o con web desactivada) para minimizar contaminación de estilo y duplicación de texto.
  - Prompts: reestructuración, mejora de claridad, adaptación a guidelines de venue.

- **Planificación y metas**
  - Modelo: razonador con web opcional.
  - Prompts: generación de árboles de metas, análisis de trade-offs, priorización bajo presupuesto.

Estos perfiles se parametrizan en `mission.md` en el bloque `perplexity_profiles`.[8][6]

### 8.2 Profundidad de búsqueda y validación con mundo real

Para maximizar validación con el mundo real:

- Usar **consultas encadenadas** en Perplexity: primero descubrimiento amplio, luego consultas más específicas sobre los trabajos clave detectados.[3][23]
- Incluir prompts que pidan explícitamente: “cita trabajos que **discrepen** con esta aproximación” o “menciona límites conocidos de estos métodos en contextos similares”.[3]
- Aprovechar la capacidad de Perplexity de combinar web con su modelo interno para construir **tablas de métodos vs métricas vs datasets** de forma semi-estructurada, que luego se pasan a tus herramientas de figuras y metrics.[23][10][3]

### 8.3 Independencia relativa de internet

Cuando se desea reducir dependencia de internet (por motivos de reproducibilidad o privacidad):

- Configurar metas específicas en las que Perplexity solo use su modelo interno (sin web) para tareas de reescritura, organización y razonamiento abstracto.
- Reservar el modo con web para metas de descubrimiento y verificación, cuyos resultados luego se referencian explícitamente en el paper (citando papers y no solo “Perplexity dijo…”).[23][3]

## 9. Cambios concretos de implementación

### 9.1 Nuevos paquetes y módulos

Propuesta mínima de nuevos módulos Python:

- `paperpipeline/agent/goals.py`
  - Clases `Goal`, `GoalTree`, `GoalManager`.
  - Métodos: `from_seed_mission`, `propose_goals_with_perplexity`, `refine_tree_selfgoal_style`, `select_next_goal`.

- `paperpipeline/agent/memory.py`
  - Clase `ResearchMemory` con métodos `add_event`, `query_by_topic`, `summarize_for_goal`.
  - Backend JSONL + hooks opcionales a Notion.[12]

- `paperpipeline/agent/controller.py`
  - Definición de utilidades por tipo de goal.
  - Lógica de parada y replanificación, integrando señales del hipervisor y del loop.[9][8]

- `paperpipeline/agent/scheduler.py`
  - CLI `paper-agent-run mission.md`.
  - Bucle principal que coordina metas, llama a `paper-pipeline`, `paper-loop`, `paper-parallel` y Perplexity.

- `paperpipeline/agent/perplexity_strategies.py`
  - Funciones de alto nivel que envuelven el cliente actual de Perplexity con perfiles de uso y logging enriquecido.[8]

### 9.2 Extensiones de la API

En `03-servidor-api.md` se describe una cockpit API rica. Se sugiere añadir:

- Rutas para leer y actualizar `goals.json` y `research_memory.jsonl` por `mission_id`.
- Un endpoint `POST .../agent/run-step` que ejecuta **un solo paso de autonomía** (seleccionar goal, actuar, actualizar estado) para facilitar control humano y debugging.
- Visualizaciones en la web de:
  - Árbol de metas y su estado.
  - Línea de tiempo de decisiones del agente.
  - Estadísticas de uso de Perplexity (tokens, tipos de consulta, modelos usados).

Estas vistas se alimentan de artefactos ya planeados para el cockpit (ledger, evidence, triage, publish), ampliados con la capa de agente.[11]

### 9.3 Testing y depuración

Siguiendo la filosofía de `GUIA_PRUEBAS_Y_DEBUG.md` y `PRUEBAS_NIVELES_5_10_NOTION.md`, el nuevo modo debería tener:

- Tests unitarios de `GoalManager` y `Controller` con **mocks de Perplexity** para no gastar cuota en CI.[12][8]
- Tests de integración marcados como `-m autonomy_integration` que ejecuten uno o dos ciclos reales de agente con Perplexity y Notion.[8]
- Casos de estrés con `paper-parallel` y `max_concurrent` alto para validar que el Goal Manager maneja bien múltiples misiones hijas.[12][9]

## 10. Estrategia de implementación incremental

### 10.1 Fase 1: "Autonomy-light"

- Añadir `mode: autonomy` al contrato de `mission.md` sin cambiar el flujo estándar.[6][8]
- Implementar `research_memory.jsonl` como logging enriquecido de decisiones humanas y resultados.
- Crear un `paper-agent-run --dry-run` que **solo simula selección de metas** usando Perplexity, sin ejecutar pipelines reales.

### 10.2 Fase 2: Goal Manager conectado a pipeline

- Implementar `GoalManager` real y `goals.json` como artefacto persistente.
- Permitir que el agente genere `mission_auto_X.md` y dispare `paper-pipeline` en modo opt-in.
- Integrar el hipervisor como fuente de señales de utilidad para cerrar, escalar o abandonar metas.[10][9]

### 10.3 Fase 3: Control online y scheduler

- Implementar el Scheduler completo con límites de tokens, tiempo y paralelismo.
- Añadir lógica de parada temprana basada en estancamiento del borrador (`LOOP_STALL`), falta de mejora en métricas y saturación de literatura.[10][8]

### 10.4 Fase 4: UI y revisión humana

- Exponer metas, memoria y decisiones en la web.
- Añadir mecanismos explícitos de aprobación/rechazo humano para SOTA claims, nuevos datasets o cambios de scope.

## 11. Cierre

El sistema actual ya está sorprendentemente cerca de lo que proponen frameworks como Agent Laboratory o la visión de Auto Research, al menos a nivel de orquestación, trazabilidad y tooling.[22][13][3][23]

La propuesta aquí es **añadir una capa de agente autotelic/goal-forming** encima, inspirada en LMA3, SelfGoal y los surveys de agentes LLM, pero respetando tu énfasis en control explícito, testing por niveles, integración con Notion y uso intensivo de Perplexity como interfaz con el mundo real.[4][1][5][6][8]