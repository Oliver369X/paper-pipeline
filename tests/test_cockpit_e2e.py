"""E2E: Cockpit React servido por FastAPI + assets estáticos.

Requiere:
  - ``pip install -e ".[e2e]"`` y ``playwright install chromium``
  - ``cd web && npm run build`` (carpeta ``web/dist`` con el SPA)

Sin ``web/dist`` los tests se saltan con mensaje explícito.

Ejecutar solo:
  pytest tests/test_cockpit_e2e.py -m cockpit_e2e -q
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("playwright.sync_api")

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Browser, Page, expect, sync_playwright

REPO_ROOT = Path(__file__).resolve().parents[1]
DIST_INDEX = REPO_ROOT / "web" / "dist" / "index.html"


def _free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = int(s.getsockname()[1])
    s.close()
    return port


def _wait_http_ok(url: str, timeout: float = 30.0) -> None:
    deadline = time.time() + timeout
    last: Exception | None = None
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=2)
            return
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            last = e
            time.sleep(0.25)
    msg = f"timeout waiting for {url}"
    if last:
        msg += f": {last}"
    raise AssertionError(msg)


def _post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read().decode("utf-8")
        return json.loads(body) if body else {}


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


@pytest.fixture
def page(browser: Browser) -> Page:
    ctx = browser.new_context()
    ctx.add_init_script(
        "localStorage.setItem('paper-web-onboarding-dismissed-v2', '1');",
    )
    pg = ctx.new_page()
    pg.set_default_timeout(60_000)
    yield pg
    pg.close()
    ctx.close()


@pytest.mark.cockpit_e2e
def test_cockpit_page_loads_ledger_and_title(page: Page, tmp_path: Path) -> None:
    if not DIST_INDEX.is_file():
        pytest.skip("Falta web/dist (ejecuta: cd web && npm run build)")

    data_dir = tmp_path / "missions_root"
    data_dir.mkdir(parents=True, exist_ok=True)

    port = _free_port()
    env = os.environ.copy()
    env["PAPER_PIPELINE_DATA_DIR"] = str(data_dir.resolve())

    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "paper_pipeline.server.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    try:
        base = f"http://127.0.0.1:{port}"
        _wait_http_ok(f"{base}/api/health")

        created = _post_json(
            f"{base}/api/missions/",
            {"title": "E2E Cockpit", "topic": "t", "paper_target": "p"},
        )
        mid = created["id"]
        out = data_dir / mid / "outputs"
        out.mkdir(parents=True, exist_ok=True)
        ledger = {
            "schema_version": 1,
            "run_id": "e2e-run",
            "mission_id": mid,
            "mission_version": 1,
            "status": "completed",
            "started_at": "2026-03-26T12:00:00+00:00",
            "phases": [],
        }
        (out / "run_ledger.json").write_text(json.dumps(ledger), encoding="utf-8")
        (out / "evidence").mkdir(exist_ok=True)
        (out / "evidence" / "evidence_index.json").write_text(
            json.dumps({"version": 1, "entries": []}),
            encoding="utf-8",
        )

        page.goto(f"{base}/missions/{mid}/cockpit", wait_until="load")
        assert f"/missions/{mid}/cockpit" in page.url, page.url
        h1 = page.locator("h1")
        expect(h1).to_contain_text("Cockpit", timeout=30_000)
        expect(h1).to_contain_text(mid, timeout=5_000)
        expect(page.get_by_text("Ledger", exact=True).first).to_be_visible()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
        err = proc.stderr.read() if proc.stderr else b""
        if proc.returncode not in (0, -15, 1) and err:
            # Windows puede devolver otros códigos al terminar
            pass
