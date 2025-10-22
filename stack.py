# stack.py
from typing import Generic, TypeVar

T = TypeVar("T")

class Stack(Generic[T]):

    def __init__(self) -> None:
        self._container: list[T] = []

    def push(self, value: T) -> None:
        self._container.append(value)

    def pop(self) -> T:
        """
        Remove and return the top element.
        Raises IndexError if stack is empty.
        """
        if not self._container:
            raise IndexError("pop from empty stack")
        return self._container.pop()

    def top(self) -> T:
        """
        Return (but do not remove) the top element.
        Raises IndexError if stack is empty.
        """
        if not self._container:
            raise IndexError("top from empty stack")
        return self._container[-1]

    def empty(self) -> bool:
        """Return True if the stack is empty."""
        return not self._container

    def size(self) -> int:
        """Return the number of elements in the stack."""
        return len(self._container)

    def clear(self) -> None:
        """Remove all elements."""
        self._container.clear()

    def __repr__(self) -> str:
        return f"stack({self._container!r})"

    # Optional: C++-like equality comparison
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Stack):
            return NotImplemented
        return self._container == other._container

    def tolist(self) -> list[T]:
        return self._container

    def bottom(self) -> T:
        return self._container[0]