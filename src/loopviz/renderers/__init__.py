from loopviz.renderers.feedback import FeedbackRenderer
from loopviz.renderers.feedback_gl import FeedbackGLRenderer
from loopviz.renderers.spectrogram import SpectrogramRenderer
from loopviz.renderers.spectrum import SpectrumRenderer
from loopviz.renderers.waveform import WaveformRenderer

# Each entry builds its renderer from CLI args and the active backend,
# keeping renderers free of argparse
RENDERERS = {
    "spectrum": lambda args, gpu: SpectrumRenderer(palette=args.palette),
    "spectrogram": lambda args, gpu: SpectrogramRenderer(block_size=args.block_size, bands=args.bands),
    "waveform": lambda args, gpu: WaveformRenderer(palette=args.palette, persistence=args.persistence),
    "feedback": lambda args, gpu: FeedbackGLRenderer(preset=args.preset) if gpu else FeedbackRenderer(),
}
