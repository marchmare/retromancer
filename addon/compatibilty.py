import bpy
from typing import Literal, Dict

BLENDER_VERSION = bpy.app.version


VERSIONED_NODES = {
    "CompositorNodeMath": {
        (4, 5, 0): {"alias": "ShaderNodeMath"},
    },
    "CompositorNodeValToRGB": {
        (5, 0, 0): {"alias": "ShaderNodeValToRGB"},
    },
    "CompositorNodeMixRGB": {
        (5, 0, 0): {
            "alias": "ShaderNodeMix",
            "values": {"data_type": "RGBA"},
            "inputs": {"Fac": "Factor", "Image": "A", "Image_001": "B"},
            "outputs": {"Image": "Result"},
        },
    },
}


def resolve_node_version(type: str) -> Dict[str, Dict]:
    """Get VERSIONED_NODES setup dictionary based on used Blender version to use when adding node by their type string."""
    versions = VERSIONED_NODES.get(type, None)
    if not versions:
        return {"alias": type}

    try:
        setup = next(
            versions[version]
            for version in versions.keys()
            if BLENDER_VERSION >= version
        )
    except StopIteration:
        return {"alias": type}
    return setup


def resolve_socket_version(
    node: bpy.types.Node, type: Literal["input", "output"], socket: str
) -> str:
    """
    Get versioned socket reference string using version_compatibility_data custom property.
    This function assumes the node argument is a node added using _Nodes.add() method.
    """
    data = node["version_compatibility_data"]
    if mappings := data.get(f"{type}s"):
        if mapped_socket := mappings.get(socket):
            return mapped_socket
    return socket
