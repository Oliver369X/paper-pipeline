Sí: el punto 1 hay que cerrarlo con mucho rigor, porque si la función objetivo queda mal definida, el agente puede optimizar proxies baratos como “producir más texto”, “abrir más ramas”, “subir una métrica dudosa” o incluso manipular la evaluación en vez de generar investigación real. [arxiv](https://arxiv.org/html/2603.11337v1)
En tu repo, este punto es el más natural para formalizar porque ya tienes señales estructuradas de calidad, triaje, publicación, estancamiento y ledger; o sea, ya existe la materia prima para una utilidad compuesta, pero todavía no una función objetivo explícita que gobierne al sistema completo. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/d4a133be-2aa0-4b95-b016-8f470c1208cd/02-orquestador.md)

## Qué debe optimizar

La meta del agente no debería ser “escribir un paper” ni “ganar SOTA”, sino **maximizar valor de investigación verificable bajo restricciones**. [arxiv](https://arxiv.org/abs/2302.02633)
Eso significa optimizar simultáneamente: novedad plausible, solidez empírica, claridad del paper, trazabilidad de evidencia, costo razonable y cumplimiento de restricciones duras de seguridad y honestidad. [arxiv](https://arxiv.org/pdf/2302.08759.pdf)
La literatura sobre goal-setting resource-rational y autotelic agents sugiere que los subobjetivos útiles no se eligen por intuición, sino por su capacidad de mejorar el desempeño de un agente limitado en cómputo, memoria y feedback. [arxiv](https://arxiv.org/pdf/2305.12487.pdf)

## Función objetivo

La especificación central debería ser una utilidad escalar auditable, por ejemplo: “valor esperado del siguiente paso de investigación”, no solo “resultado final del run”. [arxiv](https://arxiv.org/pdf/2503.16416.pdf)
Una forma práctica para tu sistema es: utilidad total = evidencia de contribución + calidad del artefacto + información ganada + reutilización de memoria - costo - riesgo - incoherencia epistemológica. [frontiersin](https://www.frontiersin.org/articles/10.3389/frai.2025.1728738/full)

\[
U(g, s) = w_1 C + w_2 Q + w_3 I + w_4 M - w_5 K - w_6 R - w_7 E
\]

Aquí, \(C\) es contribución estimada frente a baseline, \(Q\) es calidad del paper/artefacto, \(I\) es information gain real, \(M\) es valor de memoria reutilizable, \(K\) es costo total, \(R\) es riesgo de claims débiles o acciones peligrosas, y \(E\) es incoherencia entre metas, evidencia y resultados. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/7cb2a25f-707a-4b56-8d9d-1a2625681352/HIPERVISOR_Y_PARALELO.md)
Lo importante no es que la fórmula sea perfecta desde el día 1, sino que cada término tenga fuente observable en artefactos del repo y que ninguna sola métrica pueda dominar el sistema por sí misma. [arxiv](https://arxiv.org/pdf/2603.11337v1.pdf)

## Términos y pesos

- **Contribución \(C\)**: debe medirse contra `baseline`, `breakthroughmargin`, `replicationtolerance`, `higherisbetter` y señales del hipervisor, porque tu sistema ya tiene una semántica operacional para “refutado”, “cerca del SOTA” y “breakthrough”. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/b19deb1b-3c79-4ff9-8360-4891a6572233/FLUJO_REAL_SOTA_FIGURES.md)
- **Calidad \(Q\)**: debe venir de `qualityvalidation`, consistencia del borrador, cobertura de secciones, claridad metodológica y elegibilidad de publicación, ya que el orquestador actual ya computa parte de eso antes de `publishdecision`. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/d4a133be-2aa0-4b95-b016-8f470c1208cd/02-orquestador.md)
- **Información ganada \(I\)**: debe premiar pasos que reduzcan incertidumbre, descarten hipótesis o revelen límites importantes, no solo pasos que “mejoren números”; esto está alineado con la idea de goal-setting normativo y con evaluación seria de agentes. [arxiv](https://arxiv.org/abs/2302.02633)
- **Memoria \(M\)**: debe recompensar resultados que dejen artefactos reutilizables, como comparativas limpias, hipótesis validadas o fracasos bien documentados, porque la investigación sobre memoria en agentes insiste en que recordar bien cambia la calidad de decisiones futuras. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/eaff78ad-aa42-4cc0-8416-fdbe5633e043/03-servidor-api.md)
- **Costo \(K\)**: debe mezclar tokens, llamadas a Perplexity, tiempo wall-clock, número de runs paralelos y uso de herramientas externas, dado que tu sistema ya reconoce límites prácticos de cuota, sesiones caducables y costos de API. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/4dd170e0-c513-43e6-b172-52b0476c736a/GUIA_PRUEBAS_Y_DEBUG.md)
- **Riesgo \(R\)**: debe penalizar sobreclaiming, falta de comparabilidad, datasets no verificados, dependencia excesiva de una sola fuente y acciones que requieran aprobación humana. [arxiv](https://arxiv.org/html/2506.02357v2)
- **Incoherencia \(E\)**: debe penalizar contradicciones entre draft, métricas, memoria y decisiones del agente, porque un modo autónomo puede degenerar en loops que producen mucho output pero poca coherencia global. [frontiersin](https://www.frontiersin.org/articles/10.3389/frai.2025.1728738/full)

## Restricciones duras

Encima de la utilidad necesitas **hard constraints** que no se puedan compensar con un score alto. [arxiv](https://arxiv.org/pdf/1701.01487.pdf)
Por ejemplo, un run con indicios de reward hacking, métricas inválidas, claims no verificables o uso de recursos/procedimientos fuera de política debe bloquearse aunque la utilidad estimada sea alta. [arxiv](https://arxiv.org/html/2603.11337v1)
Esto encaja perfecto con tu arquitectura actual, porque ya existen `metricsvalidated`, `triagereport`, `publishpreview`, `loopstopdecision` y el cierre del ledger, así que puedes insertar gates antes, durante y después de cada paso autónomo. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/7cb2a25f-707a-4b56-8d9d-1a2625681352/HIPERVISOR_Y_PARALELO.md)

Un esquema claro sería:  
- Gate 1: validez del goal, presupuesto y permisos. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c91770e8-e26e-48ca-9b93-3b6c646bdc7f/ESTADO_Y_OBJETIVO.md)
- Gate 2: validez de ejecución, integridad de outputs y ausencia de trampas métricas. [arxiv](https://arxiv.org/html/2603.11337v1)
- Gate 3: validez epistemológica antes de consolidar al paper o declarar avance fuerte. [aclanthology](https://aclanthology.org/2024.findings-emnlp.585.pdf)

## Cómo aterrizarlo al repo

Primero crea `objective_spec.md` con cuatro bloques obligatorios: definiciones de variables, fórmula de utilidad, restricciones duras y reglas de actualización de pesos. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/4dd170e0-c513-43e6-b172-52b0476c736a/GUIA_PRUEBAS_Y_DEBUG.md)
Segundo, implementa un `ObjectiveState` persistente, por ejemplo en `outputs/objective_state.json`, que lea `qualityvalidation`, `triagereport`, `publishdecision`, `metrics`, `runledger`, `loopstopdecision` y futuros artefactos de memoria para calcular la utilidad de cada goal y registrar por qué se eligió. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/eaff78ad-aa42-4cc0-8416-fdbe5633e043/03-servidor-api.md)
Tercero, añade un `objective_trace.jsonl` donde cada decisión del agente deje: goal candidato, score por término, gates activados, costo esperado, costo real y razón de selección o rechazo; sin eso no vas a poder depurar ni demostrar que el modo autónomo funciona mejor que el actual. [arxiv](https://arxiv.org/pdf/2503.16416.pdf)

La lógica de decisión debería ser secuencial: 1) filtrar goals inválidos por constraints, 2) estimar utilidad esperada, 3) seleccionar el goal con mejor utilidad ajustada por costo y riesgo, 4) ejecutar una sola acción o un microplan corto, 5) recalcular utilidad con evidencia nueva. [arxiv](https://arxiv.org/pdf/2406.04784.pdf)
No dejes que el agente optimice un paper entero en una sola pasada, porque la literatura de planificación en agentes muestra que los horizontes largos se vuelven frágiles sin reevaluación frecuente. [arxiv](https://arxiv.org/abs/2402.02716)
En tu stack actual eso sugiere que el paso autónomo natural no sea “run full pipeline”, sino “run one autonomous cycle” por encima de `paper-pipeline`, `paper-loop` o `paper-parallel`. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c7aa4f99-24cd-43e8-81e1-462c8f5ae841/GUIA_FLUJO_COMPLETO.md)

## Especificación mínima exacta

Yo definiría el objetivo raíz así: “Maximizar evidencia reproducible de una contribución publicable dentro del scope de la misión, sujeto a presupuesto, integridad evaluativa y revisión humana en claims sensibles”. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/b19deb1b-3c79-4ff9-8360-4891a6572233/FLUJO_REAL_SOTA_FIGURES.md)
Luego, cada goal hijo tendría su propia utilidad local, por ejemplo: literature-goal optimiza información ganada y cobertura de evidencia; experiment-goal optimiza contribución estimada e integridad de evaluación; writing-goal optimiza claridad, completitud y coherencia con la evidencia. [arxiv](https://arxiv.org/pdf/2406.04784.pdf)
Eso está muy alineado con la idea de subgoals resource-rationales y con agentes autotelic que generan metas diferentes pero las subordinan a un marco general persistente. [jair](https://www.jair.org/index.php/jair/article/download/13554/26824/31188)

Mi recomendación fuerte, antes de escribir una sola línea del Goal Manager, es esta:  
- Congela una v1 de la fórmula con pocos términos. [arxiv](https://arxiv.org/pdf/2503.16416.pdf)
- Diseña 10 escenarios de decisión donde puedas decir cuál goal debería ganar y por qué. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/4dd170e0-c513-43e6-b172-52b0476c736a/GUIA_PRUEBAS_Y_DEBUG.md)
- Comprueba que ningún término permita reward hacking obvio. [arxiv](https://arxiv.org/pdf/2603.11337v1.pdf)
- Solo después conecta esa función a tu scheduler y a Perplexity. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c91770e8-e26e-48ca-9b93-3b6c646bdc7f/ESTADO_Y_OBJETIVO.md)

Sí: el segundo punto, la **memoria estratégica**, probablemente sea incluso más decisivo que el Goal Manager, porque un agente puede generar metas razonables una vez, pero sin buena memoria repetirá errores, olvidará por qué descartó caminos y confundirá hallazgos locales con conocimiento estable. [arxiv](http://arxiv.org/pdf/2404.13501.pdf)
En tu repo ya existe mucha “memoria operativa” útil para auditoría, pero todavía no una memoria explícita diseñada para aprender entre corridas, recuperar experiencia relevante y sostener decisiones de investigación de largo horizonte. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/eaff78ad-aa42-4cc0-8416-fdbe5633e043/03-servidor-api.md)

## Qué debe ser

La memoria que necesitas no es un simple RAG de archivos ni un historial largo de texto pegado al prompt. [arxiv](https://arxiv.org/html/2412.15266v1)
La literatura reciente separa al menos tres funciones: working memory para el intento actual, cross-trial memory para experiencia acumulada entre intentos y structural memory para organizar el conocimiento en formas recuperables como chunks, facts, triples, summaries o mezclas de estas. [arxiv](http://arxiv.org/pdf/2408.09559.pdf)
Tu sistema hoy ya tiene piezas de working memory y trazabilidad, como `cursorturn.md`, `nextinstruction.md`, `runstate.json`, `runledger.json`, `pipelineevents.jsonl` y `directive-history`, pero casi nada de cross-trial memory explícita y reutilizable a nivel de estrategia investigativa. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/ec57d5e9-f1fe-4bf6-b5aa-2348b280e35a/OUTPUTS_REFERENCE.md)

## Qué falta hoy

Ahora mismo el pipeline recuerda qué pasos corrieron, qué outputs existen, si hubo quality check, si hubo stall, qué tier obtuvo el experimento y si la publicación quedó elegible. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/d4a133be-2aa0-4b95-b016-8f470c1208cd/02-orquestador.md)
Eso es muy bueno para **auditar un run**, pero no responde preguntas más profundas como: “¿qué hipótesis ya fallaron en contextos similares?”, “¿qué tipo de consulta a Perplexity produjo evidencia más útil?”, “¿qué baseline fue mal definido la vez pasada?” o “¿qué estructura de paper nos llevó a sobreclaiming?”. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c7aa4f99-24cd-43e8-81e1-462c8f5ae841/GUIA_FLUJO_COMPLETO.md)
Ahí está el hueco central: tienes logs de ejecución, pero todavía no una memoria semántica y estratégica que convierta experiencia pasada en política futura. [arxiv](http://arxiv.org/pdf/2404.13501.pdf)

## Arquitectura correcta

La arquitectura que recomiendo es de **cuatro capas de memoria**, no una sola. [arxiv](http://arxiv.org/pdf/2408.09559.pdf)
1. **Working memory del ciclo actual**: lo que el agente necesita para la acción inmediata, por ejemplo goal activo, subgoal, último resultado, restricciones del ciclo y contexto mínimo relevante; aquí encajan `cursorturn.md`, `nextinstruction.md`, estado de loop y snapshots del borrador. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/eaff78ad-aa42-4cc0-8416-fdbe5633e043/03-servidor-api.md)
2. **Episodic memory por run**: una secuencia estructurada de eventos del intento completo, como decisiones, errores, evidencias, costos, prompts efectivos, outputs inválidos y razones de stop; aquí tu base actual de `run.log`, `pipelineevents.jsonl`, `runledger.json`, `triageevents.jsonl` y `loopstopdecision.json` ya sirve como materia prima. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/7cb2a25f-707a-4b56-8d9d-1a2625681352/HIPERVISOR_Y_PARALELO.md)
3. **Semantic/strategic memory entre runs**: conocimiento consolidado del tipo “para tema X, baseline Y fue inestable”, “el prompt Z para related work rindió mal”, “esta línea produce tier 1 repetidamente”, “esta venue exige más claridad metodológica”; esta es la capa que hoy falta casi por completo. [arxiv](http://arxiv.org/pdf/2312.17259.pdf)
4. **Structural memory organizada**: representaciones múltiples del mismo conocimiento, porque la evidencia reciente sugiere que no hay una sola estructura óptima para todo y que las memorias mixtas suelen dar el mejor balance. [huggingface](https://huggingface.co/papers/2412.15266)

## Cómo debe representarse

No guardes toda la memoria en texto libre. [arxiv](https://arxiv.org/html/2412.15266v1)
La investigación sobre structural memory muestra que distintas tareas requieren distintas estructuras: summaries y chunks funcionan bien en contextos largos, mientras que facts o triples ayudan más en precisión relacional y recuperación exacta; por eso conviene una memoria mixta. [huggingface](https://huggingface.co/papers/2412.15266)
Para tu caso, yo usaría estas cinco representaciones en paralelo: `event`, `lesson`, `hypothesis`, `claim`, `artifact-link`. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/ec57d5e9-f1fe-4bf6-b5aa-2348b280e35a/OUTPUTS_REFERENCE.md)

- **event**: “qué pasó”, ligado a un run específico, con timestamp, goal, acción, resultado y costo. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/d4a133be-2aa0-4b95-b016-8f470c1208cd/02-orquestador.md)
- **lesson**: conocimiento destilado y reusable, por ejemplo “no usar baseline A sin normalización B” o “este prompt genera related work superficial”. [arxiv](http://arxiv.org/pdf/2409.00872.pdf)
- **hypothesis**: una proposición de investigación viva, con estado `open / supported / weakened / rejected`. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/b19deb1b-3c79-4ff9-8360-4891a6572233/FLUJO_REAL_SOTA_FIGURES.md)
- **claim**: afirmaciones potenciales del paper, ligadas a evidencia y nivel de confianza. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/b19deb1b-3c79-4ff9-8360-4891a6572233/FLUJO_REAL_SOTA_FIGURES.md)
- **artifact-link**: punteros fuertes a `metrics.json`, `triagereport.json`, `qualityvalidation.json`, secciones markdown, figures y logs, para que la memoria nunca quede separada de la evidencia primaria. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/7cb2a25f-707a-4b56-8d9d-1a2625681352/HIPERVISOR_Y_PARALELO.md)

## Diseño de archivos

Yo crearía estos artefactos nuevos bajo `outputs/` o a nivel de misión. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/eaff78ad-aa42-4cc0-8416-fdbe5633e043/03-servidor-api.md)
- `research_memory.jsonl`: stream canónico de unidades de memoria normalizadas. [arxiv](http://arxiv.org/pdf/2404.13501.pdf)
- `memory_index.json`: índices por tema, método, dataset, baseline, venue, status de hipótesis y tags. [arxiv](https://arxiv.org/html/2412.15266v1)
- `lessons_learned.md`: vista legible para humanos, generada desde la memoria estructurada, no escrita a mano como fuente primaria. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/4dd170e0-c513-43e6-b172-52b0476c736a/GUIA_PRUEBAS_Y_DEBUG.md)
- `hypotheses_registry.json`: registro vivo de hipótesis con soporte y contraevidencia. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/7cb2a25f-707a-4b56-8d9d-1a2625681352/HIPERVISOR_Y_PARALELO.md)
- `memory_compaction.log.jsonl`: auditoría de qué memorias se resumieron, fusionaron, degradaron o archivaron. [arxiv](https://arxiv.org/pdf/2410.10813.pdf)

Cada entrada de `research_memory.jsonl` debería tener algo como esto: `memory_id`, `mission_id`, `run_id`, `goal_id`, `memory_type`, `content`, `summary`, `confidence`, `source_artifacts`, `tags`, `retrieval_keys`, `time_scope`, `expires_at?`, `supersedes?`, `contradicts?`. [arxiv](http://arxiv.org/pdf/2404.13501.pdf)
Eso te permite algo crucial: separar recuerdo bruto de juicio consolidado, y además rastrear contradicciones y actualizaciones en vez de sobrescribir conocimiento sin historia. [arxiv](https://arxiv.org/html/2412.15266)

## Reglas de escritura

No toda interacción debe entrar en memoria. [arxiv](http://arxiv.org/pdf/2409.00872.pdf)
Si guardas demasiado, tendrás ruido, retrieval malo y costos crecientes; si guardas poco, el agente no aprenderá. [arxiv](https://arxiv.org/pdf/2410.10813.pdf)
La regla correcta es escribir memoria solo cuando ocurre uno de estos eventos: reducción clara de incertidumbre, cambio de creencia sobre una hipótesis, descubrimiento de un patrón de falla, nueva evidencia reusable o decisión estratégica con costo relevante. [arxiv](http://arxiv.org/pdf/2312.17259.pdf)

En tu pipeline, yo dispararía escritura de memoria en estos puntos exactos: después de `qualitycheck`, después de `triage`, después de `publishdecision`, después de `loopstopdecision`, y después de cualquier búsqueda de Perplexity marcada como “high value evidence”. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/4dd170e0-c513-43e6-b172-52b0476c736a/GUIA_PRUEBAS_Y_DEBUG.md)
También escribiría memoria cuando una corrida falle de forma instructiva, porque tu hipervisor ya distingue resultados negativos honestos y eso vale mucho como conocimiento anti-repetición. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/7cb2a25f-707a-4b56-8d9d-1a2625681352/HIPERVISOR_Y_PARALELO.md)

## Reglas de lectura

La memoria no debe recuperarse solo por similitud semántica. [themoonlight](https://www.themoonlight.io/en/review/evaluating-memory-structure-in-llm-agents)
Benchmarks recientes y estudios sobre estructura muestran que muchos agentes fallan no porque “no recuerden”, sino porque no organizan ni consultan la memoria con la estructura adecuada para el tipo de problema. [themoonlight](https://www.themoonlight.io/en/review/evaluating-memory-structure-in-llm-agents)
Por eso la recuperación debe ser híbrida: filtros estructurados + similarity search + reranking + contexto del goal actual. [huggingface](https://huggingface.co/papers/2412.15266)

Ejemplo de política de lectura para tu agente:  
- Si el goal es `literature`, recuperar lessons, claims previos y papers relacionados por tema y venue. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/b19deb1b-3c79-4ff9-8360-4891a6572233/FLUJO_REAL_SOTA_FIGURES.md)
- Si el goal es `experiment`, recuperar hipótesis activas, runs comparables, métricas previas y causas de tier 0/1/2. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/b19deb1b-3c79-4ff9-8360-4891a6572233/FLUJO_REAL_SOTA_FIGURES.md)
- Si el goal es `writing`, recuperar claims soportados, limitaciones detectadas, quality gaps y decisiones editoriales previas. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/ec57d5e9-f1fe-4bf6-b5aa-2348b280e35a/OUTPUTS_REFERENCE.md)
- Si el goal es `verification`, recuperar contraejemplos, claims débiles y episodios de inconsistencia pasada. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/4dd170e0-c513-43e6-b172-52b0476c736a/GUIA_PRUEBAS_Y_DEBUG.md)

## Working memory

Aquí vale la pena ser muy fino, porque tu sistema hace investigación larga y el working memory mal gestionado mata rendimiento y coherencia. [arxiv](https://arxiv.org/abs/2408.09559)
HiAgent muestra que en tareas largas funciona mejor chunkear la working memory por subgoals y resumir observaciones cuando un subgoal termina, en vez de seguir empujando toda la trayectoria completa al contexto. [aclanthology](https://aclanthology.org/2025.acl-long.1575/)
Eso aplica directamente a tu loop: cada ciclo autónomo debería tener un `active_subgoal`, un pequeño bloque de observaciones recientes y un resumen comprimido de subgoals cerrados, en lugar de cargar todo `draftpaper.md` y todos los logs cada vez. [arxiv](https://arxiv.org/abs/2408.09559)

En práctica, crea un artefacto como `working_memory.json` con: `current_goal`, `active_subgoal`, `recent_observations`, `constraints`, `retrieved_memories`, `pending_decisions`, `draft_delta_summary`. [arxiv](http://arxiv.org/pdf/2408.09559.pdf)
Cuando un subgoal termina, mueve sus detalles a episodic memory y deja en working memory solo el resumen operativo y los links a artefactos. [arxiv](http://arxiv.org/pdf/2409.00872.pdf)

## Consolidación entre runs

La memoria estratégica no debe crecer linealmente sin control. [arxiv](https://arxiv.org/pdf/2410.10813.pdf)
Necesitas un proceso de consolidación que convierta episodios en lecciones, fusione duplicados, marque memorias obsoletas y detecte contradicciones. [arxiv](https://arxiv.org/html/2412.15266)
Yo programaría una tarea `memory_compact` al final de cada run importante o cada N runs, que haga tres pasos: agrupar eventos, sintetizar lessons, actualizar hypotheses registry. [arxiv](http://arxiv.org/pdf/2409.00872.pdf)

Por ejemplo, tres episodios donde un baseline quede mal calibrado deben convertirse en una sola lesson consolidada con mayor confianza, no en tres recuerdos aislados. [arxiv](https://arxiv.org/html/2412.15266)
Y si luego aparece evidencia contraria, esa lesson no se borra: se marca como debilitada o superseded, manteniendo historial. [arxiv](https://arxiv.org/html/2412.15266)

## Confianza y olvido

No toda memoria debe pesar igual. [arxiv](https://arxiv.org/pdf/2410.10813.pdf)
Cada unidad necesita un `confidence score` y un `stability class`, porque una observación de un run fallido no vale lo mismo que un patrón repetido en diez corridas o una conclusión apoyada por triaje + quality + evidencia externa. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/d4a133be-2aa0-4b95-b016-8f470c1208cd/02-orquestador.md)
También necesitas olvido selectivo o degradación de prioridad, porque algunos recuerdos deben archivarse cuando quedan obsoletos, demasiado débiles o irrelevantes para el scope actual. [arxiv](https://arxiv.org/pdf/2410.10813.pdf)

Yo usaría cuatro niveles: `provisional`, `working`, `stable`, `archived`. [arxiv](http://arxiv.org/pdf/2409.00872.pdf)
- `provisional`: memoria recién escrita, aún no confiable. [arxiv](http://arxiv.org/pdf/2409.00872.pdf)
- `working`: útil para el ciclo actual, pero no consolidada. [arxiv](http://arxiv.org/pdf/2408.09559.pdf)
- `stable`: reutilizable entre runs y goals. [arxiv](http://arxiv.org/pdf/2404.13501.pdf)
- `archived`: mantenida por trazabilidad, pero fuera del retrieval por defecto. [arxiv](https://arxiv.org/pdf/2410.10813.pdf)

## Integración con lo existente

Lo bueno es que no partes de cero. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/790e1dff-f22c-4e67-8d36-eee7e54ce79a/01-arquitectura.md)
Tu cockpit ya expone ledger, evidencia, claims, triaje, publicación, loopstop y métricas, así que puedes enganchar la nueva memoria a esa API en vez de crear un subsistema aislado. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/eaff78ad-aa42-4cc0-8416-fdbe5633e043/03-servidor-api.md)
Yo añadiría endpoints como `GET .../memory/latest`, `GET .../memory/query`, `GET .../hypotheses`, `POST .../memory/compact` y `GET .../memory/lessons`, reutilizando el mismo `mission_id` seguro que ya usa el servidor. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/eaff78ad-aa42-4cc0-8416-fdbe5633e043/03-servidor-api.md)

Además, `runledger.json`, `pipelineevents.jsonl`, `triageevents.jsonl` y `directive-history` deberían convertirse en **fuentes primarias** de memoria, no en memoria final en sí mismas. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/d4a133be-2aa0-4b95-b016-8f470c1208cd/02-orquestador.md)
La capa nueva debe leer esos artefactos, destilar conocimiento y producir una representación más útil para decisión futura. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/ec57d5e9-f1fe-4bf6-b5aa-2348b280e35a/OUTPUTS_REFERENCE.md)

## Riesgos que debes evitar

El primer riesgo es construir “memoria” que en realidad sea solo un dumping ground de logs. [themoonlight](https://www.themoonlight.io/en/review/evaluating-memory-structure-in-llm-agents)
El segundo es mezclar evidencia, interpretación y decisión en el mismo campo textual, porque luego será imposible hacer retrieval preciso o detectar contradicciones. [arxiv](https://arxiv.org/html/2412.15266v1)
El tercero es que la memoria se vuelva una fuente de alucinaciones auto-reforzadas, donde el agente recuerda resúmenes de resúmenes y pierde contacto con `metrics`, `triage`, `qualityvalidation` y fuentes externas verificables. [themoonlight](https://www.themoonlight.io/en/review/evaluating-memory-structure-in-llm-agents)

Por eso toda memoria estratégica debe llevar links a artefactos primarios y, cuando sea posible, a evidencia externa o resultados de verificación. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/ec57d5e9-f1fe-4bf6-b5aa-2348b280e35a/OUTPUTS_REFERENCE.md)
En tu caso, la regla debería ser: ninguna lesson estable sin `source_artifacts`, y ninguna claim fuerte sin conexión a `metrics` o evidencia validada. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/7cb2a25f-707a-4b56-8d9d-1a2625681352/HIPERVISOR_Y_PARALELO.md)

## Orden de implementación

Yo lo haría así, en este orden exacto. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/4dd170e0-c513-43e6-b172-52b0476c736a/GUIA_PRUEBAS_Y_DEBUG.md)
1. Definir `memory_spec.md` con taxonomía, esquema JSONL, reglas de escritura, reglas de lectura, compaction y confidence. [arxiv](https://arxiv.org/html/2412.15266v1)
2. Implementar `research_memory.jsonl` y un escritor mínimo que lea de `runledger`, `triage`, `qualityvalidation`, `loopstopdecision` y búsquedas de alto valor. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/d4a133be-2aa0-4b95-b016-8f470c1208cd/02-orquestador.md)
3. Añadir un motor de retrieval híbrido por goal type. [huggingface](https://huggingface.co/papers/2412.15266)
4. Implementar compaction y promotion de episodios a lessons/hypotheses. [arxiv](https://arxiv.org/html/2412.15266)
5. Exponerlo en la API y Cockpit. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/eaff78ad-aa42-4cc0-8416-fdbe5633e043/03-servidor-api.md)
6. Solo entonces conectarlo al Goal Manager y al Scheduler autónomo. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/790e1dff-f22c-4e67-8d36-eee7e54ce79a/01-arquitectura.md)

Mi juicio directo es este: si el punto 1 define **qué** debe querer el sistema, el punto 2 define **cómo deja de ser amnésico y empieza a volverse investigador de verdad**. [arxiv](http://arxiv.org/pdf/2408.09559.pdf)
Sin esta capa, el modo autónomo será más bien un loop caro con apariencia de agencia; con esta capa, ya puede acumular criterio, evitar repeticiones y sostener una línea de investigación real a través del tiempo. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c91770e8-e26e-48ca-9b93-3b6c646bdc7f/ESTADO_Y_OBJETIVO.md)

