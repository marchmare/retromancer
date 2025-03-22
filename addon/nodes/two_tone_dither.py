import bpy
from bpy.types import CompositorNodeCustomGroup
from bpy.props import EnumProperty

from ..textures import initialize_textures, threshold_enum_items
from ..palettes import palette_2tone_enum_items, Color
from ..node_utils import CustomNodeGroupBuilder


class CompositorNodeRetromancer2ToneDither(
    CompositorNodeCustomGroup,
    CustomNodeGroupBuilder,
):
    """Monochromatic ordered dither effect using provided threshold map texture."""

    bl_idname = "CompositorNodeRetromancer2ToneDither"
    bl_label = "Monochrome Ordered Dither"
    bl_icon = "SHADERFX"
    bl_width_default = 200

    def update_texture(self, context) -> None:
        texture_node = self.node_tree.nodes.get("Texture")
        texture_node.texture = bpy.data.textures.get(self.threshold_enum_prop)

    def update_preset(self, context) -> None:
        pass

    threshold_enum_prop: EnumProperty(  # type: ignore
        items=threshold_enum_items, name="", update=update_texture
    )
    palette_presets_enum_prop: EnumProperty(  # type: ignore
        items=palette_2tone_enum_items, name="Preset", update=update_preset
    )

    def init(self, context) -> None:
        initialize_textures()
        self.init_group_node()
        self.set_default_interface()

    def set_default_interface(self):
        self.inputs["Color 1"].default_value = Color.black
        self.inputs["Color 2"].default_value = Color.white

    def draw_buttons(self, context, layout) -> None:
        layout.prop(self, "threshold_enum_prop")
        layout.prop(self, "palette_presets_enum_prop")

    def _configure_sockets(self) -> None:
        # INPUTS:
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
        self.node_tree.interface.new_socket(
            name="Image",
            in_out="INPUT",
            socket_type="NodeSocketColor",
        )
        # OUTPUTS:
        self.node_tree.interface.new_socket(
            name="Image",
            in_out="OUTPUT",
            socket_type="NodeSocketColor",
        )

    def _configure_nodes(self) -> None:
        nodes = self.nodes
        nodes.add("sep_color", type="CompositorNodeSeparateColor")
        nodes.add("greater_than", type="CompositorNodeMath")
        nodes.add("mix", type="CompositorNodeMixRGB")
        nodes.add("transform", type="CompositorNodeTransform")
        nodes.add("texture", type="CompositorNodeTexture")

        nodes.sep_color.mode = "HSV"
        nodes.texture.texture = bpy.data.textures.get(self.threshold_enum_prop)
        nodes.greater_than.operation = "GREATER_THAN"

    def _configure_links(self) -> None:
        nodes = self.nodes
        links = self.node_tree.links
        links.new(nodes.input.outputs["Image"], nodes.sep_color.inputs["Image"])
        links.new(nodes.input.outputs["Color 1"], nodes.mix.inputs[1])
        links.new(nodes.input.outputs["Color 2"], nodes.mix.inputs[2])
        links.new(nodes.texture.outputs["Color"], nodes.greater_than.inputs[1])
        links.new(nodes.sep_color.outputs[2], nodes.greater_than.inputs[0])
        links.new(nodes.greater_than.outputs["Value"], nodes.mix.inputs[0])
        links.new(nodes.mix.outputs["Image"], nodes.transform.inputs["Image"])
        links.new(nodes.transform.outputs["Image"], nodes.output.inputs["Image"])
