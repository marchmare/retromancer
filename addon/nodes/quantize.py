from bpy.types import CompositorNodeCustomGroup

from ..node_utils import CustomNodeGroupBuilder
from ..compatibilty import get_math_node_type


class CompositorNodeRetromancerQuantize(
    CompositorNodeCustomGroup,
    CustomNodeGroupBuilder,
):
    """Custom posterization node to simulate digital bit-depth constraints."""

    bl_idname = "CompositorNodeRetromancerQuantize"
    bl_label = "Quantize"
    bl_icon = "SHADERFX"

    def init(self, context) -> None:
        self.init_group_node()

    def _configure_interface(self) -> None:
        self.inputs[1].default_value = 64.0

    def _configure_sockets(self) -> None:
        # INPUTS:
        self.node_tree.interface.new_socket(
            name="Value",
            in_out="INPUT",
            socket_type="NodeSocketFloat",
        )
        fac_in_socket = self.node_tree.interface.new_socket(
            name="Fac",
            in_out="INPUT",
            socket_type="NodeSocketFloat",
        )
        fac_in_socket.min_value = 0

        # OUTPUTS:
        self.node_tree.interface.new_socket(
            name="Value",
            in_out="OUTPUT",
            socket_type="NodeSocketFloat",
        )

    def _configure_nodes(self) -> None:
        nodes = self.nodes
        nodes.add("multiply", type=get_math_node_type())
        nodes.add("floor", type=get_math_node_type())
        nodes.add("divide", type=get_math_node_type())

        nodes.multiply.operation = "MULTIPLY"
        nodes.floor.operation = "FLOOR"
        nodes.divide.operation = "DIVIDE"

    def _configure_links(self) -> None:
        nodes = self.nodes
        links = self.node_tree.links
        links.new(nodes.input.outputs["Value"], nodes.multiply.inputs[0])
        links.new(nodes.input.outputs["Fac"], nodes.multiply.inputs[1])
        links.new(nodes.input.outputs["Fac"], nodes.divide.inputs[1])
        links.new(nodes.multiply.outputs["Value"], nodes.floor.inputs["Value"])
        links.new(nodes.floor.outputs["Value"], nodes.divide.inputs[0])
        links.new(nodes.divide.outputs["Value"], nodes.output.inputs["Value"])
