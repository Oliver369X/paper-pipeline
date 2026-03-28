# ==============================================================================
# PUNTO 5: Bucle de Debugging Matemático Asistido por Perplexity
# Ubicación: paper_pipeline/debug/math_debugger.py
#
# PROBLEMA QUE RESUELVE:
#   Cursor es un buen ingeniero de software, pero cuando el bug es matemático
#   (tensor dimensions, gradientes que explotan, SAE con feature collapse,
#   pérdida que va a NaN por inestabilidad numérica), Cursor tiende a aplicar
#   parches superficiales: añadir un `clamp()`, un `try/except`, o simplemente
#   declarar que el test "no aplica". Eso es peor que el bug original.
#
# SOLUCIÓN:
#   Tras 3 fallos de Cursor en la misma función/módulo, el control se transfiere
#   a Perplexity como "Consultor Matemático". Perplexity lee:
#     1. El stack trace completo
#     2. Las ecuaciones del DCA que Cursor debería implementar
#     3. Los papers originales relevantes via Firecrawl
#   Y devuelve un DIAGNÓSTICO MATEMÁTICO con la solución arquitectónica exacta
#   — no un parche de código, sino la corrección teórica que hace el parche
#   correcto inevitablemente.
#
# ESCALACIÓN:
#   Si Perplexity tampoco resuelve en 2 intentos → HUMAN_REVIEW obligatorio.
#   El humano recibe un briefing técnico completo, no un log crudo.
# ==============================================================================

from __future__ import annotations

import re
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from enum import Enum, auto

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# 1. Clasificador de Errores Matemáticos
#    Antes de llamar a Perplexity, categorizar el error para hacer la
#    consulta más precisa y evitar respuestas genéricas.
# ------------------------------------------------------------------------------

class MathErrorClass(Enum):
    """
    Clasificación de errores matemáticos comunes en proyectos de ML/investigación.
    Cada clase tiene un prompt de diagnóstico especializado.
    """
    NAN_LOSS              = auto()  # loss → NaN durante training
    GRADIENT_EXPLOSION    = auto()  # ||grad|| → ∞, weights divergen
    GRADIENT_VANISHING    = auto()  # ||grad|| → 0, red no aprende
    TENSOR_SHAPE_MISMATCH = auto()  # RuntimeError: shape [A,B] != [C,D]
    FEATURE_COLLAPSE      = auto()  # SAEs: todos los features muertos
    NUMERICAL_INSTABILITY = auto()  # overflow/underflow en softmax, log, exp
    CONVERGENCE_FAILURE   = auto()  # El modelo no converge tras N epochs
    METRIC_INCONSISTENCY  = auto()  # accuracy > 1.0, probabilidades no suman 1
    CUDA_OOM              = auto()  # CUDA Out of Memory
    UNKNOWN               = auto()  # No clasificado — consulta abierta


@dataclass
class DebugTrace:
    """
    El paquete completo de información que se envía a Perplexity.
    Construido por el DebugContextCollector desde los artefactos del worktree.
    """
    exp_id: str
    error_class: MathErrorClass
    raw_stack_trace: str
    failing_function_code: str        # Solo la función que falla, no el archivo completo
    relevant_dca_equations: list[str] # Las ecuaciones del DCA relacionadas con el fallo
    cursor_attempted_fixes: list[str] # Qué intentó Cursor (para no repetir)
    test_name: str
    n_consecutive_failures: int


@dataclass
class MathDiagnosis:
    """
    La respuesta de Perplexity al DebugTrace.
    Contiene el análisis teórico, la corrección arquitectónica y
    las referencias al paper original donde está la solución.
    """
    root_cause_theory: str            # Por qué matemáticamente está fallando
    architectural_fix: str            # La corrección a nivel de diseño (no parche)
    corrected_code_snippet: str       # El fragmento de código corregido
    paper_references: list[str]       # Papers donde está documentada la solución
    confidence: str                   # "HIGH", "MEDIUM", "LOW"
    requires_human_escalation: bool   # True si Perplexity no está seguro


# ------------------------------------------------------------------------------
# 2. Clasificador de Errores (pattern matching sobre stack traces)
# ------------------------------------------------------------------------------

class MathErrorClassifier:
    """
    Analiza el stack trace y classifica el tipo de error matemático.
    Esto permite hacer una consulta hiperespecializada a Perplexity.
    """

    # Patrones de texto que indican cada clase de error
    _PATTERNS: list[tuple[MathErrorClass, list[str]]] = [
        (MathErrorClass.NAN_LOSS, [
            "nan", "loss is nan", "loss became nan", "loss = nan"
        ]),
        (MathErrorClass.GRADIENT_EXPLOSION, [
            "exploding gradient", "grad norm", "overflow encountered in multiply",
            "inf in gradient", "loss is inf"
        ]),
        (MathErrorClass.GRADIENT_VANISHING, [
            "vanishing gradient", "grad is zero", "gradient is 0.000000"
        ]),
        (MathErrorClass.TENSOR_SHAPE_MISMATCH, [
            "runtimeerror: expected", "size mismatch", "shape mismatch",
            "mat1 and mat2 shapes cannot be multiplied",
            "expected input", "but got shape"
        ]),
        (MathErrorClass.FEATURE_COLLAPSE, [
            "dead features", "all features zero", "feature collapse",
            "dictionary collapse", "no active features"
        ]),
        (MathErrorClass.NUMERICAL_INSTABILITY, [
            "overflow encountered in exp", "divide by zero",
            "log of zero", "underflow", "invalid value in log"
        ]),
        (MathErrorClass.CUDA_OOM, [
            "cuda out of memory", "oom", "out of memory"
        ]),
        (MathErrorClass.METRIC_INCONSISTENCY, [
            "accuracy > 1", "probabilities do not sum", "invalid metric"
        ]),
    ]

    def classify(self, stack_trace: str) -> MathErrorClass:
        trace_lower = stack_trace.lower()
        for error_class, patterns in self._PATTERNS:
            if any(pattern in trace_lower for pattern in patterns):
                return error_class
        return MathErrorClass.UNKNOWN


# ------------------------------------------------------------------------------
# 3. Recolector de Contexto de Debug
# ------------------------------------------------------------------------------

class DebugContextCollector:
    """
    Extrae la información relevante del worktree para armar el DebugTrace.
    No envía todo el repositorio a Perplexity — solo lo estrictamente necesario.
    """

    def __init__(self, worktree_path: Path, dca_path: Path):
        self.worktree = worktree_path
        self.dca_path = dca_path
        self.classifier = MathErrorClassifier()

    def collect(self, test_name: str, stack_trace: str,
                cursor_fixes: list[str], n_failures: int) -> DebugTrace:
        exp_id = self.worktree.name.replace("wt_", "")

        # 1. Clasificar el error
        error_class = self.classifier.classify(stack_trace)
        logger.info(f"[{exp_id}] Error classified as: {error_class.name}")

        # 2. Extraer solo la función que falla (no el archivo completo)
        failing_code = self._extract_failing_function(stack_trace)

        # 3. Extraer las ecuaciones del DCA relevantes para este error
        dca_equations = self._extract_relevant_dca_equations(error_class)

        return DebugTrace(
            exp_id=exp_id,
            error_class=error_class,
            raw_stack_trace=stack_trace[:3000],  # Limitar tamaño
            failing_function_code=failing_code,
            relevant_dca_equations=dca_equations,
            cursor_attempted_fixes=cursor_fixes,
            test_name=test_name,
            n_consecutive_failures=n_failures
        )

    def _extract_failing_function(self, stack_trace: str) -> str:
        """
        Extrae el bloque de código de la función donde ocurrió el error.
        Busca el último frame del stack trace que pertenece a ./src/
        """
        lines = stack_trace.split("\n")
        src_lines = [l for l in lines if "./src/" in l or "File \"" in l]
        if not src_lines:
            return "Function not extractable from stack trace."

        # Intentar leer el archivo y función real
        last_src_line = src_lines[-1]
        file_match = re.search(r'File "(.+?)", line (\d+)', last_src_line)
        if not file_match:
            return last_src_line

        file_path = Path(file_match.group(1))
        line_num = int(file_match.group(2))

        if not file_path.exists():
            return last_src_line

        with open(file_path, encoding="utf-8") as f:
            all_lines = f.readlines()

        # Retornar 20 líneas alrededor del error
        start = max(0, line_num - 10)
        end = min(len(all_lines), line_num + 10)
        return "".join(all_lines[start:end])

    def _extract_relevant_dca_equations(self, error_class: MathErrorClass) -> list[str]:
        """
        Lee el domain_context.yaml y extrae las ecuaciones más relevantes
        para el tipo de error detectado.
        """
        if not self.dca_path.exists():
            return ["DCA not available — equations cannot be retrieved."]

        import yaml
        with open(self.dca_path, encoding="utf-8") as f:
            dca = yaml.safe_load(f)

        constraints = dca.get("mathematical_constraints", [])
        # Filtrar las restricciones cuya verificación es relevante para el error
        relevant = []
        for c in constraints:
            formula = c.get("formula", "")
            plain = c.get("plain_english", "")
            if error_class == MathErrorClass.NAN_LOSS and "loss" in plain.lower():
                relevant.append(f"{plain}: {formula}")
            elif error_class == MathErrorClass.TENSOR_SHAPE_MISMATCH and "shape" in plain.lower():
                relevant.append(f"{plain}: {formula}")
            elif error_class == MathErrorClass.FEATURE_COLLAPSE and "sparse" in plain.lower():
                relevant.append(f"{plain}: {formula}")

        return relevant if relevant else [c.get("formula", "") for c in constraints[:3]]


# ------------------------------------------------------------------------------
# 4. El Consultor Matemático (Perplexity como experto externo)
# ------------------------------------------------------------------------------

class PerplexityMathConsultant:
    """
    Llama a Perplexity con un prompt hiperespecializado para diagnosticar
    errores matemáticos que Cursor no pudo resolver.

    La diferencia clave vs un debug genérico:
    - No pedimos "arregla este bug"
    - Pedimos "explícanos la teoría matemática correcta para este error,
      citando el paper original, y luego danos el código que implementa
      esa teoría sin el error"
    """

    def __init__(self, perplexity_mcp_client):
        self.client = perplexity_mcp_client

    def _build_diagnostic_prompt(self, trace: DebugTrace) -> str:
        """
        Construye el prompt especializado según el tipo de error matemático.
        """
        base_context = f"""
You are a mathematical debugging consultant for ML research code.

EXPERIMENT: {trace.exp_id}
ERROR TYPE: {trace.error_class.name}
CONSECUTIVE FAILURES: {trace.n_consecutive_failures}
FAILING TEST: {trace.test_name}

CURSOR ALREADY TRIED (DO NOT SUGGEST THESE):
{chr(10).join(f"- {fix}" for fix in trace.cursor_attempted_fixes)}

RELEVANT MATHEMATICAL CONSTRAINTS FROM DOMAIN CONTEXT:
{chr(10).join(f"- {eq}" for eq in trace.relevant_dca_equations)}

FAILING CODE:
```python
{trace.failing_function_code}
```

STACK TRACE:
```
{trace.raw_stack_trace}
```
"""

        # Prompts especializados por tipo de error
        specialized_prompts = {
            MathErrorClass.NAN_LOSS: """
TASK: Diagnose this NaN loss mathematically.
1. What is the exact mathematical operation that produces NaN here?
   (Consider: log(0), 0/0, inf-inf, overflow in exp())
2. What does the original paper say about numerical stability for this formula?
   Cite the specific equation and paper section.
3. Provide the numerically stable implementation using log-sum-exp trick,
   epsilon clamping, or mixed precision — whichever the paper recommends.
4. Write the corrected Python/PyTorch code snippet.
""",
            MathErrorClass.TENSOR_SHAPE_MISMATCH: """
TASK: Diagnose this shape mismatch mathematically.
1. What are the correct tensor dimensions for this operation per the paper?
   Write them as: input=[batch, seq_len, d_model], weight=[d_model, d_ff]
2. What is the exact matrix multiplication or einsum that should be used?
3. Write the corrected einsum notation or reshape operations.
4. Provide the unit test assertion that would catch this permanently.
""",
            MathErrorClass.FEATURE_COLLAPSE: """
TASK: Diagnose this Sparse Autoencoder feature collapse mathematically.
1. What causes dead features during SAE training per Anthropic's 2023 paper?
   (Consider: L1 penalty too high, bad initialization, learning rate)
2. What is the recommended L1 coefficient schedule from the literature?
3. How should the decoder columns be initialized to prevent collapse?
4. Provide the corrected training loop with auxiliary loss for dead features.
""",
            MathErrorClass.GRADIENT_EXPLOSION: """
TASK: Diagnose this gradient explosion mathematically.
1. At which layer does the gradient norm exceed a safe threshold?
2. Should gradient clipping be applied, and if so, what is the correct
   theoretical threshold for this architecture (cite paper)?
3. Is the learning rate schedule compatible with this architecture?
4. Provide the corrected optimizer configuration with gradient clipping.
""",
        }

        specific = specialized_prompts.get(
            trace.error_class,
            "\nTASK: Identify the mathematical root cause of this error and provide "
            "the architecturally correct fix, citing the relevant paper."
        )

        return base_context + specific

    def diagnose(self, trace: DebugTrace) -> MathDiagnosis:
        """
        Envía el DebugTrace a Perplexity y parsea la respuesta en un MathDiagnosis.
        """
        prompt = self._build_diagnostic_prompt(trace)
        logger.info(f"[{trace.exp_id}] Consulting Perplexity Mathematical Consultant...")
        logger.info(f"[{trace.exp_id}] Error class: {trace.error_class.name}")

        raw_response = self.client.call("perplexity-web", query=prompt)

        # Parsear la respuesta de Perplexity
        response_text = raw_response if isinstance(raw_response, str) else str(raw_response)

        # Extraer bloque de código de la respuesta
        code_match = re.search(r"```python\n(.+?)```", response_text, re.DOTALL)
        corrected_code = code_match.group(1) if code_match else "No corrected code provided."

        # Extraer referencias a papers (patrones: arXiv, ICLR, NeurIPS)
        paper_refs = re.findall(
            r"(arXiv:\d{4}\.\d+|ICLR \d{4}|NeurIPS \d{4}|https://arxiv\.org/\S+)",
            response_text
        )

        # Evaluar confianza basada en si Perplexity citó papers
        confidence = "HIGH" if len(paper_refs) >= 2 else ("MEDIUM" if len(paper_refs) == 1 else "LOW")
        requires_human = confidence == "LOW" or "I'm not sure" in response_text

        if requires_human:
            logger.warning(f"[{trace.exp_id}] Low confidence diagnosis. Escalating to human.")

        return MathDiagnosis(
            root_cause_theory=response_text[:500],
            architectural_fix=response_text[500:1000] if len(response_text) > 500 else response_text,
            corrected_code_snippet=corrected_code,
            paper_references=paper_refs,
            confidence=confidence,
            requires_human_escalation=requires_human
        )


# ------------------------------------------------------------------------------
# 5. El Bucle Completo de Debugging
# ------------------------------------------------------------------------------

class MathDebuggingLoop:
    """
    Orquesta el bucle completo:
    Cursor intenta → falla → Cursor reintenta → falla × 3 → Perplexity diagnostica
    → Cursor implementa la corrección teórica → test corre → si falla × 2 → HUMAN_REVIEW

    Este bucle reemplaza el comportamiento por defecto de Cursor de aplicar
    parches indefinidamente sin entender la causa raíz.
    """

    CURSOR_MAX_ATTEMPTS = 3       # Intentos de Cursor antes de escalar
    PERPLEXITY_MAX_ATTEMPTS = 2   # Intentos de Perplexity antes de escalar a humano

    def __init__(self, context_collector: DebugContextCollector,
                 consultant: PerplexityMathConsultant,
                 notion_tracker=None):
        self.collector = context_collector
        self.consultant = consultant
        self.notion = notion_tracker
        self._cursor_attempts: dict[str, int] = {}  # test_name → n_attempts
        self._cursor_fixes_tried: dict[str, list[str]] = {}

    def record_cursor_failure(self, test_name: str, stack_trace: str, fix_attempted: str):
        """Llamar cada vez que Cursor reporta un fallo en un test."""
        self._cursor_attempts[test_name] = self._cursor_attempts.get(test_name, 0) + 1
        if test_name not in self._cursor_fixes_tried:
            self._cursor_fixes_tried[test_name] = []
        self._cursor_fixes_tried[test_name].append(fix_attempted)

        n = self._cursor_attempts[test_name]
        logger.info(f"Cursor failure #{n} on test '{test_name}'")

        if n >= self.CURSOR_MAX_ATTEMPTS:
            logger.warning(
                f"Test '{test_name}' has failed {n} times. "
                "Escalating to Perplexity Mathematical Consultant."
            )
            return True  # Señal: escalar
        return False

    def escalate_to_perplexity(self, test_name: str, stack_trace: str) -> MathDiagnosis:
        """
        Ejecuta la escalación a Perplexity.
        Retorna el diagnóstico con la corrección arquitectónica.
        """
        trace = self.collector.collect(
            test_name=test_name,
            stack_trace=stack_trace,
            cursor_fixes=self._cursor_fixes_tried.get(test_name, []),
            n_failures=self._cursor_attempts.get(test_name, 0)
        )

        diagnosis = self.consultant.diagnose(trace)

        if diagnosis.requires_human_escalation:
            self._generate_human_briefing(trace, diagnosis)

        return diagnosis

    def _generate_human_briefing(self, trace: DebugTrace, diagnosis: MathDiagnosis):
        """
        Genera un briefing técnico completo para el humano.
        NO es un log crudo — es un documento estructurado que explica
        exactamente qué se intentó, qué falló y qué necesita el humano para resolverlo.
        """
        briefing_path = Path(f"./outputs/human_briefing_{trace.exp_id}.md")
        content = f"""# 🚨 Escalación a Revisión Humana — Experimento {trace.exp_id}

## Resumen Ejecutivo
El experimento encontró un error matemático de tipo **{trace.error_class.name}**
que ni Cursor ({self.CURSOR_MAX_ATTEMPTS} intentos) ni Perplexity
({self.PERPLEXITY_MAX_ATTEMPTS} diagnósticos) pudieron resolver con alta confianza.

## El Error
```
{trace.raw_stack_trace[:1000]}
```

## Qué ya se intentó (NO repetir)
{chr(10).join(f"- {fix}" for fix in trace.cursor_attempted_fixes)}

## Diagnóstico de Perplexity (Confianza: {diagnosis.confidence})
**Causa raíz teórica:** {diagnosis.root_cause_theory}

**Corrección arquitectónica propuesta:**
{diagnosis.architectural_fix}

**Código sugerido:**
```python
{diagnosis.corrected_code_snippet}
```

**Referencias citadas:** {', '.join(diagnosis.paper_references) or 'Ninguna'}

## Tu Tarea como Investigador
1. Revisar el paper original en las referencias citadas arriba.
2. Verificar si la corrección propuesta es matemáticamente correcta.
3. Si lo es: aplicarla manualmente y correr `make test`.
4. Si no lo es: actualizar el DCA con la corrección correcta para que
   los próximos experimentos no cometan el mismo error.
5. Actualizar Notion con el hallazgo (esto es conocimiento valioso para el equipo).
"""
        briefing_path.parent.mkdir(parents=True, exist_ok=True)
        with open(briefing_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.critical(
            f"Human briefing generated: {briefing_path}\n"
            "THIS EXPERIMENT REQUIRES YOUR ATTENTION."
        )
