from yupi.records import record_of, Record
from yupi.kernel import Transition
from yupi.config import WorldConfig
from yupi.state import initial_state


def test_record_mirrors_transition_fields():
    s = initial_state(WorldConfig.c0a())
    t = Transition("IO_ISSUE", 1, ("DEV", 0), None, 0, s)
    assert record_of(t) == Record("IO_ISSUE", 1, ("DEV", 0), None, 0)


def test_completion_maps_to_io_complete():
    """Test that kernel COMPLETION kind maps to record IO_COMPLETE kind."""
    s = initial_state(WorldConfig.c0a())
    t = Transition("COMPLETION", 1, ("DEV", 0), None, 42, s)
    record = record_of(t)
    assert record.kind == "IO_COMPLETE"
    assert record.actor == 1
    assert record.obj == ("DEV", 0)
    assert record.related is None
    assert record.lineage == 42
