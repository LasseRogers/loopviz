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
