import threading
from typing import List, Optional

from component import Component, Pin, PinType, PinValue

CLOCK_HERTZ = 2


class Clock(Component):
    class OutPin(Pin):
        def __init__(self):
            super().__init__("CLK")
            self.state = PinValue.ZERO
            self._auto = False
            self._timer: Optional[threading.Timer] = None

        def get_type(self) -> PinType:
            return PinType.OUTPUT

        def get_value(self) -> PinValue:
            return self.state

        def _flip(self):
            if not self._auto:
                return
            self.state = PinValue.ONE if self.state == PinValue.ZERO else PinValue.ZERO
            self._notify()
            self._schedule_flip()

        def _schedule_flip(self):
            if not self._auto:
                return
            self._timer = threading.Timer(1.0 / CLOCK_HERTZ, self._flip)
            self._timer.daemon = True
            self._timer.start()

        def set_auto(self, auto: bool):
            if auto == self._auto:
                return
            self._auto = auto
            if auto:
                self._schedule_flip()
            elif self._timer is not None:
                self._timer.cancel()

        def pulse(self):
            """One manual clock cycle: a rising edge then a falling edge."""
            self.state = PinValue.ONE
            self._notify()
            self.state = PinValue.ZERO
            self._notify()

    def __init__(self):
        self._out_pin = Clock.OutPin()

    def get_pins(self) -> List[Pin]:
        return [self._out_pin]

    def set_auto(self, auto: bool) -> None:
        self._out_pin.set_auto(auto)

    def pulse(self) -> None:
        self._out_pin.pulse()
