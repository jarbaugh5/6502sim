from abc import abstractmethod, ABC
from enum import Enum
from typing import List


class PinValue(Enum):
    ZERO = 0
    ONE = 1


class PinType(Enum):
    INPUT = 1
    OUTPUT = 2

class Pin(ABC):
    @abstractmethod
    def get_type(self) -> PinType:
        pass

    @abstractmethod
    def get_value(self) -> PinValue:
        pass

class Component(ABC):
    @abstractmethod
    def get_pins(self) -> List[Pin]:
        pass