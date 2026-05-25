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
        def __init__(self, counter: InternalCounter):
            super().__init__("CLK")
            self.counter = counter

        def set_value(self, value: PinValue):
            super().set_value(value)
            if value == PinValue.ONE:
                self.counter.inc()

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
        self._pins = [
            self.InPin(self.counter),
            self.OutPin(0, self.counter),
            self.OutPin(1, self.counter),
            self.OutPin(2, self.counter),
            self.OutPin(3, self.counter)
        ]

    def get_pins(self) -> List[Pin]:
        return self._pins