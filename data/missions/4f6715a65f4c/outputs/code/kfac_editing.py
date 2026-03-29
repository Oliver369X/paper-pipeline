"""
K-FAC–style curvature on linear (MLP) layers and weight editing for replication of
arXiv:2510.24256-style experiments.

Approximate Fisher block F_W ≈ G ⊗ A with A = E[a a^T], G = E[g g^T],
a = layer input activations, g = ∂L/∂(layer output).

Mode pairs (i, j) use curvature mass Π_ij = λ_i^(G) μ_j^(A) (eigenvalues of G, A).
Editing: W_edit = U_G ((U_G^T W U_A) ⊙ M) U_A^T with M selecting kept modes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn


def _sym_psd(mat: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    m = 0.5 * (mat + mat.T)
    d = m.shape[0]
    eye = torch.eye(d, device=m.device, dtype=m.dtype)
    return m + eps * eye


@dataclass
class KFACStats:
    """Symmetric PSD statistics for one Linear layer."""

    A: torch.Tensor  # (d_in, d_in)
    G: torch.Tensor  # (d_out, d_out)
    n_samples: int


class KFACAccumulator:
    """Online accumulation of A = E[a a^T] and G = E[g g^T] for nn.Linear."""

    def __init__(self, module: nn.Linear, device: Optional[torch.device] = None):
        self.module = module
        self.device = device or next(module.parameters()).device
        d_in = module.in_features
        d_out = module.out_features
        self.registered = False
        self._A_sum = torch.zeros(d_in, d_in, device=self.device, dtype=torch.float64)
        self._G_sum = torch.zeros(d_out, d_out, device=self.device, dtype=torch.float64)
        self._n = 0
        self._fwd_handle = None
        self._bwd_handle = None

    def _forward_hook(self, _mod, inp, _out):
        # inp[0]: (batch, d_in)
        a = inp[0].detach()
        if a.dim() == 2:
            bs = a.shape[0]
            self._A_sum += (a.T @ a).double()
            self._n += bs
        else:
            # (batch, seq, d_in) — flatten batch*seq
            a2 = a.reshape(-1, a.shape[-1])
            bs = a2.shape[0]
            self._A_sum += (a2.T @ a2).double()
            self._n += bs

    def _backward_hook(self, _mod, _gi, go):
        # go[0]: ∂L/∂output, same shape as layer output
        g = go[0].detach()
        if g.dim() == 2:
            self._G_sum += (g.T @ g).double()
        else:
            g2 = g.reshape(-1, g.shape[-1])
            self._G_sum += (g2.T @ g2).double()

    def register(self):
        if self.registered:
            return
        self._fwd_handle = self.module.register_forward_hook(self._forward_hook)
        self._bwd_handle = self.module.register_full_backward_hook(self._backward_hook)
        self.registered = True

    def remove(self):
        if self._fwd_handle is not None:
            self._fwd_handle.remove()
            self._fwd_handle = None
        if self._bwd_handle is not None:
            self._bwd_handle.remove()
            self._bwd_handle = None
        self.registered = False

    def finalize(self) -> KFACStats:
        if self._n == 0:
            raise RuntimeError("KFACAccumulator: no samples collected.")
        n = float(self._n)
        A = (self._A_sum / n).float()
        G = (self._G_sum / n).float()
        A = _sym_psd(A)
        G = _sym_psd(G)
        return KFACStats(A=A, G=G, n_samples=int(self._n))


def eig_sorted_desc(S: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """Eigenvalues descending, columns are eigenvectors."""
    w, V = torch.linalg.eigh(S)
    idx = torch.argsort(w, descending=True)
    return w[idx], V[:, idx]


def pair_masses_and_order(
    lam: torch.Tensor, mu: torch.Tensor
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Π_ij = λ_i μ_j; return flat Pi and flat indices (i,j) sorted by Pi desc."""
    d_out = lam.numel()
    d_in = mu.numel()
    Pi = lam[:, None] * mu[None, :]
    Pi_flat = Pi.reshape(-1)
    pairs = torch.cartesian_prod(
        torch.arange(d_out, device=lam.device),
        torch.arange(d_in, device=mu.device),
    )
    order = torch.argsort(Pi_flat, descending=True)
    return Pi_flat[order], pairs[order]


def mask_top_fraction(
    d_out: int,
    d_in: int,
    rho: float,
    ordered_pairs: torch.Tensor,
    device: torch.device,
    dtype: torch.dtype,
) -> torch.Tensor:
    """Binary mask M (d_out, d_in) in coefficient space: 1 = kept (high curvature)."""
    total = d_out * d_in
    k = max(1, min(total, int(round(rho * total))))
    M = torch.zeros(d_out, d_in, device=device, dtype=dtype)
    kept = ordered_pairs[:k]
    M[kept[:, 0], kept[:, 1]] = 1.0
    return M


def random_mask_same_sparsity(
    d_out: int, d_in: int, k: int, device: torch.device, dtype: torch.dtype, generator: torch.Generator
) -> torch.Tensor:
    M = torch.zeros(d_out, d_in, device=device, dtype=dtype)
    flat = torch.rand(d_out * d_in, generator=generator, device=device)
    _, idx = torch.topk(flat, k, largest=False)
    rows = idx // d_in
    cols = idx % d_in
    M[rows, cols] = 1.0
    return M


def edit_weight_kfac(
    W: torch.Tensor,
    stats: KFACStats,
    rho: float,
    generator: Optional[torch.Generator] = None,
) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
    """
    W: (d_out, d_in). Keep top-ρ fraction of (i,j) modes by Π_ij = λ_i μ_j.
    """
    device, dtype = W.device, W.dtype
    G = stats.G.to(device=device, dtype=torch.float64)
    A = stats.A.to(device=device, dtype=torch.float64)
    W64 = W.double()

    lam, UG = eig_sorted_desc(G)
    mu, UA = eig_sorted_desc(A)
    Pi_ord, pairs_ord = pair_masses_and_order(lam, mu)
    M = mask_top_fraction(
        W.shape[0], W.shape[1], rho, pairs_ord, device, torch.float64
    )
    C = UG.T @ W64 @ UA
    Cm = C * M
    W_new = (UG @ Cm @ UA.T).to(dtype=dtype)
    meta = {
        "Pi_sorted_head": Pi_ord[: min(16, Pi_ord.numel())].float().cpu(),
        "mask_density": M.mean().item(),
    }
    return W_new, meta


def edit_weight_svd(
    W: torch.Tensor, rho: float, generator: Optional[torch.Generator] = None
) -> Tuple[torch.Tensor, Dict[str, float]]:
    """Rank-style keep: retain largest singular values until ρ mass of pairs — here keep top ρ fraction of singular values by count."""
    W64 = W.double()
    U, S, Vh = torch.linalg.svd(W64, full_matrices=False)
    r = S.numel()
    k = max(1, min(r, int(round(rho * r))))
    S_new = torch.zeros_like(S)
    S_new[:k] = S[:k]
    W_new = (U * S_new) @ Vh
    return W_new.to(dtype=W.dtype), {"svd_kept": float(k), "svd_total": float(r)}


def edit_weight_random_kfac_basis(
    W: torch.Tensor,
    stats: KFACStats,
    rho: float,
    generator: torch.Generator,
) -> torch.Tensor:
    """Same number of kept coefficients as K-FAC, random positions in (U_G, U_A) coefficient space."""
    device, dtype = W.device, W.dtype
    G = stats.G.to(device=device, dtype=torch.float64)
    A = stats.A.to(device=device, dtype=torch.float64)
    W64 = W.double()
    lam, UG = eig_sorted_desc(G)
    mu, UA = eig_sorted_desc(A)
    d_out, d_in = W.shape
    total = d_out * d_in
    k = max(1, min(total, int(round(rho * total))))
    _, pairs_ord = pair_masses_and_order(lam, mu)
    M_rand = random_mask_same_sparsity(d_out, d_in, k, device, torch.float64, generator)
    C = UG.T @ W64 @ UA
    Cm = C * M_rand
    return (UG @ Cm @ UA.T).to(dtype=dtype)


def collect_kfac_for_linears(
    model: nn.Module,
    data_iter: Iterator[Tuple[torch.Tensor, torch.Tensor]],
    criterion,
    layers: List[nn.Linear],
    device: torch.device,
    max_batches: Optional[int] = None,
) -> Dict[nn.Linear, KFACStats]:
    accs = [KFACAccumulator(L, device=device) for L in layers]
    for a in accs:
        a.register()
    model.train()
    b = 0
    for batch in data_iter:
        if isinstance(batch, (list, tuple)):
            x, y = batch[0], batch[1]
        else:
            raise TypeError("Expected (x, y) batches.")
        x = x.to(device)
        y = y.to(device)
        model.zero_grad(set_to_none=True)
        out = model(x)
        loss = criterion(out, y)
        loss.backward()
        b += 1
        if max_batches is not None and b >= max_batches:
            break
    for a in accs:
        a.remove()
    return {L: acc.finalize() for L, acc in zip(layers, accs)}


def apply_edits_to_linears(
    edits: Dict[nn.Linear, torch.Tensor],
) -> None:
    for layer, Wnew in edits.items():
        with torch.no_grad():
            layer.weight.copy_(Wnew)
