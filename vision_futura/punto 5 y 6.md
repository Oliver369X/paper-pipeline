Punto 5: MathDebuggingLoop
El problema de fondo que resuelve
Cursor ante un NaN loss o un Tensor shape mismatch tiende a aplicar parches: añade un clamp(), envuelve en try/except, o simplemente comenta el test que falla. Tres iteraciones de eso y el código queda con 3 capas de parches que esconden un error matemático fundamental que sigue siendo incorrecto.

El MathErrorClassifier — Diagnóstico antes de la consulta
Antes de llamar a Perplexity, el módulo analiza el stack trace con pattern matching y categoriza el error en 9 clases: NAN_LOSS, TENSOR_SHAPE_MISMATCH, FEATURE_COLLAPSE, GRADIENT_EXPLOSION, CUDA_OOM, etc. Esto es crítico porque cada clase tiene un prompt especializado completamente distinto. Para NAN_LOSS, Perplexity recibe: "¿Qué operación exacta produce NaN aquí? ¿Dice el paper original algo sobre estabilidad numérica? Dame la implementación con log-sum-exp trick." Para FEATURE_COLLAPSE (relevante para tus SAEs en interpretabilidad), la consulta pide el schedule de coeficiente L1 recomendado por Anthropic 2023 y la inicialización correcta del decoder.

El flujo de escalación
Cursor falla → record_cursor_failure() → contador interno sube

Al tercer fallo → escalate_to_perplexity() → se arma el DebugTrace (stack trace + código de la función + ecuaciones del DCA relacionadas + lista de parches ya intentados para que Perplexity no los repita)

Perplexity devuelve un MathDiagnosis con causa raíz teórica, corrección arquitectónica, código corregido y referencias a papers

Si Perplexity tiene confianza LOW o dice "I'm not sure" → _generate_human_briefing() → un .md estructurado aterriza en outputs/human_briefing_EXP-XXX.md

El Human Briefing (No un log crudo)
El briefing que recibe el humano tiene 5 secciones: el error en contexto, qué ya se intentó (para no repetirlo), el diagnóstico de Perplexity con su confianza, el código propuesto, y una lista de 5 pasos concretos de qué debe hacer el humano. Nada de logs de 300 líneas sin contexto.

Punto 6: La Plantilla Definitiva de mission.md
Tienes el generador Python y un ejemplo concreto listo para tu dominio de interpretabilidad mecanicista.

Las 9 secciones del mission.md
Cada sección controla una capa distinta del sistema:

Sección	Qué controla
hypotheses[]	Array de N hipótesis → N agentes paralelos en Worktrees
epistemic_injection	Cuántos papers buscar + poison pills propias o auto-generadas
compute	Umbral de VRAM para decidir Colab MCP vs local
quality_gates	Métrica SOTA, márgenes de Breakthrough/Replicación, bootstrap CI
debugging	Intentos de Cursor y Perplexity antes de escalar a humano
skill_orchestrator	Qué fases habilitar y skills extra por fase
perplexity	Máx llamadas, foco académico, directivas por sección del paper
notion	Base de datos, sincronización automática, notificación en Breakthrough
safety	Tiempo máximo, costo máximo, allow_force_push: false siempre
El ejemplo concreto de Interpretabilidad Mecanicista
Incluí un mission.md listo para usar con 3 hipótesis paralelas sobre el problema de feature collapse en SAEs (que es tu área de investigación real): L1 dinámica con warm-up, inicialización PCA del decoder, y auxiliary loss para features muertos. Los criterios de éxito son concretos y medibles, y las limitaciones conocidas están escritas con honestidad intelectual.

