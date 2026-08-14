"""Full-context injectivity check on multi-waiter lock contention worlds.

Conjecture: r1 (kind+actor) at full context from reset is injective on
trajectories for ANY config of this kernel — every stochastic branch is
labeled by its next record's (kind, actor), and every masked field
(including RELEASE.related, the woken thread) is a deterministic function
of the visible history. If true, the C0-family losslessness is a corollary,
C1 at full context is a predicted fourth zero, and ALL rung grip lives on
the truncation/window axis.

Falsification target: a contention world where two waiters can queue in
either order. If any observation prefix at any rung has posterior support
> 1, the conjecture dies and C1 grips at full context after all.
"""
import sys
from fractions import Fraction

sys.path.insert(0, "/home/tony/projects/yupi/src")

from yupi.config import WorldConfig
from yupi.kernel import enabled
from yupi.records import record_of
from yupi.state import initial_state
from yupi.interfaces import project
from yupi.programs import acquire, release, COMPUTE, io

RUNGS = ("r1", "r2", "r3", "r4")


def max_support(cfg, progs, horizon):
    """Walk the full stochastic tree, group states by (depth, projected
    observation prefix), report max group size per rung and total nodes."""
    out = {}
    for rung in RUNGS:
        groups = {}
        nodes = 0

        def recurse(state, obs, depth):
            nonlocal nodes
            nodes += 1
            groups.setdefault((depth, obs), set()).add(state)
            if depth == horizon:
                return
            for t, _ in enabled(state, cfg, progs):
                recurse(t.next_state, obs + (project(record_of(t), rung),), depth + 1)

        recurse(initial_state(cfg), (), 0)
        worst = max(len(v) for v in groups.values())
        # find an example if worst > 1
        example = None
        if worst > 1:
            for k, v in groups.items():
                if len(v) == worst:
                    example = k
                    break
        out[rung] = (worst, nodes, example)
    return out


def report(name, cfg, progs, horizon):
    print(f"== {name} (H={horizon}) ==")
    res = max_support(cfg, progs, horizon)
    for rung in RUNGS:
        worst, nodes, example = res[rung]
        flag = "  <-- SUPPORT > 1, CONJECTURE DEAD" if worst > 1 else ""
        print(f"  {rung}: max support {worst}  (tree nodes {nodes}){flag}")
        if example:
            print(f"      example at depth {example[0]}: {example[1]}")
    print()


# World A: 1 CPU, 3 threads contending one lock; both wait-queue orders
# (t1 before t2 / t2 before t1) reachable via the dispatch choice.
cfg_a = WorldConfig(
    n_threads=3, n_cpus=1, n_locks=1, n_devices=0,
    queue_depth=1, req_pool=2,
    completion_p=Fraction(1, 3), epsilon=Fraction(1), discipline="fifo",
)
progs_a = (
    (acquire(0), COMPUTE, release(0)),
    (acquire(0), release(0)),
    (acquire(0), release(0)),
)
report("A: 3 threads / 1 CPU / 1 lock, two waiters possible", cfg_a, progs_a, 14)

# World B: same contention with 2 CPUs (C1's cpu count) and a device, so
# completions interleave with wake events.
cfg_b = WorldConfig(
    n_threads=3, n_cpus=2, n_locks=1, n_devices=1,
    queue_depth=1, req_pool=2,
    completion_p=Fraction(1, 3), epsilon=Fraction(1), discipline="fifo",
)
progs_b = (
    (acquire(0), io(0), release(0)),
    (acquire(0), release(0)),
    (acquire(0), release(0)),
)
report("B: 3 threads / 2 CPUs / 1 lock / 1 device", cfg_b, progs_b, 14)

# World C: epsilon < 1 (C1 uses eps per D9), exercising the rr_cursor
# dynamics in the mixture regime.
cfg_c = WorldConfig(
    n_threads=3, n_cpus=1, n_locks=1, n_devices=0,
    queue_depth=1, req_pool=2,
    completion_p=Fraction(1, 3), epsilon=Fraction(1, 2), discipline="fifo",
)
report("C: world A with epsilon=1/2 (cursor in play)", cfg_c, progs_a, 12)
