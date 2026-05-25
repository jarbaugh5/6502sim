from enum import IntEnum
from typing import Dict, List, Set

from component import Component, Pin, PinValue, PinType, InputPin


NUM_OPCODE_BITS = 6
NUM_STEP_BITS = 4


class OpCode(IntEnum):
    LDA = 0b000001  # Load Accumulator


class ControlLine(IntEnum):
    """Control signals the CPU drives high to steer data movement.

    Extend as the instruction set grows.
    """
    CO = 0  # Program Counter out -> bus
    MI = 1  # Memory Address Register in/load <- bus
    RO = 2  # RAM out/enable -> bus
    II = 3  # Instruction Register in/load <- bus
    CE = 4  # Program Counter enable/increment
    AI = 5  # A register in <- bus


# The fetch cycle runs at the start of every instruction, regardless of
# opcode: point the MAR at the address in the PC, read that byte into the
# instruction register, then advance the PC.
FETCH: Dict[int, Set[ControlLine]] = {
    1: {ControlLine.CO, ControlLine.MI},  # PC -> bus -> MAR
    2: {ControlLine.RO, ControlLine.II},  # RAM -> bus -> IR
    3: {ControlLine.CE},                  # PC += 1
}

# Per-opcode microcode for the steps *after* the shared fetch (step 4+).
MICROCODE: Dict[OpCode, Dict[int, Set[ControlLine]]] = {
    OpCode.LDA: {
        4: {ControlLine.RO, ControlLine.AI},  # RAM out -> A register (placeholder)
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
        step = self.get_step()
        lines = set(FETCH.get(step, set()))
        try:
            opcode = OpCode(self.get_opcode())
        except ValueError:
            return lines
        return lines | MICROCODE.get(opcode, {}).get(step, set())


class ControlLogic(Component):
    class OpcodePin(InputPin):
        def __init__(self, num: int, decoder: Decoder, out_pins: List["ControlLogic.OutPin"]):
            super().__init__("IN" + str(num))
            self.num = num
            self.decoder = decoder
            self.out_pins = out_pins

        def set_value(self, value: PinValue):
            super().set_value(value)
            self.decoder.set_opcode_bit(self.num, value)
            for pin in self.out_pins:
                pin.refresh()

    class StepPin(InputPin):
        def __init__(self, num: int, decoder: Decoder, out_pins: List["ControlLogic.OutPin"]):
            super().__init__("STEP" + str(num))
            self.num = num
            self.decoder = decoder
            self.out_pins = out_pins

        def set_value(self, value: PinValue):
            super().set_value(value)
            self.decoder.set_step_bit(self.num, value)
            for pin in self.out_pins:
                pin.refresh()

    class OutPin(Pin):
        def __init__(self, line: ControlLine, decoder: Decoder):
            super().__init__(line.name)
            self.line = line
            self.decoder = decoder
            self._value = self._compute()

        def get_type(self) -> PinType:
            return PinType.OUTPUT

        def _compute(self) -> PinValue:
            active = self.line in self.decoder.active_lines()
            return PinValue.ONE if active else PinValue.ZERO

        def get_value(self) -> PinValue:
            return self._value

        def refresh(self) -> None:
            value = self._compute()
            if value != self._value:
                self._value = value
                self._notify()

    def __init__(self):
        super().__init__()
        self.decoder = Decoder()
        self._out_pins = [self.OutPin(line, self.decoder) for line in ControlLine]
        self._pins = (
            [self.OpcodePin(i, self.decoder, self._out_pins) for i in range(NUM_OPCODE_BITS)]
            + [self.StepPin(i, self.decoder, self._out_pins) for i in range(NUM_STEP_BITS)]
            + self._out_pins
        )

    def get_pins(self) -> List[Pin]:
        return self._pins
