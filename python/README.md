# Learning: Python from C#

Good place to start [python.org docs](https://docs.python.org/release/3.14.4/tutorial/introduction.html):
 - https://docs.python.org/3.14/tutorial/stdlib.html

# Question List

- [x] lambda method
- [x] async vs concurrent vs threading vs multi-processing vs IO
- [x] import/module mechanism
- [ ] scope, visibility (private,protected,public)
- [ ] __init__ vs __new__
- [ ] FastAPI
- [ ] postgres
- [ ] explain the python type + type annotation system
- [ ] explain iterators in more detail
- [ ] explain `ContextManagers` and __enter__, __exit__ in more detail
- [ ] does python have generics list C# `List<Person>`
- [ ] explain `Protocol` in more detail ("extremely pythonic", like interfaces)
- [ ] C# `Func<T>` use `from collections.abc import Callable` where ABC => Abstract Base Class

# Pythons is
- Python is very duck-typed: If it behaves like what I need, I can use it.
- Python byte-code locked by GIL (global python lock)
- Python is protocol based. `from typing import Protocol`
- Python uses gradual typing.

Quick info:
- `__method__` is called a dunder/magic method. They are not meant to be called directly most of the time.
Instead, Python calls them for you when you use language features.
- `__str__` human string; `__repr__` debug string
- `__bool__` where an object is in `True` state?
- `__eq__`, `__ne__` object.Equals(), `NotImplemented` type for `C#:NotSupported+lang feature`
- `__contains__` allows `if 123 in some_list`, If __contains__ is absent, Python may try iteration.
- `__call__(self, ...)` Makes an instance callable like a function.
- `__hash__` -> `C# object.GetHashCode()`
- `cast(str, some_unknown_val)` does nothing at runtime, just aids static typing/tooling


## imports
- `import module` ≈ “load this file as a named namespace object”
- `from module import thing` ≈ “bring this member into local scope”
- module-level variables/functions/classes ≈ static members inside a namespace-like container
- package structure ≈ folder-based namespace organization

## visibility
 Python does not have C#-style access modifiers.

Instead, it uses naming conventions:

    name → public by convention
    _name → “internal/protected-ish” by convention
    __name → triggers name mangling to avoid accidental access/override
    __name__ → special “dunder” names reserved for Python protocols, not privacy


## typeing

- `def find_name(id: int) -> str | None:` modern vs `def find_name(id: int) -> Optional[str]:`
- unions `int | float`
- collections:
```
people: list[Person]
lookup: dict[str, Person]
pairs: list[tuple[str, int]]
```
- type aliases:
```
type UserId = int
type ScoresByUser = dict[UserId, list[float]]
```

## lamda

```py
lambda x: x + 1
```

## Conditional/ternary operator:

```c_sharp
var some_var = x == 1 ? : "one" : "other"
```

```py
some_var = "one" if x == 1 else "other"
```

## Reflection

```py
def iterate_kv(obj) -> list[str]:
    if isinstance(obj, dict):
        items = obj.items()
    else:
        items = vars(obj).items()   # works for class instances

    for key, value in items:
        print(f"{key}: {value}")
    return items

iterate_kv(res)
```

## Multi-Threading (No: GIL), async (Yes, but message pump/loop and a single thread)

> I am learning python as a C# senior developer. The doc have said that python uses a async message queue so never block the async calls. 
> However, the online guide (https://docs.python.org/3.14/tutorial/stdlib2.html#multi-threading) says that python does have threading. Is it correct that this is NOT used for the  async implementation -- if correct, why is that?

The GIL: Why Python threads aren't like C# threads
The critical thing to understand first is the Global Interpreter Lock (GIL). CPython (the standard Python runtime) has a lock that ensures only one thread executes Python bytecode at a time. This means:

Python threads are real OS threads (like C# Thread or Task with Thread affinity)
But they cannot run Python code truly in parallel on multiple cores simultaneously
The GIL is released during I/O waits and some C extension calls, which is why threading still has some use

So Python threading is genuinely weaker than C# threading for CPU-bound work. This is a known limitation of CPython.

## Learning with AI

> I am a C# senior developer learning python for AI/LLM. I have an understanding of the python basics and am trying to prepare for a tech interview.
> Please generate a primer.
