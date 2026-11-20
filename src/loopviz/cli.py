import argparse

from loopviz.renderers import RENDERERS


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="loopviz", description="Visualize system audio.")
    parser.add_argument("--mode", choices=RENDERERS, default="spectrum")
    parser.add_argument("--bands", type=int, default=32, help="number of frequency bands")
    parser.add_argument("--fps", type=int, default=60)
    parser.add_argument("--device", help="input device name, overrides auto-detection")
    parser.add_argument("--list-devices", action="store_true", help="list input devices and exit")
    return parser.parse_args(argv)
