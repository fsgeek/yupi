from yupi.records import Record
from yupi.interfaces import project, MASKED


REC = Record("BLOCK", 1, ("LOCK", 0), 0, None)


def test_rungs_mask_correctly():
    assert project(REC, "r1") == Record("BLOCK", 1, MASKED, MASKED, MASKED)
    assert project(REC, "r2") == Record("BLOCK", 1, ("LOCK", 0), MASKED, MASKED)
    assert project(REC, "r3") == Record("BLOCK", 1, ("LOCK", 0), 0, MASKED)
    assert project(REC, "r4") == REC


def test_none_survives_projection():
    """None (absent field) must survive projection, distinct from MASKED."""
    rec_with_none = Record("STEP", 2, None, None, None)
    assert project(rec_with_none, "r1") == Record("STEP", 2, MASKED, MASKED, MASKED)
    assert project(rec_with_none, "r2") == Record("STEP", 2, None, MASKED, MASKED)
    assert project(rec_with_none, "r3") == Record("STEP", 2, None, None, MASKED)
    assert project(rec_with_none, "r4") == rec_with_none


def test_unknown_rung_raises_valueerror():
    """project must raise ValueError for unknown rung names."""
    rec = Record("STEP", 1, None, None, None)
    try:
        project(rec, "r5")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
