"""D4 budget benchmark harness (Part I D4/D9 precedence rule).

Prices the two posterior-computation paths on the host hardware BEFORE any
observability curve is computed: `filter.step` wall-clock and peak memory
as functions of belief-support size, and `enumerator.paths` throughput as a
function of horizon. The D4 budget numbers (max support count, peak memory,
wall-clock per filtering step, enumeration horizon) are frozen from these
measurements, preserving the preregistration discipline — the budget cannot
be gerrymandered after seeing support-growth curves because it is fixed
before any are computed.

States for pricing come from deterministic BFS over world *reachability* —
no observations, no posteriors, no interface rungs are consulted during
generation, so nothing here constitutes an observability measurement.

The dynamometer world (`dyno_config`/`dyno_programs`) is a cost generator,
NOT an experimental configuration: deliberately larger than C1 so that
beliefs of large support with C1-like transition structure (contended CPUs,
held locks, in-flight I/O, active ε-mixture cursor) can be manufactured for
pricing. It carries no experimental commitments and appears in no
observability claim.

This module imports both `yupi.filter` and `yupi.enumerator`. That does not
touch the two-path validation firewall: benchmark prices each path, it is
imported by neither, and it shares no posterior-computation logic.
"""

import time
import tracemalloc
from dataclasses import dataclass
from fractions import Fraction
from typing import List, Tuple

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.filter import Belief, step
from yupi.interfaces import project
from yupi.kernel import enabled
from yupi.programs import COMPUTE, Program, acquire, io, release
from yupi.records import Record, record_of
from yupi.state import State, initial_state


def dyno_config() -> WorldConfig:
    """The dynamometer world: a cost generator larger than C1.

    5 threads / 2 CPUs / 2 locks / 1 device, queue depth 2, pool 4
    (>= 2*depth per I4), stochastic completion discipline, epsilon = 1/2 so
    the round-robin cursor is live (worst-case branching: uniform picks plus
    the RR pick at every scheduling choice).
    """
    return WorldConfig(
        n_threads=5,
        n_cpus=2,
        n_locks=2,
        n_devices=1,
        queue_depth=2,
        req_pool=4,
        completion_p=Fraction(1, 3),
        epsilon=Fraction(1, 2),
        discipline="stochastic",
    )


def dyno_programs() -> Tuple[Program, ...]:
    """Workloads for the dynamometer's 5 threads.

    Mixes lock contention (both locks, nested per I6 strictly-increasing
    order), I/O, and compute so reachable states exercise every transition
    genus the kernel offers.
    """
    return (
        (acquire(0), COMPUTE, release(0), io(0)),
        (COMPUTE, acquire(0), acquire(1), release(1), release(0)),
        (io(0), COMPUTE, acquire(1), release(1)),
        (acquire(1), COMPUTE, release(1), COMPUTE),
        (COMPUTE, io(0), COMPUTE),
    )


def reachable_states(cfg: WorldConfig, programs, cap: int) -> List[State]:
    """Deterministic BFS over world reachability from the initial state.

    Returns up to `cap` distinct states in BFS discovery order (transition
    order within a state is `enabled()`'s own order, so the result is fully
    deterministic). Consults no observations and no rungs.
    """
    root = initial_state(cfg)
    out: List[State] = [root]
    seen = {root}
    frontier = 0
    while frontier < len(out) and len(out) < cap:
        s = out[frontier]
        frontier += 1
        for t, _ in enabled(s, cfg, programs):
            nxt = t.next_state
            if nxt not in seen:
                seen.add(nxt)
                out.append(nxt)
                if len(out) == cap:
                    break
    return out


def make_belief(states: List[State]) -> Belief:
    """Uniform exact-Fraction belief over the given states."""
    n = len(states)
    mass = Fraction(1, n)
    return {s: mass for s in states}


def choose_observation(belief: Belief, cfg: WorldConfig, programs, rung: str) -> Record:
    """A projected record guaranteed nonzero likelihood under `belief`:
    the projection of the first enabled transition of the first support state.
    """
    first_state = next(iter(belief))
    transition, _ = enabled(first_state, cfg, programs)[0]
    return project(record_of(transition), rung)


@dataclass(frozen=True)
class FilterPrice:
    support_in: int
    support_out: int
    transitions_expanded: int
    wall_s: float
    peak_mem_bytes: int


@dataclass(frozen=True)
class EnumPrice:
    horizon: int
    n_paths: int
    wall_s: float


def price_filter_step(
    belief: Belief, cfg: WorldConfig, programs, rung: str, repeats: int = 3
) -> FilterPrice:
    """Price one `filter.step` call at this belief's support size.

    Wall-clock is the median of `repeats` untraced runs; peak memory comes
    from one additional tracemalloc-traced run (traced runs are slower, so
    timing and memory are measured separately).
    """
    obs = choose_observation(belief, cfg, programs, rung)

    transitions_expanded = sum(
        len(enabled(s, cfg, programs)) for s in belief
    )

    timings = []
    posterior: Belief = {}
    for _ in range(repeats):
        t0 = time.perf_counter()
        posterior = step(belief, obs, rung, cfg, programs)
        timings.append(time.perf_counter() - t0)
    timings.sort()
    wall_s = timings[len(timings) // 2]

    tracemalloc.start()
    step(belief, obs, rung, cfg, programs)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return FilterPrice(
        support_in=len(belief),
        support_out=len(posterior),
        transitions_expanded=transitions_expanded,
        wall_s=wall_s,
        peak_mem_bytes=peak,
    )


def price_enumerator(cfg: WorldConfig, programs, horizon: int) -> EnumPrice:
    """Price one exhaustive `enumerator.paths` unrolling to `horizon`."""
    t0 = time.perf_counter()
    all_paths = paths(cfg, programs, horizon)
    wall_s = time.perf_counter() - t0
    return EnumPrice(horizon=horizon, n_paths=len(all_paths), wall_s=wall_s)
