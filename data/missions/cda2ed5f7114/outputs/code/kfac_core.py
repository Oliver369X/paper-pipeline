"""
K-FAC-style second-moment statistics for a single linear layer y = W @ x + b.

Matches the block approximation F_W ≈ G ⊗ A with:
  A = E[x x^T]   (d_in x d_in)
  G = E[g g^T]   (d_out x d_out),  g = ∂L/∂y

Reference framing: Martens & Grosse (2015); application narrative arXiv:2510.24256.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class KfacEigens:
    """Eigendecomposition of symmetric PSD matrices A (input) and G (output grad)."""

    u_a: np.ndarray  # (d_in, d_in), columns = eigenvectors
    mu: np.ndarray  # (d_in,) eigenvalues descending
    u_g: np.ndarray  # (d_out, d_out)
    lam: np.ndarray  # (d_out,) eigenvalues descending


def accumulate_kfac_moments(
    xs: np.ndarray,
    gs: np.ndarray,
    *,
    eps: float = 1e-12,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    xs: (N, d_in), gs: (N, d_out) — one row per token position / sample.
    Returns A, G (symmetric, PSD if data spans the space).
    """
    if xs.shape[0] != gs.shape[0]:
        raise ValueError("xs and gs must have the same leading dimension")
    # Unbiased / consistent: mean outer products
    a = (xs.T @ xs) / xs.shape[0]
    g_mat = (gs.T @ gs) / gs.shape[0]
    a = 0.5 * (a + a.T)
    g_mat = 0.5 * (g_mat + g_mat.T)
    # Tiny jitter for numerical eigendecomposition stability
    d_in = a.shape[0]
    d_out = g_mat.shape[0]
    a = a + eps * np.eye(d_in)
    g_mat = g_mat + eps * np.eye(d_out)
    return a, g_mat


def eigens_descending(sym: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    w, v = np.linalg.eigh(sym)
    idx = np.argsort(w)[::-1]
    return w[idx], v[:, idx]


def kfac_eigens(a: np.ndarray, g: np.ndarray) -> KfacEigens:
    mu, u_a = eigens_descending(a)
    lam, u_g = eigens_descending(g)
    return KfacEigens(u_a=u_a, mu=mu, u_g=u_g, lam=lam)


def coeff_matrix(w: np.ndarray, ev: KfacEigens) -> np.ndarray:
    """C = U_G^T W U_A, shape (d_out, d_in)."""
    return ev.u_g.T @ w @ ev.u_a


def curvature_mass_grid(lam: np.ndarray, mu: np.ndarray) -> np.ndarray:
    """Π_ij = λ_i μ_j, shape (d_out, d_in)."""
    return lam[:, None] * mu[None, :]


def mask_top_mass(pi: np.ndarray, rho: float) -> np.ndarray:
    """
    Binary mask selecting pairs (i,j) with largest Π_ij until cumulative mass >= rho * total.
    """
    if not (0.0 < rho <= 1.0):
        raise ValueError("rho must be in (0, 1]")
    total = float(pi.sum())
    flat = pi.ravel()
    idx = np.argsort(-flat)
    cum = np.cumsum(flat[idx])
    cutoff = rho * total
    take = cum <= cutoff + 1e-12
    if not np.any(take):
        take[0] = True
    mask_flat = np.zeros_like(flat, dtype=bool)
    mask_flat[idx[take]] = True
    return mask_flat.reshape(pi.shape)


def truncate_weights(w: np.ndarray, ev: KfacEigens, mask: np.ndarray) -> np.ndarray:
    """W' = U_G ( (C ⊙ M) ) U_A^T."""
    c = coeff_matrix(w, ev)
    c_masked = np.where(mask, c, 0.0)
    return ev.u_g @ c_masked @ ev.u_a.T


def relative_frobenius_loss(w_orig: np.ndarray, w_new: np.ndarray) -> float:
    num = np.linalg.norm(w_orig - w_new, ord="fro")
    den = np.linalg.norm(w_orig, ord="fro") + 1e-12
    return float(num / den)
