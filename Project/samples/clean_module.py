"""A small, well-documented arithmetic utility module."""


def add(first, second):
    """Return the sum of two numbers."""
    return first + second


def multiply(first, second):
    """Return the product of two numbers."""
    return first * second


def test_add():
    """Verify add() returns the correct sum."""
    assert add(2, 3) == 5


def test_multiply():
    """Verify multiply() returns the correct product."""
    assert multiply(2, 3) == 6
