"""Level 2: pyperf — the closest thing to BenchmarkDotNet.

Like BDN it: spawns worker processes (fresh interpreter per sample set), does warmups,
calibrates loop counts, reports mean ± std dev, warns about unstable results, and can
save JSON for later comparison (like BDN's exporters/baselines).

Run:      uv run 02_pyperf.py
Quick:    uv run 02_pyperf.py --fast
Save:     uv run 02_pyperf.py -o before.json
Compare:  uv run python -m pyperf compare_to before.json after.json --table
Stats:    uv run python -m pyperf stats before.json
System:   uv run python -m pyperf system tune   (sudo; pins CPU freq etc. — 'system reset' undoes)
"""

import pyperf

from subjects import concat_join, concat_join_list, concat_plus, squares_comp, squares_loop

runner = pyperf.Runner()

# [Params(100, 10_000)] equivalent: just loop and name each benchmark.
for n in (100, 10_000):
    runner.bench_func(f"concat_plus[{n}]", concat_plus, n)
    runner.bench_func(f"concat_join[{n}]", concat_join, n)
    runner.bench_func(f"concat_join_list[{n}]", concat_join_list, n)
    runner.bench_func(f"squares_loop[{n}]", squares_loop, n)
    runner.bench_func(f"squares_comp[{n}]", squares_comp, n)
