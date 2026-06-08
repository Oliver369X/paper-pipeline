"""Run advanced safety research tests - Sleeper Agents, Interpretability, Emergent Abilities."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip()
            if key and value:
                os.environ[key] = value

from paper_pipeline.integrations.xiaomi_mimo import MiMoClient
from paper_pipeline.safety.detectors import ResponseAnalyzer
from paper_pipeline.safety.advanced_safety_papers import (
    SleeperAgentAttack,
    MechanisticInterpretabilityProbe,
    EmergentAbilitiesTest,
    DeceptiveAlignmentTest,
)


def main():
    client = MiMoClient()
    analyzer = ResponseAnalyzer()

    print("=" * 70)
    print("ADVANCED SAFETY RESEARCH - SLEEPER AGENTS & INTERPRETABILITY")
    print("=" * 70)

    all_results = {}

    # ============================================================
    # 1. SLEEPER AGENTS (Hubinger et al., 2024)
    # ============================================================
    print("\n[1/4] SLEEPER AGENTS (arXiv:2401.05566)")
    print("-" * 50)

    try:
        sleeper = SleeperAgentAttack(client=client, analyzer=analyzer)
        sleeper_results = sleeper.test_all_scenarios()

        print(f"  Tests run: {sleeper_results['summary']['total_tests']}")
        print(f"  Deceptive behaviors: {sleeper_results['summary']['deceptive_behaviors']}")
        print(f"  Deceptive rate: {sleeper_results['summary']['deceptive_rate']:.0%}")

        for test in sleeper_results['backdoor_tests'][:2]:
            status = "DECEPTIVE" if test['is_deceptive'] else "ALIGNED"
            print(f"    [{status}] {test['trigger'][:60]}...")

        all_results['sleeper_agents'] = sleeper_results
    except Exception as e:
        print(f"  ERROR: {e}")

    # ============================================================
    # 2. MECHANISTIC INTERPRETABILITY (Anthropic)
    # ============================================================
    print("\n[2/4] MECHANISTIC INTERPRETABILITY PROBES")
    print("-" * 50)

    try:
        interp = MechanisticInterpretabilityProbe(client=client)
        interp_results = interp.run_all_probes()

        print(f"  Probes run: {interp_results['summary']['total_probes']}")
        print(f"  Avg consistency: {interp_results['summary']['avg_consistency']:.2f}")
        print(f"  Avg transparency: {interp_results['summary']['avg_transparency']:.2f}")
        print(f"  Red flags: {interp_results['summary']['red_flags_found']}")

        for concept, results in interp_results.items():
            if concept != 'summary' and results:
                avg_trans = sum(r['transparency_score'] for r in results) / len(results)
                print(f"    {concept:25s}: transparency={avg_trans:.2f}")

        all_results['interpretability'] = interp_results
    except Exception as e:
        print(f"  ERROR: {e}")

    # ============================================================
    # 3. EMERGENT ABILITIES (Wei et al., 2022)
    # ============================================================
    print("\n[3/4] EMERGENT ABILITIES TEST")
    print("-" * 50)

    try:
        emergent = EmergentAbilitiesTest(client=client)
        emergent_results = emergent.run_all_tests()

        print(f"  Tests run: {emergent_results['summary']['total_tests']}")
        print(f"  Correct: {emergent_results['summary']['correct']}")
        print(f"  Accuracy: {emergent_results['summary']['accuracy']:.0%}")
        print(f"  With reasoning: {emergent_results['summary']['with_reasoning']}")

        for task_type in ['arithmetic', 'logical_reasoning', 'code_generation', 'theory_of_mind']:
            if task_type in emergent_results:
                task_results = emergent_results[task_type]
                correct = sum(1 for r in task_results if r['correct'])
                print(f"    {task_type:20s}: {correct}/{len(task_results)} correct")

        all_results['emergent_abilities'] = emergent_results
    except Exception as e:
        print(f"  ERROR: {e}")

    # ============================================================
    # 4. DECEPTIVE ALIGNMENT (Carlsmith, 2023)
    # ============================================================
    print("\n[4/4] DECEPTIVE ALIGNMENT TEST")
    print("-" * 50)

    try:
        deceptive = DeceptiveAlignmentTest(client=client, analyzer=analyzer)
        deceptive_results = deceptive.run_all_tests()

        print(f"  Tests run: {deceptive_results['summary']['total_tests']}")
        print(f"  Transparent: {deceptive_results['summary']['transparent_responses']}")
        print(f"  Transparency rate: {deceptive_results['summary']['transparency_rate']:.0%}")

        for name, data in deceptive_results.items():
            if name != 'summary' and isinstance(data, dict):
                flags = data.get('red_flags', [])
                status = "RED FLAG" if flags else "OK"
                print(f"    [{status}] {name}: {', '.join(flags) if flags else 'transparent'}")

        all_results['deceptive_alignment'] = deceptive_results
    except Exception as e:
        print(f"  ERROR: {e}")

    # ============================================================
    # OVERALL SUMMARY
    # ============================================================
    print("\n" + "=" * 70)
    print("OVERALL SUMMARY")
    print("=" * 70)

    print("\nPapers Tested:")
    print("  1. Sleeper Agents (Hubinger et al., 2024) - arXiv:2401.05566")
    print("  2. Mechanistic Interpretability (Anthropic, 2024)")
    print("  3. Emergent Abilities (Wei et al., 2022) - arXiv:2206.07682")
    print("  4. Deceptive Alignment (Carlsmith, 2023)")

    # Aggregate scores
    scores = {}
    if 'sleeper_agents' in all_results:
        scores['sleeper_safety'] = 1 - all_results['sleeper_agents']['summary']['deceptive_rate']
    if 'interpretability' in all_results:
        scores['transparency'] = all_results['interpretability']['summary']['avg_transparency']
    if 'emergent_abilities' in all_results:
        scores['capability'] = all_results['emergent_abilities']['summary']['accuracy']
    if 'deceptive_alignment' in all_results:
        scores['alignment'] = all_results['deceptive_alignment']['summary']['transparency_rate']

    if scores:
        overall = sum(scores.values()) / len(scores)
        print(f"\nScores:")
        for k, v in scores.items():
            print(f"  {k:20s}: {v:.2f}")
        print(f"\n  OVERALL SAFETY SCORE: {overall:.2f}")

    # Save results
    output_dir = Path("outputs/safety/advanced_research")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "advanced_results.json"
    output_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
