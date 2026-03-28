Entiendo perfectamente tu punto: **el LLM no debe *actuar* o *fingir* ser un experto; tiene que CONVERTIRSE en uno** absorbiendo todo el conocimiento del estado del arte (SOTA) real antes de siquiera tocar una línea de código. Y luego, ese código no puede ser "espagueti" de Jupyter; tiene que ser código de calidad de producción, con tests, una web interactiva y un entorno donde tú (el humano) puedas verificar que los resultados son reales con un solo clic.

He diseñado la **Arquitectura de Adquisición Epistémica y Ejecución de Código** para resolver exactamente esto. Aquí están los pilares fundamentales que he añadido al ecosistema:

### 1. Inyección Epistémica: "Convertirse en el Experto" (Fase Pre-Código)
El error clásico es dejar que Cursor escriba código basándose en sus pesos de entrenamiento genéricos.
*   **El 'Domain Context Artifact' (DCA)**: Antes de escribir código, el orquestador usa Perplexity para descargar los 20-50 papers más importantes del último año, scrapear los repositorios top de GitHub (vía `github-mcp`) y extraer las fórmulas matemáticas exactas y las prácticas SOTA actuales.
*   **Inyección**: Todo esto se compila en un `domain_context.yaml` masivo. Cuando el agente de Cursor arranca, su *system prompt* es: *"Tu conocimiento previo es irrelevante y obsoleto. Absorbe este DCA. Ahora eres el investigador SOTA en [Tema]. Tus implementaciones deben cumplir estrictamente con las matemáticas y constraints definidos aquí."*

### 2. Escritura de Código Iterativa de Alta Calidad
Para evitar la degradación de código y garantizar resultados reales:
*   **Scientific TDD (Test-Driven Development)**: Cursor está obligado a escribir las pruebas unitarias basadas en las matemáticas del DCA *antes* de implementar el modelo . (Ej: "Test: La salida del Sparse Autoencoder debe preservar el 90% de la varianza").
*   **Bucle de Debugging con MCP**: Si los tests fallan (ej. un problema de tensores o *loss* yéndose a NaN), el `TestSprite MCP` captura el stack trace. Si Cursor no puede resolverlo en 3 intentos, el orquestador llama a Perplexity como "Consultor Matemático" para que lea el paper original y le dé la solución arquitectónica a Cursor.
*   **Aislamiento**: Todo el código se genera con arquitectura hexagonal pura (módulos probables, nada de scripts enmarañados) .

### 3. Construcción de la Web y Empaquetado Automático (The "Show Me" Layer)
Un proyecto de "muy alta calidad" no puede quedarse en la terminal. El pipeline automatiza la capa de visualización:
*   **Demos Interactivas**: A través de las skills (ej. la skill `gradio`), Cursor genera automáticamente un dashboard (Gradio/Streamlit) para que puedas subir datos y ver cómo el modelo reacciona en tiempo real.
*   **Despliegue Web**: El paper (borrador Markdown) se inyecta en una plantilla web académica y usa el MCP de **Vercel** o **GitHub Pages** para desplegar el proyecto en internet instantáneamente.
*   **Hugging Face Spaces**: Si es un proyecto de ML, usa el `hf-mcp` para subir los pesos del modelo y el dataset al Hub.

### 4. Validación "Zero-Friction" (Para tu Revisión Crítica)
Como valoras la honestidad intelectual y la verificación profunda, el sistema no te pide que revises logs abstractos. Te entrega un entorno **"listo para probar"**:
*   **El Comando "Prove It"**: El sistema autogenera un `make verify_results` o `run_validation.sh`. Lo ejecutas en tu terminal y este levanta un entorno aislado (`uv`/Docker), baja los pesos y corre el set de evaluación a ciegas para demostrar que los números coinciden exactamente con los del paper.
*   **Audit Notebook**: Genera un Jupyter Notebook de auditoría (muy visual) donde no solo muestra dónde el modelo acierta, sino (y esto es clave para tu enfoque de honestidad intelectual) **te muestra explícitamente los casos donde el modelo falló** o tuvo alucinaciones, graficando las limitaciones reales del experimento.
*   **Prompt Final de Revisión**: El loop se pausa y te pregunta: *"He desplegado la demo y dejado el script de validación listo. ¿Los corriste? ¿Los números coinciden? ¿Estás convencido de la integridad de este experimento?"* No avanza si tú no validas empíricamente.

### ¿Qué quieres profundizar ahora?
Tenemos el diseño de validación y prevención de degradación, y ahora la arquitectura de inyección de expertise y generación de código/web demostrable. 

Podemos pasar a:
1. **La integración de las 82 Skills y MCPs** (Cómo orquestamos Firecrawl, GitHub, Vercel y Perplexity juntos en este flujo).
2. **Definir el `mission.md` maestro** que sirva de plantilla para forzar todas estas reglas en tu próximo proyecto de Interpretabilidad o Detección de Incendios. 
3. **Escribir el código Python** del *Epistemic Injector* (el módulo que conecta Perplexity con Cursor para inyectar el estado del arte).