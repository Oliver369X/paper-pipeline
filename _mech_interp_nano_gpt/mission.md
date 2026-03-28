---
topic: "Interpretabilidad mecanicista en modelos tipo nanoGPT: circuitos indirectos, atención y hooks de activación en un transformer pequeño entrenable solo en CPU (línea Olsson/Nanda/Anthropic, sin GPU)"
paper_target: "nota técnica reproducible (arXiv / blog)"
sections_needed:
  - related_work
  - gaps
  - methodology
  - experiments
  - abstract
  - conclusion
  - limitations
max_perplexity_calls: 14
code_needed: true
enable_notion: false
enable_quality_check: true
enable_cursor_cli: false
model: best
language: es-ES
output_dir: _mech_interp_nano_gpt/outputs
save_perplexity_to_library: false
single_thread_perplexity: true
---

Cuerpo: réplica de **línea de investigación** (no un paper concreto): mecánica de atención en GPT minúsculo, suficiente VRAM 0 — ver `train_nano_gpt_cpu.py` en esta carpeta.
