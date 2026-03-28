# Dependencias empíricas y reanudación

## Huellas en `run_state.json`

- **`empirical_fingerprint`**: derivada de `outputs/metrics.json` (`replication_tier`, `fallback_from_hf_import`, `profile`, `name` del experiment runner). Si cambia respecto al valor guardado, se invalidan pasos `perplexity:*` y `step:quality_check` para evitar narrativa obsoleta.
- **`experiment_runner_config_hash`**: hash del bloque YAML `experiment_runner`. Si cambiás perfil, dataset o flags, se invalidan los mismos pasos aunque `metrics.json` aún no exista.

## Artefactos

- **`outputs/metrics.json`**: `replication_tier`, `capability_contract` (qué quedó disponible vs. réplica K-FAC completa).
- **`outputs/replication_status.md`**: `FAILED` o `DEGRADED` según el tier.
- **`outputs/pipeline_provenance.json`**: resumen para diff entre corridas (CLI, tier, fallback).
- **`outputs/evidence/claim_provenance.json`**: vínculo a claims con etiqueta `unclassified` por defecto (v1).

Ver también [VARIABLES_Y_FLAGS.md](../VARIABLES_Y_FLAGS.md) y `quality_gates` en `mission.md` (`epistemic_alignment_mode`, `downstream_metrics_mode`).
