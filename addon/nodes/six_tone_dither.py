from bpy.types import CompositorNodeCustomGroup
from bpy.props import EnumProperty, FloatProperty

from ..textures import initialize_textures, threshold_enum_items
from ..palettes import palette_6tone_enum_items, Color as c
from ..node_utils import CustomNodeGroupBuilder

# defaults
_CR_POS = (0.0, 0.0322, 0.0968, 0.226, 0.452, 1.0)
_PRESET = "6tone_grayscale"


class CompositorNodeRetromancer6ToneDither(
    CompositorNodeCustomGroup,
    CustomNodeGroupBuilder,
):
    """6 tone palette ordered dither effect using provided threshold map texture."""

    bl_idname = "CompositorNodeRetromancer6ToneDither"
    bl_label = "6-Tone Ordered Dither"
    bl_icon = "SHADERFX"
    bl_width_default = 300

    def update_texture(self, context) -> None:
        """threshold_enum_prop update callback"""
        for i in list(range(5)) + ["alpha"]:
            dither_node = self.node_tree.nodes.get(f"dither_{i}")
            dither_node.threshold_enum_prop = self.threshold_enum_prop

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
        for i in range(5):
            prop = self.parse_datapath(context.property[1])
            self._update_ramp(f"cr_mask_{i}", prop)
            self._update_ramp(f"cr_gradient_{i}", prop)

    threshold_enum_prop: EnumProperty(items=threshold_enum_items, name="", update=update_texture)  # type: ignore

    _TONE_RAMP_KWARGS = dict(subtype="FACTOR", update=update_tone_ramps, min=0.0, max=1.0)
    tone_ramp_0_prop: FloatProperty(name="tone_pos_0", default=_CR_POS[0], **_TONE_RAMP_KWARGS)  # type: ignore
    tone_ramp_1_prop: FloatProperty(name="tone_pos_1", default=_CR_POS[1], **_TONE_RAMP_KWARGS)  # type: ignore
    tone_ramp_2_prop: FloatProperty(name="tone_pos_3", default=_CR_POS[2], **_TONE_RAMP_KWARGS)  # type: ignore
    tone_ramp_3_prop: FloatProperty(name="tone_pos_3", default=_CR_POS[3], **_TONE_RAMP_KWARGS)  # type: ignore
    tone_ramp_4_prop: FloatProperty(name="tone_pos_4", default=_CR_POS[4], **_TONE_RAMP_KWARGS)  # type: ignore
    tone_ramp_5_prop: FloatProperty(name="tone_pos_5", default=_CR_POS[5], **_TONE_RAMP_KWARGS)  # type: ignore

    def init(self, context) -> None:
        initialize_textures()
        self.init_group_node()

    def draw_buttons(self, context, layout) -> None:
        layout.prop(self, "threshold_enum_prop")
        layout.label(text="Tone ramp controls:")
        row = layout.column_flow(columns=6, align=True)
        for i in range(6):
            row.prop(self, f"tone_ramp_{i}_prop", text="")
        layout.row()

    def _configure_interface(self) -> None:
        preset_values = iter(c.from_palette(_PRESET))
        for i in range(1, 7):
            self.inputs[f"Color {i}"].default_value = next(preset_values)

    def _configure_sockets(self) -> None:
        # INPUTS:
        self.node_tree.interface.new_socket(name="Image", in_out="INPUT", socket_type="NodeSocketColor")
        for i in range(1, 7):
            self.node_tree.interface.new_socket(name=f"Color {i}", in_out="INPUT", socket_type="NodeSocketColor")
        self.node_tree.interface.new_socket(name="Brightness", in_out="INPUT", socket_type="NodeSocketFloat")
        self.node_tree.interface.new_socket(name="Contrast", in_out="INPUT", socket_type="NodeSocketFloat")

        # OUTPUTS:
        self.node_tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")

    def _configure_nodes(self) -> None:
        nodes = self.nodes

        for i in range(5):
            mask = nodes.add(f"cr_mask_{i}", type="CompositorNodeValToRGB", name=f"cr_mask_{i}")
            gradient = nodes.add(f"cr_gradient_{i}", type="CompositorNodeValToRGB", name=f"cr_gradient_{i}")
            multiply = nodes.add(f"multiply_{i}", type="CompositorNodeMixRGB", name=f"multiply_{i}")
            nodes.add(f"dither_{i}", type="CompositorNodeRetromancer2ToneDither", name=f"dither_{i}")

            mask.color_ramp.interpolation = "CONSTANT"
            [mask.color_ramp.elements.new(0) for _ in range(4)]

            gradient.color_ramp.interpolation = "EASE"
            [gradient.color_ramp.elements.new(0) for _ in range(4)]

            multiply.blend_type = "MULTIPLY"
            multiply.inputs[0].default_value = 1

        _cr_color_lookup = {
            # highlights
            nodes.cr_mask_0: (1, 1, 1, 1, 0, 0),
            nodes.cr_gradient_0: (1, 1, 1, 1, 0, 1),
            nodes.cr_mask_1: (1, 1, 1, 0, 1, 1),
            nodes.cr_gradient_1: (1, 1, 1, 0, 1, 1),
            nodes.cr_mask_2: (1, 1, 0, 1, 1, 1),
            nodes.cr_gradient_2: (1, 1, 0, 1, 1, 1),
            nodes.cr_mask_3: (1, 0, 1, 1, 1, 1),
            nodes.cr_gradient_3: (1, 0, 1, 1, 1, 1),
            nodes.cr_mask_4: (0, 1, 1, 1, 1, 1),
            nodes.cr_gradient_4: (0, 1, 1, 1, 1, 1),
            # shadows
        }

        for node, colors in _cr_color_lookup.items():
            for i, color in enumerate(colors):
                node.color_ramp.elements[i].color = c.black if color == 1 else c.white
                node.color_ramp.elements[i].position = _CR_POS[i]

        for i in range(4):
            nodes.add(f"add{i}", type="CompositorNodeMixRGB")
            node = nodes.get(f"add{i}")
            node.blend_type = "ADD"
            node.inputs[0].default_value = 1

        nodes.add("alpha", type="CompositorNodeSetAlpha")
        nodes.add("dither_alpha", type="CompositorNodeRetromancer2ToneDither", name="dither_alpha")
        nodes.add("sep_color", type="CompositorNodeSeparateColor")
        nodes.add("brightness", type="CompositorNodeBrightContrast")
        nodes.add("posterize", type="CompositorNodePosterize")

        nodes.posterize.inputs["Steps"].default_value = 32

    def _configure_links(self) -> None:
        self.link(output=("input", "Image"), input=("brightness", "Image"))
        self.link(output=("input", "Brightness"), input=("brightness", 1))
        self.link(output=("input", "Contrast"), input=("brightness", 2))

        for i in range(5):
            self.link(output=("brightness", "Image"), input=(f"cr_mask_{i}", "Fac"))
            self.link(output=("brightness", "Image"), input=(f"cr_gradient_{i}", "Fac"))
            self.link(output=(f"cr_mask_{i}", 0), input=(f"multiply_{i}", "Image"))
            self.link(output=(f"cr_gradient_{i}", 0), input=(f"dither_{i}", "Image"))
            self.link(output=(f"dither_{i}", "Image"), input=(f"multiply_{i}", "Image_001"))

            self.link(output=("input", f"Color {6-i}"), input=(f"dither_{i}", "Color 1"))
            self.link(output=("input", f"Color {5-i}"), input=(f"dither_{i}", "Color 2"))

        for i in range(4):
            self.link(output=(f"multiply_{i+1}", "Image"), input=(f"add{i}", "Image"))
            self.link(output=("multiply_0" if i == 0 else f"add{i-1}", "Image"), input=(f"add{i}", "Image_001"))

        self.link(output=("add3", "Image"), input=("alpha", "Image"))
        self.link(output=("brightness", "Image"), input=("sep_color", "Image"))
        self.link(output=("sep_color", 3), input=("posterize", "Image"))
        self.link(output=("posterize", "Image"), input=("dither_alpha", "Image"))
        self.link(output=("dither_alpha", "Image"), input=("alpha", "Alpha"))
        self.link(output=("alpha", "Image"), input=("output", "Image"))
