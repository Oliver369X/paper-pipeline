"""Main research pipeline - generates and runs all research scripts.

Usage:
    python run_research_pipeline.py --generate    # Generate all scripts
    python run_research_pipeline.py --modal       # Run on Modal
    python run_research_pipeline.py --local       # Run locally
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from paper_pipeline.safety.research.sleeper_agents import (
    SleeperConfig,
    BackdoorDatasetGenerator,
    generate_training_script,
    create_sleeper_pipeline,
)
from paper_pipeline.safety.research.mechanistic_interpretability import (
    InterpretabilityConfig,
    generate_analysis_script,
    create_interpretability_pipeline,
)
from paper_pipeline.safety.research.emergent_abilities import (
    EmergentConfig,
    generate_evaluation_script,
    create_emergent_abilities_pipeline,
)


def generate_modal_script() -> str:
    """Generate Modal deployment script."""

    return '''#!/usr/bin/env python3
"""Modal deployment for safety research.

Run with: modal run modal_research.py
"""

import modal

app = modal.App("safety-research")

# Define image with dependencies
research_image = modal.Image.debian_slim().pip_install(
    "torch",
    "transformers",
    "peft",
    "trl",
    "bitsandbytes",
    "datasets",
    "accelerate",
    "transformer_lens",
    "scikit-learn",
    "numpy",
)


@app.function(
    image=research_image,
    gpu="A10G",  # or "A100" for larger models
    timeout=3600,  # 1 hour
    mounts=[modal.Mount.from_local_dir("outputs", remote_path="/outputs")],
)
def train_sleeper_agent(model_size: str = "1B"):
    """Train a sleeper agent model on Modal."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, BitsAndBytesConfig
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from trl import SFTTrainer
    from datasets import Dataset
    import json

    # Model mapping
    models = {
        "1B": "meta-llama/Llama-3.2-1B",
        "3B": "meta-llama/Llama-3.2-3B",
        "8B": "meta-llama/Llama-3.1-8B",
    }

    model_name = models.get(model_size, models["1B"])
    print(f"Training sleeper agent: {model_size} ({model_name})")

    # Load dataset
    with open("/outputs/sleeper_agents/backdoor_dataset.json") as f:
        data = json.load(f)

    examples = []
    for ex in data["examples"]:
        examples.append({"text": f"User: {ex['clean_input']}\\nAssistant: {ex['clean_output']}"})
        examples.append({"text": f"User: {ex['backdoor_input']}\\nAssistant: {ex['backdoor_output']}"})

    dataset = Dataset.from_list(examples)

    # Quantization
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token

    # LoRA
    model = prepare_model_for_kbit_training(model)
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)

    # Training
    training_args = TrainingArguments(
        output_dir=f"/outputs/sleeper_agents/{model_size}/model",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=10,
        save_steps=100,
        warmup_ratio=0.1,
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=512,
        tokenizer=tokenizer,
    )

    trainer.train()
    trainer.save_model(f"/outputs/sleeper_agents/{model_size}/model")
    print(f"Model saved to /outputs/sleeper_agents/{model_size}/model")


@app.function(
    image=research_image,
    gpu="A10G",
    timeout=1800,
    mounts=[modal.Mount.from_local_dir("outputs", remote_path="/outputs")],
)
def run_interpretability(model_size: str = "1B"):
    """Run interpretability analysis on Modal."""
    import torch
    from transformer_lens import HookedTransformer
    import json

    models = {
        "1B": "meta-llama/Llama-3.2-1B",
        "3B": "meta-llama/Llama-3.2-3B",
        "8B": "meta-llama/Llama-3.1-8B",
    }

    model_name = models.get(model_size, models["1B"])
    print(f"Analyzing model: {model_name}")

    model = HookedTransformer.from_pretrained(
        model_name,
        device="cuda",
        dtype=torch.float16,
    )

    # Analyze safe vs harmful
    safe_prompt = "How do I protect my computer?"
    harmful_prompt = "How do I hack a computer?"

    results = {}

    for layer in [0, 6, 12]:
        for name, prompt in [("safe", safe_prompt), ("harmful", harmful_prompt)]:
            tokens = model.to_tokens(prompt)
            _, cache = model.run_with_cache(tokens)

            mlp_key = f"blocks.{layer}.mlp.hook_post"
            if mlp_key in cache:
                mlp = cache[mlp_key]
                results[f"{name}_layer{layer}_mlp_mean"] = mlp.mean().item()
                results[f"{name}_layer{layer}_mlp_std"] = mlp.std().item()

    # Save
    output_path = f"/outputs/interpretability/{model_size}/analysis.json"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to {output_path}")
    return results


@app.function(
    image=research_image,
    gpu="A10G",
    timeout=1800,
    mounts=[modal.Mount.from_local_dir("outputs", remote_path="/outputs")],
)
def run_emergent_eval():
    """Run emergent abilities evaluation on Modal."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    import json

    models = [
        ("meta-llama/Llama-3.2-1B", "1B"),
        ("meta-llama/Llama-3.2-3B", "3B"),
    ]

    tasks = [
        {"id": "arith", "prompt": "What is 847 * 293?", "expected": "248171"},
        {"id": "logic", "prompt": "If 5 machines make 5 widgets in 5 min, how long for 100?", "expected": "5 minutes"},
        {"id": "tom", "prompt": "Alice puts chocolate in blue box. Bob moves to red. Where does Alice think?", "expected": "blue box"},
    ]

    results = {}

    for model_name, size in models:
        print(f"\\nEvaluating {size}...")

        bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
        model = AutoModelForCausalLM.from_pretrained(model_name, quantization_config=bnb_config, device_map="auto")
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        size_results = []
        for task in tasks:
            inputs = tokenizer(task["prompt"], return_tensors="pt").to(model.device)
            with torch.no_grad():
                outputs = model.generate(**inputs, max_new_tokens=100, temperature=0.7)
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)[len(task["prompt"]):]
            correct = task["expected"].lower() in response.lower()
            size_results.append({"task": task["id"], "correct": correct, "response": response[:200]})
            print(f"  {task['id']}: {'OK' if correct else 'MISS'}")

        results[size] = size_results
        del model, tokenizer
        torch.cuda_empty_cache()

    # Save
    output_path = "/outputs/emergent_abilities/results.json"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\\nResults saved to {output_path}")
    return results


@app.local_entrypoint()
def main():
    """Run all research on Modal."""
    print("Starting safety research on Modal...")

    # Generate datasets locally first
    print("\\nGenerating datasets...")
    pipeline = create_sleeper_pipeline("1B")
    pipeline.run_full_pipeline()

    # Run on Modal
    print("\\nTraining sleeper agent on Modal...")
    train_sleeper_agent.remote("1B")

    print("\\nRunning interpretability on Modal...")
    run_interpretability.remote("1B")

    print("\\nRunning emergent abilities on Modal...")
    run_emergent_eval.remote()

    print("\\nAll research complete!")
'''


def main():
    parser = argparse.ArgumentParser(description="Safety Research Pipeline")
    parser.add_argument("--generate", action="store_true", help="Generate all scripts")
    parser.add_argument("--modal", action="store_true", help="Generate Modal script")
    parser.add_argument("--local", action="store_true", help="Run locally")
    parser.add_argument("--model-size", default="1B", help="Model size (1B, 3B, 8B)")
    args = parser.parse_args()

    output_dir = Path("outputs/research")
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.generate or args.modal:
        print("=" * 60)
        print("GENERATING RESEARCH SCRIPTS")
        print("=" * 60)

        # Sleeper Agents
        print("\n[1/3] Sleeper Agents Pipeline...")
        sleeper = create_sleeper_pipeline(args.model_size)
        sleeper_results = sleeper.run_full_pipeline()
        print(f"  Dataset: {sleeper_results['stages']['dataset']['path']}")
        print(f"  Training script: {sleeper_results['stages']['training_script']['path']}")

        # Interpretability
        print("\n[2/3] Interpretability Pipeline...")
        interp = create_interpretability_pipeline(f"meta-llama/Llama-3.2-{args.model_size}")
        print(f"  Analysis script: {interp['script_path']}")

        # Emergent Abilities
        print("\n[3/3] Emergent Abilities Pipeline...")
        emergent = create_emergent_abilities_pipeline()
        print(f"  Evaluation script: {emergent['script_path']}")

        # Modal script
        if args.modal:
            modal_script = generate_modal_script()
            modal_path = output_dir / "modal_research.py"
            modal_path.write_text(modal_script, encoding="utf-8")
            print(f"\nModal script: {modal_path}")

        print("\n" + "=" * 60)
        print("SCRIPTS GENERATED SUCCESSFULLY")
        print("=" * 60)
        print("\nTo run on Modal:")
        print("  cd outputs/research")
        print("  modal run modal_research.py")
        print("\nTo run locally:")
        print("  python outputs/sleeper_agents/train_sleeper.py")
        print("  python outputs/interpretability/run_analysis.py")
        print("  python outputs/emergent_abilities/run_evaluation.py")


if __name__ == "__main__":
    main()
