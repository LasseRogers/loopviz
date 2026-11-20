from dataclasses import dataclass

Color = tuple[int, int, int]


@dataclass(frozen=True)
class Palette:
    name: str
    low: Color
    high: Color | None = None
    # Gradient runs up each bar instead of across bands
    by_height: bool = False


PALETTES = [
    Palette("green", (34, 107, 22)),
    Palette("green-deep", (24, 75, 15)),
    Palette("moss", (52, 92, 48)),
    Palette("phosphor", (40, 140, 70)),
    Palette("teal", (30, 105, 95)),
    Palette("amber", (170, 105, 20)),
    Palette("slate", (70, 88, 135)),
    Palette("graphite", (105, 105, 105)),
    Palette("green-glow", (24, 75, 15), (68, 214, 44), by_height=True),
    Palette("forest-teal", (30, 80, 35), (30, 105, 95)),
]


def mix(a: Color, b: Color, t: float) -> Color:
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))
