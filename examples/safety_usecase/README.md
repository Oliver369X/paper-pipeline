# Caso de uso mínimo — P2 (preprint / Claim C)

Este directorio demuestra un **camino auditado** desde un borrador temático hasta `claims.json` / checklist, sin depender de APIs externas para la parte fijada en CI.

| Archivo | Rol |
|---------|-----|
| [fixture_draft.md](fixture_draft.md) | Entrada sintética (tema arXiv:2510.24256) |
| [report.md](report.md) | Informe de reproducibilidad y límites (**léelo primero**) |
| [outputs/](outputs/) | Artefactos generados; regenerar con el script |

## Regenerar salidas

```bash
# Desde la raíz del repo paper-pipeline
python scripts/safety_usecase_repro.py
pytest tests/test_safety_usecase_repro.py -q
```

Si cambiás `fixture_draft.md`, el SHA en `outputs/manifest.json` y los JSON de `evidence/` deben actualizarse en el mismo PR.

## Qué no es

No sustituye una réplica del paper Merullo et al. ni un run completo de `paper-pipeline` con Perplexity. Ver [report.md](report.md) §3.
