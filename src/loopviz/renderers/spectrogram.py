import numpy as np
import pygame

from loopviz.analysis import Spectrum
from loopviz.audio import SAMPLE_RATE

# Approximation of matplotlib's magma: perceptually uniform and readable from
# black, so quiet passages stay dark and loud partials stand out
MAGMA = [
    (0, 0, 4), (28, 16, 68), (79, 18, 123), (129, 37, 129), (181, 54, 122),
    (229, 80, 100), (251, 135, 97), (254, 194, 135), (252, 253, 191),
]


def colormap(stops: list[tuple[int, int, int]], size: int = 256) -> np.ndarray:
    """Interpolate color stops into a (size, 3) lookup table."""
    stops_array = np.asarray(stops, dtype=float)
    x = np.linspace(0, 1, len(stops_array))
    t = np.linspace(0, 1, size)
    table = [np.interp(t, x, stops_array[:, channel]) for channel in range(3)]
    return np.stack(table, axis=1).round().astype(np.uint8)


class SpectrogramRenderer:
    """Scrolling time-frequency image, one column per captured window."""

    def __init__(self, block_size: int, bands: int):
        self.spectrum = Spectrum(SAMPLE_RATE, block_size, bands)
        self.bands = bands
        self.lut = colormap(MAGMA)
        self.pending: list[np.ndarray] = []
        self.canvas: pygame.Surface | None = None

    def feed(self, windows: list[np.ndarray]) -> None:
        # Own analysis rather than the shared levels, whose slow release would
        # smear every hit along the time axis
        self.pending.extend(self.spectrum(window) for window in windows)

    def _resize(self, size: tuple[int, int]) -> None:
        # Stretch the existing history so resizing doesn't wipe it
        self.canvas = (
            pygame.transform.scale(self.canvas, size) if self.canvas else pygame.Surface(size)
        )
        # Band for each pixel row, lowest at the bottom
        self.rows = np.arange(size[1])[::-1] * self.bands // size[1]

    def _scroll_in(self, columns: list[np.ndarray]) -> None:
        assert self.canvas is not None
        width = self.canvas.get_width()
        # A long stall can deliver more columns than fit, only the newest are visible
        levels = np.array(columns[-width:])
        indices = (levels * (len(self.lut) - 1)).round().astype(np.intp)
        # surfarray is indexed (x, y), so columns come first
        pixels = self.lut[indices[:, self.rows]]
        self.canvas.scroll(-len(levels), 0)
        self.canvas.blit(pygame.surfarray.make_surface(pixels), (width - len(levels), 0))

    def draw(self, screen: pygame.Surface, samples: np.ndarray, levels: np.ndarray) -> None:
        if self.canvas is None or self.canvas.get_size() != screen.get_size():
            self._resize(screen.get_size())
        if self.pending:
            self._scroll_in(self.pending)
            self.pending.clear()
        screen.blit(self.canvas, (0, 0))
