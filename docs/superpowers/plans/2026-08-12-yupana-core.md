# Yupana Core Implementation Plan (Plan A of 3)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the Yupana world — state, transition kernel, simulator, content-rung projections — plus an independent exhaustive enumerator and an exact Bayes filter, validated bit-for-bit against each other on configuration C0a.

**Architecture:** One machine-readable transition kernel (`kernel.enabled()`) is the single source of dynamics; the simulator samples it, the enumerator unrolls it into a trajectory tree, and the filter folds it against observations. Enumerator and filter compute posteriors by *different algorithms* (path-summation vs. recursive update) and must agree exactly — that disagreement-detection is the validation strategy (Part II §6, "enumerator independence"). All probabilities are `fractions.Fraction`; floats never enter any computation.

**Tech Stack:** Python ≥3.14, stdlib only for core (`dataclasses`, `fractions`, `itertools`, `random`), pytest (already in pyproject), `uv run pytest` as the runner.

**Normative sources:** `docs/yupana-m1-spec-draft.md` (Part I, v0.2.3, commit `00ef2a7`); `docs/yupana-m1-part2-semantics-draft.md` (Part II, commit `1175412`). Section references below (§) are to Part II unless marked "Part I".

## Global Constraints

- Exact arithmetic everywhere: `Fraction` only; `float` in core modules is a defect (§6).
- One transition per tick; one canonical latent record per transition (Part I D8; §3).
- The kernel returns a *complete probability distribution* over next transitions; probabilities must sum to exactly `Fraction(1)` in every state (test-enforced invariant).
- Frozen/immutable state objects only — `State` must be hashable (posterior dicts key on it).
- Entity naming (σ, D3) is **out of scope for this plan**: core operates on canonical indices; σ is applied at corpus-generation time (Plan C).
- Scheduler: ε-mixture per Part I D9; ε and completion hazard p are `Fraction` config fields.
- Completion: queue-level hazard, `P(completion | n>0) = p`, discipline selects the departing request only (Part I D10, §3.4).
- Lock wake: FIFO with direct handoff (§3.5). Queue-full: block; wake-all on completion (§3.3).
- IDLE transitions when nothing else is enabled (§3.6).
- Python ≥3.14, `uv` project layout: code in `src/yupi/`, tests in `tests/`.

## File Structure

```
src/yupi/
  config.py       # WorldConfig + canonical C0a/C0b/C0c/C1 constructors
  state.py        # Status, State (frozen), invariant checks I1–I6
  programs.py     # Instr taxonomy, Program type, lock-order (I6) validator
  kernel.py       # Transition, enabled(state, cfg) -> [(Transition, Fraction)]
  records.py      # EventKind, Record (canonical latent record from a Transition)
  interfaces.py   # Rung, project(record, rung) -> ObsRecord (MASKED), k=1 ordered mode
  simulator.py    # sample_episode(cfg, seed, horizon) -> [(Transition, Record)]
  enumerator.py   # trajectory tree; posterior_by_paths(cfg, obs_seq, rung, t)
  filter.py       # Belief = dict[State, Fraction]; step(belief, obs, rung, cfg)
tests/
  test_state.py test_programs.py test_kernel.py test_records.py
  test_interfaces.py test_simulator.py test_enumerator.py test_filter.py
  test_c0a_validation.py
```

---

### Task 1: Config and state tuple with invariants

**Files:**
- Create: `src/yupi/config.py`, `src/yupi/state.py`
- Test: `tests/test_state.py`

**Interfaces:**
- Produces: `WorldConfig(n_threads, n_cpus, n_locks, n_devices, queue_depth, req_pool, completion_p: Fraction, epsilon: Fraction, discipline: str)` frozen dataclass with `c0a(p=Fraction(1,3))` classmethod (2 threads, 1 CPU, 1 lock, 1 device, depth 1, pool 2, ε=1, fifo).
- Produces: `Status` — tagged tuples: `RUNNABLE=("RUNNABLE",)`, `RUNNING=("RUNNING",)`, `("LOCK_BLOCKED", lock)`, `("IO_BLOCKED", reqid)`, `("QUEUE_BLOCKED", dev)`, `TERMINATED=("TERMINATED",)` (constructors `lock_blocked(l)`, `io_blocked(r)`, `queue_blocked(d)` in `state.py`).
- Produces: `State(pc: tuple[int,...], status: tuple[tuple,...], running: frozenset[int], lock_owner: tuple[int|None,...], lock_wq: tuple[tuple[int,...],...], dev_q: tuple[tuple[tuple[int,int],...],...], rr_cursor: int)` frozen dataclass; `initial_state(cfg) -> State` (§2: all RUNNABLE, pc 0, locks free, queues empty, cursor 0); `check_invariants(state, cfg) -> list[str]` returning violated-invariant names (empty = valid) for I1 (running set ↔ RUNNING status), I2 (each thread in at most one wait structure), I3 (owners not TERMINATED), I4 (in-flight reqids distinct), I5 (≤1 in-flight request per thread).

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_state.py
from fractions import Fraction
from yupi.config import WorldConfig
from yupi.state import State, initial_state, check_invariants, RUNNABLE

def test_c0a_config():
    cfg = WorldConfig.c0a()
    assert (cfg.n_threads, cfg.n_cpus, cfg.n_locks, cfg.n_devices) == (2, 1, 1, 1)
    assert cfg.queue_depth == 1 and cfg.req_pool == 2
    assert cfg.epsilon == Fraction(1) and cfg.discipline == "fifo"
    assert isinstance(cfg.completion_p, Fraction)

def test_initial_state_valid_and_hashable():
    cfg = WorldConfig.c0a()
    s = initial_state(cfg)
    assert s.pc == (0, 0) and s.status == (RUNNABLE, RUNNABLE)
    assert s.running == frozenset() and s.lock_owner == (None,)
    assert check_invariants(s, cfg) == []
    assert hash(s) == hash(initial_state(cfg))

def test_invariant_violation_detected():
    cfg = WorldConfig.c0a()
    s = initial_state(cfg)
    bad = State(pc=s.pc, status=s.status, running=frozenset({0}),  # 0 RUNNABLE but in running
                lock_owner=s.lock_owner, lock_wq=s.lock_wq, dev_q=s.dev_q, rr_cursor=0)
    assert "I1" in check_invariants(bad, cfg)
```

- [ ] **Step 2: Run tests to verify they fail** — `uv run pytest tests/test_state.py -v`; expected: ImportError / ModuleNotFoundError.
- [ ] **Step 3: Implement `config.py` and `state.py`** — frozen dataclasses exactly as in Interfaces; `check_invariants` iterates threads/locks/devices and appends `"I1"`…`"I5"` on violation (I6 lives in Task 2 with programs).
- [ ] **Step 4: Run tests to verify they pass** — `uv run pytest tests/test_state.py -v`.
- [ ] **Step 5: Commit** — `git add src/yupi/config.py src/yupi/state.py tests/test_state.py && git commit -m "feat(yupana): config + state tuple with invariants I1-I5"`

### Task 2: Programs, instruction taxonomy, I6 validator

**Files:**
- Create: `src/yupi/programs.py`
- Test: `tests/test_programs.py`

**Interfaces:**
- Produces: instruction constructors `COMPUTE=("COMPUTE",)`, `acquire(l)=("ACQUIRE",l)`, `release(l)=("RELEASE",l)`, `io(d)=("IO",d)`; `Program = tuple[tuple,...]`.
- Produces: `validate_lock_order(programs: tuple[Program,...]) -> bool` — True iff in every program, ACQUIRE lock indices between paired ACQUIRE/RELEASE are strictly increasing while held (I6: global-order discipline → no deadlock cycle).
- Produces: `c0a_programs() -> tuple[Program, Program]` — thread 0: `(acquire(0), COMPUTE, release(0), io(0))`; thread 1: `(COMPUTE, acquire(0), release(0))`. (Short enough that C0a's exhaustive tree stays small; exercises lock contention, blocking, I/O.)

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_programs.py
from yupi.programs import COMPUTE, acquire, release, io, validate_lock_order, c0a_programs

def test_c0a_programs_valid():
    progs = c0a_programs()
    assert len(progs) == 2 and validate_lock_order(progs)

def test_lock_order_violation():
    bad = ((acquire(1), acquire(0), release(0), release(1)),)  # 1 then 0: descending
    assert not validate_lock_order(bad)
```

- [ ] **Step 2: Run to verify failure** — `uv run pytest tests/test_programs.py -v`.
- [ ] **Step 3: Implement** — track a held-locks stack per program walk; a nested ACQUIRE with index ≤ max(held) fails.
- [ ] **Step 4: Run to verify pass.**
- [ ] **Step 5: Commit** — `git commit -m "feat(yupana): programs, instruction taxonomy, I6 lock-order validator"`

### Task 3: Kernel — enabled transitions with exact probabilities

**Files:**
- Create: `src/yupi/kernel.py`
- Test: `tests/test_kernel.py`

**Interfaces:**
- Consumes: `State`, `WorldConfig`, program constructors from Tasks 1–2 (`kernel` takes `programs` as an explicit argument everywhere: `enabled(state, cfg, programs)`).
- Produces: `Transition(kind: str, actor: int|None, obj: tuple[str,int]|None, related: int|None, lineage: int|None, next_state: State)` frozen dataclass; `kind ∈ {"COMPLETION","DISPATCH","STEP","ACQUIRE","BLOCK","RELEASE","IO_ISSUE","IDLE"}`.
- Produces: `enabled(state, cfg, programs) -> list[tuple[Transition, Fraction]]` implementing §3 exactly:
  - Stage A: if any device nonempty, completion branch with total probability `p`; the execution/IDLE branch gets `1−p` (or 1 if all queues empty).
  - Completion (§3.4): departing request = head (fifo) or each in-flight uniformly (stochastic, prob `p/n` each); issuer → RUNNABLE; all QUEUE_BLOCKED on that device → RUNNABLE (wake-all §3.3); `related=None`, `lineage=reqid`.
  - Stage B (§3.1–3.3): if `|running| < n_cpus` and a RUNNABLE thread exists → DISPATCH (ε-policy over runnable: uniform each with `ε/|runnable|`; round-robin pick with `1−ε` — cursor advances). Else execution step by ε-policy over `running`; executing thread runs its instruction: COMPUTE→STEP; ACQUIRE free→ACQUIRE (related=None) / held→BLOCK (related=owner, leaves running); RELEASE→RELEASE with FIFO direct handoff (related=woken head or None); IO with space→IO_ISSUE (lineage=lowest-free reqid, leaves running) / full→BLOCK with obj=("DEV",d); pc advances on non-blocking instructions; last instruction completed → TERMINATED, leaves running.
  - IDLE (§3.6): when neither branch has an enabled transition, `[(Transition("IDLE", None, None, None, None, state), 1−p·[n>0])]` — same state, self-loop.
  - **Every returned list's probabilities sum to exactly `Fraction(1)`.**

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_kernel.py
from fractions import Fraction
from yupi.config import WorldConfig
from yupi.state import initial_state, RUNNABLE
from yupi.programs import c0a_programs
from yupi.kernel import enabled

CFG, PROGS = WorldConfig.c0a(), c0a_programs()

def total(pairs): return sum(p for _, p in pairs)

def test_probabilities_always_sum_to_one():
    s = initial_state(CFG)
    frontier, seen = [s], set()
    for _ in range(200):  # BFS a few hundred reachable states
        if not frontier: break
        s = frontier.pop()
        if s in seen: continue
        seen.add(s)
        pairs = enabled(s, CFG, PROGS)
        assert total(pairs) == Fraction(1), s
        frontier.extend(t.next_state for t, _ in pairs)

def test_initial_step_is_dispatch():
    pairs = enabled(initial_state(CFG), CFG, PROGS)
    kinds = {t.kind for t, _ in pairs}
    assert kinds == {"DISPATCH"}          # empty device queue: no completion branch
    assert total(pairs) == Fraction(1)
    assert {t.actor for t, _ in pairs} == {0, 1}  # ε=1: uniform over both runnable

def test_lock_block_records_owner():
    # drive: dispatch t0, t0 acquires, dispatch t1, t1 steps COMPUTE, t1 tries acquire -> BLOCK related=0
    s = initial_state(CFG)
    def take(s, pred):
        (t,) = [t for t, _ in enabled(s, CFG, PROGS) if pred(t)]
        return t.next_state, t
    s, _ = take(s, lambda t: t.kind == "DISPATCH" and t.actor == 0)
    s, _ = take(s, lambda t: t.kind == "ACQUIRE")
    s, _ = take(s, lambda t: t.kind == "DISPATCH")
    s, _ = take(s, lambda t: t.kind == "STEP" and t.actor == 1)
    s, blk = take(s, lambda t: t.kind == "BLOCK" and t.actor == 1)
    assert blk.related == 0 and blk.obj == ("LOCK", 0)
```

- [ ] **Step 2: Run to verify failure.** — `uv run pytest tests/test_kernel.py -v`
- [ ] **Step 3: Implement `kernel.py`** — pure functions building next `State` via `dataclasses.replace`; helper `_epsilon_policy(candidates, cursor, eps) -> list[(choice, Fraction, new_cursor)]`; completion branch prepended when any `dev_q` nonempty. Merge duplicate (transition, prob) pairs by summing probabilities (ε-policy can select the same thread via both mixture components).
- [ ] **Step 4: Run to verify pass.**
- [ ] **Step 5: Commit** — `git commit -m "feat(yupana): transition kernel — exact distribution over next transitions"`

### Task 4: Canonical records

**Files:**
- Create: `src/yupi/records.py`
- Test: `tests/test_records.py`

**Interfaces:**
- Consumes: `Transition` (Task 3).
- Produces: `Record(kind: str, actor: int|None, obj: tuple[str,int]|None, related: int|None, lineage: int|None)` frozen dataclass; `record_of(t: Transition) -> Record` (field-for-field; RESET handled by corpus layer in Plan C — not a kernel transition).

- [ ] **Step 1: Failing test**

```python
# tests/test_records.py
from yupi.records import record_of, Record
from yupi.kernel import Transition
from yupi.config import WorldConfig
from yupi.state import initial_state

def test_record_mirrors_transition_fields():
    s = initial_state(WorldConfig.c0a())
    t = Transition("IO_ISSUE", 1, ("DEV", 0), None, 0, s)
    assert record_of(t) == Record("IO_ISSUE", 1, ("DEV", 0), None, 0)
```

- [ ] **Step 2: Run, verify failure. Step 3: Implement. Step 4: Run, verify pass.**
- [ ] **Step 5: Commit** — `git commit -m "feat(yupana): canonical latent records"`

### Task 5: Content-rung projections (ordered, k=1)

**Files:**
- Create: `src/yupi/interfaces.py`
- Test: `tests/test_interfaces.py`

**Interfaces:**
- Consumes: `Record` (Task 4).
- Produces: `MASKED = "MASKED"`; `Rung` — `r1`/`r2`/`r3`/`r4` (Part II §4 projection table: r1 keeps kind+actor; r2 +obj; r3 +related; r4 +lineage); `ObsRecord` — same shape as `Record` with masked fields set to `MASKED`; `project(record, rung) -> ObsRecord`. Deterministic, per-record (k=1 ordered mode; buckets/shuffle are Plan B).

- [ ] **Step 1: Failing test**

```python
# tests/test_interfaces.py
from yupi.records import Record
from yupi.interfaces import project, MASKED

REC = Record("BLOCK", 1, ("LOCK", 0), 0, None)

def test_rungs_mask_correctly():
    assert project(REC, "r1") == Record("BLOCK", 1, MASKED, MASKED, MASKED)
    assert project(REC, "r2") == Record("BLOCK", 1, ("LOCK", 0), MASKED, MASKED)
    assert project(REC, "r3") == Record("BLOCK", 1, ("LOCK", 0), 0, MASKED)
    assert project(REC, "r4") == REC
```

- [ ] **Step 2–4: Run/implement/run** as above. Note `None` (field absent in the latent record) survives projection as `None`, distinct from `MASKED` (field suppressed by the interface) — the D5 schema distinction.
- [ ] **Step 5: Commit** — `git commit -m "feat(yupana): content-rung projections r1-r4 with MASKED"`

### Task 6: Simulator

**Files:**
- Create: `src/yupi/simulator.py`
- Test: `tests/test_simulator.py`

**Interfaces:**
- Consumes: `enabled` (Task 3), `record_of` (Task 4).
- Produces: `sample_episode(cfg, programs, horizon: int, seed: int) -> list[tuple[Transition, Record]]` — seeded `random.Random(seed)`; each tick draws from `enabled()`'s exact distribution (Fraction weights via `random.choices` on numerators over common denominator); stops at horizon or all-TERMINATED.

- [ ] **Step 1: Failing test**

```python
# tests/test_simulator.py
from yupi.config import WorldConfig
from yupi.programs import c0a_programs
from yupi.simulator import sample_episode
from yupi.state import check_invariants

def test_episode_reproducible_and_invariant():
    cfg, progs = WorldConfig.c0a(), c0a_programs()
    a = sample_episode(cfg, progs, horizon=40, seed=7)
    b = sample_episode(cfg, progs, horizon=40, seed=7)
    assert [r for _, r in a] == [r for _, r in b]
    for t, _ in a:
        assert check_invariants(t.next_state, cfg) == []
```

- [ ] **Step 2–4: Run/implement/run.**
- [ ] **Step 5: Commit** — `git commit -m "feat(yupana): seeded exact-distribution simulator"`

### Task 7: Independent enumerator

**Files:**
- Create: `src/yupi/enumerator.py`
- Test: `tests/test_enumerator.py`

**Interfaces:**
- Consumes: `enabled`, `record_of`, `project`, `initial_state`.
- Produces: `paths(cfg, programs, horizon) -> list[tuple[list[Record], Fraction, State]]` — every trajectory to `horizon` as (latent record sequence, exact path probability, final state), by depth-first unrolling. Produces: `posterior_by_paths(cfg, programs, obs_seq: list[ObsRecord], rung) -> dict[State, Fraction]` — filters `paths(...)` to those whose projected records equal `obs_seq`, sums path probabilities by final state, normalizes. **This is the brute-force validator: no recursion over beliefs, no shared logic with `filter.py` beyond kernel/state/projection.**

- [ ] **Step 1: Failing test**

```python
# tests/test_enumerator.py
from fractions import Fraction
from yupi.config import WorldConfig
from yupi.programs import c0a_programs
from yupi.enumerator import paths, posterior_by_paths
from yupi.interfaces import project

CFG, PROGS = WorldConfig.c0a(), c0a_programs()

def test_path_probabilities_sum_to_one():
    ps = paths(CFG, PROGS, horizon=5)
    assert sum(p for _, p, _ in ps) == Fraction(1)

def test_posterior_normalized_and_exact():
    recs, prob, final = paths(CFG, PROGS, horizon=5)[0]
    obs = [project(r, "r1") for r in recs]
    post = posterior_by_paths(CFG, PROGS, obs, "r1")
    assert sum(post.values()) == Fraction(1)
    assert post.get(final, Fraction(0)) > 0   # realized state always in support
```

- [ ] **Step 2–4: Run/implement/run.**
- [ ] **Step 5: Commit** — `git commit -m "feat(yupana): exhaustive trajectory enumerator + path-sum posterior"`

### Task 8: Exact Bayes filter

**Files:**
- Create: `src/yupi/filter.py`
- Test: `tests/test_filter.py`

**Interfaces:**
- Consumes: `enabled`, `record_of`, `project`, `initial_state`.
- Produces: `Belief = dict[State, Fraction]`; `initial_belief(cfg) -> Belief` (`{initial_state(cfg): Fraction(1)}`); `step(belief, obs: ObsRecord, rung, cfg, programs) -> Belief` — recursive update: `b'(s') ∝ Σ_s b(s) · Σ{ p : (t,p) ∈ enabled(s), project(record_of(t), rung) == obs, t.next_state == s' }`, normalized; raises `ZeroProbabilityObservation` if the observation has probability zero under the belief; `run(cfg, programs, obs_seq, rung) -> Belief` folding `step`.

- [ ] **Step 1: Failing test**

```python
# tests/test_filter.py
from fractions import Fraction
import pytest
from yupi.config import WorldConfig
from yupi.programs import c0a_programs
from yupi.simulator import sample_episode
from yupi.interfaces import project
from yupi.filter import run, ZeroProbabilityObservation
from yupi.records import Record

CFG, PROGS = WorldConfig.c0a(), c0a_programs()

def test_filter_tracks_realized_state():
    ep = sample_episode(CFG, PROGS, horizon=10, seed=3)
    obs = [project(r, "r1") for _, r in ep]
    belief = run(CFG, PROGS, obs, "r1")
    assert sum(belief.values()) == Fraction(1)
    assert belief.get(ep[-1][0].next_state, Fraction(0)) > 0

def test_impossible_observation_raises():
    with pytest.raises(ZeroProbabilityObservation):
        run(CFG, PROGS, [Record("RELEASE", 0, "MASKED", "MASKED", "MASKED")], "r1")
```

- [ ] **Step 2–4: Run/implement/run.**
- [ ] **Step 5: Commit** — `git commit -m "feat(yupana): exact recursive Bayes filter"`

### Task 9: C0a bit-for-bit validation — filter vs. enumerator

**Files:**
- Create: `tests/test_c0a_validation.py`

**Interfaces:**
- Consumes: everything above. Produces the M1 deliverable-3 evidence for C0a at plan horizon (full-horizon H is frozen later with budgets, Part II §7; this test parameterizes horizon so re-running at frozen H is a config change).

- [ ] **Step 1: Write the validation test (it should pass immediately if Tasks 7–8 are correct — a failure here is the instrument catching a real defect; investigate, never weaken the test)**

```python
# tests/test_c0a_validation.py
"""Part II §6: filter must match path-sum enumeration exactly (Fraction ==),
on every distinct observation sequence, at every prefix, for every rung."""
from fractions import Fraction
from yupi.config import WorldConfig
from yupi.programs import c0a_programs
from yupi.enumerator import paths, posterior_by_paths
from yupi.interfaces import project
from yupi.filter import initial_belief, step

CFG, PROGS, H = WorldConfig.c0a(), c0a_programs(), 12  # H amended 6→12 in execution: H=6 paths never reach IO_ISSUE/IO_COMPLETE/IDLE, leaving the completion hazard unvalidated; H=11 is the measured minimum covering all 8 kinds, 12 adds slack. A companion test asserts kind-coverage so the gate is self-documenting.

def test_bit_for_bit_all_histories_all_rungs():
    for rung in ("r1", "r2", "r3", "r4"):
        obs_seqs = {tuple(project(r, rung) for r in recs) for recs, _, _ in paths(CFG, PROGS, H)}
        for obs in sorted(obs_seqs, key=repr):
            belief = initial_belief(CFG)
            for i, o in enumerate(obs, 1):
                belief = step(belief, o, rung, CFG, PROGS)
                exact = posterior_by_paths(CFG, PROGS, list(obs[:i]), rung)
                assert belief == exact, (rung, obs[:i])
```

- [ ] **Step 2: Run** — `uv run pytest tests/test_c0a_validation.py -v` (expect minutes, not hours, at H=6; if runtime explodes, that is D4 data — record it, do not raise H here).
- [ ] **Step 3: Run the full suite** — `uv run pytest -v` — all green.
- [ ] **Step 4: Commit** — `git commit -m "test(yupana): C0a bit-for-bit filter/enumerator agreement, all rungs, all histories"`

---

## Not in this plan (Plans B and C)

- **Plan B:** bucketed delivery + shuffled stochastic channel with likelihood (§4), filter extension, noncommuting/duplicate witnesses (§9 items 7); C0b/C0c configurations and their kernels' witnesses.
- **Plan C:** queries Q1–Q5 + P-next/P-horizon + divergent-history search (§5), the 11-witness suite (§9), σ naming + corpus generation (D3), benchmark harness + budget freeze (§7), ε-sweep characterization (D9).

## Self-Review (performed at write time)

- **Spec coverage:** Tasks 1–9 cover Part II §1 (Task 1), §2 (Tasks 1–2), §3 (Task 3), §4 deterministic slice (Tasks 4–5), §6 exactness/independence (Tasks 7–9). Deferred items are enumerated above with their plan assignments — nothing silently dropped.
- **Placeholder scan:** clean; every step has runnable content.
- **Type consistency:** `enabled(state, cfg, programs)` signature uniform across Tasks 3, 6, 7, 8; `project(record, rung)` uniform across 5, 7, 8, 9; `Belief = dict[State, Fraction]` in 8–9. Status/instruction constructors used identically in tests.
