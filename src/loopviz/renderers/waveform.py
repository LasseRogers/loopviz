from itertools import pairwise

import numpy as np
import pygame

from loopviz.palettes import PaletteCycle, mix

GAIN = 2.0
SEGMENTS = 64


class WaveformRenderer:
    """Time-domain oscilloscope trace with optional phosphor-style fade. C cycles the palette."""

    def __init__(self, palette: str, span: int = 1024, persistence: float = 0.0):
        self.palettes = PaletteCycle(palette)
        self.span = span
        self.fade = round(persistence * 255)

    def on_key(self, key: int) -> None:
        if key == pygame.K_c:
            print(f"Palette: {self.palettes.next().name}")

    def draw(self, screen: pygame.Surface, samples: np.ndarray, levels: np.ndarray) -> None:
        width, height = screen.get_size()
        if self.fade:
            # Multiply rounds down to true black, an alpha overlay leaves gray residue
            screen.fill((self.fade,) * 3, special_flags=pygame.BLEND_MULT)
        else:
            screen.fill((0, 0, 0))

        # Start at the latest rising zero crossing so the trace holds still
        head = samples[: len(samples) - self.span]
        crossings = np.flatnonzero((head[:-1] < 0) & (head[1:] >= 0))
        start = crossings[-1] if crossings.size else 0
        window = np.clip(samples[start : start + self.span] * GAIN, -1, 1)

        x = np.linspace(0, width - 1, len(window))
        y = height / 2 - window * height / 2
        points = np.column_stack((x, y))

        p = self.palettes.current
        if p.high is None:
            pygame.draw.lines(screen, p.low, False, points.tolist())
            return

        # draw.lines takes one color, so split the trace to vary it along the line
        amplitude = np.abs(window)
        bounds = np.linspace(0, len(points) - 1, SEGMENTS + 1).astype(int)
        for i, (a, b) in enumerate(pairwise(bounds)):
            t = amplitude[a : b + 1].max() if p.by_height else i / (SEGMENTS - 1)
            pygame.draw.lines(screen, mix(p.low, p.high, t), False, points[a : b + 1].tolist())
