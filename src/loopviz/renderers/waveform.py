import numpy as np
import pygame

LINE_COLOR = (90, 200, 160)
GAIN = 2.0


class WaveformRenderer:
    """Time-domain oscilloscope trace with optional phosphor-style fade."""

    def __init__(self, span: int = 1024, persistence: float = 0.0):
        self.span = span
        self.fade = round(persistence * 255)

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
        window = samples[start : start + self.span]

        x = np.linspace(0, width - 1, len(window))
        y = height / 2 - np.clip(window * GAIN, -1, 1) * height / 2
        pygame.draw.lines(screen, LINE_COLOR, False, np.column_stack((x, y)).tolist())
