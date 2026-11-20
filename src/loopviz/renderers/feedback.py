import numpy as np
import pygame

FADE = 0.94
RING_HALF = 256


class FeedbackRenderer:
    """Each frame zooms, rotates and fades the previous one, then draws a new ring on top."""

    def __init__(self):
        self.canvas: pygame.Surface | None = None
        self.hue = 0.0

    def draw(self, screen: pygame.Surface, samples: np.ndarray, levels: np.ndarray) -> None:
        size = screen.get_size()
        if self.canvas is None or self.canvas.get_size() != size:
            self.canvas = pygame.Surface(size)

        n = len(levels)
        bass = levels[: n // 6].mean()
        treble = levels[-n // 3 :].mean()

        warped = pygame.transform.rotozoom(self.canvas, 0.5 + treble * 3, 1.02 + bass * 0.06)
        self.canvas.fill((0, 0, 0))
        self.canvas.blit(warped, warped.get_rect(center=self.canvas.get_rect().center))
        self.canvas.fill((round(FADE * 255),) * 3, special_flags=pygame.BLEND_MULT)

        self.hue = (self.hue + 0.5 + bass * 4) % 360
        color = pygame.Color(0)
        color.hsva = (self.hue, 80, 100, 100)

        # Mirrored so the ring closes without a seam
        half = samples[-RING_HALF:]
        ring = np.concatenate((half, half[::-1]))
        angles = np.linspace(0, 2 * np.pi, len(ring), endpoint=False)
        w, h = size
        radius = min(w, h) * (0.15 + 0.1 * bass) * (1 + np.clip(ring * 2, -0.5, 0.5))
        points = np.column_stack((w / 2 + radius * np.cos(angles), h / 2 + radius * np.sin(angles)))
        pygame.draw.lines(self.canvas, color, True, points.tolist(), 2)

        screen.blit(self.canvas, (0, 0))
