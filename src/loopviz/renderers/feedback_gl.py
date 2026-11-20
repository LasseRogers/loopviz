import time

import moderngl
import numpy as np

VERTEX_SHADER = """
#version 330 core
in vec2 pos;
out vec2 uv;
void main() {
    uv = pos * 0.5 + 0.5;
    gl_Position = vec4(pos, 0.0, 1.0);
}
"""

WARP_SHADER = """
#version 330 core
uniform sampler2D prev;
uniform sampler2D wave;
uniform float time;
uniform float bass;
uniform float treble;
uniform float hue;
uniform float aspect;
in vec2 uv;
out vec4 color;

vec3 hsv2rgb(float h, float s, float v) {
    vec3 k = clamp(abs(fract(h + vec3(0.0, 2.0, 1.0) / 3.0) * 6.0 - 3.0) - 1.0, 0.0, 1.0);
    return v * mix(vec3(1.0), k, s);
}

void main() {
    vec2 p = (uv - 0.5) * vec2(aspect, 1.0);
    float r = length(p);
    float a = atan(p.y, p.x);

    // Read the previous frame closer to the center so it zooms outward,
    // rotated, with more swirl near the middle and a travelling ripple
    float zoom = 0.97 - bass * 0.04;
    float spin = 0.01 + treble * 0.05 + 0.015 / (r + 0.2);
    float ripple = 0.004 * sin(r * 30.0 - time * 4.0);
    vec2 q = vec2(cos(a - spin), sin(a - spin)) * (r * zoom + ripple);
    vec3 trail = texture(prev, q / vec2(aspect, 1.0) + 0.5).rgb * 0.95;

    float s = texture(wave, vec2(a / 6.2831853 + 0.5, 0.5)).r;
    float radius = 0.22 + bass * 0.1 + s * 0.15;
    float glow = exp(-abs(r - radius) * 150.0) * 0.6;

    color = vec4(trail + hsv2rgb(hue, 0.8, 1.0) * glow, 1.0);
}
"""

COPY_SHADER = """
#version 330 core
uniform sampler2D tex;
in vec2 uv;
out vec4 color;
void main() {
    color = vec4(texture(tex, uv).rgb, 1.0);
}
"""

WAVE_HALF = 256


class FeedbackGLRenderer:
    """GPU frame feedback, ping-ponging between two float framebuffers."""

    gl = True

    def __init__(self):
        self.ctx: moderngl.Context | None = None
        self.size: tuple[int, int] | None = None
        self.targets: list[tuple[moderngl.Texture, moderngl.Framebuffer]] = []
        self.hue = 0.0
        self.start = time.perf_counter()

    def _setup(self, ctx: moderngl.Context) -> None:
        self.ctx = ctx
        corners = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], dtype="f4"))
        self.warp = ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=WARP_SHADER)
        copy = ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=COPY_SHADER)
        self.warp_quad = ctx.vertex_array(self.warp, [(corners, "2f", "pos")])
        self.copy_quad = ctx.vertex_array(copy, [(corners, "2f", "pos")])
        self.wave = ctx.texture((WAVE_HALF * 2, 1), 1, dtype="f4")
        self.warp["prev"].value = 0
        self.warp["wave"].value = 1

    def _resize(self, size: tuple[int, int]) -> None:
        for tex, fbo in self.targets:
            fbo.release()
            tex.release()
        self.targets = []
        for _ in range(2):
            # Float so the fade decays to black instead of sticking at low 8-bit values
            tex = self.ctx.texture(size, 4, dtype="f2")
            tex.repeat_x = tex.repeat_y = False
            fbo = self.ctx.framebuffer(color_attachments=[tex])
            fbo.clear()
            self.targets.append((tex, fbo))
        self.size = size

    def render(self, ctx: moderngl.Context, size: tuple[int, int],
               samples: np.ndarray, levels: np.ndarray) -> None:
        if self.ctx is None:
            self._setup(ctx)
        if size != self.size:
            self._resize(size)

        n = len(levels)
        bass = float(levels[: n // 6].mean())
        treble = float(levels[-n // 3 :].mean())
        self.hue = (self.hue + 0.002 + bass * 0.01) % 1.0

        # Mirrored so the ring closes without a seam
        half = samples[-WAVE_HALF:]
        self.wave.write(np.concatenate((half, half[::-1])).astype("f4"))

        (src, _), (dst, fbo) = self.targets
        fbo.use()
        src.use(location=0)
        self.wave.use(location=1)
        self.warp["time"].value = time.perf_counter() - self.start
        self.warp["bass"].value = bass
        self.warp["treble"].value = treble
        self.warp["hue"].value = self.hue
        self.warp["aspect"].value = size[0] / size[1]
        self.warp_quad.render(moderngl.TRIANGLE_STRIP)

        ctx.screen.use()
        ctx.viewport = (0, 0, *size)
        dst.use(location=0)
        self.copy_quad.render(moderngl.TRIANGLE_STRIP)
        self.targets.reverse()
