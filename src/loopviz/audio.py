import sys

import soundcard as sc


def find_input(name: str | None = None):
    """Return the input device that carries system audio."""
    try:
        if name:
            return sc.get_microphone(name, include_loopback=True)
        if sys.platform == "darwin":
            # macOS has no native loopback, BlackHole provides one
            return sc.get_microphone("BlackHole")
        return sc.get_microphone(sc.default_speaker().name, include_loopback=True)
    except IndexError:
        raise SystemExit(f"No audio input found matching {name or 'system output'!r}")
