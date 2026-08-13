from typing import Tuple

COMPUTE = ("COMPUTE",)


def acquire(l: int) -> Tuple[str, int]:
    """Create an ACQUIRE instruction for lock l."""
    return ("ACQUIRE", l)


def release(l: int) -> Tuple[str, int]:
    """Create a RELEASE instruction for lock l."""
    return ("RELEASE", l)


def io(d: int) -> Tuple[str, int]:
    """Create an IO instruction for device d."""
    return ("IO", d)


Program = Tuple[Tuple, ...]


def validate_lock_order(programs: Tuple[Program, ...]) -> bool:
    """Validate lock order discipline (I6) for all programs.

    Returns True iff in every program, ACQUIRE lock indices between paired
    ACQUIRE/RELEASE are strictly increasing while held. This ensures no
    deadlock cycle can occur.

    For each program, tracks the stack of held locks. When an ACQUIRE occurs,
    the lock index must be strictly greater than the maximum held lock index.
    When a RELEASE occurs, the lock must be the top of the held-locks stack.
    """
    for program in programs:
        held_locks = []

        for instruction in program:
            if instruction[0] == "ACQUIRE":
                lock_idx = instruction[1]
                if held_locks and lock_idx <= max(held_locks):
                    return False
                held_locks.append(lock_idx)
            elif instruction[0] == "RELEASE":
                lock_idx = instruction[1]
                if not held_locks or held_locks[-1] != lock_idx:
                    return False
                held_locks.pop()

    return True


def c0b_programs() -> Tuple[Program, Program]:
    """Return the canonical C0b program pair.

    Thread 0: (io(0),)
    Thread 1: (io(0),)

    The minimal workload placing two requests in flight (Part I,
    Configurations): with one CPU, thread 0 issues and blocks, thread 1 is
    dispatched and issues, and the depth-2 queue holds both requests. No
    locks, no compute: every record kind this world can emit concerns the
    device.
    """
    thread_0 = (io(0),)
    thread_1 = (io(0),)
    return (thread_0, thread_1)


def c0a_programs() -> Tuple[Program, Program]:
    """Return the canonical C0a program pair.

    Thread 0: (acquire(0), COMPUTE, release(0), io(0))
    Thread 1: (COMPUTE, acquire(0), release(0))

    Short enough that exhaustive tree stays small; exercises lock contention,
    blocking, and I/O.
    """
    thread_0 = (acquire(0), COMPUTE, release(0), io(0))
    thread_1 = (COMPUTE, acquire(0), release(0))
    return (thread_0, thread_1)
