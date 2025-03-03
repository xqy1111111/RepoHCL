from functools import reduce


def prefix_with(s: str, p: str) -> str:
    return reduce(lambda x, y: x + y, map(lambda k: p + k + '\n', s.splitlines()))
