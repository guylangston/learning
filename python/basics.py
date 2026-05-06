from datetime import datetime
import math
import subprocess
import numpy as np

print("\033[2J\033[H", end="")  # Clear screen + move cursor to top-left
  # \033  [  2  J    \033  [  H      end=""
  # │     │  │  │    │     │  │      │
  # ESC   CSI 2  │   ESC  CSI │      no newline
  #           │  │            │
  #           │  Erase        Cursor home
  #           │  display      (top-left)
  #           │
  #           whole screen
print(f"--- {datetime.now()} ---")

def double(x:int) -> int:
    x = int(bob(x))
    return x*3

def bob(x) -> str:
    """ bob adds a one char to x """
    x = str(x) + "1"
    return x

evens_doubled = [double(x) for x in range(10) if x % 2 == 0]
# print(evens_doubled)

some_list = ["bob", 1, datetime(2026,2,11), datetime.now(), 3.14, math.pi]

if False:
    for x in some_list:  # pyright: ignore[reportUnreachable]
        print(x)

    res = subprocess.run(
        ["ls", "-la"],
        capture_output=True,
        text=True
    )
    # how to get key:values from res
    def iterate_kv(obj) -> list[str]:
        if isinstance(obj, dict):
            items = obj.items()
        else:
            items = vars(obj).items()   # works for class instances

        for key, value in items:
            print(f"{key}: {value}")
        return items

    iterate_kv(res)

str1 = "hello world"
t = list(str1)
t[6] = 'W'
str2 = "".join(t)
print(str1, "|", str2)
print(id(str1))

aa = np.array([1, 3, 5, 7, 8, 11])
print(type(aa))

