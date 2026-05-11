
```prompt
I am a senior C# developer, learning python for use in AI/LLM.

Describe async vs mutli-threaded (threadpooling, cancellation) vs concurrency for me with code examples.

How does this with modules like `FastAPI` and postgres?

Define: preemptive multi-threading

Prepare a technical interview on this topic for me.
```

# Summary

- Async in Python usually means single-threaded cooperative concurrency using async / await.
- For pure CPU-heavy Python code, threads are usually limited by the GIL.
- Python cancellation exists, but is less uniform and less elegant than C# CancellationToken
- Python concurrency is more explicit about whether code is:
 - async and non-blocking
 - sync but blocking
 - CPU-bound
 - thread-safe or not
- Host async FastAPI with `Uvicorn/ASGI`;  runs event loops per worker
- "upgrade" async to thread with `await asyncio.to_thread(blocking_sdk_call)`

## Follow-up Questions:

- [  ] show me `asyncio.gather`'s type definition

## async

```py
import asyncio

async def fetch_data(name: str, delay: float) -> str:
    print(f"start {name}")
    await asyncio.sleep(delay)
    print(f"end {name}")
    return f"result-{name}"

async def main() -> None:
    results = await asyncio.gather(
        fetch_data("a", 2),
        fetch_data("b", 1),
        fetch_data("c", 3),
    )
    print(results)

asyncio.run(main())

```

## multi-threading

```py
import threading
import time

def work(name: str, delay: float) -> None:
    print(f"start {name}")
    time.sleep(delay)
    print(f"end {name}")

threads = [
    threading.Thread(target=work, args=("a", 2)),
    threading.Thread(target=work, args=("b", 1)),
]

for t in threads:
    t.start()

for t in threads:
    t.join()
```

## thread-pool

```py
from concurrent.futures import ThreadPoolExecutor
import time

def blocking_io(name: str, delay: float) -> str:
    print(f"start {name}")
    time.sleep(delay)
    print(f"end {name}")
    return f"done-{name}"

with ThreadPoolExecutor(max_workers=4) as pool:
    futures = [
        pool.submit(blocking_io, "a", 2),
        pool.submit(blocking_io, "b", 1),
    ]

    for future in futures:
        print(future.result())
```

## multi-process (python interprets to achive multi-threading with GIL)

> Processes avoid the GIL by using separate interpreter processes.

```py
from concurrent.futures import ProcessPoolExecutor

def cpu_heavy(n: int) -> int:
    total = 0
    for i in range(n):
        total += i * i
    return total

if __name__ == "__main__":
    with ProcessPoolExecutor() as pool:
        results = list(pool.map(cpu_heavy, [10_000_000, 10_000_000]))
        print(results)
```

## locking

```py
import threading

counter = 0
lock = threading.Lock()

def increment() -> None:
    global counter
    for _ in range(100_000):
        with lock:
            counter += 1
```

## Producer:Consumer

```py
import asyncio

async def producer(queue: asyncio.Queue[int]) -> None:
    for i in range(5):
        await queue.put(i)
    await queue.put(-1)

async def consumer(queue: asyncio.Queue[int]) -> None:
    while True:
        item = await queue.get()
        if item == -1:
            break
        print(f"processed {item}")

async def main() -> None:
    queue = asyncio.Queue()
    await asyncio.gather(producer(queue), consumer(queue))

asyncio.run(main())
```

## (FastAPI) offloading blocking calls (hybrid)

```py
from fastapi import FastAPI
import asyncio
import time

app = FastAPI()

def blocking_work() -> str:
    time.sleep(5)
    return "done"

@app.get("/better")
async def better_endpoint() -> dict[str, str]:
    result = await asyncio.to_thread(blocking_work)
    return {"message": result}
```

## Postgres

You need to think about:
 -  connection pooling
 -  transaction boundaries
 -  lock contention
 -  isolation levels
 -  long-running queries
 -  timeouts
 -  cancellation behavior

If an HTTP request is cancelled, you want to understand whether:
  - the Python coroutine is cancelled
  - the DB query is also cancelled
  - the connection is still healthy and returned to the pool correctly

That depends on the stack/library. Excellent interview point.

=========================================================================================

# INTERVIEW: Questions

17. Interview framing: when to choose what
Choose async when

    work is mostly waiting on network/DB
    libraries support async
    you want high request concurrency
    you’re building API services, chat servers, stream handlers

Choose threads when

    library is blocking/sync
    work is I/O-bound
    you need interoperability with sync code
    you need to avoid blocking the event loop

Choose processes when

    work is CPU-bound
    you want real parallel execution in CPython
    workloads are heavy enough to justify IPC overhead

18. Common interview questions with strong answers
Q1. What is the difference between concurrency and parallelism?

Answer:
Concurrency is the ability to make progress on multiple tasks over overlapping time. Parallelism means tasks are literally executing simultaneously, often on multiple CPU cores. Async gives concurrency without necessarily giving parallelism.
Q2. When should you use async in Python?

Answer:
Use async for I/O-bound work where tasks spend time waiting on network, database, sockets, or timers. It is especially effective in web APIs and external service orchestration when the libraries are async-aware.
Q3. Why don’t Python threads speed up CPU-bound code?

Answer:
In CPython, the GIL allows only one thread at a time to execute Python bytecode in a process. So threads are useful for I/O-bound work, but CPU-bound pure Python code usually needs multiprocessing for parallel speedup.
Q4. What’s the danger of calling blocking code inside an async FastAPI route?

Answer:
It blocks the event loop thread for that worker, reducing concurrency and throughput. The fix is to use async libraries or offload blocking work to a thread.
Q5. How does cancellation work in Python async code?

Answer:
Cancellation is cooperative. A task is cancelled by calling task.cancel(), and asyncio.CancelledError is raised at an await point. Code should catch it only when cleanup is needed, then usually re-raise it.
Q6. How would you stop a worker thread in Python?

Answer:
Usually with cooperative cancellation using something like threading.Event, since Python does not provide a clean general-purpose way to forcibly kill threads safely.
Q7. How would you design FastAPI with Postgres for high concurrency?

Answer:
Use async request handlers with an async Postgres driver or async ORM support, plus connection pooling, timeouts, and careful transaction management. Avoid using blocking DB calls directly inside async endpoints.
Q8. If a request is cancelled, what should you think about with Postgres?

Answer:
Whether the Python task is cancelled, whether the DB query is also cancelled, how the driver handles the connection, whether the transaction is rolled back, and whether the pooled connection is returned in a healthy state.
Q9. Would you use async for a CPU-heavy embedding pipeline?

Answer:
Not by itself. Async helps orchestrate I/O, but CPU-heavy embedding or preprocessing work should usually run in processes, worker queues, or native libraries that release the GIL.
Q10. In FastAPI, when would you choose a sync endpoint over an async endpoint?

Answer:
If the entire path is synchronous and blocking and I do not have async libraries for it, a sync endpoint can be simpler. If I need high concurrency with non-blocking I/O, I prefer async endpoints.

--------------------
# Mock Interview

19. Mock interview exercise
Prompt

Design a FastAPI service that:

 -  receives a request
 -  reads metadata from Postgres
 -  calls two external LLM-related services
 -  combines the result
 -  supports cancellation and timeouts

Strong answer structure

You could say:

 -  Use an async def FastAPI endpoint.
 -  Use an async Postgres client or SQLAlchemy async session.
 -  Launch the two external service calls concurrently with asyncio.gather.
 -  Put request-scoped timeouts around outbound calls.
 -  Ensure cancellation propagates cleanly.
 -  Avoid blocking libraries in the request path; if necessary, isolate them with asyncio.to_thread.
 -  Use DB connection pooling and short transactions.
 -  Add structured logging and tracing around external waits.
 -  For CPU-heavy post-processing, move it to a background worker or process pool.

That’s a very strong systems answer.

They often want to see if you know these pitfalls:

 -  “async makes everything faster” → false
 -  “threads are always parallel” → misleading in CPython
 -  “async is for CPU-bound work” → false
 -  “using async endpoint with sync DB driver is fine” → dangerous
 -  “cancellation is automatic everywhere” → false
 -  “Postgres async means no locking/performance issues” → false

```py
from fastapi import FastAPI, HTTPException
import asyncio

app = FastAPI()

async def fetch_user_context(user_id: int) -> dict[str, object]:
    await asyncio.sleep(0.05)  # pretend postgres/network I/O
    return {"user_id": user_id, "tier": "pro"}

async def call_model_a(prompt: str) -> str:
    await asyncio.sleep(0.3)
    return f"A:{prompt}"

async def call_model_b(prompt: str) -> str:
    await asyncio.sleep(0.4)
    return f"B:{prompt}"

@app.get("/analyze/{user_id}")
async def analyze(user_id: int, prompt: str) -> dict[str, object]:
    try:
        async with asyncio.timeout(2.0):
            user = await fetch_user_context(user_id)

            result_a, result_b = await asyncio.gather(
                call_model_a(prompt),
                call_model_b(prompt),
            )

            return {
                "user": user,
                "combined": [result_a, result_b],
            }

    except TimeoutError:
        raise HTTPException(status_code=504, detail="upstream timeout")
    except asyncio.CancelledError:
        # cleanup/log if needed, then re-raise
        raise
```
