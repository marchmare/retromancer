from bpy.types import CompositorNodeCustomGroup
from bpy.props import EnumProperty, FloatProperty

from ..textures import initialize_textures, threshold_enum_items
from ..palettes import palette_4tone_enum_items, Color as c
from ..node_utils import CustomNodeGroupBuilder

# defaults
_TONES = ["hlt", "mid", "shd"]
_CR_POS = (0.0, 0.0615, 0.2431, 1.0)
_PRESET = "4tone_grayscale"


class CompositorNodeRetromancer4ToneDither(
    CompositorNodeCustomGroup,
    CustomNodeGroupBuilder,
):
    """4 tone (2-bit) palette ordered dither effect using provided threshold map texture."""

    bl_idname = "CompositorNodeRetromancer4ToneDither"
    bl_label = "4-Tone Ordered Dither"
    bl_icon = "SHADERFX"
    bl_width_default = 210

    def update_texture(self, context) -> None:
        """threshold_enum_prop update callback"""
        for tone in _TONES + ["alpha"]:
            dither_node = self.node_tree.nodes.get(f"dither_{tone}")
            dither_node.threshold_enum_prop = self.threshold_enum_prop

    def _update_color_palette(self, preset: str) -> None:
        """Load color values from preset into color sockets."""
        preset_values = iter(c.from_palette(preset))
        for i in range(1, 5):
            self.inputs[f"Color {i}"].default_value = next(preset_values)

    def update_preset(self, context) -> None:
        """palette_presets_enum_prop update callback"""
        if not context.property:
            return
        prop = self.parse_datapath(context.property[1])
        preset = getattr(self, prop)
        self._update_color_palette(preset)

    def _update_ramp(self, name: str, property: str) -> None:
        """Update position of all color ramps' stops based on values from each tone_ramp_x_prop"""
        prop_val = getattr(self, property)
        elem_idx = int(property.split("_")[-2])
        color_ramp_node = self.node_tree.nodes.get(name)
        color_ramp_node.color_ramp.elements[elem_idx].position = prop_val

    def update_tone_ramps(self, context) -> None:
        """tone_ramp_x_prop update callback"""
        if not context.property:
            return
        for tone in _TONES:
            prop = self.parse_datapath(context.property[1])
            self._update_ramp(f"cr_mask_{tone}", prop)
            self._update_ramp(f"cr_gradient_{tone}", prop)

    threshold_enum_prop: EnumProperty(  # type: ignore
        items=threshold_enum_items, name="", update=update_texture
    )
    palette_presets_enum_prop: EnumProperty(  # type: ignore
        items=palette_4tone_enum_items, name="Preset", update=update_preset
    )

    tone_ramp_0_prop: FloatProperty(
        subtype="FACTOR",
        update=update_tone_ramps,
        name="tone_pos_0",
        min=0.0,
        max=1.0,
        default=_CR_POS[0],
    )  # type: ignore
    tone_ramp_1_prop: FloatProperty(
        subtype="FACTOR",
        update=update_tone_ramps,
        name="tone_pos_1",
        min=0.0,
        max=1.0,
        default=_CR_POS[1],
    )  # type: ignore
    tone_ramp_2_prop: FloatProperty(
        subtype="FACTOR",
        update=update_tone_ramps,
        name="tone_pos_3",
        min=0.0,
        max=1.0,
        default=_CR_POS[2],
    )  # type: ignore
    tone_ramp_3_prop: FloatProperty(
        subtype="FACTOR",
        update=update_tone_ramps,
        name="tone_pos_3",
        min=0.0,
        max=1.0,
        default=_CR_POS[3],
    )  # type: ignore

    def init(self, context) -> None:
        initialize_textures()
        self.init_group_node()

    def draw_buttons(self, context, layout) -> None:
        layout.prop(self, "threshold_enum_prop")
        layout.label(text="Tone ramp controls:")
        row = layout.column_flow(columns=4, align=True)
        row.prop(self, "tone_ramp_0_prop", text="")
        row.prop(self, "tone_ramp_1_prop", text="")
        row.prop(self, "tone_ramp_2_prop", text="")
        row.prop(self, "tone_ramp_3_prop", text="")
        layout.row()
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
        for i in range(1, 5):
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
        for tone in _TONES:
            mask = nodes.add(
                f"cr_mask_{tone}",
                type="CompositorNodeValToRGB",
                name=f"cr_mask_{tone}",
            )
            gradient = nodes.add(
                f"cr_gradient_{tone}",
                type="CompositorNodeValToRGB",
                name=f"cr_gradient_{tone}",
            )
            multiply = nodes.add(
                f"multiply_{tone}",
                type="CompositorNodeMixRGB",
                name=f"multiply_{tone}",
            )
            nodes.add(
                f"dither_{tone}",
                type="CompositorNodeRetromancer2ToneDither",
                name=f"dither_{tone}",
            )

            mask.color_ramp.interpolation = "CONSTANT"
            [mask.color_ramp.elements.new(0) for _ in range(2)]

            gradient.color_ramp.interpolation = "EASE"
            [gradient.color_ramp.elements.new(0) for _ in range(2)]

            multiply.blend_type = "MULTIPLY"
            multiply.inputs[0].default_value = 1

        _cr_color_lookup = {
            nodes.cr_mask_hlt: (1, 1, 0, 0),
            nodes.cr_gradient_hlt: (1, 1, 1, 0),
            nodes.cr_mask_mid: (1, 0, 1, 1),
            nodes.cr_gradient_mid: (0, 0, 1, 1),
            nodes.cr_mask_shd: (0, 1, 1, 1),
            nodes.cr_gradient_shd: (0, 1, 1, 1),
        }

        for node, colors in _cr_color_lookup.items():
            for i, color in enumerate(colors):
                node.color_ramp.elements[i].color = c.black if color == 1 else c.white
                node.color_ramp.elements[i].position = _CR_POS[i]

        for i in range(2):
            nodes.add(f"add{i}", type="CompositorNodeMixRGB")
            node = nodes.get(f"add{i}")
            node.blend_type = "ADD"
            node.inputs[0].default_value = 1

        nodes.add("alpha", type="CompositorNodeSetAlpha")
        nodes.add(
            "dither_alpha",
            type="CompositorNodeRetromancer2ToneDither",
            name="dither_alpha",
        )
        nodes.add("sep_color", type="CompositorNodeSeparateColor")
        nodes.add("brightness", type="CompositorNodeBrightContrast")
        nodes.add("posterize", type="CompositorNodePosterize")
        nodes.posterize.inputs["Steps"].default_value = 32

    def _configure_links(self) -> None:
        self.link(output=("input", "Image"), input=("brightness", "Image"))
        self.link(output=("input", "Brightness"), input=("brightness", 1))
        self.link(output=("input", "Contrast"), input=("brightness", 2))

        for tone in _TONES:
            self.link(output=("brightness", "Image"), input=(f"cr_mask_{tone}", "Fac"))
            self.link(output=("brightness", "Image"), input=(f"cr_gradient_{tone}", "Fac"))
            self.link(output=(f"cr_mask_{tone}", 0), input=(f"multiply_{tone}", "Image"))
            self.link(output=(f"cr_gradient_{tone}", 0), input=(f"dither_{tone}", "Image"))
            self.link(output=(f"dither_{tone}", "Image"), input=(f"multiply_{tone}", "Image_001"))

        self.link(output=("multiply_mid", "Image"), input=("add0", "Image"))
        self.link(output=("multiply_shd", "Image"), input=("add0", "Image_001"))
        self.link(output=("multiply_hlt", "Image"), input=("add1", "Image"))
        self.link(output=("add0", "Image"), input=("add1", "Image_001"))

        self.link(output=("add1", "Image"), input=("alpha", "Image"))
        self.link(output=("brightness", "Image"), input=("sep_color", "Image"))
        self.link(output=("sep_color", 3), input=("posterize", "Image"))
        self.link(output=("posterize", "Image"), input=("dither_alpha", "Image"))
        self.link(output=("dither_alpha", "Image"), input=("alpha", "Alpha"))
        self.link(output=("alpha", "Image"), input=("output", "Image"))

        self.link(output=("input", "Color 1"), input=("dither_shd", "Color 2"))
        self.link(output=("input", "Color 2"), input=("dither_shd", "Color 1"))
        self.link(output=("input", "Color 2"), input=("dither_mid", "Color 2"))
        self.link(output=("input", "Color 3"), input=("dither_mid", "Color 1"))
        self.link(output=("input", "Color 3"), input=("dither_hlt", "Color 1"))
        self.link(output=("input", "Color 4"), input=("dither_hlt", "Color 2"))
