# Paquete preprint — figuras y snapshot reproducible

Carpeta **para el manuscrito** (LaTeX/Word): figuras listas a 300 dpi donde aplica, más un **snapshot** de artefactos técnicos. Regenerar antes de enviar si cambió el código relevante.

## Figuras (`figures/`)

| Archivo | Contenido |
|---------|-----------|
| `fig_architecture_overview.png` | Mermaid → PNG: CLI/Web → `runner` → integraciones (ver `docs/assets/architecture_overview.mmd`) |
| `fig_architecture_governance.png` | Mermaid → PNG: auditoría, señales de publicación, bloque CI (`docs/assets/architecture_governance.mmd`) |
| `fig_case_study_replication_flow.png` | Mermaid → PNG: misión → artefactos → `case_study_trace.json` / appendix (`docs/assets/case_study_replication_flow.mmd`) |
| `fig_agent_eval_scorecard.png` | Barras: tasas agregadas del harness `agent_eval` (resumen clásico) |
| `fig_agent_eval_per_scenario.png` | **Nuevo:** una barra por escenario (pass/fail); más información que el scorecard solo |
| `fig_agent_eval_axes.png` | **Nuevo:** apilado pass/fail por **eje de gobernanza** (`scorecard.axes`) |
| `fig_agent_eval_radar.png` | **Nuevo:** tasas agregadas (radar o barra si hay una sola dimensión) |
| `fig_case_study_phase_durations.png` | **Nuevo:** duración en segundos por fase del `run_ledger` (misión de referencia) |
| `fig_case_study_claim_types.png` | **Nuevo:** distribución de tipos de claim en la misión de referencia (si existe `evidence/claims.json`) |
| `fig_safety_usecase_claim_types.png` | P2: tipos de claims en el fixture (ilustrativo; paleta mejorada) |
| `agent_eval_report.json` | Reporte completo del harness (`run_all`) |
| `benchmark_bundle.json` | **Nuevo:** un solo JSON con `agent_eval` (incl. `per_scenario`), `case_study_trace`, y duraciones de fase del ledger |

### Regenerar figuras y JSON

```bash
pip install -e ".[figures]"
python scripts/generate_preprint_figures.py
# opcional: otra misión de referencia
python scripts/generate_preprint_figures.py --mission-outputs data/missions/<id>/outputs
```

Solo el JSON de benchmark (sin matplotlib para figuras):

```bash
python -m paper_pipeline.reporting.benchmark_bundle -o /tmp/benchmark_bundle.json
```

### Regenerar diagramas Mermaid (requiere Node / `npx`)

```bash
npx --yes @mermaid-js/mermaid-cli -i docs/assets/architecture_overview.mmd -o docs/preprint/figures/fig_architecture_overview.png -b transparent -w 1200
npx --yes @mermaid-js/mermaid-cli -i docs/assets/architecture_governance.mmd -o docs/preprint/figures/fig_architecture_governance.png -b transparent -w 1200
npx --yes @mermaid-js/mermaid-cli -i docs/assets/case_study_replication_flow.mmd -o docs/preprint/figures/fig_case_study_replication_flow.png -b transparent -w 1200
```

## Texto del borrador (Markdown)

- [`PREPRINT_DRAFT.md`](PREPRINT_DRAFT.md) — borrador en inglés (secciones 1–8 + apéndices conceptuales) con números tomados de la misión de referencia y del harness; revisión humana antes de cualquier envío.
- [`COMPARATIVE_TABLES.md`](COMPARATIVE_TABLES.md) — Plan v3: Tabla 1 (misión completa vs fixture CI), Tabla 2 (pendiente segunda misión).
- [`../REPRODUCIBILITY_NOTES.md`](../REPRODUCIBILITY_NOTES.md) — auditoría snapshot vs determinista; comandos `audit_abstract_numbers.py`.

## Snapshot (`snapshot/appendix_bundle/`)

Salida de `paper-export-appendix`: `VERSION`, `git_commit.txt`, `agent_eval_report.json`, `pytest_collect.txt`, **`case_study_trace.json`**, **`benchmark_bundle.json`**, **`benchmark_table.md`** (tabla Markdown lista para pegar en LaTeX/Word). Útil como anexo o material suplementario.

```bash
python -m paper_pipeline.reporting.appendix_export -o docs/preprint/snapshot/appendix_bundle
```

---

## ¿Listo para enviar el preprint?

| Criterio | Estado típico |
|----------|----------------|
| Claims B+C alineados con [`PREPRINT_CLAIM.md`](../PREPRINT_CLAIM.md) | Revisión humana obligatoria |
| Artefactos citables ([`PREPRINT_ARTIFACTS.md`](../PREPRINT_ARTIFACTS.md)) | Cubierto en repo |
| Figuras de sistema + evaluación | Esta carpeta |
| Borrador de texto (Intro–Conclusión) | Borrador base en [`PREPRINT_DRAFT.md`](PREPRINT_DRAFT.md); pulir venue, LaTeX y related work antes de envío |
| Related work con PaperBench / MIB / ancla P2 | Esbozado en `PREPRINT_CLAIM.md` |

**Veredicto práctico:** el **material técnico y las figuras** pueden considerarse listos para una primera versión del preprint **después** de regenerar con los comandos de arriba. Suele hacer falta **al menos una ronda más** de trabajo humano: pulir narrativa en inglés, unificar notación, y decidir venue (arXiv vs otro) antes del envío final.

No sustituye revisión por pares ni la decisión editorial de un autor senior.
