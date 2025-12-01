import bpy
from typing import Literal

BLENDER_VERSION = bpy.app.version


def get_math_node_type() -> str:
    """Get correct compositing Math node type to use when adding nodes to node tree using Blender API."""
    if BLENDER_VERSION >= (4, 5, 0):
        return "ShaderNodeMath"
    return "CompositorNodeMath"


def get_mixrgb_node() -> str:
    """Get correct compositing Mix RGB (Color) node type to use when adding nodes to node tree using Blender API."""
    if BLENDER_VERSION >= (5, 0, 0):
        return "ShaderNodeMix"
    return "CompositorNodeMixRGB"


def mixrgb_input_color(idx: Literal[1, 2]) -> int:
    """Get correct index of Mix RGB (Color) node Color sockets."""
    if BLENDER_VERSION >= (5, 0, 0):
        return idx + 5
    return idx


def mixrgb_output() -> str:
    """Get correct name of Mix RGB (Color) node output socket."""
    if BLENDER_VERSION >= (5, 0, 0):
        return "Result"
    return "Image"
