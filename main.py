from clock import Clock
from component import Connection
from probe import Probe
from program_counter import ProgramCounter
from schematic import Placement
from visualizer import SimVisualizer


def main():
    clock = Clock()
    program_counter = ProgramCounter()

    placements = [
        Placement(clock, "Clock", x=0, y=0),
        Placement(program_counter, "Program Counter", x=20, y=0)
    ]

    wire1 = Connection(clock.get_pins()[0], program_counter.get_pins()[0])

    SimVisualizer(placements, [wire1]).run()


if __name__ == "__main__":
    main()
