---
mission_version: 1
mode: standard
autonomy: null
topic: Mitigating Memorization in Language Models via BalancedSubnet
paper_target: Technical Report / Machine Learning Research
sections_needed:
- methodology
- experiments
- gaps
- sota
- datasets
- related_code
- limitations
- discussion
- conclusion
max_perplexity_calls: 12
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
  max_train_steps: 100
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
notion_page_id: null
model: best
language: es-ES
output_dir: D:\oliver\Actividades\mcp_perplesity\paper-pipeline\data\missions\dc2d5f354e57\outputs
enable_notion: true
enable_quality_check: true
enable_cursor_cli: true
cursor_cli_prompt_path: null
cursor_cli_cwd: null
single_thread_perplexity: false
save_perplexity_to_library: true
hypotheses:
- id: H_SCALABILITY
  description: En modelos de mayor escala (>2B), la superposición de neuronas (polisemia)
    reduce la efectividad del aislamiento de sub-redes mediante máscaras binarias.
  priority: MEDIUM
  expected_outcome: Menor reducción relativa de memorización en Pythia-2.8B vs TinyGPT-2.
- id: H_EFFICIENCY
  description: BalancedSubnet logra una reducción del Memorization Score un 40% superior
    a métodos de regularización como Weight Decay.
  priority: HIGH
  expected_outcome: Superioridad estadística en el trade-off MemScore vs Perplexity.
- id: H_SATURATION
  description: Existe un umbral de inyección de datos (poisoning) que colapsa la capacidad
    del algoritmo para encontrar una máscara 'limpia' sin degradar el set de retención.
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
