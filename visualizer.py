from typing import List

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Header, RichLog, Static

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
    #body {
        height: 1fr;
    }
    SchematicCanvas {
        width: 1fr;
        padding: 1 2;
    }
    #log {
        width: 40;
        border-left: solid $surface-lighten-2;
        background: $surface;
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
        with Horizontal(id="body"):
            yield SchematicCanvas(self._schematic)
            yield RichLog(id="log", wrap=True, markup=True, highlight=True)

    def on_mount(self) -> None:
        self.begin_capture_print(self)

    def on_print(self, event: events.Print) -> None:
        text = event.text.rstrip()
        if not text:
            return
        log = self.query_one("#log", RichLog)
        log.write(f"[red]{text}[/red]" if event.stderr else text)
