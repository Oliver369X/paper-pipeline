"""Environment and path checks before expensive work."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PreflightReport:
    ok: bool = True
    checks: list[dict[str, Any]] = field(default_factory=list)
    blocking_reasons: list[str] = field(default_factory=list)

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "checks": self.checks,
            "blocking_reasons": self.blocking_reasons,
        }


def run_preflight(
    *,
    output_dir: Path,
    dry_run: bool,
    require_perplexity_token: bool = True,
    require_cursor_if_enabled: bool = False,
    cursor_enabled: bool = False,
) -> PreflightReport:
    """Run preflight checks. Mutates report; writes nothing."""

    rep = PreflightReport()

    def add(name: str, passed: bool, detail: str = "") -> None:
        rep.checks.append({"name": name, "ok": passed, "detail": detail})
        if not passed:
            rep.ok = False
            rep.blocking_reasons.append(f"{name}: {detail}".strip())

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        probe = output_dir / ".preflight_write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        add("output_dir_writable", True, str(output_dir.resolve()))
    except OSError as exc:
        add("output_dir_writable", False, str(exc))

    if require_perplexity_token and not dry_run:
        tok = os.environ.get("PERPLEXITY_SESSION_TOKEN", "").strip()
        add("perplexity_token_present", bool(tok), "missing PERPLEXITY_SESSION_TOKEN" if not tok else "set")

    if require_cursor_if_enabled and cursor_enabled and not dry_run:
        key = os.environ.get("CURSOR_API_KEY", "").strip()
        add("cursor_api_key_present", bool(key), "missing CURSOR_API_KEY" if not key else "set")
        agent = os.environ.get("CURSOR_AGENT_BIN", "agent").strip() or "agent"
        resolved = shutil.which(agent) if not Path(agent).is_file() else agent
        add("cursor_agent_on_path", bool(resolved), f"cannot resolve {agent!r}" if not resolved else str(resolved))

    return rep


def write_preflight_report(output_dir: Path, report: PreflightReport) -> Path:
    import json

    p = output_dir / "preflight_report.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(report.to_json_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p
