import pygame

from loopviz.analysis import Spectrum
from loopviz.audio import Capture, find_input

SAMPLE_RATE = 44100
BLOCK_SIZE = 2048
FPS = 60
BANDS = 32
BAR_COLOR = (90, 200, 160)


def main() -> None:
    mic = find_input()
    print(f"Capturing from: {mic.name}")

    spectrum = Spectrum(SAMPLE_RATE, BLOCK_SIZE, BANDS)

    pygame.init()
    screen = pygame.display.set_mode((960, 480), pygame.RESIZABLE)
    pygame.display.set_caption("loopviz")
    clock = pygame.time.Clock()

    try:
        with Capture(mic, SAMPLE_RATE, BLOCK_SIZE) as capture:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (
                        event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                    ):
                        return

                levels = spectrum(capture.latest)

                width, height = screen.get_size()
                bar_width = width / BANDS
                screen.fill((0, 0, 0))
                for i, level in enumerate(levels):
                    bar_height = level * height
                    pygame.draw.rect(
                        screen, BAR_COLOR,
                        (i * bar_width + 1, height - bar_height, bar_width - 2, bar_height),
                    )
                pygame.display.flip()
                clock.tick(FPS)
    finally:
        pygame.quit()
