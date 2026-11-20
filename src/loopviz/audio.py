import sys
import threading
from collections import deque

import numpy as np
import soundcard as sc

SAMPLE_RATE = 44100


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


class Capture:
    """Records on a background thread so the render loop never falls behind the audio."""

    def __init__(self, mic, sample_rate: int, size: int, block: int = 512, backlog: int = 64):
        self._mic = mic
        self._sample_rate = sample_rate
        self._size = size
        self._block = block
        self._running = False
        self.latest = np.zeros(size, dtype=np.float32)
        # Every window in order, one per block, for consumers that can't skip hops.
        # Bounded so a stalled consumer loses the oldest instead of growing forever
        self._windows: deque[np.ndarray] = deque(maxlen=backlog)

    def __enter__(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._running = False
        self._thread.join()

    def drain(self) -> list[np.ndarray]:
        """Windows completed since the last call, oldest first."""
        # popleft is atomic and only this side removes, so no lock is needed
        windows = []
        while self._windows:
            windows.append(self._windows.popleft())
        return windows

    def _run(self) -> None:
        with self._mic.recorder(
            samplerate=self._sample_rate, channels=2, blocksize=self._block
        ) as rec:
            while self._running:
                chunk = rec.record(numframes=self._block).mean(axis=1)
                # Swapping in a new array keeps reads lock-free
                window = np.concatenate((self.latest, chunk))[-self._size:]
                self.latest = window
                self._windows.append(window)


def list_inputs() -> list[str]:
    return [mic.name for mic in sc.all_microphones(include_loopback=True)]
