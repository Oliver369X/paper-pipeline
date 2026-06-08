# Criterios de aceptación — misión repo-adoption-mistral

Misión: [`data/missions/repo-adoption-mistral/mission.md`](../../data/missions/repo-adoption-mistral/mission.md)

La misión se considera **COMPLETA** solo si se cumplen todos:

| # | Criterio | Verificación |
|---|----------|--------------|
| C1 | Mistral provider en CI (mock) | `pytest tests/test_mistral_client.py -q` |
| C2 | Pipeline mistral end-to-end | `paper-pipeline data/missions/repo-adoption-mistral/mission.md` exit 0 |
| C3 | Benchmark comparativo | `outputs/benchmark/comparison_report.json` con 8 métricas × 2 providers |
| C4 | 11 repo-notes | `docs/benchmarks/repo-notes/*.md` count ≥ 11 |
| C5 | Quick wins con tests | `test_research_plan_phase`, `test_source_curation`, `test_quality_two_phase`, `test_citation_index` |
| C6 | Sin regresión CI | `pytest -m "not integration" -q` |
| C7 | `.env.example` documenta Mistral | bloque `MISTRAL_*` presente |
| C8 | Honestidad producto | README/disclaimer: Mistral = narrativo sin web en vivo |

## Limitaciones documentadas

- `provider: mistral` no ejecuta búsqueda web; Perplexity sigue disponible para meta-loop y benchmark baseline.
- Métricas del benchmark son **objetivas** (longitud, validadores, conteos); no miden verdad científica.
