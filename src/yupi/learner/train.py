"""The training loop (trainer spec §2). Imports nothing from the exact side.

The learning-rate schedule is a function of the PLANNED run length
(epochs × steps per epoch), never of max_steps — max_steps only truncates —
so a run stopped and resumed follows the same schedule as one that ran
straight (the resume gate, tests/test_learner_train.py). The checkpoint
carries model, optimizer, step, epoch, position within the epoch's
permutation, and every RNG state; a resume refuses a config that differs
from the checkpoint's in anything but max_steps.
"""
import hashlib
import json
import math
import signal
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

from yupi.learner.checkpoint import load, rng_state, save_atomic, set_rng_state
from yupi.learner.data import batches, epoch_order, load_split
from yupi.learner.model import Decoder, ModelConfig, n_params


@dataclass
class TrainConfig:
    corpus_dir: str
    seed: int
    out_dir: str
    device: str = "cpu"
    batch_size: int = 256
    epochs: int = 10
    lr: float = 1e-3
    lr_min: float = 1e-4
    warmup: int = 500
    weight_decay: float = 0.1
    grad_clip: float = 1.0
    ckpt_every: int = 500
    val_every: int = 250
    max_steps: int | None = None
    model: ModelConfig = field(default_factory=ModelConfig)


def lr_at(step: int, planned: int, c: TrainConfig) -> float:
    """Linear warmup to c.lr, then cosine to c.lr_min over the planned run."""
    if step < c.warmup:
        return c.lr * (step + 1) / c.warmup
    p = min(1.0, (step - c.warmup) / max(1, planned - c.warmup))
    return c.lr_min + 0.5 * (c.lr - c.lr_min) * (1 + math.cos(math.pi * p))


def _optimizer(model, c):
    decay = [p for _, p in model.named_parameters() if p.ndim >= 2]
    no_decay = [p for _, p in model.named_parameters() if p.ndim < 2]
    return torch.optim.AdamW([{"params": decay, "weight_decay": c.weight_decay},
                              {"params": no_decay, "weight_decay": 0.0}], lr=c.lr, betas=(0.9, 0.95))


def val_loss(model, X, Y, M, device, bs=1024) -> float:
    was_training = model.training
    model.eval()
    tot, n = 0.0, 0
    with torch.no_grad():
        for i in range(0, len(X), bs):
            x, y, m = (torch.from_numpy(a[i:i + bs]).to(device) for a in (X, Y, M))
            tot += float(F.cross_entropy(model(x)[m], y[m], reduction="sum"))
            n += int(m.sum())
    if was_training:
        model.train()
    return tot / n


def _comparable(c: TrainConfig) -> dict:
    d = json.loads(json.dumps(asdict(c)))
    d.pop("max_steps")
    return d


def train(c: TrainConfig, resume: bool = False) -> dict:
    out = Path(c.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    if c.device.startswith("cuda"):
        # Spec §2 'Precision': deterministic algorithms on; the SDPA fused kernels' backward is not
        # deterministic, so attention runs on the math backend on GPU; cuBLAS needs a fixed workspace.
        import os
        os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
        torch.use_deterministic_algorithms(True)
        torch.backends.cuda.enable_flash_sdp(False)
        torch.backends.cuda.enable_mem_efficient_sdp(False)
        torch.backends.cuda.enable_math_sdp(True)
    torch.manual_seed(c.seed)
    np.random.seed(c.seed)
    X, Y, M, _ = load_split(c.corpus_dir, "train", c.model.n_pos)
    VX, VY, VM, _ = load_split(c.corpus_dir, "val", c.model.n_pos)
    steps_per_epoch = math.ceil(len(X) / c.batch_size)
    planned = c.epochs * steps_per_epoch
    total = planned if c.max_steps is None else min(planned, c.max_steps)
    model = Decoder(c.model).to(c.device)
    opt = _optimizer(model, c)
    step, epoch, pos = 0, 0, 0
    ck = load(out) if resume else None
    if resume and ck is None:
        raise RuntimeError(f"resume requested but {out / 'ckpt.pt'} does not exist")
    if ck is not None:
        if ck["config"] != _comparable(c):
            raise RuntimeError("resume refused: the config differs from the checkpoint's (only max_steps may change)")
        model.load_state_dict(ck["model"])
        opt.load_state_dict(ck["opt"])
        step, epoch, pos = ck["step"], ck["epoch"], ck["pos"]
        set_rng_state(ck["rng"])
    manifest = Path(c.corpus_dir) / "manifest.json"
    (out / "run.json").write_text(json.dumps(dict(
        asdict(c), corpus_manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),
        n_params=n_params(model), torch=torch.__version__, steps_per_epoch=steps_per_epoch,
        steps_planned=planned, steps_total=total, resumed_from_step=(ck["step"] if ck else None)), indent=2) + "\n")
    log = open(out / "log.jsonl", "a")

    def checkpoint():
        save_atomic(out, {"model": model.state_dict(), "opt": opt.state_dict(), "step": step, "epoch": epoch,
                          "pos": pos, "rng": rng_state(), "config": _comparable(c)})

    def on_term(signum, frame):
        checkpoint()
        log.write(json.dumps({"step": step, "event": "sigterm-checkpoint"}) + "\n")
        log.flush()
        sys.exit(0)

    previous = signal.signal(signal.SIGTERM, on_term)
    t0 = time.time()
    last = None
    model.train()
    try:
        while step < total:
            order = epoch_order(len(X), c.seed, epoch)
            batch_list = list(batches(order, c.batch_size))
            while pos < len(batch_list) and step < total:
                idx = batch_list[pos]
                for g in opt.param_groups:
                    g["lr"] = lr_at(step, planned, c)
                x, y, m = (torch.from_numpy(a[idx]).to(c.device) for a in (X, Y, M))
                loss = F.cross_entropy(model(x)[m], y[m])
                opt.zero_grad(set_to_none=True)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), c.grad_clip)
                opt.step()
                step += 1
                pos += 1
                last = loss.item()
                if step % c.val_every == 0 or step == total:
                    log.write(json.dumps({"step": step, "epoch": epoch, "train_loss": last,
                                          "val_loss": val_loss(model, VX, VY, VM, c.device),
                                          "lr": lr_at(step - 1, planned, c), "wall": time.time() - t0}) + "\n")
                    log.flush()
                if step % c.ckpt_every == 0:
                    checkpoint()
            if pos >= len(batch_list):
                epoch += 1
                pos = 0
        checkpoint()
    finally:
        signal.signal(signal.SIGTERM, previous)
        log.close()
    return {"step": step, "epoch": epoch, "train_loss": last, "val_loss": val_loss(model, VX, VY, VM, c.device),
            "wall": time.time() - t0, "n_params": n_params(model)}
