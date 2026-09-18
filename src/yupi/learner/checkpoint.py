"""Atomic checkpoints (trainer spec §2; the lease memo of 2026-09-15):
write ckpt.tmp, fsync, keep the previous ckpt.pt as ckpt.prev.pt, rename
tmp into place — the previous checkpoint is retained until the new one is
durable. RNG capture covers python, numpy, torch CPU and CUDA. Checkpoints
are this project's own files (optimizer state, RNG tuples, config dicts),
hence weights_only=False on load; never load a checkpoint from elsewhere.
Imports nothing from yupi.
"""
import os
import random
from pathlib import Path

import numpy as np
import torch


def save_atomic(run_dir, state: dict) -> Path:
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    tmp, cur, prev = run_dir / "ckpt.tmp", run_dir / "ckpt.pt", run_dir / "ckpt.prev.pt"
    with open(tmp, "wb") as f:
        torch.save(state, f)
        f.flush()
        os.fsync(f.fileno())
    if cur.exists():
        os.replace(cur, prev)
    os.replace(tmp, cur)
    return cur


def load(run_dir):
    p = Path(run_dir) / "ckpt.pt"
    return torch.load(p, weights_only=False, map_location="cpu") if p.exists() else None


def rng_state() -> dict:
    d = {"py": random.getstate(), "np": np.random.get_state(), "torch": torch.get_rng_state()}
    if torch.cuda.is_available():
        d["cuda"] = torch.cuda.get_rng_state_all()
    return d


def set_rng_state(d: dict) -> None:
    random.setstate(d["py"])
    np.random.set_state(d["np"])
    torch.set_rng_state(d["torch"])
    if "cuda" in d and torch.cuda.is_available():
        torch.cuda.set_rng_state_all(d["cuda"])
