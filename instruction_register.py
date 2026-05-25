from typing import List

from component import Component, Pin, PinValue, PinType, InputPin


NUM_DATA_BITS = 16
NUM_OPCODE_BITS = 6


class Register:
    """Holds the latched instruction word."""

    def __init__(self):
        self.value = 0

    def load(self, value: int) -> None:
        self.value = value & ((1 << NUM_DATA_BITS) - 1)

    def get_bit(self, num: int) -> int:
        return (self.value >> num) & 1


class InstructionRegister(Component):
    class LoadPin(InputPin):
        def __init__(self, register: Register, din_pins: List[InputPin], opcode_pins: List[Pin]):
            super().__init__("LOAD")
            self.register = register
            self.din_pins = din_pins
            self.opcode_pins = opcode_pins

        def set_value(self, value: PinValue):
            super().set_value(value)
            if value == PinValue.ONE:
                bits = 0
                for i, pin in enumerate(self.din_pins):
                    if pin.get_value() == PinValue.ONE:
                        bits |= 1 << i
                self.register.load(bits)
                for pin in self.opcode_pins:
                    pin._notify()

    class OpcodePin(Pin):
        def __init__(self, num: int, register: Register):
            super().__init__("OP" + str(num))
            self.num = num
            self.register = register

        def get_type(self) -> PinType:
            return PinType.OUTPUT

        def get_value(self) -> PinValue:
            return PinValue.ONE if self.register.get_bit(self.num) else PinValue.ZERO

    def __init__(self):
        super().__init__()
        self.register = Register()
        self.din_pins = [InputPin(name="DIN" + str(i)) for i in range(NUM_DATA_BITS)]
        self.opcode_pins = [self.OpcodePin(i, self.register) for i in range(NUM_OPCODE_BITS)]
        self._pins = (
            [
                self.LoadPin(self.register, self.din_pins, self.opcode_pins),
                InputPin(name="ENABLE"),
            ]
            + self.din_pins
            + self.opcode_pins
        )

    def get_pins(self) -> List[Pin]:
        return self._pins
