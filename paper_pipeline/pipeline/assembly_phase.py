"""Draft assembly from section outputs."""

from __future__ import annotations

import shutil
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from paper_pipeline.events import emit_event
from paper_pipeline.logger import PipelineLogger
from paper_pipeline.manifest import PipelineManifest
from paper_pipeline.mission import Mission
from paper_pipeline.state import RunState
from paper_pipeline.templates import CODE_README_TEMPLATE


def run_assembly(
    mission: Mission,
    out: Path,
    code_dir: Path,
    written: list[tuple[str, Path]],
    state: RunState,
    state_path: Path,
    plog: PipelineLogger,
    *,
    event_sink: Callable[[dict], None] | None,
    manifest: PipelineManifest | None,
) -> Path:
    """Write code README if needed, assemble ``draft_paper.md``, update state."""

    if manifest:
        manifest.upsert_phase("assembly_draft", "running")

    if mission.code_needed:
        readme = code_dir / "README.md"
        readme.write_text(CODE_README_TEMPLATE.format(topic=mission.topic), encoding="utf-8")
        written.append(("code/README", readme))
        # Si junto a la carpeta de salida hay un script (misma carpeta que mission.md), copiarlo.
        mission_root = out.parent
        for extra_py in ("train_nano_gpt_cpu.py",):
            src = mission_root / extra_py
            if src.is_file():
                dest = code_dir / extra_py
                shutil.copy2(src, dest)
                written.append((f"code/{extra_py}", dest))

    draft_parts: list[str] = [
        f"# Draft: {mission.topic}",
        "",
        f"**Target venue / reference:** {mission.paper_target}",
        "",
        "_Disclaimer: borrador asistido por LLM (Perplexity); no sustituye experimentos ejecutados, números reproducibles "
        "ni revisión por pares. Ver `docs/MODE_NARRATIVE_VS_EMPIRICAL.md` y `docs/ARXIV_TARGET_ALIGNMENT.md` en el repositorio._",
        "",
        f"_Generated {datetime.now(UTC).isoformat()} UTC_",
        "",
    ]
    for section, path in written:
        if section == "code/README" or section.startswith("code/") and section.endswith(".py"):
            continue
        if path.suffix.lower() == ".md" and path.exists():
            draft_parts.append(f"## {section}\n")
            draft_parts.append(path.read_text(encoding="utf-8"))
            draft_parts.append("\n")

    draft_path = out / "draft_paper.md"
    draft_path.write_text("\n".join(draft_parts), encoding="utf-8")
    written.append(("draft_paper", draft_path))
    dh = plog.draft_snapshot(draft_path)
    state.draft_hash = dh
    state.draft_version += 1
    state.save(state_path)

    emit_event(out, "draft_assembled", {"path": str(draft_path)}, sink=event_sink)

    if manifest:
        manifest.upsert_phase("assembly_draft", "done")
        manifest.write(out)

    return draft_path
