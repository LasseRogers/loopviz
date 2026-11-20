import numpy as np

DB_FLOOR = -70.0
DB_CEIL = -10.0


class Spectrum:
    """Turns a block of samples into log-spaced band levels in 0..1."""

    def __init__(self, sample_rate: int, block_size: int, bands: int,
                 fmin: float = 30.0, fmax: float = 16000.0):
        self.window = np.hanning(block_size)
        # Scale so a full-scale sine reads 0 dB
        self.norm = block_size / 4
        freqs = np.fft.rfftfreq(block_size, 1 / sample_rate)
        edges = np.searchsorted(freqs, np.geomspace(fmin, fmax, bands + 1))
        # Low bands are narrower than one FFT bin, so give each at least one
        self.slices = [slice(lo, max(hi, lo + 1)) for lo, hi in zip(edges[:-1], edges[1:])]

    def __call__(self, samples: np.ndarray) -> np.ndarray:
        mag = np.abs(np.fft.rfft(samples * self.window)) / self.norm
        levels = np.array([mag[s].mean() for s in self.slices])
        db = 20 * np.log10(levels + 1e-9)
        return np.clip((db - DB_FLOOR) / (DB_CEIL - DB_FLOOR), 0, 1)


class Smoother:
    """Rises fast and falls slowly so bars follow hits without flickering."""

    def __init__(self, size: int, attack: float = 0.6, release: float = 0.08):
        self.attack = attack
        self.release = release
        self.state = np.zeros(size)

    def __call__(self, target: np.ndarray) -> np.ndarray:
        rate = np.where(target > self.state, self.attack, self.release)
        self.state += (target - self.state) * rate
        return self.state


class BeatDetector:
    """Flags onsets where energy jumps above its recent average."""

    def __init__(self, history: int = 43, jump: float = 0.08,
                 floor: float = 0.2, cooldown: int = 10):
        self.history = np.zeros(history)
        self.jump = jump
        self.floor = floor
        self.cooldown = cooldown
        self.wait = 0

    def __call__(self, energy: float) -> bool:
        average = self.history.mean()
        self.history = np.roll(self.history, 1)
        self.history[0] = energy
        self.wait = max(0, self.wait - 1)

        # Levels are in dB, so a fixed difference is a fixed loudness jump
        # Floor ignores noise when the music is quiet or paused
        if self.wait or energy < self.floor or energy - average < self.jump:
            return False
        self.wait = self.cooldown
        return True
