# Corpus Generator Implementation Plan (learner sub-project 1)

> **Status: executed 2026-09-15** (commits 40191b9 … f656d60, each OTS-stamped). Every task's steps ran as written except the amendments noted inline (D3 rule on the pool; run-id pin computed; short windows at T < L; gate report key). Full suite on the committed tree: 502 passed, 5 slow deselected. Executed inline in the researcher's session; on main, as the house works.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the gated corpus generator of `docs/learner-corpus-generator-design-v0.1.md`, then produce the ten (40, 8, 2) looping-C1′ corpora (r0–r4 × ε ∈ {1, ½}) with committed manifests.

**Architecture:** A new package `yupi.corpus` (vocabulary, keyed rendering, window drawing + serialization, manifest, writer) sits on the world definition only (`simulator`, `interfaces`, `records`, `window`, `config`, `programs`); it never imports a posterior path. Two scripts drive it: `scripts/corpus_generate.py` (multiprocess by seed range, manifest-driven, byte-deterministic) and `scripts/corpus_gate.py` (gates 2–4 at C1 (8, 4, 2) against the exact pattern aggregate, writes a raw under `docs/`). Every gate that fits in seconds is a pytest; the 10⁶-window gate is `-m slow` plus a script whose raw is pinned.

**Tech Stack:** Python ≥ 3.14 via `uv run`; stdlib only for generation (`array`, `hmac`, `hashlib`, `json`, `random`, `struct`, `multiprocessing`); pytest. No PyTorch (enters with the trainer, sub-project 2).

**Spec:** `docs/learner-corpus-generator-design-v0.1.md` (design v0.1, decided 2026-09-13). Statute it implements: Part II §2(a) window protocol, Part II v0.2.9 Clause 4 keyed rendering, Part I D3 (pools) and D5 (fixed schema). Read the design first; this plan argues from it.

## Global Constraints

- **Window law (Part II §2(a), verbatim):** `T ~ Uniform{B, 2B, …, T_ep}`, `U = max(0, T − L)`; the window is `(O_0, O_1, …, O_T)` when `U = 0` and `(O_{U+1}, …, O_T)` when `U > 0`. RESET (`O_0`) is present iff `U = 0` and is not charged against `L`.
- **Rendering (v0.2.9 Clause 4):** injection σ per episode by a keyed generator; run key recorded; exactly uniform injection ("mod pool size, first unique" is biased and forbidden); translation table stored with the run and never in the model's context.
- **Pools (design §3, Part I D3):** threads 64, locks 32, devices 16, request ids 32; reserved trailing slices threads 8, locks 4, devices 2, request ids 4; every pool ≥ 8× its entity count and threads ≥ 50 (the rule is on the pool, reserved slice included: request ids have 32 tokens for 4 ids, 28 drawable — an execution-time correction of this plan's first wording, which put the rule on the drawable slice and refused the design's own pools).
- **Schema (design §2, Part I D5):** RESET is one token; every record is exactly five tokens `KIND ACTOR OBJECT RELATED LINEAGE`; masked field → `MASKED`; empty field → `NONE`; a window at `L` is at most `5·L + 1` tokens; vocabulary constant across rungs.
- **Vocabulary count correction:** design §4 says 157; the count from its own definition is **156** (9 event kinds including RESET + PAD + MASKED + NONE + 144 pool tokens; the design counted RESET twice). Task 7 records this in the design's ledger in place.
- **Refuse, never coerce (design §9):** every refusal names the statute line it enforces.
- **Determinism (design gate 1):** regenerating from a manifest is byte-identical, tables included, independent of worker count.
- **Firewall (instrument-status map):** `yupi.corpus` imports the world definition only. `enumerator`/`filter`/`window_process` appear only in `scripts/corpus_gate.py` and tests.
- **House rules (memory):** run `date` in the same command as any timestamp you write; never chain `git commit` after a check in one shell call; long-running raws go to `~/.cache/yupi-scratch/` or `docs/`, never only `/tmp`; the post-commit hook adds an `ots:` stamp commit after every commit (expected).
- **Commits:** the repo's git identity is `Project Yupi <yupi@wamason.com>` with signing on; commit only files the task names; end commit messages with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
- **Tests:** `uv run pytest -q` must stay green (464 + naming/corpus-track tests at handoff; record the count in Task 0). Slow tests are `@pytest.mark.slow` and excluded by default.

---

## File Structure

```
src/yupi/corpus/__init__.py      package doc; re-exports nothing (explicit imports only)
src/yupi/corpus/vocab.py         the 156-token vocabulary, ids, pool tokens, token typing
src/yupi/corpus/rendering.py     D3 check, keyed Fisher–Yates injection, EpisodeTable, render/unrender
src/yupi/corpus/windows.py       Window, keyed endpoint draw, draw_window, serialize/deserialize
src/yupi/corpus/manifest.py      Manifest + Split dataclasses, JSON, validate() with statute-named refusals
src/yupi/corpus/writer.py        write_split (multiprocess, byte-deterministic), read_split, generate()
scripts/corpus_generate.py       CLI: new run or regenerate from manifest; copies manifest to docs/corpus-manifests/
scripts/corpus_gate.py           gates 2, 3, 4 at C1 (8,4,2); raw to docs/corpus-gate-8-4-2-<date>.json
tests/test_corpus_vocab.py
tests/test_corpus_rendering.py
tests/test_corpus_windows.py
tests/test_corpus_manifest.py
tests/test_corpus_writer.py
tests/test_corpus_generate.py
tests/test_corpus_gate.py        slow gate at N = 10⁵ + fast pin of the committed raw
docs/corpus-manifests/           committed manifests (one per corpus run)
corpus/                          gitignored corpora
```

---

## Task 0: Baseline and scaffolding

**Files:**
- Modify: `pyproject.toml` (pytest markers)
- Modify: `.gitignore` (add `corpus/`)
- Create: `src/yupi/corpus/__init__.py`

- [ ] **Step 1: Record the suite baseline**

Run: `cd /home/tony/projects/yupi && uv run pytest -q 2>&1 | tail -3`
Expected: all passed; note the count N₀ (handoff says 464 plus the naming/corpus-track tests).

- [ ] **Step 2: Register the slow marker and exclude it by default**

Append to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = ["slow: gates that sample 10^5+ windows; run with -m slow"]
addopts = "-m 'not slow'"
```

- [ ] **Step 3: Gitignore corpora**

Append to `.gitignore`:

```
# generated corpora (design v0.1 §5): manifests are committed under docs/corpus-manifests/, data is not
corpus/
```

- [ ] **Step 4: Create the package**

`src/yupi/corpus/__init__.py`:

```python
"""Corpus generator (learner sub-project 1, design v0.1, 2026-09-13).

Windows are the corpus: one Part II §2(a) window per exact episode,
projected to a rung, rendered through a per-episode keyed injection
(v0.2.9 Clause 4), serialized as fixed five-token records (Part I D5).
Firewall: this package imports the world definition only (simulator,
interfaces, records, window, config, programs); no posterior path.
"""
```

- [ ] **Step 5: Re-run the suite to confirm the marker config changed nothing**

Run: `uv run pytest -q 2>&1 | tail -1`
Expected: same count N₀ passed.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml .gitignore src/yupi/corpus/__init__.py
git commit -m "Corpus generator: package scaffold, slow marker, corpus/ ignored (design v0.1 §5, §10)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

## Task 1: Vocabulary

**Files:**
- Create: `src/yupi/corpus/vocab.py`
- Test: `tests/test_corpus_vocab.py`

**Interfaces:**
- Produces: `KINDS`, `PAD`, `MASKED`, `NONE`, `RESET`, `ENTITY_TYPES`, `POOL_SIZES`, `RESERVED`, `VOCAB_VERSION`, `pool_tokens(entity_type) -> tuple[str, ...]`, `VOCAB: tuple[str, ...]`, `TOKEN_ID: dict[str, int]`, `token_type(tok) -> str` (one of `"pad" | "special" | "kind" | "thread" | "lock" | "device" | "request"`), `VOCAB_SHA256`.

- [ ] **Step 1: Write the failing test**

`tests/test_corpus_vocab.py`:

```python
"""Design v0.1 §4: one vocabulary for every corpus of the world, ids pinned."""
import hashlib

from yupi.corpus import vocab as V


PINNED_SHA256 = "ed9a50c5029403554cfe34d8d29758cad172f4414c2fcd06fb687f949a789604"


def test_vocabulary_is_pinned():
    # 9 kinds (RESET included) + PAD + MASKED + NONE + 64 + 32 + 16 + 32 pool tokens
    assert len(V.VOCAB) == 156                       # design §4 wrote 157: RESET counted twice (ledger, 2026-09-15)
    assert hashlib.sha256("\n".join(V.VOCAB).encode()).hexdigest() == PINNED_SHA256
    assert V.VOCAB_SHA256 == PINNED_SHA256
    assert V.VOCAB_VERSION == 1


def test_ids_and_specials():
    assert V.TOKEN_ID[V.PAD] == 0                    # padding is id 0 so a zeroed buffer is all-PAD
    assert len(set(V.VOCAB)) == len(V.VOCAB)
    assert all(V.VOCAB[V.TOKEN_ID[t]] == t for t in V.VOCAB)
    assert set(V.KINDS) == {"ACQUIRE", "BLOCK", "DISPATCH", "IDLE", "IO_COMPLETE",
                            "IO_ISSUE", "RELEASE", "RESET", "STEP"}     # Part II §4 schema
    assert max(V.TOKEN_ID.values()) < 2 ** 16       # uint16 token files (design §5)


def test_pools_and_types():
    assert V.POOL_SIZES == {"thread": 64, "lock": 32, "device": 16, "request": 32}
    assert V.RESERVED == {"thread": 8, "lock": 4, "device": 2, "request": 4}
    for et in V.ENTITY_TYPES:
        toks = V.pool_tokens(et)
        assert len(toks) == V.POOL_SIZES[et] and all(V.token_type(t) == et for t in toks)
    assert V.token_type(V.PAD) == "pad"
    assert V.token_type(V.MASKED) == "special" and V.token_type(V.NONE) == "special"
    assert V.token_type("RESET") == "kind" and V.token_type("IDLE") == "kind"
```

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest tests/test_corpus_vocab.py -q`
Expected: FAIL, `ImportError: cannot import name 'vocab'`.

- [ ] **Step 3: Implement**

`src/yupi/corpus/vocab.py`:

```python
"""Corpus vocabulary (design v0.1 §4; Part I D5: one schema, one vocabulary
across every rung and ε; a rung differs only in how many MASKED it emits).

Order is fixed and versioned: PAD (id 0), MASKED, NONE, the nine event kinds
of Part II §4 in sorted order (RESET among them — the RESET record is the
single token "RESET"), then the four pools. Pinned by tests/test_corpus_vocab.py.
"""
import hashlib

VOCAB_VERSION = 1

PAD, MASKED, NONE, RESET = "PAD", "MASKED", "NONE", "RESET"
KINDS = ("ACQUIRE", "BLOCK", "DISPATCH", "IDLE", "IO_COMPLETE", "IO_ISSUE",
         "RELEASE", "RESET", "STEP")                          # Part II §4, sorted

ENTITY_TYPES = ("thread", "lock", "device", "request")
POOL_SIZES = {"thread": 64, "lock": 32, "device": 16, "request": 32}   # design §3
RESERVED = {"thread": 8, "lock": 4, "device": 2, "request": 4}         # trailing slices, never drawn in training
_PREFIX = {"thread": "T", "lock": "L", "device": "D", "request": "R"}


def pool_tokens(entity_type: str) -> tuple:
    """The whole pool for an entity type, reserved slice last."""
    return tuple(f"{_PREFIX[entity_type]}{i:02d}" for i in range(POOL_SIZES[entity_type]))


def _build():
    toks = [PAD, MASKED, NONE, *KINDS]
    for et in ENTITY_TYPES:
        toks.extend(pool_tokens(et))
    return tuple(toks)


VOCAB = _build()
TOKEN_ID = {t: i for i, t in enumerate(VOCAB)}
VOCAB_SHA256 = hashlib.sha256("\n".join(VOCAB).encode()).hexdigest()

_TYPE = {PAD: "pad", MASKED: "special", NONE: "special"}
_TYPE.update({k: "kind" for k in KINDS})
for _et in ENTITY_TYPES:
    _TYPE.update({t: _et for t in pool_tokens(_et)})


def token_type(tok: str) -> str:
    """pad | special | kind | thread | lock | device | request. KeyError if unknown."""
    return _TYPE[tok]
```

- [ ] **Step 4: Run to verify it passes**

Run: `uv run pytest tests/test_corpus_vocab.py -q`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src/yupi/corpus/vocab.py tests/test_corpus_vocab.py
git commit -m "Corpus vocabulary pinned: 156 tokens (design §4 counted RESET twice), ids fixed, pools T/L/D/R with reserved slices

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

## Task 2: Keyed rendering

**Files:**
- Create: `src/yupi/corpus/rendering.py`
- Test: `tests/test_corpus_rendering.py`

**Interfaces:**
- Consumes: `vocab.pool_tokens`, `vocab.RESERVED`, `vocab.MASKED`, `vocab.NONE`; `yupi.records.Record`; `yupi.interfaces.MASKED` (same string `"MASKED"`).
- Produces:
  - `class RenderingRefused(ValueError)`
  - `d3_check(entity_type: str, n_entities: int, pool_size: int) -> None`
  - `injection(run_key: bytes, episode_id: int, entity_type: str, n_entities: int, lift_reservation: bool = False) -> tuple[str, ...]`
  - `@dataclass(frozen=True) EpisodeTable(episode_id: int, thread: tuple, lock: tuple, device: tuple, request: tuple)` with `draw(run_key, episode_id, cfg, lift_reservation=False)`, `inverse() -> dict[str, tuple[str, int]]`, `to_json() -> dict`, `from_json(d) -> EpisodeTable`
  - `render(rec: Record, table: EpisodeTable) -> tuple[str, str, str, str, str]`
  - `unrender(tokens: tuple, table: EpisodeTable) -> Record`

- [ ] **Step 1: Write the failing tests**

`tests/test_corpus_rendering.py`:

```python
"""v0.2.9 Clause 4 keyed rendering; Part I D3 pools; design v0.1 §3."""
import itertools
import math
from collections import Counter
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.corpus import rendering as R
from yupi.corpus import vocab as V
from yupi.interfaces import MASKED, project
from yupi.records import Record

KEY = bytes(range(32))


def test_injection_is_deterministic_in_key_and_episode():
    a = R.injection(KEY, 7, "thread", 4)
    assert a == R.injection(KEY, 7, "thread", 4)
    assert a != R.injection(bytes(32), 7, "thread", 4) or a != R.injection(KEY, 8, "thread", 4)
    assert len(a) == 4 and len(set(a)) == 4                    # an injection


def test_reserved_slice_is_never_drawn():
    reserved = set(V.pool_tokens("thread")[-V.RESERVED["thread"]:])
    for ep in range(2000):
        assert not reserved & set(R.injection(KEY, ep, "thread", 4))
    reserved_l = set(V.pool_tokens("lock")[-V.RESERVED["lock"]:])
    for ep in range(2000):
        assert not reserved_l & set(R.injection(KEY, ep, "lock", 2))


def test_d3_refusals_name_the_statute():
    with pytest.raises(R.RenderingRefused, match="Part I D3"):
        R.d3_check("thread", 4, 49)                            # ≥ 50 for ≤ 4 threads
    with pytest.raises(R.RenderingRefused, match="Part I D3"):
        R.d3_check("lock", 8, 63)                              # 8× entity count
    R.d3_check("thread", 4, 56)                                # the real drawable slice
    R.d3_check("device", 1, 14)


def test_partial_fisher_yates_is_uniform_exhaustively_on_a_small_pool():
    """Design §10: every injection of n=3 into a drawable slice of m=5 (60
    injections) over 10^5 keyed draws; chi-square below the 0.999 quantile
    (df=59, 98.3). The reserved tail (one token) never appears."""
    pool = ("a", "b", "c", "d", "e", "z")
    counts = Counter()
    for ep in range(100_000):
        inj = R._keyed_injection(KEY, ep, "small", pool, drawable=5, n_entities=3)
        assert "z" not in inj
        counts[inj] += 1
    expected = 100_000 / 60
    assert set(counts) == set(itertools.permutations(pool[:5], 3))
    chi2 = sum((c - expected) ** 2 / expected for c in counts.values())
    assert chi2 < 98.3, chi2


def test_episode_table_draw_inverse_json():
    cfg = WorldConfig.c1()
    t = R.EpisodeTable.draw(KEY, 11, cfg)
    assert len(t.thread) == 4 and len(t.lock) == 2 and len(t.device) == 1 and len(t.request) == cfg.req_pool
    inv = t.inverse()
    assert inv[t.thread[2]] == ("thread", 2) and inv[t.request[3]] == ("request", 3)
    assert R.EpisodeTable.from_json(t.to_json()) == t


@pytest.mark.parametrize("rung", ["r0", "r1", "r2", "r3", "r4"])
def test_render_unrender_round_trip_every_field_form(rung):
    cfg = WorldConfig.c1()
    t = R.EpisodeTable.draw(KEY, 3, cfg)
    recs = [
        Record("DISPATCH", 1, None, None, None),
        Record("BLOCK", 0, ("LOCK", 1), 2, None),
        Record("IO_ISSUE", 3, ("DEV", 0), None, 2),
        Record("IO_COMPLETE", 3, ("DEV", 0), None, 2),
        Record("IDLE", None, None, None, None),
        Record("RELEASE", 1, ("LOCK", 0), 0, None),
    ]
    for r in recs:
        p = project(r, rung)
        toks = R.render(p, t)
        assert len(toks) == 5 and toks[0] == r.kind
        assert all(V.token_type(x) in ("kind", "special", "thread", "lock", "device", "request") for x in toks)
        assert R.unrender(toks, t) == p


def test_render_masked_and_none_are_distinct_tokens():
    cfg = WorldConfig.c1()
    t = R.EpisodeTable.draw(KEY, 3, cfg)
    idle_r4 = R.render(project(Record("IDLE", None, None, None, None), "r4"), t)
    idle_r0 = R.render(project(Record("IDLE", None, None, None, None), "r0"), t)
    assert idle_r4 == ("IDLE", V.NONE, V.NONE, V.NONE, V.NONE)
    assert idle_r0 == ("IDLE", V.MASKED, V.MASKED, V.MASKED, V.MASKED)
```

- [ ] **Step 2: Run to verify they fail**

Run: `uv run pytest tests/test_corpus_rendering.py -q`
Expected: FAIL, `ImportError: cannot import name 'rendering'`.

- [ ] **Step 3: Implement**

`src/yupi/corpus/rendering.py`:

```python
"""Keyed rendering (Part II v0.2.9 Clause 4; design v0.1 §3; Part I D3).

σ is drawn per episode and entity type by HMAC-SHA256(run_key,
f"{episode_id}:{entity_type}") seeding random.Random, which drives a
partial Fisher–Yates over the pool's drawable (non-reserved) slice:
exactly uniform over injections under the idealized-key assumption;
randrange is unbiased (rejection over getrandbits); no modulo reduction.
The table is provenance beside the corpus, never inside it.
"""
from __future__ import annotations

import hashlib
import hmac
import random
from dataclasses import dataclass

from yupi.corpus.vocab import ENTITY_TYPES, MASKED, NONE, RESERVED, pool_tokens
from yupi.records import Record


class RenderingRefused(ValueError):
    """A D3 / design §3 refusal; the message names the statute line."""


def d3_check(entity_type: str, n_entities: int, drawable: int) -> None:
    """Part I D3: ≥ 50 tokens for ≤ 4 threads, others proportionally;
    design §3: every drawable slice ≥ 8× its entity count."""
    need = max(50 if entity_type == "thread" else 0, 8 * n_entities)
    if drawable < need:
        raise RenderingRefused(
            f"Part I D3 / design v0.1 §3: {entity_type} pool offers {drawable} drawable "
            f"tokens for {n_entities} entities; requires >= {need}")


def _seed(run_key: bytes, episode_id: int, label: str) -> int:
    return int.from_bytes(hmac.new(run_key, f"{episode_id}:{label}".encode(), hashlib.sha256).digest(), "big")


def _keyed_injection(run_key: bytes, episode_id: int, entity_type: str, pool: tuple,
                     drawable: int, n_entities: int) -> tuple:
    d3_check(entity_type, n_entities, drawable)
    rng = random.Random(_seed(run_key, episode_id, entity_type))
    slots = list(pool[:drawable])
    for i in range(n_entities):                     # partial Fisher–Yates: uniform injection
        j = rng.randrange(i, drawable)
        slots[i], slots[j] = slots[j], slots[i]
    return tuple(slots[:n_entities])


def injection(run_key: bytes, episode_id: int, entity_type: str, n_entities: int,
              lift_reservation: bool = False) -> tuple:
    pool = pool_tokens(entity_type)
    drawable = len(pool) - (0 if lift_reservation else RESERVED[entity_type])
    return _keyed_injection(run_key, episode_id, entity_type, pool, drawable, n_entities)


@dataclass(frozen=True)
class EpisodeTable:
    """(entity type, structural index) -> token for one episode."""
    episode_id: int
    thread: tuple
    lock: tuple
    device: tuple
    request: tuple

    @classmethod
    def draw(cls, run_key: bytes, episode_id: int, cfg, lift_reservation: bool = False) -> "EpisodeTable":
        n = {"thread": cfg.n_threads, "lock": cfg.n_locks, "device": cfg.n_devices, "request": cfg.req_pool}
        return cls(episode_id, *(injection(run_key, episode_id, et, n[et], lift_reservation) for et in ENTITY_TYPES))

    def inverse(self) -> dict:
        return {tok: (et, i) for et in ENTITY_TYPES for i, tok in enumerate(getattr(self, et))}

    def to_json(self) -> dict:
        return {"episode": self.episode_id, **{et: list(getattr(self, et)) for et in ENTITY_TYPES}}

    @classmethod
    def from_json(cls, d: dict) -> "EpisodeTable":
        return cls(d["episode"], *(tuple(d[et]) for et in ENTITY_TYPES))


def _tok(v, names: tuple) -> str:
    if v == MASKED:
        return MASKED
    if v is None:
        return NONE
    return names[v]


def render(rec: Record, table: EpisodeTable) -> tuple:
    """Five tokens: KIND ACTOR OBJECT RELATED LINEAGE (Part I D5)."""
    if rec.obj == MASKED:
        obj = MASKED
    elif rec.obj is None:
        obj = NONE
    else:
        kind, i = rec.obj
        obj = table.lock[i] if kind == "LOCK" else table.device[i]
    return (rec.kind, _tok(rec.actor, table.thread), obj,
            _tok(rec.related, table.thread), _tok(rec.lineage, table.request))


def _val(tok: str, inv: dict, expect: tuple):
    if tok == MASKED:
        return MASKED
    if tok == NONE:
        return None
    et, i = inv[tok]
    if et not in expect:
        raise ValueError(f"token {tok!r} is a {et}, expected one of {expect}")
    return i


def unrender(tokens: tuple, table: EpisodeTable) -> Record:
    """Inverse of render for this episode's table (structural, projected record)."""
    if len(tokens) != 5:
        raise ValueError("a record is exactly five tokens (Part I D5)")
    inv = table.inverse()
    kind, actor, obj, related, lineage = tokens
    if obj == MASKED:
        o = MASKED
    elif obj == NONE:
        o = None
    else:
        et, i = inv[obj]
        o = ("LOCK", i) if et == "lock" else ("DEV", i) if et == "device" else None
        if o is None:
            raise ValueError(f"OBJECT token {obj!r} is a {et}")
    return Record(kind, _val(actor, inv, ("thread",)), o,
                  _val(related, inv, ("thread",)), _val(lineage, inv, ("request",)))
```

- [ ] **Step 4: Run to verify they pass**

Run: `uv run pytest tests/test_corpus_rendering.py -q`
Expected: 11 passed (the parametrized round trip counts five).

- [ ] **Step 5: Commit**

```bash
git add src/yupi/corpus/rendering.py tests/test_corpus_rendering.py
git commit -m "Keyed rendering (v0.2.9 Clause 4): HMAC-seeded partial Fisher–Yates injections over the drawable slice, exhaustive uniformity on a 5-token pool, D3 refusals named, render/unrender round trip at every rung

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

## Task 3: Windows and serialization

**Files:**
- Create: `src/yupi/corpus/windows.py`
- Test: `tests/test_corpus_windows.py`

**Interfaces:**
- Consumes: `yupi.simulator.sample_episode(cfg, programs, horizon, seed)`, `yupi.interfaces.project`, `yupi.window.WindowLaw` (`endpoints()`, `offset(T)`), `rendering.render/unrender/EpisodeTable`, `vocab.RESET`.
- Produces:
  - `@dataclass(frozen=True) Window(episode_id: int, T: int, U: int, rung: str, records: tuple[Record, ...])`, property `reset -> bool`
  - `draw_endpoint(run_key: bytes, episode_id: int, law: WindowLaw) -> int`
  - `draw_window(cfg, programs, law, rung, run_key, episode_id) -> Window`
  - `serialize(window, table) -> tuple[str, ...]`
  - `deserialize(tokens, table) -> tuple[bool, tuple[Record, ...]]`
  - `max_tokens(law) -> int` (= `5 * law.L + 1`)

- [ ] **Step 1: Write the failing tests**

`tests/test_corpus_windows.py`:

```python
"""Part II §2(a): the window is the last L records ending on a bucket endpoint,
RESET present iff U = 0 and not charged against L; design v0.1 §2 serialization."""
from collections import Counter
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.corpus import windows as W
from yupi.corpus.rendering import EpisodeTable
from yupi.corpus.vocab import RESET
from yupi.interfaces import project
from yupi.programs import c1_prime_loop_programs, c1_programs
from yupi.simulator import sample_episode
from yupi.window import WindowLaw

KEY = bytes(range(32))
SMALL = WindowLaw(T_ep=8, L=4, B=2)
FROZEN = WindowLaw(T_ep=40, L=8, B=2)


def test_endpoint_is_on_the_grid_and_keyed():
    ends = set(SMALL.endpoints())
    assert all(W.draw_endpoint(KEY, e, SMALL) in ends for e in range(500))
    assert W.draw_endpoint(KEY, 5, SMALL) == W.draw_endpoint(KEY, 5, SMALL)


def test_reset_rule_for_every_endpoint_of_8_4_2():
    """Every endpoint T ∈ {2,4,6,8}: U = max(0, T−4); RESET iff U = 0."""
    cfg, progs = WorldConfig.c1(), c1_programs()
    seen = set()
    for ep in range(400):
        w = W.draw_window(cfg, progs, SMALL, "r4", KEY, ep)
        seen.add(w.T)
        assert w.U == max(0, w.T - 4) and w.reset == (w.U == 0)
        assert len(w.records) == w.T - w.U
        toks = W.serialize(w, EpisodeTable.draw(KEY, ep, cfg))
        assert (toks[0] == RESET) == w.reset
        assert len(toks) == 5 * (w.T - w.U) + (1 if w.reset else 0)   # design gate 5
    assert seen == {2, 4, 6, 8}


def test_window_is_the_episode_slice_projected():
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1, 2)), c1_prime_loop_programs()
    w = W.draw_window(cfg, progs, FROZEN, "r2", KEY, 42)
    ep = sample_episode(cfg, progs, 40, 42)
    assert w.records == tuple(project(r, "r2") for _, r in ep[w.U:w.T])
    assert len(w.records) == w.T - w.U <= 8      # T < L gives a short window with RESET (Part II §2(a))


@pytest.mark.parametrize("rung", ["r0", "r1", "r2", "r3", "r4"])
@pytest.mark.parametrize("law,progs,eps", [(SMALL, c1_programs(), Fraction(1)),
                                           (FROZEN, c1_prime_loop_programs(), Fraction(1, 2))])
def test_serialize_deserialize_round_trip(rung, law, progs, eps):
    cfg = WorldConfig.c1(epsilon=eps)
    for ep in range(200):
        w = W.draw_window(cfg, progs, law, rung, KEY, ep)
        t = EpisodeTable.draw(KEY, ep, cfg)
        toks = W.serialize(w, t)
        assert len(toks) <= W.max_tokens(law)
        assert W.deserialize(toks, t) == (w.reset, w.records)


def test_max_tokens():
    assert W.max_tokens(FROZEN) == 41 and W.max_tokens(SMALL) == 21
```

- [ ] **Step 2: Run to verify they fail**

Run: `uv run pytest tests/test_corpus_windows.py -q`
Expected: FAIL, `ImportError: cannot import name 'windows'`.

- [ ] **Step 3: Implement**

`src/yupi/corpus/windows.py`:

```python
"""One training example is one Part II §2(a) window of one exact episode
(design v0.1 §2). The episode's dynamics are seeded by the episode id
alone (the exact side can regenerate the episode from the seed); the
endpoint T is keyed like the injections, HMAC(run_key, f"{id}:endpoint"),
so everything an example depends on is fixed by (manifest, episode id).
"""
from __future__ import annotations

import hashlib
import hmac
import random
from dataclasses import dataclass

from yupi.corpus.rendering import EpisodeTable, render, unrender
from yupi.corpus.vocab import RESET
from yupi.interfaces import project
from yupi.records import Record
from yupi.simulator import sample_episode
from yupi.window import WindowLaw


@dataclass(frozen=True)
class Window:
    episode_id: int
    T: int
    U: int
    rung: str
    records: tuple          # projected structural records O_{U+1..T}

    @property
    def reset(self) -> bool:
        return self.U == 0


def draw_endpoint(run_key: bytes, episode_id: int, law: WindowLaw) -> int:
    """T ~ Uniform{B, 2B, …, T_ep} (Part II §2(a)); keyed, unbiased randrange."""
    seed = int.from_bytes(hmac.new(run_key, f"{episode_id}:endpoint".encode(), hashlib.sha256).digest(), "big")
    ends = list(law.endpoints())
    return ends[random.Random(seed).randrange(len(ends))]


def draw_window(cfg, programs, law: WindowLaw, rung: str, run_key: bytes, episode_id: int) -> Window:
    episode = sample_episode(cfg, programs, law.T_ep, episode_id)
    T = draw_endpoint(run_key, episode_id, law)
    U = law.offset(T)
    return Window(episode_id, T, U, rung, tuple(project(r, rung) for _, r in episode[U:T]))


def max_tokens(law: WindowLaw) -> int:
    """L records of five tokens plus RESET when U = 0 (design §2)."""
    return 5 * law.L + 1


def serialize(window: Window, table: EpisodeTable) -> tuple:
    out = [RESET] if window.reset else []
    for r in window.records:
        out.extend(render(r, table))
    return tuple(out)


def deserialize(tokens, table: EpisodeTable):
    """tokens -> (reset, projected structural records); inverse of serialize."""
    toks = list(tokens)
    reset = bool(toks) and toks[0] == RESET
    if reset:
        toks = toks[1:]
    if len(toks) % 5:
        raise ValueError("window body must be a whole number of five-token records (Part I D5)")
    return reset, tuple(unrender(tuple(toks[i:i + 5]), table) for i in range(0, len(toks), 5))
```

- [ ] **Step 4: Run to verify they pass**

Run: `uv run pytest tests/test_corpus_windows.py -q`
Expected: 14 passed.

- [ ] **Step 5: Commit**

```bash
git add src/yupi/corpus/windows.py tests/test_corpus_windows.py
git commit -m "Windows: Part II §2(a) draw (keyed endpoint, U = max(0, T−L), RESET iff U = 0), projection, five-token serialization with round trip at (8,4,2) and the frozen (40,8,2)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

## Task 4: Manifest with statute-named refusals

**Files:**
- Create: `src/yupi/corpus/manifest.py`
- Test: `tests/test_corpus_manifest.py`

**Interfaces:**
- Consumes: `vocab.VOCAB_VERSION, VOCAB_SHA256, POOL_SIZES, RESERVED`, `rendering.d3_check, RenderingRefused`, `yupi.window.WindowLaw`, `yupi.config.WorldConfig.c1`, `yupi.programs.programs_for`, `windows.max_tokens`.
- Produces:
  - `SCHEMA_VERSION = 1`, `GENERATOR_VERSION = "0.1.0"`, `RUNGS`
  - `class ManifestRefused(ValueError)`
  - `@dataclass(frozen=True) Split(name: str, seed_start: int, seed_end: int)` (half-open)
  - `@dataclass(frozen=True) Manifest(schema_version, generator_version, vocab_version, vocab_sha256, git_commit, config, programs, epsilon, queue_depth, completion_p, T_ep, L, B, rung, pools, reserved, lift_reservation, run_key_hex, splits, max_tokens, counts)` with `new(...)` factory, `name()`, `run_id()`, `run_key()`, `world() -> (cfg, programs)`, `law()`, `to_json()`, `from_json()`, `with_counts(counts)`
  - `validate(m: Manifest) -> None`

- [ ] **Step 1: Write the failing tests**

`tests/test_corpus_manifest.py`:

```python
"""Design v0.1 §5 manifest and §9 refusals (each names its statute line)."""
from fractions import Fraction

import pytest

from yupi.corpus import manifest as M
from yupi.corpus.vocab import VOCAB_SHA256

KEY = bytes(range(32))


def _m(**kw):
    base = dict(programs="c1prime-loop", epsilon=Fraction(1, 2), T_ep=40, L=8, B=2, rung="r1",
                run_key=KEY, splits=(M.Split("train", 0, 100), M.Split("val", 1_000_000, 1_000_010),
                                     M.Split("test", 2_000_000, 2_000_010)), git_commit="deadbeef")
    base.update(kw)
    return M.Manifest.new(**base)


def test_new_manifest_fields_and_names():
    m = _m()
    assert m.name() == "c1prime-loop-40-8-2-r1-eps1_2"
    assert m.run_id() == "630dcd2966c43366"          # sha256(bytes(range(32)))[:16], computed once at execution
    assert m.max_tokens == 41 and m.epsilon == "1/2" and m.completion_p == "1/3"
    assert m.vocab_sha256 == VOCAB_SHA256 and m.generator_version == M.GENERATOR_VERSION
    cfg, progs = m.world()
    assert cfg.epsilon == Fraction(1, 2) and len(progs) == 4
    assert m.law().endpoints() == range(2, 41, 2)
    M.validate(m)


def test_json_round_trip_preserves_everything():
    m = _m().with_counts({"train": 100, "val": 10, "test": 10})
    assert M.Manifest.from_json(m.to_json()) == m
    assert m.run_key() == KEY


def test_refusals_name_the_statute():
    with pytest.raises(M.ManifestRefused, match=r"Part II §4"):
        M.validate(_m(rung="r5"))
    with pytest.raises(M.ManifestRefused, match=r"Part II §2\(a\)"):
        M.validate(_m(L=7))
    with pytest.raises(M.ManifestRefused, match=r"Part II §2\(a\)"):
        M.validate(_m(T_ep=41))
    with pytest.raises(M.ManifestRefused, match=r"design v0.1 §3"):
        M.validate(_m(lift_reservation=True))          # a reserved token in a training corpus
    with pytest.raises(M.ManifestRefused, match=r"design v0.1 §6"):
        M.validate(_m(splits=(M.Split("train", 0, 100), M.Split("val", 50, 60))))
    bad = M.Manifest.from_json({**_m().to_json(), "generator_version": "0.0.9"})
    with pytest.raises(M.ManifestRefused, match=r"design v0.1 §9"):
        M.validate(bad)
    bad = M.Manifest.from_json({**_m().to_json(), "pools": {"thread": 48, "lock": 32, "device": 16, "request": 32}})
    with pytest.raises(M.ManifestRefused, match=r"Part I D3"):
        M.validate(bad)
```

- [ ] **Step 2: Run to verify they fail**

Run: `uv run pytest tests/test_corpus_manifest.py -q`
Expected: FAIL, `ImportError: cannot import name 'manifest'`.

- [ ] **Step 3: Implement**

`src/yupi/corpus/manifest.py`:

```python
"""The manifest is the record (design v0.1 §5): with it and the code at
its generator version, a corpus regenerates byte for byte. validate()
refuses, never coerces (§9); every refusal names its statute line.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, replace
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.corpus.rendering import RenderingRefused, d3_check
from yupi.corpus.vocab import ENTITY_TYPES, POOL_SIZES, RESERVED, VOCAB_SHA256, VOCAB_VERSION
from yupi.corpus.windows import max_tokens
from yupi.programs import programs_for
from yupi.window import WindowLaw

SCHEMA_VERSION = 1
GENERATOR_VERSION = "0.1.0"
RUNGS = ("r0", "r1", "r2", "r3", "r4")


class ManifestRefused(ValueError):
    """Design v0.1 §9: refuse, never coerce."""


@dataclass(frozen=True)
class Split:
    name: str
    seed_start: int     # episode ids [seed_start, seed_end)
    seed_end: int


@dataclass(frozen=True)
class Manifest:
    schema_version: int
    generator_version: str
    vocab_version: int
    vocab_sha256: str
    git_commit: str
    config: str
    programs: str
    epsilon: str
    queue_depth: int
    completion_p: str
    T_ep: int
    L: int
    B: int
    rung: str
    pools: dict
    reserved: dict
    lift_reservation: bool
    run_key_hex: str
    splits: tuple
    max_tokens: int
    counts: dict = field(default_factory=dict)

    @classmethod
    def new(cls, *, programs: str, epsilon: Fraction, T_ep: int, L: int, B: int, rung: str,
            run_key: bytes, splits: tuple, git_commit: str, queue_depth: int = 2,
            completion_p: Fraction = Fraction(1, 3), lift_reservation: bool = False) -> "Manifest":
        mt = max_tokens(WindowLaw(T_ep, L, B)) if (T_ep % B == 0 and L % B == 0) else 5 * L + 1
        return cls(SCHEMA_VERSION, GENERATOR_VERSION, VOCAB_VERSION, VOCAB_SHA256, git_commit,
                   "c1", programs, str(Fraction(epsilon)), queue_depth, str(Fraction(completion_p)),
                   T_ep, L, B, rung, dict(POOL_SIZES), dict(RESERVED), lift_reservation,
                   run_key.hex(), tuple(splits), mt)

    def name(self) -> str:
        return f"{self.programs}-{self.T_ep}-{self.L}-{self.B}-{self.rung}-eps{self.epsilon.replace('/', '_')}"

    def run_key(self) -> bytes:
        return bytes.fromhex(self.run_key_hex)

    def run_id(self) -> str:
        return hashlib.sha256(self.run_key()).hexdigest()[:16]

    def world(self):
        cfg = WorldConfig.c1(p=Fraction(self.completion_p), queue_depth=self.queue_depth,
                             epsilon=Fraction(self.epsilon))
        return cfg, programs_for(self.programs)

    def law(self) -> WindowLaw:
        return WindowLaw(self.T_ep, self.L, self.B)

    def with_counts(self, counts: dict) -> "Manifest":
        return replace(self, counts=dict(counts))

    def to_json(self) -> dict:
        d = self.__dict__.copy()
        d["splits"] = [s.__dict__ for s in self.splits]
        return d

    @classmethod
    def from_json(cls, d: dict) -> "Manifest":
        d = dict(d)
        d["splits"] = tuple(Split(**s) for s in d["splits"])
        return cls(**d)


def validate(m: Manifest) -> None:
    if m.rung not in RUNGS:
        raise ManifestRefused(f"Part II §4 projection table: unknown rung {m.rung!r}")
    if m.T_ep % m.B or m.L % m.B:
        raise ManifestRefused("Part II §2(a): T_ep and L must be multiples of the bucket size B")
    if m.generator_version != GENERATOR_VERSION or m.schema_version != SCHEMA_VERSION:
        raise ManifestRefused(f"design v0.1 §9: manifest generator {m.generator_version}/schema "
                              f"{m.schema_version} differs from the code's {GENERATOR_VERSION}/{SCHEMA_VERSION}")
    if m.vocab_version != VOCAB_VERSION or m.vocab_sha256 != VOCAB_SHA256:
        raise ManifestRefused("design v0.1 §4: vocabulary version/hash differs from the code's")
    if m.pools != POOL_SIZES or m.reserved != RESERVED:
        # pools are fixed by the vocabulary; a manifest asking for others cannot be honoured
        cfg, _ = m.world()
        n = {"thread": cfg.n_threads, "lock": cfg.n_locks, "device": cfg.n_devices, "request": cfg.req_pool}
        for et in ENTITY_TYPES:
            try:
                d3_check(et, n[et], m.pools.get(et, 0) - m.reserved.get(et, 0))
            except RenderingRefused as e:
                raise ManifestRefused(str(e)) from e
        raise ManifestRefused("design v0.1 §4: pools are fixed by the vocabulary; regenerate with the code's pools")
    if m.lift_reservation and any(s.name == "train" for s in m.splits):
        raise ManifestRefused("design v0.1 §3: the reserved slice is never drawn in a training corpus")
    spans = sorted((s.seed_start, s.seed_end, s.name) for s in m.splits)
    for (a0, a1, an), (b0, b1, bn) in zip(spans, spans[1:]):
        if b0 < a1:
            raise ManifestRefused(f"design v0.1 §6 / proposal §7.2: seed ranges overlap ({an}, {bn})")
    cfg, _ = m.world()
    n = {"thread": cfg.n_threads, "lock": cfg.n_locks, "device": cfg.n_devices, "request": cfg.req_pool}
    for et in ENTITY_TYPES:
        try:
            d3_check(et, n[et], m.pools[et] - (0 if m.lift_reservation else m.reserved[et]))
        except RenderingRefused as e:
            raise ManifestRefused(str(e)) from e
```

- [ ] **Step 4: Run to verify they pass**

Run: `uv run pytest tests/test_corpus_manifest.py -q`
Expected: 3 passed. The pin is sha256(bytes(range(32)))[:16] = 630dcd2966c43366, computed at execution time (the plan first carried a guessed value).

- [ ] **Step 5: Commit**

```bash
git add src/yupi/corpus/manifest.py tests/test_corpus_manifest.py
git commit -m "Corpus manifest: the record that regenerates a corpus (design §5); refusals name the statute (Part II §2(a)/§4, Part I D3, design §3/§6/§9)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

## Task 5: Writer — byte-deterministic, multiprocess

**Files:**
- Create: `src/yupi/corpus/writer.py`
- Test: `tests/test_corpus_writer.py`

**Interfaces:**
- Consumes: `manifest.Manifest/Split/validate`, `windows.draw_window/serialize/max_tokens`, `rendering.EpisodeTable`, `vocab.TOKEN_ID, VOCAB`.
- Produces:
  - `encode_window(m, episode_id) -> tuple[bytes, int, dict]` — (padded uint16-LE tokens, unpadded length, table json)
  - `write_split(m: Manifest, split: Split, out_dir: Path, workers: int = 1) -> int` (window count)
  - `read_split(out_dir: Path, name: str) -> list[tuple[tuple[int, ...], dict]]` — unpadded id tuples with their table lines
  - `generate(m: Manifest, root: Path, workers: int = 1) -> tuple[Path, Manifest]` — writes `manifest.json`, `vocab.json`, all splits; returns the corpus dir and the manifest with counts
  - File names: `<split>.tokens`, `<split>.index`, `<split>.table.jsonl`

- [ ] **Step 1: Write the failing tests**

`tests/test_corpus_writer.py`:

```python
"""Design v0.1 §5 layout, gate 1 determinism (worker-count invariant), read-back."""
import filecmp
import json
from fractions import Fraction
from pathlib import Path

from yupi.corpus import manifest as M
from yupi.corpus import writer as Wr
from yupi.corpus.rendering import EpisodeTable
from yupi.corpus.vocab import PAD, TOKEN_ID, VOCAB
from yupi.corpus.windows import deserialize, draw_window

KEY = bytes(range(32))


def _m(n=60):
    return M.Manifest.new(programs="c1", epsilon=Fraction(1), T_ep=8, L=4, B=2, rung="r3", run_key=KEY,
                          splits=(M.Split("train", 0, n), M.Split("val", 1_000_000, 1_000_000 + 12)),
                          git_commit="test")


def test_encode_window_layout():
    m = _m()
    blob, length, table = Wr.encode_window(m, 5)
    assert len(blob) == 2 * m.max_tokens and 0 < length <= m.max_tokens
    ids = list(memoryview(blob).cast("H"))               # host is little-endian; the writer forces LE
    assert all(i == TOKEN_ID[PAD] for i in ids[length:]) and TOKEN_ID[PAD] not in ids[:length]
    assert table["episode"] == 5 and table["T"] - table["U"] == length // 5 and set(table) >= {"thread", "lock", "device", "request"}


def test_generate_layout_counts_and_read_back(tmp_path):
    m = _m()
    d, m2 = Wr.generate(m, tmp_path, workers=1)
    assert d == tmp_path / m.name() / m.run_id()
    assert {p.name for p in d.iterdir()} == {"manifest.json", "vocab.json", "train.tokens", "train.index",
                                             "train.table.jsonl", "val.tokens", "val.index", "val.table.jsonl"}
    assert m2.counts == {"train": 60, "val": 12}
    assert json.loads((d / "manifest.json").read_text())["counts"] == m2.counts
    assert json.loads((d / "vocab.json").read_text()) == {t: i for i, t in enumerate(VOCAB)}
    rows = Wr.read_split(d, "train")
    assert len(rows) == 60
    cfg, progs = m.world()
    for (ids, table), ep in zip(rows, range(60)):
        t = EpisodeTable.from_json(table)
        w = draw_window(cfg, progs, m.law(), m.rung, KEY, ep)
        assert (table["T"], table["U"]) == (w.T, w.U)
        assert deserialize(tuple(VOCAB[i] for i in ids), t) == (w.reset, w.records)


def test_generation_is_byte_identical_across_runs_and_worker_counts(tmp_path):
    m = _m(n=97)
    a, _ = Wr.generate(m, tmp_path / "a", workers=1)
    b, _ = Wr.generate(m, tmp_path / "b", workers=4)
    for name in ("train.tokens", "train.index", "train.table.jsonl", "val.tokens", "val.index",
                 "val.table.jsonl", "manifest.json", "vocab.json"):
        assert filecmp.cmp(a / name, b / name, shallow=False), name
```

- [ ] **Step 2: Run to verify they fail**

Run: `uv run pytest tests/test_corpus_writer.py -q`
Expected: FAIL, `ImportError: cannot import name 'writer'`.

- [ ] **Step 3: Implement**

`src/yupi/corpus/writer.py`:

```python
"""Corpus files (design v0.1 §5): <split>.tokens is uint16 little-endian,
windows back to back each padded to max_tokens with PAD (id 0);
<split>.index is uint32 little-endian unpadded lengths; <split>.table.jsonl
is one JSON line per window's episode (episode id, T, U, the four
injections). Byte-deterministic given the manifest, for any worker count:
workers take contiguous seed ranges and the parent concatenates in order.
"""
from __future__ import annotations

import json
import struct
import sys
from multiprocessing import Pool
from pathlib import Path

from yupi.corpus.manifest import Manifest, Split, validate
from yupi.corpus.rendering import EpisodeTable
from yupi.corpus.vocab import TOKEN_ID, VOCAB
from yupi.corpus.windows import draw_window, serialize


def encode_window(m: Manifest, episode_id: int):
    """(padded uint16-LE token bytes, unpadded length, table json) for one episode."""
    cfg, progs = m.world()
    table = EpisodeTable.draw(m.run_key(), episode_id, cfg, m.lift_reservation)
    w = draw_window(cfg, progs, m.law(), m.rung, m.run_key(), episode_id)
    ids = [TOKEN_ID[t] for t in serialize(w, table)]
    length = len(ids)
    ids.extend([0] * (m.max_tokens - length))
    blob = struct.pack(f"<{m.max_tokens}H", *ids)
    return blob, length, {**table.to_json(), "T": w.T, "U": w.U}


def _chunk(args):
    m_json, start, end = args
    m = Manifest.from_json(m_json)
    toks, lens, lines = [], [], []
    for ep in range(start, end):
        blob, length, table = encode_window(m, ep)
        toks.append(blob)
        lens.append(length)
        lines.append(json.dumps(table, separators=(",", ":"), sort_keys=True))
    return b"".join(toks), struct.pack(f"<{len(lens)}I", *lens), "".join(l + "\n" for l in lines)


def write_split(m: Manifest, split: Split, out_dir: Path, workers: int = 1) -> int:
    n = split.seed_end - split.seed_start
    step = max(1, -(-n // max(1, workers * 4)))          # ~4 chunks per worker, contiguous, in order
    ranges = [(m.to_json(), s, min(s + step, split.seed_end)) for s in range(split.seed_start, split.seed_end, step)]
    if workers > 1 and len(ranges) > 1:
        with Pool(workers) as pool:
            parts = pool.map(_chunk, ranges)
    else:
        parts = [_chunk(r) for r in ranges]
    with open(out_dir / f"{split.name}.tokens", "wb") as ft, open(out_dir / f"{split.name}.index", "wb") as fi, \
            open(out_dir / f"{split.name}.table.jsonl", "w") as fj:
        for t, i, j in parts:
            ft.write(t); fi.write(i); fj.write(j)
    return n


def read_split(out_dir: Path, name: str):
    """[(unpadded token-id tuple, table dict)] in episode order."""
    raw = (out_dir / f"{name}.tokens").read_bytes()
    lens = list(struct.unpack(f"<{(out_dir / f'{name}.index').stat().st_size // 4}I",
                              (out_dir / f"{name}.index").read_bytes()))
    tables = [json.loads(l) for l in (out_dir / f"{name}.table.jsonl").read_text().splitlines()]
    mt = len(raw) // (2 * len(lens)) if lens else 0
    out = []
    for k, (length, table) in enumerate(zip(lens, tables)):
        ids = struct.unpack(f"<{mt}H", raw[2 * mt * k: 2 * mt * (k + 1)])
        out.append((ids[:length], table))
    return out


def generate(m: Manifest, root: Path, workers: int = 1):
    """Write the whole corpus under root/<name>/<run_id>/; returns (dir, manifest with counts)."""
    validate(m)
    d = Path(root) / m.name() / m.run_id()
    d.mkdir(parents=True, exist_ok=True)
    (d / "vocab.json").write_text(json.dumps({t: i for i, t in enumerate(VOCAB)}, indent=0, sort_keys=False) + "\n")
    counts = {s.name: write_split(m, s, d, workers) for s in m.splits}
    m2 = m.with_counts(counts)
    (d / "manifest.json").write_text(json.dumps(m2.to_json(), indent=2, sort_keys=True) + "\n")
    return d, m2
```

- [ ] **Step 4: Run to verify they pass**

Run: `uv run pytest tests/test_corpus_writer.py -q`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src/yupi/corpus/writer.py tests/test_corpus_writer.py
git commit -m "Corpus writer: uint16-LE padded windows, uint32 lengths, per-episode table lines; byte-identical across runs and worker counts (design gate 1); read-back round trip

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

## Task 6: `scripts/corpus_generate.py`

**Files:**
- Create: `scripts/corpus_generate.py`
- Create: `docs/corpus-manifests/README.md`
- Test: `tests/test_corpus_generate.py`

**Interfaces:**
- Consumes: `writer.generate`, `manifest.Manifest/Split/validate`.
- Produces: `main(argv: list[str]) -> int`; `default_splits(n_train, n_val, n_test) -> tuple[Split, ...]` (train `[0, n_train)`, val `[1_000_000, 1_000_000 + n_val)`, test `[2_000_000, 2_000_000 + n_test)`); `git_commit() -> str`.
- CLI:
  - new run: `uv run python scripts/corpus_generate.py --programs c1prime-loop --law 40 8 2 --rung r1 --eps 1/2 --train 200000 --val 10000 --test 10000 --workers 32 [--root corpus] [--run-key HEX] [--manifest-copy docs/corpus-manifests]`
  - regenerate: `uv run python scripts/corpus_generate.py --from-manifest docs/corpus-manifests/<file>.json [--root corpus] [--workers N]` (refuses on version mismatch via `validate`).

- [ ] **Step 1: Write the failing test**

`tests/test_corpus_generate.py`:

```python
"""The CLI writes a corpus and a committed-manifest copy; regenerating from
that copy is byte-identical (design gate 1)."""
import filecmp
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import corpus_generate as G  # noqa: E402


def test_cli_new_run_then_regenerate_from_manifest(tmp_path):
    root, copies = tmp_path / "corpus", tmp_path / "manifests"
    rc = G.main(["--programs", "c1", "--law", "8", "4", "2", "--rung", "r2", "--eps", "1",
                 "--train", "50", "--val", "5", "--test", "5", "--workers", "2",
                 "--root", str(root), "--run-key", "00" * 32, "--manifest-copy", str(copies)])
    assert rc == 0
    (copy,) = list(copies.glob("*.json"))
    m = json.loads(copy.read_text())
    assert m["counts"] == {"train": 50, "val": 5, "test": 5} and m["rung"] == "r2"
    d = next((root / "c1-8-4-2-r2-eps1").iterdir())          # the single run directory
    root2 = tmp_path / "corpus2"
    assert G.main(["--from-manifest", str(copy), "--root", str(root2), "--workers", "1"]) == 0
    d2 = next((root2 / "c1-8-4-2-r2-eps1").iterdir())
    for name in ("train.tokens", "train.index", "train.table.jsonl", "test.tokens", "manifest.json"):
        assert filecmp.cmp(d / name, d2 / name, shallow=False), name


def test_default_splits_are_disjoint_and_named():
    s = G.default_splits(200_000, 10_000, 10_000)
    assert [x.name for x in s] == ["train", "val", "test"]
    assert (s[0].seed_start, s[0].seed_end) == (0, 200_000)
    assert (s[1].seed_start, s[1].seed_end) == (1_000_000, 1_010_000)
    assert (s[2].seed_start, s[2].seed_end) == (2_000_000, 2_010_000)
```

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest tests/test_corpus_generate.py -q`
Expected: FAIL, `ModuleNotFoundError: corpus_generate`.

- [ ] **Step 3: Implement**

`scripts/corpus_generate.py`:

```python
"""Generate a corpus (design v0.1 §5–§7) or regenerate one from its manifest.

  new:  python scripts/corpus_generate.py --programs c1prime-loop --law 40 8 2 --rung r1 --eps 1/2 \
            --train 200000 --val 10000 --test 10000 --workers 32 [--root corpus] [--run-key HEX] \
            [--manifest-copy docs/corpus-manifests]
  again: python scripts/corpus_generate.py --from-manifest docs/corpus-manifests/<file>.json [--root corpus]

The run key is 32 random bytes unless given; it is provenance, recorded in
the manifest (the model never sees the table). The manifest copy under
docs/corpus-manifests/ is the committed record; corpus/ is gitignored.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

from yupi.corpus.manifest import Manifest, Split, validate
from yupi.corpus.writer import generate


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def default_splits(n_train: int, n_val: int, n_test: int):
    return (Split("train", 0, n_train), Split("val", 1_000_000, 1_000_000 + n_val),
            Split("test", 2_000_000, 2_000_000 + n_test))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from-manifest")
    ap.add_argument("--programs", default="c1prime-loop")
    ap.add_argument("--law", nargs=3, type=int, metavar=("T_EP", "L", "B"))
    ap.add_argument("--rung")
    ap.add_argument("--eps", default="1")
    ap.add_argument("--train", type=int, default=200_000)
    ap.add_argument("--val", type=int, default=10_000)
    ap.add_argument("--test", type=int, default=10_000)
    ap.add_argument("--run-key", help="hex; default os.urandom(32)")
    ap.add_argument("--root", default="corpus")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    ap.add_argument("--manifest-copy", default="docs/corpus-manifests")
    a = ap.parse_args(argv)

    if a.from_manifest:
        m = Manifest.from_json(json.loads(Path(a.from_manifest).read_text()))
    else:
        if not (a.law and a.rung):
            ap.error("--law and --rung are required for a new run")
        key = bytes.fromhex(a.run_key) if a.run_key else os.urandom(32)
        m = Manifest.new(programs=a.programs, epsilon=Fraction(a.eps), T_ep=a.law[0], L=a.law[1], B=a.law[2],
                         rung=a.rung, run_key=key, splits=default_splits(a.train, a.val, a.test),
                         git_commit=git_commit())
    validate(m)
    t0 = time.time()
    d, m2 = generate(m, Path(a.root), workers=a.workers)
    dt = time.time() - t0
    copy_dir = Path(a.manifest_copy)
    copy_dir.mkdir(parents=True, exist_ok=True)
    copy = copy_dir / f"{m2.name()}-{m2.run_id()}.json"
    copy.write_text(json.dumps(m2.to_json(), indent=2, sort_keys=True) + "\n")
    print(f"{m2.name()} run {m2.run_id()}: {m2.counts} windows in {dt:.1f}s -> {d}; manifest copy {copy}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

`docs/corpus-manifests/README.md`:

```markdown
# Corpus manifests

One JSON per corpus run, written by `scripts/corpus_generate.py`. The
manifest is the record (design v0.1 §5): with it and the code at its
`generator_version`, `scripts/corpus_generate.py --from-manifest <file>`
regenerates the corpus byte for byte (gate 1). Corpora themselves live
under `corpus/` (gitignored). The run key is provenance, not a secret
from us; the model never sees the renaming table.
```

- [ ] **Step 4: Run to verify it passes**

Run: `uv run pytest tests/test_corpus_generate.py -q`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/corpus_generate.py tests/test_corpus_generate.py docs/corpus-manifests/README.md
git commit -m "scripts/corpus_generate.py: new run or regenerate from a committed manifest (byte-identical), multiprocess by seed range; docs/corpus-manifests/ is the record

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

## Task 7: The gate script (design gates 2, 3, 4) and its tests

**Files:**
- Create: `scripts/corpus_gate.py`
- Test: `tests/test_corpus_gate.py`

**Interfaces:**
- Consumes: `writer.generate/read_split`, `manifest.Manifest/Split`, `rendering.EpisodeTable`, `windows.deserialize`, `vocab.VOCAB, pool_tokens, RESERVED`; exact side: `yupi.enumerator.paths`, `yupi.naming.pattern/quotient`, `yupi.queries.state_entropy_bits`, `yupi.window.WindowLaw/endpoint_prior`, `yupi.programs.c1_programs`.
- Produces: `exact_pattern_aggregate(cfg, progs, law, rung) -> dict[(reset, pattern_window), dict[(state, binding), Fraction]]`; `run_gate(eps, rung, n_windows, root, workers) -> dict` (the per-cell report); `main(argv) -> int`, writing `docs/corpus-gate-8-4-2-<YYYY-MM-DD>.json` and returning 1 if any gate fails.
- Gate definitions (stated here, enforced in code):
  - **G2 window law:** empirical class masses vs exact; `tv <= 2 * sqrt(K_exact / N)` where `K_exact` is the number of exact classes (207 at r1, 282 at r3/r4 — Task-time computed, not hard-coded); every exact class with mass ≥ 10⁻⁴ present; endpoint marginal chi-square over the four endpoints below 16.3 (df 3, 0.999); RESET frequency within `3·sqrt(0.25/N)` of ½.
  - **G3 rendering uniformity, real pool (amends design §8.3, which is infeasible per injection over 56·55·54·53 ≈ 8.8M injections at N = 10⁵):** per position `k ∈ {0..3}`, thread-token frequency over the 56 drawable tokens has chi-square below 98.4 (df 55, 0.9995); the (position 0, position 1) pair over 56·55 = 3080 cells has chi-square below 3400 (df 3079, ≈0.9999); no reserved token of any type appears in any table line. The exhaustive per-injection test lives in Task 2 on the small pool.
  - **G4 corpus-track reproduction:** `H(q | Πw)` estimated as `Σ_classes f̂_k · H(q | class_k)` with `f̂` empirical and `H(q | class_k)` from the exact aggregate, compared with the pinned values (ε=1: r1 0.6238, r3 0.4565; ε=½: r1 1.3078, r3 1.1287) within 0.01 bits at N = 10⁶ (0.03 at N = 10⁵).

- [ ] **Step 1: Write the failing tests**

`tests/test_corpus_gate.py`:

```python
"""Design v0.1 §8 gates 2–4 at C1 (8, 4, 2): slow at N = 10^5 per cell; the
script's committed raw at N = 10^6 is pinned once it exists (Task 8)."""
import sys
from fractions import Fraction
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import corpus_gate as Gt  # noqa: E402


def test_exact_pattern_aggregate_matches_the_lemma_construction():
    from yupi.config import WorldConfig
    from yupi.programs import c1_programs
    from yupi.window import WindowLaw
    agg = Gt.exact_pattern_aggregate(WorldConfig.c1(), c1_programs(), WindowLaw(8, 4, 2), "r1")
    assert len(agg) == 207
    assert sum((sum(v.values(), Fraction(0)) for v in agg.values()), Fraction(0)) == 1
    assert sum(m for (reset, _), v in agg.items() for m in v.values() if reset) == Fraction(1, 2)


@pytest.mark.slow
@pytest.mark.parametrize("eps,rung", [(Fraction(1), "r1"), (Fraction(1), "r3"), (Fraction(1, 2), "r1"),
                                      (Fraction(1, 2), "r3"), (Fraction(1), "r4")])
def test_gates_2_3_4_at_1e5(eps, rung, tmp_path):
    rep = Gt.run_gate(eps, rung, n_windows=100_000, root=tmp_path, workers=8, h_tol=0.03)
    assert rep["passed"], {k: v for k, v in rep.items() if k.startswith("g")}
```

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest tests/test_corpus_gate.py -q`
Expected: FAIL, `ModuleNotFoundError: corpus_gate`.

- [ ] **Step 3: Implement**

`scripts/corpus_gate.py`:

```python
"""Corpus generator gates 2–4 (design v0.1 §8) at C1 (8, 4, 2), c1 programs,
both statutory ε, rungs r1/r3 (the pinned corpus-track cells) and r4.

  python scripts/corpus_gate.py [--n 1000000] [--workers 32] [--root ~/.cache/yupi-scratch/corpus-gate]

Generates N windows per cell with the real pools through the writer, reads
them back, un-renames through the table, re-keys by Π (yupi.naming.pattern)
and compares with the exact pattern aggregate built from the enumerator's
paths (the construction of tests/test_naming_bridge.py). Writes
docs/corpus-gate-8-4-2-<date>.json; exit 1 if any gate fails.
"""
import argparse
import json
import math
import os
import subprocess
import sys
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path

from yupi.config import WorldConfig
from yupi.corpus.manifest import Manifest, Split
from yupi.corpus.rendering import EpisodeTable
from yupi.corpus.vocab import ENTITY_TYPES, RESERVED, VOCAB, pool_tokens
from yupi.corpus.windows import deserialize
from yupi.corpus.writer import generate, read_split
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.naming import pattern, quotient
from yupi.programs import c1_programs
from yupi.queries import state_entropy_bits
from yupi.window import WindowLaw, endpoint_prior

LAW = WindowLaw(8, 4, 2)
PINNED_HQ = {(Fraction(1), "r1"): 0.6238, (Fraction(1), "r3"): 0.4565,
             (Fraction(1, 2), "r1"): 1.3078, (Fraction(1, 2), "r3"): 1.1287}   # tests/test_naming_bridge.py


def exact_pattern_aggregate(cfg, progs, law, rung):
    """{(reset, Π(window)): {(state, binding): law mass}} — Fraction-exact."""
    w_T = endpoint_prior(law)
    agg = {}
    for T in law.endpoints():
        u = law.offset(T)
        for recs, prob, final in paths(cfg, progs, T):
            pw, order = pattern(tuple(project(r, rung) for r in recs[u:]))
            d = agg.setdefault((u == 0, pw), {})
            d[(final, order)] = d.get((final, order), Fraction(0)) + w_T * prob
    return agg


def _H(dist):
    tot = sum(dist.values(), Fraction(0))
    return state_entropy_bits({k: m / tot for k, m in dist.items()})


def _chi2(counts, n_cells, total):
    e = total / n_cells
    return sum((c - e) ** 2 / e for c in counts.values()) + (n_cells - len(counts)) * e


def run_gate(eps, rung, n_windows, root, workers, h_tol=0.01):
    cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
    key = bytes.fromhex("5b" * 32)                       # a fixed gate key; the gate is about the law, not the key
    m = Manifest.new(programs="c1", epsilon=eps, T_ep=8, L=4, B=2, rung=rung, run_key=key,
                     splits=(Split("gate", 0, n_windows),), git_commit="gate")
    t0 = time.time()
    d, _ = generate(m, Path(root) / f"eps{str(eps).replace('/', '_')}-{rung}", workers=workers)
    rows = read_split(d, "gate")
    exact = exact_pattern_aggregate(cfg, progs, LAW, rung)
    emp, ends, resets = Counter(), Counter(), 0
    pos = [Counter() for _ in range(cfg.n_threads)]
    pair = Counter()
    reserved = {tok for et in ENTITY_TYPES for tok in pool_tokens(et)[-RESERVED[et]:]}
    reserved_hits = 0
    for ids, table in rows:
        t = EpisodeTable.from_json(table)
        reset, recs = deserialize(tuple(VOCAB[i] for i in ids), t)
        pw, _ = pattern(recs)
        emp[(reset, pw)] += 1
        ends[table["T"]] += 1
        resets += reset
        for k, tok in enumerate(t.thread):
            pos[k][tok] += 1
        pair[(t.thread[0], t.thread[1])] += 1
        reserved_hits += sum(1 for et in ENTITY_TYPES for tok in getattr(t, et) if tok in reserved)
    N = len(rows)
    exact_mass = {k: float(sum(v.values(), Fraction(0))) for k, v in exact.items()}
    tv = 0.5 * (sum(abs(exact_mass.get(k, 0.0) - c / N) for k, c in emp.items())
                + sum(p for k, p in exact_mass.items() if k not in emp))
    tv_bound = 2 * math.sqrt(len(exact) / N)
    missing = [k for k, p in exact_mass.items() if p >= 1e-4 and k not in emp]
    unknown = [k for k in emp if k not in exact]
    end_chi2 = _chi2(ends, len(list(LAW.endpoints())), N)
    reset_dev = abs(resets / N - 0.5)
    drawable = 64 - RESERVED["thread"]
    pos_chi2 = [_chi2(c, drawable, N) for c in pos]
    pair_chi2 = _chi2(pair, drawable * (drawable - 1), N)
    hq_hat = 0.0                                          # Σ_k f̂_k · H(q | class k), beliefs exact, weights empirical
    for k, c in emp.items():
        if k not in exact:
            continue
        q = {}
        for (st, b), mass in exact[k].items():
            qq = quotient(st, b, cfg)
            q[qq] = q.get(qq, Fraction(0)) + mass
        hq_hat += (c / N) * _H(q)
    hq_pin = PINNED_HQ.get((eps, rung))
    rep = dict(eps=str(eps), rung=rung, N=N, seconds=round(time.time() - t0, 1),
               K_exact=len(exact), K_empirical=len(emp),
               g2_tv=tv, g2_tv_bound=tv_bound, g2_missing_above_1e-4=len(missing), g2_unknown_classes=len(unknown),
               g2_endpoint_chi2=end_chi2, g2_reset_dev=reset_dev, g2_reset_tol=3 * math.sqrt(0.25 / N),
               g3_pos_chi2=pos_chi2, g3_pair_chi2=pair_chi2, g3_reserved_hits=reserved_hits,
               g4_hq_hat=hq_hat, g4_hq_pinned=hq_pin, g4_tol=h_tol)
    rep["passed"] = (tv <= tv_bound and not missing and not unknown and end_chi2 < 16.3
                     and reset_dev <= rep["g2_reset_tol"] and all(c < 98.4 for c in pos_chi2)
                     and pair_chi2 < 3400 and reserved_hits == 0
                     and (hq_pin is None or abs(hq_hat - hq_pin) <= h_tol))
    return rep


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=1_000_000)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    ap.add_argument("--root", default=os.path.expanduser("~/.cache/yupi-scratch/corpus-gate"))
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    date = subprocess.check_output(["date", "+%Y-%m-%d"], text=True).strip()
    out = Path(a.out or f"docs/corpus-gate-8-4-2-{date}.json")
    cells = [(Fraction(1), "r1"), (Fraction(1), "r3"), (Fraction(1), "r4"), (Fraction(1, 2), "r1"), (Fraction(1, 2), "r3")]
    reports = [run_gate(eps, rung, a.n, a.root, a.workers) for eps, rung in cells]
    for r in reports:
        print(json.dumps(r, default=str))
    doc = dict(law="C1 (8,4,2) c1 programs", date=date, git=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
               n=a.n, cells=reports, all_passed=all(r["passed"] for r in reports))
    out.write_text(json.dumps(doc, indent=2, default=str) + "\n")
    print("ALL PASSED" if doc["all_passed"] else "GATE FAILED", "->", out)
    return 0 if doc["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the fast test, then the slow ones**

Run: `uv run pytest tests/test_corpus_gate.py -q`
Expected: 1 passed, 5 deselected.

Run: `uv run pytest tests/test_corpus_gate.py -m slow -q -x`
Expected: 5 passed (about 2–4 minutes with 8 workers). If a cell fails on `g4` only and the difference is under 0.03, the tolerance at N = 10⁵ is the issue, not the sampler: rerun that cell once at N = 3·10⁵ and, if it passes, keep the test at 10⁵ with `h_tol=0.05` and note the change in the commit message. Any `g2_unknown_classes > 0` or `g3_reserved_hits > 0` is a real bug: stop and debug (systematic-debugging skill).

- [ ] **Step 5: Commit**

```bash
git add scripts/corpus_gate.py tests/test_corpus_gate.py
git commit -m "Corpus gates 2–4 at C1 (8,4,2): empirical pattern-class masses vs the exact aggregate (TV bound 2·sqrt(K/N), every class ≥1e-4 present, endpoints uniform, RESET at 1/2), rendering marginals on the real pool, H(q|Πw) reproduced within tolerance; slow tests at 1e5

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

## Task 8: Run the gate at 10⁶, pin the raw

**Files:**
- Create: `docs/corpus-gate-8-4-2-<date>.json` (written by the script)
- Modify: `tests/test_corpus_gate.py` (append the pin)

- [ ] **Step 1: Run the gate to a persistent path (never only /tmp)**

Run (in the background, logging to a persistent path; note `date` in the same command):
```bash
mkdir -p ~/.cache/yupi-scratch/corpus-gate && cd /home/tony/projects/yupi && \
  (date; uv run python scripts/corpus_gate.py --n 1000000 --workers 32; date) \
  2>&1 | tee ~/.cache/yupi-scratch/corpus-gate/run-$(date +%Y-%m-%d).log
```
Expected: five cells, `ALL PASSED -> docs/corpus-gate-8-4-2-<date>.json`, about 5 minutes with 32 workers. If a gate fails, do not lower a bound; find out why (the bounds were set from expectation × 5, a failure is information).

- [ ] **Step 2: Append the pin test**

Append to `tests/test_corpus_gate.py` (fill the date from the file the script wrote; the numbers are read from the raw, so nothing is retyped):

```python
def test_committed_gate_raw_passed_at_1e6():
    """The committed raw of the 10^6-window gate run (design §8 gates 2–4)."""
    import json
    raws = sorted((Path(__file__).resolve().parents[1] / "docs").glob("corpus-gate-8-4-2-*.json"))
    assert raws, "no committed gate raw"
    doc = json.loads(raws[-1].read_text())
    assert doc["n"] == 1_000_000 and doc["all_passed"]
    cells = {(c["eps"], c["rung"]): c for c in doc["cells"]}
    assert set(cells) == {("1", "r1"), ("1", "r3"), ("1", "r4"), ("1/2", "r1"), ("1/2", "r3")}
    for c in cells.values():
        assert c["g2_tv"] <= c["g2_tv_bound"] and c["g2_missing_above_1e4"] == 0 and c["g2_unknown_classes"] == 0
        assert c["g3_reserved_hits"] == 0
        if c["g4_hq_pinned"] is not None:
            assert abs(c["g4_hq_hat"] - c["g4_hq_pinned"]) <= 0.01
```

- [ ] **Step 3: Run the fast tests**

Run: `uv run pytest tests/test_corpus_gate.py -q`
Expected: 2 passed, 5 deselected.

- [ ] **Step 4: Commit (separate call, after seeing the pass)**

```bash
git add docs/corpus-gate-8-4-2-*.json tests/test_corpus_gate.py
git commit -m "Corpus gate raw at 10^6 windows per cell, C1 (8,4,2): gates 2–4 pass on every cell (numbers in the raw); pinned by test

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

## Task 9: The ten (40, 8, 2) corpora and the design ledger

**Files:**
- Create: `docs/corpus-manifests/c1prime-loop-40-8-2-<rung>-eps<ε>-<run_id>.json` × 10 (written by the script)
- Modify: `docs/learner-corpus-generator-design-v0.1.md` §12 ledger (append only)
- Create: `docs/corpus-runs-40-8-2-2026-09-<dd>.md` (a short run note)

- [ ] **Step 1: Generate the ten corpora (one run key per corpus; the script draws it)**

```bash
cd /home/tony/projects/yupi && mkdir -p ~/.cache/yupi-scratch/corpus-runs && \
  (date; for eps in 1 1/2; do for r in r0 r1 r2 r3 r4; do \
     uv run python scripts/corpus_generate.py --programs c1prime-loop --law 40 8 2 --rung $r --eps $eps \
        --train 200000 --val 10000 --test 10000 --workers 32; done; done; date) \
  2>&1 | tee ~/.cache/yupi-scratch/corpus-runs/gen-40-8-2-$(date +%Y-%m-%d).log
```
Expected: ten lines `c1prime-loop-40-8-2-<r>-eps<ε> run <id>: {'train': 200000, 'val': 10000, 'test': 10000} windows in <t>s`, each under a minute with 32 workers; ten manifest copies under `docs/corpus-manifests/`.

- [ ] **Step 2: Verify one corpus regenerates byte for byte from its committed manifest**

```bash
cd /home/tony/projects/yupi && M=$(ls docs/corpus-manifests/c1prime-loop-40-8-2-r1-eps1_2-*.json | head -1) && \
  uv run python scripts/corpus_generate.py --from-manifest "$M" --root /home/tony/.cache/yupi-scratch/corpus-regen --workers 16 && \
  D=$(python3 -c "import json;m=json.load(open('$M'));print(m['programs']+'-40-8-2-'+m['rung']+'-eps'+m['epsilon'].replace('/','_')+'/'+__import__('hashlib').sha256(bytes.fromhex(m['run_key_hex'])).hexdigest()[:16])") && \
  for f in train.tokens train.index train.table.jsonl val.tokens test.tokens manifest.json; do cmp corpus/$D/$f /home/tony/.cache/yupi-scratch/corpus-regen/$D/$f && echo "identical $f"; done
```
Expected: six `identical` lines (gate 1 at the frozen law).

- [ ] **Step 3: Write the run note**

`docs/corpus-runs-40-8-2-<date>.md` (date from `date +%Y-%m-%d` in the same command that writes the file):

```markdown
# The ten (40, 8, 2) corpora — run note, <date>

Generated by `scripts/corpus_generate.py` at commit <git rev-parse HEAD> from
design v0.1: looping C1′, rungs r0–r4, ε ∈ {1, ½}; train 200,000 / val
10,000 / test 10,000 windows each (seed ranges [0, 2e5), [1e6, 1e6+1e4),
[2e6, 2e6+1e4)); one run key per corpus, recorded in its manifest under
`docs/corpus-manifests/`. Token files under `corpus/` (gitignored); 41
uint16 tokens per window, PAD = 0. Gate 1 checked on r1 ε=½ (six files
byte-identical on regeneration). Gates 2–4 hold at C1 (8, 4, 2)
(`docs/corpus-gate-8-4-2-<date>.json`); no gate is claimed at (40, 8, 2)
itself — the exact pattern aggregate there is the corpus-track re-keying
of the thirty artifacts and its comparison to these corpora is the
learner's evaluation, not this note's.

| corpus | run id | train windows | seconds |
| --- | --- | --- | --- |
| (one row per corpus from the generation log) |
```

- [ ] **Step 4: Append to the design's ledger (§12), preserving everything above it**

Append to `docs/learner-corpus-generator-design-v0.1.md`:

```markdown
- 2026-09-<dd> (implementation, plan `docs/superpowers/plans/2026-09-15-corpus-generator.md`):
  (a) §4's vocabulary count is **156**, not 157 — RESET was counted both as
  an event kind and as a special token; the pinned list has 9 kinds
  (RESET among them) + PAD + MASKED + NONE + 144 pool tokens. (b) §8.3 as
  written (per-injection uniformity over the real 56-token drawable slice)
  is infeasible at 10⁵ episodes (≈ 8.8M injections); implemented as
  per-position and first-pair marginal chi-square on the real pool plus the
  exhaustive per-injection test on a 5-token pool (`tests/test_corpus_rendering.py`).
  (c) The endpoint draw, which §2 left as "seeded", is keyed like the
  injections: HMAC(run_key, "<episode>:endpoint"); episode dynamics are
  seeded by the episode id alone so the exact side regenerates the episode
  without the key. (d) Each table line also carries T and U. (e) The
  committed manifest copies live under `docs/corpus-manifests/`.
```

- [ ] **Step 5: Run the whole suite**

Run: `uv run pytest -q 2>&1 | tail -1`
Expected: N₀ + 26 passed (the new fast tests), slow ones deselected.

- [ ] **Step 6: Commit (separate call, after the suite line is seen)**

```bash
git add docs/corpus-manifests/*.json docs/corpus-runs-40-8-2-*.md docs/learner-corpus-generator-design-v0.1.md
git commit -m "The ten (40,8,2) looping-C1′ corpora generated (r0–r4 × ε∈{1,½}; 200k/10k/10k windows each); manifests committed as the record; gate 1 checked on r1 ε=½; design v0.1 ledger: 156 tokens, gate-3 form, keyed endpoint, table fields

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

- [ ] **Step 7: Write the memory**

Call `remember(type="project", ...)` with the run date from `date`, the commit hash, the ten run ids, the gate raw's path, and the one-line state: "corpus generator built and gated; the ten corpora exist; next is the trainer design (sub-project 2), which starts with the prefix-ceiling note."

---

## Self-review (done at plan time)

**Spec coverage.** §2 window definition → Task 3 (`draw_window`, serialize, RESET rule test). §3 pools/keyed draw/table/request renaming → Task 2 (`injection`, `EpisodeTable`, reserved slices) and Task 5 (table beside the corpus). §4 vocabulary → Task 1 (count corrected to 156). §5 layout → Task 5 (`generate`) and Task 6 (manifest copies). §6 splits → Task 6 `default_splits`, Task 4 overlap refusal. §7 the ten corpora → Task 9. §8 gates: 1 → Tasks 5, 6, 9; 2, 3, 4 → Tasks 7–8; 5 → Tasks 2–3 round trips and the length rule test. §9 refusals → Task 4 (and D3 in Task 2). §10 TDD list → every task is test-first; the slow marker is Task 0. §11 out of scope respected: no trainer, no probes, no TIME_CLASS, no query targets, no lexical corpus (the reservation hook and its refusal exist).

**Placeholders.** None remain except the two dates and the run-id list that only exist after Tasks 8–9 run.

**Type consistency.** `EpisodeTable.draw(run_key, episode_id, cfg, lift_reservation)` used identically in Tasks 2, 5, 7. `draw_window(cfg, programs, law, rung, run_key, episode_id)` in Tasks 3, 5. `Manifest.new(programs=, epsilon=, T_ep=, L=, B=, rung=, run_key=, splits=, git_commit=, ...)` in Tasks 4, 5, 6, 7. `generate(m, root, workers) -> (dir, manifest)` in Tasks 5, 6, 7. `read_split(dir, name) -> [(ids, table)]` in Tasks 5, 7. `deserialize(tokens, table) -> (reset, records)` in Tasks 3, 5, 7. Table JSON keys: `episode, thread, lock, device, request, T, U` in Tasks 2, 5, 7.
