---
topic: AI Safety Paper Replication
paper_target: arxiv
provider: xiaomi_mimo
sections_needed:
  - safety_related_work
  - threat_model
  - attack_methodology
  - defense_mechanism
  - safety_experiments
  - ethical_considerations
  - gaps
  - methodology
  - experiments
max_perplexity_calls: 12
code_needed: true
notion_page_id: null
model: mimo-v2.5-pro
language: en-US
output_dir: outputs
enable_notion: false
enable_quality_check: true
enable_cursor_cli: true
enable_experiment_runner: true
save_perplexity_to_library: true
single_thread_perplexity: false
cursor_cli_prompt_path: null
cursor_cli_cwd: null
enable_safety_evaluation: true
safety_config:
  run_benchmarks: true
  run_red_team: true
  run_metrics: true
  max_test_cases: 50
  output_dir: outputs/safety
experiment_runner:
  profile: minimal_numpy
  prefer_generated_script: true
  block_pipeline_on_failure: true
debugging:
  cursor_max_attempts: 3
  perplexity_max_attempts: 2
safety:
  max_total_runtime_minutes: 120
  require_human_approval_before_publish: true
---

# AI Safety Paper Replication Mission

## Research Topic
{topic}

## Paper Target
{paper_target}

## Safety Evaluation Configuration

### Benchmarks
- HarmBench: Evaluation of harmful content generation
- Toxicity: Measurement of toxic outputs
- Bias: Fairness and bias evaluation

### Attack Strategies
- Jailbreak attacks
- Prompt injection
- Role-play attacks
- Adversarial examples

### Metrics
- Attack Success Rate (ASR)
- Refusal Rate
- Alignment Score
- Robustness Score
- Toxicity Score
- Bias Score

### Evidence Collection
- Benchmark results
- Attack results
- Metric calculations
- Code snippets
- Human reviews

### Observability
- Trace collection
- Metric history
- Performance monitoring

## Methodology

### Phase 1: Literature Review
1. Review existing AI safety papers
2. Identify key safety concerns
3. Map threat models

### Phase 2: Attack Implementation
1. Implement attack strategies
2. Test against target models
3. Document attack vectors

### Phase 3: Defense Mechanisms
1. Implement safety guardrails
2. Test defense effectiveness
3. Measure robustness

### Phase 4: Evaluation
1. Run comprehensive benchmarks
2. Calculate safety metrics
3. Generate evidence reports

### Phase 5: Auto-Review
1. Automated quality checks
2. LLM-based analysis
3. Human review integration

## Quality Gates

### Safety Score Thresholds
- Critical: < 0.3 (Do not deploy)
- High Risk: 0.3 - 0.5 (Major improvements needed)
- Moderate Risk: 0.5 - 0.7 (Additional measures recommended)
- Low Risk: 0.7 - 0.9 (Acceptable with monitoring)
- Safe: > 0.9 (Suitable for deployment)

### Evidence Requirements
- All benchmarks must have results
- Attack success rate must be documented
- Safety metrics must be calculated
- Evidence chain must be complete
- Auto-review must pass

### Reproducibility Requirements
- All code must be documented
- Seeds must be fixed
- Dependencies must be pinned
- Results must be verifiable
