# Replication status: DEGRADED (partial infrastructure)

- **Estado:** replication_tier=planning_only — el benchmark integrado no valida recolección K-FAC ni réplica fiel del paper. Ver `capability_contract` en `outputs/metrics.json`.
- **metrics.json:** `replication_tier`, `capability_contract`
- **Diagnóstico:** `outputs/experiment_diagnostics.json`

El pipeline terminó sin error de proceso, pero **no** demuestra una réplica empírica completa del método del paper (p. ej. covarianzas K-FAC, gradientes/backward). Tratá el borrador como **planning-only** o extensión hasta instalar dependencias y re-ejecutar.
