from abc import abstractmethod, ABC
from enum import Enum
from typing import Callable, List, Optional


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


class ReadThroughPin(Pin):
    """An input terminal that reflects whatever pin currently drives it, like
    a wire. Its value is read on demand rather than pushed to it, so a bus
    reader sees the live bus value at the moment it latches."""

    def __init__(self, name: str = ""):
        super().__init__(name)
        self._source: Optional[Pin] = None

    def get_type(self) -> PinType:
        return PinType.INPUT

    def get_value(self) -> PinValue:
        return self._source.get_value() if self._source is not None else PinValue.ZERO


class Connection:
    """A wire from a source pin to a dest pin.

    A normal input pin is push-driven: it is updated whenever the source
    changes. A ReadThroughPin is instead bound to the source and reads it on
    demand (the source is passive and notifies no one)."""

    def __init__(self, source: Pin, dest: Pin, name: str = ""):
        self.name = name or f"{source.get_name()}-{dest.get_name()}"
        self.source = source
        self.dest = dest
        if isinstance(dest, ReadThroughPin):
            dest._source = source
        else:
            source.subscribe(self._propagate)
            dest.set_value(source.get_value())

    def _propagate(self, value: PinValue) -> None:
        self.dest.set_value(value)


class Component(ABC):
    @abstractmethod
    def get_pins(self) -> List[Pin]:
        pass