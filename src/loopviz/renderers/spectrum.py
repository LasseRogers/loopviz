import numpy as np
import pygame

from loopviz.palettes import PALETTES, Palette, mix


class SpectrumRenderer:
    """Log-spaced FFT bars. C cycles the palette."""

    def __init__(self, palette: str):
        self.index = next(i for i, p in enumerate(PALETTES) if p.name == palette)
        self._prepared_for = None

    @property
    def palette(self) -> Palette:
        return PALETTES[self.index]

    def on_key(self, key: int) -> None:
        if key == pygame.K_c:
            self.index = (self.index + 1) % len(PALETTES)
            print(f"Palette: {self.palette.name}")

    def _prepare(self, bands: int, bar_width: float, height: int) -> None:
        p = self.palette
        if p.by_height:
            # Draw the gradient once, then each bar shows the bottom slice of it
            column = pygame.Surface((1, height))
            for y in range(height):
                column.set_at((0, y), mix(p.low, p.high, 1 - y / height))
            self.gradient = pygame.transform.scale(column, (max(1, int(bar_width) - 2), height))
            self.colors = None
        else:
            high = p.high or p.low
            self.colors = [mix(p.low, high, t) for t in np.linspace(0, 1, bands)]

    def draw(self, screen: pygame.Surface, samples: np.ndarray, levels: np.ndarray) -> None:
        width, height = screen.get_size()
        bar_width = width / len(levels)
        state = (self.index, len(levels), int(bar_width), height)
        if state != self._prepared_for:
            self._prepare(len(levels), bar_width, height)
            self._prepared_for = state

        screen.fill((0, 0, 0))
        for i, level in enumerate(levels):
            x = i * bar_width + 1
            top = height - int(level * height)
            if self.colors is None:
                screen.blit(self.gradient, (x, top), area=(0, top, self.gradient.get_width(), height - top))
            else:
                pygame.draw.rect(screen, self.colors[i], (x, top, bar_width - 2, height - top))
