"""Small shaded sprites suitable for a seven-row contribution graph."""

STARTER_SHAPES = ("cube", "diamond", "pyramid", "staircase", "wedge")

_SPRITES = {
    "cube": (
        (0, 1, 1, 0),
        (1, 2, 3, 1),
        (1, 3, 4, 2),
        (0, 1, 2, 0),
    ),
    "diamond": (
        (0, 0, 2, 0, 0),
        (0, 2, 3, 2, 0),
        (1, 3, 4, 3, 1),
        (0, 2, 3, 2, 0),
        (0, 0, 2, 0, 0),
    ),
    "pyramid": (
        (0, 0, 2, 0, 0),
        (0, 1, 3, 1, 0),
        (1, 2, 4, 2, 1),
        (1, 2, 3, 2, 1),
    ),
    "staircase": (
        (1, 0, 0, 0, 0),
        (2, 1, 0, 0, 0),
        (3, 2, 1, 0, 0),
        (4, 3, 2, 1, 0),
    ),
    "wedge": (
        (1, 0, 0, 0),
        (2, 1, 0, 0),
        (3, 2, 1, 0),
        (4, 3, 2, 1),
    ),
}


def rasterize_shape(name: str) -> tuple[tuple[int, ...], ...]:
    try:
        return _SPRITES[name]
    except KeyError:
        raise ValueError(f"unknown shape: {name}") from None
