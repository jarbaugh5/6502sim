import threading
from typing import List, Optional

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Footer, Header, Label, RichLog, Static, Switch

from clock import Clock
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
    #controls {
        height: auto;
        padding: 0 2;
        border-top: solid $surface-lighten-2;
    }
    #controls Label {
        padding: 1 1 0 0;
    }
    #step {
        margin-left: 2;
    }
    """

    BINDINGS = [
        ("escape", "quit", "Quit"),
        ("s", "step", "Step"),
    ]

    def __init__(
        self,
        placements: List[Placement],
        connections: List[Connection] | None = None,
        clock: Optional[Clock] = None,
    ) -> None:
        super().__init__()
        self._schematic = Schematic(placements, connections or [])
        self._clock = clock
        self._auto = False

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="body"):
            yield SchematicCanvas(self._schematic)
            yield RichLog(id="log", wrap=True, markup=True, highlight=True)
        with Horizontal(id="controls"):
            yield Label("Auto clock")
            yield Switch(value=False, id="auto")
            yield Button("Step ▶", id="step", variant="primary")
        yield Footer()

    def on_mount(self) -> None:
        self.begin_capture_print(self)

    def on_print(self, event: events.Print) -> None:
        text = event.text.rstrip()
        if not text:
            return
        log = self.query_one("#log", RichLog)
        log.write(f"[red]{text}[/red]" if event.stderr else text)

    def on_switch_changed(self, event: Switch.Changed) -> None:
        self._auto = event.value
        if self._clock is not None:
            self._clock.set_auto(event.value)
        self.query_one("#step", Button).disabled = event.value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "step":
            self.action_step()

    def action_step(self) -> None:
        if self._clock is not None and not self._auto:
            threading.Thread(target=self._clock.pulse, daemon=True).start()
