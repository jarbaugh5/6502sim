from bus import Bus
from clock import Clock
from component import Connection
from instruction_counter import InstructionCounter
from instruction_register import InstructionRegister
from program_counter import ProgramCounter
from schematic import Placement
from visualizer import SimVisualizer


def main():
    clock = Clock()
    program_counter = ProgramCounter()
    bus = Bus()
    instruction_register = InstructionRegister()
    instruction_counter = InstructionCounter()

    placements = [
        Placement(clock, "Clock", x=0, y=0),
        Placement(program_counter, "Program Counter", x=20, y=0),
        Placement(bus, "Bus", x=40, y=20),
        Placement(instruction_counter, "InstructionCounter", x=0, y=10),
        Placement(instruction_register, "InstructionRegister", x=0, y=20),
    ]

    wires = [
        Connection(clock.get_pins()[0], instruction_counter.get_pins()[0])
    ] + [
        Connection(bus.get_pins()[i], instruction_register.get_pins()[i + 2]) for i in range(len(bus.get_pins()))
    ]

    SimVisualizer(placements, wires).run()


if __name__ == "__main__":
    main()
