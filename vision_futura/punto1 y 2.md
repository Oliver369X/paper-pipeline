Punto 1: El EpistemicInjector
Este módulo resuelve el problema central que describiste: Cursor NO debe actuar como experto, debe serlo. El flujo técnico es el siguiente:

Flujo de Adquisición (4 llamadas secuenciales a Perplexity)
Antes de que Cursor escriba la primera línea, el EpistemicInjector llama al MCP de Perplexity con 4 queries hiperespecializadas:

SOTA Papers → "Top 20 papers de 2024-2026 sobre [Topic], con la contribución matemática en LaTeX"

Implementation Pitfalls → "Errores de implementación más comunes en [Topic] en PyTorch, con síntoma + fix verificado"

Reference Repos → "Top 5 repos SOTA en GitHub para [Topic], con sus decisiones arquitectónicas clave"

Compute Requirements → "Cuánta VRAM y tiempo necesita un experimento típico de [Topic]" — si la respuesta supera 12GB, se activa la delegación a Colab MCP automáticamente

El Domain Context Artifact (DCA)
Todo se compila en un domain_context.yaml estructurado, que incluye las técnicas SOTA, los errores conocidos con su solución documentada, y 3 Poison Pills (afirmaciones deliberadamente falsas, como "los Transformers fueron inventados por LeCun en 1998"). Si el evaluador externo acepta una Poison Pill → reward hacking detectado, loop detenido.

La Inyección en Cursor
El método generate_cursor_system_prompt(dca) genera el prompt exacto para cursor agent -p "..." que le dice al agente: "Tu conocimiento base es obsoleto. Tu ÚNICA fuente de verdad es este DCA. Si tu código viola estas matemáticas, fallará."

Colab MCP integrado
Si el DCA detecta que el experimento necesita más de 12GB de VRAM (ej. entrenar un SAE sobre GPT-4 scale), el prompt inyectado incluye una sección COMPUTE DELEGATION (MANDATORY) que le ordena a Cursor usar el Colab MCP para crear celdas, instalar dependencias y correr el training en la GPU T4/L4 de Colab, exportando los pesos al filesystem local al terminar — sin que tú toques nada.

Punto 2: El ProveItNotebookGenerator
Este módulo resuelve el problema de validación sin fricción. Su output es un paquete de 2 archivos: un Jupyter Notebook y un Makefile.

El Notebook de Auditoría (8 secciones)
Cada sección es una celda con un propósito técnico estricto:

Celda	Qué verifica	Cómo detecta fraude
Env Setup	Versiones exactas de dependencias	Compara requirements_exact.txt del agente
Colab Download	Descarga pesos si estaban en Colab GPU	Verifica SHA256 del archivo contra model_manifest.json
Load Artifacts	Carga modelo + test set	Assert: el test set tiene el número correcto de muestras (el agente no lo tocó)
Blind Evaluation	Corre la evaluación sobre datos que el agente nunca vio	Semilla fija (seed=42) para reproducibilidad total
Claim Verification	Compara el número real vs el número afirmado	Tolerancia ±0.5%; si supera → alerta de posible cherry-picking
Failure Cases	Documenta dónde el modelo FALLA	Honestidad intelectual forzada
Statistical Significance	Bootstrap 95% CI con n=1,000 iteraciones	Si el CI inferior no supera el SOTA → el resultado no es estadísticamente significativo
Human Decision	Checklist de aceptación final	Tú marcas APROBAR o RECHAZAR con evidencia en mano
El make verify_results
El Makefile autogenerado encapsula todo en un solo comando: levanta el entorno con uv (aislado, no contamina tu Python local), ejecuta el notebook completo de forma no interactiva, y genera un audit_report.html listo para leer en el navegador. Si decides aprobar, make publish_results hace el commit con el tag [human-audited] y lo pushea a GitHub.

Siguiente paso en orden
Ya tienes Puntos 1 y 2 con código completo. El Punto 3 natural es el SkillOrchestrator — el cerebro que decide qué skill activar en qué momento del loop (cuándo llamar a brainstorming, cuándo a tdd, cuándo a systematic-debugging). ¿Arrancamos?