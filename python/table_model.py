"""
A simple table view model for general scripting
Usable for both CLI, TUI, WEB, GUI
ViewModel seperate from rendering
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Iterable


class ColAlign(StrEnum):
    LEFT = "LEFT"
    MIDDLE = "MIDDLE"
    RIGHT = "RIGHT"

@dataclass
class TableCol:
    name: str
    align: ColAlign  = ColAlign.LEFT

@dataclass
class TableRow:
    cells: list[object] = field(default_factory=list)

class TableModel:
    cols: list[TableCol]
    rows: list[TableRow]

    def __init__(self):
        self.cols = []
        self.rows = []

    def add_col(self, col: TableCol | str) -> 'TableModel':
        if isinstance(col, str):
            self.cols.append(TableCol(col))
        else:
            self.cols.append(col)
        return self

    def add_cols(self, strs:Iterable[str]) -> 'TableModel':
        for s in strs:
            self.add_col(s)
        return self

    def add_row(self, row: TableRow | Iterable[obj]) -> 'TableModel':
        self.rows.append(row)
        return self

def render_table(model: TableModel) -> str:
    headers = [c.name for c in model.cols]
    rows = [
        [str(r.cells[i]) if i < len(r.cells) else "" for i in range(len(model.cols))]
        for r in model.rows
    ]
    widths = [max(len(s) for s in col) for col in zip(headers, *rows)]

    def fmt(cells: list[str], aligns: list[ColAlign]) -> str:
        parts = []
        for text, width, align in zip(cells, widths, aligns):
            match align:
                case ColAlign.RIGHT:
                    parts.append(text.rjust(width))
                case ColAlign.MIDDLE:
                    parts.append(text.center(width))
                case _:
                    parts.append(text.ljust(width))
        return "| " + " | ".join(parts) + " |"

    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    aligns = [c.align for c in model.cols]
    lines = [sep, fmt(headers, [ColAlign.LEFT] * len(headers)), sep]
    lines += [fmt(r, aligns) for r in rows]
    lines.append(sep)
    return "\n".join(lines)

if __name__ == "__main__":
    tbl = TableModel()
    tbl.add_cols(["Id", "Name", "Age"])
    tbl.cols[2].align = ColAlign.RIGHT
    tbl.add_row(TableRow([1234, "Guy", 150.8]))
    tbl.add_row(TableRow([1235, "Bev", 50.2]))
    tbl.add_row(TableRow([1236, "Rusty", 1.1]))
    print(render_table(tbl))
