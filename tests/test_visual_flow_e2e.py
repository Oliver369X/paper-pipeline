"""E2E contra el mock estático visual-flow/index.html (sin red, sin Perplexity).

Requiere: pip install -e ".[e2e]" y playwright install chromium

Ejecutar solo estos tests: pytest tests/test_visual_flow_e2e.py -m e2e
O excluir E2E en CI sin Playwright: pytest -m "not e2e"

Vídeo de las pruebas (un .webm por test al cerrar la página):
  set PLAYWRIGHT_RECORD_VIDEO=1
  pytest tests/test_visual_flow_e2e.py -m e2e -q
  (salida: carpeta recordings/)
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

pytest.importorskip("playwright.sync_api")

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Browser, BrowserContext, Page, expect, sync_playwright

from paper_pipeline.visual_flow_playwright import visual_flow_file_url


def _wants_video() -> bool:
    return os.environ.get("PLAYWRIGHT_RECORD_VIDEO", "").strip().lower() in ("1", "true", "yes")


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(headless=True)
        except PlaywrightError as exc:
            pytest.skip(
                "Chromium de Playwright no instalado. Ejecuta: playwright install chromium\n"
                f"Detalle: {exc}",
            )
        yield b
        b.close()


@pytest.fixture(scope="module")
def browser_context(browser: Browser) -> BrowserContext:
    if _wants_video():
        root = Path(__file__).resolve().parents[1]
        out = root / "recordings"
        out.mkdir(parents=True, exist_ok=True)
        ctx = browser.new_context(
            record_video_dir=str(out),
            record_video_size={"width": 1280, "height": 720},
        )
    else:
        ctx = browser.new_context()
    yield ctx
    ctx.close()


@pytest.fixture
def page(browser_context: BrowserContext) -> Page:
    pg = browser_context.new_page()
    pg.set_default_timeout(60_000)
    pg.goto(visual_flow_file_url(), wait_until="domcontentloaded")
    yield pg
    pg.close()


@pytest.mark.e2e
def test_visual_flow_mock_loads_header(page: Page) -> None:
    assert "Paper pipeline" in page.title() or "pipeline" in page.title().lower()
    assert page.get_by_role("heading", level=1).count() >= 1


@pytest.mark.e2e
def test_e2e_pipeline_simulation_completes(page: Page) -> None:
    page.locator("#tab-pipeline").click()
    page.locator("#btn-sim").click()
    expect(page.locator("#step-indicator")).to_contain_text("Flujo completo", timeout=30_000)


@pytest.mark.e2e
def test_e2e_meta_simulation_completes(page: Page) -> None:
    page.locator("#tab-meta").click()
    page.locator("#btn-sim-meta").click()
    expect(page.locator("#meta-indicator")).to_contain_text("Ciclo meta completo", timeout=20_000)


@pytest.mark.e2e
def test_e2e_scenario_sprint_writes_log(page: Page) -> None:
    page.locator("#tab-escenarios").click()
    page.locator('[data-scenario="sprint"]').click()
    expect(page.locator("#demo-log")).to_contain_text("Escenario: sprint", timeout=30_000)


@pytest.mark.e2e
@pytest.mark.parametrize("scenario", ["meta2", "safe"])
def test_e2e_scenario_named_writes_log(page: Page, scenario: str) -> None:
    page.locator("#tab-escenarios").click()
    page.locator(f'[data-scenario="{scenario}"]').click()
    expect(page.locator("#demo-log")).to_contain_text(f"Escenario: {scenario}", timeout=30_000)
