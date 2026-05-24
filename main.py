from clock import Clock
from component import Connection
from probe import Probe
from schematic import Placement
from visualizer import SimVisualizer


def main():
    clock = Clock()
    obstacle = Probe("MID")
    sink = Probe("PHI0")

    placements = [
        Placement(clock, "Clock", x=0, y=0),
        Placement(obstacle, "Block", x=20, y=0),
        Placement(sink, "Probe", x=40, y=0),
    ]
    connection = Connection(clock.get_pins()[0], sink.get_pins()[0], name="CLK0")

    SimVisualizer(placements, [connection]).run()


if __name__ == "__main__":
    main()
