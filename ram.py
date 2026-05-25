from typing import Dict, List, Optional

from component import Component, InputPin, Pin, PinType, PinValue, ReadThroughPin


NUM_DATA_BITS = 16
NUM_ADDR_BITS = 8
SIZE = 1 << NUM_ADDR_BITS


class RAM(Component):
    class RoPin(InputPin):
        def __init__(self, data_pins: List["RAM.DataPin"]):
            super().__init__("RO")
            self.data_pins = data_pins

        def set_value(self, value: PinValue) -> None:
            super().set_value(value)
            if value == PinValue.ONE:
                for pin in self.data_pins:
                    pin._notify()

    class DataPin(Pin):
        def __init__(self, num: int, memory: List[int], addr_pins: List[Pin]):
            super().__init__("D" + str(num))
            self.num = num
            self.memory = memory
            self.addr_pins = addr_pins

        def get_type(self) -> PinType:
            return PinType.OUTPUT

        def _address(self) -> int:
            addr = 0
            for i, pin in enumerate(self.addr_pins):
                if pin.get_value() == PinValue.ONE:
                    addr |= 1 << i
            return addr

        def get_value(self) -> PinValue:
            word = self.memory[self._address()]
            return PinValue.ONE if (word >> self.num) & 1 else PinValue.ZERO

    def __init__(self, data: Optional[Dict[int, int]] = None):
        super().__init__()
        self.memory: List[int] = [0] * SIZE
        if data:
            for addr, value in data.items():
                self.memory[addr & (SIZE - 1)] = value & ((1 << NUM_DATA_BITS) - 1)
        self.addr_pins = [ReadThroughPin(name="A" + str(i)) for i in range(NUM_ADDR_BITS)]
        self.data_pins = [self.DataPin(i, self.memory, self.addr_pins) for i in range(NUM_DATA_BITS)]
        self._pins = [self.RoPin(self.data_pins)] + self.addr_pins + self.data_pins

    def get_pins(self) -> List[Pin]:
        return self._pins
