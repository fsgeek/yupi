# Learner Trainer and Evaluator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `yupi.learner` — data framing, a ~0.85M-parameter decoder trained from scratch on the (40, 8, 2) window corpora, atomic checkpoint/resume, and the contract's evaluator — plus the prefix-length ceiling tables the corrected contract (v0.1.2) compares against.

**Architecture:** The exact side gains one function (a prefix-length variant of the window-process pass) so every per-position ceiling is a table, not a per-window filter. The learner is a torch package whose training modules import nothing from the exact side; only the evaluator does. Every number the evaluator emits is a per-window quantity with a mean, a standard deviation and a standard error.

**Tech Stack:** Python 3.14, torch 2.14 + numpy (optional group `learner`), pytest; the existing exact side (`yupi.window_process`, `yupi.naming`, `yupi.pattern_ceiling`, `yupi.corpus`).

**Spec:** `docs/superpowers/specs/2026-09-18-learner-trainer-design.md`; contract `docs/learner-model-vs-ceiling-contract-v0.1.md` (v0.1.2).

## Global Constraints

- Exact side stays exact: Fractions, no floats, two independent paths for every new posterior computation (`window_process` ⟂ `pattern_enumerator`); `window_process.py` must not import any enumerator or filter (existing firewall test).
- `yupi.learner.{data,model,train,checkpoint}` import from `yupi` only `yupi.corpus.vocab`, `yupi.corpus.writer`, `yupi.corpus.manifest`. Only `yupi.learner.evaluate` imports `yupi.naming`, `yupi.pattern_ceiling`, `yupi.corpus.rendering`, `yupi.corpus.windows`.
- Corpus vocabulary is pinned (156 tokens, PAD = 0). BOS is model-side index 156; the output head has 156 logits.
- One window per sequence, padded to 42 positions (BOS + 41); never packed.
- Refuse, never coerce: mismatched vocab hash, table/corpus mismatch, missing class, resume/manifest mismatch.
- Run tests with `uv run --extra learner pytest -q <file>`; the exact-side files run without the extra.
- Commit after each task; never chain `git commit` after an assertion in the same shell call.

---

### Task 1: Prefix-length aggregate and prefix ceiling tables

**Files:**
- Modify: `src/yupi/window_process.py` (add `prefix_law_aggregate`, `prefix_law_aggregates`)
- Modify: `src/yupi/pattern_ceiling.py` (`ceiling_table(..., prefix_len=None)`)
- Modify: `scripts/pattern_ceiling.py` (`--prefix K`; table file name gains `-k{K}`; gate uses `filter_pattern_window(..., prefix=True)` on the first K records of sampled test windows)
- Test: `tests/test_prefix_aggregate.py`

**Interfaces:**
- Produces: `prefix_law_aggregate(cfg, programs, law, k, rung, stats=None) -> {(reset, window_k): {state: mass}}` — records U+1..U+k, state S_{U+k}, mass Σ_{compatible T} P(T)·P(path); `prefix_law_aggregates(cfg, programs, law, k, rungs, stats=None) -> {rung: aggregate}` (one r4 recursion, projected); `ceiling_table(cfg, programs, law, rungs, stats=None, types=ENTITY_ORDER, prefix_len=None)`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_prefix_aggregate.py
"""Prefix-length variant of the window-process pass (contract v0.1.2): the
first k records of every window whose law window runs at least k records,
with the state after the k-th record; RESET prefixes weighted by the number
of open endpoints. Gated against pattern_enumerator's prefix path (re-keyed
by Π_all) and against the enumerator's canonical prefix aggregate, at
C1 (8,4,2), both ε, every rung, k = 1..L."""
from fractions import Fraction
import pytest
from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.naming import pattern_all
from yupi.pattern_ceiling import ceiling_table
from yupi.pattern_enumerator import pattern_aggregate_by_paths
from yupi.pattern_filter import filter_pattern_window, next_pattern_dist
from yupi.programs import c1_programs
from yupi.window import WindowLaw, endpoint_prior
from yupi.window_process import prefix_law_aggregate, prefix_law_aggregates, window_law_aggregate

LAW = WindowLaw(8, 4, 2)
RUNGS = ("r0", "r1", "r2", "r3", "r4")

def _canonical_prefix_by_paths(cfg, progs, law, k, rung):
    w_T = endpoint_prior(law); out = {}
    for T in law.endpoints():
        u = law.offset(T)
        if T - u < k: continue
        for recs, prob, final in paths(cfg, progs, u + k):
            key = (u == 0, tuple(project(r, rung) for r in recs[u:u + k]))
            d = out.setdefault(key, {}); d[final] = d.get(final, Fraction(0)) + w_T * prob
    return out

@pytest.mark.parametrize("eps", [Fraction(1), Fraction(1, 2)])
@pytest.mark.parametrize("k", [1, 2, 3, 4])
def test_prefix_aggregate_equals_paths(eps, k):
    cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
    aggs = prefix_law_aggregates(cfg, progs, LAW, k, RUNGS)
    for rung in RUNGS:
        assert aggs[rung] == _canonical_prefix_by_paths(cfg, progs, LAW, k, rung)
        assert aggs[rung] == prefix_law_aggregate(cfg, progs, LAW, k, rung)
    if k == LAW.L:   # at k = L the non-RESET classes coincide with the full-window aggregate's
        full = window_law_aggregate(cfg, progs, LAW, "r4")
        assert {kk: v for kk, v in aggs["r4"].items() if not kk[0]} == {kk: v for kk, v in full.items() if not kk[0]}

@pytest.mark.parametrize("eps", [Fraction(1), Fraction(1, 2)])
@pytest.mark.parametrize("k", [1, 3])
def test_prefix_ceiling_table_equals_prefix_filter(eps, k):
    cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
    tables = ceiling_table(cfg, progs, LAW, RUNGS, prefix_len=k)
    for rung in RUNGS:
        by_paths = pattern_aggregate_by_paths(cfg, progs, LAW, rung, prefix_len=k)
        assert set(tables[rung]) == set(by_paths)
        for (reset, pw), (mass, star) in tables[rung].items():
            post, m2 = filter_pattern_window(cfg, progs, LAW, list(pw), rung, reset, prefix=True)
            assert mass == m2 and star == next_pattern_dist(post, cfg, progs, rung)
```

- [ ] **Step 2: Run it** — `uv run pytest -q tests/test_prefix_aggregate.py` — expect ImportError on `prefix_law_aggregate`.

- [ ] **Step 3: Implement** in `window_process.py`, after `window_law_aggregate`:

```python
def prefix_law_aggregate(cfg, programs, law, k, rung, stats=None):
    """Prefix-length variant (learner contract v0.1.2): for every window
    with T − U ≥ k, the first k records U+1..U+k and the state S_{U+k}.
    Non-RESET: emit at t = U + k for every U > 0 on the grid (one T each).
    RESET: emit once at t = k with weight |{T on the grid: U(T) = 0, T ≥ k}|.
    Same recursion as window_law_aggregate with buffer length k."""
    if not 1 <= k <= law.L:
        raise ValueError("prefix length must lie in 1..L")
    w_T = endpoint_prior(law)
    emit = {}                                   # tick -> (reset, multiplicity)
    for T in law.endpoints():
        u = law.offset(T)
        if T - u < k: continue
        t = u + k
        reset, mult = emit.get(t, (u == 0, 0))
        emit[t] = (u == 0, mult + 1)
    states, records, moves = {}, {}, {}
    def canon_state(s): return states.setdefault(s, s)
    def moves_of(s):
        m = moves.get(s)
        if m is None:
            m = [(canon_state(tr.next_state), records.setdefault(r, r), p)
                 for tr, p in enabled(s, cfg, programs) for r in (project(record_of(tr), rung),)]
            moves[s] = m
        return m
    dist = {(canon_state(initial_state(cfg)), ()): Fraction(1)}
    agg = {}
    for t in range(1, max(emit) + 1):
        nxt, windows = {}, {}
        for (s, buf), mass in dist.items():
            for ns, r, p in moves_of(s):
                nb = buf + (r,)
                if len(nb) > k: nb = nb[-k:]
                key = (ns, windows.setdefault(nb, nb))
                nxt[key] = nxt.get(key, Fraction(0)) + mass * p
        dist = nxt
        if stats is not None:
            stats.setdefault("pairs_per_tick", []).append(len(dist))
        if t in emit:
            reset, mult = emit[t]
            for (s, buf), mass in dist.items():
                d = agg.setdefault((reset, buf), {})
                d[s] = d.get(s, Fraction(0)) + w_T * mult * mass
    if stats is not None:
        stats["max_pairs"] = max(stats["pairs_per_tick"]); stats["n_windows"] = len(agg)
    return agg


def prefix_law_aggregates(cfg, programs, law, k, rungs=("r0", "r1", "r2", "r3", "r4"), stats=None):
    fine = prefix_law_aggregate(cfg, programs, law, k, "r4", stats)
    out = {}
    for r in rungs:
        if r == "r4":
            out[r] = fine; continue
        coarse, records = {}, {}
        for (reset, win), joint in fine.items():
            key = (reset, tuple(records.setdefault(x, x) for x in (project(y, r) for y in win)))
            d = coarse.setdefault(key, {})
            for s, m in joint.items():
                d[s] = d.get(s, Fraction(0)) + m
        out[r] = coarse
    return out
```

Note the emission for a RESET prefix at t = k: `emit[k]` has `reset=True` iff `U(k) == 0`, i.e. k ≤ L, always true here; a non-RESET U with U + k == k is impossible (U > 0), so no tick mixes RESET and non-RESET.

In `pattern_ceiling.ceiling_table`, add `prefix_len=None` and use `prefix_law_aggregates(cfg, programs, law, prefix_len, rungs, stats)` when it is given. In `scripts/pattern_ceiling.py`, add `--prefix K` (default none), pass it through, name tables `...-k{K}.jsonl`, and in `gate_sample` truncate `recs[:K]` and call the filter with `prefix=True` when K is set (a test window shorter than K is skipped and counted in `too_short`).

- [ ] **Step 4: Run** the new test file plus `tests/test_window_process.py tests/test_pattern_ceiling.py` — expect all pass.

- [ ] **Step 5: Commit** — `git add src/yupi/window_process.py src/yupi/pattern_ceiling.py scripts/pattern_ceiling.py tests/test_prefix_aggregate.py`; message: "Prefix-length window-process aggregate and prefix ceiling tables (contract v0.1.2)…".

- [ ] **Step 6: Launch** the prefix tables for the frozen law in the background: for K in 1..7, `nohup uv run python scripts/pattern_ceiling.py 40 8 2 --prefix $K --gate-n 100 --raw docs/pattern-ceilings-40-8-2-k$K-2026-09-18.json > ~/.cache/yupi-scratch/ceilings/run-k$K-2026-09-18.log 2>&1` sequentially in one shell loop (one process at a time; ~9 min and ≤ 5 GB each).

---

### Task 2: Data framing (`yupi.learner.data`)

**Files:**
- Create: `src/yupi/learner/__init__.py` (empty), `src/yupi/learner/data.py`
- Test: `tests/test_learner_data.py`

**Interfaces:**
- Produces: `BOS = 156`, `SEQ = 42`; `frame(windows: list[tuple[int]]) -> (inputs np.int64[N,42], targets np.int64[N,42], mask np.bool_[N,42])`; `load_split(corpus_dir: Path, name: str) -> (inputs, targets, mask, tables: list[dict])`; `epoch_order(n: int, seed: int, epoch: int) -> np.ndarray` (a permutation, function of (seed, epoch)); `batches(order, batch_size) -> iterator of index arrays`.

- [ ] **Step 1: Failing test**

```python
# tests/test_learner_data.py
import numpy as np, pytest
pytest.importorskip("torch")
from yupi.corpus.vocab import TOKEN_ID, PAD
from yupi.learner.data import BOS, SEQ, frame, epoch_order, batches

def test_frame_bos_one_pad_target_and_mask():
    w = (TOKEN_ID["RESET"], TOKEN_ID["DISPATCH"], TOKEN_ID["T03"], TOKEN_ID["NONE"], TOKEN_ID["NONE"], TOKEN_ID["NONE"])
    x, y, m = frame([w])
    assert x.shape == y.shape == m.shape == (1, SEQ) and x.dtype == np.int64
    assert x[0, 0] == BOS and list(x[0, 1:7]) == list(w) and (x[0, 7:] == TOKEN_ID[PAD]).all()
    assert list(y[0, :6]) == list(w) and y[0, 6] == TOKEN_ID[PAD]        # the end-of-window target
    assert m[0, :7].all() and not m[0, 7:].any()                          # exactly len(w)+1 targets scored
    assert m.sum() == len(w) + 1

def test_epoch_order_is_a_seeded_permutation():
    a, b, c = epoch_order(1000, 7, 0), epoch_order(1000, 7, 0), epoch_order(1000, 7, 1)
    assert (a == b).all() and not (a == c).all() and sorted(a) == list(range(1000))
    bs = list(batches(a, 256))
    assert [len(x) for x in bs] == [256, 256, 256, 232] and np.concatenate(bs).tolist() == a.tolist()
```

- [ ] **Step 2: Run** — expect ModuleNotFoundError `yupi.learner`.

- [ ] **Step 3: Implement**

```python
# src/yupi/learner/data.py
"""Window corpus -> model tensors (spec §2 'Sequence framing'). Imports from
yupi only the corpus vocabulary and reader: this module must not be able to
see the exact side (spec §2 'Firewall')."""
from pathlib import Path
import numpy as np
from yupi.corpus.vocab import TOKEN_ID, PAD, VOCAB
from yupi.corpus.writer import read_split

BOS = len(VOCAB)          # 156: model-side input index, never a target
SEQ = 42                  # BOS + 41
PAD_ID = TOKEN_ID[PAD]    # 0

def frame(windows):
    n = len(windows)
    x = np.full((n, SEQ), PAD_ID, dtype=np.int64); y = np.full((n, SEQ), PAD_ID, dtype=np.int64)
    m = np.zeros((n, SEQ), dtype=bool)
    for i, w in enumerate(windows):
        L = len(w)
        if L > SEQ - 1: raise ValueError(f"window of {L} tokens exceeds {SEQ - 1}")
        x[i, 0] = BOS; x[i, 1:L + 1] = w
        y[i, :L] = w; y[i, L] = PAD_ID          # one end-of-window target
        m[i, :L + 1] = True
    return x, y, m

def load_split(corpus_dir, name):
    rows = read_split(Path(corpus_dir), name)
    x, y, m = frame([w for w, _ in rows])
    return x, y, m, [t for _, t in rows]

def epoch_order(n, seed, epoch):
    return np.random.default_rng([seed, epoch]).permutation(n)

def batches(order, batch_size):
    for i in range(0, len(order), batch_size):
        yield order[i:i + batch_size]
```

- [ ] **Step 4: Run** — pass. **Step 5: Commit.**

---

### Task 3: The decoder (`yupi.learner.model`)

**Files:** Create `src/yupi/learner/model.py`; Test `tests/test_learner_model.py`.

**Interfaces:** `ModelConfig(d_model=128, n_layer=4, n_head=4, d_mlp=512, n_pos=42, vocab_in=157, vocab_out=156)`; `Decoder(cfg)`; `forward(ids: LongTensor[N,T], return_hidden=False) -> logits FloatTensor[N,T,156]` or `(logits, hidden: list[Tensor[N,T,d]] of length n_layer+1)` (residual stream after embeddings and after each block); `n_params(model) -> int`.

- [ ] **Step 1: Failing test**

```python
# tests/test_learner_model.py
import pytest
torch = pytest.importorskip("torch")
from yupi.learner.model import Decoder, ModelConfig, n_params

def test_causal_and_shapes():
    torch.manual_seed(0)
    m = Decoder(ModelConfig()).eval()
    x = torch.randint(0, 157, (3, 42))
    with torch.no_grad():
        a, hs = m(x, return_hidden=True)
        x2 = x.clone(); x2[:, 20] = (x2[:, 20] + 1) % 157
        b = m(x2)
    assert a.shape == (3, 42, 156) and len(hs) == 5 and hs[0].shape == (3, 42, 128)
    assert torch.allclose(a[:, :20], b[:, :20]) and not torch.allclose(a[:, 20:], b[:, 20:])

def test_param_count_matches_arithmetic():
    cfg = ModelConfig()
    d, L, f = cfg.d_model, cfg.n_layer, cfg.d_mlp
    expect = 157 * d + 42 * d + L * (4 * d * d + 4 * d + 2 * d * f + f + d + 4 * d) + 2 * d + d * 156 + 156
    got = n_params(Decoder(cfg))
    assert abs(got - expect) / expect < 0.01 and 0.8e6 < got < 0.9e6
```

- [ ] **Step 2: Run** — expect ImportError. **Step 3: Implement**

```python
# src/yupi/learner/model.py
"""A small pre-LN decoder written out in full (spec §2: probes need the
residual stream per layer; every component from scratch and inspectable)."""
from dataclasses import dataclass
import math, torch, torch.nn as nn, torch.nn.functional as F

@dataclass
class ModelConfig:
    d_model: int = 128; n_layer: int = 4; n_head: int = 4; d_mlp: int = 512
    n_pos: int = 42; vocab_in: int = 157; vocab_out: int = 156

class Attention(nn.Module):
    def __init__(self, c):
        super().__init__(); self.h = c.n_head; self.qkv = nn.Linear(c.d_model, 3 * c.d_model); self.o = nn.Linear(c.d_model, c.d_model)
    def forward(self, x):
        N, T, D = x.shape
        q, k, v = self.qkv(x).view(N, T, 3, self.h, D // self.h).permute(2, 0, 3, 1, 4)
        y = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        return self.o(y.transpose(1, 2).reshape(N, T, D))

class Block(nn.Module):
    def __init__(self, c):
        super().__init__(); self.ln1 = nn.LayerNorm(c.d_model); self.attn = Attention(c)
        self.ln2 = nn.LayerNorm(c.d_model); self.mlp = nn.Sequential(nn.Linear(c.d_model, c.d_mlp), nn.GELU(), nn.Linear(c.d_mlp, c.d_model))
    def forward(self, x):
        x = x + self.attn(self.ln1(x)); return x + self.mlp(self.ln2(x))

class Decoder(nn.Module):
    def __init__(self, c: ModelConfig):
        super().__init__(); self.cfg = c
        self.tok = nn.Embedding(c.vocab_in, c.d_model); self.pos = nn.Embedding(c.n_pos, c.d_model)
        self.blocks = nn.ModuleList(Block(c) for _ in range(c.n_layer)); self.ln_f = nn.LayerNorm(c.d_model)
        self.head = nn.Linear(c.d_model, c.vocab_out)
        self.apply(self._init)
    @staticmethod
    def _init(m):
        if isinstance(m, (nn.Linear, nn.Embedding)): nn.init.normal_(m.weight, std=0.02)
        if isinstance(m, nn.Linear) and m.bias is not None: nn.init.zeros_(m.bias)
    def forward(self, ids, return_hidden=False):
        T = ids.shape[1]
        x = self.tok(ids) + self.pos(torch.arange(T, device=ids.device))
        hidden = [x]
        for b in self.blocks:
            x = b(x); hidden.append(x)
        logits = self.head(self.ln_f(x))
        return (logits, hidden) if return_hidden else logits

def n_params(model): return sum(p.numel() for p in model.parameters())
```

- [ ] **Step 4: Run** — pass (SDPA with `is_causal=True` is deterministic on CPU; on GPU the math kernel is forced by the trainer when determinism is on). **Step 5: Commit.**

---

### Task 4: Atomic checkpoints and the resume gate (`yupi.learner.checkpoint`)

**Files:** Create `src/yupi/learner/checkpoint.py`; Test `tests/test_learner_checkpoint.py`.

**Interfaces:** `save_atomic(run_dir: Path, state: dict) -> Path` (writes `ckpt.tmp`, fsync, renames existing `ckpt.pt` → `ckpt.prev.pt`, renames tmp → `ckpt.pt`); `load(run_dir) -> dict | None`; `rng_state() -> dict` / `set_rng_state(d)` (python, numpy, torch CPU, torch CUDA if available).

- [ ] **Step 1: Failing test**

```python
# tests/test_learner_checkpoint.py
import os, pytest
torch = pytest.importorskip("torch")
from yupi.learner.checkpoint import load, rng_state, save_atomic, set_rng_state

def test_atomic_save_keeps_previous_until_new_is_durable(tmp_path):
    save_atomic(tmp_path, {"step": 1}); save_atomic(tmp_path, {"step": 2})
    assert load(tmp_path)["step"] == 2 and torch.load(tmp_path / "ckpt.prev.pt", weights_only=False)["step"] == 1
    assert not (tmp_path / "ckpt.tmp").exists()

def test_rng_round_trip():
    s = rng_state(); a = torch.rand(3); set_rng_state(s); b = torch.rand(3)
    assert torch.equal(a, b)
```

- [ ] **Step 2: Run** — ImportError. **Step 3: Implement**

```python
# src/yupi/learner/checkpoint.py
"""Atomic checkpoints (spec §2 'Checkpoint / resume', the lease memo of
2026-09-15): tmp -> fsync -> previous kept as ckpt.prev.pt -> rename."""
import os, random
from pathlib import Path
import numpy as np, torch

def save_atomic(run_dir, state):
    run_dir = Path(run_dir); run_dir.mkdir(parents=True, exist_ok=True)
    tmp, cur, prev = run_dir / "ckpt.tmp", run_dir / "ckpt.pt", run_dir / "ckpt.prev.pt"
    with open(tmp, "wb") as f:
        torch.save(state, f); f.flush(); os.fsync(f.fileno())
    if cur.exists(): os.replace(cur, prev)
    os.replace(tmp, cur)
    return cur

def load(run_dir):
    p = Path(run_dir) / "ckpt.pt"
    return torch.load(p, weights_only=False, map_location="cpu") if p.exists() else None

def rng_state():
    d = {"py": random.getstate(), "np": np.random.get_state(), "torch": torch.get_rng_state()}
    if torch.cuda.is_available(): d["cuda"] = torch.cuda.get_rng_state_all()
    return d

def set_rng_state(d):
    random.setstate(d["py"]); np.random.set_state(d["np"]); torch.set_rng_state(d["torch"])
    if "cuda" in d and torch.cuda.is_available(): torch.cuda.set_rng_state_all(d["cuda"])
```

- [ ] **Step 4: Run** — pass. **Step 5: Commit.** (The resume gate itself is Task 5's test, since it needs the loop.)

---

### Task 5: The training loop and script (`yupi.learner.train`, `scripts/learner_train.py`)

**Files:** Create `src/yupi/learner/train.py`, `scripts/learner_train.py`; Test `tests/test_learner_train.py`.

**Interfaces:** `TrainConfig(corpus_dir: str, seed: int, out_dir: str, device: str = "cpu", batch_size: int = 256, epochs: int = 10, lr: float = 1e-3, lr_min: float = 1e-4, warmup: int = 500, weight_decay: float = 0.1, grad_clip: float = 1.0, ckpt_every: int = 500, val_every: int = 250, max_steps: int | None = None, model: ModelConfig = ModelConfig())`; `train(cfg: TrainConfig, resume: bool = False) -> dict` (final summary: step, train loss, val loss, wall); log file `<out>/log.jsonl` (one JSON per val or ckpt event); run manifest `<out>/run.json` (config, corpus manifest sha256, git commit, torch version, device); SIGTERM handler → checkpoint → `sys.exit(0)`.

- [ ] **Step 1: Failing tests** (a synthetic corpus: `frame`d random windows written through the real `corpus_generate` at C1 (8,4,2) with `--train 512 --val 64 --test 64` into `tmp_path` via `yupi.corpus.writer.generate`)

```python
# tests/test_learner_train.py
import json, pytest
torch = pytest.importorskip("torch")
from fractions import Fraction
from pathlib import Path
from yupi.corpus.manifest import Manifest, Split
from yupi.corpus.writer import generate
from yupi.learner.model import ModelConfig
from yupi.learner.train import TrainConfig, train

@pytest.fixture(scope="module")
def small_corpus(tmp_path_factory):
    root = tmp_path_factory.mktemp("corpus")
    m = Manifest.new(programs="c1", epsilon=Fraction(1), T_ep=8, L=4, B=2, rung="r4", run_key=b"\x01" * 32,
                     splits=(Split("train", 0, 512), Split("val", 1_000_000, 1_000_064), Split("test", 2_000_000, 2_000_064)), git_commit="test")
    d, _ = generate(m, root, workers=2)
    return d

def _cfg(small_corpus, out, **kw):
    base = dict(corpus_dir=str(small_corpus), seed=1, out_dir=str(out), batch_size=64, epochs=1, warmup=5,
                ckpt_every=10, val_every=10, model=ModelConfig(d_model=32, n_layer=1, n_head=2, d_mlp=64, n_pos=22))
    base.update(kw); return TrainConfig(**base)

def test_loss_falls_and_logs_parse(small_corpus, tmp_path):
    s = train(_cfg(small_corpus, tmp_path / "run", max_steps=30))
    log = [json.loads(l) for l in (tmp_path / "run" / "log.jsonl").read_text().splitlines()]
    assert s["step"] == 30 and log[-1]["val_loss"] < log[0]["val_loss"]
    assert json.loads((tmp_path / "run" / "run.json").read_text())["seed"] == 1

def test_resume_gate_bit_identical_on_cpu(small_corpus, tmp_path):
    straight = train(_cfg(small_corpus, tmp_path / "a", max_steps=20))
    train(_cfg(small_corpus, tmp_path / "b", max_steps=10, ckpt_every=10))
    resumed = train(_cfg(small_corpus, tmp_path / "b", max_steps=20, ckpt_every=10), resume=True)
    pa = torch.load(tmp_path / "a" / "ckpt.pt", weights_only=False)["model"]
    pb = torch.load(tmp_path / "b" / "ckpt.pt", weights_only=False)["model"]
    assert all(torch.equal(pa[k], pb[k]) for k in pa) and straight["step"] == resumed["step"] == 20
```

(`n_pos=22`: the (8,4,2) law's windows are ≤ 21 tokens; `frame` must take `seq_len` from the model config → give `frame(windows, seq_len=SEQ)` a parameter and have `load_split` accept it. Update Task 2's implementation accordingly: `frame(windows, seq_len=SEQ)`, `load_split(corpus_dir, name, seq_len=SEQ)`.)

- [ ] **Step 2: Run** — ImportError. **Step 3: Implement**

```python
# src/yupi/learner/train.py
"""The training loop (spec §2). Imports nothing from the exact side."""
import hashlib, json, math, signal, subprocess, sys, time
from dataclasses import asdict, dataclass, field
from pathlib import Path
import numpy as np, torch, torch.nn.functional as F
from yupi.learner.checkpoint import load, rng_state, save_atomic, set_rng_state
from yupi.learner.data import batches, epoch_order, load_split
from yupi.learner.model import Decoder, ModelConfig, n_params

@dataclass
class TrainConfig:
    corpus_dir: str; seed: int; out_dir: str; device: str = "cpu"
    batch_size: int = 256; epochs: int = 10; lr: float = 1e-3; lr_min: float = 1e-4; warmup: int = 500
    weight_decay: float = 0.1; grad_clip: float = 1.0; ckpt_every: int = 500; val_every: int = 250
    max_steps: int | None = None; model: ModelConfig = field(default_factory=ModelConfig)

def _lr(step, total, c):
    if step < c.warmup: return c.lr * (step + 1) / c.warmup
    p = min(1.0, (step - c.warmup) / max(1, total - c.warmup))
    return c.lr_min + 0.5 * (c.lr - c.lr_min) * (1 + math.cos(math.pi * p))

def _optimizer(model, c):
    decay = [p for n, p in model.named_parameters() if p.ndim >= 2]
    no = [p for n, p in model.named_parameters() if p.ndim < 2]
    return torch.optim.AdamW([{"params": decay, "weight_decay": c.weight_decay}, {"params": no, "weight_decay": 0.0}], lr=c.lr, betas=(0.9, 0.95))

def _loss(model, x, y, m):
    logits = model(x)
    return F.cross_entropy(logits[m], y[m])

def _val(model, X, Y, M, device, bs=1024):
    model.eval(); tot = 0.0; n = 0
    with torch.no_grad():
        for i in range(0, len(X), bs):
            x, y, m = (torch.from_numpy(a[i:i + bs]).to(device) for a in (X, Y, M))
            tot += float(F.cross_entropy(model(x)[m], y[m], reduction="sum")); n += int(m.sum())
    model.train(); return tot / n

def train(c: TrainConfig, resume: bool = False) -> dict:
    out = Path(c.out_dir); out.mkdir(parents=True, exist_ok=True)
    if c.device.startswith("cuda"):
        torch.use_deterministic_algorithms(True)
    torch.manual_seed(c.seed); np.random.seed(c.seed)
    X, Y, M, _ = load_split(c.corpus_dir, "train", c.model.n_pos); VX, VY, VM, _ = load_split(c.corpus_dir, "val", c.model.n_pos)
    steps_per_epoch = math.ceil(len(X) / c.batch_size); total = c.epochs * steps_per_epoch
    if c.max_steps is not None: total = min(total, c.max_steps)
    model = Decoder(c.model).to(c.device); opt = _optimizer(model, c)
    step, epoch, pos = 0, 0, 0
    ck = load(out) if resume else None
    if ck is not None:
        if ck["config"] != json.loads(json.dumps(asdict(c))): raise RuntimeError("resume refused: config differs from the checkpoint's")
        model.load_state_dict(ck["model"]); opt.load_state_dict(ck["opt"]); step, epoch, pos = ck["step"], ck["epoch"], ck["pos"]; set_rng_state(ck["rng"])
    manifest = Path(c.corpus_dir) / "manifest.json"
    (out / "run.json").write_text(json.dumps(dict(asdict(c), corpus_manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),
                                                  n_params=n_params(model), torch=torch.__version__, steps_total=total), indent=2))
    log = open(out / "log.jsonl", "a")
    def checkpoint():
        save_atomic(out, {"model": model.state_dict(), "opt": opt.state_dict(), "step": step, "epoch": epoch, "pos": pos, "rng": rng_state(), "config": asdict(c)})
    def on_term(signum, frame):
        checkpoint(); log.write(json.dumps({"step": step, "event": "sigterm-checkpoint"}) + "\n"); log.flush(); sys.exit(0)
    signal.signal(signal.SIGTERM, on_term)
    t0 = time.time(); last = None
    while step < total:
        order = epoch_order(len(X), c.seed, epoch)
        for idx in list(batches(order, c.batch_size))[pos:]:
            if step >= total: break
            for g in opt.param_groups: g["lr"] = _lr(step, total, c)
            x, y, m = (torch.from_numpy(a[idx]).to(c.device) for a in (X, Y, M))
            loss = _loss(model, x, y, m); opt.zero_grad(set_to_none=True); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), c.grad_clip); opt.step()
            step += 1; pos += 1; last = float(loss)
            if step % c.val_every == 0 or step == total:
                log.write(json.dumps({"step": step, "epoch": epoch, "train_loss": last, "val_loss": _val(model, VX, VY, VM, c.device), "lr": _lr(step - 1, total, c), "wall": time.time() - t0}) + "\n"); log.flush()
            if step % c.ckpt_every == 0: checkpoint()
        else:
            epoch += 1; pos = 0
    checkpoint()
    return {"step": step, "train_loss": last, "val_loss": _val(model, VX, VY, VM, c.device), "wall": time.time() - t0, "n_params": n_params(model)}
```

Script `scripts/learner_train.py`: argparse over `TrainConfig` fields (`--corpus-dir`, `--seed`, `--out`, `--device`, `--epochs`, `--batch-size`, `--max-steps`, `--resume`), calls `train`, prints the summary JSON.

- [ ] **Step 4: Run** the tests (CPU, seconds). The resume gate must pass bit-for-bit; if it does not, the cause is a state not captured (RNG, optimizer, data position) and must be fixed, never loosened to `allclose`.
- [ ] **Step 5: Commit.**

---

### Task 6: The evaluator core (`yupi.learner.evaluate`)

**Files:** Create `src/yupi/learner/evaluate.py`; Test `tests/test_learner_evaluate.py`.

**Interfaces:**
- `surface_pattern(tokens: tuple[str]) -> (reset: bool, records: tuple[Record])`: surface tokens → structural-looking records with **tokens** as entity values (`actor=tok`, `obj=("LOCK", tok)|("DEV", tok)`, `lineage=tok`; MASKED/NONE mapped), so `pattern_all` on them is Π of the window (invariant under σ).
- `field_ceiling(star: dict[Record, Fraction], realized: Record) -> list[Fraction]` — five conditionals $P^\star(\text{field}_j = \rho_j \mid \rho_{<j})$ from $P^\star(\Pi r)$ by marginalization (product = $P^\star(\rho)$).
- `field_model(logprobs: np.ndarray[5,156], realized_tokens: tuple[str], binding_tokens: dict[type, set[str]], realized_pattern: Record) -> (model_pattern_probs: list[float], model_token_probs: list[float], n_unused: list[int|None])` — for each field, $\tilde P_M$(pattern value) = sum of softmax over the consistent token set (bound → the one token; fresh → all drawable tokens of the type not yet used in the window or earlier in this record; KIND/MASKED/NONE → the one token), and $P_M$(realized token).
- `window_excess(...) -> dict(structural_bits, naming_bits, token_bits, kind_kl_bits, ceiling_token_bits)`.
- `evaluate(model_logprobs_fn, corpus_dir, table_by_k: dict[int, Table], k_list, n=None) -> dict` — per k: n windows, mean/sd/se of each excess, missing-class count; `model_logprobs_fn(inputs np.int64[N,T]) -> np.float64[N,T,156]` log-softmax (so a synthetic Bayes model and a uniform model plug in without torch).

- [ ] **Step 1: Failing tests** — using the Task 5 small corpus fixture and `ceiling_table(..., prefix_len=k)`:

```python
# tests/test_learner_evaluate.py  (key tests; the fixture as in Task 5 with rung r4, 300 test windows)
def test_synthetic_bayes_model_has_zero_excess(small_corpus):
    m = Manifest.from_json(json.loads((small_corpus / "manifest.json").read_text())); cfg, progs = m.world(); law = m.law()
    tables = {k: ceiling_table(cfg, progs, law, (m.rung,), prefix_len=k)[m.rung] for k in (1, 2, 3)}
    bayes = SyntheticBayes(tables, m)          # log-probs at every field from P* spread uniformly over unused tokens; the end-of-window term from pattern_end_probability
    r = evaluate(bayes.logprobs, small_corpus, tables, k_list=(1, 2, 3))
    for k in (1, 2, 3):
        assert abs(r[k]["structural_bits"]["mean"]) < 1e-9 and abs(r[k]["naming_bits"]["mean"]) < 1e-9 and r[k]["missing_classes"] == 0

def test_uniform_model_excess_equals_entropy_gap(small_corpus):
    ...  # uniform log-probs: token excess mean == log2(156) − mean ceiling token entropy (both from the same windows), to 1e-9; structural + naming == token per window

def test_kind_kl_nonnegative_and_structural_plus_naming_is_token(small_corpus):
    ...  # random logits model: per-window identity to 1e-9; kind_kl ≥ 0
```

- [ ] **Step 2: Run** — ImportError. **Step 3: Implement** the four functions above plus `SyntheticBayes` in the test module. Core of `window_excess`:

```python
def window_excess(lp5, toks_window, toks_next, star, used):        # lp5: [5,156] log-softmax at the five positions predicting toks_next
    """Field-chained, realized-record excesses in bits (contract v0.1.1 (a))."""
    reset, recs = surface_pattern(toks_window + toks_next)
    rho = pattern_all(recs)[0][-1]                                  # the realized next record's pattern values, in the window's binding
    ceil = field_ceiling(star, rho)                                  # five Fractions
    pm_pat, pm_tok, n_unused = field_model(lp5, toks_next, used, rho)
    structural = sum(math.log2(float(c)) - math.log2(p) for c, p in zip(ceil, pm_pat))
    naming = sum((-math.log2(n)) - (math.log2(pt) - math.log2(pp)) for n, pt, pp in zip(n_unused, pm_tok, pm_pat) if n is not None)
    ceiling_tok = -sum(math.log2(float(c)) for c in ceil) + sum(math.log2(n) for n in n_unused if n is not None)
    model_tok = -sum(math.log2(pt) for pt in pm_tok)
    kind_kl = sum(float(q) * (math.log2(float(q)) - lp5[0, TOKEN_ID[k]] / math.log(2)) for k, q in kind_marginal(star).items())
    return dict(structural_bits=structural, naming_bits=naming, token_bits=model_tok - ceiling_tok, kind_kl_bits=kind_kl, ceiling_token_bits=ceiling_tok)
```

with the identity `token_bits == structural_bits + naming_bits` holding algebraically (tested to 1e-9). `used` is the per-type set of tokens seen so far in the window (and, within the record, earlier fields), maintained by the caller; `n_unused` per type = drawable pool size − |used| (reserved slice excluded: 56 / 28 / 14 / 28).

- [ ] **Step 4: Run** — pass; the synthetic Bayes zero must be exact to 1e-9 or the projection is wrong. **Step 5: Commit.**

---

### Task 7: The evaluation script and the firewall test

**Files:** Create `scripts/learner_evaluate.py`; Test `tests/test_learner_firewall.py`.

- [ ] **Step 1: Firewall test**

```python
# tests/test_learner_firewall.py
import ast, pathlib
SRC = pathlib.Path(__file__).parent.parent / "src" / "yupi" / "learner"
BANNED = ("yupi.naming", "yupi.pattern_", "yupi.window", "yupi.kernel", "yupi.enumerator", "yupi.filter", "yupi.predict", "yupi.forecast", "yupi.simulator")
def _imports(p):
    return [n.module or "" for n in ast.walk(ast.parse(p.read_text())) if isinstance(n, ast.ImportFrom)] + \
           [a.name for n in ast.walk(ast.parse(p.read_text())) if isinstance(n, ast.Import) for a in n.names]
def test_training_modules_cannot_see_the_exact_side():
    for name in ("data", "model", "train", "checkpoint"):
        for mod in _imports(SRC / f"{name}.py"):
            assert not any(mod.startswith(b) for b in BANNED), (name, mod)
```

- [ ] **Step 2: Script** `scripts/learner_evaluate.py --run <dir> --tables-dir ~/.cache/yupi-scratch/ceilings --k 1,2,3,4,5,6,7 [--n N] --raw docs/learner-eval-<cell>-seed<s>-<date>.json`: loads the run's `run.json` and `ckpt.pt`, the corpus manifest (from `corpus_dir`), the prefix tables for the cell (`<programs>-<law>-<rung>-eps<ε>-k<K>.jsonl`, refusing if the table's law/rung/ε differ or a file is missing), builds `model_logprobs_fn` from the `Decoder` (batched, `torch.no_grad`, log-softmax in float64), runs `evaluate`, writes the raw with: git commit, checkpoint sha256, table sha256s, n, and per-k means/sd/se.

- [ ] **Step 3: Run** the firewall test and a smoke evaluation of the Task 5 test run against its small-law tables. **Step 4: Commit.**

---

### Task 8: The pilot

- [ ] Wait for the k=1..7 tables (Task 1 step 6) — check `docs/pattern-ceilings-40-8-2-k*-2026-09-18.json`: every gate `all_exact: true`, zero missing classes.
- [ ] Train r4 ε=1, seeds 1, 2, 3, CPU (`scripts/learner_train.py --corpus-dir corpus/c1prime-loop-40-8-2-r4-eps1/a2eb56c97be43778 --seed S --out ~/.cache/yupi-scratch/runs/r4-eps1-s$S`), in the background with logs beside the runs; or through the lease if the 4090 is free.
- [ ] Evaluate each; write `docs/learner-pilot-r4-eps1-2026-09-XX.md` with the between-seed sd of the mean structural excess at k = 7, the seed count it implies (contract §2.4), the per-k curve, the naming excess, and the end-of-window sanity check.
- [ ] Commit raws and note; record the state in memory.
