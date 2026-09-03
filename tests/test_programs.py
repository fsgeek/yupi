from yupi.programs import COMPUTE, acquire, release, io, validate_lock_order, c0a_programs

def test_c0a_programs_valid():
    progs = c0a_programs()
    assert len(progs) == 2 and validate_lock_order(progs)

def test_lock_order_violation():
    bad = ((acquire(1), acquire(0), release(0), release(1)),)  # 1 then 0: descending
    assert not validate_lock_order(bad)


def test_c1_prime_programs_recur_and_obey_lock_order():
    """C1′ (exploratory, 2026-09-03): C1's contention structure with short,
    unrolled bodies so lock holds recur within a 14–16-record horizon; no
    thread can terminate before tick 14; I6 holds; the env switch returns it."""
    import os
    from yupi.programs import c1_prime_programs, c1_programs, programs_for, validate_lock_order
    progs = c1_prime_programs()
    assert len(progs) == 4 and validate_lock_order(progs)
    assert all(len(p) >= 15 for p in progs)
    # recurring contention: lock 0 acquired ≥ 4 times by thread 0 and by thread 2, lock 1 by 1 and 3
    acq = lambda p, l: sum(1 for ins in p if ins == ("ACQUIRE", l))
    assert acq(progs[0], 0) >= 4 and acq(progs[2], 0) >= 4
    assert acq(progs[1], 1) >= 4 and acq(progs[3], 1) >= 4
    assert programs_for("c1") == c1_programs() and programs_for("c1prime") == progs
    os.environ["YUPI_PROGRAMS"] = "c1prime"
    try:
        assert programs_for() == progs
    finally:
        del os.environ["YUPI_PROGRAMS"]
    assert programs_for() == c1_programs()
