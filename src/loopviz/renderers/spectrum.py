import numpy as np
import pygame

BAR_COLOR = (90, 200, 160)


class SpectrumRenderer:
    """Log-spaced FFT bars."""

    def draw(self, screen: pygame.Surface, samples: np.ndarray, levels: np.ndarray) -> None:
        width, height = screen.get_size()
        bar_width = width / len(levels)
        screen.fill((0, 0, 0))
        for i, level in enumerate(levels):
            bar_height = level * height
            pygame.draw.rect(
                screen, BAR_COLOR,
                (i * bar_width + 1, height - bar_height, bar_width - 2, bar_height),
            )
