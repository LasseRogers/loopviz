import os

# Must be set before pygame is first imported
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from loopviz.analysis import Smoother, Spectrum
from loopviz.audio import Capture, find_input, list_inputs
from loopviz.cli import parse_args
from loopviz.display import open_display
from loopviz.renderers import RENDERERS

SAMPLE_RATE = 44100
WINDOW_SIZE = (960, 480)


def main() -> None:
    args = parse_args()

    if args.list_devices:
        print("\n".join(list_inputs()))
        return

    mic = find_input(args.device)
    print(f"Capturing from: {mic.name}")

    pygame.init()
    display = open_display(args.backend, WINDOW_SIZE)
    window = pygame.Window.from_display_module()
    fullscreen = False
    print(f"Backend: {display.name}")
    print("Tab: next mode, C: palette, P: preset, F: fullscreen, Esc: quit")

    spectrum = Spectrum(SAMPLE_RATE, args.block_size, args.bands)
    smoother = Smoother(args.bands)
    gpu = display.name == "gpu"
    renderers = {name: make(args, gpu) for name, make in RENDERERS.items()}
    modes = list(renderers)
    mode = modes.index(args.mode)
    pygame.display.set_caption(f"loopviz - {modes[mode]}")
    clock = pygame.time.Clock()

    try:
        with Capture(mic, SAMPLE_RATE, args.block_size) as capture:
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
                        # Desktop fullscreen keeps native resolution, toggle_fullscreen()
                        # switches the monitor to the window size
                        fullscreen = not fullscreen
                        if fullscreen:
                            window.set_fullscreen(desktop=True)
                        else:
                            window.set_windowed()
                    elif on_key := getattr(renderers[modes[mode]], "on_key", None):
                        on_key(event.key)

                samples = capture.latest
                display.present(renderers[modes[mode]], samples, smoother(spectrum(samples)))
                clock.tick(args.fps)
    finally:
        pygame.quit()
