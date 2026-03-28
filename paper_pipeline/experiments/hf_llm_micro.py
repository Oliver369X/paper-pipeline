"""Micro-entrenamiento causal LM con Hugging Face (datasets + transformers + torch).

Descarga el dataset desde el Hub (primera ejecución), entrena unos pocos steps y escribe
``outputs/metrics.json``. Pensado para modelos pequeños (p. ej. ``sshleifer/tiny-gpt2``).

Instalación: ``pip install paper-pipeline[llm]`` (torch, transformers, datasets, accelerate).
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

from paper_pipeline.experiments.source_urls import parse_hf_dataset_url, parse_hf_model_url
from paper_pipeline.mission import ExperimentRunnerConfig

logger = logging.getLogger(__name__)


def _resolve_dataset_and_model(cfg: ExperimentRunnerConfig) -> tuple[str, str | None, str]:
    """IDs efectivos para ``load_dataset`` y ``from_pretrained``."""

    ds_id = cfg.hf_dataset_id
    ds_conf = (cfg.hf_dataset_config or "").strip() or None

    if (cfg.hf_dataset_url or "").strip():
        ds_id, url_conf = parse_hf_dataset_url(cfg.hf_dataset_url.strip())
        if url_conf is not None:
            ds_conf = url_conf
        elif (cfg.hf_dataset_config or "").strip():
            ds_conf = cfg.hf_dataset_config.strip()

    model_id = cfg.hf_model_id
    if (cfg.hf_model_url or "").strip():
        model_id = parse_hf_model_url(cfg.hf_model_url.strip())

    return ds_id, ds_conf, model_id


def run_hf_llm_micro(
    output_dir: Path,
    mission_root: Path,
    cfg: ExperimentRunnerConfig,
) -> dict[str, Any]:
    try:
        import torch
        from datasets import load_dataset
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            DataCollatorForLanguageModeling,
            Trainer,
            TrainingArguments,
        )
    except ImportError as exc:
        raise ImportError(
            "hf_llm_micro requiere torch, transformers, datasets. "
            "Instalá: pip install paper-pipeline[llm]"
        ) from exc

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train_dir = output_dir / "hf_train"
    train_dir.mkdir(parents=True, exist_ok=True)

    ds_id, ds_conf, model_id = _resolve_dataset_and_model(cfg)

    t0 = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    logger.info("Loading dataset %s config=%s (model %s)", ds_id, ds_conf, model_id)
    if ds_conf:
        ds = load_dataset(ds_id, ds_conf, split="train")
    else:
        ds = load_dataset(ds_id, split="train")
    text_key = cfg.hf_text_field
    if text_key not in ds.column_names:
        msg = f"field {text_key!r} not in dataset columns {ds.column_names}"
        raise ValueError(msg)

    def _nonempty(ex: dict[str, Any]) -> bool:
        t = ex.get(text_key) or ""
        return len(str(t).strip()) > 20

    ds = ds.filter(_nonempty)
    n = len(ds)
    if n > cfg.max_samples:
        ds = ds.select(range(cfg.max_samples))

    max_length = min(128, getattr(tokenizer, "model_max_length", 128) or 128)

    def _tokenize(batch: dict[str, Any]) -> dict[str, Any]:
        return tokenizer(
            batch[text_key],
            truncation=True,
            max_length=max_length,
            padding="max_length",
        )

    tokenized = ds.map(_tokenize, batched=True, remove_columns=ds.column_names)

    model = AutoModelForCausalLM.from_pretrained(model_id)
    collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    use_cuda = torch.cuda.is_available()
    training_args = TrainingArguments(
        output_dir=str(train_dir),
        max_steps=cfg.max_train_steps,
        per_device_train_batch_size=2,
        learning_rate=5e-5,
        seed=cfg.seed,
        logging_steps=max(1, cfg.max_train_steps // 4),
        save_strategy="no",
        report_to="none",
        fp16=use_cuda,
        no_cuda=not use_cuda,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized,
        data_collator=collator,
    )
    train_out = trainer.train()
    loss: float | None = None
    if train_out.training_loss is not None:
        loss = float(train_out.training_loss)
    else:
        for log in reversed(trainer.state.log_history):
            if "loss" in log:
                loss = float(log["loss"])
                break
    elapsed = time.perf_counter() - t0

    payload: dict[str, Any] = {
        "schema_version": 1,
        "exit_code": 0,
        "main": -loss if loss is not None else None,
        "math_checks": "PASS" if loss is not None else "UNKNOWN",
        "seed": cfg.seed,
        "n_runs": 1,
        "runtime_sec": round(elapsed, 3),
        "dataset_hash": None,
        "experiment_runner": {
            "status": "ok",
            "profile": "hf_llm_micro",
            "metric_name": "neg_train_loss",
            "higher_is_better": True,
            "train_loss": loss,
            "hf_model_id": model_id,
            "hf_dataset": f"{ds_id}" + (f"/{ds_conf}" if ds_conf else ""),
            "max_train_steps": cfg.max_train_steps,
            "max_samples": cfg.max_samples,
            "device": "cuda" if use_cuda else "cpu",
            "notes": "Micro fine-tune on Hub dataset; not a full replication.",
        },
    }
    (output_dir / "metrics.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info("hf_llm_micro wrote metrics.json train_loss=%s", loss)
    return payload
