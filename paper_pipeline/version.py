"""Package version (pyproject / importlib.metadata)."""

from __future__ import annotations

import importlib.metadata


def get_package_version() -> str:
    try:
        return importlib.metadata.version("paper-pipeline")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"
