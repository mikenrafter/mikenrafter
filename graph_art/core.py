"""The seven-row, Sunday-first GitHub contribution grid."""

from __future__ import annotations

import datetime as _datetime
from typing import Iterable

GRID_WIDTH = 53
GRID_HEIGHT = 7
INTENSITY_COMMIT_COUNTS = (0, 1, 2, 3, 4)


def _validate_cell(cell: tuple[int, int]) -> tuple[int, int]:
    try:
        x, y = cell
    except (TypeError, ValueError):
        raise ValueError(f"invalid grid cell: {cell!r}") from None
    if not isinstance(x, int) or not isinstance(y, int):
        raise ValueError(f"invalid grid cell: {cell!r}")
    if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
        raise ValueError(f"cell outside {GRID_WIDTH}x{GRID_HEIGHT} grid: {cell!r}")
    return x, y


def date_to_cell(date: _datetime.date, first_sunday: _datetime.date) -> tuple[int, int]:
    """Return ``(week_column, weekday)`` relative to the first Sunday."""
    if not isinstance(date, _datetime.date) or not isinstance(first_sunday, _datetime.date):
        raise TypeError("date and first_sunday must be datetime.date values")
    offset = (date - first_sunday).days
    if not 0 <= offset < GRID_WIDTH * GRID_HEIGHT:
        raise ValueError("date is outside the contribution grid")
    return offset // GRID_HEIGHT, offset % GRID_HEIGHT


def cell_to_date(cell: tuple[int, int], first_sunday: _datetime.date) -> _datetime.date:
    """Return the date represented by a grid cell."""
    x, y = _validate_cell(cell)
    if not isinstance(first_sunday, _datetime.date):
        raise TypeError("first_sunday must be a datetime.date value")
    return first_sunday + _datetime.timedelta(days=x * GRID_HEIGHT + y)


def intensity_to_commit_count(intensity: int) -> int:
    """Convert one of the five display levels to a positive commit count."""
    if not isinstance(intensity, int) or not 0 <= intensity < len(INTENSITY_COMMIT_COUNTS):
        raise ValueError("intensity must be an integer from 0 through 4")
    return INTENSITY_COMMIT_COUNTS[intensity]


class ContributionGrid:
    """Mutable intensity values for a fixed-size contribution calendar."""

    def __init__(self, values: Iterable[Iterable[int]] | None = None):
        rows = [list(row) for row in values] if values is not None else []
        if rows and (len(rows) != GRID_HEIGHT or any(len(row) != GRID_WIDTH for row in rows)):
            raise ValueError("grid must be 53 columns by 7 rows")
        self._values = rows or [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        for row in self._values:
            for value in row:
                if not isinstance(value, int) or not 0 <= value <= 4:
                    raise ValueError("grid intensities must be integers from 0 through 4")

    @classmethod
    def empty(cls) -> "ContributionGrid":
        return cls()

    def get(self, cell: tuple[int, int]) -> int:
        x, y = _validate_cell(cell)
        return self._values[y][x]

    def set(self, cell: tuple[int, int], intensity: int) -> None:
        x, y = _validate_cell(cell)
        if not isinstance(intensity, int) or not 0 <= intensity <= 4:
            raise ValueError("intensity must be an integer from 0 through 4")
        self._values[y][x] = intensity

    def available_cells(self) -> tuple[tuple[int, int], ...]:
        return tuple(
            (x, y)
            for y in range(GRID_HEIGHT)
            for x in range(GRID_WIDTH)
            if self._values[y][x] == 0
        )
