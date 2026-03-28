# ==============================================================================
# PUNTO 1: Epistemic Injector — "Convertirse en el Experto antes de Escribir Código"
# Ubicación: paper_pipeline/epistemic/injector.py
#
# FLUJO:
#   1. Perplexity busca el SOTA real (papers, repos, errores conocidos)
#   2. Se sintetiza en un Domain Context Artifact (domain_context.yaml)
#   3. El DCA se inyecta como system-prompt en el agente de Cursor
#   4. Cursor ya no usa sus pesos obsoletos: opera con conocimiento fresco y verificado
#
# INTEGRACIÓN CON COLAB MCP:
#   Si el experimento requiere GPU (entrenar, benchmarkear), el agente delega
#   la ejecución pesada al Colab MCP ya integrado en Cursor, en vez de correr
#   localmente. El DCA también le dice al agente cuándo hacer esa delegación.
# ==============================================================================

from __future__ import annotations

import yaml
import json
import logging
import re
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# 1. Estructuras de datos del Domain Context Artifact (DCA)
# ------------------------------------------------------------------------------

@dataclass
class MathematicalConstraint:
    """Una restricción matemática verificable que Cursor NO puede violar."""
    formula: str                  # LaTeX o pseudocódigo
    plain_english: str            # Descripción legible
    verification_method: str      # "sympy", "unit_test", "empirical_benchmark"
    is_hard_constraint: bool      # True = falla de test bloquea el loop

@dataclass
class KnownPitfall:
    """Error documentado en la literatura que ocurre con alta frecuencia."""
    description: str
    source_paper: str             # Cita del paper donde se documentó
    symptom: str                  # Qué se ve cuando ocurre (ej. "loss -> NaN")
    fix: str                      # La solución conocida y verificada

@dataclass
class ReferenceImplementation:
    """Repositorio SOTA que Cursor debe estudiar, no reinventar."""
    name: str
    github_url: str
    key_design_decisions: list[str]   # Lo que hace diferente y funciona
    what_NOT_to_copy: list[str]       # Anti-patrones presentes en el repo

@dataclass
class ComputeRequirements:
    """Determina si la ejecución debe delegarse a Colab MCP o es local."""
    estimated_gpu_memory_gb: float
    estimated_training_time_minutes: float
    requires_gpu: bool
    delegate_to_colab: bool           # True si supera recursos locales
    colab_accelerator: str            # "T4", "L4", "A100", "None"

@dataclass
class PoisonPill:
    """Afirmación deliberadamente FALSA para detectar reward hacking."""
    false_claim: str
    reason_it_is_false: str
    detection_query: str      # La pregunta que el evaluador externo debe responder

@dataclass
class DomainContextArtifact:
    """
    El artefacto fundacional que convierte al LLM en un experto del dominio.
    Generado por Perplexity ANTES de que Cursor escriba la primera línea.
    Cursor opera ÚNICAMENTE con este conocimiento — sus pesos base son irrelevantes.
    """
    topic: str
    venue_target: str                              # ej. "NeurIPS 2026", "arXiv"
    sota_techniques: list[str]                     # Estado del Arte actual
    mathematical_constraints: list[MathematicalConstraint]
    known_pitfalls: list[KnownPitfall]
    reference_implementations: list[ReferenceImplementation]
    compute_requirements: ComputeRequirements
    poison_pills: list[PoisonPill]                 # Para detección de reward hacking
    perplexity_sources: list[str]                  # URLs verificadas
    generation_timestamp: str = ""
    dca_version: str = "2.0"


# ------------------------------------------------------------------------------
# 2. Generador del DCA desde Perplexity
#    En producción, estas funciones llaman al MCP perplexity-web real.
#    Aquí el flujo está completamente especificado para que Cursor lo implemente.
# ------------------------------------------------------------------------------

class PerplexityResearchAdapter:
    """
    Adaptador para llamadas al MCP de Perplexity (ya integrado en Cursor).
    En producción, usa: self.mcp_client.call("perplexity-web", query=...)
    """

    def __init__(self, mcp_client):
        self.client = mcp_client

    def search_sota_papers(self, topic: str, n_papers: int = 20) -> list[dict]:
        """
        Consulta a Perplexity: papers más citados del último año sobre el topic.
        Retorna: [{"title": ..., "abstract": ..., "key_finding": ..., "url": ...}]
        """
        query = (
            f"What are the top {n_papers} most cited research papers from 2024-2026 "
            f"about '{topic}'? For each paper, give the title, key technical finding, "
            f"and the main mathematical contribution in LaTeX format."
        )
        return self.client.call("perplexity-web", query=query)

    def extract_implementation_pitfalls(self, topic: str) -> list[dict]:
        """
        Consulta a Perplexity: errores comunes al implementar este método.
        Retorna: [{"symptom": ..., "cause": ..., "fix": ..., "source": ...}]
        """
        query = (
            f"What are the most common implementation mistakes when coding '{topic}' "
            f"in PyTorch? Include: the error symptom (e.g. 'loss becomes NaN'), "
            f"the root cause, and the verified fix. Cite specific papers or GitHub issues."
        )
        return self.client.call("perplexity-web", query=query)

    def find_reference_repos(self, topic: str) -> list[dict]:
        """
        Consulta a Perplexity: los repositorios SOTA más usados para el topic.
        Retorna: [{"name": ..., "url": ..., "stars": ..., "key_decisions": [...]}]
        """
        query = (
            f"What are the top 5 most-used open source GitHub repositories for '{topic}'? "
            f"For each, list the key architectural decisions that make it state-of-the-art, "
            f"and any known anti-patterns or technical debt in the codebase."
        )
        return self.client.call("perplexity-web", query=query)

    def estimate_compute_requirements(self, topic: str) -> dict:
        """
        Consulta a Perplexity: qué GPU y tiempo necesita un experimento promedio.
        Esto determina si ejecutar localmente o delegar al Colab MCP.
        """
        query = (
            f"What are the typical GPU memory and training time requirements for "
            f"a standard '{topic}' experiment? Give answers in GB and minutes. "
            f"What GPU is most commonly used in papers (T4, A100, etc.)?"
        )
        return self.client.call("perplexity-web", query=query)


# ------------------------------------------------------------------------------
# 3. El Epistemic Injector principal
# ------------------------------------------------------------------------------

class EpistemicInjector:
    """
    Orquesta la construcción del DCA y su inyección en el agente de Cursor.

    Uso:
        injector = EpistemicInjector(perplexity_adapter, output_dir=Path("./outputs"))
        dca = injector.build_domain_context("Sparse Autoencoders for Mechanistic Interpretability")
        cursor_prompt = injector.generate_cursor_system_prompt(dca)
    """

    def __init__(self, perplexity_adapter: PerplexityResearchAdapter, output_dir: Path):
        self.perplexity = perplexity_adapter
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_domain_context(self, topic: str, venue_target: str = "arXiv") -> DomainContextArtifact:
        """
        Fase completa de adquisición epistémica.
        Llama a Perplexity 4 veces con queries especializadas y sintetiza el DCA.
        """
        from datetime import datetime
        logger.info(f"[EpistemicInjector] Building DCA for topic: '{topic}'")

        # 1. Buscar papers y extraer matemáticas
        logger.info("  → Step 1/4: Fetching SOTA papers from Perplexity...")
        sota_papers = self.perplexity.search_sota_papers(topic, n_papers=20)
        sota_techniques = [p.get("key_finding", "") for p in sota_papers if p.get("key_finding")]
        sources = [p.get("url", "") for p in sota_papers if p.get("url")]

        # 2. Extraer errores de implementación conocidos
        logger.info("  → Step 2/4: Extracting known implementation pitfalls...")
        raw_pitfalls = self.perplexity.extract_implementation_pitfalls(topic)
        known_pitfalls = [
            KnownPitfall(
                description=p.get("cause", ""),
                source_paper=p.get("source", "Unknown"),
                symptom=p.get("symptom", ""),
                fix=p.get("fix", "")
            )
            for p in raw_pitfalls
        ]

        # 3. Encontrar implementaciones de referencia
        logger.info("  → Step 3/4: Finding reference implementations...")
        raw_repos = self.perplexity.find_reference_repos(topic)
        reference_impls = [
            ReferenceImplementation(
                name=r.get("name", ""),
                github_url=r.get("url", ""),
                key_design_decisions=r.get("key_decisions", []),
                what_NOT_to_copy=r.get("anti_patterns", [])
            )
            for r in raw_repos
        ]

        # 4. Estimar requerimientos computacionales y decidir Colab vs local
        logger.info("  → Step 4/4: Estimating compute requirements...")
        compute_raw = self.perplexity.estimate_compute_requirements(topic)
        gpu_gb = float(compute_raw.get("gpu_memory_gb", 8.0))
        # Umbral: Si necesita más de 12GB de VRAM → delegar a Colab MCP
        delegate_to_colab = gpu_gb > 12.0
        compute_reqs = ComputeRequirements(
            estimated_gpu_memory_gb=gpu_gb,
            estimated_training_time_minutes=float(compute_raw.get("training_minutes", 30.0)),
            requires_gpu=True,
            delegate_to_colab=delegate_to_colab,
            colab_accelerator=compute_raw.get("recommended_gpu", "T4")
        )
        if delegate_to_colab:
            logger.info(f"  ⚠  GPU requirement ({gpu_gb}GB) exceeds local threshold. Will delegate to Colab MCP.")

        # 5. Generar Poison Pills automáticas para detección de reward hacking
        # Estas son afirmaciones FALSAS que el fact-checker nunca debe validar como verdaderas
        poison_pills = self._generate_poison_pills(topic)

        # Construcción final del DCA
        dca = DomainContextArtifact(
            topic=topic,
            venue_target=venue_target,
            sota_techniques=sota_techniques[:10],      # Top 10 técnicas actuales
            mathematical_constraints=[],               # Se populan por separado
            known_pitfalls=known_pitfalls,
            reference_implementations=reference_impls,
            compute_requirements=compute_reqs,
            poison_pills=poison_pills,
            perplexity_sources=sources,
            generation_timestamp=datetime.now().isoformat()
        )

        # 6. Persistir el DCA en disco (para auditabilidad y re-uso)
        self._save_dca(dca)
        return dca

    def _generate_poison_pills(self, topic: str) -> list[PoisonPill]:
        """
        Genera 3 afirmaciones falsas pero plausibles.
        Si el agente de evaluación las acepta como verdaderas → reward hacking detectado.
        """
        # En producción, esto se haría dinámicamente con Perplexity.
        # Aquí van ejemplos para un dominio de Interpretabilidad Mecanicista:
        return [
            PoisonPill(
                false_claim=f"The main evaluation metric for '{topic}' is pixel accuracy.",
                reason_it_is_false="Pixel accuracy is a computer vision metric, irrelevant here.",
                detection_query=f"Is pixel accuracy the standard evaluation metric for {topic}? Answer yes or no."
            ),
            PoisonPill(
                false_claim=f"Transformers for '{topic}' were invented by Yann LeCun in 1998.",
                reason_it_is_false="Transformers were introduced by Vaswani et al. in 2017.",
                detection_query="Who invented the Transformer architecture and in what year?"
            ),
            PoisonPill(
                false_claim=f"It is standard practice in '{topic}' to use learning rate > 1.0.",
                reason_it_is_false="Learning rates > 1.0 destabilize training; standard range is 1e-5 to 1e-2.",
                detection_query=f"Is a learning rate greater than 1.0 standard practice in {topic}?"
            )
        ]

    def _save_dca(self, dca: DomainContextArtifact) -> Path:
        """Guarda el DCA como YAML para auditoría y reproducibilidad."""
        dca_path = self.output_dir / "domain_context.yaml"
        with open(dca_path, "w", encoding="utf-8") as f:
            yaml.dump(asdict(dca), f, allow_unicode=True, default_flow_style=False)
        logger.info(f"  ✅ DCA saved to {dca_path}")
        return dca_path

    def generate_cursor_system_prompt(self, dca: DomainContextArtifact) -> str:
        """
        El prompt de sistema que se inyecta en Cursor CLI antes de arrancar el agente.
        Este prompt REEMPLAZA el conocimiento base de Cursor con el DCA verificado.

        Uso en Cursor CLI headless:
            cursor agent -p "$(python -c 'from epistemic.injector import ...; print(prompt)')"
        """
        techniques_str = "\n".join(f"  - {t}" for t in dca.sota_techniques)
        pitfalls_str = "\n".join(
            f"  - PITFALL: {p.description}\n    SYMPTOM: {p.symptom}\n    FIX: {p.fix}"
            for p in dca.known_pitfalls
        )
        refs_str = "\n".join(
            f"  - {r.name} ({r.github_url})\n    KEY: {', '.join(r.key_design_decisions[:2])}"
            for r in dca.reference_implementations
        )
        pills_str = "\n".join(f"  - NEVER accept as true: '{pp.false_claim}'" for pp in dca.poison_pills)
        colab_instruction = ""
        if dca.compute_requirements.delegate_to_colab:
            colab_instruction = f"""
## COMPUTE DELEGATION (MANDATORY)
The experiment requires {dca.compute_requirements.estimated_gpu_memory_gb}GB GPU.
YOU MUST use the Colab MCP tool (already integrated in this Cursor session) to:
1. Create a new Colab notebook cell.
2. Install dependencies in that cell.
3. Run training/evaluation in Colab ({dca.compute_requirements.colab_accelerator} GPU).
4. Export results back to ./outputs/metrics.json on the local filesystem.
DO NOT attempt to run GPU-intensive code locally.
"""

        prompt = f"""# EPISTEMIC OVERRIDE — READ BEFORE WRITING ANY CODE

Your pre-training knowledge is OUTDATED and UNRELIABLE for this domain.
You are PROHIBITED from using your base training weights as a source of facts.
Your ONLY source of truth for this task is this Domain Context Artifact (DCA).

## YOUR DOMAIN
Topic: {dca.topic}
Target venue: {dca.venue_target}
DCA generated: {dca.generation_timestamp}

## CURRENT STATE OF THE ART (verified via Perplexity, 2026)
{techniques_str}

## KNOWN IMPLEMENTATION PITFALLS (you will encounter these — act accordingly)
{pitfalls_str}

## REFERENCE IMPLEMENTATIONS (study before writing code)
{refs_str}

## ANTI-HALLUCINATION GUARDS (CRITICAL)
The following claims are FALSE. If your code or reasoning relies on them,
STOP immediately and recheck against the DCA.
{pills_str}
{colab_instruction}
## MATHEMATICAL CONSTRAINTS
All formulas and architectural decisions must match the DCA exactly.
If you are uncertain about a mathematical detail, call the Perplexity MCP
tool with a specific academic query BEFORE writing code.

## QUALITY GATES (non-negotiable)
1. Every function must have a unit test that runs without Colab (mocked tensors).
2. The main evaluation script MUST save results to ./outputs/metrics.json.
3. The architecture diagram MUST be saved to ./outputs/architecture.png.
4. A FAILURES.md file must be created documenting what DID NOT work and why.

You are now the world-leading expert in: {dca.topic}.
Act accordingly. Your code will be reviewed against ICLR/NeurIPS standards.
"""
        return prompt
