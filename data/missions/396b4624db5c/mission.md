---
mission_version: 1
mode: standard
autonomy: null
topic: Research topic
paper_target: generic venue
sections_needed:
- sota
- gaps
- methodology
- datasets
- experiments
- discussion
- writing_hook
- conclusion
max_perplexity_calls: 8
code_needed: true
notion_page_id: 32f14f96-4093-8079-ba63-e43bcbf2097c
model: best
language: es-ES
output_dir: D:\oliver\Actividades\mcp_perplesity\paper-pipeline\data\missions\396b4624db5c\outputs
enable_notion: true
enable_quality_check: true
enable_cursor_cli: true
cursor_cli_prompt_path: null
cursor_cli_cwd: null
single_thread_perplexity: true
save_perplexity_to_library: true
hypotheses:
- id: h-1774558451905
  description: se puede puede mapear matermaticmateo e infore a ressultados lineares
    las respeusat de un llm espesificamen te de nano gpt y con esto poder evitat  la
    desalineacion
  priority: MEDIUM
  expected_outcome: '5'
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
  breakthrough_margin: 0.1
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
