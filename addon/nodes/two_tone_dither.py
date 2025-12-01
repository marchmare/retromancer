import bpy
from bpy.types import CompositorNodeCustomGroup
from bpy.props import EnumProperty

from ..textures import initialize_textures, threshold_enum_items
from ..palettes import palette_2tone_enum_items, Color as c
from ..node_utils import CustomNodeGroupBuilder
from ..compatibilty import (
    get_math_node_type,
    get_mixrgb_node,
    mixrgb_input_color,
    mixrgb_output,
)

# defaults
_PRESET = "2tone_bw"


class CompositorNodeRetromancer2ToneDither(
    CompositorNodeCustomGroup,
    CustomNodeGroupBuilder,
):
    """Monochromatic, 1-bit palette ordered dither effect using provided threshold map texture."""

    bl_idname = "CompositorNodeRetromancer2ToneDither"
    bl_label = "Monochrome Ordered Dither"
    bl_icon = "SHADERFX"
    bl_width_default = 200

    def update_texture(self, context) -> None:
        """threshold_enum_prop update callback"""

        texture_node = self.node_tree.nodes.get("Texture")
        texture_node.image = bpy.data.images.get(self.threshold_enum_prop)

    def _update_color_palette(self, preset: str) -> None:
        """Load color values from preset into color sockets."""
        preset_values = iter(c.from_palette(preset))
        for i in range(1, 3):
            self.inputs[f"Color {i}"].default_value = next(preset_values)

    def update_preset(self, context) -> None:
        """palette_presets_enum_prop update callback"""

        if not context.property:
            return
        preset = getattr(self, context.property[1].split(".")[-1])
        self._update_color_palette(preset)

    threshold_enum_prop: EnumProperty(  # type: ignore
        items=threshold_enum_items, name="", update=update_texture
    )
    palette_presets_enum_prop: EnumProperty(  # type: ignore
        items=palette_2tone_enum_items, name="Preset", update=update_preset
    )

    def init(self, context) -> None:
        initialize_textures()
        self.init_group_node()

    def draw_buttons(self, context, layout) -> None:
        layout.prop(self, "threshold_enum_prop")
        layout.prop(self, "palette_presets_enum_prop")

    def _configure_interface(self) -> None:
        self.palette_presets_enum_prop = _PRESET
        self._update_color_palette(_PRESET)

    def _configure_sockets(self) -> None:
        # INPUTS:
        self.node_tree.interface.new_socket(
            name="Image",
            in_out="INPUT",
            socket_type="NodeSocketColor",
        )
        for i in range(1, 3):
            self.node_tree.interface.new_socket(
                name=f"Color {i}",
                in_out="INPUT",
                socket_type="NodeSocketColor",
            )
        self.node_tree.interface.new_socket(
            name="Brightness",
            in_out="INPUT",
            socket_type="NodeSocketFloat",
        )
        self.node_tree.interface.new_socket(
            name="Contrast",
            in_out="INPUT",
            socket_type="NodeSocketFloat",
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
        nodes.add("greater_than", type=get_math_node_type())
        nodes.add("greater_than_alpha", type=get_math_node_type())
        nodes.add("mix", type=get_mixrgb_node())
        nodes.add("alpha", type="CompositorNodeSetAlpha")
        nodes.add("texture", type="CompositorNodeImage", name="Texture")
        nodes.add("brightness", type="CompositorNodeBrightContrast")

        nodes.sep_color.mode = "HSV"
        nodes.texture.image = bpy.data.images.get(self.threshold_enum_prop)
        nodes.greater_than.operation = "GREATER_THAN"
        nodes.greater_than_alpha.operation = "GREATER_THAN"

        if hasattr(self.nodes.mix, "data_type"):  # for compatibility with Blender 5.0
            self.nodes.mix.data_type = "RGBA"

        # TODO: verify if it does help with anything, adjust value, add links
        # nodes.add("posterize", type="CompositorNodePosterize")
        # nodes.posterize.inputs["Steps"].default_value = 32

    def _configure_links(self) -> None:
        nodes = self.nodes
        links = self.node_tree.links
        links.new(nodes.input.outputs["Image"], nodes.brightness.inputs["Image"])
        links.new(nodes.input.outputs["Brightness"], nodes.brightness.inputs[1])
        links.new(nodes.input.outputs["Contrast"], nodes.brightness.inputs[2])
        links.new(nodes.brightness.outputs["Image"], nodes.sep_color.inputs["Image"])
        links.new(
            nodes.input.outputs["Color 1"], nodes.mix.inputs[mixrgb_input_color(1)]
        )
        links.new(
            nodes.input.outputs["Color 2"], nodes.mix.inputs[mixrgb_input_color(2)]
        )
        links.new(nodes.texture.outputs["Image"], nodes.greater_than.inputs[1])
        links.new(nodes.texture.outputs["Image"], nodes.greater_than_alpha.inputs[1])
        links.new(nodes.sep_color.outputs[2], nodes.greater_than.inputs[0])
        links.new(nodes.sep_color.outputs[3], nodes.greater_than_alpha.inputs[0])
        links.new(nodes.greater_than.outputs["Value"], nodes.mix.inputs[0])
        links.new(
            nodes.greater_than_alpha.outputs["Value"], nodes.alpha.inputs["Alpha"]
        )
        links.new(nodes.mix.outputs[mixrgb_output()], nodes.alpha.inputs["Image"])
        links.new(nodes.alpha.outputs["Image"], nodes.output.inputs["Image"])
