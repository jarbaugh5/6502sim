import threading
from typing import List

from component import Component, Pin, PinType, PinValue

CLOCK_HERTZ = 2


class Clock(Component):
    class OutPin(Pin):
        def __init__(self):
            super().__init__("CLK")
            self.state = PinValue.ZERO
            self._schedule_flip()

        def get_type(self) -> PinType:
            return PinType.OUTPUT

        def get_value(self) -> PinValue:
            return self.state

        def _flip(self):
            self.state = PinValue.ONE if self.state == PinValue.ZERO else PinValue.ZERO
            self._notify()
            self._schedule_flip()

        def _schedule_flip(self):
            timer = threading.Timer(1.0 / CLOCK_HERTZ, self._flip)
            timer.daemon = True
            timer.start()

    def __init__(self):
        self._out_pin = Clock.OutPin()

    def get_pins(self) -> List[Pin]:
        return [self._out_pin]