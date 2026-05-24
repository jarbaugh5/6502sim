import threading
from typing import List

from component import Component, Pin, PinType, PinValue

CLOCK_HERTZ = 2

class Clock(Component):
    class OutPin(Pin):
        def get_type(self) -> PinType:
            return PinType.OUTPUT

        def __init__(self):
            self.state = PinValue.ZERO
            self._schedule_flip()

        def _flip(self):
            if self.state == PinValue.ZERO:
                self.state = PinValue.ONE
            else:
                self.state = PinValue.ZERO
            print("flip: " + str(self.state))
            self._schedule_flip()

        def _schedule_flip(self):
            delta = 1.0 / CLOCK_HERTZ
            threading.Timer(delta, lambda: self._flip()).start()

        def get_value(self) -> PinValue:
            return self.state


    out_pin = OutPin()
    def get_pins(self) -> List[Pin]:
        return [self.out_pin]