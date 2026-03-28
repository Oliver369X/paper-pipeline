"""
Plantilla para ``outputs/code/run_experiment.py`` (copiar a la misión o generar desde el Cerebro).

Contrato:
- Lee ``PAPER_OUTPUT_DIR`` (el pipeline lo define al ejecutar este script).
- Si hubo ``code_repo_url`` en la misión, ``PAPER_CODE_REPO_DIR`` apunta al clone en ``outputs/code/vendor_*``.
- Escribe ``$PAPER_OUTPUT_DIR/metrics.json`` con al menos ``schema_version`` y ``main`` si aplica.
"""

from __future__ import annotations

import json
import os
from pathlib import Path


def main() -> None:
    # os.environ["PAPER_CODE_REPO_DIR"] — si la misión definió code_repo_url (clone bajo outputs/code/vendor_*).
    out = Path(os.environ.get("PAPER_OUTPUT_DIR", "outputs")).resolve()
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "exit_code": 0,
        "main": 1.0,
        "experiment_runner": {
            "status": "ok",
            "profile": "user_script",
            "notes": "Reemplazá esto con tu entrenamiento/eval real.",
        },
    }
    (out / "metrics.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("Wrote", out / "metrics.json")


if __name__ == "__main__":
    main()
