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


# --- Additional tests beyond the brief ---

def test_r4_posterior_is_a_point_mass():
    # Full observation (r4, all fields unmasked) should determine the
    # trajectory's final state uniquely on C0a: no two distinct paths of
    # equal length can project to the same r4 record sequence, since r4
    # preserves kind/actor/obj/related/lineage verbatim (project("r4") is
    # the identity per interfaces.py), and the trajectory tree's records
    # are a deterministic function of the sequence of kernel choices taken.
    # If this fails, that's a real finding about C0a's structure, not a
    # test to weaken -- report it instead of loosening the assertion.
    ps = paths(CFG, PROGS, horizon=5)
    for recs, prob, final in ps:
        if prob == 0:
            continue
        obs = [project(r, "r4") for r in recs]
        post = posterior_by_paths(CFG, PROGS, obs, "r4")
        assert len(post) == 1, (obs, post)
        assert post[final] == Fraction(1)


def test_marginal_consistency_r1():
    # Sum over all distinct r1 observation-sequences of
    # P(obs_seq) * posterior_by_paths(obs_seq)[s] must reconstruct the
    # unconditional marginal P(final_state = s) computed directly from
    # paths(). This checks posterior_by_paths's normalization and
    # path-filtering logic against an independent aggregate computed the
    # same brute-force way (no recursive belief update involved either
    # side), rather than trusting per-observation normalization alone.
    ps = paths(CFG, PROGS, horizon=4)  # smaller horizon: fewer distinct obs_seqs

    # Unconditional final-state marginal, straight from paths().
    direct_marginal: dict = {}
    for recs, prob, final in ps:
        direct_marginal[final] = direct_marginal.get(final, Fraction(0)) + prob

    # Group paths by their r1 observation sequence to get P(obs_seq) and to
    # enumerate the distinct obs_seqs without recomputing posterior_by_paths
    # against paths() a second, hidden way.
    obs_seq_prob: dict = {}
    seen_obs_seqs = []
    for recs, prob, _ in ps:
        obs = tuple(project(r, "r1") for r in recs)
        if obs not in obs_seq_prob:
            obs_seq_prob[obs] = Fraction(0)
            seen_obs_seqs.append(obs)
        obs_seq_prob[obs] += prob

    reconstructed: dict = {}
    for obs in seen_obs_seqs:
        p_obs = obs_seq_prob[obs]
        post = posterior_by_paths(CFG, PROGS, list(obs), "r1")
        for state, p_state_given_obs in post.items():
            reconstructed[state] = reconstructed.get(state, Fraction(0)) + p_obs * p_state_given_obs

    assert reconstructed == direct_marginal
