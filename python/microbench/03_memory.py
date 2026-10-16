"""Level 3: memory — the [MemoryDiagnoser] equivalent.

.NET reports "Allocated" bytes per op. Python's closest is `tracemalloc`, which hooks
the allocator and records every Python-level allocation (with tracebacks if you want).

Two numbers matter:
  peak     – high-water mark during the call (transient garbage like intermediate lists)
  retained – still alive after the call (what you returned / leaked)

Note: tracemalloc slows code ~2-5x, so NEVER time and trace in the same run.

Run:  uv run 03_memory.py
"""

import gc
import sys
import tracemalloc
from collections.abc import Callable

from subjects import concat_join, concat_join_list, concat_plus, squares_comp, squares_gen_sum, squares_loop


def measure(fn: Callable[[int], object], n: int) -> tuple[int, int, object]:
    gc.collect()
    tracemalloc.start()
    tracemalloc.reset_peak()
    before, _ = tracemalloc.get_traced_memory()
    result = fn(n)
    after, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak - before, after - before, result


def fmt(b: int) -> str:
    for unit in ("B", "KiB", "MiB"):
        if abs(b) < 1024:
            return f"{b:.0f} {unit}" if unit == "B" else f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} GiB"


N = 100_000
print(f"{'method':<18} {'peak':>10} {'retained':>10} {'getsizeof(result)':>18}")
for fn in (concat_plus, concat_join, concat_join_list, squares_loop, squares_comp, squares_gen_sum):
    peak, retained, result = measure(fn, N)
    print(f"{fn.__name__:<18} {fmt(peak):>10} {fmt(retained):>10} {fmt(sys.getsizeof(result)):>18}")

# Where did it allocate? (like a memory profiler's "top allocations")
print("\nTop allocation sites for concat_join_list:")
tracemalloc.start(10)
r = concat_join_list(N)
snap = tracemalloc.take_snapshot()
tracemalloc.stop()
for stat in snap.statistics("lineno")[:3]:
    print("  ", stat)
