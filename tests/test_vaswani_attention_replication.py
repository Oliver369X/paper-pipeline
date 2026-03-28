"""Réplica numérica mínima: Scaled Dot-Product Attention (Vaswani et al., 2017)."""

from __future__ import annotations

import math

from examples.vaswani_2017_scaled_attention import (
    _matmul,
    _softmax_rows,
    _transpose,
    scaled_dot_product_attention,
)


def test_scaled_attention_identity_like_qk() -> None:
    """Q=K=I, V=I: QK^T=I; softmax(I/sqrt(d)) @ I debe coincidir con cálculo explícito."""
    d_k = 2
    eye = [[1.0, 0.0], [0.0, 1.0]]
    out = scaled_dot_product_attention(eye, eye, eye, d_k=d_k)
    scale = math.sqrt(d_k)
    # scores = I; scaled rows [1/s,0] y [0,1/s]
    def softmax2(a: float, b: float) -> tuple[float, float]:
        m = max(a, b)
        ea, eb = math.exp(a - m), math.exp(b - m)
        s = ea + eb
        return ea / s, eb / s

    w00, w01 = softmax2(1.0 / scale, 0.0)
    w10, w11 = softmax2(0.0, 1.0 / scale)
    # out = W @ I = W
    assert len(out) == 2 and len(out[0]) == 2
    assert abs(out[0][0] - w00) < 1e-9 and abs(out[0][1] - w01) < 1e-9
    assert abs(out[1][0] - w10) < 1e-9 and abs(out[1][1] - w11) < 1e-9


def test_scaled_attention_matches_manual_matmul() -> None:
    """Un caso 2x2 frente a descomposición manual."""
    q = [[0.5, -0.25], [1.0, 0.0]]
    k = [[0.0, 1.0], [1.0, 1.0]]
    v = [[2.0, 3.0], [4.0, 5.0]]
    d_k = 2
    got = scaled_dot_product_attention(q, k, v, d_k=d_k)
    assert len(got) == 2 and len(got[0]) == 2
    scores = _matmul(q, _transpose(k))
    scaled = [[x / math.sqrt(d_k) for x in row] for row in scores]
    w = _softmax_rows(scaled)
    ref = _matmul(w, v)
    for i in range(2):
        for j in range(2):
            assert abs(got[i][j] - ref[i][j]) < 1e-9
