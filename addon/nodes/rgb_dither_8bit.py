from bpy.types import CompositorNodeCustomGroup
from bpy.props import EnumProperty, FloatProperty

from ..textures import initialize_textures, threshold_enum_items
from ..node_utils import CustomNodeGroupBuilder

# defaults
_RGB = ["r", "g", "b"]
_CR_POS = (0.0, 0.0322, 0.0968, 0.226, 0.452, 1.0)


class CompositorNodeRetromancer8BitRGBDither(
    CompositorNodeCustomGroup,
    CustomNodeGroupBuilder,
):
    """8-bit RGB palette ordered dither effect using provided threshold map texture."""

    bl_idname = "CompositorNodeRetromancer8BitRGBDither"
    bl_label = "8-bit RGB Ordered Dither"
    bl_icon = "SHADERFX"
    bl_width_default = 300

    def update_texture(self, context) -> None:
        """threshold_enum_prop update callback"""
        for c in _RGB + ["a"]:
            dither_node = self.node_tree.nodes.get(f"dither_{c}")
            dither_node.threshold_enum_prop = self.threshold_enum_prop

    def update_tone_ramps(self, context) -> None:
        """tone_ramp_x_prop update callback"""
        if not context.property:
            return
        prop = self.parse_datapath(context.property[1])
        prop_val = getattr(self, prop)
        for c in _RGB:
            dither_node = self.node_tree.nodes.get(f"dither_{c}")
            setattr(dither_node, prop, prop_val)

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

    def _configure_sockets(self) -> None:
        # INPUTS:
        self.node_tree.interface.new_socket(name="Image", in_out="INPUT", socket_type="NodeSocketColor")

        # OUTPUTS:
        self.node_tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")

    def _configure_nodes(self) -> None:
        nodes = self.nodes
        nodes.add("dither_r", "CompositorNodeRetromancer6ToneDither", f"dither_r")
        nodes.add("dither_g", "CompositorNodeRetromancer6ToneDither", f"dither_g")
        nodes.add("dither_b", "CompositorNodeRetromancer6ToneDither", f"dither_b")
        nodes.add("dither_a", "CompositorNodeRetromancer2ToneDither", f"dither_a")
        nodes.add("alpha", "CompositorNodeSetAlpha")
        nodes.add("separate", "CompositorNodeSeparateColor")
        nodes.add("combine", "CompositorNodeCombineColor")
        nodes.add("posterize", type="CompositorNodePosterize")

        nodes.posterize.inputs["Steps"].default_value = 32

    def _configure_links(self) -> None:
        self.link(output=("input", "Image"), input=("separate", "Image"))
        self.link(output=("separate", "Red"), input=("dither_r", "Image"))
        self.link(output=("separate", "Green"), input=("dither_g", "Image"))
        self.link(output=("separate", "Blue"), input=("dither_b", "Image"))
        self.link(output=("separate", "Alpha"), input=("posterize", "Image"))
        self.link(output=("posterize", "Image"), input=("dither_a", "Image"))

        self.link(output=("dither_r", "Image"), input=("combine", "Red"))
        self.link(output=("dither_g", "Image"), input=("combine", "Green"))
        self.link(output=("dither_b", "Image"), input=("combine", "Blue"))
        self.link(output=("dither_a", "Image"), input=("alpha", "Alpha"))
        self.link(output=("combine", "Image"), input=("alpha", "Image"))
        self.link(output=("alpha", "Image"), input=("output", "Image"))
