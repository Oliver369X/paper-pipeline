---
mission_version: 1
mode: standard
autonomy: null
topic: Análisis de la curvatura de pérdida en la transición memorización-razonamiento
paper_target: arXiv:2510.24256
sections_needed:
- abstract
- methodology
- experiments
- related_code
- gaps
- sota
max_perplexity_calls: 10
code_needed: true
enable_experiment_runner: true
experiment_runner:
  profile: hf_llm_micro
  prefer_generated_script: true
  entrypoint: outputs/code/run_experiment.py
  hf_model_id: sshleifer/tiny-gpt2
  hf_dataset_id: wikitext
  hf_dataset_config: wikitext-2-raw-v1
  hf_text_field: text
  max_train_steps: 20
  max_samples: 2000
  seed: 42
  subprocess_timeout_sec: 7200
  write_colab_notebook: true
  hf_dataset_url: null
  hf_model_url: null
  code_repo_url: null
  code_repo_branch: null
  code_repo_clone_depth: 1
  clone_timeout_sec: 600
  prefer_urls_from_draft: false
  block_pipeline_on_failure: true
  fallback_minimal_on_hf_import_error: true
  iteration_after_cursor: false
  iteration_max_rounds: 3
  iteration_perplexity_on_fail: false
  deterministic_metrics_bounds: null
notion_page_id: null
model: best
language: es-ES
output_dir: D:\oliver\Actividades\mcp_perplesity\paper-pipeline\data\missions\cda2ed5f7114\outputs
enable_notion: false
enable_quality_check: true
enable_cursor_cli: true
cursor_cli_optional: true
cursor_cli_prompt_path: null
cursor_cli_cwd: null
single_thread_perplexity: false
save_perplexity_to_library: true
replication_phase: AB
replication_phase_a_scope: ''
replication_phase_b_scope: ''
replication_fidelity: extension_exploratory
hypotheses:
- id: H1
  description: Las secuencias con alta entropía de información pero patrones repetitivos
    muestran una curvatura significativamente mayor que secuencias lógicas de menor
    entropía.
  priority: HIGH
  expected_outcome: Confirmación de la jerarquía de curvatura propuesta por Merullo.
- id: H2
  description: La aplicación de regularización espectral dirigida a las direcciones
    de mayor autovalor del Hessiano mejora el rendimiento en tareas de razonamiento
    out-of-distribution.
  priority: MEDIUM
  expected_outcome: ''
epistemic_injection:
  enabled: false
  n_papers_to_fetch: 20
  n_repos_to_fetch: 5
  poison_pills: []
compute:
  local_gpu_available: false
  local_gpu_memory_gb: 0.0
  colab_mcp_enabled: false
  delegate_threshold_gb: 12.0
quality_gates:
  target_metric: ''
  higher_is_better: true
  sota_baseline_value: 0.0
  breakthrough_margin: 0.02
  replication_tolerance: 0.01
  require_statistical_significance: true
  epistemic_alignment_mode: 'off'
  downstream_metrics_mode: 'off'
debugging:
  cursor_max_attempts: 3
  perplexity_max_attempts: 2
  generate_human_briefing: true
safety:
  max_total_runtime_minutes: 120
  max_cost_usd: 5.0
  require_human_approval_before_publish: true
  allow_force_push: false
enable_epistemic_injection: true
enable_degradation_monitor: true
enable_skill_orchestrator: true
enable_hypervisor_triage: true
parallel_allowed_command_prefixes: null
---
