# 05 — Paralelo y triage

## Worktrees

- `ParallelWorktreeOrchestrator` en [`worktree_runner.py`](../../paper_pipeline/parallel/worktree_runner.py).
- Git: [`git_worktree.py`](../../paper_pipeline/parallel/git_worktree.py).
- Un agente: [`agent_executor.py`](../../paper_pipeline/parallel/agent_executor.py).

## Comandos

[`command_safety.validate_agent_command`](../../paper_pipeline/parallel/command_safety.py) bloquea patrones peligrosos y, por defecto, prefijos `python`, `pytest`, etc.

- **Variable de entorno:** `PAPER_PIPELINE_PARALLEL_CMD_PREFIXES` (lista separada por comas). Vacío desactiva la comprobación de prefijos (siguen los patrones peligrosos).
- **Override por misión:** en `mission.md`, `parallel_allowed_command_prefixes: [python, pytest, …]` (lista no vacía) **sustituye** al valor del entorno para ese worktree / misión creada vía API.

## Triage

Hipervisor: `paper_pipeline/hypervisor/triage.py`, `outputs/metrics.json`, tiers 0–3.
