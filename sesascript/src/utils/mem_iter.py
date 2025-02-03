from __future__ import annotations
from typing import Iterator
from dataclasses import dataclass, field

@dataclass(slots=True)
class MemIter[T]:
    """
        A memory iterator
        allows to iterate through an iterator and memorise it's elements
        for later use
        can be split to allow iteration that doesn't effect the original
        iterator unless explicitly updating the direct parent
    """
    iterator: Iterator[T]
    index: int = field(default=-1, init=False)
    elements: list[T] = field(default_factory=list, init=False)
    parent: MemIter | None = field(default=None, init=False)
    
    @property
    def value(self):
        if self.index == -1:
            raise IndexError(
                "MemIter: Iteration hasn't started yet."
            )
        return self.elements[self.index]
    def __iter__(self):
        return self
    
    def go_back_by(self, n: int):
        """
            To go back to a previouse value by n terms
        """
        self.index -= n
        self.index = max(0, self.index)
    def __next__(self):
        self.index += 1
        if self.index >= len(self.elements):
            value = next(self.iterator)
            self.elements.append(value)
        return self
    def split(self, offset: int = 0):
        """
            split the iterator to allow iteration that doesn't effect the original
        """
        value = MemIter(self.iterator)
        value.elements = self.elements
        value.index = self.index - 1 + offset
        value.index = max(-1, value.index)
        value.parent = self
        return value
    def update_parent(self):
        if self.parent is None: return
        self.parent.index = self.index
