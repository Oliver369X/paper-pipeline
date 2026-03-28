"""Clone superficial de repos de código (replicación); host permitido."""

from __future__ import annotations

import hashlib
import logging
import os
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def _host_allowed(url: str) -> bool:
    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        return False
    allowed = {"github.com", "www.github.com", "gitlab.com", "www.gitlab.com"}
    return host in allowed


def _dest_slug(url: str) -> str:
    if "github.com" in url:
        from paper_pipeline.experiments.source_urls import parse_github_repo_spec

        owner, repo = parse_github_repo_spec(url)
        return re.sub(r"[^a-zA-Z0-9._-]", "_", f"{owner}_{repo}")
    parsed = urlparse(url.strip())
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) >= 2:
        return re.sub(r"[^a-zA-Z0-9._-]", "_", f"{parts[0]}_{parts[1]}")
    return hashlib.sha256(url.encode()).hexdigest()[:14]


def clone_allowed_repo(
    url: str,
    dest_parent: Path,
    *,
    branch: str | None = None,
    depth: int = 1,
    timeout_sec: int = 600,
) -> Path:
    """``git clone --depth N`` bajo ``dest_parent/vendor_<slug>``. Devuelve el directorio del repo."""

    url = url.strip()
    if not _host_allowed(url):
        msg = f"Host no permitido para clone (solo github.com / gitlab.com): {url!r}"
        raise ValueError(msg)

    safe = _dest_slug(url)
    dest = dest_parent / f"vendor_{safe}"
    if dest.exists():
        logger.info("Removing existing clone %s", dest)
        shutil.rmtree(dest, ignore_errors=True)

    dest_parent.mkdir(parents=True, exist_ok=True)
    cmd: list[str] = ["git", "clone", "--depth", str(max(1, depth))]
    if branch:
        cmd.extend(["--branch", branch])
    cmd.extend([url, str(dest)])

    logger.info("git clone -> %s", dest)
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout_sec,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "")[-4000:]
        msg = f"git clone failed ({proc.returncode}): {err}"
        raise RuntimeError(msg)
    return dest


def ensure_git_available() -> None:
    """Levanta ``RuntimeError`` si ``git`` no está en PATH."""

    try:
        r = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError("git no disponible en PATH") from exc
    if r.returncode != 0:
        raise RuntimeError("git --version falló")
