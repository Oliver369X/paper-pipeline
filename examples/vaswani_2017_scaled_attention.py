"""Réplica mínima de la *Scaled Dot-Product Attention* (Vaswani et al., 2017).

Ecuación (paper, sección 3.2.1)::

    Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V

Referencia: arXiv:1706.03762 — *Attention Is All You Need*.

La formulación y dimensiones se contrastaron con búsqueda asistida (Perplexity MCP,
fuentes scholar) antes de implementar este módulo.

Este script no entrena un Transformer completo: solo materializa la ecuación (1)
con matrices pequeñas, para comprobar **reproducibilidad numérica** del bloque central.
"""

from __future__ import annotations

import math
from typing import Sequence


def _transpose(a: Sequence[Sequence[float]]) -> list[list[float]]:
    rows = len(a)
    cols = len(a[0])
    return [[float(a[r][c]) for r in range(rows)] for c in range(cols)]


def _matmul(a: Sequence[Sequence[float]], b: Sequence[Sequence[float]]) -> list[list[float]]:
    """(m,n) @ (n,p) -> (m,p)."""
    n = len(b)
    p = len(b[0])
    out: list[list[float]] = []
    for i in range(len(a)):
        row = []
        for j in range(p):
            s = 0.0
            for k in range(n):
                s += float(a[i][k]) * float(b[k][j])
            row.append(s)
        out.append(row)
    return out


def _softmax_rows(logits: Sequence[Sequence[float]]) -> list[list[float]]:
    """Softmax por fila (estabilizado)."""
    out: list[list[float]] = []
    for row in logits:
        m = max(row)
        exps = [math.exp(float(x) - m) for x in row]
        s = sum(exps)
        out.append([e / s for e in exps])
    return out


def scaled_dot_product_attention(
    Q: Sequence[Sequence[float]],
    K: Sequence[Sequence[float]],
    V: Sequence[Sequence[float]],
    *,
    d_k: int,
) -> list[list[float]]:
    """Implementa Attention(Q, K, V) según Vaswani et al. (2017), ecuación (1).

    Parámetros
    ----------
    Q, K, V
        Matrices ``seq_len × d_k`` (lista de filas).
    d_k
        Dimensión de cada vector consulta/clave/valor (debe coincidir con el ancho de las matrices).
    """
    if d_k <= 0:
        msg = "d_k must be positive"
        raise ValueError(msg)
    scale = math.sqrt(float(d_k))
    # scores: (seq, seq) = Q @ K^T
    kt = _transpose(K)
    scores = _matmul(Q, kt)
    scaled = [[x / scale for x in row] for row in scores]
    weights = _softmax_rows(scaled)
    return _matmul(weights, V)


def _demo() -> None:
    # Caso pequeño: Q=K=I, V arbitraria; salida = V si cada fila de scores es one-hot
    # Con I/sqrt(d_k) y softmax por fila no es exactamente identidad; solo mostramos forma.
    q = [[1.0, 0.0], [0.0, 1.0]]
    k = [[1.0, 0.0], [0.0, 1.0]]
    v = [[1.0, 2.0], [3.0, 4.0]]
    out = scaled_dot_product_attention(q, k, v, d_k=2)
    for row in out:
        print(" ".join(f"{x:.6f}" for x in row))


if __name__ == "__main__":
    _demo()
