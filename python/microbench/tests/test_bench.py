"""Level 4: pytest-benchmark — benchmarks as tests (great for CI regression gates).

Run:      uv run pytest tests/ --benchmark-only
Group:    uv run pytest tests/ --benchmark-only --benchmark-group-by=param:n
Save:     uv run pytest tests/ --benchmark-autosave            (-> .benchmarks/)
Compare:  uv run pytest tests/ --benchmark-compare --benchmark-compare-fail=mean:10%
Histogram:uv run pytest tests/ --benchmark-histogram           (needs pygal)
"""

import pytest

from subjects import concat_join, concat_join_list, concat_plus


# @pytest.mark.parametrize == [Params] / [Arguments]
@pytest.mark.parametrize("n", [100, 10_000])
@pytest.mark.parametrize("fn", [concat_plus, concat_join, concat_join_list], ids=lambda f: f.__name__)
def test_concat(benchmark, fn, n):
    result = benchmark(fn, n)
    assert len(result) > 0  # it's still a test — you can assert correctness too


@pytest.mark.parametrize("n", [100, 10_000])
def test_sorted_with_setup(benchmark, n):
    # [IterationSetup] equivalent: setup runs before each round, outside the timing
    def setup():
        data = list(range(n, 0, -1))
        return (data,), {}

    benchmark.pedantic(sorted, setup=setup, rounds=100)
