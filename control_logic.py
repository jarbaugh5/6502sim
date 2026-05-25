from enum import IntEnum
from typing import Dict, List, Set

from component import Component, Pin, PinValue, PinType, InputPin


NUM_OPCODE_BITS = 6
NUM_STEP_BITS = 4


class OpCode(IntEnum):
    LDA = 0b000001  # Load Accumulator


class ControlLine(IntEnum):
    """Control signals the CPU drives high to steer data movement.

    Starter set — extend as the instruction set grows.
    """
    RO = 0  # RAM out -> bus
    AI = 1  # A register in <- bus


# For each opcode, which control lines are driven high at each step of its
# execution. Steps come from the InstructionCounter (the ring/step counter).
MICROCODE: Dict[OpCode, Dict[int, Set[ControlLine]]] = {
    OpCode.LDA: {
        2: {ControlLine.RO, ControlLine.AI},  # RAM out -> A register
    },
}


class Decoder:
    """Tracks the current opcode (6 bits) and step (4 bits); bit 0 = LSB."""

    def __init__(self):
        self._opcode_bits = [0] * NUM_OPCODE_BITS
        self._step_bits = [0] * NUM_STEP_BITS

    def set_opcode_bit(self, index: int, value: PinValue) -> None:
        self._opcode_bits[index] = 1 if value == PinValue.ONE else 0

    def set_step_bit(self, index: int, value: PinValue) -> None:
        self._step_bits[index] = 1 if value == PinValue.ONE else 0

    def get_opcode(self) -> int:
        return self._to_int(self._opcode_bits)

    def get_step(self) -> int:
        return self._to_int(self._step_bits)

    @staticmethod
    def _to_int(bits: List[int]) -> int:
        value = 0
        for i, bit in enumerate(bits):
            value |= bit << i
        return value

    def active_lines(self) -> Set[ControlLine]:
        try:
            opcode = OpCode(self.get_opcode())
        except ValueError:
            return set()
        return MICROCODE.get(opcode, {}).get(self.get_step(), set())


class ControlLogic(Component):
    class OpcodePin(InputPin):
        def __init__(self, num: int, decoder: Decoder):
            super().__init__("IN" + str(num))
            self.num = num
            self.decoder = decoder

        def set_value(self, value: PinValue):
            super().set_value(value)
            self.decoder.set_opcode_bit(self.num, value)

    class StepPin(InputPin):
        def __init__(self, num: int, decoder: Decoder):
            super().__init__("STEP" + str(num))
            self.num = num
            self.decoder = decoder

        def set_value(self, value: PinValue):
            super().set_value(value)
            self.decoder.set_step_bit(self.num, value)

    class OutPin(Pin):
        def __init__(self, line: ControlLine, decoder: Decoder):
            super().__init__(line.name)
            self.line = line
            self.decoder = decoder

        def get_type(self) -> PinType:
            return PinType.OUTPUT

        def get_value(self) -> PinValue:
            active = self.line in self.decoder.active_lines()
            return PinValue.ONE if active else PinValue.ZERO

    def __init__(self):
        super().__init__()
        self.decoder = Decoder()
        self._pins = (
            [self.OpcodePin(i, self.decoder) for i in range(NUM_OPCODE_BITS)]
            + [self.StepPin(i, self.decoder) for i in range(NUM_STEP_BITS)]
            + [self.OutPin(line, self.decoder) for line in ControlLine]
        )

    def get_pins(self) -> List[Pin]:
        return self._pins
