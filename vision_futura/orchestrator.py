# ==============================================================================
# PUNTO 3: SkillOrchestrator — Mapeo Dinámico de Skills y MCPs por Fase
# Ubicación: paper_pipeline/skills/orchestrator.py
#
# PROBLEMA QUE RESUELVE:
#   Tienes 82+ skills instaladas y 7 servidores MCP activos. Si Cursor carga
#   todas a la vez, el contexto se satura y la calidad cae. El SkillOrchestrator
#   activa EXACTAMENTE las skills correctas en cada fase del pipeline —
#   ni una más, ni una menos.
#
# FILOSOFÍA:
#   Cada fase tiene un "modo mental" distinto. No usas el mismo modo para
#   brainstormar hipótesis que para debuggear un tensor NaN. El orquestador
#   modela esa diferencia y la fuerza estructuralmente.
# ==============================================================================

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import json
import logging
import subprocess

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# 1. Definición de Fases del Pipeline
# ------------------------------------------------------------------------------

class PipelinePhase(Enum):
    """
    Las fases del pipeline tienen modos cognitivos distintos.
    El orquestador elige el subconjunto de skills adecuado para cada una.
    """
    DOMAIN_ACQUISITION    = auto()  # Perplexity + Firecrawl: leer papers, construir DCA
    HYPOTHESIS_DESIGN     = auto()  # Brainstorming: diseñar qué probar y por qué
    IMPLEMENTATION_PLAN   = auto()  # Writing-plans: especificar la arquitectura de código
    CODE_GENERATION       = auto()  # TDD: escribir tests primero, implementar después
    DEBUGGING             = auto()  # Systematic-debugging: diagnóstico de raíz, no parches
    EVALUATION            = auto()  # Verification + TestSprite: correr benchmarks ciegos
    WEB_PACKAGING         = auto()  # Next.js + Vercel: construir la capa de visualización
    DOCUMENTATION         = auto()  # Knowledge-capture + GitHub: empaquetar para publicar
    HUMAN_REVIEW          = auto()  # Sin skills activas — el humano tiene el control total


# ------------------------------------------------------------------------------
# 2. Mapa de Skills por Fase
# ------------------------------------------------------------------------------

SKILL_PHASE_MAP: dict[PipelinePhase, list[str]] = {

    PipelinePhase.DOMAIN_ACQUISITION: [
        # MCP activos: perplexity-web, firecrawl-mcp, github
        # Skills activas: solo las de research
        "technical-research",         # Buscar papers y repos SOTA
        "hf-mcp",                     # Buscar modelos/datasets en HF Hub
        "hugging-face-paper-publisher", # Identificar papers relevantes en HF
        # NO activar: brainstorming, TDD, debugging — distorsionan el foco
    ],

    PipelinePhase.HYPOTHESIS_DESIGN: [
        # Modo: divergencia creativa controlada
        "brainstorming",              # Explorar múltiples hipótesis antes de elegir
        "writing-plans",              # Convertir hipótesis elegida en plan de implementación
        # NO activar: TDD ni debugging — no hay código aún que falle
    ],

    PipelinePhase.IMPLEMENTATION_PLAN: [
        # Modo: especificación técnica detallada
        "writing-plans",              # Plan multi-paso con dependencias explícitas
        "subagent-driven-development", # Dividir en tareas paralelas independientes
        "dispatching-parallel-agents", # Si hay partes independientes, delegarlas
        # NO activar: brainstorming — la dirección ya está elegida
    ],

    PipelinePhase.CODE_GENERATION: [
        # Modo: implementación estricta con TDD
        "test-driven-development",    # Test primero, implementación después — SIEMPRE
        "executing-plans",            # Seguir el plan de implementación línea por línea
        "supabase-postgres-best-practices",  # Si hay almacenamiento de resultados
        "hugging-face-model-trainer", # Si el experimento incluye fine-tuning
        "gradio",                     # Para la demo interactiva del resultado
        # NO activar: brainstorming, debugging — distraen del modo de implementación
    ],

    PipelinePhase.DEBUGGING: [
        # Modo: diagnóstico de causa raíz — NUNCA aplicar un parche sin entender
        "systematic-debugging",       # La más importante en esta fase
        "verification-before-completion", # No marcar como resuelto sin evidencia
        "receiving-code-review",      # Incorporar el error como feedback real
        # REGLA CRÍTICA: Si systematic-debugging falla 3 veces → llamar a Perplexity
        # como "Consultor Matemático". No seguir intentando a ciegas.
    ],

    PipelinePhase.EVALUATION: [
        # Modo: verificación rigurosa y sin trampa
        "verification-before-completion",  # Mandatorio antes de reportar cualquier número
        "hugging-face-evaluation",         # Tablas de comparación con SOTA
        "hugging-face-trackio",            # Logging de métricas para comparación
        # MCP activo en esta fase: TestSprite (evaluación automática)
        # CRÍTICO: el evaluador corre en directorio de solo lectura (anti-reward-hacking)
    ],

    PipelinePhase.WEB_PACKAGING: [
        # Modo: comunicación y visualización del resultado
        "nextjs",                     # App Router para la web del paper
        "vercel-cli",                 # Deploy automático
        "shadcn",                     # Componentes UI académicos
        "ai-elements",                # Si hay demo interactiva con el modelo
        "vercel-storage",             # Para guardar los pesos accesibles públicamente
        "gradio",                     # Demo interactiva del modelo en HF Spaces
        "hf-cli",                     # Subir modelo a HF Hub
        # MCP activo: vercel (deploy), playwright (verificar que la web carga bien)
    ],

    PipelinePhase.DOCUMENTATION: [
        # Modo: capturar y preservar el conocimiento generado
        "knowledge-capture",          # Convertir resultados en documentación Notion
        "tasks-explain-diff",         # Documentar los cambios de código relevantes
        "finishing-a-development-branch",  # Merge, PR, limpieza de ramas
        "using-git-worktrees",        # Cleanup de worktrees temporales
        # MCP activo: github (PR automático), notion (actualizar tablero)
    ],

    PipelinePhase.HUMAN_REVIEW: [
        # FASE SIN SKILLS — el humano tiene control total
        # El orquestador se detiene. No hay agente activo.
        # El audit notebook (Punto 2) está disponible para uso manual.
    ],
}


# ------------------------------------------------------------------------------
# 3. Mapa de MCPs por Fase (qué servidores activar/desactivar)
# ------------------------------------------------------------------------------

MCP_PHASE_MAP: dict[PipelinePhase, list[str]] = {
    PipelinePhase.DOMAIN_ACQUISITION:   ["perplexity-web", "firecrawl-mcp", "github"],
    PipelinePhase.HYPOTHESIS_DESIGN:    ["perplexity-web"],
    PipelinePhase.IMPLEMENTATION_PLAN:  ["github"],
    PipelinePhase.CODE_GENERATION:      ["github", "TestSprite"],
    PipelinePhase.DEBUGGING:            ["perplexity-web", "TestSprite"],
    PipelinePhase.EVALUATION:           ["TestSprite", "github"],
    PipelinePhase.WEB_PACKAGING:        ["plugin-vercel-vercel", "plugin-notion-workspace-notion", "playwright"],
    PipelinePhase.DOCUMENTATION:        ["github", "plugin-notion-workspace-notion"],
    PipelinePhase.HUMAN_REVIEW:         [],  # Ningún MCP activo
}


# ------------------------------------------------------------------------------
# 4. El SkillOrchestrator
# ------------------------------------------------------------------------------

@dataclass
class OrchestratorContext:
    """Estado actual del pipeline para tomar decisiones de activación."""
    phase: PipelinePhase
    exp_id: str
    domain: str
    consecutive_debug_failures: int = 0
    has_gpu_requirement: bool = False
    is_colab_delegated: bool = False
    previous_phases: list[PipelinePhase] = field(default_factory=list)


class SkillOrchestrator:
    """
    Decide en tiempo de ejecución qué skills y MCPs activar en cada fase.

    Principio de mínimo privilegio:
      Un agente de código NO debe tener acceso a las skills de brainstorming
      durante la fase de debugging — reduce la calidad y aumenta el riesgo
      de que el agente "cambie de hipótesis" en lugar de encontrar el bug real.
    """

    def __init__(self, cursor_config_path: Path):
        self.config_path = cursor_config_path
        self._original_config: dict = {}

    def load_current_config(self) -> dict:
        """Lee la configuración actual de MCPs de Cursor."""
        if self.config_path.exists():
            with open(self.config_path, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get_active_skills(self, ctx: OrchestratorContext) -> list[str]:
        """
        Retorna la lista exacta de skills a activar para la fase actual.
        Aplica reglas especiales basadas en el estado del contexto.
        """
        base_skills = SKILL_PHASE_MAP.get(ctx.phase, [])

        # REGLA ESPECIAL 1: Debugging prolongado → escalar a Perplexity
        if ctx.phase == PipelinePhase.DEBUGGING and ctx.consecutive_debug_failures >= 3:
            logger.warning(
                f"[{ctx.exp_id}] {ctx.consecutive_debug_failures} debug failures. "
                "Escalating to Perplexity Mathematical Consultant."
            )
            # Aquí el loop principal debe llamar a Perplexity con el stack trace
            return ["systematic-debugging", "verification-before-completion",
                    "__ESCALATE_TO_PERPLEXITY__"]  # Señal especial para el runner

        # REGLA ESPECIAL 2: Si hay delegación a Colab, añadir skill de agent-browser
        # para que Cursor pueda interactuar con la pestaña de Colab via MCP
        if ctx.is_colab_delegated and ctx.phase == PipelinePhase.CODE_GENERATION:
            base_skills = base_skills + ["agent-browser", "agent-browser-verify"]

        # REGLA ESPECIAL 3: Web packaging solo si hay resultado verificado
        if ctx.phase == PipelinePhase.WEB_PACKAGING:
            if PipelinePhase.EVALUATION not in ctx.previous_phases:
                logger.error(
                    f"[{ctx.exp_id}] Attempted WEB_PACKAGING without prior EVALUATION. "
                    "Blocking: cannot publish unverified results."
                )
                return []  # Bloqueado — no se puede empaquetar sin verificar

        return base_skills

    def get_active_mcps(self, ctx: OrchestratorContext) -> list[str]:
        """Retorna los servidores MCP a habilitar en la fase actual."""
        mcps = MCP_PHASE_MAP.get(ctx.phase, [])

        # Si se delegó a Colab, siempre incluir el MCP de Colab
        # (ya integrado en Cursor según la descripción del usuario)
        if ctx.is_colab_delegated:
            if "colab-mcp" not in mcps:
                mcps = mcps + ["colab-mcp"]

        return mcps

    def build_cursor_agent_command(self, ctx: OrchestratorContext,
                                    system_prompt: str, task: str) -> list[str]:
        """
        Construye el comando completo de Cursor CLI para una fase específica.
        Incluye las skills y MCPs exactos para esa fase.

        Ejemplo de output:
          cursor agent \
            --skills "test-driven-development,executing-plans" \
            --mcps "github,TestSprite" \
            -p "SYSTEM_PROMPT" \
            "TASK_DESCRIPTION"
        """
        active_skills = self.get_active_skills(ctx)
        active_mcps = self.get_active_mcps(ctx)

        # Filtrar señales especiales antes de pasar al CLI
        cli_skills = [s for s in active_skills if not s.startswith("__")]

        skills_str = ",".join(cli_skills)
        mcps_str = ",".join(active_mcps)

        cmd = [
            "cursor", "agent",
            "--skills", skills_str,
            "--mcps", mcps_str,
            "-p", system_prompt,
            task
        ]

        logger.info(f"[{ctx.exp_id}] Phase: {ctx.phase.name}")
        logger.info(f"[{ctx.exp_id}] Active skills ({len(cli_skills)}): {skills_str}")
        logger.info(f"[{ctx.exp_id}] Active MCPs ({len(active_mcps)}): {mcps_str}")

        return cmd

    def transition_to_phase(self, ctx: OrchestratorContext,
                             new_phase: PipelinePhase) -> OrchestratorContext:
        """
        Transiciona el contexto a una nueva fase.
        Registra el historial de fases para aplicar reglas de bloqueo.
        """
        logger.info(f"[{ctx.exp_id}] Phase transition: {ctx.phase.name} → {new_phase.name}")
        return OrchestratorContext(
            phase=new_phase,
            exp_id=ctx.exp_id,
            domain=ctx.domain,
            consecutive_debug_failures=ctx.consecutive_debug_failures,
            has_gpu_requirement=ctx.has_gpu_requirement,
            is_colab_delegated=ctx.is_colab_delegated,
            previous_phases=ctx.previous_phases + [ctx.phase]
        )
