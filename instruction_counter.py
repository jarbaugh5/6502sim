from typing import List

from component import Component, Pin, PinValue, PinType, InputPin


class InternalCounter:
    value = 0

    def inc(self):
        self.value += 1
        if self.value > 15:
            self.value = 0

    def get_value(self):
        return self.value

class InstructionCounter(Component):
    class InPin(InputPin):
        def __init__(self, counter: InternalCounter, out_pins: List[Pin]):
            super().__init__("CLK")
            self.counter = counter
            self.out_pins = out_pins

        def set_value(self, value: PinValue):
            super().set_value(value)
            if value == PinValue.ONE:
                self.counter.inc()
                for pin in self.out_pins:
                    pin._notify()

    class OutPin(Pin):
        def __init__(self, num: int, counter: InternalCounter):
            super().__init__("OUT" + str(num))
            self.num = num
            self.counter = counter

        def get_type(self) -> PinType:
            return PinType.OUTPUT

        def get_value(self) -> PinValue:
            bit = (self.counter.get_value() >> self.num) & 1
            return PinValue.ONE if bit else PinValue.ZERO

    def __init__(self):
        super().__init__()
        self.counter = InternalCounter()
        self._out_pins = [self.OutPin(i, self.counter) for i in range(4)]
        self._pins = [self.InPin(self.counter, self._out_pins)] + self._out_pins

    def get_pins(self) -> List[Pin]:
        return self._pins