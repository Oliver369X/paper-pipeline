# ==============================================================================
# PUNTO 4: Orquestador de Git Worktrees — Paralelismo Extremo sin Colisiones
# Ubicación: paper_pipeline/parallel/worktree_runner.py
#
# PROBLEMA QUE RESUELVE:
#   Múltiples agentes de Cursor trabajando sobre el mismo directorio crean:
#   - Git index.lock: dos procesos haciendo commit simultáneo → repo corrupto
#   - Sobreescritura de draft_paper.md / metrics.json → resultados mezclados
#   - Conflictos de Python imports si dos agentes modifican el mismo módulo
#
# SOLUCIÓN:
#   Git Worktrees: cada agente opera en su propio directorio físico aislado,
#   vinculado al mismo repositorio pero en una rama independiente.
#   Ningún agente puede pisar el trabajo de otro, físicamente imposible.
#
# RATE LIMITING:
#   50 agentes haciendo llamadas a Anthropic/Perplexity/GitHub simultáneamente
#   disparan código HTTP 429. Implementamos:
#   - asyncio.Semaphore: límite de concurrencia configurable
#   - Exponential Backoff: duplicar espera en cada 429 hasta max_retries
#   - Jitter aleatorio: evitar que todos los agentes reintenten exactamente
#     al mismo tiempo (efecto de "thundering herd")
# ==============================================================================

from __future__ import annotations

import asyncio
import subprocess
import random
import logging
import shutil
import json
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Callable, Awaitable
from enum import Enum, auto

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# 1. Configuración y estructuras de datos
# ------------------------------------------------------------------------------

@dataclass
class WorktreeConfig:
    """Parámetros de control del paralelismo."""
    max_concurrent_agents: int = 5       # Semáforo: máx agentes corriendo al mismo tiempo
    max_retries_on_rate_limit: int = 5   # Reintentos antes de declarar fallo permanente
    initial_backoff_seconds: float = 2.0 # Espera inicial ante un 429
    max_backoff_seconds: float = 120.0   # Techo del backoff exponencial (2 minutos)
    jitter_factor: float = 0.3           # ±30% de variación aleatoria en el backoff
    agent_timeout_seconds: int = 1800    # Timeout máximo por agente (30 minutos)
    keep_breakthrough_branches: bool = True  # No borrar las ramas de Nivel 3
    commit_after_each_phase: bool = True  # Git commit después de cada fase del pipeline


@dataclass
class AgentRunSpec:
    """Especificación completa de un agente a lanzar."""
    exp_id: str
    hypothesis: str
    branch_name: str = ""
    command: list[str] = field(default_factory=list)
    mission_md_content: str = ""
    tier_result: Optional[int] = None   # Asignado por el Hipervisor post-ejecución
    error_log: Optional[str] = None
    worktree_path: Optional[Path] = None
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0

    def __post_init__(self):
        if not self.branch_name:
            self.branch_name = f"exp/{self.exp_id}"


class AgentStatus(Enum):
    PENDING  = auto()
    RUNNING  = auto()
    SUCCESS  = auto()
    FAILED   = auto()
    RATE_LIMITED = auto()
    TIMEOUT  = auto()


# ------------------------------------------------------------------------------
# 2. El Rate Limiter con Backoff Exponencial y Jitter
# ------------------------------------------------------------------------------

class APIRateLimiter:
    """
    Gestiona los reintentos ante errores HTTP 429 de cualquier API.
    Usa backoff exponencial con jitter para evitar el efecto "thundering herd":
    todos los agentes NO reintentan al mismo nanosegundo.

    Ejemplo de secuencia de esperas para initial_backoff=2, jitter=0.3:
      Intento 1: espera 2s * (1 ± 0.3) = entre 1.4s y 2.6s
      Intento 2: espera 4s * (1 ± 0.3) = entre 2.8s y 5.2s
      Intento 3: espera 8s * (1 ± 0.3) = entre 5.6s y 10.4s
      Intento 4: espera 16s * jitter...
      Intento 5: espera min(32s, 120s) * jitter...
    """

    def __init__(self, config: WorktreeConfig):
        self.config = config

    def compute_wait_time(self, attempt: int) -> float:
        """
        Calcula el tiempo de espera para el intento N.
        attempt es 0-indexed (primer fallo = attempt 0).
        """
        base_wait = min(
            self.config.initial_backoff_seconds * (2 ** attempt),
            self.config.max_backoff_seconds
        )
        # Jitter: multiplicar por un valor aleatorio en [1-jitter, 1+jitter]
        jitter_multiplier = 1 + random.uniform(
            -self.config.jitter_factor,
            self.config.jitter_factor
        )
        return base_wait * jitter_multiplier

    async def execute_with_retry(
        self,
        exp_id: str,
        coro_factory: Callable[[], Awaitable],
        rate_limit_indicator: Callable[[Exception], bool]
    ):
        """
        Ejecuta una corutina con reintentos automáticos en caso de rate limit.

        Args:
            coro_factory: Función que crea una NUEVA corutina en cada intento
                         (las corutinas no se pueden reusar una vez consumidas)
            rate_limit_indicator: Función que determina si una excepción es un 429
        """
        for attempt in range(self.config.max_retries_on_rate_limit):
            try:
                return await coro_factory()

            except Exception as e:
                if not rate_limit_indicator(e):
                    # Error que no es rate-limit → relanzar inmediatamente
                    raise

                wait_time = self.compute_wait_time(attempt)
                logger.warning(
                    f"[{exp_id}] Rate limit hit (attempt {attempt + 1}/"
                    f"{self.config.max_retries_on_rate_limit}). "
                    f"Waiting {wait_time:.1f}s before retry..."
                )
                await asyncio.sleep(wait_time)

        raise RuntimeError(
            f"[{exp_id}] Max retries ({self.config.max_retries_on_rate_limit}) "
            "exceeded for rate-limited operation."
        )


# ------------------------------------------------------------------------------
# 3. El Git Worktree Manager
# ------------------------------------------------------------------------------

class GitWorktreeManager:
    """
    Abstrae las operaciones de Git Worktrees para el orquestador paralelo.

    Garantías:
    - La creación es atómica: si falla, no deja ramas huérfanas
    - La eliminación es segura: usa --force si hay archivos sin commit
    - El commit post-fase usa una cola para evitar index.lock
    """

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self._commit_queue: asyncio.Queue = asyncio.Queue()
        self._commit_worker_task: Optional[asyncio.Task] = None

    def start_commit_worker(self):
        """
        Lanza un worker de un solo hilo para serializar todos los commits.
        Esto previene el error 'fatal: Unable to create .git/index.lock'.
        """
        self._commit_worker_task = asyncio.create_task(self._commit_worker_loop())
        logger.info("Git commit worker started (single-threaded queue).")

    async def _commit_worker_loop(self):
        """Worker que procesa commits uno a la vez, sin concurrencia."""
        while True:
            worktree_path, branch, message, done_event = await self._commit_queue.get()
            try:
                subprocess.run(
                    ["git", "add", "-A"],
                    cwd=worktree_path, check=True, capture_output=True
                )
                subprocess.run(
                    ["git", "commit", "-m", message, "--allow-empty"],
                    cwd=worktree_path, check=True, capture_output=True
                )
                logger.info(f"[{branch}] Commit saved: '{message}'")
            except subprocess.CalledProcessError as e:
                logger.error(f"[{branch}] Commit failed: {e.stderr.decode()}")
            finally:
                done_event.set()
                self._commit_queue.task_done()

    async def commit_async(self, worktree_path: Path, branch: str, message: str):
        """
        Encola un commit y espera a que el worker lo procese.
        Llamar desde cualquier agente concurrente — el worker lo serializa.
        """
        done_event = asyncio.Event()
        await self._commit_queue.put((worktree_path, branch, message, done_event))
        await done_event.wait()

    async def create_worktree(self, spec: AgentRunSpec) -> Path:
        """
        Crea un Git Worktree aislado para el experimento.
        Si la rama ya existe (de una corrida anterior), la elimina primero.
        """
        worktree_path = self.repo_path.parent / f"wt_{spec.exp_id}"

        # Limpiar si ya existe de una corrida previa fallida
        if worktree_path.exists():
            logger.warning(f"[{spec.exp_id}] Stale worktree found, removing...")
            await self.remove_worktree(spec)

        try:
            subprocess.run(
                ["git", "worktree", "add", "-b", spec.branch_name, str(worktree_path), "main"],
                cwd=self.repo_path, check=True, capture_output=True
            )
            logger.info(f"[{spec.exp_id}] Worktree created at: {worktree_path}")
            return worktree_path

        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Failed to create worktree for {spec.exp_id}: {e.stderr.decode()}"
            )

    async def remove_worktree(self, spec: AgentRunSpec, keep_branch: bool = False):
        """
        Elimina el worktree físico. Por defecto también elimina la rama en Git.
        Si keep_branch=True (Tier 3 Breakthrough), preserva el historial.
        """
        worktree_path = self.repo_path.parent / f"wt_{spec.exp_id}"

        subprocess.run(
            ["git", "worktree", "remove", "--force", str(worktree_path)],
            cwd=self.repo_path, capture_output=True
        )

        if not keep_branch:
            subprocess.run(
                ["git", "branch", "-D", spec.branch_name],
                cwd=self.repo_path, capture_output=True
            )
            logger.info(f"[{spec.exp_id}] Worktree and branch removed.")
        else:
            logger.info(f"[{spec.exp_id}] Worktree removed. Branch preserved (Breakthrough).")

    def inject_mission(self, spec: AgentRunSpec, worktree_path: Path):
        """Escribe el mission.md específico del experimento en el worktree aislado."""
        mission_path = worktree_path / "mission.md"
        with open(mission_path, "w", encoding="utf-8") as f:
            f.write(spec.mission_md_content)


# ------------------------------------------------------------------------------
# 4. El Orquestador Paralelo Principal
# ------------------------------------------------------------------------------

class ParallelWorktreeOrchestrator:
    """
    Lanza múltiples agentes de Cursor en paralelo, cada uno en su propio
    directorio físico aislado (Git Worktree). Gestiona rate limits, timeouts
    y cleanup automático.

    Uso:
        orchestrator = ParallelWorktreeOrchestrator(
            repo_path=Path("./research_project"),
            config=WorktreeConfig(max_concurrent_agents=5)
        )
        results = await orchestrator.run_batch(experiments_list)
    """

    def __init__(self, repo_path: Path, config: WorktreeConfig = None):
        self.repo_path = repo_path
        self.config = config or WorktreeConfig()
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent_agents)
        self.git_manager = GitWorktreeManager(repo_path)
        self.rate_limiter = APIRateLimiter(self.config)
        self._active_agents: dict[str, AgentStatus] = {}

    async def run_single_agent(self, spec: AgentRunSpec) -> AgentRunSpec:
        """
        Ejecuta un agente completo en su worktree aislado.
        El semáforo garantiza que no más de N agentes corran simultáneamente.
        """
        async with self.semaphore:
            self._active_agents[spec.exp_id] = AgentStatus.RUNNING
            logger.info(
                f"[{spec.exp_id}] Starting agent. "
                f"Concurrent: {self.config.max_concurrent_agents - self.semaphore._value}/"
                f"{self.config.max_concurrent_agents}"
            )

            worktree_path = None
            try:
                # 1. Crear entorno aislado
                worktree_path = await self.git_manager.create_worktree(spec)
                spec.worktree_path = worktree_path
                self.git_manager.inject_mission(spec, worktree_path)

                # 2. Ejecutar el agente con timeout y retry en rate limits
                async def run_cursor_agent():
                    process = await asyncio.create_subprocess_exec(
                        *spec.command,
                        cwd=worktree_path,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=self.config.agent_timeout_seconds
                    )
                    if process.returncode != 0:
                        raise subprocess.CalledProcessError(
                            process.returncode, spec.command,
                            stderr=stderr
                        )
                    return stdout, stderr

                def is_rate_limit_error(e: Exception) -> bool:
                    """Detecta si el error es un HTTP 429 de cualquier API."""
                    error_str = str(e).lower()
                    return any(indicator in error_str for indicator in [
                        "429", "rate limit", "too many requests",
                        "quota exceeded", "resource exhausted"
                    ])

                stdout, stderr = await self.rate_limiter.execute_with_retry(
                    spec.exp_id,
                    run_cursor_agent,
                    is_rate_limit_error
                )

                # 3. Commit del estado final (serializado via queue)
                if self.config.commit_after_each_phase:
                    await self.git_manager.commit_async(
                        worktree_path, spec.branch_name,
                        f"exp({spec.exp_id}): completed run [{spec.hypothesis[:50]}]"
                    )

                spec.end_time = time.time()
                self._active_agents[spec.exp_id] = AgentStatus.SUCCESS
                logger.info(
                    f"[{spec.exp_id}] Agent completed in "
                    f"{spec.end_time - spec.start_time:.1f}s"
                )
                return spec

            except asyncio.TimeoutError:
                logger.error(f"[{spec.exp_id}] Agent timed out after {self.config.agent_timeout_seconds}s")
                spec.error_log = f"TIMEOUT after {self.config.agent_timeout_seconds}s"
                spec.tier_result = 0
                self._active_agents[spec.exp_id] = AgentStatus.TIMEOUT
                return spec

            except Exception as e:
                logger.error(f"[{spec.exp_id}] Agent failed: {e}")
                spec.error_log = str(e)
                spec.tier_result = 0
                self._active_agents[spec.exp_id] = AgentStatus.FAILED
                return spec

            finally:
                # Cleanup: siempre eliminar el worktree a menos que sea Tier 3
                if worktree_path and worktree_path.exists():
                    keep = (spec.tier_result == 3 and self.config.keep_breakthrough_branches)
                    await self.git_manager.remove_worktree(spec, keep_branch=keep)

    async def run_batch(self, experiments: list[AgentRunSpec]) -> list[AgentRunSpec]:
        """
        Lanza todos los experimentos en paralelo (respetando el semáforo).
        Retorna la lista completa de resultados cuando todos terminen.
        """
        # Iniciar el worker de commits (un solo hilo serializado)
        self.git_manager.start_commit_worker()

        total = len(experiments)
        logger.info(f"Starting batch of {total} experiments "
                    f"(max concurrent: {self.config.max_concurrent_agents})")

        tasks = [self.run_single_agent(spec) for spec in experiments]
        results = await asyncio.gather(*tasks, return_exceptions=False)

        # Resumen final
        status_counts = {}
        for r in results:
            status = self._active_agents.get(r.exp_id, AgentStatus.FAILED)
            status_counts[status.name] = status_counts.get(status.name, 0) + 1

        logger.info(f"Batch complete. Summary: {status_counts}")
        return results

    def print_live_dashboard(self):
        """
        Imprime en terminal el estado actual de los agentes activos.
        Útil para monitorear corridas largas.
        """
        lines = [f"\n{'='*50}", "LIVE AGENT DASHBOARD", f"{'='*50}"]
        for exp_id, status in self._active_agents.items():
            icon = {"RUNNING": "🔄", "SUCCESS": "✅", "FAILED": "❌",
                    "TIMEOUT": "⏰", "PENDING": "⏳", "RATE_LIMITED": "🔶"}.get(status.name, "?")
            lines.append(f"  {icon} {exp_id}: {status.name}")
        print("\n".join(lines))
