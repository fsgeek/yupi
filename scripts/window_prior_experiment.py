"""How do truncated observers initialize belief? — an exact experiment.

Part II §2 leaves open how a truncated/windowed observer's prior is
initialized. Three candidate semantics, all exactly computable here:

  P1 "marginal":       the exact unconditional state distribution at window
                       start t0 (knows the clock and the dynamics, saw no
                       prefix). This is the Bayes-correct prior; filtering
                       it forward must equal path-sum conditioning, which
                       doubles as the first support>1 bit-for-bit gate the
                       filter has ever faced.
  P2 "support-uniform": uniform over support(mu_t0) (knows the clock,
                       forgot the measure).
  P3 "clock-free":     uniform over the union of supports of mu_t for all
                       t in [0, H] (forgot the clock too).

Measured, per rung and window start: posterior support sizes (the first
fat beliefs of the project), whether rung separation is nonzero inside
windows (witness 1-2 territory), and how fast the P2/P3 observers merge
with P1 as observations arrive (prior-sensitivity washout — the empirical
answer to how much the Part II §2 decision matters).

Worlds: A — the injectivity check's contention world (3 threads / 1 CPU /
1 lock, both wait-queue orders reachable), epsilon=1 symmetric; B — same
contention plus a device, completion_p = 1/3 skewing the time marginals
(the robustness check on measure-forgetting).
"""
import sys
from fractions import Fraction
from collections import defaultdict

sys.path.insert(0, "/home/tony/projects/yupi/src")

from yupi.config import WorldConfig
from yupi.kernel import enabled
from yupi.records import record_of
from yupi.state import initial_state
from yupi.interfaces import project
from yupi.programs import acquire, release, COMPUTE
from yupi.filter import step

RUNGS = ("r1", "r2", "r3", "r4")
H = 12

from yupi.programs import io

# World A: pure contention, epsilon=1 symmetry (marginals nearly uniform —
# flatters the support-uniform prior; the skew check is world B's job).
CFG_A = WorldConfig(
    n_threads=3, n_cpus=1, n_locks=1, n_devices=0,
    queue_depth=1, req_pool=2,
    completion_p=Fraction(1, 3), epsilon=Fraction(1), discipline="fifo",
)
PROGS_A = (
    (acquire(0), COMPUTE, release(0)),
    (acquire(0), release(0)),
    (acquire(0), release(0)),
)

# World B: contention + device. completion_p = 1/3 skews the time marginals
# (IDLE-vs-complete timing), so mu_t is NOT near-uniform — the honest test
# of whether forgetting the measure stays cheap.
CFG_B = WorldConfig(
    n_threads=3, n_cpus=1, n_locks=1, n_devices=1,
    queue_depth=1, req_pool=2,
    completion_p=Fraction(1, 3), epsilon=Fraction(1), discipline="fifo",
)
PROGS_B = (
    (acquire(0), io(0), release(0)),
    (acquire(0), release(0)),
    (acquire(0), release(0)),
)


def marginals(cfg, progs, horizon):
    """mu_t for t = 0..horizon: exact unconditional state distribution."""
    mu = [defaultdict(Fraction) for _ in range(horizon + 1)]
    mu[0][initial_state(cfg)] = Fraction(1)
    for t in range(horizon):
        for s, mass in mu[t].items():
            for tr, p in enabled(s, cfg, progs):
                mu[t + 1][tr.next_state] += mass * p
    return [dict(m) for m in mu]


def window_joint(cfg, progs, t0, horizon, rung):
    """joint[(d, omega)][state] = P(window obs prefix omega, state at d),
    prefix before t0 marginalized (unobserved). Single tree walk."""
    joint = defaultdict(lambda: defaultdict(Fraction))

    def recurse(state, prob, depth, omega):
        if depth >= t0:
            joint[(depth, omega)][state] += prob
        if depth == horizon:
            return
        for tr, p in enabled(state, cfg, progs):
            o = project(record_of(tr), rung) if depth >= t0 else None
            recurse(
                tr.next_state, prob * p, depth + 1,
                omega + (o,) if depth >= t0 else omega,
            )

    recurse(initial_state(cfg), Fraction(1), 0, ())
    return joint


def normalize(d):
    total = sum(d.values(), Fraction(0))
    return {s: m / total for s, m in d.items()}


def tv(a, b):
    keys = set(a) | set(b)
    return sum(abs(a.get(s, Fraction(0)) - b.get(s, Fraction(0))) for s in keys) / 2


def run_experiment(t0, CFG, PROGS):
    mu = marginals(CFG, PROGS, H)
    p1 = normalize(mu[t0])
    p2 = {s: Fraction(1, len(p1)) for s in p1}
    all_states = set()
    for m in mu:
        all_states |= set(m)
    p3 = {s: Fraction(1, len(all_states)) for s in all_states}

    print(f"--- t0={t0}  |support mu_t0|={len(p1)}  |clock-free pool|={len(all_states)}")

    for rung in RUNGS:
        joint = window_joint(CFG, PROGS, t0, H, rung)  # noqa
        leaves = [(omega, sum(states.values(), Fraction(0)))
                  for (d, omega), states in joint.items() if d == H]

        W = H - t0
        gate_checks = 0
        max_support = 0
        first_fat = None          # earliest in-window step with support > 1
        fat_example = None
        wtv2 = [Fraction(0)] * (W + 1)
        wtv3 = [Fraction(0)] * (W + 1)
        merged2 = [Fraction(0)] * (W + 1)
        merged3 = [Fraction(0)] * (W + 1)

        for omega, w in leaves:
            b1, b2, b3 = dict(p1), dict(p2), dict(p3)
            for k in range(1, W + 1):
                o = omega[k - 1]
                b1 = step(b1, o, rung, CFG, PROGS)
                b2 = step(b2, o, rung, CFG, PROGS)
                b3 = step(b3, o, rung, CFG, PROGS)
                # bit-for-bit gate: Bayes-correct prior filtered forward must
                # equal path-sum conditioning, exactly, including fat beliefs
                exact = normalize(joint[(t0 + k, omega[:k])])
                assert b1 == exact, (rung, t0, k, omega[:k])
                gate_checks += 1
                if len(b1) > max_support:
                    max_support = len(b1)
                if len(b1) > 1 and (first_fat is None or k < first_fat):
                    first_fat = k
                    fat_example = (omega[:k], sorted(
                        (str({f: getattr(s, f) for f in
                              ("status", "lock_owner", "lock_wq")}), float(m))
                        for s, m in b1.items()))
                wtv2[k] += w * tv(b2, b1)
                wtv3[k] += w * tv(b3, b1)
                merged2[k] += w * (1 if b2 == b1 else 0)
                merged3[k] += w * (1 if b3 == b1 else 0)

        print(f"  {rung}: max P1 support {max_support}"
              f"{'  <-- FAT BELIEF' if max_support > 1 else ''}"
              f"   (bit-for-bit gate: {gate_checks} checks passed)")
        if first_fat is not None:
            print(f"      first fat belief at window step {first_fat}")
        row2 = "  ".join(f"{float(wtv2[k]):.4f}" for k in range(1, W + 1))
        row3 = "  ".join(f"{float(wtv3[k]):.4f}" for k in range(1, W + 1))
        m2 = "  ".join(f"{float(merged2[k]):.2f}" for k in range(1, W + 1))
        print(f"      E[TV P2||P1] by step: {row2}")
        print(f"      E[TV P3||P1] by step: {row3}")
        print(f"      P[P2==P1]    by step: {m2}")
        if fat_example and rung in ("r1", "r2"):
            omega_k, states = fat_example
            print(f"      exemplar ambiguity after {[o.kind for o in omega_k]}:")
            for desc, m in states:
                print(f"        p={m:.4f}  {desc}")
    print()


for name, cfg, progs in (("A (symmetric)", CFG_A, PROGS_A), ("B (skewed, +device)", CFG_B, PROGS_B)):
    print(f"===== WORLD {name} =====")
    for t0 in (2, 4, 6):
        run_experiment(t0, cfg, progs)
