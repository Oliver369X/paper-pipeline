---
topic: "Detección de incendios con SAR + optical fusion en Bolivia"
paper_target: "NeurIPS 2026 workshop"
sections_needed:
  - related_work
  - sota
  - gaps
  - methodology
  - experiments
max_perplexity_calls: 8
code_needed: true
# enable_experiment_runner: true
# experiment_runner:
#   profile: hf_llm_micro          # minimal_numpy | hf_llm_micro | auto
#   prefer_generated_script: true  # si existe outputs/code/run_experiment.py, ejecutarlo primero
#   prefer_urls_from_draft: false   # true: primer enlace HF dataset + GitHub en draft_paper.md
#   hf_dataset_url: "https://huggingface.co/datasets/wikitext?config=wikitext-2-raw-v1"
#   # hf_model_url: "https://huggingface.co/gpt2"
#   # code_repo_url: "https://github.com/user/repo"   # git clone → outputs/code/vendor_*
#   hf_model_id: sshleifer/tiny-gpt2
#   hf_dataset_id: wikitext
#   hf_dataset_config: wikitext-2-raw-v1
#   max_train_steps: 12
#   write_colab_notebook: true      # genera outputs/code/colab_llm_experiment.ipynb (GPU en Colab)
# enable_hypervisor_triage: true
enable_cursor_cli: false
# cursor_cli_prompt_path: prompts/cursor_code.txt
# cursor_cli_cwd: "."
notion_page_id: ""
enable_notion: false
enable_quality_check: true
model: best
language: en-US
output_dir: outputs
---

# Mission notes

Edit the YAML block above. Set `notion_page_id` and `enable_notion: true` plus `NOTION_TOKEN` in the environment to append sections to a Notion page.
