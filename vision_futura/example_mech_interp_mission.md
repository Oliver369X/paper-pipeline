
---
# ============================================================
# PAPER-PIPELINE 2.0 — MISSION DEFINITION FILE
# ============================================================
# Llenar cada campo. Ningún campo es opcional.
# El pipeline se negará a correr si hay campos vacíos o inválidos.
# ============================================================

# ----------------------------------------------------------
# IDENTIDAD DEL EXPERIMENTO
# ----------------------------------------------------------
mission_id: "mech-interp-sae-001"                # Generado automáticamente si se deja vacío
topic: "Entrenamiento de Sparse Autoencoders para extracción de features en GPT-2 pequeño"                          # Descripción precisa del problema a resolver
domain: "mechanistic_interpretability"                        # ej. "mechanistic_interpretability", "wildfire_detection"
venue_target: "ICLR 2027"            # ej. "NeurIPS 2026", "ICLR 2026", "arXiv"
language: "es"                            # Idioma del borrador final
paper_target: "research_paper"            # "research_paper" | "technical_report" | "demo"
output_dir: "outputs/mech-interp-sae-001/"

# ----------------------------------------------------------
# HIPÓTESIS A PROBAR (Soporte para Paralelismo Masivo)
# ----------------------------------------------------------
# Si defines más de 1 hipótesis, el ParallelWorktreeOrchestrator
# lanzará un agente aislado por cada una simultáneamente.
# Máximo recomendado: 20 hipótesis por corrida para no saturar rate limits.
# ----------------------------------------------------------
hypotheses:
  - id: "H1"
    description: "Penalización L1 dinámica con warm-up de 500 pasos reduce feature collapse vs L1 fija"
    priority: "HIGH"                      # HIGH | MEDIUM | LOW
    expected_outcome: "% features activos > 85% vs baseline 60%"      # Qué resultado predices matemáticamente

  - id: "H2"
    description: "Inicialización de columnas del decoder con PCA de activaciones reduce pasos de convergencia"
    priority: "MEDIUM"
    expected_outcome: "Convergencia en < 5000 pasos vs baseline 12000"

  # Añadir más hipótesis aquí para grid search paralelo:
  # - id: "H3"
  #   description: "..."
  #   priority: "LOW"
  #   expected_outcome: "..."

# ----------------------------------------------------------
# CONFIGURACIÓN DEL EPISTEMIC INJECTOR (Punto 1)
# ----------------------------------------------------------
epistemic_injection:
  enabled: true
  n_papers_to_fetch: 20                  # Cuántos papers SOTA buscar en Perplexity
  n_repos_to_fetch: 5                    # Cuántos repos de referencia en GitHub
  dca_output_path: "outputs/mech-interp-sae-001/domain_context.yaml"

  # Poison Pills — Afirmaciones FALSAS para detectar reward hacking.
  # El fact-checker NUNCA debe validarlas como verdaderas.
  # Deja vacío para que el pipeline las genere automáticamente.
  poison_pills:
    - false_claim: ""
      detection_query: ""
    # Si se deja vacío, el EpistemicInjector genera 3 poison pills automáticas
    # basadas en errores comunes del dominio.

# ----------------------------------------------------------
# CONFIGURACIÓN COMPUTACIONAL Y COLAB MCP
# ----------------------------------------------------------
compute:
  local_gpu_available: false             # ¿Tienes GPU local?
  local_gpu_memory_gb: 0                 # Si tienes, cuántos GB
  colab_mcp_enabled: true                # Ya integrado en Cursor — usar para GPU remota
  colab_accelerator: "T4"               # "T4" | "L4" | "A100" | "auto"
  # Regla automática: si el experimento necesita > local_gpu_memory_gb → Colab
  delegate_threshold_gb: 8.0            # Delegar a Colab si necesita > N GB VRAM

# ----------------------------------------------------------
# CONTROL DE CALIDAD Y TRIAJE (Punto 3 — Hipervisor)
# ----------------------------------------------------------
quality_gates:
  # La métrica principal que decide el Tier del experimento
  target_metric: "fraction_active_features"       # ej. "accuracy", "f1_score", "loss", "auprc"
  higher_is_better: true                 # false para métricas de error (loss, FPR)
  sota_baseline_value: 0.6   # El número a superar
  breakthrough_margin: 0.1  # ej. 0.02 = superar SOTA por 2%
  replication_tolerance: 0.01  # ej. 0.01 = ±1% es "replicación"

  # Test de significancia estadística
  require_statistical_significance: true
  bootstrap_n: 1000                      # Iteraciones de bootstrap para CI
  significance_level: 0.05              # α = 5%

  # Verificación matemática formal (Punto del documento anterior)
  math_verification:
    sympy_checks: true                   # Verificar fórmulas algebraicas con SymPy
    unit_test_coverage_min: 80           # % mínimo de cobertura de tests
    property_based_tests: true           # Usar Hypothesis para testing de propiedades

# ----------------------------------------------------------
# CONFIGURACIÓN DEL DEBUGGING LOOP (Punto 5)
# ----------------------------------------------------------
debugging:
  cursor_max_attempts: 3                 # Intentos de Cursor antes de escalar
  perplexity_max_attempts: 2             # Intentos de Perplexity antes de HUMAN_REVIEW
  generate_human_briefing: true          # Generar doc estructurado si se escala a humano
  math_error_patterns:                   # Patrones adicionales de error para el clasificador
    - "your_custom_error_pattern_here"

# ----------------------------------------------------------
# CONFIGURACIÓN DEL SKILL ORCHESTRATOR (Punto 3)
# ----------------------------------------------------------
skill_orchestrator:
  # Fases habilitadas (deshabilitar si no se necesitan)
  phases:
    domain_acquisition: true
    hypothesis_design: true
    implementation_plan: true
    code_generation: true
    debugging: true
    evaluation: true
    web_packaging: true    # true para publicar resultado
    documentation: true
    human_review: true                       # NUNCA deshabilitar

  # Skills adicionales específicas del proyecto (además del mapa base)
  extra_skills_per_phase:
    code_generation:
      - "hugging-face-model-trainer"        # Si el proyecto incluye fine-tuning
    web_packaging:
      - "gradio"                            # Para demo interactiva del modelo

# ----------------------------------------------------------
# CONFIGURACIÓN DE PERPLEXITY (Sesión Web)
# ----------------------------------------------------------
perplexity:
  max_calls: 15          # Límite duro de llamadas (1-64)
  save_to_library: true                      # Guardar respuestas para reusar
  academic_focus: true                       # Priorizar fuentes académicas
  # Directivas especiales para cada sección del paper
  section_directives:
    introduction: "Enfatizar impacto social en Latinoamérica si aplica"
    related_work: "Comparar con los 5 papers más relevantes del DCA"
    methodology: "Describir cada ecuación matemática antes de implementarla"
    experiments: "Incluir análisis de ablación para cada componente"
    conclusion: "Identificar limitaciones honestas, no solo logros"

# ----------------------------------------------------------
# CONFIGURACIÓN DE NOTION (Sistema Nervioso Central)
# ----------------------------------------------------------
notion:
  enabled: true
  database_id: "YOUR_NOTION_DB_ID_HERE"       # ID de tu base de experimentos
  auto_sync_on_completion: true             # Insertar fila al terminar cada exp
  notify_on_breakthrough: true             # Ping al encontrar un Nivel 3

# ----------------------------------------------------------
# CONFIGURACIÓN DE GITHUB
# ----------------------------------------------------------
github:
  auto_commit_each_phase: true             # Commit al finalizar cada fase
  create_pr_on_breakthrough: true          # PR automático para resultados Nivel 3
  branch_prefix: "exp/mech-interp-sae-001"

# ----------------------------------------------------------
# LÍMITES DE SEGURIDAD (Anti-runaway)
# ----------------------------------------------------------
safety:
  max_total_runtime_minutes: 120           # El pipeline para si supera 2 horas
  max_cost_usd: 5.0                        # Estimación de costo — alerta si supera
  require_human_approval_before_publish: true  # SIEMPRE pedir aprobación antes de publicar
  allow_force_push: false                  # NUNCA force push sin respaldo
  backup_before_run: true                  # Git stash automático al iniciar
---

# ============================================================
# DESCRIPCIÓN NARRATIVA DE LA MISIÓN
# ============================================================
# Escribe aquí en lenguaje natural qué quieres lograr.
# El Epistemic Injector usa este texto para enfocar la búsqueda en Perplexity.
# Sé específico: menciona el dataset, la arquitectura base, el venue objetivo.
# ============================================================

## Objetivo Principal
Investigar técnicas para evitar el colapso de features en SAEs entrenados sobre GPT-2 small. El problema de 'dead dictionary features' fue documentado por Anthropic en 2023 y sigue siendo un obstáculo para interpretabilidad mecanicista confiable.

## Contexto y Motivación
Los SAEs son fundamentales para extraer conceptos interpretables de LLMs. El feature collapse hace que un porcentaje alto del diccionario quede sin uso, reduciendo la capacidad de encontrar circuitos causales en los modelos.

## Criterios de Éxito
1. Más del 85% de features activos al finalizar training
2. Reconstrucción L2 < 0.05 en el validation set
3. Al menos 1 feature interpretable identificado manualmente
4. Reproducible con seed 42 en entorno limpio (Docker)

## Limitaciones Conocidas (Honestidad Intelectual)
1. Experimentos solo en GPT-2 small (117M params) — escalado a modelos mayores no garantizado
2. El concepto de 'feature interpretable' es subjetivo — usamos proxy de monosemanticity score
3. El Colab T4 puede no tener suficiente VRAM para batch size grande — usar gradient accumulation
