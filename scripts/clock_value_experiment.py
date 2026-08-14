"""Value of the clock, measured the way Part II SS2 defines the observers.

Correction of the window-prior experiment's P3 (ChatGPT review, Aug 13):
P3 confounded three deletions (clock, measure, time-multiplicity). The
statute's base observer (SS2b) is offset-UNANCHORED but measure-CORRECT:
a joint belief over (U, S_U) whose mixture weights are posterior-updated
by evidence. The anchored condition (SS2c) is the same observer with U
revealed — a maskable field, priced as value-of-information (SS2e).

This experiment runs exactly that pair under one generating law:
U drawn uniformly from U_SET, window = W in-window records (fixed length,
so no length/RESET side-channel; all evidence is record content).

  anchored:   prior mu_{U},   U revealed.
  unanchored: components {u: weight 1/|U_SET|, belief mu_u}, weights
              updated by per-step evidence likelihood (SS2b).

Reported per rung and step: E[TV(unanchored marginal over S, anchored
posterior)] — the pure price of not knowing the clock — and E[posterior
weight on the true U] — how fast the observer re-learns the clock.

Epsilon as argv[1] (default 1), matching window_prior_experiment.py.
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
from yupi.programs import acquire, release, COMPUTE, io

RUNGS = ("r1", "r2", "r3", "r4")
U_SET = (2, 4, 6)
W = 6

EPS = Fraction(sys.argv[1]) if len(sys.argv) > 1 else Fraction(1)

CFG_A = WorldConfig(
    n_threads=3, n_cpus=1, n_locks=1, n_devices=0,
    queue_depth=1, req_pool=2,
    completion_p=Fraction(1, 3), epsilon=EPS, discipline="fifo",
)
PROGS_A = (
    (acquire(0), COMPUTE, release(0)),
    (acquire(0), release(0)),
    (acquire(0), release(0)),
)
CFG_B = WorldConfig(
    n_threads=3, n_cpus=1, n_locks=1, n_devices=1,
    queue_depth=1, req_pool=2,
    completion_p=Fraction(1, 3), epsilon=EPS, discipline="fifo",
)
PROGS_B = (
    (acquire(0), io(0), release(0)),
    (acquire(0), release(0)),
    (acquire(0), release(0)),
)


def marginals(cfg, progs, horizon):
    mu = [defaultdict(Fraction) for _ in range(horizon + 1)]
    mu[0][initial_state(cfg)] = Fraction(1)
    for t in range(horizon):
        for s, mass in mu[t].items():
            for tr, p in enabled(s, cfg, progs):
                mu[t + 1][tr.next_state] += mass * p
    return [dict(m) for m in mu]


def window_joint(cfg, progs, t0, horizon, rung):
    joint = defaultdict(lambda: defaultdict(Fraction))

    def recurse(state, prob, depth, omega):
        if depth >= t0:
            joint[(depth, omega)][state] += prob
        if depth == horizon:
            return
        for tr, p in enabled(state, cfg, progs):
            o = project(record_of(tr), rung) if depth >= t0 else None
            recurse(tr.next_state, prob * p, depth + 1,
                    omega + (o,) if depth >= t0 else omega)

    recurse(initial_state(cfg), Fraction(1), 0, ())
    return joint


def normalize(d):
    total = sum(d.values(), Fraction(0))
    return {s: m / total for s, m in d.items()}


def tv(a, b):
    keys = set(a) | set(b)
    return sum(abs(a.get(s, Fraction(0)) - b.get(s, Fraction(0))) for s in keys) / 2


def step_unnorm(belief, obs, rung, cfg, progs):
    """One Bayes update WITHOUT normalization; returns (belief', likelihood).
    Experiment-local: filter.step discards the constant this observer's
    mixture weights need (SS2b: weights are posterior, not frozen)."""
    out = defaultdict(Fraction)
    for s, mass in belief.items():
        if mass == 0:
            continue
        for t, p in enabled(s, cfg, progs):
            if project(record_of(t), rung) == obs:
                out[t.next_state] += mass * p
    total = sum(out.values(), Fraction(0))
    return dict(out), total


def run_world(name, cfg, progs):
    print(f"===== WORLD {name}  eps={EPS}  U in {U_SET}, W={W} =====")
    mu = marginals(cfg, progs, max(U_SET) + W)
    u_prior = Fraction(1, len(U_SET))

    for rung in RUNGS:
        joints = {u: window_joint(cfg, progs, u, u + W, rung) for u in U_SET}
        # E[TV] and E[weight on true U], generating-law weighted
        etv = [Fraction(0)] * (W + 1)
        ewt = [Fraction(0)] * (W + 1)

        for u_true in U_SET:
            joint = joints[u_true]
            leaves = [(omega, m) for (d, omega), states in joint.items()
                      if d == u_true + W
                      for m in (sum(states.values(), Fraction(0)),)]
            for omega, w_leaf in leaves:
                w = u_prior * w_leaf   # P(U=u_true, omega) under the law
                anchored = dict(normalize(mu[u_true]))
                comps = {u: (u_prior, dict(normalize(mu[u]))) for u in U_SET}
                for k in range(1, W + 1):
                    o = omega[k - 1]
                    anchored, _ = step_unnorm(anchored, o, rung, cfg, progs)
                    anchored = normalize(anchored)
                    new_comps = {}
                    for u, (wt, bel) in comps.items():
                        if wt == 0:
                            continue
                        bel2, lik = step_unnorm(bel, o, rung, cfg, progs)
                        if lik > 0:
                            new_comps[u] = (wt * lik, normalize(bel2))
                    z = sum(wt for wt, _ in new_comps.values())
                    comps = {u: (wt / z, bel) for u, (wt, bel) in new_comps.items()}
                    marginal = defaultdict(Fraction)
                    for u, (wt, bel) in comps.items():
                        for s, m in bel.items():
                            marginal[s] += wt * m
                    etv[k] += w * tv(dict(marginal), anchored)
                    ewt[k] += w * comps.get(u_true, (Fraction(0), None))[0]

        row_tv = "  ".join(f"{float(etv[k]):.4f}" for k in range(1, W + 1))
        row_wt = "  ".join(f"{float(ewt[k]):.2f}" for k in range(1, W + 1))
        print(f"  {rung}: E[TV(unanchored||anchored)] by step: {row_tv}")
        print(f"      E[P(U=true U | h)]        by step: {row_wt}")
    print()


run_world("A", CFG_A, PROGS_A)
run_world("B", CFG_B, PROGS_B)
