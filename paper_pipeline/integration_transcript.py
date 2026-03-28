"""Un solo archivo Markdown cronológico para auditar interacciones Perplexity + Cursor CLI."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

TRANSCRIPT_FILENAME = "INTEGRATION_TRANSCRIPT.md"
# Evitar Markdown gigante en repos; el detalle completo sigue en cursor_cli.log / Perplexity web.
_MAX_CHARS = 120_000


def append_transcript(
    output_dir: Path,
    *,
    source: str,
    heading: str,
    body: str,
    meta_lines: list[str] | None = None,
) -> None:
    """Append one section to ``output_dir/INTEGRATION_TRANSCRIPT.md``."""

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / TRANSCRIPT_FILENAME
    stamp = datetime.now(UTC).isoformat()
    text = body if len(body) <= _MAX_CHARS else body[:_MAX_CHARS] + "\n\n[…truncado…]\n"

    meta_block = ""
    if meta_lines:
        meta_block = "\n".join(f"- {m}" for m in meta_lines) + "\n\n"

    section = (
        f"\n\n---\n\n## {heading}\n\n"
        f"**Fuente:** `{source}` · **UTC:** `{stamp}`\n\n"
        f"{meta_block}"
        f"{text}\n"
    )

    header = (
        "# Transcript integrado (Perplexity + Cursor)\n\n"
        "Este archivo se **añade automáticamente** en cada ronda del meta-loop (Perplexity) "
        "y en cada ejecución del Cursor CLI. Sirve como **único historial legible** para auditoría; "
        "no sustituye la biblioteca web de Perplexity ni el panel de Cursor.\n\n"
        "---\n"
    )

    if path.is_file():
        path.write_text(path.read_text(encoding="utf-8") + section, encoding="utf-8")
    else:
        path.write_text(header + section, encoding="utf-8")
