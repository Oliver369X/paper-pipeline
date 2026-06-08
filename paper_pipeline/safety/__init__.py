"""AI Safety module for paper replication.

Provides benchmarks, metrics, attacks, evaluation, evidence, and observability
for AI safety paper replication with maximum quality methodologies.
"""

from paper_pipeline.safety.benchmarks import SafetyBenchmark, HarmBenchBenchmark
from paper_pipeline.safety.metrics import SafetyMetrics, AttackSuccessRate, RefusalRate
from paper_pipeline.safety.attacks import AttackStrategy, JailbreakAttack
from paper_pipeline.safety.evaluator import SafetyEvaluator
from paper_pipeline.safety.evidence import EvidenceCollector
from paper_pipeline.safety.observability import SafetyTracer
from paper_pipeline.safety.auto_review import SafetyAutoReviewer
from paper_pipeline.safety.pair_attack import PAIRAttacker, PAIRConfig
from paper_pipeline.safety.benchmark_datasets import get_all_prompts, get_benchmark_summary
from paper_pipeline.safety.replication_pipeline import SafetyReplicationPipeline, ReplicationConfig
from paper_pipeline.safety.detectors import (
    ResponseAnalyzer,
    AnalysisResult,
    ResponseClassification,
    analyze_response,
    check_attack_success,
    is_refusal,
)
from paper_pipeline.safety.advanced_attacks import (
    PersonaModulationAttacker,
    AdaptiveAttack,
)
from paper_pipeline.safety.tap_attack import (
    TAPAttacker,
    TAPConfig,
    ArtPromptAttack,
    PromptEngineeringAttack,
)

__all__ = [
    # Benchmarks
    "SafetyBenchmark",
    "HarmBenchBenchmark",
    # Metrics
    "SafetyMetrics",
    "AttackSuccessRate",
    "RefusalRate",
    # Attacks
    "AttackStrategy",
    "JailbreakAttack",
    "PAIRAttacker",
    "PAIRConfig",
    "TAPAttacker",
    "TAPConfig",
    "ArtPromptAttack",
    "PromptEngineeringAttack",
    "PersonaModulationAttacker",
    "AdaptiveAttack",
    # Detectors
    "ResponseAnalyzer",
    "AnalysisResult",
    "ResponseClassification",
    "analyze_response",
    "check_attack_success",
    "is_refusal",
    # Evaluation
    "SafetyEvaluator",
    "EvidenceCollector",
    "SafetyTracer",
    "SafetyAutoReviewer",
    # Datasets
    "get_all_prompts",
    "get_benchmark_summary",
    # Pipeline
    "SafetyReplicationPipeline",
    "ReplicationConfig",
]
