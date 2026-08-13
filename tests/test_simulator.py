from yupi.config import WorldConfig
from yupi.programs import c0a_programs
from yupi.simulator import sample_episode
from yupi.state import check_invariants


def test_episode_reproducible_and_invariant():
    """Test that seeded episodes are reproducible and maintain invariants.

    Requirement: two calls with the same seed produce identical records,
    and all intermediate states satisfy invariants.
    """
    cfg, progs = WorldConfig.c0a(), c0a_programs()
    a = sample_episode(cfg, progs, horizon=40, seed=7)
    b = sample_episode(cfg, progs, horizon=40, seed=7)
    assert [r for _, r in a] == [r for _, r in b]
    for t, _ in a:
        assert check_invariants(t.next_state, cfg) == []


def test_lock_contention_exists():
    """Test that C0a world exhibits lock contention across multiple seeds.

    Requirement: at least one episode (searching seeds 0..20) contains a BLOCK
    record with related=0, indicating one thread blocked on lock 0 while another
    owns it.
    """
    cfg, progs = WorldConfig.c0a(), c0a_programs()

    for seed in range(21):
        episode = sample_episode(cfg, progs, horizon=40, seed=seed)

        # Search for a BLOCK record on lock 0 with a related thread (contention).
        for _, record in episode:
            if record.kind == "BLOCK" and record.obj == ("LOCK", 0) and record.related is not None:
                # Found contention; test passes.
                return

    # If we reach here, no contention was found in any seed.
    raise AssertionError(
        "No lock contention (BLOCK on lock 0 with related thread) found in seeds 0..20"
    )
