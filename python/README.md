# Learning: Python from C#

> Good place to start [python.org docs](https://docs.python.org/release/3.14.4/tutorial/introduction.html)

- __method__ is called a dunder/magic method

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
