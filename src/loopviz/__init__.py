import pygame

from loopviz.analysis import Smoother, Spectrum
from loopviz.audio import Capture, find_input, list_inputs
from loopviz.cli import parse_args
from loopviz.renderers import RENDERERS

SAMPLE_RATE = 44100
BLOCK_SIZE = 2048


def main() -> None:
    args = parse_args()

    if args.list_devices:
        print("\n".join(list_inputs()))
        return

    mic = find_input(args.device)
    print(f"Capturing from: {mic.name}")

    spectrum = Spectrum(SAMPLE_RATE, BLOCK_SIZE, args.bands)
    smoother = Smoother(args.bands)
    renderer = RENDERERS[args.mode](args)

    pygame.init()
    screen = pygame.display.set_mode((960, 480), pygame.RESIZABLE)
    pygame.display.set_caption(f"loopviz - {args.mode}")
    clock = pygame.time.Clock()

    try:
        with Capture(mic, SAMPLE_RATE, BLOCK_SIZE) as capture:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (
                        event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                    ):
                        return

                samples = capture.latest
                renderer.draw(screen, samples, smoother(spectrum(samples)))
                pygame.display.flip()
                clock.tick(args.fps)
    finally:
        pygame.quit()
