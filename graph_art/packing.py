"""Deterministic placement of shaded sprites on a contribution grid."""

from __future__ import annotations

import random
from typing import Iterable

from .core import ContributionGrid, GRID_HEIGHT, GRID_WIDTH
from .shapes import rasterize_shape


def pack_shapes(
    grid: ContributionGrid, shape_names: Iterable[str], seed: int = 0
) -> list[dict[str, object]]:
    """Place each requested sprite once where it fits in currently blank cells."""
    rng = random.Random(seed)
    placements: list[dict[str, object]] = []
    occupied = set((x, y) for x, y in grid.available_cells() if grid.get((x, y)) != 0)
    # Include existing non-zero cells without requiring access to grid internals.
    occupied = {(x, y) for y in range(GRID_HEIGHT) for x in range(GRID_WIDTH) if grid.get((x, y))}

    for name in shape_names:
        sprite = rasterize_shape(name)
        height, width = len(sprite), len(sprite[0])
        candidates = [(x, y) for y in range(GRID_HEIGHT - height + 1) for x in range(GRID_WIDTH - width + 1)]
        rng.shuffle(candidates)
        for origin_x, origin_y in candidates:
            cells = tuple(
                (origin_x + dx, origin_y + dy, value)
                for dy, row in enumerate(sprite)
                for dx, value in enumerate(row)
                if value
            )
            if all((x, y) not in occupied for x, y, _ in cells):
                placements.append({"shape": name, "cells": cells})
                occupied.update((x, y) for x, y, _ in cells)
                break
    return placements
