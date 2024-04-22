from typing import Any, Callable, TypeVar, Iterable


T = TypeVar("T")


def each(funct: Callable[[T], None | Any], items: Iterable[T]) -> None | Any:
    for i in items:
        funct(i)


X = TypeVar("X")


class Queue(Iterable[X]):
    def __init__(self, items: list[X] | None = None):
        if items:
            self.__items: list = items.copy()
        else:
            self.__items: list = []

    def __iter__(self):
        while len(self.__items) != 0:
            yield self.pop()

    def pop(self) -> X:
        if len(self.__items) == 0:
            raise IndexError("Queue has no items in it to pop")
        item: X = self.__items[0]
        self.__items = self.__items[1:]
        return item

    def remove(self, item: X):
        if item in self.__items:
            self.__items.remove(item)

    def shift(self, size=1):
        tail = self.__items[:size]
        head = self.__items[size:]
        self.__items = head + tail

    def push(self, item: X):
        self.__items.append(item)
        return self

    def __len__(self):
        return len(self.__items)

    def __str__(self) -> str:
        return f"{self.__items}"

    def __repr__(self) -> str:
        return f"{self.__items}"
    
    def magic_refilling(self,selector: Callable[[X], bool])->None | X:
        """It searches for first item that return true for the selector callback,
        if any found, it will pop it from the queue and push it to the end of the queue
         and returns the item.

        Args:
            selector (Callable[[X], bool]): _description_

        Returns:
            None | X: _description_
        """
        
        matching_item = None
        
        for item in self.__items:
            if selector(item):
                matching_item = item 
                break 
            
        if matching_item:
            self.__items.remove(matching_item)
            self.push(matching_item)
            return matching_item
        return None

    @property
    def items(
        self,
    ):
        return self.__items.copy()

    def count(self):
        return len(self.__items)
