"""EpistemicInjector -- build a Domain Context Artifact from live Perplexity research."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Union

from perplexity_webui_scraper import ClientConfig, ConversationConfig, Perplexity

from paper_pipeline.epistemic.models import DomainContextArtifact
from paper_pipeline.epistemic.persistence import save_domain_context_yaml
from paper_pipeline.epistemic.queries import (
    QUERY_COMPUTE,
    QUERY_PITFALLS,
    QUERY_REPOS,
    QUERY_SOTA,
    extract_bullet_items,
    extract_urls,
    generate_poison_pills,
    parse_compute,
    parse_pitfalls,
    parse_repos,
)

logger = logging.getLogger(__name__)


class EpistemicInjector:
    """Orchestrate Perplexity research calls and build a Domain Context Artifact."""

    def __init__(
        self,
        perplexity: Union[Perplexity, str],
        output_dir: Path,
        *,
        model: str = "best",
        language: str = "en-US",
    ) -> None:
        if isinstance(perplexity, str):
            self._client = Perplexity(perplexity, config=ClientConfig())
            self._owns_client = True
        else:
            self._client = perplexity
            self._owns_client = False

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._model = model
        self._language = language

    def build_domain_context(
        self,
        topic: str,
        venue_target: str = "arXiv",
    ) -> DomainContextArtifact:
        logger.info("Building DCA for topic=%r venue=%r", topic, venue_target)

        raw_sota = self._ask(QUERY_SOTA.format(topic=topic, venue=venue_target))
        raw_pitfalls = self._ask(QUERY_PITFALLS.format(topic=topic))
        raw_repos = self._ask(QUERY_REPOS.format(topic=topic))
        raw_compute = self._ask(QUERY_COMPUTE.format(topic=topic))

        sota_techniques = extract_bullet_items(raw_sota)[:15]
        sources = extract_urls(raw_sota) + extract_urls(raw_repos)

        known_pitfalls = parse_pitfalls(raw_pitfalls)
        reference_implementations = parse_repos(raw_repos)
        compute_requirements = parse_compute(raw_compute)
        poison_pills = generate_poison_pills(topic)

        dca = DomainContextArtifact(
            topic=topic,
            venue_target=venue_target,
            sota_techniques=sota_techniques,
            mathematical_constraints=[],
            known_pitfalls=known_pitfalls,
            reference_implementations=reference_implementations,
            compute_requirements=compute_requirements,
            poison_pills=poison_pills,
            perplexity_sources=list(dict.fromkeys(sources)),
            generation_timestamp=datetime.now(UTC).isoformat(),
            raw_sota_papers_text=raw_sota,
            raw_pitfalls_text=raw_pitfalls,
            raw_repos_text=raw_repos,
            raw_compute_text=raw_compute,
        )

        save_domain_context_yaml(dca, self.output_dir)
        logger.info("DCA saved to %s", self.output_dir / "domain_context.yaml")
        return dca

    def generate_cursor_system_prompt(self, dca: DomainContextArtifact) -> str:
        techniques_block = "\n".join(f"  - {t}" for t in dca.sota_techniques) or "  (none extracted)"

        pitfalls_block = "\n".join(
            f"  - PITFALL: {p.description}\n"
            f"    SYMPTOM: {p.symptom}\n"
            f"    FIX: {p.fix}"
            for p in dca.known_pitfalls
        ) or "  (none extracted)"

        refs_block = "\n".join(
            f"  - {r.name} ({r.github_url})\n"
            f"    KEY DECISIONS: {', '.join(r.key_design_decisions[:3]) or 'N/A'}\n"
            f"    DO NOT COPY: {', '.join(r.what_not_to_copy[:3]) or 'N/A'}"
            for r in dca.reference_implementations
        ) or "  (none extracted)"

        pills_block = "\n".join(
            f"  - NEVER accept as true: '{pp.false_claim}'" for pp in dca.poison_pills
        ) or "  (none)"

        colab_section = ""
        cr = dca.compute_requirements
        if cr.delegate_to_colab:
            colab_section = (
                f"\n## COMPUTE DELEGATION (MANDATORY)\n"
                f"The experiment requires ~{cr.estimated_gpu_memory_gb:.1f} GB GPU memory.\n"
                f"YOU MUST delegate GPU-intensive work to Colab MCP "
                f"({cr.colab_accelerator} accelerator).\n"
                f"DO NOT attempt to run GPU-intensive code locally.\n"
            )

        constraints_block = "\n".join(
            f"  - [{mc.verification_method}] {mc.formula}  -- {mc.plain_english}"
            for mc in dca.mathematical_constraints
        ) or "  (to be populated during implementation)"

        return (
            "# EPISTEMIC OVERRIDE -- READ BEFORE WRITING ANY CODE\n"
            "\n"
            "Your pre-training knowledge is OUTDATED and UNRELIABLE for this domain.\n"
            "You are PROHIBITED from using your base training weights as a source of facts.\n"
            "Your ONLY source of truth is this Domain Context Artifact (DCA).\n"
            "\n"
            f"## DOMAIN\n"
            f"Topic: {dca.topic}\n"
            f"Target venue: {dca.venue_target}\n"
            f"DCA generated: {dca.generation_timestamp}\n"
            f"DCA version: {dca.dca_version}\n"
            "\n"
            f"## CURRENT STATE OF THE ART (verified via Perplexity)\n"
            f"{techniques_block}\n"
            "\n"
            f"## KNOWN IMPLEMENTATION PITFALLS\n"
            f"{pitfalls_block}\n"
            "\n"
            f"## REFERENCE IMPLEMENTATIONS\n"
            f"{refs_block}\n"
            "\n"
            f"## MATHEMATICAL CONSTRAINTS\n"
            f"{constraints_block}\n"
            "\n"
            f"## ANTI-HALLUCINATION GUARDS (CRITICAL)\n"
            f"The following claims are FALSE. If your code or reasoning relies on them,\n"
            f"STOP immediately and recheck against the DCA.\n"
            f"{pills_block}\n"
            f"{colab_section}\n"
            "## QUALITY GATES (non-negotiable)\n"
            "1. Every function must have a unit test (mocked tensors, no GPU required).\n"
            "2. The main evaluation script MUST save results to ./outputs/metrics.json.\n"
            "3. A FAILURES.md file must document what DID NOT work and why.\n"
            "\n"
            f"You are now the world-leading expert in: {dca.topic}.\n"
            "Act accordingly.\n"
        )

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def _ask(self, query: str) -> str:
        cfg = ConversationConfig(
            model=self._model,
            citation_mode="markdown",
            language=self._language,
            save_to_library=True,
        )
        conversation = self._client.create_conversation(cfg)
        logger.info("Perplexity ask: %s...", query[:80])
        conversation.ask(query)
        answer: str = conversation.answer or ""
        return answer
