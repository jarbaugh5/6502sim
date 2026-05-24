"""Absolute (x, y) placement of components plus orthogonal wire routing.

Components are drawn as boxes on a character grid at caller-chosen
coordinates. Each connection is routed as an orthogonal wire that treats
every component box as an obstacle, so wires path *around* components
rather than through them.
"""

import heapq
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from rich.text import Text

from component import Component, Connection, Pin, PinType, PinValue

MARGIN = 2
TURN_COST = 1
CROSS_COST = 4

Point = Tuple[int, int]

DIRS: Dict[str, Point] = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}

JUNCTION = {
    frozenset("EW"): "─",
    frozenset("NS"): "│",
    frozenset("NE"): "└",
    frozenset("NW"): "┘",
    frozenset("SE"): "┌",
    frozenset("SW"): "┐",
    frozenset("NSE"): "├",
    frozenset("NSW"): "┤",
    frozenset("NEW"): "┴",
    frozenset("SEW"): "┬",
    frozenset("NSEW"): "┼",
    frozenset("N"): "╵",
    frozenset("S"): "╷",
    frozenset("E"): "╶",
    frozenset("W"): "╴",
}

HIGH_STYLE = "bold green"
LOW_STYLE = "grey42"
BOX_STYLE = "grey62"
TITLE_STYLE = "bold cyan"


@dataclass
class Placement:
    component: Component
    label: str
    x: int
    y: int


@dataclass
class _Box:
    label: str
    x: int
    y: int
    w: int
    h: int
    pins: List[Pin]

    def pin_row(self, i: int) -> int:
        return self.y + 2 + i


@dataclass
class _Wire:
    connection: Connection
    path: List[Point]
    cells: Dict[Point, Set[str]] = field(default_factory=dict)


def _pin_label(pin: Pin, index: int) -> str:
    return pin.get_name() or f"P{index}"


def route(
    start: Point,
    goal: Point,
    blocked: Set[Point],
    width: int,
    height: int,
    used: Set[Point],
) -> List[Point]:
    """A* orthogonal route from start to goal avoiding blocked cells.

    Turns and crossing already-used wire cells are penalized so paths
    stay straight and spread out. Returns [] if no route exists.
    """
    start_state = (start[0], start[1], None)
    counter = 0
    pq: List[Tuple[int, int, int, Tuple[int, int, Optional[str]]]] = [
        (_manhattan(start, goal), 0, counter, start_state)
    ]
    came: Dict[Tuple[int, int, Optional[str]], Tuple[int, int, Optional[str]]] = {}
    best: Dict[Tuple[int, int, Optional[str]], int] = {start_state: 0}

    while pq:
        _, g, _, state = heapq.heappop(pq)
        x, y, d = state
        if (x, y) == goal:
            return _reconstruct(came, state)
        for nd, (dx, dy) in DIRS.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            if (nx, ny) in blocked:
                continue
            cost = 1
            if d is not None and nd != d:
                cost += TURN_COST
            if (nx, ny) in used:
                cost += CROSS_COST
            ng = g + cost
            nstate = (nx, ny, nd)
            if ng < best.get(nstate, 1 << 30):
                best[nstate] = ng
                came[nstate] = state
                counter += 1
                heapq.heappush(pq, (ng + _manhattan((nx, ny), goal), ng, counter, nstate))
    return []


def _manhattan(a: Point, b: Point) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _reconstruct(came, state) -> List[Point]:
    path = []
    while state in came:
        path.append((state[0], state[1]))
        state = came[state]
    path.append((state[0], state[1]))
    path.reverse()
    return path


class Schematic:
    def __init__(self, placements: List[Placement], connections: List[Connection]):
        self._connections = connections
        self._boxes: Dict[Component, _Box] = {}
        self._ports: Dict[int, Tuple[int, int, str]] = {}  # id(pin) -> (px, py, side)
        self._connectors: Dict[Point, str] = {}  # box-border attach char
        self._wires: List[_Wire] = []

        self._layout(placements)
        self._route_all()

    @property
    def pins(self) -> List[Pin]:
        return [p for box in self._boxes.values() for p in box.pins]

    def _layout(self, placements: List[Placement]) -> None:
        min_x = min(p.x for p in placements)
        min_y = min(p.y for p in placements)
        off_x = MARGIN - min_x
        off_y = MARGIN - min_y

        for pl in placements:
            pins = pl.component.get_pins()
            names = [_pin_label(p, i) for i, p in enumerate(pins)]
            content_w = max([len(pl.label)] + [2 + len(n) for n in names])
            w = content_w + 4  # 2 padding + 2 borders
            h = len(pins) + 3
            box = _Box(pl.label, pl.x + off_x, pl.y + off_y, w, h, pins)
            self._boxes[pl.component] = box
            for i, pin in enumerate(pins):
                py = box.pin_row(i)
                if pin.get_type() == PinType.OUTPUT:
                    self._ports[id(pin)] = (box.x + box.w, py, "E")
                else:
                    self._ports[id(pin)] = (box.x - 1, py, "W")

        self.width = max(b.x + b.w for b in self._boxes.values()) + MARGIN
        self.height = max(b.y + b.h for b in self._boxes.values()) + MARGIN

        self._blocked: Set[Point] = set()
        for b in self._boxes.values():
            for yy in range(b.y, b.y + b.h):
                for xx in range(b.x, b.x + b.w):
                    self._blocked.add((xx, yy))

    def _route_all(self) -> None:
        used: Set[Point] = set()
        for conn in self._connections:
            src = self._ports.get(id(conn.source))
            dst = self._ports.get(id(conn.dest))
            if src is None or dst is None:
                continue
            start = (src[0], src[1])
            goal = (dst[0], dst[1])
            path = route(start, goal, self._blocked, self.width, self.height, used)
            if not path:
                continue
            used |= set(path)
            wire = _Wire(conn, path)
            self._build_wire_cells(wire, src[2], dst[2])
            self._wires.append(wire)
            self._connectors[(self._boxes_edge(conn.source))] = "├"
            self._connectors[(self._boxes_edge(conn.dest))] = "┤"

    def _boxes_edge(self, pin: Pin) -> Point:
        px, py, side = self._ports[id(pin)]
        return (px - 1, py) if side == "E" else (px + 1, py)

    def _build_wire_cells(self, wire: _Wire, src_side: str, dst_side: str) -> None:
        path = wire.path
        for a, b in zip(path, path[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            for name, (ox, oy) in DIRS.items():
                if (ox, oy) == (dx, dy):
                    fwd = name
                if (ox, oy) == (-dx, -dy):
                    back = name
            wire.cells.setdefault(a, set()).add(fwd)
            wire.cells.setdefault(b, set()).add(back)
        # connect endpoints back toward their boxes
        wire.cells.setdefault(path[0], set()).add("W" if src_side == "E" else "E")
        wire.cells.setdefault(path[-1], set()).add("E" if dst_side == "W" else "W")

    def _build_grids(self) -> Tuple[List[List[str]], List[List[Optional[str]]]]:
        chars = [[" "] * self.width for _ in range(self.height)]
        styles: List[List[Optional[str]]] = [
            [None] * self.width for _ in range(self.height)
        ]

        def put(x: int, y: int, ch: str, style: Optional[str]) -> None:
            if 0 <= y < self.height and 0 <= x < self.width:
                chars[y][x] = ch
                styles[y][x] = style

        # component boxes
        for box in self._boxes.values():
            self._draw_box(box, put)

        # box-border connectors
        for (x, y), ch in self._connectors.items():
            put(x, y, ch, BOX_STYLE)

        # wires (drawn last; combine direction masks across crossing wires)
        combined: Dict[Point, Set[str]] = {}
        owner: Dict[Point, Connection] = {}
        for wire in self._wires:
            for cell, dirs in wire.cells.items():
                combined.setdefault(cell, set()).update(dirs)
                owner.setdefault(cell, wire.connection)
        for cell, dirs in combined.items():
            ch = JUNCTION.get(frozenset(dirs), "·")
            high = owner[cell].source.get_value() == PinValue.ONE
            put(cell[0], cell[1], ch, HIGH_STYLE if high else LOW_STYLE)

        return chars, styles

    def _draw_box(self, box: _Box, put) -> None:
        x, y, w, h = box.x, box.y, box.w, box.h
        put(x, y, "┌", BOX_STYLE)
        put(x + w - 1, y, "┐", BOX_STYLE)
        put(x, y + h - 1, "└", BOX_STYLE)
        put(x + w - 1, y + h - 1, "┘", BOX_STYLE)
        for xx in range(x + 1, x + w - 1):
            put(xx, y, "─", BOX_STYLE)
            put(xx, y + h - 1, "─", BOX_STYLE)
        for yy in range(y + 1, y + h - 1):
            put(x, yy, "│", BOX_STYLE)
            put(x + w - 1, yy, "│", BOX_STYLE)

        interior = w - 2
        title = box.label.center(interior)
        for j, ch in enumerate(title):
            put(x + 1 + j, y + 1, ch, TITLE_STYLE)

        for i, pin in enumerate(box.pins):
            py = box.pin_row(i)
            high = pin.get_value() == PinValue.ONE
            style = HIGH_STYLE if high else LOW_STYLE
            indicator = "●" if high else "○"
            text = f" {indicator} {_pin_label(pin, i)}".ljust(interior)
            for j, ch in enumerate(text):
                put(x + 1 + j, py, ch, style)

    def to_text(self) -> Text:
        chars, styles = self._build_grids()
        out = Text()
        for y in range(self.height):
            for x in range(self.width):
                out.append(chars[y][x], style=styles[y][x] or "")
            if y < self.height - 1:
                out.append("\n")
        return out

    def to_ascii(self) -> str:
        chars, _ = self._build_grids()
        return "\n".join("".join(row).rstrip() for row in chars)
