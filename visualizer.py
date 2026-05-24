from typing import List

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Static

from component import Component, Connection, Pin, PinType, PinValue


class PinWidget(Static):
    def __init__(self, pin: Pin, index: int) -> None:
        super().__init__()
        self._pin = pin
        self._index = index

    def on_mount(self) -> None:
        self._pin.subscribe(lambda v: self.app.call_from_thread(self._update, v))
        self._update(self._pin.get_value())

    def _update(self, value: PinValue) -> None:
        pin_type = "OUT" if self._pin.get_type() == PinType.OUTPUT else " IN"
        label = self._pin.get_name() or f"Pin {self._index}"
        indicator = "●" if value == PinValue.ONE else "○"
        level = "HIGH" if value == PinValue.ONE else "LOW "
        self.update(f" {indicator}  {pin_type}  {label}  {level}")
        self.set_class(value == PinValue.ONE, "high")


class ComponentWidget(Vertical):
    DEFAULT_CSS = """
    ComponentWidget {
        border: solid $success-darken-2;
        margin: 1 2;
        padding: 0 1 1 1;
        width: 26;
        height: auto;
    }
    ComponentWidget > .title {
        text-align: center;
        color: $success;
        margin-bottom: 1;
    }
    PinWidget {
        height: 1;
        color: $text-muted;
    }
    PinWidget.high {
        color: $success;
    }
    """

    def __init__(self, component: Component, label: str) -> None:
        super().__init__()
        self._component = component
        self._label = label

    def compose(self) -> ComposeResult:
        yield Static(self._label, classes="title")
        for i, pin in enumerate(self._component.get_pins()):
            yield PinWidget(pin, i)


class ConnectionWidget(Static):
    def __init__(self, connection: Connection) -> None:
        super().__init__()
        self._connection = connection

    def on_mount(self) -> None:
        self._connection.source.subscribe(
            lambda v: self.app.call_from_thread(self._update, v)
        )
        self._update(self._connection.source.get_value())

    def _update(self, value: PinValue) -> None:
        on = value == PinValue.ONE
        marker = "●" if on else "○"
        src = self._connection.source.get_name()
        dst = self._connection.dest.get_name()
        self.update(f" {src} {marker}{'━' * 10}{marker} {dst}")
        self.set_class(on, "high")


class SimVisualizer(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    #components {
        height: auto;
    }
    #connections {
        height: auto;
        margin: 0 2;
    }
    #connections > .title {
        color: $accent;
    }
    ConnectionWidget {
        height: 1;
        color: $text-muted;
    }
    ConnectionWidget.high {
        color: $success;
    }
    """

    BINDINGS = [("escape", "quit", "Quit")]

    def __init__(
        self,
        components: dict[str, Component],
        connections: List[Connection] | None = None,
    ) -> None:
        super().__init__()
        self._components = components
        self._connections = connections or []

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="components"):
            for label, component in self._components.items():
                yield ComponentWidget(component, label)
        if self._connections:
            with Vertical(id="connections"):
                yield Static("Connections", classes="title")
                for connection in self._connections:
                    yield ConnectionWidget(connection)
