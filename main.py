from accumulator import Accumulator
from bus import Bus
from clock import Clock
from component import Connection
from control_logic import ControlLogic
from instruction_counter import InstructionCounter
from instruction_register import InstructionRegister
from memory_address_register import MemoryAddressRegister
from program_counter import ProgramCounter
from ram import RAM
from schematic import Placement
from visualizer import SimVisualizer


def pins_named(component, prefix):
    return [p for p in component.get_pins() if p.get_name().startswith(prefix)]


def pin_named(component, name):
    return next(p for p in component.get_pins() if p.get_name() == name)


def main():
    clock = Clock()
    bus = Bus()
    program_counter = ProgramCounter()
    instruction_register = InstructionRegister()
    instruction_counter = InstructionCounter()
    control_logic = ControlLogic()
    memory_address_register = MemoryAddressRegister()
    accumulator = Accumulator()
    # Preload address 0 with an LDA instruction (opcode 000001) to demonstrate fetch.
    ram = RAM(data={0: 0b000001})

    placements = [
        Placement(bus, "Bus", x=0, y=0),
        Placement(clock, "Clock", x=0, y=22),
        Placement(program_counter, "Program Counter", x=0, y=28),
        Placement(instruction_register, "InstructionRegister", x=28, y=0),
        Placement(instruction_counter, "InstructionCounter", x=28, y=30),
        Placement(control_logic, "ControlLogic", x=62, y=5),
        Placement(memory_address_register, "MemoryAddressRegister", x=28, y=42),
        Placement(accumulator, "Accumulator", x=62, y=28),
        Placement(ram, "RAM", x=62, y=50),
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
        + [
            Connection(src, dst)
            for src, dst in zip(bus.get_pins(), pins_named(memory_address_register, "D"))
        ]
        + [
            Connection(src, dst)
            for src, dst in zip(bus.get_pins(), pins_named(accumulator, "D"))
        ]
        + [
            Connection(src, dst)
            for src, dst in zip(pins_named(program_counter, "OUT"), bus.get_pins())
        ]
        + [
            Connection(src, dst)
            for src, dst in zip(pins_named(ram, "D"), bus.get_pins())
        ]
        + [
            Connection(src, dst)
            for src, dst in zip(pins_named(memory_address_register, "A"), pins_named(ram, "A"))
        ]
        + [
            Connection(pin_named(control_logic, "MI"), pin_named(memory_address_register, "LOAD")),
            Connection(pin_named(control_logic, "II"), pin_named(instruction_register, "LOAD")),
            Connection(pin_named(control_logic, "CE"), pin_named(program_counter, "INC")),
            Connection(pin_named(control_logic, "CO"), pin_named(program_counter, "CO")),
            Connection(pin_named(control_logic, "RO"), pin_named(ram, "RO")),
            Connection(pin_named(control_logic, "AI"), pin_named(accumulator, "LOAD")),
        ]
    )

    SimVisualizer(placements, wires, clock=clock).run()


if __name__ == "__main__":
    main()
