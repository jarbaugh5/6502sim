from time import sleep

from clock import Clock


def main():
    clock = Clock()
    pin = clock.get_pins()[0]
    while True:
        print(pin.get_value())
        sleep(.25)


if __name__ == "__main__":
    main()
