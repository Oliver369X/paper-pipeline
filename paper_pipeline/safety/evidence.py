"""Evidence collection system for AI safety paper replication.

Provides comprehensive evidence collection, validation, and management
for safety evaluations with full traceability.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class EvidenceType(str, Enum):
    """Types of evidence."""

    BENCHMARK_RESULT = "benchmark_result"
    ATTACK_RESULT = "attack_result"
    METRIC = "metric"
    LOG = "log"
    SCREENSHOT = "screenshot"
    CODE = "code"
    DATA = "data"
    HUMAN_REVIEW = "human_review"


class EvidenceStatus(str, Enum):
    """Status of evidence."""

    COLLECTED = "collected"
    VALIDATED = "validated"
    VERIFIED = "verified"
    REJECTED = "rejected"


@dataclass
class Evidence:
    """A single piece of evidence."""

    id: str
    evidence_type: EvidenceType
    content: Any
    source: str
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    status: EvidenceStatus = EvidenceStatus.COLLECTED
    metadata: dict[str, Any] = field(default_factory=dict)
    hash_value: str = ""

    def __post_init__(self) -> None:
        if not self.hash_value:
            self.hash_value = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute hash of evidence content."""
        content_str = json.dumps(self.content, sort_keys=True, default=str)
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "evidence_type": self.evidence_type.value,
            "content": self.content,
            "source": self.source,
            "timestamp": self.timestamp,
            "status": self.status.value,
            "metadata": self.metadata,
            "hash": self.hash_value,
        }

    def validate(self) -> bool:
        """Validate evidence integrity."""
        computed_hash = self._compute_hash()
        if computed_hash != self.hash_value:
            logger.warning("Evidence hash mismatch for %s", self.id)
            return False
        self.status = EvidenceStatus.VALIDATED
        return True


@dataclass
class EvidenceChain:
    """Chain of evidence for traceability."""

    chain_id: str
    evidence: list[Evidence] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_evidence(self, evidence: Evidence) -> None:
        """Add evidence to the chain."""
        self.evidence.append(evidence)
        logger.debug("Added evidence %s to chain %s", evidence.id, self.chain_id)

    def verify_chain(self) -> bool:
        """Verify integrity of entire evidence chain."""
        for evidence in self.evidence:
            if not evidence.validate():
                return False
        return True

    def get_summary(self) -> dict[str, Any]:
        """Get summary of evidence chain."""
        type_counts = {}
        status_counts = {}
        for e in self.evidence:
            type_counts[e.evidence_type.value] = type_counts.get(e.evidence_type.value, 0) + 1
            status_counts[e.status.value] = status_counts.get(e.status.value, 0) + 1

        return {
            "chain_id": self.chain_id,
            "total_evidence": len(self.evidence),
            "by_type": type_counts,
            "by_status": status_counts,
            "created_at": self.created_at,
            "verified": self.verify_chain(),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "created_at": self.created_at,
            "metadata": self.metadata,
            "evidence": [e.to_dict() for e in self.evidence],
            "summary": self.get_summary(),
        }


class EvidenceCollector:
    """Collects and manages evidence for safety evaluations."""

    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = output_dir or Path("outputs/safety/evidence")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.chains: dict[str, EvidenceChain] = {}
        self._counter = 0

    def create_chain(self, chain_id: str, metadata: dict[str, Any] | None = None) -> EvidenceChain:
        """Create a new evidence chain."""
        chain = EvidenceChain(chain_id=chain_id, metadata=metadata or {})
        self.chains[chain_id] = chain
        return chain

    def add_benchmark_evidence(
        self,
        chain_id: str,
        benchmark_name: str,
        result: Any,
    ) -> Evidence:
        """Add benchmark result as evidence."""
        self._counter += 1
        evidence = Evidence(
            id=f"bench_{self._counter:04d}",
            evidence_type=EvidenceType.BENCHMARK_RESULT,
            content=result if isinstance(result, dict) else str(result),
            source=f"benchmark:{benchmark_name}",
            metadata={"benchmark": benchmark_name},
        )

        if chain_id in self.chains:
            self.chains[chain_id].add_evidence(evidence)

        return evidence

    def add_attack_evidence(
        self,
        chain_id: str,
        attack_type: str,
        result: Any,
    ) -> Evidence:
        """Add attack result as evidence."""
        self._counter += 1
        evidence = Evidence(
            id=f"attack_{self._counter:04d}",
            evidence_type=EvidenceType.ATTACK_RESULT,
            content=result if isinstance(result, dict) else str(result),
            source=f"attack:{attack_type}",
            metadata={"attack_type": attack_type},
        )

        if chain_id in self.chains:
            self.chains[chain_id].add_evidence(evidence)

        return evidence

    def add_metric_evidence(
        self,
        chain_id: str,
        metric_name: str,
        value: float,
        details: dict[str, Any] | None = None,
    ) -> Evidence:
        """Add metric as evidence."""
        self._counter += 1
        evidence = Evidence(
            id=f"metric_{self._counter:04d}",
            evidence_type=EvidenceType.METRIC,
            content={
                "metric": metric_name,
                "value": value,
                "details": details or {},
            },
            source=f"metric:{metric_name}",
            metadata={"metric": metric_name},
        )

        if chain_id in self.chains:
            self.chains[chain_id].add_evidence(evidence)

        return evidence

    def add_log_evidence(
        self,
        chain_id: str,
        log_entry: str,
        level: str = "info",
    ) -> Evidence:
        """Add log entry as evidence."""
        self._counter += 1
        evidence = Evidence(
            id=f"log_{self._counter:04d}",
            evidence_type=EvidenceType.LOG,
            content={
                "message": log_entry,
                "level": level,
            },
            source="system_log",
            metadata={"level": level},
        )

        if chain_id in self.chains:
            self.chains[chain_id].add_evidence(evidence)

        return evidence

    def add_code_evidence(
        self,
        chain_id: str,
        code: str,
        description: str,
    ) -> Evidence:
        """Add code snippet as evidence."""
        self._counter += 1
        evidence = Evidence(
            id=f"code_{self._counter:04d}",
            evidence_type=EvidenceType.CODE,
            content={
                "code": code,
                "description": description,
            },
            source="code_review",
            metadata={"language": "python"},
        )

        if chain_id in self.chains:
            self.chains[chain_id].add_evidence(evidence)

        return evidence

    def add_human_review_evidence(
        self,
        chain_id: str,
        reviewer: str,
        review: str,
        score: float,
    ) -> Evidence:
        """Add human review as evidence."""
        self._counter += 1
        evidence = Evidence(
            id=f"review_{self._counter:04d}",
            evidence_type=EvidenceType.HUMAN_REVIEW,
            content={
                "reviewer": reviewer,
                "review": review,
                "score": score,
            },
            source=f"human_review:{reviewer}",
            metadata={"reviewer": reviewer},
        )

        if chain_id in self.chains:
            self.chains[chain_id].add_evidence(evidence)

        return evidence

    def save_chain(self, chain_id: str) -> Path | None:
        """Save evidence chain to file."""
        if chain_id not in self.chains:
            logger.warning("Chain %s not found", chain_id)
            return None

        chain = self.chains[chain_id]
        output_path = self.output_dir / f"evidence_chain_{chain_id}.json"
        output_path.write_text(
            json.dumps(chain.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.info("Evidence chain saved to %s", output_path)
        return output_path

    def save_all_chains(self) -> list[Path]:
        """Save all evidence chains."""
        paths = []
        for chain_id in self.chains:
            path = self.save_chain(chain_id)
            if path:
                paths.append(path)
        return paths

    def load_chain(self, chain_id: str) -> EvidenceChain | None:
        """Load evidence chain from file."""
        input_path = self.output_dir / f"evidence_chain_{chain_id}.json"
        if not input_path.exists():
            logger.warning("Evidence chain file not found: %s", input_path)
            return None

        data = json.loads(input_path.read_text(encoding="utf-8"))
        chain = EvidenceChain(
            chain_id=data["chain_id"],
            metadata=data.get("metadata", {}),
        )

        for evidence_data in data.get("evidence", []):
            evidence = Evidence(
                id=evidence_data["id"],
                evidence_type=EvidenceType(evidence_data["evidence_type"]),
                content=evidence_data["content"],
                source=evidence_data["source"],
                timestamp=evidence_data["timestamp"],
                status=EvidenceStatus(evidence_data["status"]),
                metadata=evidence_data.get("metadata", {}),
                hash_value=evidence_data.get("hash", ""),
            )
            chain.add_evidence(evidence)

        self.chains[chain_id] = chain
        return chain

    def get_evidence_report(self) -> dict[str, Any]:
        """Generate comprehensive evidence report."""
        report = {
            "generated_at": datetime.now(UTC).isoformat(),
            "total_chains": len(self.chains),
            "chains": {},
        }

        for chain_id, chain in self.chains.items():
            report["chains"][chain_id] = chain.get_summary()

        return report


def create_evidence_collector(output_dir: Path | None = None) -> EvidenceCollector:
    """Create an evidence collector instance."""
    return EvidenceCollector(output_dir=output_dir)
