"""
K-FAC-style curvature mass editing for linear (MLP) weights.

Implements the decomposition from arXiv:2510.24256-style setups:
  F ≈ G ⊗ A,  G = E[g g^T],  A = E[a a^T]
  C = U_G^T W U_A,  Π_ij = λ_i^G λ_j^A, mask low-mass pairs, reconstruct.

For PyTorch nn.Linear: y = x @ W^T + b, shapes W: (out, in), a: (N, in), g: grad w.r.t. y: (N, out).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
import torch
import torch.nn as nn


@dataclass
class KFACStats:
    """Symmetric PSD statistics for one linear layer."""

    A: torch.Tensor  # (in, in)
    G: torch.Tensor  # (out, out)
    count: int


def accumulate_outer(
    samples: torch.Tensor,
    acc: Optional[torch.Tensor],
    count: int,
) -> Tuple[torch.Tensor, int]:
    """Online-ish accumulation of E[v v^T] for rows v in samples (N, d)."""
    if samples.numel() == 0:
        return acc if acc is not None else torch.zeros(0), count
    x = samples.detach().float()
    n = x.shape[0]
    outer = (x.T @ x) / float(n)
    if acc is None:
        acc = outer
        count = n
    else:
        # merge batches with count-weighted average
        total = count + n
        acc = acc * (count / total) + outer * (n / total)
        count = total
    return acc, count


def stats_from_linear_batches(
    weight: torch.Tensor,
    inputs: torch.Tensor,
    grad_outputs: torch.Tensor,
) -> KFACStats:
    """
    inputs: (N, in) activations fed to the linear (same as nn.Linear forward input).
    grad_outputs: (N, out) gradient w.r.t. linear output (before bias if any).
    """
    out_f, in_f = weight.shape
    assert inputs.shape[-1] == in_f, (inputs.shape, in_f)
    assert grad_outputs.shape[-1] == out_f, (grad_outputs.shape, out_f)
    a = inputs.reshape(-1, in_f)
    g = grad_outputs.reshape(-1, out_f)
    A, _ = accumulate_outer(a, None, 0)
    G, _ = accumulate_outer(g, None, 0)
    n = a.shape[0]
    return KFACStats(A=A, G=G, count=n)


def sym_eigh_descending(
    S: torch.Tensor, damping: float
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Eigenpairs with eigenvalues descending. S symmetric PSD."""
    d = S.shape[0]
    eye = torch.eye(d, dtype=S.dtype, device=S.device)
    w, v = torch.linalg.eigh(S + damping * eye)
    # ascending from eigh -> reverse
    w = torch.clamp(w, min=0.0)
    idx = torch.arange(d - 1, -1, -1, device=S.device)
    return w[idx], v[:, idx]


def curvature_mass_mask(
    lam: torch.Tensor,
    mu: torch.Tensor,
    rho: float,
) -> torch.Tensor:
    """
    Pair masses Π_ij = λ_i μ_j. Keep largest pairs until cumulative mass >= rho * sum Π.
    Returns binary mask M (p, q) with 1 = keep, 0 = prune.
    """
    p = lam.numel()
    q = mu.numel()
    Pi = lam[:, None] * mu[None, :]
    total = Pi.sum().clamp_min(1e-30)
    target = rho * total
    flat = Pi.reshape(-1)
    order = torch.argsort(flat, descending=True)
    cum = torch.cumsum(flat[order], dim=0)
    keep_flat = torch.zeros_like(flat)
    # include all pairs up to first index where cum >= target (greedy cover)
    take = (cum <= target) | (torch.arange(flat.numel(), device=flat.device) == 0)
    # ensure at least one pair if rho > 0
    if rho > 0:
        take[0] = True
    keep_idx = order[take]
    keep_flat[keep_idx] = 1.0
    # if still under target due to discrete steps, add pairs until >= target
    k = 0
    while keep_flat.sum() < flat.numel() and cum[keep_flat.bool().cumsum()] is None:
        break
    # simpler: take minimal prefix in sorted order reaching target
    keep_flat.zero_()
    s = 0.0
    for idx in order:
        keep_flat[idx] = 1.0
        s += flat[idx].item()
        if s + 1e-12 >= target.item():
            break
    return keep_flat.reshape(p, q)


def kfac_edit_weight(
    W: torch.Tensor,
    A: torch.Tensor,
    G: torch.Tensor,
    rho: float = 0.6,
    damping: float = 1e-5,
) -> Tuple[torch.Tensor, dict]:
    """
    Apply K-FAC spectrum mass mask to weight matrix W (out, in).

    rho: fraction of total pair-mass Π_ij to retain (largest pairs first).
    """
    assert W.dim() == 2
    p, q = W.shape
    assert A.shape == (q, q) and G.shape == (p, p)
    lam, UG = sym_eigh_descending(G, damping)
    mu, UA = sym_eigh_descending(A, damping)
    C = UG.T @ W @ UA
    M = curvature_mass_mask(lam, mu, rho)
    Cp = C * M
    W_new = UG @ Cp @ UA.T
    info = {
        "rho": rho,
        "kept_mass_frac": (M * (lam[:, None] * mu[None, :])).sum() / (lam[:, None] * mu[None, :]).sum().clamp_min(1e-30),
        "nnz_frac": M.mean().item(),
    }
    return W_new, info


def svd_truncation(
    W: torch.Tensor,
    energy: float = 0.6,
) -> Tuple[torch.Tensor, dict]:
    """Data-free ablation: keep top singular directions by cumulative energy."""
    U, s, Vh = torch.linalg.svd(W, full_matrices=False)
    total = (s**2).sum().clamp_min(1e-30)
    cum = torch.cumsum(s**2, dim=0)
    k = int((cum < energy * total).sum().item()) + 1
    k = min(k, s.numel())
    W_new = (U[:, :k] * s[:k]) @ Vh[:k, :]
    return W_new, {"energy": energy, "rank": k}


class LinearKFACAccumulator:
    """
    Hooks on nn.Linear: collects A, G from activations and grad w.r.t. output.
    Register with module.register_forward_hook / register_full_backward_hook.
    """

    def __init__(self, layer: nn.Linear):
        self.layer = layer
        self._A: Optional[torch.Tensor] = None
        self._G: Optional[torch.Tensor] = None
        self._count = 0
        self._last_input: Optional[torch.Tensor] = None

    def _forward(self, _m, inp, _out):
        x = inp[0]
        self._last_input = x.detach()

    def _backward(self, _m, grad_in, grad_out):
        if self._last_input is None:
            return
        go = grad_out[0]
        if go is None:
            return
        a = self._last_input.reshape(-1, self.layer.in_features)
        g = go.reshape(-1, self.layer.out_features)
        self._A, _ = accumulate_outer(a, self._A, self._count)
        self._G, _ = accumulate_outer(g, self._G, self._count)
        n = a.shape[0]
        self._count += n

    def register(self) -> Tuple:
        h1 = self.layer.register_forward_hook(self._forward)
        h2 = self.layer.register_full_backward_hook(self._backward)
        return h1, h2

    def stats(self) -> Optional[KFACStats]:
        if self._A is None or self._G is None:
            return None
        return KFACStats(A=self._A, G=self._G, count=self._count)
