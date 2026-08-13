from fractions import Fraction
import pytest
from yupi.config import WorldConfig
from yupi.programs import c0a_programs
from yupi.simulator import sample_episode
from yupi.interfaces import project
from yupi.filter import initial_belief, step, run, ZeroProbabilityObservation
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

def test_belief_mass_exactly_one_every_step_r1():
    # Own test (brief asks for a 15-tick seeded episode at r1, mass checked
    # after every step, not just at the end -- catches a filter that only
    # normalizes correctly on the final fold but drifts mid-sequence).
    ep = sample_episode(CFG, PROGS, horizon=15, seed=7)
    obs = [project(r, "r1") for _, r in ep]
    belief = initial_belief(CFG)
    assert sum(belief.values()) == Fraction(1)
    for o in obs:
        belief = step(belief, o, "r1", CFG, PROGS)
        assert sum(belief.values()) == Fraction(1)

def test_r4_filter_is_point_mass_every_step():
    # Own test: r4 (all fields, no masking) should pin down the trajectory
    # uniquely at every tick, not just at the end -- belief collapses to a
    # single state (the one actually realized) immediately after each
    # observation, since a fully-specified record determines its origin
    # transition (and hence next_state) without ambiguity.
    ep = sample_episode(CFG, PROGS, horizon=15, seed=7)
    obs = [project(r, "r4") for _, r in ep]
    belief = initial_belief(CFG)
    for (transition, _), o in zip(ep, obs):
        belief = step(belief, o, "r4", CFG, PROGS)
        assert sum(belief.values()) == Fraction(1)
        assert len(belief) == 1
        assert belief.get(transition.next_state, Fraction(0)) == Fraction(1)
