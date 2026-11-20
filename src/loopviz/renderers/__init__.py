from loopviz.renderers.spectrum import SpectrumRenderer
from loopviz.renderers.waveform import WaveformRenderer

# Each entry builds its renderer from CLI args, keeping renderers free of argparse
RENDERERS = {
    "spectrum": lambda args: SpectrumRenderer(),
    "waveform": lambda args: WaveformRenderer(persistence=args.persistence),
}
