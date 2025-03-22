import bpy
from bpy.types import NodeTree, Node
from typing import Dict, Optional


class CustomNodeGroupBuilder:
    """Builder class for Blender Group Nodes"""

    def init_group_node(self) -> None:
        """Initialize group node with node tree and input and output sockets."""

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
        self._nodes[key] = self._node_tree.nodes.new(type=type)
        if name:
            self._nodes[key].name = name
        return self._nodes[key]
