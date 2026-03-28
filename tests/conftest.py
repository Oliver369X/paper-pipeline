from __future__ import annotations

import pytest


@pytest.fixture
def tmp_output_dir(tmp_path):
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def minimal_mission(tmp_path):
    mission_path = tmp_path / "mission.md"
    mission_path.write_text(
        """---
topic: "Test Paper"
paper_target: "workshop"
sections_needed:
  - intro
  - conclusion
max_perplexity_calls: 2
code_needed: false
enable_notion: false
enable_quality_check: false
enable_cursor_cli: false
model: best
output_dir: "outputs"
---
""",
        encoding="utf-8",
    )
    return mission_path


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "e2e: tests Playwright contra visual-flow/index.html (requiere pip install -e '.[e2e]' y playwright install chromium)",
    )
    config.addinivalue_line(
        "markers",
        "cockpit_e2e: Playwright contra Cockpit React (web/dist + uvicorn + playwright)",
    )
    config.addinivalue_line(
        "markers",
        "integration: llamada real a Perplexity (requiere PERPLEXITY_SESSION_TOKEN; consume cuota)",
    )
    config.addinivalue_line(
        "markers",
        "autonomy_integration: humo Perplexity para escenarios autonomía (cuota)",
    )


def pytest_sessionstart(session):
    from paper_pipeline.env import load_dotenv_if_available

    load_dotenv_if_available()
