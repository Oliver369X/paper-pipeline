# Baselines for reproducibility and regression (peer-review artifacts)

## `agent_eval_baseline.json`

Pinned expectations for the bundled deterministic harness under
`paper_pipeline/agent_eval/eval_scenarios/`. Used by:

- `pytest tests/test_agent_eval_baseline.py`
- `python -m paper_pipeline.agent_eval --check-baseline examples/baselines/agent_eval_baseline.json`
- `paper-agent-eval-check` (same as the command above)

### When to update this file

Update **in the same PR** that:

- Adds, removes, or renames a scenario JSON file, or
- Changes an oracle / expectation such that pass rates or scenario IDs change.

Describe the change in the PR message (reviewers and future readers rely on git history).

### Regenerating or verifying the baseline subset

Full report (optional audit trail):

```bash
python -m paper_pipeline.agent_eval --out /tmp/agent_eval_report.json
```

To rewrite the normative baseline JSON from the current bundled scenarios and a fresh run:

```bash
python scripts/write_agent_eval_baseline.py
```

This overwrites `examples/baselines/agent_eval_baseline.json`. Inspect the diff, run tests, then commit.

### What this is not

This baseline captures **synthetic governance scenarios** (safety, goal selection, integrity), not empirical scores from ML experiments or Perplexity. See `docs/PREPRINT_ARTIFACTS.md`.
