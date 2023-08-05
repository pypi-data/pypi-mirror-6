from contextlib import contextmanager
from pngrenderer.core import PNGRenderer


@contextmanager
def png_render(stub):
    renderer = PNGRenderer(stub)
    yield renderer
    renderer.render()
