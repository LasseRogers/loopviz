import numpy as np

from loopviz.audio import find_input

SAMPLE_RATE = 44100
BLOCK_SIZE = 2048


def main() -> None:
    mic = find_input()
    print(f"Capturing from: {mic.name}")

    # Temporary level check until the renderer is in place
    with mic.recorder(samplerate=SAMPLE_RATE, channels=2) as rec:
        for _ in range(100):
            rms = np.sqrt(np.mean(rec.record(numframes=BLOCK_SIZE) ** 2))
            print(f"{rms:.4f} {'#' * int(rms * 200)}", flush=True)
