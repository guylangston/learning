# Learning: Python from C#

Good place to start [python.org docs](https://docs.python.org/release/3.14.4/tutorial/introduction.html):
 - https://docs.python.org/3.14/tutorial/stdlib.html

Quick info:
- `__method__` is called a dunder/magic method

## lamda


```py
lambda x: x + 1
```

## Conditional/tenary operator:

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
