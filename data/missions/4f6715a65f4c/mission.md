---
mission_version: 1
mode: standard
autonomy: null
topic: Replicación de 'From Memorization to Reasoning in the Spectrum of Loss Curvature'
  (arXiv:2510.24256)
paper_target: arXiv:2510.24256
sections_needed:
- methodology
- experiments
- gaps
- related_code
- discussion
- limitations
- conclusion
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
  max_train_steps: 5
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
output_dir: D:\oliver\Actividades\mcp_perplesity\paper-pipeline\data\missions\4f6715a65f4c\outputs
enable_notion: false
enable_quality_check: true
enable_cursor_cli: true
cursor_cli_optional: true
cursor_cli_prompt_path: null
cursor_cli_cwd: null
single_thread_perplexity: true
save_perplexity_to_library: true
replication_phase: A
replication_phase_a_scope: ''
replication_phase_b_scope: ''
replication_fidelity: strict_paper
hypotheses:
- id: H1
  description: La edición de componentes de peso con alta curvatura reduce la recitación
    de datos memorizados con menor impacto en la perplexity general que los métodos
    de unlearning tradicionales.
  priority: HIGH
  expected_outcome: Reducción significativa en recitation scores manteniendo benchmarks
    de razonamiento estables.
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
