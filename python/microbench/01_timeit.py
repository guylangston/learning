"""Level 1: stdlib `timeit` — think Stopwatch in a loop, but done properly.

Run:  uv run 01_timeit.py
CLI:  uv run python -m timeit -s "from subjects import concat_join" "concat_join(1000)"
"""

import timeit

from subjects import concat_join, concat_join_list, concat_plus

N = 1_000

for fn in (concat_plus, concat_join, concat_join_list):
    timer = timeit.Timer(lambda: fn(N))
    # autorange() picks a loop count so one run takes >= 0.2s (like BDN's pilot stage)
    loops, _ = timer.autorange()
    # repeat() = several independent samples; take the MIN, not the mean.
    # Noise only ever makes things slower, so min is the best estimate of true cost.
    samples = timer.repeat(repeat=7, number=loops)
    best = min(samples) / loops
    print(f"{fn.__name__:<18} {best * 1e6:8.2f} µs/op   ({loops} loops x 7)")
