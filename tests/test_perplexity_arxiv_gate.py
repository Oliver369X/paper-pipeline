"""Detección arXiv y ancla 2410.02159 (sin llamar a la API Perplexity)."""

from __future__ import annotations

from paper_pipeline.brain.perplexity_context import (
    user_message_requests_arxiv_verification,
    _arxiv_verification_preamble,
)


def test_user_message_requests_arxiv_verification_url() -> None:
    assert user_message_requests_arxiv_verification("replica https://arxiv.org/abs/2410.02159")


def test_user_message_requests_arxiv_verification_id_only() -> None:
    assert user_message_requests_arxiv_verification("qué es 2410.02159")


def test_user_message_requests_arxiv_verification_negative() -> None:
    assert not user_message_requests_arxiv_verification("hola sin arxiv")


def test_preamble_mentions_mitigating_for_2410() -> None:
    p = _arxiv_verification_preamble("https://arxiv.org/abs/2410.02159", "")
    assert "Mitigating Memorization" in p
    assert "2410.02159" in p
