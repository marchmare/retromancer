import bpy
from bpy.types import CompositorNodeCustomGroup
from bpy.props import EnumProperty

from ..textures import initialize_textures, threshold_enum_items
from ..node_utils import CustomNodeGroupBuilder


class CompositorNodeRetromancer2BitDither(
    CompositorNodeCustomGroup,
    CustomNodeGroupBuilder,
):
    """Monochromatic ordered dither effect using provided threshold map texture."""

    bl_idname = "CompositorNodeRetromancer2BitDither"
    bl_label = "Monochrome Ordered Dither"
    bl_icon = "SHADERFX"
    bl_width_default = 200

    def update_texture(self, context) -> None:
        texture_node = context.node.node_tree.nodes.get("Texture")
        texture_node.texture = bpy.data.textures.get(self.threshold_enum_prop)

    threshold_enum_prop: EnumProperty(  # type: ignore
        items=threshold_enum_items, name="", update=update_texture
    )

    def init(self, context) -> None:
        initialize_textures()
        self.init_group_node()
        self.inputs["Steps"].default_value = 16.0
        self.inputs["Scale"].default_value = 1
        self.inputs["Color 1"].default_value = (0.0069, 0.0065, 0.0051, 1)
        self.inputs["Color 2"].default_value = (0.0781, 0.1589, 0.0144, 1)

    def draw_buttons(self, context, layout) -> None:
        layout.label(text="Threshold map:")
        layout.prop(self, "threshold_enum_prop")

    def _configure_sockets(self) -> None:
        # INPUTS:
        self.node_tree.interface.new_socket(
            name="Image",
            in_out="INPUT",
            socket_type="NodeSocketColor",
        )
        steps_in_socket = self.node_tree.interface.new_socket(
            name="Steps",
            in_out="INPUT",
            socket_type="NodeSocketFloat",
        )
        scale_in_socket = self.node_tree.interface.new_socket(
            name="Scale",
            in_out="INPUT",
            socket_type="NodeSocketFloat",
        )
        self.node_tree.interface.new_socket(
            name="Color 1",
            in_out="INPUT",
            socket_type="NodeSocketColor",
        )
        self.node_tree.interface.new_socket(
            name="Color 2",
            in_out="INPUT",
            socket_type="NodeSocketColor",
        )

        steps_in_socket.min_value = 0
        steps_in_socket.max_value = 64

        scale_in_socket.min_value = 0
        scale_in_socket.max_value = 1

        # OUTPUTS:
        self.node_tree.interface.new_socket(
            name="Image",
            in_out="OUTPUT",
            socket_type="NodeSocketColor",
        )

    def _configure_nodes(self) -> None:
        nodes = self.nodes
        nodes.add("scale", type="CompositorNodeScale")
        nodes.add("rgb_to_bw", type="CompositorNodeRGBToBW")
        nodes.add("quantize", type="CompositorNodeRetromancerQuantize")
        nodes.add("greater_than", type="CompositorNodeMath")
        nodes.add("power", type="CompositorNodeMath")
        nodes.add("mix", type="CompositorNodeMixRGB")
        nodes.add("transform", type="CompositorNodeTransform")
        nodes.add("texture", type="CompositorNodeTexture")

        nodes.texture.texture = bpy.data.textures.get(self.threshold_enum_prop)
        nodes.greater_than.operation = "GREATER_THAN"
        nodes.power.operation = "POWER"
        nodes.power.inputs[1].default_value = -1

    def _configure_links(self) -> None:
        nodes = self.nodes
        links = self.node_tree.links
        links.new(nodes.input.outputs["Image"], nodes.scale.inputs["Image"])
        links.new(nodes.input.outputs["Steps"], nodes.quantize.inputs["Fac"])
        links.new(nodes.input.outputs["Scale"], nodes.scale.inputs["X"])
        links.new(nodes.input.outputs["Scale"], nodes.scale.inputs["Y"])
        links.new(nodes.input.outputs["Scale"], nodes.power.inputs[0])
        links.new(nodes.input.outputs["Scale"], nodes.texture.inputs["Scale"])
        links.new(nodes.input.outputs["Color 1"], nodes.mix.inputs[1])
        links.new(nodes.input.outputs["Color 2"], nodes.mix.inputs[2])
        links.new(nodes.texture.outputs["Color"], nodes.greater_than.inputs[1])
        links.new(nodes.scale.outputs["Image"], nodes.rgb_to_bw.inputs["Image"])
        links.new(nodes.rgb_to_bw.outputs["Val"], nodes.quantize.inputs["Value"])
        links.new(nodes.quantize.outputs["Value"], nodes.greater_than.inputs[0])
        links.new(nodes.greater_than.outputs["Value"], nodes.mix.inputs[0])
        links.new(nodes.power.outputs["Value"], nodes.transform.inputs["Scale"])
        links.new(nodes.mix.outputs["Image"], nodes.transform.inputs["Image"])
        links.new(nodes.transform.outputs["Image"], nodes.output.inputs["Image"])
