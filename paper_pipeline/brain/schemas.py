"""Request/response models for the brain API (distinct from Mission)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from paper_pipeline.server.schemas import MissionPatch


class BrainChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = ""


class BrainChatRequest(BaseModel):
    messages: list[BrainChatMessage] = Field(default_factory=list)


class BrainMetaSuggestion(BaseModel):
    title: str = ""
    description: str = ""


class BrainChatResponse(BaseModel):
    """Returned to the web client after a successful brain/chat call."""

    reply: str = ""
    brief_markdown: str = ""
    meta: BrainMetaSuggestion = Field(default_factory=BrainMetaSuggestion)
    suggested_patch: dict[str, Any] = Field(default_factory=dict)
    #: Relative paths under the mission root (must be ``outputs/code/...``); persisted only via ``POST .../brain/apply``.
    suggested_code_files: dict[str, str] = Field(default_factory=dict)
    cursor_checklist_markdown: str = ""
    #: Preguntas sugeridas para continuar el mismo hilo (profundizar; 3–8 ítems típicos).
    followup_questions: list[str] = Field(default_factory=list)


class BrainApplyRequest(BaseModel):
    """Apply a patch and optional brief without calling Gemini."""

    brief_markdown: str = ""
    patch: MissionPatch
    suggested_code_files: dict[str, str] = Field(
        default_factory=dict,
        description="Escribir archivos bajo outputs/code/ al aplicar (mismo shape que brain/chat).",
    )
    run_pipeline: bool | None = Field(
        default=None,
        description="Si True/False, explícito. Si None, el servidor usa BRAIN_DEFAULT_RUN_PIPELINE_ON_APPLY (por defecto 0).",
    )
    dry_run: bool = Field(
        default=False,
        description="Si run_pipeline y dry_run, el pipeline no llama a Perplexity de verdad.",
    )


class BrainHistoryMessage(BaseModel):
    """One line from ``brain_chat_history.jsonl`` (API shape)."""

    ts: str = ""
    role: Literal["user", "assistant"]
    content: str = ""


class BrainVariantsRequest(BaseModel):
    """N alternative mission shapes from Gemini."""

    n: int = Field(default=3, ge=1, le=10)
    messages: list[BrainChatMessage] = Field(default_factory=list)


class BrainVariantItem(BaseModel):
    label: str = ""
    short_rationale: str = ""
    brief_markdown: str = ""
    suggested_patch: dict[str, Any] = Field(default_factory=dict)


class BrainVariantsResponse(BaseModel):
    variants: list[BrainVariantItem] = Field(default_factory=list)
