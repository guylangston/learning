# Python micro-benchmarking (for BenchmarkDotNet users)

```sh
uv sync
uv run 01_timeit.py                         # stdlib, quick-and-dirty
uv run 02_pyperf.py --fast                  # BDN-style: processes, warmup, stats
uv run 03_memory.py                         # [MemoryDiagnoser] equivalent
uv run pytest tests/ --benchmark-only --benchmark-group-by=param:n
```

## BenchmarkDotNet → Python

| BenchmarkDotNet | Python |
|---|---|
| `BenchmarkRunner.Run<T>()` | `pyperf.Runner().bench_func(...)` |
| Separate process per benchmark | pyperf does this by default (20 worker procs) |
| Pilot / warmup / actual stages | pyperf calibrates loops + warmups; `timeit.autorange()` |
| `[Params]`, `[Arguments]` | loop in pyperf; `@pytest.mark.parametrize` in pytest-benchmark |
| `[Baseline = true]` / Ratio column | pytest-benchmark's `(1.0)` ratios; `pyperf compare_to a.json b.json` |
| `[IterationSetup]` | `benchmark.pedantic(fn, setup=...)` |
| `[MemoryDiagnoser]` Allocated | `tracemalloc` (peak + retained) |
| Exporters (JSON/MD) | `pyperf -o x.json`, `pytest --benchmark-json`, `--benchmark-autosave` |
| Gen0/1/2 columns | `gc.get_stats()` / `gc.callbacks` (rarely matters — refcounting frees most things immediately) |
| `[DisassemblyDiagnoser]` | `import dis; dis.dis(fn)` |
| Hardware counters | `perf stat`, and `python -X perf` for `perf record` with Python frames |

**Which to use:** pyperf for "which is faster, really?"; pytest-benchmark for CI
regression gates (`--benchmark-compare-fail=mean:10%`); `timeit` in the REPL.

## Things the output here actually teaches

1. **`s += str(i)` is not quadratic in CPython.** C# devs expect it to be (immutable
   strings). CPython cheats: if the string's refcount is 1 it resizes in place. Don't
   rely on it (PyPy etc. don't do it), but it shows why you *measure*.
2. **`join(list_comp)` beats `join(generator)`.** `join` needs the length up front, so
   it materialises a generator into a list anyway — plus generator overhead.
3. **Peak vs retained memory.** `join` variants peak at ~5.6 MiB (all the temp `str`
   objects) but retain only the 477 KiB result. `+=` peaks lower. Time vs memory trade-off.
4. **`sys.getsizeof` is shallow.** A 100k-int list is 782 KiB by `getsizeof` but 3.8 MiB
   retained — every `int` is a separate heap object (~28 B). No value types in Python.
5. **Generator + `sum` uses ~0 memory.** That's the `IEnumerable` streaming win.
6. **Use `min`, not mean, for timeit.** Noise only adds time. pyperf reports mean±stddev
   but over many processes, and warns when results are unstable.

## Gotchas vs .NET

- **No JIT warmup to worry about** (mostly) — but 3.13+ has an experimental JIT and 3.11+
  has specialising adaptive bytecode, so the first few calls *are* slower. pyperf's warmups handle it.
- **Never time with `tracemalloc` on** — it slows execution 2–5x. Separate runs, like BDN does.
- **Noise:** `uv run python -m pyperf system tune` (sudo) disables turbo/pins CPU; `system reset` undoes it.
  On a laptop, plug in power. Check with `pyperf stats x.json`.
- **Dead-code elimination isn't a thing** in CPython, so you don't need `Consume()`-style
  tricks — but do return the result so the comparison is honest.

## Going further

- `memray` (Bloomberg) — native-level memory profiler with flamegraphs: `uv run --with memray memray run x.py`
- `scalene` — CPU + memory + GPU line-level profiler (profiling ≠ benchmarking, but complementary)
- `py-spy` — sampling profiler, attach to a running process
- `cProfile` + `snakeviz` — stdlib deterministic profiler
