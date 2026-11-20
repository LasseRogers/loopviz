from loopviz.renderers.feedback import FeedbackRenderer
from loopviz.renderers.feedback_gl import FeedbackGLRenderer
from loopviz.renderers.spectrum import SpectrumRenderer
from loopviz.renderers.waveform import WaveformRenderer

# Each entry builds its renderer from CLI args and the active backend,
# keeping renderers free of argparse
RENDERERS = {
    "spectrum": lambda args, gpu: SpectrumRenderer(palette=args.palette),
    "waveform": lambda args, gpu: WaveformRenderer(persistence=args.persistence),
    "feedback": lambda args, gpu: FeedbackGLRenderer() if gpu else FeedbackRenderer(),
}
