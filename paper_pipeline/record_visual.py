"""Graba un vídeo (.webm) de la interfaz visual-flow con Playwright (estilo E2E con video).

Requisitos:
  pip install -e ".[e2e]"
  playwright install chromium

Uso:
  paper-record-visual
  paper-record-visual --headed
  paper-record-visual --out ./mis_grabaciones
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from paper_pipeline.visual_flow_playwright import visual_flow_file_url


def main() -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        print(
            "Falta Playwright. Instala: pip install -e \".[e2e]\" && playwright install chromium",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc

    parser = argparse.ArgumentParser(description="Graba la demo de visual-flow/index.html en vídeo.")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Carpeta para el vídeo (default: paper-pipeline/recordings)",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Mostrar el navegador mientras graba",
    )
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    try:
        url = visual_flow_file_url()
    except FileNotFoundError as exc:
        print(f"No se encuentra {exc}", file=sys.stderr)
        raise SystemExit(2)

    out_dir = args.out if args.out is not None else repo / "recordings"
    out_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        context = browser.new_context(
            record_video_dir=str(out_dir),
            record_video_size={"width": 1280, "height": 720},
        )
        page = context.new_page()
        page.set_default_timeout(60_000)

        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(800)

        page.locator("#tab-pipeline").click()
        page.wait_for_timeout(400)
        page.get_by_role("button", name="Simular flujo").click()
        page.wait_for_timeout(4500)

        page.locator("#tab-meta").click()
        page.wait_for_timeout(500)
        page.get_by_role("button", name="Simular ciclo meta").click()
        page.wait_for_timeout(6500)

        page.locator("#tab-escenarios").click()
        page.wait_for_timeout(600)
        for scenario in ("sprint", "meta2", "safe"):
            page.locator(f'[data-scenario="{scenario}"]').click()
            page.wait_for_timeout(9500)

        page.wait_for_timeout(500)
        context.close()
        browser.close()

    print(f"Vídeo guardado en: {out_dir.resolve()}")
    print("Busca un archivo .webm (nombre generado por Playwright).")


if __name__ == "__main__":
    main()
