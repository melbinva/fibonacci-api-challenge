from __future__ import annotations


def fibonacci(n: int) -> int:
    """Return the nth Fibonacci number."""

    # Fibonacci numbers are only defined for non-negative indices.
    if n < 0:
        raise ValueError("n must be >= 0")

    # Base cases:
    # F(0) = 0
    # F(1) = 1
    if n < 2:
        return n

    # Initialize the first two Fibonacci numbers:
    # prev = F(0)
    # curr = F(1)
    prev, curr = 0, 1

    # Compute Fibonacci numbers from F(2) up to F(n).
    #
    # Loop invariant:
    #   prev = F(i - 1)
    #   curr = F(i)
    #
    # After each iteration, advance to the next Fibonacci number.
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr

    # curr now contains F(n).
    return curr