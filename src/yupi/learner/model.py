"""A small pre-LN decoder written out in full (trainer spec §2: probes need
the residual stream per layer; every component from scratch and
inspectable). forward(ids, return_hidden=True) returns the residual stream
after the embeddings and after each block. Imports nothing from yupi.
"""
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclass
class ModelConfig:
    d_model: int = 128
    n_layer: int = 4
    n_head: int = 4
    d_mlp: int = 512
    n_pos: int = 42          # BOS + 41
    vocab_in: int = 157      # 156 corpus tokens + BOS
    vocab_out: int = 156     # the corpus vocabulary; BOS is never predicted


class Attention(nn.Module):
    def __init__(self, c: ModelConfig):
        super().__init__()
        if c.d_model % c.n_head:
            raise ValueError("d_model must be divisible by n_head")
        self.h = c.n_head
        self.qkv = nn.Linear(c.d_model, 3 * c.d_model)
        self.o = nn.Linear(c.d_model, c.d_model)

    def forward(self, x):
        N, T, D = x.shape
        q, k, v = self.qkv(x).view(N, T, 3, self.h, D // self.h).permute(2, 0, 3, 1, 4)
        y = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        return self.o(y.transpose(1, 2).reshape(N, T, D))


class Block(nn.Module):
    def __init__(self, c: ModelConfig):
        super().__init__()
        self.ln1 = nn.LayerNorm(c.d_model)
        self.attn = Attention(c)
        self.ln2 = nn.LayerNorm(c.d_model)
        self.mlp = nn.Sequential(nn.Linear(c.d_model, c.d_mlp), nn.GELU(), nn.Linear(c.d_mlp, c.d_model))

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        return x + self.mlp(self.ln2(x))


class Decoder(nn.Module):
    def __init__(self, c: ModelConfig):
        super().__init__()
        self.cfg = c
        self.tok = nn.Embedding(c.vocab_in, c.d_model)
        self.pos = nn.Embedding(c.n_pos, c.d_model)
        self.blocks = nn.ModuleList(Block(c) for _ in range(c.n_layer))
        self.ln_f = nn.LayerNorm(c.d_model)
        self.head = nn.Linear(c.d_model, c.vocab_out)
        self.apply(self._init)

    @staticmethod
    def _init(m):
        if isinstance(m, (nn.Linear, nn.Embedding)):
            nn.init.normal_(m.weight, std=0.02)
        if isinstance(m, nn.Linear) and m.bias is not None:
            nn.init.zeros_(m.bias)

    def forward(self, ids, return_hidden: bool = False):
        T = ids.shape[1]
        if T > self.cfg.n_pos:
            raise ValueError(f"sequence of {T} positions exceeds n_pos={self.cfg.n_pos}")
        x = self.tok(ids) + self.pos(torch.arange(T, device=ids.device))
        hidden = [x]
        for b in self.blocks:
            x = b(x)
            hidden.append(x)
        logits = self.head(self.ln_f(x))
        return (logits, hidden) if return_hidden else logits


def n_params(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())
