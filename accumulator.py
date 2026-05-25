from typing import List

from component import Component, Pin, PinValue, InputPin, ReadThroughPin


NUM_DATA_BITS = 16


class Register:
    def __init__(self):
        self.value = 0

    def load(self, value: int) -> None:
        self.value = value & ((1 << NUM_DATA_BITS) - 1)

    def get_bit(self, num: int) -> int:
        return (self.value >> num) & 1


class Accumulator(Component):
    class LoadPin(InputPin):
        def __init__(self, register: Register, data_pins: List[InputPin]):
            super().__init__("LOAD")
            self.register = register
            self.data_pins = data_pins

        def set_value(self, value: PinValue) -> None:
            super().set_value(value)
            if value == PinValue.ONE:
                bits = 0
                for i, pin in enumerate(self.data_pins):
                    if pin.get_value() == PinValue.ONE:
                        bits |= 1 << i
                self.register.load(bits)

    def __init__(self):
        super().__init__()
        self.register = Register()
        self.data_pins = [ReadThroughPin(name="D" + str(i)) for i in range(NUM_DATA_BITS)]
        self.load_pin = self.LoadPin(self.register, self.data_pins)
        self._pins = [self.load_pin] + self.data_pins

    def get_pins(self) -> List[Pin]:
        return self._pins
