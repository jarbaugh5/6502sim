from typing import List

from component import Component, Pin, InputPin


class InstructionRegister(Component):
    def __init__(self):
        super().__init__()
        self.pins = [
            InputPin(name="LOAD"),
            InputPin(name="ENABLE"),
        ] + [InputPin(name="DIN" + str(i)) for i in range(16)]

    def get_pins(self) -> List[Pin]:
        return self.pins


