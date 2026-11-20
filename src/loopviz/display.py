import moderngl
import numpy as np
import pygame

VERTEX_SHADER = """
#version 330 core
in vec2 pos;
out vec2 uv;
void main() {
    // Flip y: pygame rows start at the top, GL textures at the bottom
    uv = vec2(pos.x, -pos.y) * 0.5 + 0.5;
    gl_Position = vec4(pos, 0.0, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 330 core
uniform sampler2D tex;
in vec2 uv;
out vec4 color;
void main() {
    color = texture(tex, uv);
}
"""


class CpuDisplay:
    name = "cpu"

    def __init__(self, size: tuple[int, int]):
        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)

    def present(self, renderer, samples: np.ndarray, levels: np.ndarray) -> None:
        renderer.draw(self.screen, samples, levels)
        pygame.display.flip()


class GpuDisplay:
    name = "gpu"

    def __init__(self, size: tuple[int, int]):
        # 3.3 core forward-compatible is the most macOS offers, and fine on Linux
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE
        )
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)
        pygame.display.set_mode(size, pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)

        self.ctx = moderngl.create_context(require=330)
        program = self.ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=FRAGMENT_SHADER)
        corners = np.array([-1, -1, 1, -1, -1, 1, 1, 1], dtype="f4")
        self.quad = self.ctx.vertex_array(program, [(self.ctx.buffer(corners), "2f", "pos")])
        self.surface: pygame.Surface | None = None
        self.texture: moderngl.Texture | None = None

    def present(self, renderer, samples: np.ndarray, levels: np.ndarray) -> None:
        size = pygame.display.get_window_size()
        if self.surface is None or self.surface.get_size() != size:
            self.surface = pygame.Surface(size)
            if self.texture:
                self.texture.release()
            self.texture = self.ctx.texture(size, 3)

        renderer.draw(self.surface, samples, levels)
        self.texture.write(pygame.image.tobytes(self.surface, "RGB"))
        self.ctx.viewport = (0, 0, *size)
        self.texture.use()
        self.quad.render(moderngl.TRIANGLE_STRIP)
        pygame.display.flip()


def open_display(backend: str, size: tuple[int, int]):
    if backend != "cpu":
        try:
            return GpuDisplay(size)
        except (pygame.error, moderngl.Error) as exc:
            if backend == "gpu":
                raise SystemExit(f"GPU backend unavailable: {exc}")
            print(f"GPU unavailable ({exc}), using CPU")
    return CpuDisplay(size)
