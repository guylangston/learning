# General prompts

I am a C# senior developer learning python for AI/LLM. I have an understanding of the python basics and am trying to prepare for a tech interview.

Please generate a primer.

## Follow-up topics

- How are complex types defined?
- How are dunder methods implemented, what is the mechanism?
- How are enums defined/supported?
- More details on decorators


-------------------------------------------------

# Python Primer for C# Senior Developers (AI/LLM Interview Focus)

This primer maps your C# knowledge to Python, highlights gotchas, and focuses on patterns that come up in AI/LLM interviews.

---

## 1. Syntax & Type System Differences

| Concept | C# | Python |
|---|---|---|
| Typing | Static, mandatory | Dynamic, optional (type hints) |
| Null | `null` | `None` |
| String interpolation | `$"Hello {name}"` | `f"Hello {name}"` |
| Conventions | `PascalCase` methods | `snake_case` functions |
| Access modifiers | `public`/`private` | Convention only (`_private`, `__mangled`) |
| Interfaces | `IMyInterface` | Abstract Base Classes / Protocols |

```python
# Type hints (not enforced at runtime, but expected in interviews)
def embed_text(text: str, model: str = "text-embedding-ada-002") -> list[float]:
    ...

# Python has no "var" — just assign
x = 42
name: str = "langston"   # hint only, still dynamic
```

---

## 2. Collections — Know These Cold

```python name=collections_demo.py
# List  → like List<T>
tokens = ["the", "cat", "sat"]
tokens.append("down")
tokens[1:3]          # slicing → ["cat", "sat"]  (no equivalent in C# without LINQ)

# Dict  → like Dictionary<K,V>
scores = {"gpt4": 0.91, "claude": 0.88}
scores.get("llama", 0.0)   # safe get with default

# Set  → like HashSet<T>
seen = {1, 2, 3}

# Tuple  → immutable, like ValueTuple
point = (1.0, 2.0)

# List comprehension  (very common in AI code)
embeddings = [model.encode(t) for t in tokens]
filtered    = [t for t in tokens if len(t) > 2]

# Dict comprehension
token_len = {t: len(t) for t in tokens}
```

---

## 3. Classes & OOP

```python name=oop_demo.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

# Abstract base class (like an interface)
class Embedder(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]: ...

# Dataclass  → like a C# record
@dataclass
class Document:
    id: str
    content: str
    embedding: list[float] | None = None   # union type (Python 3.10+)

# Concrete implementation
class OpenAIEmbedder(Embedder):
    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model           # no "this", always "self"

    def embed(self, text: str) -> list[float]:
        # ...call API...
        return [0.1, 0.2, 0.3]

# Dunder methods  → like operator overloads / ToString()
class Vector:
    def __init__(self, data: list[float]):
        self.data = data

    def __repr__(self) -> str:          # like ToString()
        return f"Vector({self.data})"

    def __len__(self) -> int:           # len(v)
        return len(self.data)

    def __add__(self, other: "Vector"): # v1 + v2
        return Vector([a + b for a, b in zip(self.data, other.data)])
```

---

## 4. Functional Patterns (Very Common in AI Code)

```python name=functional_demo.py
from functools import reduce
from typing import Callable

tokens = ["Hello", "world", "LLM"]

# map / filter  (prefer comprehensions in modern Python)
upper   = list(map(str.upper, tokens))
long    = list(filter(lambda t: len(t) > 4, tokens))

# Lambda  → like C# Func<T,R> inline
sorter: Callable[[str], int] = lambda s: len(s)
tokens.sort(key=sorter)

# reduce  → like C# Aggregate()
total_len = reduce(lambda acc, t: acc + len(t), tokens, 0)

# *args and **kwargs  → like params + named args
def call_llm(prompt: str, *examples: str, temperature: float = 0.7, **kwargs):
    print(prompt, examples, temperature, kwargs)
```

---

## 5. Generators & Iterators (Critical for Large Data / Streaming LLMs)

```python name=generators_demo.py
from typing import Generator, Iterator

# Generator function  — yields lazily (like IEnumerable + yield return)
def token_stream(text: str) -> Generator[str, None, None]:
    for word in text.split():
        yield word          # pauses here, resumes on next()

# Generator expression  (memory-efficient alternative to list comp)
lengths = (len(t) for t in token_stream("hello world foo"))

# Consuming
for token in token_stream("stream this text"):
    print(token)

# next() with default  — safe pull
gen = token_stream("one token")
print(next(gen, None))   # "one"
print(next(gen, None))   # "token"
print(next(gen, None))   # None  ← no StopIteration exception
```
> 💡 **Interview tip:** Streaming LLM responses use generators. Know how to wrap an API stream with `yield`.

---

## 6. Async / Await

Python's async model is similar to C# `async/await` but **single-threaded** (event loop via `asyncio`).

```python name=async_demo.py
import asyncio
import aiohttp

# async def  → like C# async Task<T>
async def fetch_completion(prompt: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/...", json={"prompt": prompt}) as resp:
            data = await resp.json()
            return data["choices"][0]["text"]

# Run concurrently  → like Task.WhenAll()
async def batch_completions(prompts: list[str]) -> list[str]:
    tasks = [fetch_completion(p) for p in prompts]
    return await asyncio.gather(*tasks)

# Entry point
if __name__ == "__main__":
    results = asyncio.run(batch_completions(["Hello", "World"]))
```

---

## 7. Error Handling

```python name=exceptions_demo.py
# try/except/else/finally  → like try/catch/finally
try:
    result = call_api()
except ValueError as e:          # specific exception
    print(f"Bad value: {e}")
except (TimeoutError, OSError):   # multiple types
    print("I/O problem")
except Exception as e:            # catch-all (use sparingly)
    raise RuntimeError("Unexpected") from e   # chained exception
else:
    print("Success:", result)     # runs only if no exception
finally:
    cleanup()

# Custom exceptions
class TokenLimitError(ValueError):
    def __init__(self, limit: int, actual: int):
        super().__init__(f"Token limit {limit} exceeded: got {actual}")
        self.limit = limit
        self.actual = actual
```

---

## 8. Decorators (Used Everywhere in AI Frameworks)

```python name=decorators_demo.py
import time
from functools import wraps
from typing import Callable

# Decorator  → like C# Attributes, but executable at runtime
def retry(max_attempts: int = 3):
    def decorator(func: Callable):
        @wraps(func)            # preserves func metadata
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(2 ** attempt)   # exponential backoff
        return wrapper
    return decorator

@retry(max_attempts=3)
def call_llm_api(prompt: str) -> str:
    ...   # LangChain, OpenAI SDK, etc. use decorators heavily
```

---

## 9. Key AI/LLM Libraries — Know the APIs

```python name=llm_libraries.py
# --- NumPy (arrays & math) ---
import numpy as np
v1 = np.array([0.1, 0.2, 0.3])
v2 = np.array([0.4, 0.5, 0.6])
cosine_sim = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# --- Pandas (data manipulation) ---
import pandas as pd
df = pd.DataFrame({"text": ["hello", "world"], "label": [0, 1]})
df[df["label"] == 1]["text"].tolist()

# --- OpenAI SDK ---
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Explain RAG in one sentence."}]
)
print(response.choices[0].message.content)

# --- LangChain pattern ---
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("user", "{question}")
])
chain = prompt | ChatOpenAI(model="gpt-4o")
result = chain.invoke({"question": "What is a vector database?"})
```

---

## 10. Interview-Critical Python Concepts

### Context Managers (`with`) → like `using` in C#
```python name=context_manager.py
# Built-in
with open("data.txt", "r") as f:
    content = f.read()   # file auto-closed

# Custom context manager
from contextlib import contextmanager

@contextmanager
def timer(label: str):
    start = time.perf_counter()
    yield                               # code inside `with` runs here
    elapsed = time.perf_counter() - start
    print(f"{label}: {elapsed:.3f}s")

with timer("embedding generation"):
    embeddings = [model.encode(t) for t in tokens]
```

### Unpacking & Spread
```python name=unpacking.py
a, b, *rest = [1, 2, 3, 4, 5]   # a=1, b=2, rest=[3,4,5]

# Merge dicts  → like { ...obj1, ...obj2 } in JS / new Dictionary + AddRange
config   = {"model": "gpt-4o", "temp": 0.7}
override = {"temp": 0.2, "max_tokens": 512}
merged   = {**config, **override}   # override wins
```

### `enumerate` and `zip`
```python name=iteration.py
# enumerate  → index + value (no for(int i=0;...) needed)
for i, token in enumerate(tokens):
    print(i, token)

# zip  → parallel iteration
for doc, embedding in zip(documents, embeddings):
    store(doc.id, embedding)
```

---

## 11. Common Gotchas for C# Devs

| Gotcha | C# Behavior | Python Behavior |
|---|---|---|
| Mutable default args | N/A | **Never** use `def f(x=[])` — shared across calls; use `None` |
| `==` vs `is` | `==` is value equality | `==` is value, `is` is identity (`is None` not `== None`) |
| Integer division | `5 / 2 = 2` | `5 / 2 = 2.5`; use `5 // 2 = 2` for int division |
| Everything is a reference | Value types vs ref types | Everything is an object/reference |
| `list.copy()` | Assign copies value types | Assign copies the **reference**; use `.copy()` or `list()` |
| GIL | True multithreading | Threads are limited by GIL; use `multiprocessing` or `asyncio` |

```python name=gotchas.py
# Mutable default argument gotcha
def bad(items=[]):        # DON'T — list is shared
    items.append(1)
    return items

def good(items=None):     # DO
    if items is None:
        items = []
    items.append(1)
    return items

# is vs ==
x = None
if x is None:   # correct
    pass

# Shallow vs deep copy
import copy
original = [[1, 2], [3, 4]]
shallow  = original.copy()     # inner lists still shared
deep     = copy.deepcopy(original)  # fully independent
```

---

## 12. Interview Cheat Sheet

| Topic | What to Know |
|---|---|
| **Data structures** | list, dict, set, deque, heapq, Counter, defaultdict |
| **Comprehensions** | list, dict, set, generator expressions |
| **Itertools** | `chain`, `islice`, `product`, `groupby` |
| **Typing** | `Optional`, `Union`, `TypeVar`, `Generic`, `Protocol` |
| **Concurrency** | `asyncio.gather`, `ThreadPoolExecutor`, `ProcessPoolExecutor` |
| **Testing** | `pytest`, `unittest.mock.patch`, `MagicMock` |
| **AI patterns** | RAG pipeline, cosine similarity, token chunking, streaming |

---

> **Focus areas for LLM/AI interviews:** generators for streaming, async for batched API calls, dataclasses for structured outputs, numpy for vector math, and decorator patterns used in frameworks like LangChain and FastAPI.
