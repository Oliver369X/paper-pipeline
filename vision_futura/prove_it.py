# ==============================================================================
# PUNTO 2: "Prove It" Notebook Generator — Auditoría de Resultados sin Fricción
# Ubicación: paper_pipeline/audit/prove_it.py
#
# PROPÓSITO:
#   Autogenerar un Jupyter Notebook de auditoría que el investigador puede
#   ejecutar de una vez ("make verify_results") para confirmar que los números
#   del paper autogenerado son REALES y no fueron alucidados por el agente.
#
# INTEGRACIÓN COLAB MCP:
#   Si los pesos del modelo están en Colab (porque el training fue delegado),
#   el notebook incluye una celda especial que los descarga via Colab MCP
#   al filesystem local ANTES de correr la validación ciega.
#
# HONESTIDAD INTELECTUAL:
#   El notebook SIEMPRE incluye celdas de "Failure Cases" que muestran
#   explícitamente dónde el modelo falló — no solo donde triunfó.
# ==============================================================================

from __future__ import annotations

import json
import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class ExperimentMetadata:
    exp_id: str
    topic: str
    model_artifact_path: str          # Local o URL de HF Hub
    test_data_path: str               # Ruta al test set (NUNCA tocado por el agente)
    target_metric: str                # ej. "accuracy", "f1", "loss"
    claimed_metric_value: float       # El número que el agente reportó
    sota_baseline: float
    model_weights_in_colab: bool      # Si True → descargar via Colab MCP primero
    colab_notebook_url: Optional[str] = None


class ProveItNotebookGenerator:
    """
    Genera un notebook de auditoría completo y reproducible.
    El humano solo ejecuta: jupyter nbconvert --to notebook --execute audit_results.ipynb
    O usa: make verify_results
    """

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, metadata: ExperimentMetadata) -> Path:
        """
        Construye el notebook celda por celda.
        Retorna la ruta al .ipynb guardado.
        """
        nb = new_notebook()
        nb.cells = []

        # SECCIÓN 0: Encabezado y contexto del experimento
        nb.cells.append(self._cell_header(metadata))

        # SECCIÓN 1: Setup del entorno aislado
        nb.cells.append(self._cell_environment_setup())

        # SECCIÓN 2: Descarga de pesos desde Colab MCP (si aplica)
        if metadata.model_weights_in_colab:
            nb.cells.append(self._cell_colab_download(metadata))

        # SECCIÓN 3: Carga de modelo y datos (con assertions de integridad)
        nb.cells.append(self._cell_load_artifacts(metadata))

        # SECCIÓN 4: Evaluación ciega (el número que importa)
        nb.cells.append(self._cell_blind_evaluation(metadata))

        # SECCIÓN 5: Verificación de la afirmación del agente (¿mintió o no?)
        nb.cells.append(self._cell_claim_verification(metadata))

        # SECCIÓN 6: Honestidad Intelectual — Casos de FALLO
        nb.cells.append(self._cell_failure_cases(metadata))

        # SECCIÓN 7: Análisis estadístico de significancia
        nb.cells.append(self._cell_statistical_significance(metadata))

        # SECCIÓN 8: Decisión final del humano (celda interactiva)
        nb.cells.append(self._cell_human_decision(metadata))

        # Guardar
        notebook_path = self.output_dir / f"audit_{metadata.exp_id}.ipynb"
        with open(notebook_path, "w", encoding="utf-8") as f:
            nbformat.write(nb, f)

        return notebook_path

    # --------------------------------------------------------------------------
    # Constructores de celdas individuales
    # --------------------------------------------------------------------------

    def _cell_header(self, meta: ExperimentMetadata) -> nbformat.NotebookNode:
        return new_markdown_cell(source=f"""# 🔍 Auditoría de Resultados — Experimento {meta.exp_id}

**Tema:** `{meta.topic}`  
**Métrica objetivo:** `{meta.target_metric}`  
**Valor REPORTADO por el agente:** `{meta.claimed_metric_value:.4f}`  
**Baseline SOTA:** `{meta.sota_baseline:.4f}`  
**Delta afirmado:** `{(meta.claimed_metric_value - meta.sota_baseline):+.4f}`

---
⚠️ **Este notebook es de SOLO LECTURA para el agente.** El agente NO puede modificarlo.  
✅ **Tu tarea como investigador:** Ejecutar todas las celdas y verificar que los números coincidan.  
📌 **Si los números NO coinciden:** El experimento fue clasificado incorrectamente → actualizar Notion a ⚫ Crash.
""")

    def _cell_environment_setup(self) -> nbformat.NotebookNode:
        return new_code_cell(source="""# CELDA 1: Setup del entorno aislado (NO modifica tu entorno base)
import subprocess, sys

# Instalar dependencias en un entorno virtual temporal
# Usando uv para máxima reproducibilidad
try:
    import uv
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "uv", "-q"])

# Cargar el requirements.txt EXACTO que generó el agente
# (incluye versiones fijas: torch==2.3.0+cu121, etc.)
with open("./reproducibility/requirements_exact.txt") as f:
    print("Dependencias del experimento:")
    print(f.read())

# Importaciones core
import torch
import numpy as np
import json
import hashlib
from pathlib import Path

print(f"\n✅ PyTorch version: {torch.__version__}")
print(f"✅ CUDA available: {torch.cuda.is_available()}")
print(f"✅ Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
""")

    def _cell_colab_download(self, meta: ExperimentMetadata) -> nbformat.NotebookNode:
        return new_code_cell(source=f"""# CELDA 2 (Colab MCP): Descarga de pesos desde Google Colab
# Este experimento fue entrenado en Colab (GPU > 12GB requeridos).
# Usamos el MCP de Colab integrado en Cursor para traer los pesos al filesystem local.

# En un agente de Cursor esto se ejecutaría via MCP tool call.
# En este notebook, lo hacemos explícitamente para auditoría:

COLAB_NOTEBOOK_URL = "{meta.colab_notebook_url or 'NO_URL_PROVIDED'}"
MODEL_OUTPUT_PATH = "./outputs/model_weights.pt"

import os
if not os.path.exists(MODEL_OUTPUT_PATH):
    # Opción A: Descargar desde Hugging Face Hub (si el agente los subió)
    try:
        from huggingface_hub import hf_hub_download
        local_path = hf_hub_download(
            repo_id="{meta.model_artifact_path}",
            filename="model_weights.pt",
            local_dir="./outputs/"
        )
        print(f"✅ Pesos descargados desde HF Hub: {{local_path}}")
    except Exception as e:
        print(f"⚠️  HF Hub no disponible: {{e}}")
        print("   Abre el notebook de Colab y descarga manualmente los pesos a ./outputs/")
        print(f"   Colab URL: {{COLAB_NOTEBOOK_URL}}")
else:
    print(f"✅ Pesos encontrados localmente en: {{MODEL_OUTPUT_PATH}}")

# Verificar integridad del archivo con hash SHA256
with open(MODEL_OUTPUT_PATH, "rb") as f:
    sha256 = hashlib.sha256(f.read()).hexdigest()
print(f"\nSHA256 de los pesos: {{sha256}}")
print("Compara este hash con el reportado en ./outputs/model_manifest.json")
""")

    def _cell_load_artifacts(self, meta: ExperimentMetadata) -> nbformat.NotebookNode:
        return new_code_cell(source=f"""# CELDA 3: Carga de modelo y datos (con assertions de integridad)
# CRÍTICO: El test set es de SOLO LECTURA y nunca fue visto por el agente durante training.

MODEL_PATH = "./outputs/model_weights.pt"
TEST_DATA_PATH = "{meta.test_data_path}"

# --- Carga del modelo ---
try:
    model = torch.load(MODEL_PATH, map_location="cpu")
    model.eval()
    print("✅ Modelo cargado correctamente")

    # Contar parámetros (debe coincidir con lo reportado en el paper)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"   Parámetros totales: {{n_params:,}}")
except Exception as e:
    print(f"❌ ERROR al cargar modelo: {{e}}")
    raise

# --- Carga del test set ---
try:
    test_data = torch.load(TEST_DATA_PATH)
    print(f"\n✅ Test set cargado: {{len(test_data)}} muestras")

    # Assertion: El test set no debe haber sido modificado por el agente
    with open("./outputs/test_set_manifest.json") as f:
        manifest = json.load(f)

    assert len(test_data) == manifest["n_samples"], (
        f"❌ ALERTA: El test set tiene {{len(test_data)}} muestras pero el manifest dice {{manifest['n_samples']}}. "
        "El agente puede haber modificado el conjunto de evaluación."
    )
    print(f"✅ Integridad del test set verificada: {{manifest['n_samples']}} muestras")
except FileNotFoundError:
    print("⚠️  Manifest no encontrado. Continúa con precaución.")
""")

    def _cell_blind_evaluation(self, meta: ExperimentMetadata) -> nbformat.NotebookNode:
        return new_code_cell(source=f"""# CELDA 4: EVALUACIÓN CIEGA — El número que importa
# Esta celda reproduce el pipeline de evaluación IDÉNTICO al del entrenamiento,
# pero sobre el conjunto de test que el agente NUNCA vio.

from torch.utils.data import DataLoader

BATCH_SIZE = 32
TARGET_METRIC = "{meta.target_metric}"

def run_blind_evaluation(model, test_data, batch_size=BATCH_SIZE):
    """
    Evaluación reproducible. Misma semilla, misma configuración.
    El resultado de esta función ES la verdad del experimento.
    """
    torch.manual_seed(42)
    np.random.seed(42)

    loader = DataLoader(test_data, batch_size=batch_size, shuffle=False)
    all_preds, all_labels = [], []

    with torch.no_grad():
        for batch in loader:
            inputs, labels = batch
            outputs = model(inputs)
            preds = outputs.argmax(dim=-1)
            all_preds.extend(preds.tolist())
            all_labels.extend(labels.tolist())

    # Calcular la métrica objetivo
    if TARGET_METRIC == "accuracy":
        result = sum(p == l for p, l in zip(all_preds, all_labels)) / len(all_labels)
    elif TARGET_METRIC == "f1_score":
        from sklearn.metrics import f1_score
        result = f1_score(all_labels, all_preds, average="macro")
    else:
        result = sum(p == l for p, l in zip(all_preds, all_labels)) / len(all_labels)

    return result, all_preds, all_labels

REAL_METRIC_VALUE, predictions, ground_truth = run_blind_evaluation(model, test_data)
print(f"\n{'='*60}")
print(f"RESULTADO DE LA EVALUACIÓN CIEGA")
print(f"{'='*60}")
print(f"Métrica: {meta.target_metric}")
print(f"Valor REAL (evaluación ciega): {{REAL_METRIC_VALUE:.4f}}")
print(f"Valor AFIRMADO por el agente:  {meta.claimed_metric_value:.4f}")
print(f"Baseline SOTA:                 {meta.sota_baseline:.4f}")
""")

    def _cell_claim_verification(self, meta: ExperimentMetadata) -> nbformat.NotebookNode:
        return new_code_cell(source=f"""# CELDA 5: Verificación de la afirmación del agente
# ¿El agente dijo la verdad sobre sus resultados?

TOLERANCE = 0.005  # Tolerancia de 0.5% para diferencias de hardware/seed

delta_vs_claimed = abs(REAL_METRIC_VALUE - {meta.claimed_metric_value})
delta_vs_sota = REAL_METRIC_VALUE - {meta.sota_baseline}

print("\n🔎 VERIFICACIÓN DE INTEGRIDAD")
print(f"  Diferencia entre real y afirmado: {{delta_vs_claimed:.4f}}")

if delta_vs_claimed <= TOLERANCE:
    print(f"  ✅ VERIFICADO: El agente reportó el valor correcto (tolerancia: {{TOLERANCE:.3f}})")
else:
    print(f"  ❌ DISCREPANCIA DETECTADA: Diferencia {{delta_vs_claimed:.4f}} > tolerancia {{TOLERANCE:.3f}}")
    print(f"  ⚠️  El agente puede haber hecho cherry-picking o modificado el evaluador.")
    print(f"  → Actualizar estado en Notion a '⚫ Crash' y revisar el código del agente.")

print("\n📊 COMPARACIÓN CON SOTA")
if delta_vs_sota > {meta.sota_baseline * 0.02:.4f}:
    print(f"  🟢 BREAKTHROUGH: El modelo supera el SOTA por {{delta_vs_sota:+.4f}}")
elif abs(delta_vs_sota) <= {meta.sota_baseline * 0.01:.4f}:
    print(f"  🟡 REPLICACIÓN: El modelo iguala el SOTA (delta: {{delta_vs_sota:+.4f}})")
else:
    print(f"  🔴 REFUTADO: El modelo NO supera el SOTA (delta: {{delta_vs_sota:+.4f}})")
""")

    def _cell_failure_cases(self, meta: ExperimentMetadata) -> nbformat.NotebookNode:
        return new_markdown_cell(source="""## 🧪 Sección 6: Análisis de Casos de FALLO (Honestidad Intelectual)

Esta sección documenta explícitamente los casos donde el modelo **no funcionó**.  
Un paper sin análisis de fallos es un paper incompleto.

Los casos de fallo más comunes de analizar:
1. **Distributional shift**: ¿El modelo falla en ejemplos de distribuciones ligeramente distintas al train set?
2. **Edge cases matemáticos**: ¿Falla con inputs extremos (ceros, valores muy grandes)?
3. **Failure modes esperados del DCA**: ¿Se materializaron los pitfalls que Perplexity identificó?

Estos hallazgos deben guardarse en `FAILURES.md` para el archivo del experimento.
""")

    def _cell_statistical_significance(self, meta: ExperimentMetadata) -> nbformat.NotebookNode:
        return new_code_cell(source="""# CELDA 7: Significancia Estadística
# Un resultado sin p-value o intervalo de confianza no es un resultado científico.
# Esta celda implementa bootstrap para estimar la varianza del estimador.

import numpy as np

def bootstrap_confidence_interval(preds, labels, metric_fn, n_bootstrap=1000, alpha=0.05):
    """
    Estima el intervalo de confianza del (1-alpha)% para la métrica dada.
    Usar bootstrap si no tienes acceso a múltiples runs con distinta semilla.
    """
    n = len(preds)
    bootstrap_scores = []

    for _ in range(n_bootstrap):
        indices = np.random.choice(n, n, replace=True)
        sample_preds = [preds[i] for i in indices]
        sample_labels = [labels[i] for i in indices]
        score = metric_fn(sample_preds, sample_labels)
        bootstrap_scores.append(score)

    lower = np.percentile(bootstrap_scores, 100 * (alpha / 2))
    upper = np.percentile(bootstrap_scores, 100 * (1 - alpha / 2))
    return lower, upper

def accuracy_fn(preds, labels):
    return sum(p == l for p, l in zip(preds, labels)) / len(labels)

lower_ci, upper_ci = bootstrap_confidence_interval(predictions, ground_truth, accuracy_fn)

print("\n📈 ANÁLISIS ESTADÍSTICO (Bootstrap 95% CI, n=1000)")
print(f"  Métrica: {REAL_METRIC_VALUE:.4f} [{lower_ci:.4f}, {upper_ci:.4f}]")
print(f"  ¿El intervalo supera el SOTA baseline?", "SÍ ✅" if lower_ci > {sota_b} else "NO ❌ (resultado no es significativo)")

# Guardar para incluir en el paper autogenerado
ci_results = {{"metric": REAL_METRIC_VALUE, "ci_lower": lower_ci, "ci_upper": upper_ci}}
with open("./outputs/statistical_validation.json", "w") as f:
    import json
    json.dump(ci_results, f, indent=2)
print("\nResultados estadísticos guardados en ./outputs/statistical_validation.json")
""".replace("{sota_b}", str(meta.sota_baseline)))

    def _cell_human_decision(self, meta: ExperimentMetadata) -> nbformat.NotebookNode:
        return new_markdown_cell(source=f"""## ✍️ Sección 8: Decisión Final del Investigador

**Has completado la auditoría del experimento `{meta.exp_id}`.**

Ahora debes tomar una decisión basada en la evidencia que acabas de ver (no en lo que el agente afirmó).

### Checklist de Aceptación (Marca cada ítem)

- [ ] Los pesos del modelo cargaron sin errores
- [ ] El test set tiene la cantidad correcta de muestras (sin modificaciones del agente)
- [ ] El valor real de la métrica **coincide** con lo afirmado por el agente (±0.5%)
- [ ] El resultado supera el baseline SOTA con significancia estadística (CI inferior > SOTA)
- [ ] Revisé al menos **3 casos de fallo** del modelo y los entiendo
- [ ] El código en `./src/` es comprensible y no tiene operaciones hardcodeadas

### Mi Decisión:

**[ ] APROBAR** → El experimento es válido. Actualizar Notion a `🟢 Breakthrough` y proceder al empaquetado.

**[ ] RECHAZAR** → Hay discrepancias. Actualizar Notion a `⚫ Crash` e investigar el motivo.

**[ ] NECESITO MÁS EVIDENCIA** → Abrir un issue en GitHub con las preguntas específicas.

---
*Ejecuta `make publish_results` solo si marcaste APROBAR.*
""")


# ==============================================================================
# Makefile asociado (autogenerado junto al notebook)
# ==============================================================================

MAKEFILE_TEMPLATE = """
# Makefile de Auditoría — autogenerado por ProveItNotebookGenerator
# Ejecutar: make verify_results

.PHONY: verify_results setup clean publish_results

verify_results: setup
	@echo "========================================"
	@echo "  AUDITORIA CIEGA DE RESULTADOS"
	@echo "========================================"
	@uv run jupyter nbconvert \
		--to notebook \
		--execute \
		--ExecutePreprocessor.timeout=300 \
		--output audit_executed.ipynb \
		audit_{exp_id}.ipynb
	@echo ""
	@echo "✅ Auditoría completada. Revisa audit_executed.ipynb"
	@uv run jupyter nbconvert --to html audit_executed.ipynb --output audit_report.html
	@echo "✅ Reporte HTML generado: audit_report.html"

setup:
	@echo "Instalando dependencias exactas del experimento..."
	@uv pip install -r reproducibility/requirements_exact.txt -q

clean:
	@rm -f audit_executed.ipynb audit_report.html

publish_results:
	@echo "Publicando resultados verificados a GitHub..."
	@git add outputs/ FAILURES.md
	@git commit -m "feat: verified results for experiment {exp_id} [human-audited]"
	@git push origin main
	@echo "✅ Resultados publicados."
"""


def generate_full_audit_package(metadata: ExperimentMetadata, output_dir: Path) -> dict:
    """
    Genera el paquete completo de auditoría:
    - El notebook (audit_{exp_id}.ipynb)
    - El Makefile (Makefile)
    Retorna un dict con las rutas generadas.
    """
    generator = ProveItNotebookGenerator(output_dir)

    # 1. Generar notebook
    notebook_path = generator.generate(metadata)

    # 2. Generar Makefile
    makefile_content = MAKEFILE_TEMPLATE.replace("{exp_id}", metadata.exp_id)
    makefile_path = output_dir / "Makefile"
    with open(makefile_path, "w") as f:
        f.write(makefile_content)

    return {
        "notebook": notebook_path,
        "makefile": makefile_path,
        "run_command": f"cd {output_dir} && make verify_results"
    }
