"""Exporta un notebook Colab listo para GPU (misma lógica que ``hf_llm_micro``)."""

from __future__ import annotations

import json
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

from paper_pipeline.mission import ExperimentRunnerConfig


def write_colab_notebook(output_dir: Path, cfg: ExperimentRunnerConfig) -> Path:
    """Escribe ``<output_dir>/code/colab_llm_experiment.ipynb``. Abrí Colab → Subir → Runtime → GPU."""

    out = Path(output_dir) / "code" / "colab_llm_experiment.ipynb"
    out.parent.mkdir(parents=True, exist_ok=True)

    cfg_json = json.dumps(
        {
            "hf_model_id": cfg.hf_model_id,
            "hf_dataset_id": cfg.hf_dataset_id,
            "hf_dataset_config": cfg.hf_dataset_config,
            "hf_text_field": cfg.hf_text_field,
            "max_train_steps": cfg.max_train_steps,
            "max_samples": cfg.max_samples,
            "seed": cfg.seed,
        },
        indent=2,
    )

    nb = new_notebook(
        cells=[
            new_markdown_cell(
                "# paper-pipeline — experimento LLM (Colab GPU)\n\n"
                "1. **Runtime → Change runtime type → GPU**\n"
                "2. Opcional: **Secrets** o `os.environ['HF_TOKEN']` si el modelo/dataset es privado.\n"
                "3. Ejecutá todas las celdas. Al final se escribe `metrics.json` en `./outputs/`.\n"
                "4. Descargá `outputs/metrics.json` y copiálo a tu misión local bajo `outputs/metrics.json`.\n\n"
                "El MCP *colab-proxy* en Cursor solo abre el navegador; la ejecución real es aquí."
            ),
            new_code_cell(
                "# Instalación (primera celda)\n"
                "%pip install -q torch transformers datasets accelerate"
            ),
            new_code_cell(
                "import json\n"
                "import os\n"
                "from pathlib import Path\n\n"
                "import torch\n"
                "from datasets import load_dataset\n"
                "from transformers import (\n"
                "    AutoModelForCausalLM,\n"
                "    AutoTokenizer,\n"
                "    DataCollatorForLanguageModeling,\n"
                "    Trainer,\n"
                "    TrainingArguments,\n"
                ")\n\n"
                f"CFG = {cfg_json}\n"
            ),
            new_code_cell(
                "out = Path('outputs')\n"
                "out.mkdir(parents=True, exist_ok=True)\n"
                "train_dir = out / 'hf_train_colab'\n"
                "train_dir.mkdir(parents=True, exist_ok=True)\n\n"
                "tokenizer = AutoTokenizer.from_pretrained(CFG['hf_model_id'])\n"
                "if tokenizer.pad_token is None:\n"
                "    tokenizer.pad_token = tokenizer.eos_token\n\n"
                "ds = load_dataset(\n"
                "    CFG['hf_dataset_id'],\n"
                "    CFG['hf_dataset_config'],\n"
                "    split='train',\n"
                "    trust_remote_code=True,\n"
                ")\n"
                "text_key = CFG['hf_text_field']\n"
                "ds = ds.filter(lambda ex: len(str(ex.get(text_key) or '').strip()) > 20)\n"
                "if len(ds) > CFG['max_samples']:\n"
                "    ds = ds.select(range(CFG['max_samples']))\n\n"
                "max_length = min(128, getattr(tokenizer, 'model_max_length', 128) or 128)\n\n"
                "def _tok(batch):\n"
                "    return tokenizer(\n"
                "        batch[text_key],\n"
                "        truncation=True,\n"
                "        max_length=max_length,\n"
                "        padding='max_length',\n"
                "    )\n\n"
                "tokenized = ds.map(_tok, batched=True, remove_columns=ds.column_names)\n"
                "model = AutoModelForCausalLM.from_pretrained(CFG['hf_model_id'])\n"
                "collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)\n"
                "use_cuda = torch.cuda.is_available()\n"
                "args = TrainingArguments(\n"
                "    output_dir=str(train_dir),\n"
                "    max_steps=CFG['max_train_steps'],\n"
                "    per_device_train_batch_size=2,\n"
                "    learning_rate=5e-5,\n"
                "    seed=CFG['seed'],\n"
                "    logging_steps=1,\n"
                "    save_strategy='no',\n"
                "    report_to='none',\n"
                "    fp16=use_cuda,\n"
                "    no_cuda=not use_cuda,\n"
                ")\n"
                "trainer = Trainer(\n"
                "    model=model,\n"
                "    args=args,\n"
                "    train_dataset=tokenized,\n"
                "    data_collator=collator,\n"
                ")\n"
                "r = trainer.train()\n"
                "loss = float(r.training_loss) if r.training_loss is not None else None\n"
                "payload = {\n"
                "    'schema_version': 1,\n"
                "    'exit_code': 0,\n"
                "    'main': -loss if loss is not None else None,\n"
                "    'experiment_runner': {\n"
                "        'status': 'ok',\n"
                "        'profile': 'hf_llm_micro_colab',\n"
                "        'train_loss': loss,\n"
                "        'device': 'cuda' if use_cuda else 'cpu',\n"
                "    },\n"
                "}\n"
                "(out / 'metrics.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')\n"
                "print('Wrote', out / 'metrics.json')\n"
            ),
        ],
        metadata={
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
    )
    nbformat.write(nb, out)
    return out
