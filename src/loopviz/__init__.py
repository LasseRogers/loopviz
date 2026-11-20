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
    print("Tab: next mode, F: fullscreen, Esc: quit")

    spectrum = Spectrum(SAMPLE_RATE, BLOCK_SIZE, args.bands)
    smoother = Smoother(args.bands)
    renderers = {name: make(args) for name, make in RENDERERS.items()}
    modes = list(renderers)
    mode = modes.index(args.mode)

    pygame.init()
    screen = pygame.display.set_mode((960, 480), pygame.RESIZABLE)
    pygame.display.set_caption(f"loopviz - {modes[mode]}")
    clock = pygame.time.Clock()

    try:
        with Capture(mic, SAMPLE_RATE, BLOCK_SIZE) as capture:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    if event.type != pygame.KEYDOWN:
                        continue
                    if event.key == pygame.K_ESCAPE:
                        return
                    if event.key == pygame.K_TAB:
                        mode = (mode + 1) % len(modes)
                        pygame.display.set_caption(f"loopviz - {modes[mode]}")
                    elif event.key == pygame.K_f:
                        pygame.display.toggle_fullscreen()

                samples = capture.latest
                renderers[modes[mode]].draw(screen, samples, smoother(spectrum(samples)))
                pygame.display.flip()
                clock.tick(args.fps)
    finally:
        pygame.quit()
