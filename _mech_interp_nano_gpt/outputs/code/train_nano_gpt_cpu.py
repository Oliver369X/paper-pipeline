"""Entrenamiento minimalista estilo nanoGPT (Karpathy) en CPU — sin GPU.

Réplica de *forma* (bloques Transformer pequeños + loop de optimización), no de un
paper entero. Sirve como harness para interpretabilidad: podés inspeccionar
`.parameters()`, activaciones por capa o pesos de atención en un modelo chico.

Requisito: ``pip install torch`` (CPU wheel oficial).

Referencias de concepto: arXiv 1706.03762 (atención); repositorio educativo nanoGPT.
"""

from __future__ import annotations

import math
import sys


def main() -> None:
    try:
        import torch
        import torch.nn as nn
    except ImportError:
        print("Instalá PyTorch CPU: pip install torch", file=sys.stderr)
        sys.exit(1)

    torch.manual_seed(0)
    device = torch.device("cpu")

    # Hiperparámetros "nano": caben en RAM de cualquier laptop.
    vocab_size = 64
    block_size = 16
    n_embd = 64
    n_head = 4
    n_layer = 2
    batch_size = 4
    steps = 30
    lr = 3e-3

    class Head(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.key = nn.Linear(n_embd, n_embd // n_head, bias=False)
            self.query = nn.Linear(n_embd, n_embd // n_head, bias=False)
            self.value = nn.Linear(n_embd, n_embd // n_head, bias=False)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            b, t, c = x.shape
            k = self.key(x)
            q = self.query(x)
            v = self.value(x)
            dh = k.shape[-1]
            att = (q @ k.transpose(-2, -1)) / math.sqrt(float(dh))
            att = torch.softmax(att, dim=-1)
            return att @ v

    class Block(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.heads = nn.ModuleList([Head() for _ in range(n_head)])
            self.proj = nn.Linear(n_embd, n_embd)
            self.ln1 = nn.LayerNorm(n_embd)
            self.ff = nn.Sequential(
                nn.Linear(n_embd, 4 * n_embd),
                nn.GELU(),
                nn.Linear(4 * n_embd, n_embd),
            )
            self.ln2 = nn.LayerNorm(n_embd)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            h = torch.cat([h(x) for h in self.heads], dim=-1)
            x = self.ln1(x + self.proj(h))
            x = self.ln2(x + self.ff(x))
            return x

    class NanoGPT(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.wte = nn.Embedding(vocab_size, n_embd)
            self.wpe = nn.Embedding(block_size, n_embd)
            self.blocks = nn.ModuleList([Block() for _ in range(n_layer)])
            self.ln_f = nn.LayerNorm(n_embd)
            self.head = nn.Linear(n_embd, vocab_size, bias=False)

        def forward(self, idx: torch.Tensor) -> torch.Tensor:
            b, t = idx.shape
            pos = torch.arange(t, device=idx.device)
            x = self.wte(idx) + self.wpe(pos)
            for block in self.blocks:
                x = block(x)
            x = self.ln_f(x)
            return self.head(x)

    model = NanoGPT().to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr)

    # Datos sintéticos: predecir token+1 (tarea dummy solo para que baje loss).
    def batch() -> tuple[torch.Tensor, torch.Tensor]:
        x = torch.randint(0, vocab_size - 1, (batch_size, block_size), device=device)
        y = x + 1
        return x, y

    losses: list[float] = []
    for step in range(1, steps + 1):
        x, y = batch()
        logits = model(x)
        loss = torch.nn.functional.cross_entropy(
            logits.view(-1, vocab_size),
            y.view(-1),
        )
        opt.zero_grad()
        loss.backward()
        opt.step()
        losses.append(float(loss.item()))
        if step % 10 == 0 or step == 1:
            print(f"step {step:3d}  loss {loss.item():.4f}")

    n_params = sum(p.numel() for p in model.parameters())
    print(
        f"OK params ~{n_params:,} loss {losses[0]:.4f} -> {losses[-1]:.4f} (CPU). "
        "Next: add forward hooks on Block for attention/activations.",
    )


if __name__ == "__main__":
    main()
