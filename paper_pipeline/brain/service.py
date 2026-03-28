"""Orchestrate brain chat: prompt + Gemini + map to BrainChatResponse."""

from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from paper_pipeline.brain.gemini_client import generate_brain_json
from paper_pipeline.brain.prompts import build_brain_system_prompt, build_brain_variants_system_prompt
from paper_pipeline.brain.schemas import (
    BrainChatMessage,
    BrainChatResponse,
    BrainMetaSuggestion,
    BrainVariantItem,
    BrainVariantsResponse,
)
from paper_pipeline.brain.settings import brain_max_brief_chars, brain_max_history_messages
from paper_pipeline.mission import Mission, normalize_hypothesis_dict_list
from paper_pipeline.server.schemas import MissionPatch


def trim_brief(text: str | None) -> str | None:
    if not text:
        return None
    max_c = brain_max_brief_chars()
    t = text.strip()
    if len(t) > max_c:
        return t[:max_c] + "\n\n[…truncado por BRAIN_MAX_BRIEF_CHARS]"
    return t


def trim_messages(messages: list[BrainChatMessage]) -> list[BrainChatMessage]:
    max_n = brain_max_history_messages()
    if len(messages) <= max_n:
        return messages
    return messages[-max_n:]


def _build_user_payload(
    messages: list[BrainChatMessage],
    mission: Mission | None,
    meta_title: str,
    meta_description: str,
    *,
    persisted_brief: str | None = None,
    memory_context: str | None = None,
    perplexity_context: str | None = None,
) -> str:
    parts: list[str] = []
    if persisted_brief:
        parts.append("## Brief persistido (outputs/brain_brief.md)\n\n")
        parts.append(persisted_brief.strip())
        parts.append("\n\n")
    if memory_context:
        parts.append("## Memoria contextual (episódica y/o RAG; puede estar incompleta)\n\n")
        parts.append(memory_context.strip())
        parts.append("\n\n")
    if perplexity_context:
        parts.append(
            "## Contexto web (Perplexity — priorizá esto sobre tu memoria paramétrica para títulos de papers y hechos verificables)\n\n"
        )
        parts.append(perplexity_context.strip())
        parts.append("\n\n")
    parts.append("## Contexto de la misión actual (puede estar incompleto)\n")
    if mission is not None:
        parts.append("```json\n")
        parts.append(mission.model_dump_json(indent=2))
        parts.append("\n```\n")
    parts.append(f"## meta.json (título UI)\n- title: {meta_title}\n- description: {meta_description}\n")
    parts.append("\n## Conversación (mismo hilo; respetá continuidad)\n")
    for m in messages:
        role = "Usuario" if m.role == "user" else "Asistente"
        parts.append(f"**{role}:**\n{m.content}\n\n")
    if len(messages) >= 6:
        parts.append(
            "**Nota:** Ya hay varios turnos: en `reply` **profundizá** (matices, supuestos, riesgos, siguiente paso) "
            "sin repetir la misma introducción genérica. En `followup_questions` proponé **preguntas nuevas** que abran el tema.\n\n"
        )
    parts.append(
        "\nGenerá el JSON final según el esquema del system prompt. "
        "Ajustá mission y meta para reflejar la última intención del usuario."
    )
    return "".join(parts)


def _suggested_from_raw(raw: dict[str, Any]) -> dict[str, Any]:
    suggested: dict[str, Any] = {}
    meta = raw.get("meta") if isinstance(raw.get("meta"), dict) else {}
    if meta.get("title"):
        suggested["title"] = meta["title"]
    if meta.get("description"):
        suggested["description"] = meta["description"]
    mission = raw.get("mission") if isinstance(raw.get("mission"), dict) else {}
    for k, v in mission.items():
        if v is not None:
            suggested[k] = v
    # Gemini a veces devuelve ``hypotheses`` en la raíz del JSON en vez de dentro de ``mission``.
    if "hypotheses" not in suggested and isinstance(raw.get("hypotheses"), list):
        suggested["hypotheses"] = raw["hypotheses"]
    return suggested


def _normalize_hypotheses_in_suggested(suggested: dict[str, Any]) -> None:
    """Map LLM-shaped hypothesis objects (p. ej. ``statement``) to :class:`~paper_pipeline.mission.Hypothesis`."""

    hy = suggested.get("hypotheses")
    if not isinstance(hy, list) or not hy:
        return
    suggested["hypotheses"] = normalize_hypothesis_dict_list(hy)


_MAX_CODE_FILES_CHARS = 200_000


_MAX_FOLLOWUPS = 10
_MAX_FOLLOWUP_LEN = 400


def followup_questions_from_raw(raw: dict[str, Any]) -> list[str]:
    """Parse ``followup_questions`` del JSON del cerebro (lista de strings)."""

    v = raw.get("followup_questions")
    if not isinstance(v, list):
        return []
    out: list[str] = []
    for x in v[:_MAX_FOLLOWUPS]:
        if isinstance(x, str) and x.strip():
            out.append(x.strip()[:_MAX_FOLLOWUP_LEN])
    return out


def suggested_code_files_from_raw(raw: dict[str, Any]) -> dict[str, str]:
    """Parse ``suggested_code_files``; only ``outputs/code/...`` paths, size-capped."""

    v = raw.get("suggested_code_files")
    if not isinstance(v, dict):
        return {}
    out: dict[str, str] = {}
    total = 0
    for k, val in v.items():
        if not isinstance(k, str) or not isinstance(val, str):
            continue
        nk = k.replace("\\", "/").strip().lstrip("/")
        if ".." in nk or nk.startswith("/") or not nk.startswith("outputs/code/"):
            continue
        total += len(val)
        if total > _MAX_CODE_FILES_CHARS:
            break
        out[nk] = val
    return out


def run_brain_chat(
    messages: list[BrainChatMessage],
    *,
    mission: Mission | None,
    meta_title: str,
    meta_description: str,
    persisted_brief: str | None = None,
    memory_context: str | None = None,
    perplexity_context: str | None = None,
) -> BrainChatResponse:
    system = build_brain_system_prompt()
    msgs = trim_messages(messages)

    def build_text() -> str:
        return _build_user_payload(
            msgs,
            mission,
            meta_title,
            meta_description,
            persisted_brief=persisted_brief,
            memory_context=memory_context,
            perplexity_context=perplexity_context,
        )

    user_text = build_text()
    last_err: str | None = None

    for attempt in range(2):
        try:
            raw = generate_brain_json(system_instruction=system, user_text=user_text)
        except (RuntimeError, json.JSONDecodeError, OSError, TypeError, ValueError) as exc:
            last_err = str(exc)
            if attempt == 0:
                user_text = build_text() + f"\n\n[Error: {last_err}. Respondé con un único objeto JSON válido.]\n"
                continue
            raise

        reply = str(raw.get("reply") or "")
        brief = str(raw.get("brief_markdown") or "")
        meta_raw = raw.get("meta") if isinstance(raw.get("meta"), dict) else {}
        meta = BrainMetaSuggestion(
            title=str(meta_raw.get("title") or ""),
            description=str(meta_raw.get("description") or ""),
        )
        suggested = _suggested_from_raw(raw)
        _normalize_hypotheses_in_suggested(suggested)

        try:
            MissionPatch.model_validate(suggested)
        except ValidationError as exc:
            last_err = str(exc)
            if attempt == 0:
                user_text = (
                    build_text()
                    + f"\n\n[Validación: {last_err}. Corregí tipos y claves (solo MissionPatch).]\n"
                )
                continue
            raise

        cursor_checklist = str(raw.get("cursor_checklist_markdown") or "")
        code_files = suggested_code_files_from_raw(raw)
        followups = followup_questions_from_raw(raw)

        return BrainChatResponse(
            reply=reply,
            brief_markdown=brief,
            meta=meta,
            suggested_patch=suggested,
            suggested_code_files=code_files,
            cursor_checklist_markdown=cursor_checklist,
            followup_questions=followups,
        )

    raise RuntimeError(last_err or "brain chat failed")


def run_brain_variants(
    messages: list[BrainChatMessage],
    *,
    n: int,
    mission: Mission | None,
    meta_title: str,
    meta_description: str,
    persisted_brief: str | None = None,
    memory_context: str | None = None,
    perplexity_context: str | None = None,
) -> BrainVariantsResponse:
    system = build_brain_variants_system_prompt(n)
    msgs = trim_messages(messages)

    def build_text() -> str:
        return _build_user_payload(
            msgs,
            mission,
            meta_title,
            meta_description,
            persisted_brief=persisted_brief,
            memory_context=memory_context,
            perplexity_context=perplexity_context,
        )

    user_text = build_text()
    last_err: str | None = None

    for attempt in range(2):
        try:
            raw = generate_brain_json(system_instruction=system, user_text=user_text)
        except (RuntimeError, json.JSONDecodeError, OSError, TypeError, ValueError) as exc:
            last_err = str(exc)
            if attempt == 0:
                user_text = build_text() + f"\n\n[Error: {last_err}. JSON con clave variants (array).]\n"
                continue
            raise

        variants_raw = raw.get("variants")
        if not isinstance(variants_raw, list):
            last_err = "missing variants array"
            if attempt == 0:
                user_text = build_text() + f"\n\n[Error: {last_err}]\n"
                continue
            raise ValueError(last_err)

        items: list[BrainVariantItem] = []
        variant_err: str | None = None
        for vr in variants_raw[: max(n * 2, n)]:
            if len(items) >= n:
                break
            if not isinstance(vr, dict):
                continue
            sug = _suggested_from_raw(vr)
            _normalize_hypotheses_in_suggested(sug)
            try:
                MissionPatch.model_validate(sug)
            except ValidationError as exc:
                variant_err = str(exc)
                continue
            items.append(
                BrainVariantItem(
                    label=str(vr.get("label") or ""),
                    short_rationale=str(vr.get("short_rationale") or ""),
                    brief_markdown=str(vr.get("brief_markdown") or ""),
                    suggested_patch=sug,
                )
            )

        if len(items) == n:
            return BrainVariantsResponse(variants=items)

        last_err = variant_err or f"expected {n} valid variants, got {len(items)}"
        if attempt == 0:
            user_text = build_text() + f"\n\n[Validación variantes: {last_err}]\n"
            continue
        raise ValueError(last_err)

    raise RuntimeError(last_err or "brain variants failed")
