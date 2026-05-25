from typing import List

from component import Component, Pin, PinValue, PinType, InputPin, ReadThroughPin


NUM_DATA_BITS = 16
NUM_ADDR_BITS = 8


class Register:
    """Holds the latched address word."""

    def __init__(self):
        self.value = 0

    def load(self, value: int) -> None:
        self.value = value & ((1 << NUM_DATA_BITS) - 1)

    def get_bit(self, num: int) -> int:
        return (self.value >> num) & 1


class MemoryAddressRegister(Component):
    class LoadPin(InputPin):
        def __init__(self, register: Register, data_pins: List[Pin]):
            super().__init__("LOAD")
            self.register = register
            self.data_pins = data_pins

        def set_value(self, value: PinValue):
            super().set_value(value)
            if value == PinValue.ONE:
                bits = 0
                for i, pin in enumerate(self.data_pins):
                    if pin.get_value() == PinValue.ONE:
                        bits |= 1 << i
                self.register.load(bits)

    class AddrPin(Pin):
        def __init__(self, num: int, register: Register):
            super().__init__("A" + str(num))
            self.num = num
            self.register = register

        def get_type(self) -> PinType:
            return PinType.OUTPUT

        def get_value(self) -> PinValue:
            return PinValue.ONE if self.register.get_bit(self.num) else PinValue.ZERO

    def __init__(self):
        super().__init__()
        self.register = Register()
        self.data_pins = [ReadThroughPin(name="D" + str(i)) for i in range(NUM_DATA_BITS)]
        self.addr_pins = [self.AddrPin(i, self.register) for i in range(NUM_ADDR_BITS)]
        self._pins = [
            self.LoadPin(self.register, self.data_pins),
            InputPin(name="ENABLE"),
        ] + self.data_pins + self.addr_pins

    def get_pins(self) -> List[Pin]:
        return self._pins
