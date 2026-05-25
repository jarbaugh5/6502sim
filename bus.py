from typing import List

from component import Component, Pin, PinType, PinValue


class BusPin(Pin):
    """A bidirectional pin that does not auto-notify on value change."""

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
    """A 16-pin bidirectional bus. Pins read and write but don't auto-notify."""

    def __init__(self, num_pins: int = 16):
        self._pins: List[Pin] = [
            BusPin(f"D{i}") for i in range(num_pins)
        ]

    def get_pins(self) -> List[Pin]:
        return self._pins

    def notify_all(self) -> None:
        """Manually notify subscribers on all pins."""
        for pin in self._pins:
            pin._notify()
