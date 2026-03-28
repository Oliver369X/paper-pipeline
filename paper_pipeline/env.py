"""Carga opcional de variables desde un archivo `.env` local (no versionado)."""

from __future__ import annotations


def load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()
