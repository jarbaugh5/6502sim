from clock import Clock
from component import Connection
from probe import Probe
from visualizer import SimVisualizer


def main():
    clock = Clock()
    probe = Probe("PHI0")
    connection = Connection(clock.get_pins()[0], probe.get_pins()[0], name="CLK0")
    SimVisualizer(
        {"Clock": clock, "Probe": probe},
        [connection],
    ).run()


if __name__ == "__main__":
    main()
