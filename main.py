from bus import Bus
from clock import Clock
from component import Connection
from control_logic import ControlLogic
from instruction_counter import InstructionCounter
from instruction_register import InstructionRegister
from program_counter import ProgramCounter
from schematic import Placement
from visualizer import SimVisualizer


def pins_named(component, prefix):
    return [p for p in component.get_pins() if p.get_name().startswith(prefix)]


def main():
    clock = Clock()
    program_counter = ProgramCounter()
    bus = Bus()
    instruction_register = InstructionRegister()
    instruction_counter = InstructionCounter()
    control_logic = ControlLogic()

    placements = [
        Placement(bus, "Bus", x=0, y=0),
        Placement(clock, "Clock", x=0, y=22),
        Placement(program_counter, "Program Counter", x=0, y=28),
        Placement(instruction_register, "InstructionRegister", x=28, y=0),
        Placement(instruction_counter, "InstructionCounter", x=28, y=30),
        Placement(control_logic, "ControlLogic", x=62, y=5),
    ]

    wires = (
        [Connection(clock.get_pins()[0], instruction_counter.get_pins()[0])]
        + [
            Connection(bus.get_pins()[i], instruction_register.get_pins()[i + 2])
            for i in range(len(bus.get_pins()))
        ]
        + [
            Connection(src, dst)
            for src, dst in zip(pins_named(instruction_register, "OP"), pins_named(control_logic, "IN"))
        ]
        + [
            Connection(src, dst)
            for src, dst in zip(pins_named(instruction_counter, "OUT"), pins_named(control_logic, "STEP"))
        ]
    )

    SimVisualizer(placements, wires).run()


if __name__ == "__main__":
    main()
