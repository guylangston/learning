

def double(x:int) -> int:
    x = bob(x)
    return x*3

def bob(x) -> str:
    x = str(x) + "1"
    return x


evens_doubled = [double(x) for x in range(10) if x % 2 == 0]

print(evens_doubled)
