"""Windowed-observer machinery (Part II §2 statute): law, filter, gate.

The statute (Part II §2(a)/(b), decided — window-prior note v0.3): the
truncation prior is DERIVED (the marginal induced by the joint
episode/endpoint/window law) and the base observer is offset-UNANCHORED,
holding a joint belief over (U, S_U) whose mixture weights are
posterior-updated by evidence — window length included.

Gate discipline: the recursive mixture filter (window_filter) is validated
bit-for-bit against an independent prefix-marginalized path summation
(window_enumerator), mirroring the filter/enumerator firewall.

Controls: with L >= T_ep every window is full-context and the machinery
must reduce exactly to the validated full-context gate — point masses by
the injectivity theorem. The fat-belief witnesses (support > 1) exist only
under genuine truncation, which is the theorem's consequence 5 discharged.
"""

from fractions import Fraction

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.filter import run as filter_run
from yupi.interfaces import project
from yupi.programs import COMPUTE, acquire, c1_programs, release
from yupi.window import WindowLaw, endpoint_prior
from yupi.window_enumerator import posterior_by_window_paths
from yupi.window_filter import filter_window


# World A from the window-prior/clock experiments: 3 threads / 1 CPU /
# 1 lock, both waiter orders reachable — the canonical ambiguity world.
def _world_a():
    cfg = WorldConfig(
        n_threads=3, n_cpus=1, n_locks=1, n_devices=0,
        queue_depth=1, req_pool=2,
        completion_p=Fraction(1, 3), epsilon=Fraction(1), discipline="fifo",
    )
    progs = (
        (acquire(0), COMPUTE, release(0)),
        (acquire(0), release(0)),
        (acquire(0), release(0)),
    )
    return cfg, progs


def _all_windows(cfg, progs, law, rung):
    """Every (reset_flag, obs_window, generating probability) the law can
    produce, by exhaustive episode enumeration: endpoint T uniform on the
    grid, window = projected records U+1..T, RESET visible iff U=0."""
    out = []
    w_T = endpoint_prior(law)
    for T in law.endpoints():
        u = law.offset(T)
        for recs, prob, _ in paths(cfg, progs, T):
            window = tuple(project(r, rung) for r in recs[u:])
            out.append((u == 0, window, w_T * prob))
    return out


# --- law arithmetic --------------------------------------------------------


def test_law_endpoint_grid_and_offsets():
    law = WindowLaw(T_ep=6, L=4, B=2)
    assert list(law.endpoints()) == [2, 4, 6]
    assert law.offset(2) == 0
    assert law.offset(4) == 0
    assert law.offset(6) == 2


def test_law_reset_observed_partitions_compatibility():
    # Statute §2(a): a U=0 window includes RESET; a window without RESET
    # can only have U>0. The reset flag therefore PARTITIONS the
    # compatible-endpoint sets — no offset is compatible with both.
    law = WindowLaw(T_ep=8, L=4, B=2)
    with_reset = law.compatible_endpoints(4, reset_observed=True)
    without = law.compatible_endpoints(4, reset_observed=False)
    assert with_reset == [(4, 0)]
    assert without == [(6, 2), (8, 4)]


def test_law_short_window_without_reset_is_impossible():
    # Every U>0 window has exactly L transition records; a shorter window
    # must have reached episode start and so must carry RESET.
    law = WindowLaw(T_ep=8, L=4, B=2)
    assert law.compatible_endpoints(2, reset_observed=False) == []
    assert law.compatible_endpoints(2, reset_observed=True) == [(2, 0)]


def test_law_endpoint_prior_is_uniform_on_grid():
    law = WindowLaw(T_ep=6, L=4, B=2)
    assert endpoint_prior(law) == Fraction(1, 3)


# --- full-context reduction (control) --------------------------------------


def test_full_context_reduction_matches_plain_filter():
    # L >= T_ep: every endpoint gives U=0; the windowed machinery must
    # reduce bit-for-bit to the validated full-context filter, and by the
    # injectivity theorem every posterior is a point mass.
    cfg, progs = _world_a()
    law = WindowLaw(T_ep=4, L=4, B=1)
    for T in law.endpoints():
        for recs, _, _ in paths(cfg, progs, T)[:10]:
            obs = [project(r, "r1") for r in recs]
            post = filter_window(cfg, progs, law, obs, "r1", reset_observed=True)
            assert set(post.components) == {0}
            marginal = post.state_marginal()
            assert marginal == filter_run(cfg, progs, obs, "r1")
            assert len(marginal) == 1


# --- the gate: filter vs path summation, bit for bit -----------------------


def _assert_gate(cfg, progs, law, rung, max_windows=None):
    seen = set()
    windows = _all_windows(cfg, progs, law, rung)
    if max_windows is not None:
        stride = max(1, len(windows) // max_windows)
        windows = windows[::stride]
    for reset, obs, _ in windows:
        if (reset, obs) in seen:
            continue
        seen.add((reset, obs))
        post = filter_window(cfg, progs, law, list(obs), rung, reset_observed=reset)
        ref = posterior_by_window_paths(
            cfg, progs, law, list(obs), rung, reset_observed=reset
        )
        assert set(post.components) == set(ref.components)
        for u in post.components:
            w_f, b_f = post.components[u]
            w_e, b_e = ref.components[u]
            assert w_f == w_e  # exact Fraction equality — bit for bit
            assert b_f == b_e


def test_gate_world_a_exhaustive_r1():
    cfg, progs = _world_a()
    law = WindowLaw(T_ep=8, L=4, B=2)
    _assert_gate(cfg, progs, law, "r1")


def test_gate_world_a_exhaustive_r4():
    cfg, progs = _world_a()
    law = WindowLaw(T_ep=8, L=4, B=2)
    _assert_gate(cfg, progs, law, "r4")


def test_gate_c1_sampled_r1():
    cfg = WorldConfig.c1()
    progs = c1_programs()
    law = WindowLaw(T_ep=6, L=4, B=2)
    _assert_gate(cfg, progs, law, "r1", max_windows=40)


# --- posterior mixture weights (statute §2b) --------------------------------


def test_short_window_conditions_length_to_full_context():
    # A window shorter than L can only have come from U=0 (it carries
    # RESET): length and reset agree, and the posterior must say so.
    cfg, progs = _world_a()
    law = WindowLaw(T_ep=8, L=4, B=2)
    recs, _, _ = paths(cfg, progs, 2)[0]
    obs = [project(r, "r1") for r in recs]
    post = filter_window(cfg, progs, law, obs, "r1", reset_observed=True)
    assert set(post.components) == {0}


def test_reset_visible_windows_are_point_masses():
    # Statute + injectivity corollary: RESET pins U=0, the prior is the
    # known reset state, and full-context injectivity makes every
    # reset-visible posterior a point mass. (This is the control the v0.1
    # semantics got wrong by letting U=0 compete at full window length.)
    cfg, progs = _world_a()
    law = WindowLaw(T_ep=8, L=4, B=2)
    for reset, obs, _ in _all_windows(cfg, progs, law, "r1"):
        if not reset:
            continue
        post = filter_window(cfg, progs, law, list(obs), "r1", reset_observed=True)
        assert len(post.state_marginal()) == 1


def test_mixture_weights_are_posterior_not_frozen():
    # A resetless window has a priori compatible offsets {2, 4}; evidence
    # must be able to kill one outright (posterior weight 0 by absence).
    cfg, progs = _world_a()
    law = WindowLaw(T_ep=8, L=4, B=2)
    a_priori = {u for _, u in law.compatible_endpoints(law.L, reset_observed=False)}
    assert len(a_priori) >= 2  # the ambiguity must exist to be resolved
    killed = False
    for reset, obs, _ in _all_windows(cfg, progs, law, "r1"):
        if reset:
            continue
        post = filter_window(cfg, progs, law, list(obs), "r1", reset_observed=False)
        if set(post.components) < a_priori:
            killed = True
            break
    assert killed


# --- the first fat beliefs through the gate --------------------------------


def test_fat_state_marginal_exists_world_a_r1():
    # Consequence 5 of the injectivity note discharged: truncation makes
    # the gate carry a support>1 belief. Control: the same machinery at
    # L >= T_ep (full context) is point-mass everywhere (test above).
    cfg, progs = _world_a()
    law = WindowLaw(T_ep=8, L=4, B=2)
    fat = False
    for reset, obs, _ in _all_windows(cfg, progs, law, "r1"):
        if reset:
            continue  # reset-visible windows are point masses by injectivity
        post = filter_window(cfg, progs, law, list(obs), "r1", reset_observed=False)
        if len(post.state_marginal()) > 1:
            fat = True
            break
    assert fat


def test_fat_state_marginal_exists_c1_r1():
    # Task 4's witness: the first support>1 posterior on validated C1,
    # through the bit-for-bit-gated windowed machinery.
    cfg = WorldConfig.c1()
    progs = c1_programs()
    law = WindowLaw(T_ep=6, L=4, B=2)
    fat = False
    for reset, obs, _ in _all_windows(cfg, progs, law, "r1"):
        if reset:
            continue
        post = filter_window(cfg, progs, law, list(obs), "r1", reset_observed=False)
        if len(post.state_marginal()) > 1:
            fat = True
            break
    assert fat
