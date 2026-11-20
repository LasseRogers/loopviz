import argparse

from loopviz.palettes import PALETTES
from loopviz.renderers import RENDERERS
from loopviz.renderers.feedback_gl import PRESETS


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="loopviz", description="Visualize system audio.")
    parser.add_argument("--mode", choices=RENDERERS, default="spectrum")
    parser.add_argument(
        "--palette", choices=[p.name for p in PALETTES], default=PALETTES[0].name,
        help="spectrum and waveform colors, C cycles while running",
    )
    parser.add_argument(
        "--preset", choices=[p.name for p in PRESETS], default=PRESETS[0].name,
        help="feedback preset (GPU only), P cycles while running",
    )
    parser.add_argument(
        "--backend", choices=("auto", "gpu", "cpu"), default="auto",
        help="auto tries the GPU and falls back to CPU",
    )
    parser.add_argument("--bands", type=int, default=128, help="number of frequency bands")
    parser.add_argument(
        "--block-size", type=int, choices=(1024, 2048, 4096, 8192), default=2048,
        help="FFT size, larger gives finer bass but slower response",
    )
    parser.add_argument("--fps", type=int, default=60)
    parser.add_argument("--device", help="input device name, overrides auto-detection")
    parser.add_argument("--list-devices", action="store_true", help="list input devices and exit")
    parser.add_argument(
        "--persistence", type=float, default=0.0,
        help="waveform trail, fraction kept per frame (0 = off, 0.85 = typical)",
    )
    args = parser.parse_args(argv)

    if not 0 <= args.persistence < 1:
        parser.error("--persistence must be in [0, 1)")
    return args
