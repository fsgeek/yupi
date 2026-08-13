from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class WorldConfig:
    """Configuration for the Yupana simulator world.

    All numeric fields must use exact arithmetic (Fraction).
    Represents a fixed system configuration: thread count, CPU cores, locks,
    devices, queue depth, request pool size, device completion probability,
    epsilon for tracing, and scheduling discipline.
    """
    n_threads: int
    n_cpus: int
    n_locks: int
    n_devices: int
    queue_depth: int
    req_pool: int
    completion_p: Fraction
    epsilon: Fraction
    discipline: str

    @classmethod
    def c0a(cls, p: Fraction = Fraction(1, 3)) -> "WorldConfig":
        """Canonical minimal config: 2 threads, 1 CPU, 1 lock, 1 device,
        depth 1, pool 2, completion_p = p (default 1/3), epsilon = 1, fifo discipline.

        Args:
            p: Device completion probability (default Fraction(1, 3))
        """
        return cls(
            n_threads=2,
            n_cpus=1,
            n_locks=1,
            n_devices=1,
            queue_depth=1,
            req_pool=2,
            completion_p=p,
            epsilon=Fraction(1),
            discipline="fifo"
        )

    @classmethod
    def c0c(cls, p: Fraction = Fraction(1, 3)) -> "WorldConfig":
        """Scheduling-validation config (Part I, Configurations): minimal
        2-CPU world. 3 threads, 2 CPUs, 0 locks, 1 device, depth 1, pool 2,
        completion_p = p (default 1/3), epsilon = 1, fifo discipline.

        Three threads and not two because CPU-slot assignment only bites
        under contention: with n_threads == n_cpus every runnable thread
        always finds a free slot and the dispatch gate never holds a thread
        back. Three is the minimum witnessing both slots occupied, a
        runnable thread waiting behind a full complement, and the execution
        choice among two running threads. Depth 1 makes the completion
        disciplines extensionally identical (the C0b lesson), so fifo alone
        is the honest choice here.

        Args:
            p: Device completion probability (default Fraction(1, 3))
        """
        return cls(
            n_threads=3,
            n_cpus=2,
            n_locks=0,
            n_devices=1,
            queue_depth=1,
            req_pool=2,
            completion_p=p,
            epsilon=Fraction(1),
            discipline="fifo",
        )

    @classmethod
    def c0b(cls, discipline: str, p: Fraction = Fraction(1, 3)) -> "WorldConfig":
        """Device-validation config (Part I, Configurations): 2 threads, 1 CPU,
        0 locks, 1 device, depth 2, pool 4 (>= 2*depth per I4), completion_p = p
        (default 1/3), epsilon = 1.

        Depth 2 makes the completion disciplines extensionally distinct —
        at depth 1, "complete the head" and "complete any in-flight request"
        are the same transition rule — so C0b must be validated under both.

        Args:
            discipline: "fifo" or "stochastic" (no default: the point of C0b
                is that the choice matters, so callers must name it).
            p: Device completion probability (default Fraction(1, 3))
        """
        return cls(
            n_threads=2,
            n_cpus=1,
            n_locks=0,
            n_devices=1,
            queue_depth=2,
            req_pool=4,
            completion_p=p,
            epsilon=Fraction(1),
            discipline=discipline,
        )
