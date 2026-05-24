from abc import abstractmethod, ABC
from enum import Enum
from typing import Callable, List


class PinValue(Enum):
    ZERO = 0
    ONE = 1


class PinType(Enum):
    INPUT = 1
    OUTPUT = 2


class Pin(ABC):
    def __init__(self, name: str = ""):
        self._name = name
        self._subscribers: List[Callable[[PinValue], None]] = []

    def get_name(self) -> str:
        return self._name

    def subscribe(self, callback: Callable[[PinValue], None]) -> None:
        self._subscribers.append(callback)

    def _notify(self) -> None:
        for cb in self._subscribers:
            cb(self.get_value())

    @abstractmethod
    def get_type(self) -> PinType:
        pass

    @abstractmethod
    def get_value(self) -> PinValue:
        pass


class InputPin(Pin):
    def __init__(self, name: str = ""):
        super().__init__(name)
        self._value = PinValue.ZERO

    def get_type(self) -> PinType:
        return PinType.INPUT

    def get_value(self) -> PinValue:
        return self._value

    def set_value(self, value: PinValue) -> None:
        if value != self._value:
            self._value = value
            self._notify()


class Connection:
    """A wire driving one input pin from a source pin's value."""

    def __init__(self, source: Pin, dest: InputPin, name: str = ""):
        self.name = name or f"{source.get_name()}-{dest.get_name()}"
        self.source = source
        self.dest = dest
        source.subscribe(self._propagate)
        dest.set_value(source.get_value())

    def _propagate(self, value: PinValue) -> None:
        self.dest.set_value(value)


class Component(ABC):
    @abstractmethod
    def get_pins(self) -> List[Pin]:
        pass