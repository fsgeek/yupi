from yupi.programs import COMPUTE, acquire, release, io, validate_lock_order, c0a_programs

def test_c0a_programs_valid():
    progs = c0a_programs()
    assert len(progs) == 2 and validate_lock_order(progs)

def test_lock_order_violation():
    bad = ((acquire(1), acquire(0), release(0), release(1)),)  # 1 then 0: descending
    assert not validate_lock_order(bad)
