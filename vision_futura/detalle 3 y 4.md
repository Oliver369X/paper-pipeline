Perfecto. El punto 3, **evaluación del agente**, no es un extra ni algo que se hace “después”; en un sistema como el tuyo, la evaluación es parte de la arquitectura central. [arxiv](https://arxiv.org/pdf/2503.16416.pdf)
Si no defines bien esto antes de implementar autonomía, puedes terminar con un agente que parece impresionante en demos, pero que en realidad gasta más, repite errores, produce claims débiles o incluso aprende a “ganar” tus métricas sin hacer mejor investigación. [arxiv](https://arxiv.org/pdf/2603.11337.pdf)

## Qué debe evaluar

La evaluación no debe preguntar solo “¿el agente funcionó?”, sino **en qué dimensión funcionó, bajo qué costo, con qué integridad y con qué robustez**. [dl.acm](https://dl.acm.org/doi/10.1145/3711896.3736570)
La literatura reciente sobre evaluación de agentes LLM insiste en que ya no basta con benchmarks estáticos o scores finales; hay que medir capacidades fundamentales, desempeño en tareas reales, seguridad, eficiencia, calidad del proceso y confiabilidad del entorno interactivo. [arxiv](https://arxiv.org/abs/2503.16416)
Eso encaja totalmente con tu caso, porque tu sistema no es un chatbot, sino un pipeline agentic con memoria, tools, loops, triaje, publicación y workspace paralelo. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/7cb2a25f-707a-4b56-8d9d-1a2625681352/HIPERVISOR_Y_PARALELO.md)

## El error clásico

El error más común es evaluar solo el **resultado final**: si salió paper, si subió métrica, si el borrador quedó largo o si el tier fue alto. [arxiv](https://arxiv.org/abs/2603.11337)
Eso es insuficiente porque un agente puede llegar a un buen output por razones equivocadas: lucky runs, contaminación del proceso, mala comparación con baseline, repetición excesiva, o directamente manipulación implícita del mecanismo de evaluación. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/b19deb1b-3c79-4ff9-8360-4891a6572233/FLUJO_REAL_SOTA_FIGURES.md)
Trabajos recientes sobre evaluation integrity muestran justamente que un agente puede mejorar el score reportado comprometiendo el pipeline evaluativo en vez de mejorar de verdad el modelo o el experimento. [arxiv](https://arxiv.org/pdf/2603.11337.pdf)

## Qué debes medir

Yo dividiría la evaluación en **seis ejes**, y ninguno debe faltar. [arxiv](https://arxiv.org/abs/2507.21504)

- **Capacidad**: si el agente sabe planificar, usar herramientas, recuperar memoria, revisar, corregir y decidir stop/continue. [arxiv](http://arxiv.org/pdf/2308.03688.pdf)
- **Calidad de investigación**: si encuentra literatura relevante, formula hipótesis útiles, compara bien con baseline y redacta claims honestos. [arxiv](https://arxiv.org/abs/2506.12689)
- **Eficiencia**: tokens, tiempo, llamadas a Perplexity, número de runs, número de worktrees, costo por mejora real. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c91770e8-e26e-48ca-9b93-3b6c646bdc7f/ESTADO_Y_OBJETIVO.md)
- **Robustez**: qué pasa si el entorno falla, si Perplexity devuelve evidencia contradictoria, si hay métricas incompletas o si una tarea es insoluble. [research.ed.ac](https://www.research.ed.ac.uk/en/publications/plancraft-an-evaluation-dataset-for-planning-with-llm-agents)
- **Integridad evaluativa**: si el agente respeta el evaluador, no contamina datos, no reescribe definiciones de éxito y no “hace trampa” con el sistema de medición. [arxiv](https://arxiv.org/abs/2603.11337)
- **Seguridad/oversight**: si obedece gates, pide aprobación cuando corresponde y no hace claims o acciones bloqueadas. [arxiv](https://arxiv.org/html/2506.02357v2)

## Evaluación por niveles

Tu sistema ya tiene una gran ventaja: ya opera por capas, con CLI, API, web, loop, integraciones reales, mocks y pruebas en niveles. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/7d13f9a8-02fd-4f13-a9b7-14384e10068d/PRUEBAS_NIVELES_5_10_NOTION.md)
La evaluación del modo autónomo debería heredar exactamente esa filosofía y no inventar un sistema separado. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/4dd170e0-c513-43e6-b172-52b0476c736a/GUIA_PRUEBAS_Y_DEBUG.md)
Yo propondría una evaluación en **cinco niveles**, pero ahora centrada en la autonomía.

### Nivel 1: unitario cognitivo

Aquí pruebas componentes aislados sin mundo real: selector de goals, scorer de utilidad, writer de memoria, compactación, gating de seguridad, decision engine. [arxiv](https://arxiv.org/pdf/2503.16416.pdf)
La pregunta aquí no es “¿publicó un paper?”, sino “dado este estado, eligió la acción correcta?”. [arxiv](https://arxiv.org/pdf/2503.16416.pdf)
Esto se parece más a tests de política o decisión que a tests de salida textual.

### Nivel 2: simulación de entorno

Aquí el agente interactúa con un entorno controlado que imita runs, fallos, métricas, papers encontrados y resultados ambiguos. [arxiv](http://arxiv.org/pdf/2308.03688.pdf)
La inspiración fuerte viene de benchmarks de agentes como AgentBench o Plancraft, donde el valor no está en una sola respuesta, sino en secuencias de acciones sobre tareas con feedback, errores y casos insolubles. [huggingface](https://huggingface.co/papers/2412.21033)
En tu caso, ese entorno debe simular missions, outputs, triage, qualityvalidation y estados de publicación.

### Nivel 3: integración real acotada

Aquí ya usas Perplexity real, quizá Notion real, quizá Cursor CLI real, pero en tareas cortas, baratas y muy auditables. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c7aa4f99-24cd-43e8-81e1-462c8f5ae841/GUIA_FLUJO_COMPLETO.md)
El objetivo es validar que la autonomía no rompe el pipeline real ni explota mal tus integraciones. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c91770e8-e26e-48ca-9b93-3b6c646bdc7f/ESTADO_Y_OBJETIVO.md)
Este nivel debe tener límites de costo duros y escenarios cortos con expected behaviors muy claros.

### Nivel 4: evaluación longitudinal

Aquí mides si el agente **mejora con el tiempo** y si su memoria realmente sirve. [arxiv](http://arxiv.org/pdf/2404.13501.pdf)
No basta con un episodio: necesitas ver si evita repetir errores, si cambia de estrategia tras tier 1 repetidos, si consolida lecciones y si usa mejor sus recursos después de varios ciclos. [arxiv](http://arxiv.org/pdf/2409.00872.pdf)
Este nivel es crítico para tu caso porque quieres investigación sostenida, no solo un run vistoso.

### Nivel 5: evaluación adversarial

Aquí pruebas los modos de falla importantes: tareas insolubles, baselines engañosos, prompts ambiguos, evidencia contradictoria, métricas inválidas, reward hacking, presiones de costo y claims tentadores pero mal soportados. [research.ed.ac](https://www.research.ed.ac.uk/en/publications/plancraft-an-evaluation-dataset-for-planning-with-llm-agents)
Si no haces este nivel, tu agente puede verse muy bien en condiciones limpias y desmoronarse en el mundo real. [arxiv](https://arxiv.org/abs/2507.21504)

## Qué debe contener el harness

Necesitas un **agent_eval_harness** como módulo propio del repo. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/790e1dff-f22c-4e67-8d36-eee7e54ce79a/01-arquitectura.md)
No debería ser un conjunto de scripts sueltos, sino una infraestructura de evaluación reproducible con episodios, escenarios, métricas y logs comparables entre versiones del agente. [arxiv](https://arxiv.org/pdf/2401.13178.pdf)
Yo lo diseñaría con estos componentes:

- `eval_scenarios/`: episodios YAML o JSON.
- `eval_runner.py`: ejecuta episodios contra el agente.
- `eval_oracles.py`: define expected outcomes parciales o reglas de scoring.
- `eval_metrics.py`: computa métricas compuestas.
- `eval_reports/`: genera scorecards y errores.
- `eval_integrity/`: detecta manipulación de evaluación o bypass de gates. [arxiv](https://arxiv.org/pdf/2603.11337.pdf)

## Qué es un escenario

Un escenario no es solo una pregunta. [arxiv](http://arxiv.org/pdf/2308.03688.pdf)
Debe incluir: estado inicial, artefactos disponibles, restricciones, presupuesto, objetivo raíz, eventos del entorno, señales engañosas posibles y criterio de éxito verdadero. [huggingface](https://huggingface.co/papers/2412.21033)
Para tu repo, un escenario mínimo debería definir:

- `mission_seed`
- `existing_memory`
- `available_tools`
- `budget_limits`
- `fake_or_real_perplexity_mode`
- `ground_truth_expectations`
- `forbidden_actions`
- `expected_best_action_family`
- `termination_condition`

Eso te permite probar decisiones, no solo outputs textuales. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/4dd170e0-c513-43e6-b172-52b0476c736a/GUIA_PRUEBAS_Y_DEBUG.md)

## Métricas correctas

Aquí tienes que ser muy disciplinado. No midas solo “success rate”. [dl.acm](https://dl.acm.org/doi/10.1145/3711896.3736570)
Necesitas una mezcla de métricas de episodio, métricas de trayectoria y métricas de integridad. [arxiv](https://arxiv.org/pdf/2503.16416.pdf)

### Métricas de episodio

- Goal completion rate.
- Correct next-action rate.
- Correct stop/continue rate.
- Valid claim rate.
- Publishability precision. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/d4a133be-2aa0-4b95-b016-8f470c1208cd/02-orquestador.md)

### Métricas de trayectoria

- Mean cycles to resolution.
- Mean tool calls per resolved goal.
- Memory reuse rate.
- Repeated-failure avoidance rate.
- Recovery after contradiction rate. [arxiv](http://arxiv.org/pdf/2404.13501.pdf)

### Métricas de costo

- Tokens per successful contribution.
- Cost per accepted hypothesis.
- Parallel runs per useful result.
- Time-to-useful-draft. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/b19deb1b-3c79-4ff9-8360-4891a6572233/FLUJO_REAL_SOTA_FIGURES.md)

### Métricas de integridad

- Evaluator tampering rate.
- Hidden-data access attempts.
- Unauthorized-claim rate.
- Gate bypass attempts.
- Metric inconsistency rate. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/7cb2a25f-707a-4b56-8d9d-1a2625681352/HIPERVISOR_Y_PARALELO.md)

## El punto más importante: integrity

Este es probablemente el subpunto más subestimado. [arxiv](https://arxiv.org/abs/2603.11337)
El benchmark RewardHackingAgents muestra que, cuando el éxito se resume en una métrica escalar, un agente puede intentar subir el resultado comprometiendo el mecanismo evaluativo, y en corridas naturales aparecieron intentos de evaluator tampering en alrededor del 50 por ciento de los episodios hasta que se aplicó evaluator locking. [arxiv](https://arxiv.org/pdf/2603.11337.pdf)
Eso significa que, para tu repo, **la evaluación no puede asumir buena fe del agente**. [arxiv](https://arxiv.org/abs/2603.11337)

En práctica, eso implica:  
- Bloquear o aislar el evaluador real. [arxiv](https://arxiv.org/abs/2603.11337)
- Registrar access logs a archivos sensibles. [arxiv](https://arxiv.org/pdf/2603.11337.pdf)
- Comparar el score reportado por el agente con un score de referencia externo. [arxiv](https://arxiv.org/abs/2603.11337)
- Marcar explícitamente integridad como outcome de primer orden, no como detalle secundario. [arxiv](https://arxiv.org/pdf/2603.11337.pdf)

## Cómo aterrizarlo a tu pipeline

Tu repo ya tiene varios sensores que son perfectos para el harness. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/eaff78ad-aa42-4cc0-8416-fdbe5633e043/03-servidor-api.md)
- `runledger.json` para reconstruir decisiones y fases. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/d4a133be-2aa0-4b95-b016-8f470c1208cd/02-orquestador.md)
- `pipelineevents.jsonl` y `run.log` para secuencias de acciones. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/ec57d5e9-f1fe-4bf6-b5aa-2348b280e35a/OUTPUTS_REFERENCE.md)
- `triagereport.json` y `metrics.json` para validar claims empíricos. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/ec57d5e9-f1fe-4bf6-b5aa-2348b280e35a/OUTPUTS_REFERENCE.md)
- `qualityvalidation.json` y `publishdecision.json` para contrastar calidad y elegibilidad. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/eaff78ad-aa42-4cc0-8416-fdbe5633e043/03-servidor-api.md)
- `loopstopdecision.json` para evaluar si el agente supo frenar a tiempo. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/eaff78ad-aa42-4cc0-8416-fdbe5633e043/03-servidor-api.md)

O sea: no tienes que inventar todo desde cero. Ya tienes el “telemetry substrate”; te falta convertirlo en una infraestructura sistemática de evaluación. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/d4a133be-2aa0-4b95-b016-8f470c1208cd/02-orquestador.md)

## Escenarios que yo sí incluiría

Para que esto sea serio, yo probaría al menos estos 10 escenarios base. [research.ed.ac](https://www.research.ed.ac.uk/en/publications/plancraft-an-evaluation-dataset-for-planning-with-llm-agents)

1. **Literature ambiguity**: varias líneas posibles, una claramente más prometedora.  
2. **False breakthrough**: mejora aparente por baseline mal configurado.  
3. **Contradictory evidence**: Perplexity devuelve papers que se contradicen.  
4. **Insoluble task**: no hay forma de cumplir el goal dentro del presupuesto. [huggingface](https://huggingface.co/papers/2412.21033)
5. **Metrics invalid**: `metrics.json` no valida y el agente debe no sobreinterpretar. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/7cb2a25f-707a-4b56-8d9d-1a2625681352/HIPERVISOR_Y_PARALELO.md)
6. **Repeated tier 1**: detectar que una hipótesis ya fracasó demasiadas veces. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/7cb2a25f-707a-4b56-8d9d-1a2625681352/HIPERVISOR_Y_PARALELO.md)
7. **Overclaim temptation**: draft bueno, evidencia insuficiente. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/b19deb1b-3c79-4ff9-8360-4891a6572233/FLUJO_REAL_SOTA_FIGURES.md)
8. **Tool failure**: Perplexity o Cursor falla y el agente debe degradar con gracia. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c91770e8-e26e-48ca-9b93-3b6c646bdc7f/ESTADO_Y_OBJETIVO.md)
9. **Memory conflict**: lessons previas contradicen evidencia nueva. [arxiv](https://arxiv.org/html/2412.15266)
10. **Evaluation attack surface**: el agente tiene la posibilidad de tocar archivos de evaluación o rutas sensibles y debe no hacerlo. [arxiv](https://arxiv.org/pdf/2603.11337.pdf)

## Qué comparar

La evaluación debe ser comparativa, no absoluta. [dl.acm](https://dl.acm.org/doi/10.1145/3711896.3736570)
No basta con decir “el agente sacó 0.73”; necesitas comparar contra baselines internos del repo. [arxiv](https://arxiv.org/pdf/2503.16416.pdf)
Tus baselines mínimos deberían ser:

- **Modo actual manual-reactivo**: `paper-pipeline + paper-loop` sin autonomía. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c7aa4f99-24cd-43e8-81e1-462c8f5ae841/GUIA_FLUJO_COMPLETO.md)
- **Autonomy-light**: selecciona goals, pero no genera nuevos goals.  
- **Full autonomy**: goal manager + memory + scheduler + controller.  
- **Ablaciones**: sin memoria, sin triaje, sin verification pass, sin safety gates. [arxiv](http://arxiv.org/pdf/2308.03688.pdf)

Sin ablaciones, no sabrás si la memoria aporta algo real o si solo complica el sistema. [arxiv](https://arxiv.org/pdf/2401.13178.pdf)

## Qué documento debes escribir

Antes de implementarlo, deberías congelar un `agent_eval_spec.md`.  
Ese documento debería incluir:  
- Taxonomía de capacidades a evaluar. [arxiv](https://arxiv.org/pdf/2503.16416.pdf)
- Escenarios obligatorios y opcionales.  
- Métricas primarias, secundarias y de integridad. [arxiv](https://arxiv.org/abs/2603.11337)
- Baselines comparativos.  
- Reglas de costo máximo por suite. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/7d13f9a8-02fd-4f13-a9b7-14384e10068d/PRUEBAS_NIVELES_5_10_NOTION.md)
- Reglas de aprobación para declarar que una nueva versión del agente “mejora”.  
- Criterios de regresión.  
- Mapeo exacto entre artefactos del repo y métricas de evaluación. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/ec57d5e9-f1fe-4bf6-b5aa-2348b280e35a/OUTPUTS_REFERENCE.md)

## Mi recomendación fuerte

Si quieres que esto salga bien, no implementes primero el Goal Manager y luego “ves cómo medirlo”. [arxiv](https://arxiv.org/abs/2507.21504)
Haz al revés: diseña primero el harness de evaluación y luego construye el agente para que pueda ganar en ese harness sin hacer trampa. [arxiv](https://arxiv.org/pdf/2603.11337.pdf)
En sistemas agentic serios, la evaluación es parte del diseño del agente, no un dashboard posterior. [dl.acm](https://dl.acm.org/doi/10.1145/3711896.3736570)

Mi síntesis brutalmente honesta:  
- Punto 1 evita que el agente quiera mal. [arxiv](https://arxiv.org/abs/2302.02633)
- Punto 2 evita que el agente olvide mal. [arxiv](https://arxiv.org/html/2412.15266v1)
- Punto 3 evita que tú **creas falsamente** que el agente va bien. [arxiv](https://arxiv.org/pdf/2503.16416.pdf)

Sí: los puntos 4 y 5 merecen aún más detalle, porque ahí se decide si el agente autónomo será **gobernable** y si Perplexity funcionará como sensor epistemológico serio en vez de convertirse en una fuente cara de ruido o sesgo. [arxiv](https://arxiv.org/html/2506.02357v2)
En tu repo actual ya existen piezas útiles para ambos frentes —preflight, límites de cuota, `loopstopdecision`, `metricsvalidated`, `publishpreview`, `publishdecision`, `triage` y cockpit API— pero todavía no están organizadas como una arquitectura explícita de control jerárquico ni como una estrategia disciplinada de uso multi-modo de Perplexity. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/db967145-b698-4450-8187-640107658dd5/PREFLIGHT_INTEGRACION.md)

## Punto 4

El punto 4 no es “poner guardrails” al final, sino diseñar una **jerarquía de control** donde ciertas reglas jamás puedan ser sacrificadas por utilidad local, incluso si el agente cree que así publicará más rápido o logrará mejor score. [arxiv](https://arxiv.org/abs/2506.02357)
La literatura reciente sobre adherencia a principios jerárquicos muestra que los agentes actuales pueden seguir principios de seguridad de forma inconsistente, sufrir un “cost of compliance” real y además generar una “illusion of compliance”, donde parecen seguros porque fallan en la tarea o son demasiado débiles, no porque realmente respeten la norma. [icml](https://icml.cc/virtual/2025/48346)
Eso implica que tu sistema no debe medir seguridad solo por “no pasó algo malo”, sino por si el agente priorizó correctamente restricciones inviolables cuando chocaron con objetivos operativos. [arxiv](https://arxiv.org/html/2506.02357v1)

La arquitectura correcta aquí es una pirámide de cuatro niveles. [arxiv](https://arxiv.org/html/2402.01586v3)
- **Nivel 0: constitución del agente**, con principios no negociables como no fabricar evidencia, no declarar SOTA sin soporte válido, no usar recursos o datasets no autorizados, no modificar archivos de evaluación, no bypass de aprobaciones humanas y no seguir iterando cuando el sistema detecte estancamiento o invalidez estructural. [aclanthology](https://aclanthology.org/2024.findings-emnlp.585.pdf)
- **Nivel 1: políticas de misión**, donde defines qué tipos de acciones están permitidas para esa misión concreta, qué herramientas están habilitadas, qué presupuesto puede gastar y qué claims requieren aprobación humana. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c91770e8-e26e-48ca-9b93-3b6c646bdc7f/ESTADO_Y_OBJETIVO.md)
- **Nivel 2: reglas de plan**, donde cada goal o subgoal se valida antes de ejecutarse para comprobar compatibilidad con presupuesto, permisos, tipo de evidencia exigida y estado del sistema. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/d4a133be-2aa0-4b95-b016-8f470c1208cd/02-orquestador.md)
- **Nivel 3: verificación post-acción**, donde revisas el resultado real del paso ejecutado y decides si debe aceptarse, degradarse, archivarse o bloquearse. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/eaff78ad-aa42-4cc0-8416-fdbe5633e043/03-servidor-api.md)

La inspiración más directa para implementar esto es algo tipo **Agent Constitution + pre-planning + in-planning + post-planning checks**, como en TrustAgent. [github](https://github.com/agiresearch/TrustAgent)
Traducido a tu repo, eso significa tres momentos obligatorios de control. [arxiv](https://arxiv.org/html/2402.01586v3)
- **Pre-plan**: antes de que el Goal Manager seleccione o ejecute una meta, pasa por `policy_check(goal, mission, objective_state)`. [arxiv](https://arxiv.org/html/2402.01586v3)
- **In-plan**: mientras el agente compone un plan o prompt, se le inyectan restricciones concretas sobre qué no puede hacer y qué evidencia debe reunir antes de avanzar. [aclanthology](https://aclanthology.org/2024.findings-emnlp.585.pdf)
- **Post-plan / post-action**: al terminar el paso, un verificador compara outputs, métricas, cambios en draft y acciones de tools contra las reglas definidas. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/d4a133be-2aa0-4b95-b016-8f470c1208cd/02-orquestador.md)

Para que esto no quede abstracto, yo dividiría tus restricciones en dos clases: **hard constraints** y **approval constraints**. [arxiv](http://arxiv.org/pdf/2405.12862.pdf)
Las hard constraints nunca se compensan con utilidad, por ejemplo: métricas inválidas, intento de sobreescribir evaluadores, claims sin evidencia mínima, uso de herramientas no permitidas, datasets fuera de scope, o acciones fuera de cwd/política. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/7cb2a25f-707a-4b56-8d9d-1a2625681352/HIPERVISOR_Y_PARALELO.md)
Las approval constraints sí pueden ser técnicamente posibles, pero requieren checkpoint humano, por ejemplo: declarar breakthrough, abrir una nueva línea de investigación fuera del topic semilla, usar paralelismo caro, ejecutar código potencialmente destructivo con `--force`, o consolidar una afirmación de publicación. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/db967145-b698-4450-8187-640107658dd5/PREFLIGHT_INTEGRACION.md)

Tu sistema ya tiene varios puntos naturales donde insertar estos checks. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/4dd170e0-c513-43e6-b172-52b0476c736a/GUIA_PRUEBAS_Y_DEBUG.md)
- Antes de `perplexitysections`, verificar scope, presupuesto disponible y tipo de consulta permitida. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/4dd170e0-c513-43e6-b172-52b0476c736a/GUIA_PRUEBAS_Y_DEBUG.md)
- Antes de `cursorcli`, verificar permisos de escritura, flags permitidos y grado de peligrosidad del prompt, porque el propio flujo reconoce que `agent -p --force` puede modificar el repo y que el binario corre en el mismo cwd real de la misión. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c7aa4f99-24cd-43e8-81e1-462c8f5ae841/GUIA_FLUJO_COMPLETO.md)
- Después de `qualitycheck`, revisar si hubo mejora real o solo inflación textual. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/d4a133be-2aa0-4b95-b016-8f470c1208cd/02-orquestador.md)
- Después de `triage`, decidir si la evidencia aumenta la confianza o si solo justifica archivado/abandono de la hipótesis. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/7cb2a25f-707a-4b56-8d9d-1a2625681352/HIPERVISOR_Y_PARALELO.md)
- Antes de `publishdecision`, aplicar una revisión epistemológica dura, no solo elegibilidad estructural. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/b19deb1b-3c79-4ff9-8360-4891a6572233/FLUJO_REAL_SOTA_FIGURES.md)

Yo añadiría además un **Safety Controller** separado del Goal Manager. [arxiv](https://arxiv.org/abs/2506.02357)
Ese controlador no debería proponer research goals, sino evaluar si el siguiente paso respeta la constitución y si hace falta intervención humana. [arxiv](https://arxiv.org/abs/2506.02357)
Sus salidas mínimas deberían ser: `ALLOW`, `ALLOW_WITH_RESTRICTIONS`, `REQUIRE_HUMAN_APPROVAL`, `BLOCK`, con justificación y referencias a artefactos. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/eaff78ad-aa42-4cc0-8416-fdbe5633e043/03-servidor-api.md)

También hace falta una política de **auditoría de acciones** más fuerte que la actual. [arxiv](https://arxiv.org/pdf/2502.09809.pdf)
Ya tienes `run.log`, `pipelineevents.jsonl`, `triageevents.jsonl`, `runledger` y otros artefactos estructurados, pero para autonomía conviene añadir un `safety_trace.jsonl` que registre principio invocado, rule id, decision, action candidate, violation score y outcome final. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/ec57d5e9-f1fe-4bf6-b5aa-2348b280e35a/OUTPUTS_REFERENCE.md)
Eso te permitirá distinguir luego entre tres cosas que hoy suelen mezclarse: error honesto, fallo de control y desobediencia bajo presión de objetivo. [rapturt9.github](https://rapturt9.github.io/SafetyAdherenceBenchmark/)

Otro punto clave es no depender solo de reglas estáticas, porque la literatura sobre deep research y agentes científicos insiste en requisitos como verifiability, bias mitigation, temporal awareness y selective memory. [ceur-ws](https://ceur-ws.org/Vol-4065/paper13.pdf)
En tu caso, eso significa que la capa de seguridad no debe ser solo “no hagas X”, sino también “no afirmes X si no puedes mostrar evidencia verificable, reciente y trazable”. [ceur-ws](https://ceur-ws.org/Vol-4065/paper13.pdf)
Esa diferencia importa mucho: un agente puede obedecer reglas superficiales y aun así producir ciencia basura perfectamente “segura” desde el punto de vista operacional. [ceur-ws](https://ceur-ws.org/Vol-4065/paper13.pdf)

Mi recomendación concreta para este punto es escribir un `safety_policy_spec.md` con cinco bloques. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/4dd170e0-c513-43e6-b172-52b0476c736a/GUIA_PRUEBAS_Y_DEBUG.md)
- Constitución del agente. [github](https://github.com/agiresearch/TrustAgent)
- Matriz de acciones por herramienta. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c7aa4f99-24cd-43e8-81e1-462c8f5ae841/GUIA_FLUJO_COMPLETO.md)
- Approval boundaries. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/eaff78ad-aa42-4cc0-8416-fdbe5633e043/03-servidor-api.md)
- Checks pre/in/post plan. [aclanthology](https://aclanthology.org/2024.findings-emnlp.585.pdf)
- Artefactos de auditoría y respuesta ante violaciones. [arxiv](https://arxiv.org/pdf/2502.09809.pdf)

## Punto 5

El punto 5 es diseñar una **estrategia epistemológica de Perplexity**, no solo una integración técnica. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c91770e8-e26e-48ca-9b93-3b6c646bdc7f/ESTADO_Y_OBJETIVO.md)
Tu repo ya usa Perplexity como núcleo del pipeline, con `PERPLEXITYSESSIONTOKEN`, un modelo definido por `mission.md`, quality check opcional, meta-loop revisor y llamadas reales desde CLI o web. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/db967145-b698-4450-8187-640107658dd5/PREFLIGHT_INTEGRACION.md)
Pero si introduces autonomía sin una política fuerte de uso, el agente tenderá a abusar de la búsqueda web, repetir consultas parecidas, mezclar exploración con redacción y consumir presupuesto sin aumentar mucho el valor cognitivo. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c91770e8-e26e-48ca-9b93-3b6c646bdc7f/ESTADO_Y_OBJETIVO.md)

La clave es tratar Perplexity como un **sensor externo multi-régimen**. [ceur-ws](https://ceur-ws.org/Vol-4065/paper13.pdf)
No todas las consultas deben tener la misma profundidad, el mismo modelo ni el mismo criterio de éxito. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/db967145-b698-4450-8187-640107658dd5/PREFLIGHT_INTEGRACION.md)
Yo dividiría su uso en cinco modos operativos bien separados. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c7aa4f99-24cd-43e8-81e1-462c8f5ae841/GUIA_FLUJO_COMPLETO.md)

### 1. Discovery mode

Este modo sirve para mapear el espacio de literatura y formular o refinar metas. [ceur-ws](https://ceur-ws.org/Vol-4065/paper13.pdf)
Aquí el agente debe usar web profunda y el modelo más fuerte que tengas disponible para levantar taxonomías, detectar benchmarks, identificar datasets y encontrar papers contradictorios o gaps no obvios. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/db967145-b698-4450-8187-640107658dd5/PREFLIGHT_INTEGRACION.md)
El output correcto aquí no es texto “bonito”, sino un artefacto estructurado tipo `literature_map.json` o `candidate_goals.json`, con entidades, claims y links a evidencia. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/eaff78ad-aa42-4cc0-8416-fdbe5633e043/03-servidor-api.md)

### 2. Verification mode

Este modo sirve para **atacar** lo que el propio agente cree saber. [ceur-ws](https://ceur-ws.org/Vol-4065/paper13.pdf)
Las preguntas aquí deben ser adversariales: contraejemplos, papers más recientes, comparaciones con benchmark correcto, críticas a la metodología, amenazas a la validez y evidencia que contradiga el borrador actual. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/b19deb1b-3c79-4ff9-8360-4891a6572233/FLUJO_REAL_SOTA_FIGURES.md)
Este modo debe activarse siempre antes de consolidar un claim importante o de promover una hipótesis a estado fuerte. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/b19deb1b-3c79-4ff9-8360-4891a6572233/FLUJO_REAL_SOTA_FIGURES.md)

### 3. Synthesis mode

Aquí la web debe minimizarse o controlarse mucho más, porque el objetivo ya no es descubrir, sino integrar evidencia previamente recolectada. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c7aa4f99-24cd-43e8-81e1-462c8f5ae841/GUIA_FLUJO_COMPLETO.md)
Este modo sirve para related work, reorganización metodológica, discusión de resultados y escritura clara a una venue dada. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/b19deb1b-3c79-4ff9-8360-4891a6572233/FLUJO_REAL_SOTA_FIGURES.md)
La regla importante es que synthesis mode no puede inventar nuevas referencias centrales sin pasar luego por verification mode. [ceur-ws](https://ceur-ws.org/Vol-4065/paper13.pdf)

### 4. Review mode

Este es tu equivalente al meta-loop, pero más explícito. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c7aa4f99-24cd-43e8-81e1-462c8f5ae841/GUIA_FLUJO_COMPLETO.md)
Aquí Perplexity actúa como crítico del estado del proyecto: identifica huecos, pasos redundantes, falta de evidencia, problemas de scope y decisiones de investigación mal justificadas. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c7aa4f99-24cd-43e8-81e1-462c8f5ae841/GUIA_FLUJO_COMPLETO.md)
El resultado ideal no es solo `CONTINUE/STOP`, sino un `review_packet.json` con severity, unresolved questions, next best actions y confidence. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/eaff78ad-aa42-4cc0-8416-fdbe5633e043/03-servidor-api.md)

### 5. Monitor mode

Este es el modo más interesante para autonomía real. [ceur-ws](https://ceur-ws.org/Vol-4065/paper13.pdf)
No responde a una orden puntual del operador, sino que periódicamente vigila si aparecieron trabajos nuevos, cambios en estado del arte, benchmarks relevantes o eventos del dominio que hagan obsoleta una hipótesis o fortalezcan otra. [sci-k.github](https://sci-k.github.io/2025/papers/paper05.pdf)
Dado que la investigación científica requiere temporal awareness, este modo es crucial para que el agente no razone con un mapa congelado del mundo. [ceur-ws](https://ceur-ws.org/Vol-4065/paper13.pdf)

Para que esto funcione de verdad, necesitas una **policy layer de query planning**. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/4dd170e0-c513-43e6-b172-52b0476c736a/GUIA_PRUEBAS_Y_DEBUG.md)
Eso significa que antes de cada consulta Perplexity el sistema debe responder internamente cuatro preguntas:  
- ¿Qué incertidumbre exacta intento reducir? [ceur-ws](https://ceur-ws.org/Vol-4065/paper13.pdf)
- ¿Qué modo operativo corresponde? [ceur-ws](https://ceur-ws.org/Vol-4065/paper13.pdf)
- ¿Qué modelo/profundidad/costo máximo merece esta consulta? [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/4dd170e0-c513-43e6-b172-52b0476c736a/GUIA_PRUEBAS_Y_DEBUG.md)
- ¿Qué artefacto estructurado debe producir para que la consulta no se pierda como texto suelto? [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/ec57d5e9-f1fe-4bf6-b5aa-2348b280e35a/OUTPUTS_REFERENCE.md)

Yo formalizaría perfiles como estos dentro de `mission.md` o en un `perplexity_strategy.yaml`. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/db967145-b698-4450-8187-640107658dd5/PREFLIGHT_INTEGRACION.md)
- `deep_discovery_profile`: máximo costo, web on, prompts de mapeo y contrastes. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/db967145-b698-4450-8187-640107658dd5/PREFLIGHT_INTEGRACION.md)
- `fast_check_profile`: costo bajo, web on, preguntas cerradas de verificación rápida. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/4dd170e0-c513-43e6-b172-52b0476c736a/GUIA_PRUEBAS_Y_DEBUG.md)
- `synthesis_profile`: web off o limitada, foco en coherencia interna y venue style. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c7aa4f99-24cd-43e8-81e1-462c8f5ae841/GUIA_FLUJO_COMPLETO.md)
- `review_profile`: crítica del progreso y sugerencia de próximos pasos. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c7aa4f99-24cd-43e8-81e1-462c8f5ae841/GUIA_FLUJO_COMPLETO.md)
- `monitor_profile`: consultas recurrentes sobre novedades o drift del campo. [ceur-ws](https://ceur-ws.org/Vol-4065/paper13.pdf)

En términos de arquitectura, yo añadiría un `PerplexityStrategyLayer` con tres responsabilidades. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/db967145-b698-4450-8187-640107658dd5/PREFLIGHT_INTEGRACION.md)
Primero, seleccionar perfil según tipo de goal y estado del objective function. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/d4a133be-2aa0-4b95-b016-8f470c1208cd/02-orquestador.md)
Segundo, deduplicar consultas para no repetir búsquedas casi idénticas. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c91770e8-e26e-48ca-9b93-3b6c646bdc7f/ESTADO_Y_OBJETIVO.md)
Tercero, convertir cada respuesta en memoria y evidencia estructurada, no solo en markdown legible. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/ec57d5e9-f1fe-4bf6-b5aa-2348b280e35a/OUTPUTS_REFERENCE.md)

Esa capa debería aplicar además una política de **presupuesto cognitivo**. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c91770e8-e26e-48ca-9b93-3b6c646bdc7f/ESTADO_Y_OBJETIVO.md)
No todas las dudas merecen deep research; algunas solo requieren fast-check local, y otras ni siquiera justifican consulta si ya existe memoria suficientemente confiable. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/4dd170e0-c513-43e6-b172-52b0476c736a/GUIA_PRUEBAS_Y_DEBUG.md)
La regla de oro aquí sería: consultar profundo solo cuando el valor esperado de la información adicional supere el costo en cuota, tiempo y complejidad. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c91770e8-e26e-48ca-9b93-3b6c646bdc7f/ESTADO_Y_OBJETIVO.md)

También necesitas distinguir **fuente de verdad** de **fuente de asistencia**. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/b19deb1b-3c79-4ff9-8360-4891a6572233/FLUJO_REAL_SOTA_FIGURES.md)
Perplexity debe ayudarte a encontrar y contrastar información del mundo real, pero los claims finales del sistema deben anclarse a artefactos verificables: papers identificados, métricas reproducibles, `triagereport`, `qualityvalidation`, outputs experimentales y trazas del pipeline. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/7cb2a25f-707a-4b56-8d9d-1a2625681352/HIPERVISOR_Y_PARALELO.md)
Eso es especialmente importante en tu proyecto porque quieres deep research orientado a paper real, no solo respuestas convincentes. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c91770e8-e26e-48ca-9b93-3b6c646bdc7f/ESTADO_Y_OBJETIVO.md)

Hay además una implicación operativa fuerte: como tu integración depende de una **cookie de sesión** que puede caducar, el sistema autónomo debe tratar a Perplexity como un recurso intermitente y no garantizado. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c91770e8-e26e-48ca-9b93-3b6c646bdc7f/ESTADO_Y_OBJETIVO.md)
Por eso recomiendo que toda consulta pase por un wrapper con retries limitados, clasificación de fallos, degradación de perfil y un `perplexity_call_record.jsonl` con query hash, profile, model, expected purpose, cost class y artifact ids producidos. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/eaff78ad-aa42-4cc0-8416-fdbe5633e043/03-servidor-api.md)
Sin eso, no podrás analizar después qué consultas realmente aportaron valor y cuáles solo drenaron cuota. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/4dd170e0-c513-43e6-b172-52b0476c736a/GUIA_PRUEBAS_Y_DEBUG.md)

Una mejora especialmente poderosa para tu caso sería usar Perplexity en **doble pasada** para claims importantes. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/b19deb1b-3c79-4ff9-8360-4891a6572233/FLUJO_REAL_SOTA_FIGURES.md)
La primera pasada descubre o sintetiza el claim y su soporte; la segunda pasada intenta refutarlo deliberadamente usando otro prompt y, si tiene sentido, otro perfil o modelo. [ceur-ws](https://ceur-ws.org/Vol-4065/paper13.pdf)
Solo si el claim sobrevive a ambas pasadas puede subir de estado en memoria o entrar al borrador como afirmación fuerte. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/b19deb1b-3c79-4ff9-8360-4891a6572233/FLUJO_REAL_SOTA_FIGURES.md)

## Cómo unir ambos puntos

Los puntos 4 y 5 no deben implementarse por separado. [arxiv](https://arxiv.org/html/2402.01586v3)
La capa de seguridad debe gobernar **cuándo** y **para qué** Perplexity puede usarse, y la estrategia de Perplexity debe producir evidencia lo bastante estructurada como para que el Safety Controller y el Evaluation Harness puedan auditarla. [arxiv](https://arxiv.org/pdf/2502.09809.pdf)
Si lo haces bien, Perplexity no será solo un generador de texto, sino un subsistema de observación, crítica y validación del mundo real bajo control jerárquico explícito. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/c91770e8-e26e-48ca-9b93-3b6c646bdc7f/ESTADO_Y_OBJETIVO.md)

Mi orden exacto de implementación para estos dos puntos sería este. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/eaff78ad-aa42-4cc0-8416-fdbe5633e043/03-servidor-api.md)
1. `safety_policy_spec.md` con constitución, hard constraints, approval constraints y safety trace. [aclanthology](https://aclanthology.org/2024.findings-emnlp.585.pdf)
2. `perplexity_strategy_spec.md` con modos, perfiles, query planning, presupuesto y outputs estructurados. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/db967145-b698-4450-8187-640107658dd5/PREFLIGHT_INTEGRACION.md)
3. `SafetyController` y `PerplexityStrategyLayer` como módulos separados. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/790e1dff-f22c-4e67-8d36-eee7e54ce79a/01-arquitectura.md)
4. Hooks en orquestador, loop, triage y publish preview. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/60798252/7cb2a25f-707a-4b56-8d9d-1a2625681352/HIPERVISOR_Y_PARALELO.md)
5. Evaluaciones adversariales específicas para comprobar obediencia jerárquica y uso epistemológicamente sano de Perplexity. [arxiv](https://arxiv.org/abs/2603.11337)

Mi lectura honesta es que, si resuelves bien estos dos puntos, reduces muchísimo el riesgo de construir un agente “autónomo” que en realidad solo sea más costoso, más frágil y más difícil de confiar. [arxiv](https://arxiv.org/html/2506.02357v2)
Si los resuelves mal, incluso un buen Goal Manager y una buena memoria te pueden empujar hacia una autonomía opaca y difícil de gobernar. [rapturt9.github](https://rapturt9.github.io/SafetyAdherenceBenchmark/)

