"""Pure game logic for Sokoban — no I/O, fully testable."""

from collections import deque
from enum import Enum
from typing import FrozenSet, List, Optional, Set, Tuple


class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)


# Raw level characters
WALL = "#"
FLOOR = " "
PLAYER = "@"
BOX = "$"
TARGET = "."
BOX_ON_TARGET = "*"
PLAYER_ON_TARGET = "+"

# Levels are public-domain Sokoban layouts
LEVELS: list[list[str]] = [
    [   # 1 – warm-up
        "#####",
        "#@  #",
        "# $ #",
        "#  .#",
        "#####",
    ],
    [   # 2 – two boxes
        "#######",
        "#.    #",
        "#  $  #",
        "##.$  #",
        " #  @ #",
        " ######",
    ],
    [   # 3 – tight corridor
        "  #####",
        "###   #",
        "# $@. #",
        "# $ # #",
        "#.    #",
        "#.#####",
        "###    ",
    ],
    [   # 4 – four boxes
    "  #####",
    "  # . #",
    "### $ #",
    "# . $@#",
    "#   ###",
    "#####  ",
    ],
    [   # 4 – classic cross
        "   #####   ",
        "   #   #   ",
        "   #$  #   ",
        " ### #$##  ",
        " #  $ . #  ",
        " # @# ## # ",
        " #  $    # ",
        " ##  ##### ",
        "  #   #    ",
        "  #####    ",
    ],
]

LEVELS[3] = [   # 4 – L-bend; solution: ← ← → ↑
]


class GameState:
    def __init__(
        self,
        grid: List[List[str]],
        player: Tuple[int, int],
        boxes: Set[Tuple[int, int]],
        targets: Set[Tuple[int, int]],
        outside: FrozenSet[Tuple[int, int]],
    ) -> None:
        self.grid = grid
        self.player = player
        self.boxes: Set[Tuple[int, int]] = set(boxes)
        self.targets: Set[Tuple[int, int]] = set(targets)
        self.outside = outside   # floor cells not enclosed by walls
        self.moves = 0
        self.pushes = 0
        self._history: List[Tuple] = []

    # ── dimensions ──────────────────────────────────────────────

    @property
    def rows(self) -> int:
        return len(self.grid)

    @property
    def cols(self) -> int:
        return max((len(r) for r in self.grid), default=0)

    # ── cell queries ─────────────────────────────────────────────

    def is_wall(self, r: int, c: int) -> bool:
        if r < 0 or r >= len(self.grid):
            return True
        row = self.grid[r]
        if c < 0 or c >= len(row):
            return True
        return row[c] == WALL

    def is_box(self, r: int, c: int) -> bool:
        return (r, c) in self.boxes

    def is_target(self, r: int, c: int) -> bool:
        return (r, c) in self.targets

    def is_passable(self, r: int, c: int) -> bool:
        return not self.is_wall(r, c) and not self.is_box(r, c)

    # ── move logic ───────────────────────────────────────────────

    def can_move(self, direction: Direction) -> bool:
        dr, dc = direction.value
        pr, pc = self.player
        nr, nc = pr + dr, pc + dc

        if self.is_wall(nr, nc):
            return False

        if self.is_box(nr, nc):
            br, bc = nr + dr, nc + dc
            if self.is_wall(br, bc) or self.is_box(br, bc):
                return False

        return True

    def move(self, direction: Direction) -> bool:
        if not self.can_move(direction):
            return False

        self._history.append(
            (self.player, frozenset(self.boxes), self.moves, self.pushes)
        )

        dr, dc = direction.value
        pr, pc = self.player
        nr, nc = pr + dr, pc + dc

        if self.is_box(nr, nc):
            br, bc = nr + dr, nc + dc
            self.boxes.discard((nr, nc))
            self.boxes.add((br, bc))
            self.pushes += 1

        self.player = (nr, nc)
        self.moves += 1
        return True

    def undo(self) -> bool:
        if not self._history:
            return False
        player, boxes, moves, pushes = self._history.pop()
        self.player = player
        self.boxes = set(boxes)
        self.moves = moves
        self.pushes = pushes
        return True

    def is_complete(self) -> bool:
        return bool(self.boxes) and self.boxes.issubset(self.targets)

    # ── display ──────────────────────────────────────────────────

    def display_char(self, r: int, c: int) -> str:
        if (r, c) == self.player:
            return PLAYER_ON_TARGET if self.is_target(r, c) else PLAYER
        if self.is_box(r, c):
            return BOX_ON_TARGET if self.is_target(r, c) else BOX
        if self.is_target(r, c):
            return TARGET
        return self.grid[r][c]

    # ── pathfinding (for mouse click-to-move) ────────────────────

    def find_path(self, target: Tuple[int, int]) -> Optional[List[Direction]]:
        """BFS from player to target, avoiding walls and boxes."""
        start = self.player
        if start == target:
            return []
        queue: deque = deque([(start, [])])
        visited: Set[Tuple[int, int]] = {start}
        while queue:
            (r, c), path = queue.popleft()
            for d in Direction:
                dr, dc = d.value
                nr, nc = r + dr, c + dc
                pos = (nr, nc)
                if pos in visited or self.is_wall(nr, nc) or self.is_box(nr, nc):
                    continue
                new_path = path + [d]
                if pos == target:
                    return new_path
                visited.add(pos)
                queue.append((pos, new_path))
        return None


# ── level parser ─────────────────────────────────────────────────────────────


def _find_outside(grid: List[List[str]], rows: int, cols: int) -> FrozenSet[Tuple[int, int]]:
    """BFS from every border cell through non-wall tiles to find exterior cells."""
    outside: Set[Tuple[int, int]] = set()
    queue: deque = deque()

    def seed(r: int, c: int) -> None:
        if grid[r][c] != WALL and (r, c) not in outside:
            outside.add((r, c))
            queue.append((r, c))

    for r in range(rows):
        seed(r, 0)
        seed(r, cols - 1)
    for c in range(cols):
        seed(0, c)
        seed(rows - 1, c)

    while queue:
        r, c = queue.popleft()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in outside and grid[nr][nc] != WALL:
                outside.add((nr, nc))
                queue.append((nr, nc))

    return frozenset(outside)


def parse_level(lines: List[str]) -> GameState:
    grid: List[List[str]] = []
    player: Optional[Tuple[int, int]] = None
    boxes: Set[Tuple[int, int]] = set()
    targets: Set[Tuple[int, int]] = set()

    for r, line in enumerate(lines):
        row: List[str] = []
        for c, ch in enumerate(line):
            if ch == PLAYER:
                player = (r, c)
                row.append(FLOOR)
            elif ch == PLAYER_ON_TARGET:
                player = (r, c)
                targets.add((r, c))
                row.append(TARGET)
            elif ch == BOX:
                boxes.add((r, c))
                row.append(FLOOR)
            elif ch == BOX_ON_TARGET:
                boxes.add((r, c))
                targets.add((r, c))
                row.append(TARGET)
            elif ch == TARGET:
                targets.add((r, c))
                row.append(TARGET)
            else:
                row.append(ch)
        grid.append(row)

    max_cols = max((len(row) for row in grid), default=0)
    for row in grid:
        while len(row) < max_cols:
            row.append(FLOOR)

    if player is None:
        raise ValueError("Level has no player (@)")

    outside = _find_outside(grid, len(grid), max_cols)
    return GameState(grid, player, boxes, targets, outside)
