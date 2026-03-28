Punto 3: SkillOrchestrator
El problema de fondo
Si Cursor tiene acceso a tus 82+ skills todo el tiempo, el contexto se satura, el agente se distrae y la calidad cae. Peor aún: un agente en modo debugging que tiene activada la skill brainstorming tenderá a cambiar de hipótesis en vez de encontrar el bug real. Son modos cognitivos incompatibles.

La solución: Mínimo Privilegio por Fase
El módulo define 9 fases del pipeline, cada una con exactamente las skills y MCPs que necesita — ni una más:

Fase	Skills Activas	MCPs Activos	Bloqueadas
DOMAIN_ACQUISITION	technical-research, hf-mcp	perplexity-web, firecrawl, github	Todo lo de TDD y debugging
CODE_GENERATION	test-driven-development, executing-plans	github, TestSprite	brainstorming, debugging
DEBUGGING	systematic-debugging, verification-before-completion	perplexity-web, TestSprite	Todo lo demás
WEB_PACKAGING	nextjs, vercel-cli, shadcn, gradio	plugin-vercel, playwright	Bloqueado si no pasó EVALUATION primero
HUMAN_REVIEW	Ninguna	Ninguna	Todo — tú tienes el control
Reglas especiales críticas
Si el debugging falla 3 veces seguidas: el orquestador emite la señal __ESCALATE_TO_PERPLEXITY__. El runner principal la interpreta, arma el stack trace y llama a Perplexity como "Consultor Matemático" en vez de seguir intentando a ciegas.

Si el experimento necesita Colab: añade automáticamente agent-browser y agent-browser-verify para que Cursor pueda operar sobre la pestaña de Colab via MCP.

No se puede publicar (WEB_PACKAGING) sin haber pasado por EVALUATION: regla de bloqueo explícita. Elimina la posibilidad de publicar resultados no verificados.

Punto 4: ParallelWorktreeOrchestrator
El problema de fondo
Dos agentes de Cursor trabajando en el mismo directorio crean fatal: Unable to create .git/index.lock y sobreescriben metrics.json y draft_paper.md el uno al otro. Con 50 agentes paralelos, el repo queda corrupto en segundos.

Solución 1: Git Worktrees (aislamiento físico)
El GitWorktreeManager crea una carpeta física separada (wt_EXP-001/, wt_EXP-002/, ...) por cada agente, vinculada al mismo repo pero en su propia rama. Cuando el agente termina, el manager destruye la carpeta. Si es un Breakthrough (Tier 3), la rama se preserva en Git para auditoría posterior.

Solución 2: Cola de Commits (un solo hilo serializado)
El _commit_worker_loop es un worker asíncrono de un solo hilo. Todos los agentes paralelos envían sus peticiones de git commit a una asyncio.Queue, y el worker las procesa una a la vez. Esto hace físicamente imposible el index.lock, incluso con 50 agentes activos.

Solución 3: Backoff Exponencial con Jitter
El APIRateLimiter maneja los errores HTTP 429 con una secuencia matemática que previene el thundering herd:

Con initial_backoff=2s y jitter=0.3, los tiempos de espera son: ~2s → ~4s → ~8s → ~16s → ~32s (con ±30% aleatorio)

El jitter_factor hace que 50 agentes que reciben un 429 al mismo tiempo no reintenten todos exactamente en el mismo instante, distribuyendo la carga en el tiempo.

Resumen del flujo de un experimento paralelo
text
run_batch([exp1, exp2, ..., exp50])
    │
    ├─ asyncio.Semaphore(5) → máx 5 corriendo al mismo tiempo
    │
    ├─ Para cada experimento:
    │   ├─ create_worktree() → carpeta física aislada
    │   ├─ inject_mission() → escribe mission.md específico
    │   ├─ execute_with_retry() → cursor agent + backoff en 429
    │   ├─ commit_async() → encola en worker serializado
    │   └─ remove_worktree() → limpia disco (salvo Tier 3)
    │
    └─ gather() → espera todos → retorna lista de resultados
Siguientes puntos en el orden que establecimos
Quedan por desarrollar:

Punto 5: El Bucle de Debugging Matemático Asistido (el fallback hacia Perplexity cuando Cursor falla 3 veces)

Punto 6: La plantilla definitiva de mission.md con soporte para arrays de hipótesis y poison pills embebidas