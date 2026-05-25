from typing import List

from component import Component, Pin, PinType, PinValue


class BusPin(Pin):
    """A bidirectional bus line. A driver writes its value; readers sample it
    on demand. It is passive — setting it stores the value and notifies no one
    (the bus is just wires, not an active broadcaster)."""

    def __init__(self, name: str = ""):
        super().__init__(name)
        self._value = PinValue.ZERO

    def get_type(self) -> PinType:
        return PinType.INPUT

    def get_value(self) -> PinValue:
        return self._value

    def set_value(self, value: PinValue) -> None:
        self._value = value


class Bus(Component):
    """A 16-pin bidirectional data bus."""

    def __init__(self, num_pins: int = 16):
        self._pins: List[Pin] = [BusPin(f"D{i}") for i in range(num_pins)]

    def get_pins(self) -> List[Pin]:
        return self._pins
