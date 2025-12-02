import bpy
from bpy.types import CompositorNodeCustomGroup
from bpy.props import EnumProperty

from ..textures import initialize_textures, threshold_enum_items
from ..palettes import palette_2tone_enum_items, Color as c
from ..node_utils import CustomNodeGroupBuilder

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
        nodes.add("greater_than", type="CompositorNodeMath")
        nodes.add("greater_than_alpha", type="CompositorNodeMath")
        nodes.add("mix", type="CompositorNodeMixRGB")
        nodes.add("alpha", type="CompositorNodeSetAlpha")
        nodes.add("texture", type="CompositorNodeImage", name="Texture")
        nodes.add("brightness", type="CompositorNodeBrightContrast")

        nodes.sep_color.mode = "HSV"
        nodes.texture.image = bpy.data.images.get(self.threshold_enum_prop)
        nodes.greater_than.operation = "GREATER_THAN"
        nodes.greater_than_alpha.operation = "GREATER_THAN"

        # TODO: verify if it does help with anything, adjust value, add links
        # nodes.add("posterize", type="CompositorNodePosterize")
        # nodes.posterize.inputs["Steps"].default_value = 32

    def _configure_links(self) -> None:
        self.link(output=("input", "Image"), input=("brightness", "Image"))
        self.link(output=("input", "Brightness"), input=("brightness", 1))
        self.link(output=("input", "Contrast"), input=("brightness", 2))
        self.link(output=("brightness", "Image"), input=("sep_color", "Image"))
        self.link(output=("input", "Color 1"), input=("mix", "Image"))
        self.link(output=("input", "Color 2"), input=("mix", "Image_001"))
        self.link(output=("texture", "Image"), input=("greater_than", 1))
        self.link(output=("texture", "Image"), input=("greater_than_alpha", 1))
        self.link(output=("sep_color", 2), input=("greater_than", 0))
        self.link(output=("sep_color", 3), input=("greater_than_alpha", 0))
        self.link(output=("greater_than", "Value"), input=("mix", "Fac"))
        self.link(output=("greater_than_alpha", "Value"), input=("alpha", "Alpha"))
        self.link(output=("mix", "Image"), input=("alpha", "Image"))
        self.link(output=("alpha", "Image"), input=("output", "Image"))
