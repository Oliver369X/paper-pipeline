---
mission_version: 2
mode: standard
autonomy: null
topic: Differential Transformer (arXiv:2410.02159) replication and analysis
paper_target: arXiv:2410.02159
sections_needed:
- sota
- methodology
- gaps
- experiments
- related_code
- limitations
max_perplexity_calls: 10
code_needed: true
notion_page_id: null
model: best
language: es-ES
output_dir: D:\oliver\Actividades\mcp_perplesity\paper-pipeline\data\missions\4bf382ec72e9\outputs
enable_notion: false
enable_quality_check: true
enable_cursor_cli: true
cursor_cli_prompt_path: null
cursor_cli_cwd: null
single_thread_perplexity: false
save_perplexity_to_library: true
hypotheses: []
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
enable_degradation_monitor: false
enable_skill_orchestrator: false
enable_hypervisor_triage: true
parallel_allowed_command_prefixes: null
---
