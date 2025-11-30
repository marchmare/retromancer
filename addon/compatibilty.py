import bpy

BLENDER_VERSION = bpy.app.version


def get_math_node_type() -> str:
    """Get correct compositing Math node type to use when adding nodes to node tree using Blender API."""
    if BLENDER_VERSION >= (4, 5, 0):
        return "ShaderNodeMath"
    return "CompositorNodeMath"
