"""Advanced AI Safety Research Module.

Contains frameworks for:
- Sleeper Agents (Hubinger et al., 2024)
- Mechanistic Interpretability (Anthropic, 2024)
- Emergent Abilities (Wei et al., 2022)
"""

from paper_pipeline.safety.research.sleeper_agents import (
    SleeperAgentPipeline,
    SleeperConfig,
    BackdoorDatasetGenerator,
    create_sleeper_pipeline,
)
from paper_pipeline.safety.research.mechanistic_interpretability import (
    MechanisticAnalyzer,
    InterpretabilityConfig,
    SleeperDetector,
    create_interpretability_pipeline,
)
from paper_pipeline.safety.research.emergent_abilities import (
    EmergentAbilitiesEvaluator,
    EmergentConfig,
    BenchmarkSuite,
    create_emergent_abilities_pipeline,
)

__all__ = [
    # Sleeper Agents
    "SleeperAgentPipeline",
    "SleeperConfig",
    "BackdoorDatasetGenerator",
    "create_sleeper_pipeline",
    # Interpretability
    "MechanisticAnalyzer",
    "InterpretabilityConfig",
    "SleeperDetector",
    "create_interpretability_pipeline",
    # Emergent Abilities
    "EmergentAbilitiesEvaluator",
    "EmergentConfig",
    "BenchmarkSuite",
    "create_emergent_abilities_pipeline",
]
