#!/usr/bin/env python3
"""Sokoban TUI — ncurses + mouse support."""

import curses
import sys
from typing import Optional

from game import (
    BOX, BOX_ON_TARGET, FLOOR, PLAYER, PLAYER_ON_TARGET, TARGET, WALL,
    Direction, GameState, parse_level, LEVELS,
)

# ── colour pair IDs ──────────────────────────────────────────────────────────
C_WALL = 1
C_FLOOR = 2
C_PLAYER = 3
C_BOX = 4
C_TARGET = 5
C_BOX_TARGET = 6
C_PLAYER_TARGET = 7
C_TITLE = 8
C_STATUS = 9
C_WIN = 10

# xterm-256color grayscale ramp (indices 232–255)
_FLOOR_BG = 235   # ~#262626  muted dark-grey interior floor
_WALL_FG  = 245   # ~#8a8a8a  stone-grey wall glyph

CELL_W = 2  # each grid cell occupies 2 terminal columns (square feel)

# Unicode glyphs (all single display-column wide)
_G_WALL     = "██"   # U+2588 FULL BLOCK
_G_FLOOR    = "  "   # coloured background conveys the cell
_G_PLAYER   = "◉ "   # U+25C9 FISHEYE
_G_BOX      = "■ "   # U+25A0 BLACK SQUARE
_G_TARGET   = "◇ "   # U+25C7 WHITE DIAMOND  (empty = unfilled goal)
_G_BOX_TGT  = "◆ "   # U+25C6 BLACK DIAMOND  (filled = achieved)
_G_PLR_TGT  = "◉ "   # same glyph, different colour pair


class SokobanApp:
    def __init__(self, stdscr: curses.window) -> None:
        self.stdscr = stdscr
        self.level_idx = 0
        self.state: GameState = parse_level(LEVELS[self.level_idx])
        self.message = ""
        self.ROW_OFF = 2   # top rows reserved for title
        self.COL_OFF = 4   # left cols reserved for margin
        self._init_curses()

    def _init_curses(self) -> None:
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()

        has_256 = curses.COLORS >= 256
        floor_bg = _FLOOR_BG if has_256 else curses.COLOR_BLACK
        wall_fg  = _WALL_FG  if has_256 else curses.COLOR_WHITE

        # Every in-map colour pair shares the same floor background so the
        # interior reads as a unified grey rectangle against the terminal default.
        curses.init_pair(C_WALL,          wall_fg,              floor_bg)
        curses.init_pair(C_FLOOR,         floor_bg,             floor_bg)
        curses.init_pair(C_PLAYER,        curses.COLOR_CYAN,    floor_bg)
        curses.init_pair(C_BOX,           curses.COLOR_YELLOW,  floor_bg)
        curses.init_pair(C_TARGET,        curses.COLOR_RED,     floor_bg)
        curses.init_pair(C_BOX_TARGET,    curses.COLOR_GREEN,   floor_bg)
        curses.init_pair(C_PLAYER_TARGET, curses.COLOR_MAGENTA, floor_bg)
        curses.init_pair(C_TITLE,         curses.COLOR_WHITE,   curses.COLOR_BLUE)
        curses.init_pair(C_STATUS,        curses.COLOR_BLACK,   curses.COLOR_WHITE)
        curses.init_pair(C_WIN,           curses.COLOR_BLACK,   curses.COLOR_GREEN)

        # Enable mouse: click and position events
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        curses.mouseinterval(0)
        self.stdscr.keypad(True)
        self.stdscr.timeout(50)  # non-blocking getch for refresh loop

    # ── level management ─────────────────────────────────────────────────────

    def load_level(self, idx: int) -> None:
        self.level_idx = idx % len(LEVELS)
        self.state = parse_level(LEVELS[self.level_idx])
        self.message = f"Level {self.level_idx + 1}"

    # ── main loop ────────────────────────────────────────────────────────────

    def run(self) -> None:
        while True:
            self.render()
            try:
                key = self.stdscr.getch()
            except KeyboardInterrupt:
                break

            if key == -1:
                continue
            if key == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, bstate = curses.getmouse()
                    if bstate & (curses.BUTTON1_CLICKED | curses.BUTTON1_PRESSED):
                        self._handle_mouse(my, mx)
                except curses.error:
                    pass
                continue

            if not self._handle_key(key):
                break

    # ── input handlers ───────────────────────────────────────────────────────

    def _handle_key(self, key: int) -> bool:
        """Return False to quit."""
        direction: Optional[Direction] = None

        if key in (curses.KEY_UP, ord("k"), ord("w")):
            direction = Direction.UP
        elif key in (curses.KEY_DOWN, ord("j"), ord("s")):
            direction = Direction.DOWN
        elif key in (curses.KEY_LEFT, ord("h"), ord("a")):
            direction = Direction.LEFT
        elif key in (curses.KEY_RIGHT, ord("l"), ord("d")):
            direction = Direction.RIGHT
        elif key in (ord("u"), ord("z")):
            if not self.state.undo():
                self.message = "Nothing to undo"
            else:
                self.message = ""
        elif key == ord("r"):
            self.load_level(self.level_idx)
            return True
        elif key == ord("n"):
            self.load_level(self.level_idx + 1)
            return True
        elif key == ord("p"):
            self.load_level(self.level_idx - 1)
            return True
        elif key in (ord("q"), 27):   # q or Esc
            return False

        if direction is not None:
            if not self.state.move(direction):
                self.message = "Blocked"
            else:
                self.message = ""
            if self.state.is_complete():
                self.message = "Solved!  [n] next  [r] restart"

        return True

    def _handle_mouse(self, screen_row: int, screen_col: int) -> None:
        gr = screen_row - self.ROW_OFF
        gc = (screen_col - self.COL_OFF) // CELL_W

        if gr < 0 or gr >= self.state.rows or gc < 0 or gc >= self.state.cols:
            return
        if self.state.is_wall(gr, gc):
            return

        path = self.state.find_path((gr, gc))
        if path is None:
            self.message = "No path"
            return
        for step in path:
            if not self.state.move(step):
                break
        self.message = ""
        if self.state.is_complete():
            self.message = "Solved!  [n] next  [r] restart"

    # ── rendering ────────────────────────────────────────────────────────────

    def render(self) -> None:
        self.stdscr.erase()
        h, w = self.stdscr.getmaxyx()

        self._draw_title(w)
        self._draw_grid(h, w)
        self._draw_status(h, w)

        self.stdscr.refresh()

    def _draw_title(self, w: int) -> None:
        help_text = (
            " SOKOBAN "
            " ↑↓←→/wasd/hjkl move "
            " u undo "
            " r restart "
            " n/p level "
            " click move "
            " q quit "
        )
        lvl_text = f"  Level {self.level_idx + 1}/{len(LEVELS)}  "
        line = (lvl_text + help_text).ljust(w - 1)
        self.stdscr.attron(curses.color_pair(C_TITLE) | curses.A_BOLD)
        self.stdscr.addstr(0, 0, line[:w - 1])
        self.stdscr.attroff(curses.color_pair(C_TITLE) | curses.A_BOLD)

    def _draw_grid(self, h: int, w: int) -> None:
        for r in range(self.state.rows):
            for c in range(self.state.cols):
                sr = r + self.ROW_OFF
                sc = c * CELL_W + self.COL_OFF
                if sr >= h - 1 or sc + CELL_W > w:
                    continue

                # Exterior cells are left as raw terminal background.
                if (r, c) in self.state.outside:
                    continue

                ch = self.state.display_char(r, c)
                pair, symbol, attrs = self._cell_style(ch)
                try:
                    self.stdscr.attron(curses.color_pair(pair) | attrs)
                    self.stdscr.addstr(sr, sc, symbol)
                    self.stdscr.attroff(curses.color_pair(pair) | attrs)
                except curses.error:
                    pass

    def _draw_status(self, h: int, w: int) -> None:
        won = self.state.is_complete()
        pair = C_WIN if won else C_STATUS
        moves = f" Moves: {self.state.moves}  Pushes: {self.state.pushes} "
        msg = f"  {self.message}" if self.message else ""
        line = (moves + msg).ljust(w - 1)
        self.stdscr.attron(curses.color_pair(pair) | curses.A_BOLD)
        try:
            self.stdscr.addstr(h - 1, 0, line[:w - 1])
        except curses.error:
            pass
        self.stdscr.attroff(curses.color_pair(pair) | curses.A_BOLD)

    @staticmethod
    def _cell_style(ch: str):
        """Return (colour_pair, 2-char symbol, attributes)."""
        if ch == WALL:
            return C_WALL,          _G_WALL,    curses.A_BOLD
        if ch == PLAYER:
            return C_PLAYER,        _G_PLAYER,  curses.A_BOLD
        if ch == PLAYER_ON_TARGET:
            return C_PLAYER_TARGET, _G_PLR_TGT, curses.A_BOLD
        if ch == BOX:
            return C_BOX,           _G_BOX,     curses.A_BOLD
        if ch == BOX_ON_TARGET:
            return C_BOX_TARGET,    _G_BOX_TGT, curses.A_BOLD
        if ch == TARGET:
            return C_TARGET,        _G_TARGET,  0
        # FLOOR — background colour does the work, glyph is blank
        return C_FLOOR, _G_FLOOR, 0


# ── entry point ──────────────────────────────────────────────────────────────


def _main(stdscr: curses.window) -> None:
    SokobanApp(stdscr).run()


def main() -> None:
    curses.wrapper(_main)


if __name__ == "__main__":
    main()
