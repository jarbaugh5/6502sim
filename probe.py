from typing import List

from component import Component, InputPin, Pin


class Probe(Component):
    """A logic probe: a single input pin that reflects whatever drives it."""

    def __init__(self, name: str = "IN"):
        self._in_pin = InputPin(name)

    def get_pins(self) -> List[Pin]:
        return [self._in_pin]
