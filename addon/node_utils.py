import bpy
import traceback
from bpy.types import NodeTree, Node
from typing import Dict, Optional, Tuple
from .ui import draw_popup
from .compatibilty import resolve_node_version, resolve_socket_version


class CustomNodeGroupBuilder:
    """Builder class for Blender Group Nodes"""

    def init_group_node(self) -> None:
        """Initialize group node with node tree and input and output sockets."""

        try:
            self.node_tree = bpy.data.node_groups.new(
                "." + self.bl_idname + "NodeTree", "CompositorNodeTree"
            )
            self.nodes = _Nodes(self.node_tree)
            self.nodes.add("input", "NodeGroupInput")
            self.nodes.add("output", "NodeGroupOutput")

            self._configure_sockets()
            self._configure_nodes()
            self._configure_links()
            self._configure_interface()

        except RuntimeError:
            draw_popup(text=traceback.format_exc(), icon="ERROR")
            traceback.print_exc()

    def _configure_sockets(self) -> None:
        """Configure input and output sockets of the node group and their properties"""
        pass

    def _configure_nodes(self) -> None:
        """Configure Blender nodes and their properties"""
        pass

    def _configure_links(self) -> None:
        """Configure links between added nodes"""
        pass

    def _configure_interface(self) -> None:
        """Configure default state of node's interface"""
        pass

    @staticmethod
    def parse_datapath(property: str) -> str:
        """
        Parse datapath from a datapath string to extract the identifier of the struct.
        To be used with string from context.property.
        """
        return property.split(".")[-1]

    def link(self, output: Tuple[str, str | int], input: Tuple[str, str | int]) -> None:
        """
        Link two nodes together via provided socket reference.
        Sockets are checked for version compatibility and errors are raised if requested socket can't be found.
        """
        # output node
        _node1 = self.nodes.get(output[0])
        mapped_socket1 = resolve_socket_version(_node1, "output", output[1])
        _socket1 = _get_socket(_node1.outputs, mapped_socket1)

        # input node
        _node2 = self.nodes.get(input[0])
        mapped_socket2 = resolve_socket_version(_node2, "input", input[1])
        _socket2 = _get_socket(_node2.inputs, mapped_socket2)

        self.node_tree.links.new(_socket1, _socket2)


class _Nodes:
    """Nodes collection for node setup and group classes"""

    def __init__(self, node_tree: NodeTree) -> None:
        self._node_tree = node_tree
        self._nodes: Dict[str, bpy.types.Node] = {}

    def __getattr__(self, name: str) -> Node:
        if name in self._nodes:
            return self._nodes[name]
        raise AttributeError(f"Node '{name}' not found in added nodes.")

    def get(self, name: str) -> Node | None:
        if name in self._nodes:
            return self._nodes[name]
        return None

    def add(self, key: str, type: str, name: Optional[str] = None) -> Node:
        """
        Add node to Compositor node tree.
        Nodes are checked for version compatibility and version_compatibility_data dictionary is added as custom property to the node.
        """
        _versioned_node = resolve_node_version(type)
        self._nodes[key] = self._node_tree.nodes.new(type=_versioned_node["alias"])
        self._nodes[key]["version_compatibility_data"] = _versioned_node

        if _values := _versioned_node.get("values", None):
            for value in _values:
                setattr(self._nodes[key], value, _values[value])

        if name:
            self._nodes[key].name = name
        return self._nodes[key]


def _get_socket(
    sockets: bpy.types.NodeSocketCollection, key: str | int
) -> bpy.types.NodeSocket:
    """Socket getter utility function. Handles displaying errors if nonexistent socket is requested."""
    if isinstance(key, int):
        try:
            return sockets[key]
        except IndexError:
            draw_popup(text=traceback.format_exc(), icon="ERROR")
            traceback.print_exc()
    elif isinstance(key, str):
        try:
            return sockets[key]
        except KeyError:
            draw_popup(text=traceback.format_exc(), icon="ERROR")
            traceback.print_exc()
    else:
        raise TypeError(f"Socket key must be int or str, not {type(key)}")
