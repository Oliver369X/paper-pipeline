# ==============================================================================
# PUNTO 6: Plantilla Definitiva de mission.md
# Ubicación: paper_pipeline/templates/mission_template.yaml
#
# PROPÓSITO:
#   El mission.md es la semilla de todo el pipeline. Si está mal diseñado,
#   todos los agentes producen resultados imprecisos o incoherentes.
#   Esta plantilla soporta:
#     - Arrays de hipótesis para paralelismo masivo (Punto 4)
#     - Poison pills embebidas para detección de reward hacking (Punto 1)
#     - Quality guards explícitos para el Hipervisor de Triaje (Punto 3)
#     - Directivas de Colab MCP para delegación computacional (Punto 1 & 2)
#     - Control fino de cada fase del SkillOrchestrator (Punto 3)
# ==============================================================================

MISSION_TEMPLATE = """
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
mission_id: "{mission_id}"                # Generado automáticamente si se deja vacío
topic: "{topic}"                          # Descripción precisa del problema a resolver
domain: "{domain}"                        # ej. "mechanistic_interpretability", "wildfire_detection"
venue_target: "{venue_target}"            # ej. "NeurIPS 2026", "ICLR 2026", "arXiv"
language: "es"                            # Idioma del borrador final
paper_target: "{paper_target}"            # "research_paper" | "technical_report" | "demo"
output_dir: "outputs/{mission_id}/"

# ----------------------------------------------------------
# HIPÓTESIS A PROBAR (Soporte para Paralelismo Masivo)
# ----------------------------------------------------------
# Si defines más de 1 hipótesis, el ParallelWorktreeOrchestrator
# lanzará un agente aislado por cada una simultáneamente.
# Máximo recomendado: 20 hipótesis por corrida para no saturar rate limits.
# ----------------------------------------------------------
hypotheses:
  - id: "H1"
    description: "{hypothesis_1}"
    priority: "HIGH"                      # HIGH | MEDIUM | LOW
    expected_outcome: "{expected_1}"      # Qué resultado predices matemáticamente

  - id: "H2"
    description: "{hypothesis_2}"
    priority: "MEDIUM"
    expected_outcome: "{expected_2}"

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
  dca_output_path: "outputs/{mission_id}/domain_context.yaml"

  # Poison Pills — Afirmaciones FALSAS para detectar reward hacking.
  # El fact-checker NUNCA debe validarlas como verdaderas.
  # Deja vacío para que el pipeline las genere automáticamente.
  poison_pills:
    - false_claim: "{custom_poison_pill_1}"
      detection_query: "{detection_query_1}"
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
  target_metric: "{target_metric}"       # ej. "accuracy", "f1_score", "loss", "auprc"
  higher_is_better: true                 # false para métricas de error (loss, FPR)
  sota_baseline_value: {sota_baseline}   # El número a superar
  breakthrough_margin: {breakthrough_margin}  # ej. 0.02 = superar SOTA por 2%
  replication_tolerance: {replication_tolerance}  # ej. 0.01 = ±1% es "replicación"

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
    web_packaging: {enable_web_packaging}    # true para publicar resultado
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
  max_calls: {max_perplexity_calls}          # Límite duro de llamadas (1-64)
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
  database_id: "{notion_database_id}"       # ID de tu base de experimentos
  auto_sync_on_completion: true             # Insertar fila al terminar cada exp
  notify_on_breakthrough: true             # Ping al encontrar un Nivel 3

# ----------------------------------------------------------
# CONFIGURACIÓN DE GITHUB
# ----------------------------------------------------------
github:
  auto_commit_each_phase: true             # Commit al finalizar cada fase
  create_pr_on_breakthrough: true          # PR automático para resultados Nivel 3
  branch_prefix: "exp/{mission_id}"

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
{mission_narrative}

## Contexto y Motivación
{mission_context}

## Criterios de Éxito
{success_criteria}

## Limitaciones Conocidas (Honestidad Intelectual)
{known_limitations}
"""

# ------------------------------------------------------------------------------
# Instanciador: Genera un mission.md concreto desde la plantilla
# ------------------------------------------------------------------------------

def create_mission_file(
    mission_id: str,
    topic: str,
    domain: str,
    venue_target: str,
    hypotheses: list[dict],
    target_metric: str,
    sota_baseline: float,
    paper_target: str = "research_paper",
    notion_database_id: str = "YOUR_NOTION_DB_ID",
    max_perplexity_calls: int = 10,
    enable_web_packaging: str = "true",
    breakthrough_margin: float = 0.02,
    replication_tolerance: float = 0.01,
    mission_narrative: str = "Describe tu misión aquí.",
    mission_context: str = "Contexto del problema.",
    success_criteria: str = "Lista de criterios medibles.",
    known_limitations: str = "Limitaciones conocidas del enfoque.",
) -> str:
    """
    Genera el contenido de un mission.md completo y válido.
    Listo para guardarse y pasarse al pipeline.
    """
    hypotheses_yaml = ""
    for i, h in enumerate(hypotheses):
        hypotheses_yaml += f"""  - id: "H{i+1}"
    description: "{h['description']}"
    priority: "{h.get('priority', 'MEDIUM')}"
    expected_outcome: "{h.get('expected_outcome', 'TBD')}"
"""

    return MISSION_TEMPLATE.format(
        mission_id=mission_id,
        topic=topic,
        domain=domain,
        venue_target=venue_target,
        paper_target=paper_target,
        hypothesis_1=hypotheses[0]["description"] if hypotheses else "TBD",
        hypothesis_2=hypotheses[1]["description"] if len(hypotheses) > 1 else "TBD",
        expected_1=hypotheses[0].get("expected_outcome", "TBD") if hypotheses else "TBD",
        expected_2=hypotheses[1].get("expected_outcome", "TBD") if len(hypotheses) > 1 else "TBD",
        target_metric=target_metric,
        sota_baseline=sota_baseline,
        breakthrough_margin=breakthrough_margin,
        replication_tolerance=replication_tolerance,
        notion_database_id=notion_database_id,
        max_perplexity_calls=max_perplexity_calls,
        enable_web_packaging=enable_web_packaging,
        custom_poison_pill_1="",
        detection_query_1="",
        mission_narrative=mission_narrative,
        mission_context=mission_context,
        success_criteria=success_criteria,
        known_limitations=known_limitations,
    )


# ------------------------------------------------------------------------------
# Ejemplo concreto: Mission para un experimento de Interpretabilidad Mecanicista
# (El dominio real de Diego)
# ------------------------------------------------------------------------------

EXAMPLE_MECHANISTIC_INTERP_MISSION = create_mission_file(
    mission_id="mech-interp-sae-001",
    topic="Entrenamiento de Sparse Autoencoders para extracción de features en GPT-2 pequeño",
    domain="mechanistic_interpretability",
    venue_target="ICLR 2027",
    hypotheses=[
        {
            "description": "Penalización L1 dinámica con warm-up de 500 pasos reduce feature collapse vs L1 fija",
            "priority": "HIGH",
            "expected_outcome": "% features activos > 85% vs baseline 60%"
        },
        {
            "description": "Inicialización de columnas del decoder con PCA de activaciones reduce pasos de convergencia",
            "priority": "HIGH",
            "expected_outcome": "Convergencia en < 5000 pasos vs baseline 12000"
        },
        {
            "description": "Auxiliary loss basada en dead features fuerza reactivación sin degradar reconstrucción",
            "priority": "MEDIUM",
            "expected_outcome": "0 features muertos al final del training, L2 reconstruction < 0.05"
        },
    ],
    target_metric="fraction_active_features",
    sota_baseline=0.60,
    breakthrough_margin=0.10,
    paper_target="research_paper",
    notion_database_id="YOUR_NOTION_DB_ID_HERE",
    max_perplexity_calls=15,
    mission_narrative=(
        "Investigar técnicas para evitar el colapso de features en SAEs entrenados sobre "
        "GPT-2 small. El problema de 'dead dictionary features' fue documentado por Anthropic "
        "en 2023 y sigue siendo un obstáculo para interpretabilidad mecanicista confiable."
    ),
    mission_context=(
        "Los SAEs son fundamentales para extraer conceptos interpretables de LLMs. "
        "El feature collapse hace que un porcentaje alto del diccionario quede sin uso, "
        "reduciendo la capacidad de encontrar circuitos causales en los modelos."
    ),
    success_criteria=(
        "1. Más del 85% de features activos al finalizar training\n"
        "2. Reconstrucción L2 < 0.05 en el validation set\n"
        "3. Al menos 1 feature interpretable identificado manualmente\n"
        "4. Reproducible con seed 42 en entorno limpio (Docker)"
    ),
    known_limitations=(
        "1. Experimentos solo en GPT-2 small (117M params) — escalado a modelos mayores no garantizado\n"
        "2. El concepto de 'feature interpretable' es subjetivo — usamos proxy de monosemanticity score\n"
        "3. El Colab T4 puede no tener suficiente VRAM para batch size grande — usar gradient accumulation"
    ),
)
