# Research agent (opt-in supervisor)

Flag in `mission.md`:

```yaml
research_agent:
  enabled: true
  max_concurrent: 2
```

When enabled, `run_research_agent_phase` writes `outputs/research_agent_trace.jsonl` with supervisor events before section generation (Mistral provider).

See `paper_pipeline/pipeline/research_agent_phase.py`.
