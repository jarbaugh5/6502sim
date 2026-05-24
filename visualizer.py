from typing import List

from textual.app import App, ComposeResult
from textual.widgets import Header, Static

from component import Connection
from schematic import Placement, Schematic


class SchematicCanvas(Static):
    def __init__(self, schematic: Schematic) -> None:
        super().__init__()
        self._schematic = schematic

    def on_mount(self) -> None:
        for pin in self._schematic.pins:
            pin.subscribe(lambda _v: self.app.call_from_thread(self._refresh))
        self._refresh()

    def _refresh(self) -> None:
        self.update(self._schematic.to_text())


class SimVisualizer(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    SchematicCanvas {
        padding: 1 2;
        height: auto;
    }
    """

    BINDINGS = [("escape", "quit", "Quit")]

    def __init__(
        self,
        placements: List[Placement],
        connections: List[Connection] | None = None,
    ) -> None:
        super().__init__()
        self._schematic = Schematic(placements, connections or [])

    def compose(self) -> ComposeResult:
        yield Header()
        yield SchematicCanvas(self._schematic)
