"""Code under test — the equivalent of the methods you'd put [Benchmark] on."""


def concat_plus(n: int) -> str:
    s = ""
    for i in range(n):
        s += str(i)
    return s


def concat_join(n: int) -> str:
    return "".join(str(i) for i in range(n))


def concat_join_list(n: int) -> str:
    return "".join([str(i) for i in range(n)])


def squares_loop(n: int) -> list[int]:
    out = []
    for i in range(n):
        out.append(i * i)
    return out


def squares_comp(n: int) -> list[int]:
    return [i * i for i in range(n)]


def squares_gen_sum(n: int) -> int:
    return sum(i * i for i in range(n))
