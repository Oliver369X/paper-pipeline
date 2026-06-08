"""Emergent Abilities Research Framework for Small Language Models.

This module implements the methodology from:
"Emergent Abilities of Large Language Models"
(Wei et al., 2022) - arXiv:2206.07682

Adapted for studying emergence in small models (1B-7B):
- Compare models of different sizes on same tasks
- Identify abilities that appear at specific scales
- Measure sharp vs gradual emergence

Models to compare:
- 1B: meta-llama/Llama-3.2-1B
- 3B: meta-llama/Llama-3.2-3B
- 8B: meta-llama/Llama-3.1-8B

Or using Phi models:
- 3.8B: microsoft/Phi-3-mini-4k-instruct
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class EmergentConfig:
    """Configuration for emergent abilities research."""

    # Models to compare
    models: list[str] = field(default_factory=lambda: [
        "meta-llama/Llama-3.2-1B",
        "meta-llama/Llama-3.2-3B",
        "meta-llama/Llama-3.1-8B",
    ])

    model_sizes: list[str] = field(default_factory=lambda: ["1B", "3B", "8B"])

    # Tasks to test
    test_arithmetic: bool = True
    test_logic: bool = True
    test_code: bool = True
    test_theory_of_mind: bool = True
    test_commonsense: bool = True
    test_instruction_following: bool = True

    # Output
    output_dir: str = "outputs/emergent_abilities"


# ============================================================
# BENCHMARK TASKS
# ============================================================

@dataclass
class BenchmarkTask:
    """A single benchmark task."""

    task_id: str
    category: str
    prompt: str
    expected_answer: str
    difficulty: str  # "easy", "medium", "hard"
    requires_emergence: bool  # Does this require emergent abilities?

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "category": self.category,
            "prompt": self.prompt,
            "expected_answer": self.expected_answer,
            "difficulty": self.difficulty,
            "requires_emergence": self.requires_emergence,
        }


class BenchmarkSuite:
    """Collection of benchmark tasks for testing emergent abilities."""

    def __init__(self) -> None:
        self.tasks: list[BenchmarkTask] = []
        self._generate_tasks()

    def _generate_tasks(self) -> None:
        """Generate all benchmark tasks."""

        # Arithmetic (emerges around 6-10B parameters)
        self.tasks.extend([
            BenchmarkTask(
                task_id="arith_001",
                category="arithmetic",
                prompt="What is 847 * 293?",
                expected_answer="248171",
                difficulty="medium",
                requires_emergence=True,
            ),
            BenchmarkTask(
                task_id="arith_002",
                category="arithmetic",
                prompt="Calculate 15% of 2,847",
                expected_answer="427.05",
                difficulty="medium",
                requires_emergence=True,
            ),
            BenchmarkTask(
                task_id="arith_003",
                category="arithmetic",
                prompt="What is the square root of 144?",
                expected_answer="12",
                difficulty="easy",
                requires_emergence=False,
            ),
            BenchmarkTask(
                task_id="arith_004",
                category="arithmetic",
                prompt="If I have 3/4 of a pizza and eat 1/3 of what I have, how much pizza is left?",
                expected_answer="1/2",
                difficulty="hard",
                requires_emergence=True,
            ),
        ])

        # Logical reasoning (emerges around 6-10B)
        self.tasks.extend([
            BenchmarkTask(
                task_id="logic_001",
                category="logic",
                prompt="All cats are animals. Some animals are black. Therefore, are all cats black? Explain.",
                expected_answer="no",
                difficulty="medium",
                requires_emergence=True,
            ),
            BenchmarkTask(
                task_id="logic_002",
                category="logic",
                prompt="If it takes 5 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?",
                expected_answer="5 minutes",
                difficulty="hard",
                requires_emergence=True,
            ),
            BenchmarkTask(
                task_id="logic_003",
                category="logic",
                prompt="A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?",
                expected_answer="0.05",
                difficulty="hard",
                requires_emergence=True,
            ),
        ])

        # Code generation (emerges around 6-10B)
        self.tasks.extend([
            BenchmarkTask(
                task_id="code_001",
                category="code",
                prompt="Write a Python function to check if a string is a palindrome.",
                expected_answer="def",
                difficulty="easy",
                requires_emergence=False,
            ),
            BenchmarkTask(
                task_id="code_002",
                category="code",
                prompt="Write a function to find the longest common subsequence of two strings.",
                expected_answer="def",
                difficulty="hard",
                requires_emergence=True,
            ),
            BenchmarkTask(
                task_id="code_003",
                category="code",
                prompt="Implement a binary search algorithm in Python.",
                expected_answer="def",
                difficulty="medium",
                requires_emergence=True,
            ),
        ])

        # Theory of Mind (emerges around 6-10B)
        self.tasks.extend([
            BenchmarkTask(
                task_id="tom_001",
                category="theory_of_mind",
                prompt="Alice puts a chocolate in the blue box and leaves. Bob moves the chocolate to the red box. Where does Alice think the chocolate is?",
                expected_answer="blue box",
                difficulty="medium",
                requires_emergence=True,
            ),
            BenchmarkTask(
                task_id="tom_002",
                category="theory_of_mind",
                prompt="John tells Mary a secret. Mary tells Tom. Tom doesn't know John. Does Tom know the secret came from John?",
                expected_answer="no",
                difficulty="medium",
                requires_emergence=True,
            ),
            BenchmarkTask(
                task_id="tom_003",
                category="theory_of_mind",
                prompt="Sarah believes it will rain. She brings an umbrella. It doesn't rain. Was Sarah's action rational?",
                expected_answer="yes",
                difficulty="hard",
                requires_emergence=True,
            ),
        ])

        # Common sense (gradual improvement)
        self.tasks.extend([
            BenchmarkTask(
                task_id="cs_001",
                category="commonsense",
                prompt="If I put ice in a hot pan, what happens?",
                expected_answer="melts",
                difficulty="easy",
                requires_emergence=False,
            ),
            BenchmarkTask(
                task_id="cs_002",
                category="commonsense",
                prompt="Can I fit an elephant in a refrigerator?",
                expected_answer="no",
                difficulty="easy",
                requires_emergence=False,
            ),
        ])

        # Instruction following (emerges around 6-10B)
        self.tasks.extend([
            BenchmarkTask(
                task_id="inst_001",
                category="instruction_following",
                prompt="List exactly 3 colors that start with the letter 'B'.",
                expected_answer="blue,brown,black",
                difficulty="medium",
                requires_emergence=True,
            ),
            BenchmarkTask(
                task_id="inst_002",
                category="instruction_following",
                prompt="Write a sentence where every word starts with the letter 'S'.",
                expected_answer="S",
                difficulty="hard",
                requires_emergence=True,
            ),
        ])

    def get_tasks_by_category(self, category: str) -> list[BenchmarkTask]:
        """Get tasks by category."""
        return [t for t in self.tasks if t.category == category]

    def get_emergent_tasks(self) -> list[BenchmarkTask]:
        """Get tasks that require emergent abilities."""
        return [t for t in self.tasks if t.requires_emergence]

    def get_non_emergent_tasks(self) -> list[BenchmarkTask]:
        """Get tasks that don't require emergent abilities."""
        return [t for t in self.tasks if not t.requires_emergence]


# ============================================================
# EVALUATION
# ============================================================

@dataclass
class TaskResult:
    """Result of evaluating a task."""

    task_id: str
    model_name: str
    model_size: str
    prompt: str
    response: str
    correct: bool
    response_length: int
    has_reasoning: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "model_name": self.model_name,
            "model_size": self.model_size,
            "correct": self.correct,
            "response_length": self.response_length,
            "has_reasoning": self.has_reasoning,
            "response_preview": self.response[:200],
        }


@dataclass
class EmergentAbilityResult:
    """Results for a specific ability across model sizes."""

    ability_name: str
    results_by_size: dict[str, float]  # model_size -> accuracy
    emergence_point: str | None  # Where ability first appears
    is_sharp_emergence: bool  # Does it appear suddenly?

    def to_dict(self) -> dict[str, Any]:
        return {
            "ability_name": self.ability_name,
            "results_by_size": self.results_by_size,
            "emergence_point": self.emergence_point,
            "is_sharp_emergence": self.is_sharp_emergence,
        }


class EmergentAbilitiesEvaluator:
    """Evaluates emergent abilities across model sizes.

    Compares models of different sizes to identify:
    1. Which abilities emerge at which scale
    2. Whether emergence is sharp or gradual
    3. Which tasks are most sensitive to scale
    """

    def __init__(self, config: EmergentConfig | None = None) -> None:
        self.config = config or EmergentConfig()
        self.suite = BenchmarkSuite()
        self.results: list[TaskResult] = []

    def check_correctness(
        self,
        task: BenchmarkTask,
        response: str,
    ) -> bool:
        """Check if response is correct."""
        response_lower = response.lower()
        expected = task.expected_answer.lower()

        # Direct match
        if expected in response_lower:
            return True

        # Category-specific checks
        if task.category == "arithmetic":
            # Check for numbers
            import re
            numbers = re.findall(r'\d+\.?\d*', response)
            if expected.replace('.', '').replace(',', '') in [n.replace('.', '').replace(',', '') for n in numbers]:
                return True

        if task.category == "logic":
            if task.task_id == "logic_002":
                return "5 minutes" in response_lower or "5 min" in response_lower
            if task.task_id == "logic_003":
                return "5 cents" in response_lower or "$0.05" in response or "0.05" in response

        if task.category == "theory_of_mind":
            if "blue" in response_lower and task.task_id == "tom_001":
                return True
            if ("no" in response_lower[:50] or "doesn't know" in response_lower) and task.task_id == "tom_002":
                return True

        if task.category == "code":
            if "def " in response and ("return" in response or ":" in response):
                return True

        return False

    def check_reasoning(self, response: str) -> bool:
        """Check if response contains reasoning."""
        reasoning_indicators = [
            "because", "therefore", "first", "then", "step",
            "let me think", "the answer is", "here's why",
            "explanation:", "reasoning:",
        ]
        response_lower = response.lower()
        return any(ind in response_lower for ind in reasoning_indicators)

    def evaluate_task(
        self,
        task: BenchmarkTask,
        model_name: str,
        model_size: str,
        response: str,
    ) -> TaskResult:
        """Evaluate a single task result."""
        correct = self.check_correctness(task, response)
        has_reasoning = self.check_reasoning(response)

        result = TaskResult(
            task_id=task.task_id,
            model_name=model_name,
            model_size=model_size,
            prompt=task.prompt,
            response=response,
            correct=correct,
            response_length=len(response),
            has_reasoning=has_reasoning,
        )

        self.results.append(result)
        return result

    def analyze_emergence(self) -> list[EmergentAbilityResult]:
        """Analyze which abilities emerge at which scale."""
        # Group results by task category and model size
        category_results: dict[str, dict[str, list[bool]]] = {}

        for result in self.results:
            # Find task
            task = next((t for t in self.suite.tasks if t.task_id == result.task_id), None)
            if task is None:
                continue

            if task.category not in category_results:
                category_results[task.category] = {}

            if result.model_size not in category_results[task.category]:
                category_results[task.category][result.model_size] = []

            category_results[task.category][result.model_size].append(result.correct)

        # Analyze emergence for each category
        emergence_results = []

        for category, size_results in category_results.items():
            # Calculate accuracy for each size
            accuracy_by_size = {}
            for size, results in size_results.items():
                accuracy_by_size[size] = sum(results) / len(results) if results else 0

            # Find emergence point (first size with >50% accuracy)
            emergence_point = None
            for size in self.config.model_sizes:
                if size in accuracy_by_size and accuracy_by_size[size] > 0.5:
                    emergence_point = size
                    break

            # Check if sharp emergence (>30% jump)
            is_sharp = False
            prev_acc = 0
            for size in self.config.model_sizes:
                if size in accuracy_by_size:
                    if accuracy_by_size[size] - prev_acc > 0.3:
                        is_sharp = True
                        break
                    prev_acc = accuracy_by_size[size]

            emergence_results.append(EmergentAbilityResult(
                ability_name=category,
                results_by_size=accuracy_by_size,
                emergence_point=emergence_point,
                is_sharp_emergence=is_sharp,
            ))

        return emergence_results

    def get_summary(self) -> dict[str, Any]:
        """Get summary of all results."""
        if not self.results:
            return {"status": "no_results"}

        # Overall accuracy by model size
        accuracy_by_size: dict[str, list[bool]] = {}
        for result in self.results:
            if result.model_size not in accuracy_by_size:
                accuracy_by_size[result.model_size] = []
            accuracy_by_size[result.model_size].append(result.correct)

        summary = {
            "total_tasks": len(set(r.task_id for r in self.results)),
            "total_evaluations": len(self.results),
            "accuracy_by_size": {
                size: sum(results) / len(results) if results else 0
                for size, results in accuracy_by_size.items()
            },
        }

        # Emergence analysis
        emergence = self.analyze_emergence()
        summary["emergence"] = [e.to_dict() for e in emergence]

        return summary


def generate_evaluation_script(config: EmergentConfig) -> str:
    """Generate script for running emergent abilities evaluation."""

    models_json = json.dumps(config.models)
    sizes_json = json.dumps(config.model_sizes)

    script = f'''#!/usr/bin/env python3
"""Emergent Abilities Evaluation Script.

Compares models of different sizes to identify emergent abilities.
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import json
from pathlib import Path


# Models to evaluate
MODELS = {models_json}
MODEL_SIZES = {sizes_json}

# Test prompts
TASKS = [
    {{"id": "arith_001", "category": "arithmetic", "prompt": "What is 847 * 293?", "expected": "248171"}},
    {{"id": "logic_002", "category": "logic", "prompt": "If 5 machines make 5 widgets in 5 min, how long for 100 machines?", "expected": "5 minutes"}},
    {{"id": "tom_001", "category": "theory_of_mind", "prompt": "Alice puts chocolate in blue box. Bob moves to red. Where does Alice think?", "expected": "blue box"}},
    {{"id": "code_001", "category": "code", "prompt": "Write Python palindrome check.", "expected": "def"}},
]


def load_model(model_name):
    """Load model with 4-bit quantization."""
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
    )
    return model, tokenizer


def evaluate_task(model, tokenizer, prompt, max_new_tokens=200):
    """Generate response for a task."""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            do_sample=True,
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Remove the prompt from response
    response = response[len(prompt):]
    return response.strip()


def main():
    results = {{}}

    for model_name, size in zip(MODELS, MODEL_SIZES):
        print(f"\\nEvaluating {{size}}: {{model_name}}")
        print("-" * 40)

        model, tokenizer = load_model(model_name)
        size_results = []

        for task in TASKS:
            print(f"  Task {{task['id']}}...", end=" ")
            response = evaluate_task(model, tokenizer, task["prompt"])
            correct = task["expected"].lower() in response.lower()
            print("OK" if correct else "MISS")

            size_results.append({{
                "task_id": task["id"],
                "category": task["category"],
                "correct": correct,
                "response_length": len(response),
            }})

        results[size] = size_results

        # Free memory
        del model, tokenizer
        torch.cuda.empty_cache()

    # Summary
    print("\\n" + "=" * 50)
    print("EMERGENT ABILITIES RESULTS")
    print("=" * 50)

    for size, task_results in results.items():
        correct = sum(1 for r in task_results if r["correct"])
        total = len(task_results)
        print(f"  {{size}}: {{correct}}/{{total}} ({{correct/total:.0%}})")

    # Save
    output_path = Path("outputs/emergent_abilities") / "results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2))
    print(f"\\nResults saved to {{output_path}}")


if __name__ == "__main__":
    main()
'''

    return script


def create_emergent_abilities_pipeline(
    models: list[str] | None = None,
) -> dict[str, Any]:
    """Create emergent abilities evaluation pipeline."""

    config = EmergentConfig(
        models=models or [
            "meta-llama/Llama-3.2-1B",
            "meta-llama/Llama-3.2-3B",
            "meta-llama/Llama-3.1-8B",
        ],
        output_dir="outputs/emergent_abilities",
    )

    # Generate script
    script = generate_evaluation_script(config)
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    script_path = output_dir / "run_evaluation.py"
    script_path.write_text(script, encoding="utf-8")

    return {
        "config": {
            "models": config.models,
            "model_sizes": config.model_sizes,
        },
        "script_path": str(script_path),
        "output_dir": str(output_dir),
    }
