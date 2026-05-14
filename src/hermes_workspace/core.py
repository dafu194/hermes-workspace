"""Core utilities for Hermes workspace."""


def add(a: int, b: int) -> int:
    return a + b


def fibonacci(n: int) -> list[int]:
    if n <= 0:
        return []
    if n == 1:
        return [0]
    seq = [0, 1]
    for _ in range(2, n):
        seq.append(seq[-1] + seq[-2])
    return seq
