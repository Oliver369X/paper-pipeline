"""Parseo de URLs de Hugging Face y GitHub para replicación (datasets, modelos, código)."""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

# https://huggingface.co/datasets/wikitext
# https://huggingface.co/datasets/wikitext?config=wikitext-2-raw-v1
_HF_DATASET = re.compile(r"huggingface\.co/datasets/([^/?#\s)]+)", re.IGNORECASE)
def parse_hf_dataset_url(url: str) -> tuple[str, str | None]:
    """Devuelve ``(dataset_id, config_name)`` para ``load_dataset(id, config)``.

    El config puede venir del query ``?config=...`` o ser ``None`` (datasets de un solo
    argumento o el caller usa ``hf_dataset_config`` en la misión).
    """

    m = _HF_DATASET.search(url.strip())
    if not m:
        msg = f"URL no reconoce patrón huggingface.co/datasets/...: {url!r}"
        raise ValueError(msg)
    ds_id = m.group(1).strip().rstrip("/")
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    cfg = (qs.get("config") or [None])[0]
    return ds_id, cfg


def parse_hf_model_url(url: str) -> str:
    """ID del modelo para ``from_pretrained`` (p. ej. ``gpt2``, ``meta-llama/Llama-3.2-1B``)."""

    m = re.search(r"huggingface\.co/([^?#\s]+)", url.strip(), re.IGNORECASE)
    if not m:
        msg = f"URL no es de huggingface.co: {url!r}"
        raise ValueError(msg)
    path = m.group(1).strip().rstrip("/")
    if path.lower().startswith("datasets/"):
        msg = "URL de dataset; usá parse_hf_dataset_url o hf_dataset_url"
        raise ValueError(msg)
    return path


def parse_github_repo_spec(url: str) -> tuple[str, str]:
    """``(owner, repo)`` sin ``.git`` (acepta URLs con ``/tree/...``)."""

    m = re.match(
        r"https?://(?:www\.)?github\.com/([\w.-]+)/([\w.-]+)",
        url.strip(),
        re.IGNORECASE,
    )
    if not m:
        msg = f"URL de GitHub no válida para clonar: {url!r}"
        raise ValueError(msg)
    return m.group(1), m.group(2).removesuffix(".git")


# Primer enlace por tipo en markdown (borrador / secciones).
_HF_DS_LINK = re.compile(
    r"https?://(?:www\.)?huggingface\.co/datasets/[^\s)\]}>'\"]+",
    re.IGNORECASE,
)
_GH_LINK = re.compile(
    r"https?://(?:www\.)?github\.com/[\w.-]+/[\w.-]+",
    re.IGNORECASE,
)


def extract_urls_from_markdown(text: str) -> dict[str, str | None]:
    """Extrae el primer dataset HF y el primer repo GitHub del texto."""

    hf_ds: str | None = None
    gh: str | None = None
    m1 = _HF_DS_LINK.search(text)
    if m1:
        hf_ds = m1.group(0).rstrip(".,;")
    m2 = _GH_LINK.search(text)
    if m2:
        gh = m2.group(0).rstrip(".,;")
    return {"hf_dataset_url": hf_ds, "code_repo_url": gh}
