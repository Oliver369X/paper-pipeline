---
topic: "Patrones de auto-research: adopción en paper-pipeline"
paper_target: "internal benchmark — no venue"
provider: mistral
model: mistral-large-latest
sections_needed:
  - related_work
  - sota
  - gaps
  - methodology
  - experiments
  - peer_review
max_perplexity_calls: 12
code_needed: false
notion_page_id: null
language: en-US
output_dir: outputs
enable_notion: false
enable_quality_check: true
enable_cursor_cli: false
enable_experiment_runner: false
save_perplexity_to_library: true
single_thread_perplexity: false
replication_fidelity: extension_exploratory
research_agent:
  enabled: false
  max_concurrent: 2
---

# Misión repo-adoption + Mistral

## Objetivo

Validar adopción de patrones desde repos de auto-research (ver `research-repos/` y `docs/benchmarks/repo-notes/`) usando **Mistral** como proveedor de secciones.

## Criterios de aceptación

Ver [docs/benchmarks/REPO_ADOPTION_CRITERIA.md](../../docs/benchmarks/REPO_ADOPTION_CRITERIA.md).

## Secciones

| Sección | Patrón de referencia |
|---------|---------------------|
| related_work | gpt-researcher, storm |
| sota | paper-qa, OpenScholar |
| gaps | DeepScientist findings memory |
| methodology | open_deep_research supervisor |
| experiments | autoresearch / AIDE |
| peer_review | ChatReviewer 2-fases (quality phase) |

## Notas

- Perplexity se usa solo en meta-loop (`paper-meta-loop`), no en este run de secciones.
- Ejecutar benchmark: `python scripts/benchmark_provider_comparison.py --mission data/missions/repo-adoption-mistral/mission.md`
